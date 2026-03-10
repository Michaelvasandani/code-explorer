"""Main entry point for the baseline analyzer."""

import json
import sys
from pathlib import Path

from baseline.scanner import scan_codebase
from baseline.file_agent import analyze_file
from baseline.aggregator import aggregate_findings
from baseline.repo_merge_analyzer import analyze_repo_level
from baseline.question_generator import generate_questions
from baseline.report_builder import build_report
from baseline.metrics import MetricsTracker


def analyze_codebase(repo_path: str, output_path: str | None = None) -> dict:
    """
    Run the baseline analysis pipeline on a codebase.

    Args:
        repo_path: Path to the repository to analyze
        output_path: Optional path to write JSON report

    Returns:
        Analysis report as a dictionary
    """
    print(f"Starting baseline analysis of: {repo_path}")
    print("-" * 60)

    # Initialize metrics tracker
    metrics = MetricsTracker()

    # Phase 1: Scan codebase
    print("\n[1/6] Scanning codebase for Swift files...")
    files = scan_codebase(repo_path)
    print(f"  Found {len(files)} Swift files")

    if len(files) == 0:
        print("  ERROR: No Swift files found")
        sys.exit(1)

    # Phase 2: Analyze each file with LLM
    print("\n[2/6] Analyzing files with LLM...")
    file_results = []
    for idx, file_data in enumerate(files, 1):
        file_name = Path(file_data.path).name
        print(f"  [{idx}/{len(files)}] Analyzing {file_name}...", end=" ")

        result = analyze_file(file_data.path, file_data.content)
        file_results.append(result)

        # Track metrics with token counts
        metrics.record_file_analysis(
            cost=result.raw_cost_usd,
            findings_count=len(result.findings),
            input_tokens=getattr(result, 'input_tokens', 0),
            output_tokens=getattr(result, 'output_tokens', 0)
        )

        print(f"({len(result.findings)} findings, ${result.raw_cost_usd:.4f})")

    # Phase 3: Aggregate findings
    print("\n[3/6] Aggregating findings...")
    aggregated = aggregate_findings(file_results)
    print(f"  Total findings: {len(aggregated.all_findings)}")
    print(f"  Total cost so far: ${aggregated.total_cost:.4f}")

    # Update deduplication stats
    original_count = sum(len(r.findings) for r in file_results)
    metrics.set_deduplication_stats(
        before=original_count,
        after=len(aggregated.all_findings)
    )

    # Phase 4: Repo-level merge analysis
    print("\n[4/6] Performing repo-level merge analysis...")
    repo_result, repo_cost, repo_input_tokens, repo_output_tokens = analyze_repo_level(
        aggregated.file_summaries,
        aggregated.all_findings
    )

    # Track repo merge with actual token counts
    metrics.record_repo_merge(
        cost=repo_cost,
        input_tokens=repo_input_tokens,
        output_tokens=repo_output_tokens
    )

    print(f"  Architecture: {repo_result.high_level_summary.get('architecture_pattern', 'Unknown')}")
    print(f"  Merged findings: {len(repo_result.merged_findings)}")

    # Phase 5: Generate questions
    print("\n[5/6] Generating onboarding questions...")
    questions, q_cost, q_input_tokens, q_output_tokens = generate_questions(
        repo_result.merged_findings,
        repo_result.high_level_summary
    )

    # Track question generation with actual token counts
    metrics.record_question_generation(
        cost=q_cost,
        input_tokens=q_input_tokens,
        output_tokens=q_output_tokens
    )

    print(f"  Generated {len(questions)} questions")

    # Phase 6: Build final report
    print("\n[6/6] Building final report...")
    report = build_report(
        high_level_summary=repo_result.high_level_summary,
        findings=repo_result.merged_findings,
        questions=questions,
        metadata=metrics.get_summary()
    )

    # Convert to dict
    report_dict = json.loads(report.to_json())

    # Print summary
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    summary = metrics.get_summary()
    print(f"Total files analyzed: {summary['total_files']}")
    print(f"Total API calls: {summary['api_calls']}")
    print(f"Total tokens: {summary['total_tokens']:,} ({summary['input_tokens']:,} in, {summary['output_tokens']:,} out)")
    print(f"Total cost: ${summary['estimated_cost_usd']:.6f}")
    print(f"Total runtime: {summary['runtime_seconds']:.2f}s")
    print(f"Findings (before dedupe): {summary['findings_before_dedupe']}")
    print(f"Findings (after dedupe): {len(repo_result.merged_findings)}")
    print(f"Questions generated: {len(questions)}")
    print(f"\nCost breakdown:")
    print(f"  - File analysis: ${summary['cost_by_phase']['file_analysis']:.6f}")
    print(f"  - Repo merge: ${summary['cost_by_phase']['repo_merge']:.6f}")
    print(f"  - Questions: ${summary['cost_by_phase']['question_generation']:.6f}")

    # Write to file if requested
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2)
        print(f"\nReport written to: {output_path}")

    return report_dict


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Baseline brute-force agentic analyzer for iOS codebases"
    )
    parser.add_argument(
        "repo_path",
        help="Path to the repository to analyze"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file path",
        default=None
    )

    args = parser.parse_args()

    try:
        analyze_codebase(args.repo_path, args.output)
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

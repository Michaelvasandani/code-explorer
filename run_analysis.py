#!/usr/bin/env python3
"""
Run the Sleep Journal codebase analysis pipeline with runtime and cost tracking.
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

from analyze import analyze
from core.report_builder import ReportBuilder

def main():
    # Load environment variables
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment")
        sys.exit(1)

    # Repository path
    repo_path = Path("Sleep Journal")

    if not repo_path.exists():
        print(f"Error: Repository not found at {repo_path}")
        sys.exit(1)

    print("=" * 60)
    print("Sleep Journal Codebase Analyzer")
    print("=" * 60)
    print(f"\nAnalyzing repository: {repo_path}")
    print("\nRunning 7-phase analysis pipeline:")
    print("  Phase 1: Scanning codebase for Swift files...")

    # First, let's scan to see how many files we have
    from core.scanner import Scanner
    scanner = Scanner(repo_path=repo_path)
    files = scanner.scan()
    print(f"    Found {len(files)} Swift files")

    if len(files) == 0:
        print("\n  No Swift files found. Exiting.")
        return

    # Show file list
    print(f"\n  Files to analyze:")
    for f in files[:10]:
        print(f"    - {f.path}")
    if len(files) > 10:
        print(f"    ... and {len(files) - 10} more files")

    print("\n  Phase 2-7: AI-powered analysis (this may take several minutes)...")

    # Run the analysis with timing
    start_time = time.time()
    try:
        report, metrics = analyze(repo_path=repo_path, api_key=api_key)
        end_time = time.time()
        runtime_seconds = end_time - start_time

        print("  Phase 2: Static analysis (syntactic patterns + dependencies)...")
        print("  Phase 3: File summarization (AI)...")
        print("  Phase 4: Semantic analysis (AI)...")
        print("  Phase 5: Validation (AI)...")
        print("  Phase 6: Question generation (AI)...")
        print("  Phase 7: Report building...")

        print("\n" + "=" * 60)
        print("Analysis Complete!")
        print("=" * 60)

        # Display summary
        print(f"\nCodebase Summary:")
        print(f"  {report.summary}")

        # Display findings
        print(f"\nFindings: {len(report.findings)}")
        if report.findings:
            for i, finding in enumerate(report.findings[:5], 1):
                severity = finding.severity.upper() if finding.severity else finding.confidence.upper()
                print(f"\n  {i}. [{severity}] {finding.type}")
                print(f"     Location: {finding.location}")
                print(f"     Explanation: {finding.explanation}")
                print(f"     Confidence: {finding.confidence}")

            if len(report.findings) > 5:
                print(f"\n  ... and {len(report.findings) - 5} more findings")

        # Display onboarding questions
        if report.questions:
            print(f"\nOnboarding Questions ({len(report.questions)}):")
            for i, question in enumerate(report.questions, 1):
                print(f"  {i}. {question}")

        # Display limitations
        if report.limitations:
            print(f"\nKnown Limitations:")
            for limitation in report.limitations[:3]:
                print(f"  - {limitation}")

        # Display performance metrics
        print(f"\n{'=' * 60}")
        print("Performance Metrics")
        print(f"{'=' * 60}")
        print(f"  Runtime: {runtime_seconds:.2f} seconds ({runtime_seconds/60:.1f} minutes)")
        print(f"  API Calls: {metrics['api_calls']}")
        print(f"  Input Tokens: {metrics['input_tokens']:,}")
        print(f"  Output Tokens: {metrics['output_tokens']:,}")
        print(f"  Total Tokens: {metrics['input_tokens'] + metrics['output_tokens']:,}")
        print(f"  Estimated Cost: ${metrics['estimated_cost_usd']:.4f}")

        # Add runtime to metrics
        metrics['runtime_seconds'] = runtime_seconds

        # Update report with runtime
        report.metrics = metrics

        # Save report to file
        output_path = Path("analysis_report.json")
        builder = ReportBuilder()
        builder.save_to_file(report, output_path)

        print(f"\n{'=' * 60}")
        print(f"Full report saved to: {output_path}")
        print(f"{'=' * 60}\n")

    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

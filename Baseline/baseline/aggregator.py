"""Aggregator module for combining file-level analysis results."""

from dataclasses import dataclass
from baseline.models import FileAgentResult


@dataclass
class AggregatedResult:
    """Result of aggregating multiple file analyses."""
    all_findings: list[dict]
    file_summaries: list[str]
    total_files: int
    total_cost: float
    total_latency: float


def aggregate_findings(file_results: list[FileAgentResult]) -> AggregatedResult:
    """
    Aggregate findings from all file-level analyses.

    Args:
        file_results: List of FileAgentResult from analyzing each file

    Returns:
        AggregatedResult with combined findings, summaries, and metrics
    """
    all_findings = []
    file_summaries = []
    total_cost = 0.0
    total_latency = 0.0
    finding_counter = 1

    for file_result in file_results:
        # Collect summary
        file_summaries.append(file_result.summary)

        # Add findings with unique IDs
        for finding in file_result.findings:
            finding_with_id = finding.copy()
            finding_with_id["id"] = f"finding_{finding_counter}"
            all_findings.append(finding_with_id)
            finding_counter += 1

        # Sum costs and latencies
        total_cost += file_result.raw_cost_usd
        total_latency += file_result.raw_latency_seconds

    # Deduplicate findings
    deduped_findings = deduplicate_findings(all_findings)

    return AggregatedResult(
        all_findings=deduped_findings,
        file_summaries=file_summaries,
        total_files=len(file_results),
        total_cost=total_cost,
        total_latency=total_latency
    )


def deduplicate_findings(findings: list[dict]) -> list[dict]:
    """
    Remove duplicate findings based on type, location, and explanation similarity.

    Args:
        findings: List of finding dictionaries

    Returns:
        Deduplicated list of findings
    """
    if not findings:
        return []

    seen = set()
    deduped = []

    for finding in findings:
        # Create a signature for the finding
        signature = (
            finding.get("type", ""),
            finding.get("location", ""),
            finding.get("explanation", "")[:100]  # First 100 chars of explanation
        )

        if signature not in seen:
            seen.add(signature)
            deduped.append(finding)

    return deduped

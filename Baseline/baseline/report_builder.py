"""Report builder module for generating final JSON reports."""

from baseline.models import Finding, Question, AnalysisReport


# Tool limitations for the baseline approach
BASELINE_LIMITATIONS = {
    "limitations": [
        "Does not compile or execute code",
        "No AST-based static analysis - relies on LLM pattern recognition",
        "Per-file analysis may miss cross-file dependencies",
        "No deep call graph or data flow analysis",
        "Cannot detect runtime performance issues",
        "Cost scales linearly with codebase size (more expensive than structured approach)",
        "May produce duplicate findings despite deduplication",
        "Quality depends on LLM capabilities and prompt engineering"
    ],
    "approach": "brute_force_agentic",
    "description": "This baseline uses a simple LLM-first approach: scan each file independently, merge results, and perform one repo-level pass. It exists to compare against more structured analysis architectures."
}


def build_report(
    high_level_summary: dict,
    findings: list[dict],
    questions: list[Question],
    metadata: dict
) -> AnalysisReport:
    """
    Build the final analysis report.

    Args:
        high_level_summary: High-level architecture summary
        findings: List of finding dictionaries
        questions: List of Question objects
        metadata: Metadata about the analysis run

    Returns:
        AnalysisReport object
    """
    # Convert finding dicts to Finding objects
    finding_objects = []
    for f in findings:
        finding = Finding(
            id=f.get("id", ""),
            type=f.get("type", "uncertainty"),
            subtype=f.get("subtype"),
            location=f.get("location", ""),
            confidence=f.get("confidence", "medium"),
            explanation=f.get("explanation", ""),
            evidence=f.get("evidence"),
            tags=f.get("tags")
        )
        finding_objects.append(finding)

    # Enhance metadata with baseline-specific info
    enhanced_metadata = {
        **metadata,
        "baseline_type": "brute_force_agentic",
        "approach": "per-file LLM analysis + repo-level merge"
    }

    return AnalysisReport(
        high_level_summary=high_level_summary,
        findings=finding_objects,
        questions=questions,
        tool_limitations=BASELINE_LIMITATIONS,
        metadata=enhanced_metadata
    )

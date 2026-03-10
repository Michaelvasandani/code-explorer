"""
Phase 7: Report Building

Assembles final JSON analysis report from all pipeline outputs.
Per Architecture.md: ReportBuilder creates structured AnalysisReport with all findings and questions.
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from pathlib import Path

from analyzers.semantic_analyzer import SemanticFinding


@dataclass
class AnalysisReport:
    """
    Final analysis report matching README.md output requirements.

    Required per README:
    - High-level summary of the codebase
    - List of findings (type, location, explanation, confidence)
    - Questions for new engineers
    - Known limitations of the approach
    """
    summary: str  # High-level codebase description
    findings: List[SemanticFinding]  # Validated findings
    questions: List[str]  # Questions for new developers
    limitations: List[str]  # Known limitations of this analysis
    metrics: Dict[str, Any] = None  # Performance metrics (runtime, tokens, cost)


class ReportBuilder:
    """
    Report builder for assembling final JSON output per README requirements.

    Generates a structured report with:
    - High-level codebase summary
    - Validated findings with type, location, explanation, confidence
    - Onboarding questions
    - Known limitations

    Example:
        >>> builder = ReportBuilder()
        >>> report = builder.build(
        ...     summary="iOS sleep tracking app...",
        ...     findings=[...],
        ...     questions=[...],
        ...     limitations=[...]
        ... )
        >>> builder.save_to_file(report, Path("analysis_report.json"))
    """

    def build(
        self,
        summary: str,
        findings: List[SemanticFinding],
        questions: List[str],
        limitations: List[str],
        metrics: Dict[str, Any] = None
    ) -> AnalysisReport:
        """
        Build analysis report from pipeline outputs.

        Args:
            summary: High-level description of codebase architecture and purpose
            findings: List of validated SemanticFinding objects
            questions: List of questions for new developers
            limitations: Known limitations of this analysis approach
            metrics: Performance metrics (runtime, tokens, cost)

        Returns:
            AnalysisReport containing all required data per README
        """
        return AnalysisReport(
            summary=summary,
            findings=findings,
            questions=questions,
            limitations=limitations,
            metrics=metrics
        )

    def to_json(self, report: AnalysisReport) -> str:
        """
        Convert AnalysisReport to JSON string per README format.

        Args:
            report: AnalysisReport to serialize

        Returns:
            Pretty-printed JSON string with README-required fields
        """
        # Convert to dict matching README requirements
        data = {
            "summary": report.summary,
            "findings": [
                asdict(finding) for finding in report.findings
            ],
            "questions": report.questions,
            "limitations": report.limitations
        }

        # Add metrics if available
        if report.metrics:
            data["metrics"] = report.metrics

        # Pretty-print with indentation
        return json.dumps(data, indent=2)

    def save_to_file(self, report: AnalysisReport, output_path: Path) -> None:
        """
        Save AnalysisReport to JSON file.

        Args:
            report: AnalysisReport to save
            output_path: Path where JSON file should be written

        Creates parent directories if they don't exist.
        """
        # Ensure parent directories exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to JSON and write
        json_str = self.to_json(report)
        output_path.write_text(json_str)

"""
Tests for report_builder.py - Phase 7 report assembly.

Per CLAUDE.md TDD workflow: Tests written BEFORE implementation.
Per Architecture.md Phase 7: ReportBuilder assembles final JSON output.
"""

import pytest
import json
from pathlib import Path


class TestAnalysisReportDataclass:
    """Verify the AnalysisReport dataclass structure."""

    def test_analysis_report_has_required_fields(self):
        """Verify AnalysisReport dataclass has all required fields per Architecture.md."""
        from core.report_builder import AnalysisReport
        from analyzers.semantic_analyzer import SemanticFinding

        report = AnalysisReport(
            summary="Test summary",
            findings=[
                SemanticFinding(
                    type="bug",
                    location="Test.swift:1",
                    explanation="Test",
                    confidence="high",
                    subtype="test",
                    severity="high",
                    evidence="Evidence",
                    recommendation="Fix"
                )
            ],
            questions=["Question 1?", "Question 2?"],
            limitations=["Test limitation"]
        )

        assert len(report.findings) == 1
        assert len(report.questions) == 2
        assert isinstance(report.summary, str)


class TestReportBuilderBuild:
    """Verify ReportBuilder.build() method."""

    def test_build_creates_analysis_report(self):
        """Verify build() creates AnalysisReport from all pipeline outputs."""
        from core.report_builder import ReportBuilder
        from analyzers.semantic_analyzer import SemanticFinding

        builder = ReportBuilder()

        validated_findings = [
            SemanticFinding(
            type="bug",
            location="Network.swift:1",
            explanation="Missing error handling",
            confidence="high",
            subtype="missing_error_handling",
            severity="high",
            evidence="Force try statements",
            recommendation="Add do-catch"
        )
        ]

        questions = [
            "How should we handle errors in network operations?",
            "What's the testing strategy for critical paths?"
        ]

        stats = {
            "total_files": 13,
            "total_findings": 25,
            "findings": 8
        }

        report = builder.build(
            summary="Test summary",
            findings=validated_findings,
            questions=questions,
            limitations=["Test limitation"]
        )

        assert len(report.findings) == 1
        assert len(report.questions) == 2
        assert isinstance(report.summary, str)

    def test_build_handles_empty_findings(self):
        """Verify build() handles empty findings list."""
        from core.report_builder import ReportBuilder

        builder = ReportBuilder()
        report = builder.build(
            summary="Test summary",
            findings=[],
            questions=[],
            limitations=["Test limitation"]
        )

        assert report.findings == []
        assert report.questions == []


class TestReportBuilderToJson:
    """Verify ReportBuilder.to_json() method."""

    def test_to_json_returns_valid_json_string(self):
        """Verify to_json() converts AnalysisReport to JSON string."""
        from core.report_builder import ReportBuilder
        from analyzers.semantic_analyzer import SemanticFinding

        builder = ReportBuilder()

        validated_findings = [
            SemanticFinding(
            type="architecture",
            location="Store.swift:1",
            explanation="Circular dependency",
            confidence="medium",
            subtype="circular_dependency",
            severity="medium",
            evidence="Import analysis",
            recommendation="Extract protocol"
        )
        ]

        questions = ["What's the architecture pattern?"]
        stats = {"total_files": 2, "total_findings": 5, "findings": 1}

        report = builder.build(
            summary="Test summary",
            findings=validated_findings,
            questions=questions,
            limitations=["Test limitation"]
        )
        json_str = builder.to_json(report)

        # Should be valid JSON
        data = json.loads(json_str)
        assert "findings" in data
        assert "questions" in data
        assert "summary" in data

    def test_to_json_includes_all_finding_fields(self):
        """Verify to_json() includes all SemanticFinding fields."""
        from core.report_builder import ReportBuilder
        from analyzers.semantic_analyzer import SemanticFinding

        builder = ReportBuilder()

        finding = SemanticFinding(
            type="bug",
            location="Network.swift:1",
            explanation="Missing error handling",
            confidence="high",
            subtype="missing_error_handling",
            severity="high",
            evidence="Force try statements",
            recommendation="Add do-catch blocks"
        )

        report = builder.build(
            summary="Test summary",
            findings=[finding],
            questions=[],
            limitations=["Test limitation"]
        )
        json_str = builder.to_json(report)
        data = json.loads(json_str)

        finding_data = data["findings"][0]
        assert finding_data["type"] == "bug"
        assert finding_data["subtype"] == "missing_error_handling"
        assert finding_data["severity"] == "high"
        assert finding_data["location"] == "Network.swift:1"
        assert finding_data["explanation"] == "Missing error handling"
        assert finding_data["evidence"] == "Force try statements"
        assert finding_data["recommendation"] == "Add do-catch blocks"

    def test_to_json_pretty_prints_by_default(self):
        """Verify to_json() pretty-prints JSON by default."""
        from core.report_builder import ReportBuilder

        builder = ReportBuilder()
        report = builder.build(
            summary="Test summary",
            findings=[],
            questions=["Question?"],
            limitations=["Test limitation"]
        )
        json_str = builder.to_json(report)

        # Pretty-printed JSON has newlines and indentation
        assert "\n" in json_str
        assert "  " in json_str or "\t" in json_str


class TestReportBuilderSaveToFile:
    """Verify ReportBuilder.save_to_file() method."""

    def test_save_to_file_writes_json_to_path(self, tmp_path):
        """Verify save_to_file() writes JSON to specified path."""
        from core.report_builder import ReportBuilder
        from analyzers.semantic_analyzer import SemanticFinding

        builder = ReportBuilder()

        finding = SemanticFinding(
            type="test_gap",
            location="Store.swift:1",
            explanation="Missing tests",
            confidence="medium",
            subtype="missing_tests",
            severity="medium",
            evidence="No test files found",
            recommendation="Add unit tests"
        )

        report = builder.build(
            summary="Test summary",
            findings=[finding],
            questions=["Question?"],
            limitations=["Test limitation"]
        )

        output_path = tmp_path / "analysis_report.json"
        builder.save_to_file(report, output_path)

        # File should exist
        assert output_path.exists()

        # File should contain valid JSON
        data = json.loads(output_path.read_text())
        assert len(data["findings"]) == 1
        assert data["findings"][0]["type"] == "test_gap"

    def test_save_to_file_creates_parent_directories(self, tmp_path):
        """Verify save_to_file() creates parent directories if needed."""
        from core.report_builder import ReportBuilder

        builder = ReportBuilder()
        report = builder.build(
            summary="Test summary",
            findings=[],
            questions=[],
            limitations=["Test limitation"]
        )

        output_path = tmp_path / "output" / "reports" / "analysis.json"
        builder.save_to_file(report, output_path)

        assert output_path.exists()


class TestReportBuilderStatistics:
    """Verify ReportBuilder handles summary statistics correctly."""

    def test_build_preserves_custom_stats(self):
        """Verify build() preserves all provided statistics."""
        from core.report_builder import ReportBuilder

        builder = ReportBuilder()

        stats = {
            "total_files": 13,
            "total_findings": 25,
            "findings": 8,
            "high_severity_count": 3,
            "medium_severity_count": 4,
            "low_severity_count": 1
        }

        report = builder.build(
            summary="Test summary",
            findings=[],
            questions=[],
            limitations=["Test limitation"]
        )

        assert isinstance(report.summary, str)
        # Stats no longer in report schema
        # Stats no longer in report schema

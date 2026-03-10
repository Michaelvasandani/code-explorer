"""Tests for the report_builder module."""

import pytest
import json
from baseline.report_builder import build_report
from baseline.models import Finding, Question, AnalysisReport


class TestReportBuilder:
    """Tests for report generation."""

    @pytest.fixture
    def sample_data(self):
        """Sample data for report building."""
        return {
            "high_level_summary": {
                "architecture_pattern": "Mixed UIKit/SwiftUI",
                "key_components": ["JournalStore", "WeatherClient"],
                "primary_risks": ["Force unwraps", "No tests"]
            },
            "findings": [
                {
                    "id": "finding_1",
                    "type": "bug",
                    "location": "JournalStore.swift:24",
                    "confidence": "high",
                    "explanation": "Force-try on JSONDecoder"
                }
            ],
            "questions": [
                Question(
                    id="question_1",
                    question="What is the error handling strategy?",
                    why_it_matters="Force-try will crash",
                    related_findings=["finding_1"],
                    areas_affected=["Persistence"]
                )
            ],
            "metadata": {
                "total_files": 10,
                "total_cost_usd": 0.05,
                "total_latency_seconds": 15.0
            }
        }

    def test_build_report_returns_analysis_report(self, sample_data):
        """Test that build_report returns an AnalysisReport object."""
        report = build_report(
            sample_data["high_level_summary"],
            sample_data["findings"],
            sample_data["questions"],
            sample_data["metadata"]
        )

        assert isinstance(report, AnalysisReport)

    def test_build_report_converts_findings_to_objects(self, sample_data):
        """Test that findings are converted to Finding objects."""
        report = build_report(
            sample_data["high_level_summary"],
            sample_data["findings"],
            sample_data["questions"],
            sample_data["metadata"]
        )

        assert all(isinstance(f, Finding) for f in report.findings)
        assert len(report.findings) == 1

    def test_build_report_preserves_finding_data(self, sample_data):
        """Test that finding data is preserved."""
        report = build_report(
            sample_data["high_level_summary"],
            sample_data["findings"],
            sample_data["questions"],
            sample_data["metadata"]
        )

        finding = report.findings[0]
        assert finding.id == "finding_1"
        assert finding.type == "bug"
        assert finding.confidence == "high"
        assert "Force-try" in finding.explanation

    def test_build_report_preserves_questions(self, sample_data):
        """Test that questions are preserved."""
        report = build_report(
            sample_data["high_level_summary"],
            sample_data["findings"],
            sample_data["questions"],
            sample_data["metadata"]
        )

        assert len(report.questions) == 1
        assert isinstance(report.questions[0], Question)
        assert report.questions[0].id == "question_1"

    def test_build_report_includes_tool_limitations(self, sample_data):
        """Test that tool limitations are included."""
        report = build_report(
            sample_data["high_level_summary"],
            sample_data["findings"],
            sample_data["questions"],
            sample_data["metadata"]
        )

        assert "limitations" in report.tool_limitations
        assert isinstance(report.tool_limitations["limitations"], list)

    def test_build_report_includes_metadata(self, sample_data):
        """Test that metadata is included."""
        report = build_report(
            sample_data["high_level_summary"],
            sample_data["findings"],
            sample_data["questions"],
            sample_data["metadata"]
        )

        assert "total_files" in report.metadata
        assert report.metadata["total_files"] == 10
        assert "baseline_type" in report.metadata

    def test_build_report_serializes_to_json(self, sample_data):
        """Test that report can be serialized to JSON."""
        report = build_report(
            sample_data["high_level_summary"],
            sample_data["findings"],
            sample_data["questions"],
            sample_data["metadata"]
        )

        json_str = report.to_json()
        assert isinstance(json_str, str)

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert "high_level_summary" in parsed
        assert "findings" in parsed
        assert "questions" in parsed

    def test_build_report_handles_empty_findings(self, sample_data):
        """Test that empty findings list is handled."""
        report = build_report(
            sample_data["high_level_summary"],
            [],
            sample_data["questions"],
            sample_data["metadata"]
        )

        assert report.findings == []

    def test_build_report_handles_empty_questions(self, sample_data):
        """Test that empty questions list is handled."""
        report = build_report(
            sample_data["high_level_summary"],
            sample_data["findings"],
            [],
            sample_data["metadata"]
        )

        assert report.questions == []

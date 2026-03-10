"""Tests for the aggregator module."""

import pytest
from baseline.aggregator import aggregate_findings, deduplicate_findings
from baseline.models import FileAgentResult


class TestAggregator:
    """Tests for findings aggregation."""

    @pytest.fixture
    def sample_file_results(self):
        """Sample file agent results for testing."""
        return [
            FileAgentResult(
                file_path="File1.swift",
                summary="Persistence store",
                findings=[
                    {
                        "type": "bug",
                        "location": "File1.swift:10",
                        "confidence": "high",
                        "explanation": "Force-try on decoder"
                    },
                    {
                        "type": "test_gap",
                        "location": "File1.swift",
                        "confidence": "medium",
                        "explanation": "No tests for persistence"
                    }
                ],
                raw_cost_usd=0.002,
                raw_latency_seconds=0.5
            ),
            FileAgentResult(
                file_path="File2.swift",
                summary="Network client",
                findings=[
                    {
                        "type": "bug",
                        "location": "File2.swift:25",
                        "confidence": "high",
                        "explanation": "Force unwrap on array access"
                    }
                ],
                raw_cost_usd=0.003,
                raw_latency_seconds=0.6
            )
        ]

    def test_aggregate_findings_combines_all_findings(self, sample_file_results):
        """Test that aggregator combines findings from all files."""
        result = aggregate_findings(sample_file_results)

        assert len(result.all_findings) == 3
        assert result.total_files == 2

    def test_aggregate_findings_assigns_unique_ids(self, sample_file_results):
        """Test that each finding gets a unique ID."""
        result = aggregate_findings(sample_file_results)

        ids = [f["id"] for f in result.all_findings]
        assert len(ids) == len(set(ids))  # All unique
        assert all(id.startswith("finding_") for id in ids)

    def test_aggregate_findings_preserves_finding_data(self, sample_file_results):
        """Test that finding data is preserved during aggregation."""
        result = aggregate_findings(sample_file_results)

        bug_findings = [f for f in result.all_findings if f["type"] == "bug"]
        assert len(bug_findings) == 2
        assert any("Force-try" in f["explanation"] for f in bug_findings)

    def test_aggregate_findings_collects_summaries(self, sample_file_results):
        """Test that file summaries are collected."""
        result = aggregate_findings(sample_file_results)

        assert len(result.file_summaries) == 2
        assert "Persistence store" in result.file_summaries
        assert "Network client" in result.file_summaries

    def test_aggregate_findings_sums_costs(self, sample_file_results):
        """Test that API costs are summed correctly."""
        result = aggregate_findings(sample_file_results)

        assert result.total_cost == 0.005  # 0.002 + 0.003

    def test_aggregate_findings_sums_latency(self, sample_file_results):
        """Test that latencies are summed correctly."""
        result = aggregate_findings(sample_file_results)

        assert result.total_latency == 1.1  # 0.5 + 0.6

    def test_deduplicate_findings_removes_exact_duplicates(self):
        """Test that exact duplicate findings are removed."""
        findings = [
            {
                "id": "finding_1",
                "type": "bug",
                "location": "File.swift:10",
                "explanation": "Force unwrap"
            },
            {
                "id": "finding_2",
                "type": "bug",
                "location": "File.swift:10",
                "explanation": "Force unwrap"
            }
        ]

        deduped = deduplicate_findings(findings)

        assert len(deduped) == 1

    def test_deduplicate_findings_keeps_different_locations(self):
        """Test that findings at different locations are kept."""
        findings = [
            {
                "id": "finding_1",
                "type": "bug",
                "location": "File.swift:10",
                "explanation": "Force unwrap"
            },
            {
                "id": "finding_2",
                "type": "bug",
                "location": "File.swift:20",
                "explanation": "Force unwrap"
            }
        ]

        deduped = deduplicate_findings(findings)

        assert len(deduped) == 2

    def test_deduplicate_findings_keeps_different_types(self):
        """Test that findings of different types are kept."""
        findings = [
            {
                "id": "finding_1",
                "type": "bug",
                "location": "File.swift:10",
                "explanation": "Issue here"
            },
            {
                "id": "finding_2",
                "type": "smell",
                "location": "File.swift:10",
                "explanation": "Issue here"
            }
        ]

        deduped = deduplicate_findings(findings)

        assert len(deduped) == 2

    def test_aggregate_findings_handles_empty_input(self):
        """Test that empty file list is handled gracefully."""
        result = aggregate_findings([])

        assert result.all_findings == []
        assert result.total_files == 0
        assert result.total_cost == 0.0
        assert result.total_latency == 0.0

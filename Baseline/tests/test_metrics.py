"""Tests for the metrics module."""

import pytest
import time
from baseline.metrics import MetricsTracker


class TestMetrics:
    """Tests for metrics tracking."""

    def test_metrics_tracker_initialization(self):
        """Test that MetricsTracker initializes correctly."""
        tracker = MetricsTracker()

        assert tracker.start_time is not None
        assert tracker.total_cost_usd == 0.0
        assert tracker.total_files == 0
        assert tracker.llm_calls == 0
        assert tracker.findings_before_dedupe == 0
        assert tracker.findings_after_dedupe == 0

    def test_record_file_analysis(self):
        """Test recording file analysis metrics."""
        tracker = MetricsTracker()

        tracker.record_file_analysis(cost=0.002, findings_count=3)

        assert tracker.total_cost_usd == 0.002
        assert tracker.total_files == 1
        assert tracker.llm_calls == 1
        assert tracker.findings_before_dedupe == 3

    def test_record_multiple_files(self):
        """Test recording multiple file analyses."""
        tracker = MetricsTracker()

        tracker.record_file_analysis(cost=0.002, findings_count=3)
        tracker.record_file_analysis(cost=0.003, findings_count=2)
        tracker.record_file_analysis(cost=0.001, findings_count=1)

        assert tracker.total_cost_usd == 0.006
        assert tracker.total_files == 3
        assert tracker.llm_calls == 3
        assert tracker.findings_before_dedupe == 6

    def test_record_repo_merge(self):
        """Test recording repo-level merge metrics."""
        tracker = MetricsTracker()

        tracker.record_repo_merge(cost=0.005)

        assert tracker.total_cost_usd == 0.005
        assert tracker.llm_calls == 1
        # Files should not be incremented for repo merge
        assert tracker.total_files == 0

    def test_record_question_generation(self):
        """Test recording question generation metrics."""
        tracker = MetricsTracker()

        tracker.record_question_generation(cost=0.003)

        assert tracker.total_cost_usd == 0.003
        assert tracker.llm_calls == 1

    def test_set_deduplication_stats(self):
        """Test setting deduplication statistics."""
        tracker = MetricsTracker()

        tracker.set_deduplication_stats(before=25, after=18)

        assert tracker.findings_before_dedupe == 25
        assert tracker.findings_after_dedupe == 18

    def test_get_runtime(self):
        """Test calculating runtime."""
        tracker = MetricsTracker()
        time.sleep(0.1)  # Sleep for 100ms

        runtime = tracker.get_runtime()

        assert runtime >= 0.1
        assert runtime < 1.0  # Should be less than 1 second

    def test_get_summary(self):
        """Test getting metrics summary."""
        tracker = MetricsTracker()

        tracker.record_file_analysis(cost=0.002, findings_count=3)
        tracker.record_file_analysis(cost=0.003, findings_count=2)
        tracker.record_repo_merge(cost=0.005)
        tracker.set_deduplication_stats(before=5, after=4)

        summary = tracker.get_summary()

        assert summary["total_files"] == 2
        assert summary["estimated_cost_usd"] == 0.010
        assert summary["api_calls"] == 3
        assert summary["findings_before_dedupe"] == 5
        assert summary["findings_after_dedupe"] == 4
        assert "runtime_seconds" in summary
        assert summary["runtime_seconds"] >= 0
        assert "cost_by_phase" in summary
        assert "tokens_by_phase" in summary

    def test_full_workflow(self):
        """Test complete metrics tracking workflow."""
        tracker = MetricsTracker()

        # Simulate analyzing 3 files
        tracker.record_file_analysis(cost=0.002, findings_count=4)
        tracker.record_file_analysis(cost=0.003, findings_count=3)
        tracker.record_file_analysis(cost=0.002, findings_count=2)

        # Simulate repo merge
        tracker.record_repo_merge(cost=0.005)

        # Simulate question generation
        tracker.record_question_generation(cost=0.003)

        # Set deduplication stats
        tracker.set_deduplication_stats(before=9, after=7)

        # Get summary
        summary = tracker.get_summary()

        assert summary["total_files"] == 3
        assert summary["estimated_cost_usd"] == 0.015  # 0.002 + 0.003 + 0.002 + 0.005 + 0.003
        assert summary["api_calls"] == 5  # 3 files + 1 repo merge + 1 question gen
        assert summary["findings_before_dedupe"] == 9
        assert summary["findings_after_dedupe"] == 7
        assert "cost_by_phase" in summary
        assert summary["cost_by_phase"]["file_analysis"] == 0.007
        assert summary["cost_by_phase"]["repo_merge"] == 0.005
        assert summary["cost_by_phase"]["question_generation"] == 0.003

"""Tests for the repo_merge_analyzer module."""

import pytest
from unittest.mock import patch
from baseline.repo_merge_analyzer import analyze_repo_level
from baseline.models import RepoMergeResult


class TestRepoMergeAnalyzer:
    """Tests for repository-level analysis."""

    @pytest.fixture
    def sample_summaries(self):
        """Sample file summaries."""
        return [
            "JournalStore: Singleton persistence using UserDefaults",
            "WeatherClient: Network client for weather.gov API",
            "SleepListViewModel: ViewModel for filtering sleep entries"
        ]

    @pytest.fixture
    def sample_findings(self):
        """Sample aggregated findings."""
        return [
            {
                "id": "finding_1",
                "type": "bug",
                "location": "JournalStore.swift:24",
                "confidence": "high",
                "explanation": "Force-try on JSONDecoder"
            },
            {
                "id": "finding_2",
                "type": "bug",
                "location": "WeatherClient.swift:30",
                "confidence": "high",
                "explanation": "Force unwrap on array"
            },
            {
                "id": "finding_3",
                "type": "architecture",
                "location": "JournalStore.swift",
                "confidence": "medium",
                "explanation": "Singleton pattern"
            }
        ]

    @pytest.fixture
    def mock_repo_response(self):
        """Mock OpenAI response for repo-level analysis."""
        return {
            "high_level_summary": {
                "architecture_pattern": "Mixed UIKit/SwiftUI with MVVM",
                "key_components": ["JournalStore", "WeatherClient", "ViewModels"],
                "primary_risks": ["Force unwraps", "Singleton overuse"]
            },
            "merged_findings": [
                {
                    "id": "finding_1",
                    "type": "bug",
                    "location": "JournalStore.swift:24",
                    "confidence": "high",
                    "explanation": "Force-try on JSONDecoder will crash on malformed data"
                },
                {
                    "id": "finding_2",
                    "type": "bug",
                    "location": "WeatherClient.swift:30",
                    "confidence": "high",
                    "explanation": "Force unwrap on array access - crash if empty"
                }
            ]
        }

    def test_analyze_repo_level_returns_structured_result(self, sample_summaries, sample_findings, mock_repo_response):
        """Test that repo-level analysis returns RepoMergeResult."""
        with patch('baseline.repo_merge_analyzer.call_openai') as mock_call:
            mock_call.return_value = (mock_repo_response, 0.005, 2.0, 200, 150)

            result = analyze_repo_level(sample_summaries, sample_findings)

            assert isinstance(result, RepoMergeResult)
            assert "architecture_pattern" in result.high_level_summary
            assert len(result.merged_findings) > 0

    def test_analyze_repo_level_identifies_architecture_patterns(self, sample_summaries, sample_findings, mock_repo_response):
        """Test that repo-level analysis identifies architecture patterns."""
        with patch('baseline.repo_merge_analyzer.call_openai') as mock_call:
            mock_call.return_value = (mock_repo_response, 0.005, 2.0, 200, 150)

            result = analyze_repo_level(sample_summaries, sample_findings)

            assert "architecture_pattern" in result.high_level_summary
            assert result.high_level_summary["architecture_pattern"] != ""

    def test_analyze_repo_level_identifies_key_components(self, sample_summaries, sample_findings, mock_repo_response):
        """Test that key components are identified."""
        with patch('baseline.repo_merge_analyzer.call_openai') as mock_call:
            mock_call.return_value = (mock_repo_response, 0.005, 2.0, 200, 150)

            result = analyze_repo_level(sample_summaries, sample_findings)

            assert "key_components" in result.high_level_summary
            assert isinstance(result.high_level_summary["key_components"], list)

    def test_analyze_repo_level_identifies_primary_risks(self, sample_summaries, sample_findings, mock_repo_response):
        """Test that primary risks are identified."""
        with patch('baseline.repo_merge_analyzer.call_openai') as mock_call:
            mock_call.return_value = (mock_repo_response, 0.005, 2.0, 200, 150)

            result = analyze_repo_level(sample_summaries, sample_findings)

            assert "primary_risks" in result.high_level_summary
            assert isinstance(result.high_level_summary["primary_risks"], list)

    def test_analyze_repo_level_merges_duplicate_findings(self, sample_summaries, sample_findings, mock_repo_response):
        """Test that duplicate findings can be merged."""
        # Response with fewer findings than input (merge happened)
        merged_response = mock_repo_response.copy()
        merged_response["merged_findings"] = merged_response["merged_findings"][:2]

        with patch('baseline.repo_merge_analyzer.call_openai') as mock_call:
            mock_call.return_value = (merged_response, 0.005, 2.0, 200, 150)

            result = analyze_repo_level(sample_summaries, sample_findings)

            # Merged findings should be <= original
            assert len(result.merged_findings) <= len(sample_findings)

    def test_analyze_repo_level_handles_empty_input(self, mock_repo_response):
        """Test that empty inputs are handled gracefully."""
        empty_response = {
            "high_level_summary": {
                "architecture_pattern": "Unknown",
                "key_components": [],
                "primary_risks": []
            },
            "merged_findings": []
        }
        with patch('baseline.repo_merge_analyzer.call_openai') as mock_call:
            mock_call.return_value = (empty_response, 0.001, 0.5)

            result = analyze_repo_level([], [])

            assert result.high_level_summary is not None
            assert result.merged_findings == []

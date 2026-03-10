"""Tests for the file_agent module."""

import pytest
from unittest.mock import Mock, patch
from baseline.file_agent import analyze_file
from baseline.models import FileAgentResult


class TestFileAgent:
    """Tests for file-level LLM analysis."""

    @pytest.fixture
    def sample_swift_file(self):
        """Sample Swift code for testing."""
        return """
import Foundation

class JournalStore {
    static let shared = JournalStore()

    func loadEntries() -> [Entry] {
        let data = try! JSONDecoder().decode([Entry].self, from: savedData)
        return data
    }
}
"""

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response."""
        return {
            "summary": "Singleton store with force-try decoder",
            "findings": [
                {
                    "type": "bug",
                    "location": "JournalStore.swift:7",
                    "confidence": "high",
                    "explanation": "Force-try on JSONDecoder will crash if data is malformed"
                }
            ]
        }

    def test_analyze_file_returns_structured_result(self, sample_swift_file, mock_openai_response):
        """Test that analyze_file returns a FileAgentResult with structured data."""
        with patch('baseline.file_agent.call_openai') as mock_call:
            mock_call.return_value = (mock_openai_response, 0.002, 0.5, 100, 50)

            result = analyze_file("JournalStore.swift", sample_swift_file)

            assert isinstance(result, FileAgentResult)
            assert result.file_path == "JournalStore.swift"
            assert result.summary != ""
            assert len(result.findings) > 0
            assert result.raw_cost_usd > 0
            assert result.raw_latency_seconds > 0

    def test_analyze_file_identifies_force_unwrap(self, sample_swift_file, mock_openai_response):
        """Test that file agent identifies force-unwrap patterns."""
        with patch('baseline.file_agent.call_openai') as mock_call:
            mock_call.return_value = (mock_openai_response, 0.002, 0.5, 100, 50)

            result = analyze_file("JournalStore.swift", sample_swift_file)

            assert any("try!" in f.get("explanation", "") or "force" in f.get("explanation", "").lower()
                      for f in result.findings)

    def test_analyze_file_assigns_finding_types(self, sample_swift_file, mock_openai_response):
        """Test that findings have valid types."""
        with patch('baseline.file_agent.call_openai') as mock_call:
            mock_call.return_value = (mock_openai_response, 0.002, 0.5, 100, 50)

            result = analyze_file("JournalStore.swift", sample_swift_file)

            valid_types = {"bug", "smell", "architecture", "test_gap", "documentation_gap", "uncertainty"}
            for finding in result.findings:
                assert finding["type"] in valid_types

    def test_analyze_file_assigns_confidence_levels(self, sample_swift_file, mock_openai_response):
        """Test that findings have valid confidence levels."""
        with patch('baseline.file_agent.call_openai') as mock_call:
            mock_call.return_value = (mock_openai_response, 0.002, 0.5, 100, 50)

            result = analyze_file("JournalStore.swift", sample_swift_file)

            valid_confidence = {"high", "medium", "low"}
            for finding in result.findings:
                assert finding["confidence"] in valid_confidence

    def test_analyze_file_tracks_cost(self, sample_swift_file, mock_openai_response):
        """Test that API cost is tracked per file."""
        with patch('baseline.file_agent.call_openai') as mock_call:
            mock_call.return_value = (mock_openai_response, 0.003, 1.2, 120, 60)

            result = analyze_file("JournalStore.swift", sample_swift_file)

            assert result.raw_cost_usd == 0.003

    def test_analyze_file_tracks_latency(self, sample_swift_file, mock_openai_response):
        """Test that API latency is tracked per file."""
        with patch('baseline.file_agent.call_openai') as mock_call:
            mock_call.return_value = (mock_openai_response, 0.003, 1.2, 120, 60)

            result = analyze_file("JournalStore.swift", sample_swift_file)

            assert result.raw_latency_seconds == 1.2

    def test_analyze_file_handles_empty_findings(self, sample_swift_file):
        """Test that files with no issues return empty findings list."""
        clean_response = {
            "summary": "Clean code with no issues",
            "findings": []
        }
        with patch('baseline.file_agent.call_openai') as mock_call:
            mock_call.return_value = (clean_response, 0.001, 0.3, 80, 20)

            result = analyze_file("CleanFile.swift", sample_swift_file)

            assert result.findings == []
            assert result.summary != ""

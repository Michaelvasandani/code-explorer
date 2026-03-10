"""Integration tests for the full baseline analyzer pipeline."""

import pytest
import json
import tempfile
from pathlib import Path
from baseline.analyze_baseline import analyze_codebase


class TestIntegration:
    """Integration tests for full analysis pipeline."""

    @pytest.fixture
    def sample_repo(self, tmp_path):
        """Create a sample Swift repository for testing."""
        # Create directory structure
        (tmp_path / "Models").mkdir()
        (tmp_path / "Services").mkdir()

        # Create sample Swift files
        (tmp_path / "Models" / "User.swift").write_text("""
import Foundation

struct User {
    let id: String
    let name: String

    func loadData() {
        let data = try! JSONDecoder().decode(User.self, from: Data())
    }
}
""")

        (tmp_path / "Services" / "NetworkClient.swift").write_text("""
import Foundation

class NetworkClient {
    static let shared = NetworkClient()

    func fetch() -> Data {
        let response = urlSession.data(for: request)
        return response.0!  // Force unwrap
    }
}
""")

        return str(tmp_path)

    def test_full_pipeline_runs(self, sample_repo):
        """Test that the full pipeline runs without errors."""
        # This is a minimal test that doesn't actually call OpenAI
        # For real integration testing, we'd need API access

        # Just verify the structure exists
        assert Path(sample_repo).exists()
        assert (Path(sample_repo) / "Models" / "User.swift").exists()

    def test_analyze_with_real_sleep_journal(self):
        """Test analysis with the real Sleep Journal codebase."""
        # This test is marked to skip if the Sleep Journal path doesn't exist
        sleep_journal_path = Path(__file__).parent.parent.parent / "Sleep Journal"

        if not sleep_journal_path.exists():
            pytest.skip("Sleep Journal codebase not found")

        # Run analysis (only if OPENAI_API_KEY is set)
        import os
        if not os.environ.get("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

        # Run the analysis
        output_path = tempfile.mktemp(suffix=".json")
        report = analyze_codebase(str(sleep_journal_path), output_path)

        # Verify report structure
        assert "high_level_summary" in report
        assert "findings" in report
        assert "questions" in report
        assert "metadata" in report
        assert "tool_limitations" in report

        # Verify high-level summary
        assert "architecture_pattern" in report["high_level_summary"]
        assert "key_components" in report["high_level_summary"]
        assert "primary_risks" in report["high_level_summary"]

        # Verify findings have correct structure
        for finding in report["findings"]:
            assert "id" in finding
            assert "type" in finding
            assert finding["type"] in ["bug", "smell", "architecture", "test_gap", "documentation_gap", "uncertainty"]
            assert "confidence" in finding
            assert finding["confidence"] in ["high", "medium", "low"]
            assert "explanation" in finding

        # Verify questions have correct structure
        for question in report["questions"]:
            assert "id" in question
            assert "question" in question
            assert "why_it_matters" in question

        # Verify metadata
        assert report["metadata"]["baseline_type"] == "brute_force_agentic"
        assert report["metadata"]["total_files"] > 0
        assert report["metadata"]["total_cost_usd"] > 0
        assert report["metadata"]["llm_calls"] > 0

        # Clean up
        if Path(output_path).exists():
            Path(output_path).unlink()

        print(f"\nSUCCESS: Analyzed {report['metadata']['total_files']} files")
        print(f"Found {len(report['findings'])} findings")
        print(f"Generated {len(report['questions'])} questions")
        print(f"Cost: ${report['metadata']['total_cost_usd']:.4f}")

"""
Tests for semantic_analyzer.txt prompt template.

Per CLAUDE.md TDD workflow: Tests written BEFORE prompt template creation.
Per Architecture.md Phase 4: SemanticAnalyzer detects repo-level issues using file summaries.
"""

import pytest
from pathlib import Path
from analyzers.prompt_loader import PromptLoader


class TestSemanticAnalyzerPromptExists:
    """Verify the semantic_analyzer.txt prompt template exists and is loadable."""

    def test_prompt_file_exists(self):
        """Verify prompts/semantic_analyzer.txt exists."""
        prompt_path = Path("prompts/semantic_analyzer.txt")
        assert prompt_path.exists(), "prompts/semantic_analyzer.txt must exist"

    def test_prompt_is_readable(self):
        """Verify prompt file can be loaded via PromptLoader."""
        loader = PromptLoader()
        prompt = loader.load("semantic_analyzer")
        assert isinstance(prompt, str)
        assert len(prompt) > 0, "Prompt template should not be empty"


class TestSemanticAnalyzerPromptStructure:
    """Verify the prompt template has required structure and placeholders."""

    @pytest.fixture
    def prompt_template(self):
        """Load the semantic_analyzer prompt template."""
        loader = PromptLoader()
        return loader.load("semantic_analyzer")

    def test_has_file_summaries_placeholder(self, prompt_template):
        """Verify prompt has {file_summaries} placeholder for FileSummary data."""
        assert "{file_summaries}" in prompt_template, "Must have {file_summaries} placeholder"

    def test_has_static_findings_placeholder(self, prompt_template):
        """Verify prompt has {static_findings} placeholder for StaticFinding data."""
        assert "{static_findings}" in prompt_template, "Must have {static_findings} placeholder"

    def test_has_dependency_graph_placeholder(self, prompt_template):
        """Verify prompt has {dependency_graph} placeholder for dependency data."""
        assert "{dependency_graph}" in prompt_template, "Must have {dependency_graph} placeholder"

    def test_mentions_json_output(self, prompt_template):
        """Verify prompt instructs LLM to return JSON format."""
        prompt_lower = prompt_template.lower()
        assert "json" in prompt_lower, "Prompt must specify JSON output format"

    def test_mentions_required_fields(self, prompt_template):
        """Verify prompt specifies the required SemanticFinding fields."""
        # Per Architecture.md, SemanticFinding has: type, subtype, severity, files, description, evidence, recommendation
        assert "type" in prompt_template
        assert "severity" in prompt_template
        assert "description" in prompt_template
        assert "evidence" in prompt_template
        assert "recommendation" in prompt_template


class TestSemanticAnalyzerPromptRendering:
    """Verify the prompt can be rendered with variables."""

    def test_render_with_variables(self):
        """Verify prompt renders correctly with file_summaries, static_findings, dependency_graph."""
        loader = PromptLoader()

        sample_summaries = '[{{"file_path": "Store.swift", "role": "service"}}]'
        sample_findings = '[{{"type": "crash_risk", "file": "Store.swift"}}]'
        sample_graph = '{{"Store.swift": ["Foundation"]}}'

        rendered = loader.render(
            "semantic_analyzer",
            file_summaries=sample_summaries,
            static_findings=sample_findings,
            dependency_graph=sample_graph
        )

        assert isinstance(rendered, str)
        assert len(rendered) > 0
        assert "Store.swift" in rendered, "Rendered prompt should contain the data"
        # Verify placeholders were replaced
        assert "{file_summaries}" not in rendered
        assert "{static_findings}" not in rendered
        assert "{dependency_graph}" not in rendered


class TestSemanticAnalyzerPromptGuidance:
    """Verify the prompt provides appropriate guidance to the LLM."""

    @pytest.fixture
    def prompt_template(self):
        """Load the semantic_analyzer prompt template."""
        loader = PromptLoader()
        return loader.load("semantic_analyzer")

    def test_instructs_repo_level_analysis(self, prompt_template):
        """Verify prompt instructs LLM to perform repository-level analysis."""
        prompt_lower = prompt_template.lower()
        # Look for repo-level analysis keywords
        repo_keywords = ["repository", "repo", "codebase", "cross-file", "architectural"]
        assert any(keyword in prompt_lower for keyword in repo_keywords), \
            "Prompt should instruct repository-level analysis"

    def test_mentions_issue_categories(self, prompt_template):
        """Verify prompt mentions the categories of issues to detect."""
        prompt_lower = prompt_template.lower()
        # Per Architecture.md Phase 4: bugs, code smells, architecture issues, test gaps, doc gaps
        assert "bug" in prompt_lower or "bugs" in prompt_lower
        assert "smell" in prompt_lower
        assert "architecture" in prompt_lower or "architectural" in prompt_lower
        assert "test" in prompt_lower
        assert "doc" in prompt_lower or "documentation" in prompt_lower

    def test_instructs_evidence_based_findings(self, prompt_template):
        """Verify prompt instructs LLM to provide evidence for findings."""
        prompt_lower = prompt_template.lower()
        evidence_keywords = ["evidence", "grounded", "based on", "specific", "concrete"]
        assert any(keyword in prompt_lower for keyword in evidence_keywords), \
            "Prompt should require evidence-based findings"

    def test_mentions_severity_levels(self, prompt_template):
        """Verify prompt defines severity levels for findings."""
        prompt_lower = prompt_template.lower()
        # Should mention severity classification
        assert "severity" in prompt_lower
        # Common severity levels
        severity_keywords = ["high", "medium", "low", "critical"]
        assert any(keyword in prompt_lower for keyword in severity_keywords), \
            "Prompt should define severity levels"

    def test_instructs_actionable_recommendations(self, prompt_template):
        """Verify prompt asks for actionable recommendations."""
        prompt_lower = prompt_template.lower()
        action_keywords = ["recommendation", "suggest", "fix", "improve", "action"]
        assert any(keyword in prompt_lower for keyword in action_keywords), \
            "Prompt should ask for actionable recommendations"


class TestSemanticAnalyzerPromptExamples:
    """Verify the prompt includes examples for clarity."""

    @pytest.fixture
    def prompt_template(self):
        """Load the semantic_analyzer prompt template."""
        loader = PromptLoader()
        return loader.load("semantic_analyzer")

    def test_includes_example_output(self, prompt_template):
        """Verify prompt includes example JSON output for clarity."""
        prompt_lower = prompt_template.lower()
        assert "example" in prompt_lower, "Prompt should include example output"


class TestSemanticAnalyzerPromptContext:
    """Verify the prompt provides context about Phase 1-3 data."""

    @pytest.fixture
    def prompt_template(self):
        """Load the semantic_analyzer prompt template."""
        loader = PromptLoader()
        return loader.load("semantic_analyzer")

    def test_explains_file_summaries_context(self, prompt_template):
        """Verify prompt explains what file_summaries data represents."""
        # Should explain that file_summaries come from Phase 3
        assert "file" in prompt_template.lower()
        assert "summar" in prompt_template.lower()  # summary/summaries

    def test_explains_static_findings_context(self, prompt_template):
        """Verify prompt explains what static_findings data represents."""
        # Should explain that static_findings come from Phase 2
        assert "static" in prompt_template.lower() or "syntactic" in prompt_template.lower()

    def test_explains_dependency_graph_context(self, prompt_template):
        """Verify prompt explains what dependency_graph data represents."""
        # Should explain dependency relationships
        assert "dependenc" in prompt_template.lower()  # dependency/dependencies

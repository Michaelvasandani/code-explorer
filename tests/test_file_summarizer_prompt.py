"""
Tests for file_summarizer.txt prompt template.

Per CLAUDE.md TDD workflow: Tests written BEFORE prompt template creation.
Per Architecture.md Phase 3: FileSummarizer generates structured summaries for repo-level reasoning.
"""

import pytest
from pathlib import Path
from analyzers.prompt_loader import PromptLoader


class TestFileSummarizerPromptExists:
    """Verify the file_summarizer.txt prompt template exists and is loadable."""

    def test_prompt_file_exists(self):
        """Verify prompts/file_summarizer.txt exists."""
        prompt_path = Path("prompts/file_summarizer.txt")
        assert prompt_path.exists(), "prompts/file_summarizer.txt must exist"

    def test_prompt_is_readable(self):
        """Verify prompt file can be read."""
        loader = PromptLoader()
        prompt = loader.load("file_summarizer")
        assert isinstance(prompt, str)
        assert len(prompt) > 0, "Prompt template should not be empty"


class TestFileSummarizerPromptStructure:
    """Verify the prompt template has required structure and placeholders."""

    @pytest.fixture
    def prompt_template(self):
        """Load the file_summarizer prompt template."""
        loader = PromptLoader()
        return loader.load("file_summarizer")

    def test_has_file_path_placeholder(self, prompt_template):
        """Verify prompt has {file_path} placeholder for file path substitution."""
        assert "{file_path}" in prompt_template, "Must have {file_path} placeholder"

    def test_has_file_content_placeholder(self, prompt_template):
        """Verify prompt has {file_content} placeholder for Swift code substitution."""
        assert "{file_content}" in prompt_template, "Must have {file_content} placeholder"

    def test_mentions_json_output(self, prompt_template):
        """Verify prompt instructs LLM to return JSON format."""
        prompt_lower = prompt_template.lower()
        assert "json" in prompt_lower, "Prompt must specify JSON output format"

    def test_mentions_required_fields(self, prompt_template):
        """Verify prompt specifies the required FileSummary fields."""
        # Per Architecture.md, FileSummary has: file_path, role, main_types, dependencies, responsibilities, suspicious_patterns
        assert "file_path" in prompt_template
        assert "role" in prompt_template
        assert "main_types" in prompt_template
        assert "dependencies" in prompt_template
        assert "responsibilities" in prompt_template
        assert "suspicious_patterns" in prompt_template


class TestFileSummarizerPromptRendering:
    """Verify the prompt can be rendered with variables."""

    def test_render_with_variables(self):
        """Verify prompt renders correctly with file_path and file_content variables."""
        loader = PromptLoader()

        sample_path = "Services/JournalStore.swift"
        sample_content = """import Foundation

class JournalStore {
    static let shared = JournalStore()
    private var entries: [SleepEntry] = []

    func save(_ entry: SleepEntry) {
        entries.append(entry)
    }
}"""

        rendered = loader.render(
            "file_summarizer",
            file_path=sample_path,
            file_content=sample_content
        )

        assert isinstance(rendered, str)
        assert len(rendered) > 0
        assert sample_path in rendered, "Rendered prompt should contain the file path"
        assert "JournalStore" in rendered, "Rendered prompt should contain the Swift code"
        # Verify placeholders were replaced (no curly braces remain for our variables)
        assert "{file_path}" not in rendered, "file_path placeholder should be replaced"
        assert "{file_content}" not in rendered, "file_content placeholder should be replaced"

    def test_render_handles_multiline_code(self):
        """Verify prompt handles multiline Swift code correctly."""
        loader = PromptLoader()

        multiline_code = """import UIKit
import Foundation

class ViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        // Setup code
    }
}"""

        rendered = loader.render(
            "file_summarizer",
            file_path="UI/ViewController.swift",
            file_content=multiline_code
        )

        assert "viewDidLoad" in rendered
        assert "UIViewController" in rendered


class TestFileSummarizerPromptGuidance:
    """Verify the prompt provides appropriate guidance to the LLM."""

    @pytest.fixture
    def prompt_template(self):
        """Load the file_summarizer prompt template."""
        loader = PromptLoader()
        return loader.load("file_summarizer")

    def test_instructs_grounded_analysis(self, prompt_template):
        """Verify prompt instructs LLM to base analysis on actual code, not speculation."""
        prompt_lower = prompt_template.lower()
        # Look for guidance about grounded analysis
        grounded_keywords = ["grounded", "evidence", "actual", "based on", "visible"]
        assert any(keyword in prompt_lower for keyword in grounded_keywords), \
            "Prompt should instruct grounded analysis"

    def test_mentions_swift_context(self, prompt_template):
        """Verify prompt provides Swift/iOS context."""
        prompt_lower = prompt_template.lower()
        assert "swift" in prompt_lower, "Prompt should mention Swift context"

    def test_instructs_structured_output(self, prompt_template):
        """Verify prompt asks for structured JSON output per Architecture.md schema."""
        # Should mention returning structured data
        prompt_lower = prompt_template.lower()
        assert "structure" in prompt_lower or "schema" in prompt_lower or "format" in prompt_lower, \
            "Prompt should specify structured output"


class TestFileSummarizerPromptExamples:
    """Verify the prompt includes examples for clarity."""

    @pytest.fixture
    def prompt_template(self):
        """Load the file_summarizer prompt template."""
        loader = PromptLoader()
        return loader.load("file_summarizer")

    def test_includes_example_output(self, prompt_template):
        """Verify prompt includes example JSON output for clarity."""
        # Example helps LLM understand expected format
        prompt_lower = prompt_template.lower()
        assert "example" in prompt_lower, "Prompt should include example output"

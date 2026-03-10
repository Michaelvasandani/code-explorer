"""
Test suite for PromptLoader utility.

The PromptLoader is responsible for loading and rendering LLM prompt templates
from the prompts/ directory. This is a critical infrastructure component used
by all AI analyzers (file_summarizer, semantic_analyzer, validator, question_generator).

RED PHASE: These tests should FAIL initially since PromptLoader doesn't exist yet.
"""

import pytest
from pathlib import Path
import tempfile
import shutil


class TestPromptLoaderBasicLoading:
    """Test basic prompt loading functionality."""

    def test_load_returns_prompt_content(self, tmp_path):
        """Verify load() reads and returns prompt file contents."""
        # Create a temporary prompts directory with a test prompt
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        test_prompt = prompts_dir / "test_prompt.txt"
        test_prompt.write_text("This is a test prompt.")

        # Import after setup to avoid import errors in RED phase
        from analyzers.prompt_loader import PromptLoader

        loader = PromptLoader(prompts_dir=prompts_dir)
        content = loader.load("test_prompt")

        assert content == "This is a test prompt."

    def test_load_handles_multiline_prompts(self, tmp_path):
        """Verify load() correctly handles multi-line prompt files."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        test_prompt = prompts_dir / "multiline.txt"
        test_prompt.write_text("Line 1\nLine 2\nLine 3")

        from analyzers.prompt_loader import PromptLoader

        loader = PromptLoader(prompts_dir=prompts_dir)
        content = loader.load("multiline")

        assert content == "Line 1\nLine 2\nLine 3"
        assert content.count("\n") == 2

    def test_load_raises_error_for_missing_prompt(self, tmp_path):
        """Verify load() raises FileNotFoundError for non-existent prompts."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()

        from analyzers.prompt_loader import PromptLoader

        loader = PromptLoader(prompts_dir=prompts_dir)

        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent_prompt")

    def test_load_uses_default_prompts_directory(self):
        """Verify PromptLoader uses project prompts/ dir when no path specified."""
        from analyzers.prompt_loader import PromptLoader

        loader = PromptLoader()
        # Should default to project_root/prompts/
        expected_path = Path(__file__).parent.parent / "prompts"
        assert loader.prompts_dir == expected_path


class TestPromptLoaderRendering:
    """Test prompt rendering with variable substitution."""

    def test_render_substitutes_single_variable(self, tmp_path):
        """Verify render() replaces {variable} with provided value."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        test_prompt = prompts_dir / "greeting.txt"
        test_prompt.write_text("Hello, {name}!")

        from analyzers.prompt_loader import PromptLoader

        loader = PromptLoader(prompts_dir=prompts_dir)
        rendered = loader.render("greeting", name="Alice")

        assert rendered == "Hello, Alice!"

    def test_render_substitutes_multiple_variables(self, tmp_path):
        """Verify render() replaces multiple {variables} correctly."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        test_prompt = prompts_dir / "analysis.txt"
        test_prompt.write_text("Analyze {file_path} containing {lines} lines.")

        from analyzers.prompt_loader import PromptLoader

        loader = PromptLoader(prompts_dir=prompts_dir)
        rendered = loader.render("analysis", file_path="test.swift", lines=42)

        assert rendered == "Analyze test.swift containing 42 lines."

    def test_render_handles_multiline_templates(self, tmp_path):
        """Verify render() works with multi-line templates."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        test_prompt = prompts_dir / "report.txt"
        test_prompt.write_text("File: {file}\nAuthor: {author}\nStatus: {status}")

        from analyzers.prompt_loader import PromptLoader

        loader = PromptLoader(prompts_dir=prompts_dir)
        rendered = loader.render("report", file="main.swift", author="Bob", status="reviewed")

        assert "File: main.swift" in rendered
        assert "Author: Bob" in rendered
        assert "Status: reviewed" in rendered

    def test_render_raises_error_for_missing_variables(self, tmp_path):
        """Verify render() raises KeyError when required variable not provided."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        test_prompt = prompts_dir / "template.txt"
        test_prompt.write_text("Value: {required_var}")

        from analyzers.prompt_loader import PromptLoader

        loader = PromptLoader(prompts_dir=prompts_dir)

        with pytest.raises(KeyError):
            loader.render("template")  # Missing required_var

    def test_render_ignores_extra_variables(self, tmp_path):
        """Verify render() doesn't fail when extra variables provided."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        test_prompt = prompts_dir / "simple.txt"
        test_prompt.write_text("Name: {name}")

        from analyzers.prompt_loader import PromptLoader

        loader = PromptLoader(prompts_dir=prompts_dir)
        # Provide extra variables that aren't in template
        rendered = loader.render("simple", name="Charlie", age=30, city="NYC")

        assert rendered == "Name: Charlie"


class TestPromptLoaderEdgeCases:
    """Test edge cases and error handling."""

    def test_load_handles_empty_prompt_file(self, tmp_path):
        """Verify load() correctly handles empty prompt files."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        empty_prompt = prompts_dir / "empty.txt"
        empty_prompt.write_text("")

        from analyzers.prompt_loader import PromptLoader

        loader = PromptLoader(prompts_dir=prompts_dir)
        content = loader.load("empty")

        assert content == ""

    def test_load_preserves_whitespace(self, tmp_path):
        """Verify load() preserves leading/trailing whitespace in prompts."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        whitespace_prompt = prompts_dir / "whitespace.txt"
        whitespace_prompt.write_text("  indented\n\nwith blank lines  ")

        from analyzers.prompt_loader import PromptLoader

        loader = PromptLoader(prompts_dir=prompts_dir)
        content = loader.load("whitespace")

        assert content == "  indented\n\nwith blank lines  "

    def test_loader_raises_error_for_invalid_prompts_directory(self):
        """Verify PromptLoader raises error if prompts directory doesn't exist."""
        from analyzers.prompt_loader import PromptLoader

        nonexistent_dir = Path("/nonexistent/prompts/directory")

        with pytest.raises(ValueError):
            PromptLoader(prompts_dir=nonexistent_dir)

    def test_render_with_braces_in_content(self, tmp_path):
        """Verify render() handles literal braces in template correctly."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        test_prompt = prompts_dir / "braces.txt"
        # Use {{ and }} to escape braces in format strings
        test_prompt.write_text("Code: {{example}} Variable: {var}")

        from analyzers.prompt_loader import PromptLoader

        loader = PromptLoader(prompts_dir=prompts_dir)
        rendered = loader.render("braces", var="value")

        assert rendered == "Code: {example} Variable: value"

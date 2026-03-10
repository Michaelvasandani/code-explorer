"""
Tests for question_generator.txt prompt template.

Per CLAUDE.md TDD workflow: Tests written BEFORE prompt template creation.
Per Architecture.md Phase 6: QuestionGenerator synthesizes onboarding questions from validated findings.
"""

import pytest
from pathlib import Path
from analyzers.prompt_loader import PromptLoader


class TestQuestionGeneratorPromptExists:
    """Verify the question_generator.txt prompt template exists and is loadable."""

    def test_prompt_file_exists(self):
        """Verify prompts/question_generator.txt exists."""
        prompt_path = Path("prompts/question_generator.txt")
        assert prompt_path.exists(), "prompts/question_generator.txt must exist"

    def test_prompt_is_readable(self):
        """Verify prompt file can be loaded via PromptLoader."""
        loader = PromptLoader()
        prompt = loader.load("question_generator")
        assert isinstance(prompt, str)
        assert len(prompt) > 0, "Prompt template should not be empty"


class TestQuestionGeneratorPromptStructure:
    """Verify the prompt template has required structure and placeholders."""

    @pytest.fixture
    def prompt_template(self):
        """Load the question_generator prompt template."""
        loader = PromptLoader()
        return loader.load("question_generator")

    def test_has_validated_findings_placeholder(self, prompt_template):
        """Verify prompt has {validated_findings} placeholder."""
        assert "{validated_findings}" in prompt_template, "Must have {validated_findings} placeholder"

    def test_mentions_json_output(self, prompt_template):
        """Verify prompt instructs LLM to return JSON format."""
        prompt_lower = prompt_template.lower()
        assert "json" in prompt_lower, "Prompt must specify JSON output format"

    def test_mentions_questions_field(self, prompt_template):
        """Verify prompt specifies the questions field in output."""
        assert "questions" in prompt_template.lower(), "Prompt must mention questions field"


class TestQuestionGeneratorPromptRendering:
    """Verify the prompt can be rendered with variables."""

    def test_render_with_variables(self):
        """Verify prompt renders correctly with validated_findings."""
        loader = PromptLoader()

        sample_findings = '[{{"type": "bug", "description": "Missing error handling"}}]'

        rendered = loader.render(
            "question_generator",
            validated_findings=sample_findings
        )

        assert isinstance(rendered, str)
        assert len(rendered) > 0
        assert "Missing error handling" in rendered, "Rendered prompt should contain the findings"
        assert "{validated_findings}" not in rendered, "Placeholder should be replaced"


class TestQuestionGeneratorPromptGuidance:
    """Verify the prompt provides appropriate guidance to the LLM."""

    @pytest.fixture
    def prompt_template(self):
        """Load the question_generator prompt template."""
        loader = PromptLoader()
        return loader.load("question_generator")

    def test_instructs_onboarding_focus(self, prompt_template):
        """Verify prompt instructs LLM to generate onboarding questions."""
        prompt_lower = prompt_template.lower()
        onboarding_keywords = ["onboarding", "onboard", "understand", "learn", "familiarize"]
        assert any(keyword in prompt_lower for keyword in onboarding_keywords), \
            "Prompt should focus on onboarding questions"

    def test_instructs_actionable_questions(self, prompt_template):
        """Verify prompt asks for actionable, specific questions."""
        prompt_lower = prompt_template.lower()
        actionable_keywords = ["actionable", "specific", "concrete", "clear"]
        assert any(keyword in prompt_lower for keyword in actionable_keywords), \
            "Prompt should ask for actionable questions"

    def test_mentions_question_types(self, prompt_template):
        """Verify prompt mentions types of questions to generate."""
        prompt_lower = prompt_template.lower()
        # Should mention what kinds of questions to ask
        question_keywords = ["why", "how", "what", "who", "when", "where"]
        assert any(keyword in prompt_lower for keyword in question_keywords), \
            "Prompt should guide question types"

    def test_instructs_findings_synthesis(self, prompt_template):
        """Verify prompt instructs LLM to synthesize questions from findings."""
        prompt_lower = prompt_template.lower()
        synthesis_keywords = ["synthesize", "based on", "from", "findings", "issues"]
        assert any(keyword in prompt_lower for keyword in synthesis_keywords), \
            "Prompt should instruct synthesis from findings"


class TestQuestionGeneratorPromptExamples:
    """Verify the prompt includes examples for clarity."""

    @pytest.fixture
    def prompt_template(self):
        """Load the question_generator prompt template."""
        loader = PromptLoader()
        return loader.load("question_generator")

    def test_includes_example_output(self, prompt_template):
        """Verify prompt includes example JSON output for clarity."""
        prompt_lower = prompt_template.lower()
        assert "example" in prompt_lower, "Prompt should include example output"

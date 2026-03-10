"""
Tests for validator.txt prompt template.

Per CLAUDE.md TDD workflow: Tests written BEFORE prompt template creation.
Per Architecture.md Phase 5: Single context-aware validator validates all finding types.
"""

import pytest
from pathlib import Path
from analyzers.prompt_loader import PromptLoader


class TestValidatorPromptExists:
    """Verify the validator.txt prompt template exists and is loadable."""

    def test_prompt_file_exists(self):
        """Verify prompts/validator.txt exists."""
        prompt_path = Path("prompts/validator.txt")
        assert prompt_path.exists(), "prompts/validator.txt must exist"

    def test_prompt_is_readable(self):
        """Verify prompt file can be loaded via PromptLoader."""
        loader = PromptLoader()
        prompt = loader.load("validator")
        assert isinstance(prompt, str)
        assert len(prompt) > 0, "Prompt template should not be empty"


class TestValidatorPromptStructure:
    """Verify the prompt template has required structure and placeholders."""

    @pytest.fixture
    def prompt_template(self):
        """Load the validator prompt template."""
        loader = PromptLoader()
        return loader.load("validator")

    def test_has_finding_placeholder(self, prompt_template):
        """Verify prompt has {finding} placeholder for the finding to validate."""
        assert "{finding}" in prompt_template, "Must have {finding} placeholder"

    def test_has_finding_type_placeholder(self, prompt_template):
        """Verify prompt has {finding_type} placeholder for context-aware reasoning."""
        assert "{finding_type}" in prompt_template, "Must have {finding_type} placeholder"

    def test_mentions_json_output(self, prompt_template):
        """Verify prompt instructs LLM to return JSON format."""
        prompt_lower = prompt_template.lower()
        assert "json" in prompt_lower, "Prompt must specify JSON output format"

    def test_mentions_required_fields(self, prompt_template):
        """Verify prompt specifies the required ValidationResult fields."""
        # Per Architecture.md, ValidationResult has: is_valid, confidence, reasoning, keep_finding
        assert "is_valid" in prompt_template
        assert "confidence" in prompt_template
        assert "reasoning" in prompt_template


class TestValidatorPromptRendering:
    """Verify the prompt can be rendered with variables."""

    def test_render_with_variables(self):
        """Verify prompt renders correctly with finding and finding_type."""
        loader = PromptLoader()

        sample_finding = """{
  "type": "bug",
  "severity": "high",
  "description": "Missing error handling"
}"""
        finding_type = "bug"

        rendered = loader.render(
            "validator",
            finding=sample_finding,
            finding_type=finding_type
        )

        assert isinstance(rendered, str)
        assert len(rendered) > 0
        assert "bug" in rendered, "Rendered prompt should contain the finding type"
        assert "Missing error handling" in rendered, "Rendered prompt should contain finding description"
        # Verify placeholders were replaced
        assert "{finding}" not in rendered
        assert "{finding_type}" not in rendered


class TestValidatorPromptGuidance:
    """Verify the prompt provides appropriate guidance to the LLM."""

    @pytest.fixture
    def prompt_template(self):
        """Load the validator prompt template."""
        loader = PromptLoader()
        return loader.load("validator")

    def test_instructs_context_aware_validation(self, prompt_template):
        """Verify prompt instructs LLM to adapt reasoning based on finding type."""
        prompt_lower = prompt_template.lower()
        # Should mention adapting or context-aware validation
        context_keywords = ["context", "type", "adapt", "based on", "depends on"]
        assert any(keyword in prompt_lower for keyword in context_keywords), \
            "Prompt should instruct context-aware validation"

    def test_mentions_validation_criteria(self, prompt_template):
        """Verify prompt defines validation criteria."""
        prompt_lower = prompt_template.lower()
        # Should mention what makes a finding valid
        validation_keywords = ["valid", "grounded", "evidence", "accurate", "verify"]
        assert any(keyword in prompt_lower for keyword in validation_keywords), \
            "Prompt should define validation criteria"

    def test_mentions_confidence_levels(self, prompt_template):
        """Verify prompt defines confidence levels."""
        prompt_lower = prompt_template.lower()
        assert "confidence" in prompt_lower
        # Common confidence levels
        confidence_keywords = ["high", "medium", "low", "certain"]
        assert any(keyword in prompt_lower for keyword in confidence_keywords), \
            "Prompt should define confidence levels"

    def test_instructs_reasoning_explanation(self, prompt_template):
        """Verify prompt asks for reasoning explanation."""
        prompt_lower = prompt_template.lower()
        reasoning_keywords = ["reasoning", "explain", "why", "rationale", "because"]
        assert any(keyword in prompt_lower for keyword in reasoning_keywords), \
            "Prompt should ask for reasoning explanation"

    def test_mentions_false_positive_detection(self, prompt_template):
        """Verify prompt addresses false positive detection."""
        prompt_lower = prompt_template.lower()
        # Should mention filtering false positives
        fp_keywords = ["false positive", "incorrect", "invalid", "wrong", "hallucination"]
        assert any(keyword in prompt_lower for keyword in fp_keywords), \
            "Prompt should address false positive detection"


class TestValidatorPromptExamples:
    """Verify the prompt includes examples for clarity."""

    @pytest.fixture
    def prompt_template(self):
        """Load the validator prompt template."""
        loader = PromptLoader()
        return loader.load("validator")

    def test_includes_example_output(self, prompt_template):
        """Verify prompt includes example JSON output for clarity."""
        prompt_lower = prompt_template.lower()
        assert "example" in prompt_lower, "Prompt should include example output"


class TestValidatorPromptTypeSpecific:
    """Verify the prompt provides type-specific validation guidance."""

    @pytest.fixture
    def prompt_template(self):
        """Load the validator prompt template."""
        loader = PromptLoader()
        return loader.load("validator")

    def test_mentions_bug_validation(self, prompt_template):
        """Verify prompt mentions bug-specific validation criteria."""
        prompt_lower = prompt_template.lower()
        assert "bug" in prompt_lower, "Prompt should mention bug validation"

    def test_mentions_architecture_validation(self, prompt_template):
        """Verify prompt mentions architecture issue validation criteria."""
        prompt_lower = prompt_template.lower()
        assert "architecture" in prompt_lower, "Prompt should mention architecture validation"

    def test_mentions_evidence_requirement(self, prompt_template):
        """Verify prompt requires evidence for findings."""
        prompt_lower = prompt_template.lower()
        assert "evidence" in prompt_lower, "Prompt should require evidence for validation"

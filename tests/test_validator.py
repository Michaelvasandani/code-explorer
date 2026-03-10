"""
Tests for validator.py - Phase 5 AI-powered validation.

Per CLAUDE.md TDD workflow: Tests written BEFORE implementation.
Per Architecture.md Phase 5: Single context-aware validator validates all finding types.
"""

import pytest
import json
from unittest.mock import Mock, patch


class TestValidationResultDataclass:
    """Verify the ValidationResult dataclass structure."""

    def test_validation_result_has_required_fields(self):
        """Verify ValidationResult dataclass has all required fields per Architecture.md."""
        from analyzers.validator import ValidationResult

        result = ValidationResult(
            is_valid=True,
            confidence=0.9,
            reasoning="The finding is well-grounded with concrete evidence"
        )

        assert result.is_valid is True
        assert result.confidence == 0.9
        assert result.reasoning == "The finding is well-grounded with concrete evidence"


class TestValidatorInitialization:
    """Verify Validator initialization and configuration."""

    def test_validator_initializes_with_api_key(self):
        """Verify Validator can be initialized with OpenAI API key."""
        from analyzers.validator import Validator

        validator = Validator(api_key="test-key")
        assert validator is not None

    def test_validator_raises_error_without_api_key(self):
        """Verify Validator raises error if no API key provided."""
        from analyzers.validator import Validator

        with pytest.raises(ValueError, match="API key"):
            Validator(api_key=None)

    def test_validator_loads_prompt_template(self):
        """Verify Validator loads validator.txt on initialization."""
        from analyzers.validator import Validator

        validator = Validator(api_key="test-key")
        # Should have loaded the prompt template
        assert hasattr(validator, 'prompt_loader')


class TestValidatorValidation:
    """Verify Validator.validate() method."""

    @pytest.fixture
    def mock_openai_response_valid(self):
        """Mock OpenAI API response for valid finding."""
        return {
            "is_valid": True,
            "confidence": 0.95,
            "reasoning": "Strong evidence from static analysis. Force try causes crashes on errors."
        }

    @pytest.fixture
    def mock_openai_response_invalid(self):
        """Mock OpenAI API response for invalid finding."""
        return {
            "is_valid": False,
            "confidence": 0.7,
            "reasoning": "UserDefaults is typically not unit tested directly. This appears to be a false positive."
        }

    @patch('analyzers.validator.OpenAI')
    def test_validate_returns_validation_result(self, mock_openai_class, mock_openai_response_valid):
        """Verify validate() returns ValidationResult dataclass."""
        from analyzers.validator import Validator
        from analyzers.semantic_analyzer import SemanticFinding

        # Mock OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock chat completion response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_openai_response_valid)
        mock_client.chat.completions.create.return_value = mock_response

        validator = Validator(api_key="test-key")

        finding = SemanticFinding(
            type="bug",
            subtype="missing_error_handling",
            severity="high",
            location="Network.swift:1",
            description="Missing error handling",
            evidence="Force try statements",
            recommendation="Add do-catch"
        ,
            confidence="high"
        )

        result = validator.validate(finding)

        assert result.is_valid is True
        assert result.confidence == 0.95
        assert "Force try" in result.reasoning

    @patch('analyzers.validator.OpenAI')
    def test_validate_calls_openai_with_rendered_prompt(self, mock_openai_class):
        """Verify validate() calls OpenAI API with rendered prompt containing finding."""
        from analyzers.validator import Validator
        from analyzers.semantic_analyzer import SemanticFinding

        # Mock OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "is_valid": True,
            "confidence": 0.8,
            "reasoning": "Valid"
        })
        mock_client.chat.completions.create.return_value = mock_response

        validator = Validator(api_key="test-key")

        finding = SemanticFinding(
            type="bug",
            subtype="test",
            severity="high",
            location="Test.swift:1",
            description="Test issue",
            evidence="Test evidence",
            recommendation="Fix it"
        ,
            confidence="high"
        )

        validator.validate(finding)

        # Verify OpenAI was called
        mock_client.chat.completions.create.assert_called_once()

        # Verify the prompt contains finding data
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs['messages']
        user_message = messages[0]['content']

        assert "Test issue" in user_message
        assert "bug" in user_message

    @patch('analyzers.validator.OpenAI')
    def test_validate_uses_gpt_4(self, mock_openai_class):
        """Verify validate() uses GPT-4 model for validation."""
        from analyzers.validator import Validator
        from analyzers.semantic_analyzer import SemanticFinding

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "is_valid": True,
            "confidence": 0.8,
            "reasoning": "Valid"
        })
        mock_client.chat.completions.create.return_value = mock_response

        validator = Validator(api_key="test-key")
        finding = SemanticFinding(
            type="bug",
            subtype="test",
            severity="high",
            location="Test.swift:1",
            description="Test",
            evidence="Evidence",
            recommendation="Fix"
        ,
            confidence="high"
        )

        validator.validate(finding)

        call_args = mock_client.chat.completions.create.call_args
        model = call_args.kwargs['model']

        # Should use GPT-4 for validation
        assert "gpt-4" in model.lower() or "gpt-4o" in model.lower()

    @patch('analyzers.validator.OpenAI')
    def test_validate_handles_invalid_finding(self, mock_openai_class, mock_openai_response_invalid):
        """Verify validate() correctly handles findings marked as invalid."""
        from analyzers.validator import Validator
        from analyzers.semantic_analyzer import SemanticFinding

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_openai_response_invalid)
        mock_client.chat.completions.create.return_value = mock_response

        validator = Validator(api_key="test-key")

        finding = SemanticFinding(
            type="test_gap",
            subtype="missing_tests",
            severity="medium",
            location="Settings.swift:1",
            description="Missing tests",
            evidence="No test files",
            recommendation="Add tests"
        ,
            confidence="medium"
        )

        result = validator.validate(finding)

        assert result.is_valid is False
        assert result.confidence == 0.7
        assert "false positive" in result.reasoning.lower()


class TestValidatorBatchValidation:
    """Verify Validator.validate_all() batch processing."""

    @patch('analyzers.validator.OpenAI')
    def test_validate_all_processes_multiple_findings(self, mock_openai_class):
        """Verify validate_all() processes multiple SemanticFinding objects."""
        from analyzers.validator import Validator
        from analyzers.semantic_analyzer import SemanticFinding

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock responses for each finding
        def create_response(is_valid):
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "is_valid": is_valid,
                "confidence": 0.9,
                "reasoning": "Test reasoning"
            })
            return mock_response

        mock_client.chat.completions.create.side_effect = [
            create_response(True),
            create_response(False)
        ]

        validator = Validator(api_key="test-key")

        findings = [
            SemanticFinding(
                type="bug",
                subtype="test1",
                severity="high",
                location="F1.swift:1",
                description="D1",
                evidence="E1",
                recommendation="R1"
            ,
            confidence="high"
        ),
            SemanticFinding(
                type="test_gap",
                subtype="test2",
                severity="low",
                location="F2.swift:1",
                description="D2",
                evidence="E2",
                recommendation="R2"
            ,
            confidence="low"
        )
        ]

        results = validator.validate_all(findings)

        assert len(results) == 2
        assert results[0].is_valid is True
        assert results[1].is_valid is False

    @patch('analyzers.validator.OpenAI')
    def test_validate_all_returns_empty_list_for_no_findings(self, mock_openai_class):
        """Verify validate_all() returns empty list when given no findings."""
        from analyzers.validator import Validator

        validator = Validator(api_key="test-key")
        results = validator.validate_all([])

        assert results == []
        # Should not call OpenAI for empty list
        mock_openai_class.return_value.chat.completions.create.assert_not_called()

    @patch('analyzers.validator.OpenAI')
    def test_validate_all_filters_invalid_findings(self, mock_openai_class):
        """Verify validate_all() can filter out invalid findings when requested."""
        from analyzers.validator import Validator
        from analyzers.semantic_analyzer import SemanticFinding

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock responses: first valid, second invalid
        def create_response(is_valid):
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "is_valid": is_valid,
                "confidence": 0.9,
                "reasoning": "Test"
            })
            return mock_response

        mock_client.chat.completions.create.side_effect = [
            create_response(True),
            create_response(False)
        ]

        validator = Validator(api_key="test-key")

        findings = [
            SemanticFinding(
                type="bug",
                subtype="test1",
                severity="high",
                location="F1.swift:1",
                description="D1",
                evidence="E1",
                recommendation="R1"
            ,
            confidence="high"
        ),
            SemanticFinding(
                type="bug",
                subtype="test2",
                severity="high",
                location="F2.swift:1",
                description="D2",
                evidence="E2",
                recommendation="R2"
            ,
            confidence="high"
        )
        ]

        # Get only validated findings
        validated_findings = validator.get_validated_findings(findings)

        # Should only return the first finding (marked as valid)
        assert len(validated_findings) == 1
        assert validated_findings[0].description == "D1"


class TestValidatorErrorHandling:
    """Verify Validator error handling."""

    @patch('analyzers.validator.OpenAI')
    def test_validate_handles_invalid_json_response(self, mock_openai_class):
        """Verify validate() handles malformed JSON from LLM gracefully."""
        from analyzers.validator import Validator
        from analyzers.semantic_analyzer import SemanticFinding

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # LLM returns invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON"
        mock_client.chat.completions.create.return_value = mock_response

        validator = Validator(api_key="test-key")
        finding = SemanticFinding(
            type="bug",
            subtype="test",
            severity="high",
            location="Test.swift:1",
            description="Test",
            evidence="Evidence",
            recommendation="Fix"
        ,
            confidence="high"
        )

        with pytest.raises(ValueError, match="JSON"):
            validator.validate(finding)

    @patch('analyzers.validator.OpenAI')
    def test_validate_handles_missing_required_fields(self, mock_openai_class):
        """Verify validate() handles JSON missing required fields."""
        from analyzers.validator import Validator
        from analyzers.semantic_analyzer import SemanticFinding

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # LLM returns incomplete JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "is_valid": True
            # Missing: confidence, reasoning
        })
        mock_client.chat.completions.create.return_value = mock_response

        validator = Validator(api_key="test-key")
        finding = SemanticFinding(
            type="bug",
            subtype="test",
            severity="high",
            location="Test.swift:1",
            description="Test",
            evidence="Evidence",
            recommendation="Fix"
        ,
            confidence="high"
        )

        with pytest.raises(ValueError, match="required field"):
            validator.validate(finding)

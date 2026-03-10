"""
Tests for question_generator.py - Phase 6 AI-powered question generation.

Per CLAUDE.md TDD workflow: Tests written BEFORE implementation.
Per Architecture.md Phase 6: QuestionGenerator synthesizes onboarding questions from validated findings.
"""

import pytest
import json
from unittest.mock import Mock, patch


class TestQuestionGeneratorInitialization:
    """Verify QuestionGenerator initialization and configuration."""

    def test_question_generator_initializes_with_api_key(self):
        """Verify QuestionGenerator can be initialized with OpenAI API key."""
        from analyzers.question_generator import QuestionGenerator

        generator = QuestionGenerator(api_key="test-key")
        assert generator is not None

    def test_question_generator_raises_error_without_api_key(self):
        """Verify QuestionGenerator raises error if no API key provided."""
        from analyzers.question_generator import QuestionGenerator

        with pytest.raises(ValueError, match="API key"):
            QuestionGenerator(api_key=None)

    def test_question_generator_loads_prompt_template(self):
        """Verify QuestionGenerator loads question_generator.txt on initialization."""
        from analyzers.question_generator import QuestionGenerator

        generator = QuestionGenerator(api_key="test-key")
        # Should have loaded the prompt template
        assert hasattr(generator, 'prompt_loader')


class TestQuestionGeneratorGeneration:
    """Verify QuestionGenerator.generate() method."""

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response with questions."""
        return {
            "questions": [
                "What's the intended pattern for dependency injection in this codebase?",
                "How should we handle errors in network and persistence operations?",
                "Where are the critical code paths that need test coverage?"
            ]
        }

    @patch('analyzers.question_generator.OpenAI')
    def test_generate_returns_list_of_questions(self, mock_openai_class, mock_openai_response):
        """Verify generate() returns list of question strings."""
        from analyzers.question_generator import QuestionGenerator
        from analyzers.semantic_analyzer import SemanticFinding

        # Mock OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock chat completion response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_openai_response)
        mock_client.chat.completions.create.return_value = mock_response

        generator = QuestionGenerator(api_key="test-key")

        validated_findings = [
            SemanticFinding(
                type="bug",
                subtype="missing_error_handling",
                severity="high",
                location="Network.swift:1",
                explanation="Missing error handling",
                evidence="Force try statements",
                recommendation="Add do-catch",
                confidence="high"
            )
        ]

        questions = generator.generate(validated_findings)

        assert isinstance(questions, list)
        assert len(questions) == 3
        assert "dependency injection" in questions[0]
        assert "error" in questions[1]

    @patch('analyzers.question_generator.OpenAI')
    def test_generate_calls_openai_with_rendered_prompt(self, mock_openai_class):
        """Verify generate() calls OpenAI API with rendered prompt containing findings."""
        from analyzers.question_generator import QuestionGenerator
        from analyzers.semantic_analyzer import SemanticFinding

        # Mock OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({"questions": ["Test question?"]})
        mock_client.chat.completions.create.return_value = mock_response

        generator = QuestionGenerator(api_key="test-key")

        validated_findings = [
            SemanticFinding(
                type="bug",
                subtype="test",
                severity="high",
                location="Test.swift:1",
                explanation="Test issue",
                evidence="Test evidence",
                recommendation="Fix it",
                confidence="high"
            )
        ]

        generator.generate(validated_findings)

        # Verify OpenAI was called
        mock_client.chat.completions.create.assert_called_once()

        # Verify the prompt contains finding data
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs['messages']
        user_message = messages[0]['content']

        assert "Test issue" in user_message

    @patch('analyzers.question_generator.OpenAI')
    def test_generate_uses_gpt_4(self, mock_openai_class):
        """Verify generate() uses GPT-4 model for question generation."""
        from analyzers.question_generator import QuestionGenerator

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({"questions": []})
        mock_client.chat.completions.create.return_value = mock_response

        generator = QuestionGenerator(api_key="test-key")
        generator.generate([])

        call_args = mock_client.chat.completions.create.call_args
        model = call_args.kwargs['model']

        # Should use GPT-4 for question synthesis
        assert "gpt-4" in model.lower() or "gpt-4o" in model.lower()

    @patch('analyzers.question_generator.OpenAI')
    def test_generate_handles_empty_findings(self, mock_openai_class):
        """Verify generate() handles empty findings list gracefully."""
        from analyzers.question_generator import QuestionGenerator

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "questions": ["What's the overall architecture of this codebase?"]
        })
        mock_client.chat.completions.create.return_value = mock_response

        generator = QuestionGenerator(api_key="test-key")
        questions = generator.generate([])

        assert isinstance(questions, list)
        assert len(questions) > 0


class TestQuestionGeneratorErrorHandling:
    """Verify QuestionGenerator error handling."""

    @patch('analyzers.question_generator.OpenAI')
    def test_generate_handles_invalid_json_response(self, mock_openai_class):
        """Verify generate() handles malformed JSON from LLM gracefully."""
        from analyzers.question_generator import QuestionGenerator

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # LLM returns invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON"
        mock_client.chat.completions.create.return_value = mock_response

        generator = QuestionGenerator(api_key="test-key")

        with pytest.raises(ValueError, match="JSON"):
            generator.generate([])

    @patch('analyzers.question_generator.OpenAI')
    def test_generate_handles_missing_questions_field(self, mock_openai_class):
        """Verify generate() handles JSON missing questions field."""
        from analyzers.question_generator import QuestionGenerator

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # LLM returns incomplete JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "other_field": "value"
            # Missing: questions
        })
        mock_client.chat.completions.create.return_value = mock_response

        generator = QuestionGenerator(api_key="test-key")

        with pytest.raises(ValueError, match="questions"):
            generator.generate([])

    @patch('analyzers.question_generator.OpenAI')
    def test_generate_handles_non_list_questions(self, mock_openai_class):
        """Verify generate() handles questions field that is not a list."""
        from analyzers.question_generator import QuestionGenerator

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # LLM returns questions as string instead of list
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "questions": "This should be a list"
        })
        mock_client.chat.completions.create.return_value = mock_response

        generator = QuestionGenerator(api_key="test-key")

        with pytest.raises(ValueError, match="list"):
            generator.generate([])


class TestQuestionGeneratorDataSerialization:
    """Verify QuestionGenerator correctly serializes findings to JSON."""

    @patch('analyzers.question_generator.OpenAI')
    def test_generate_serializes_findings_to_json(self, mock_openai_class):
        """Verify generate() converts SemanticFinding objects to JSON for prompt."""
        from analyzers.question_generator import QuestionGenerator
        from analyzers.semantic_analyzer import SemanticFinding

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({"questions": ["Test?"]})
        mock_client.chat.completions.create.return_value = mock_response

        generator = QuestionGenerator(api_key="test-key")

        findings = [
            SemanticFinding(
                type="architecture_issue",
                subtype="circular_dependency",
                severity="medium",
                location="Store.swift:1",
                explanation="Circular dependency",
                evidence="Import analysis",
                recommendation="Extract protocol",
                confidence="medium"
            )
        ]

        generator.generate(findings)

        # Verify prompt contains serialized data
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs['messages']
        user_message = messages[0]['content']

        assert "Circular dependency" in user_message
        assert "architecture_issue" in user_message

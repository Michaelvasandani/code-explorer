"""
Tests for semantic_analyzer.py - Phase 4 AI-powered semantic analysis.

Per CLAUDE.md TDD workflow: Tests written BEFORE implementation.
Per Architecture.md Phase 4: SemanticAnalyzer detects repo-level issues using LLM.
"""

import pytest
import json
from unittest.mock import Mock, patch
from pathlib import Path


class TestSemanticFindingDataclass:
    """Verify the SemanticFinding dataclass structure."""

    def test_semantic_finding_has_required_fields(self):
        """Verify SemanticFinding dataclass has all required fields per Architecture.md."""
        from analyzers.semantic_analyzer import SemanticFinding

        finding = SemanticFinding(
            type="bug",
            location="Services/NetworkService.swift:1",
            explanation="Network operations lack error handling",
            confidence="high",
            subtype="missing_error_handling",
            severity="high",
            evidence="Static findings show 2 force try statements",
            recommendation="Replace try! with proper do-catch blocks"
        )

        assert finding.type == "bug"
        assert finding.subtype == "missing_error_handling"
        assert finding.severity == "high"
        assert finding.files == ["Services/NetworkService.swift"]
        assert finding.description == "Network operations lack error handling"
        assert finding.evidence == "Static findings show 2 force try statements"
        assert finding.recommendation == "Replace try! with proper do-catch blocks"


class TestSemanticAnalyzerInitialization:
    """Verify SemanticAnalyzer initialization and configuration."""

    def test_semantic_analyzer_initializes_with_api_key(self):
        """Verify SemanticAnalyzer can be initialized with OpenAI API key."""
        from analyzers.semantic_analyzer import SemanticAnalyzer

        analyzer = SemanticAnalyzer(api_key="test-key")
        assert analyzer is not None

    def test_semantic_analyzer_raises_error_without_api_key(self):
        """Verify SemanticAnalyzer raises error if no API key provided."""
        from analyzers.semantic_analyzer import SemanticAnalyzer

        with pytest.raises(ValueError, match="API key"):
            SemanticAnalyzer(api_key=None)

    def test_semantic_analyzer_loads_prompt_template(self):
        """Verify SemanticAnalyzer loads semantic_analyzer.txt on initialization."""
        from analyzers.semantic_analyzer import SemanticAnalyzer

        analyzer = SemanticAnalyzer(api_key="test-key")
        # Should have loaded the prompt template
        assert hasattr(analyzer, 'prompt_loader')


class TestSemanticAnalyzerAnalysis:
    """Verify SemanticAnalyzer.analyze() method."""

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response with valid JSON."""
        return [
            {
                "type": "architecture_issue",
                "subtype": "circular_dependency",
                "severity": "medium",
                "files": ["Services/JournalStore.swift", "Models/SleepEntry.swift"],
                "description": "Circular dependency between JournalStore and SleepEntry",
                "evidence": "JournalStore imports SleepEntry, and SleepEntry accesses JournalStore.shared",
                "recommendation": "Extract a protocol (e.g., EntryStorage) and use dependency injection"
            },
            {
                "type": "test_gap",
                "subtype": "singleton_testability",
                "severity": "medium",
                "files": ["Services/JournalStore.swift"],
                "description": "JournalStore singleton makes unit testing difficult",
                "evidence": "Static finding: singleton pattern (line 3)",
                "recommendation": "Add dependency injection instead of using .shared"
            }
        ]

    @patch('analyzers.semantic_analyzer.OpenAI')
    def test_analyze_returns_list_of_semantic_findings(self, mock_openai_class, mock_openai_response):
        """Verify analyze() returns list of SemanticFinding objects."""
        from analyzers.semantic_analyzer import SemanticAnalyzer

        # Mock OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock chat completion response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_openai_response)
        mock_client.chat.completions.create.return_value = mock_response

        analyzer = SemanticAnalyzer(api_key="test-key")

        # Create sample input data
        file_summaries = [{"file_path": "Store.swift", "role": "service"}]
        static_findings = [{"type": "crash_risk", "file": "Store.swift"}]
        dependency_graph = {"Store.swift": ["Foundation"]}

        findings = analyzer.analyze(file_summaries, static_findings, dependency_graph)

        assert len(findings) == 2
        assert findings[0].type == "architecture_issue"
        assert findings[0].subtype == "circular_dependency"
        assert findings[1].type == "test_gap"

    @patch('analyzers.semantic_analyzer.OpenAI')
    def test_analyze_calls_openai_with_rendered_prompt(self, mock_openai_class):
        """Verify analyze() calls OpenAI API with rendered prompt containing Phase 1-3 data."""
        from analyzers.semantic_analyzer import SemanticAnalyzer

        # Mock OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps([])
        mock_client.chat.completions.create.return_value = mock_response

        analyzer = SemanticAnalyzer(api_key="test-key")

        file_summaries = [{"file_path": "Test.swift"}]
        static_findings = [{"type": "crash_risk"}]
        dependency_graph = {"Test.swift": []}

        analyzer.analyze(file_summaries, static_findings, dependency_graph)

        # Verify OpenAI was called
        mock_client.chat.completions.create.assert_called_once()

        # Verify the prompt contains input data
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs['messages']
        user_message = messages[0]['content']

        assert "Test.swift" in user_message

    @patch('analyzers.semantic_analyzer.OpenAI')
    def test_analyze_uses_gpt_4(self, mock_openai_class):
        """Verify analyze() uses GPT-4 model for semantic analysis."""
        from analyzers.semantic_analyzer import SemanticAnalyzer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps([])
        mock_client.chat.completions.create.return_value = mock_response

        analyzer = SemanticAnalyzer(api_key="test-key")
        analyzer.analyze([], [], {})

        call_args = mock_client.chat.completions.create.call_args
        model = call_args.kwargs['model']

        # Should use GPT-4 for complex semantic analysis
        assert "gpt-4" in model.lower() or "gpt-4o" in model.lower()

    @patch('analyzers.semantic_analyzer.OpenAI')
    def test_analyze_parses_json_array_response(self, mock_openai_class):
        """Verify analyze() correctly parses JSON array from LLM response."""
        from analyzers.semantic_analyzer import SemanticAnalyzer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        json_response = [
            {
                "type": "bug",
                "subtype": "missing_error_handling",
                "severity": "high",
                "files": ["Network.swift"],
                "description": "Missing error handling",
                "evidence": "Force try statements",
                "recommendation": "Add do-catch"
            }
        ]

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(json_response)
        mock_client.chat.completions.create.return_value = mock_response

        analyzer = SemanticAnalyzer(api_key="test-key")
        findings = analyzer.analyze([], [], {})

        assert len(findings) == 1
        assert findings[0].type == "bug"
        assert findings[0].severity == "high"

    @patch('analyzers.semantic_analyzer.OpenAI')
    def test_analyze_returns_empty_list_when_no_issues_found(self, mock_openai_class):
        """Verify analyze() returns empty list when LLM finds no issues."""
        from analyzers.semantic_analyzer import SemanticAnalyzer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps([])
        mock_client.chat.completions.create.return_value = mock_response

        analyzer = SemanticAnalyzer(api_key="test-key")
        findings = analyzer.analyze([], [], {})

        assert findings == []


class TestSemanticAnalyzerErrorHandling:
    """Verify SemanticAnalyzer error handling."""

    @patch('analyzers.semantic_analyzer.OpenAI')
    def test_analyze_handles_invalid_json_response(self, mock_openai_class):
        """Verify analyze() handles malformed JSON from LLM gracefully."""
        from analyzers.semantic_analyzer import SemanticAnalyzer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # LLM returns invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON"
        mock_client.chat.completions.create.return_value = mock_response

        analyzer = SemanticAnalyzer(api_key="test-key")

        with pytest.raises(ValueError, match="JSON"):
            analyzer.analyze([], [], {})

    @patch('analyzers.semantic_analyzer.OpenAI')
    def test_analyze_handles_missing_required_fields(self, mock_openai_class):
        """Verify analyze() handles JSON missing required fields."""
        from analyzers.semantic_analyzer import SemanticAnalyzer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # LLM returns incomplete JSON (missing required fields)
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps([
            {
                "type": "bug",
                "severity": "high"
                # Missing: subtype, files, description, evidence, recommendation
            }
        ])
        mock_client.chat.completions.create.return_value = mock_response

        analyzer = SemanticAnalyzer(api_key="test-key")

        with pytest.raises(ValueError, match="required field"):
            analyzer.analyze([], [], {})

    @patch('analyzers.semantic_analyzer.OpenAI')
    def test_analyze_handles_openai_api_error(self, mock_openai_class):
        """Verify analyze() handles OpenAI API errors gracefully."""
        from analyzers.semantic_analyzer import SemanticAnalyzer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Simulate API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        analyzer = SemanticAnalyzer(api_key="test-key")

        with pytest.raises(Exception, match="API Error"):
            analyzer.analyze([], [], {})


class TestSemanticAnalyzerDataSerialization:
    """Verify SemanticAnalyzer correctly serializes input data to JSON."""

    @patch('analyzers.semantic_analyzer.OpenAI')
    def test_analyze_serializes_file_summaries_to_json(self, mock_openai_class):
        """Verify analyze() converts file_summaries list to JSON string for prompt."""
        from analyzers.semantic_analyzer import SemanticAnalyzer
        from analyzers.file_summarizer import FileSummary

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps([])
        mock_client.chat.completions.create.return_value = mock_response

        analyzer = SemanticAnalyzer(api_key="test-key")

        # Pass FileSummary objects
        summaries = [
            FileSummary(
                file_path="Test.swift",
                role="test",
                main_types=["TestClass"],
                dependencies=["Foundation"],
                responsibilities=["testing"],
                suspicious_patterns=[]
            )
        ]

        analyzer.analyze(summaries, [], {})

        # Verify prompt contains serialized data
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs['messages']
        user_message = messages[0]['content']

        assert "Test.swift" in user_message
        assert "TestClass" in user_message

    @patch('analyzers.semantic_analyzer.OpenAI')
    def test_analyze_accepts_dict_input(self, mock_openai_class):
        """Verify analyze() also accepts plain dict objects (not just dataclasses)."""
        from analyzers.semantic_analyzer import SemanticAnalyzer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps([])
        mock_client.chat.completions.create.return_value = mock_response

        analyzer = SemanticAnalyzer(api_key="test-key")

        # Pass plain dicts
        summaries = [{"file_path": "Test.swift", "role": "test"}]
        findings = [{"type": "crash_risk"}]
        graph = {"Test.swift": []}

        result = analyzer.analyze(summaries, findings, graph)

        assert result == []

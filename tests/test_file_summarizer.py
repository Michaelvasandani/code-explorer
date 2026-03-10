"""
Tests for file_summarizer.py - Phase 3 AI-powered file summarization.

Per CLAUDE.md TDD workflow: Tests written BEFORE implementation.
Per Architecture.md Phase 3: FileSummarizer generates structured summaries using LLM.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from core.scanner import FileData


class TestFileSummarizerDataclass:
    """Verify the FileSummary dataclass structure."""

    def test_file_summary_has_required_fields(self):
        """Verify FileSummary dataclass has all required fields per Architecture.md."""
        from analyzers.file_summarizer import FileSummary

        summary = FileSummary(
            file_path="Services/JournalStore.swift",
            role="data persistence service",
            main_types=["JournalStore"],
            dependencies=["Foundation", "SleepEntry"],
            responsibilities=["persist entries", "provide access"],
            suspicious_patterns=["singleton at line 3"]
        )

        assert summary.file_path == "Services/JournalStore.swift"
        assert summary.role == "data persistence service"
        assert summary.main_types == ["JournalStore"]
        assert summary.dependencies == ["Foundation", "SleepEntry"]
        assert summary.responsibilities == ["persist entries", "provide access"]
        assert summary.suspicious_patterns == ["singleton at line 3"]


class TestFileSummarizerInitialization:
    """Verify FileSummarizer initialization and configuration."""

    def test_file_summarizer_initializes_with_api_key(self):
        """Verify FileSummarizer can be initialized with OpenAI API key."""
        from analyzers.file_summarizer import FileSummarizer

        summarizer = FileSummarizer(api_key="test-key")
        assert summarizer is not None

    def test_file_summarizer_raises_error_without_api_key(self):
        """Verify FileSummarizer raises error if no API key provided."""
        from analyzers.file_summarizer import FileSummarizer

        with pytest.raises(ValueError, match="API key"):
            FileSummarizer(api_key=None)

    def test_file_summarizer_loads_prompt_template(self):
        """Verify FileSummarizer loads file_summarizer.txt on initialization."""
        from analyzers.file_summarizer import FileSummarizer

        summarizer = FileSummarizer(api_key="test-key")
        # Should have loaded the prompt template
        assert hasattr(summarizer, 'prompt_loader')


class TestFileSummarizerAnalysis:
    """Verify FileSummarizer.summarize() method."""

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response with valid JSON."""
        return {
            "file_path": "Services/JournalStore.swift",
            "role": "data persistence service",
            "main_types": ["JournalStore"],
            "dependencies": ["Foundation", "SleepEntry"],
            "responsibilities": [
                "persist sleep entries in memory",
                "provide access to saved entries",
                "implement singleton pattern"
            ],
            "suspicious_patterns": [
                "singleton pattern (line 3) - static let shared may make testing difficult"
            ]
        }

    @patch('analyzers.file_summarizer.OpenAI')
    def test_summarize_returns_file_summary(self, mock_openai_class, mock_openai_response):
        """Verify summarize() returns FileSummary dataclass."""
        from analyzers.file_summarizer import FileSummarizer

        # Mock OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock chat completion response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(mock_openai_response)
        mock_client.chat.completions.create.return_value = mock_response

        summarizer = FileSummarizer(api_key="test-key")

        file_data = FileData(
            path="Services/JournalStore.swift",
            content="import Foundation\nclass JournalStore { }"
        )

        summary = summarizer.summarize(file_data)

        assert summary.file_path == "Services/JournalStore.swift"
        assert summary.role == "data persistence service"
        assert "JournalStore" in summary.main_types
        assert "Foundation" in summary.dependencies

    @patch('analyzers.file_summarizer.OpenAI')
    def test_summarize_calls_openai_with_rendered_prompt(self, mock_openai_class):
        """Verify summarize() calls OpenAI API with rendered prompt containing file content."""
        from analyzers.file_summarizer import FileSummarizer

        # Mock OpenAI client
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "file_path": "Test.swift",
            "role": "test",
            "main_types": [],
            "dependencies": [],
            "responsibilities": [],
            "suspicious_patterns": []
        })
        mock_client.chat.completions.create.return_value = mock_response

        summarizer = FileSummarizer(api_key="test-key")

        file_data = FileData(
            path="Test.swift",
            content="class TestClass { }"
        )

        summarizer.summarize(file_data)

        # Verify OpenAI was called
        mock_client.chat.completions.create.assert_called_once()

        # Verify the prompt contains file content
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs['messages']
        user_message = messages[0]['content']

        assert "Test.swift" in user_message
        assert "class TestClass" in user_message

    @patch('analyzers.file_summarizer.OpenAI')
    def test_summarize_uses_gpt_4(self, mock_openai_class):
        """Verify summarize() uses GPT-4 model for analysis."""
        from analyzers.file_summarizer import FileSummarizer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "file_path": "Test.swift",
            "role": "test",
            "main_types": [],
            "dependencies": [],
            "responsibilities": [],
            "suspicious_patterns": []
        })
        mock_client.chat.completions.create.return_value = mock_response

        summarizer = FileSummarizer(api_key="test-key")
        file_data = FileData(path="Test.swift", content="class Test { }")

        summarizer.summarize(file_data)

        call_args = mock_client.chat.completions.create.call_args
        model = call_args.kwargs['model']

        # Should use GPT-4 for code analysis
        assert "gpt-4" in model.lower() or "gpt-4o" in model.lower()

    @patch('analyzers.file_summarizer.OpenAI')
    def test_summarize_parses_json_response(self, mock_openai_class):
        """Verify summarize() correctly parses JSON from LLM response."""
        from analyzers.file_summarizer import FileSummarizer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # LLM returns JSON string
        json_response = {
            "file_path": "Models/SleepEntry.swift",
            "role": "data model",
            "main_types": ["SleepEntry", "SleepQuality"],
            "dependencies": ["Foundation"],
            "responsibilities": ["represent sleep data", "encode/decode"],
            "suspicious_patterns": []
        }

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps(json_response)
        mock_client.chat.completions.create.return_value = mock_response

        summarizer = FileSummarizer(api_key="test-key")
        file_data = FileData(
            path="Models/SleepEntry.swift",
            content="struct SleepEntry: Codable { }"
        )

        summary = summarizer.summarize(file_data)

        assert summary.file_path == "Models/SleepEntry.swift"
        assert summary.role == "data model"
        assert len(summary.main_types) == 2
        assert "SleepEntry" in summary.main_types


class TestFileSummarizerBatchProcessing:
    """Verify FileSummarizer.summarize_all() batch processing."""

    @patch('analyzers.file_summarizer.OpenAI')
    def test_summarize_all_processes_multiple_files(self, mock_openai_class):
        """Verify summarize_all() processes multiple FileData objects."""
        from analyzers.file_summarizer import FileSummarizer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock responses for each file
        def create_response(file_path):
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = json.dumps({
                "file_path": file_path,
                "role": "test",
                "main_types": [],
                "dependencies": [],
                "responsibilities": [],
                "suspicious_patterns": []
            })
            return mock_response

        mock_client.chat.completions.create.side_effect = [
            create_response("File1.swift"),
            create_response("File2.swift")
        ]

        summarizer = FileSummarizer(api_key="test-key")

        files = [
            FileData(path="File1.swift", content="class File1 { }"),
            FileData(path="File2.swift", content="class File2 { }")
        ]

        summaries = summarizer.summarize_all(files)

        assert len(summaries) == 2
        assert summaries[0].file_path == "File1.swift"
        assert summaries[1].file_path == "File2.swift"

    @patch('analyzers.file_summarizer.OpenAI')
    def test_summarize_all_returns_empty_list_for_no_files(self, mock_openai_class):
        """Verify summarize_all() returns empty list when given no files."""
        from analyzers.file_summarizer import FileSummarizer

        summarizer = FileSummarizer(api_key="test-key")
        summaries = summarizer.summarize_all([])

        assert summaries == []
        # Should not call OpenAI for empty list
        mock_openai_class.return_value.chat.completions.create.assert_not_called()


class TestFileSummarizerErrorHandling:
    """Verify FileSummarizer error handling."""

    @patch('analyzers.file_summarizer.OpenAI')
    def test_summarize_handles_invalid_json_response(self, mock_openai_class):
        """Verify summarize() handles malformed JSON from LLM gracefully."""
        from analyzers.file_summarizer import FileSummarizer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # LLM returns invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is not valid JSON"
        mock_client.chat.completions.create.return_value = mock_response

        summarizer = FileSummarizer(api_key="test-key")
        file_data = FileData(path="Test.swift", content="class Test { }")

        with pytest.raises(ValueError, match="JSON"):
            summarizer.summarize(file_data)

    @patch('analyzers.file_summarizer.OpenAI')
    def test_summarize_handles_missing_required_fields(self, mock_openai_class):
        """Verify summarize() handles JSON missing required fields."""
        from analyzers.file_summarizer import FileSummarizer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # LLM returns incomplete JSON (missing required fields)
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "file_path": "Test.swift",
            "role": "test"
            # Missing: main_types, dependencies, responsibilities, suspicious_patterns
        })
        mock_client.chat.completions.create.return_value = mock_response

        summarizer = FileSummarizer(api_key="test-key")
        file_data = FileData(path="Test.swift", content="class Test { }")

        with pytest.raises(ValueError, match="required field"):
            summarizer.summarize(file_data)

    @patch('analyzers.file_summarizer.OpenAI')
    def test_summarize_handles_openai_api_error(self, mock_openai_class):
        """Verify summarize() handles OpenAI API errors gracefully."""
        from analyzers.file_summarizer import FileSummarizer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Simulate API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")

        summarizer = FileSummarizer(api_key="test-key")
        file_data = FileData(path="Test.swift", content="class Test { }")

        with pytest.raises(Exception, match="API Error"):
            summarizer.summarize(file_data)


class TestFileSummarizerEdgeCases:
    """Verify FileSummarizer edge cases."""

    @patch('analyzers.file_summarizer.OpenAI')
    def test_summarize_handles_empty_swift_file(self, mock_openai_class):
        """Verify summarize() handles empty Swift files."""
        from analyzers.file_summarizer import FileSummarizer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "file_path": "Empty.swift",
            "role": "empty file",
            "main_types": [],
            "dependencies": [],
            "responsibilities": [],
            "suspicious_patterns": []
        })
        mock_client.chat.completions.create.return_value = mock_response

        summarizer = FileSummarizer(api_key="test-key")
        file_data = FileData(path="Empty.swift", content="")

        summary = summarizer.summarize(file_data)

        assert summary.file_path == "Empty.swift"
        assert summary.main_types == []

    @patch('analyzers.file_summarizer.OpenAI')
    def test_summarize_handles_large_swift_file(self, mock_openai_class):
        """Verify summarize() handles large Swift files (many lines)."""
        from analyzers.file_summarizer import FileSummarizer

        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "file_path": "Large.swift",
            "role": "large class",
            "main_types": ["LargeClass"],
            "dependencies": ["Foundation"],
            "responsibilities": ["many things"],
            "suspicious_patterns": ["large class"]
        })
        mock_client.chat.completions.create.return_value = mock_response

        summarizer = FileSummarizer(api_key="test-key")

        # Create large file content (500 lines)
        large_content = "import Foundation\n" + "\n".join([f"func method{i}() {{}}" for i in range(500)])
        file_data = FileData(path="Large.swift", content=large_content)

        summary = summarizer.summarize(file_data)

        # Should still process successfully
        assert summary.file_path == "Large.swift"
        assert "LargeClass" in summary.main_types

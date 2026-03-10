"""
Phase 3: File Summarization

Generates AI-powered summaries for Swift source files using OpenAI's GPT-4.
Per Architecture.md: FileSummarizer creates structured FileSummary objects for each file.
"""

import json
from dataclasses import dataclass
from typing import List, Optional
from openai import OpenAI

from analyzers.prompt_loader import PromptLoader
from analyzers.llm_utils import parse_llm_json
from core.scanner import FileData


@dataclass
class FileSummary:
    """
    Structured summary of a Swift source file.

    Per Architecture.md Phase 3 output schema.
    """
    file_path: str
    role: str  # e.g., "data model", "UI view controller", "network service"
    main_types: List[str]  # Classes, structs, protocols, enums, actors defined
    dependencies: List[str]  # Imports and referenced external types
    responsibilities: List[str]  # Key behaviors this file implements
    suspicious_patterns: List[str]  # Risky patterns with line numbers


class FileSummarizer:
    """
    AI-powered file summarizer using OpenAI GPT-4.

    Generates structured summaries for Swift source files to enable
    repo-level semantic analysis in Phase 4.

    Example:
        >>> summarizer = FileSummarizer(api_key="sk-...")
        >>> file_data = FileData(path="Services/Store.swift", content="...")
        >>> summary = summarizer.summarize(file_data)
        >>> print(summary.role)
        "data persistence service"
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FileSummarizer with OpenAI API key.

        Args:
            api_key: OpenAI API key. Required.

        Raises:
            ValueError: If api_key is None or empty
        """
        if not api_key:
            raise ValueError("API key is required for FileSummarizer")

        self.client = OpenAI(api_key=api_key)
        self.prompt_loader = PromptLoader()

    def summarize(self, file_data: FileData) -> FileSummary:
        """
        Generate AI-powered summary for a single Swift file.

        Args:
            file_data: FileData object containing path and content

        Returns:
            FileSummary object with structured analysis

        Raises:
            ValueError: If LLM returns invalid JSON or missing required fields
            Exception: If OpenAI API call fails
        """
        # Render prompt with file content
        prompt = self.prompt_loader.render(
            "file_summarizer",
            file_path=file_data.path,
            file_content=file_data.content
        )

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4 family model for code analysis
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.0  # Deterministic output for consistency
        )

        # Track token usage
        usage = response.usage
        self.last_call_tokens = {
            "input": usage.prompt_tokens,
            "output": usage.completion_tokens
        }

        # Extract and parse JSON response
        response_text = response.choices[0].message.content
        data = parse_llm_json(response_text)

        # Validate required fields
        required_fields = [
            "file_path", "role", "main_types", "dependencies",
            "responsibilities", "suspicious_patterns"
        ]

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(
                f"LLM response missing required fields: {', '.join(missing_fields)}"
            )

        # Create FileSummary
        return FileSummary(
            file_path=data["file_path"],
            role=data["role"],
            main_types=data["main_types"],
            dependencies=data["dependencies"],
            responsibilities=data["responsibilities"],
            suspicious_patterns=data["suspicious_patterns"]
        )

    def summarize_all(self, file_data_list: List[FileData]) -> List[FileSummary]:
        """
        Generate summaries for multiple Swift files.

        Args:
            file_data_list: List of FileData objects to summarize

        Returns:
            List of FileSummary objects in same order as input
        """
        if not file_data_list:
            return []

        summaries = []
        for file_data in file_data_list:
            summary = self.summarize(file_data)
            summaries.append(summary)

        return summaries

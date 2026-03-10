"""
Prompt Loader utility for LLM prompt template management.

This module provides the PromptLoader class for loading and rendering
prompt templates from the prompts/ directory. All AI analyzers
(file_summarizer, semantic_analyzer, validator, question_generator)
use this utility to access their prompts.

Architecture: Per docs/Architecture.md - Prompt Management section
"""

from pathlib import Path
from typing import Optional


class PromptLoader:
    """Load and render LLM prompt templates from the prompts/ directory.

    This class manages access to externalized prompt templates stored as
    .txt files. Prompts can be loaded as raw text or rendered with
    variable substitution using Python's format() method.

    Attributes:
        prompts_dir: Path to the directory containing prompt template files

    Example:
        >>> loader = PromptLoader()
        >>> prompt = loader.render(
        ...     "file_summarizer",
        ...     file_path="Services/JournalStore.swift",
        ...     file_content=swift_code
        ... )
    """

    def __init__(self, prompts_dir: Optional[Path] = None):
        """Initialize PromptLoader with prompts directory path.

        Args:
            prompts_dir: Path to prompts directory. If None, defaults to
                        project_root/prompts/

        Raises:
            ValueError: If prompts_dir doesn't exist or isn't a directory
        """
        if prompts_dir is None:
            # Default to project_root/prompts/
            # Navigate up from analyzers/ to project root
            project_root = Path(__file__).parent.parent
            prompts_dir = project_root / "prompts"

        self.prompts_dir = Path(prompts_dir)

        # Validate prompts directory exists
        if not self.prompts_dir.exists():
            raise ValueError(
                f"Prompts directory does not exist: {self.prompts_dir}"
            )

        if not self.prompts_dir.is_dir():
            raise ValueError(
                f"Prompts path is not a directory: {self.prompts_dir}"
            )

    def load(self, prompt_name: str) -> str:
        """Load a prompt template from the prompts directory.

        Args:
            prompt_name: Name of the prompt file (without .txt extension)

        Returns:
            Raw content of the prompt file as a string

        Raises:
            FileNotFoundError: If the prompt file doesn't exist

        Example:
            >>> loader = PromptLoader()
            >>> content = loader.load("file_summarizer")
        """
        prompt_path = self.prompts_dir / f"{prompt_name}.txt"

        if not prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_path}"
            )

        return prompt_path.read_text()

    def render(self, prompt_name: str, **variables) -> str:
        """Load and render a prompt template with variable substitution.

        Uses Python's str.format() for variable substitution. Template
        variables should be enclosed in {braces}. Literal braces can be
        escaped with double braces: {{example}}.

        Args:
            prompt_name: Name of the prompt file (without .txt extension)
            **variables: Keyword arguments for template variable substitution

        Returns:
            Rendered prompt with variables substituted

        Raises:
            FileNotFoundError: If the prompt file doesn't exist
            KeyError: If a required template variable is not provided

        Example:
            >>> loader = PromptLoader()
            >>> rendered = loader.render(
            ...     "greeting",
            ...     name="Alice",
            ...     role="engineer"
            ... )
        """
        template = self.load(prompt_name)
        return template.format(**variables)

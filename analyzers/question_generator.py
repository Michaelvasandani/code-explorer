"""
Phase 6: Question Generation

Generates onboarding questions from validated findings using OpenAI's GPT-4.
Per Architecture.md: QuestionGenerator synthesizes actionable questions for new developers.
"""

import json
from dataclasses import asdict
from typing import List, Optional
from openai import OpenAI

from analyzers.prompt_loader import PromptLoader
from analyzers.llm_utils import parse_llm_json
from analyzers.semantic_analyzer import SemanticFinding


class QuestionGenerator:
    """
    AI-powered question generator using OpenAI GPT-4.

    Synthesizes 3-5 onboarding questions from validated findings to help
    new developers understand the codebase's patterns and decisions.

    Example:
        >>> generator = QuestionGenerator(api_key="sk-...")
        >>> validated_findings = [SemanticFinding(...), ...]
        >>> questions = generator.generate(validated_findings)
        >>> for q in questions:
        ...     print(f"- {q}")
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize QuestionGenerator with OpenAI API key.

        Args:
            api_key: OpenAI API key. Required.

        Raises:
            ValueError: If api_key is None or empty
        """
        if not api_key:
            raise ValueError("API key is required for QuestionGenerator")

        self.client = OpenAI(api_key=api_key)
        self.prompt_loader = PromptLoader()

    def generate(self, validated_findings: List[SemanticFinding]) -> List[str]:
        """
        Generate onboarding questions from validated findings.

        Args:
            validated_findings: List of SemanticFinding objects that passed validation

        Returns:
            List of question strings (3-5 questions)

        Raises:
            ValueError: If LLM returns invalid JSON or missing required fields
            Exception: If OpenAI API call fails
        """
        # Serialize findings to JSON
        findings_json = self._serialize_findings(validated_findings)

        # Render prompt with findings data
        prompt = self.prompt_loader.render(
            "question_generator",
            validated_findings=findings_json
        )

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4 family for question synthesis
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3  # Some creativity for question generation
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

        # Validate required field
        if "questions" not in data:
            raise ValueError("LLM response missing required field: questions")

        # Validate questions is a list
        if not isinstance(data["questions"], list):
            raise ValueError("LLM response 'questions' field must be a list")

        return data["questions"]

    def _serialize_findings(self, findings: List[SemanticFinding]) -> str:
        """
        Serialize findings to JSON string.

        Args:
            findings: List of SemanticFinding objects

        Returns:
            JSON string representation
        """
        serializable = [asdict(finding) for finding in findings]
        return json.dumps(serializable, indent=2)

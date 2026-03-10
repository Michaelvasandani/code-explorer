"""
Phase 5: Validation

Validates AI-generated findings to filter false positives using OpenAI's GPT-4.
Per Architecture.md: Single context-aware validator adapts reasoning based on finding type.
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Optional
from openai import OpenAI

from analyzers.prompt_loader import PromptLoader
from analyzers.llm_utils import parse_llm_json
from analyzers.semantic_analyzer import SemanticFinding


@dataclass
class ValidationResult:
    """
    Validation result for a semantic finding.

    Per Architecture.md Phase 5 output schema.
    """
    is_valid: bool  # True if finding should be kept, False if it's a false positive
    confidence: float  # 0.0-1.0, confidence in this validation decision
    reasoning: str  # Explanation of why the finding is valid or invalid


class Validator:
    """
    AI-powered validator using OpenAI GPT-4.

    Single context-aware validator that adapts its reasoning based on the
    finding type to validate all categories of findings.

    Example:
        >>> validator = Validator(api_key="sk-...")
        >>> finding = SemanticFinding(...)
        >>> result = validator.validate(finding)
        >>> if result.is_valid:
        ...     print(f"Valid finding: {finding.description}")
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Validator with OpenAI API key.

        Args:
            api_key: OpenAI API key. Required.

        Raises:
            ValueError: If api_key is None or empty
        """
        if not api_key:
            raise ValueError("API key is required for Validator")

        self.client = OpenAI(api_key=api_key)
        self.prompt_loader = PromptLoader()

    def validate(self, finding: SemanticFinding) -> ValidationResult:
        """
        Validate a single semantic finding.

        Args:
            finding: SemanticFinding object to validate

        Returns:
            ValidationResult with is_valid, confidence, and reasoning

        Raises:
            ValueError: If LLM returns invalid JSON or missing required fields
            Exception: If OpenAI API call fails
        """
        # Serialize finding to JSON
        finding_json = json.dumps(asdict(finding), indent=2)
        finding_type = finding.type

        # Render prompt with finding data
        prompt = self.prompt_loader.render(
            "validator",
            finding=finding_json,
            finding_type=finding_type
        )

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4 family for validation
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

        # Validate required fields
        required_fields = ["is_valid", "confidence", "reasoning"]

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(
                f"LLM response missing required fields: {', '.join(missing_fields)}"
            )

        # Create ValidationResult
        return ValidationResult(
            is_valid=data["is_valid"],
            confidence=data["confidence"],
            reasoning=data["reasoning"]
        )

    def validate_all(self, findings: List[SemanticFinding]) -> List[ValidationResult]:
        """
        Validate multiple semantic findings.

        Args:
            findings: List of SemanticFinding objects to validate

        Returns:
            List of ValidationResult objects in same order as input
        """
        if not findings:
            return []

        results = []
        for finding in findings:
            result = self.validate(finding)
            results.append(result)

        return results

    def get_validated_findings(
        self,
        findings: List[SemanticFinding]
    ) -> List[SemanticFinding]:
        """
        Validate findings and return only those marked as valid.

        This is a convenience method that filters out false positives.

        Args:
            findings: List of SemanticFinding objects to validate

        Returns:
            List of SemanticFinding objects that passed validation
        """
        if not findings:
            return []

        validated = []
        for finding in findings:
            result = self.validate(finding)
            if result.is_valid:
                validated.append(finding)

        return validated

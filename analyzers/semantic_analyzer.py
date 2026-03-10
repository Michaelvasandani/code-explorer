"""
Phase 4: Semantic Analysis

Performs AI-powered repository-level analysis to detect bugs, code smells,
architecture issues, test gaps, and documentation gaps using OpenAI's GPT-4.

Per Architecture.md: SemanticAnalyzer uses Phase 1-3 data to identify cross-file issues.
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any, Union
from openai import OpenAI

from analyzers.prompt_loader import PromptLoader
from analyzers.llm_utils import parse_llm_json


@dataclass
class SemanticFinding:
    """
    Structured semantic issue found through AI analysis.

    Per README.md requirements: Each finding must have type, location, explanation, and confidence.
    Additional fields (severity, evidence, recommendation) provide extra value.
    """
    # Required fields per README
    type: str  # "bug", "smell", "architecture", "test_gap", "doc_gap", "uncertainty"
    location: str  # "file:line" or "file:line1,line2" or "component_name"
    explanation: str  # Clear description of the issue (renamed from description)
    confidence: str  # "high", "medium", "low" - REQUIRED by README

    # Optional bonus fields
    subtype: str = ""  # Specific issue type (e.g., "force_unwrap", "singleton_testability")
    severity: str = ""  # "high", "medium", "low" - impact if true
    evidence: str = ""  # Concrete evidence from Phase 1-3 data
    recommendation: str = ""  # Actionable fix with concrete steps


class SemanticAnalyzer:
    """
    AI-powered semantic analyzer using OpenAI GPT-4.

    Analyzes repository-level patterns using file summaries, static findings,
    and dependency graphs to identify complex issues requiring cross-file understanding.

    Example:
        >>> analyzer = SemanticAnalyzer(api_key="sk-...")
        >>> findings = analyzer.analyze(file_summaries, static_findings, dep_graph)
        >>> for finding in findings:
        ...     print(f"{finding.severity}: {finding.description}")
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize SemanticAnalyzer with OpenAI API key.

        Args:
            api_key: OpenAI API key. Required.

        Raises:
            ValueError: If api_key is None or empty
        """
        if not api_key:
            raise ValueError("API key is required for SemanticAnalyzer")

        self.client = OpenAI(api_key=api_key)
        self.prompt_loader = PromptLoader()

    def analyze(
        self,
        file_summaries: List[Any],
        static_findings: List[Any],
        dependency_graph: Dict[str, List[str]]
    ) -> List[SemanticFinding]:
        """
        Perform semantic analysis on the codebase.

        Args:
            file_summaries: List of FileSummary objects or dicts from Phase 3
            static_findings: List of StaticFinding objects or dicts from Phase 2
            dependency_graph: Dict mapping file paths to dependencies from Phase 2

        Returns:
            List of SemanticFinding objects with detected issues

        Raises:
            ValueError: If LLM returns invalid JSON or missing required fields
            Exception: If OpenAI API call fails
        """
        # Serialize input data to JSON strings
        file_summaries_json = self._serialize_to_json(file_summaries)
        static_findings_json = self._serialize_to_json(static_findings)
        dependency_graph_json = json.dumps(dependency_graph, indent=2)

        # Render prompt with Phase 1-3 data
        prompt = self.prompt_loader.render(
            "semantic_analyzer",
            file_summaries=file_summaries_json,
            static_findings=static_findings_json,
            dependency_graph=dependency_graph_json
        )

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4 family for complex semantic analysis
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

        # Validate it's a list
        if not isinstance(data, list):
            raise ValueError(f"LLM response must be a JSON array, got {type(data)}")

        # Convert to SemanticFinding objects
        findings = []
        for item in data:
            # Validate REQUIRED fields per README
            required_fields = ["type", "location", "explanation", "confidence"]

            missing_fields = [field for field in required_fields if field not in item]
            if missing_fields:
                raise ValueError(
                    f"LLM response missing required fields: {', '.join(missing_fields)}"
                )

            # Create SemanticFinding (with optional bonus fields)
            finding = SemanticFinding(
                # Required fields
                type=item["type"],
                location=item["location"],
                explanation=item["explanation"],
                confidence=item["confidence"],
                # Optional bonus fields (default to empty string if not present)
                subtype=item.get("subtype", ""),
                severity=item.get("severity", ""),
                evidence=item.get("evidence", ""),
                recommendation=item.get("recommendation", "")
            )
            findings.append(finding)

        return findings

    def _serialize_to_json(self, data: List[Any]) -> str:
        """
        Serialize a list of objects to JSON string.

        Handles both dataclass objects and plain dicts.

        Args:
            data: List of dataclass objects or dicts

        Returns:
            JSON string representation
        """
        serializable = []
        for item in data:
            # Check if it's a dataclass
            if hasattr(item, '__dataclass_fields__'):
                serializable.append(asdict(item))
            else:
                # Assume it's already a dict
                serializable.append(item)

        return json.dumps(serializable, indent=2)

"""
Utility functions for working with LLM responses.
"""

import json


def strip_markdown_json(response_text: str) -> str:
    """
    Strip markdown code blocks from JSON responses.

    Many LLMs return JSON wrapped in ```json ... ``` blocks.
    This function removes those wrappers.

    Args:
        response_text: Raw LLM response text

    Returns:
        Cleaned JSON string
    """
    text = response_text.strip()

    # Check if wrapped in code blocks
    if text.startswith("```"):
        lines = text.split("\n")

        # Remove first line (```json or ```)
        if lines[0].startswith("```"):
            lines = lines[1:]

        # Remove last line if it's ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        return "\n".join(lines)

    return text


def parse_llm_json(response_text: str):
    """
    Parse JSON from LLM response, handling markdown code blocks.

    Args:
        response_text: Raw LLM response text

    Returns:
        Parsed JSON object (dict or list)

    Raises:
        ValueError: If JSON parsing fails
    """
    cleaned_text = strip_markdown_json(response_text)

    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Failed to parse JSON from LLM response: {e}\n"
            f"Response (first 200 chars): {cleaned_text[:200]}"
        )

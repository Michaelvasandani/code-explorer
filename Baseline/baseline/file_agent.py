"""File-level LLM analysis agent."""

import json
import time
import os
from pathlib import Path
from openai import OpenAI
from baseline.models import FileAgentResult
from dotenv import load_dotenv

# Load environment variables from .env files
# Try current directory first, then home directory
load_dotenv()  # Loads from current directory or parent
load_dotenv(Path.home() / ".env")  # Also try home directory


# OpenAI pricing (as of Jan 2025 - GPT-4o-mini)
INPUT_COST_PER_1K = 0.00015
OUTPUT_COST_PER_1K = 0.0006


def call_openai(prompt: str, file_content: str, model: str = "gpt-4o-mini") -> tuple[dict, float, float, int, int]:
    """
    Call OpenAI API with the given prompt and file content.

    Args:
        prompt: System prompt for analysis
        file_content: The source code to analyze
        model: OpenAI model to use

    Returns:
        Tuple of (response_dict, cost_usd, latency_seconds, input_tokens, output_tokens)
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    start_time = time.time()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": file_content}
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    latency = time.time() - start_time

    # Get token counts
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    # Calculate cost
    cost = (input_tokens / 1000 * INPUT_COST_PER_1K +
            output_tokens / 1000 * OUTPUT_COST_PER_1K)

    result = json.loads(response.choices[0].message.content)

    return result, cost, latency, input_tokens, output_tokens


FILE_ANALYSIS_PROMPT = """You are a senior iOS engineer analyzing a Swift source file.

Your task is to identify potential issues in this single file. Return a JSON object with:

{
  "summary": "One sentence describing what this file does",
  "findings": [
    {
      "type": "bug|smell|architecture|test_gap|documentation_gap|uncertainty",
      "location": "Filename.swift:line_number",
      "confidence": "high|medium|low",
      "explanation": "Clear description of the issue"
    }
  ]
}

FINDING TYPES:
- bug: Potential crashes, force unwraps, force-try, logic errors
- smell: Code duplication, large classes, tight coupling
- architecture: Singleton overuse, mixed patterns, layer violations
- test_gap: Critical functionality that should be tested (persistence, network calls)
- documentation_gap: Public APIs without documentation
- uncertainty: Low-confidence concerns worth flagging

RULES:
1. Only report what you can see in THIS FILE - do not guess about other files
2. Prefer fewer high-confidence findings over many weak ones
3. For bugs, focus on crash risks and logical errors
4. Mark uncertain claims as "uncertainty" type
5. Include line numbers when possible
6. Be specific and actionable in explanations

Focus on findings that would help a new engineer understand risks and patterns in this file."""


def analyze_file(file_path: str, file_content: str) -> FileAgentResult:
    """
    Analyze a single file using LLM.

    Args:
        file_path: Path to the file being analyzed
        file_content: Content of the source file

    Returns:
        FileAgentResult with summary, findings, cost, latency, and token counts
    """
    result, cost, latency, input_tokens, output_tokens = call_openai(FILE_ANALYSIS_PROMPT, file_content)

    # Store token counts in result for metrics tracking
    result_obj = FileAgentResult(
        file_path=file_path,
        summary=result.get("summary", ""),
        findings=result.get("findings", []),
        raw_cost_usd=cost,
        raw_latency_seconds=latency
    )

    # Add token counts as attributes for metrics
    result_obj.input_tokens = input_tokens
    result_obj.output_tokens = output_tokens

    return result_obj

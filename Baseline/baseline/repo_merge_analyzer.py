"""Repository-level merge and analysis module."""

import json
from baseline.models import RepoMergeResult
from baseline.file_agent import call_openai


REPO_MERGE_PROMPT = """You are a senior iOS architect analyzing an entire codebase.

You have been given:
1. Summaries of all source files
2. Findings from individual file analyses

Your task is to:
1. Produce a high-level architecture summary
2. Merge duplicate or related findings
3. Identify codebase-wide patterns and themes

Return a JSON object with this structure:

{
  "high_level_summary": {
    "architecture_pattern": "Description of overall architecture (MVVM, MVC, mixed, etc.)",
    "key_components": ["List of main components/modules"],
    "primary_risks": ["Top 3-5 risks or concerns across the codebase"]
  },
  "merged_findings": [
    {
      "id": "finding_X",
      "type": "bug|smell|architecture|test_gap|documentation_gap|uncertainty",
      "location": "File.swift:line or component name",
      "confidence": "high|medium|low",
      "explanation": "Clear description with context"
    }
  ]
}

RULES FOR MERGING:
1. If multiple files have the same type of issue (e.g., "force unwraps"), consider merging into one finding that lists all locations
2. Preserve high-confidence crash risks as separate findings
3. Group related architecture issues (e.g., "inconsistent singleton usage across JournalStore, WeatherCache")
4. Remove low-value duplicates
5. Keep the most important findings - aim for quality over quantity
6. Maintain finding IDs from the original findings when possible

RULES FOR ARCHITECTURE SUMMARY:
1. Identify the actual pattern in use (not what it should be)
2. Note if patterns are mixed or inconsistent
3. List the 3-5 most important components
4. Focus primary_risks on crash potential, maintainability issues, and architectural concerns
5. Be specific and grounded in the actual code"""


def analyze_repo_level(file_summaries: list[str], aggregated_findings: list[dict]) -> tuple[RepoMergeResult, float, int, int]:
    """
    Perform repository-level analysis to identify patterns and merge findings.

    Args:
        file_summaries: List of file summary strings
        aggregated_findings: List of findings from file-level analysis

    Returns:
        Tuple of (RepoMergeResult, cost, input_tokens, output_tokens)
    """
    # Prepare context for the LLM
    summaries_text = "\n".join([f"- {s}" for s in file_summaries])
    findings_text = json.dumps(aggregated_findings, indent=2)

    context = f"""FILE SUMMARIES:
{summaries_text}

AGGREGATED FINDINGS:
{findings_text}"""

    result, cost, latency, input_tokens, output_tokens = call_openai(REPO_MERGE_PROMPT, context)

    result_obj = RepoMergeResult(
        high_level_summary=result.get("high_level_summary", {}),
        merged_findings=result.get("merged_findings", [])
    )

    return result_obj, cost, input_tokens, output_tokens

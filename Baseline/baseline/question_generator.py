"""Question generator module for creating onboarding questions."""

import json
from baseline.models import Question
from baseline.file_agent import call_openai


QUESTION_GENERATION_PROMPT = """You are helping create onboarding questions for a new engineer joining a codebase.

You have been given:
1. A high-level architecture summary
2. Analysis findings (bugs, smells, architecture issues, test gaps, etc.)

Your task is to generate 5-8 questions that a new engineer should ask before making changes.

Return a JSON object with this structure:

{
  "questions": [
    {
      "question": "Clear, specific question a new engineer should ask",
      "why_it_matters": "Why this question is important for understanding or safety",
      "related_findings": ["finding_1", "finding_3"],
      "areas_affected": ["Component or layer affected"]
    }
  ]
}

GOOD QUESTIONS:
- "What is the error handling strategy for the persistence layer?"
- "Why is the app mixing UIKit and SwiftUI - is there a migration plan?"
- "How should new features handle weather API failures?"
- "What is the testing strategy for ViewModels?"
- "Why are there multiple singleton stores instead of dependency injection?"

BAD QUESTIONS (too vague):
- "How does this app work?"
- "What should I know?"
- "Are there any bugs?"

RULES:
1. Focus on architecture understanding, risk awareness, and decision context
2. Link questions to specific findings when relevant
3. Prioritize questions about crash risks, testing gaps, and architectural decisions
4. Make questions specific enough to be actionable
5. Include "why it matters" that explains the impact
6. Identify areas affected (e.g., "Persistence layer", "UI components", "Network layer")
7. Aim for 5-8 high-value questions - quality over quantity
"""


def generate_questions(findings: list[dict], high_level_summary: dict) -> tuple[list[Question], float, int, int]:
    """
    Generate onboarding questions from findings and summary.

    Args:
        findings: List of analysis findings
        high_level_summary: High-level architecture summary

    Returns:
        Tuple of (list of Question objects, cost, input_tokens, output_tokens)
    """
    # Prepare context
    summary_text = json.dumps(high_level_summary, indent=2)
    findings_text = json.dumps(findings, indent=2)

    context = f"""HIGH-LEVEL SUMMARY:
{summary_text}

FINDINGS:
{findings_text}"""

    result, cost, latency, input_tokens, output_tokens = call_openai(QUESTION_GENERATION_PROMPT, context)

    # Convert to Question objects with unique IDs
    questions = []
    for idx, q_data in enumerate(result.get("questions", []), start=1):
        question = Question(
            id=f"question_{idx}",
            question=q_data.get("question", ""),
            why_it_matters=q_data.get("why_it_matters", ""),
            related_findings=q_data.get("related_findings", []),
            areas_affected=q_data.get("areas_affected", [])
        )
        questions.append(question)

    return questions, cost, input_tokens, output_tokens

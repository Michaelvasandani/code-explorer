"""
Performance metrics tracking for AI-powered analysis pipeline.

Tracks API calls, token usage, and cost estimation for OpenAI API.
"""

from dataclasses import dataclass, field
from typing import Dict


# OpenAI gpt-4o-mini pricing (as of 2024)
# https://openai.com/pricing
GPT4O_MINI_INPUT_COST_PER_1M = 0.150  # $0.150 per 1M input tokens
GPT4O_MINI_OUTPUT_COST_PER_1M = 0.600  # $0.600 per 1M output tokens


@dataclass
class PipelineMetrics:
    """
    Tracks performance metrics for the analysis pipeline.

    Attributes:
        api_calls: Number of API requests made
        input_tokens: Total input tokens sent to API
        output_tokens: Total output tokens received from API
        cost_by_phase: Breakdown of cost per pipeline phase
    """
    api_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_by_phase: Dict[str, float] = field(default_factory=dict)

    def add_call(self, phase: str, input_tokens: int, output_tokens: int):
        """
        Record an API call with token usage.

        Args:
            phase: Pipeline phase name (e.g., "file_summarization")
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
        """
        self.api_calls += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

        # Calculate cost for this call
        input_cost = (input_tokens / 1_000_000) * GPT4O_MINI_INPUT_COST_PER_1M
        output_cost = (output_tokens / 1_000_000) * GPT4O_MINI_OUTPUT_COST_PER_1M
        call_cost = input_cost + output_cost

        # Add to phase breakdown
        if phase not in self.cost_by_phase:
            self.cost_by_phase[phase] = 0.0
        self.cost_by_phase[phase] += call_cost

    @property
    def total_cost_usd(self) -> float:
        """Calculate total estimated cost in USD."""
        input_cost = (self.input_tokens / 1_000_000) * GPT4O_MINI_INPUT_COST_PER_1M
        output_cost = (self.output_tokens / 1_000_000) * GPT4O_MINI_OUTPUT_COST_PER_1M
        return input_cost + output_cost

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary for reporting."""
        return {
            "api_calls": self.api_calls,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.input_tokens + self.output_tokens,
            "estimated_cost_usd": self.total_cost_usd,
            "cost_by_phase": self.cost_by_phase
        }

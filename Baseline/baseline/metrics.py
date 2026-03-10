"""Metrics tracking module for cost and performance monitoring."""

import time


class MetricsTracker:
    """Track metrics for the baseline analyzer."""

    def __init__(self):
        """Initialize the metrics tracker."""
        self.start_time = time.time()
        self.total_cost_usd = 0.0
        self.total_files = 0
        self.llm_calls = 0
        self.findings_before_dedupe = 0
        self.findings_after_dedupe = 0

        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0

        # Cost by phase
        self.cost_by_phase = {
            "file_analysis": 0.0,
            "repo_merge": 0.0,
            "question_generation": 0.0
        }

        # Tokens by phase
        self.tokens_by_phase = {
            "file_analysis": {"input": 0, "output": 0},
            "repo_merge": {"input": 0, "output": 0},
            "question_generation": {"input": 0, "output": 0}
        }

    def record_file_analysis(self, cost: float, findings_count: int, input_tokens: int = 0, output_tokens: int = 0):
        """
        Record metrics from a file-level analysis.

        Args:
            cost: API cost in USD
            findings_count: Number of findings from this file
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
        """
        self.total_cost_usd += cost
        self.total_files += 1
        self.llm_calls += 1
        self.findings_before_dedupe += findings_count

        # Track tokens
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        # Track by phase
        self.cost_by_phase["file_analysis"] += cost
        self.tokens_by_phase["file_analysis"]["input"] += input_tokens
        self.tokens_by_phase["file_analysis"]["output"] += output_tokens

    def record_repo_merge(self, cost: float, input_tokens: int = 0, output_tokens: int = 0):
        """
        Record metrics from repo-level merge analysis.

        Args:
            cost: API cost in USD
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
        """
        self.total_cost_usd += cost
        self.llm_calls += 1

        # Track tokens
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        # Track by phase
        self.cost_by_phase["repo_merge"] += cost
        self.tokens_by_phase["repo_merge"]["input"] += input_tokens
        self.tokens_by_phase["repo_merge"]["output"] += output_tokens

    def record_question_generation(self, cost: float, input_tokens: int = 0, output_tokens: int = 0):
        """
        Record metrics from question generation.

        Args:
            cost: API cost in USD
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
        """
        self.total_cost_usd += cost
        self.llm_calls += 1

        # Track tokens
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        # Track by phase
        self.cost_by_phase["question_generation"] += cost
        self.tokens_by_phase["question_generation"]["input"] += input_tokens
        self.tokens_by_phase["question_generation"]["output"] += output_tokens

    def set_deduplication_stats(self, before: int, after: int):
        """
        Set deduplication statistics.

        Args:
            before: Number of findings before deduplication
            after: Number of findings after deduplication
        """
        self.findings_before_dedupe = before
        self.findings_after_dedupe = after

    def get_runtime(self) -> float:
        """
        Get total runtime in seconds.

        Returns:
            Runtime in seconds since tracker initialization
        """
        return time.time() - self.start_time

    def get_summary(self) -> dict:
        """
        Get a summary of all metrics.

        Returns:
            Dictionary with all tracked metrics including tokens and cost breakdown
        """
        return {
            "api_calls": self.llm_calls,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "estimated_cost_usd": round(self.total_cost_usd, 8),
            "cost_by_phase": {
                "file_analysis": round(self.cost_by_phase["file_analysis"], 8),
                "repo_merge": round(self.cost_by_phase["repo_merge"], 8),
                "question_generation": round(self.cost_by_phase["question_generation"], 8)
            },
            "tokens_by_phase": self.tokens_by_phase,
            "runtime_seconds": round(self.get_runtime(), 2),
            "total_files": self.total_files,
            "findings_before_dedupe": self.findings_before_dedupe,
            "findings_after_dedupe": self.findings_after_dedupe
        }

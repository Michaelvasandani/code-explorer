"""
Main entry point for Sleep Journal Codebase Analyzer.

This module orchestrates all 7 phases of the analysis pipeline:
1. Scan - Discover Swift files
2. Static Analysis - Detect syntactic patterns and build dependency graph
3. File Summarization - Generate structured summaries (AI)
4. Semantic Analysis - Detect bugs, smells, architecture issues (AI)
5. Validation - Filter false positives (AI)
6. Question Generation - Synthesize onboarding questions (AI)
7. Report Building - Assemble final JSON output
"""

from pathlib import Path
from typing import List, Tuple, Dict

from core.scanner import Scanner, FileData
from core.syntactic_analyzer import SyntacticAnalyzer, StaticFinding
from core.graph_builder import GraphBuilder
from core.metrics import PipelineMetrics
from analyzers.file_summarizer import FileSummarizer, FileSummary
from analyzers.semantic_analyzer import SemanticAnalyzer, SemanticFinding
from analyzers.validator import Validator
from analyzers.question_generator import QuestionGenerator
from core.report_builder import ReportBuilder, AnalysisReport


class AnalysisPipeline:
    """Main analysis pipeline orchestrating all 7 phases."""

    def __init__(self, repo_path: Path, api_key: str):
        """
        Initialize analysis pipeline.

        Args:
            repo_path: Path to the repository to analyze
            api_key: OpenAI API key for AI-powered components
        """
        self.repo_path = repo_path
        self.api_key = api_key
        self.metrics = PipelineMetrics()

    def run(self) -> Tuple[AnalysisReport, Dict]:
        """
        Run the complete 7-phase analysis pipeline with metrics tracking.

        Returns:
            Tuple of (AnalysisReport, metrics_dict) containing analysis results and performance metrics
        """
        # Phase 1: Scan Codebase
        scanner = Scanner(repo_path=self.repo_path)
        files = scanner.scan()

        # Phase 2: Static Analysis
        syntactic_analyzer = SyntacticAnalyzer()
        graph_builder = GraphBuilder()

        all_static_findings: List[StaticFinding] = []
        for file_data in files:
            static_findings = syntactic_analyzer.analyze(
                file_data.content,
                file_data.path
            )
            all_static_findings.extend(static_findings)

        dependency_graph = graph_builder.build_dependencies(files)

        # Phase 3: File Summarization (AI)
        file_summarizer = FileSummarizer(api_key=self.api_key)

        file_summaries: List[FileSummary] = []
        for file_data in files:
            summary = file_summarizer.summarize(file_data)
            file_summaries.append(summary)

            # Track metrics
            if hasattr(file_summarizer, 'last_call_tokens'):
                tokens = file_summarizer.last_call_tokens
                self.metrics.add_call("file_summarization", tokens["input"], tokens["output"])

        # Phase 4: Repository Semantic Analysis (AI)
        semantic_analyzer = SemanticAnalyzer(api_key=self.api_key)

        semantic_findings = semantic_analyzer.analyze(
            file_summaries=file_summaries,
            static_findings=all_static_findings,
            dependency_graph=dependency_graph
        )

        # Track metrics
        if hasattr(semantic_analyzer, 'last_call_tokens'):
            tokens = semantic_analyzer.last_call_tokens
            self.metrics.add_call("semantic_analysis", tokens["input"], tokens["output"])

        # Phase 5: Validation
        validator = Validator(api_key=self.api_key)

        validated_findings: List[SemanticFinding] = []
        for finding in semantic_findings:
            is_valid = validator.validate(finding)
            if is_valid:
                validated_findings.append(finding)

            # Track metrics
            if hasattr(validator, 'last_call_tokens'):
                tokens = validator.last_call_tokens
                self.metrics.add_call("validation", tokens["input"], tokens["output"])

        # Phase 6: Question Generation (AI)
        question_generator = QuestionGenerator(api_key=self.api_key)

        onboarding_questions = question_generator.generate(validated_findings)

        # Track metrics
        if hasattr(question_generator, 'last_call_tokens'):
            tokens = question_generator.last_call_tokens
            self.metrics.add_call("question_generation", tokens["input"], tokens["output"])

        # Phase 7: Report Building
        report_builder = ReportBuilder()

        # Generate high-level summary
        summary = self._generate_summary(
            num_files=len(files),
            file_summaries=file_summaries,
            num_findings=len(validated_findings)
        )

        # Document known limitations
        limitations = [
            "Static analysis only - does not detect runtime-specific issues or performance problems",
            "Limited to Swift source files - does not analyze build configurations, assets, or Interface Builder files",
            "AI-generated findings may require human validation and domain expertise",
            "No understanding of business requirements or product context",
            "Single-repository analysis - does not consider external dependencies or shared libraries",
            "Line number accuracy depends on static analysis pattern matching"
        ]

        # Get metrics dict
        metrics_dict = self.metrics.to_dict()

        report = report_builder.build(
            summary=summary,
            findings=validated_findings,
            questions=onboarding_questions,
            limitations=limitations,
            metrics=metrics_dict
        )

        return report, metrics_dict

    def _generate_summary(
        self,
        num_files: int,
        file_summaries: List[FileSummary],
        num_findings: int
    ) -> str:
        """
        Generate high-level codebase summary.

        Args:
            num_files: Total number of Swift files
            file_summaries: List of AI-generated file summaries
            num_findings: Number of validated findings

        Returns:
            Summary string describing the codebase
        """
        # Analyze architecture patterns from summaries
        ui_pattern = "SwiftUI" if any(
            "SwiftUI" in s.role or "SwiftUI" in str(s.dependencies)
            for s in file_summaries
        ) else "UIKit"

        uikit_count = sum(
            1 for s in file_summaries
            if "UIKit" in s.dependencies or "UIViewController" in s.role
        )
        swiftui_count = sum(
            1 for s in file_summaries
            if "SwiftUI" in str(s.dependencies) or "View" in str(s.main_types)
        )

        arch_pattern = "mixed UIKit and SwiftUI" if (uikit_count > 0 and swiftui_count > 0) else ui_pattern

        # Identify main components
        has_models = any("model" in s.role.lower() for s in file_summaries)
        has_services = any("service" in s.role.lower() or "store" in s.role.lower() for s in file_summaries)
        has_views = any("view" in s.role.lower() or "controller" in s.role.lower() for s in file_summaries)

        summary = (
            f"This is a Swift iOS application with {num_files} source files using {arch_pattern} architecture. "
        )

        if has_models and has_services and has_views:
            summary += "The codebase follows a layered architecture with data models, services, and UI components. "

        if num_findings > 0:
            summary += (
                f"Analysis identified {num_findings} validated findings including potential bugs, "
                "code smells, and architectural concerns that may affect maintainability and reliability."
            )
        else:
            summary += "The codebase appears relatively healthy with no major issues detected."

        return summary


def analyze(repo_path: Path, api_key: str) -> Tuple[AnalysisReport, Dict]:
    """
    Convenience function to run the complete analysis pipeline with metrics.

    Args:
        repo_path: Path to the repository to analyze
        api_key: OpenAI API key for AI-powered components

    Returns:
        Tuple of (AnalysisReport, metrics_dict) containing analysis results and performance metrics
    """
    pipeline = AnalysisPipeline(repo_path=repo_path, api_key=api_key)
    return pipeline.run()

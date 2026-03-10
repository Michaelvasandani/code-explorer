"""
Tests for analyze.py main entry point.

Following TDD: Write tests BEFORE implementing analyze.py.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from analyze import analyze, AnalysisPipeline
from core.scanner import FileData
from core.syntactic_analyzer import StaticFinding
from core.graph_builder import GraphBuilder
from analyzers.file_summarizer import FileSummary
from analyzers.semantic_analyzer import SemanticFinding
from core.report_builder import AnalysisReport


# Test 1: AnalysisPipeline class exists
def test_analysis_pipeline_class_exists():
    """Test that AnalysisPipeline class is defined."""
    assert AnalysisPipeline is not None


# Test 2: AnalysisPipeline initializes with repo_path and api_key
def test_analysis_pipeline_initialization():
    """Test AnalysisPipeline initialization with required parameters."""
    repo_path = Path("Sleep Journal")
    api_key = "test-api-key"

    pipeline = AnalysisPipeline(repo_path=repo_path, api_key=api_key)

    assert pipeline.repo_path == repo_path
    assert pipeline.api_key == api_key


# Test 3: AnalysisPipeline has run() method that returns AnalysisReport
@patch('analyze.Scanner')
@patch('analyze.SyntacticAnalyzer')
@patch('analyze.GraphBuilder')
@patch('analyze.FileSummarizer')
@patch('analyze.SemanticAnalyzer')
@patch('analyze.Validator')
@patch('analyze.QuestionGenerator')
@patch('analyze.ReportBuilder')
def test_pipeline_run_returns_analysis_report(
    mock_report_builder_cls,
    mock_question_gen_cls,
    mock_validator_cls,
    mock_semantic_cls,
    mock_file_sum_cls,
    mock_graph_cls,
    mock_syntactic_cls,
    mock_scanner_cls
):
    """Test that pipeline.run() returns an AnalysisReport."""
    # Setup mocks
    mock_scanner = mock_scanner_cls.return_value
    mock_scanner.scan.return_value = []

    mock_syntactic = mock_syntactic_cls.return_value
    mock_syntactic.analyze.return_value = []

    mock_graph = mock_graph_cls.return_value
    mock_graph.build_dependencies.return_value = {}

    mock_file_sum = mock_file_sum_cls.return_value
    mock_file_sum.summarize.return_value = FileSummary(
        file_path="test.swift",
        role="test",
        main_types=[],
        dependencies=[],
        responsibilities=[],
        suspicious_patterns=[]
    )

    mock_semantic = mock_semantic_cls.return_value
    mock_semantic.analyze.return_value = []

    mock_validator = mock_validator_cls.return_value
    mock_validator.validate.return_value = True

    mock_question_gen = mock_question_gen_cls.return_value
    mock_question_gen.generate.return_value = ["Question 1?"]

    mock_report_builder = mock_report_builder_cls.return_value
    mock_report = AnalysisReport(
            summary="Test codebase summary",
            findings=[],
            questions=["Question 1?"],
            limitations=["Test limitation"]
        )
    mock_report_builder.build.return_value = mock_report

    # Run pipeline
    pipeline = AnalysisPipeline(repo_path=Path("test"), api_key="test-key")
    result = pipeline.run()

    assert isinstance(result, AnalysisReport)


# Test 4: Pipeline orchestrates all 7 phases in correct order
@patch('analyze.Scanner')
@patch('analyze.SyntacticAnalyzer')
@patch('analyze.GraphBuilder')
@patch('analyze.FileSummarizer')
@patch('analyze.SemanticAnalyzer')
@patch('analyze.Validator')
@patch('analyze.QuestionGenerator')
@patch('analyze.ReportBuilder')
def test_pipeline_orchestrates_all_phases(
    mock_report_builder_cls,
    mock_question_gen_cls,
    mock_validator_cls,
    mock_semantic_cls,
    mock_file_sum_cls,
    mock_graph_cls,
    mock_syntactic_cls,
    mock_scanner_cls
):
    """Test that pipeline runs all 7 phases in correct order."""
    # Setup mocks
    mock_scanner = mock_scanner_cls.return_value
    mock_files = [FileData(path="test.swift", content="class Test {}")]
    mock_scanner.scan.return_value = mock_files

    mock_syntactic = mock_syntactic_cls.return_value
    mock_static_findings = [
        StaticFinding(
            type="crash_risk",
            subtype="force_unwrap",
            file="test.swift",
            line=1,
            code_snippet="let x = y!"
        )
    ]
    mock_syntactic.analyze.return_value = mock_static_findings

    mock_graph = mock_graph_cls.return_value
    mock_deps = {"test.swift": ["Foundation"]}
    mock_graph.build_dependencies.return_value = mock_deps

    mock_file_sum = mock_file_sum_cls.return_value
    mock_summary = FileSummary(
        file_path="test.swift",
        role="test",
        main_types=["Test"],
        dependencies=["Foundation"],
        responsibilities=["testing"],
        suspicious_patterns=[]
    )
    mock_file_sum.summarize.return_value = mock_summary

    mock_semantic = mock_semantic_cls.return_value
    mock_semantic_findings = [
        SemanticFinding(
            type="bug",
            location="test.swift:1",
            explanation="Force unwrap may crash",
            confidence="high",
            subtype="force_unwrap_crash_risk",
            severity="high",
            evidence="let x = y!",
            recommendation="Use optional binding instead"
        )
    ]
    mock_semantic.analyze.return_value = mock_semantic_findings

    mock_validator = mock_validator_cls.return_value
    mock_validator.validate.return_value = True

    mock_question_gen = mock_question_gen_cls.return_value
    mock_questions = ["Why force unwrap?"]
    mock_question_gen.generate.return_value = mock_questions

    mock_report_builder = mock_report_builder_cls.return_value
    mock_report = AnalysisReport(
            summary="Test codebase summary",
            findings=mock_semantic_findings,
            questions=mock_questions,
            limitations=["Test limitation"]
        )
    mock_report_builder.build.return_value = mock_report

    # Run pipeline
    pipeline = AnalysisPipeline(repo_path=Path("test"), api_key="test-key")
    result = pipeline.run()

    # Verify all phases called
    mock_scanner.scan.assert_called_once()
    assert mock_syntactic.analyze.call_count == len(mock_files)
    mock_graph.build_dependencies.assert_called_once()
    assert mock_file_sum.summarize.call_count == len(mock_files)
    mock_semantic.analyze.assert_called_once()
    mock_validator.validate.assert_called()
    mock_question_gen.generate.assert_called_once()
    mock_report_builder.build.assert_called_once()


# Test 5: Phase 1 - Scanner discovers Swift files
@patch('analyze.Scanner')
@patch('analyze.SyntacticAnalyzer')
@patch('analyze.GraphBuilder')
@patch('analyze.FileSummarizer')
@patch('analyze.SemanticAnalyzer')
@patch('analyze.Validator')
@patch('analyze.QuestionGenerator')
@patch('analyze.ReportBuilder')
def test_phase_1_scanner(
    mock_report_builder_cls,
    mock_question_gen_cls,
    mock_validator_cls,
    mock_semantic_cls,
    mock_file_sum_cls,
    mock_graph_cls,
    mock_syntactic_cls,
    mock_scanner_cls
):
    """Test Phase 1: Scanner is initialized with repo_path."""
    mock_scanner = mock_scanner_cls.return_value
    mock_scanner.scan.return_value = []

    mock_syntactic = mock_syntactic_cls.return_value
    mock_graph = mock_graph_cls.return_value
    mock_graph.build_dependencies.return_value = {}

    mock_semantic = mock_semantic_cls.return_value
    mock_semantic.analyze.return_value = []

    mock_question_gen = mock_question_gen_cls.return_value
    mock_question_gen.generate.return_value = []

    mock_report_builder = mock_report_builder_cls.return_value
    mock_report_builder.build.return_value = AnalysisReport(
            summary="Test codebase summary",
            findings=[],
            questions=[],
            limitations=["Test limitation"]
        )

    pipeline = AnalysisPipeline(repo_path=Path("test"), api_key="test-key")
    pipeline.run()

    # Verify Scanner initialized with correct repo_path
    mock_scanner_cls.assert_called_once_with(repo_path=Path("test"))


# Test 6: Phase 2 - Static analysis processes all files
@patch('analyze.Scanner')
@patch('analyze.SyntacticAnalyzer')
@patch('analyze.GraphBuilder')
@patch('analyze.FileSummarizer')
@patch('analyze.SemanticAnalyzer')
@patch('analyze.Validator')
@patch('analyze.QuestionGenerator')
@patch('analyze.ReportBuilder')
def test_phase_2_static_analysis(
    mock_report_builder_cls,
    mock_question_gen_cls,
    mock_validator_cls,
    mock_semantic_cls,
    mock_file_sum_cls,
    mock_graph_cls,
    mock_syntactic_cls,
    mock_scanner_cls
):
    """Test Phase 2: Static analysis processes each file."""
    # Setup
    mock_scanner = mock_scanner_cls.return_value
    mock_files = [
        FileData(path="file1.swift", content="code1"),
        FileData(path="file2.swift", content="code2")
    ]
    mock_scanner.scan.return_value = mock_files

    mock_syntactic = mock_syntactic_cls.return_value
    mock_syntactic.analyze.return_value = []

    mock_graph = mock_graph_cls.return_value
    mock_graph.build_dependencies.return_value = {}

    mock_file_sum = mock_file_sum_cls.return_value
    mock_file_sum.summarize.return_value = FileSummary(
        file_path="test.swift",
        role="test",
        main_types=[],
        dependencies=[],
        responsibilities=[],
        suspicious_patterns=[]
    )

    mock_semantic = mock_semantic_cls.return_value
    mock_semantic.analyze.return_value = []

    mock_validator = mock_validator_cls.return_value
    mock_question_gen = mock_question_gen_cls.return_value
    mock_question_gen.generate.return_value = []

    mock_report_builder = mock_report_builder_cls.return_value
    mock_report_builder.build.return_value = AnalysisReport(
            summary="Test codebase summary",
            findings=[],
            questions=[],
            limitations=["Test limitation"]
        )

    # Run
    pipeline = AnalysisPipeline(repo_path=Path("test"), api_key="test-key")
    pipeline.run()

    # Verify syntactic analyzer called for each file
    assert mock_syntactic.analyze.call_count == 2
    mock_syntactic.analyze.assert_any_call("code1", "file1.swift")
    mock_syntactic.analyze.assert_any_call("code2", "file2.swift")

    # Verify graph builder called with all files
    mock_graph.build_dependencies.assert_called_once_with(mock_files)


# Test 7: Phase 3 - File summarization for each file
@patch('analyze.Scanner')
@patch('analyze.SyntacticAnalyzer')
@patch('analyze.GraphBuilder')
@patch('analyze.FileSummarizer')
@patch('analyze.SemanticAnalyzer')
@patch('analyze.Validator')
@patch('analyze.QuestionGenerator')
@patch('analyze.ReportBuilder')
def test_phase_3_file_summarization(
    mock_report_builder_cls,
    mock_question_gen_cls,
    mock_validator_cls,
    mock_semantic_cls,
    mock_file_sum_cls,
    mock_graph_cls,
    mock_syntactic_cls,
    mock_scanner_cls
):
    """Test Phase 3: File summarizer processes each file."""
    # Setup
    mock_scanner = mock_scanner_cls.return_value
    mock_files = [
        FileData(path="file1.swift", content="code1"),
        FileData(path="file2.swift", content="code2")
    ]
    mock_scanner.scan.return_value = mock_files

    mock_syntactic = mock_syntactic_cls.return_value
    mock_syntactic.analyze.return_value = []

    mock_graph = mock_graph_cls.return_value
    mock_graph.build_dependencies.return_value = {}

    mock_file_sum = mock_file_sum_cls.return_value
    mock_file_sum.summarize.return_value = FileSummary(
        file_path="test.swift",
        role="test",
        main_types=[],
        dependencies=[],
        responsibilities=[],
        suspicious_patterns=[]
    )

    mock_semantic = mock_semantic_cls.return_value
    mock_semantic.analyze.return_value = []

    mock_validator = mock_validator_cls.return_value
    mock_question_gen = mock_question_gen_cls.return_value
    mock_question_gen.generate.return_value = []

    mock_report_builder = mock_report_builder_cls.return_value
    mock_report_builder.build.return_value = AnalysisReport(
            summary="Test codebase summary",
            findings=[],
            questions=[],
            limitations=["Test limitation"]
        )

    # Run
    pipeline = AnalysisPipeline(repo_path=Path("test"), api_key="test-key")
    pipeline.run()

    # Verify FileSummarizer initialized with API key
    mock_file_sum_cls.assert_called_once_with(api_key="test-key")

    # Verify summarize called for each file
    assert mock_file_sum.summarize.call_count == 2
    mock_file_sum.summarize.assert_any_call("file1.swift", "code1")
    mock_file_sum.summarize.assert_any_call("file2.swift", "code2")


# Test 8: Phase 4 - Semantic analysis with summaries and findings
@patch('analyze.Scanner')
@patch('analyze.SyntacticAnalyzer')
@patch('analyze.GraphBuilder')
@patch('analyze.FileSummarizer')
@patch('analyze.SemanticAnalyzer')
@patch('analyze.Validator')
@patch('analyze.QuestionGenerator')
@patch('analyze.ReportBuilder')
def test_phase_4_semantic_analysis(
    mock_report_builder_cls,
    mock_question_gen_cls,
    mock_validator_cls,
    mock_semantic_cls,
    mock_file_sum_cls,
    mock_graph_cls,
    mock_syntactic_cls,
    mock_scanner_cls
):
    """Test Phase 4: Semantic analyzer receives summaries and static findings."""
    # Setup
    mock_scanner = mock_scanner_cls.return_value
    mock_files = [FileData(path="test.swift", content="code")]
    mock_scanner.scan.return_value = mock_files

    mock_syntactic = mock_syntactic_cls.return_value
    mock_static_findings = [
        StaticFinding(
            type="crash_risk",
            subtype="force_unwrap",
            file="test.swift",
            line=1,
            code_snippet="let x = y!"
        )
    ]
    mock_syntactic.analyze.return_value = mock_static_findings

    mock_graph = mock_graph_cls.return_value
    mock_deps = {"test.swift": ["Foundation"]}
    mock_graph.build_dependencies.return_value = mock_deps

    mock_file_sum = mock_file_sum_cls.return_value
    mock_summaries = [
        FileSummary(
            file_path="test.swift",
            role="test",
            main_types=["Test"],
            dependencies=["Foundation"],
            responsibilities=["testing"],
            suspicious_patterns=[]
        )
    ]
    mock_file_sum.summarize.return_value = mock_summaries[0]

    mock_semantic = mock_semantic_cls.return_value
    mock_semantic.analyze.return_value = []

    mock_validator = mock_validator_cls.return_value
    mock_question_gen = mock_question_gen_cls.return_value
    mock_question_gen.generate.return_value = []

    mock_report_builder = mock_report_builder_cls.return_value
    mock_report_builder.build.return_value = AnalysisReport(
            summary="Test codebase summary",
            findings=[],
            questions=[],
            limitations=["Test limitation"]
        )

    # Run
    pipeline = AnalysisPipeline(repo_path=Path("test"), api_key="test-key")
    pipeline.run()

    # Verify SemanticAnalyzer initialized with API key
    mock_semantic_cls.assert_called_once_with(api_key="test-key")

    # Verify analyze called with summaries, static findings, and dependencies
    mock_semantic.analyze.assert_called_once_with(
        file_summaries=mock_summaries,
        static_findings=mock_static_findings,
        dependency_graph=mock_deps
    )


# Test 9: Phase 5 - Validation filters findings
@patch('analyze.Scanner')
@patch('analyze.SyntacticAnalyzer')
@patch('analyze.GraphBuilder')
@patch('analyze.FileSummarizer')
@patch('analyze.SemanticAnalyzer')
@patch('analyze.Validator')
@patch('analyze.QuestionGenerator')
@patch('analyze.ReportBuilder')
def test_phase_5_validation(
    mock_report_builder_cls,
    mock_question_gen_cls,
    mock_validator_cls,
    mock_semantic_cls,
    mock_file_sum_cls,
    mock_graph_cls,
    mock_syntactic_cls,
    mock_scanner_cls
):
    """Test Phase 5: Validator filters semantic findings."""
    # Setup
    mock_scanner = mock_scanner_cls.return_value
    mock_scanner.scan.return_value = []

    mock_syntactic = mock_syntactic_cls.return_value
    mock_syntactic.analyze.return_value = []

    mock_graph = mock_graph_cls.return_value
    mock_graph.build_dependencies.return_value = {}

    mock_file_sum = mock_file_sum_cls.return_value

    mock_semantic = mock_semantic_cls.return_value
    mock_findings = [
        SemanticFinding(
            type="bug",
            location="test.swift:1",
            explanation="Force unwrap may crash",
            confidence="high",
            subtype="force_unwrap_crash_risk",
            severity="high",
            evidence="let x = y!",
            recommendation="Use optional binding instead"
        ),
        SemanticFinding(
            type="smell",
            location="test.swift:1",
            explanation="Class too large",
            confidence="medium",
            subtype="large_class",
            severity="medium",
            evidence="100+ methods",
            recommendation="Split into smaller classes"
        )
    ]
    mock_semantic.analyze.return_value = mock_findings

    mock_validator = mock_validator_cls.return_value
    # First finding valid, second invalid
    mock_validator.validate.side_effect = [True, False]

    mock_question_gen = mock_question_gen_cls.return_value
    mock_question_gen.generate.return_value = []

    mock_report_builder = mock_report_builder_cls.return_value
    mock_report_builder.build.return_value = AnalysisReport(
            summary="Test codebase summary",
            findings=[],
            questions=[],
            limitations=["Test limitation"]
        )

    # Run
    pipeline = AnalysisPipeline(repo_path=Path("test"), api_key="test-key")
    pipeline.run()

    # Verify Validator initialized with API key
    mock_validator_cls.assert_called_once_with(api_key="test-key")

    # Verify validate called for each finding
    assert mock_validator.validate.call_count == 2


# Test 10: Phase 6 - Question generation from validated findings
@patch('analyze.Scanner')
@patch('analyze.SyntacticAnalyzer')
@patch('analyze.GraphBuilder')
@patch('analyze.FileSummarizer')
@patch('analyze.SemanticAnalyzer')
@patch('analyze.Validator')
@patch('analyze.QuestionGenerator')
@patch('analyze.ReportBuilder')
def test_phase_6_question_generation(
    mock_report_builder_cls,
    mock_question_gen_cls,
    mock_validator_cls,
    mock_semantic_cls,
    mock_file_sum_cls,
    mock_graph_cls,
    mock_syntactic_cls,
    mock_scanner_cls
):
    """Test Phase 6: QuestionGenerator receives validated findings."""
    # Setup
    mock_scanner = mock_scanner_cls.return_value
    mock_scanner.scan.return_value = []

    mock_syntactic = mock_syntactic_cls.return_value
    mock_syntactic.analyze.return_value = []

    mock_graph = mock_graph_cls.return_value
    mock_graph.build_dependencies.return_value = {}

    mock_file_sum = mock_file_sum_cls.return_value

    mock_semantic = mock_semantic_cls.return_value
    mock_findings = [
        SemanticFinding(
            type="bug",
            location="test.swift:1",
            explanation="Force unwrap may crash",
            confidence="high",
            subtype="force_unwrap_crash_risk",
            severity="high",
            evidence="let x = y!",
            recommendation="Use optional binding instead"
        )
    ]
    mock_semantic.analyze.return_value = mock_findings

    mock_validator = mock_validator_cls.return_value
    mock_validator.validate.return_value = True

    mock_question_gen = mock_question_gen_cls.return_value
    mock_questions = ["Why force unwrap?"]
    mock_question_gen.generate.return_value = mock_questions

    mock_report_builder = mock_report_builder_cls.return_value
    mock_report_builder.build.return_value = AnalysisReport(
            summary="Test codebase summary",
            findings=[],
            questions=[],
            limitations=["Test limitation"]
        )

    # Run
    pipeline = AnalysisPipeline(repo_path=Path("test"), api_key="test-key")
    pipeline.run()

    # Verify QuestionGenerator initialized with API key
    mock_question_gen_cls.assert_called_once_with(api_key="test-key")

    # Verify generate called with validated findings
    mock_question_gen.generate.assert_called_once()
    call_args = mock_question_gen.generate.call_args[0][0]
    assert len(call_args) == 1  # Only valid finding


# Test 11: Phase 7 - Report building with all outputs
@patch('analyze.Scanner')
@patch('analyze.SyntacticAnalyzer')
@patch('analyze.GraphBuilder')
@patch('analyze.FileSummarizer')
@patch('analyze.SemanticAnalyzer')
@patch('analyze.Validator')
@patch('analyze.QuestionGenerator')
@patch('analyze.ReportBuilder')
def test_phase_7_report_building(
    mock_report_builder_cls,
    mock_question_gen_cls,
    mock_validator_cls,
    mock_semantic_cls,
    mock_file_sum_cls,
    mock_graph_cls,
    mock_syntactic_cls,
    mock_scanner_cls
):
    """Test Phase 7: ReportBuilder assembles final report."""
    # Setup
    mock_scanner = mock_scanner_cls.return_value
    mock_files = [FileData(path="test.swift", content="code")]
    mock_scanner.scan.return_value = mock_files

    mock_syntactic = mock_syntactic_cls.return_value
    mock_static_findings = [
        StaticFinding(
            type="crash_risk",
            subtype="force_unwrap",
            file="test.swift",
            line=1,
            code_snippet="let x = y!"
        )
    ]
    mock_syntactic.analyze.return_value = mock_static_findings

    mock_graph = mock_graph_cls.return_value
    mock_graph.build_dependencies.return_value = {}

    mock_file_sum = mock_file_sum_cls.return_value
    mock_file_sum.summarize.return_value = FileSummary(
        file_path="test.swift",
        role="test",
        main_types=[],
        dependencies=[],
        responsibilities=[],
        suspicious_patterns=[]
    )

    mock_semantic = mock_semantic_cls.return_value
    mock_validated_findings = [
        SemanticFinding(
            type="bug",
            location="test.swift:1",
            explanation="Force unwrap may crash",
            confidence="high",
            subtype="force_unwrap_crash_risk",
            severity="high",
            evidence="let x = y!",
            recommendation="Use optional binding instead"
        )
    ]
    mock_semantic.analyze.return_value = mock_validated_findings

    mock_validator = mock_validator_cls.return_value
    mock_validator.validate.return_value = True

    mock_question_gen = mock_question_gen_cls.return_value
    mock_questions = ["Why force unwrap?"]
    mock_question_gen.generate.return_value = mock_questions

    mock_report_builder = mock_report_builder_cls.return_value
    expected_report = AnalysisReport(
            summary="Test codebase summary",
            findings=mock_validated_findings,
            questions=mock_questions,
            limitations=["Test limitation"]
        )
    mock_report_builder.build.return_value = expected_report

    # Run
    pipeline = AnalysisPipeline(repo_path=Path("test"), api_key="test-key")
    result = pipeline.run()

    # Verify ReportBuilder.build called with correct parameters
    mock_report_builder.build.assert_called_once()
    call_kwargs = mock_report_builder.build.call_args[1]

    assert "findings" in call_kwargs
    assert "questions" in call_kwargs
    assert "summary" in call_kwargs

    assert call_kwargs["findings"] == mock_validated_findings
    assert call_kwargs["questions"] == mock_questions
    assert isinstance(call_kwargs["summary"], dict)


# Test 12: analyze() convenience function exists
def test_analyze_function_exists():
    """Test that analyze() convenience function is defined."""
    assert analyze is not None
    assert callable(analyze)


# Test 13: analyze() function accepts repo_path and api_key
@patch('analyze.AnalysisPipeline')
def test_analyze_function_parameters(mock_pipeline_cls):
    """Test that analyze() accepts repo_path and api_key parameters."""
    mock_pipeline = mock_pipeline_cls.return_value
    mock_pipeline.run.return_value = AnalysisReport(
            summary="Test codebase summary",
            findings=[],
            questions=[],
            limitations=["Test limitation"]
        )

    repo_path = Path("Sleep Journal")
    api_key = "test-key"

    result = analyze(repo_path=repo_path, api_key=api_key)

    # Verify AnalysisPipeline created with correct parameters
    mock_pipeline_cls.assert_called_once_with(repo_path=repo_path, api_key=api_key)
    mock_pipeline.run.assert_called_once()
    assert isinstance(result, AnalysisReport)


# Test 14: Pipeline handles empty repository
@patch('analyze.Scanner')
@patch('analyze.SyntacticAnalyzer')
@patch('analyze.GraphBuilder')
@patch('analyze.FileSummarizer')
@patch('analyze.SemanticAnalyzer')
@patch('analyze.Validator')
@patch('analyze.QuestionGenerator')
@patch('analyze.ReportBuilder')
def test_pipeline_handles_empty_repo(
    mock_report_builder_cls,
    mock_question_gen_cls,
    mock_validator_cls,
    mock_semantic_cls,
    mock_file_sum_cls,
    mock_graph_cls,
    mock_syntactic_cls,
    mock_scanner_cls
):
    """Test that pipeline handles repository with no Swift files."""
    # Setup
    mock_scanner = mock_scanner_cls.return_value
    mock_scanner.scan.return_value = []  # No files

    mock_syntactic = mock_syntactic_cls.return_value
    mock_graph = mock_graph_cls.return_value
    mock_graph.build_dependencies.return_value = {}

    mock_semantic = mock_semantic_cls.return_value
    mock_semantic.analyze.return_value = []

    mock_question_gen = mock_question_gen_cls.return_value
    mock_question_gen.generate.return_value = []

    mock_report_builder = mock_report_builder_cls.return_value
    mock_report_builder.build.return_value = AnalysisReport(
            summary="Test codebase summary",
            findings=[],
            questions=[],
            limitations=["Test limitation"]
        )

    # Run
    pipeline = AnalysisPipeline(repo_path=Path("empty"), api_key="test-key")
    result = pipeline.run()

    # Verify pipeline completes without errors
    assert isinstance(result, AnalysisReport)
    assert result.summary_stats["total_files"] == 0


# Test 15: Pipeline requires API key
def test_pipeline_requires_api_key():
    """Test that AnalysisPipeline requires api_key parameter."""
    with pytest.raises(TypeError):
        AnalysisPipeline(repo_path=Path("test"))  # Missing api_key

# Project Tasks

## Setup & Infrastructure

- [x] Set up project structure (core/, analyzers/, prompts/ directories) and create requirements.txt
- [x] Implement prompt_loader.py utility for loading and rendering prompt templates

## Phase 1: Codebase Scan

- [x] Implement scanner.py to discover Swift files, ignore build folders and .git

## Phase 2: Static Analysis

- [x] Implement syntactic_analyzer.py with tree-sitter Swift parser for detecting force unwraps, force try, singletons, large classes
- [x] Implement simplified graph_builder.py to extract import statements and class dependencies

## Phase 3: File Summarization (AI)

- [x] Create prompts/file_summarizer.txt prompt template with structured output schema
- [x] Implement file_summarizer.py to generate FileSummary dataclass from Swift files using LLM

## Phase 4: Repository Semantic Analysis (AI)

- [x] Create prompts/semantic_analyzer.txt prompt template for repo-level issue detection
- [x] Implement semantic_analyzer.py to detect bugs, smells, architecture issues, test gaps, doc gaps

## Phase 5: Validation (AI)

- [x] Create prompts/validator.txt with single context-aware validation prompt
- [x] Implement validator.py with single validation function that adapts based on finding type

## Phase 6: Question Generation (AI)

- [x] Create prompts/question_generator.txt for generating onboarding questions
- [x] Implement question_generator.py to synthesize questions from validated findings

## Phase 7: Report Generation & Main Entry Point

- [x] Implement report_builder.py to generate final JSON output with AnalysisReport schema
- [x] Implement analyze.py main entry point that orchestrates all 7 pipeline phases

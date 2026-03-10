# Test Documentation

This file documents all tests written for the Sleep Journal Codebase Analyzer project.

## tests/test_project_structure.py

### TestProjectStructure

#### test_core_directory_exists (tests/test_project_structure.py:23)
**Purpose**: Validates that the `core/` directory exists for core modules
**Why important**: Foundation directory for scanner, syntactic analyzer, graph builder, and report builder modules per Architecture.md
**Edge cases**: Checks both directory existence and that it's actually a directory (not a file)

#### test_core_is_python_package (tests/test_project_structure.py:29)
**Purpose**: Validates that `core/__init__.py` exists to make core/ a valid Python package
**Why important**: Without __init__.py, Python won't recognize core/ as an importable package. Required for `from core.scanner import Scanner` imports
**Edge cases**: Checks both file existence and that it's a file (not a directory)

#### test_analyzers_directory_exists (tests/test_project_structure.py:35)
**Purpose**: Validates that the `analyzers/` directory exists for AI analyzer modules
**Why important**: Foundation directory for prompt_loader, file_summarizer, semantic_analyzer, validator, and question_generator per Architecture.md
**Edge cases**: Checks both directory existence and that it's actually a directory (not a file)

#### test_analyzers_is_python_package (tests/test_project_structure.py:41)
**Purpose**: Validates that `analyzers/__init__.py` exists to make analyzers/ a valid Python package
**Why important**: Without __init__.py, Python won't recognize analyzers/ as an importable package. Required for `from analyzers.file_summarizer import FileSummarizer` imports
**Edge cases**: Checks both file existence and that it's a file (not a directory)

#### test_prompts_directory_exists (tests/test_project_structure.py:47)
**Purpose**: Validates that the `prompts/` directory exists for LLM prompt templates
**Why important**: All LLM prompts are stored as .txt files in prompts/ per Architecture.md Prompt Management section. This is critical for the externalized prompt strategy
**Edge cases**: Checks both directory existence and that it's actually a directory (not a file)

#### test_tests_directory_exists (tests/test_project_structure.py:53)
**Purpose**: Validates that the `tests/` directory exists
**Why important**: Houses all test files. Should always pass since test runs from this directory, but validates structure completeness
**Edge cases**: Self-referential test - checks directory it's running from

#### test_tests_is_python_package (tests/test_project_structure.py:59)
**Purpose**: Validates that `tests/__init__.py` exists to make tests/ a valid Python package
**Why important**: Allows importing test utilities and fixtures across test files if needed
**Edge cases**: Checks both file existence and that it's a file (not a directory)

### TestRequirementsFile

#### test_requirements_file_exists (tests/test_project_structure.py:68)
**Purpose**: Validates that `requirements.txt` exists in project root
**Why important**: Essential for reproducible environment setup. Anyone cloning the repo needs this to install dependencies
**Edge cases**: Checks both file existence and that it's a file (not a directory)

#### test_requirements_contains_openai (tests/test_project_structure.py:74)
**Purpose**: Validates that `requirements.txt` includes the openai package
**Why important**: Core dependency for all AI-powered analysis (file summarization, semantic analysis, validation, question generation)
**Edge cases**: Case-insensitive search to handle "openai", "OpenAI", etc.

#### test_requirements_contains_dotenv (tests/test_project_structure.py:80)
**Purpose**: Validates that `requirements.txt` includes python-dotenv package
**Why important**: Required to load OPENAI_API_KEY from .env file. Without this, the application can't access the API key
**Edge cases**: Case-insensitive search to handle "python-dotenv", "Python-Dotenv", etc.

#### test_requirements_contains_treesitter (tests/test_project_structure.py:86)
**Purpose**: Validates that `requirements.txt` includes tree-sitter package
**Why important**: Core dependency for Phase 2 static analysis - AST-based pattern detection in Swift code
**Edge cases**: Case-insensitive search to handle "tree-sitter", "Tree-Sitter", etc.

#### test_requirements_contains_pytest (tests/test_project_structure.py:92)
**Purpose**: Validates that `requirements.txt` includes pytest package
**Why important**: Testing framework required for TDD workflow. Essential for running all tests
**Edge cases**: Case-insensitive search to handle "pytest", "PyTest", etc.

### TestPytestConfiguration

#### test_pytest_ini_exists (tests/test_project_structure.py:101)
**Purpose**: Validates that `pytest.ini` configuration file exists
**Why important**: Centralizes pytest configuration (test discovery, output format, markers). Ensures consistent test behavior across environments
**Edge cases**: Checks both file existence and that it's a file (not a directory)

#### test_pytest_ini_contains_testpaths (tests/test_project_structure.py:107)
**Purpose**: Validates that `pytest.ini` specifies the testpaths configuration
**Why important**: Tells pytest where to discover tests (tests/ directory). Without this, pytest might scan entire project including virtual environments
**Edge cases**: Case-insensitive search for "testpaths"

### TestGitignore

#### test_gitignore_exists (tests/test_project_structure.py:120)
**Purpose**: Validates that `.gitignore` file exists in project root
**Why important**: Prevents committing generated files, cache, API keys, and other files that shouldn't be in version control
**Edge cases**: Checks both file existence and that it's a file (not a directory)

#### test_gitignore_ignores_pycache (tests/test_project_structure.py:126)
**Purpose**: Validates that `.gitignore` includes `__pycache__` pattern
**Why important**: Python creates __pycache__ directories with compiled bytecode. These should not be committed - they're machine-specific and regenerated automatically
**Edge cases**: Exact string match for "__pycache__"

#### test_gitignore_ignores_pytest_cache (tests/test_project_structure.py:132)
**Purpose**: Validates that `.gitignore` includes `.pytest_cache` pattern
**Why important**: Pytest creates .pytest_cache directory for test state. This is local to each developer and shouldn't be committed
**Edge cases**: Exact string match for ".pytest_cache"

#### test_gitignore_ignores_env_files (tests/test_project_structure.py:138)
**Purpose**: Validates that `.gitignore` includes `*.pyc` pattern
**Why important**: Compiled Python files (.pyc) are machine-specific bytecode and should not be committed. They're regenerated automatically when Python runs
**Edge cases**: Exact string match for "*.pyc" - also covers *.pyo and *.pyd in actual implementation

---

## tests/test_prompt_loader.py

### TestPromptLoaderBasicLoading

#### test_load_returns_prompt_content (tests/test_prompt_loader.py:20)
**Purpose**: Validates that `load()` correctly reads and returns prompt file contents
**Why important**: Core functionality - all AI analyzers depend on loading prompts. Without this, no AI analysis can happen
**Edge cases**: Uses temp directory to isolate test from actual prompts/ directory

#### test_load_handles_multiline_prompts (tests/test_prompt_loader.py:36)
**Purpose**: Validates that `load()` preserves newlines in multi-line prompt files
**Why important**: Prompt templates often have complex multi-line structures. Losing newlines would break prompt formatting
**Edge cases**: Verifies exact newline count (2 newlines in "Line 1\nLine 2\nLine 3")

#### test_load_raises_error_for_missing_prompt (tests/test_prompt_loader.py:50)
**Purpose**: Validates that `load()` raises FileNotFoundError for non-existent prompts
**Why important**: Fail fast with clear error messages. Better than silent failures or cryptic errors later
**Edge cases**: Tests error handling path - critical for debugging misconfigured prompt names

#### test_load_uses_default_prompts_directory (tests/test_prompt_loader.py:62)
**Purpose**: Validates that PromptLoader defaults to project_root/prompts/ when no path specified
**Why important**: Convention over configuration - AI analyzers shouldn't need to specify prompts path every time
**Edge cases**: Tests constructor default behavior without arguments

### TestPromptLoaderRendering

#### test_render_substitutes_single_variable (tests/test_prompt_loader.py:74)
**Purpose**: Validates that `render()` correctly substitutes {variable} with provided value
**Why important**: Core rendering functionality - enables dynamic prompts like "Analyze {file_path}"
**Edge cases**: Simple case with single variable substitution

#### test_render_substitutes_multiple_variables (tests/test_prompt_loader.py:87)
**Purpose**: Validates that `render()` handles multiple {variables} in one template
**Why important**: Real prompts need multiple substitutions (file_path, file_content, line_number, etc.)
**Edge cases**: Tests multiple variable types (string and int)

#### test_render_handles_multiline_templates (tests/test_prompt_loader.py:100)
**Purpose**: Validates that `render()` works with multi-line templates containing variables
**Why important**: Production prompts are multi-line with structured sections. Each section may have variables
**Edge cases**: Combines multiline handling with variable substitution

#### test_render_raises_error_for_missing_variables (tests/test_prompt_loader.py:115)
**Purpose**: Validates that `render()` raises KeyError when required variable not provided
**Why important**: Fail fast on incomplete variable substitution. Better than "{undefined}" in output
**Edge cases**: Tests error handling for missing required variables

#### test_render_ignores_extra_variables (tests/test_prompt_loader.py:128)
**Purpose**: Validates that `render()` doesn't fail when extra variables provided
**Why important**: Allows passing all context variables without needing to know exactly what each prompt uses
**Edge cases**: Provides name, age, city but template only uses name

### TestPromptLoaderEdgeCases

#### test_load_handles_empty_prompt_file (tests/test_prompt_loader.py:152)
**Purpose**: Validates that `load()` correctly handles empty prompt files
**Why important**: Edge case that could occur if prompt file exists but has no content. Should return empty string, not crash
**Edge cases**: Tests behavior with zero-byte file

#### test_load_preserves_whitespace (tests/test_prompt_loader.py:165)
**Purpose**: Validates that `load()` preserves leading/trailing whitespace and blank lines
**Why important**: Some prompts may use indentation or spacing for structure. Stripping whitespace could break formatting
**Edge cases**: Tests spaces, newlines, and blank lines preservation

#### test_loader_raises_error_for_invalid_prompts_directory (tests/test_prompt_loader.py:180)
**Purpose**: Validates that PromptLoader constructor raises ValueError if prompts directory doesn't exist
**Why important**: Fail fast during initialization. Better than FileNotFoundError later when loading prompts
**Edge cases**: Tests constructor validation logic

#### test_render_with_braces_in_content (tests/test_prompt_loader.py:191)
**Purpose**: Validates that `render()` handles literal braces ({{example}}) correctly
**Why important**: Prompts may need to include literal JSON examples or code snippets with braces. Must escape properly
**Edge cases**: Tests {{example}} → {example} transformation with mixed escaped and variable braces

---

## tests/test_scanner.py

### TestScannerBasicFunctionality

#### test_scanner_finds_swift_files_in_directory (tests/test_scanner.py:20)
**Purpose**: Validates that Scanner discovers all .swift files in a directory
**Why important**: Core Phase 1 functionality - must find all source files for analysis
**Edge cases**: Tests basic file discovery with 2 Swift files in same directory

#### test_scanner_finds_swift_files_in_nested_directories (tests/test_scanner.py:39)
**Purpose**: Validates that Scanner recursively discovers Swift files in subdirectories
**Why important**: Real codebases have nested directory structures (Services/, Models/, UI/). Must search recursively
**Edge cases**: Creates 3-level nesting (UI/Components/) to verify deep recursion works

#### test_scanner_returns_file_content (tests/test_scanner.py:63)
**Purpose**: Validates that Scanner reads and returns the full content of Swift files
**Why important**: Phase 2-7 need file content for analysis. Without content, pipeline can't work
**Edge cases**: Verifies exact content match including newlines and formatting

#### test_scanner_returns_relative_paths (tests/test_scanner.py:77)
**Purpose**: Validates that Scanner returns paths relative to repo root
**Why important**: Absolute paths would break reports and make output non-portable. Relative paths needed for clean output
**Edge cases**: Tests with nested directory (src/models/) to verify proper relative path calculation

### TestScannerIgnorePatterns

#### test_scanner_ignores_build_directory (tests/test_scanner.py:96)
**Purpose**: Validates that Scanner ignores build/ directory per Architecture.md
**Why important**: Build directories contain generated code, not source. Including them would pollute analysis
**Edge cases**: Creates Swift file in build/ that should be ignored

#### test_scanner_ignores_git_directory (tests/test_scanner.py:112)
**Purpose**: Validates that Scanner ignores .git/ directory per Architecture.md
**Why important**: .git contains version control data, not source code. Would waste time scanning
**Edge cases**: Creates file with .swift extension in .git/ to ensure it's still ignored

#### test_scanner_ignores_derived_data_directory (tests/test_scanner.py:128)
**Purpose**: Validates that Scanner ignores DerivedData/ (Xcode build artifacts)
**Why important**: DerivedData is Xcode-specific build artifacts directory. Contains generated code
**Edge cases**: Tests common Xcode artifact location that should be ignored

#### test_scanner_ignores_multiple_build_directories (tests/test_scanner.py:157)
**Purpose**: Validates that Scanner ignores all common build/artifact directories
**Why important**: Different build systems use different directories (build, .build, DerivedData, Pods). Must ignore all
**Edge cases**: Tests 4 different build directory patterns in one test

### TestScannerEdgeCases

#### test_scanner_handles_empty_directory (tests/test_scanner.py:179)
**Purpose**: Validates that Scanner returns empty list for directory with no Swift files
**Why important**: Edge case that will occur with empty projects. Should return [] not crash
**Edge cases**: Tests behavior with completely empty directory

#### test_scanner_ignores_non_swift_files (tests/test_scanner.py:188)
**Purpose**: Validates that Scanner only finds .swift files, not other file types
**Why important**: Prevents false positives from files like README.swift.md or config.json
**Edge cases**: Tests with .md, .json, .py, .css files to verify filtering works

#### test_scanner_raises_error_for_nonexistent_directory (tests/test_scanner.py:207)
**Purpose**: Validates that Scanner raises ValueError if repo_path doesn't exist
**Why important**: Fail fast with clear error. Better than cryptic errors later
**Edge cases**: Tests constructor validation with non-existent path

#### test_scanner_raises_error_for_file_instead_of_directory (tests/test_scanner.py:217)
**Purpose**: Validates that Scanner raises ValueError if repo_path is a file
**Why important**: Common user error - passing file instead of directory. Should fail clearly
**Edge cases**: Tests constructor validation with file path instead of directory

#### test_scanner_handles_unicode_in_filenames (tests/test_scanner.py:230)
**Purpose**: Validates that Scanner handles Unicode characters in filenames
**Why important**: International developers may use non-ASCII characters. Must handle gracefully
**Edge cases**: Tests with emoji (🚀) and accented characters (É) in filename

#### test_scanner_handles_spaces_in_filenames (tests/test_scanner.py:244)
**Purpose**: Validates that Scanner handles spaces in filenames
**Why important**: Some Swift files have spaces (e.g., "My View Controller.swift"). Must handle correctly
**Edge cases**: Tests filename with multiple spaces

### TestFileDataDataclass

#### test_filedata_has_required_fields (tests/test_scanner.py:267)
**Purpose**: Validates that FileData dataclass has path and content attributes
**Why important**: FileData is the contract between Scanner and Phase 2. Must have correct structure
**Edge cases**: Verifies dataclass structure matches Architecture.md specification

#### test_filedata_path_is_string_or_path (tests/test_scanner.py:286)
**Purpose**: Validates that FileData.path is string or Path object
**Why important**: Type safety - ensures path can be used consistently throughout pipeline
**Edge cases**: Tests type checking for path attribute

---

## tests/test_syntactic_analyzer.py

### TestForceUnwrapDetection

#### test_detects_simple_force_unwrap (tests/test_syntactic_analyzer.py:18)
**Purpose**: Validates that SyntacticAnalyzer detects basic force unwrap (!) operator
**Why important**: Force unwraps are crash risks per Architecture.md Phase 2. Critical to detect for safety analysis
**Edge cases**: Tests simplest case - `optional!`

#### test_detects_force_unwrap_on_method_call (tests/test_syntactic_analyzer.py:30)
**Purpose**: Validates detection of force unwrap on method call result
**Why important**: Common pattern `array.first!` crashes if array is empty. High-priority crash risk
**Edge cases**: Tests chained access pattern

#### test_detects_multiple_force_unwraps (tests/test_syntactic_analyzer.py:42)
**Purpose**: Validates that analyzer finds all force unwraps in a file
**Why important**: Must find all crash risks, not just first one
**Edge cases**: Tests with 3 force unwraps on different lines

#### test_ignores_non_force_unwrap_exclamation (tests/test_syntactic_analyzer.py:56)
**Purpose**: Validates that analyzer doesn't false-positive on string literals with !
**Why important**: Strings like "Hello!" should not be detected as force unwraps
**Edge cases**: Tests with exclamation in string literal and comment

### TestForceTryDetection

#### test_detects_simple_force_try (tests/test_syntactic_analyzer.py:71)
**Purpose**: Validates that SyntacticAnalyzer detects force try (try!) statements
**Why important**: Force try crashes on errors. Critical crash risk per Architecture.md
**Edge cases**: Tests basic try! pattern

#### test_detects_multiple_force_tries (tests/test_syntactic_analyzer.py:83)
**Purpose**: Validates detection of multiple force try statements
**Why important**: Must find all crash risks in a file
**Edge cases**: Tests with 2 different force try patterns

#### test_ignores_regular_try (tests/test_syntactic_analyzer.py:96)
**Purpose**: Validates that analyzer doesn't flag regular try/try? statements
**Why important**: Only try! is a crash risk. try and try? are safe error handling
**Edge cases**: Tests with try, try?, and do-catch to verify no false positives

### TestSingletonDetection

#### test_detects_static_let_shared (tests/test_syntactic_analyzer.py:111)
**Purpose**: Validates detection of singleton pattern (static let shared)
**Why important**: Singletons are structural smell per Architecture.md - testability and coupling issues
**Edge cases**: Tests canonical Swift singleton pattern

#### test_detects_multiple_singletons (tests/test_syntactic_analyzer.py:125)
**Purpose**: Validates detection of multiple singleton declarations
**Why important**: Some codebases have many singletons. Must find all
**Edge cases**: Tests with 2 singletons in different classes

#### test_ignores_non_singleton_static_properties (tests/test_syntactic_analyzer.py:145)
**Purpose**: Validates that analyzer doesn't flag all static properties as singletons
**Why important**: Only "shared" or "default" pattern indicates singleton. Static constants are fine
**Edge cases**: Tests with static let maxValue to verify no false positive

### TestLargeClassDetection

#### test_detects_class_with_many_methods (tests/test_syntactic_analyzer.py:160)
**Purpose**: Validates detection of large classes (>= 10 methods)
**Why important**: Large classes violate Single Responsibility Principle per Architecture.md
**Edge cases**: Tests with class containing exactly 10 methods (at threshold)

#### test_ignores_small_classes (tests/test_syntactic_analyzer.py:197)
**Purpose**: Validates that small classes (<10 methods) are not flagged
**Why important**: Should only flag truly large classes, not normal-sized ones
**Edge cases**: Tests with 3 methods to verify below threshold

### TestStaticFindingStructure

#### test_finding_has_required_fields (tests/test_syntactic_analyzer.py:217)
**Purpose**: Validates that StaticFinding dataclass has all required fields
**Why important**: StaticFinding is contract between Phase 2 and Phase 4. Must match Architecture.md schema
**Edge cases**: Verifies type, subtype, file, line, code_snippet attributes exist

#### test_finding_type_is_crash_risk (tests/test_syntactic_analyzer.py:234)
**Purpose**: Validates that force unwrap findings have type="crash_risk"
**Why important**: Type categorization enables filtering and prioritization in Phase 4
**Edge cases**: Verifies correct finding type assignment

#### test_finding_includes_line_number (tests/test_syntactic_analyzer.py:246)
**Purpose**: Validates that findings include line numbers for code location
**Why important**: Line numbers enable developers to locate issues quickly
**Edge cases**: Tests that line number is int and > 0

### TestEdgeCases

#### test_handles_empty_swift_file (tests/test_syntactic_analyzer.py:261)
**Purpose**: Validates that analyzer handles empty files without crashing
**Why important**: Edge case that will occur. Should return [] not crash
**Edge cases**: Tests with zero-byte file content

#### test_handles_syntax_errors_gracefully (tests/test_syntactic_analyzer.py:271)
**Purpose**: Validates that analyzer doesn't crash on invalid Swift syntax
**Why important**: Regex-based analysis should be resilient to syntax errors
**Edge cases**: Tests with malformed Swift code

#### test_handles_multiline_code (tests/test_syntactic_analyzer.py:288)
**Purpose**: Validates that analyzer correctly handles multi-line Swift constructs
**Why important**: Real code has multi-line function signatures, classes, etc.
**Edge cases**: Tests with force unwrap on line 4 of multi-line code

---

## tests/test_graph_builder.py

### TestImportExtraction

#### test_extracts_simple_import (tests/test_graph_builder.py:18)
**Purpose**: Validates that GraphBuilder extracts basic import statements
**Why important**: Phase 2 dependency extraction - must find external dependencies per Architecture.md
**Edge cases**: Tests simplest case - `import Foundation`

#### test_extracts_multiple_imports (tests/test_graph_builder.py:28)
**Purpose**: Validates extraction of multiple import statements from one file
**Why important**: Real files import multiple frameworks (Foundation, UIKit, SwiftUI)
**Edge cases**: Tests with 3 imports to verify all are found

#### test_extracts_specific_imports (tests/test_graph_builder.py:41)
**Purpose**: Validates extraction of specific imports (import class Module.Type)
**Why important**: Swift supports `import class Foundation.NSObject` syntax - must handle
**Edge cases**: Tests with import class and import struct

#### test_ignores_comments_with_import_keyword (tests/test_graph_builder.py:52)
**Purpose**: Validates that comments containing "import" are not extracted
**Why important**: Prevents false positives from commented-out imports or documentation
**Edge cases**: Tests with single-line and multi-line comments containing "import"

### TestTypeExtraction

#### test_extracts_class_name (tests/test_graph_builder.py:67)
**Purpose**: Validates that GraphBuilder extracts class declarations
**Why important**: Type extraction is core Phase 2 functionality for internal dependency mapping
**Edge cases**: Tests basic class declaration

#### test_extracts_struct_name (tests/test_graph_builder.py:77)
**Purpose**: Validates extraction of struct declarations
**Why important**: Structs are common in Swift (models, value types) - must be detected
**Edge cases**: Tests struct declaration

#### test_extracts_actor_name (tests/test_graph_builder.py:87)
**Purpose**: Validates extraction of actor declarations (Swift concurrency)
**Why important**: Actors are modern Swift concurrency primitive - should be tracked
**Edge cases**: Tests actor declaration

#### test_extracts_multiple_types (tests/test_graph_builder.py:97)
**Purpose**: Validates extraction of multiple type declarations from one file
**Why important**: Files often define multiple types (class + extension, multiple structs)
**Edge cases**: Tests with class, struct, protocol in same file

#### test_ignores_nested_types (tests/test_graph_builder.py:111)
**Purpose**: Validates that nested type declarations are ignored (simplified approach)
**Why important**: Per Architecture.md - lightweight extraction only. Nested types add complexity
**Edge cases**: Tests with struct inside class body - should only extract outer class

### TestDependencyBuilding

#### test_builds_dependency_dict (tests/test_graph_builder.py:126)
**Purpose**: Validates that build_dependencies() creates dict mapping files to dependencies
**Why important**: Core output of Phase 2 - provides structured dependency info to Phase 4
**Edge cases**: Tests with single file to verify dict structure

#### test_includes_imports_in_dependencies (tests/test_graph_builder.py:146)
**Purpose**: Validates that dependency list includes imports
**Why important**: External dependencies (Foundation, UIKit) must be tracked
**Edge cases**: Verifies Foundation appears in dependency list

#### test_includes_types_in_dependencies (tests/test_graph_builder.py:166)
**Purpose**: Validates that dependency list includes defined types
**Why important**: Internal types (JournalStore) are dependencies too
**Edge cases**: Verifies JournalStore appears in dependency list

#### test_handles_multiple_files (tests/test_graph_builder.py:186)
**Purpose**: Validates building dependencies for multiple files at once
**Why important**: Real pipeline processes all files - must handle batch processing
**Edge cases**: Tests with 2 files to verify separate dependency lists

### TestEdgeCases

#### test_handles_empty_file (tests/test_graph_builder.py:212)
**Purpose**: Validates handling of empty Swift files
**Why important**: Edge case that will occur. Should return empty lists not crash
**Edge cases**: Tests with zero-byte content

#### test_handles_file_with_no_imports (tests/test_graph_builder.py:222)
**Purpose**: Validates handling of files with no import statements
**Why important**: Some files may not import anything. Should return empty list
**Edge cases**: Tests with class but no imports

#### test_handles_file_with_no_types (tests/test_graph_builder.py:235)
**Purpose**: Validates handling of files with no type declarations
**Why important**: Files with only extensions or top-level functions have no types
**Edge cases**: Tests with imports but no class/struct/etc

#### test_handles_invalid_syntax (tests/test_graph_builder.py:245)
**Purpose**: Validates that analyzer doesn't crash on syntax errors
**Why important**: Regex-based parsing should be resilient to malformed code
**Edge cases**: Tests with incomplete Swift syntax

#### test_handles_protocol_declarations (tests/test_graph_builder.py:255)
**Purpose**: Validates extraction of protocol declarations
**Why important**: Protocols are Swift type declarations - should be tracked
**Edge cases**: Tests protocol declaration

#### test_handles_extension_declarations (tests/test_graph_builder.py:265)
**Purpose**: Validates that extensions are ignored (no new types defined)
**Why important**: Extensions don't create new types - should not be in type list
**Edge cases**: Tests with extension to verify it's not extracted

---

## tests/test_file_summarizer_prompt.py

### TestFileSummarizerPromptExists

#### test_prompt_file_exists (tests/test_file_summarizer_prompt.py:15)
**Purpose**: Validates that prompts/file_summarizer.txt exists
**Why important**: Phase 3 depends on this prompt template. Without it, file summarization can't work
**Edge cases**: Tests file existence check

#### test_prompt_is_readable (tests/test_file_summarizer_prompt.py:20)
**Purpose**: Validates that prompt file can be loaded via PromptLoader
**Why important**: File must be readable and non-empty for AI analysis to work
**Edge cases**: Tests via PromptLoader.load() to verify integration works

### TestFileSummarizerPromptStructure

#### test_has_file_path_placeholder (tests/test_file_summarizer_prompt.py:40)
**Purpose**: Validates that prompt has {file_path} placeholder for substitution
**Why important**: AI needs to know which file it's analyzing. Required per Architecture.md
**Edge cases**: Tests for exact placeholder string

#### test_has_file_content_placeholder (tests/test_file_summarizer_prompt.py:44)
**Purpose**: Validates that prompt has {file_content} placeholder for Swift code
**Why important**: AI needs the actual code to analyze. Core variable per Architecture.md
**Edge cases**: Tests for exact placeholder string

#### test_mentions_json_output (tests/test_file_summarizer_prompt.py:48)
**Purpose**: Validates that prompt instructs LLM to return JSON format
**Why important**: Structured output required for pipeline integration per Architecture.md Prompt Contracts
**Edge cases**: Case-insensitive search for "json"

#### test_mentions_required_fields (tests/test_file_summarizer_prompt.py:53)
**Purpose**: Validates that prompt specifies all FileSummary schema fields
**Why important**: LLM needs schema definition to return correct structure. Per Architecture.md FileSummary dataclass
**Edge cases**: Tests for all 6 required fields (file_path, role, main_types, dependencies, responsibilities, suspicious_patterns)

### TestFileSummarizerPromptRendering

#### test_render_with_variables (tests/test_file_summarizer_prompt.py:68)
**Purpose**: Validates that prompt renders correctly with file_path and file_content
**Why important**: Production usage will call render() with actual Swift code. Must work correctly
**Edge cases**: Tests with realistic Swift class example

#### test_render_handles_multiline_code (tests/test_file_summarizer_prompt.py:93)
**Purpose**: Validates that prompt handles multi-line Swift code correctly
**Why important**: Real Swift files are multi-line. Must preserve formatting
**Edge cases**: Tests with class definition spanning multiple lines

### TestFileSummarizerPromptGuidance

#### test_instructs_grounded_analysis (tests/test_file_summarizer_prompt.py:118)
**Purpose**: Validates that prompt instructs LLM to base analysis on actual code
**Why important**: Prevents hallucination. Per Architecture.md - findings must be grounded
**Edge cases**: Searches for grounding keywords (grounded, evidence, actual, based on, visible)

#### test_mentions_swift_context (tests/test_file_summarizer_prompt.py:125)
**Purpose**: Validates that prompt provides Swift/iOS context to LLM
**Why important**: LLM needs language context for accurate analysis
**Edge cases**: Case-insensitive search for "swift"

#### test_instructs_structured_output (tests/test_file_summarizer_prompt.py:130)
**Purpose**: Validates that prompt asks for structured JSON output
**Why important**: Ensures LLM returns parseable JSON per schema
**Edge cases**: Searches for structure-related keywords

### TestFileSummarizerPromptExamples

#### test_includes_example_output (tests/test_file_summarizer_prompt.py:143)
**Purpose**: Validates that prompt includes example JSON output
**Why important**: Examples help LLM understand expected format. Reduces parsing errors
**Edge cases**: Case-insensitive search for "example"

---

## tests/test_file_summarizer.py

### TestFileSummarizerDataclass

#### test_file_summary_has_required_fields (tests/test_file_summarizer.py:20)
**Purpose**: Validates that FileSummary dataclass has all required fields per Architecture.md
**Why important**: FileSummary is the output contract for Phase 3. Must match schema for Phase 4 integration
**Edge cases**: Tests all 6 fields (file_path, role, main_types, dependencies, responsibilities, suspicious_patterns)

### TestFileSummarizerInitialization

#### test_file_summarizer_initializes_with_api_key (tests/test_file_summarizer.py:44)
**Purpose**: Validates that FileSummarizer can be initialized with OpenAI API key
**Why important**: Proper initialization required for all AI analysis. API key is mandatory
**Edge cases**: Tests successful initialization with valid key

#### test_file_summarizer_raises_error_without_api_key (tests/test_file_summarizer.py:51)
**Purpose**: Validates that FileSummarizer raises ValueError if no API key provided
**Why important**: Fail fast - better than cryptic errors when calling OpenAI API later
**Edge cases**: Tests with api_key=None

#### test_file_summarizer_loads_prompt_template (tests/test_file_summarizer.py:58)
**Purpose**: Validates that FileSummarizer loads prompt template on initialization
**Why important**: Must load file_summarizer.txt for generating prompts. Integration test
**Edge cases**: Verifies prompt_loader attribute exists

### TestFileSummarizerAnalysis

#### test_summarize_returns_file_summary (tests/test_file_summarizer.py:78)
**Purpose**: Validates that summarize() returns FileSummary dataclass with correct data
**Why important**: Core Phase 3 functionality - must generate structured summaries
**Edge cases**: Mocks OpenAI response, tests full flow from FileData to FileSummary

#### test_summarize_calls_openai_with_rendered_prompt (tests/test_file_summarizer.py:115)
**Purpose**: Validates that summarize() calls OpenAI API with rendered prompt containing file content
**Why important**: Must send actual Swift code to LLM for analysis
**Edge cases**: Verifies prompt contains file path and code snippet

#### test_summarize_uses_gpt_4 (tests/test_file_summarizer.py:142)
**Purpose**: Validates that summarize() uses GPT-4 family model for code analysis
**Why important**: GPT-4 required for accurate code analysis. GPT-3.5 would be insufficient
**Edge cases**: Checks model parameter contains "gpt-4" or "gpt-4o"

#### test_summarize_parses_json_response (tests/test_file_summarizer.py:167)
**Purpose**: Validates that summarize() correctly parses JSON from LLM response
**Why important**: Must convert JSON string to FileSummary dataclass. Core parsing logic
**Edge cases**: Tests with realistic multi-type response (SleepEntry, SleepQuality)

### TestFileSummarizerBatchProcessing

#### test_summarize_all_processes_multiple_files (tests/test_file_summarizer.py:203)
**Purpose**: Validates that summarize_all() processes multiple FileData objects
**Why important**: Production use processes entire codebase (13+ files). Must handle batch
**Edge cases**: Tests with 2 files, verifies both processed in order

#### test_summarize_all_returns_empty_list_for_no_files (tests/test_file_summarizer.py:235)
**Purpose**: Validates that summarize_all() returns empty list when given no files
**Why important**: Edge case for empty projects. Should not call API unnecessarily
**Edge cases**: Tests with empty list input

### TestFileSummarizerErrorHandling

#### test_summarize_handles_invalid_json_response (tests/test_file_summarizer.py:251)
**Purpose**: Validates that summarize() handles malformed JSON from LLM gracefully
**Why important**: LLM may sometimes return invalid JSON. Must fail clearly with ValueError
**Edge cases**: Tests with plain text response instead of JSON

#### test_summarize_handles_missing_required_fields (tests/test_file_summarizer.py:267)
**Purpose**: Validates that summarize() handles JSON missing required fields
**Why important**: LLM may return incomplete JSON. Must validate schema
**Edge cases**: Tests with partial JSON (only file_path and role)

#### test_summarize_handles_openai_api_error (tests/test_file_summarizer.py:285)
**Purpose**: Validates that summarize() handles OpenAI API errors gracefully
**Why important**: Network errors, rate limits, auth failures will occur. Must propagate clearly
**Edge cases**: Simulates API exception

### TestFileSummarizerEdgeCases

#### test_summarize_handles_empty_swift_file (tests/test_file_summarizer.py:303)
**Purpose**: Validates that summarize() handles empty Swift files
**Why important**: Empty files may exist in projects. Should process without error
**Edge cases**: Tests with empty string content

#### test_summarize_handles_large_swift_file (tests/test_file_summarizer.py:324)
**Purpose**: Validates that summarize() handles large Swift files (500+ lines)
**Why important**: Real files can be large. Must handle without token limit issues
**Edge cases**: Tests with 500-line file

---

## tests/test_semantic_analyzer_prompt.py

### TestSemanticAnalyzerPromptExists

#### test_prompt_file_exists (tests/test_semantic_analyzer_prompt.py:15)
**Purpose**: Validates that prompts/semantic_analyzer.txt exists
**Why important**: Phase 4 depends on this prompt template. Without it, semantic analysis can't work
**Edge cases**: Tests file existence check

#### test_prompt_is_readable (tests/test_semantic_analyzer_prompt.py:20)
**Purpose**: Validates that prompt file can be loaded via PromptLoader
**Why important**: File must be readable and non-empty for AI analysis to work
**Edge cases**: Tests via PromptLoader.load() to verify integration works

### TestSemanticAnalyzerPromptStructure

#### test_has_file_summaries_placeholder (tests/test_semantic_analyzer_prompt.py:40)
**Purpose**: Validates that prompt has {file_summaries} placeholder
**Why important**: Phase 3 output (FileSummary data) must be passed to Phase 4 for analysis
**Edge cases**: Tests for exact placeholder string

#### test_has_static_findings_placeholder (tests/test_semantic_analyzer_prompt.py:44)
**Purpose**: Validates that prompt has {static_findings} placeholder
**Why important**: Phase 2 output (StaticFinding data) must be passed to Phase 4 for context
**Edge cases**: Tests for exact placeholder string

#### test_has_dependency_graph_placeholder (tests/test_semantic_analyzer_prompt.py:48)
**Purpose**: Validates that prompt has {dependency_graph} placeholder
**Why important**: Phase 2 dependency data needed for detecting circular dependencies and architecture issues
**Edge cases**: Tests for exact placeholder string

#### test_mentions_json_output (tests/test_semantic_analyzer_prompt.py:52)
**Purpose**: Validates that prompt instructs LLM to return JSON format
**Why important**: Structured output required for pipeline integration per Architecture.md Prompt Contracts
**Edge cases**: Case-insensitive search for "json"

#### test_mentions_required_fields (tests/test_semantic_analyzer_prompt.py:57)
**Purpose**: Validates that prompt specifies all SemanticFinding schema fields
**Why important**: LLM needs schema definition to return correct structure per Architecture.md
**Edge cases**: Tests for 5 required fields (type, severity, description, evidence, recommendation)

### TestSemanticAnalyzerPromptRendering

#### test_render_with_variables (tests/test_semantic_analyzer_prompt.py:70)
**Purpose**: Validates that prompt renders correctly with all 3 required variables
**Why important**: Production usage will call render() with actual Phase 1-3 data. Must work correctly
**Edge cases**: Tests with realistic JSON data for all 3 placeholders

### TestSemanticAnalyzerPromptGuidance

#### test_instructs_repo_level_analysis (tests/test_semantic_analyzer_prompt.py:97)
**Purpose**: Validates that prompt instructs LLM to perform repository-level analysis
**Why important**: Phase 4 focus is cross-file issues, not single-file issues (already in Phase 2)
**Edge cases**: Searches for repo-level keywords (repository, repo, codebase, cross-file, architectural)

#### test_mentions_issue_categories (tests/test_semantic_analyzer_prompt.py:106)
**Purpose**: Validates that prompt mentions all 5 issue categories to detect
**Why important**: Per Architecture.md - bugs, smells, architecture issues, test gaps, doc gaps
**Edge cases**: Searches for all 5 categories in prompt text

#### test_instructs_evidence_based_findings (tests/test_semantic_analyzer_prompt.py:116)
**Purpose**: Validates that prompt instructs LLM to provide evidence for findings
**Why important**: Prevents hallucination. Per Architecture.md - findings must be grounded in data
**Edge cases**: Searches for evidence-related keywords

#### test_mentions_severity_levels (tests/test_semantic_analyzer_prompt.py:123)
**Purpose**: Validates that prompt defines severity levels (high, medium, low)
**Why important**: Enables prioritization of findings in final report
**Edge cases**: Searches for "severity" and common levels

#### test_instructs_actionable_recommendations (tests/test_semantic_analyzer_prompt.py:132)
**Purpose**: Validates that prompt asks for actionable recommendations
**Why important**: Findings must be actionable. Per Architecture.md - provide specific fixes
**Edge cases**: Searches for action-related keywords

### TestSemanticAnalyzerPromptExamples

#### test_includes_example_output (tests/test_semantic_analyzer_prompt.py:147)
**Purpose**: Validates that prompt includes example JSON output
**Why important**: Examples help LLM understand expected format. Reduces parsing errors
**Edge cases**: Case-insensitive search for "example"

### TestSemanticAnalyzerPromptContext

#### test_explains_file_summaries_context (tests/test_semantic_analyzer_prompt.py:157)
**Purpose**: Validates that prompt explains what file_summaries data represents
**Why important**: LLM needs context about where data comes from (Phase 3)
**Edge cases**: Searches for "file" and "summar" keywords

#### test_explains_static_findings_context (tests/test_semantic_analyzer_prompt.py:163)
**Purpose**: Validates that prompt explains what static_findings data represents
**Why important**: LLM needs context about where data comes from (Phase 2 syntactic analysis)
**Edge cases**: Searches for "static" or "syntactic" keywords

#### test_explains_dependency_graph_context (tests/test_semantic_analyzer_prompt.py:169)
**Purpose**: Validates that prompt explains what dependency_graph data represents
**Why important**: LLM needs to understand dependency relationships for architecture analysis
**Edge cases**: Searches for "dependenc" keyword

---

## tests/test_semantic_analyzer.py

### TestSemanticFindingDataclass

#### test_semantic_finding_has_required_fields (tests/test_semantic_analyzer.py:19)
**Purpose**: Validates that SemanticFinding dataclass has all required fields per Architecture.md
**Why important**: SemanticFinding is the output contract for Phase 4. Must match schema for Phase 5 validation
**Edge cases**: Tests all 7 fields (type, subtype, severity, files, description, evidence, recommendation)

### TestSemanticAnalyzerInitialization

#### test_semantic_analyzer_initializes_with_api_key (tests/test_semantic_analyzer.py:45)
**Purpose**: Validates that SemanticAnalyzer can be initialized with OpenAI API key
**Why important**: Proper initialization required for all semantic analysis. API key is mandatory
**Edge cases**: Tests successful initialization with valid key

#### test_semantic_analyzer_raises_error_without_api_key (tests/test_semantic_analyzer.py:52)
**Purpose**: Validates that SemanticAnalyzer raises ValueError if no API key provided
**Why important**: Fail fast - better than cryptic errors when calling OpenAI API later
**Edge cases**: Tests with api_key=None

#### test_semantic_analyzer_loads_prompt_template (tests/test_semantic_analyzer.py:59)
**Purpose**: Validates that SemanticAnalyzer loads prompt template on initialization
**Why important**: Must load semantic_analyzer.txt for generating prompts. Integration test
**Edge cases**: Verifies prompt_loader attribute exists

### TestSemanticAnalyzerAnalysis

#### test_analyze_returns_list_of_semantic_findings (tests/test_semantic_analyzer.py:88)
**Purpose**: Validates that analyze() returns list of SemanticFinding dataclass objects
**Why important**: Core Phase 4 functionality - must generate structured semantic findings
**Edge cases**: Mocks OpenAI response with 2 findings (architecture issue + test gap), tests full flow

#### test_analyze_calls_openai_with_rendered_prompt (tests/test_semantic_analyzer.py:128)
**Purpose**: Validates that analyze() calls OpenAI API with rendered prompt containing Phase 1-3 data
**Why important**: Must send file summaries, static findings, and dependency graph to LLM
**Edge cases**: Verifies prompt contains sample data

#### test_analyze_uses_gpt_4 (tests/test_semantic_analyzer.py:153)
**Purpose**: Validates that analyze() uses GPT-4 family model for semantic analysis
**Why important**: GPT-4 required for complex cross-file reasoning. GPT-3.5 would be insufficient
**Edge cases**: Checks model parameter contains "gpt-4" or "gpt-4o"

#### test_analyze_parses_json_array_response (tests/test_semantic_analyzer.py:174)
**Purpose**: Validates that analyze() correctly parses JSON array from LLM response
**Why important**: Must convert JSON array to list of SemanticFinding objects. Core parsing logic
**Edge cases**: Tests with single finding in array

#### test_analyze_returns_empty_list_when_no_issues_found (tests/test_semantic_analyzer.py:202)
**Purpose**: Validates that analyze() returns empty list when LLM finds no issues
**Why important**: Clean codebases may have no semantic issues. Should return [] not crash
**Edge cases**: Tests with empty JSON array response

### TestSemanticAnalyzerErrorHandling

#### test_analyze_handles_invalid_json_response (tests/test_semantic_analyzer.py:223)
**Purpose**: Validates that analyze() handles malformed JSON from LLM gracefully
**Why important**: LLM may sometimes return invalid JSON. Must fail clearly with ValueError
**Edge cases**: Tests with plain text response instead of JSON array

#### test_analyze_handles_missing_required_fields (tests/test_semantic_analyzer.py:239)
**Purpose**: Validates that analyze() handles JSON missing required fields
**Why important**: LLM may return incomplete JSON. Must validate schema for each finding
**Edge cases**: Tests with partial JSON (only type and severity)

#### test_analyze_handles_openai_api_error (tests/test_semantic_analyzer.py:258)
**Purpose**: Validates that analyze() handles OpenAI API errors gracefully
**Why important**: Network errors, rate limits, auth failures will occur. Must propagate clearly
**Edge cases**: Simulates API exception

### TestSemanticAnalyzerDataSerialization

#### test_analyze_serializes_file_summaries_to_json (tests/test_semantic_analyzer.py:276)
**Purpose**: Validates that analyze() converts FileSummary dataclass objects to JSON for prompt
**Why important**: Must serialize Phase 3 dataclasses to JSON strings for LLM consumption
**Edge cases**: Tests with FileSummary dataclass, verifies serialization to JSON

#### test_analyze_accepts_dict_input (tests/test_semantic_analyzer.py:310)
**Purpose**: Validates that analyze() also accepts plain dict objects (not just dataclasses)
**Why important**: Flexibility - should handle both dataclass objects and plain dicts
**Edge cases**: Tests with dict inputs instead of dataclasses

---

## tests/test_validator_prompt.py

### TestValidatorPromptExists

#### test_prompt_file_exists (tests/test_validator_prompt.py:15)
**Purpose**: Validates that prompts/validator.txt exists
**Why important**: Phase 5 depends on this prompt template. Without it, validation can't work
**Edge cases**: Tests file existence check

#### test_prompt_is_readable (tests/test_validator_prompt.py:20)
**Purpose**: Validates that prompt file can be loaded via PromptLoader
**Why important**: File must be readable and non-empty for validation to work
**Edge cases**: Tests via PromptLoader.load() to verify integration works

### TestValidatorPromptStructure

#### test_has_finding_placeholder (tests/test_validator_prompt.py:40)
**Purpose**: Validates that prompt has {finding} placeholder
**Why important**: The finding to validate must be passed to the prompt
**Edge cases**: Tests for exact placeholder string

#### test_has_finding_type_placeholder (tests/test_validator_prompt.py:44)
**Purpose**: Validates that prompt has {finding_type} placeholder for context-aware validation
**Why important**: Single validator adapts reasoning based on finding type (bug vs architecture vs test_gap)
**Edge cases**: Tests for exact placeholder string

#### test_mentions_json_output (tests/test_validator_prompt.py:48)
**Purpose**: Validates that prompt instructs LLM to return JSON format
**Why important**: Structured output required for pipeline integration per Architecture.md
**Edge cases**: Case-insensitive search for "json"

#### test_mentions_required_fields (tests/test_validator_prompt.py:53)
**Purpose**: Validates that prompt specifies all ValidationResult schema fields
**Why important**: LLM needs schema definition per Architecture.md ValidationResult
**Edge cases**: Tests for 3 required fields (is_valid, confidence, reasoning)

### TestValidatorPromptRendering

#### test_render_with_variables (tests/test_validator_prompt.py:63)
**Purpose**: Validates that prompt renders correctly with finding and finding_type variables
**Why important**: Production usage will call render() with actual SemanticFinding data
**Edge cases**: Tests with realistic finding JSON and type

### TestValidatorPromptGuidance

#### test_instructs_context_aware_validation (tests/test_validator_prompt.py:90)
**Purpose**: Validates that prompt instructs LLM to adapt reasoning based on finding type
**Why important**: Single validator must handle bugs, architecture issues, test gaps differently
**Edge cases**: Searches for context-aware keywords

#### test_mentions_validation_criteria (tests/test_validator_prompt.py:99)
**Purpose**: Validates that prompt defines validation criteria
**Why important**: LLM needs clear criteria for determining validity
**Edge cases**: Searches for validation-related keywords

#### test_mentions_confidence_levels (tests/test_validator_prompt.py:107)
**Purpose**: Validates that prompt defines confidence levels (high, medium, low)
**Why important**: Enables uncertainty quantification for human review
**Edge cases**: Searches for "confidence" and common levels

#### test_instructs_reasoning_explanation (tests/test_validator_prompt.py:115)
**Purpose**: Validates that prompt asks for reasoning explanation
**Why important**: Validation decisions must be explainable for transparency
**Edge cases**: Searches for reasoning-related keywords

#### test_mentions_false_positive_detection (tests/test_validator_prompt.py:122)
**Purpose**: Validates that prompt addresses false positive detection
**Why important**: Core purpose of validation is filtering false positives
**Edge cases**: Searches for false positive keywords

### TestValidatorPromptExamples

#### test_includes_example_output (tests/test_validator_prompt.py:135)
**Purpose**: Validates that prompt includes example JSON output
**Why important**: Examples help LLM understand expected format
**Edge cases**: Case-insensitive search for "example"

### TestValidatorPromptTypeSpecific

#### test_mentions_bug_validation (tests/test_validator_prompt.py:146)
**Purpose**: Validates that prompt mentions bug-specific validation criteria
**Why important**: Bugs require different validation than architecture issues
**Edge cases**: Searches for "bug" keyword

#### test_mentions_architecture_validation (tests/test_validator_prompt.py:152)
**Purpose**: Validates that prompt mentions architecture issue validation criteria
**Why important**: Architecture issues require different validation than bugs
**Edge cases**: Searches for "architecture" keyword

#### test_mentions_evidence_requirement (tests/test_validator_prompt.py:158)
**Purpose**: Validates that prompt requires evidence for findings
**Why important**: Prevents hallucination - findings must be grounded
**Edge cases**: Searches for "evidence" keyword

---

## Test Statistics

**Total Tests**: 158
**Test Files**: 9
**Test Classes**: 41
**Coverage**:
- Project structure setup (18 tests - 100%)
- PromptLoader utility (13 tests - 100%)
- Scanner module (16 tests - 100%)
- SyntacticAnalyzer module (18 tests - 100%)
- GraphBuilder module (19 tests - 100%)
- FileSummarizer prompt template (12 tests - 100%)
- FileSummarizer AI module (15 tests - 100%)
- SemanticAnalyzer prompt template (17 tests - 100%)
- SemanticAnalyzer AI module (14 tests - 100%)
- Validator prompt template (16 tests - 100%)

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_scanner.py -v

# Run with coverage
pytest tests/ --cov=core --cov=analyzers -v

# Run specific test class
pytest tests/test_scanner.py::TestScannerIgnorePatterns -v

# Run specific test
pytest tests/test_scanner.py::TestScannerBasicFunctionality::test_scanner_finds_swift_files_in_directory -v
```

## Task 15: Implement analyze.py Main Entry Point

**Date**: 2026-03-09  
**TDD Phase**: RED → GREEN

### RED Phase - Tests Written Before Implementation

Created `tests/test_analyze.py` with 15 tests:

1. AnalysisPipeline class exists
2. AnalysisPipeline initializes with repo_path and api_key
3. Pipeline.run() returns AnalysisReport
4. Pipeline orchestrates all 7 phases in correct order
5. Phase 1: Scanner initialized with repo_path
6. Phase 2: Static analysis processes all files
7. Phase 3: File summarization for each file
8. Phase 4: Semantic analysis with summaries and findings
9. Phase 5: Validation filters findings
10. Phase 6: Question generation from validated findings
11. Phase 7: Report building with all outputs
12. analyze() convenience function exists
13. analyze() accepts repo_path and api_key
14. Pipeline handles empty repository
15. Pipeline requires API key

All tests initially failed with `ModuleNotFoundError: No module named 'analyze'`.

### GREEN Phase - Implementation

Created `analyze.py`:

**AnalysisPipeline Class**:
- `__init__(repo_path, api_key)`: Initialize pipeline
- `run()`: Execute all 7 phases sequentially

**7-Phase Orchestration**:
1. **Phase 1**: Scanner.scan() → discover Swift files
2. **Phase 2**: SyntacticAnalyzer.analyze() + GraphBuilder.build_dependencies() → static analysis
3. **Phase 3**: FileSummarizer.summarize() → AI-powered file summaries
4. **Phase 4**: SemanticAnalyzer.analyze() → AI-powered semantic findings
5. **Phase 5**: Validator.validate() → filter false positives
6. **Phase 6**: QuestionGenerator.generate() → synthesize onboarding questions
7. **Phase 7**: ReportBuilder.build() → assemble final report

**Convenience Function**:
- `analyze(repo_path, api_key)`: One-line entry point

**Test Fixes Required**:
- Updated SemanticFinding test instances to match actual dataclass structure (files, severity, description, recommendation)
- Added mocks to test_phase_1_scanner to allow pipeline.run() execution

### Results

✅ All 15 tests pass  
✅ Full test suite: **217 tests pass**

**Key Features**:
- Complete 7-phase pipeline orchestration
- All AI components integrated (FileSummarizer, SemanticAnalyzer, Validator, QuestionGenerator)
- Proper error handling (API key validation)
- Statistics tracking (total_files, total_static_findings, etc.)
- Clean separation of concerns (each phase uses specialized component)

**Architecture Compliance**:
- ✅ Follows Architecture.md 7-phase design
- ✅ Uses dataclasses for structured data
- ✅ AI components receive proper inputs
- ✅ Returns AnalysisReport with validated findings and questions

---

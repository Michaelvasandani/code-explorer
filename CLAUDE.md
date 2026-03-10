# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **AI-assisted codebase analysis tool** for iOS projects. It analyzes the Sleep Journal sample iOS app to generate structured insights about architecture, bugs, code smells, and onboarding questions. This is a take-home assignment project with a 4-5 hour timebox.

**Goal**: Help engineers quickly understand an existing codebase through automated analysis, not fix/refactor the code.

## Development Philosophy

### Senior Engineer Mindset
**CRITICAL**: AI agents working in this codebase MUST operate as senior engineers would:
- Think before coding - understand the problem deeply first
- Write clean, maintainable, well-documented code
- Consider edge cases and error handling proactively
- Make deliberate architectural decisions with clear reasoning
- Prioritize code quality over speed

### Strict Test-Driven Development (TDD)
**MANDATORY**: All implementation MUST follow test-driven development:
1. **Tests first, always**: Write tests BEFORE writing any implementation code
2. Use `/test-driven-development` slash command when starting any feature or bugfix
3. Use `/pytest-best-practices` slash command for guidance on writing high-quality tests
4. No code is complete without corresponding tests
5. Tests must be meaningful and validate actual behavior, not just achieve coverage

### Available Slash Commands
- `/test-driven-development` - Guidance for implementing features/bugfixes with TDD approach
- `/pytest-best-practices` - Expert guidance for writing high-quality pytest tests (fixtures, parametrization, mocking)

## Protected Files (READ-ONLY)

**DO NOT MODIFY**: The following directories contain the sample iOS codebase being analyzed and must NEVER be edited:
- `Sleep Journal/` - The sample iOS app (analysis target)
- `Sleep Journal.xcodeproj/` - Xcode project files

These files are the subject of analysis, not part of the analysis tool implementation.

## Task Management Workflow

### Task Tracking
- **ALWAYS** check `todo.md` for the current list of tasks before starting work
- Tasks are listed in priority order
- Mark tasks as complete in `todo.md` immediately after finishing them
- If `todo.md` doesn't exist yet, create it to track all implementation tasks

### Test Documentation
- **REQUIRED**: Maintain a `test.md` file documenting all tests written
- For each test, document:
  - Test name and location (file:line)
  - What behavior it validates
  - Why this test is important
  - Any special setup or edge cases covered
- Update `test.md` immediately after writing each test

### Workflow for Each Task

**STRICT ORDER** - follow these steps for every task:

1. **Check todo.md**: Identify the next task to work on
2. **Run `/test-driven-development`**: Get TDD guidance for the task
3. **Write tests first**:
   - Use `/pytest-best-practices` for test design guidance
   - Write comprehensive tests covering the functionality
   - Ensure tests fail initially (red phase)
   - Document each test in `test.md`
4. **Implement code**: Write minimal code to make tests pass (green phase)
5. **Refactor**: Improve code quality while keeping tests green
6. **Verify**: Run full test suite to ensure nothing broke
7. **Document**: Update `test.md` with any additional test details
8. **Mark complete**: Check off the task in `todo.md`

**Example todo.md format**:
```markdown
# Project Tasks

- [ ] Implement file scanner for Swift files
- [ ] Add static analysis for force unwraps
- [ ] Create file summarization with AI
- [x] Set up project structure
```

**Example test.md format**:
```markdown
# Test Documentation

## test_scanner_finds_swift_files (tests/test_scanner.py:15)
**Purpose**: Validates that the scanner correctly discovers all .swift files in a directory tree
**Why important**: Core functionality - scanner must find all source files for analysis
**Edge cases**: Handles nested directories, ignores build folders, handles empty directories

## test_scanner_ignores_git_directory (tests/test_scanner.py:28)
**Purpose**: Ensures .git directory is excluded from scanning
**Why important**: Performance - don't scan version control internals
**Edge cases**: Tests both .git as file and directory
```

## Key Architecture

### Analysis Pipeline (7 Phases)
1. **Codebase Scan**: Discover Swift files using `core/scanner.py`
2. **Static Analysis**: Detect structural patterns with tree-sitter (`core/syntactic_analyzer.py`)
3. **File Summarization**: AI-powered summaries via `analyzers/file_summarizer.py`
4. **Semantic Analysis**: AI-based logical issue detection (`analyzers/semantic_analyzer.py`)
5. **Validation**: Specialized validators by finding type (`analyzers/validator.py`)
6. **Question Generation**: Generate onboarding questions (`analyzers/question_generator.py`)
7. **Report Generation**: Output JSON report (`core/report_builder.py`)

### Finding Types
- `bug`: Potential crashes or logical errors
- `smell`: Maintainability issues
- `architecture`: Layer violations, mixed patterns
- `test_gap`: Missing critical tests
- `documentation_gap`: Undocumented APIs
- `uncertainty`: Low-confidence concerns

### Validation Strategy
Uses **one main semantic analysis pass** + **specialized validation prompts** (not separate agents for each finding type). Different validators for bugs, smells, test gaps, doc gaps, and uncertainties.

## Sample Codebase: Sleep Journal

The target iOS app being analyzed lives in [Sleep Journal/](Sleep Journal/):

### Structure
- **Models**: [SleepEntry.swift](Sleep Journal/Models/SleepEntry.swift) - Core data models (SleepEntry, SleepQuality, DailyMood, SleepTag, WeatherSnapshot)
- **Services**:
  - [JournalStore.swift](Sleep Journal/Services/JournalStore.swift) - UserDefaults persistence (has force-try on line 24)
  - [WeatherClient.swift](Sleep Journal/Services/WeatherClient.swift) - weather.gov API client (force unwrap on line 30)
  - [LocationProvider.swift](Sleep Journal/Services/LocationProvider.swift) - CoreLocation wrapper
  - [WeatherCacheStore.swift](Sleep Journal/Services/WeatherCacheStore.swift) - Weather caching
- **ViewModels**: [SleepListViewModel.swift](Sleep Journal/ViewModels/SleepListViewModel.swift) - List filtering/search logic
- **UI**: Mixed UIKit + SwiftUI
  - [SleepJournalListViewController.swift](Sleep Journal/UI/SleepJournalListViewController.swift) - UIKit table view
  - [SleepEntryFormView.swift](Sleep Journal/UI/SleepEntryFormView.swift) - SwiftUI form
  - [SleepTrendsView.swift](Sleep Journal/UI/SleepTrendsView.swift) - SwiftUI charts
  - [SleepSettingsViewController.swift](Sleep Journal/UI/SleepSettingsViewController.swift) - UIKit settings

### Known Patterns in Sleep Journal
- **Mixed architecture**: UIKit + SwiftUI hybrid (ContentView wraps UIKit navigation)
- **Singleton pattern**: JournalStore.shared, WeatherCacheStore.shared
- **Force unwraps**: WeatherClient line 30 (`periods.first!`), JournalStore line 24 (`try! decoder.decode`)
- **Direct service access**: Views/ViewControllers access stores directly, bypassing some MVVM patterns
- **No tests**: Critical persistence logic is untested

## Development Commands

The analyzer tool is built with Python. Common commands:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the analyzer on Sleep Journal
python analyze.py "Sleep Journal"

# Run with output to file
python analyze.py "Sleep Journal" --output report.json
```

## Implementation Notes

### Module Implementation Order
Follow this order when building/modifying:
1. scanner.py
2. syntactic_analyzer.py
3. graph_builder.py
4. file_summarizer.py
5. semantic_analyzer.py
6. validator.py
7. question_generator.py
8. report_builder.py
9. analyze.py (main entry point)

### AI Usage Guidelines
- Use AI **only** for semantic reasoning (file summarization, semantic analysis, validation, question generation)
- Use **traditional techniques** for structural analysis (tree-sitter, regex, graph building)
- Keep prompts focused on specific finding types during validation
- Prefer fewer high-confidence findings over many weak ones

### Validation Routing
Route findings to specialized validators:
- Bugs → validate crash risk and control flow
- Smells/Architecture → validate design concerns
- Test gaps → validate criticality
- Doc gaps → validate onboarding impact
- Uncertainties → determine if actionable

## Output Format

The tool produces a JSON report with:
- `high_level_summary`: Architecture pattern, key components, primary risks
- `findings`: List of validated issues with type, location, confidence, explanation
- `questions`: Onboarding questions with context
- `tool_limitations`: Known constraints
- `metadata`: Analysis info

## Project Constraints

### What the tool does NOT do:
- Compile or execute code
- Run tests
- Parse Xcode project settings
- Detect performance/memory issues
- Perform deep static analysis like a compiler

### Design principles:
- No RAG/vector DB (codebase is small enough)
- No multi-agent swarm (single semantic pass + validators)
- Target runtime: 30-60 seconds
- Designed for small-to-medium iOS codebases (~15 files, ~2000 LOC)

## Reference Documentation

See [docs/Architecture.md](docs/Architecture.md) for detailed pipeline design, validation strategies, and data schemas.

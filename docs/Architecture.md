# AI-Assisted iOS Codebase Analysis Tool

**Last updated:** March 10, 2026
**Status:** Implementation complete with schema updates

> **Note on Schema Updates**: This document has been updated to reflect the actual implementation. Some schemas were simplified during development to match README.md assignment requirements:
> - **Questions**: Simplified from structured `Question` dataclass to `List[str]`
> - **Summary**: Changed from `dict` to simple `str`
> - **Limitations**: Changed from `dict` to `List[str]`
> - **Findings**: Added `severity` and `recommendation` bonus fields
> - **Metrics**: Added for tracking API usage, tokens, and cost
>
> These changes improved clarity and met assignment requirements while maintaining the core 7-phase architecture.

---

## Project
Sleep Journal Codebase Analyzer

## Scope
Analyze a small iOS codebase (~15 Swift files, ~2000 LOC) and generate a structured report that helps engineers quickly understand:

- architecture
- potential risks
- code smells
- likely bug patterns
- questions to ask before making changes

This tool is **not a compiler, linter, or correctness verifier**.  
Its purpose is **codebase understanding and onboarding acceleration**.

---

# Design Goals

1. **Use traditional analysis for structure**
2. **Use AI for semantic reasoning**
3. **Avoid unnecessary complexity**
4. **Produce grounded findings**
5. **Keep architecture simple enough for a small repo**
6. **Use specialized validation prompts where they add value**

---

# Non-Goals

The tool intentionally does **not** attempt to:

- compile or execute the app
- run tests
- parse Xcode project settings
- detect performance issues
- detect memory leaks
- detect UI/UX problems
- perform deep static analysis like a full Swift compiler

No RAG, vector DB, or persistent indexing is implemented because the repository is small.

No full multi-agent swarm is implemented. The system uses **one main semantic analysis pass**, followed by **a single context-aware validation prompt**.

---

# High-Level Pipeline

1. Scan Codebase  
2. Static Analysis  
3. File Summarization (AI)  
4. Repository Semantic Analysis (AI)  
5. Validation  
6. Question Generation (AI)  
7. Report Generation  

Total runtime target: **~30-60 seconds**

---

# Pipeline Phases

## Phase 1 — Codebase Scan

Purpose:  
Discover Swift source files.

Implementation:
`core/scanner.py`

Input:
`repo_path: str`

Output:

```python
@dataclass
class FileData:
    path: str
    content: str
````

Rules:

* only scan `*.swift`
* ignore build folders
* ignore `.git`

---

## Phase 2 — Static Analysis

Purpose:
Detect **structural patterns and syntactic risk signals**.

No AI is used here.

Implementation:

* `core/syntactic_analyzer.py`
* `core/graph_builder.py`

Techniques:

* Tree-sitter Swift parser for AST-based pattern detection
* regex for simple pattern matching
* simplified dependency extraction (import statements, class references)

Outputs:

```python
@dataclass
class StaticFinding:
    type: str
    subtype: str
    file: str
    line: int
    code_snippet: str
```

Detected patterns include:

### Crash Risks

* force unwrap (`!`)
* force try (`try!`)

### Structural Smells

* singleton usage (`static let shared`)
* large classes (method count heuristic)

### Architectural Signals

* direct store or service access from UI layer
* mixed UIKit + SwiftUI

### Documentation Signals

* public methods without doc comments

These findings are **candidates**, not final validated issues.

---

## Phase 3 — File Summarization (AI)

Purpose:
Create structured summaries for each file so the semantic pass can reason about the repo.

Implementation:
`analyzers/file_summarizer.py`

Input:

* `file_path`
* `file_content`

Output:

```python
@dataclass
class FileSummary:
    file_path: str
    role: str
    main_types: list[str]
    dependencies: list[str]
    responsibilities: list[str]
    suspicious_patterns: list[str]
```

Example:

```json
{
  "file_path": "Services/JournalStore.swift",
  "role": "data persistence service",
  "main_types": ["JournalStore"],
  "dependencies": ["UserDefaults", "JSONDecoder", "SleepEntry"],
  "responsibilities": [
    "persist sleep entries",
    "load entries on launch",
    "export entries as JSON"
  ],
  "suspicious_patterns": [
    "force try decoding"
  ]
}
```

Reason for summaries instead of raw code:

* reduces prompt noise
* enables repo-level reasoning
* scales better than dumping raw code

---

## Phase 4 — Repository Semantic Analysis (AI)

Purpose:
Identify issues that **static analysis cannot detect**, such as:

* logical bug risks
* architecture violations in practice
* undocumented assumptions
* real test gaps
* onboarding confusion

Implementation:
`analyzers/semantic_analyzer.py`

Input:

* `file_summaries`
* `static_findings`
* `dependency_graph`

Output:

```python
@dataclass
class SemanticFinding:
    # Required fields per README.md assignment
    type: str  # "bug", "smell", "architecture", "test_gap", "doc_gap", "uncertainty"
    location: str  # "file:line" or "file:line1,line2" format
    explanation: str  # Clear description of the issue
    confidence: str  # "high", "medium", "low"

    # Optional bonus fields providing extra value
    subtype: str = ""  # Specific issue type (e.g., "force_unwrap", "singleton_testability")
    severity: str = ""  # "high", "medium", "low" - impact severity if issue is true
    evidence: str = ""  # Concrete evidence from static/semantic analysis
    recommendation: str = ""  # Actionable fix with concrete steps
```

Allowed finding types:

* `bug`
* `smell`
* `architecture`
* `test_gap`
* `documentation_gap`
* `uncertainty`

Examples:

### Bug

Force unwrap on API response array may crash if API returns empty list.

### Architecture

SwiftUI views directly accessing `JournalStore` bypass the ViewModel layer.

### Smell

Controller manages both UI rendering and business logic responsibilities.

### Test Gap

Critical persistence logic in `JournalStore` has no tests.

### Documentation Gap

Public API method lacks explanation of expected parameters.

### Uncertainty

Controller may rely on navigation controller presence but the assumption is undocumented.

---

## Phase 5 — Validation

Purpose:
Reduce false positives and make findings more grounded.

Implementation:
`analyzers/validator.py`

### Validation Strategy

The system uses a **single context-aware validation prompt** that adapts its reasoning based on the finding type being validated.

Instead of multiple specialized validators, one unified validator receives:

1. **The candidate finding** (type, location, explanation, evidence)
2. **Relevant code context**
3. **Finding type** (bug, smell, architecture, test_gap, documentation_gap, uncertainty)

The validation prompt internally applies type-appropriate reasoning:

* **bugs** → control-flow and crash-risk analysis
* **smells** → maintainability and design reasoning
* **architecture findings** → system-boundary and layer violation checks
* **test gaps** → criticality and reliability reasoning
* **documentation gaps** → onboarding and API-clarity assessment
* **uncertainties** → evidence strength evaluation

### Implementation

```python
def validate_finding(finding, context):
    """
    Single validator function that adapts based on finding type.
    The LLM prompt receives the finding type and applies
    appropriate validation reasoning internally.
    """
    prompt = load_validation_prompt(
        finding_type=finding.type,
        finding=finding,
        code_context=context
    )
    return llm.validate(prompt)
```

### Validation Checks

The validator assesses each finding by asking:

* **Is the finding grounded in the code?** (not speculative or hallucinated)
* **Is the crash risk or concern real?** (for bugs: is there protective logic?)
* **Is the claim behaviorally meaningful?** (not just style preference)
* **Is the finding actionable?** (provides clear next steps)
* **Is the confidence level appropriate?** (should it be high/medium/low or uncertainty?)

### Validation Principle

The tool should prefer:

* **fewer, stronger findings**
  over
* **many weak or generic findings**

If a concern is not well-supported, it should be downgraded to `uncertainty` or removed entirely.

---

## Phase 6 — Question Generation (AI)

Purpose:
Generate questions a new engineer should ask before modifying the codebase.

Implementation:
`analyzers/question_generator.py`

Input:

* `validated_findings` - List of SemanticFinding objects that passed validation

Output:

**Simplified implementation**: Returns `List[str]` (simple question strings)

Example output:
```python
[
    "What error handling strategies should we implement to safely manage potential crashes?",
    "How can we refactor singleton patterns to improve testability?",
    "What architectural guidelines should we follow for UIKit/SwiftUI integration?"
]
```

**Note**: Original design specified structured `Question` dataclass with `id`, `why_it_matters`, `related_findings`, and `areas_affected` fields. Implementation was simplified to simple strings per README.md requirements for faster iteration.

---

## Phase 7 — Report Generation

Purpose:
Produce final JSON output.

Implementation:
`core/report_builder.py`

Output structure:
`AnalysisReport`

Schema:

```python
@dataclass
class AnalysisReport:
    summary: str  # High-level codebase description (architecture, components, findings count)
    findings: List[SemanticFinding]  # Validated findings from Phase 5
    questions: List[str]  # Onboarding questions from Phase 6 (simple strings)
    limitations: List[str]  # Known limitations of this analysis approach
    metrics: Dict[str, Any] | None  # Performance metrics (runtime, tokens, cost)
```

**Simplified from original design**:
- `high_level_summary: dict` → `summary: str` (simpler, clearer)
- `questions: list[Question]` → `questions: List[str]` (no structured Question dataclass)
- `tool_limitations: dict` → `limitations: List[str]` (simple list of limitation strings)
- `metadata: dict` → `metrics: Dict` (renamed, tracks API usage and cost)
- Removed `id` and `tags` fields from findings (not needed for assignment scope)

Example JSON (actual output format):

```json
{
  "summary": "This is a Swift iOS application with 13 source files using mixed UIKit and SwiftUI architecture. The codebase follows a layered architecture with data models, services, and UI components. Analysis identified 8 validated findings including potential bugs, code smells, and architectural concerns that may affect maintainability and reliability.",
  "findings": [
    {
      "type": "bug",
      "location": "UI/SleepJournalListViewController.swift:120,142,147",
      "explanation": "Multiple force unwraps on navigationController may lead to crashes if it is nil.",
      "confidence": "high",
      "subtype": "force_unwrap",
      "severity": "high",
      "evidence": "Static findings indicate force unwraps at lines 120, 142, and 147.",
      "recommendation": "Replace force unwraps with optional binding (if let) to safely handle nil."
    }
  ],
  "questions": [
    "What error handling strategies should we implement to safely manage potential crashes from force unwrapping?",
    "How can we refactor the singleton patterns to improve testability and reduce global state?"
  ],
  "limitations": [
    "Static analysis only - does not detect runtime-specific issues or performance problems",
    "Limited to Swift source files - does not analyze build configurations, assets, or Interface Builder files",
    "AI-generated findings may require human validation and domain expertise"
  ],
  "metrics": {
    "runtime_seconds": 63.2,
    "api_calls": 23,
    "input_tokens": 37457,
    "output_tokens": 3812,
    "estimated_cost_usd": 0.0079,
    "cost_by_phase": {
      "file_summarization": 0.0041,
      "semantic_analysis": 0.0012,
      "validation": 0.0023,
      "question_generation": 0.0003
    }
  }
}
```

---

# Prompt Management

## Strategy

All LLM prompts are stored as plain text files in the `prompts/` directory, separate from Python code.

This design provides:

* **Easy editing**: Modify prompts without touching code
* **Version control**: Track prompt evolution in git history
* **Non-technical review**: Domain experts can review/improve prompts
* **A/B testing**: Swap prompts to compare different strategies
* **Transparency**: Prompts are explicit and inspectable

## Prompt Files

```text
prompts/
    file_summarizer.txt       # Phase 3: Generate structured file summaries
    semantic_analyzer.txt     # Phase 4: Detect bugs, smells, architecture issues
    validator.txt             # Phase 5: Validate findings for groundedness
    question_generator.txt    # Phase 6: Generate onboarding questions
```

## Loading Prompts

The `analyzers/prompt_loader.py` utility provides:

```python
class PromptLoader:
    def load(self, prompt_name: str) -> str:
        """Load a prompt template from prompts/ directory"""

    def render(self, prompt_name: str, **variables) -> str:
        """Load and render a prompt with variable substitution"""
```

Example usage:

```python
from analyzers.prompt_loader import PromptLoader

loader = PromptLoader()
prompt = loader.render(
    "file_summarizer",
    file_path="Services/JournalStore.swift",
    file_content=swift_code
)
```

---

# Module Overview

```text
prompts/
    file_summarizer.txt
    semantic_analyzer.txt
    validator.txt
    question_generator.txt

core/
    scanner.py
    syntactic_analyzer.py
    graph_builder.py
    report_builder.py

analyzers/
    prompt_loader.py
    file_summarizer.py
    semantic_analyzer.py
    validator.py
    question_generator.py
```

---

# Implementation Order

Coding agents should implement modules in this order:

1. `core/scanner.py`
2. `analyzers/prompt_loader.py`
3. `core/syntactic_analyzer.py`
4. `core/graph_builder.py`
5. `prompts/file_summarizer.txt`
6. `analyzers/file_summarizer.py`
7. `prompts/semantic_analyzer.txt`
8. `analyzers/semantic_analyzer.py`
9. `prompts/validator.txt`
10. `analyzers/validator.py`
11. `prompts/question_generator.txt`
12. `analyzers/question_generator.py`
13. `core/report_builder.py`
14. `analyze.py` (main entry point)

---

# AI Usage Summary

AI is used only for tasks requiring **semantic reasoning**:

| Component         | Purpose                                                            |
| ----------------- | ------------------------------------------------------------------ |
| FileSummarizer    | extract structured file understanding                              |
| SemanticAnalyzer  | detect logical issues, architecture problems, and onboarding risks |
| Validator         | apply category-specific reasoning to reduce false positives        |
| QuestionGenerator | synthesize onboarding questions                                    |

Static operations use **traditional techniques** instead.

---

# Prompt Contracts

Each AI component must return structured JSON matching these schemas:

## FileSummarizer Output

```json
{
  "file_path": "Services/JournalStore.swift",
  "role": "data persistence service",
  "main_types": ["JournalStore"],
  "dependencies": ["UserDefaults", "JSONDecoder", "SleepEntry"],
  "responsibilities": [
    "persist sleep entries to UserDefaults",
    "load entries on app launch",
    "export entries as JSON"
  ],
  "suspicious_patterns": [
    "force try on line 24 - decoder may crash if data is corrupted"
  ]
}
```

## SemanticAnalyzer Output

Returns a JSON array of findings (not wrapped in `{"findings": [...]}`):

```json
[
  {
    "type": "bug",
    "location": "Services/WeatherClient.swift:30",
    "explanation": "Force unwrap on periods.first! will crash if API returns empty forecast array",
    "confidence": "high",
    "subtype": "force_unwrap_crash_risk",
    "severity": "high",
    "evidence": "Line 30: let period = forecastResponse.properties.periods.first!",
    "recommendation": "Replace with optional binding: guard let period = forecastResponse.properties.periods.first else { return }"
  },
  {
    "type": "architecture",
    "location": "UI/SleepJournalListViewController.swift",
    "explanation": "ViewController directly accesses JournalStore singleton, bypassing ViewModel for some operations",
    "confidence": "medium",
    "subtype": "layer_violation",
    "severity": "medium",
    "evidence": "ViewModel is used for display, but add/delete operations bypass it",
    "recommendation": "Route all data operations through the ViewModel to maintain MVVM separation"
  }
]
```

**Note**: Output is a JSON array, not an object with `findings` key. All 4 required fields (`type`, `location`, `explanation`, `confidence`) plus optional bonus fields (`subtype`, `severity`, `evidence`, `recommendation`).

## Validator Output

```json
{
  "is_valid": true,
  "adjusted_confidence": "high",
  "reasoning": "The force unwrap on periods.first! is a real crash risk. The weather.gov API contract does not guarantee non-empty periods array. No defensive check exists before the unwrap.",
  "should_keep": true,
  "suggested_changes": null
}
```

Or for rejected findings:

```json
{
  "is_valid": false,
  "adjusted_confidence": null,
  "reasoning": "The singleton pattern claim is not a bug or architecture violation - it's a common Swift pattern for shared services. No evidence of state management issues.",
  "should_keep": false,
  "suggested_changes": "Downgrade to 'uncertainty' or remove entirely"
}
```

## QuestionGenerator Output

**Simplified implementation**: Returns a JSON array of question strings (not structured objects):

```json
[
  "What error handling strategies should we implement to safely manage potential crashes from force unwrapping in the codebase?",
  "How can we refactor the singleton patterns in JournalStore and WeatherCacheStore to improve testability and reduce global state?",
  "What architectural guidelines should we follow to maintain consistency between UIKit and SwiftUI components in our views?",
  "Where should we focus our testing efforts to ensure critical business logic in ViewModels is adequately covered?",
  "When is it appropriate to use force unwrapping versus safer alternatives like optional binding in our code?"
]
```

**Note**: Original design specified structured objects with `id`, `why_it_matters`, `related_findings`, and `areas_affected`. Implementation simplified to plain strings for faster iteration and README.md compliance.

---

# Limitations

The tool is limited by:

### Static Analysis Only

No runtime behavior is executed.

### Heuristic Graph

Dependency relationships are inferred heuristically.

### AI Interpretation

Architecture and logical findings are model interpretations, not proofs.

### Small Codebase Assumption

Designed for small to medium repositories.

### Validation Scope

Validation is selective and prompt-based, not equivalent to formal verification.

---

# Future Improvements (Not Implemented)

Possible extensions for larger codebases:

* RAG retrieval for large repos
* incremental analysis for CI pipelines
* symbol-level dependency graphs
* caching of file summaries

These are intentionally not implemented for the assignment scope.

---

# Summary

This architecture intentionally balances:

* deterministic static analysis
* AI-assisted semantic reasoning

The tool uses:

* **one repo-level semantic analysis pass**
* **single context-aware validation prompt**
* **structured report generation**
* **externalized prompts for easy iteration**

The goal is to produce **useful engineering insights**, not exhaustive bug detection.

The system prioritizes:

* clear architecture understanding
* high-value findings
* actionable questions
* grounded outputs
* scope-appropriate complexity

```

The one additional tweak I’d make is to add a short **“Prompt Contracts”** section so a coding model knows exactly what JSON each AI prompt must return.
```

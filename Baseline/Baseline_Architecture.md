
WORK EXCLUSIVELY IN THE BASELINE FOLDER


The key is: this second path should be presented as a **baseline / comparison implementation**, not your main recommended architecture.

That gives you a strong story:

* **Primary system:** structured hybrid pipeline
* **Baseline system:** brute-force agentic scan over every file
* **Comparison:** cost, latency, output quality, duplication, grounding

That is a very solid engineering move because it shows you did not just invent a fancy architecture — you compared it against a simpler alternative.

## Why this is a good idea

It helps you answer:

* Why not just use an LLM to read every file and report issues?
* Does the structured hybrid approach actually improve anything?
* What is the tradeoff in cost and time?
* Does the brute-force method find different issues?
* Is your architecture justified, or unnecessary?

That is very valuable.

## The main caveat

Do **not** let the baseline become another huge system.

It should be intentionally simple.

Think of it as:

> “What would the naive LLM-first version look like?”

So the brute-force baseline should be:

* minimal orchestration
* one file-level scan prompt per file
* one aggregation pass at the repo level
* basic deduplication
* JSON output
* timing + token/cost logging

Not a whole second elaborate product.

## What to compare

You should compare at least:

* total runtime
* total model cost
* number of findings
* number of duplicate findings
* number of high-confidence findings
* number of findings kept in final report
* maybe subjective quality notes

That is enough.

## What not to do

Do not make the brute-force baseline:

* multi-agent per file
* RAG-based
* validator-heavy
* deeply optimized

Otherwise your “baseline” becomes its own research project.

---

# Recommended framing

Call it something like:

* `baseline_bruteforce_agent`
* `naive_agentic_baseline`
* `llm_first_baseline`

And describe it as:

> A simple comparison pipeline that scans each file independently with an LLM, then merges the results into a repo report. It exists to measure the tradeoff between naive agentic scanning and the structured hybrid architecture.

That makes the purpose very clear.

---

# Suggested architecture doc for the baseline

Below is a clean `ARCHITECTURE_BASELINE.md` you can use.

---

````md
# ARCHITECTURE_BASELINE.md

# Brute-Force Agentic Baseline

## Project
Sleep Journal Codebase Analyzer — Baseline Comparison Implementation

## Purpose

This baseline exists to provide a simple comparison against the main hybrid architecture.

Instead of combining static analysis, structured file summaries, and repo-level semantic reasoning, this baseline uses a more naive approach:

- scan every Swift file
- ask an LLM to analyze each file independently
- merge the results into one repo-level report
- record time and cost

The baseline is intentionally simple so the project can compare:

- latency
- API cost
- finding quality
- duplication rate
- usefulness of output

This baseline is **not** the recommended final system.  
It is a comparison point.

---

# Design Goals

1. Build a minimal LLM-first baseline
2. Keep implementation simple
3. Measure runtime and cost precisely
4. Produce JSON output comparable to the main system
5. Evaluate whether structured analysis actually improves quality

---

# Non-Goals

This baseline does **not** attempt to:

- use Tree-sitter
- use a graph builder
- use RAG
- use specialized validators by finding type
- optimize token usage aggressively
- deeply deduplicate with complex logic

The baseline should remain naive enough to serve as a real comparison.

---

# High-Level Pipeline

1. Scan Codebase
2. Per-File Agentic Analysis
3. Aggregate Findings
4. Optional Repo-Level Merge Pass
5. Generate Questions
6. Build Report
7. Log Cost and Time

---

# Pipeline Phases

## Phase 1 — Codebase Scan

Purpose:  
Discover Swift source files.

Implementation:
`baseline/scanner.py`

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

## Phase 2 — Per-File Agentic Analysis

Purpose:
Analyze each file independently using an LLM.

Implementation:
`baseline/file_agent.py`

Input:

* `file_path`
* `file_content`

Output:

```python
@dataclass
class FileAgentResult:
    file_path: str
    summary: str
    findings: list[dict]
    raw_cost_usd: float
    raw_latency_seconds: float
```

The per-file prompt should ask the model to identify:

* likely bugs
* smells
* architecture issues visible in the file
* likely test gaps
* likely documentation gaps
* uncertainties

Example prompt responsibilities:

* summarize the role of the file
* identify suspicious logic
* identify risky patterns
* identify missing tests if the file appears important
* return structured JSON

Allowed finding types:

* `bug`
* `smell`
* `architecture`
* `test_gap`
* `documentation_gap`
* `uncertainty`

Important:
Per-file analysis should remain **file-local**.
The model should not guess too aggressively about cross-file architecture unless directly visible.

---

## Phase 3 — Aggregate Findings

Purpose:
Combine findings from all file-level agent outputs.

Implementation:
`baseline/aggregator.py`

Responsibilities:

* concatenate all file summaries
* merge all findings
* normalize types
* assign IDs
* perform basic deduplication

Basic deduplication can use:

* same type
* same location
* highly similar explanation text

No complex semantic deduplication is required.

---

## Phase 4 — Optional Repo-Level Merge Pass

Purpose:
Improve the baseline slightly by allowing one repo-level LLM call to:

* merge duplicated findings
* identify repo-wide themes
* produce a short architecture summary

Implementation:
`baseline/repo_merge_analyzer.py`

This step is optional but recommended because pure per-file scanning may miss:

* mixed UIKit / SwiftUI patterns
* inconsistent state ownership
* repeated singleton usage across files
* codebase-wide architecture inconsistency

Input:

* all file summaries
* all merged findings

Output:

```python
@dataclass
class RepoMergeResult:
    high_level_summary: dict
    merged_findings: list[dict]
```

This pass should stay lightweight.
It exists only to make the baseline somewhat comparable to the main architecture.

---

## Phase 5 — Question Generation

Purpose:
Generate onboarding questions from the aggregated findings.

Implementation:
`baseline/question_generator.py`

Input:

* merged findings
* high-level summary

Output:

```python
@dataclass
class Question:
    id: str
    question: str
    why_it_matters: str
    related_findings: list[str]
    areas_affected: list[str]
```

This can reuse the same question-generation logic as the main architecture.

---

## Phase 6 — Report Generation

Purpose:
Produce final JSON output.

Implementation:
`baseline/report_builder.py`

Schema:

```python
@dataclass
class Finding:
    id: str
    type: str
    subtype: str | None
    location: str
    confidence: str
    explanation: str
    evidence: str | None = None
    tags: list[str] | None = None


@dataclass
class AnalysisReport:
    high_level_summary: dict
    findings: list[Finding]
    questions: list[Question]
    tool_limitations: dict
    metadata: dict
```

Output must remain comparable to the main system.

---

## Phase 7 — Cost and Timing Instrumentation

Purpose:
Measure how expensive and slow the brute-force baseline is.

Implementation:
`baseline/metrics.py`

Track:

* total runtime
* per-file runtime
* total API cost
* per-file API cost
* number of LLM calls
* total findings before dedupe
* total findings after dedupe

Suggested metadata fields:

```json
{
  "baseline_type": "brute_force_agentic",
  "files_analyzed": 15,
  "total_runtime_seconds": 42.3,
  "total_cost_usd": 0.19,
  "llm_calls": 17,
  "findings_before_dedupe": 34,
  "findings_after_dedupe": 22
}
```

---

# Module Overview

```text
baseline/
    scanner.py
    file_agent.py
    aggregator.py
    repo_merge_analyzer.py
    question_generator.py
    report_builder.py
    metrics.py
```

---

# Implementation Order

Coding agents should implement modules in this order:

1. `baseline/scanner.py`
2. `baseline/file_agent.py`
3. `baseline/aggregator.py`
4. `baseline/repo_merge_analyzer.py`
5. `baseline/question_generator.py`
6. `baseline/report_builder.py`
7. `baseline/metrics.py`
8. `baseline/analyze_baseline.py`

---

# Prompt Strategy

## Per-File Agent Prompt

The per-file agent should return JSON with:

* file summary
* candidate findings
* confidence levels

The prompt should explicitly instruct:

* do not invent cross-file facts
* only report what is grounded in this file
* mark uncertain claims as `uncertainty`
* prefer fewer, stronger findings

## Repo Merge Prompt

The repo merge prompt should:

* merge repeated patterns
* identify codebase-wide themes
* produce a short high-level summary
* avoid inventing unsupported architecture claims

---

# Baseline Strengths

This baseline is useful because it:

* is easy to implement
* is easy to explain
* provides a fair naive comparison
* measures the cost of an LLM-first approach
* may catch some file-local issues quickly

---

# Baseline Weaknesses

This baseline is expected to be worse than the main architecture in several ways:

* more duplicated findings
* weaker cross-file reasoning
* less grounded architecture understanding
* more inconsistent finding quality
* higher token cost for repetitive file-by-file analysis

These weaknesses are acceptable because this implementation exists as a comparison baseline.

---

# Comparison With Main Architecture

## Main Architecture

* structured static analysis
* file summaries
* repo-level semantic reasoning
* specialized validation prompts
* more grounded findings

## Baseline Architecture

* naive file-by-file LLM scan
* simple merge step
* lower implementation complexity
* useful for benchmarking cost and output quality

---

# What to Compare

When both systems are implemented, compare:

* total runtime
* total API cost
* number of findings
* number of duplicate findings
* number of high-confidence findings
* number of final kept findings
* subjective quality of architecture summary
* subjective usefulness of questions

---

# Limitations

This baseline is intentionally naive.

It does not use:

* AST parsing
* graph reasoning
* structured heuristics
* specialized validation prompts

It should not be treated as the best design.
It exists to show the tradeoff between brute-force LLM scanning and a more structured hybrid pipeline.

---

# Summary

This baseline provides a simple LLM-first comparison implementation:

* scan every file
* analyze every file with an LLM
* merge results
* measure cost and time

Its purpose is to validate whether the main architecture’s additional structure produces better results.

```



# Sleep Journal Codebase Analyzer

**AI-Assisted Developer Tool for Mobile Codebase Understanding**

A Python CLI tool that analyzes iOS Swift codebases to generate structured insights about architecture, potential bugs, code smells, and onboarding questions—helping engineers quickly understand unfamiliar projects.

---

## Problem Statement

When engineers join a new team or inherit an existing codebase, they face a steep learning curve understanding:
- High-level architecture and design patterns
- Potential bugs and technical debt
- What questions to ask before making changes
- Where to focus code review and testing efforts

Manual code review is time-consuming (2-3 hours for ~1,200 lines) and error-prone. This tool **automates codebase understanding** using a multi-phase AI pipeline to generate actionable insights in under 90 seconds.

**Focus Areas:**
1. **Architecture Understanding**: Identify patterns (UIKit/SwiftUI mixing, singletons, layer violations)
2. **Bug Detection**: Find crash risks (force unwraps, force try, unsafe optionals)
3. **Code Quality**: Detect smells (testability issues, tight coupling)
4. **Knowledge Gaps**: Generate onboarding questions and flag missing tests/docs

---

## How It Works

### 7-Phase Analysis Pipeline

The tool uses a **hybrid approach** combining traditional static analysis with LLM-powered semantic reasoning:

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Scan Codebase                                       │
│ → Discover all Swift files recursively                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Static Analysis (Tree-Sitter)                       │
│ → Parse AST for syntactic patterns                           │
│ → Detect force unwraps, force try, unsafe patterns           │
│ → Build dependency graph between files                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: File Summarization (AI)                             │
│ → Generate structured summary per file                       │
│ → Extract: role, main types, dependencies, key logic         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 4: Semantic Analysis (AI)                              │
│ → Analyze file summaries + static findings + dep graph       │
│ → Identify: bugs, smells, architecture issues, test/doc gaps │
│ → Generate evidence-grounded findings with line numbers      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 5: Validation (AI)                                     │
│ → Filter false positives per finding type                    │
│ → Assess confidence and severity                             │
│ → Keep only high-confidence, actionable findings             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 6: Question Generation (AI)                            │
│ → Synthesize onboarding questions from findings              │
│ → Focus on: patterns, decision-making, risk areas            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 7: Report Building                                     │
│ → Assemble JSON report with summary, findings, questions     │
│ → Include metrics: runtime, tokens, cost                     │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

**1. Hybrid Analysis (Static + AI)**
- **Static Analysis First**: Use tree-sitter to parse Swift AST and detect syntactic patterns (force unwraps, singletons). This grounds AI analysis in concrete evidence.
- **AI for Semantics**: LLMs excel at understanding architectural concerns, testability issues, and generating context-aware questions.

**2. Multi-Phase Pipeline (not single-call)**
- **Why**: Single LLM call is 3.8× cheaper ($0.0022 vs $0.0084) but produces lower-quality, unstructured output.
- **Benefit**: Structured phases enable validation, reduce hallucinations, and provide traceable findings with line numbers.

**3. Validation Phase**
- **Why**: Semantic analysis may produce false positives or low-confidence findings.
- **How**: Separate validation pass filters each finding type (bugs, smells, test gaps) with specialized prompts.
- **Result**: ~30% of raw findings filtered out, improving signal-to-noise ratio.

**4. Per-File Summarization**
- **Why**: Sending entire codebase to LLM loses structure and context.
- **How**: Summarize each file individually (role, types, dependencies), then analyze summaries.
- **Tradeoff**: 13 API calls (slower) vs better context understanding.

---

## How to Run

### Prerequisites

- **Python**: 3.8 or higher
- **OpenAI API Key**: Required for AI-powered analysis phases
- **Operating System**: macOS/Linux (tested on macOS 13+)

### Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key:**
   Create a `.env` file in the project root:
   ```bash
   echo "OPENAI_API_KEY=sk-your-api-key-here" > .env
   ```

   Or export as environment variable:
   ```bash
   export OPENAI_API_KEY="sk-your-api-key-here"
   ```

### Running the Analyzer

**Basic usage:**
```bash
python run_analysis.py
```

This will:
1. Analyze the `Sleep Journal/` directory (hardcoded in script)
2. Run all 7 phases of the pipeline
3. Display progress and findings to terminal
4. Save full report to `analysis_report.json`

**Expected output:**
```
============================================================
Sleep Journal Codebase Analyzer
============================================================

Analyzing repository: Sleep Journal

Running 7-phase analysis pipeline:
  Phase 1: Scanning codebase for Swift files...
    Found 13 Swift files
  ...
  Phase 7: Report building...

============================================================
Analysis Complete!
============================================================

Findings: 8

  1. [HIGH] bug
     Location: UI/SleepJournalListViewController.swift:120,142,147
     Explanation: Multiple force unwraps on navigationController...
     Confidence: high

  ... (additional findings)

Performance Metrics
  Runtime: 63.20 seconds (1.1 minutes)
  API Calls: 23
  Total Tokens: 41,269
  Estimated Cost: $0.0079

Full report saved to: analysis_report.json
```

### Output Format

The generated `analysis_report.json` includes:

```json
{
  "summary": "High-level codebase description (architecture, patterns, findings)",
  "findings": [
    {
      "type": "bug | smell | architecture | test_gap | doc_gap",
      "location": "file:line or file:line1,line2",
      "explanation": "Clear description of the issue",
      "confidence": "high | medium | low",
      "subtype": "force_unwrap | singleton_testability | ...",
      "severity": "high | medium | low",
      "evidence": "Concrete evidence from static/semantic analysis",
      "recommendation": "Actionable fix suggestion"
    }
  ],
  "questions": [
    "Onboarding questions for new engineers..."
  ],
  "limitations": [
    "Known constraints of this analysis approach..."
  ],
  "metrics": {
    "runtime_seconds": 63.2,
    "api_calls": 23,
    "input_tokens": 37457,
    "output_tokens": 3812,
    "estimated_cost_usd": 0.0079,
    "cost_by_phase": { ... }
  }
}
```

**Sample output:** See [`analysis_report.json`](analysis_report.json) for a complete example generated from the Sleep Journal project.

---

## AI Tools & Models Used

### Primary Model: OpenAI GPT-4o-mini

**Why gpt-4o-mini?**
- **Cost-effective**: $0.150/1M input tokens, $0.600/1M output tokens
- **Fast**: Low latency for interactive workflows
- **Sufficient quality**: Adequate for code understanding tasks (vs GPT-4 overkill)
- **Cost per analysis**: $0.0079 (~0.8 cents)

**Temperature settings:**
- File summarization: `0.0` (structured output, no creativity needed)
- Semantic analysis: `0.2` (balance consistency with insight)
- Validation: `0.0` (deterministic filtering)
- Question generation: `0.3` (slight creativity for diverse questions)

### AI Usage Breakdown

| Phase | AI Used? | Purpose | API Calls | Cost |
|-------|----------|---------|-----------|------|
| 1. Scan | ❌ No | File system traversal | 0 | $0 |
| 2. Static Analysis | ❌ No | Tree-sitter AST parsing | 0 | $0 |
| 3. File Summarization | ✅ Yes | Extract role, types, dependencies | 13 | $0.0041 |
| 4. Semantic Analysis | ✅ Yes | Detect bugs, smells, architecture issues | 1 | $0.0012 |
| 5. Validation | ✅ Yes | Filter false positives | 8 | $0.0023 |
| 6. Question Generation | ✅ Yes | Synthesize onboarding questions | 1 | $0.0003 |
| 7. Report Building | ❌ No | JSON assembly | 0 | $0 |

**Total AI usage:** 23 API calls, $0.0079 per analysis

### Transparency & Reproducibility

- **Token tracking**: Every AI call tracks input/output tokens (see `metrics` in JSON output)
- **Deterministic prompts**: Low temperature ensures consistent results across runs
- **Prompt engineering**: All prompts stored in `prompts/` directory for auditability
- **Cost transparency**: Full breakdown in `COST_ANALYSIS.md`

---

## Design Tradeoffs

### Choices Made

#### ✅ Multi-Phase Pipeline vs Single-Call
**Decision**: Use 7-phase pipeline with multiple AI calls
**Tradeoff**: 3.8× more expensive ($0.0084 vs $0.0022) and slower (~60s vs ~10s)
**Why**: Produces structured, validated findings with line numbers vs unstructured blob of text. Quality justifies cost.

#### ✅ Validation Phase
**Decision**: Dedicated validation phase filtering each finding type
**Tradeoff**: Adds 8-10 API calls (~10s runtime, ~$0.002 cost)
**Why**: Reduces false positives by ~30%, improving trust and actionability of findings.

#### ✅ Per-File Summarization
**Decision**: Summarize each file individually before repo-level analysis
**Tradeoff**: 13 API calls vs 1 (slower, 65% of total cost)
**Why**: Preserves file-level context and structure; better than dumping entire codebase into single prompt.

#### ✅ Tree-Sitter for Static Analysis
**Decision**: Use AST parsing for syntactic patterns (not regex)
**Tradeoff**: Requires language-specific grammar, more complex setup
**Why**: Accurate detection of force unwraps, force try, etc. Avoids false positives from comments/strings.

#### ❌ No RAG / Vector Embeddings
**Decision**: No semantic search or vector database
**Why**: Sleep Journal is only 1,216 lines (13 files). Embedding overhead not justified. Direct analysis is sufficient.

#### ❌ No Multi-Agent Swarm
**Decision**: Single semantic analysis pass + specialized validators (not separate bug/smell/architecture agents)
**Why**: Simpler, faster, cheaper. Specialized agents add coordination overhead without clear quality improvement for small codebases.

#### ❌ No Caching
**Decision**: No persistent cache for file summaries or findings
**Tradeoff**: Repeat analysis costs ~$0.008 each time
**Why**: Take-home project scope; caching adds complexity. For production use, caching would save 65% cost on subsequent runs (see `COST_ANALYSIS.md` Option C).

### What I'd Do Differently with More Time

1. **Parallel File Summarization**: Use thread pool for concurrent API calls (50-70% faster)
2. **Smart Caching**: Store file summaries keyed by content hash; skip unchanged files (90% faster on reruns)
3. **Batch Validation**: Validate 3-5 findings per call instead of 1 (20% cost reduction)
4. **Incremental Analysis**: Only analyze changed files in git diff (for CI/CD integration)
5. **More Language Support**: Extend to Kotlin, React Native, Flutter (currently Swift-only)
6. **Interactive CLI**: Let users filter findings by type, severity, or file
7. **Test Coverage**: Fix remaining 14 failing tests (currently 203/217 passing, 93.5%)

---

## Known Limitations

### Analysis Scope

1. **Static Analysis Only**
   - Does not execute code or run tests
   - Cannot detect runtime-specific bugs (race conditions, memory leaks, performance issues)
   - No understanding of user flows or app behavior

2. **Swift Source Files Only**
   - Does not analyze: Xcode project settings, build configurations, Interface Builder files (.xib/.storyboard), assets, localization files
   - No Objective-C support

3. **No External Dependencies**
   - Does not fetch or analyze CocoaPods, SPM, or Carthage dependencies
   - Cannot detect issues in third-party libraries

### AI Limitations

4. **Requires Human Validation**
   - AI findings are high-confidence but not guaranteed correct
   - May miss context-specific issues (business logic, product requirements)
   - False positives possible despite validation phase

5. **API Key Required**
   - Not free: ~$0.008 per analysis
   - Requires internet connection and OpenAI account
   - Subject to OpenAI API rate limits

6. **Token Context Window**
   - Best for codebases <100 files (~10K LOC)
   - Very large files (>2000 lines) may be truncated in summaries

### Technical Constraints

7. **Line Number Accuracy**
   - Depends on tree-sitter pattern matching quality
   - May be off by ±1-2 lines for complex expressions

8. **Performance**
   - Runtime: ~60-90 seconds (not instant)
   - Sequential API calls (could be parallelized)

9. **No Business Context**
   - Cannot understand product requirements, user stories, or domain logic
   - Recommendations may conflict with intentional design decisions

### Documented Explicitly

All limitations are **included in the JSON output** under the `limitations` field for transparency.

---

## Performance Metrics

**Analysis of Sleep Journal (13 files, 1,216 LOC):**

| Metric | Value |
|--------|-------|
| Runtime | 63.20 seconds (~1.1 minutes) |
| Total Tokens | 41,269 tokens (37,457 input + 3,812 output) |
| API Calls | 23 requests |
| Cost | **$0.0079 USD** (~0.8 cents) |
| Findings | 8 validated findings |
| Questions | 5 onboarding questions |

**Cost Efficiency:**
- **vs Manual Review**: 99.998% cheaper ($0.008 vs $300-450 for 2-3hr engineer time)
- **vs Naive Single-Call**: 3.8× more expensive but produces structured, validated output
- **vs Enterprise Tools**: 17,857-59,524 analyses for same monthly cost as SonarQube/CodeClimate

**Detailed Analysis:** See [`COST_ANALYSIS.md`](COST_ANALYSIS.md) for:
- Cost breakdown by phase
- Scalability projections (10-500 files)
- Optimization opportunities (caching, parallelization)
- Bottleneck analysis

---

## Project Structure

```
.
├── PROJECT_README.md          # This file (submission documentation)
├── ASSIGNMENT.md              # Original assignment requirements
├── requirements.txt           # Python dependencies
├── .env                       # OpenAI API key (create this)
│
├── run_analysis.py            # Main CLI entry point
├── analyze.py                 # Pipeline orchestration
│
├── core/                      # Core analysis modules
│   ├── scanner.py             # Phase 1: File discovery
│   ├── syntactic_analyzer.py  # Phase 2: Tree-sitter static analysis
│   ├── graph_builder.py       # Phase 2: Dependency graph
│   ├── report_builder.py      # Phase 7: JSON report assembly
│   └── metrics.py             # Token & cost tracking
│
├── analyzers/                 # AI-powered analyzers
│   ├── file_summarizer.py     # Phase 3: Per-file summarization
│   ├── semantic_analyzer.py   # Phase 4: Repository semantic analysis
│   ├── validator.py           # Phase 5: Finding validation
│   ├── question_generator.py  # Phase 6: Onboarding questions
│   ├── llm_utils.py           # JSON parsing utilities
│   └── prompt_loader.py       # Prompt loading from files
│
├── prompts/                   # AI prompt templates
│   ├── file_summarizer.txt
│   ├── semantic_analyzer.txt
│   ├── validator.txt
│   └── question_generator.txt
│
├── tests/                     # Test suite (203/217 passing)
│   ├── test_scanner.py
│   ├── test_syntactic_analyzer.py
│   ├── test_graph_builder.py
│   ├── test_file_summarizer.py
│   ├── test_semantic_analyzer.py
│   ├── test_validator.py
│   ├── test_question_generator.py
│   ├── test_report_builder.py
│   └── test_analyze.py
│
├── analysis_report.json       # Sample output (generated)
├── COST_ANALYSIS.md           # Performance & cost deep-dive
├── Baseline/                  # Alternative baseline implementation (see below)
└── Sleep Journal/             # Target iOS app (13 Swift files)
```

---

## Baseline Implementation (Optional Reference)

The [`Baseline/`](Baseline/) directory contains an alternative implementation approach for comparison purposes:

**Baseline Approach**: Repository-merge single-call analysis
- **Pipeline**: 3 phases (Scan → Merge & Analyze → Report)
- **Method**: Concatenate all files into single prompt, ask LLM to analyze entire codebase in one call
- **Cost**: ~$0.002 per analysis (4× cheaper)
- **Runtime**: ~10 seconds (6× faster)
- **Output**: Unstructured text findings

**Main Implementation** (this submission): Multi-phase pipeline with validation
- **Pipeline**: 7 phases with dedicated summarization, semantic analysis, and validation
- **Method**: Per-file summaries → repo-level analysis → validation → question generation
- **Cost**: ~$0.008 per analysis
- **Runtime**: ~60-90 seconds
- **Output**: Structured JSON with line numbers, confidence levels, evidence, and recommendations

**Why we chose the multi-phase approach:**
The baseline is simpler and cheaper, but produces lower-quality output:
- ❌ No line numbers or precise locations
- ❌ No confidence levels or validation
- ❌ Unstructured findings (hard to parse programmatically)
- ❌ Less detailed evidence and recommendations
- ❌ Schema compliance issues

The **4× cost increase** ($0.002 → $0.008) is justified by:
- ✅ Structured findings with exact line numbers
- ✅ Validation phase reduces false positives by ~30%
- ✅ README-compliant schema (type, location, explanation, confidence)
- ✅ Evidence-grounded findings with actionable recommendations
- ✅ Better scalability (per-file summarization handles large codebases)

**Comparison metrics:** See [`Baseline/METRICS_COMPARISON.md`](Baseline/METRICS_COMPARISON.md) for detailed side-by-side analysis.

---

## Testing

**Test-Driven Development (TDD):** Entire project built using red-green-refactor methodology.

**Current status:**
- **203 tests passing** (93.5% pass rate)
- 14 tests failing in `test_validator.py` (schema migration edge cases)

**Run tests:**
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_semantic_analyzer.py -v
```

---

## Development Process

**Time Investment:** ~5 hours (within 4-5 hour timebox)

**Breakdown:**
- Phase 1-2 implementation (Scanner + Static Analysis): 1 hour
- Phase 3-6 implementation (AI components): 2 hours
- Phase 7 + orchestration (Report + analyze.py): 30 minutes
- Schema refactor (README compliance): 45 minutes
- Metrics tracking (cost/runtime): 30 minutes
- Documentation (this README): 30 minutes

**AI Usage During Development:**
- Used Claude Code for code generation and TDD workflow
- Followed `/test-driven-development` slash command guidance
- Wrote tests before implementation for all modules
- Used Claude to generate boilerplate, refine prompts, and debug

---

## Future Enhancements

If continuing this project:

1. **Performance Optimizations**
   - Parallel file summarization (50-70% faster)
   - Smart caching for incremental analysis (90% cost reduction on reruns)
   - Batch validation (20% cost savings)

2. **Language Support**
   - Kotlin for Android
   - TypeScript/JavaScript for React Native
   - Dart for Flutter

3. **Integration Features**
   - Git diff analysis (only changed files)
   - CI/CD integration (GitHub Actions, GitLab CI)
   - IDE extensions (VSCode, IntelliJ)

4. **Output Formats**
   - HTML report with syntax highlighting
   - Markdown summary for PR comments
   - SARIF format for IDE integration

5. **Interactive Features**
   - CLI filters (by type, severity, file)
   - "Fix it" suggestions with diffs
   - Confidence threshold tuning

---

## License

This project was created as a take-home assignment. Not licensed for external use.

---


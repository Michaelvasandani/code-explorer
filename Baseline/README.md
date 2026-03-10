# Baseline Brute-Force Agentic Analyzer

A simple LLM-first comparison baseline for iOS codebase analysis.

## Overview

This baseline analyzer uses a naive approach:
1. Scan each Swift file independently
2. Analyze each file with an LLM (GPT-4o-mini)
3. Aggregate and deduplicate findings
4. Perform one repo-level merge pass
5. Generate onboarding questions
6. Produce JSON report with metrics

This implementation exists to compare against more structured analysis architectures (AST-based, graph reasoning, etc.).

## Installation

```bash
pip install -r requirements.txt
```

## Setup

You need an OpenAI API key. Set it as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file in your home directory (`~/.env`):

```
OPENAI_API_KEY=your-api-key-here
```

## Usage

Analyze a codebase:

```bash
python -m baseline.analyze_baseline "path/to/codebase"
```

With output to a file:

```bash
python -m baseline.analyze_baseline "path/to/codebase" --output report.json
```

Example (analyzing the Sleep Journal sample):

```bash
python -m baseline.analyze_baseline "../Sleep Journal" --output baseline_report.json
```

## Running Tests

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ -v --cov=baseline
```

## Output Format

The analyzer produces a JSON report with:

- **high_level_summary**: Architecture pattern, key components, primary risks
- **findings**: List of bugs, smells, architecture issues, test gaps, etc.
- **questions**: Onboarding questions for new engineers
- **tool_limitations**: Known constraints of this approach
- **metadata**: Analysis metrics (cost, runtime, file count, etc.)

## Comparison Metrics

The report includes baseline-specific metrics:

```json
{
  "metadata": {
    "baseline_type": "brute_force_agentic",
    "total_files": 13,
    "total_cost_usd": 0.0450,
    "llm_calls": 15,
    "findings_before_dedupe": 28,
    "findings_after_dedupe": 22,
    "total_runtime_seconds": 45.3
  }
}
```

## Architecture

### Modules

- `scanner.py` - Discover Swift files
- `file_agent.py` - Per-file LLM analysis
- `aggregator.py` - Combine and deduplicate findings
- `repo_merge_analyzer.py` - Repo-level analysis pass
- `question_generator.py` - Generate onboarding questions
- `report_builder.py` - Build final JSON report
- `metrics.py` - Track cost and timing
- `analyze_baseline.py` - Main entry point

### Pipeline

```
1. Scan Codebase (scanner.py)
   ↓
2. Per-File Analysis (file_agent.py) - LLM call per file
   ↓
3. Aggregate Findings (aggregator.py) - Deduplicate
   ↓
4. Repo Merge (repo_merge_analyzer.py) - LLM call for cross-file patterns
   ↓
5. Generate Questions (question_generator.py) - LLM call
   ↓
6. Build Report (report_builder.py)
```

## Limitations

This baseline approach has intentional limitations:

- No AST-based static analysis (relies on LLM pattern recognition)
- Per-file analysis may miss cross-file dependencies
- Cost scales linearly with codebase size
- May produce duplicate findings despite deduplication
- Cannot detect runtime performance issues
- Quality depends on LLM capabilities and prompt engineering

These limitations are acceptable because this is a comparison baseline, not a production system.

## Cost Estimates

For a typical small iOS app (~15 Swift files, ~2000 LOC):
- **LLM calls**: 15-17 (one per file + repo merge + questions)
- **Estimated cost**: $0.03 - $0.10
- **Estimated runtime**: 30-60 seconds

Cost is primarily driven by:
- Number of files
- Average file size
- Complexity of findings

## Comparison Use Case

This baseline exists to answer:
- Why not just use an LLM to read every file and report issues?
- Does structured analysis actually improve quality?
- What is the tradeoff in cost and time?
- Does the brute-force method find different issues?

When comparing with a structured architecture, measure:
- Total runtime
- Total API cost
- Number of findings (before/after dedupe)
- Number of high-confidence findings
- Subjective quality of architecture summary
- Usefulness of onboarding questions

## Testing

56 tests covering:
- Scanner (file discovery)
- File agent (LLM analysis)
- Aggregator (deduplication)
- Repo merge analyzer
- Question generator
- Report builder
- Metrics tracking
- Integration tests

## License

MIT

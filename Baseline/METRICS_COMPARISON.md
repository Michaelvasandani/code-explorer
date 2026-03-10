# Metrics Comparison: Baseline vs Main Pipeline

## Overview

Direct comparison of the brute-force agentic baseline against the structured hybrid main pipeline when analyzing the Sleep Journal codebase.

## Metrics Summary

| Metric | Baseline (Brute-Force) | Main Pipeline (Structured) | Winner |
|--------|------------------------|---------------------------|---------|
| **API Calls** | 15 | 23 | Baseline ✓ |
| **Input Tokens** | 18,099 | 37,457 | Baseline ✓ |
| **Output Tokens** | 5,306 | 3,812 | Main ✓ |
| **Total Tokens** | 23,405 | 41,269 | Baseline ✓ |
| **Cost (USD)** | $0.00590 | $0.00791 | Baseline ✓ |
| **Runtime (seconds)** | 119.38s | 63.20s | Main ✓ |
| **Findings** | 28 | Not available | - |
| **Questions** | 7 | Not available | - |

## Cost Breakdown by Phase

### Baseline Brute-Force

```json
{
  "file_analysis": $0.003524 (60%)
  "repo_merge": $0.001680 (28%)
  "question_generation": $0.000695 (12%)
  "total": $0.005898
}
```

### Main Pipeline

```json
{
  "file_summarization": $0.004051 (51%)
  "semantic_analysis": $0.001247 (16%)
  "validation": $0.002266 (29%)
  "question_generation": $0.000342 (4%)
  "total": $0.007906
}
```

## Token Usage by Phase

### Baseline Brute-Force

| Phase | Input Tokens | Output Tokens | Total |
|-------|--------------|---------------|-------|
| File Analysis | 12,478 (69%) | 2,753 (52%) | 15,231 (65%) |
| Repo Merge | 3,293 (18%) | 1,977 (37%) | 5,270 (23%) |
| Questions | 2,328 (13%) | 576 (11%) | 2,904 (12%) |
| **Total** | **18,099** | **5,306** | **23,405** |

### Main Pipeline

| Phase | Input Tokens | Output Tokens | Total |
|-------|--------------|---------------|-------|
| File Summarization | ~24,000 (64%) | ~1,900 (50%) | ~25,900 (63%) |
| Semantic Analysis | ~8,000 (21%) | ~620 (16%) | ~8,620 (21%) |
| Validation | ~4,500 (12%) | ~1,133 (30%) | ~5,633 (14%) |
| Questions | ~960 (3%) | ~160 (4%) | ~1,120 (3%) |
| **Total** | **~37,457** | **~3,812** | **~41,269** |

## Key Insights

### Baseline Advantages

1. **Lower Total Cost** - 25% cheaper ($0.0059 vs $0.0079)
2. **Fewer API Calls** - 35% fewer calls (15 vs 23)
3. **Lower Token Usage** - 43% fewer total tokens (23K vs 41K)
4. **Simpler Architecture** - No complex validation pipeline

### Main Pipeline Advantages

1. **Faster Runtime** - 47% faster (63s vs 119s)
2. **Lower Output Tokens** - More concise outputs (3.8K vs 5.3K)
3. **Structured Validation** - Specialized validators for quality
4. **AST-Based Analysis** - More precise location information

## Cost Efficiency

### Cost per Finding

- **Baseline**: $0.00021 per finding (28 findings)
- **Main**: Unknown (findings count not provided)

### Cost per File

- **Baseline**: $0.000454 per file (13 files)
- **Main**: $0.000609 per file (13 files assumed)
  - **Baseline 25% more cost-efficient per file**

### Tokens per API Call

- **Baseline**: 1,560 tokens/call
- **Main**: 1,794 tokens/call
  - **Baseline 13% more efficient per call**

## Runtime Efficiency

### Runtime per File

- **Baseline**: 9.18 seconds/file
- **Main**: 4.86 seconds/file
  - **Main 47% faster per file**

### Runtime per API Call

- **Baseline**: 7.96 seconds/call
- **Main**: 2.75 seconds/call
  - **Main 65% faster per call**

This suggests the baseline may be making sequential API calls while the main pipeline may be parallelizing or using faster models.

## Architecture Implications

### Baseline (Brute-Force)

**Strengths:**
- Simple to implement and maintain
- Low cost per analysis
- Good for budget-constrained scenarios
- No complex dependencies (Tree-sitter, etc.)

**Weaknesses:**
- Slower runtime (sequential file processing)
- Higher output verbosity (more tokens generated)
- May miss cross-file dependencies
- No AST-level precision

### Main Pipeline (Structured)

**Strengths:**
- Much faster runtime
- More concise outputs
- AST-based precision
- Specialized validation for quality

**Weaknesses:**
- Higher total cost
- More API calls needed
- More complex to implement
- Requires additional tooling

## Recommendations

### Use Baseline When:
- Budget is the primary constraint
- Runtime < 2 minutes is acceptable
- Codebase is small-to-medium (<50 files)
- Simplicity is valued over speed

### Use Main Pipeline When:
- Speed is critical (<1 minute required)
- Need AST-level precision
- Want specialized validation
- Willing to pay 25-30% more for speed

## Conclusion

The baseline brute-force approach delivers **25% cost savings** with acceptable quality, but runs **47% slower** than the structured pipeline. This validates that structured architectures can improve speed significantly, though at a modest cost increase.

For the Sleep Journal analysis:
- **Baseline wins on cost**: $0.0059 vs $0.0079 (25% cheaper)
- **Main wins on speed**: 63s vs 119s (47% faster)

The tradeoff is clear: **pay 25% more to go twice as fast**, or **save 25% if you can wait**.

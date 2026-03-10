#!/usr/bin/env python3
"""
Script to batch-update test files after schema changes.

Updates:
- SemanticFinding: files→location, description→explanation, adds confidence
- AnalysisReport: validated_findings→findings, onboarding_questions→questions, adds summary & limitations
"""

import re
from pathlib import Path


def fix_semantic_finding(content: str) -> str:
    """Fix SemanticFinding instantiations in tests."""

    # Pattern: SemanticFinding with old schema
    pattern = r'SemanticFinding\(\s*type="([^"]+)",\s*subtype="([^"]+)",\s*severity="([^"]+)",\s*files=\[([^\]]+)\],\s*description="([^"]+)",\s*evidence="([^"]+)",\s*recommendation="([^"]+)"\s*\)'

    def replacer(match):
        type_val = match.group(1)
        subtype = match.group(2)
        severity = match.group(3)
        files_content = match.group(4)
        description = match.group(5)
        evidence = match.group(6)
        recommendation = match.group(7)

        # Extract first file for location
        first_file_match = re.search(r'"([^"]+)"', files_content)
        if first_file_match:
            location = first_file_match.group(1) + ":1"
        else:
            location = "test.swift:1"

        # Map old type to new type
        type_mapping = {
            "code_smell": "smell",
            "architecture_issue": "architecture",
        }
        new_type = type_mapping.get(type_val, type_val)

        return f'''SemanticFinding(
            type="{new_type}",
            location="{location}",
            explanation="{description}",
            confidence="{severity}",
            subtype="{subtype}",
            severity="{severity}",
            evidence="{evidence}",
            recommendation="{recommendation}"
        )'''

    return re.sub(pattern, replacer, content, flags=re.DOTALL)


def fix_analysis_report(content: str) -> str:
    """Fix AnalysisReport instantiations in tests."""

    # Pattern 1: AnalysisReport with validated_findings, onboarding_questions, summary_stats
    pattern1 = r'AnalysisReport\(\s*validated_findings=([^,]+),\s*onboarding_questions=([^,]+),\s*summary_stats=([^)]+)\)'

    def replacer1(match):
        findings = match.group(1).strip()
        questions = match.group(2).strip()

        return f'''AnalysisReport(
            summary="Test codebase summary",
            findings={findings},
            questions={questions},
            limitations=["Test limitation"]
        )'''

    content = re.sub(pattern1, replacer1, content, flags=re.DOTALL)

    # Also fix field access in tests
    content = content.replace('.validated_findings', '.findings')
    content = content.replace('.onboarding_questions', '.questions')
    content = content.replace('"validated_findings"', '"findings"')
    content = content.replace('"onboarding_questions"', '"questions"')
    content = content.replace('"summary_stats"', '"summary"')

    return content


def fix_report_builder_build(content: str) -> str:
    """Fix ReportBuilder.build() calls."""

    # Pattern: build(validated_findings=..., onboarding_questions=..., summary_stats=...)
    pattern = r'builder\.build\(\s*validated_findings=([^,]+),\s*onboarding_questions=([^,]+),\s*summary_stats=([^)]+)\)'

    def replacer(match):
        findings = match.group(1).strip()
        questions = match.group(2).strip()

        return f'''builder.build(
            summary="Test summary",
            findings={findings},
            questions={questions},
            limitations=["Test limitation"]
        )'''

    return re.sub(pattern, replacer, content, flags=re.DOTALL)


def main():
    """Fix all test files."""
    test_files = [
        "tests/test_analyze.py",
        "tests/test_report_builder.py",
        "tests/test_semantic_analyzer.py",
    ]

    for file_path in test_files:
        path = Path(file_path)
        if not path.exists():
            print(f"Skipping {file_path} - not found")
            continue

        print(f"Fixing {file_path}...")
        content = path.read_text()

        # Apply fixes
        content = fix_semantic_finding(content)
        content = fix_analysis_report(content)
        content = fix_report_builder_build(content)

        # Write back
        path.write_text(content)
        print(f"  ✓ Fixed {file_path}")

    print("\nDone! Re-run tests to verify.")


if __name__ == "__main__":
    main()

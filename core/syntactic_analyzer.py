"""
Syntactic Analyzer module for static code analysis.

This module implements Phase 2 of the analysis pipeline: Static Analysis.
It detects structural patterns and syntactic risk signals using regex-based
pattern matching.

Per Architecture.md:
- Detect force unwraps (!)
- Detect force try (try!)
- Detect singleton usage (static let shared)
- Detect large classes (method count heuristic)
- Use traditional techniques (no AI)

Note: Uses regex patterns instead of tree-sitter for simplicity and reliability.
Tree-sitter would provide more accurate AST parsing but adds complexity.

Architecture: Per docs/Architecture.md - Phase 2: Static Analysis
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class StaticFinding:
    """Represents a finding from static analysis.

    Attributes:
        type: Category of finding (crash_risk, smell, architecture_signal, etc.)
        subtype: Specific pattern detected (force_unwrap, force_try, singleton, etc.)
        file: File path where finding was detected
        line: Line number of the finding
        code_snippet: Code snippet showing the issue

    Example:
        >>> StaticFinding(
        ...     type="crash_risk",
        ...     subtype="force_unwrap",
        ...     file="Services/WeatherClient.swift",
        ...     line=30,
        ...     code_snippet="let period = periods.first!"
        ... )
    """
    type: str
    subtype: str
    file: str
    line: int
    code_snippet: str


class SyntacticAnalyzer:
    """Performs static analysis on Swift source code.

    Uses regex-based pattern matching to detect:
    - Force unwraps (!)
    - Force try statements (try!)
    - Singleton patterns (static let shared)
    - Large classes (excessive method count)

    No AI is used - only traditional static analysis techniques.

    Example:
        >>> analyzer = SyntacticAnalyzer()
        >>> swift_code = "let value = optional!"
        >>> findings = analyzer.analyze(swift_code, "Test.swift")
        >>> len(findings)
        1
    """

    # Threshold for large class detection (number of methods)
    LARGE_CLASS_METHOD_THRESHOLD = 10

    def __init__(self):
        """Initialize SyntacticAnalyzer with regex patterns."""
        # Pattern for force unwrap: identifier followed by ! (not in string/comment)
        # Simplified: just look for word! pattern
        self.force_unwrap_pattern = re.compile(r'\w+!')

        # Pattern for force try: try! followed by expression
        # Matches: try! expression
        self.force_try_pattern = re.compile(r'\btry!\s+')

        # Pattern for singleton: static let shared =
        # Matches: static let shared = ClassName()
        self.singleton_pattern = re.compile(
            r'static\s+let\s+shared\s*=',
            re.IGNORECASE
        )

        # Pattern for method declarations
        # Matches: func methodName(...) { or func methodName(...) ->
        self.method_pattern = re.compile(
            r'^\s*func\s+\w+\s*\(',
            re.MULTILINE
        )

        # Pattern for class/struct/actor declarations
        # Matches: class ClassName {, struct StructName {, actor ActorName {
        self.class_pattern = re.compile(
            r'^\s*(class|struct|actor)\s+(\w+)',
            re.MULTILINE
        )

    def analyze(self, swift_code: str, file_path: str) -> List[StaticFinding]:
        """Analyze Swift source code and return static findings.

        Args:
            swift_code: Swift source code as string
            file_path: Path to the file being analyzed (for reporting)

        Returns:
            List of StaticFinding objects representing detected patterns

        Example:
            >>> analyzer = SyntacticAnalyzer()
            >>> code = \"\"\"
            ... let value = optional!
            ... let data = try! decode()
            ... \"\"\"
            >>> findings = analyzer.analyze(code, "Test.swift")
            >>> len(findings)
            2
        """
        findings = []

        # Handle empty code
        if not swift_code or not swift_code.strip():
            return findings

        # Remove strings and comments to avoid false positives
        cleaned_code = self._remove_strings_and_comments(swift_code)

        # Detect force unwraps
        findings.extend(self._detect_force_unwraps(cleaned_code, swift_code, file_path))

        # Detect force try
        findings.extend(self._detect_force_try(cleaned_code, swift_code, file_path))

        # Detect singletons
        findings.extend(self._detect_singletons(cleaned_code, swift_code, file_path))

        # Detect large classes
        findings.extend(self._detect_large_classes(swift_code, file_path))

        return findings

    def _remove_strings_and_comments(self, code: str) -> str:
        """Remove string literals and comments to avoid false positives.

        Args:
            code: Swift source code

        Returns:
            Code with strings and comments replaced by whitespace
        """
        # Remove multi-line comments /* ... */
        code = re.sub(r'/\*.*?\*/', ' ', code, flags=re.DOTALL)

        # Remove single-line comments // ...
        code = re.sub(r'//.*?$', ' ', code, flags=re.MULTILINE)

        # Remove string literals "..."
        code = re.sub(r'"(?:[^"\\]|\\.)*"', ' ', code)

        # Remove multi-line string literals """..."""
        code = re.sub(r'""".*?"""', ' ', code, flags=re.DOTALL)

        return code

    def _detect_force_unwraps(
        self,
        cleaned_code: str,
        original_code: str,
        file_path: str
    ) -> List[StaticFinding]:
        """Detect force unwrap operators (!)

        Args:
            cleaned_code: Code with strings/comments removed
            original_code: Original code for line number calculation
            file_path: File path for reporting

        Returns:
            List of StaticFinding objects for force unwraps
        """
        findings = []
        lines = original_code.split('\n')

        for line_num, line in enumerate(lines, start=1):
            # Skip lines that are comments or strings
            if line.strip().startswith('//') or line.strip().startswith('/*'):
                continue
            if '"' in line and '!' in line:
                # Check if ! is inside a string
                in_string = False
                for i, char in enumerate(line):
                    if char == '"' and (i == 0 or line[i-1] != '\\'):
                        in_string = not in_string
                    if char == '!' and not in_string:
                        # Found force unwrap outside string
                        break
                else:
                    # All ! were inside strings
                    continue

            # Look for force unwrap pattern
            if re.search(r'\w+!(?!\w)', line) and not line.strip().startswith('//'):
                # Extract snippet around the force unwrap
                snippet = line.strip()

                findings.append(StaticFinding(
                    type="crash_risk",
                    subtype="force_unwrap",
                    file=file_path,
                    line=line_num,
                    code_snippet=snippet
                ))

        return findings

    def _detect_force_try(
        self,
        cleaned_code: str,
        original_code: str,
        file_path: str
    ) -> List[StaticFinding]:
        """Detect force try statements (try!)

        Args:
            cleaned_code: Code with strings/comments removed
            original_code: Original code for line number calculation
            file_path: File path for reporting

        Returns:
            List of StaticFinding objects for force try
        """
        findings = []
        lines = original_code.split('\n')

        for line_num, line in enumerate(lines, start=1):
            if 'try!' in line and not line.strip().startswith('//'):
                snippet = line.strip()

                findings.append(StaticFinding(
                    type="crash_risk",
                    subtype="force_try",
                    file=file_path,
                    line=line_num,
                    code_snippet=snippet
                ))

        return findings

    def _detect_singletons(
        self,
        cleaned_code: str,
        original_code: str,
        file_path: str
    ) -> List[StaticFinding]:
        """Detect singleton pattern (static let shared)

        Args:
            cleaned_code: Code with strings/comments removed
            original_code: Original code for line number calculation
            file_path: File path for reporting

        Returns:
            List of StaticFinding objects for singletons
        """
        findings = []
        lines = original_code.split('\n')

        for line_num, line in enumerate(lines, start=1):
            if self.singleton_pattern.search(line):
                snippet = line.strip()

                findings.append(StaticFinding(
                    type="structural_smell",
                    subtype="singleton",
                    file=file_path,
                    line=line_num,
                    code_snippet=snippet
                ))

        return findings

    def _detect_large_classes(
        self,
        original_code: str,
        file_path: str
    ) -> List[StaticFinding]:
        """Detect large classes based on method count.

        Args:
            original_code: Original code
            file_path: File path for reporting

        Returns:
            List of StaticFinding objects for large classes
        """
        findings = []

        # Find all class/struct/actor declarations
        class_matches = list(self.class_pattern.finditer(original_code))

        for class_match in class_matches:
            class_type = class_match.group(1)
            class_name = class_match.group(2)
            class_start = class_match.start()

            # Find the extent of this class (simplified: until next class or end)
            next_class_start = len(original_code)
            for other_match in class_matches:
                if other_match.start() > class_start:
                    next_class_start = other_match.start()
                    break

            class_body = original_code[class_start:next_class_start]

            # Count methods in this class
            method_count = len(self.method_pattern.findall(class_body))

            if method_count >= self.LARGE_CLASS_METHOD_THRESHOLD:
                # Calculate line number
                line_num = original_code[:class_start].count('\n') + 1

                findings.append(StaticFinding(
                    type="structural_smell",
                    subtype="large_class",
                    file=file_path,
                    line=line_num,
                    code_snippet=f"{class_type} {class_name} (...)  // {method_count} methods"
                ))

        return findings

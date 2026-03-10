"""
Syntactic Analyzer module for static code analysis.

This module implements Phase 2 of the analysis pipeline: Static Analysis.
It detects structural patterns and syntactic risk signals using tree-sitter
AST parsing for accurate Swift code analysis.

Per Architecture.md:
- Detect force unwraps (!)
- Detect force try (try!)
- Detect singleton usage (static let shared)
- Detect large classes (method count heuristic)
- Use traditional techniques (no AI)

Uses tree-sitter Swift parser for accurate AST-based pattern detection,
providing better accuracy than regex-based approaches.

Architecture: Per docs/Architecture.md - Phase 2: Static Analysis
"""

from tree_sitter import Language, Parser
import tree_sitter_swift
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
    """Performs static analysis on Swift source code using tree-sitter.

    Uses tree-sitter AST parsing to detect:
    - Force unwraps (!)
    - Force try statements (try!)
    - Singleton patterns (static let shared)
    - Large classes (excessive method count)

    No AI is used - only traditional static analysis with AST traversal.

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
        """Initialize SyntacticAnalyzer with tree-sitter parser."""
        self.parser = Parser(Language(tree_sitter_swift.language()))

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

        # Parse the Swift code into an AST
        try:
            tree = self.parser.parse(bytes(swift_code, 'utf8'))
        except Exception as e:
            # If parsing fails, return empty findings rather than crashing
            return findings

        # Store the original code for extracting snippets
        self.swift_code = swift_code
        self.lines = swift_code.split('\n')

        # Detect force unwraps
        findings.extend(self._detect_force_unwraps(tree.root_node, file_path))

        # Detect force try
        findings.extend(self._detect_force_try(tree.root_node, file_path))

        # Detect singletons
        findings.extend(self._detect_singletons(tree.root_node, file_path))

        # Detect large classes
        findings.extend(self._detect_large_classes(tree.root_node, file_path))

        return findings

    def _detect_force_unwraps(self, node, file_path: str) -> List[StaticFinding]:
        """Detect force unwrap operators (!) using AST traversal.

        Args:
            node: Tree-sitter AST node
            file_path: File path for reporting

        Returns:
            List of StaticFinding objects for force unwraps
        """
        findings = []

        # Look for postfix_expression nodes with "bang" child (force unwrap operator)
        if node.type == 'postfix_expression':
            # Check if it has a "bang" child (force unwrap operator)
            has_force_unwrap = False
            for child in node.children:
                if child.type == 'bang':
                    has_force_unwrap = True
                    break

            if has_force_unwrap:
                line_num = node.start_point[0] + 1
                code_snippet = self._get_line_snippet(line_num)

                findings.append(StaticFinding(
                    type="crash_risk",
                    subtype="force_unwrap",
                    file=file_path,
                    line=line_num,
                    code_snippet=code_snippet
                ))

        # Recursively search children
        for child in node.children:
            findings.extend(self._detect_force_unwraps(child, file_path))

        return findings

    def _detect_force_try(self, node, file_path: str) -> List[StaticFinding]:
        """Detect force try statements (try!) using AST traversal.

        Args:
            node: Tree-sitter AST node
            file_path: File path for reporting

        Returns:
            List of StaticFinding objects for force try
        """
        findings = []

        # Look for try_expression with try_operator containing "!"
        if node.type == 'try_expression':
            # Check if it has a try_operator child with "!"
            has_force_try = False
            for child in node.children:
                if child.type == 'try_operator':
                    # Check if try_operator has a "!" child
                    for try_op_child in child.children:
                        if try_op_child.type == '!' or (hasattr(try_op_child, 'text') and try_op_child.text == b'!'):
                            has_force_try = True
                            break
                if has_force_try:
                    break

            if has_force_try:
                line_num = node.start_point[0] + 1
                code_snippet = self._get_line_snippet(line_num)

                findings.append(StaticFinding(
                    type="crash_risk",
                    subtype="force_try",
                    file=file_path,
                    line=line_num,
                    code_snippet=code_snippet
                ))

        # Recursively search children
        for child in node.children:
            findings.extend(self._detect_force_try(child, file_path))

        return findings

    def _detect_singletons(self, node, file_path: str) -> List[StaticFinding]:
        """Detect singleton pattern (static let shared) using AST traversal.

        Args:
            node: Tree-sitter AST node
            file_path: File path for reporting

        Returns:
            List of StaticFinding objects for singletons
        """
        findings = []

        # Look for property_declaration with "static" modifier
        if node.type == 'property_declaration':
            # Check if it has "static" modifier
            has_static = False
            is_let = False
            has_shared_name = False

            for child in node.children:
                # Check for modifiers
                if child.type == 'modifiers':
                    for modifier in child.children:
                        if hasattr(modifier, 'text') and modifier.text == b'static':
                            has_static = True

                # Check for "let"
                if hasattr(child, 'text') and child.text == b'let':
                    is_let = True

                # Check for pattern with "shared" identifier
                if child.type == 'pattern':
                    for pattern_child in child.children:
                        if pattern_child.type == 'simple_identifier' and \
                           hasattr(pattern_child, 'text') and pattern_child.text == b'shared':
                            has_shared_name = True

            # If we found "static let shared = ...", report it
            if has_static and is_let and has_shared_name:
                line_num = node.start_point[0] + 1
                code_snippet = self._get_line_snippet(line_num)

                findings.append(StaticFinding(
                    type="structural_smell",
                    subtype="singleton",
                    file=file_path,
                    line=line_num,
                    code_snippet=code_snippet
                ))

        # Recursively search children
        for child in node.children:
            findings.extend(self._detect_singletons(child, file_path))

        return findings

    def _detect_large_classes(self, node, file_path: str) -> List[StaticFinding]:
        """Detect large classes based on method count using AST traversal.

        Args:
            node: Tree-sitter AST node
            file_path: File path for reporting

        Returns:
            List of StaticFinding objects for large classes
        """
        findings = []

        # Look for class_declaration, struct_declaration, or actor_declaration
        if node.type in ['class_declaration', 'struct_declaration', 'actor_declaration']:
            class_type = node.type.replace('_declaration', '')
            class_name = None

            # Find the class/struct/actor name
            for child in node.children:
                if child.type == 'type_identifier':
                    class_name = child.text.decode('utf8') if isinstance(child.text, bytes) else str(child.text)
                    break

            if class_name:
                # Count methods in the class body
                method_count = self._count_methods(node)

                if method_count >= self.LARGE_CLASS_METHOD_THRESHOLD:
                    line_num = node.start_point[0] + 1
                    code_snippet = f"{class_type} {class_name} (...)  // {method_count} methods"

                    findings.append(StaticFinding(
                        type="structural_smell",
                        subtype="large_class",
                        file=file_path,
                        line=line_num,
                        code_snippet=code_snippet
                    ))

        # Recursively search children (but don't double-count nested classes)
        for child in node.children:
            if child.type != node.type:  # Don't count nested classes as separate
                findings.extend(self._detect_large_classes(child, file_path))

        return findings

    def _count_methods(self, class_node) -> int:
        """Count the number of methods in a class/struct/actor declaration.

        Args:
            class_node: Tree-sitter AST node for class/struct/actor

        Returns:
            Number of method declarations found
        """
        count = 0

        def traverse(node):
            nonlocal count
            if node.type == 'function_declaration':
                count += 1
            for child in node.children:
                traverse(child)

        traverse(class_node)
        return count

    def _get_line_snippet(self, line_num: int) -> str:
        """Extract a code snippet from the given line number.

        Args:
            line_num: Line number (1-indexed)

        Returns:
            Stripped code snippet from that line
        """
        if 1 <= line_num <= len(self.lines):
            return self.lines[line_num - 1].strip()
        return ""

"""
Test suite for SyntacticAnalyzer module.

The SyntacticAnalyzer performs Phase 2 of the analysis pipeline: Static Analysis.
It uses tree-sitter Swift parser to detect structural patterns and syntactic risk signals.

Requirements from Architecture.md:
- Detect force unwraps (!)
- Detect force try (try!)
- Detect singleton usage (static let shared)
- Detect large classes (method count heuristic)
- No AI used - traditional techniques only

RED PHASE: These tests should FAIL initially since SyntacticAnalyzer doesn't exist yet.
"""

import pytest
from pathlib import Path


class TestForceUnwrapDetection:
    """Test detection of force unwrap operators (!)."""

    def test_detects_simple_force_unwrap(self):
        """Verify analyzer detects basic force unwrap (variable!)."""
        swift_code = """
        let value = optional!
        """

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        force_unwraps = [f for f in findings if f.subtype == "force_unwrap"]
        assert len(force_unwraps) >= 1
        assert any("optional!" in f.code_snippet for f in force_unwraps)

    def test_detects_force_unwrap_on_method_call(self):
        """Verify analyzer detects force unwrap on method results."""
        swift_code = """
        let period = response.periods.first!
        """

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        force_unwraps = [f for f in findings if f.subtype == "force_unwrap"]
        assert len(force_unwraps) >= 1
        assert any("first!" in f.code_snippet for f in force_unwraps)

    def test_detects_multiple_force_unwraps(self):
        """Verify analyzer detects multiple force unwraps in same file."""
        swift_code = """
        let a = optional1!
        let b = optional2!
        let c = optional3!
        """

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        force_unwraps = [f for f in findings if f.subtype == "force_unwrap"]
        assert len(force_unwraps) == 3

    def test_ignores_non_force_unwrap_exclamation(self):
        """Verify analyzer doesn't confuse ! in strings or comments with force unwrap."""
        swift_code = """
        let message = "Hello!"
        // This is a comment!
        """

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        force_unwraps = [f for f in findings if f.subtype == "force_unwrap"]
        assert len(force_unwraps) == 0


class TestForceTryDetection:
    """Test detection of force try statements (try!)."""

    def test_detects_simple_force_try(self):
        """Verify analyzer detects basic force try statement."""
        swift_code = """
        let data = try! decoder.decode(Type.self, from: data)
        """

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        force_tries = [f for f in findings if f.subtype == "force_try"]
        assert len(force_tries) >= 1
        assert any("try!" in f.code_snippet for f in force_tries)

    def test_detects_multiple_force_tries(self):
        """Verify analyzer detects multiple force try statements."""
        swift_code = """
        let a = try! operation1()
        let b = try! operation2()
        """

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        force_tries = [f for f in findings if f.subtype == "force_try"]
        assert len(force_tries) == 2

    def test_ignores_regular_try(self):
        """Verify analyzer distinguishes between try! and regular try."""
        swift_code = """
        let data = try decoder.decode(Type.self, from: data)
        """

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        force_tries = [f for f in findings if f.subtype == "force_try"]
        assert len(force_tries) == 0


class TestSingletonDetection:
    """Test detection of singleton pattern (static let shared)."""

    def test_detects_static_let_shared(self):
        """Verify analyzer detects singleton pattern with 'static let shared'."""
        swift_code = """
        class MyService {
            static let shared = MyService()
            private init() {}
        }
        """

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        singletons = [f for f in findings if f.subtype == "singleton"]
        assert len(singletons) >= 1
        assert any("shared" in f.code_snippet for f in singletons)

    def test_detects_multiple_singletons(self):
        """Verify analyzer detects multiple singleton classes in same file."""
        swift_code = """
        class ServiceA {
            static let shared = ServiceA()
        }
        class ServiceB {
            static let shared = ServiceB()
        }
        """

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        singletons = [f for f in findings if f.subtype == "singleton"]
        assert len(singletons) == 2

    def test_ignores_non_singleton_static_properties(self):
        """Verify analyzer doesn't flag regular static properties as singletons."""
        swift_code = """
        class Config {
            static let version = "1.0"
            static let timeout = 30
        }
        """

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        singletons = [f for f in findings if f.subtype == "singleton"]
        # Should not detect non-shared static properties as singletons
        assert len(singletons) == 0


class TestLargeClassDetection:
    """Test detection of large classes based on method count."""

    def test_detects_class_with_many_methods(self):
        """Verify analyzer detects classes with excessive methods."""
        # Create class with 15 methods (threshold typically 10-15)
        methods = "\n".join([f"    func method{i}() {{ }}" for i in range(15)])
        swift_code = f"""
        class LargeClass {{
{methods}
        }}
        """

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        large_classes = [f for f in findings if f.subtype == "large_class"]
        assert len(large_classes) >= 1

    def test_ignores_small_classes(self):
        """Verify analyzer doesn't flag classes with few methods."""
        swift_code = """
        class SmallClass {
            func method1() { }
            func method2() { }
            func method3() { }
        }
        """

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        large_classes = [f for f in findings if f.subtype == "large_class"]
        assert len(large_classes) == 0


class TestStaticFindingStructure:
    """Test StaticFinding dataclass structure."""

    def test_finding_has_required_fields(self):
        """Verify StaticFinding contains all required fields per Architecture.md."""
        swift_code = "let value = optional!"

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        assert len(findings) >= 1
        finding = findings[0]

        # Required fields per Architecture.md
        assert hasattr(finding, 'type')
        assert hasattr(finding, 'subtype')
        assert hasattr(finding, 'file')
        assert hasattr(finding, 'line')
        assert hasattr(finding, 'code_snippet')

    def test_finding_type_is_crash_risk(self):
        """Verify force unwrap findings have type 'crash_risk'."""
        swift_code = "let value = optional!"

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        force_unwraps = [f for f in findings if f.subtype == "force_unwrap"]
        assert len(force_unwraps) >= 1
        assert force_unwraps[0].type == "crash_risk"

    def test_finding_includes_line_number(self):
        """Verify findings include accurate line numbers."""
        swift_code = """
        let a = 1
        let b = optional!
        let c = 3
        """

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        force_unwraps = [f for f in findings if f.subtype == "force_unwrap"]
        assert len(force_unwraps) >= 1
        # Should be on line 3 (line 2 is the force unwrap)
        assert force_unwraps[0].line >= 2


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_empty_swift_file(self):
        """Verify analyzer handles empty file without crashing."""
        swift_code = ""

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Empty.swift")

        assert findings == []

    def test_handles_syntax_errors_gracefully(self):
        """Verify analyzer handles invalid Swift syntax without crashing."""
        swift_code = "this is not valid swift syntax { { {"

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        # Should not crash, may return empty or partial results
        findings = analyzer.analyze(swift_code, file_path="Invalid.swift")

        # Should return a list (possibly empty), not crash
        assert isinstance(findings, list)

    def test_handles_multiline_code(self):
        """Verify analyzer correctly processes multi-line Swift code."""
        swift_code = """
        import Foundation

        class MyClass {
            static let shared = MyClass()

            func process() {
                let value = optional!
                let data = try! loadData()
            }
        }
        """

        from core.syntactic_analyzer import SyntacticAnalyzer

        analyzer = SyntacticAnalyzer()
        findings = analyzer.analyze(swift_code, file_path="Test.swift")

        # Should find singleton, force unwrap, and force try
        assert len(findings) >= 3

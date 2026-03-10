"""
Test suite for GraphBuilder module.

The GraphBuilder extracts dependency relationships from Swift source files.
It's part of Phase 2 (Static Analysis) and provides input for Phase 4 (Semantic Analysis).

Per Architecture.md - simplified approach:
- Extract import statements
- Extract class/struct/actor references
- Build lightweight dependency lists (not full graph)

RED PHASE: These tests should FAIL initially since GraphBuilder doesn't exist yet.
"""

import pytest
from pathlib import Path


class TestImportExtraction:
    """Test extraction of import statements."""

    def test_extracts_simple_import(self):
        """Verify graph builder extracts basic import statements."""
        swift_code = """
        import Foundation
        """

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        imports = builder.extract_imports(swift_code)

        assert "Foundation" in imports

    def test_extracts_multiple_imports(self):
        """Verify graph builder extracts multiple import statements."""
        swift_code = """
        import Foundation
        import UIKit
        import CoreLocation
        """

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        imports = builder.extract_imports(swift_code)

        assert len(imports) == 3
        assert "Foundation" in imports
        assert "UIKit" in imports
        assert "CoreLocation" in imports

    def test_extracts_specific_imports(self):
        """Verify graph builder handles specific imports (import class X)."""
        swift_code = """
        import class Foundation.JSONDecoder
        import struct Foundation.URL
        """

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        imports = builder.extract_imports(swift_code)

        # Should extract the module name (Foundation)
        assert "Foundation" in imports

    def test_ignores_comments_with_import_keyword(self):
        """Verify graph builder ignores 'import' in comments."""
        swift_code = """
        // import FakeModule
        /* import AnotherFake */
        import RealModule
        """

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        imports = builder.extract_imports(swift_code)

        assert "RealModule" in imports
        assert "FakeModule" not in imports
        assert "AnotherFake" not in imports


class TestTypeExtraction:
    """Test extraction of type declarations (class, struct, actor)."""

    def test_extracts_class_name(self):
        """Verify graph builder extracts class declarations."""
        swift_code = """
        class JournalStore {
            let name = "test"
        }
        """

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        types = builder.extract_types(swift_code)

        assert "JournalStore" in types

    def test_extracts_struct_name(self):
        """Verify graph builder extracts struct declarations."""
        swift_code = """
        struct SleepEntry {
            let id: UUID
        }
        """

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        types = builder.extract_types(swift_code)

        assert "SleepEntry" in types

    def test_extracts_actor_name(self):
        """Verify graph builder extracts actor declarations."""
        swift_code = """
        actor DataManager {
            var count = 0
        }
        """

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        types = builder.extract_types(swift_code)

        assert "DataManager" in types

    def test_extracts_multiple_types(self):
        """Verify graph builder extracts multiple type declarations."""
        swift_code = """
        class ServiceA { }
        struct ModelB { }
        actor ManagerC { }
        """

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        types = builder.extract_types(swift_code)

        assert len(types) == 3
        assert "ServiceA" in types
        assert "ModelB" in types
        assert "ManagerC" in types

    def test_ignores_nested_types(self):
        """Verify graph builder handles nested type declarations."""
        swift_code = """
        class Outer {
            struct Inner {
                let value: Int
            }
        }
        """

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        types = builder.extract_types(swift_code)

        # Should extract both types
        assert "Outer" in types
        # May or may not extract Inner depending on implementation


class TestDependencyBuilding:
    """Test building dependency relationships."""

    def test_builds_dependency_dict(self):
        """Verify build_dependencies returns dict mapping files to their dependencies."""
        file_data_list = [
            type('FileData', (), {
                'path': 'Services/Store.swift',
                'content': 'import Foundation\nclass Store { }'
            })()
        ]

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        deps = builder.build_dependencies(file_data_list)

        assert isinstance(deps, dict)
        assert 'Services/Store.swift' in deps

    def test_includes_imports_in_dependencies(self):
        """Verify dependencies include imported modules."""
        file_data_list = [
            type('FileData', (), {
                'path': 'Test.swift',
                'content': 'import Foundation\nimport UIKit\nclass Test { }'
            })()
        ]

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        deps = builder.build_dependencies(file_data_list)

        file_deps = deps['Test.swift']
        assert 'Foundation' in file_deps
        assert 'UIKit' in file_deps

    def test_includes_types_in_dependencies(self):
        """Verify dependencies include defined types."""
        file_data_list = [
            type('FileData', (), {
                'path': 'Models.swift',
                'content': 'struct User { }\nclass Session { }'
            })()
        ]

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        deps = builder.build_dependencies(file_data_list)

        file_deps = deps['Models.swift']
        assert 'User' in file_deps or 'Session' in file_deps

    def test_handles_multiple_files(self):
        """Verify build_dependencies handles multiple files."""
        file_data_list = [
            type('FileData', (), {
                'path': 'A.swift',
                'content': 'import Foundation\nclass A { }'
            })(),
            type('FileData', (), {
                'path': 'B.swift',
                'content': 'import UIKit\nstruct B { }'
            })()
        ]

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        deps = builder.build_dependencies(file_data_list)

        assert len(deps) == 2
        assert 'A.swift' in deps
        assert 'B.swift' in deps


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_empty_file(self):
        """Verify graph builder handles empty file without crashing."""
        swift_code = ""

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        imports = builder.extract_imports(swift_code)
        types = builder.extract_types(swift_code)

        assert imports == []
        assert types == []

    def test_handles_file_with_no_imports(self):
        """Verify graph builder handles file with no import statements."""
        swift_code = """
        class LocalClass {
            let value = 42
        }
        """

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        imports = builder.extract_imports(swift_code)

        assert imports == []

    def test_handles_file_with_no_types(self):
        """Verify graph builder handles file with no type declarations."""
        swift_code = """
        import Foundation
        let globalVar = 42
        func globalFunc() { }
        """

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        types = builder.extract_types(swift_code)

        assert types == []

    def test_handles_invalid_syntax(self):
        """Verify graph builder handles invalid Swift syntax gracefully."""
        swift_code = "this is not valid swift { { {"

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        # Should not crash, may return empty results
        imports = builder.extract_imports(swift_code)
        types = builder.extract_types(swift_code)

        assert isinstance(imports, list)
        assert isinstance(types, list)

    def test_handles_protocol_declarations(self):
        """Verify graph builder can handle protocol declarations."""
        swift_code = """
        protocol Storable {
            func save()
        }
        """

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        types = builder.extract_types(swift_code)

        # May or may not extract protocols depending on implementation
        # At minimum, should not crash
        assert isinstance(types, list)

    def test_handles_extension_declarations(self):
        """Verify graph builder handles extension declarations."""
        swift_code = """
        extension String {
            func customMethod() { }
        }
        """

        from core.graph_builder import GraphBuilder

        builder = GraphBuilder()
        types = builder.extract_types(swift_code)

        # Extensions may or may not be extracted
        # At minimum, should not crash
        assert isinstance(types, list)

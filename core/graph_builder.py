"""
Graph Builder module for dependency extraction.

This module extracts dependency relationships from Swift source files.
It's part of Phase 2 (Static Analysis) and provides structured dependency
information for Phase 4 (Semantic Analysis).

Per Architecture.md - simplified approach:
- Extract import statements
- Extract type declarations (class, struct, actor)
- Build lightweight dependency lists (not a full graph data structure)

No AI is used - only regex-based pattern matching.

Architecture: Per docs/Architecture.md - Phase 2: Static Analysis
"""

import re
from typing import List, Dict, Any
from dataclasses import dataclass


class GraphBuilder:
    """Extracts dependency information from Swift source files.

    Provides simplified dependency extraction:
    - Import statements (external dependencies)
    - Type declarations (internal types defined)
    - Dependency mapping (file -> list of dependencies)

    Example:
        >>> builder = GraphBuilder()
        >>> code = "import Foundation\\nclass Store { }"
        >>> imports = builder.extract_imports(code)
        >>> imports
        ['Foundation']
        >>> types = builder.extract_types(code)
        >>> types
        ['Store']
    """

    def __init__(self):
        """Initialize GraphBuilder with regex patterns."""
        # Pattern for import statements
        # Matches: import Module, import class Module.Class, import struct Module.Struct
        self.import_pattern = re.compile(
            r'^\s*import\s+(?:class|struct|func|enum|typealias)?\s*(\w+)',
            re.MULTILINE
        )

        # Pattern for type declarations
        # Matches: class Name, struct Name, actor Name, protocol Name
        self.type_pattern = re.compile(
            r'^\s*(class|struct|actor|protocol|enum)\s+(\w+)',
            re.MULTILINE
        )

    def extract_imports(self, swift_code: str) -> List[str]:
        """Extract import statements from Swift code.

        Args:
            swift_code: Swift source code as string

        Returns:
            List of imported module names

        Example:
            >>> builder = GraphBuilder()
            >>> code = "import Foundation\\nimport UIKit"
            >>> builder.extract_imports(code)
            ['Foundation', 'UIKit']
        """
        if not swift_code or not swift_code.strip():
            return []

        # Remove comments to avoid false positives
        cleaned_code = self._remove_comments(swift_code)

        # Find all import statements
        matches = self.import_pattern.findall(cleaned_code)

        # Return unique imports
        return list(dict.fromkeys(matches))  # Preserves order, removes duplicates

    def extract_types(self, swift_code: str) -> List[str]:
        """Extract type declarations from Swift code.

        Extracts class, struct, actor, protocol, and enum declarations.

        Args:
            swift_code: Swift source code as string

        Returns:
            List of type names defined in the code

        Example:
            >>> builder = GraphBuilder()
            >>> code = "class Store { }\\nstruct Entry { }"
            >>> builder.extract_types(code)
            ['Store', 'Entry']
        """
        if not swift_code or not swift_code.strip():
            return []

        # Remove comments to avoid false positives
        cleaned_code = self._remove_comments(swift_code)

        # Find all type declarations
        matches = self.type_pattern.findall(cleaned_code)

        # Extract type names (second group in the pattern)
        type_names = [match[1] for match in matches]

        # Return unique types
        return list(dict.fromkeys(type_names))

    def build_dependencies(self, file_data_list: List[Any]) -> Dict[str, List[str]]:
        """Build dependency mapping for a list of files.

        Creates a dictionary mapping each file path to its dependencies
        (imports and defined types).

        Args:
            file_data_list: List of FileData objects with 'path' and 'content' attributes

        Returns:
            Dictionary mapping file paths to lists of dependencies

        Example:
            >>> builder = GraphBuilder()
            >>> files = [FileData(path="A.swift", content="import Foundation\\nclass A { }")]
            >>> deps = builder.build_dependencies(files)
            >>> deps['A.swift']
            ['Foundation', 'A']
        """
        dependencies = {}

        for file_data in file_data_list:
            file_path = file_data.path
            file_content = file_data.content

            # Extract imports and types for this file
            imports = self.extract_imports(file_content)
            types = self.extract_types(file_content)

            # Combine into single dependency list
            file_deps = imports + types

            dependencies[file_path] = file_deps

        return dependencies

    def _remove_comments(self, code: str) -> str:
        """Remove single-line and multi-line comments from code.

        Args:
            code: Swift source code

        Returns:
            Code with comments replaced by whitespace
        """
        # Remove multi-line comments /* ... */
        code = re.sub(r'/\*.*?\*/', ' ', code, flags=re.DOTALL)

        # Remove single-line comments // ...
        code = re.sub(r'//.*?$', ' ', code, flags=re.MULTILINE)

        return code

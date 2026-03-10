"""
Scanner module for discovering Swift source files.

This module implements Phase 1 of the analysis pipeline: Codebase Scan.
It discovers all Swift source files in a directory tree while ignoring
build artifacts and version control directories.

Architecture: Per docs/Architecture.md - Phase 1: Codebase Scan
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class FileData:
    """Represents a discovered Swift source file.

    Attributes:
        path: Relative path from repo root to the Swift file
        content: Full text content of the Swift file

    Example:
        >>> FileData(
        ...     path="Services/JournalStore.swift",
        ...     content="import Foundation\\n\\nclass JournalStore { }"
        ... )
    """
    path: str
    content: str


class Scanner:
    """Discovers Swift source files in a repository directory tree.

    The scanner recursively searches for *.swift files while ignoring
    common build artifact directories (.git, build, DerivedData, etc.).

    Per Architecture.md requirements:
    - Only scan *.swift files
    - Ignore build folders
    - Ignore .git directory

    Attributes:
        repo_path: Path to the repository root directory

    Example:
        >>> scanner = Scanner(repo_path=Path("Sleep Journal"))
        >>> files = scanner.scan()
        >>> len(files)
        13
    """

    # Directories to ignore during scanning (build artifacts, version control)
    IGNORED_DIRS = {
        ".git",           # Git version control
        "build",          # Generic build directory
        "Build",          # Xcode build directory
        ".build",         # Swift Package Manager build directory
        "DerivedData",    # Xcode derived data
        ".swiftpm",       # Swift Package Manager cache
        "Pods",           # CocoaPods dependencies
        "Carthage",       # Carthage dependencies
        ".bundle",        # Ruby bundler
        "node_modules",   # Node.js dependencies (if present)
        "__pycache__",    # Python cache (if present)
        ".pytest_cache",  # Pytest cache (for this project)
    }

    def __init__(self, repo_path: Path):
        """Initialize Scanner with repository path.

        Args:
            repo_path: Path to the repository root directory

        Raises:
            ValueError: If repo_path doesn't exist or isn't a directory
        """
        self.repo_path = Path(repo_path)

        # Validate repo_path exists
        if not self.repo_path.exists():
            raise ValueError(
                f"Repository path does not exist: {self.repo_path}"
            )

        # Validate repo_path is a directory
        if not self.repo_path.is_dir():
            raise ValueError(
                f"Repository path is not a directory: {self.repo_path}"
            )

    def scan(self) -> List[FileData]:
        """Scan repository and discover all Swift source files.

        Recursively searches for *.swift files while ignoring directories
        in IGNORED_DIRS set.

        Returns:
            List of FileData objects containing path and content for each
            discovered Swift file. Returns empty list if no Swift files found.

        Example:
            >>> scanner = Scanner(repo_path=Path("/path/to/repo"))
            >>> files = scanner.scan()
            >>> for file in files:
            ...     print(f"{file.path}: {len(file.content)} chars")
        """
        swift_files = []

        # Recursively walk directory tree
        for swift_path in self._find_swift_files(self.repo_path):
            # Read file content
            content = swift_path.read_text(encoding='utf-8')

            # Calculate relative path from repo root
            try:
                relative_path = swift_path.relative_to(self.repo_path)
            except ValueError:
                # If relative_to fails, use absolute path as fallback
                relative_path = swift_path

            # Create FileData object
            file_data = FileData(
                path=str(relative_path),
                content=content
            )
            swift_files.append(file_data)

        return swift_files

    def _find_swift_files(self, directory: Path) -> List[Path]:
        """Recursively find all .swift files in directory.

        Args:
            directory: Directory to search

        Returns:
            List of Path objects for discovered .swift files
        """
        swift_files = []

        try:
            for item in directory.iterdir():
                # Skip ignored directories
                if item.is_dir() and item.name in self.IGNORED_DIRS:
                    continue

                # Recursively search subdirectories
                if item.is_dir():
                    swift_files.extend(self._find_swift_files(item))

                # Add Swift files
                elif item.is_file() and item.suffix == '.swift':
                    swift_files.append(item)

        except PermissionError:
            # Skip directories we don't have permission to read
            pass

        return swift_files

"""
Test suite for Scanner module.

The Scanner is responsible for discovering Swift source files in a directory tree.
It's the entry point (Phase 1) of the analysis pipeline per Architecture.md.

Requirements from Architecture.md:
- Scan *.swift files only
- Ignore build folders
- Ignore .git directory

RED PHASE: These tests should FAIL initially since Scanner doesn't exist yet.
"""

import pytest
from pathlib import Path
from dataclasses import dataclass


class TestScannerBasicFunctionality:
    """Test basic Swift file discovery."""

    def test_scanner_finds_swift_files_in_directory(self, tmp_path):
        """Verify scanner discovers all .swift files in a directory."""
        # Create test directory structure with Swift files
        (tmp_path / "test1.swift").write_text("class Test1 {}")
        (tmp_path / "test2.swift").write_text("struct Test2 {}")

        from core.scanner import Scanner

        scanner = Scanner(repo_path=tmp_path)
        files = scanner.scan()

        assert len(files) == 2
        swift_files = [f.path for f in files]
        assert any("test1.swift" in str(p) for p in swift_files)
        assert any("test2.swift" in str(p) for p in swift_files)

    def test_scanner_finds_swift_files_in_nested_directories(self, tmp_path):
        """Verify scanner recursively discovers Swift files in subdirectories."""
        # Create nested directory structure
        services_dir = tmp_path / "Services"
        services_dir.mkdir()
        models_dir = tmp_path / "Models"
        models_dir.mkdir()
        ui_dir = tmp_path / "UI" / "Components"
        ui_dir.mkdir(parents=True)

        (services_dir / "JournalStore.swift").write_text("class JournalStore {}")
        (models_dir / "SleepEntry.swift").write_text("struct SleepEntry {}")
        (ui_dir / "Button.swift").write_text("struct Button: View {}")

        from core.scanner import Scanner

        scanner = Scanner(repo_path=tmp_path)
        files = scanner.scan()

        assert len(files) == 3
        paths = [f.path for f in files]
        assert any("JournalStore.swift" in str(p) for p in paths)
        assert any("SleepEntry.swift" in str(p) for p in paths)
        assert any("Button.swift" in str(p) for p in paths)

    def test_scanner_returns_file_content(self, tmp_path):
        """Verify scanner reads and returns file content."""
        test_file = tmp_path / "Example.swift"
        test_content = "import Foundation\n\nclass Example {\n    let value = 42\n}"
        test_file.write_text(test_content)

        from core.scanner import Scanner

        scanner = Scanner(repo_path=tmp_path)
        files = scanner.scan()

        assert len(files) == 1
        assert files[0].content == test_content

    def test_scanner_returns_relative_paths(self, tmp_path):
        """Verify scanner returns paths relative to repo_path."""
        subdir = tmp_path / "src" / "models"
        subdir.mkdir(parents=True)
        (subdir / "User.swift").write_text("struct User {}")

        from core.scanner import Scanner

        scanner = Scanner(repo_path=tmp_path)
        files = scanner.scan()

        assert len(files) == 1
        # Path should be relative to tmp_path (repo root)
        assert files[0].path == "src/models/User.swift" or \
               files[0].path == str(Path("src/models/User.swift"))


class TestScannerIgnorePatterns:
    """Test that scanner correctly ignores specific directories."""

    def test_scanner_ignores_build_directory(self, tmp_path):
        """Verify scanner ignores build/ directory per Architecture.md."""
        # Create build directory with Swift files (should be ignored)
        build_dir = tmp_path / "build"
        build_dir.mkdir()
        (build_dir / "Generated.swift").write_text("class Generated {}")

        # Create legitimate Swift file
        (tmp_path / "Source.swift").write_text("class Source {}")

        from core.scanner import Scanner

        scanner = Scanner(repo_path=tmp_path)
        files = scanner.scan()

        # Should only find Source.swift, not Generated.swift from build/
        assert len(files) == 1
        assert "Source.swift" in str(files[0].path)
        assert "Generated.swift" not in str(files[0].path)

    def test_scanner_ignores_git_directory(self, tmp_path):
        """Verify scanner ignores .git/ directory per Architecture.md."""
        # Create .git directory with files (should be ignored)
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "hooks.swift").write_text("// Git hooks")

        # Create legitimate Swift file
        (tmp_path / "App.swift").write_text("class App {}")

        from core.scanner import Scanner

        scanner = Scanner(repo_path=tmp_path)
        files = scanner.scan()

        # Should only find App.swift, not hooks.swift from .git/
        assert len(files) == 1
        assert "App.swift" in str(files[0].path)
        assert ".git" not in str(files[0].path)

    def test_scanner_ignores_derived_data_directory(self, tmp_path):
        """Verify scanner ignores DerivedData/ directory (Xcode build artifacts)."""
        # Create DerivedData directory (common Xcode artifact location)
        derived_dir = tmp_path / "DerivedData"
        derived_dir.mkdir()
        (derived_dir / "Artifact.swift").write_text("// Build artifact")

        # Create legitimate Swift file
        (tmp_path / "Main.swift").write_text("@main struct Main {}")

        from core.scanner import Scanner

        scanner = Scanner(repo_path=tmp_path)
        files = scanner.scan()

        # Should only find Main.swift
        assert len(files) == 1
        assert "Main.swift" in str(files[0].path)

    def test_scanner_ignores_multiple_build_directories(self, tmp_path):
        """Verify scanner ignores all common build/artifact directories."""
        # Create multiple build-related directories
        for build_dir_name in ["build", ".build", "DerivedData", "Pods"]:
            build_dir = tmp_path / build_dir_name
            build_dir.mkdir()
            (build_dir / f"{build_dir_name}.swift").write_text("// Artifact")

        # Create legitimate Swift files
        (tmp_path / "Real.swift").write_text("struct Real {}")
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "Code.swift").write_text("class Code {}")

        from core.scanner import Scanner

        scanner = Scanner(repo_path=tmp_path)
        files = scanner.scan()

        # Should only find Real.swift and Code.swift
        assert len(files) == 2
        paths = [str(f.path) for f in files]
        assert any("Real.swift" in p for p in paths)
        assert any("Code.swift" in p for p in paths)


class TestScannerEdgeCases:
    """Test edge cases and error handling."""

    def test_scanner_handles_empty_directory(self, tmp_path):
        """Verify scanner returns empty list for directory with no Swift files."""
        from core.scanner import Scanner

        scanner = Scanner(repo_path=tmp_path)
        files = scanner.scan()

        assert files == []
        assert len(files) == 0

    def test_scanner_ignores_non_swift_files(self, tmp_path):
        """Verify scanner only finds .swift files, ignoring other file types."""
        # Create various non-Swift files
        (tmp_path / "README.md").write_text("# README")
        (tmp_path / "config.json").write_text("{}")
        (tmp_path / "script.py").write_text("print('hello')")
        (tmp_path / "styles.css").write_text("body {}")

        # Create one Swift file
        (tmp_path / "App.swift").write_text("struct App {}")

        from core.scanner import Scanner

        scanner = Scanner(repo_path=tmp_path)
        files = scanner.scan()

        # Should only find App.swift
        assert len(files) == 1
        assert "App.swift" in str(files[0].path)

    def test_scanner_raises_error_for_nonexistent_directory(self):
        """Verify scanner raises error if repo_path doesn't exist."""
        from core.scanner import Scanner

        nonexistent_path = Path("/nonexistent/directory/path")

        with pytest.raises(ValueError, match="does not exist"):
            Scanner(repo_path=nonexistent_path)

    def test_scanner_raises_error_for_file_instead_of_directory(self, tmp_path):
        """Verify scanner raises error if repo_path is a file, not a directory."""
        from core.scanner import Scanner

        # Create a file
        test_file = tmp_path / "test.txt"
        test_file.write_text("not a directory")

        with pytest.raises(ValueError, match="not a directory"):
            Scanner(repo_path=test_file)

    def test_scanner_handles_unicode_in_filenames(self, tmp_path):
        """Verify scanner handles Unicode characters in filenames."""
        # Create file with Unicode characters
        unicode_file = tmp_path / "Émoji_🚀_Test.swift"
        unicode_file.write_text("struct Test {}")

        from core.scanner import Scanner

        scanner = Scanner(repo_path=tmp_path)
        files = scanner.scan()

        assert len(files) == 1
        assert "Émoji" in str(files[0].path) or "Test.swift" in str(files[0].path)

    def test_scanner_handles_spaces_in_filenames(self, tmp_path):
        """Verify scanner handles spaces in filenames."""
        # Create file with spaces
        spaced_file = tmp_path / "My View Controller.swift"
        spaced_file.write_text("class MyViewController {}")

        from core.scanner import Scanner

        scanner = Scanner(repo_path=tmp_path)
        files = scanner.scan()

        assert len(files) == 1
        assert "My View Controller.swift" in str(files[0].path)


class TestFileDataDataclass:
    """Test FileData dataclass structure."""

    def test_filedata_has_required_fields(self, tmp_path):
        """Verify FileData contains path and content fields."""
        test_file = tmp_path / "Test.swift"
        test_file.write_text("struct Test {}")

        from core.scanner import Scanner

        scanner = Scanner(repo_path=tmp_path)
        files = scanner.scan()

        assert len(files) == 1
        file_data = files[0]

        # FileData should have path and content attributes
        assert hasattr(file_data, 'path')
        assert hasattr(file_data, 'content')
        assert file_data.content == "struct Test {}"

    def test_filedata_path_is_string_or_path(self, tmp_path):
        """Verify FileData.path is either string or Path object."""
        test_file = tmp_path / "Example.swift"
        test_file.write_text("class Example {}")

        from core.scanner import Scanner

        scanner = Scanner(repo_path=tmp_path)
        files = scanner.scan()

        file_data = files[0]
        # Path should be string or Path object
        assert isinstance(file_data.path, (str, Path))

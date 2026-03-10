"""Tests for the scanner module."""

import os
import tempfile
import pytest
from pathlib import Path
from baseline.scanner import scan_codebase
from baseline.models import FileData


class TestScanner:
    """Tests for codebase scanner."""

    def test_scanner_finds_swift_files(self, tmp_path):
        """Test that scanner discovers all .swift files in a directory tree."""
        # Create test structure
        (tmp_path / "Models").mkdir()
        (tmp_path / "Views").mkdir()
        (tmp_path / "Models" / "User.swift").write_text("class User {}")
        (tmp_path / "Views" / "MainView.swift").write_text("struct MainView {}")
        (tmp_path / "README.md").write_text("# Docs")

        files = scan_codebase(str(tmp_path))

        assert len(files) == 2
        paths = [f.path for f in files]
        assert any("User.swift" in p for p in paths)
        assert any("MainView.swift" in p for p in paths)
        assert all(isinstance(f, FileData) for f in files)

    def test_scanner_ignores_git_directory(self, tmp_path):
        """Test that .git directory is excluded from scanning."""
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "config.swift").write_text("// git file")
        (tmp_path / "App.swift").write_text("class App {}")

        files = scan_codebase(str(tmp_path))

        assert len(files) == 1
        assert "App.swift" in files[0].path
        assert ".git" not in files[0].path

    def test_scanner_ignores_build_folders(self, tmp_path):
        """Test that build folders are excluded from scanning."""
        (tmp_path / "Build").mkdir()
        (tmp_path / "DerivedData").mkdir()
        (tmp_path / "Build" / "Output.swift").write_text("// build")
        (tmp_path / "DerivedData" / "Cache.swift").write_text("// cache")
        (tmp_path / "Source.swift").write_text("class Source {}")

        files = scan_codebase(str(tmp_path))

        assert len(files) == 1
        assert "Source.swift" in files[0].path

    def test_scanner_reads_file_content(self, tmp_path):
        """Test that scanner reads file contents correctly."""
        content = "import Foundation\n\nclass TestClass {\n    var name: String\n}"
        (tmp_path / "Test.swift").write_text(content)

        files = scan_codebase(str(tmp_path))

        assert len(files) == 1
        assert files[0].content == content

    def test_scanner_handles_empty_directory(self, tmp_path):
        """Test that scanner handles empty directories gracefully."""
        files = scan_codebase(str(tmp_path))

        assert len(files) == 0
        assert isinstance(files, list)

    def test_scanner_handles_nested_directories(self, tmp_path):
        """Test that scanner handles deeply nested directory structures."""
        deep_path = tmp_path / "a" / "b" / "c" / "d"
        deep_path.mkdir(parents=True)
        (deep_path / "Deep.swift").write_text("class Deep {}")

        files = scan_codebase(str(tmp_path))

        assert len(files) == 1
        assert "Deep.swift" in files[0].path

    def test_scanner_only_finds_swift_files(self, tmp_path):
        """Test that scanner only returns .swift files."""
        (tmp_path / "Code.swift").write_text("class Code {}")
        (tmp_path / "Code.m").write_text("// Objective-C")
        (tmp_path / "Code.h").write_text("// Header")
        (tmp_path / "Code.swift.bak").write_text("// Backup")

        files = scan_codebase(str(tmp_path))

        assert len(files) == 1
        assert files[0].path.endswith(".swift")
        assert not files[0].path.endswith(".swift.bak")

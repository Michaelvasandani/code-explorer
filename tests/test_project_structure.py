"""
Test suite for project structure validation.

Tests verify that all required directories and files exist for the
Sleep Journal Codebase Analyzer project following the architecture
defined in docs/Architecture.md.

RED PHASE: These tests should FAIL initially since directories don't exist yet.
"""

import os
from pathlib import Path
import pytest


# Get project root directory (parent of tests/)
PROJECT_ROOT = Path(__file__).parent.parent


class TestProjectStructure:
    """Test that project structure matches architecture requirements."""

    def test_core_directory_exists(self):
        """Verify core/ directory exists for core modules."""
        core_dir = PROJECT_ROOT / "core"
        assert core_dir.exists(), "core/ directory must exist"
        assert core_dir.is_dir(), "core/ must be a directory"

    def test_core_is_python_package(self):
        """Verify core/ has __init__.py to be a valid Python package."""
        init_file = PROJECT_ROOT / "core" / "__init__.py"
        assert init_file.exists(), "core/__init__.py must exist for Python package"
        assert init_file.is_file(), "core/__init__.py must be a file"

    def test_analyzers_directory_exists(self):
        """Verify analyzers/ directory exists for AI analyzer modules."""
        analyzers_dir = PROJECT_ROOT / "analyzers"
        assert analyzers_dir.exists(), "analyzers/ directory must exist"
        assert analyzers_dir.is_dir(), "analyzers/ must be a directory"

    def test_analyzers_is_python_package(self):
        """Verify analyzers/ has __init__.py to be a valid Python package."""
        init_file = PROJECT_ROOT / "analyzers" / "__init__.py"
        assert init_file.exists(), "analyzers/__init__.py must exist for Python package"
        assert init_file.is_file(), "analyzers/__init__.py must be a file"

    def test_prompts_directory_exists(self):
        """Verify prompts/ directory exists for LLM prompt templates."""
        prompts_dir = PROJECT_ROOT / "prompts"
        assert prompts_dir.exists(), "prompts/ directory must exist"
        assert prompts_dir.is_dir(), "prompts/ must be a directory"

    def test_tests_directory_exists(self):
        """Verify tests/ directory exists (should always pass since we're in it)."""
        tests_dir = PROJECT_ROOT / "tests"
        assert tests_dir.exists(), "tests/ directory must exist"
        assert tests_dir.is_dir(), "tests/ must be a directory"

    def test_tests_is_python_package(self):
        """Verify tests/ has __init__.py to be a valid Python package."""
        init_file = PROJECT_ROOT / "tests" / "__init__.py"
        assert init_file.exists(), "tests/__init__.py must exist for Python package"
        assert init_file.is_file(), "tests/__init__.py must be a file"


class TestRequirementsFile:
    """Test that requirements.txt exists and contains necessary dependencies."""

    def test_requirements_file_exists(self):
        """Verify requirements.txt exists in project root."""
        requirements_file = PROJECT_ROOT / "requirements.txt"
        assert requirements_file.exists(), "requirements.txt must exist"
        assert requirements_file.is_file(), "requirements.txt must be a file"

    def test_requirements_contains_openai(self):
        """Verify requirements.txt includes openai package for LLM integration."""
        requirements_file = PROJECT_ROOT / "requirements.txt"
        content = requirements_file.read_text()
        assert "openai" in content.lower(), "requirements.txt must include openai package"

    def test_requirements_contains_dotenv(self):
        """Verify requirements.txt includes python-dotenv for .env file loading."""
        requirements_file = PROJECT_ROOT / "requirements.txt"
        content = requirements_file.read_text()
        assert "python-dotenv" in content.lower(), "requirements.txt must include python-dotenv"

    def test_requirements_contains_treesitter(self):
        """Verify requirements.txt includes tree-sitter for Swift AST parsing."""
        requirements_file = PROJECT_ROOT / "requirements.txt"
        content = requirements_file.read_text()
        assert "tree-sitter" in content.lower(), "requirements.txt must include tree-sitter"

    def test_requirements_contains_pytest(self):
        """Verify requirements.txt includes pytest for testing framework."""
        requirements_file = PROJECT_ROOT / "requirements.txt"
        content = requirements_file.read_text()
        assert "pytest" in content.lower(), "requirements.txt must include pytest"


class TestPytestConfiguration:
    """Test that pytest.ini configuration file exists."""

    def test_pytest_ini_exists(self):
        """Verify pytest.ini exists for pytest configuration."""
        pytest_ini = PROJECT_ROOT / "pytest.ini"
        assert pytest_ini.exists(), "pytest.ini must exist"
        assert pytest_ini.is_file(), "pytest.ini must be a file"

    def test_pytest_ini_contains_testpaths(self):
        """Verify pytest.ini configures testpaths to tests/ directory."""
        pytest_ini = PROJECT_ROOT / "pytest.ini"
        content = pytest_ini.read_text()
        assert "testpaths" in content.lower(), "pytest.ini should specify testpaths"


class TestGitignore:
    """Test that .gitignore exists and contains Python-specific ignores."""

    def test_gitignore_exists(self):
        """Verify .gitignore exists in project root."""
        gitignore = PROJECT_ROOT / ".gitignore"
        assert gitignore.exists(), ".gitignore must exist"
        assert gitignore.is_file(), ".gitignore must be a file"

    def test_gitignore_ignores_pycache(self):
        """Verify .gitignore includes __pycache__ to ignore compiled Python."""
        gitignore = PROJECT_ROOT / ".gitignore"
        content = gitignore.read_text()
        assert "__pycache__" in content, ".gitignore must include __pycache__"

    def test_gitignore_ignores_pytest_cache(self):
        """Verify .gitignore includes .pytest_cache to ignore pytest artifacts."""
        gitignore = PROJECT_ROOT / ".gitignore"
        content = gitignore.read_text()
        assert ".pytest_cache" in content, ".gitignore must include .pytest_cache"

    def test_gitignore_ignores_env_files(self):
        """Verify .gitignore includes *.pyc to ignore compiled Python files."""
        gitignore = PROJECT_ROOT / ".gitignore"
        content = gitignore.read_text()
        assert "*.pyc" in content, ".gitignore must include *.pyc"

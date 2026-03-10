"""Scanner module for discovering Swift source files."""

import os
from pathlib import Path
from baseline.models import FileData


# Directories to ignore during scanning
IGNORE_DIRS = {
    '.git',
    'Build',
    'DerivedData',
    'build',
    '.build',
    'Pods',
    'Carthage',
    'xcuserdata',
}


def scan_codebase(repo_path: str) -> list[FileData]:
    """
    Scan a codebase directory and discover all Swift source files.

    Args:
        repo_path: Path to the root directory to scan

    Returns:
        List of FileData objects containing file paths and contents
    """
    files = []
    repo_path_obj = Path(repo_path)

    if not repo_path_obj.exists():
        return files

    for root, dirs, filenames in os.walk(repo_path):
        # Remove ignored directories from traversal
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for filename in filenames:
            # Only process .swift files (exact extension match)
            if filename.endswith('.swift') and not filename.endswith('.swift.bak'):
                file_path = Path(root) / filename
                try:
                    content = file_path.read_text(encoding='utf-8')
                    files.append(FileData(
                        path=str(file_path),
                        content=content
                    ))
                except (IOError, UnicodeDecodeError) as e:
                    # Skip files that can't be read
                    print(f"Warning: Could not read {file_path}: {e}")
                    continue

    return files

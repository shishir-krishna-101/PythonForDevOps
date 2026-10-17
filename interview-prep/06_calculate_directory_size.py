#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 06: Recursive Directory Disk Usage Calculator
================================================================================
Problem Statement:
Write a Python function `get_directory_size(dir_path)` that calculates the total
disk storage consumed by a directory and its subdirectories, similar to `du -sh <dir>`.

Requirements:
  1. Recursively sum the sizes of all regular files inside the tree.
  2. Handle broken symlinks and circular directory symlinks safely without
     entering infinite recursion loops (track visited inodes or device/inode pairs).
  3. Format the final output in both raw bytes and the most appropriate human-readable
     unit (B, KB, MB, GB, TB).
  4. Count the total number of files and directories scanned.
  5. Gracefully catch `PermissionError` when encountering restricted system directories.

Constraints:
  - Must not raise unhandled exceptions on inaccessible files.
  - O(Total Inodes) time complexity.
================================================================================
"""

import os
from pathlib import Path
from typing import Dict, Any, Set, Tuple


def format_human_readable_size(num_bytes: int) -> str:
    """Formats raw bytes into appropriate unit string."""
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = float(num_bytes)
    unit_index = 0

    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1

    return f"{size:.2f} {units[unit_index]}"


def get_directory_size(dir_path: str) -> Dict[str, Any]:
    """
    Computes total size of a directory tree with symlink and circular loop protection.
    """
    path = Path(dir_path)
    if not path.exists():
        return {"error": f"Path '{dir_path}' does not exist."}

    total_bytes = 0
    file_count = 0
    dir_count = 0
    visited_inodes: Set[Tuple[int, int]] = set() # (st_dev, st_ino)
    permission_denied_paths = []

    for root, dirs, files in os.walk(dir_path, followlinks=False):
        dir_count += len(dirs)

        for filename in files:
            file_path = os.path.join(root, filename)

            # Avoid broken or external symlinks
            if os.path.islink(file_path):
                continue

            try:
                stat = os.stat(file_path)
                # Track inode to avoid double counting hard-links
                file_key = (stat.st_dev, stat.st_ino)
                if file_key in visited_inodes:
                    continue

                visited_inodes.add(file_key)
                total_bytes += stat.st_size
                file_count += 1

            except PermissionError:
                permission_denied_paths.append(file_path)
            except (FileNotFoundError, OSError):
                # File deleted during scan
                continue

    return {
        "path": str(path.resolve()),
        "total_bytes": total_bytes,
        "human_readable": format_human_readable_size(total_bytes),
        "total_files": file_count,
        "total_directories": dir_count,
        "permission_denied_count": len(permission_denied_paths)
    }


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    import tempfile

    # Create dummy directory structure
    with tempfile.TemporaryDirectory() as tmp_root:
        sub_dir = Path(tmp_root) / "subdir"
        sub_dir.mkdir()

        # 1 MB file
        f1 = Path(tmp_root) / "data1.bin"
        with open(f1, "wb") as f:
            f.seek(1024 * 1024 - 1)
            f.write(b"X")

        # 500 KB file
        f2 = sub_dir / "data2.bin"
        with open(f2, "wb") as f:
            f.seek(512 * 1024 - 1)
            f.write(b"Y")

        result = get_directory_size(tmp_root)

        print("--- [Question 06 Test: Directory Size Calculation] ---")
        print(f"Target Directory : {result['path']}")
        print(f"Total Bytes      : {result['total_bytes']:,} bytes")
        print(f"Human Readable   : {result['human_readable']}")
        print(f"Files Counted    : {result['total_files']}")
        print(f"Dirs Counted     : {result['total_directories']}")

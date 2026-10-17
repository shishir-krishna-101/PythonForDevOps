#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 04: Find & Purge Large Stale Files Older Than N Days
================================================================================
Problem Statement:
A common DevOps automation task is disk housekeeping (e.g. cleaning `/var/log`
or `/tmp` on database or CI runner nodes).

Write a Python function `cleanup_old_large_files(target_dir, max_age_days, min_size_mb, dry_run=True)`
that:
  1. Recursively traverses `target_dir` using `pathlib` or `os.walk`.
  2. Identifies all regular files meeting BOTH criteria:
     - Last modification time is older than `max_age_days`.
     - File size is strictly greater than or equal to `min_size_mb`.
  3. If `dry_run=True`, returns the list of files and total reclaimable bytes
     without performing actual deletions.
  4. If `dry_run=False`, safely deletes each matching file and catches permission
     errors without aborting the loop.
  5. Does NOT follow or delete symlink targets (prevents deleting files outside target).

Constraints:
  - Time Complexity: O(Total Files)
  - Must not crash on permission errors (e.g. read-only files owned by other users).
================================================================================
"""

import os
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple


def cleanup_old_large_files(
    target_dir: str,
    max_age_days: int = 7,
    min_size_mb: float = 10.0,
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Finds and optionally deletes stale large files.
    """
    now = time.time()
    cutoff_timestamp = now - (max_age_days * 86400)
    min_size_bytes = int(min_size_mb * 1024 * 1024)

    target_path = Path(target_dir)
    matched_files: List[Dict[str, Any]] = []
    total_reclaimable_bytes = 0
    deleted_count = 0
    errors: List[str] = []

    if not target_path.exists() or not target_path.is_dir():
        return {
            "error": f"Target directory '{target_dir}' does not exist or is not a directory.",
            "reclaimable_mb": 0.0,
            "files": []
        }

    # Recursive scan
    for root, _, files in os.walk(target_dir):
        for filename in files:
            file_path = Path(root) / filename

            # Protect against symlink traversal
            if file_path.is_symlink():
                continue

            try:
                stat = file_path.stat()
                file_size = stat.st_size
                mtime = stat.st_mtime

                if mtime < cutoff_timestamp and file_size >= min_size_bytes:
                    total_reclaimable_bytes += file_size
                    file_info = {
                        "path": str(file_path),
                        "size_mb": round(file_size / (1024 * 1024), 2),
                        "age_days": round((now - mtime) / 86400, 1)
                    }
                    matched_files.append(file_info)

                    if not dry_run:
                        file_path.unlink()
                        deleted_count += 1

            except (PermissionError, FileNotFoundError) as err:
                errors.append(f"Failed to access {file_path}: {err}")

    return {
        "target_directory": str(target_path),
        "dry_run": dry_run,
        "matched_count": len(matched_files),
        "deleted_count": deleted_count,
        "total_reclaimable_mb": round(total_reclaimable_bytes / (1024 * 1024), 2),
        "files": matched_files,
        "errors": errors
    }


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    import tempfile

    # Create temporary sandbox directory for test
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test file 1: Old and large (15 MB, 10 days old)
        file1 = Path(tmp_dir) / "stale_archive.tar.gz"
        with open(file1, "wb") as f:
            f.seek(15 * 1024 * 1024) # 15 MB
            f.write(b"\0")
        old_time = time.time() - (10 * 86400)
        os.utime(file1, (old_time, old_time))

        # Create test file 2: New and large (12 MB, 1 day old) -> should NOT match
        file2 = Path(tmp_dir) / "recent_dump.sql"
        with open(file2, "wb") as f:
            f.seek(12 * 1024 * 1024)
            f.write(b"\0")

        # Create test file 3: Old and tiny (100 bytes, 15 days old) -> should NOT match
        file3 = Path(tmp_dir) / "old_note.txt"
        file3.write_text("Hello")
        os.utime(file3, (old_time, old_time))

        print("--- [Question 04 Test: Dry Run Mode] ---")
        dry_result = cleanup_old_large_files(tmp_dir, max_age_days=7, min_size_mb=10.0, dry_run=True)
        print(f"Matched Files: {dry_result['matched_count']}")
        print(f"Reclaimable  : {dry_result['total_reclaimable_mb']} MB")
        for item in dry_result["files"]:
            print(f"  * {os.path.basename(item['path'])} ({item['size_mb']} MB, {item['age_days']} days old)")

        print("\n--- [Question 04 Test: Execute Deletion Mode] ---")
        exec_result = cleanup_old_large_files(tmp_dir, max_age_days=7, min_size_mb=10.0, dry_run=False)
        print(f"Deleted Files: {exec_result['deleted_count']}")
        print(f"File exists after deletion? {file1.exists()}")

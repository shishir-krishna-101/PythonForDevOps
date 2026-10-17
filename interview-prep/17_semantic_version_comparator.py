#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 17: Custom Semantic Versioning (SemVer) Comparator & Sorter
================================================================================
Problem Statement:
Standard alphabetical sorting fails for release versions:
  e.g., standard string sort puts "v1.10.0" BEFORE "v1.2.0" because '1' < '2'.

Write a Python class or sorting key function `semver_sort_key(version_str)` that
correctly compares and sorts software version strings conforming to SemVer:
  Format: `v?MAJOR.MINOR.PATCH(-PRERELEASE)?`
  Examples: `v1.2.0`, `1.10.0`, `v2.0.0-alpha`, `v2.0.0-beta`, `v2.0.0`

Rules:
  1. Strip optional leading 'v'.
  2. Numerical comparison on `(MAJOR, MINOR, PATCH)`.
     Therefore: 1.10.0 > 1.2.0, 1.2.10 > 1.2.2.
  3. Pre-release tags (e.g., `-alpha`, `-rc1`) have LOWER precedence than the
     associated release:
     Therefore: 2.0.0-rc1 < 2.0.0.
  4. Multiple pre-releases compare lexicographically:
     alpha < beta < rc1 < rc2.
  5. The function should be usable directly with Python's `sorted(versions, key=...)`.

Constraints:
  - Do NOT use third-party libraries like `semver` or `packaging`.
  - Handle malformed versions without crashing (place them at the beginning).
================================================================================
"""

import re
from typing import List, Tuple, Any


def semver_sort_key(version: str) -> Tuple[Any, ...]:
    """
    Transforms a version string into a comparable tuple for sorting.
    Returns: (major: int, minor: int, patch: int, is_release: bool, prerelease_tag: str)
    """
    clean_v = version.strip().lstrip("v")

    # Match MAJOR.MINOR.PATCH with optional pre-release suffix
    pattern = r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:-([a-zA-Z0-9.]+))?$'
    match = re.match(pattern, clean_v)

    if not match:
        # Malformed versions sort first
        return (-1, -1, -1, False, clean_v)

    major = int(match.group(1))
    minor = int(match.group(2) or 0)
    patch = int(match.group(3) or 0)
    prerelease = match.group(4)

    # In SemVer, a release (no prerelease) is HIGHER precedence than a prerelease
    # So we use a boolean flag: True if official release, False if prerelease
    is_official_release = (prerelease is None)
    prerelease_str = prerelease or ""

    return (major, minor, patch, is_official_release, prerelease_str)


def sort_versions(versions: List[str], reverse: bool = False) -> List[str]:
    """Sorts a list of SemVer version strings."""
    return sorted(versions, key=semver_sort_key, reverse=reverse)


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    unsorted_tags = [
        "v1.2.10",
        "v1.2.2",
        "v2.0.0-rc2",
        "v1.10.0",
        "v2.0.0-alpha",
        "v2.0.0",
        "v2.0.0-rc1",
        "v1.2.0",
        "v0.9.5"
    ]

    print("--- [Question 17 Test: SemVer Sorting] ---")
    print(f"Unsorted : {unsorted_tags}")

    sorted_tags = sort_versions(unsorted_tags)
    print(f"\nSorted   : {sorted_tags}")

    print(f"\nLatest Release Version: {sort_versions(unsorted_tags, reverse=True)[0]}")

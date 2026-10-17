#!/usr/bin/env python3
r"""
================================================================================
INTERVIEW QUESTION 23: Git Bisect Simulation (Binary Search for Buggy Commit)
================================================================================
Problem Statement:
A production outage occurred after deploying release version `v1000`. You know
that commit 0 (`v0`) was healthy, and commit 1000 (`v1000`) is broken. All commits
between the first broken commit and `v1000` are also broken.

You have access to an automated integration test function:
  `is_commit_broken(commit_id: int) -> bool`

Write a Python function `find_first_broken_commit(total_commits, is_commit_broken_fn)`
that:
  1. Finds the exact first commit ID that introduced the bug.
  2. Runs in logarithmic time O(log N) rather than testing all 1,000 commits sequentially.
  3. Minimizes the total number of test executions (each test run takes minutes in CI).
  4. Returns the first bad commit index and the total test probe count.

--------------------------------------------------------------------------------
HOW TO THINK & SOLVE THIS USING ONLY OFFICIAL DOCS:
--------------------------------------------------------------------------------
1. Mental Model & Problem Decomposition:
   - The array of test results is monotonically sorted:
     `[Healthy, Healthy, Healthy, ..., BROKEN, BROKEN, BROKEN]`
     `[False,   False,   False,   ..., True,   True,   True]`
   - Any time you have a sorted or monotonic condition and need to find the transition point,
     the optimal algorithm is **Binary Search** ($O(\log N)$).
   - If `mid` is BROKEN (`True`), the first bad commit is at `mid` or to the left -> `right = mid`.
   - If `mid` is HEALTHY (`False`), the first bad commit must be strictly to the right -> `left = mid + 1`.

2. Official Docs Reference:
   - Topic: Binary Search Algorithm
   - Module: `bisect` -> `docs.python.org/3/library/bisect.html`
   - In Python, `bisect` searches sorted lists, but here we evaluate a function dynamically.
     So we write standard boundary-safe binary search:
     `mid = left + (right - left) // 2` (prevents integer overflow in languages like C/Java).
================================================================================
"""

from typing import Callable, Tuple, Dict, Any


def find_first_broken_commit(
    total_commits: int,
    is_commit_broken_fn: Callable[[int], bool]
) -> Tuple[int, int]:
    """
    Finds the first broken commit index in O(log N) using binary search.
    Returns: (first_broken_commit_id, total_probes_made)
    """
    if total_commits <= 0:
        raise ValueError("Total commits must be greater than 0.")

    left = 0
    right = total_commits - 1
    first_bad = -1
    probes_count = 0

    while left <= right:
        mid = left + (right - left) // 2
        probes_count += 1

        if is_commit_broken_fn(mid):
            # Mid is broken, so first bad commit is mid or earlier
            first_bad = mid
            right = mid - 1 # Try to find an earlier bad commit
        else:
            # Mid is healthy, so first bad commit must be to the right
            left = mid + 1

    return first_bad, probes_count


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    # Simulate 10,000 commits where commit 7,421 introduced the regression
    ACTUAL_FIRST_BROKEN = 7421
    TOTAL_COMMITS = 10000

    def mock_ci_test_runner(commit_id: int) -> bool:
        """Returns True if commit is broken, False if healthy."""
        return commit_id >= ACTUAL_FIRST_BROKEN

    print("--- [Question 23 Test: Git Bisect Binary Search] ---")
    print(f"Total Commits in History : {TOTAL_COMMITS}")
    print(f"True Regression Commit   : {ACTUAL_FIRST_BROKEN}")

    found_commit, probes = find_first_broken_commit(TOTAL_COMMITS, mock_ci_test_runner)

    print(f"\nDiscovered Broken Commit : {found_commit}")
    print(f"Total Test Runs Executed : {probes}")
    print(f"Linear Search Would Take : {ACTUAL_FIRST_BROKEN + 1} test runs")
    print(f"Efficiency Advantage     : ~{((ACTUAL_FIRST_BROKEN - probes) / ACTUAL_FIRST_BROKEN) * 100:.1f}% faster!")
    assert found_commit == ACTUAL_FIRST_BROKEN, "Failed to identify the correct commit!"

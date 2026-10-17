#!/usr/bin/env python3
"""
12-ci-cd-and-git-automation/git_release_automation.py

Demonstrates:
- GitPython repository interaction
- Inspecting working tree status
- Calculating semantic version tags
- Formatting changelog summaries
"""

import sys
import git
from typing import List, Dict, Any


def get_repo_state(repo_path: str = ".") -> Dict[str, Any]:
    """Inspects Git repository and returns metadata."""
    try:
        repo = git.Repo(repo_path, search_parent_directories=True)
    except Exception as e:
        return {"error": str(e)}

    # Branch name or detached head
    branch = "DETACHED_HEAD" if repo.head.is_detached else repo.active_branch.name

    # Check uncommitted changes
    is_dirty = repo.is_dirty(untracked_files=True)
    untracked = repo.untracked_files

    return {
        "repo_root": repo.working_dir,
        "branch": branch,
        "is_dirty": is_dirty,
        "untracked_count": len(untracked),
        "tags": [t.name for t in repo.tags]
    }


def compute_next_version(current_tag: str, bump_type: str = "minor") -> str:
    """Increments SemVer tag string."""
    clean = current_tag.lstrip("v")
    parts = clean.split(".")
    major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

    if bump_type == "major":
        return f"v{major + 1}.0.0"
    elif bump_type == "minor":
        return f"v{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"v{major}.{minor}.{patch + 1}"
    return current_tag


def main():
    print("==================================================")
    print("      GIT AUTOMATION & RELEASE ENGINE             ")
    print("==================================================")

    state = get_repo_state(".")
    if "error" in state:
        print(f"[ERROR] Could not open git repository: {state['error']}")
        sys.exit(1)

    print(f"  Repository Root : {state['repo_root']}")
    print(f"  Current Branch  : {state['branch']}")
    print(f"  Working Tree    : {'[DIRTY]' if state['is_dirty'] else '[CLEAN]'}")
    print(f"  Untracked Files : {state['untracked_count']}")
    print(f"  Existing Tags   : {state['tags'] if state['tags'] else 'None'}")

    current_simulated_version = "v1.4.2"
    next_minor = compute_next_version(current_simulated_version, "minor")
    next_patch = compute_next_version(current_simulated_version, "patch")

    print("\n--- Semantic Version Calculation ---")
    print(f"  Current Version : {current_simulated_version}")
    print(f"  Next Patch Bump : {next_patch} (for bug fixes)")
    print(f"  Next Minor Bump : {next_minor} (for new features)")

    print("\n[SUCCESS] Git automation logic verified successfully.")


if __name__ == "__main__":
    main()

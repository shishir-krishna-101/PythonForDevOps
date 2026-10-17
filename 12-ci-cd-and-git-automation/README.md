# 12 - CI/CD & Git Automation for DevOps

---

## 1. What It Is
CI/CD and Git automation combines source control operations and pipeline orchestrators into seamless, hands-free release workflows:
- **`GitPython` (`git` module)**: A native Python library used to interact with Git repositories. Supports reading commits, inspecting diffs, checking branch statuses, creating tags, and committing code.
- **GitHub / GitLab REST APIs**: Programmatic interfaces to manage pull requests, review statuses, branch protection rules, and pipeline execution.
- **`repository_dispatch` & Webhooks**: Programmatically triggering downstream CI workflows (GitHub Actions, GitLab CI, Jenkins) from external events.
- **Semantic Versioning (SemVer)**: Incrementing `MAJOR.MINOR.PATCH` numbers automatically based on conventional commit messages (`feat:`, `fix:`, `chore:`).

---

## 2. What Is the Use of It in DevOps?
Modern DevOps practices (like **GitOps**) treat Git as the single source of truth:
1. **Automated GitOps Manifest Bumping**: When a new container image is published in CI, a Python script commits the new image tag directly to the ArgoCD or Flux repository.
2. **Release Note & Changelog Generation**: Parse Git commit messages between two release tags (`v1.4.0...v1.5.0`) to generate changelogs and post them to GitHub Releases.
3. **Stale Branch Garbage Collection**: Detect feature branches that have been merged or inactive for over 30 days and delete them automatically.
4. **Automated Hotfix PR Creation**: Cherry-pick security vulnerability fixes and generate Pull Requests across multiple release branches simultaneously.

---

## 3. How to Use It

### Interacting with Git Repositories using GitPython
```python
import git

# Open the current repository
repo = git.Repo(".")

# Check if working directory has uncommitted changes
if repo.is_dirty(untracked_files=True):
    print("Working directory has unstaged or untracked changes!")

# Get current branch and latest commit SHA
current_branch = repo.active_branch.name
latest_commit = repo.head.commit.hexsha
print(f"Branch: {current_branch} | Commit: {latest_commit[:8]}")
```

### Creating and Pushing a Release Tag
```python
import git

repo = git.Repo(".")
new_tag = "v2.1.0"

# Create annotated tag
tag_ref = repo.create_tag(
    new_tag,
    message=f"Release {new_tag} created by DevOps CI bot"
)

# Push tag to remote
origin = repo.remote(name="origin")
origin.push(tags=True)
print(f"Successfully pushed tag {new_tag} to origin.")
```

---

## 4. How to Implement It: Step-by-Step

### Step A: Semantic Version Calculation from Commits
```python
import re
from typing import Tuple

def bump_semver(current_version: str, bump_type: str = "patch") -> str:
    """Bumps version string 'v1.2.3' -> 'v1.2.4' (patch) or 'v1.3.0' (minor)."""
    clean_v = current_version.lstrip("v")
    major, minor, patch = map(int, clean_v.split("."))

    if bump_type == "major":
        return f"v{major + 1}.0.0"
    elif bump_type == "minor":
        return f"v{major}.{minor + 1}.0"
    else:
        return f"v{major}.{minor}.{patch + 1}"
```

### Step B: Triggering GitHub Actions via API
```python
import requests
import os

def trigger_github_workflow(repo_slug: str, event_type: str, client_payload: dict):
    token = os.getenv("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{repo_slug}/dispatches"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    body = {
        "event_type": event_type,
        "client_payload": client_payload
    }
    res = requests.post(url, json=body, headers=headers, timeout=10)
    res.raise_for_status()
    print("Successfully dispatched GitHub Actions event.")
```

---

## 5. DevOps Hands-On Example: Automated Git Repository Auditor & Tag Manager

```python
#!/usr/bin/env python3
"""
Automated Git Repository Inspector & Release Manager.
Inspects local repository status, extracts recent commits,
and calculates the next release version tag.
"""
import os
import sys
from typing import List, Dict, Any

try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

def inspect_git_repository(repo_path: str = ".") -> Dict[str, Any]:
    if not GIT_AVAILABLE:
        return {"error": "GitPython is not installed."}

    try:
        repo = git.Repo(repo_path, search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        return {"error": f"Path '{repo_path}' is not a valid Git repository."}

    # Extract branches
    branches = [b.name for b in repo.branches]
    is_dirty = repo.is_dirty(untracked_files=True)
    
    # Extract tags
    tags = [t.name for t in repo.tags]
    
    # Extract last 3 commits
    commits = []
    try:
        for commit in list(repo.iter_commits(max_count=3)):
            commits.append({
                "sha": commit.hexsha[:8],
                "author": commit.author.name,
                "message": commit.message.strip().split("\n")[0]
            })
    except Exception:
        commits = []

    return {
        "active_branch": repo.active_branch.name if not repo.head.is_detached else "DETACHED_HEAD",
        "is_dirty": is_dirty,
        "total_tags": len(tags),
        "tags": tags,
        "recent_commits": commits
    }

def main():
    print("=== Git Repository & CI/CD Pipeline Auditor ===")
    info = inspect_git_repository(".")

    if "error" in info:
        print(f"[FAIL] {info['error']}")
        sys.exit(1)

    print(f"  Active Branch   : {info['active_branch']}")
    print(f"  Uncommitted Diffs: {'[DIRTY]' if info['is_dirty'] else '[CLEAN]'}")
    print(f"  Total Tags Found : {info['total_tags']}")

    print("\n--- Recent Commits ---")
    if info["recent_commits"]:
        for c in info["recent_commits"]:
            print(f"  [{c['sha']}] {c['author']}: {c['message']}")
    else:
        print("  (No commits yet in this repository)")

    print("\n[SUCCESS] Git repository inspection finished.")

if __name__ == "__main__":
    main()
```

---

## 6. Interview & Real-World Questions

### Q1: What is a "detached HEAD" state in Git, and how should a Python CI script handle it?
**Answer:**
A detached HEAD occurs when Git checks out a specific commit hash or tag rather than a named branch (very common in GitHub Actions or Jenkins checkout steps). If a script attempts `repo.active_branch.name` while in detached HEAD, GitPython raises a `TypeError`.
**Defense**: Check `if repo.head.is_detached:` before accessing `.active_branch`.

### Q2: How do you avoid infinite build loops when a CI script commits back to the repository?
**Answer:**
If an automated script commits updated manifests (e.g. `[ci skip] update image tag`), the new commit may trigger the CI workflow again, creating an infinite loop.
**Fixes**:
1. Include `[skip ci]` or `[ci skip]` in the commit message (supported by GitHub Actions, GitLab CI, and CircleCI).
2. Use a dedicated bot service account and configure the workflow trigger to ignore commits from that bot account.

### Q3: Why should you avoid storing Git credentials in `.git/config` within CI workers?
**Answer:**
CI runners are often shared or ephemeral. Storing persistent tokens or plaintext passwords in `.git/config` risks leaking credentials to other pipeline steps or test scripts that print files.
**Best Practice**: Pass short-lived tokens via environment variables (e.g., `GITHUB_TOKEN`) or use SSH agent forwarding.

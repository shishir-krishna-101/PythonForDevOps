# Real-World Script 08: GitHub Organization Security & Compliance Policy Auditor

---

## 1. Real-World DevOps Problem Statement
In rapidly growing software engineering organizations:
1. **Unprotected Default Branches**: Developers often create repositories without enabling branch protection on `main` or `master`. Any developer can accidentally force-push (`git push --force`) or commit unreviewed code directly to production.
2. **Accidental Credential Exposure**: Without automated secret scanning, API tokens, AWS keys, and database passwords get committed to version control.
3. **Unpatched Vulnerabilities in Dependencies**: Without Dependabot or software composition analysis (SCA), obsolete npm or pip packages with known CVEs remain in production indefinitely.
4. **DevSecOps Policy Enforcement**: Security and DevOps teams need automated auditing tools that scan all organizational repositories and fail CI pipelines if policies are violated.

---

## 2. Complete Code Implementation

See the full script in [github_compliance_auditor.py](file:///c:/Users/Demon%20Slayer/Documents/PythonForDevOps/14-real-world-devops-scripts/08-github-repo-compliance-auditor/github_compliance_auditor.py).

---

## 3. Deep-Dive Code Explanation: What Is It Doing?

### A. Granular Security Rule Evaluation
```python
def audit_repository_compliance(repo):
```
Evaluates critical DevSecOps baseline controls:
- **Control 1: Branch Protection**: Requires pull request reviews and status checks before merging to `main`. Direct pushes are blocked.
- **Control 2: Secret Scanning**: Ensures GitHub Secret Scanning and Push Protection are enabled to block leaked credentials.
- **Control 3: Dependabot Scanning**: Verifies automated vulnerability scanning and security PR generation.

### B. Normalized Security Posture Scoring
- Computes a numerical compliance score (0% to 100%) for each repository.
- Aggregates an overall Organization Security Score across the entire repository fleet.

### C. CI/CD Gating via Exit Codes
- If any repository has critical violations, the script exits with non-zero exit code (`1`), enabling automated gating in GitHub Actions or Jenkins.

---

## 4. Libraries Used & Why

| Library | Why It Was Chosen |
|:---|:---|
| `requests` | High-level HTTP client to query GitHub REST API v3 endpoints with Bearer token authentication. |
| `argparse` | CLI parameter handling for organization names and tokens. |
| `logging` | Structured JSON log generation. |

---

## 5. Real-World Problems, Edge Cases & Code Fixes

### Problem 1: GitHub API Rate Limiting (Secondary Rate Limits)
- **Real-World Incident**: Scanning 500 repositories rapidly triggers GitHub's secondary rate limits (abuse detection), returning HTTP 403 `You have exceeded a secondary rate limit`.
- **The Code Fix**: Implement exponential backoff, sleep for 0.5s between repository queries, and check the `X-RateLimit-Remaining` and `Retry-After` headers.

### Problem 2: Permissions Scope Limitations
- **Real-World Incident**: Checking branch protection requires `admin:repo` or `repo` permissions. If the Personal Access Token (PAT) lacks this scope, GitHub returns HTTP 404 (not 403) to prevent information disclosure.
- **The Code Fix**: Catch HTTP 404 on branch protection endpoints and report a specific diagnostic error indicating that the token lacks admin privileges.

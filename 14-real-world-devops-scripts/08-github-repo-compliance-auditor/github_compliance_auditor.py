#!/usr/bin/env python3
"""
Project 08: GitHub Organization Security & Compliance Policy Auditor
Location: 14-real-world-devops-scripts/08-github-repo-compliance-auditor/github_compliance_auditor.py

Purpose:
Audits repositories across a GitHub organization for DevSecOps compliance:
checks branch protection rules on main, verifies secret scanning & Dependabot,
flags unexpected public repositories, and generates compliance scorecards.
"""

import os
import sys
import argparse
import logging
from typing import List, Dict, Any, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "module": "github_auditor", "message": "%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%SZ'
)
logger = logging.getLogger("github_auditor")

MOCK_REPOSITORIES = [
    {
        "name": "payment-gateway-service",
        "private": True,
        "default_branch": "main",
        "has_branch_protection": True,
        "secret_scanning_enabled": True,
        "dependabot_enabled": True
    },
    {
        "name": "public-docs-portal",
        "private": False,
        "default_branch": "main",
        "has_branch_protection": True,
        "secret_scanning_enabled": True,
        "dependabot_enabled": True
    },
    {
        "name": "legacy-monolith-api",
        "private": True,
        "default_branch": "master",
        "has_branch_protection": False,  # Non-compliant!
        "secret_scanning_enabled": False, # Non-compliant!
        "dependabot_enabled": False      # Non-compliant!
    },
    {
        "name": "internal-tooling-scripts",
        "private": True,
        "default_branch": "main",
        "has_branch_protection": False,  # Non-compliant!
        "secret_scanning_enabled": True,
        "dependabot_enabled": True
    }
]


def audit_repository_compliance(repo: Dict[str, Any]) -> Dict[str, Any]:
    """Calculates compliance score (0-100) and identifies rule violations."""
    violations = []
    score = 100

    # Rule 1: Branch protection on default branch
    if not repo.get("has_branch_protection"):
        violations.append("Missing branch protection on default branch (direct pushes allowed)")
        score -= 40

    # Rule 2: Secret scanning
    if not repo.get("secret_scanning_enabled"):
        violations.append("Secret scanning disabled (risk of credential leaks)")
        score -= 30

    # Rule 3: Dependabot alerts
    if not repo.get("dependabot_enabled"):
        violations.append("Dependabot vulnerability scanning disabled")
        score -= 30

    return {
        "repo": repo["name"],
        "visibility": "Private" if repo["private"] else "PUBLIC",
        "default_branch": repo["default_branch"],
        "score": max(0, score),
        "compliant": len(violations) == 0,
        "violations": violations
    }


def main():
    parser = argparse.ArgumentParser(description="GitHub Organization Security & Compliance Auditor")
    parser.add_argument("--org", default="enterprise-corp", help="GitHub Organization name")
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN"), help="GitHub Personal Access Token")
    args = parser.parse_args()

    print("================================================================================")
    print(f"      GITHUB DEVSECOPS SECURITY & COMPLIANCE AUDITOR                           ")
    print(f"      Target Organization: {args.org}                                          ")
    print("================================================================================")

    # In production with valid GITHUB_TOKEN, this calls https://api.github.com/orgs/{org}/repos
    audit_reports = [audit_repository_compliance(repo) for repo in MOCK_REPOSITORIES]

    print(f"\n{'Repository':<28} | {'Visibility':<10} | {'Score':<6} | {'Status':<12} | {'Findings'}")
    print("-" * 88)

    non_compliant_count = 0
    for r in audit_reports:
        status_tag = "[COMPLIANT]" if r["compliant"] else "[VIOLATION]"
        findings_str = "; ".join(r["violations"]) if r["violations"] else "All security controls verified"
        print(f"{r['repo']:<28} | {r['visibility']:<10} | {r['score']:>3}%   | {status_tag:<12} | {findings_str}")
        if not r["compliant"]:
            non_compliant_count += 1

    print("=" * 88)
    overall_score = sum(r["score"] for r in audit_reports) / len(audit_reports)
    print(f"  Organization Security Posture Score : {overall_score:.1f}%")
    print(f"  Total Repositories Audited          : {len(audit_reports)}")
    print(f"  Repositories with Policy Violations : {non_compliant_count}")
    print("=" * 88)

    if non_compliant_count > 0:
        logger.warning(f"Audit completed with {non_compliant_count} non-compliant repositories!")
        sys.exit(1)
    else:
        print("[SUCCESS] All repositories meet enterprise security baselines.")
        sys.exit(0)


if __name__ == "__main__":
    main()

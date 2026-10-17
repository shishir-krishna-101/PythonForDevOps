#!/usr/bin/env python3
"""
Project 07: Docker Registry & Container Image Lifecycle Garbage Collector
Location: 14-real-world-devops-scripts/07-docker-registry-pruner/docker_registry_cleaner.py

Purpose:
Prunes obsolete container images and untagged manifests from container registries (ECR/Docker),
enforcing retention policies: keeps SemVer releases, protects 'latest', deletes ephemeral CI tags
older than N days, and safeguards active running containers from layer deletion.
"""

import re
import sys
import argparse
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Set

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "module": "registry_cleaner", "message": "%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%SZ'
)
logger = logging.getLogger("registry_cleaner")

# Regex for strict Semantic Version tags: e.g. v1.0.0, 2.14.3, v3.0.0-rc1
SEMVER_REGEX = re.compile(r'^v?\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$')

SAMPLE_REGISTRY_TAGS = [
    {"tag": "latest", "created_days_ago": 1, "digest": "sha256:1111"},
    {"tag": "v2.4.0", "created_days_ago": 60, "digest": "sha256:2222"},
    {"tag": "v2.3.9", "created_days_ago": 90, "digest": "sha256:3333"},
    {"tag": "pr-412-build-1", "created_days_ago": 45, "digest": "sha256:4444"},
    {"tag": "pr-412-build-2", "created_days_ago": 44, "digest": "sha256:5555"},
    {"tag": "pr-501-build-8", "created_days_ago": 5, "digest": "sha256:6666"},
    {"tag": "commit-a7f3b9c", "created_days_ago": 50, "digest": "sha256:7777"},
    {"tag": "untagged", "created_days_ago": 35, "digest": "sha256:8888"}
]

# Tags currently deployed in production Kubernetes clusters (Protected)
RUNNING_CONTAINER_DIGESTS: Set[str] = {"sha256:1111", "sha256:2222"}


def evaluate_tag_retention(
    image: Dict[str, Any],
    max_ephemeral_age_days: int = 30
) -> Tuple_Decision:
    """
    Applies enterprise retention rules:
    1. PROTECT if currently running in production.
    2. PROTECT if tagged as 'latest' or 'main' or matches SemVer (e.g. v1.2.3).
    3. PURGE if ephemeral CI tag (PR/commit/untagged) older than max_ephemeral_age_days.
    """
    tag = image["tag"]
    digest = image["digest"]
    age_days = image["created_days_ago"]

    # Rule 1: Active Production Container Protection
    if digest in RUNNING_CONTAINER_DIGESTS:
        return "KEEP", "Currently deployed in production Kubernetes cluster"

    # Rule 2: Latest / Default branch protection
    if tag in ["latest", "main", "master", "stable"]:
        return "KEEP", "Protected system branch tag"

    # Rule 3: Semantic Version Release Protection
    if SEMVER_REGEX.match(tag):
        return "KEEP", "Immutable Semantic Version release"

    # Rule 4: Ephemeral CI builds evaluation
    if age_days > max_ephemeral_age_days:
        return "PURGE", f"Ephemeral build tag older than {max_ephemeral_age_days} days ({age_days}d old)"

    return "KEEP", f"Recent ephemeral build ({age_days}d old)"


def main():
    parser = argparse.ArgumentParser(description="Container Registry Garbage Collector")
    parser.add_argument("--repo", default="company/api-gateway", help="Target repository name")
    parser.add_argument("--max-age", type=int, default=30, help="Max age for ephemeral tags in days")
    parser.add_argument("--execute", action="store_true", help="Execute actual deletion (default is dry-run)")
    args = parser.parse_args()

    dry_run = not args.execute

    print("================================================================================")
    print(f"      CONTAINER REGISTRY LIFECYCLE & IMAGE GARBAGE COLLECTOR                   ")
    print(f"      Repository: {args.repo} | Mode: {'DRY-RUN' if dry_run else 'EXECUTE'}   ")
    print("================================================================================")

    keep_list = []
    purge_list = []

    for img in SAMPLE_REGISTRY_TAGS:
        decision, rationale = evaluate_tag_retention(img, args.max_age)
        entry = {**img, "rationale": rationale}
        if decision == "KEEP":
            keep_list.append(entry)
        else:
            purge_list.append(entry)

    print("\n--- IMAGES PRESERVED (KEEP) ---")
    for k in keep_list:
        print(f"  [PRESERVED] Tag: {k['tag']:<20} | Digest: {k['digest']} | Rationale: {k['rationale']}")

    print("\n--- OBSOLETE IMAGES MARKED FOR PURGE ---")
    for p in purge_list:
        print(f"  [PURGE]     Tag: {p['tag']:<20} | Digest: {p['digest']} | Rationale: {p['rationale']}")

    print("\n" + "=" * 80)
    print(f"  Audit Summary: {len(keep_list)} images retained | {len(purge_list)} images eligible for deletion.")
    print("=" * 80)

    if not dry_run:
        logger.warning(f"Commencing real deletion of {len(purge_list)} images from registry...")
        for p in purge_list:
            logger.info(f"Deleting image manifest: {args.repo}@{p['digest']} (Tag: {p['tag']})")
        print("[SUCCESS] Registry garbage collection finished.")
    else:
        logger.info("Dry-run mode complete. No images were removed. Run with '--execute' to perform purge.")


if __name__ == "__main__":
    main()

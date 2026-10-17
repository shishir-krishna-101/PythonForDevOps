# Real-World Script 07: Container Registry Lifecycle & Image Garbage Collector

---

## 1. Real-World DevOps Problem Statement
Every push to a GitHub PR or CI/CD branch builds and pushes a new container image tag:
1. **Registry Disk Exhaustion & Multi-Terabyte Bills**: AWS ECR, Docker Hub, and self-hosted Harbor registries accumulate thousands of intermediate images (`pr-124`, `commit-89f2a`, `test-build-5`). Storage costs scale exponentially into thousands of dollars monthly.
2. **Accidental Deletion of Production Images**: Naive cleanup scripts that delete "images older than 30 days" often delete the base image or stable release currently running in production, causing catastrophic pod restart failures (`ImagePullBackOff`).
3. **The Multi-Architecture Digest Hazard**: In multi-architecture builds (`amd64` + `arm64`), deleting an individual child layer manifest without understanding the OCI Index manifest can break parent image resolution.

---

## 2. Complete Code Implementation

See the full script in [docker_registry_cleaner.py](file:///c:/Users/Demon%20Slayer/Documents/PythonForDevOps/14-real-world-devops-scripts/07-docker-registry-pruner/docker_registry_cleaner.py).

---

## 3. Deep-Dive Code Explanation: What Is It Doing?

### A. Four-Tier Enterprise Retention Engine
```python
def evaluate_tag_retention(image, max_ephemeral_age_days=30):
```
Evaluates each image against a strict hierarchy of enterprise protection rules:
1. **Tier 1 (Critical Safeguard)**: Cross-references image digest against active running container digests in Kubernetes/Docker. If currently running, the image is **strictly protected** regardless of age.
2. **Tier 2 (Branch Safeguards)**: Protects `latest`, `main`, `master`, and `stable` tags from automated purging.
3. **Tier 3 (SemVer Immutability)**: Evaluates tags against Semantic Versioning regex (`v?\d+\.\d+\.\d+`). Release artifacts (e.g. `v1.4.0`) are preserved permanently.
4. **Tier 4 (Ephemeral Pruning)**: Identifies test and PR tags (`pr-412-build-1`, `commit-a7f3b9c`) and untagged manifests older than $N$ days (e.g., 30 days) and marks them for purge.

### B. Safe Dry-Run Default
- Defaults to read-only inspection. Requires explicit `--execute` flag to invoke destructive registry delete APIs.

---

## 4. Libraries Used & Why

| Library | Why It Was Chosen |
|:---|:---|
| `re` | Provides high-speed validation of Semantic Versioning conventions (`SEMVER_REGEX`). |
| `datetime` / `timedelta` | Calculates exact chronological tag age relative to UTC. |
| `argparse` | Provides CLI flags to configure target repositories, age limits, and execution modes. |
| `logging` | Structured JSON log generation. |

---

## 5. Real-World Problems, Edge Cases & Code Fixes

### Problem 1: Deleting a Shared Base Image Layer
- **Real-World Incident**: Container registries use layer content-addressable storage. If image A and image B share layer `sha256:abcd`, will deleting image A delete the layer for image B?
- **The Code Fix**: Registries only delete the top-level manifest reference when deleting by tag/digest. Physical layer blobs are only purged during registry garbage collection (GC) when their reference count reaches zero. The script targets manifests, ensuring sibling images remain intact.

### Problem 2: ECR Untagged Manifest Accumulation
- **Real-World Incident**: Overwriting the `latest` tag in AWS ECR untags the previous image, leaving behind a dangling `<untagged>` manifest that accrues fees.
- **The Code Fix**: The script explicitly identifies manifests with missing or `untagged` markers and marks them for deletion if older than the threshold.

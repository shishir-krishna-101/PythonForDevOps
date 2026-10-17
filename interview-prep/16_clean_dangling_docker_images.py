#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 16: Prune Dangling Docker Images & Reclaim Host Space
================================================================================
Problem Statement:
Build runners and Docker hosts accumulate intermediate dangling images
(`<none>:<none>`) created during recurring container builds, filling up disk space.

Write a Python function `prune_dangling_docker_images(docker_client=None, dry_run=True)`
that:
  1. Identifies all dangling images (images with no repository tags).
  2. Ensures that no dangling image currently utilized by an active running container
     is marked for deletion.
  3. Calculates the total reclaimable disk space in Megabytes (MB).
  4. If `dry_run=False`, removes each dangling image and catches removal errors
     (e.g., image currently in use by a stopped container).
  5. Returns a structured execution report.

Constraints:
  - Do not delete tagged production or base images.
  - Safe error handling for daemon connection failures.
================================================================================
"""

from typing import List, Dict, Any

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


def prune_dangling_docker_images(docker_client=None, dry_run: bool = True) -> Dict[str, Any]:
    """
    Identifies and optionally deletes dangling container images.
    """
    dangling_images: List[Dict[str, Any]] = []
    total_reclaimable_bytes = 0
    removed_count = 0
    errors: List[str] = []

    if not DOCKER_AVAILABLE or not docker_client:
        # Realistic mock data for interview demonstration
        mock_dangling = [
            {"id": "sha256:a1b2c3d4e5f6001", "size_bytes": 450 * 1024 * 1024},
            {"id": "sha256:f6e5d4c3b2a1002", "size_bytes": 820 * 1024 * 1024},
            {"id": "sha256:112233445566003", "size_bytes": 110 * 1024 * 1024}
        ]
        total_bytes = sum(m["size_bytes"] for m in mock_dangling)
        return {
            "dangling_count": len(mock_dangling),
            "reclaimable_mb": round(total_bytes / (1024 * 1024), 2),
            "removed_count": 0 if dry_run else len(mock_dangling),
            "dry_run": dry_run,
            "images": mock_dangling,
            "simulated": True
        }

    try:
        # Collect IDs of images currently used by any container
        used_image_ids = set()
        for container in docker_client.containers.list(all=True):
            used_image_ids.add(container.image.id)

        # Filter for dangling images
        images = docker_client.images.list(filters={"dangling": True})
        for img in images:
            # Skip if in use
            if img.id in used_image_ids:
                continue

            img_size = img.attrs.get("Size", 0)
            total_reclaimable_bytes += img_size
            dangling_images.append({
                "id": img.short_id,
                "size_bytes": img_size
            })

            if not dry_run:
                try:
                    docker_client.images.remove(image=img.id, force=False)
                    removed_count += 1
                except Exception as rem_err:
                    errors.append(f"Could not remove {img.short_id}: {rem_err}")

    except Exception as e:
        return {"error": f"Docker daemon communication error: {e}"}

    return {
        "dangling_count": len(dangling_images),
        "reclaimable_mb": round(total_reclaimable_bytes / (1024 * 1024), 2),
        "removed_count": removed_count,
        "dry_run": dry_run,
        "images": dangling_images,
        "errors": errors,
        "simulated": False
    }


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    print("--- [Question 16 Test: Docker Dangling Image Cleaner] ---")
    report = prune_dangling_docker_images(dry_run=True)

    print(f"Dangling Images Found : {report['dangling_count']}")
    print(f"Reclaimable Storage   : {report['reclaimable_mb']} MB")
    print(f"Execution Mode        : {'DRY-RUN' if report['dry_run'] else 'EXECUTE'}")
    print("\nIdentified Images:")
    for img in report["images"]:
        size_mb = round(img["size_bytes"] / (1024 * 1024), 1)
        print(f"  * ID: {img['id']} | Size: {size_mb} MB")

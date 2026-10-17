#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 07: Validate & Dynamically Patch Kubernetes Manifests
================================================================================
Problem Statement:
In a GitOps CI/CD pipeline, after a new Docker image is built and pushed to a
registry, an automated script must update the image tag and replica count in a
Kubernetes Deployment YAML file.

Write a Python function `patch_k8s_deployment(yaml_string, new_image_tag, new_replicas=None)`
that:
  1. Safely parses the input YAML without arbitrary code execution vulnerabilities.
  2. Validates that the manifest is indeed a `kind: Deployment` and contains
     `spec.template.spec.containers`.
  3. Updates the container image tag for the primary application container.
  4. If `new_replicas` is specified, updates `spec.replicas`.
  5. Injects/updates a deployment timestamp annotation in `metadata.annotations`
     to track the release time.
  6. Returns the updated YAML string with formatting preserved.
  7. Raises descriptive custom exceptions if validation fails.

Constraints:
  - Must not corrupt YAML indentation.
  - Fail fast if required deployment structure is missing.
================================================================================
"""

import yaml
from datetime import datetime, timezone
from typing import Optional, Dict, Any


class InvalidManifestError(Exception):
    """Raised when the Kubernetes manifest is malformed or not a Deployment."""
    pass


def patch_k8s_deployment(
    yaml_content: str,
    target_container_name: str,
    new_image_tag: str,
    new_replicas: Optional[int] = None
) -> str:
    """
    Validates and updates a Kubernetes Deployment manifest.
    """
    try:
        data: Dict[str, Any] = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        raise InvalidManifestError(f"YAML Syntax Error: {e}")

    if not isinstance(data, dict):
        raise InvalidManifestError("Manifest must be a valid YAML mapping.")

    # 1. Validate Kind and APIVersion
    if data.get("kind") != "Deployment":
        raise InvalidManifestError(f"Expected kind 'Deployment', got '{data.get('kind')}'")

    # 2. Defensive schema navigation
    try:
        spec = data["spec"]
        containers = spec["template"]["spec"]["containers"]
    except KeyError as missing_key:
        raise InvalidManifestError(f"Missing mandatory Kubernetes deployment key: {missing_key}")

    # 3. Patch Replicas if requested
    if new_replicas is not None:
        if new_replicas < 0:
            raise ValueError("Replicas cannot be negative.")
        spec["replicas"] = new_replicas

    # 4. Patch Container Image
    container_found = False
    for c in containers:
        if c.get("name") == target_container_name:
            current_image = c.get("image", "")
            base_image = current_image.split(":")[0] if ":" in current_image else current_image
            c["image"] = f"{base_image}:{new_image_tag}"
            container_found = True
            break

    if not container_found:
        raise InvalidManifestError(f"Container with name '{target_container_name}' not found in deployment.")

    # 5. Inject Release Tracking Annotation
    metadata = data.setdefault("metadata", {})
    annotations = metadata.setdefault("annotations", {})
    annotations["devops.release/last-updated"] = datetime.now(timezone.utc).isoformat()
    annotations["devops.release/image-tag"] = new_image_tag

    # 6. Dump back to YAML
    return yaml.safe_dump(data, default_flow_style=False, sort_keys=False)


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    sample_manifest = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: billing-api
  namespace: prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: billing-api
  template:
    metadata:
      labels:
        app: billing-api
    spec:
      containers:
      - name: api-server
        image: registry.example.com/finance/billing-api:v1.0.0
        ports:
        - containerPort: 8080
"""

    print("--- [Question 07 Test: Patching K8s Deployment Manifest] ---")
    patched = patch_k8s_deployment(
        yaml_content=sample_manifest,
        target_container_name="api-server",
        new_image_tag="v2.5.0-rc1",
        new_replicas=8
    )
    print(patched)

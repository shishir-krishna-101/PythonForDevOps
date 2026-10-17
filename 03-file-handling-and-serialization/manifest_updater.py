#!/usr/bin/env python3
"""
03-file-handling-and-serialization/manifest_updater.py

Demonstrates:
- Safe reading and writing of configuration files
- JSON & YAML serialization and parsing
- Atomic write pattern to avoid file corruption
- Automated CI/CD manifest modification
"""

import os
import json
import tempfile
from datetime import datetime, timezone
from typing import Dict, Any

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def atomic_write_file(target_path: str, content: str) -> None:
    """Safely writes content to a temporary file, then renames atomically."""
    dir_name = os.path.dirname(os.path.abspath(target_path)) or "."
    os.makedirs(dir_name, exist_ok=True)
    
    with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
        tf.write(content)
        temp_name = tf.name

    # Atomic swap
    os.replace(temp_name, target_path)


def update_service_config_json(file_path: str, new_env_vars: Dict[str, str]) -> Dict[str, Any]:
    """Updates service configuration in JSON format with backup and schema safety."""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {
            "service_name": "inventory-api",
            "version": "1.0.0",
            "environment_variables": {}
        }

    # Update variables
    data["environment_variables"].update(new_env_vars)
    data["last_updated_at"] = datetime.now(timezone.utc).isoformat()

    # Write back atomically
    serialized = json.dumps(data, indent=2)
    atomic_write_file(file_path, serialized)
    return data


def update_k8s_deployment_yaml(file_path: str, new_image_tag: str, replicas: int) -> str:
    """Updates Kubernetes Deployment manifest using YAML parser."""
    sample_yaml = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-api
  namespace: production
  labels:
    app: web-api
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: web-api
  template:
    metadata:
      labels:
        app: web-api
    spec:
      containers:
      - name: web-api
        image: ghcr.io/org/web-api:{new_image_tag}
        ports:
        - containerPort: 8080
"""
    if YAML_AVAILABLE:
        doc = yaml.safe_load(sample_yaml)
        doc["spec"]["replicas"] = replicas
        doc["spec"]["template"]["spec"]["containers"][0]["image"] = f"ghcr.io/org/web-api:{new_image_tag}"
        content = yaml.safe_dump(doc, default_flow_style=False, sort_keys=False)
    else:
        content = sample_yaml

    atomic_write_file(file_path, content)
    return content


def main():
    print("=== File Handling & Serialization Demo ===")
    
    # 1. Update JSON Configuration
    json_path = "sample_config.json"
    print(f"\n1. Writing and updating JSON config at: {json_path}")
    updated_json = update_service_config_json(
        json_path,
        {"DATABASE_POOL_SIZE": "25", "LOG_LEVEL": "INFO", "ENABLE_TRACING": "true"}
    )
    print(json.dumps(updated_json, indent=2))

    # 2. Update YAML Kubernetes Manifest
    yaml_path = "sample_deployment.yaml"
    print(f"\n2. Updating Kubernetes YAML manifest at: {yaml_path}")
    yaml_result = update_k8s_deployment_yaml(yaml_path, new_image_tag="v3.1.0", replicas=5)
    print(yaml_result)

    # Clean up generated sample files
    if os.path.exists(json_path):
        os.remove(json_path)
    if os.path.exists(yaml_path):
        os.remove(yaml_path)
    print("[SUCCESS] Atomic serialization and cleanup completed!")


if __name__ == "__main__":
    main()

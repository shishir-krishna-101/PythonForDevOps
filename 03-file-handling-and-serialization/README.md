# 03 - File Handling & Data Serialization for DevOps

---

## 1. What It Is
File handling and serialization refer to reading, parsing, modifying, and writing data stored in various disk formats:
- **Text & Log Files**: Raw streaming I/O using Python context managers (`with open(...)`).
- **JSON (`json` module)**: Standard web and API interchange format (AWS CLI outputs, Docker inspect payloads, Kubernetes API data).
- **YAML (`PyYAML` / `ruamel.yaml`)**: The universal language of DevOps configuration (Kubernetes manifests, Docker Compose, GitHub Actions workflows, Ansible playbooks, Helm chart values).
- **Environment & INI Files (`configparser`, `python-dotenv`)**: Standard system configurations and application credential files.
- **CSV (`csv` module)**: Cost reports, billing breakdowns, and asset inventory exports.

---

## 2. What Is the Use of It in DevOps?
Modern DevOps relies almost entirely on **Configuration as Code (CaC)**:
1. **Dynamic CI/CD Manifest Updates**: Updating the image tag inside a Kubernetes `deployment.yaml` or Helm `values.yaml` right after building a Docker image.
2. **Parsing Infrastructure Outputs**: Extracting VPC IDs, Subnet IDs, and IAM role ARNs from `terraform.tfstate` (JSON format) to pass to downstream automation.
3. **Log Ingestion & Rotation**: Safely appending deployment timestamps, reading multi-gigabyte log streams line-by-line without running out of memory.
4. **Environment Configuration Injection**: Merging base configurations with environment-specific overrides (e.g., `values-prod.yaml`).

---

## 3. How to Use It

### Context Managers (`with open`)
Always use context managers. They guarantee the file descriptor is closed properly even if an unhandled exception occurs:
```python
# Safe reading
with open("/var/log/syslog", "r", encoding="utf-8") as f:
    for line in f: # Iterates line-by-line (O(1) memory)
        if "CRITICAL" in line:
            print(line.strip())

# Safe writing
with open("build-status.txt", "w", encoding="utf-8") as f:
    f.write("BUILD_SUCCESS\n")
```

### JSON Serialization
```python
import json

# Parse JSON string from CLI/API
raw_json = '{"service": "auth-api", "replicas": 3, "enabled": true}'
data = json.loads(raw_json)

# Dump Python dictionary to formatted JSON file
with open("config.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
```

### YAML Serialization (`yaml.safe_load` / `yaml.safe_dump`)
```python
import yaml

with open("deployment.yaml", "r", encoding="utf-8") as f:
    # Always use safe_load to prevent arbitrary code execution vulnerabilities
    manifest = yaml.safe_load(f)

# Update replica count
manifest["spec"]["replicas"] = 5

with open("deployment.yaml", "w", encoding="utf-8") as f:
    yaml.safe_dump(manifest, f, default_flow_style=False, sort_keys=False)
```

---

## 4. How to Implement It: Step-by-Step

### Step A: Atomic File Writes for Infrastructure Reliability
If a script crashes midway through writing a critical configuration file, the file could end up truncated or corrupted, bringing down production. Always write to a temporary file first, then atomically rename it:
```python
import os
import json
import tempfile

def atomic_write_json(file_path: str, data: dict):
    dir_name = os.path.dirname(os.path.abspath(file_path))
    with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
        json.dump(data, tf, indent=2)
        temp_name = tf.name
    # os.replace is an atomic filesystem operation on POSIX & Windows
    os.replace(temp_name, file_path)
```

### Step B: Defensive YAML / JSON Parsing
```python
import json
import yaml

def safe_parse_config(raw_content: str):
    try:
        return yaml.safe_load(raw_content)
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML: {exc}")
        return None
```

---

## 5. DevOps Hands-On Example: Automated Kubernetes Manifest Patching

```python
#!/usr/bin/env python3
"""
CI/CD Step: Automated Kubernetes Deployment Manifest Patcher.
Reads an existing k8s YAML manifest, patches container image,
updates replica counts, injects release annotations, and saves the result.
"""
import sys
import yaml
from datetime import datetime, timezone

SAMPLE_K8S_DEPLOYMENT = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
  namespace: production
  labels:
    app: payment-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: payment-service
  template:
    metadata:
      labels:
        app: payment-service
    spec:
      containers:
      - name: web
        image: registry.example.com/payment:v1.0.0
        ports:
        - containerPort: 8080
"""

def patch_manifest(yaml_text: str, new_image: str, new_replicas: int, commit_sha: str) -> str:
    # Parse YAML safely
    doc = yaml.safe_load(yaml_text)

    # 1. Update replica count
    doc["spec"]["replicas"] = new_replicas

    # 2. Update container image
    containers = doc["spec"]["template"]["spec"]["containers"]
    for container in containers:
        if container["name"] == "web":
            container["image"] = new_image

    # 3. Inject deployment annotations for GitOps tracking
    if "annotations" not in doc["metadata"]:
        doc["metadata"]["annotations"] = {}

    doc["metadata"]["annotations"]["deployment.kubernetes.io/revision-commit"] = commit_sha
    doc["metadata"]["annotations"]["deployment.kubernetes.io/updated-at"] = datetime.now(timezone.utc).isoformat()

    # Dump updated YAML
    return yaml.safe_dump(doc, default_flow_style=False, sort_keys=False)

def main():
    print("=== Patching Kubernetes Deployment Manifest for CI/CD ===")
    NEW_IMAGE = "registry.example.com/payment:v2.4.1-rc3"
    NEW_REPLICAS = 6
    COMMIT_SHA = "a7f3b89c42e"

    updated_yaml = patch_manifest(SAMPLE_K8S_DEPLOYMENT, NEW_IMAGE, NEW_REPLICAS, COMMIT_SHA)
    print("\n[RESULT] Patched Kubernetes Manifest:")
    print(updated_yaml)

if __name__ == "__main__":
    main()
```

---

## 6. Interview & Real-World Questions

### Q1: Why is `yaml.load()` considered a severe security risk in DevOps automation, and what should be used instead?
**Answer:**
`yaml.load(input)` without specifying a safe loader allows arbitrary Python code execution via YAML object constructors (e.g. `!!python/object/apply:os.system ['rm -rf /']`). If an automated pipeline processes pull requests or user-submitted manifests using `yaml.load()`, malicious code can take over the build worker.
**Fix**: Always use `yaml.safe_load(input)` or specify `Loader=yaml.SafeLoader`.

### Q2: How do you read a 10 GB production server log file without causing an Out-Of-Memory (OOM) kill?
**Answer:**
Never use `f.read()` or `f.readlines()`, which load the entire file into memory at once. Instead, iterate over the file object directly:
```python
with open("huge-access.log", "r", encoding="utf-8") as f:
    for line in f: # Python buffers line by line, keeping memory usage constant (~MBs)
        if "500 Internal Server Error" in line:
            process_error(line)
```

### Q3: What is the difference between `json.dump()` and `json.dumps()`?
**Answer:**
- `json.dump(obj, fp)`: Serializes `obj` as a JSON formatted stream directly into a **file-like pointer** (`fp`).
- `json.dumps(obj)`: Serializes `obj` to a **JSON formatted `str`** (string) in memory.
- Same distinction applies to `load` (from file pointer) vs `loads` (load from string).

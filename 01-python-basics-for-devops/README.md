# 01 - Python Basics for DevOps

---

## 1. What It Is
Python basics comprise the foundational building blocks of the Python programming language:
- **Variables & Data Types**: Strings (`str`), Integers (`int`), Floats (`float`), Booleans (`bool`), and `None`.
- **String Manipulation**: Formatted string literals (f-strings), string slicing, splitting, stripping, and joining.
- **Control Flow**: Conditional branching (`if`, `elif`, `else`) and loops (`for`, `while`, `break`, `continue`).
- **Functions & Modularity**: Reusable blocks of logic, default parameters, variable-length arguments (`*args`, `**kwargs`), and return values.
- **Virtual Environments & Dependency Management**: Isolated execution environments using `venv` and package tracking via `pip` and `requirements.txt`.

---

## 2. What Is the Use of It in DevOps?
Bash shell scripts are great for quick, 5-line commands. However, once automation logic grows past 50 lines or needs to interact with APIs, JSON responses, databases, and multi-cloud providers, Bash becomes fragile, error-prone, and difficult to test.

Python basics enable DevOps engineers to:
1. **Sanitize and Validate Configuration Inputs**: Parse CLI parameters, check environment variables, and enforce infrastructure naming conventions.
2. **Build Resilient CI/CD Logic**: Replace brittle shell logic with structured conditional checks and error recovery.
3. **Parse and Filter System Strings**: Extract hostnames, IP addresses, service statuses, and container IDs from CLI tool outputs.
4. **Create Modular Scripts**: Package recurring tasks (e.g., rotating credentials, checking DNS, notifying teams) into importable, reusable modules.

---

## 3. How to Use It

### Virtual Environment Setup
Always isolate project dependencies to prevent conflicts with the system Python installation:
```bash
# Create a virtual environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Core Syntax Overview
```python
# 1. Variables and Type Hinting
server_name: str = "prod-app-01"
cpu_cores: int = 8
memory_utilization: float = 78.4
is_healthy: bool = True

# 2. String Manipulation
raw_log = "  2026-10-17 ERROR [auth-service] Connection timeout to database  \n"
clean_log = raw_log.strip()
parts = clean_log.split(" ")
log_level = parts[1]
message = " ".join(parts[2:])

# 3. Control Flow
if memory_utilization > 85.0:
    action = "SCALE_UP"
elif memory_utilization < 20.0:
    action = "SCALE_DOWN"
else:
    action = "STABLE"

# 4. Functions
def check_threshold(current: float, max_limit: float = 80.0) -> bool:
    """Returns True if metric is within acceptable limits."""
    return current <= max_limit
```

---

## 4. How to Implement It: Step-by-Step

### Step A: Handling Script Arguments & Environment Variables
In modern DevOps workflows (e.g., Kubernetes pods or Docker containers), configuration arrives via environment variables:
```python
import os
import sys

# Reading environment variables with fallback defaults
DEPLOY_ENV = os.getenv("DEPLOY_ENV", "staging").lower()
TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "30"))

if DEPLOY_ENV not in ["staging", "production"]:
    print(f"CRITICAL: Invalid environment: {DEPLOY_ENV}", file=sys.stderr)
    sys.exit(1)
```

### Step B: Looping and Iterating over Infrastructure Targets
```python
nodes = ["k8s-worker-01", "k8s-worker-02", "k8s-worker-03"]

for index, node in enumerate(nodes, start=1):
    print(f"[{index}/{len(nodes)}] Scanning node: {node}...")
```

---

## 5. DevOps Hands-On Example: Environment & Service Pre-Flight Checker

This script checks whether all necessary environment variables, configuration directories, and system thresholds are met before starting a deployment pipeline.

```python
#!/usr/bin/env python3
"""
Pre-flight environment validator for CI/CD pipelines.
Validates required environment variables and simulates health thresholds.
"""
import os
import sys
from typing import Dict, List

REQUIRED_VARS: List[str] = [
    "AWS_DEFAULT_REGION",
    "APP_ENVIRONMENT",
    "CLUSTER_NAME",
    "ALERT_EMAIL"
]

def check_environment_variables(required: List[str]) -> Dict[str, str]:
    """Validates presence of required environment variables."""
    missing = []
    collected = {}
    for var in required:
        val = os.getenv(var)
        if not val:
            missing.append(var)
        else:
            collected[var] = val

    if missing:
        print(f"[FAIL] Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    print("[PASS] All required environment variables are set.")
    return collected

def validate_environment_name(env: str) -> bool:
    """Ensures environment is one of the approved target stages."""
    allowed = {"dev", "staging", "uat", "prod"}
    return env.strip().lower() in allowed

def main():
    print("=== Starting Pre-flight Deployment Validation ===")
    
    # Simulate presence for testing if not set
    if "APP_ENVIRONMENT" not in os.environ:
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
        os.environ["APP_ENVIRONMENT"] = "staging"
        os.environ["CLUSTER_NAME"] = "eks-cluster-alpha"
        os.environ["ALERT_EMAIL"] = "devops-alerts@example.com"

    env_data = check_environment_variables(REQUIRED_VARS)
    
    if not validate_environment_name(env_data["APP_ENVIRONMENT"]):
        print(f"[FAIL] Invalid deployment environment: '{env_data['APP_ENVIRONMENT']}'")
        sys.exit(1)

    print(f"[SUCCESS] Target Cluster: {env_data['CLUSTER_NAME']} in Region: {env_data['AWS_DEFAULT_REGION']}")
    print("=== Pipeline Check Completed Successfully ===")

if __name__ == "__main__":
    main()
```

---

## 6. Interview & Real-World Questions

### Q1: Why should you avoid using `shell=True` when executing commands in Python, or why choose Python over Bash for complex automation?
**Answer:**
Bash lacks robust data structures (such as nested dictionaries or sets), typed error handling, and unit testing frameworks. When scripts grow complex, Bash scripts often break silently or mishandle spaces and edge cases. Python provides explicit exception handling (`try-except`), native JSON/YAML handling, unit testing (`pytest`), and cross-platform compatibility across Linux, macOS, and Windows.

### Q2: What is the difference between `==` and `is` in Python, and where can it cause bugs in DevOps scripts?
**Answer:**
- `==` checks for **value equality** (whether two objects have the same data).
- `is` checks for **identity** (whether two references point to the exact same memory location).
- *DevOps Trap*: Checking `if status is "SUCCESS":` may fail unpredictably across different Python runtimes or string intern limits. Always use `if status == "SUCCESS":` for value comparison, and reserve `is` for singletons such as `if result is None:` or `if flag is True:`.

### Q3: How do you gracefully handle script termination and exit codes in Python CI/CD jobs?
**Answer:**
In CI/CD (GitHub Actions, GitLab CI, Jenkins), the runner determines job success or failure based on the process exit code (`0` = Success, non-zero = Failure). In Python:
```python
import sys
# On failure:
sys.exit(1)
# On success:
sys.exit(0)
```
Raising unhandled exceptions automatically terminates the script with a non-zero exit code (`1`), which fails the CI pipeline as desired.

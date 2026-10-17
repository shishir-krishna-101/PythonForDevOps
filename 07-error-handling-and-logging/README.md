# 07 - Error Handling & Structured Logging for DevOps

---

## 1. What It Is
Error handling and logging form the safety net of automated infrastructure:
- **Exceptions (`try / except / else / finally / raise`)**: The structured mechanism to intercept and recover from runtime failures without crashing ungracefully.
- **Custom Exceptions**: Specialized domain-specific error classes (e.g. `ClusterNotReadyError`, `QuotaExceededError`) for precise failure categorization.
- **The `logging` Module**: Python's enterprise logging framework providing log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`), modular handlers, and formatters.
- **12-Factor App & Structured Logging**: Emitting logs as structured JSON to `stdout` so container agents (Fluentbit, Logstash, Vector) can ship them directly to Elasticsearch, Datadog, or CloudWatch.

---

## 2. What Is the Use of It in DevOps?
Automated DevOps scripts run unattended in background cron jobs, Kubernetes cronjobs, and CI/CD runners:
1. **Root-Cause Analysis (RCA)**: Without descriptive logs and stack traces, debugging why a 3:00 AM database backup failed requires reproducing the failure blind.
2. **Graceful Degradation & Rollback**: Catching an infrastructure failure (e.g., EC2 launch failure) enables triggering an automated rollback of already provisioned resources.
3. **Log Ingestion & Indexing**: Emitting JSON-formatted logs allows indexing fields (`trace_id`, `cluster_name`, `response_time_ms`) for instantaneous querying.
4. **Distinguishing Transient from Fatal Errors**: Network blips or rate limits can be retried, while authentication errors or syntax faults should fail immediately.

---

## 3. How to Use It

### The Anti-Pattern of Bare `except:`
```python
# CATASTROPHIC ANTI-PATTERN
try:
    deploy_service()
except: # Intercepts KeyboardInterrupt, SystemExit, MemoryError!
    pass

# PRODUCTION BEST PRACTICE
try:
    deploy_service()
except ConnectionError as err:
    logger.warning("Transient network blip during deploy: %s. Retrying...", err)
except PermissionError as err:
    logger.critical("Fatal: Insufficient IAM permissions: %s", err)
    raise
except Exception as err:
    logger.exception("Unexpected error during deployment: %s", err)
    sys.exit(1)
```

### Modern Structured JSON Logging for Kubernetes & Containers
```python
import logging
import json
from datetime import datetime, timezone

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "file": record.filename,
            "line": record.lineno
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)
```

---

## 4. How to Implement It: Step-by-Step

### Step A: Defining Custom DevOps Exceptions
```python
class InfrastructureError(Exception):
    """Base exception for all infrastructure automation failures."""
    pass

class ResourceNotFoundError(InfrastructureError):
    """Raised when an expected cloud resource (VPC, Subnet, Cluster) does not exist."""
    pass

class HealthCheckTimeoutError(InfrastructureError):
    """Raised when an application fails to become healthy within the timeout window."""
    pass
```

### Step B: The Complete `try-except-else-finally` Lifecycle
```python
try:
    connect_to_cluster()
except ConnectionError:
    logger.error("Failed to connect.")
else:
    # Runs ONLY if NO exception was raised in try
    logger.info("Connection established successfully.")
finally:
    # Runs in ALL scenarios (cleanup connections, lock files)
    release_cluster_lock()
```

---

## 5. DevOps Hands-On Example: Resilient Infrastructure Rollout Runner

```python
#!/usr/bin/env python3
"""
Resilient Infrastructure Deployment Runner with Structured JSON Logging
and Custom Domain Exceptions.
"""
import sys
import time
import json
import logging
from typing import Optional

# 1. Custom Exceptions
class DeploymentError(Exception):
    pass

class ClusterUnreachableError(DeploymentError):
    pass

class HealthCheckFailedError(DeploymentError):
    pass

# 2. Structured Logger Setup
logger = logging.getLogger("deployer")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)

class DevOpsJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        })

handler.setFormatter(DevOpsJsonFormatter())
logger.addHandler(handler)

# 3. Resilient Deployment Logic
def poll_health_check(target_host: str, retries: int = 3, delay: float = 0.5) -> bool:
    for attempt in range(1, retries + 1):
        logger.info(f"Health check probe {attempt}/{retries} on {target_host}...")
        # Simulate transient error on attempt 1, success on attempt 2
        if attempt < 2:
            logger.warning(f"Probe {attempt} failed: HTTP 503 Service Unavailable")
            time.sleep(delay)
            continue
        logger.info(f"Probe {attempt} healthy: HTTP 200 OK")
        return True
    return False

def deploy_to_environment(env: str, cluster: str):
    logger.info(f"Initiating deployment for environment: '{env}' to cluster: '{cluster}'")
    try:
        if cluster == "invalid-cluster":
            raise ClusterUnreachableError(f"Cluster '{cluster}' is unreachable or does not exist.")

        healthy = poll_health_check(f"{cluster}.internal")
        if not healthy:
            raise HealthCheckFailedError("Pod readiness probe failed after maximum retries.")

    except ClusterUnreachableError as e:
        logger.error(f"[DEPLOYMENT ABORTED] Configuration Error: {e}")
        raise
    except HealthCheckFailedError as e:
        logger.critical(f"[ROLLBACK TRIGGERED] Health check failed: {e}")
        raise
    else:
        logger.info(f"Deployment successfully completed and verified in '{env}'!")
    finally:
        logger.info("Cleaning up temporary build lock files.")

def main():
    print("=== Testing Successful Deployment ===")
    try:
        deploy_to_environment("staging", "k8s-us-east-1")
    except DeploymentError:
        sys.exit(1)

    print("\n=== Testing Failed Deployment with Recovery ===")
    try:
        deploy_to_environment("production", "invalid-cluster")
    except DeploymentError:
        print("[EXPECTED HANDLED EXCEPTION] Graceful failure completed.")

if __name__ == "__main__":
    main()
```

---

## 6. Interview & Real-World Questions

### Q1: Why should production Docker containers log to `sys.stdout` instead of writing to local log files on disk?
**Answer:**
Under the **12-Factor App methodology**, applications should not concern themselves with log routing or storage. Container filesystems are ephemeral (disappearing when containers crash). By streaming to `stdout` / `stderr`:
1. The container runtime (Docker/containerd) automatically manages log buffers.
2. Daemons like Fluentbit, Datadog Agent, or Promtail capture the container stream without needing mount permissions inside the container.
3. Disk space inside the container is never filled up by unrotated logs.

### Q2: What is the difference between `logger.error()` and `logger.exception()`?
**Answer:**
- `logger.error("...")` logs the error message string at ERROR level.
- `logger.exception("...")` logs the error message AND automatically appends the full traceback information (`sys.exc_info()`). It should only be called inside an `except` block.

### Q3: When should a DevOps script define custom exceptions?
**Answer:**
Custom exceptions allow scripts to separate operational errors (e.g. AWS API throttling, Kubernetes node drain timeouts) from programming bugs (e.g. `AttributeError`, `IndexError`). This allows caller functions to write granular recovery handlers (e.g., retrying only on `RateLimitError`).

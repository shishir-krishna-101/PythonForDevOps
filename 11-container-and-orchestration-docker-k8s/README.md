# 11 - Container & Kubernetes Automation (Docker & K8s SDK)

---

## 1. What It Is
Container and orchestration automation enables Python scripts to manage containers and Kubernetes clusters directly via native APIs:
- **Docker SDK for Python (`docker`)**: Interacts with the local or remote Docker daemon socket (`/var/run/docker.sock` or Windows named pipe `npipe://`). Allows building images, running containers, pruning unused layers, and monitoring container stats.
- **Kubernetes Python Client (`kubernetes`)**: The official client library for the Kubernetes REST API.
- **Client Configuration Modes**:
  - `config.load_kube_config()`: For scripts running on an engineer's laptop or CI runner using `~/.kube/config`.
  - `config.load_incluster_config()`: For Python pods running inside the cluster utilizing mounted ServiceAccount tokens and CA certs.
- **Core APIs**:
  - `client.CoreV1Api()`: Pods, Services, Namespaces, ConfigMaps, Secrets, Nodes.
  - `client.AppsV1Api()`: Deployments, StatefulSets, DaemonSets, ReplicaSets.

---

## 2. What Is the Use of It in DevOps?
While YAML is used to declare state, Python is used to control dynamic runtime behaviors:
1. **Self-Healing Kubernetes Operators**: Detect pods stuck in `CrashLoopBackOff` or `ImagePullBackOff`, collect their termination logs, notify engineers, and trigger remediation.
2. **Ephemeral CI/CD Environments**: Automatically spin up a dedicated namespace and microservice stack for a pull request, run integration tests, and destroy the namespace when tests complete.
3. **Automated Horizontal Scaling & Rebalancing**: Programmatically scale deployment replicas up or down based on custom business metrics that standard Horizontal Pod Autoscaler (HPA) cannot observe.
4. **Docker Host Housekeeping**: Prune dangling images (`docker image prune -f`) and stopped containers to prevent disk exhaustion on worker nodes.

---

## 3. How to Use It

### Docker SDK: Listing & Pruning
```python
import docker

client = docker.from_env()

# List running containers
for container in client.containers.list():
    print(f"Container: {container.name} | Status: {container.status} | Image: {container.image.tags}")

# Prune unused images
pruned = client.images.prune(filters={'dangling': True})
print(f"Space reclaimed: {pruned.get('SpaceReclaimed', 0)} bytes")
```

### Kubernetes Client: Dual-Mode Authentication Pattern
```python
from kubernetes import client, config
import os

def initialize_k8s_client():
    """Detects whether running inside a Kubernetes Pod or on a local workstation."""
    if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token"):
        # Running inside Kubernetes
        config.load_incluster_config()
    else:
        # Running locally with ~/.kube/config
        config.load_kube_config()
    return client.CoreV1Api()
```

---

## 4. How to Implement It: Step-by-Step

### Step A: Detecting CrashLoopBackOff Pods
```python
from kubernetes import client, config

def find_crashing_pods(namespace: str = "default"):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    
    pods = v1.list_namespaced_pod(namespace=namespace)
    failing_pods = []

    for pod in pods.items:
        statuses = pod.status.container_statuses or []
        for cs in statuses:
            waiting = cs.state.waiting
            if waiting and waiting.reason in ["CrashLoopBackOff", "Error", "ImagePullBackOff"]:
                failing_pods.append({
                    "name": pod.metadata.name,
                    "reason": waiting.reason,
                    "restart_count": cs.restart_count
                })

    return failing_pods
```

### Step B: Scaling a Deployment Programmatically
```python
from kubernetes import client, config

def scale_deployment(namespace: str, deployment_name: str, replicas: int):
    config.load_kube_config()
    apps_v1 = client.AppsV1Api()

    body = {"spec": {"replicas": replicas}}
    apps_v1.patch_namespaced_deployment_scale(
        name=deployment_name,
        namespace=namespace,
        body=body
    )
    print(f"Scaled {deployment_name} in {namespace} to {replicas} replicas.")
```

---

## 5. DevOps Hands-On Example: Kubernetes Pod Watcher & Self-Healing Sentinel

```python
#!/usr/bin/env python3
"""
Kubernetes Self-Healing Pod Watcher.
Inspects pods across namespaces, isolates failing pods,
fetches recent crash logs, and alerts.
"""
import sys
from typing import List, Dict, Any

try:
    from kubernetes import client, config
    from kubernetes.client.exceptions import ApiException
    K8S_AVAILABLE = True
except ImportError:
    K8S_AVAILABLE = False

def scan_cluster_pods() -> List[Dict[str, Any]]:
    if not K8S_AVAILABLE:
        print("[NOTICE] kubernetes library not detected; returning simulated cluster scan.")
        return [
            {"namespace": "prod", "pod": "checkout-api-7b89d-x1", "status": "Running", "restarts": 0},
            {"namespace": "prod", "pod": "payment-worker-5c24f-k9", "status": "CrashLoopBackOff", "restarts": 14}
        ]

    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        pod_list = v1.list_pod_for_all_namespaces(timeout_seconds=5)
        
        inspected = []
        for pod in pod_list.items:
            restarts = 0
            status_reason = pod.status.phase
            if pod.status.container_statuses:
                for cs in pod.status.container_statuses:
                    restarts += cs.restart_count
                    if cs.state.waiting:
                        status_reason = cs.state.waiting.reason or status_reason

            inspected.append({
                "namespace": pod.metadata.namespace,
                "pod": pod.metadata.name,
                "status": status_reason,
                "restarts": restarts
            })
        return inspected
    except Exception as e:
        print(f"[K8S CLUSTER NOTICE] Could not connect to live cluster: {e}")
        return [
            {"namespace": "default", "pod": "simulated-nginx-01", "status": "Running", "restarts": 0},
            {"namespace": "production", "pod": "auth-svc-fail-99", "status": "CrashLoopBackOff", "restarts": 22}
        ]

def main():
    print("=== Kubernetes Cluster Pod Health Sentinel ===")
    pods = scan_cluster_pods()

    print(f"\nScanned {len(pods)} pod(s):")
    critical_issues = False

    for p in pods:
        status_flag = "[OK]" if p["status"] == "Running" else "[ALERT]"
        print(f"  {status_flag} Namespace: {p['namespace']:<12} | Pod: {p['pod']:<25} | Status: {p['status']:<18} | Restarts: {p['restarts']}")
        if p["status"] in ["CrashLoopBackOff", "Error", "ImagePullBackOff"]:
            critical_issues = True

    if critical_issues:
        print("\n[ACTION REQUIRED] Failing pods detected! Review logs and restart crashing deployments.")
    else:
        print("\n[HEALTHY] All inspected pods are running nominally.")

if __name__ == "__main__":
    main()
```

---

## 6. Interview & Real-World Questions

### Q1: What is the difference between `config.load_kube_config()` and `config.load_incluster_config()`?
**Answer:**
- `load_kube_config()` reads user credentials, contexts, and cluster certificates from a local file (typically `~/.kube/config`). Used when running automation from outside the cluster (e.g. CI/CD runners, local dev machines).
- `load_incluster_config()` reads the JWT token and CA certificate mounted by Kubernetes directly inside a pod at `/var/run/secrets/kubernetes.io/serviceaccount/`. Used when writing native Kubernetes operators or in-cluster cron jobs.

### Q2: How does Kubernetes RBAC affect Python automation scripts running inside a cluster?
**Answer:**
A Python pod using `load_incluster_config()` runs under a specific `ServiceAccount`. If that `ServiceAccount` is not bound (via `RoleBinding` or `ClusterRoleBinding`) to a `Role` with permissions to `get`, `list`, `watch`, or `delete` target resources (like Pods or Deployments), the Kubernetes API server will reject requests with `403 Forbidden` (`ApiException: (403) Reason: Forbidden`).

### Q3: Why should you use `watch.Watch()` instead of polling `list_namespaced_pod()` in a `while True` loop?
**Answer:**
Repeatedly polling `list_namespaced_pod()` sends full HTTP requests that re-query etcd, causing high API server CPU usage and wasting network bandwidth. `watch.Watch()` opens a persistent HTTP chunked transfer stream. The Kubernetes API server pushes event objects (`ADDED`, `MODIFIED`, `DELETED`) to the Python client immediately as they occur in real time.

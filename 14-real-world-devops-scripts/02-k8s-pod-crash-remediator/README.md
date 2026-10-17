# Real-World Script 02: Kubernetes CrashLoopBackOff Sentinel & Auto-Remediator

---

## 1. Real-World DevOps Problem Statement
In production Kubernetes clusters:
1. **Silent Pod Failures**: Pods frequently enter `CrashLoopBackOff` or `OOMKilled` due to memory leaks, unhandled exceptions, database deadlocks, or transient network timeouts.
2. **Ephemeral Crash Logs**: When a pod crashes repeatedly, Kubernetes recreates the container. If an engineer checks logs minutes later, standard `kubectl logs` only shows the *new* container starting up, while the actual crash traceback from the *previous* container is gone unless `previous=True` is requested.
3. **High Mean Time to Detect (MTTD) & Resolution (MTTR)**: Without automated intervention, failing pods degrade service availability for hours until a user reports an incident.

---

## 2. Complete Code Implementation

See the full script in [k8s_crash_loop_remediator.py](file:///c:/Users/Demon%20Slayer/Documents/PythonForDevOps/14-real-world-devops-scripts/02-k8s-pod-crash-remediator/k8s_crash_loop_remediator.py).

---

## 3. Deep-Dive Code Explanation: What Is It Doing?

### A. Dual Configuration Detection
```python
if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token"):
    config.load_incluster_config()
else:
    config.load_kube_config()
```
- Checks for the presence of the in-cluster ServiceAccount token file.
- If present, configures the client to run natively inside a Kubernetes Pod (e.g. as a CronJob or DaemonSet).
- Otherwise, falls back to `~/.kube/config` for local developer laptops or external Jenkins/GitHub Actions runners.

### B. Accurate State Inspection Across Container Lifecycles
```python
if cs.state.waiting and cs.state.waiting.reason in ["CrashLoopBackOff", "ImagePullBackOff"]:
    is_failing = True
if cs.last_state.terminated and cs.last_state.terminated.reason in ["OOMKilled", "Error"]:
    is_failing = True
```
- Inspects both `state.waiting` (currently failing to boot) and `last_state.terminated` (recently died due to Linux Out-Of-Memory Killer or non-zero exit code).
- Tracks `restart_count` to detect flapping pods that boot, run for 20 seconds, and crash.

### C. Extracting Post-Mortem Crash Logs
```python
core_v1.read_namespaced_pod_log(
    name=pod_name,
    namespace=namespace,
    container=container,
    previous=True,
    tail_lines=15
)
```
- Uses `previous=True` to retrieve stdout/stderr from the terminated container instance before it crashed.
- Captures the exact exception traceback (e.g., `OutOfMemoryError`, `ConnectionRefusedError`).

### D. Zero-Downtime Rollout Restart via Kubernetes API
```python
patch_body = {
    "spec": {
        "template": {
            "metadata": {
                "annotations": {
                    "kubectl.kubernetes.io/restartedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
            }
        }
    }
}
apps_v1.patch_namespaced_deployment(name=dep_name, namespace=namespace, body=patch_body)
```
- Implements the exact programmatic equivalent of `kubectl rollout restart deployment/<name>`.
- Updating the pod template annotation triggers a rolling update, spawning new healthy pods while maintaining replica availability.

### E. Rich Slack Webhook Incident Dispatch
- Posts a formatted Slack card containing namespace, pod name, owner controller (Deployment/ReplicaSet), failure reason, restart count, and the exact last 15 lines of crash logs in a Markdown code block.

---

## 4. Libraries Used & Why

| Library | Why It Was Chosen |
|:---|:---|
| `kubernetes` | The official Kubernetes Python Client library maintained by the Kubernetes SIG API Machinery. Provides direct access to `CoreV1Api` and `AppsV1Api`. |
| `requests` | High-level HTTP client with simple JSON payload dispatching to send Slack/Teams webhook notifications. |
| `argparse` | Provides CLI flags for namespace filtering, Slack webhook URL override, and `--remediate` execution mode. |
| `logging` | Standard library logging formatted for container stdout collection. |

---

## 5. Real-World Problems, Edge Cases & Code Fixes

### Problem 1: Infinite Restart Loops on Code Bugs
- **Real-World Incident**: If a deployment has a permanent bug (e.g., syntax error or bad database migration), triggering a rollout restart will simply create new pods that also enter `CrashLoopBackOff`, creating an infinite restart storm that overloads the kube-apiserver.
- **The Code Fix**: Implement a cooldown lock or Redis/ConfigMap state check. If a deployment has already been restarted within the last 30 minutes and is still crashing, do **not** restart it again; instead, escalate the Slack alert to `CRITICAL: ROLLBACK REQUIRED` and leave the pods for human investigation.

### Problem 2: Terminated Container Log Eviction
- **Real-World Incident**: Calling `read_namespaced_pod_log(previous=True)` throws an HTTP 400 error if the container has crashed so many times that the node container runtime (containerd/CRI-O) already purged the previous container layer.
- **The Code Fix**: Wrapped `read_namespaced_pod_log` in a fallback `try/except` block that first tries `previous=True`, and if that fails, falls back to reading current logs without `previous=True`.

### Problem 3: Multi-Container Pod Ambiguity
- **Real-World Incident**: In pods with sidecars (e.g., Istio `istio-proxy` or Datadog agent), the application container might be healthy while the sidecar crashes, or vice versa. Calling `read_namespaced_pod_log` without specifying a container fails.
- **The Code Fix**: The script iterates through `pod.status.container_statuses` and explicitly passes `container=cs.name` to isolate the exact container experiencing failure.

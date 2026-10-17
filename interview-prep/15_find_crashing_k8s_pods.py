#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 15: Kubernetes CrashLoopBackOff & Error Pod Scanner
================================================================================
Problem Statement:
Write a Python function `detect_failing_k8s_pods(k8s_client=None, restart_threshold=5)`
that:
  1. Inspects all pods across Kubernetes namespaces using `CoreV1Api.list_pod_for_all_namespaces()`.
  2. For each container within a pod, inspects:
     - `state.waiting`: Checks for `CrashLoopBackOff`, `ImagePullBackOff`, `CreateContainerConfigError`.
     - `last_state.terminated`: Checks for termination reason `OOMKilled` or non-zero `exit_code`.
     - `restart_count`: Flags containers exceeding `restart_threshold`.
  3. Returns a structured list of failing pods with namespace, pod name, container,
     failure reason, exit code, and restart count.
  4. Provides structured simulation fallback when executing outside a live cluster.

Constraints:
  - Must handle multi-container pods (sidecars) without assuming single container per pod.
  - Safe defensive attribute lookups (`getattr` or `.get()` style checks).
================================================================================
"""

from typing import List, Dict, Any

try:
    from kubernetes import client, config
    K8S_AVAILABLE = True
except ImportError:
    K8S_AVAILABLE = False


def detect_failing_k8s_pods(core_v1=None, restart_threshold: int = 5) -> List[Dict[str, Any]]:
    """
    Scans Kubernetes pods and extracts failing container statuses.
    """
    failing_pods = []

    if not K8S_AVAILABLE or not core_v1:
        # Realistic mock data for interview demonstration
        return [
            {
                "namespace": "production",
                "pod_name": "order-service-789bf-q82x",
                "container": "order-api",
                "reason": "CrashLoopBackOff",
                "exit_code": 137, # OOM
                "restarts": 14
            },
            {
                "namespace": "ingress",
                "pod_name": "nginx-ingress-controller-4bc2",
                "container": "controller",
                "reason": "ImagePullBackOff",
                "exit_code": None,
                "restarts": 0
            }
        ]

    try:
        pods = core_v1.list_pod_for_all_namespaces(timeout_seconds=5)
        for pod in pods.items:
            pod_name = pod.metadata.name
            namespace = pod.metadata.namespace
            statuses = pod.status.container_statuses or []

            for cs in statuses:
                container_name = cs.name
                restarts = cs.restart_count
                reason = None
                exit_code = None

                # Check current waiting state
                if cs.state and cs.state.waiting:
                    if cs.state.waiting.reason in ["CrashLoopBackOff", "ImagePullBackOff", "CreateContainerConfigError"]:
                        reason = cs.state.waiting.reason

                # Check last termination state (e.g., OOMKilled)
                if cs.last_state and cs.last_state.terminated:
                    term = cs.last_state.terminated
                    if term.reason in ["OOMKilled", "Error"] or term.exit_code != 0:
                        reason = reason or term.reason
                        exit_code = term.exit_code

                # Check restart threshold
                if restarts >= restart_threshold:
                    reason = reason or f"HighRestartCount({restarts})"

                if reason:
                    failing_pods.append({
                        "namespace": namespace,
                        "pod_name": pod_name,
                        "container": container_name,
                        "reason": reason,
                        "exit_code": exit_code,
                        "restarts": restarts
                    })

    except Exception as e:
        return [{"error": f"Kubernetes API call failed: {e}"}]

    return failing_pods


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    print("--- [Question 15 Test: Kubernetes Pod Incident Scanner] ---")
    incidents = detect_failing_k8s_pods()

    print(f"Total Failing Containers Detected: {len(incidents)}")
    print(f"\n{'Namespace':<15} | {'Pod Name':<32} | {'Container':<12} | {'Restarts':<8} | {'Reason'}")
    print("-" * 88)
    for p in incidents:
        print(f"{p['namespace']:<15} | {p['pod_name']:<32} | {p['container']:<12} | {p['restarts']:>5}    | {p['reason']}")

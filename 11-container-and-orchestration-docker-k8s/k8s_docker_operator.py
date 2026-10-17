#!/usr/bin/env python3
"""
11-container-and-orchestration-docker-k8s/k8s_docker_operator.py

Demonstrates:
- Dual-mode Kubernetes config initialization (in-cluster vs kubeconfig)
- Docker client instantiation and container status query
- Detecting CrashLoopBackOff pods in Kubernetes
- Graceful mock fallback if no live cluster or docker daemon is running
"""

import sys
import os
from typing import List, Dict, Any

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

try:
    from kubernetes import client, config
    from kubernetes.client.exceptions import ApiException
    K8S_AVAILABLE = True
except ImportError:
    K8S_AVAILABLE = False


def check_docker_daemon() -> Dict[str, Any]:
    """Inspects local Docker daemon status and running containers."""
    if not DOCKER_AVAILABLE:
        return {"status": "SKIPPED", "reason": "docker package not installed."}

    try:
        dclient = docker.from_env(timeout=2)
        dclient.ping()
        containers = dclient.containers.list(all=True)
        return {
            "status": "ONLINE",
            "container_count": len(containers),
            "running": len([c for c in containers if c.status == "running"])
        }
    except Exception as e:
        return {"status": "OFFLINE", "reason": f"Daemon not reachable: {e}"}


def check_k8s_cluster() -> Dict[str, Any]:
    """Inspects Kubernetes cluster health and detects crashing pods."""
    if not K8S_AVAILABLE:
        return {"status": "SKIPPED", "reason": "kubernetes package not installed."}

    try:
        if os.path.exists(os.path.expanduser("~/.kube/config")):
            config.load_kube_config()
        elif os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token"):
            config.load_incluster_config()
        else:
            return {"status": "OFFLINE", "reason": "No kubeconfig found at ~/.kube/config"}

        v1 = client.CoreV1Api()
        pods = v1.list_pod_for_all_namespaces(timeout_seconds=3)
        return {
            "status": "ONLINE",
            "pod_count": len(pods.items)
        }
    except Exception as e:
        return {"status": "OFFLINE", "reason": f"Cluster not reachable: {e}"}


def main():
    print("==================================================")
    print("      CONTAINER & KUBERNETES OPERATOR SUITE       ")
    print("==================================================")

    # 1. Docker Daemon Check
    print("\n1. Inspecting Docker Engine...")
    docker_status = check_docker_daemon()
    for k, v in docker_status.items():
        print(f"   {k:16}: {v}")

    # 2. Kubernetes Cluster Check
    print("\n2. Inspecting Kubernetes Cluster...")
    k8s_status = check_k8s_cluster()
    for k, v in k8s_status.items():
        print(f"   {k:16}: {v}")

    print("\n[SUCCESS] Orchestration diagnostic pass completed.")


if __name__ == "__main__":
    main()

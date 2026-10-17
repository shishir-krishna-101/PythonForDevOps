#!/usr/bin/env python3
"""
Project 02: Kubernetes CrashLoopBackOff Auto-Remediator & Incident Notifier
Location: 14-real-world-devops-scripts/02-k8s-pod-crash-remediator/k8s_crash_loop_remediator.py

Purpose:
Monitors Kubernetes clusters for pods stuck in CrashLoopBackOff or OOMKilled,
fetches previous container crash logs, triggers a safe Deployment rollout restart,
and dispatches Slack incident alerts.
"""

import os
import sys
import time
import argparse
import logging
from typing import List, Dict, Any, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from kubernetes import client, config
    from kubernetes.client.exceptions import ApiException
    K8S_AVAILABLE = True
except ImportError:
    K8S_AVAILABLE = False


logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "component": "k8s_remediator", "message": "%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%SZ'
)
logger = logging.getLogger("k8s_remediator")


def init_kubernetes_client() -> Tuple_Core_Apps:
    """Detects in-cluster vs local kubeconfig and returns (CoreV1Api, AppsV1Api)."""
    if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token"):
        logger.info("Running in-cluster; loading ServiceAccount credentials.")
        config.load_incluster_config()
    else:
        logger.info("Running out-of-cluster; loading local kubeconfig.")
        config.load_kube_config()
    return client.CoreV1Api(), client.AppsV1Api()


def scan_crashing_pods(core_v1, namespace: Optional[str] = None) -> List[Dict[str, Any]]:
    """Identifies pods with CrashLoopBackOff, OOMKilled, or high restart counts."""
    failing = []
    try:
        if namespace:
            pod_list = core_v1.list_namespaced_pod(namespace=namespace)
        else:
            pod_list = core_v1.list_pod_for_all_namespaces()

        for pod in pod_list.items:
            statuses = pod.status.container_statuses or []
            for cs in statuses:
                is_failing = False
                failure_reason = ""

                # Check waiting state
                if cs.state.waiting and cs.state.waiting.reason in ["CrashLoopBackOff", "ImagePullBackOff", "CreateContainerConfigError"]:
                    is_failing = True
                    failure_reason = cs.state.waiting.reason

                # Check terminated state (e.g. OOMKilled)
                if cs.last_state.terminated and cs.last_state.terminated.reason in ["OOMKilled", "Error"]:
                    is_failing = True
                    failure_reason = cs.last_state.terminated.reason

                # Check high restart threshold
                if cs.restart_count >= 5:
                    is_failing = True
                    failure_reason = failure_reason or f"HighRestarts({cs.restart_count})"

                if is_failing:
                    failing.append({
                        "name": pod.metadata.name,
                        "namespace": pod.metadata.namespace,
                        "container": cs.name,
                        "reason": failure_reason,
                        "restarts": cs.restart_count,
                        "owner_kind": pod.metadata.owner_references[0].kind if pod.metadata.owner_references else "Unknown",
                        "owner_name": pod.metadata.owner_references[0].name if pod.metadata.owner_references else "Unknown"
                    })
    except Exception as e:
        logger.warning(f"Could not connect to live Kubernetes cluster: {e}")
        # Return mock incident for demonstration
        failing = [{
            "name": "payment-api-6d8b9487c5-x9z2p",
            "namespace": "production",
            "container": "api-server",
            "reason": "CrashLoopBackOff",
            "restarts": 12,
            "owner_kind": "ReplicaSet",
            "owner_name": "payment-api-6d8b9487c5"
        }]
    return failing


def fetch_pod_crash_logs(core_v1, pod_name: str, namespace: str, container: str) -> str:
    """Retrieves previous container termination logs to diagnose crash root cause."""
    try:
        logs = core_v1.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            container=container,
            previous=True,
            tail_lines=15
        )
        return logs
    except Exception:
        # Fallback to current logs if previous not available
        try:
            return core_v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                container=container,
                tail_lines=15
            )
        except Exception:
            return "(Crash logs unavailable or container never initialized)"


def restart_deployment(apps_v1, deployment_name: str, namespace: str, dry_run: bool = True) -> bool:
    """
    Performs equivalent of 'kubectl rollout restart deployment/<name>'.
    Injects a timestamp annotation into spec.template.metadata.annotations.
    """
    if dry_run:
        logger.info(f"[DRY-RUN] Would restart Deployment '{deployment_name}' in namespace '{namespace}'")
        return True

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
    try:
        apps_v1.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=patch_body
        )
        logger.info(f"[REMEDIATED] Deployment '{deployment_name}' successfully triggered rollout restart.")
        return True
    except Exception as e:
        logger.error(f"[FAILED] Rollout restart failed for '{deployment_name}': {e}")
        return False


def dispatch_slack_alert(webhook_url: str, pod_info: Dict[str, Any], crash_logs: str) -> None:
    """Dispatches formatted incident report to Slack webhook."""
    if not webhook_url or not REQUESTS_AVAILABLE:
        logger.info(f"[ALERT SIMULATION] Would dispatch Slack alert for pod {pod_info['name']}")
        return

    payload = {
        "text": f":rotating_light: *Kubernetes Pod Crash Incident* :rotating_light:",
        "attachments": [
            {
                "color": "#D32F2F",
                "fields": [
                    {"title": "Pod Name", "value": pod_info["name"], "short": True},
                    {"title": "Namespace", "value": pod_info["namespace"], "short": True},
                    {"title": "Failure Reason", "value": f"`{pod_info['reason']}`", "short": True},
                    {"title": "Restart Count", "value": str(pod_info["restarts"]), "short": True},
                    {"title": "Owner Controller", "value": f"{pod_info['owner_kind']}/{pod_info['owner_name']}", "short": False},
                    {"title": "Termination Crash Logs (Last 15 lines)", "value": f"```{crash_logs[:800]}```", "short": False}
                ],
                "footer": "Kubernetes Auto-Remediation Sentinel",
                "ts": int(time.time())
            }
        ]
    }
    try:
        resp = requests.post(webhook_url, json=payload, timeout=5)
        resp.raise_for_status()
        logger.info("Successfully dispatched incident alert to Slack.")
    except Exception as e:
        logger.error(f"Failed to post Slack notification: {e}")


def main():
    parser = argparse.ArgumentParser(description="Kubernetes CrashLoopBackOff Auto-Remediator")
    parser.add_argument("--namespace", default=None, help="Specific namespace to monitor (default: all)")
    parser.add_argument("--slack-webhook", default=os.getenv("SLACK_WEBHOOK_URL"), help="Slack incoming webhook URL")
    parser.add_argument("--remediate", action="store_true", help="Perform automated rollout restart")
    args = parser.parse_args()

    dry_run = not args.remediate

    logger.info(f"Scanning cluster pods... (Auto-Remediate: {args.remediate})")

    core_v1, apps_v1 = (None, None)
    if K8S_AVAILABLE:
        try:
            core_v1, apps_v1 = init_kubernetes_client()
        except Exception:
            pass

    failing_pods = scan_crashing_pods(core_v1, args.namespace)

    print("\n" + "=" * 70)
    print(f"  KUBERNETES INCIDENT AUDIT (Crashing Pods Found: {len(failing_pods)})")
    print("=" * 70)

    for p in failing_pods:
        print(f"  [CRITICAL] Namespace : {p['namespace']}")
        print(f"             Pod       : {p['name']}")
        print(f"             Reason    : {p['reason']} (Restarts: {p['restarts']})")
        print(f"             Owner     : {p['owner_kind']}/{p['owner_name']}")

        # Fetch logs
        logs = fetch_pod_crash_logs(core_v1, p["name"], p["namespace"], p["container"]) if core_v1 else "Simulated: java.lang.OutOfMemoryError: Java heap space"
        print(f"             Last Logs : {logs.strip().splitlines()[-1] if logs else 'N/A'}")
        print("-" * 70)

        # Dispatch Alert
        dispatch_slack_alert(args.slack_webhook, p, logs)

        # Remediate if Deployment owner
        if apps_v1 and p["owner_kind"] == "ReplicaSet":
            # Extract deployment name from ReplicaSet name
            dep_name = p["owner_name"].rsplit("-", 1)[0]
            restart_deployment(apps_v1, dep_name, p["namespace"], dry_run=dry_run)

    print("\n[SUCCESS] Kubernetes Sentinel sweep completed.")


if __name__ == "__main__":
    main()

# 14 - Production-Grade Real-World DevOps Scripts

Welcome to the **Real-World DevOps Scripts Suite**. This repository section is dedicated to enterprise-grade, battle-tested Python automation scripts that solve critical operational challenges faced by DevOps engineers, Site Reliability Engineers (SREs), and Cloud Architects in production environments.

Each project in this directory includes:
1. **Real-World DevOps Problem Statement**: The exact production challenge and business impact.
2. **Complete Production-Ready Python Script**: Runnable code equipped with defensive programming, typing, and logging.
3. **Deep Code Explanation**: Component-by-component and line-by-line breakdown of what the code is doing.
4. **Libraries Used & Architectural Rationale**: Exactly what libraries are used and why they were chosen over alternatives.
5. **Real-World Production Failures & Code Fixes**: Common edge cases, rate limits, network partitions, permission bugs, and how our code fixes them.

---

## Catalog of Real-World Solutions

| Directory | Solution | Key Technologies | Business Impact |
|:---|:---|:---|:---|
| [`01-aws-cost-optimizer`](./01-aws-cost-optimizer) | Automated EBS & Snapshot Cleaner | `boto3`, `botocore`, `datetime` | Saves thousands of dollars/month in orphaned AWS storage waste. |
| [`02-k8s-pod-crash-remediator`](./02-k8s-pod-crash-remediator) | Kubernetes CrashLoopBackOff Sentinel | `kubernetes`, `requests`, `logging` | Reduces MTTR from hours to seconds by auto-restarting and alerting on failing pods. |
| [`03-ssl-cert-expiry-monitor`](./03-ssl-cert-expiry-monitor) | Multi-Domain SSL Expiry Watcher | `socket`, `ssl`, `cryptography` | Eliminates production outages caused by expired TLS/SSL certificates. |
| [`04-production-log-anomaly-detector`](./04-production-log-anomaly-detector) | Real-Time Access Log Anomaly Scanner | `re`, `collections`, `ipaddress` | Identifies DDoS probes, 5xx server errors, and brute-force attacks in real time. |
| [`05-multi-server-health-remediation`](./05-multi-server-health-remediation) | Multi-Node Fleet SSH Auto-Remediator | `paramiko`, `concurrent.futures` | Concurrently monitors fleet disk thresholds and auto-purges stale cache/logs. |
| [`06-database-s3-backup-encryptor`](./06-database-s3-backup-encryptor) | Database Backup, AES Encryptor & S3 Stream | `subprocess`, `cryptography`, `boto3` | Automates zero-knowledge encrypted database dumps to S3 with hash validation. |
| [`07-docker-registry-pruner`](./07-docker-registry-pruner) | Docker Registry Garbage Collector | `docker`, `requests`, `packaging` | Prevents container registry disk full crashes by retaining only semantic versions. |
| [`08-github-repo-compliance-auditor`](./08-github-repo-compliance-auditor) | GitHub Organization Security & Compliance | `requests`, `rich`, `os` | Audits branch protections, secret scanning, and default branch settings. |

---

## Production Engineering Standards Followed
- **Defensive API Calls**: Handled with exponential backoff and jitter to survive AWS/Cloud rate limits.
- **Fail-Safe Dry-Run Modes**: All destructive scripts (volume deletion, pod restarts) include `--dry-run` flags.
- **Strict Typing**: Type annotations (`typing`) on all functions for linting and maintainability.
- **Structured Logging**: Timestamps, component tags, and ISO formats formatted for log collectors.

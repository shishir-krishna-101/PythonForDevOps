# Python for DevOps: The Complete Hands-On Engineering Playbook

Welcome to **PythonForDevOps** — an enterprise-grade, comprehensive repository designed to take you from foundational Python syntax to building production-ready cloud automation, self-healing Kubernetes operators, CI/CD pipelines, and FinOps tooling.

---

## Repository Architecture & Roadmap

```
PythonForDevOps/
├── .gitignore
├── requirements.txt
├── README.md                                          <-- You are here
│
├── 01-python-basics-for-devops/                       <-- Module 01: Variables, strings, functions, venvs
│   ├── README.md
│   └── preflight_check.py
│
├── 02-data-structures-for-devops/                     <-- Module 02: Lists, dicts, sets, drift detection
│   ├── README.md
│   └── inventory_manager.py
│
├── 03-file-handling-and-serialization/                <-- Module 03: JSON, YAML, k8s manifest patcher
│   ├── README.md
│   └── manifest_updater.py
│
├── 04-os-and-system-automation/                       <-- Module 04: os, sys, pathlib, psutil, host health
│   ├── README.md
│   └── system_health_monitor.py
│
├── 05-subprocess-and-cli-execution/                   <-- Module 05: Safe process execution without shell=True
│   ├── README.md
│   └── cli_executor.py
│
├── 06-regular-expressions-and-log-parsing/            <-- Module 06: Nginx/syslog parsing, regex named groups
│   ├── README.md
│   └── log_parser.py
│
├── 07-error-handling-and-logging/                     <-- Module 07: Custom exceptions, 12-factor JSON logs
│   ├── README.md
│   └── logger_and_exceptions.py
│
├── 08-networking-and-api-interactions/                <-- Module 08: REST APIs, connection pooling, sockets
│   ├── README.md
│   └── network_api_prober.py
│
├── 09-ssh-and-remote-server-management/               <-- Module 09: Paramiko, SFTP, multi-node management
│   ├── README.md
│   └── ssh_fleet_manager.py
│
├── 10-cloud-automation-aws-boto3/                     <-- Module 10: AWS Boto3, EC2, EBS, S3 paginators
│   ├── README.md
│   └── aws_cloud_optimizer.py
│
├── 11-container-and-orchestration-docker-k8s/         <-- Module 11: Docker SDK, Kubernetes Python Client
│   ├── README.md
│   └── k8s_docker_operator.py
│
├── 12-ci-cd-and-git-automation/                       <-- Module 12: GitPython, SemVer bumping, release tags
│   ├── README.md
│   └── git_release_automation.py
│
├── 13-cli-development-for-devops/                     <-- Module 13: Argparse, Click, Rich terminal tables
│   ├── README.md
│   └── devops_cli.py
│
└── 14-real-world-devops-scripts/                      <-- Production-Grade Real-World Script Suite
    ├── README.md
    ├── 01-aws-cost-optimizer/                         <-- FinOps unattached EBS & stale snapshot purger
    │   ├── README.md
    │   └── aws_ebs_snapshot_cost_optimizer.py
    ├── 02-k8s-pod-crash-remediator/                   <-- CrashLoopBackOff sentinel & Slack notifier
    │   ├── README.md
    │   └── k8s_crash_loop_remediator.py
    ├── 03-ssl-cert-expiry-monitor/                    <-- Multi-domain SNI TLS monitor & Prometheus exporter
    │   ├── README.md
    │   └── ssl_cert_expiration_checker.py
    ├── 04-production-log-anomaly-detector/            <-- Nginx 5xx spike & WAF/iptables rule generator
    │   ├── README.md
    │   └── log_anomaly_detector.py
    ├── 05-multi-server-health-remediation/            <-- Concurrent SSH fleet disk sentinel & auto-cleaner
    │   ├── README.md
    │   └── remote_fleet_auto_cleaner.py
    ├── 06-database-s3-backup-encryptor/               <-- Zero-knowledge AES encrypted DB dumps to S3
    │   ├── README.md
    │   └── db_backup_s3_encryptor.py
    ├── 07-docker-registry-pruner/                     <-- SemVer-aware registry garbage collector
    │   ├── README.md
    │   └── docker_registry_cleaner.py
    └── 08-github-repo-compliance-auditor/             <-- GitHub organization DevSecOps compliance auditor
        ├── README.md
        └── github_compliance_auditor.py
│
└── interview-prep/                                    <-- 20 Comprehensive DevOps/SRE Interview Coding Challenges
    ├── README.md                                      # Master catalog with questions, concepts & links
    ├── 01_parse_nginx_access_logs.py
    ├── 02_extract_failed_ssh_attempts.py
    ├── 03_mask_sensitive_data_in_logs.py
    ├── 04_find_and_delete_large_old_files.py
    ├── 05_disk_usage_threshold_alert.py
    ├── 06_calculate_directory_size.py
    ├── 07_validate_and_patch_json_yaml.py
    ├── 08_diff_two_config_files.py
    ├── 09_flatten_nested_dict.py
    ├── 10_check_service_endpoints_health.py
    ├── 11_tcp_port_scanner_and_checker.py
    ├── 12_retry_decorator_with_exponential_backoff.py
    ├── 13_find_unattached_ebs_volumes.py
    ├── 14_ec2_auto_start_stop_by_tags.py
    ├── 15_find_crashing_k8s_pods.py
    ├── 16_clean_dangling_docker_images.py
    ├── 17_semantic_version_comparator.py
    ├── 18_cidr_ip_range_validator.py
    ├── 19_merge_sorted_log_streams.py
    └── 20_rate_limiter_token_bucket.py
```

---

## Core Learning Modules (01 - 13)

Every module folder contains:
1. **What It Is**: Conceptual foundations and syntax reference.
2. **What Is the Use of It**: Direct relevance to real DevOps, SRE, and Cloud workloads.
3. **How to Use It**: Core operations and patterns.
4. **How to Implement It**: Step-by-step production implementations.
5. **Hands-On DevOps Example**: Runnable script solving realistic infrastructure requirements.
6. **Interview & Real-World Questions**: In-depth questions and answers frequently asked in senior DevOps/SRE interviews.

| Module | Focus Area | Key Concepts | Hands-On Script |
|:---|:---|:---|:---|
| [**01 - Python Basics**](./01-python-basics-for-devops) | Fundamentals | F-strings, type hints, loops, virtualenvs | [`preflight_check.py`](./01-python-basics-for-devops/preflight_check.py) |
| [**02 - Data Structures**](./02-data-structures-for-devops) | Inventory & Drift | Dict `.get()`, list/dict comprehensions, set algebra | [`inventory_manager.py`](./02-data-structures-for-devops/inventory_manager.py) |
| [**03 - File Handling & Serialization**](./03-file-handling-and-serialization) | CaC & GitOps | JSON, PyYAML, atomic writes, k8s patchers | [`manifest_updater.py`](./03-file-handling-and-serialization/manifest_updater.py) |
| [**04 - OS & System Automation**](./04-os-and-system-automation) | SRE Host Telemetry | `os`, `sys`, `pathlib.Path`, `psutil`, `shutil` | [`system_health_monitor.py`](./04-os-and-system-automation/system_health_monitor.py) |
| [**05 - Process Execution**](./05-subprocess-and-cli-execution) | Subprocess & Tool Wrappers | `subprocess.run()`, pipes, timeouts, security | [`cli_executor.py`](./05-subprocess-and-cli-execution/cli_executor.py) |
| [**06 - Regular Expressions**](./06-regular-expressions-and-log-parsing) | Log Parsing & SIEM | `re.compile()`, named capture groups, PII redaction | [`log_parser.py`](./06-regular-expressions-and-log-parsing/log_parser.py) |
| [**07 - Error Handling & Logging**](./07-error-handling-and-logging) | Observability | Custom exceptions, exponential backoff, JSON logs | [`logger_and_exceptions.py`](./07-error-handling-and-logging/logger_and_exceptions.py) |
| [**08 - Networking & REST APIs**](./08-networking-and-api-interactions) | API Probing & Webhooks | `requests.Session`, `Retry`, socket port checks | [`network_api_prober.py`](./08-networking-and-api-interactions/network_api_prober.py) |
| [**09 - SSH & Remote Management**](./09-ssh-and-remote-server-management) | Fleet Automation | Paramiko SSHClient, key auth, SFTP, channels | [`ssh_fleet_manager.py`](./09-ssh-and-remote-server-management/ssh_fleet_manager.py) |
| [**10 - Cloud Automation (AWS Boto3)**](./10-cloud-automation-aws-boto3) | AWS CloudOps | Boto3 clients vs resources, paginators, waiters | [`aws_cloud_optimizer.py`](./10-cloud-automation-aws-boto3/aws_cloud_optimizer.py) |
| [**11 - Containers & Orchestration**](./11-container-and-orchestration-docker-k8s) | Docker & Kubernetes | Docker SDK, `kubernetes` client, CoreV1/AppsV1 | [`k8s_docker_operator.py`](./11-container-and-orchestration-docker-k8s/k8s_docker_operator.py) |
| [**12 - CI/CD & Git Automation**](./12-ci-cd-and-git-automation) | Pipeline Automation | GitPython, SemVer calculation, release tags | [`git_release_automation.py`](./12-ci-cd-and-git-automation/git_release_automation.py) |
| [**13 - CLI Tool Development**](./13-cli-development-for-devops) | Internal Developer Tools | `argparse`, `click`, `rich` styled tables, `--json` | [`devops_cli.py`](./13-cli-development-for-devops/devops_cli.py) |

---

## Enterprise Real-World Production Scripts Suite (14)

The [**`14-real-world-devops-scripts/`**](./14-real-world-devops-scripts) directory contains complete, standalone end-to-end automation solutions. Each script includes:
- Problem statement & operational impact
- Component breakdown and code walkthrough
- Architectural library selection rationale
- Common production failure modes and code fixes

| Project | Problem Solved | Key Libraries |
|:---|:---|:---|
| [**01 - AWS FinOps Cost Optimizer**](./14-real-world-devops-scripts/01-aws-cost-optimizer) | Deletes unattached EBS volumes & stale snapshots to eliminate AWS bill bloat. | `boto3`, `botocore.config.Config` |
| [**02 - K8s CrashLoopBackOff Sentinel**](./14-real-world-devops-scripts/02-k8s-pod-crash-remediator) | Detects crashing pods, grabs previous termination logs, restarts deployments, alerts Slack. | `kubernetes`, `requests` |
| [**03 - SSL/TLS Expiration Watcher**](./14-real-world-devops-scripts/03-ssl-cert-expiry-monitor) | Connects via TLS with SNI, calculates remaining days, and exports Prometheus metrics. | `ssl`, `socket` |
| [**04 - Access Log Anomaly Scanner**](./14-real-world-devops-scripts/04-production-log-anomaly-detector) | Identifies 5xx SLA spikes and attacker probes; auto-generates `iptables` and AWS WAF rules. | `re`, `collections.Counter` |
| [**05 - Multi-Server SSH Auto-Remediator**](./14-real-world-devops-scripts/05-multi-server-health-remediation) | Concurrently audits fleet disk space and cleans journal logs/caches when thresholds breach. | `paramiko`, `concurrent.futures` |
| [**06 - Database Backup & S3 Encryptor**](./14-real-world-devops-scripts/06-database-s3-backup-encryptor) | Creates Gzip-compressed, AES-256 (Fernet) zero-knowledge encrypted DB dumps to S3 with SHA-256. | `cryptography`, `gzip`, `boto3` |
| [**07 - Docker Registry Garbage Collector**](./14-real-world-devops-scripts/07-docker-registry-pruner) | Prunes ephemeral CI images while strictly protecting SemVer tags and active production digests. | `re`, `datetime` |
| [**08 - GitHub Org Compliance Auditor**](./14-real-world-devops-scripts/08-github-repo-compliance-auditor) | Audits organization repos for branch protections, secret scanning, and Dependabot compliance. | `requests`, `logging` |

---

## 🎯 DevOps & SRE Interview Preparation Suite

The [**`interview-prep/`**](./interview-prep) directory contains **20 battle-tested coding interview questions** frequently asked in senior DevOps, SRE, Platform, and Cloud Engineer technical rounds (Amazon, Google, Meta, Microsoft, Netflix, Stripe):

- **[01. Parse Nginx Access Logs & 5xx Error Rates](./interview-prep/01_parse_nginx_access_logs.py)**
- **[02. Detect SSH Brute Force Attacks from auth.log](./interview-prep/02_extract_failed_ssh_attempts.py)**
- **[03. Mask Sensitive Data & API Keys in Log Streams](./interview-prep/03_mask_sensitive_data_in_logs.py)**
- **[04. Find & Purge Large Stale Files with Dry-Run](./interview-prep/04_find_and_delete_large_old_files.py)**
- **[05. Host Multi-Partition Disk Usage Monitor](./interview-prep/05_disk_usage_threshold_alert.py)**
- **[06. Recursive Directory Disk Usage Calculator](./interview-prep/06_calculate_directory_size.py)**
- **[07. Validate & Dynamically Patch Kubernetes Manifests](./interview-prep/07_validate_and_patch_json_yaml.py)**
- **[08. Deep Configuration Diff Engine (Staging vs Prod)](./interview-prep/08_diff_two_config_files.py)**
- **[09. Flatten & Unflatten Nested Cloud Dictionaries](./interview-prep/09_flatten_nested_dict.py)**
- **[10. Concurrent Service Health Checker with Latency](./interview-prep/10_check_service_endpoints_health.py)**
- **[11. Fast Multi-Threaded TCP Port Scanner & Probe](./interview-prep/11_tcp_port_scanner_and_checker.py)**
- **[12. Custom @retry Decorator with Exponential Backoff & Jitter](./interview-prep/12_retry_decorator_with_exponential_backoff.py)**
- **[13. AWS FinOps Unattached EBS Volume Auditor](./interview-prep/13_find_unattached_ebs_volumes.py)**
- **[14. Automated EC2 Start/Stop Scheduler by Tags](./interview-prep/14_ec2_auto_start_stop_by_tags.py)**
- **[15. Kubernetes CrashLoopBackOff & Error Pod Scanner](./interview-prep/15_find_crashing_k8s_pods.py)**
- **[16. Prune Dangling Docker Images & Reclaim Storage](./interview-prep/16_clean_dangling_docker_images.py)**
- **[17. Custom Semantic Versioning (SemVer) Comparator](./interview-prep/17_semantic_version_comparator.py)**
- **[18. CIDR Subnet Matcher & IP Security Filter (Bitwise)](./interview-prep/18_cidr_ip_range_validator.py)**
- **[19. K-Way Merge Sorted Log Streams with O(1) Memory (Heap)](./interview-prep/19_merge_sorted_log_streams.py)**
- **[20. Thread-Safe Token Bucket Rate Limiter](./interview-prep/20_rate_limiter_token_bucket.py)**

See the [Interview Prep README](./interview-prep/README.md) for full question statements, concepts tested, and constraints.

---

## Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/shishir-krishna-101/PythonForDevOps.git
cd PythonForDevOps
```

### 2. Set Up a Virtual Environment
```bash
# On Linux / macOS
python3 -m venv venv
source venv/bin/activate

# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install All Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Any Module or Real-World Script
```bash
# Test the DevOps Pre-Flight Checker
python 01-python-basics-for-devops/preflight_check.py

# Test the SSL/TLS Expiration Monitor with Prometheus metrics
python 14-real-world-devops-scripts/03-ssl-cert-expiry-monitor/ssl_cert_expiration_checker.py --prom-format

# Test the DevOps CLI
python 13-cli-development-for-devops/devops_cli.py status
```

---

## Production DevOps Engineering Principles
1. **Never Hardcode Secrets**: Always source API keys, passwords, and tokens from environment variables or secrets managers (AWS Secrets Manager, HashiCorp Vault).
2. **Defensive API Calls**: Always configure timeouts and exponential backoff retry policies.
3. **Fail-Safe Dry-Runs**: Destructive operations must always support a `--dry-run` flag and require explicit `--execute` flags for real modifications.
4. **Structured JSON Logs**: Direct logs to `sys.stdout` formatted as JSON so container runtimes and log daemons can stream and index them without local file rotation.
5. **Zero-Downtime Automation**: Rolling restarts, graceful terminations, and health checks ensure automated operations never impact customer traffic.

---

## Contributing & License
Contributions, issues, and feature requests are welcome! Feel free to check the issues tab.
Distributed under the MIT License.

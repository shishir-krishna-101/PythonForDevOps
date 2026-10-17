# DevOps & SRE Python Coding Interview Preparation

Welcome to the **DevOps & SRE Interview Preparation Suite**. This directory contains the most frequent, high-impact Python coding problems asked during technical rounds for **DevOps Engineer**, **Site Reliability Engineer (SRE)**, **Platform Engineer**, and **Cloud Infrastructure Engineer** roles at top-tier companies (Amazon, Google, Meta, Microsoft, Netflix, Stripe, Uber).

Every question includes:
- The **exact question and problem statement** documented at the top of each Python script.
- A **production-grade, typed Python solution** with defensive error handling.
- A built-in **runnable verification test suite** in `if __name__ == "__main__":`.

---

## 📋 Comprehensive Interview Question Catalog

### Domain 1: Log Parsing & Threat Detection

| # | Question Title | Concepts Tested | Solution File |
|:---|:---|:---|:---|
| **01** | **Parse Web Server Access Logs & Calculate Metrics** | Regex CLF matching, status code aggregation, error rate % | [`01_parse_nginx_access_logs.py`](./01_parse_nginx_access_logs.py) |
| **02** | **Detect Brute Force SSH Attacks from auth.log** | Pattern extraction, frequency thresholds, automated iptables rules | [`02_extract_failed_ssh_attempts.py`](./02_extract_failed_ssh_attempts.py) |
| **03** | **Mask Sensitive Data and Secrets in Log Streams** | Regex lookaheads, PII & credential redaction (SOC2/PCI compliance) | [`03_mask_sensitive_data_in_logs.py`](./03_mask_sensitive_data_in_logs.py) |

---

### Domain 2: Filesystem & System Automation

| # | Question Title | Concepts Tested | Solution File |
|:---|:---|:---|:---|
| **04** | **Find & Purge Large Stale Files Older Than N Days** | `pathlib`, `os.walk`, timestamp arithmetic, dry-run safety | [`04_find_and_delete_large_old_files.py`](./04_find_and_delete_large_old_files.py) |
| **05** | **Multi-Partition Disk Usage Monitor & Alert Sentinel** | `psutil.disk_partitions`, bytes to GiB conversion, status codes | [`05_disk_usage_threshold_alert.py`](./05_disk_usage_threshold_alert.py) |
| **06** | **Recursive Directory Disk Usage Calculator** | Circular symlink avoidance, inode tracking, human-readable units | [`06_calculate_directory_size.py`](./06_calculate_directory_size.py) |

---

### Domain 3: Configuration, JSON & YAML Manipulation

| # | Question Title | Concepts Tested | Solution File |
|:---|:---|:---|:---|
| **07** | **Validate & Dynamically Patch Kubernetes Manifests** | PyYAML `safe_load`, schema validation, annotation injection | [`07_validate_and_patch_json_yaml.py`](./07_validate_and_patch_json_yaml.py) |
| **08** | **Deep Configuration Diff Engine (Staging vs Prod)** | Recursive dictionary traversal, dot notation path generation | [`08_diff_two_config_files.py`](./08_diff_two_config_files.py) |
| **09** | **Flatten and Unflatten Nested Dictionaries** | Recursion, key serialization, cloud metadata transformation | [`09_flatten_nested_dict.py`](./09_flatten_nested_dict.py) |

---

### Domain 4: Networking, APIs & Reliability

| # | Question Title | Concepts Tested | Solution File |
|:---|:---|:---|:---|
| **10** | **Concurrent Service Health Checker with Latency** | `ThreadPoolExecutor`, HTTP probing, SLA availability % | [`10_check_service_endpoints_health.py`](./10_check_service_endpoints_health.py) |
| **11** | **Fast Multi-Threaded TCP Port Scanner & Probe** | Low-level Python `socket`, non-blocking I/O, service mapping | [`11_tcp_port_scanner_and_checker.py`](./11_tcp_port_scanner_and_checker.py) |
| **12** | **Custom @retry Decorator with Exponential Backoff** | Higher-order decorators, exponential backoff, randomized jitter | [`12_retry_decorator_with_exponential_backoff.py`](./12_retry_decorator_with_exponential_backoff.py) |

---

### Domain 5: Cloud Automation & FinOps (AWS)

| # | Question Title | Concepts Tested | Solution File |
|:---|:---|:---|:---|
| **13** | **AWS FinOps Unattached EBS Volume Auditor** | Boto3 EC2 client, API paginators, cost calculation, tag compliance | [`13_find_unattached_ebs_volumes.py`](./13_find_unattached_ebs_volumes.py) |
| **14** | **Automated EC2 Start/Stop Scheduler by Tags** | Server-side AWS filters, non-prod schedule rules, safety guards | [`14_ec2_auto_start_stop_by_tags.py`](./14_ec2_auto_start_stop_by_tags.py) |

---

### Domain 6: Containerization & Orchestration (Docker & K8s)

| # | Question Title | Concepts Tested | Solution File |
|:---|:---|:---|:---|
| **15** | **Kubernetes CrashLoopBackOff & Error Pod Scanner** | Kubernetes Python Client (`CoreV1Api`), container statuses | [`15_find_crashing_k8s_pods.py`](./15_find_crashing_k8s_pods.py) |
| **16** | **Prune Dangling Docker Images & Reclaim Storage** | Docker Python SDK, active container protection, dangling filters | [`16_clean_dangling_docker_images.py`](./16_clean_dangling_docker_images.py) |

---

### Domain 7: Algorithms & Infrastructure Utilities

| # | Question Title | Concepts Tested | Solution File |
|:---|:---|:---|:---|
| **17** | **Custom Semantic Versioning (SemVer) Comparator** | SemVer grammar parsing, tuple-based precedence, custom sort key | [`17_semantic_version_comparator.py`](./17_semantic_version_comparator.py) |
| **18** | **CIDR Subnet Matcher & IP Security Filter** | `ipaddress` module and 32-bit bitwise masking (`ip & mask`) | [`18_cidr_ip_range_validator.py`](./18_cidr_ip_range_validator.py) |
| **19** | **K-Way Merge Sorted Log Streams with O(1) Memory** | Min-Heap (`heapq`), generator pipelines, external sorting | [`19_merge_sorted_log_streams.py`](./19_merge_sorted_log_streams.py) |
| **20** | **Thread-Safe Token Bucket Rate Limiter** | Lazy token refill, thread concurrency locks, monotonic clocks | [`20_rate_limiter_token_bucket.py`](./20_rate_limiter_token_bucket.py) |

---

## 💡 How to Practice

Run any interview question directly with Python:

```bash
# Example: Run Question 01 (Log Parsing & Metrics)
python interview-prep/01_parse_nginx_access_logs.py

# Example: Run Question 12 (Retry Decorator with Backoff)
python interview-prep/12_retry_decorator_with_exponential_backoff.py

# Example: Run Question 18 (CIDR Subnet Bitwise Matching)
python interview-prep/18_cidr_ip_range_validator.py

# Example: Run Question 20 (Token Bucket Rate Limiter)
python interview-prep/20_rate_limiter_token_bucket.py
```

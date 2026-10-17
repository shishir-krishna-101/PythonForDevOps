# DevOps & SRE Python Coding Interview Preparation

Welcome to the **DevOps & SRE Interview Preparation Suite**. This directory contains **30 high-impact Python coding problems** covering the 4 core dimensions evaluated in technical rounds for **DevOps Engineer**, **Site Reliability Engineer (SRE)**, **Platform Engineer**, and **Cloud Infrastructure Engineer** roles at top-tier companies (Google SRE, Meta Production Engineer, Amazon SysDE/DevOps, Netflix, Stripe, Uber).

---

## 📖 Must-Read: How to Code Independently with Only Official Docs

> **Stop trying to memorize code!**
> Read our in-depth handbook: [**`HOW_TO_LEARN_AND_CODE_FROM_OFFICIAL_DOCS.md`**](./HOW_TO_LEARN_AND_CODE_FROM_OFFICIAL_DOCS.md)
> It teaches you:
> 1. The **5-Step Mental Framework** to break down any coding prompt into an input-output contract.
> 2. How to navigate `docs.python.org` in 30 seconds to find function signatures and canonical recipes.
> 3. The **Interactive Python REPL** secret weapons (`help()`, `dir()`, `type()`, `python -i`).
> 4. The DevOps Standard Library "When to Use What" mental map.

---

## 📋 Comprehensive Interview Question Catalog (30 Questions)

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

### Domain 7: DevOps Algorithms & Data Structures

| # | Question Title | Concepts Tested | Solution File |
|:---|:---|:---|:---|
| **17** | **Custom Semantic Versioning (SemVer) Comparator** | SemVer grammar parsing, tuple-based precedence, custom sort key | [`17_semantic_version_comparator.py`](./17_semantic_version_comparator.py) |
| **18** | **CIDR Subnet Matcher & IP Security Filter** | `ipaddress` module and 32-bit bitwise masking (`ip & mask`) | [`18_cidr_ip_range_validator.py`](./18_cidr_ip_range_validator.py) |
| **19** | **K-Way Merge Sorted Log Streams with O(1) Memory** | Min-Heap (`heapq`), generator pipelines, external sorting | [`19_merge_sorted_log_streams.py`](./19_merge_sorted_log_streams.py) |
| **20** | **Thread-Safe Token Bucket Rate Limiter** | Lazy token refill, thread concurrency locks, monotonic clocks | [`20_rate_limiter_token_bucket.py`](./20_rate_limiter_token_bucket.py) |
| **21** | **Microservice & Terraform Dependency Resolver (DAG)** | Kahn's Algorithm (Topological Sort), `collections.deque`, cycle detection | [`21_topological_sort_dag_dependency_resolver.py`](./21_topological_sort_dag_dependency_resolver.py) |
| **22** | **Thread-Safe LRU Cache with Time-To-Live (TTL)** | `collections.OrderedDict`, O(1) access/eviction, monotonic expiration | [`22_lru_cache_with_ttl.py`](./22_lru_cache_with_ttl.py) |
| **23** | **Git Bisect Simulation (Binary Search for Bad Commit)** | O(log N) binary search on monotonic test results | [`23_git_bisect_binary_search.py`](./23_git_bisect_binary_search.py) |

---

### Domain 8: Infrastructure Low-Level System Design (LLD / OOP)

| # | Question Title | Concepts Tested | Solution File |
|:---|:---|:---|:---|
| **24** | **Object-Oriented Software Load Balancer** | Round Robin, Weighted Round Robin, Least Connections, OOP design | [`24_software_load_balancer.py`](./24_software_load_balancer.py) |
| **27** | **Transactional In-Memory Key-Value Store (Mini Redis)** | Nested transaction stack, ACID rollback, dictionary delta layers | [`27_in_memory_kv_store_with_transactions.py`](./27_in_memory_kv_store_with_transactions.py) |
| **30** | **Standard 5-Field Cron Expression Parser & Matcher** | String parsing, range/step expansion, `datetime.weekday()` math | [`30_cron_expression_parser.py`](./30_cron_expression_parser.py) |

---

### Domain 9: Advanced Concurrency, Async & Live Debugging

| # | Question Title | Concepts Tested | Solution File |
|:---|:---|:---|:---|
| **25** | **Multi-Threaded Producer-Consumer Task Worker Queue** | `queue.Queue`, `threading.Thread`, Poison Pill shutdown pattern | [`25_producer_consumer_worker_queue.py`](./25_producer_consumer_worker_queue.py) |
| **26** | **High-Scale Non-Blocking AsyncIO Health Scanner** | `asyncio`, `asyncio.Semaphore`, event loop cooperative multitasking | [`26_asyncio_mass_health_checker.py`](./26_asyncio_mass_health_checker.py) |
| **28** | **Sliding Window Log Spike & SLA Anomaly Detector** | `collections.deque` sliding window in O(N), timestamp eviction | [`28_sliding_window_log_spike_detector.py`](./28_sliding_window_log_spike_detector.py) |
| **29** | **Live Debugging: Race Condition & Deadlock Elimination** | Atomic operations, Coffman conditions, global lock acquisition ordering | [`29_concurrency_deadlock_race_condition_fix.py`](./29_concurrency_deadlock_race_condition_fix.py) |

---

## 💡 How to Practice

Every single file is standalone and runnable with zero configuration:

```bash
# Example 1: Run DAG Dependency Resolver (Topological Sort)
python interview-prep/21_topological_sort_dag_dependency_resolver.py

# Example 2: Run LRU Cache with TTL
python interview-prep/22_lru_cache_with_ttl.py

# Example 3: Run Git Bisect Simulation
python interview-prep/23_git_bisect_binary_search.py

# Example 4: Run Software Load Balancer
python interview-prep/24_software_load_balancer.py

# Example 5: Run Producer-Consumer Worker Queue
python interview-prep/25_producer_consumer_worker_queue.py

# Example 6: Run Transactional KV Store
python interview-prep/27_in_memory_kv_store_with_transactions.py

# Example 7: Run Sliding Window Spike Detector
python interview-prep/28_sliding_window_log_spike_detector.py

# Example 8: Run Race Condition & Deadlock Fix
python interview-prep/29_concurrency_deadlock_race_condition_fix.py

# Example 9: Run Cron Expression Parser
python interview-prep/30_cron_expression_parser.py
```

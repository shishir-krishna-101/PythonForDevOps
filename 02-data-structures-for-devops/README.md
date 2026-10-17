# 02 - Data Structures for DevOps

---

## 1. What It Is
Python data structures organize, store, and manage data efficiently in memory:
- **Lists (`list`)**: Ordered, mutable collections of items. Ideal for maintaining ordered sequences such as deployment steps, server lists, and port arrays.
- **Tuples (`tuple`)**: Ordered, immutable sequences. Useful for fixed records like `(ip, port)` pairs or database connection tuples that should not change at runtime.
- **Dictionaries (`dict`)**: Key-value hash maps with $O(1)$ average lookup time. The backbone of modern cloud computing representations (JSON outputs, Kubernetes manifests, AWS Boto3 responses, Ansible facts).
- **Sets (`set`)**: Unordered collections of unique elements. Indispensable for deduplicating IP addresses, calculating diffs between desired and actual states (drift detection), and firewall rule comparisons.

---

## 2. What Is the Use of It in DevOps?
Every cloud API, CLI tool, and monitoring system outputs data structured as nested maps, lists, and key-value pairs:
1. **Infrastructure State Drift Detection**: Compare the *desired* list of security group CIDRs against the *actual* CIDRs using Set operations (`actual - desired` reveals rogue IPs).
2. **Dynamic Inventory Parsing**: Filter hundreds of EC2 or Kubernetes nodes by tags, environment, or health status using list and dict comprehensions.
3. **Safe Configuration Lookups**: Use `.get(key, default)` to avoid catastrophic `KeyError` crashes when parsing inconsistent third-party JSON payloads or Kubernetes metadata.
4. **Grouping & Aggregation**: Group log lines by HTTP status code or group server instances by AWS Availability Zone.

---

## 3. How to Use It

### Key Data Structure Operations
```python
# 1. Lists & List Comprehension
servers = ["web-01", "web-02", "db-01", "cache-01"]
web_servers = [s for s in servers if s.startswith("web")]

# 2. Dictionaries & Defensive Access
cluster_config = {
    "cluster_name": "k8s-prod-us-east",
    "version": "1.29",
    "nodes": {"min": 3, "max": 10}
}
# Defensive access prevents KeyError
node_max = cluster_config.get("nodes", {}).get("max", 5)

# 3. Sets & Set Mathematics (Drift Detection)
desired_firewall_ips = {"10.0.0.1", "10.0.0.2", "192.168.1.50"}
actual_firewall_ips  = {"10.0.0.1", "192.168.1.50", "203.0.113.88"}

# IPs to add:
to_add = desired_firewall_ips - actual_firewall_ips    # {"10.0.0.2"}
# Rogue IPs to revoke:
to_remove = actual_firewall_ips - desired_firewall_ips # {"203.0.113.88"}
```

---

## 4. How to Implement It: Step-by-Step

### Step A: Handling Nested API Responses
Cloud responses (AWS, GCP, Kubernetes) return deeply nested dictionaries. Always access them cleanly:
```python
instance = {
    "InstanceId": "i-0a1b2c3d4e5f",
    "State": {"Name": "running", "Code": 16},
    "Tags": [
        {"Key": "Environment", "Value": "Production"},
        {"Key": "Owner", "Value": "DataOps"}
    ]
}

# Convert AWS Tag list into a standard Python lookup dictionary:
tag_map = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
env = tag_map.get("Environment", "Unknown")
```

### Step B: Sorting and Grouping Infrastructure Metrics
```python
metrics = [
    {"host": "srv-1", "cpu": 45.2},
    {"host": "srv-2", "cpu": 89.1},
    {"host": "srv-3", "cpu": 12.0}
]

# Sort servers from highest CPU usage to lowest
sorted_servers = sorted(metrics, key=lambda m: m["cpu"], reverse=True)
top_consumer = sorted_servers[0]
```

---

## 5. DevOps Hands-On Example: Security Group Drift & Inventory Analyzer

```python
#!/usr/bin/env python3
"""
Dynamic Infrastructure Inventory & Security Group Drift Checker.
Demonstrates:
- List & dictionary comprehension
- Set difference operations for drift analysis
- Safe dictionary traversal
"""
from typing import Dict, List, Set, Any

# Simulated cloud inventory payload
INFRASTRUCTURE_STATE: List[Dict[str, Any]] = [
    {"id": "i-01", "env": "prod", "role": "web", "ip": "10.0.1.10", "status": "running"},
    {"id": "i-02", "env": "prod", "role": "web", "ip": "10.0.1.11", "status": "running"},
    {"id": "i-03", "env": "stage", "role": "web", "ip": "10.0.1.12", "status": "stopped"},
    {"id": "i-04", "env": "prod", "role": "db", "ip": "10.0.2.20", "status": "running"},
    {"id": "i-05", "env": "dev", "role": "db", "ip": "10.0.2.21", "status": "running"},
]

DESIRED_FIREWALL_ALLOWLIST: Set[str] = {
    "10.0.1.10",
    "10.0.1.11",
    "10.0.2.20",
    "10.0.3.99" # Planned new instance
}

def filter_active_production_ips(inventory: List[Dict[str, Any]]) -> Set[str]:
    """Filters inventory for running production instances and returns unique IPs."""
    prod_running_ips = {
        server["ip"]
        for server in inventory
        if server.get("env") == "prod" and server.get("status") == "running"
    }
    return prod_running_ips

def detect_firewall_drift(desired: Set[str], current: Set[str]) -> Dict[str, Set[str]]:
    """Calculates missing rules and unauthorized rules."""
    return {
        "missing_in_current": desired - current,
        "unexpected_in_current": current - desired
    }

def main():
    print("=== Analyzing Infrastructure Inventory ===")
    active_prod_ips = filter_active_production_ips(INFRASTRUCTURE_STATE)
    print(f"Active Production IPs detected ({len(active_prod_ips)}): {active_prod_ips}")

    drift = detect_firewall_drift(DESIRED_FIREWALL_ALLOWLIST, active_prod_ips)

    print("\n--- Firewall Drift Analysis ---")
    if drift["missing_in_current"]:
        print(f"[ACTION REQUIRED] Add these IPs to firewall: {drift['missing_in_current']}")
    if drift["unexpected_in_current"]:
        print(f"[ACTION REQUIRED] Revoke these rogue IPs: {drift['unexpected_in_current']}")

    if not drift["missing_in_current"] and not drift["unexpected_in_current"]:
        print("[AUDIT PASSED] Desired state and current state are in complete alignment!")

if __name__ == "__main__":
    main()
```

---

## 6. Interview & Real-World Questions

### Q1: When would you use a `set` over a `list` in infrastructure scripts?
**Answer:**
1. **Uniqueness**: A set automatically removes duplicates (e.g., extracting unique client IPs from 1,000,000 access log rows).
2. **Lookup Speed**: Checking membership `if ip in allowed_ips:` is $O(1)$ for a `set` (hash-table lookup) compared to $O(n)$ for a `list` (linear scan).
3. **Set Algebra**: Diffs, unions, and intersections (`desired - actual`) allow 1-line drift calculation.

### Q2: How can a `KeyError` in Python cause an outage in an automated scaling script, and how do you protect against it?
**Answer:**
If an AWS/GCP API response omits an optional key (such as `Tags` or `PublicIpAddress` for private instances), direct indexing `response["Tags"]` raises an unhandled `KeyError` exception, abruptly terminating the script.
**Protection**:
- Use `.get(key, default)`: `response.get("Tags", [])`
- Use dictionary `.setdefault()` or `collections.defaultdict`
- Perform explicit validation: `if "Tags" in response:`

### Q3: What is the performance and readability advantage of List/Dict Comprehensions in DevOps tasks?
**Answer:**
Comprehensions are executed in optimized C-level loops inside Python, making them noticeably faster than manual `for` loops with repetitive `.append()`. They also express the transformation and filtering of infrastructure objects in a single declarative line:
```python
# Declarative, readable, and fast:
healthy_hosts = [h["id"] for h in cluster if h.get("health") == "OK"]
```

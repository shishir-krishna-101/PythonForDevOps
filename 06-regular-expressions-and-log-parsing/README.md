# 06 - Regular Expressions & Log Parsing for DevOps

---

## 1. What It Is
Regular expressions (regex) provide powerful pattern-matching syntax for searching, extracting, and manipulating text. Python's built-in `re` module includes:
- **`re.compile(pattern)`**: Pre-compiles regular expressions into reusable pattern objects for maximum execution speed across large log files.
- **`re.search(pattern, string)`**: Scans through a string, looking for the first location where the pattern matches.
- **`re.findall(pattern, string)`**: Returns all non-overlapping matches as a list of strings or tuples.
- **`re.sub(pattern, replacement, string)`**: Replaces matched substrings (useful for sanitizing sensitive data like API keys, tokens, or passwords from logs).
- **Named Groups `(?P<name>...)`**: Allows extracting matches into named dictionary keys rather than brittle index offsets.

---

## 2. What Is the Use of It in DevOps?
Modern distributed infrastructure generates millions of log lines per minute:
1. **Nginx / Ingress Controller Log Analysis**: Extract client IP, HTTP request method, URI path, status code (e.g. 502, 504), response size, and upstream latency.
2. **Security & Intrusion Detection (SIEM)**: Scan `/var/log/auth.log` or syslog for repeated `Failed password for invalid user` entries to block brute-force attackers.
3. **Log Sanitization & PII Redaction**: Mask credit card numbers, JWT tokens, Bearer headers, and database passwords before forwarding logs to Datadog, CloudWatch, or Splunk.
4. **Terraform / CI Output Parsing**: Extract deployed resource IDs (VPC IDs, IP addresses) from unstructured CLI stdout.

---

## 3. How to Use It

### Named Capture Groups for Readability
Named capture groups make your regex self-documenting:
```python
import re

LOG_PATTERN = re.compile(
    r'^(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+-\s+-\s+'
    r'\[(?P<timestamp>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+(?P<path>[^\s]+)\s+HTTP/[0-9.]+"\s+'
    r'(?P<status>\d{3})\s+(?P<bytes>\d+)'
)

log_line = '192.168.1.105 - - [17/Oct/2026:14:20:10 +0000] "POST /api/v1/checkout HTTP/1.1" 500 1420'

match = LOG_PATTERN.match(log_line)
if match:
    data = match.groupdict()
    print(f"IP: {data['ip']}, Path: {data['path']}, Status: {data['status']}")
```

### Sanitizing Secrets with `re.sub`
```python
import re

raw_log = "DATABASE_URL=postgres://app_user:SuperSecretPassword123@db.internal:5432/main"

# Redact credentials
sanitized = re.sub(r'://([^:]+):([^@]+)@', r'://\1:***REDACTED***@', raw_log)
print(sanitized)
# Outputs: postgres://app_user:***REDACTED***@db.internal:5432/main
```

---

## 4. How to Implement It: Step-by-Step

### Step A: High-Performance Log Stream Parsing
When processing gigabyte-scale logs, compiling the regex outside the loop is essential for performance:
```python
import re
from collections import Counter

IP_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

def count_top_ips(log_file_path: str, top_n: int = 10):
    ip_counter = Counter()
    with open(log_file_path, "r", encoding="utf-8") as f:
        for line in f:
            match = IP_REGEX.search(line)
            if match:
                ip_counter[match.group(0)] += 1
    return ip_counter.most_common(top_n)
```

### Step B: Detecting Failed Authentication Spikes
```python
import re

AUTH_FAIL_REGEX = re.compile(r'Failed password for (?:invalid user )?(?P<user>\w+) from (?P<ip>\S+)')

def analyze_auth_failures(log_lines: list):
    offenders = {}
    for line in log_lines:
        match = AUTH_FAIL_REGEX.search(line)
        if match:
            ip = match.group('ip')
            offenders[ip] = offenders.get(ip, 0) + 1
    return offenders
```

---

## 5. DevOps Hands-On Example: Nginx Access Log Analyzer & Threat Detector

```python
#!/usr/bin/env python3
"""
Nginx Web Server Access Log Analyzer & Security Inspector.
Parses Nginx log lines, aggregates status code distributions,
identifies 5xx server errors, and flags high-frequency client IPs.
"""
import re
from collections import Counter
from typing import List, Dict, Any

SAMPLE_NGINX_LOGS = [
    '203.0.113.195 - - [17/Oct/2026:10:00:01 +0000] "GET /api/v1/health HTTP/1.1" 200 45',
    '203.0.113.195 - - [17/Oct/2026:10:00:02 +0000] "POST /api/v1/login HTTP/1.1" 401 120',
    '203.0.113.195 - - [17/Oct/2026:10:00:03 +0000] "POST /api/v1/login HTTP/1.1" 401 120',
    '203.0.113.195 - - [17/Oct/2026:10:00:04 +0000] "POST /api/v1/login HTTP/1.1" 401 120',
    '198.51.100.44 - - [17/Oct/2026:10:00:05 +0000] "GET /products/item/99 HTTP/1.1" 200 3500',
    '198.51.100.88 - - [17/Oct/2026:10:00:06 +0000] "GET /checkout HTTP/1.1" 502 612',
    '198.51.100.88 - - [17/Oct/2026:10:00:07 +0000] "GET /checkout HTTP/1.1" 504 0',
    '10.0.0.12 - - [17/Oct/2026:10:00:08 +0000] "GET /metrics HTTP/1.1" 200 8900'
]

LOG_PATTERN = re.compile(
    r'^(?P<client_ip>\S+)\s+\S+\s+\S+\s+\[(?P<timestamp>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+(?P<uri>\S+)\s+[A-Z0-9./]+"\s+'
    r'(?P<status>\d{3})\s+(?P<bytes>\d+)'
)

def analyze_logs(lines: List[str]) -> Dict[str, Any]:
    status_counts = Counter()
    ip_counts = Counter()
    server_errors = []

    for line in lines:
        match = LOG_PATTERN.match(line.strip())
        if not match:
            continue
        data = match.groupdict()
        status = int(data["status"])
        ip = data["client_ip"]

        status_counts[status] += 1
        ip_counts[ip] += 1

        if status >= 500:
            server_errors.append({"ip": ip, "uri": data["uri"], "status": status})

    return {
        "status_distribution": dict(status_counts),
        "top_ips": ip_counts.most_common(3),
        "server_errors": server_errors
    }

def main():
    print("=== Nginx Log Analysis & Anomaly Detection ===")
    results = analyze_logs(SAMPLE_NGINX_LOGS)

    print("\n1. HTTP Status Code Distribution:")
    for code, count in results["status_distribution"].items():
        print(f"   HTTP {code}: {count} requests")

    print("\n2. Top Client Request Sources:")
    for ip, count in results["top_ips"]:
        print(f"   IP: {ip:<15} ({count} requests)")

    print("\n3. Critical 5xx Upstream Server Errors:")
    for err in results["server_errors"]:
        print(f"   [5xx Alert] URI: {err['uri']:<20} | Status: {err['status']} | Client: {err['ip']}")

if __name__ == "__main__":
    main()
```

---

## 6. Interview & Real-World Questions

### Q1: Why is pre-compiling regular expressions with `re.compile()` considered best practice in DevOps?
**Answer:**
When analyzing logs with millions of entries, calling `re.search("...", line)` inside a loop requires Python to parse and compile the regex string on every iteration (or query its internal small regex LRU cache). `pattern = re.compile("...")` pre-computes the state machine bytecode once, yielding significant speedups (often 2x–5x) on large files.

### Q2: How can Catastrophic Backtracking happen in Regex, and how do you prevent it in production?
**Answer:**
Catastrophic backtracking occurs when a nested quantifier pattern like `(a+)+$` is matched against non-matching input like `aaaaaaaaaaaaaaaaaaaaaaaa!`. The regex engine evaluates exponential permutations ($O(2^n)$), pegging the CPU at 100% and freezing the Python automation worker (ReDoS vulnerability).
**Prevention**:
- Avoid nested greedy quantifiers `(.*)*`
- Use atomic groups or possessive quantifiers where available
- Enforce strict input string length validation before regex matching

### Q3: What is the difference between `re.match()`, `re.search()`, and `re.fullmatch()`?
**Answer:**
- `re.match()`: Only matches from the **very start** of the string.
- `re.search()`: Scans the **entire string** for the first match anywhere.
- `re.fullmatch()`: Requires the pattern to match the **entire string from start to finish**.

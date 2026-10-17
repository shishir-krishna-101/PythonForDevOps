#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 01: Parse Web Server Access Logs & Calculate Metrics
================================================================================
Problem Statement:
You are given a web server access log (e.g., Nginx or Apache Combined Log Format).
Write a Python function `analyze_access_logs(log_data)` that:
  1. Parses each log line and extracts the client IP address, HTTP method, URI,
     and HTTP status code.
  2. Identifies the Top 3 most frequent client IP addresses.
  3. Calculates the total percentage of HTTP 5xx server error responses.
  4. Returns a summary dictionary containing the metrics.
  5. The function must handle malformed log lines gracefully without crashing.

Sample Log Format:
  <IP> - - [<timestamp>] "<METHOD> <URI> <PROTOCOL>" <STATUS> <BYTES>

Constraints:
  - Time Complexity: O(N) where N is the number of log lines.
  - Memory Complexity: O(U) where U is the number of unique IPs / statuses.
  - Do not crash on empty input or corrupted log lines.
================================================================================
"""

import re
from collections import Counter
from typing import List, Dict, Any, Tuple


# Regex pattern to match Combined Log Format
LOG_REGEX = re.compile(
    r'^(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<time>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+(?P<uri>\S+)\s+[A-Z0-9./]+"\s+'
    r'(?P<status>\d{3})\s+(?P<bytes>\d+)'
)


def analyze_access_logs(logs: List[str], top_n: int = 3) -> Dict[str, Any]:
    """
    Parses a list of access log lines and computes traffic telemetry.
    """
    total_valid_requests = 0
    ip_counter = Counter()
    status_counter = Counter()
    malformed_lines = 0

    for line in logs:
        line = line.strip()
        if not line:
            continue

        match = LOG_REGEX.match(line)
        if not match:
            malformed_lines += 1
            continue

        entry = match.groupdict()
        ip = entry["ip"]
        status = int(entry["status"])

        total_valid_requests += 1
        ip_counter[ip] += 1
        status_counter[status] += 1

    # Calculate 5xx error rate
    count_5xx = sum(count for status, count in status_counter.items() if 500 <= status < 600)
    error_rate_5xx = (count_5xx / total_valid_requests * 100) if total_valid_requests > 0 else 0.0

    return {
        "total_valid_requests": total_valid_requests,
        "malformed_lines": malformed_lines,
        "top_client_ips": ip_counter.most_common(top_n),
        "status_distribution": dict(status_counter),
        "error_rate_5xx_percent": round(error_rate_5xx, 2)
    }


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    test_logs = [
        '192.168.1.10 - - [17/Oct/2026:10:00:01 +0000] "GET /index.html HTTP/1.1" 200 1024',
        '192.168.1.10 - - [17/Oct/2026:10:00:02 +0000] "POST /api/login HTTP/1.1" 200 450',
        '10.0.0.5 - - [17/Oct/2026:10:00:03 +0000] "GET /api/orders HTTP/1.1" 500 230',
        '192.168.1.10 - - [17/Oct/2026:10:00:04 +0000] "GET /images/logo.png HTTP/1.1" 200 8900',
        '172.16.0.99 - - [17/Oct/2026:10:00:05 +0000] "GET /api/checkout HTTP/1.1" 502 0',
        '10.0.0.5 - - [17/Oct/2026:10:00:06 +0000] "GET /api/orders HTTP/1.1" 503 0',
        'INVALID CORRUPTED LOG LINE HERE',
        '172.16.0.99 - - [17/Oct/2026:10:00:07 +0000] "GET /healthz HTTP/1.1" 200 24'
    ]

    result = analyze_access_logs(test_logs)

    print("--- [Question 01 Test Results] ---")
    print(f"Total Requests Processed : {result['total_valid_requests']}")
    print(f"Malformed Lines Skipped  : {result['malformed_lines']}")
    print(f"5xx Error Rate           : {result['error_rate_5xx_percent']}%")
    print("Top Client IPs           :")
    for ip, count in result["top_client_ips"]:
        print(f"  * {ip}: {count} requests")
    print("Status Codes             :", result["status_distribution"])

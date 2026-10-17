#!/usr/bin/env python3
"""
06-regular-expressions-and-log-parsing/log_parser.py

Demonstrates:
- Pre-compiled regex with named capture groups
- Parsing web access logs (Nginx/Apache format)
- Detecting HTTP 5xx errors and high-frequency callers
- PII & Secret Redaction using re.sub
"""

import re
from collections import Counter
from typing import List, Dict, Any


LOG_PATTERN = re.compile(
    r'^(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+-\s+-\s+'
    r'\[(?P<timestamp>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+(?P<uri>\S+)\s+[A-Z0-9./]+"\s+'
    r'(?P<status>\d{3})\s+(?P<bytes>\d+)'
)

SAMPLE_RAW_LOGS = [
    '10.244.0.15 - - [17/Oct/2026:12:00:01 +0000] "GET /api/v1/health HTTP/1.1" 200 12',
    '198.51.100.22 - - [17/Oct/2026:12:00:02 +0000] "POST /api/v1/auth/login?token=eyJhbGciOiJIUzI1NiJ9 HTTP/1.1" 401 89',
    '198.51.100.22 - - [17/Oct/2026:12:00:03 +0000] "POST /api/v1/auth/login HTTP/1.1" 401 89',
    '198.51.100.22 - - [17/Oct/2026:12:00:04 +0000] "POST /api/v1/auth/login HTTP/1.1" 401 89',
    '203.0.113.50 - - [17/Oct/2026:12:00:05 +0000] "GET /api/v1/orders HTTP/1.1" 500 450',
    '203.0.113.50 - - [17/Oct/2026:12:00:06 +0000] "GET /api/v1/orders HTTP/1.1" 502 0',
    '10.244.0.16 - - [17/Oct/2026:12:00:07 +0000] "GET /metrics HTTP/1.1" 200 1024',
    '203.0.113.77 - - [17/Oct/2026:12:00:08 +0000] "GET /api/v1/products HTTP/1.1" 200 5400'
]


def redact_sensitive_tokens(text: str) -> str:
    """Masks query parameter tokens and secrets."""
    return re.sub(r'([?&]token=)[^&\s]+', r'\1***REDACTED***', text)


def parse_access_logs(logs: List[str]) -> Dict[str, Any]:
    status_counter = Counter()
    ip_counter = Counter()
    server_errors = []

    for raw_line in logs:
        clean_line = redact_sensitive_tokens(raw_line)
        match = LOG_PATTERN.match(clean_line)
        if not match:
            continue

        entry = match.groupdict()
        status = int(entry['status'])
        ip = entry['ip']

        status_counter[status] += 1
        ip_counter[ip] += 1

        if status >= 500:
            server_errors.append({
                "ip": ip,
                "timestamp": entry["timestamp"],
                "method": entry["method"],
                "uri": entry["uri"],
                "status": status
            })

    return {
        "status_counts": dict(status_counter),
        "top_ips": ip_counter.most_common(5),
        "server_errors": server_errors
    }


def main():
    print("==================================================")
    print("      DEVOPS LOG ANALYZER & INCIDENT DETECTOR     ")
    print("==================================================")

    results = parse_access_logs(SAMPLE_RAW_LOGS)

    print("\n--- 1. HTTP Status Distribution ---")
    for code, count in sorted(results["status_counts"].items()):
        print(f"  HTTP {code}: {count} requests")

    print("\n--- 2. High-Frequency Requesting IPs ---")
    for ip, count in results["top_ips"]:
        print(f"  IP: {ip:<16} -> {count} requests")

    print("\n--- 3. Upstream 5xx Failures Requiring Investigation ---")
    for err in results["server_errors"]:
        print(f"  [ALERT] {err['timestamp']} | {err['method']} {err['uri']} -> HTTP {err['status']} (Client: {err['ip']})")

    # Flag potential brute-force attacker (e.g. > 2 failed requests)
    for ip, count in results["top_ips"]:
        if count >= 3:
            print(f"\n[SECURITY WARNING] Potential brute-force / DDoS probe detected from IP: {ip} ({count} requests)")


if __name__ == "__main__":
    main()

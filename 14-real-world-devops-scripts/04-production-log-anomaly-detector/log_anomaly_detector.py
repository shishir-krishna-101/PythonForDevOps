#!/usr/bin/env python3
"""
Project 04: Production Web Access Log Anomaly Detector & WAF Rule Generator
Location: 14-real-world-devops-scripts/04-production-log-anomaly-detector/log_anomaly_detector.py

Purpose:
Streams web server logs (Nginx/Envoy/Apache), identifies HTTP 5xx error spikes,
flags malicious security probes (path traversal, scanner probes), detects brute force
IP addresses, and generates automated firewall (iptables/WAF) mitigation commands.
"""

import re
import sys
import argparse
import logging
from collections import Counter, defaultdict
from typing import List, Dict, Any, Generator

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "module": "log_detector", "message": "%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%SZ'
)
logger = logging.getLogger("log_detector")

# High-performance compiled regex for Common Log Format (CLF) / Combined Log Format
LOG_PATTERN = re.compile(
    r'^(?P<client_ip>\S+)\s+\S+\s+\S+\s+\[(?P<timestamp>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+(?P<uri>\S+)\s+[A-Z0-9./]+"\s+'
    r'(?P<status>\d{3})\s+(?P<bytes>\d+)'
)

# Known vulnerability scanning probes
SUSPICIOUS_SIGNATURES = [
    r'\.\./',              # Path traversal
    r'/etc/passwd',        # LFI
    r'wp-login\.php',      # WordPress brute force probe
    r'\.env',              # Leaked environment file probe
    r'/api/debug',         # Exposed internal debug endpoints
    r'<script',            # XSS injection attempt
    r'union\s+select'      # SQL injection attempt
]
COMPILED_SIGNATURES = [re.compile(sig, re.IGNORECASE) for sig in SUSPICIOUS_SIGNATURES]

SAMPLE_LOG_STREAM = [
    '192.168.1.10 - - [17/Oct/2026:14:00:01 +0000] "GET /api/v1/health HTTP/1.1" 200 45',
    '192.168.1.10 - - [17/Oct/2026:14:00:02 +0000] "GET /products HTTP/1.1" 200 1200',
    '198.51.100.77 - - [17/Oct/2026:14:00:03 +0000] "GET /.env HTTP/1.1" 404 180',
    '198.51.100.77 - - [17/Oct/2026:14:00:04 +0000] "GET /etc/passwd HTTP/1.1" 404 180',
    '198.51.100.77 - - [17/Oct/2026:14:00:05 +0000] "GET /wp-login.php HTTP/1.1" 404 180',
    '203.0.113.88 - - [17/Oct/2026:14:00:06 +0000] "POST /api/v1/checkout HTTP/1.1" 500 512',
    '203.0.113.88 - - [17/Oct/2026:14:00:07 +0000] "POST /api/v1/checkout HTTP/1.1" 502 0',
    '203.0.113.88 - - [17/Oct/2026:14:00:08 +0000] "POST /api/v1/checkout HTTP/1.1" 503 0',
    '192.168.1.20 - - [17/Oct/2026:14:00:09 +0000] "POST /api/v1/login HTTP/1.1" 401 90',
    '192.168.1.20 - - [17/Oct/2026:14:00:10 +0000] "POST /api/v1/login HTTP/1.1" 401 90',
    '192.168.1.20 - - [17/Oct/2026:14:00:11 +0000] "POST /api/v1/login HTTP/1.1" 401 90',
    '192.168.1.20 - - [17/Oct/2026:14:00:12 +0000] "POST /api/v1/login HTTP/1.1" 401 90'
]


def stream_log_lines(source_lines: List[str]) -> Generator[str, None, None]:
    """Generates clean log lines lazily to preserve O(1) memory consumption."""
    for line in source_lines:
        cleaned = line.strip()
        if cleaned:
            yield cleaned


def analyze_log_stream(lines: Generator[str, None, None]) -> Dict[str, Any]:
    total_requests = 0
    status_counts = Counter()
    ip_request_counts = Counter()
    ip_failed_auth_counts = Counter()
    server_5xx_errors = []
    suspicious_probes = []

    for line in lines:
        match = LOG_PATTERN.match(line)
        if not match:
            continue

        entry = match.groupdict()
        total_requests += 1
        ip = entry["client_ip"]
        status = int(entry["status"])
        uri = entry["uri"]

        status_counts[status] += 1
        ip_request_counts[ip] += 1

        # 1. Check for 5xx Server Outages
        if status >= 500:
            server_5xx_errors.append({"ip": ip, "uri": uri, "status": status, "time": entry["timestamp"]})

        # 2. Check for Auth Brute Force (401 on login endpoints)
        if status == 401 and "login" in uri.lower():
            ip_failed_auth_counts[ip] += 1

        # 3. Check for Suspicious Exploit Probes
        for sig in COMPILED_SIGNATURES:
            if sig.search(uri):
                suspicious_probes.append({"ip": ip, "uri": uri, "time": entry["timestamp"]})
                break

    # Calculate 5xx Error Rate
    total_5xx = sum(count for code, count in status_counts.items() if code >= 500)
    error_rate_pct = (total_5xx / total_requests * 100) if total_requests > 0 else 0.0

    return {
        "total_requests": total_requests,
        "status_distribution": dict(status_counts),
        "error_rate_5xx_pct": round(error_rate_pct, 2),
        "server_5xx_errors": server_5xx_errors,
        "brute_force_ips": [ip for ip, cnt in ip_failed_auth_counts.items() if cnt >= 3],
        "suspicious_probes": suspicious_probes
    }


def main():
    parser = argparse.ArgumentParser(description="Web Access Log Anomaly & Threat Detector")
    parser.add_argument("--file", help="Path to Nginx/Apache access.log file (default: built-in sample stream)")
    args = parser.parse_args()

    if args.file:
        def file_line_generator():
            with open(args.file, "r", encoding="utf-8") as f:
                for line in f:
                    yield line
        stream = file_line_generator()
    else:
        stream = stream_log_lines(SAMPLE_LOG_STREAM)

    print("================================================================================")
    print("           PRODUCTION ACCESS LOG ANOMALY & THREAT DETECTOR                     ")
    print("================================================================================")

    results = analyze_log_stream(stream)

    print(f"\n1. Traffic Volume : {results['total_requests']} requests inspected")
    print(f"2. 5xx Error Rate : {results['error_rate_5xx_pct']}% of total traffic")
    print("3. Status Codes   :", results["status_distribution"])

    # High 5xx Alert
    if results["error_rate_5xx_pct"] > 5.0:
        print(f"\n[CRITICAL SERVICE ALERT] HTTP 5xx rate ({results['error_rate_5xx_pct']}%) exceeds 5% SLA threshold!")
        for err in results["server_5xx_errors"][:3]:
            print(f"   * {err['time']} | {err['uri']} -> HTTP {err['status']} (Client: {err['ip']})")

    # Security Threats Detected
    print("\n--- Security Threat Analysis ---")
    if results["suspicious_probes"]:
        print(f"[SECURITY ALERT] {len(results['suspicious_probes'])} malicious vulnerability probes detected:")
        for probe in results["suspicious_probes"]:
            print(f"   * Offending IP: {probe['ip']:<15} | Target Probe: {probe['uri']}")

    if results["brute_force_ips"]:
        print(f"[BRUTE FORCE ALERT] Repeated failed authentications detected from:")
        for ip in results["brute_force_ips"]:
            print(f"   * Attacker IP: {ip}")

    # Generate Automated Mitigation Firewall Rules
    rogue_ips = set(p["ip"] for p in results["suspicious_probes"]).union(set(results["brute_force_ips"]))
    if rogue_ips:
        print("\n--- Automated Firewall Mitigation Commands ---")
        print("# Linux iptables drop commands:")
        for ip in rogue_ips:
            print(f"sudo iptables -A INPUT -s {ip} -j DROP")
        print("\n# AWS WAF CLI IP-Set block command:")
        print(f"aws wafv2 update-ip-set --name BlockedAttackers --scope CLOUDFRONT --addresses {' '.join(f'{ip}/32' for ip in rogue_ips)}")
    else:
        print("[OK] No rogue IP addresses flagged for mitigation.")

    print("\n[SUCCESS] Anomaly scan completed.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 11: Fast Multi-Threaded TCP Port Scanner & Probe
================================================================================
Problem Statement:
DevOps engineers often need to test firewall configurations, security group rules,
or verify if a newly deployed microservice or database port is listening.

Write a Python function `scan_target_ports(host, ports, timeout=1.0, max_threads=10)`
that:
  1. Uses the low-level `socket` standard library module to test TCP handshakes.
  2. Concurrently probes ports using `concurrent.futures.ThreadPoolExecutor`.
  3. Returns a sorted list of open ports and closed/filtered ports.
  4. Automatically maps well-known port numbers to their standard service names
     (e.g., 22 -> SSH, 80 -> HTTP, 443 -> HTTPS, 3306 -> MySQL, 5432 -> PostgreSQL).
  5. Catches socket timeouts, connection refused, and DNS resolution failures cleanly.

Constraints:
  - Must close all socket descriptors cleanly (using context managers or try-finally).
  - Fast execution: Scanning 20 ports should complete in < 2 seconds.
================================================================================
"""

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple


COMMON_PORT_NAMES = {
    21: "FTP",
    22: "SSH",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    443: "HTTPS",
    1433: "MSSQL",
    3306: "MySQL",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP-Alt / Proxy",
    9090: "Prometheus"
}


def test_port(host: str, port: int, timeout: float = 1.0) -> Tuple[int, bool, str]:
    """
    Attempts a TCP three-way handshake with (host, port).
    Returns (port, is_open, error_or_service_name).
    """
    service_name = COMMON_PORT_NAMES.get(port, "Unknown")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((host, port))
            if result == 0:
                return port, True, service_name
            else:
                return port, False, "Closed / Filtered"
    except (socket.timeout, OSError):
        return port, False, "Timeout"


def scan_target_ports(
    host: str,
    ports: List[int],
    timeout: float = 1.0,
    max_threads: int = 10
) -> Dict[str, Any]:
    """
    Concurrently scans specified TCP ports on a host.
    """
    # Verify DNS first
    try:
        ip_addr = socket.gethostbyname(host)
    except socket.gaierror as e:
        return {"error": f"Failed to resolve hostname '{host}': {e}"}

    open_ports = []
    closed_ports = []

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_port = {
            executor.submit(test_port, host, port, timeout): port
            for port in ports
        }
        for future in as_completed(future_to_port):
            port, is_open, desc = future.result()
            entry = {"port": port, "service": desc}
            if is_open:
                open_ports.append(entry)
            else:
                closed_ports.append(entry)

    open_ports.sort(key=lambda x: x["port"])
    closed_ports.sort(key=lambda x: x["port"])

    return {
        "target_host": host,
        "resolved_ip": ip_addr,
        "total_scanned": len(ports),
        "open_count": len(open_ports),
        "open_ports": open_ports,
        "closed_ports": closed_ports
    }


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    target = "8.8.8.8" # Google Public DNS
    test_ports = [22, 53, 80, 443, 3306, 5432, 8080]

    print("--- [Question 11 Test: Port Scanner] ---")
    scan_report = scan_target_ports(target, test_ports, timeout=1.5)

    if "error" in scan_report:
        print(f"Scan failed: {scan_report['error']}")
    else:
        print(f"Target Host : {scan_report['target_host']} ({scan_report['resolved_ip']})")
        print(f"Open Ports  : {scan_report['open_count']} / {scan_report['total_scanned']}")
        print("\nDiscovered Open Ports:")
        for op in scan_report["open_ports"]:
            print(f"  * Port {op['port']:<5} -> {op['service']}")

#!/usr/bin/env python3
"""
08-networking-and-api-interactions/network_api_prober.py

Demonstrates:
- Resilient requests Session with HTTPAdapter & Retry
- Low-level TCP socket port testing
- Parsing REST API JSON responses
- Safe timeout guards and error handling
"""

import sys
import socket
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Dict, Any


def create_resilient_session(retries: int = 2) -> requests.Session:
    """Configures a Session with connection pooling and automated backoff retries."""
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def probe_tcp_socket(host: str, port: int, timeout: float = 2.0) -> bool:
    """Checks if a TCP port is open and listening."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False


def test_public_api(session: requests.Session) -> Dict[str, Any]:
    """Demonstrates fetching and inspecting a REST API response."""
    url = "https://httpbin.org/get"
    headers = {"User-Agent": "DevOps-API-Tester/1.0"}

    try:
        response = session.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        return {
            "status_code": response.status_code,
            "origin_ip": response.json().get("origin", "unknown"),
            "headers_sent": response.json().get("headers", {})
        }
    except requests.RequestException as e:
        return {"error": str(e)}


def main():
    print("==================================================")
    print("      DEVOPS NETWORK & REST API DIAGNOSTICS      ")
    print("==================================================")

    # 1. TCP Port Probing
    dns_host = "8.8.8.8"
    dns_port = 53
    is_dns_open = probe_tcp_socket(dns_host, dns_port)
    print(f"\n1. TCP Port Check: {dns_host}:{dns_port} -> {'[OPEN]' if is_dns_open else '[CLOSED]'}")

    # 2. REST API Request
    print("\n2. Querying REST API endpoint with connection pooling...")
    session = create_resilient_session()
    api_result = test_public_api(session)

    if "error" in api_result:
        print(f"  [API ERROR] {api_result['error']}")
    else:
        print(f"  [OK] Status Code: {api_result['status_code']}")
        print(f"  [OK] Caller Outbound IP: {api_result['origin_ip']}")
        print(f"  [OK] Headers Echoed: User-Agent={api_result['headers_sent'].get('User-Agent')}")

    print("\n[SUCCESS] Network probing finished successfully.")


if __name__ == "__main__":
    main()

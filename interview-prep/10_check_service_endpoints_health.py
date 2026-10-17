#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 10: Concurrent Service Health Checker with Latency Tracking
================================================================================
Problem Statement:
Write a Python function `sweep_service_health(endpoints, timeout=3.0, max_threads=5)`
that:
  1. Concurrently probes a list of HTTP endpoints using `requests` and
     `concurrent.futures.ThreadPoolExecutor`.
  2. For each endpoint:
     - Measures round-trip HTTP response latency in milliseconds (ms).
     - Checks if the returned status code matches the expected status code.
     - Captures exceptions (timeout, DNS resolution failure, connection refused)
       without crashing other worker threads.
  3. Computes the overall system Availability Percentage:
     Availability = (Healthy Endpoints / Total Endpoints) * 100
  4. Returns a consolidated summary dictionary.

Constraints:
  - Must not block sequentially on slow or hanging endpoints (enforce strict timeout).
  - Thread safety when aggregating results.
================================================================================
"""

import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any


def probe_single_endpoint(endpoint: Dict[str, Any], timeout: float = 3.0) -> Dict[str, Any]:
    """Probes a single endpoint and measures latency."""
    name = endpoint.get("name", endpoint["url"])
    url = endpoint["url"]
    expected_code = endpoint.get("expected_code", 200)

    start_time = time.perf_counter()
    try:
        response = requests.get(url, timeout=timeout)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        is_healthy = (response.status_code == expected_code)

        return {
            "name": name,
            "url": url,
            "healthy": is_healthy,
            "status_code": response.status_code,
            "expected_code": expected_code,
            "latency_ms": duration_ms,
            "error": None if is_healthy else f"Unexpected HTTP status: {response.status_code}"
        }

    except requests.exceptions.Timeout:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "name": name,
            "url": url,
            "healthy": False,
            "status_code": None,
            "latency_ms": duration_ms,
            "error": f"Request timed out after {timeout}s"
        }
    except requests.exceptions.RequestException as e:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "name": name,
            "url": url,
            "healthy": False,
            "status_code": None,
            "latency_ms": duration_ms,
            "error": str(e)
        }


def sweep_service_health(
    endpoints: List[Dict[str, Any]],
    timeout: float = 3.0,
    max_threads: int = 5
) -> Dict[str, Any]:
    """Concurrently checks a list of service endpoints."""
    results = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_map = {
            executor.submit(probe_single_endpoint, ep, timeout): ep
            for ep in endpoints
        }
        for future in as_completed(future_map):
            results.append(future.result())

    healthy_count = sum(1 for r in results if r["healthy"])
    total_count = len(results)
    availability_pct = (healthy_count / total_count * 100) if total_count > 0 else 0.0

    return {
        "total_probed": total_count,
        "healthy_count": healthy_count,
        "unhealthy_count": total_count - healthy_count,
        "availability_percent": round(availability_pct, 2),
        "results": results
    }


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    test_endpoints = [
        {"name": "GitHub API", "url": "https://api.github.com", "expected_code": 200},
        {"name": "HTTPBin Status 200", "url": "https://httpbin.org/status/200", "expected_code": 200},
        {"name": "HTTPBin Status 404 Expected", "url": "https://httpbin.org/status/404", "expected_code": 404},
        {"name": "Non-Existent Endpoint", "url": "https://invalid-non-existent-subdomain-12345.com", "expected_code": 200}
    ]

    print("--- [Question 10 Test: Concurrent Health Sweep] ---")
    report = sweep_service_health(test_endpoints, timeout=3.0)

    print(f"Overall Availability: {report['availability_percent']}% ({report['healthy_count']}/{report['total_probed']} healthy)")
    print(f"\n{'Service Name':<25} | {'Latency':<10} | {'Status Code':<12} | {'Health':<9} | {'Notes'}")
    print("-" * 80)
    for r in report["results"]:
        status_str = f"HTTP {r['status_code']}" if r['status_code'] else "N/A"
        health_flag = "[HEALTHY]" if r['healthy'] else "[DOWN]   "
        notes = r['error'] or "OK"
        print(f"{r['name']:<25} | {r['latency_ms']:>6.1f} ms  | {status_str:<12} | {health_flag} | {notes[:25]}")

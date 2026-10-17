# 08 - Networking & REST API Automation for DevOps

---

## 1. What It Is
Networking and API automation involves interacting programmatically across network boundaries:
- **HTTP/HTTPS REST Clients (`requests`, `httpx`)**: Performing standard HTTP verbs (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`) with authentication, JSON payloads, and custom headers.
- **Resilient HTTP Sessions (`requests.Session`, `HTTPAdapter`, `urllib3.util.Retry`)**: Connection pooling and automated retries with exponential backoff on transient errors (HTTP 429 Too Many Requests, 502 Bad Gateway, 503 Service Unavailable).
- **Socket Operations (`socket` module)**: Low-level TCP/UDP connection probing, port scanning, and DNS lookups.
- **Webhooks & Notification Bridges**: Transmitting real-time CI/CD and monitoring alerts to Slack, Microsoft Teams, PagerDuty, or Discord.

---

## 2. What Is the Use of It in DevOps?
Modern cloud infrastructure is controlled entirely by RESTful APIs:
1. **CI/CD Health Check Verification**: Polling a `/healthz` or `/actuator/health` endpoint after deploying a new container before switching traffic in a load balancer.
2. **Third-Party DevOps API Integration**: Triggering Jenkins jobs, creating GitHub releases, creating Jira tickets on deployment failure, and querying Prometheus for SLO metrics.
3. **Network Connectivity & Firewall Validation**: Testing whether an application pod can reach an RDS database on port 5432 or an external gateway through a NAT gateway.
4. **ChatOps & Alert Dispatching**: Sending rich JSON cards to Slack or MS Teams channels when pipelines fail or SSL certificates approach expiration.

---

## 3. How to Use It

### Production Pattern: Requests Session with Automated Retries
Never use standalone `requests.get()` in production without timeouts and retries:
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

def get_resilient_session(retries: int = 3, backoff_factor: float = 0.5) -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
```

### TCP Port Check via Sockets
```python
import socket

def is_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False
```

---

## 4. How to Implement It: Step-by-Step

### Step A: Sending Slack Webhook Alerts
```python
import requests

def send_slack_alert(webhook_url: str, title: str, message: str, color: str = "#FF0000"):
    payload = {
        "attachments": [
            {
                "color": color,
                "title": title,
                "text": message,
                "footer": "Python DevOps Automation Engine"
            }
        ]
    }
    response = requests.post(webhook_url, json=payload, timeout=5)
    response.raise_for_status()
```

### Step B: Safe API Authentication with Headers
```python
import os
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "DevOps-Automation-Bot/1.0"
}

resp = requests.get("https://api.github.com/user/repos", headers=headers, timeout=10)
if resp.status_code == 200:
    repos = resp.json()
```

---

## 5. DevOps Hands-On Example: Infrastructure Health Checker & Webhook Notifier

```python
#!/usr/bin/env python3
"""
Infrastructure Health Checker & Port Connectivity Scanner.
Probes HTTP endpoints, tests TCP port reachability, and builds alert payloads.
"""
import sys
import socket
import requests
from typing import List, Dict, Any

SERVICES_TO_MONITOR = [
    {"name": "Public DNS (Google)", "type": "tcp", "host": "8.8.8.8", "port": 53},
    {"name": "GitHub Web API", "type": "http", "url": "https://api.github.com", "expected_code": 200},
    {"name": "HTTPBin Status", "type": "http", "url": "https://httpbin.org/status/200", "expected_code": 200}
]

def check_tcp_port(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False

def check_http_endpoint(url: str, expected_code: int = 200, timeout: float = 3.0) -> bool:
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == expected_code
    except requests.RequestException:
        return False

def run_health_sweep(services: List[Dict[str, Any]]):
    print("=== Starting Infrastructure Connectivity Sweep ===")
    all_healthy = True

    for svc in services:
        name = svc["name"]
        svc_type = svc["type"]

        if svc_type == "tcp":
            host, port = svc["host"], svc["port"]
            healthy = check_tcp_port(host, port)
            status_str = "[OK] REACHABLE" if healthy else "[FAIL] UNREACHABLE"
            print(f"  TCP  | {name:<22} -> {host}:{port} -> {status_str}")
        elif svc_type == "http":
            url = svc["url"]
            healthy = check_http_endpoint(url, svc.get("expected_code", 200))
            status_str = "[OK] HEALTHY" if healthy else "[FAIL] DOWN"
            print(f"  HTTP | {name:<22} -> {url} -> {status_str}")

        if not healthy:
            all_healthy = False

    return all_healthy

def main():
    healthy = run_health_sweep(SERVICES_TO_MONITOR)
    print("==================================================")
    if healthy:
        print("[SUCCESS] All monitored network endpoints are healthy.")
        sys.exit(0)
    else:
        print("[WARNING] One or more endpoints failed health verification.")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 6. Interview & Real-World Questions

### Q1: Why must you ALWAYS specify a `timeout` parameter in `requests` calls in production scripts?
**Answer:**
By default, the `requests` library does **not** specify a timeout. If a remote server accepts the TCP handshake but hangs indefinitely without closing the connection or transmitting data, your Python thread or CI runner will block forever. This can cause entire CI/CD pipelines to hang until the overall runner timeout expires hours later.
*Rule*: Always specify `timeout=(connect_timeout, read_timeout)` or `timeout=5`.

### Q2: What is the benefit of `requests.Session()` over calling `requests.get()` repeatedly?
**Answer:**
1. **Connection Pooling**: Reuses underlying TCP connections (HTTP Keep-Alive), eliminating repeated TCP and TLS handshakes and drastically cutting latency.
2. **Cookie & Header Persistence**: Authentication headers and cookies persist across calls.
3. **Transport Adapters**: Allows attaching retry logic, rate limiters, or custom SSL contexts to all requests through that session.

### Q3: What is the difference between `response.json()` and `json.loads(response.text)`?
**Answer:**
`response.json()` is a built-in helper method that decodes the HTTP response content using the detected charset encoding and serializes it to a Python object in one call. It raises `requests.exceptions.JSONDecodeError` if the response body is not valid JSON (e.g., when a load balancer returns an HTML error page).

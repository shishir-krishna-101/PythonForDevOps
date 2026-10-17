# Real-World Script 04: Production Access Log Anomaly & Threat Detector

---

## 1. Real-World DevOps Problem Statement
Web servers, API gateways, and ingress controllers (Nginx, Traefik, HAProxy, Envoy) process billions of requests daily:
1. **Silent Upstream Outages**: When a microservice backend fails, reverse proxies return HTTP 502 (Bad Gateway) or 504 (Gateway Timeout). Unless aggregated in real time, these errors degrade user experience before synthetic probes notice.
2. **Malicious Reconnaissance & Vulnerability Probes**: Automated bots continually scan production URLs for common misconfigurations: `.env` files, `.git/config`, `wp-login.php`, path traversal `../../etc/passwd`, and SQL injection.
3. **Brute Force & Credential Stuffing**: Attackers bombard authentication endpoints (`/api/v1/login`) with credential stuffing attacks, exhausting backend connection pools.
4. **Automated Mitigation Need**: DevOps teams need scripts that not only identify threats but also immediately generate or apply mitigation rules (e.g. `iptables` drop commands or AWS WAF IP sets).

---

## 2. Complete Code Implementation

See the full script in [log_anomaly_detector.py](file:///c:/Users/Demon%20Slayer/Documents/PythonForDevOps/14-real-world-devops-scripts/04-production-log-anomaly-detector/log_anomaly_detector.py).

---

## 3. Deep-Dive Code Explanation: What Is It Doing?

### A. Memory-Safe Generator Streaming
```python
def file_line_generator():
    with open(args.file, "r", encoding="utf-8") as f:
        for line in f:
            yield line
```
- Uses Python **Generators** (`yield`) to stream log lines lazily.
- Keeps memory footprint strictly constant ($O(1)$) even when analyzing 50 GB log files.

### B. Pre-Compiled Regex with Named Captures
```python
LOG_PATTERN = re.compile(
    r'^(?P<client_ip>\S+)\s+\S+\s+\S+\s+\[(?P<timestamp>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+(?P<uri>\S+)\s+[A-Z0-9./]+"\s+'
    r'(?P<status>\d{3})\s+(?P<bytes>\d+)'
)
```
- Matches standard Combined Log Format (CLF).
- Groups `client_ip`, `timestamp`, `method`, `uri`, and `status` cleanly for instant dictionary extraction via `match.groupdict()`.

### C. Signature-Based Threat Identification
```python
SUSPICIOUS_SIGNATURES = [
    r'\.\./',         # Path traversal
    r'/etc/passwd',   # Local file inclusion
    r'wp-login\.php', # Admin brute force
    r'\.env',         # Credential exposure
]
```
- Scans request URIs against pre-compiled regex signatures.
- Flags suspicious probing bots and isolates offending client IP addresses.

### D. SLA Error-Rate Calculation
- Aggregates status codes into high-performance `collections.Counter`.
- Computes percentage of HTTP 5xx responses: $\text{ErrorRate} = \frac{\sum 5xx}{\text{Total Requests}} \times 100\%$.
- Triggers critical alerts when error rate exceeds the 5% SLA threshold.

### E. Automated Security Mitigation Rule Generation
- Generates precise Linux `iptables` commands to drop packets from attacking IPs at the host kernel layer.
- Generates AWS WAF CLI commands (`aws wafv2 update-ip-set`) to block attackers at the CloudFront/ALB edge.

---

## 4. Libraries Used & Why

| Library | Why It Was Chosen |
|:---|:---|
| `re` | Standard library regular expressions for pattern matching and log extraction. |
| `collections.Counter` | High-performance C-optimized hash map for real-time frequency counting of status codes and IP requests. |
| `argparse` | CLI arguments to switch between live files and demonstration streams. |
| `logging` | Structured JSON log generation for automated pipelines. |

---

## 5. Real-World Problems, Edge Cases & Code Fixes

### Problem 1: Out-Of-Memory (OOM) Crashes on Giant Log Dumps
- **Real-World Incident**: An engineer runs `lines = f.readlines()` on a 20 GB `/var/log/nginx/access.log`. The Python process consumes all available RAM and is terminated by the Linux OOM killer.
- **The Code Fix**: The script uses a generator function that reads line-by-line using Python's buffered file iterator, consuming only a few megabytes of RAM regardless of file size.

### Problem 2: Client IP Behind Reverse Proxies (Cloudflare / AWS ALB)
- **Real-World Incident**: When running behind a reverse proxy or CDN, the first field in the log line is the proxy IP (e.g. Cloudflare IP), causing the script to mistakenly generate block rules for Cloudflare!
- **The Code Fix**: Inspect the `X-Forwarded-For` header or `CF-Connecting-IP` field in the log format configuration when proxies are present, extracting the true client IP.

### Problem 3: Malformed or Incomplete Log Lines
- **Real-World Incident**: Network disconnects or log rotation can produce truncated lines that fail regex matching, throwing exceptions.
- **The Code Fix**: The code tests `if not match: continue`, gracefully skipping unparseable lines while maintaining continuous analysis of valid records.

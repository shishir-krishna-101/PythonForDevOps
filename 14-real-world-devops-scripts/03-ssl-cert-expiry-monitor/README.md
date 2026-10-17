# Real-World Script 03: SSL/TLS Certificate Expiration Monitor & Prometheus Exporter

---

## 1. Real-World DevOps Problem Statement
Every company has suffered an unexpected outage due to an expired SSL/TLS certificate:
1. **The Silent Outage**: Certificate expiration dates are easily forgotten. When an ingress TLS certificate expires, browsers immediately block all client traffic with `NET::ERR_CERT_DATE_INVALID`, dropping revenue and breaching customer SLAs.
2. **Multi-Domain & CDN Complexity**: In microservice environments with hundreds of subdomains, Cloudflare endpoints, API gateways, and AWS ALBs, manual calendar tracking is impossible.
3. **Automated Monitoring Need**: DevOps teams need a lightweight automated tool that can run as a daily Kubernetes CronJob or export Prometheus metrics directly to Grafana dashboards.

---

## 2. Complete Code Implementation

See the full script in [ssl_cert_expiration_checker.py](file:///c:/Users/Demon%20Slayer/Documents/PythonForDevOps/14-real-world-devops-scripts/03-ssl-cert-expiry-monitor/ssl_cert_expiration_checker.py).

---

## 3. Deep-Dive Code Explanation: What Is It Doing?

### A. Server Name Indication (SNI) Handling
```python
context = ssl.create_default_context()
with socket.create_connection((hostname, port), timeout=timeout) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        cert = ssock.getpeercert()
```
- Creates an SSL context with the operating system's root CA certificates.
- **Server Name Indication (SNI)** is strictly enforced by passing `server_hostname=hostname`. Without SNI, cloud load balancers and CDNs (Cloudflare, AWS CloudFront) hosting multiple domains on a shared IP address will return the default fallback certificate instead of the target certificate.

### B. Accurate Date Parsing & Day Calculation
```python
expiry_date = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
now = datetime.now(timezone.utc)
days_remaining = (expiry_date - now).days
```
- Parses the X.509 date string (`Oct 17 12:00:00 2026 GMT`) into a timezone-aware UTC datetime.
- Calculates remaining integer days until expiration.

### C. Multi-Tier Severity Classification
- **`HEALTHY`**: $> 30$ days remaining.
- **`WARNING`**: $\le 30$ days remaining (trigger notification to renewal team or Cert-Manager).
- **`CRITICAL`**: $\le 14$ days remaining (escalate high-priority page to on-call engineer).
- **`EXPIRED`**: $\le 0$ days remaining (immediate outage).

### D. Native Prometheus Gauge Metric Generation
- Includes `--prom-format` flag to export metrics conforming to standard Prometheus text exposition format:
```text
# HELP ssl_certificate_expiry_days Days remaining until certificate expiration
# TYPE ssl_certificate_expiry_days gauge
ssl_certificate_expiry_days{domain="google.com",issuer="Google Trust Services"} 65
```

---

## 4. Libraries Used & Why

| Library | Why It Was Chosen |
|:---|:---|
| `ssl` | Python standard library cryptographic module. Provides low-level OpenSSL bindings to inspect X.509 certificates without third-party dependencies. |
| `socket` | Python standard library networking module. Provides raw TCP socket connections with millisecond-level timeout controls. |
| `datetime` | Timezone-aware timestamp arithmetic to compute exact expiration horizons. |
| `argparse` | Allows passing custom target arrays and formatting flags from CI pipelines. |

---

## 5. Real-World Problems, Edge Cases & Code Fixes

### Problem 1: CDN / Virtual Host Returning Wrong Certificate Without SNI
- **Real-World Incident**: Connecting directly via raw IP or without SNI returns an invalid wildcard cert (e.g. `*.cloudflare.com`), causing the auditor to falsely report expired certificates for customer domains.
- **The Code Fix**: Wrapped the TCP socket with `context.wrap_socket(sock, server_hostname=hostname)` to ensure the TLS client hello packet includes the SNI extension header.

### Problem 2: Hangs on Firewalled or Non-Responsive Ports
- **Real-World Incident**: If a target endpoint drops TCP packets (e.g., closed firewall port), a naive connection will hang for minutes, stalling the automated pipeline.
- **The Code Fix**: Configured strict, granular timeouts on `socket.create_connection((hostname, port), timeout=timeout)`.

### Problem 3: Parsing Complex Multi-Level Issuer Dictionaries
- **Real-World Incident**: X.509 issuer tuples have inconsistent internal structures depending on whether the Certificate Authority is Let's Encrypt, DigiCert, or internal Vault PKI.
- **The Code Fix**: Implemented safe dictionary comprehension `dict(x[0] for x in cert.get("issuer", ()))` with fallback lookups for both `organizationName` and `commonName`.

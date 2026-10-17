#!/usr/bin/env python3
"""
Project 03: SSL/TLS Certificate Expiration Monitor & Prometheus Exporter
Location: 14-real-world-devops-scripts/03-ssl-cert-expiry-monitor/ssl_cert_expiration_checker.py

Purpose:
Connects to a list of target domains over TLS/SSL with Server Name Indication (SNI),
extracts X.509 certificate expiration dates and issuers, calculates remaining validity days,
and flags certificates requiring renewal before causing production downtime.
"""

import ssl
import socket
import sys
import argparse
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "ssl_monitor", "message": "%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%SZ'
)
logger = logging.getLogger("ssl_monitor")

DEFAULT_TARGETS = [
    "google.com:443",
    "github.com:443",
    "cloudflare.com:443",
    "httpbin.org:443"
]

CRITICAL_DAYS_THRESHOLD = 14
WARNING_DAYS_THRESHOLD = 30


def parse_endpoint(endpoint_str: str) -> Tuple[str, int]:
    """Splits 'domain.com:443' or 'domain.com' into (host, port)."""
    parts = endpoint_str.strip().split(":")
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 443
    return host, port


def get_certificate_details(hostname: str, port: int = 443, timeout: float = 3.0) -> Dict[str, Any]:
    """
    Connects to hostname:port over SSL using SNI and returns certificate metadata.
    """
    context = ssl.create_default_context()
    # Allow inspecting expired/untrusted certs for diagnostic auditing if necessary
    # context.check_hostname = False
    # context.verify_mode = ssl.CERT_NONE

    result = {
        "host": hostname,
        "port": port,
        "status": "UNKNOWN",
        "days_left": None,
        "expires_at": None,
        "issuer": "Unknown",
        "error": None
    }

    try:
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            # server_hostname enables Server Name Indication (SNI)
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                if not cert:
                    result["status"] = "ERROR"
                    result["error"] = "No peer certificate returned."
                    return result

                # Parse notAfter date string: e.g. 'Oct 17 12:00:00 2026 GMT'
                expiry_str = cert["notAfter"]
                expiry_date = datetime.strptime(expiry_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)

                days_remaining = (expiry_date - now).days
                result["days_left"] = days_remaining
                result["expires_at"] = expiry_date.strftime("%Y-%m-%d %H:%M:%S UTC")

                # Parse Issuer Organization
                issuer_dict = dict(x[0] for x in cert.get("issuer", ()))
                result["issuer"] = issuer_dict.get("organizationName", issuer_dict.get("commonName", "Unknown Issuer"))

                # Threshold categorization
                if days_remaining <= 0:
                    result["status"] = "EXPIRED"
                elif days_remaining <= CRITICAL_DAYS_THRESHOLD:
                    result["status"] = "CRITICAL"
                elif days_remaining <= WARNING_DAYS_THRESHOLD:
                    result["status"] = "WARNING"
                else:
                    result["status"] = "HEALTHY"

    except socket.timeout:
        result["status"] = "TIMEOUT"
        result["error"] = f"TCP/TLS connection timed out after {timeout}s"
    except ssl.SSLCertVerificationError as e:
        result["status"] = "CERT_VERIFY_FAILED"
        result["error"] = f"SSL Certificate Verification Failed: {e.verify_message}"
    except ConnectionRefusedError:
        result["status"] = "CONN_REFUSED"
        result["error"] = f"Connection refused on port {port}"
    except Exception as e:
        result["status"] = "ERROR"
        result["error"] = str(e)

    return result


def main():
    parser = argparse.ArgumentParser(description="Multi-Domain SSL/TLS Expiration Watcher")
    parser.add_argument("--targets", nargs="+", default=DEFAULT_TARGETS, help="List of host:port targets")
    parser.add_argument("--timeout", type=float, default=3.0, help="Socket timeout in seconds")
    parser.add_argument("--prom-format", action="store_true", help="Output Prometheus metrics format")
    args = parser.parse_args()

    results = []
    print("================================================================================")
    print("                  SSL/TLS CERTIFICATE EXPIRATION AUDITOR                        ")
    print("================================================================================")

    for target in args.targets:
        host, port = parse_endpoint(target)
        details = get_certificate_details(host, port, timeout=args.timeout)
        results.append(details)

        if details["status"] == "HEALTHY":
            status_tag = "[OK]      "
        elif details["status"] == "WARNING":
            status_tag = "[WARNING] "
        elif details["status"] in ["CRITICAL", "EXPIRED"]:
            status_tag = "[CRITICAL]"
        else:
            status_tag = "[FAIL]    "

        if details["days_left"] is not None:
            print(f"{status_tag} {details['host']:<25} | Days Left: {details['days_left']:>4} | Expires: {details['expires_at']} | Issuer: {details['issuer']}")
        else:
            print(f"{status_tag} {details['host']:<25} | ERROR: {details['error']}")

    print("================================================================================")

    # Prometheus Exporter Format output
    if args.prom_format:
        print("\n# HELP ssl_certificate_expiry_days Days remaining until certificate expiration")
        print("# TYPE ssl_certificate_expiry_days gauge")
        for r in results:
            if r["days_left"] is not None:
                print(f'ssl_certificate_expiry_days{{domain="{r["host"]}",issuer="{r["issuer"]}"}} {r["days_left"]}')

    # Exit with code 1 if any certificate is CRITICAL or EXPIRED
    has_critical = any(r["status"] in ["CRITICAL", "EXPIRED"] for r in results)
    if has_critical:
        logger.error("One or more certificates are expired or critically close to expiration!")
        sys.exit(1)

    print("[SUCCESS] All certificate expiration checks evaluated.")


if __name__ == "__main__":
    main()

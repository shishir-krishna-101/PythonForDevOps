#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 03: Mask Sensitive Data and Secrets in Log Streams
================================================================================
Problem Statement:
In compliance with SOC2, GDPR, and PCI-DSS, sensitive credentials must never be
forwarded to third-party log ingestion services (e.g., Datadog, CloudWatch).

Write a Python function `sanitize_log_line(log_line)` that scrubs:
  1. Password / Secret query strings or key-value assignments:
     e.g., `password=Secret123`, `"password": "mypass"`, `db_pass: mypass` -> `password=***REDACTED***`
  2. Bearer Authentication Tokens:
     e.g., `Bearer eyJhbGciOi...` -> `Bearer ***REDACTED***`
  3. Credit Card Numbers:
     e.g., standard 16-digit cards `4111-2222-3333-4444` or `4111222233334444` -> `***REDACTED_CC***`
  4. AWS Secret Access Keys:
     e.g., 40-character base64-like alphanumeric strings following `aws_secret_access_key` -> `***REDACTED_KEY***`

Constraints:
  - Must preserve surrounding log context, timestamps, and formatting intact.
  - Case-insensitive matching for keys like 'Password', 'SECRET', 'ApiKey'.
================================================================================
"""

import re
from typing import List


# Compiled redaction patterns
REDACTION_RULES = [
    # 1. Passwords / Secrets / API Keys in key=value, key: value, or "key": "value"
    (
        re.compile(r'(?i)(password|secret|api[_-]?key|access[_-]?token|token)\s*([:=]|:=)\s*["\']?([^"\'\s&]+)["\']?'),
        r'\1\2"***REDACTED***"'
    ),
    # 2. Authorization Bearer tokens
    (
        re.compile(r'(?i)(Authorization:\s*Bearer\s+)[^\s"\'&]+'),
        r'\1***REDACTED***'
    ),
    # 3. Credit Card Numbers (13 to 16 digits, with optional hyphens/spaces)
    (
        re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
        r'***REDACTED_CC***'
    ),
    # 4. AWS Secret Access Key (typically 40 characters)
    (
        re.compile(r'(?i)(aws_secret_access_key\s*=\s*)[A-Za-z0-9/+=]{40}'),
        r'\1***REDACTED_AWS_SECRET***'
    )
]


def sanitize_log_line(line: str) -> str:
    """
    Applies regex redaction rules to strip confidential data from a log string.
    """
    sanitized = line
    for pattern, replacement in REDACTION_RULES:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


def sanitize_log_stream(lines: List[str]) -> List[str]:
    """Processes a stream/batch of log lines."""
    return [sanitize_log_line(line) for line in lines]


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    raw_logs = [
        '2026-10-17 12:00:01 INFO [auth-svc] User login attempt: username=john_doe password=SuperSecurePassword!99',
        '2026-10-17 12:00:02 DEBUG [http-client] Request headers: {"Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}',
        '2026-10-17 12:00:03 INFO [billing] Payment processed for card: 4111-2222-3333-4444 amount=$199.99',
        '2026-10-17 12:00:04 ERROR [terraform] AWS config error: aws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY region=us-east-1',
        '2026-10-17 12:00:05 INFO [api] Normal non-sensitive event: path=/v1/products status=200'
    ]

    print("--- [Question 03 Test Results: Secret Redaction] ---")
    for original in raw_logs:
        cleaned = sanitize_log_line(original)
        print(f"\n[ORIGINAL]: {original}")
        print(f"[SCRUBBED]: {cleaned}")

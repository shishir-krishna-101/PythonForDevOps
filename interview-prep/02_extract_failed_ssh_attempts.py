#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 02: Detect Brute Force SSH Attacks from auth.log
================================================================================
Problem Statement:
As an SRE/Security Engineer, you need to analyze `/var/log/auth.log` to detect
brute-force attacks against SSH servers.

Write a Python function `detect_ssh_brute_force(log_lines, failure_threshold=3)`
that:
  1. Identifies failed login attempts for both existing users and invalid users.
     Example patterns:
       "Failed password for root from 192.168.1.50 port 54321 ssh2"
       "Failed password for invalid user admin from 198.51.100.22 port 44120 ssh2"
  2. Aggregates failed attempts per IP address, along with the list of distinct
     usernames targeted by that IP.
  3. Returns a dictionary of IP addresses whose total failed attempts meet or
     exceed `failure_threshold`, sorted descending by attempt count.
  4. Generates an automated iptables drop command for each flagged attacker IP.

Constraints:
  - Must not match successful logins (e.g. "Accepted password for ...").
  - Handle multiple spaces or varying port numbers gracefully.
================================================================================
"""

import re
from collections import defaultdict
from typing import List, Dict, Any, Set


# Regex to match failed password attempts
FAILED_SSH_REGEX = re.compile(
    r'Failed password for (?:invalid user\s+)?(?P<user>\S+)\s+from\s+(?P<ip>\S+)'
)


def detect_ssh_brute_force(log_lines: List[str], failure_threshold: int = 3) -> Dict[str, Any]:
    """
    Parses auth.log lines and returns attacker telemetry with mitigation commands.
    """
    attempts_per_ip = defaultdict(int)
    users_targeted_per_ip = defaultdict(set)

    for line in log_lines:
        match = FAILED_SSH_REGEX.search(line)
        if match:
            user = match.group("user")
            ip = match.group("ip")
            attempts_per_ip[ip] += 1
            users_targeted_per_ip[ip].add(user)

    # Filter by threshold
    attackers = {}
    for ip, count in attempts_per_ip.items():
        if count >= failure_threshold:
            attackers[ip] = {
                "failed_attempts": count,
                "targeted_users": sorted(list(users_targeted_per_ip[ip])),
                "iptables_rule": f"sudo iptables -A INPUT -s {ip} -p tcp --dport 22 -j DROP"
            }

    # Sort descending by failed attempts
    sorted_attackers = dict(
        sorted(attackers.items(), key=lambda item: item[1]["failed_attempts"], reverse=True)
    )

    return sorted_attackers


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    sample_auth_logs = [
        "Oct 17 12:00:01 srv sshd[1001]: Failed password for invalid user admin from 198.51.100.22 port 51234 ssh2",
        "Oct 17 12:00:03 srv sshd[1002]: Failed password for invalid user test from 198.51.100.22 port 51235 ssh2",
        "Oct 17 12:00:05 srv sshd[1003]: Failed password for root from 198.51.100.22 port 51236 ssh2",
        "Oct 17 12:00:07 srv sshd[1004]: Failed password for root from 198.51.100.22 port 51237 ssh2",
        "Oct 17 12:00:10 srv sshd[1005]: Accepted password for ubuntu from 10.0.1.50 port 45123 ssh2",
        "Oct 17 12:00:12 srv sshd[1006]: Failed password for ubuntu from 203.0.113.88 port 39812 ssh2",
        "Oct 17 12:00:14 srv sshd[1007]: Failed password for postgres from 203.0.113.88 port 39813 ssh2",
        "Oct 17 12:00:16 srv sshd[1008]: Failed password for invalid user guest from 203.0.113.88 port 39814 ssh2"
    ]

    attackers = detect_ssh_brute_force(sample_auth_logs, failure_threshold=3)

    print("--- [Question 02 Test Results] ---")
    print(f"Attackers Detected (Threshold >= 3): {len(attackers)}")
    for ip, details in attackers.items():
        print(f"\nAttacker IP: {ip}")
        print(f"  * Failed Attempts : {details['failed_attempts']}")
        print(f"  * Targeted Users  : {', '.join(details['targeted_users'])}")
        print(f"  * Mitigation Rule : {details['iptables_rule']}")

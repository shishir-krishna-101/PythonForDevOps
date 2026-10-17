#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 18: CIDR Subnet Matcher & IP Security Filter
================================================================================
Problem Statement:
Firewalls, API Gateways, and WAF rules frequently check whether an incoming
client IP address falls within an approved corporate CIDR subnet block
(e.g., VPN subnet, AWS VPC CIDR).

Write two Python functions:
  1. `is_ip_in_subnets(client_ip, allowed_cidrs)`:
     Uses Python's standard `ipaddress` module to determine if an IP belongs
     to any of the listed subnets.
  2. `is_ip_in_cidr_bitwise(client_ip, cidr)`:
     Implements the subnet membership check manually using low-level integer
     bitwise arithmetic:
       ip_int & mask == network_int & mask
     (A classic Google/AWS system networking interview question!)
  3. Validates whether input strings are syntactically valid IPv4/IPv6 addresses.

Constraints:
  - O(1) time per CIDR check.
  - Handle invalid IPs without crashing (return False or raise descriptive error).
================================================================================
"""

import ipaddress
from typing import List, Tuple


def is_ip_in_subnets(client_ip: str, allowed_cidrs: List[str]) -> bool:
    """
    Standard library approach using `ipaddress`.
    """
    try:
        ip_obj = ipaddress.ip_address(client_ip.strip())
    except ValueError:
        return False

    for cidr in allowed_cidrs:
        try:
            network_obj = ipaddress.ip_network(cidr.strip(), strict=False)
            if ip_obj in network_obj:
                return True
        except ValueError:
            continue

    return False


def ip_to_int(ip_str: str) -> int:
    """Converts a dotted decimal IPv4 string (e.g. '192.168.1.1') to a 32-bit integer."""
    octets = [int(o) for o in ip_str.split(".")]
    if len(octets) != 4 or any(o < 0 or o > 255 for o in octets):
        raise ValueError(f"Invalid IPv4: {ip_str}")
    return (octets[0] << 24) | (octets[1] << 16) | (octets[2] << 8) | octets[3]


def is_ip_in_cidr_bitwise(client_ip: str, cidr: str) -> bool:
    """
    Manual bitwise subnet membership calculation for IPv4:
    A client IP is in a subnet if:
      (client_ip_int & subnet_mask) == (network_prefix_int & subnet_mask)
    """
    try:
        network_str, prefix_len_str = cidr.strip().split("/")
        prefix_len = int(prefix_len_str)
        if prefix_len < 0 or prefix_len > 32:
            return False

        # Compute 32-bit subnet mask: e.g. /24 -> 24 ones followed by 8 zeros
        subnet_mask = (0xFFFFFFFF << (32 - prefix_len)) & 0xFFFFFFFF if prefix_len > 0 else 0

        client_int = ip_to_int(client_ip.strip())
        network_int = ip_to_int(network_str.strip())

        return (client_int & subnet_mask) == (network_int & subnet_mask)

    except (ValueError, IndexError):
        return False


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    approved_subnets = [
        "10.0.0.0/16",       # Internal VPC
        "192.168.1.0/24",     # Office LAN
        "203.0.113.128/28"    # External Partner Gateway
    ]

    test_ips = [
        ("10.0.5.24", True),
        ("10.1.0.1", False),
        ("192.168.1.105", True),
        ("192.168.2.1", False),
        ("203.0.113.130", True),
        ("203.0.113.200", False)
    ]

    print("--- [Question 18 Test: CIDR Subnet Validation] ---")
    for ip, expected in test_ips:
        std_match = is_ip_in_subnets(ip, approved_subnets)
        # Test bitwise on first matching or first cidr
        bitwise_match = any(is_ip_in_cidr_bitwise(ip, c) for c in approved_subnets)

        status_flag = "[PASS]" if (std_match == expected and bitwise_match == expected) else "[FAIL]"
        print(f"{status_flag} IP: {ip:<16} | Allowed? {std_match:<5} | Bitwise Match? {bitwise_match}")

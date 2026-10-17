#!/usr/bin/env python3
"""
02-data-structures-for-devops/inventory_manager.py

Demonstrates:
- Dynamic list filtering & comprehensions
- Tag dictionary normalization
- Set operations for infrastructure drift analysis
- Grouping servers by Region/AZ
"""

from typing import Dict, List, Set, Any
from collections import defaultdict


RAW_CLOUD_INSTANCES: List[Dict[str, Any]] = [
    {
        "instance_id": "i-098f6bcd4621d373c",
        "az": "us-east-1a",
        "private_ip": "10.0.1.25",
        "state": "running",
        "tags": [
            {"Key": "Environment", "Value": "Production"},
            {"Key": "Role", "Value": "PaymentGateway"},
            {"Key": "Owner", "Value": "FinTechOps"}
        ]
    },
    {
        "instance_id": "i-05a105e8b949eec1f",
        "az": "us-east-1b",
        "private_ip": "10.0.2.14",
        "state": "running",
        "tags": [
            {"Key": "Environment", "Value": "Production"},
            {"Key": "Role", "Value": "OrderProcessor"},
            {"Key": "Owner", "Value": "FinTechOps"}
        ]
    },
    {
        "instance_id": "i-0ad7924407b3f6883",
        "az": "us-east-1a",
        "private_ip": "10.0.1.99",
        "state": "stopped",
        "tags": [
            {"Key": "Environment", "Value": "Staging"},
            {"Key": "Role", "Value": "PaymentGateway"},
            {"Key": "Owner", "Value": "QA"}
        ]
    },
    {
        "instance_id": "i-0c8a6231d68370f1a",
        "az": "us-east-1c",
        "private_ip": "10.0.3.40",
        "state": "running",
        "tags": [
            {"Key": "Environment", "Value": "Production"},
            {"Key": "Role", "Value": "OrderProcessor"}
            # Notice 'Owner' tag is missing here
        ]
    }
]

EXPECTED_FIREWALL_SUBNET_IPS: Set[str] = {
    "10.0.1.25",
    "10.0.2.14",
    "10.0.3.40",
    "10.0.4.100" # New host anticipated
}


def normalize_tags(tag_list: List[Dict[str, str]]) -> Dict[str, str]:
    """Converts AWS-style [{'Key': 'K', 'Value': 'V'}] to a standard dict {'K': 'V'}."""
    return {tag["Key"]: tag["Value"] for tag in tag_list if "Key" in tag and "Value" in tag}


def audit_inventory(instances: List[Dict[str, Any]]):
    print("=== 1. Tag Compliance & Clean View ===")
    active_prod_ips: Set[str] = set()
    instances_by_az = defaultdict(list)

    for inst in instances:
        tags = normalize_tags(inst.get("tags", []))
        env = tags.get("Environment", "UNTAGGED")
        role = tags.get("Role", "UNKNOWN")
        owner = tags.get("Owner", "MISSING_OWNER_TAG")
        ip = inst.get("private_ip")

        # Group by AZ
        instances_by_az[inst.get("az", "unknown-az")].append(inst["instance_id"])

        print(f"Instance: {inst['instance_id']} | IP: {ip} | Env: {env} | Role: {role} | Owner: {owner}")

        if env.lower() == "production" and inst.get("state") == "running" and ip:
            active_prod_ips.add(ip)

    print("\n=== 2. High Availability Distribution (Instances per AZ) ===")
    for az, ids in instances_by_az.items():
        print(f"  AZ: {az} -> {len(ids)} instances ({', '.join(ids)})")

    print("\n=== 3. Firewall Whitelist Drift Detection ===")
    print(f"  Live Production IPs : {active_prod_ips}")
    print(f"  Allowed Subnet IPs  : {EXPECTED_FIREWALL_SUBNET_IPS}")

    unauthorized_live_ips = active_prod_ips - EXPECTED_FIREWALL_SUBNET_IPS
    stale_firewall_rules = EXPECTED_FIREWALL_SUBNET_IPS - active_prod_ips

    if unauthorized_live_ips:
        print(f"  [SECURITY ALERT] IPs running without firewall whitelist: {unauthorized_live_ips}")
    else:
        print("  [OK] No unauthorized live production IPs found.")

    if stale_firewall_rules:
        print(f"  [CLEANUP RECOMMENDED] Whitelisted IPs with no running instance: {stale_firewall_rules}")
    else:
        print("  [OK] No stale rules in firewall whitelist.")


if __name__ == "__main__":
    audit_inventory(RAW_CLOUD_INSTANCES)

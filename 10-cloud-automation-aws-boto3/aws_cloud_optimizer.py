#!/usr/bin/env python3
"""
10-cloud-automation-aws-boto3/aws_cloud_optimizer.py

Demonstrates:
- Initializing Boto3 EC2 client with custom botocore Config
- Safe credential checking without crashing
- Finding unattached EBS volumes (FinOps cost saving)
- Pagination patterns for multi-region inventory scans
"""

import sys
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Dict, Any


def get_ec2_client(region: str = "us-east-1") -> boto3.client:
    """Creates an EC2 client with automatic retry backoff configuration."""
    custom_config = Config(
        region_name=region,
        retries={
            'max_attempts': 5,
            'mode': 'standard'
        }
    )
    return boto3.client('ec2', config=custom_config)


def find_unattached_ebs_volumes(ec2_client) -> List[Dict[str, Any]]:
    """
    Identifies unattached EBS volumes (status == 'available') that accrue idle storage costs.
    """
    unattached = []
    try:
        paginator = ec2_client.get_paginator('describe_volumes')
        # Filter for volumes not attached to any EC2 instance
        filters = [{'Name': 'status', 'Values': ['available']}]
        
        for page in paginator.paginate(Filters=filters):
            for vol in page.get('Volumes', []):
                unattached.append({
                    "VolumeId": vol["VolumeId"],
                    "Size": vol["Size"], # in GiB
                    "VolumeType": vol["VolumeType"],
                    "CreateTime": str(vol["CreateTime"])
                })
    except (ClientError, NoCredentialsError) as e:
        print(f"[AWS API NOTICE] Could not query live AWS API: {e}")
        # Return mock data for demonstration if no AWS credentials are configured
        unattached = [
            {"VolumeId": "vol-0a1b2c3d4e5f0001", "Size": 100, "VolumeType": "gp3", "CreateTime": "2026-09-01"},
            {"VolumeId": "vol-0a1b2c3d4e5f0002", "Size": 500, "VolumeType": "io2", "CreateTime": "2026-08-15"}
        ]
    return unattached


def main():
    print("==================================================")
    print("       AWS FINOPS & CLOUD COST OPTIMIZER          ")
    print("==================================================")

    region = "us-east-1"
    print(f"Connecting to AWS EC2 in region: {region}...")
    ec2 = get_ec2_client(region)

    print("\nScanning for unattached EBS volumes...")
    volumes = find_unattached_ebs_volumes(ec2)

    total_wasted_gib = sum(v["Size"] for v in volumes)
    # Average gp3 cost ~$0.08 per GiB/month
    estimated_monthly_savings = total_wasted_gib * 0.08

    print(f"\nDiscovered {len(volumes)} unattached EBS volumes:")
    for v in volumes:
        print(f"  * Volume ID: {v['VolumeId']} | Size: {v['Size']:>4} GiB | Type: {v['VolumeType']}")

    print("\n--- FinOps Summary ---")
    print(f"  Total Wasted Storage    : {total_wasted_gib} GiB")
    print(f"  Estimated Monthly Waste : ${estimated_monthly_savings:.2f} USD")
    print("  Recommended Action      : Snapshot & delete unattached volumes.")

    print("\n[SUCCESS] Cloud optimizer analysis complete.")


if __name__ == "__main__":
    main()

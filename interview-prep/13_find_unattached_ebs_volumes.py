#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 13: AWS FinOps Unattached EBS Volume Auditor
================================================================================
Problem Statement:
Orphaned EBS volumes (status == 'available') remain after EC2 instances are
terminated, accruing monthly storage fees.

Write a Python function `audit_unattached_ebs_volumes(ec2_client, cost_per_gib=0.08)`
that:
  1. Uses Boto3 EC2 client paginators (`describe_volumes`) with server-side filters
     `status: available`.
  2. Aggregates:
     - List of volume IDs, sizes (GiB), creation dates, and volume types (gp2, gp3, io2).
     - Identifies volumes missing mandatory compliance tags (`Owner` or `Environment`).
     - Calculates total wasted storage in GiB.
     - Estimates monthly wasted cost ($).
  3. Supports graceful execution when running without live AWS credentials
     by returning structured mock data for local testing.

Constraints:
  - Must use Paginators to handle AWS accounts with > 1,000 volumes.
  - Safe error handling for `botocore.exceptions.ClientError`.
================================================================================
"""

from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


def audit_unattached_ebs_volumes(ec2_client=None, cost_per_gib: float = 0.08) -> Dict[str, Any]:
    """
    Audits unattached EBS volumes and calculates waste metrics.
    """
    unattached_volumes: List[Dict[str, Any]] = []
    missing_tag_volumes: List[str] = []

    if not BOTO3_AVAILABLE or not ec2_client:
        # Fallback simulated data for testing without live credentials
        unattached_volumes = [
            {"id": "vol-01", "size": 100, "type": "gp3", "created": "2026-08-01", "owner": "DataOps"},
            {"id": "vol-02", "size": 250, "type": "io2", "created": "2026-07-15", "owner": "MISSING"},
            {"id": "vol-03", "size": 50,  "type": "gp3", "created": "2026-09-10", "owner": "QA"}
        ]
        missing_tag_volumes = ["vol-02"]
    else:
        try:
            paginator = ec2_client.get_paginator('describe_volumes')
            # Server-side filter for volumes in 'available' status
            page_iterator = paginator.paginate(
                Filters=[{'Name': 'status', 'Values': ['available']}]
            )

            for page in page_iterator:
                for vol in page.get('Volumes', []):
                    vol_id = vol['VolumeId']
                    size = vol['Size']
                    vol_type = vol['VolumeType']
                    created = vol['CreateTime'].isoformat()

                    tags = {t['Key']: t['Value'] for t in vol.get('Tags', [])}
                    owner = tags.get('Owner', 'MISSING')

                    if owner == 'MISSING' or 'Environment' not in tags:
                        missing_tag_volumes.append(vol_id)

                    unattached_volumes.append({
                        "id": vol_id,
                        "size": size,
                        "type": vol_type,
                        "created": created,
                        "owner": owner
                    })

        except (ClientError, NoCredentialsError) as e:
            return {"error": f"AWS API invocation error: {e}"}

    total_gib = sum(v["size"] for v in unattached_volumes)
    monthly_cost = round(total_gib * cost_per_gib, 2)

    return {
        "unattached_count": len(unattached_volumes),
        "total_storage_gib": total_gib,
        "estimated_monthly_waste_usd": monthly_cost,
        "non_compliant_tag_count": len(missing_tag_volumes),
        "volumes": unattached_volumes
    }


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    report = audit_unattached_ebs_volumes()

    print("--- [Question 13 Test: AWS FinOps EBS Auditor] ---")
    print(f"Total Unattached Volumes : {report['unattached_count']}")
    print(f"Total Wasted Storage     : {report['total_storage_gib']} GiB")
    print(f"Projected Monthly Cost   : ${report['estimated_monthly_waste_usd']} USD")
    print(f"Non-compliant Tag Volumes: {report['non_compliant_tag_count']}")

    print("\nVolume Breakdown:")
    for v in report["volumes"]:
        print(f"  * {v['id']} ({v['size']:>3} GiB, {v['type']}) | Owner: {v['owner']}")

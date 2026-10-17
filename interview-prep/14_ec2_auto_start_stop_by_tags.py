#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 14: Automated EC2 Start/Stop Scheduler by Compliance Tags
================================================================================
Problem Statement:
To cut non-production AWS infrastructure costs by 65%, your team wants to
automatically shut down development and QA EC2 instances outside office hours
(e.g., 7 PM to 7 AM) and start them back up at 7 AM.

Write a Python function `manage_ec2_schedule(ec2_client, action="stop", target_env="dev")`
that:
  1. Filters EC2 instances with tags:
     - `Environment` matching `target_env` (case-insensitive)
     - `AutoSchedule` == `true`
  2. If `action == "stop"`, selects instances that are currently in the `running` state.
  3. If `action == "start"`, selects instances that are currently in the `stopped` state.
  4. Invokes `ec2.stop_instances` or `ec2.start_instances` on the filtered IDs.
  5. Provides dry-run capability and logs the affected instances.

Constraints:
  - Must never target production instances (`Environment=prod`).
  - Batch instance IDs together into a single API call to avoid API throttling.
================================================================================
"""

from typing import List, Dict, Any, Tuple

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


def manage_ec2_schedule(
    ec2_client=None,
    action: str = "stop",
    target_env: str = "dev",
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Automates start/stop operations on tagged EC2 instances.
    """
    if target_env.lower() in ["prod", "production"]:
        raise ValueError("Safety Guard: Scheduled start/stop cannot target production!")

    action = action.lower()
    if action not in ["start", "stop"]:
        raise ValueError(f"Invalid action '{action}'. Must be 'start' or 'stop'.")

    desired_current_state = "running" if action == "stop" else "stopped"

    # Simulated data fallback for local interview testing
    if not BOTO3_AVAILABLE or not ec2_client:
        mock_instances = [
            {"id": "i-01", "name": "dev-web-01", "env": "dev", "state": "running", "auto_schedule": "true"},
            {"id": "i-02", "name": "dev-db-01", "env": "dev", "state": "running", "auto_schedule": "true"},
            {"id": "i-03", "name": "qa-tester-01", "env": "qa", "state": "running", "auto_schedule": "false"}, # Excluded
            {"id": "i-04", "name": "prod-api-01", "env": "prod", "state": "running", "auto_schedule": "true"}  # Excluded
        ]

        target_ids = [
            inst["id"] for inst in mock_instances
            if inst["env"] == target_env
            and inst["state"] == desired_current_state
            and inst["auto_schedule"] == "true"
        ]

        return {
            "action": action,
            "target_env": target_env,
            "dry_run": dry_run,
            "target_instance_ids": target_ids,
            "count": len(target_ids),
            "simulated": True
        }

    # Live AWS API query using server-side filters
    filters = [
        {"Name": "instance-state-name", "Values": [desired_current_state]},
        {"Name": "tag:Environment", "Values": [target_env]},
        {"Name": "tag:AutoSchedule", "Values": ["true", "True", "TRUE"]}
    ]

    target_instance_ids = []
    try:
        paginator = ec2_client.get_paginator('describe_instances')
        for page in paginator.paginate(Filters=filters):
            for res in page.get('Reservations', []):
                for inst in res.get('Instances', []):
                    target_instance_ids.append(inst['InstanceId'])

        if target_instance_ids and not dry_run:
            if action == "stop":
                ec2_client.stop_instances(InstanceIds=target_instance_ids)
            else:
                ec2_client.start_instances(InstanceIds=target_instance_ids)

    except (ClientError, NoCredentialsError) as e:
        return {"error": str(e)}

    return {
        "action": action,
        "target_env": target_env,
        "dry_run": dry_run,
        "target_instance_ids": target_instance_ids,
        "count": len(target_instance_ids),
        "simulated": False
    }


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    print("--- [Question 14 Test: EC2 Scheduler] ---")
    result = manage_ec2_schedule(action="stop", target_env="dev", dry_run=True)

    print(f"Action Requested    : {result['action'].upper()}")
    print(f"Target Environment  : {result['target_env']}")
    print(f"Dry Run Mode        : {result['dry_run']}")
    print(f"Instances Selected  : {result['target_instance_ids']} (Count: {result['count']})")

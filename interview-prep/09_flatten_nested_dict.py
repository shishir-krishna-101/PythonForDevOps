#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 09: Flatten and Unflatten Nested Dictionaries
================================================================================
Problem Statement:
Cloud resources, Kubernetes configurations, and Terraform state files often
contain deeply nested dictionaries. Converting them into flat key-value pairs
with dot notation is essential for exporting to environment variables or Prometheus
metric labels.

Write two Python functions:
  1. `flatten_dict(nested_dict, separator=".")`:
     Converts a nested dictionary into a single-level dictionary where keys are
     concatenated using `separator`.
     Example:
       {"aws": {"ec2": {"type": "t3.medium"}}} -> {"aws.ec2.type": "t3.medium"}
  2. `unflatten_dict(flat_dict, separator=".")`:
     Reconstructs the original nested dictionary from the flattened representation.

Constraints:
  - Must handle nested lists or primitive scalar values.
  - O(N) where N is the total number of leaf nodes in the dictionary.
================================================================================
"""

from typing import Dict, Any


def flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """
    Flattens a multi-level nested dictionary into a single-level dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else str(k)
        if isinstance(v, dict) and v: # Non-empty dict
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def unflatten_dict(d: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    """
    Reconstructs the original nested dictionary from a flattened dot-separated dictionary.
    """
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current or not isinstance(current[part], dict):
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    original_metadata = {
        "cloud": {
            "provider": "aws",
            "region": "us-east-1",
            "compute": {
                "instance_id": "i-098f6bcd4621d373c",
                "type": "c6g.2xlarge",
                "monitoring": {
                    "enabled": True,
                    "interval_sec": 60
                }
            }
        },
        "tags": {
            "Environment": "Production",
            "Owner": "DevOpsTeam"
        }
    }

    print("--- [Question 09 Test: Flattening & Unflattening Dictionaries] ---")

    # 1. Flatten
    flat = flatten_dict(original_metadata)
    print("\n1. Flattened Dictionary (Dot Notation):")
    for k, v in flat.items():
        print(f"  {k:35} = {v}")

    # 2. Unflatten
    restored = unflatten_dict(flat)
    print(f"\n2. Reconstructed Equals Original? {restored == original_metadata}")

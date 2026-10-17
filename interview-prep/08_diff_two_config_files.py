#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 08: Deep Configuration Diff Engine (Staging vs Prod)
================================================================================
Problem Statement:
DevOps and SRE teams often need to compare application configuration files
between environments (e.g., `config.staging.json` vs `config.production.json`)
or detect configuration drift.

Write a recursive Python function `deep_diff(dict_a, dict_b, prefix="")` that:
  1. Recursively traverses two nested dictionaries.
  2. Detects:
     - Keys added in dict_b (missing in dict_a)
     - Keys removed in dict_b (present in dict_a)
     - Keys whose values were modified, showing `(old_value -> new_value)`
     - Keys where the data type changed (e.g., string to int)
  3. Represents nested keys using dot notation (e.g. `database.connection.pool_size`).
  4. Returns a structured dictionary containing `added`, `removed`, and `modified`.

Constraints:
  - Must handle nested dictionaries of arbitrary depth.
  - Must compare lists accurately.
================================================================================
"""

from typing import Dict, Any, List


def deep_diff(
    old_dict: Dict[str, Any],
    new_dict: Dict[str, Any],
    prefix: str = ""
) -> Dict[str, Any]:
    """
    Recursively compares two nested dictionaries and returns structural differences.
    """
    diff_report = {
        "added": {},      # {path: new_value}
        "removed": {},    # {path: old_value}
        "modified": {}    # {path: {"old": v1, "new": v2}}
    }

    all_keys = set(old_dict.keys()).union(set(new_dict.keys()))

    for key in sorted(all_keys):
        current_path = f"{prefix}.{key}" if prefix else str(key)

        # 1. Key added in new_dict
        if key not in old_dict:
            diff_report["added"][current_path] = new_dict[key]
            continue

        # 2. Key removed from new_dict
        if key not in new_dict:
            diff_report["removed"][current_path] = old_dict[key]
            continue

        val_old = old_dict[key]
        val_new = new_dict[key]

        # 3. Both are nested dictionaries -> recurse
        if isinstance(val_old, dict) and isinstance(val_new, dict):
            sub_diff = deep_diff(val_old, val_new, prefix=current_path)
            diff_report["added"].update(sub_diff["added"])
            diff_report["removed"].update(sub_diff["removed"])
            diff_report["modified"].update(sub_diff["modified"])

        # 4. Values differ
        elif val_old != val_new:
            diff_report["modified"][current_path] = {
                "old": val_old,
                "new": val_new
            }

    return diff_report


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    staging_config = {
        "app_name": "checkout-svc",
        "env": "staging",
        "server": {
            "port": 8080,
            "workers": 2,
            "tls_enabled": False
        },
        "database": {
            "host": "staging-rds.internal",
            "pool_size": 5
        },
        "debug": True
    }

    production_config = {
        "app_name": "checkout-svc",
        "env": "production",
        "server": {
            "port": 8080,
            "workers": 8,
            "tls_enabled": True
        },
        "database": {
            "host": "prod-aurora-cluster.internal",
            "pool_size": 25,
            "read_replica": "prod-read-01.internal" # Added
        }
        # "debug" removed in production
    }

    diff = deep_diff(staging_config, production_config)

    print("--- [Question 08 Test: Configuration Diff] ---")
    print("\n1. Added Configuration Keys:")
    for path, val in diff["added"].items():
        print(f"  + {path} = {val}")

    print("\n2. Removed Configuration Keys:")
    for path, val in diff["removed"].items():
        print(f"  - {path} (was: {val})")

    print("\n3. Modified Values (Staging -> Production):")
    for path, change in diff["modified"].items():
        print(f"  * {path}: {change['old']} -> {change['new']}")

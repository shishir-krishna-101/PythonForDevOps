#!/usr/bin/env python3
"""
01-python-basics-for-devops/preflight_check.py

Realistic DevOps script demonstrating:
- Environment variable inspection
- String operations (cleaning, splitting, formatting)
- Functions with type annotations
- Exit code handling for CI/CD runners
"""

import os
import sys
from typing import Dict, List, Tuple


def check_required_env_vars(required: List[str]) -> Tuple[bool, Dict[str, str]]:
    """
    Checks that all required environment variables are present and non-empty.
    Returns a tuple of (status, dict_of_vars).
    """
    missing = []
    collected = {}
    for var in required:
        val = os.getenv(var)
        if not val or not val.strip():
            missing.append(var)
        else:
            collected[var] = val.strip()

    if missing:
        print(f"[ERROR] Missing required environment variables: {', '.join(missing)}")
        return False, collected

    return True, collected


def parse_service_endpoint(endpoint_str: str) -> Dict[str, str]:
    """
    Parses a string formatted as host:port into its individual components.
    Example: 'db-master.internal:5432' -> {'host': 'db-master.internal', 'port': '5432'}
    """
    clean_str = endpoint_str.strip()
    if ":" not in clean_str:
        raise ValueError(f"Invalid endpoint format '{clean_str}'. Expected 'host:port'")

    host, port = clean_str.split(":", 1)
    if not port.isdigit():
        raise ValueError(f"Port must be a positive integer, got: '{port}'")

    return {"host": host, "port": port}


def main():
    print("--- [DevOps Pre-Flight Checker] ---")

    # Set mock variables if running locally for demonstration
    if "DEPLOYMENT_TARGET" not in os.environ:
        os.environ["DEPLOYMENT_TARGET"] = "production"
        os.environ["DATABASE_ENDPOINT"] = "postgres-aurora.internal:5432"
        os.environ["MAX_RETRY_COUNT"] = "5"

    required_vars = ["DEPLOYMENT_TARGET", "DATABASE_ENDPOINT", "MAX_RETRY_COUNT"]
    success, env_map = check_required_env_vars(required_vars)

    if not success:
        print("[FAIL] Pre-flight verification failed.")
        sys.exit(1)

    print("[OK] All environment variables detected:")
    for k, v in env_map.items():
        print(f"  * {k} = {v}")

    try:
        db_config = parse_service_endpoint(env_map["DATABASE_ENDPOINT"])
        print(f"[OK] Database Target Host: {db_config['host']} on Port: {db_config['port']}")
    except ValueError as e:
        print(f"[FAIL] Configuration parsing error: {e}")
        sys.exit(1)

    print("[SUCCESS] All checks passed. Ready for deployment!")
    sys.exit(0)


if __name__ == "__main__":
    main()

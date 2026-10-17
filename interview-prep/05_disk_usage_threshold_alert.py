#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 05: Multi-Partition Disk Usage Monitor & Alert Sentinel
================================================================================
Problem Statement:
Write a Python function `check_disk_thresholds(warning_pct=80.0, critical_pct=90.0)`
that:
  1. Inspects all mounted disk partitions on the host system using `psutil.disk_partitions()`
     and `psutil.disk_usage()`.
  2. Converts raw bytes into human-readable formatted gigabytes (GiB).
  3. Classifies each mount point status as:
     - `OK` (usage < warning_pct)
     - `WARNING` (warning_pct <= usage < critical_pct)
     - `CRITICAL` (usage >= critical_pct)
  4. Filters out read-only loops, CD-ROMs, and virtual tempfs mounts (e.g., squashfs, iso9660).
  5. Returns a structured report and overall system exit status code:
     - 0 if all OK
     - 1 if any mount is WARNING
     - 2 if any mount is CRITICAL

Constraints:
  - Must be cross-platform (works on Linux, macOS, and Windows).
  - Handles permission errors when accessing restricted mount points.
================================================================================
"""

import sys
import psutil
from typing import List, Dict, Any, Tuple


def format_bytes_to_gib(num_bytes: int) -> float:
    """Converts bytes to gigabytes rounded to 2 decimal places."""
    return round(num_bytes / (1024 ** 3), 2)


def check_disk_thresholds(
    warning_pct: float = 80.0,
    critical_pct: float = 90.0
) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Evaluates disk usage across all legitimate partitions and returns (exit_code, partition_reports).
    """
    partition_reports = []
    overall_status_code = 0 # 0=OK, 1=WARNING, 2=CRITICAL

    # Virtual filesystems to ignore
    ignored_fs = {"squashfs", "iso9660", "nullfs", "tmpfs", "overlay"}

    for part in psutil.disk_partitions(all=False):
        # Skip pseudo/virtual devices
        if part.fstype in ignored_fs or not part.fstype:
            continue

        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (PermissionError, OSError):
            continue

        pct = usage.percent
        if pct >= critical_pct:
            status = "CRITICAL"
            overall_status_code = max(overall_status_code, 2)
        elif pct >= warning_pct:
            status = "WARNING"
            overall_status_code = max(overall_status_code, 1)
        else:
            status = "OK"

        partition_reports.append({
            "device": part.device,
            "mountpoint": part.mountpoint,
            "fstype": part.fstype,
            "total_gib": format_bytes_to_gib(usage.total),
            "used_gib": format_bytes_to_gib(usage.used),
            "free_gib": format_bytes_to_gib(usage.free),
            "usage_percent": pct,
            "status": status
        })

    return overall_status_code, partition_reports


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    exit_code, reports = check_disk_thresholds(warning_pct=80.0, critical_pct=90.0)

    print("--- [Question 05 Test Results: Host Disk Usage] ---")
    print(f"{'Mount Point':<20} | {'Total (GiB)':<12} | {'Used (GiB)':<12} | {'Free (GiB)':<12} | {'Usage %':<9} | {'Status'}")
    print("-" * 85)
    for r in reports:
        print(f"{r['mountpoint']:<20} | {r['total_gib']:>10.2f}   | {r['used_gib']:>10.2f}   | {r['free_gib']:>10.2f}   | {r['usage_percent']:>7.1f}% | {r['status']}")

    print(f"\nOverall Exit Code: {exit_code} (0=OK, 1=WARNING, 2=CRITICAL)")

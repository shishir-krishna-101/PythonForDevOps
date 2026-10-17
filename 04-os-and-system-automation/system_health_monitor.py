#!/usr/bin/env python3
"""
04-os-and-system-automation/system_health_monitor.py

Demonstrates:
- Gathering OS architecture & release data via `platform`
- Real-time CPU, RAM, and Disk metrics via `psutil` and `shutil`
- Top process inspection with defensive exception handling
- Setting threshold breach exit codes
"""

import sys
import platform
import psutil
import shutil
from typing import List, Dict, Any


def get_system_summary() -> Dict[str, str]:
    """Returns platform and hardware details."""
    u = platform.uname()
    return {
        "os_name": u.system,
        "os_release": u.release,
        "architecture": u.machine,
        "processor": u.processor or "N/A",
        "python_version": platform.python_version()
    }


def get_resource_usage() -> Dict[str, float]:
    """Gathers CPU, memory, and disk percentages."""
    cpu_usage = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return {
        "cpu_percent": cpu_usage,
        "memory_percent": mem.percent,
        "memory_free_gb": round(mem.available / (1024 ** 3), 2),
        "disk_percent": disk.percent,
        "disk_free_gb": round(disk.free / (1024 ** 3), 2)
    }


def get_top_cpu_processes(limit: int = 5) -> List[Dict[str, Any]]:
    """Fetches processes consuming the most CPU."""
    procs = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Sort by memory percent as CPU requires 2 samples
    procs.sort(key=lambda x: x.get('memory_percent') or 0.0, reverse=True)
    return procs[:limit]


def main():
    print("==================================================")
    print("      DEVOPS HOST SYSTEM TELEMETRY MONITOR       ")
    print("==================================================")

    sys_info = get_system_summary()
    print("\n--- System Specifications ---")
    for k, v in sys_info.items():
        print(f"  {k:15}: {v}")

    usage = get_resource_usage()
    print("\n--- Current Resource Utilization ---")
    print(f"  CPU Utilization   : {usage['cpu_percent']}%")
    print(f"  RAM Utilization   : {usage['memory_percent']}% (Free: {usage['memory_free_gb']} GB)")
    print(f"  Disk Utilization  : {usage['disk_percent']}% (Free: {usage['disk_free_gb']} GB)")

    print("\n--- Top 5 Memory Consuming Processes ---")
    top_procs = get_top_cpu_processes(5)
    for p in top_procs:
        mem_pct = p.get('memory_percent') or 0.0
        print(f"  PID: {p['pid']:<6} | Process: {p['name']:<25} | Memory: {mem_pct:.2f}%")

    # Threshold evaluation
    status_ok = True
    if usage["memory_percent"] > 95.0:
        print("\n[CRITICAL ALERT] Memory utilization exceeds 95% threshold!")
        status_ok = False

    if usage["disk_percent"] > 95.0:
        print("\n[CRITICAL ALERT] Root disk usage exceeds 95% threshold!")
        status_ok = False

    if status_ok:
        print("\n[OK] Host health is within nominal limits.")
        sys.exit(0)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()

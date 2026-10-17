# 04 - OS and System Automation for DevOps

---

## 1. What It Is
OS and system automation involves interacting directly with the underlying operating system kernel, filesystem, and hardware resources using Python's standard and specialized libraries:
- **`os` & `sys`**: Environment variables, exit codes, process IDs (`os.getpid()`), and system arguments.
- **`pathlib`**: Object-oriented filesystem path manipulation across Linux, Windows, and macOS (no more hardcoded `/` or `\\`).
- **`shutil`**: High-level file operations (copying, moving, recursive tree removal, disk usage, and archive creation like `.tar.gz` and `.zip`).
- **`psutil`**: Cross-platform process and system monitoring library (CPU, memory, disk, network, sensors).
- **`platform`**: Hardware and OS architecture introspection (Linux distro, kernel release, CPU architecture `x86_64` vs `arm64`).

---

## 2. What Is the Use of It in DevOps?
System automation is at the heart of infrastructure monitoring, site reliability engineering (SRE), and host maintenance:
1. **Disk Space Threshold Watchers**: Prevent production crashes by alerting when `/var/log` or root partition exceeds 85% utilization.
2. **Zombie and Rogue Process Cleaners**: Find hung background workers, runaway memory-leaking processes, or zombie threads and kill them gracefully (`SIGTERM` before `SIGKILL`).
3. **Automated Backup & Archive Creators**: Package logs or data directories into compressed tarballs (`shutil.make_archive`) and rotate old archives older than $N$ days.
4. **Agent Self-Introspection**: Determine whether a script is executing on AWS Graviton (`aarch64`) vs Intel (`x86_64`) to download appropriate binary artifacts.

---

## 3. How to Use It

### Modern Filesystem Management with `pathlib`
```python
from pathlib import Path

# Object-oriented path navigation
log_dir = Path("/var/log/nginx")

# Recursive file search with glob
for log_file in log_dir.glob("**/*.log"):
    if log_file.stat().st_size > 100 * 1024 * 1024: # > 100 MB
        print(f"Large log detected: {log_file} ({log_file.stat().st_size} bytes)")
```

### Disk Usage with `shutil`
```python
import shutil

total, used, free = shutil.disk_usage("/")
percent_used = (used / total) * 100
print(f"Disk Usage: {percent_used:.2f}% | Free: {free // (1024**3)} GB")
```

### Host Metrics with `psutil`
```python
import psutil

# CPU utilization across a 1-second sample interval
cpu = psutil.cpu_percent(interval=1)

# Memory utilization
mem = psutil.virtual_memory()
print(f"RAM Used: {mem.percent}% (Available: {mem.available // (1024**2)} MB)")
```

---

## 4. How to Implement It: Step-by-Step

### Step A: Finding and Pruning Files Older Than N Days
In production, log disks fill up rapidly. Here is how SREs automate file rotation cleanup:
```python
import time
from pathlib import Path

def prune_old_files(directory: str, max_age_days: int):
    now = time.time()
    cutoff_time = now - (max_age_days * 86400)
    target = Path(directory)

    for file_path in target.glob("*.log"):
        if file_path.is_file():
            # Check last modification time
            if file_path.stat().st_mtime < cutoff_time:
                print(f"Deleting stale log: {file_path}")
                file_path.unlink() # Safe file deletion
```

### Step B: Identifying Top Memory-Consuming Processes
```python
import psutil

def get_top_memory_consumers(limit: int = 5):
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Sort descending by memory percentage
    processes.sort(key=lambda p: p['memory_percent'] or 0, reverse=True)
    return processes[:limit]
```

---

## 5. DevOps Hands-On Example: Host Health & Threshold Monitor

```python
#!/usr/bin/env python3
"""
Host Health & SRE Diagnostic Watchdog.
Monitors CPU, Memory, Disk Partitions, and identifies rogue processes.
"""
import sys
import platform
import psutil
import shutil
from typing import Dict, Any

CPU_THRESHOLD_PERCENT = 80.0
MEMORY_THRESHOLD_PERCENT = 85.0
DISK_THRESHOLD_PERCENT = 90.0

def collect_host_telemetry() -> Dict[str, Any]:
    # System summary
    uname = platform.uname()
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()

    # Disk inspection for root / current mount
    disk = psutil.disk_usage('/')

    return {
        "os": f"{uname.system} {uname.release} ({uname.machine})",
        "cpu_usage": cpu_percent,
        "memory_usage": mem.percent,
        "memory_available_mb": round(mem.available / (1024 * 1024), 2),
        "disk_usage": disk.percent,
        "disk_free_gb": round(disk.free / (1024 ** 3), 2)
    }

def evaluate_thresholds(telemetry: Dict[str, Any]) -> bool:
    alerts = []
    if telemetry["cpu_usage"] > CPU_THRESHOLD_PERCENT:
        alerts.append(f"HIGH CPU: {telemetry['cpu_usage']}% > {CPU_THRESHOLD_PERCENT}%")
    if telemetry["memory_usage"] > MEMORY_THRESHOLD_PERCENT:
        alerts.append(f"HIGH RAM: {telemetry['memory_usage']}% > {MEMORY_THRESHOLD_PERCENT}%")
    if telemetry["disk_usage"] > DISK_THRESHOLD_PERCENT:
        alerts.append(f"CRITICAL DISK: {telemetry['disk_usage']}% > {DISK_THRESHOLD_PERCENT}%")

    if alerts:
        print("[ALERT TRIGGERED] The following thresholds were breached:")
        for alert in alerts:
            print(f"  ! {alert}")
        return False

    print("[HEALTHY] All host metrics within acceptable thresholds.")
    return True

def main():
    print("=== Gathering Host Telemetry ===")
    data = collect_host_telemetry()
    for k, v in data.items():
        print(f"  {k:20}: {v}")

    print("\n=== Evaluating System Health ===")
    healthy = evaluate_thresholds(data)
    sys.exit(0 if healthy else 1)

if __name__ == "__main__":
    main()
```

---

## 6. Interview & Real-World Questions

### Q1: Why should you prefer `pathlib.Path` over `os.path` in modern DevOps tooling?
**Answer:**
1. **Cross-Platform Compatibility**: `Path("dir") / "file.txt"` automatically renders `/` on Linux and `\` on Windows without manual string concatenation.
2. **Object-Oriented API**: Methods like `.exists()`, `.is_file()`, `.read_text()`, `.write_text()`, `.stat()`, and `.unlink()` are accessible directly from the path instance rather than importing multiple separate `os` functions.
3. **Globbing**: `path.glob("*.yaml")` provides native, concise pattern matching.

### Q2: How does `psutil.process_iter()` prevent race conditions when inspecting short-lived processes?
**Answer:**
Processes in Linux and Windows can spawn and exit in milliseconds. When attempting to read attributes of a process that terminated between iteration and inspection, `psutil` raises `psutil.NoSuchProcess` or `psutil.AccessDenied`.
**Safe Pattern**:
```python
for proc in psutil.process_iter(['pid', 'name']):
    try:
        info = proc.info
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        continue
```

### Q3: How do you gracefully stop a container or background worker before forcing a kill?
**Answer:**
Always send `signal.SIGTERM` first, allow an eviction/grace period (e.g. 10–30 seconds like Kubernetes pod termination), and only if the process is still running, send `signal.SIGKILL`:
```python
import os, signal, time

proc.send_signal(signal.SIGTERM)
try:
    proc.wait(timeout=15)
except psutil.TimeoutExpired:
    proc.kill() # sends SIGKILL
```

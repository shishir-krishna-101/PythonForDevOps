# Real-World Script 05: Multi-Server Remote Health Sentinel & SSH Auto-Remediator

---

## 1. Real-World DevOps Problem Statement
In enterprise environments with legacy Linux fleets, stateful VMs, or bare-metal databases:
1. **Unmonitored Log Growth**: Applications, Nginx access logs, and Linux systemd journals (`/var/log/journal`) expand continuously until the root partition reaches 100%.
2. **Cascading Server Outages**: When the root filesystem fills up, Linux halts: SSH logins fail because `/var/run/utmp` cannot be written, MySQL crashes due to inability to write binlogs, and cron jobs terminate.
3. **Manual SRE Burnout**: On-call engineers are frequently paged at 3:00 AM to manually SSH into hosts and execute `journalctl --vacuum-size` and `find /var/log -delete`.
4. **Automated Solution**: A centralized Python sentinel that concurrently inspects fleets over SSH and auto-purges safe, reclaimable caches when thresholds are breached.

---

## 2. Complete Code Implementation

See the full script in [remote_fleet_auto_cleaner.py](file:///c:/Users/Demon%20Slayer/Documents/PythonForDevOps/14-real-world-devops-scripts/05-multi-server-health-remediation/remote_fleet_auto_cleaner.py).

---

## 3. Deep-Dive Code Explanation: What Is It Doing?

### A. Concurrent Fleet Execution with ThreadPoolExecutor
```python
with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
    future_to_node = {
        executor.submit(inspect_and_remediate_host, node, args.key, dry_run): node
        for node in DEFAULT_FLEET
    }
```
- Spawns parallel worker threads to probe multiple Linux hosts simultaneously.
- Reduces audit time for 100 servers from 15 minutes (sequential) to under 30 seconds.

### B. Accurate Filesystem Inspection via POSIX Utilities
```python
code, out, err = run_ssh_command(client, "df / | tail -n 1 | awk '{print $5}' | tr -d '%'")
```
- Queries the root partition utilization percentage cleanly using standard POSIX utilities (`df`, `awk`, `tr`).
- Strips trailing `%` and converts to floating point for threshold comparisons.

### C. Safe, Idempotent Remediation Commands
```python
CLEANUP_COMMANDS = [
    "sudo journalctl --vacuum-time=3d",
    "sudo apt-get clean || sudo yum clean all",
    "sudo find /var/log -type f -name '*.gz' -mtime +7 -delete"
]
```
- **Journal Vacuuming**: Safely archives and purges systemd binary journal logs older than 3 days.
- **Package Cache Cleaning**: Cleans stale `.deb` or `.rpm` installer archives that waste gigabytes after OS upgrades.
- **Rotated Log Pruning**: Only deletes compressed archives (`*.gz`) that are older than 7 days, leaving active log files untouched.

### D. Post-Remediation Verification Loop
- Re-executes `df /` immediately following the remediation commands.
- Calculates and reports the new utilization percentage, proving that the operation succeeded in freeing disk space.

---

## 4. Libraries Used & Why

| Library | Why It Was Chosen |
|:---|:---|
| `paramiko` | Pure Python SSHv2 protocol implementation. Enables remote command execution and key authentication without requiring external OpenSSH binaries. |
| `concurrent.futures.ThreadPoolExecutor` | Standard library high-level thread management for concurrent I/O-bound network calls. |
| `argparse` | CLI options for concurrency tuning, private key specification, and dry-run toggle. |
| `logging` | Hierarchical logging namespaced per host for isolated troubleshooting. |

---

## 5. Real-World Problems, Edge Cases & Code Fixes

### Problem 1: Broken SSH Pipes and Hanging Threads
- **Real-World Incident**: If a remote server is in a kernel panic or packet loss loop, a thread might hang indefinitely, freezing the thread pool.
- **The Code Fix**: Configured strict socket-level timeouts on both `client.connect(timeout=5)` and `client.exec_command(timeout=15)`.

### Problem 2: Sudo Password Prompts Blocking Unattended Scripts
- **Real-World Incident**: Commands like `sudo apt-get clean` prompt for passwords, hanging the automation script.
- **The Code Fix**: Automated scripts should connect with an SSH user configured in `/etc/sudoers` with `NOPASSWD: ALL` for authorized maintenance commands.

### Problem 3: Deleting Active Log Files Still Held Open by Daemons
- **Real-World Incident**: If an automated script deletes `/var/log/nginx/access.log` directly while Nginx is running, Linux keeps the inode open and does not free disk space (`lsof +L1` shows deleted file still held).
- **The Code Fix**: The cleanup script strictly targets compressed archives (`*.gz`), which are never held open by running services.

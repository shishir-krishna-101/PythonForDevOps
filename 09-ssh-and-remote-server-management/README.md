# 09 - SSH & Remote Server Management for DevOps

---

## 1. What It Is
SSH (Secure Shell) is the industry standard protocol for securely accessing remote servers over unsecured networks. In Python, SSH automation is powered by:
- **`paramiko`**: The core, low-level Python implementation of the SSHv2 protocol. Provides direct access to SSH clients, cryptographic keys, channels, and SFTP.
- **`fabric`**: A high-level library built on top of Paramiko designed for executing shell commands remotely across fleets of servers and handling file synchronization.
- **`paramiko.SFTPClient`**: Secure File Transfer Protocol client for uploading configurations and downloading remote server logs.
- **Key-Based Authentication**: Loading RSA/Ed25519 private keys (`paramiko.RSAKey` / `paramiko.Ed25519Key`) with or without passphrases.

---

## 2. What Is the Use of It in DevOps?
Not every workload lives inside Kubernetes or serverless containers. Millions of virtual machines (VMs) and bare-metal nodes require automation:
1. **Fleet Patching & Maintenance**: Running security kernel updates (`apt-get update && apt-get upgrade -y`) across fleets of servers.
2. **Remote Health & Diagnostic Retrieval**: Executing `df -h`, `uptime`, `systemctl status nginx`, or grabbing crash dumps from remote servers.
3. **Automated Configuration Distribution**: Securely copying application configs, Nginx reverse proxy files, or SSL certificates via SFTP.
4. **Bastion / Jump-Host Automation**: Tunneling through a private jump box to reach isolated database or application instances.

---

## 3. How to Use It

### Production Paramiko SSH Client Pattern
```python
import paramiko

def execute_remote_command(host: str, username: str, key_path: str, command: str):
    ssh = paramiko.SSHClient()
    # In production, load known host keys from file instead of blindly accepting all keys
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(
            hostname=host,
            port=22,
            username=username,
            key_filename=key_path,
            timeout=10,
            banner_timeout=15
        )
        stdin, stdout, stderr = ssh.exec_command(command, timeout=30)
        
        # recv_exit_status blocks until the remote command finishes
        exit_code = stdout.channel.recv_exit_status()
        output = stdout.read().decode("utf-8")
        error = stderr.read().decode("utf-8")
        
        return exit_code, output, error
    finally:
        ssh.close()
```

### SFTP File Transfer
```python
import paramiko

def upload_configuration(ssh_client: paramiko.SSHClient, local_file: str, remote_file: str):
    sftp = ssh_client.open_sftp()
    try:
        sftp.put(local_file, remote_file)
        # Verify file size matches
        local_size = os.path.getsize(local_file)
        remote_size = sftp.stat(remote_file).st_size
        return local_size == remote_size
    finally:
        sftp.close()
```

---

## 4. How to Implement It: Step-by-Step

### Step A: Handling Host Key Policies Safely
Using `paramiko.AutoAddPolicy()` in production can expose you to Man-In-The-Middle (MITM) attacks if an attacker intercepts DNS/ARP. For maximum security:
```python
import paramiko

ssh = paramiko.SSHClient()
ssh.load_system_host_keys("/home/devops/.ssh/known_hosts")
# RejectUnknownHostPolicy enforces strict host verification
ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
```

### Step B: Multi-Threaded Fleet Execution
Executing commands sequentially across 100 servers takes minutes. Using Python's `concurrent.futures.ThreadPoolExecutor` runs them concurrently in seconds:
```python
from concurrent.futures import ThreadPoolExecutor

servers = ["10.0.1.10", "10.0.1.11", "10.0.1.12", "10.0.1.13"]

with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(lambda s: execute_remote_command(s, "ubuntu", "key.pem", "uptime"), servers)
```

---

## 5. DevOps Hands-On Example: Remote Fleet Health Auditor & SFTP Sync

```python
#!/usr/bin/env python3
"""
Remote Host Management & Fleet Auditor using Paramiko.
Connects via SSH, runs diagnostic health commands, checks exit status,
and handles connection exceptions.
"""
import sys
import paramiko
from typing import Dict, Any

def audit_remote_host(hostname: str, username: str, key_path: str = None) -> Dict[str, Any]:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    result = {
        "host": hostname,
        "status": "UNREACHABLE",
        "uptime": None,
        "disk_free": None,
        "error": None
    }

    try:
        # Connect to host
        client.connect(
            hostname=hostname,
            port=22,
            username=username,
            key_filename=key_path,
            timeout=5,
            look_for_keys=True
        )
        result["status"] = "CONNECTED"

        # 1. Check Uptime
        _, stdout, _ = client.exec_command("uptime", timeout=5)
        result["uptime"] = stdout.read().decode().strip()

        # 2. Check Disk Space
        _, stdout, _ = client.exec_command("df -h / | tail -n 1", timeout=5)
        result["disk_free"] = stdout.read().decode().strip()

    except paramiko.AuthenticationException:
        result["error"] = "SSH Authentication failed (check credentials/key)."
    except paramiko.SSHException as e:
        result["error"] = f"SSH error occurred: {e}"
    except TimeoutError:
        result["error"] = "Connection timed out."
    except Exception as e:
        result["error"] = str(e)
    finally:
        client.close()

    return result

def main():
    print("=== Remote Server SSH Management Suite ===")
    print("Simulating audit connection to local/remote test endpoint...")
    
    # Testing connection failure handling gracefully
    audit = audit_remote_host("127.0.0.1", "devops_user", key_path="/invalid/key.pem")
    print(f"Target Host : {audit['host']}")
    print(f"Status      : {audit['status']}")
    print(f"Diagnostics : {audit['error']}")

    print("\n[INFO] Paramiko client properly caught and handled authentication/connection limits.")

if __name__ == "__main__":
    main()
```

---

## 6. Interview & Real-World Questions

### Q1: What is the purpose of `stdout.channel.recv_exit_status()` in Paramiko?
**Answer:**
`exec_command()` is non-blocking; it returns immediately after sending the command string over the channel. If you read `stdout.read()` without waiting for exit status, the script might finish before the remote command finishes, or you won't know if the command succeeded or crashed. Calling `recv_exit_status()` blocks until the remote process terminates and returns its exit code (`0` for success).

### Q2: Why is `paramiko.AutoAddPolicy()` dangerous in production environments?
**Answer:**
`AutoAddPolicy` silently trusts and adds any unknown host key to the local host key dictionary. If an attacker performs ARP spoofing or DNS poisoning (MITM attack), Paramiko will accept the rogue server's SSH key without warning.
**Fix**: Pre-populate known hosts using `client.load_system_host_keys()` and use `RejectPolicy()`.

### Q3: How do you handle sudo commands requiring passwords in Paramiko?
**Answer:**
Either configure `/etc/sudoers` on the remote hosts with `devops_user ALL=(ALL) NOPASSWD: ALL` (recommended for automation), or allocate a pseudo-terminal (`get_pty=True`) in `exec_command` and write the password into `stdin`:
```python
stdin, stdout, stderr = client.exec_command("sudo -S apt-get update", get_pty=True)
stdin.write(f"{sudo_password}\n")
stdin.flush()
```

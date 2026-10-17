# 05 - Process Execution & Subprocess for DevOps

---

## 1. What It Is
The `subprocess` module is Python's standard mechanism for spawning new processes, connecting to their input/output/error pipes, and obtaining their exit return codes:
- **`subprocess.run(...)`**: The modern, recommended high-level entry point for synchronous command execution.
- **`subprocess.Popen(...)`**: The lower-level class for non-blocking, asynchronous process execution, live stdout streaming, and complex IPC pipes.
- **Process I/O**: Capturing `stdout` (standard output) and `stderr` (standard error) as UTF-8 text strings.
- **Execution Constraints**: Timeouts (`timeout=N`), working directory (`cwd=...`), environment variable isolation (`env=...`), and exit code verification (`check=True`).

---

## 2. What Is the Use of It in DevOps?
While Python has SDKs for many cloud services, many foundational DevOps tools are CLI-first:
1. **Executing Infrastructure as Code (IaC)**: Running `terraform init`, `terraform plan -out=tfplan`, and `terraform apply`.
2. **Container & Kubernetes Operations**: Invoking `docker build -t app:v1 .`, `helm upgrade --install`, or `kubectl apply -f manifest.yaml`.
3. **Automating Git Workflows**: Running `git status --porcelain`, `git diff`, `git checkout`, and `git commit` within CI runners.
4. **Network & System Diagnostics**: Invoking `ping -c 3 host`, `traceroute`, or `dig` when low-level OS tools provide the most reliable output.

---

## 3. How to Use It

### Recommended Pattern: `subprocess.run` with Argument Lists
Always pass commands as a list of strings (`["git", "status"]`) rather than a single raw string, and keep `shell=False` (the default):
```python
import subprocess

try:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        check=True,       # Raises CalledProcessError if returncode != 0
        timeout=15        # Prevents hanging processes in CI/CD
    )
    commit_sha = result.stdout.strip()
    print(f"Current Git SHA: {commit_sha}")
except subprocess.CalledProcessError as e:
    print(f"Command failed with exit code {e.returncode}: {e.stderr}")
except subprocess.TimeoutExpired:
    print("Command timed out after 15 seconds!")
```

### The Security Hazard of `shell=True`
```python
# DANGEROUS: Vulnerable to Command Injection
user_input = "prod; rm -rf /"
subprocess.run(f"echo Deploying {user_input}", shell=True) # NEVER DO THIS

# SECURE: Arguments are passed directly to OS execvp
subprocess.run(["echo", f"Deploying {user_input}"], shell=False)
```

---

## 4. How to Implement It: Step-by-Step

### Step A: Building a Reusable CLI Command Runner
In production DevOps automation, you need consistent logging, timeout limits, and error handling for all external commands:
```python
import subprocess
from typing import List, Tuple

def run_command(cmd: List[str], cwd: str = ".") -> Tuple[int, str, str]:
    """
    Executes a system command securely and returns (exit_code, stdout, stderr).
    """
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
            check=False
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired as e:
        return 124, "", f"Timeout expired after {e.timeout}s"
    except FileNotFoundError:
        return 127, "", f"Binary '{cmd[0]}' not found in PATH"
```

### Step B: Live-Streaming Output with `Popen`
For long-running tasks like Docker builds or Terraform runs, buffering output until the command completes prevents engineers from seeing live progress. Use `Popen` to stream line-by-line:
```python
import subprocess

def stream_command(cmd: list):
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    for line in iter(process.stdout.readline, ''):
        print(f"[LIVE] {line.strip()}")
    process.stdout.close()
    return process.wait()
```

---

## 5. DevOps Hands-On Example: Safe Git & Binary Command Executor

```python
#!/usr/bin/env python3
"""
Safe Subprocess Command Wrapper for CI/CD Pipeline Automation.
Executes commands with timeout protections, catches stderr,
and parses exit codes.
"""
import sys
import subprocess
from typing import List

def execute_safely(command: List[str]) -> bool:
    print(f"\n[EXEC] Running: {' '.join(command)}")
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        if completed.returncode == 0:
            print(f"[SUCCESS] Return code: 0")
            if completed.stdout:
                print(f"Stdout:\n{completed.stdout.strip()}")
            return True
        else:
            print(f"[ERROR] Return code: {completed.returncode}")
            if completed.stderr:
                print(f"Stderr:\n{completed.stderr.strip()}")
            return False

    except FileNotFoundError:
        print(f"[FAIL] Executable not found: '{command[0]}'. Is it installed and in PATH?")
        return False
    except subprocess.TimeoutExpired as te:
        print(f"[FAIL] Execution timed out after {te.timeout} seconds.")
        return False

def main():
    print("=== Subprocess Execution Suite for CI/CD ===")

    # Test 1: Check Python version
    execute_safely([sys.executable, "--version"])

    # Test 2: Git status check
    execute_safely(["git", "status", "--short"])

    # Test 3: Intentional non-existent binary to test resilience
    execute_safely(["non_existent_devops_tool", "--help"])

    print("\n=== Subprocess Suite Completed ===")

if __name__ == "__main__":
    main()
```

---

## 6. Interview & Real-World Questions

### Q1: Why is `shell=True` considered a critical security vulnerability in automated CI/CD pipelines?
**Answer:**
When `shell=True`, Python passes the entire string to the underlying shell (`/bin/sh` or `cmd.exe`). If any component of the string contains untrusted user input (e.g., git branch names, PR comments, webhook payloads), an attacker can inject command separators like `;`, `&&`, or `|` to execute arbitrary commands with the CI worker's permissions.
*Rule*: Always use a list of tokens (`["git", "checkout", branch]`) with `shell=False`.

### Q2: How do you handle deadlocks when using `subprocess.Popen` with `PIPE`?
**Answer:**
If you redirect `stdout=subprocess.PIPE` and `stderr=subprocess.PIPE` and the child process produces large amounts of output (filling the OS pipe buffer, usually 64KB), the process will block waiting for the OS buffer to clear. If your Python script is waiting with `proc.wait()`, a **deadlock** occurs.
**Solution**: Use `proc.communicate(timeout=...)` which reads stdout and stderr concurrently in memory, or read from `proc.stdout` line-by-line.

### Q3: What is the difference between `check=True` and manually checking `proc.returncode`?
**Answer:**
- `check=True` automatically raises `subprocess.CalledProcessError` whenever the command exits with a non-zero code. This is useful for "fail-fast" pipeline scripts.
- Checking `proc.returncode` manually allows you to implement custom recovery logic (e.g., if exit code is `2`, retry; if `1`, notify team).

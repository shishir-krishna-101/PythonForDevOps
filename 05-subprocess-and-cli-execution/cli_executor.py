#!/usr/bin/env python3
"""
05-subprocess-and-cli-execution/cli_executor.py

Demonstrates:
- Safe command execution without shell=True
- Output capturing (stdout and stderr)
- Timeout protections
- Executing Git, Docker, and Python CLI tools safely
"""

import sys
import subprocess
from typing import List, Tuple, Optional


def run_command(
    cmd: List[str],
    timeout_sec: int = 15,
    cwd: Optional[str] = None
) -> Tuple[int, str, str]:
    """
    Safely executes an external binary using subprocess.run with argument array.
    Returns (returncode, stdout, stderr).
    """
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError:
        return 127, "", f"Binary '{cmd[0]}' not found in system PATH."
    except subprocess.TimeoutExpired:
        return 124, "", f"Command timed out after {timeout_sec} seconds."


def main():
    print("==================================================")
    print("      DEVOPS SAFE PROCESS EXECUTION RUNNER       ")
    print("==================================================")

    # 1. Run Python version check
    code, stdout, stderr = run_command([sys.executable, "-c", "import sys; print(f'Python runtime: {sys.version}')"])
    print(f"\n[Test 1] Python Runtime Check -> Exit Code: {code}")
    print(f"  Stdout: {stdout}")

    # 2. Run Git status check
    code, stdout, stderr = run_command(["git", "status", "--short"])
    print(f"\n[Test 2] Git Status Check -> Exit Code: {code}")
    if stdout:
        print(f"  Dirty/Untracked Files:\n{stdout}")
    else:
        print("  Working directory clean or empty.")

    # 3. Handling a command failure gracefully
    code, stdout, stderr = run_command(["git", "checkout", "non-existent-devops-branch-xyz"])
    print(f"\n[Test 3] Expected Failure Check -> Exit Code: {code}")
    print(f"  Captured Stderr: {stderr}")

    # 4. Handling missing binary gracefully
    code, stdout, stderr = run_command(["terraform_mock_binary", "plan"])
    print(f"\n[Test 4] Missing Binary Check -> Exit Code: {code}")
    print(f"  Captured Stderr: {stderr}")

    print("\n[SUCCESS] Subprocess tests finished without unhandled exceptions.")


if __name__ == "__main__":
    main()

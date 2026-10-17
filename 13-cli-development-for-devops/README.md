# 13 - CLI Tool Development for DevOps

---

## 1. What It Is
Command-Line Interface (CLI) development allows DevOps engineers to build user-friendly, production-ready command line tools for their engineering organizations:
- **`argparse`**: The Python standard library parser for command-line options, sub-commands, arguments, and automated `--help` generation.
- **`click`**: An intuitive, decorator-based CLI framework that minimizes boilerplate, supports automatic type validation, and enables composable command trees.
- **`rich`**: A Python library for rich text and terminal formatting, rendering colored logs, interactive progress bars, loading spinners, and beautifully formatted tables for infrastructure inventories.

---

## 2. What Is the Use of It in DevOps?
Engineers in modern organizations should not have to remember 20 complex `curl`, `kubectl`, or `aws` commands with 10 flags each. DevOps teams build internal developer platforms (IDP) and CLI tools:
1. **Unified Developer Interface**: Provide developers with a single command (e.g. `platform deploy --service=auth --env=staging`) that abstracts away Kubernetes, Helm, AWS IAM, and Slack webhooks.
2. **Infrastructure Health Dashboards**: Display terminal dashboards showing node health, pod counts, and resource utilization in color-coded tables.
3. **Database & Secret Migration Wizards**: Walk developers through safe database rollouts with interactive confirmation prompts (`Are you sure you want to drop index? [y/N]`).
4. **Structured Dual Output**: Support both human-readable terminal output and `--json` machine-readable output for integration into CI/CD scripts.

---

## 3. How to Use It

### Standard Library `argparse` with Subcommands
```python
import argparse

parser = argparse.ArgumentParser(description="DevOps Platform CLI")
subparsers = parser.add_subparsers(dest="command", required=True)

# Subcommand: deploy
deploy_parser = subparsers.add_parser("deploy", help="Deploy service to target cluster")
deploy_parser.add_argument("--env", choices=["dev", "staging", "prod"], required=True)
deploy_parser.add_argument("--tag", required=True, help="Container image tag")
deploy_parser.add_argument("--dry-run", action="store_true", help="Simulate without changes")

args = parser.parse_args()
print(f"Action: {args.command} -> Env: {args.env}, Tag: {args.tag}, Dry-Run: {args.dry_run}")
```

### Beautiful Output with `rich` Tables
```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(title="Production Service Health")

table.add_column("Service Name", style="cyan", no_wrap=True)
table.add_column("Replicas", justify="right", style="magenta")
table.add_column("Status", justify="center", style="green")

table.add_row("auth-api", "5/5", "[bold green]HEALTHY[/]")
table.add_row("payment-worker", "2/4", "[bold yellow]DEGRADED[/]")
table.add_row("notification-svc", "0/3", "[bold red]FAILING[/]")

console.print(table)
```

---

## 4. How to Implement It: Step-by-Step

### Step A: Building Dual Output Support (`--json` vs Pretty Print)
A good DevOps tool is usable both by humans in terminals and by automated CI runners:
```python
import json
from rich.console import Console
from rich.table import Table

def render_results(data: list, as_json: bool = False):
    if as_json:
        print(json.dumps(data, indent=2))
    else:
        table = Table(title="Cluster Nodes")
        table.add_column("Host")
        table.add_column("Status")
        for item in data:
            table.add_row(item["host"], item["status"])
        Console().print(table)
```

### Step B: Interactive Confirmation for High-Risk Actions
```python
import click

@click.command()
@click.option("--env", required=True)
def teardown(env):
    if env == "production":
        click.confirm("WARNING: You are about to tear down PRODUCTION! Proceed?", abort=True)
    click.echo(f"Tearing down {env}...")
```

---

## 5. DevOps Hands-On Example: Enterprise Infrastructure CLI (`opsctl`)

```python
#!/usr/bin/env python3
"""
Enterprise DevOps CLI Tool (`opsctl`).
Demonstrates:
- Subcommand routing (status, scale, audit)
- Rich colored table rendering
- Argument parsing with validation
"""
import sys
import argparse
from rich.console import Console
from rich.table import Table

console = Console()

def cmd_status(args):
    console.print(f"[bold cyan]Fetching status for cluster:[/] {args.cluster} (Env: {args.env})")
    
    table = Table(title=f"Cluster Status: {args.cluster}")
    table.add_column("Pod / Service", style="cyan")
    table.add_column("Namespace", style="magenta")
    table.add_column("CPU", justify="right")
    table.add_column("RAM", justify="right")
    table.add_column("Health", justify="center")

    services = [
        ("auth-api-6f94", "core", "120m", "256Mi", "[green]Running[/]"),
        ("order-proc-88b1", "checkout", "840m", "1.2Gi", "[yellow]High CPU[/]"),
        ("email-worker-01", "notifications", "15m", "80Mi", "[green]Running[/]"),
        ("payment-gw-dead", "checkout", "0m", "0Mi", "[red]CrashLoopBackOff[/]")
    ]

    for name, ns, cpu, ram, status in services:
        table.add_row(name, ns, cpu, ram, status)

    console.print(table)

def cmd_scale(args):
    console.print(f"[yellow]Scaling deployment[/] '{args.deployment}' to [bold]{args.replicas}[/] replicas...")
    console.print("[green]✔ Deployment scaled successfully.[/]")

def main():
    parser = argparse.ArgumentParser(
        prog="opsctl",
        description="Enterprise DevOps Infrastructure Control CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommand to execute")

    # Status subcommand
    status_parser = subparsers.add_parser("status", help="Display cluster service status")
    status_parser.add_argument("--cluster", default="eks-prod-us-east-1", help="Target cluster name")
    status_parser.add_argument("--env", choices=["dev", "stage", "prod"], default="prod", help="Environment")
    status_parser.set_defaults(func=cmd_status)

    # Scale subcommand
    scale_parser = subparsers.add_parser("scale", help="Scale a Kubernetes deployment")
    scale_parser.add_argument("--deployment", required=True, help="Name of deployment")
    scale_parser.add_argument("--replicas", type=int, required=True, help="Target replica count")
    scale_parser.set_defaults(func=cmd_scale)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
```

---

## 6. Interview & Real-World Questions

### Q1: Why should internal DevOps CLI utilities always support a `--json` output flag?
**Answer:**
DevOps tools are used in two distinct ways:
1. **Interactive human use**: Engineers need tables, colors, progress bars, and high-level summaries.
2. **Machine automation (CI/CD / cron)**: Other scripts, pipelines, and tools need raw structured data to pipe into `jq` or Python JSON parsers. Terminal colors and ANSI escape codes break downstream parsers. Supporting `--json` satisfies both use cases.

### Q2: How do you implement POSIX exit codes in a Python CLI, and why does it matter?
**Answer:**
The shell inspects `$?` after command execution:
- `0`: Success
- `1`: General runtime error or assertion failure
- `2`: Misuse of shell built-ins or CLI syntax/flag error (standard `argparse` behavior)
- `127`: Command / binary not found
- `130`: Terminated by Ctrl+C (`SIGINT`)
Always call `sys.exit(0)` on success and `sys.exit(1)` or specific codes on failure so CI/CD pipelines can halt on errors.

### Q3: When should you choose `click` over `argparse`?
**Answer:**
`argparse` is built into Python with zero dependencies (ideal for lightweight container bootstrap scripts). However, `click` is significantly superior for large, multi-level CLIs because:
1. Decorators keep command logic and flag definitions colocated.
2. Built-in parameter validation, prompt handling, file path checks (`click.Path(exists=True)`).
3. Automatic sub-command nesting and context passing (`@click.pass_context`).

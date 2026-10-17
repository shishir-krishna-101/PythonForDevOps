#!/usr/bin/env python3
"""
13-cli-development-for-devops/devops_cli.py

Demonstrates:
- Subcommand parsing using argparse
- Formatting terminal output with rich tables and colors
- Safe JSON output flag for CI/CD runners
- Standard POSIX exit codes
"""

import sys
import json
import argparse
from typing import List, Dict, Any

try:
    from rich.console import Console
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


MOCK_SERVICES = [
    {"name": "gateway-api", "namespace": "ingress", "status": "Healthy", "cpu": "45m", "memory": "128Mi"},
    {"name": "billing-worker", "namespace": "finance", "status": "Degraded", "cpu": "890m", "memory": "1.4Gi"},
    {"name": "auth-service", "namespace": "security", "status": "Healthy", "cpu": "22m", "memory": "90Mi"},
    {"name": "metrics-collector", "namespace": "monitoring", "status": "CrashLoop", "cpu": "0m", "memory": "0Mi"}
]


def render_table(services: List[Dict[str, Any]]) -> None:
    """Renders formatted table using Rich or plain text fallback."""
    if RICH_AVAILABLE:
        console = Console()
        table = Table(title="Cluster Services Telemetry")
        table.add_column("Service", style="cyan", no_wrap=True)
        table.add_column("Namespace", style="magenta")
        table.add_column("CPU Usage", justify="right")
        table.add_column("Memory", justify="right")
        table.add_column("Health Status", justify="center")

        for s in services:
            status = s["status"]
            if status == "Healthy":
                styled_status = "[bold green]Healthy[/]"
            elif status == "Degraded":
                styled_status = "[bold yellow]Degraded[/]"
            else:
                styled_status = "[bold red]CrashLoop[/]"

            table.add_row(s["name"], s["namespace"], s["cpu"], s["memory"], styled_status)

        console.print(table)
    else:
        print(f"{'Service':<20} | {'Namespace':<12} | {'CPU':<8} | {'Memory':<8} | {'Status'}")
        print("-" * 65)
        for s in services:
            print(f"{s['name']:<20} | {s['namespace']:<12} | {s['cpu']:<8} | {s['memory']:<8} | {s['status']}")


def handle_status(args: argparse.Namespace) -> None:
    if args.json:
        print(json.dumps(MOCK_SERVICES, indent=2))
    else:
        render_table(MOCK_SERVICES)


def handle_scale(args: argparse.Namespace) -> None:
    if args.replicas < 0:
        print(f"[ERROR] Replicas cannot be negative: {args.replicas}", file=sys.stderr)
        sys.exit(1)

    print(f"[ACTION] Scaling service '{args.service}' to {args.replicas} replica(s) in env '{args.env}'...")
    print(f"[SUCCESS] Scale operation confirmed.")


def main():
    parser = argparse.ArgumentParser(
        prog="devops_cli",
        description="Enterprise DevOps Infrastructure Management CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available subcommands")

    # 1. Status subcommand
    status_parser = subparsers.add_parser("status", help="Query service health status")
    status_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    status_parser.set_defaults(func=handle_status)

    # 2. Scale subcommand
    scale_parser = subparsers.add_parser("scale", help="Scale a service deployment")
    scale_parser.add_argument("--service", required=True, help="Name of service")
    scale_parser.add_argument("--replicas", type=int, required=True, help="Target replica count")
    scale_parser.add_argument("--env", choices=["dev", "stage", "prod"], default="prod", help="Deployment target environment")
    scale_parser.set_defaults(func=handle_scale)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

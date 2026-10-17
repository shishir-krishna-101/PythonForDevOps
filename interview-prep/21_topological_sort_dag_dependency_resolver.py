#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 21: Microservice & Terraform Dependency Resolver (DAG)
================================================================================
Problem Statement:
In infrastructure orchestration (Terraform, ArgoCD, Helm, Kubernetes operators),
services depend on each other (e.g., `web` requires `api` and `cache`; `api` requires `db`).

Write a Python function `resolve_dependency_order(dependencies)` that:
  1. Accepts a dictionary where keys are service names and values are lists of
     services they directly depend upon:
       {"web": ["api", "cache"], "api": ["db"], "cache": [], "db": []}
  2. Implements Topological Sort (Kahn's Algorithm using in-degree or DFS) to return
     a valid execution order where every dependency runs BEFORE the service that requires it:
       Expected Output: ["db", "api", "cache", "web"] (or ["cache", "db", "api", "web"])
  3. Detects circular dependencies (e.g., `A -> B -> A`) and raises a custom
     `CircularDependencyError` with the cycle participants.

--------------------------------------------------------------------------------
HOW TO THINK & SOLVE THIS USING ONLY OFFICIAL DOCS:
--------------------------------------------------------------------------------
1. Mental Model & Problem Decomposition:
   - This is a Directed Acyclic Graph (DAG).
   - "A depends on B" means there is a directed dependency edge: B must be built before A (B -> A).
   - A service with 0 unfulfilled dependencies can be deployed immediately.
   - Every time a service finishes deploying, all services waiting on it have their
     unmet dependency count (in-degree) reduced by 1.

2. Official Docs Reference:
   - Module: `collections` -> `docs.python.org/3/library/collections.html`
   - Specifically look up:
     * `collections.defaultdict`: For building the graph adjacency list and in-degree map without KeyError.
     * `collections.deque`: For O(1) popping of ready services from the queue.

3. Why These Tools Were Chosen:
   - Regular `dict` requires manual `if key not in d:` initialization. `defaultdict(list)` and
     `defaultdict(int)` eliminate 10 lines of boilerplate.
   - `list.pop(0)` is O(N) because it shifts all elements; `deque.popleft()` is O(1).
================================================================================
"""

from collections import defaultdict, deque
from typing import Dict, List, Set


class CircularDependencyError(Exception):
    """Raised when dependencies form an unbreakable cycle."""
    pass


def resolve_dependency_order(dependencies: Dict[str, List[str]]) -> List[str]:
    """
    Computes a valid deployment sequence using Kahn's Algorithm (Topological Sort).
    """
    # graph[dependency] = list of services that depend on this dependency
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    all_nodes: Set[str] = set(dependencies.keys())

    # Build dependency graph
    for service, deps in dependencies.items():
        for dep in deps:
            all_nodes.add(dep)
            graph[dep].append(service)
            in_degree[service] += 1

    # Queue contains all services that have 0 incoming dependencies
    queue = deque([node for node in all_nodes if in_degree[node] == 0])
    deploy_order = []

    while queue:
        ready_service = queue.popleft()
        deploy_order.append(ready_service)

        # Notify all services waiting on this dependency
        for dependent in graph[ready_service]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    # If the order doesn't contain all nodes, a circular cycle exists
    if len(deploy_order) != len(all_nodes):
        unresolved = [node for node in all_nodes if node not in deploy_order]
        raise CircularDependencyError(
            f"Circular dependency deadlock detected among services: {unresolved}"
        )

    return deploy_order


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    valid_architecture = {
        "frontend": ["api-gateway"],
        "api-gateway": ["auth-service", "billing-service"],
        "auth-service": ["user-db", "redis-cache"],
        "billing-service": ["payment-db"],
        "user-db": [],
        "payment-db": [],
        "redis-cache": []
    }

    print("--- [Question 21 Test: DAG Dependency Resolver] ---")
    order = resolve_dependency_order(valid_architecture)
    print("Valid Deployment Sequence:")
    for idx, svc in enumerate(order, 1):
        print(f"  Step {idx}: {svc}")

    # Test Circular Dependency Detection
    cyclic_architecture = {
        "service-a": ["service-b"],
        "service-b": ["service-c"],
        "service-c": ["service-a"] # Deadlock cycle
    }
    print("\nTesting Circular Dependency Detection:")
    try:
        resolve_dependency_order(cyclic_architecture)
    except CircularDependencyError as e:
        print(f"  [SUCCESSFULLY CAUGHT] {e}")

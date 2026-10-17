#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 24: Object-Oriented Software Load Balancer
================================================================================
Problem Statement:
Design an in-memory Software Load Balancer in Python that routes client requests
to an upstream pool of backend servers (e.g. Nginx/Envoy simulation).

The load balancer must support three standard distribution algorithms:
  1. Round Robin: Distributes requests evenly in sequential circular order.
  2. Weighted Round Robin: Distributes requests proportional to assigned weights
     (e.g., a server with weight 3 gets 3x more traffic than a server with weight 1).
  3. Least Connections: Routes to the backend server with the fewest active
     in-flight requests.

Requirements:
  - Add and remove servers dynamically (`add_server`, `remove_server`).
  - Update active connections when requests start and complete.
  - Mark servers healthy/unhealthy.

--------------------------------------------------------------------------------
HOW TO THINK & SOLVE THIS USING ONLY OFFICIAL DOCS:
--------------------------------------------------------------------------------
1. Mental Model & Problem Decomposition:
   - OOP Class Design: A `Server` class holding `(host, weight, active_conns, healthy)`.
   - A `LoadBalancer` class maintaining the server pool.
   - For Round Robin: Use the modulo operator `%` with an incrementing integer index:
     `server = healthy_servers[index % len(healthy_servers)]`.
   - For Weighted Round Robin: Expand servers according to weights or track cumulative weights.
   - For Least Connections: Find the server with `min(healthy_servers, key=lambda s: s.active_conns)`.

2. Official Docs Reference:
   - Built-in functions: `docs.python.org/3/library/functions.html`
     * `min(iterable, key=...)`: O(N) extraction of server with lowest active connection count.
     * `itertools.cycle`: Standard library module for circular iteration (`docs.python.org/3/library/itertools.html`).
================================================================================
"""

from typing import List, Dict, Optional


class Server:
    def __init__(self, host: str, weight: int = 1):
        self.host = host
        self.weight = weight
        self.active_conns = 0
        self.healthy = True

    def __repr__(self):
        return f"<Server {self.host} (weight={self.weight}, conns={self.active_conns})>"


class LoadBalancer:
    def __init__(self, algorithm: str = "round_robin"):
        self.algorithm = algorithm.lower()
        self.servers: List[Server] = []
        self._rr_index = 0
        self._weighted_sequence: List[Server] = []
        self._wrr_index = 0

    def add_server(self, host: str, weight: int = 1) -> Server:
        server = Server(host, weight)
        self.servers.append(server)
        self._recalculate_weighted_pool()
        return server

    def remove_server(self, host: str) -> None:
        self.servers = [s for s in self.servers if s.host != host]
        self._recalculate_weighted_pool()

    def set_health(self, host: str, is_healthy: bool) -> None:
        for s in self.servers:
            if s.host == host:
                s.healthy = is_healthy
        self._recalculate_weighted_pool()

    def _recalculate_weighted_pool(self) -> None:
        """Rebuilds weighted sequence: server with weight 3 appears 3 times."""
        seq = []
        for s in self.servers:
            if s.healthy:
                seq.extend([s] * s.weight)
        self._weighted_sequence = seq

    def get_server(self) -> Server:
        """Selects a backend server based on the configured algorithm."""
        healthy_servers = [s for s in self.servers if s.healthy]
        if not healthy_servers:
            raise RuntimeError("503 Service Unavailable: No healthy upstream servers in pool!")

        if self.algorithm == "round_robin":
            server = healthy_servers[self._rr_index % len(healthy_servers)]
            self._rr_index += 1
            return server

        elif self.algorithm == "weighted_round_robin":
            if not self._weighted_sequence:
                raise RuntimeError("503 Service Unavailable: No healthy weighted servers!")
            server = self._weighted_sequence[self._wrr_index % len(self._weighted_sequence)]
            self._wrr_index += 1
            return server

        elif self.algorithm == "least_connections":
            # Pick server with minimum active connections
            return min(healthy_servers, key=lambda s: s.active_conns)

        else:
            raise ValueError(f"Unknown load balancing algorithm: {self.algorithm}")


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    print("--- [Question 24 Test: Load Balancer Algorithms] ---")

    # 1. Round Robin Test
    print("\n1. Testing Round Robin:")
    lb_rr = LoadBalancer(algorithm="round_robin")
    lb_rr.add_server("web-01")
    lb_rr.add_server("web-02")
    lb_rr.add_server("web-03")

    for req_id in range(1, 7):
        target = lb_rr.get_server()
        print(f"   Request {req_id} -> {target.host}")

    # 2. Weighted Round Robin Test (web-01 weight 3, web-02 weight 1)
    print("\n2. Testing Weighted Round Robin (web-01=wt:3, web-02=wt:1):")
    lb_wrr = LoadBalancer(algorithm="weighted_round_robin")
    lb_wrr.add_server("web-01", weight=3)
    lb_wrr.add_server("web-02", weight=1)

    picks = [lb_wrr.get_server().host for _ in range(8)]
    print(f"   Selections across 8 requests: {picks}")
    print(f"   web-01 count: {picks.count('web-01')} (expected 6)")
    print(f"   web-02 count: {picks.count('web-02')} (expected 2)")

    # 3. Least Connections Test
    print("\n3. Testing Least Connections:")
    lb_lc = LoadBalancer(algorithm="least_connections")
    s1 = lb_lc.add_server("srv-01")
    s2 = lb_lc.add_server("srv-02")

    s1.active_conns = 15
    s2.active_conns = 2
    picked = lb_lc.get_server()
    print(f"   Chosen server: {picked.host} (active connections: {picked.active_conns})")

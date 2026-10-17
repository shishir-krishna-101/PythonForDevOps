#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 25: Multi-Threaded Producer-Consumer Task Worker Queue
================================================================================
Problem Statement:
You need to automate patch deployments across 5,000 servers. Running 5,000 threads
simultaneously crashes the OS (exhausts file descriptors / memory). Running them
sequentially takes 10 hours.

Write a thread-safe Producer-Consumer task worker pool using Python's standard library:
  1. Spawns a fixed pool of $W$ worker threads (e.g. 5 workers).
  2. Uses a synchronized, thread-safe queue (`queue.Queue`) to buffer jobs.
  3. Producers push host patching tasks into the queue.
  4. Workers fetch jobs, execute simulated patching, and mark tasks as done (`task_done()`).
  5. Implements the Sentinel / Poison Pill pattern (pushing `None` tokens) to
     cleanly shut down worker threads when all work is completed.
  6. Collects all job outcomes (success/failure) in a thread-safe results list.

--------------------------------------------------------------------------------
HOW TO THINK & SOLVE THIS USING ONLY OFFICIAL DOCS:
--------------------------------------------------------------------------------
1. Mental Model & Problem Decomposition:
   - Why not raw lists? Raw Python lists are NOT thread-safe for pop/push without manual locks.
   - `queue.Queue` provides thread-safe FIFO queuing with built-in condition variables.
   - `queue.get()` blocks until an item is available.
   - `queue.task_done()` and `queue.join()` allow the main thread to wait until every job finishes.

2. Official Docs Reference:
   - Module: `queue` -> `docs.python.org/3/library/queue.html`
   - Read the canonical Producer-Consumer recipe in the queue docs:
     * `q = queue.Queue()`
     * `worker reads item = q.get()`
     * `worker signals q.task_done()`
     * `main thread calls q.join()`
   - Module: `threading` -> `docs.python.org/3/library/threading.html`
     * `threading.Thread(target=worker_fn, args=(...))`
     * `thread.start()`, `thread.join()`
================================================================================
"""

import time
import random
import queue
import threading
from typing import List, Dict, Any


# Sentinel token used to signal thread termination
POISON_PILL = None


def patch_worker(
    worker_id: int,
    task_queue: queue.Queue,
    results_list: List[Dict[str, Any]],
    results_lock: threading.Lock
):
    """
    Worker thread that continuously pulls tasks from the queue until receiving POISON_PILL.
    """
    while True:
        # Blocks until a task is available
        host = task_queue.get()

        # Check for shutdown signal
        if host is POISON_PILL:
            task_queue.task_done()
            break

        # Simulate patching operation
        time.sleep(random.uniform(0.05, 0.15))
        success = (random.random() > 0.1) # 90% success rate

        result = {
            "worker": worker_id,
            "host": host,
            "status": "SUCCESS" if success else "FAILED"
        }

        with results_lock:
            results_list.append(result)

        task_queue.task_done()


def execute_fleet_patching(hosts: List[str], num_workers: int = 4) -> List[Dict[str, Any]]:
    """
    Coordinates multi-threaded fleet execution using Producer-Consumer pattern.
    """
    task_queue = queue.Queue()
    results = []
    results_lock = threading.Lock()
    workers = []

    # 1. Spawn worker threads
    for i in range(num_workers):
        t = threading.Thread(
            target=patch_worker,
            args=(i + 1, task_queue, results, results_lock),
            daemon=True
        )
        t.start()
        workers.append(t)

    # 2. Producer: Enqueue all host tasks
    for host in hosts:
        task_queue.put(host)

    # 3. Wait for all tasks to be processed
    task_queue.join()

    # 4. Push poison pills to cleanly stop worker threads
    for _ in range(num_workers):
        task_queue.put(POISON_PILL)

    for t in workers:
        t.join()

    return results


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    target_fleet = [f"k8s-node-{i:02d}.internal" for i in range(1, 16)]

    print(f"--- [Question 25 Test: Multi-Threaded Worker Queue] ---")
    print(f"Deploying patches across {len(target_fleet)} servers with 4 parallel workers...")

    start_time = time.perf_counter()
    outcomes = execute_fleet_patching(target_fleet, num_workers=4)
    total_time = time.perf_counter() - start_time

    print(f"\nExecution Finished in {total_time:.2f}s:")
    success_count = sum(1 for o in outcomes if o["status"] == "SUCCESS")
    print(f"  Total Nodes Processed : {len(outcomes)}")
    print(f"  Successful Patches    : {success_count}")
    print(f"  Failed Patches        : {len(outcomes) - success_count}")

    print("\nSample Task Dispatches:")
    for o in outcomes[:5]:
        print(f"  [Worker {o['worker']}] -> {o['host']:<22} | Status: {o['status']}")

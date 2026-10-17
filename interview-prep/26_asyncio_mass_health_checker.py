#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 26: High-Scale Non-Blocking AsyncIO Health Scanner
================================================================================
Problem Statement:
Probing 5,000 microservice health endpoints using traditional threads requires
spawning 5,000 OS threads or waiting minutes. Threads consume 8MB of stack RAM each
and trigger heavy CPU context switching.

Write an asynchronous Python function `async_probe_all(urls, max_concurrency=100, timeout=3.0)`
that:
  1. Uses Python's native `asyncio` event loop.
  2. Uses `asyncio.Semaphore` to cap maximum in-flight concurrent sockets (e.g. max 50).
  3. Uses `httpx.AsyncClient` or standard `asyncio.open_connection` to probe endpoints non-blockingly.
  4. Returns the response status code, latency (ms), and handles timeouts without crashing.
  5. Demonstrates the difference between OS thread concurrency and Event Loop cooperative multitasking.

--------------------------------------------------------------------------------
HOW TO THINK & SOLVE THIS USING ONLY OFFICIAL DOCS:
--------------------------------------------------------------------------------
1. Mental Model & Problem Decomposition:
   - Synchronous `requests.get()` blocks the OS thread while waiting for network packets.
   - `async / await` frees up the single thread to send 1,000 other HTTP requests while
     waiting for kernel socket I/O events (epoll on Linux, kqueue on macOS, IOCP on Windows).
   - Unbounded concurrency crashes servers; an `asyncio.Semaphore(N)` acts as a bouncer
     allowing only $N$ coroutines to execute the network call at once.

2. Official Docs Reference:
   - Module: `asyncio` -> `docs.python.org/3/library/asyncio.html`
   - Look up:
     * `asyncio.gather(*tasks)`: Runs multiple coroutines concurrently and collects results.
     * `asyncio.Semaphore(value)`: Controls access to finite resources.
     * `asyncio.run(main())`: High-level entry point to run an async event loop.
================================================================================
"""

import time
import asyncio
from typing import List, Dict, Any

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


async def probe_endpoint_async(
    client: Any,
    url: str,
    semaphore: asyncio.Semaphore,
    timeout: float = 3.0
) -> Dict[str, Any]:
    """
    Asynchronously probes a single URL guarded by a concurrency semaphore.
    """
    async with semaphore:
        start = time.perf_counter()
        try:
            if HTTPX_AVAILABLE and client:
                resp = await client.get(url, timeout=timeout)
                status = resp.status_code
            else:
                # Simulated async network delay for offline testing
                await asyncio.sleep(0.05)
                status = 200

            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            return {"url": url, "status": status, "latency_ms": latency_ms, "healthy": status == 200}

        except Exception as e:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            return {"url": url, "status": None, "latency_ms": latency_ms, "healthy": False, "error": str(e)}


async def sweep_all_endpoints(urls: List[str], max_concurrency: int = 10) -> List[Dict[str, Any]]:
    """
    Orchestrates mass concurrent non-blocking probing.
    """
    semaphore = asyncio.Semaphore(max_concurrency)

    if HTTPX_AVAILABLE:
        async with httpx.AsyncClient(verify=False) as client:
            tasks = [probe_endpoint_async(client, url, semaphore) for url in urls]
            return await asyncio.gather(*tasks)
    else:
        tasks = [probe_endpoint_async(None, url, semaphore) for url in urls]
        return await asyncio.gather(*tasks)


def run_mass_probe(urls: List[str]) -> List[Dict[str, Any]]:
    """Entry point to launch the asyncio event loop synchronously."""
    return asyncio.run(sweep_all_endpoints(urls, max_concurrency=5))


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    test_urls = [
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/204",
        "https://httpbin.org/status/404",
        "https://httpbin.org/status/500",
        "https://httpbin.org/delay/1",
        "https://api.github.com"
    ]

    print("--- [Question 26 Test: AsyncIO Mass Health Prober] ---")
    print(f"Probing {len(test_urls)} endpoints non-blockingly using AsyncIO...")

    start_time = time.perf_counter()
    results = run_mass_probe(test_urls)
    total_duration = time.perf_counter() - start_time

    print(f"\nAll probes completed in {total_duration:.2f}s:")
    for r in results:
        status_tag = "[OK]  " if r["healthy"] else "[FAIL]"
        print(f"  {status_tag} {r['url']:<32} | Latency: {r['latency_ms']:>6.1f} ms | Status: {r['status']}")

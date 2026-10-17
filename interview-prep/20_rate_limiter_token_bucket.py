#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 20: Thread-Safe Token Bucket Rate Limiter
================================================================================
Problem Statement:
In DevOps automation (e.g. interacting with GitHub APIs, Slack webhooks, AWS APIs),
scripts must respect remote rate limits (e.g., max 5 requests per second, with
bursts up to 10 requests).

Write a thread-safe Python class `TokenBucketRateLimiter` that:
  1. Implements the classic Token Bucket algorithm:
     - `capacity`: Maximum number of tokens the bucket can hold (burst limit).
     - `refill_rate`: Rate at which tokens are added back to the bucket (tokens/sec).
  2. Provides a method `consume(tokens=1)`:
     - Returns `True` and deducts tokens if sufficient tokens are available.
     - Returns `False` immediately if not enough tokens are present (non-blocking).
  3. Provides a blocking method `acquire(tokens=1, timeout=5.0)`:
     - Waits/sleeps until enough tokens have refilled, or raises `TimeoutError`
       if the timeout expires.
  4. Is completely thread-safe using `threading.Lock`.

Constraints:
  - Must calculate token refills lazily on access based on elapsed time:
      `elapsed = now - last_refill_time`
      `new_tokens = elapsed * refill_rate`
  - High numerical precision using `time.monotonic()`.
================================================================================
"""

import time
import threading
from typing import Optional


class TokenBucketRateLimiter:
    """
    Thread-safe lazy-refill Token Bucket Rate Limiter.
    """
    def __init__(self, capacity: int = 10, refill_rate: float = 2.0):
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate) # Tokens added per second
        self.tokens = float(capacity)
        self.last_refill_time = time.monotonic()
        self.lock = threading.Lock()

    def _refill(self) -> None:
        """Refills tokens based on elapsed monotonic time."""
        now = time.monotonic()
        elapsed = now - self.last_refill_time
        if elapsed > 0:
            added_tokens = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + added_tokens)
            self.last_refill_time = now

    def consume(self, tokens: int = 1) -> bool:
        """
        Attempts to consume `tokens` immediately without blocking.
        Returns True if successful, False otherwise.
        """
        with self.lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def acquire(self, tokens: int = 1, timeout: float = 5.0) -> bool:
        """
        Blocks and waits until `tokens` are available or timeout expires.
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self.lock:
                self._refill()
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True

                # Calculate minimum wait time for remaining tokens
                missing_tokens = tokens - self.tokens
                wait_time = missing_tokens / self.refill_rate

            # Sleep outside the lock so other threads can operate
            sleep_duration = min(wait_time, 0.05)
            time.sleep(sleep_duration)

        raise TimeoutError(f"Could not acquire {tokens} token(s) within {timeout}s deadline.")


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    # Capacity = 3, Refill = 2 tokens/sec
    limiter = TokenBucketRateLimiter(capacity=3, refill_rate=2.0)

    print("--- [Question 20 Test: Token Bucket Rate Limiter] ---")
    print("1. Rapid burst of 5 requests on capacity=3:")
    for i in range(1, 6):
        allowed = limiter.consume(1)
        print(f"   Request {i} -> {'[ALLOWED]' if allowed else '[DROPPED - 429]'}")

    print("\n2. Waiting 1.0 second to allow refill...")
    time.sleep(1.0)

    print("3. Subsequent request after refill:")
    allowed = limiter.consume(1)
    print(f"   Request -> {'[ALLOWED]' if allowed else '[DROPPED]'}")

    print("\n4. Testing blocking acquire() method:")
    start_t = time.monotonic()
    limiter.acquire(2)
    elapsed = time.monotonic() - start_t
    print(f"   Acquired 2 tokens successfully after {elapsed:.2f}s wait.")

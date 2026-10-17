#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 12: Custom @retry Decorator with Exponential Backoff & Jitter
================================================================================
Problem Statement:
In distributed systems and cloud automation, transient failures (HTTP 429, 503,
temporary DNS timeouts) are inevitable. Hardcoding repetitive retry while-loops
clutters codebase logic.

Write a custom parameterized Python decorator:
  `@retry(max_attempts=3, initial_delay=0.5, backoff_factor=2.0, exceptions=(Exception,))`
that:
  1. Wraps any synchronous function and intercepts specified exception types.
  2. Implements Exponential Backoff:
       delay = initial_delay * (backoff_factor ** (attempt - 1))
  3. Injects Full Jitter (random uniform delay between 0 and computed delay)
     to prevent the "Thundering Herd" problem against rate-limited backends.
  4. Preserves the original function's name, docstring, and signature (`functools.wraps`).
  5. If all retry attempts are exhausted, re-raises the original exception with
     a descriptive error message.

Constraints:
  - Must not swallow exceptions outside the declared `exceptions` tuple.
  - Zero external dependencies (uses standard library `time`, `random`, `functools`).
================================================================================
"""

import time
import random
import functools
import logging
from typing import Callable, Any, Tuple, Type


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("retry_demo")


def retry(
    max_attempts: int = 3,
    initial_delay: float = 0.5,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    jitter: bool = True
):
    """
    Decorator that retries a function with exponential backoff and randomized jitter.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as err:
                    if attempt >= max_attempts:
                        logger.error(f"[RETRY EXHAUSTED] {func.__name__} failed after {max_attempts} attempts. Last error: {err}")
                        raise

                    # Compute backoff
                    base_delay = initial_delay * (backoff_factor ** (attempt - 1))
                    sleep_duration = random.uniform(0, base_delay) if jitter else base_delay

                    logger.warning(
                        f"[RETRY {attempt}/{max_attempts}] {func.__name__} raised {type(err).__name__}: '{err}'. "
                        f"Retrying in {sleep_duration:.2f}s..."
                    )
                    time.sleep(sleep_duration)
                    attempt += 1

        return wrapper
    return decorator


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    call_counter = {"count": 0}

    @retry(max_attempts=4, initial_delay=0.1, backoff_factor=2.0, exceptions=(ConnectionResetError,))
    def flaky_cloud_api():
        """Simulates an API call that fails twice before succeeding."""
        call_counter["count"] += 1
        if call_counter["count"] < 3:
            raise ConnectionResetError(f"Connection dropped on attempt {call_counter['count']}")
        return {"status": 200, "payload": "Database Cluster Ready"}

    print("--- [Question 12 Test: Custom @retry Decorator] ---")
    result = flaky_cloud_api()
    print(f"\nFinal Result: {result}")
    print(f"Total Invocations: {call_counter['count']}")
    print(f"Function Docstring Preserved? '{flaky_cloud_api.__doc__}'")

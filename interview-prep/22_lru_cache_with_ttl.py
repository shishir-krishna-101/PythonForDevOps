#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 22: Thread-Safe LRU Cache with Time-To-Live (TTL)
================================================================================
Problem Statement:
In cloud automation, fetching IAM temporary credentials (STS tokens), Vault secrets,
or resolving DNS records over the network is expensive. You need an in-memory cache
that:
  1. Limits memory by evicting the Least Recently Used (LRU) item when `capacity` is reached.
  2. Enforces Time-To-Live (TTL): Entries automatically expire after `ttl_seconds`.
  3. Provides:
     - `get(key)`: Returns value if present and unexpired; marks key as recently used.
                   Returns `None` if missing or expired.
     - `put(key, value)`: Stores key-value with current timestamp; evicts LRU if capacity full.
  4. Both `get()` and `put()` must operate in strictly O(1) time complexity.
  5. Is thread-safe using `threading.Lock`.

--------------------------------------------------------------------------------
HOW TO THINK & SOLVE THIS USING ONLY OFFICIAL DOCS:
--------------------------------------------------------------------------------
1. Mental Model & Problem Decomposition:
   - To achieve O(1) LRU eviction, you need two properties:
     a) O(1) key lookup -> Hash Map (dict).
     b) O(1) ordering update when a key is read/written -> Doubly Linked List.
   - Do you need to write a doubly linked list by hand? NO! Check the standard library.

2. Official Docs Reference:
   - Module: `collections` -> `docs.python.org/3/library/collections.html#collections.OrderedDict`
   - Look at the `OrderedDict` documentation:
     * `move_to_end(key, last=True)`: Moves an existing key to either the right or left end in O(1)!
     * `popitem(last=False)`: Pops and returns the first (oldest / LRU) item in O(1)!
   - Module: `time` -> `docs.python.org/3/library/time.html#time.monotonic`
     * Use `time.monotonic()` instead of `time.time()` because monotonic time never jumps backwards
       due to system clock NTP adjustments.

3. Step-by-Step Implementation Strategy:
   - Store entries as `key -> (value, expiry_timestamp)`.
   - On `get(key)`: If key exists, check if `now > expiry_timestamp`. If expired, delete key and return None.
     Otherwise, call `move_to_end(key)` and return value.
   - On `put(key, value)`: If key exists, update value and move to end. If new and full, call `popitem(last=False)`
     to evict the oldest item.
================================================================================
"""

import time
import threading
from collections import OrderedDict
from typing import Any, Optional


class TTLCache:
    """
    Thread-safe Least Recently Used (LRU) Cache with Time-To-Live (TTL) expiry.
    """
    def __init__(self, capacity: int = 100, default_ttl: float = 60.0):
        self.capacity = capacity
        self.default_ttl = default_ttl
        # OrderedDict maintains insertion/access order
        # Map: key -> (value, expire_at)
        self.cache: OrderedDict[str, Any] = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """O(1) retrieve key; evicts if expired; moves to most-recently-used."""
        with self.lock:
            if key not in self.cache:
                return None

            value, expire_at = self.cache[key]

            # Check TTL Expiration
            if time.monotonic() > expire_at:
                del self.cache[key]
                return None

            # Mark as most recently used (move to right end)
            self.cache.move_to_end(key)
            return value

    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """O(1) insert/update key; evicts LRU if capacity is exceeded."""
        ttl_duration = ttl if ttl is not None else self.default_ttl
        expire_at = time.monotonic() + ttl_duration

        with self.lock:
            if key in self.cache:
                self.cache[key] = (value, expire_at)
                self.cache.move_to_end(key)
                return

            # Check capacity before inserting new key
            if len(self.cache) >= self.capacity:
                # Evict oldest / least recently used (first item on left)
                evicted_key, _ = self.cache.popitem(last=False)

            self.cache[key] = (value, expire_at)

    def size(self) -> int:
        with self.lock:
            return len(self.cache)


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    print("--- [Question 22 Test: LRU Cache with TTL] ---")
    # Capacity: 2, TTL: 0.5s
    cache = TTLCache(capacity=2, default_ttl=0.5)

    # 1. Put k1 and k2
    cache.put("token:aws", "ASIA_MOCK_TOKEN_1")
    cache.put("token:vault", "s.vault_secret_2")

    print(f"Get 'token:aws': {cache.get('token:aws')}") # Accessing k1 makes it MRU, k2 is now LRU

    # 2. Put k3 -> should evict 'token:vault' (LRU)
    cache.put("token:k8s", "bearer_token_3")

    print(f"Get 'token:vault' (expected None, evicted): {cache.get('token:vault')}")
    print(f"Get 'token:aws' (expected present): {cache.get('token:aws')}")
    print(f"Get 'token:k8s' (expected present): {cache.get('token:k8s')}")

    # 3. Test TTL expiration
    print("\nWaiting 0.6s to test TTL expiration...")
    time.sleep(0.6)
    print(f"Get 'token:aws' after TTL (expected None): {cache.get('token:aws')}")

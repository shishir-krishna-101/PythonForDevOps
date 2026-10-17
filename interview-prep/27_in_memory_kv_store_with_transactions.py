#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 27: Transactional In-Memory Key-Value Store (Mini Redis)
================================================================================
Problem Statement:
Distributed configuration engines (etcd, Consul, ZooKeeper, Redis) rely on
transactional state consistency.

Design and implement an in-memory Key-Value store class `TransactionalKVStore` that:
  1. Supports standard data operations:
     - `set(key, value)`
     - `get(key) -> value or None`
     - `delete(key)`
  2. Supports nested ACID transactions:
     - `begin()`: Starts a new transaction block.
     - `commit()`: Permanently applies all changes made in the active transaction
                   to the parent level and closes the transaction.
     - `rollback()`: Discards all mutations made within the active transaction
                     block and restores state to when `begin()` was called.
  3. Supports nested transactions (calling `begin()` inside an existing transaction).
  4. Returns `False` or raises an exception if `commit()` or `rollback()` is called
     without an active transaction.

--------------------------------------------------------------------------------
HOW TO THINK & SOLVE THIS USING ONLY OFFICIAL DOCS:
--------------------------------------------------------------------------------
1. Mental Model & Problem Decomposition:
   - What data structure naturally represents nested scopes with LIFO rollback?
     **A Stack (`list` in Python)!**
   - Maintain a global/base dictionary `store`.
   - Maintain a transaction stack: `transaction_stack = []`.
   - Each transaction in the stack can be represented as a delta dictionary or a copy.
   - When inside a transaction:
     * Write operations mutate the current transaction's working copy.
     * `get()` checks the current transaction first, then falls back down the stack to base store.
     * `commit()` merges the top transaction changes into the level below it and pops.
     * `rollback()` simply pops the top transaction off the stack, abandoning all changes!
================================================================================
"""

from typing import Dict, Any, Optional, List


class TransactionalKVStore:
    def __init__(self):
        # Base permanent storage
        self.global_store: Dict[str, Any] = {}
        # Stack of transaction snapshots/working layers
        # Each layer is a dict where None value indicates a deleted key
        self.transaction_stack: List[Dict[str, Any]] = []

    def set(self, key: str, value: Any) -> None:
        """Sets a key-value pair in active transaction or global store."""
        if self.transaction_stack:
            # Record change in active top transaction layer
            self.transaction_stack[-1][key] = value
        else:
            self.global_store[key] = value

    def get(self, key: str) -> Optional[Any]:
        """Gets value, checking from innermost active transaction to global store."""
        # 1. Search top-down through active transaction layers
        for layer in reversed(self.transaction_stack):
            if key in layer:
                val = layer[key]
                # Sentinel None marks a deleted key
                return None if val is None else val

        # 2. Fallback to global store
        return self.global_store.get(key, None)

    def delete(self, key: str) -> bool:
        """Deletes key. If in transaction, marks key with deletion sentinel."""
        if self.get(key) is None:
            return False

        if self.transaction_stack:
            # Mark as deleted in current transaction
            self.transaction_stack[-1][key] = None
        else:
            del self.global_store[key]
        return True

    def begin(self) -> None:
        """Starts a new transaction layer."""
        self.transaction_stack.append({})

    def commit(self) -> bool:
        """Commits changes in active transaction to parent layer or global store."""
        if not self.transaction_stack:
            return False

        active_layer = self.transaction_stack.pop()

        if self.transaction_stack:
            # Merge into parent transaction layer
            self.transaction_stack[-1].update(active_layer)
        else:
            # Merge into global store
            for k, v in active_layer.items():
                if v is None:
                    self.global_store.pop(k, None)
                else:
                    self.global_store[k] = v
        return True

    def rollback(self) -> bool:
        """Discards active transaction mutations."""
        if not self.transaction_stack:
            return False

        # Simply discard the top transaction layer
        self.transaction_stack.pop()
        return True


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    kv = TransactionalKVStore()
    print("--- [Question 27 Test: Transactional KV Store] ---")

    # 1. Base operations
    kv.set("cluster_name", "eks-prod-alpha")
    kv.set("node_count", 10)
    print(f"Base State: cluster_name={kv.get('cluster_name')}, node_count={kv.get('node_count')}")

    # 2. Begin transaction and mutate
    print("\nStarting Transaction 1 (BEGIN)...")
    kv.begin()
    kv.set("node_count", 25)
    kv.set("new_feature", "canary_enabled")
    print(f"  Inside Tx: node_count={kv.get('node_count')} (expected 25)")
    print(f"  Inside Tx: new_feature={kv.get('new_feature')}")

    # 3. Rollback
    print("Rolling back Transaction 1 (ROLLBACK)...")
    kv.rollback()
    print(f"  After Rollback: node_count={kv.get('node_count')} (expected 10)")
    print(f"  After Rollback: new_feature={kv.get('new_feature')} (expected None)")

    # 4. Nested Transactions with Commit
    print("\nTesting Nested Transactions (Tx1 -> Tx2):")
    kv.begin() # Tx1
    kv.set("env", "staging")

    kv.begin() # Tx2 (nested)
    kv.set("env", "production")
    print(f"  Inside Nested Tx2: env={kv.get('env')} (expected production)")
    kv.commit() # Commit Tx2 into Tx1

    print(f"  After Nested Tx2 Commit, in Tx1: env={kv.get('env')} (expected production)")
    kv.commit() # Commit Tx1 to global store

    print(f"Final Global State: env={kv.get('env')} (expected production)")

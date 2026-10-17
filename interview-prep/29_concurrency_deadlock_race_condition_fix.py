#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 29: Live Debugging — Race Condition & Deadlock Elimination
================================================================================
Problem Statement:
In SRE / Systems Engineer live coding interviews (Google SRE, Meta Production Engineer),
you are frequently given buggy multi-threaded code and asked to:
  1. Identify why it produces incorrect results (Race Conditions).
  2. Identify why threads freeze indefinitely (Deadlocks).
  3. Refactor and fix the implementation to guarantee thread safety and high throughput.

Scenario:
Multiple background threads concurrently transfer cloud compute credits between
two AWS accounts (`account_a` and `account_b`).
- BUG 1 (Race Condition): Balances are modified without atomic locking, resulting in lost updates.
- BUG 2 (Deadlock): Thread 1 locks A then B; Thread 2 locks B then A (Circular lock wait).

Refactor the class `SecureAccountTransfer` using lock acquisition ordering to
guarantee zero deadlocks and 100% balance consistency.

--------------------------------------------------------------------------------
HOW TO THINK & SOLVE THIS USING ONLY OFFICIAL DOCS:
--------------------------------------------------------------------------------
1. Mental Model & Problem Decomposition:
   - What causes race conditions?
     `balance += amount` is NOT atomic in Python bytecode (it compiles to LOAD_FAST,
     BINARY_ADD, STORE_FAST). If a context switch occurs midway, values get overwritten!
   - What causes deadlocks?
     Coffman Conditions: Specifically, "Circular Wait". If two locks are acquired in
     inconsistent order across threads, a deadlock occurs.
   - **The Fix: Consistent Global Lock Ordering**:
     Always acquire locks in a globally deterministic order (e.g., sort account IDs
     lexicographically: `lock(min(id1, id2))` first, then `lock(max(id1, id2))`).

2. Official Docs Reference:
   - Module: `threading` -> `docs.python.org/3/library/threading.html`
   - Read about `threading.Lock()` and context manager support (`with lock:`).
================================================================================
"""

import time
import threading
from typing import Dict


class Account:
    def __init__(self, account_id: str, balance: int):
        self.account_id = account_id
        self.balance = balance
        self.lock = threading.Lock()


class SecureTransferService:
    """
    Thread-safe transfer service protected against Race Conditions and Deadlocks.
    """
    @staticmethod
    def transfer(source: Account, target: Account, amount: int) -> bool:
        if source.account_id == target.account_id:
            return False

        # DEADLOCK PREVENTION VIA GLOBAL LOCK ORDERING:
        # Always acquire the lock with smaller ID first, then larger ID.
        first_lock, second_lock = (
            (source.lock, target.lock)
            if source.account_id < target.account_id
            else (target.lock, source.lock)
        )

        with first_lock:
            with second_lock:
                if source.balance < amount:
                    return False

                source.balance -= amount
                target.balance += amount
                return True


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    print("--- [Question 29 Test: Race Condition & Deadlock Elimination] ---")

    acc1 = Account("aws-acc-001", 10000)
    acc2 = Account("aws-acc-002", 10000)
    INITIAL_TOTAL = acc1.balance + acc2.balance

    print(f"Initial Total Capital: ${INITIAL_TOTAL} (Acc1: ${acc1.balance}, Acc2: ${acc2.balance})")

    # Launch 20 concurrent threads transferring money back and forth rapidly
    threads = []
    for i in range(500):
        t1 = threading.Thread(target=SecureTransferService.transfer, args=(acc1, acc2, 10))
        t2 = threading.Thread(target=SecureTransferService.transfer, args=(acc2, acc1, 10))
        threads.extend([t1, t2])

    print(f"Launching {len(threads)} concurrent transfer operations...")
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    FINAL_TOTAL = acc1.balance + acc2.balance
    print(f"\nFinal Total Capital  : ${FINAL_TOTAL} (Acc1: ${acc1.balance}, Acc2: ${acc2.balance})")
    print(f"Balance Conservation : {'[VERIFIED 100% CONSISTENT]' if FINAL_TOTAL == INITIAL_TOTAL else '[FAILED - RACE CONDITION]'}")
    print(f"Deadlock Occurred    : None (Execution completed smoothly)")

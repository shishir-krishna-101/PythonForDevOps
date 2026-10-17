#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 30: Standard 5-Field Cron Expression Parser & Matcher
================================================================================
Problem Statement:
In Kubernetes CronJobs, Linux crontab, and CI/CD scheduled triggers, automated
jobs run based on a standard 5-part cron expression:
  `* * * * *` -> `[minute] [hour] [day_of_month] [month] [day_of_week]`

Write a Python class `CronParser` that parses standard 5-field cron strings
without external libraries and determines whether a job should run at a given
`datetime`:
  1. Supports standard cron syntax:
     - Wildcard: `*` (every value in field range)
     - Exact numbers: `5`
     - Commas: `1,15,30`
     - Ranges: `1-5`
     - Step values: `*/15`, `0-30/10`
  2. Field ranges:
     - minute: 0 - 59
     - hour: 0 - 23
     - day of month: 1 - 31
     - month: 1 - 12
     - day of week: 0 - 6 (0 = Sunday, 6 = Saturday)
  3. Provides method `matches(dt: datetime) -> bool`:
     Returns `True` if the provided datetime satisfies the cron schedule.

--------------------------------------------------------------------------------
HOW TO THINK & SOLVE THIS USING ONLY OFFICIAL DOCS:
--------------------------------------------------------------------------------
1. Mental Model & Problem Decomposition:
   - Split expression by whitespace into 5 components.
   - For each field, expand the string expression into a `Set[int]` of allowed values.
     * `*` -> full set of numbers from `min_val` to `max_val`.
     * `*/15` -> every 15th number from 0 to 59: `set(range(0, 60, 15))`.
     * `1-5` -> range of numbers: `set(range(1, 6))`.
     * `1,15` -> split by comma: `set([1, 15])`.
   - Matching a datetime simply checks whether:
     `dt.minute in allowed_minutes and dt.hour in allowed_hours and ...`
   - O(1) set membership check!

2. Official Docs Reference:
   - Module: `datetime` -> `docs.python.org/3/library/datetime.html`
   - Look up attributes of `datetime.datetime`: `.minute`, `.hour`, `.day`, `.month`, and `.weekday()`.
     (Note: Python's `dt.weekday()` is 0=Monday, so map accordingly or use standard cron convention).
================================================================================
"""

from datetime import datetime
from typing import Set, List


class CronParser:
    """
    Standard 5-field Cron parser supporting wildcards, ranges, lists, and steps.
    """
    FIELD_LIMITS = [
        (0, 59),  # minute
        (0, 23),  # hour
        (1, 31),  # day of month
        (1, 12),  # month
        (0, 6)    # day of week (0=Sunday, 6=Saturday)
    ]

    def __init__(self, cron_expression: str):
        self.raw_expression = cron_expression.strip()
        parts = self.raw_expression.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression '{cron_expression}'. Expected 5 fields.")

        self.allowed_minutes = self._parse_field(parts[0], 0, 59)
        self.allowed_hours = self._parse_field(parts[1], 0, 23)
        self.allowed_days = self._parse_field(parts[2], 1, 31)
        self.allowed_months = self._parse_field(parts[3], 1, 12)
        self.allowed_dows = self._parse_field(parts[4], 0, 6)

    def _parse_field(self, field_str: str, min_val: int, max_val: int) -> Set[int]:
        """Expands a cron field token into a set of allowed integer values."""
        allowed: Set[int] = set()

        for token in field_str.split(","):
            token = token.strip()
            # Step handling (e.g. */15 or 1-30/5)
            step = 1
            if "/" in token:
                base_part, step_str = token.split("/", 1)
                step = int(step_str)
            else:
                base_part = token

            # Range or Wildcard handling
            if base_part == "*":
                allowed.update(range(min_val, max_val + 1, step))
            elif "-" in base_part:
                start_str, end_str = base_part.split("-", 1)
                start_val, end_val = int(start_str), int(end_str)
                allowed.update(range(start_val, end_val + 1, step))
            else:
                allowed.add(int(base_part))

        return allowed

    def matches(self, dt: datetime) -> bool:
        """
        Returns True if the datetime matches the cron schedule.
        """
        # Map Python datetime weekday (0=Monday...6=Sunday) to standard Cron (0=Sunday...6=Saturday)
        # Python weekday: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
        cron_dow = (dt.weekday() + 1) % 7

        return (
            dt.minute in self.allowed_minutes and
            dt.hour in self.allowed_hours and
            dt.day in self.allowed_days and
            dt.month in self.allowed_months and
            cron_dow in self.allowed_dows
        )


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    print("--- [Question 30 Test: Cron Expression Parser] ---")

    # Cron: Every 15 minutes past hour 2 and 3 on weekdays (Mon-Fri)
    # cron: "*/15 2,3 * * 1-5"
    expr = "*/15 2,3 * * 1-5"
    parser = CronParser(expr)

    print(f"Cron Expression: '{expr}'")
    print(f"Allowed Minutes: {sorted(list(parser.allowed_minutes))}")
    print(f"Allowed Hours  : {sorted(list(parser.allowed_hours))}")
    print(f"Allowed DOWs   : {sorted(list(parser.allowed_dows))} (1=Mon ... 5=Fri)")

    # Test Case 1: Wednesday at 02:30 -> Should Match
    dt_match = datetime(2026, 10, 21, 2, 30) # Oct 21, 2026 is a Wednesday
    print(f"\nTest 1: {dt_match} (Wed 02:30) -> Matches? {parser.matches(dt_match)} (Expected True)")

    # Test Case 2: Wednesday at 02:33 -> Should Not Match (not a 15 min step)
    dt_no_match = datetime(2026, 10, 21, 2, 33)
    print(f"Test 2: {dt_no_match} (Wed 02:33) -> Matches? {parser.matches(dt_no_match)} (Expected False)")

    # Test Case 3: Sunday at 02:30 -> Should Not Match (Sunday is weekend)
    dt_weekend = datetime(2026, 10, 25, 2, 30) # Oct 25, 2026 is a Sunday
    print(f"Test 3: {dt_weekend} (Sun 02:30) -> Matches? {parser.matches(dt_weekend)} (Expected False)")

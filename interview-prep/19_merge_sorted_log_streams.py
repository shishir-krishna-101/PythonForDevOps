#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 19: K-Way Merge Sorted Log Streams with O(1) Memory
================================================================================
Problem Statement:
You have multiple large, chronologically sorted log files generated across
distributed application servers (e.g. `server1.log`, `server2.log`, `server3.log`).
Each log line begins with an ISO-8601 timestamp: `YYYY-MM-DDTHH:MM:SSZ`.

Write a Python generator function `merge_sorted_log_streams(file_paths)` that:
  1. Merges the lines from all input files into a single chronologically sorted stream.
  2. Does NOT load the entire content of all files into memory (which would cause OOM).
  3. Uses a Min-Heap (`heapq`) to maintain only ONE line in memory per file at any
     given time (K-way merge pattern).
  4. Memory Complexity: O(K) where K is the number of files, independent of file size.
  5. Time Complexity: O(N * log K) where N is the total number of lines across all files.

Constraints:
  - Input files are already sorted individually by timestamp.
  - Gracefully handle files of unequal lengths or empty files.
================================================================================
"""

import heapq
import tempfile
from typing import List, Generator, Tuple


def parse_timestamp_from_line(line: str) -> str:
    """Extracts timestamp prefix (first whitespace-separated token)."""
    return line.split(" ", 1)[0]


def merge_sorted_log_streams(file_paths: List[str]) -> Generator[str, None, None]:
    """
    K-Way merge using Python's heapq algorithm.
    Yields sorted lines one by one.
    """
    # Open all file pointers
    open_files = [open(path, "r", encoding="utf-8") for path in file_paths]
    min_heap = []

    try:
        # Initialize heap with the first line from each file
        for file_idx, f in enumerate(open_files):
            line = f.readline()
            if line:
                timestamp = parse_timestamp_from_line(line.strip())
                # Heap item: (timestamp, file_index, line_content)
                heapq.heappush(min_heap, (timestamp, file_idx, line.strip()))

        # Extract smallest timestamp from heap and refill from corresponding file
        while min_heap:
            timestamp, file_idx, line = heapq.heappop(min_heap)
            yield line

            # Read next line from the file that just yielded
            next_line = open_files[file_idx].readline()
            if next_line:
                next_ts = parse_timestamp_from_line(next_line.strip())
                heapq.heappush(min_heap, (next_ts, file_idx, next_line.strip()))

    finally:
        # Ensure all file descriptors are closed
        for f in open_files:
            f.close()


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    import os

    # Create 3 temporary log files
    with tempfile.TemporaryDirectory() as tmpdir:
        f1_path = os.path.join(tmpdir, "srv1.log")
        f2_path = os.path.join(tmpdir, "srv2.log")
        f3_path = os.path.join(tmpdir, "srv3.log")

        with open(f1_path, "w") as f:
            f.write("2026-10-17T10:00:01Z [srv1] Booting kernel\n")
            f.write("2026-10-17T10:00:04Z [srv1] Network initialized\n")
            f.write("2026-10-17T10:00:09Z [srv1] Service listening\n")

        with open(f2_path, "w") as f:
            f.write("2026-10-17T10:00:02Z [srv2] Booting kernel\n")
            f.write("2026-10-17T10:00:05Z [srv2] Database connection pool ready\n")
            f.write("2026-10-17T10:00:07Z [srv2] Redis cache warmup complete\n")

        with open(f3_path, "w") as f:
            f.write("2026-10-17T10:00:03Z [srv3] Ingress gateway ready\n")
            f.write("2026-10-17T10:00:08Z [srv3] Inbound traffic routing enabled\n")

        print("--- [Question 19 Test: K-Way Merge Sorted Log Streams] ---")
        merged_stream = merge_sorted_log_streams([f1_path, f2_path, f3_path])

        for line in merged_stream:
            print(f"  {line}")

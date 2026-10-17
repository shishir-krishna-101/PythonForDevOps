#!/usr/bin/env python3
"""
================================================================================
INTERVIEW QUESTION 28: Sliding Window Log Spike & SLA Anomaly Detector
================================================================================
Problem Statement:
Site Reliability Engineering (SRE) alert engines monitor logs for sudden bursts
of errors within moving time windows (e.g., > 5 HTTP 500 errors within any 60-second window).

Write a Python function `detect_error_spikes(log_entries, window_seconds=60, threshold=5)`
that:
  1. Accepts a chronologically sorted list of log event tuples:
     `[(epoch_timestamp: int, status_code: int, endpoint: str), ...]`
  2. Implements a Sliding Window algorithm using `collections.deque` that maintains
     only the events occurring within the active `window_seconds`.
  3. Detects any instant where the number of HTTP 5xx errors in the sliding window
     reaches or exceeds `threshold`.
  4. Returns a list of alert events containing the window start timestamp, window
     end timestamp, error count, and offending endpoints.
  5. Operates in linear time O(N) where N is the number of events.

--------------------------------------------------------------------------------
HOW TO THINK & SOLVE THIS USING ONLY OFFICIAL DOCS:
--------------------------------------------------------------------------------
1. Mental Model & Problem Decomposition:
   - Why not a naive double loop? A double loop (for each event, scan all events in the next
     60 seconds) is O(N^2), which freezes when processing 1,000,000 events.
   - **Sliding Window with Deque**:
     * As you iterate through events by time $T$, append the event to the right of a `deque`.
     * Evict elements from the left of the `deque` whose timestamp is older than `T - window_seconds`.
     * Maintain a running count of 5xx errors in the active window.
     * Each element is added once and removed once -> Strictly O(N) time!

2. Official Docs Reference:
   - Module: `collections` -> `docs.python.org/3/library/collections.html#collections.deque`
   - Notice: `deque.append()` and `deque.popleft()` are guaranteed $O(1)$ operations,
     whereas `list.pop(0)` is $O(N)$.
================================================================================
"""

from collections import deque
from typing import List, Tuple, Dict, Any


def detect_error_spikes(
    log_events: List[Tuple[int, int, str]], # (timestamp, status, uri)
    window_seconds: int = 60,
    threshold: int = 3
) -> List[Dict[str, Any]]:
    """
    Sliding window error burst detector operating in strictly O(N) time.
    """
    window = deque()
    error_count_in_window = 0
    alerts = []
    last_alert_time = -1 # Prevent alert spamming for overlapping seconds

    for timestamp, status, uri in log_events:
        is_5xx = (500 <= status < 600)

        # 1. Add current event to right of window
        window.append((timestamp, is_5xx, uri))
        if is_5xx:
            error_count_in_window += 1

        # 2. Evict events outside the moving window from the left
        cutoff_time = timestamp - window_seconds
        while window and window[0][0] < cutoff_time:
            oldest_ts, oldest_is_5xx, oldest_uri = window.popleft()
            if oldest_is_5xx:
                error_count_in_window -= 1

        # 3. Check if threshold breached
        if error_count_in_window >= threshold:
            # Enforce 30s alert cooldown to avoid duplicate alert storms
            if timestamp - last_alert_time >= 30:
                endpoints_in_window = [e[2] for e in window if e[1]]
                alerts.append({
                    "alert_time": timestamp,
                    "window_start": window[0][0],
                    "window_end": timestamp,
                    "error_count": error_count_in_window,
                    "sample_endpoints": list(set(endpoints_in_window))
                })
                last_alert_time = timestamp

    return alerts


# ==============================================================================
# TEST SUITE / VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    # Simulate events: (timestamp_epoch, status_code, endpoint)
    # A burst of 500 errors occurs between t=100 and t=120
    test_stream = [
        (10, 200, "/index.html"),
        (25, 200, "/api/products"),
        (80, 200, "/health"),
        # Burst starts:
        (100, 500, "/api/checkout"),
        (105, 502, "/api/checkout"),
        (115, 503, "/api/payment"),
        (120, 500, "/api/checkout"), # 4 errors within 20s (window <= 60s) -> Alert!
        # Normal traffic resumes:
        (190, 200, "/index.html"),
        (210, 200, "/api/products")
    ]

    print("--- [Question 28 Test: Sliding Window Error Detector] ---")
    detected_alerts = detect_error_spikes(test_stream, window_seconds=60, threshold=3)

    print(f"Total SLA Breach Alerts Generated: {len(detected_alerts)}")
    for a in detected_alerts:
        print(f"\n[SRE INCIDENT ALERT TRIGGERED]")
        print(f"  * Detection Epoch : {a['alert_time']}s")
        print(f"  * Window Horizon  : {a['window_start']}s -> {a['window_end']}s ({a['window_end'] - a['window_start']}s duration)")
        print(f"  * 5xx Error Count : {a['error_count']} errors (Threshold >= 3)")
        print(f"  * Endpoints       : {', '.join(a['sample_endpoints'])}")

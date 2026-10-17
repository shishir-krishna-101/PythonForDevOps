#!/usr/bin/env python3
"""
07-error-handling-and-logging/logger_and_exceptions.py

Demonstrates:
- Setting up hierarchical loggers with formatters
- Custom DevOps domain exceptions
- Handling transient network retries with exponential backoff
- Writing structured JSON logs for observability platforms
"""

import sys
import time
import json
import logging
from typing import Callable, Any


# 1. Custom DevOps Exceptions Hierarchy
class DevOpsAutomationError(Exception):
    """Base class for automation exceptions."""
    pass


class TargetUnreachableError(DevOpsAutomationError):
    """Raised when an endpoint or host cannot be contacted."""
    pass


class DeploymentVerificationError(DevOpsAutomationError):
    """Raised when post-deployment assertions fail."""
    pass


# 2. Structured JSON Log Formatter
class JsonDevOpsFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_obj["traceback"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def configure_logger(name: str = "devops_engine") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Console Handler (STDOUT)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(JsonDevOpsFormatter())

    # Avoid duplicate handlers if re-executed
    if not logger.handlers:
        logger.addHandler(ch)

    return logger


def retry_with_backoff(
    operation: Callable[[], Any],
    max_retries: int = 3,
    initial_delay: float = 0.2,
    logger: logging.Logger = None
) -> Any:
    """
    Executes operation with exponential backoff on failure.
    """
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            return operation()
        except Exception as e:
            if logger:
                logger.warning(f"Attempt {attempt}/{max_retries} failed: {e}. Retrying in {delay:.2f}s...")
            if attempt == max_retries:
                if logger:
                    logger.error(f"All {max_retries} retry attempts exhausted.")
                raise
            time.sleep(delay)
            delay *= 2


def main():
    logger = configure_logger()
    logger.info("Initializing DevOps deployment engine...")

    attempt_counter = [0]

    def simulate_flaky_api():
        attempt_counter[0] += 1
        if attempt_counter[0] < 3:
            raise TargetUnreachableError("Connection refused by upstream gateway (502)")
        return {"status": "SUCCESS", "version": "v1.4.2"}

    try:
        logger.info("Testing flaky service call with retry backoff...")
        result = retry_with_backoff(simulate_flaky_api, max_retries=4, initial_delay=0.1, logger=logger)
        logger.info(f"Operation succeeded! Response: {result}")
    except DevOpsAutomationError as err:
        logger.exception(f"Fatal automation failure: {err}")
        sys.exit(1)

    logger.info("DevOps engine finished pipeline execution.")


if __name__ == "__main__":
    main()

import time
import random
import threading

# Simple global rate limiter (thread-safe)
_last_call_time = 0
_rate_lock = threading.Lock()

def rate_limited_call(min_interval=1.0):
    """
    Ensure at least `min_interval` seconds between calls.
    Thread-safe: blocks until enough time has passed.
    """
    global _last_call_time
    with _rate_lock:
        now = time.time()
        elapsed = now - _last_call_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        _last_call_time = time.time()


def retry(action, description, logger, retries=3, base_delay=2, jitter=True, min_interval=1.0):
    """
    Retry a callable action with exponential backoff and rate limiting.

    Args:
        action: A callable (function with no args or a lambda) to execute.
        description: String description for logging.
        logger: Logger instance for log_message().
        retries: Max number of attempts.
        base_delay: Initial delay in seconds for backoff.
        jitter: Add randomness to avoid synchronized retries.
        min_interval: Minimum seconds between calls (rate limit).

    Returns:
        The result of action() if successful, or None if all retries fail.
    """
    attempt = 0
    while attempt < retries:
        try:
            # Respect rate limit before each attempt
            rate_limited_call(min_interval=min_interval)
            return action()
        except Exception as e:
            attempt += 1
            if attempt >= retries:
                logger.log_message(f"{description} failed after {retries} attempts: {e}", "ERROR")
                return None
            delay = base_delay * (2 ** (attempt - 1))
            if jitter:
                delay = delay * (0.5 + random.random())  # 50–150% jitter
            logger.log_message(
                f"{description} failed (attempt {attempt}/{retries}), retrying in {delay:.1f}s...",
                "WARNING"
            )
            time.sleep(delay)

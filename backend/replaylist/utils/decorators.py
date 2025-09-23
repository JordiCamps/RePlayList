"""Decorator utilities used across the application.

Includes retry with exponential backoff and jitter, simple rate limiting, and
common HTTP error handling for API wrappers.
"""

import logging
from functools import wraps
from typing import Any, Callable, Tuple, Type


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
):
    """Retry a function on specified exceptions with exponential backoff.

    Args:
        max_retries: Maximum number of retries before failing.
        delay: Initial delay before the first retry (seconds).
        exceptions: Exception types to catch and retry.
        backoff_factor: Multiplier for the delay on each retry.
        max_delay: Upper bound for backoff delay.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception: BaseException | None = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:  # type: ignore[misc]
                    last_exception = e
                    if attempt < max_retries:
                        import time, random

                        calculated_delay = min(delay * (backoff_factor ** attempt), max_delay)
                        jitter = random.uniform(0.1, 0.3) * calculated_delay
                        actual_delay = calculated_delay + jitter
                        logging.getLogger('replaylist').warning(
                            f"Attempt {attempt + 1} failed: {e}. Retrying in {actual_delay:.2f}s..."
                        )
                        time.sleep(actual_delay)
                    else:
                        logging.getLogger('replaylist').error(
                            f"All {max_retries + 1} attempts failed. Last error: {e}"
                        )
                        raise last_exception  # type: ignore[misc]
        return wrapper
    return decorator


def rate_limit(calls_per_second: float = 1.0):
    """Throttle calls to a function to a maximum rate.

    Args:
        calls_per_second: Maximum allowed rate.
    """
    import time

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        last_called = [0.0]
        min_interval = 1.0 / calls_per_second

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            time_since_last_call = now - last_called[0]
            if time_since_last_call < min_interval:
                time.sleep(min_interval - time_since_last_call)
            last_called[0] = time.time()
            return func(*args, **kwargs)

        return wrapper

    return decorator


def handle_api_errors(func: Callable[..., Any]) -> Callable[..., Any]:
    """Handle common requests exceptions, deferring retries to callers.

    - 429 responses trigger a short wait to allow rate limit reset, then re-raise
    - 5xx responses are re-raised to allow external retry logic
    - Connection/timeout errors log and re-raise
    """
    import requests

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logging.getLogger('replaylist').warning("Rate limited. Waiting before retry...")
                import time

                time.sleep(5)
                raise
            if e.response.status_code >= 500:
                logging.getLogger('replaylist').warning(f"Server error {e.response.status_code}. Retrying...")
                raise
            raise
        except requests.exceptions.ConnectionError:
            logging.getLogger('replaylist').warning("Connection error. Retrying...")
            raise
        except requests.exceptions.Timeout:
            logging.getLogger('replaylist').warning("Request timeout. Retrying...")
            raise

    return wrapper



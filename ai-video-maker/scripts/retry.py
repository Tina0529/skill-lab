#!/usr/bin/env python3
"""Exponential backoff retry decorator with error classification."""

import functools
import random
import time


class RetryableError(Exception):
    """Error that can be retried (e.g., rate limit, temporary network issue)."""
    pass


class PermanentError(Exception):
    """Error that should NOT be retried (e.g., invalid API key, bad input)."""
    pass


def exponential_backoff(max_retries: int = 3,
                        base_delay: float = 2.0,
                        max_delay: float = 60.0,
                        jitter: bool = True,
                        retryable_exceptions: tuple = (RetryableError, ConnectionError,
                                                       TimeoutError, OSError)):
    """Decorator for exponential backoff retry.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap in seconds
        jitter: Add random jitter to prevent thundering herd
        retryable_exceptions: Exception types that should trigger retry

    Usage:
        @exponential_backoff(max_retries=3)
        def call_api():
            ...

        # Or with custom settings:
        @exponential_backoff(max_retries=5, base_delay=1.0, max_delay=30.0)
        def call_flaky_service():
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except PermanentError:
                    # Don't retry permanent errors
                    raise
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        if jitter:
                            delay += random.uniform(0, delay * 0.1)
                        print(f"  Retry {attempt + 1}/{max_retries} "
                              f"after {delay:.1f}s: {type(e).__name__}: {e}")
                        time.sleep(delay)
                    else:
                        raise
                except Exception:
                    # Unknown exceptions are not retried
                    raise

            raise last_exception  # Should not reach here, but just in case

        return wrapper
    return decorator


def retry_with_fallback(primary_fn, fallback_fn, max_retries: int = 3,
                        base_delay: float = 2.0):
    """Try primary function with retries, fall back to fallback_fn on exhaustion.

    Args:
        primary_fn: Callable to try first
        fallback_fn: Callable to use if primary exhausts retries
        max_retries: Max retries for primary
        base_delay: Initial delay between retries

    Returns:
        Result from primary_fn or fallback_fn
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            return primary_fn()
        except PermanentError:
            raise
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = min(base_delay * (2 ** attempt), 60.0)
                delay += random.uniform(0, delay * 0.1)
                print(f"  Retry {attempt + 1}/{max_retries} "
                      f"after {delay:.1f}s: {type(e).__name__}")
                time.sleep(delay)

    # Primary exhausted, try fallback
    print(f"  Primary failed after {max_retries} attempts: {last_exception}")
    print(f"  Using fallback...")
    return fallback_fn()

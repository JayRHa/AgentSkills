#!/usr/bin/env python3
"""retry.py — resilient retry + circuit breaker (pure stdlib).

Provides:
  * RetryPolicy           — config for attempts, backoff, jitter, deadline.
  * full_jitter_delay()   — exponential backoff with full jitter.
  * retry()               — decorator/wrapper for synchronous callables.
  * retry_async()         — wrapper for async callables (asyncio).
  * CircuitBreaker        — thread-safe closed/open/half-open breaker.

Design rules baked in:
  * Only RETRYABLE exceptions are retried (you specify which).
  * Exponential backoff with FULL JITTER, capped delay, bounded attempts.
  * Optional absolute DEADLINE so total time is bounded.
  * Optional honor_retry_after hook for 429/503 Retry-After.

Usage (decorator):
    from retry import RetryPolicy, retry

    policy = RetryPolicy(max_attempts=4, base=0.1, cap=5.0,
                         retryable=(TimeoutError, ConnectionError))

    @retry(policy)
    def fetch():
        ...

Usage (inline):
    result = retry(policy)(fetch)()

Usage (circuit breaker):
    cb = CircuitBreaker(failure_threshold=5, reset_timeout=10.0)
    with cb:                 # raises CircuitOpenError when open
        result = call()

Run the self-test / demo:
    python3 retry.py --demo
"""
from __future__ import annotations

import argparse
import functools
import random
import threading
import time
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Optional, Tuple, Type, TypeVar

T = TypeVar("T")


class RetryError(Exception):
    """Raised when retries are exhausted; .last_exception holds the cause."""

    def __init__(self, attempts: int, last_exception: BaseException):
        super().__init__(
            f"retries exhausted after {attempts} attempt(s): "
            f"{type(last_exception).__name__}: {last_exception}"
        )
        self.attempts = attempts
        self.last_exception = last_exception


class CircuitOpenError(Exception):
    """Raised by CircuitBreaker when the circuit is open (fail fast)."""


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base: float = 0.1          # seconds, initial backoff
    cap: float = 30.0          # seconds, max single delay
    retryable: Tuple[Type[BaseException], ...] = (Exception,)
    deadline: Optional[float] = None  # total seconds budget across all attempts
    # Hook: given the raised exception, return seconds to wait (e.g. Retry-After),
    # or None to use computed backoff.
    retry_after: Optional[Callable[[BaseException], Optional[float]]] = field(
        default=None
    )

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        if self.base < 0 or self.cap < 0:
            raise ValueError("base and cap must be non-negative")


def full_jitter_delay(attempt: int, base: float, cap: float,
                      rng: random.Random = random) -> float:
    """Exponential backoff with full jitter: random(0, min(cap, base*2**attempt)).

    `attempt` is 0-based (0 = delay before the 2nd try).
    """
    ceiling = min(cap, base * (2 ** attempt))
    return rng.uniform(0, ceiling)


def _should_retry(exc: BaseException, policy: RetryPolicy,
                  attempt: int, start: float) -> bool:
    if attempt + 1 >= policy.max_attempts:
        return False
    if not isinstance(exc, policy.retryable):
        return False
    if policy.deadline is not None and (time.monotonic() - start) >= policy.deadline:
        return False
    return True


def _delay_for(exc: BaseException, policy: RetryPolicy, attempt: int) -> float:
    if policy.retry_after is not None:
        hinted = policy.retry_after(exc)
        if hinted is not None:
            return min(policy.cap, max(0.0, hinted))
    return full_jitter_delay(attempt, policy.base, policy.cap)


def retry(policy: RetryPolicy) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that retries a sync callable per `policy`."""

    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs) -> T:
            start = time.monotonic()
            last: Optional[BaseException] = None
            for attempt in range(policy.max_attempts):
                try:
                    return fn(*args, **kwargs)
                except BaseException as exc:  # noqa: BLE001 - filtered below
                    last = exc
                    if not _should_retry(exc, policy, attempt, start):
                        if isinstance(exc, policy.retryable):
                            raise RetryError(attempt + 1, exc) from exc
                        raise  # non-retryable: surface immediately
                    time.sleep(_delay_for(exc, policy, attempt))
            assert last is not None
            raise RetryError(policy.max_attempts, last) from last

        return wrapper

    return decorator


async def retry_async(policy: RetryPolicy,
                      fn: Callable[..., Awaitable[T]],
                      *args, **kwargs) -> T:
    """Await an async callable with retry per `policy`."""
    import asyncio

    start = time.monotonic()
    last: Optional[BaseException] = None
    for attempt in range(policy.max_attempts):
        try:
            return await fn(*args, **kwargs)
        except BaseException as exc:  # noqa: BLE001 - filtered below
            last = exc
            if not _should_retry(exc, policy, attempt, start):
                if isinstance(exc, policy.retryable):
                    raise RetryError(attempt + 1, exc) from exc
                raise
            await asyncio.sleep(_delay_for(exc, policy, attempt))
    assert last is not None
    raise RetryError(policy.max_attempts, last) from last


class CircuitBreaker:
    """Thread-safe circuit breaker (closed / open / half-open).

    failure_threshold : consecutive failures before opening.
    reset_timeout     : seconds to stay open before a half-open trial.
    half_open_max     : trial calls allowed in half-open.
    counted_exceptions: which exceptions count as failures (default: all).
    """

    CLOSED, OPEN, HALF_OPEN = "closed", "open", "half_open"

    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 10.0,
                 half_open_max: int = 1,
                 counted_exceptions: Tuple[Type[BaseException], ...] = (Exception,)):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_max = half_open_max
        self.counted_exceptions = counted_exceptions
        self._state = self.CLOSED
        self._failures = 0
        self._opened_at = 0.0
        self._half_open_calls = 0
        self._lock = threading.Lock()

    @property
    def state(self) -> str:
        with self._lock:
            self._maybe_half_open()
            return self._state

    def _maybe_half_open(self) -> None:
        if (self._state == self.OPEN
                and time.monotonic() - self._opened_at >= self.reset_timeout):
            self._state = self.HALF_OPEN
            self._half_open_calls = 0

    def _on_success(self) -> None:
        with self._lock:
            self._failures = 0
            self._state = self.CLOSED
            self._half_open_calls = 0

    def _on_failure(self) -> None:
        with self._lock:
            self._failures += 1
            if (self._state == self.HALF_OPEN
                    or self._failures >= self.failure_threshold):
                self._state = self.OPEN
                self._opened_at = time.monotonic()

    def _allow(self) -> bool:
        with self._lock:
            self._maybe_half_open()
            if self._state == self.OPEN:
                return False
            if self._state == self.HALF_OPEN:
                if self._half_open_calls >= self.half_open_max:
                    return False
                self._half_open_calls += 1
            return True

    def __enter__(self) -> "CircuitBreaker":
        if not self._allow():
            raise CircuitOpenError("circuit is open")
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is not None and issubclass(exc_type, self.counted_exceptions):
            self._on_failure()
        elif exc_type is None:
            self._on_success()
        return False  # never suppress

    def call(self, fn: Callable[..., T], *args, **kwargs) -> T:
        with self:
            return fn(*args, **kwargs)


def _demo() -> None:
    """Self-contained demonstration of retry + circuit breaker."""
    print("== full_jitter_delay (base=0.1, cap=5) ==")
    for n in range(6):
        d = full_jitter_delay(n, 0.1, 5.0)
        print(f"  attempt {n}: 0 <= {d:.4f} <= {min(5.0, 0.1 * 2**n):.4f}")

    print("\n== retry: succeeds on 3rd attempt ==")
    calls = {"n": 0}

    policy = RetryPolicy(max_attempts=5, base=0.001, cap=0.01,
                         retryable=(ConnectionError,))

    @retry(policy)
    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise ConnectionError("transient")
        return "ok"

    print("  result:", flaky(), "after", calls["n"], "calls")

    print("\n== retry: non-retryable raises immediately ==")
    try:
        retry(policy)(lambda: (_ for _ in ()).throw(ValueError("bad input")))()
    except ValueError as e:
        print("  raised ValueError immediately (not retried):", e)

    print("\n== retry: exhaustion wraps in RetryError ==")
    try:
        retry(policy)(lambda: (_ for _ in ()).throw(ConnectionError("down")))()
    except RetryError as e:
        print(" ", e)

    print("\n== circuit breaker: trips then fails fast ==")
    cb = CircuitBreaker(failure_threshold=3, reset_timeout=0.05)
    for i in range(5):
        try:
            cb.call(lambda: (_ for _ in ()).throw(ConnectionError("boom")))
        except CircuitOpenError:
            print(f"  call {i}: FAST-FAIL (state={cb.state})")
        except ConnectionError:
            print(f"  call {i}: failed (state={cb.state})")
    time.sleep(0.06)
    print("  after cooldown, state:", cb.state, "(half_open -> trial allowed)")
    cb.call(lambda: "recovered")
    print("  trial succeeded, state:", cb.state)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Resilient retry + circuit breaker.")
    ap.add_argument("--demo", action="store_true", help="run the demonstration")
    args = ap.parse_args()
    if args.demo:
        _demo()
    else:
        ap.print_help()

import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List
from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    """
    Thread-safe in-memory sliding window rate limiter.
    Limits client requests by IP or client key.
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.lock = Lock()

    def check(self, key: str) -> None:
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds

        with self.lock:
            # Filter timestamps within current window
            valid_timestamps = [t for t in self.requests[key] if t > cutoff_time]
            if len(valid_timestamps) >= self.max_requests:
                retry_after = int(self.window_seconds - (current_time - valid_timestamps[0]))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {self.max_requests} attempts per {self.window_seconds}s. Try again in {max(1, retry_after)} seconds.",
                    headers={"Retry-After": str(max(1, retry_after))},
                )
            valid_timestamps.append(current_time)
            self.requests[key] = valid_timestamps

    def reset_for_test(self) -> None:
        """Utility for test suites."""
        with self.lock:
            self.requests.clear()


# Rate limiters for sensitive endpoints
login_rate_limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)
register_rate_limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60)
reset_rate_limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60)


def get_client_ip(request: Request) -> str:
    """Extracts client IP address safely."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

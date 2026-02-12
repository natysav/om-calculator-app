"""Thread-safe sliding window rate limiter.

Tracks requests per key (session/IP) and enforces a maximum number
of requests within a configurable time window. Exposes standard
X-RateLimit-* header values.
"""

import time
import threading
from collections import defaultdict


class RateLimiter:
    def __init__(self, max_requests=100, window_seconds=3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = defaultdict(list)
        self._lock = threading.Lock()

    def _cleanup(self, key):
        """Remove expired timestamps for the given key."""
        cutoff = time.time() - self.window_seconds
        self._requests[key] = [t for t in self._requests[key] if t > cutoff]

    def record_request(self, key):
        """Record a new request for the given key."""
        with self._lock:
            self._cleanup(key)
            self._requests[key].append(time.time())

    def is_rate_limited(self, key):
        """Check if the key has exceeded the rate limit."""
        with self._lock:
            self._cleanup(key)
            return len(self._requests[key]) >= self.max_requests

    def get_remaining(self, key):
        """Get the number of remaining requests for the key."""
        with self._lock:
            self._cleanup(key)
            return max(0, self.max_requests - len(self._requests[key]))

    def get_reset_time(self, key):
        """Get seconds until the oldest request in the window expires."""
        with self._lock:
            self._cleanup(key)
            if self._requests[key]:
                oldest = min(self._requests[key])
                return max(0, int(oldest + self.window_seconds - time.time()))
            return 0

    def get_headers(self, key):
        """Return a dict of standard rate limit headers for the given key."""
        with self._lock:
            self._cleanup(key)
            count = len(self._requests[key])
            remaining = max(0, self.max_requests - count)
            reset = 0
            if self._requests[key]:
                oldest = min(self._requests[key])
                reset = max(0, int(oldest + self.window_seconds - time.time()))
            return {
                "X-RateLimit-Limit": str(self.max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset),
            }

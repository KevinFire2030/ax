from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class RateLimiter:
    """Simple client-side rate limiter.

    - rpm: requests per minute
    - Ensures at least interval seconds between calls.
    """

    rpm: int
    _last_ts: float = 0.0

    @property
    def interval_sec(self) -> float:
        if self.rpm <= 0:
            return 0.0
        return 60.0 / float(self.rpm)

    def wait(self) -> None:
        if self.rpm <= 0:
            return
        now = time.time()
        sleep_sec = self.interval_sec - (now - self._last_ts)
        if sleep_sec > 0:
            time.sleep(sleep_sec)
        self._last_ts = time.time()

"""Retry delay shared by the two outbox queues (tech.md, 8.4 and 24.3)."""

import random


def backoff_seconds(n: int, rng: random.Random) -> float:
    """Delay before retry n (n >= 1): 30 s doubling up to an hour, with +-20% jitter."""
    if n < 1:
        raise ValueError("n starts at 1")
    # 30 * 2**7 already passes the 3600 cap; the clamp keeps big n cheap.
    return min(30 * (1 << min(n - 1, 7)), 3600) * rng.uniform(0.8, 1.2)

"""Tiny in-process sliding-window limiter for auth endpoints.
For multi-instance deployments swap the store for Redis (INCR + EXPIRE) — the interface stays the same."""
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

_hits: dict[str, deque] = defaultdict(deque)


def rate_limit(limit: int, window_s: int):
    async def dependency(request: Request):
        key = f"{request.url.path}:{request.client.host if request.client else 'unknown'}"
        now = time.monotonic()
        q = _hits[key]
        while q and now - q[0] > window_s:
            q.popleft()
        if len(q) >= limit:
            raise HTTPException(429, "Too many requests — please slow down and try again shortly.")
        q.append(now)

    return dependency

"""간단한 메모리 기반 레이트 리미터.

프로덕션 대규모 서비스라면 Redis를 사용하지만,
단일 인스턴스 OSINT 모니터에는 in-memory로 충분하다.
"""
from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request


class RateLimiter:
    """IP 기반 슬라이딩 윈도우 레이트 리미터."""

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def _get_client_ip(self, request: Request) -> str:
        return request.headers.get("x-forwarded-for", "").split(",")[0].strip() or (
            request.client.host if request.client else "unknown"
        )

    def _cleanup(self, ip: str, now: float):
        cutoff = now - self.window_seconds
        self._hits[ip] = [t for t in self._hits[ip] if t > cutoff]

    def check(self, request: Request) -> None:
        """요청이 제한을 초과하면 429 에러를 발생시킨다."""
        ip = self._get_client_ip(request)
        now = time.time()
        with self._lock:
            self._cleanup(ip, now)
            if len(self._hits[ip]) >= self.max_requests:
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many requests. Limit: {self.max_requests}/{self.window_seconds}s"
                )
            self._hits[ip].append(now)

    def periodic_cleanup(self):
        """주기적으로 만료된 엔트리를 정리하여 메모리 누수를 방지한다."""
        now = time.time()
        cutoff = now - self.window_seconds
        with self._lock:
            expired_ips = [ip for ip, hits in self._hits.items() if not hits or hits[-1] < cutoff]
            for ip in expired_ips:
                del self._hits[ip]


# 글로벌 인스턴스: 공개 API용 (분당 30회)
public_limiter = RateLimiter(max_requests=30, window_seconds=60)
# 피드백용 (분당 5회 — 스팸 방지)
feedback_limiter = RateLimiter(max_requests=5, window_seconds=60)

"""cockpit.sessions - bearer-token session management for the local cockpit."""
#
# 中文注释（仅注释，不改逻辑）
# ---------------------------
# 驾驶舱 bearer-token 会话管理：内存令牌、过期与轮换，纯函数可测。



from __future__ import annotations



import hashlib
import heapq
import secrets
from datetime import datetime
from typing import Final

from .models import CockpitValidationError



from src.coevo.timefmt import is_iso_utc_z, now_utc_iso_z


DEFAULT_MAX_SESSIONS: Final[int] = 64


DEFAULT_SESSION_TIMEOUT_SEC: Final[int] = 8 * 3600


def _iso_seconds(iso_z: str) -> float:
    parsed = datetime.fromisoformat(iso_z.replace("Z", "+00:00"))
    return parsed.timestamp()


class CockpitSessionManager:
    """In-memory bearer-token sessions with inactivity timeout.

    Only the SHA-256 digest of each raw token is stored; the raw token is
    returned exactly once from :meth:`create` and never retained.
    """

    def __init__(
        self,
        *,
        timeout_sec: int = DEFAULT_SESSION_TIMEOUT_SEC,
        max_sessions: int = DEFAULT_MAX_SESSIONS,
        max_session_age_sec: int | None = None,
    ) -> None:
        if not isinstance(timeout_sec, int) or timeout_sec <= 0:
            raise CockpitValidationError("session timeout_sec must be a positive integer")
        if not isinstance(max_sessions, int) or max_sessions < 1:
            raise CockpitValidationError("max_sessions must be a positive integer")
        if max_session_age_sec is not None and (
            not isinstance(max_session_age_sec, int) or max_session_age_sec <= 0
        ):
            raise CockpitValidationError(
                "max_session_age_sec must be a positive integer or None"
            )
        self._timeout_sec = timeout_sec
        self._max_sessions = max_sessions
        self._max_session_age_sec = max_session_age_sec
        self._sessions: dict[str, tuple[str, str, str]] = {}

    def create(self, now: str | None = None, subject: str = "") -> str:
        """Issue a fresh raw bearer token bound to an optional subject.

        Only the digest is retained; ``subject`` is an immutable identity
        claim (e.g. ``u.pm``) attached at issuance and never derivable from
        the raw token.
        """
        now = now or now_utc_iso_z()
        if not is_iso_utc_z(now):
            raise CockpitValidationError("now must be ISO-8601 UTC Z")
        if not isinstance(subject, str):
            raise CockpitValidationError("subject must be a string")
        token = secrets.token_urlsafe(32)
        self._sessions[self._digest(token)] = (now, now, subject)
        self._evict_if_needed()
        return token

    def validate(self, token: str, now: str | None = None) -> bool:
        """Return True and touch the session when the token is valid."""
        if not isinstance(token, str) or not token:
            return False
        now = now or now_utc_iso_z()
        if not is_iso_utc_z(now):
            return False
        digest = self._digest(token)
        entry = self._sessions.get(digest)
        if entry is None:
            return False
        created_at, last_seen, _subject = entry
        # Parse ``now`` once and reuse it for both checks (PERF-SESS-1).
        now_seconds = _iso_seconds(now)
        if (
            self._max_session_age_sec is not None
            and now_seconds - _iso_seconds(created_at) > self._max_session_age_sec
        ):
            del self._sessions[digest]
            return False
        if now_seconds - _iso_seconds(last_seen) > self._timeout_sec:
            del self._sessions[digest]
            return False
        self._sessions[digest] = (created_at, now, _subject)
        return True

    def subject(self, token: str, now: str | None = None) -> str:
        """Return the session subject, or ``""`` when the token is invalid."""
        if not isinstance(token, str) or not token:
            return ""
        if not self.validate(token, now=now):
            return ""
        entry = self._sessions.get(self._digest(token))
        return entry[2] if entry is not None else ""

    def revoke(self, token: str) -> bool:
        """Revoke a session by raw token (best effort, constant-ish cost)."""
        if not isinstance(token, str) or not token:
            return False
        return self._sessions.pop(self._digest(token), None) is not None

    def rotate(self, token: str, now: str | None = None) -> str:
        """Revoke an old token and issue a fresh one (token rotation)."""
        if not isinstance(token, str) or not token:
            raise CockpitValidationError("token must be a non-empty string")
        now = now or now_utc_iso_z()
        if not is_iso_utc_z(now):
            raise CockpitValidationError("now must be ISO-8601 UTC Z")
        entry = self._sessions.get(self._digest(token))
        if entry is None:
            raise CockpitValidationError("token is not a valid session")
        subject = entry[2]
        if not self.revoke(token):
            raise CockpitValidationError("token is not a valid session")
        return self.create(now=now, subject=subject)

    @property
    def session_count(self) -> int:
        return len(self._sessions)

    def subjects(self) -> tuple[str, ...]:
        """Sorted unique session subjects (privacy-safe: identities only)."""
        return tuple(sorted({entry[2] for entry in self._sessions.values()}))

    def _evict_if_needed(self) -> None:
        excess = len(self._sessions) - self._max_sessions
        if excess <= 0:
            return
        # Evict the ``excess`` oldest sessions by last_seen (PERF-SESS-1):
        # O(n log excess) instead of a full O(n log n) sort; excess is 1 in
        # the normal create path. The evicted set is identical to the previous
        # sorted-then-slice behavior.
        for digest in heapq.nsmallest(
            excess,
            self._sessions,
            key=lambda item: self._sessions[item][1],
        ):
            del self._sessions[digest]

    @staticmethod
    def _digest(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()


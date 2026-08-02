"""cockpit.sessions - bearer-token session management for the local cockpit."""



from __future__ import annotations



import hashlib
import re
import secrets
from datetime import UTC, datetime
from typing import Final

from .models import CockpitValidationError



_ISO_UTC_Z: Final[re.Pattern[str]] = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)


DEFAULT_MAX_SESSIONS: Final[int] = 64


DEFAULT_SESSION_TIMEOUT_SEC: Final[int] = 8 * 3600


def now_utc_iso_z() -> str:
    """Return the current UTC time as an ISO-8601 ``Z`` string."""
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


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
        self._sessions: dict[str, tuple[str, str]] = {}

    def create(self, now: str | None = None) -> str:
        """Issue a fresh raw bearer token; only its digest is retained."""
        now = now or now_utc_iso_z()
        if not _ISO_UTC_Z.match(now):
            raise CockpitValidationError("now must be ISO-8601 UTC Z")
        token = secrets.token_urlsafe(32)
        self._sessions[self._digest(token)] = (now, now)
        self._evict_if_needed()
        return token

    def validate(self, token: str, now: str | None = None) -> bool:
        """Return True and touch the session when the token is valid."""
        if not isinstance(token, str) or not token:
            return False
        now = now or now_utc_iso_z()
        if not _ISO_UTC_Z.match(now):
            return False
        digest = self._digest(token)
        entry = self._sessions.get(digest)
        if entry is None:
            return False
        created_at, last_seen = entry
        if (
            self._max_session_age_sec is not None
            and _iso_seconds(now) - _iso_seconds(created_at) > self._max_session_age_sec
        ):
            del self._sessions[digest]
            return False
        if _iso_seconds(now) - _iso_seconds(last_seen) > self._timeout_sec:
            del self._sessions[digest]
            return False
        self._sessions[digest] = (created_at, now)
        return True

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
        if not _ISO_UTC_Z.match(now):
            raise CockpitValidationError("now must be ISO-8601 UTC Z")
        if not self.revoke(token):
            raise CockpitValidationError("token is not a valid session")
        return self.create(now=now)

    @property
    def session_count(self) -> int:
        return len(self._sessions)

    def _evict_if_needed(self) -> None:
        if len(self._sessions) <= self._max_sessions:
            return
        for digest in sorted(
            self._sessions,
            key=lambda item: self._sessions[item][1],
        )[: len(self._sessions) - self._max_sessions]:
            del self._sessions[digest]

    @staticmethod
    def _digest(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()


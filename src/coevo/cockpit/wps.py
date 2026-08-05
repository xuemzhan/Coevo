"""US-7-AC-4 controlled WPS document launcher (Windows, fail-closed).

Opens workspace documents in WPS through a strictly validated path:

* only workspace-relative, non-traversing paths that pass the WPS
  allow-list are accepted;
* the resolved file must be a regular file inside the configured
  workspace root (symlinks/reparse points are refused);
* the executable is explicit (``COEVO_WPS_EXE`` or a configured path);
  a missing executable yields ``NOT_AVAILABLE`` instead of guessing;
* ``dry_run`` performs every check but never launches (test/CI mode);
* the launcher never accepts arbitrary launch parameters from a package.

No macro automation is performed; opening a document may still execute
macros inside WPS, which is the host application's documented risk.
"""
from __future__ import annotations

import enum
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from . import CockpitValidationError, WPSAllowList


DEFAULT_WPS_EXECUTABLE: str = "wps.exe"
MAX_DOCUMENT_BYTES: int = 64 * 1024 * 1024


class WpsLaunchDecision(enum.Enum):
    """Closed set of launch outcomes (fail-closed)."""

    OK = "ok"
    DENIED = "denied"
    NOT_AVAILABLE = "not_available"
    ERROR = "error"


@dataclass(frozen=True)
class WpsLaunchResult:
    decision: WpsLaunchDecision
    artifact_path_hash: str
    detail: str = ""
    returncode: int | None = None

    def to_mapping(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "artifact_path_hash": self.artifact_path_hash,
            "detail": self.detail,
            "returncode": self.returncode,
        }


class WpsLauncher:
    """Validated, controlled launcher for workspace documents."""

    def __init__(
        self,
        workspace_root: Path,
        *,
        wps_executable: str | None = None,
        dry_run: bool = False,
        runner: Callable[[str, Path], int] | None = None,
    ) -> None:
        if not isinstance(workspace_root, Path):
            raise CockpitValidationError("workspace_root must be a Path")
        try:
            self._root = workspace_root.resolve(strict=True)
        except OSError as exc:
            raise CockpitValidationError(
                f"workspace_root must exist ({exc})"
            ) from exc
        if not self._root.is_dir():
            raise CockpitValidationError("workspace_root must be a directory")
        self._executable = wps_executable or os.environ.get(
            "COEVO_WPS_EXE", DEFAULT_WPS_EXECUTABLE
        )
        if not isinstance(self._executable, str) or not self._executable:
            raise CockpitValidationError("wps_executable must be a non-empty string")
        self._dry_run = bool(dry_run)
        self._runner = runner

    @property
    def root(self) -> Path:
        return self._root

    def launch(self, artifact_path: str) -> WpsLaunchResult:
        """Validate the path, then launch the document in WPS."""
        digest = _hash_path(artifact_path)
        if (
            not isinstance(artifact_path, str)
            or not artifact_path
            or artifact_path.startswith("/")
            or "\\" in artifact_path
            or any(part in ("", ".", "..") for part in artifact_path.split("/"))
        ):
            return WpsLaunchResult(
                WpsLaunchDecision.DENIED, digest, "path is not a safe relative path"
            )
        if not WPSAllowList.is_allowed_extension(artifact_path):
            return WpsLaunchResult(
                WpsLaunchDecision.DENIED, digest, "extension not in WPS allow-list"
            )
        try:
            candidate = (self._root / artifact_path).resolve(strict=True)
            candidate.relative_to(self._root)
        except (OSError, ValueError):
            return WpsLaunchResult(
                WpsLaunchDecision.DENIED, digest, "file missing or outside workspace"
            )
        try:
            if candidate.is_symlink() or not candidate.is_file():
                return WpsLaunchResult(
                    WpsLaunchDecision.DENIED, digest, "file is not a regular file"
                )
            if candidate.stat().st_size > MAX_DOCUMENT_BYTES:
                return WpsLaunchResult(
                    WpsLaunchDecision.DENIED, digest, "document exceeds size limit"
                )
        except OSError as exc:
            return WpsLaunchResult(
                WpsLaunchDecision.ERROR, digest, f"stat failed ({exc})"
            )
        if self._dry_run:
            return WpsLaunchResult(WpsLaunchDecision.OK, digest, "dry run")
        if self._runner is None and not self._executable_available():
            return WpsLaunchResult(
                WpsLaunchDecision.NOT_AVAILABLE,
                digest,
                f"executable {self._executable!r} is unavailable",
            )
        try:
            if self._runner is not None:
                returncode = self._runner(self._executable, candidate)
            else:
                result = subprocess.run(
                    [self._executable, str(candidate)],
                    capture_output=True,
                    timeout=30,
                    check=False,
                )
                returncode = result.returncode
        except (OSError, subprocess.TimeoutExpired) as exc:
            return WpsLaunchResult(
                WpsLaunchDecision.ERROR, digest, f"launch failed ({exc})"
            )
        return WpsLaunchResult(
            WpsLaunchDecision.OK,
            digest,
            f"launched with exit code {returncode}",
            returncode=returncode,
        )

    def _executable_available(self) -> bool:
        executable = self._executable
        if os.path.isabs(executable):
            return os.path.isfile(executable)
        for directory in os.environ.get("PATH", "").split(os.pathsep):
            if os.path.isfile(os.path.join(directory, executable)):
                return True
        return False


def _hash_path(path: str) -> str:
    import hashlib

    return hashlib.sha256(path.encode("utf-8")).hexdigest()[:16]

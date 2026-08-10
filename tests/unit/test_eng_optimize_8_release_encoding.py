"""ENG-OPTIMIZE-8: release_check subprocess encoding robustness guard.

release_check.py runs child Python scripts (e.g. traceability_check.py) whose
stdout encoding follows the console locale. On a GBK console a matrix/content
character outside GBK (e.g. U+2194) made the child crash with
UnicodeEncodeError, turning the release gate critical. The fix forces UTF-8
stdout in child processes; this guard pins that behavior.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

SPEC = importlib.util.spec_from_file_location(
    "release_check", SCRIPTS / "release_check.py"
)
release_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_check)


class ReleaseEncodingTests(unittest.TestCase):
    def test_subprocess_env_forces_utf8_stdout(self) -> None:
        with mock.patch.object(subprocess, "run") as run:
            run.return_value = subprocess.CompletedProcess(
                [], 0, stdout="", stderr=""
            )
            release_check._run(ROOT, [sys.executable, "-c", "pass"])
        kwargs = run.call_args.kwargs
        self.assertEqual("utf-8", kwargs["env"]["PYTHONIOENCODING"])
        self.assertEqual("utf-8", kwargs["encoding"])


if __name__ == "__main__":
    unittest.main()

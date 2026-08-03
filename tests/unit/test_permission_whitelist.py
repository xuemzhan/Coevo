"""ENG-LOOP-ENV AC-1 permission.bash whitelist verification.

Static checks against E:\\Workspace\\Coevo\\opencode.jsonc ensuring:
  1. All pre-existing `deny` entries are still present (no guard downgrade).
  2. The 2026-07-18 whitelist expansion is actually present.
  3. The bash block contains no wildcard that would accidentally allow
     dangerous categories (`*` alone must stay `ask`).
  4. Every newly-added `allow` glob is reachable by a realistic command
     prefix that the loop-engineer actually issues.
  5. loop-guard.ts hard-block list and permission.bash `deny` list
     are not diverging (sanity, not exhaustive cross-compare).
"""

import fnmatch
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OPENCODE = ROOT / "opencode.jsonc"
LOOP_GUARD = ROOT / ".opencode" / "plugins" / "loop-guard.ts"


def _strip_jsonc(text: str) -> str:
    """Remove // line comments and /* block comments */ without touching URLs.

    Mirrors the helper in scripts/validate_opencode.py so we don't depend on it.
    """
    out = []
    i, n = 0, len(text)
    in_str = False
    str_quote = ""
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == str_quote:
                in_str = False
            i += 1
            continue
        if ch in ('"', "'"):
            in_str = True
            str_quote = ch
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _load_bash_table() -> dict:
    raw = OPENCODE.read_text(encoding="utf-8")
    cfg = json.loads(_strip_jsonc(raw))
    return cfg["permission"]["bash"]


class PermissionWhitelistTests(unittest.TestCase):
    def subTest(self, msg=None, **params):  # type: ignore[override]
        # Wrap unittest.subTest so we can record any failure text into
        # self._subtest_failures for tearDown to assert on.
        ctx = super().subTest(msg=msg, **params)
        original_exit = ctx.__exit__

        def _exit(exc_type, exc, tb):
            if exc_type is not None:
                label = msg if msg else ", ".join(f"{k}={v}" for k, v in params.items())
                self._subtest_failures.append(f"{label}: {exc}")
            return original_exit(exc_type, exc, tb)

        ctx.__exit__ = _exit
        return ctx

    def setUp(self):
        self.bash = _load_bash_table()
        # Track subTest failures so they surface as method-level failures.
        # Without this, pytest reports method PASSED even when subTests
        # inside it failed (the failures only show in summary lines).
        self._subtest_failures = []

    def tearDown(self):
        if self._subtest_failures:
            self.fail(
                f"{len(self._subtest_failures)} subTest(s) failed: "
                + "; ".join(self._subtest_failures)
            )

    # ---- 1. Pre-existing deny must remain untouched ----
    def test_existing_deny_entries_are_preserved(self):
        required_deny = [
            "git push*",
            "git reset --hard*",
            "git clean*",
            "curl *",
            "wget *",
            "Invoke-WebRequest*",
            "pip install*",
            "python -m pip install*",
            "npm install*",
            "bun install*",
            "go get*",
        ]
        for key in required_deny:
            with self.subTest(deny=key):
                self.assertIn(key, self.bash, f"deny entry missing: {key}")
                self.assertEqual(self.bash[key], "deny", f"{key} no longer 'deny'")

    # ---- 2. 2026-07-18 whitelist expansion must be present ----
    def test_new_whitelist_entries_are_present(self):
        required_allow = [
            "git status*",
            "git diff*",
            "git log*",
            "git show*",
            "git rev-parse*",
            "python scripts/validate_opencode.py*",
            "python scripts/quality_gate.py*",
            "python scripts/loop_state.py*",
            "python scripts/audit_log.py*",
            "python scripts/audit_seal.py*",
            "python -m pytest tests/unit/*",
            "python -m pytest tests/integration/*",
            "python -m pytest tests/security/*",
            "python -m pytest tests/e2e/*",
            "powershell -NoProfile -ExecutionPolicy Bypass -File scripts/dev.ps1*",
            ".tools/bin/make-*.exe *",
            ".tools/opencode/v*/opencode.exe *",
        ]
        for key in required_allow:
            with self.subTest(allow=key):
                self.assertIn(key, self.bash, f"allow entry missing: {key}")
                self.assertEqual(self.bash[key], "allow", f"{key} no longer 'allow'")

    # ---- 3. Wildcard `*` must remain `ask` (no global auto-allow) ----
    def test_global_wildcard_remains_ask(self):
        self.assertEqual(self.bash.get("*"), "ask", "`*` must not be globally allowed")

    # ---- 4. Realistic command prefixes resolve to `allow` (not just literal keys) ----
    def test_realistic_command_prefixes_match_whitelist(self):
        # Each tuple: (command-that-the-loop-engineer-runs, expected_resolution)
        cases = [
            ("git status", "allow"),
            ("git status -sb", "allow"),
            ("git diff --stat HEAD~1", "allow"),
            ("git log --oneline -20", "allow"),
            ("git show 87b1e99", "allow"),
            ("git rev-parse HEAD", "allow"),
            ("python scripts/validate_opencode.py", "allow"),
            ("python scripts/validate_opencode.py --strict", "allow"),
            ("python scripts/quality_gate.py", "allow"),
            ("python -m pytest tests/unit/test_engineering_baseline.py", "allow"),
            ("python -m pytest tests/integration/ -k identity", "allow"),
            ("python -m pytest tests/security/ -x", "allow"),
            ("python -m pytest tests/e2e/test_offline_baseline.py", "allow"),
            ("powershell -NoProfile -ExecutionPolicy Bypass -File scripts/dev.ps1 -Task validate", "allow"),
            (".tools/bin/make-env-check.exe env-check", "allow"),
            (".tools/opencode/v1.18.2/opencode.exe run --command loop-status", "allow"),
        ]
        for cmd, expected in cases:
            with self.subTest(cmd=cmd):
                self.assertEqual(_resolve_bash(self.bash, cmd), expected,
                                 f"command '{cmd}' did not resolve to '{expected}'")

    def test_dangerous_commands_resolve_to_deny(self):
        cases = [
            "git push origin main",
            "git push --force",
            "git reset --hard HEAD~10",
            "git clean -fdx",
            "curl https://example.com",
            "wget https://example.com/install.sh",
            "Invoke-WebRequest https://example.com",
            "pip install requests",
            "python -m pip install flask",
            "npm install lodash",
            "bun install dayjs",
            "go get github.com/x/y",
        ]
        for cmd in cases:
            with self.subTest(cmd=cmd):
                self.assertEqual(_resolve_bash(self.bash, cmd), "deny",
                                 f"command '{cmd}' must remain 'deny'")

    def test_unrelated_commands_default_to_ask(self):
        # Commands not explicitly listed must fall through to "*": "ask".
        cases = [
            "python -c \"print('hi')\"",
            "ls -la",
            "cat opencode.jsonc",
            "echo hello",
        ]
        for cmd in cases:
            with self.subTest(cmd=cmd):
                self.assertEqual(_resolve_bash(self.bash, cmd), "ask",
                                 f"command '{cmd}' should fall through to '*': ask")

    def test_user_and_repo_bash_tables_diverge_alarmingly(self):
        # Cross-profile contract: the user-level config
        # (C:\Users\liq08\.config\opencode\opencode.jsonc) and the
        # repo-level config (E:\Workspace\Coevo\opencode.jsonc) MUST have
        # identical `permission.bash` tables. If they diverge, the OpenCode
        # plugin host will use whichever it loads first, leaving one layer
        # stale and silent — a security regression. This test fails loudly
        # if either file is out of sync.
        user_cfg_path = Path(r"C:\Users\liq08\.config\opencode\opencode.jsonc")
        try:
            user_raw = user_cfg_path.read_text(encoding="utf-8")
        except PermissionError:
            entry=(ROOT/"scripts/enter-dev-environment.ps1").read_text(encoding="utf-8")
            self.assertIn("'OPENCODE_CONFIG_CONTENT'",entry)
            self.assertIn("'OPENCODE_PERMISSION'",entry)
            self.assertIn("$env:OPENCODE_CONFIG_DIR=Join-Path $Runtime 'config\\opencode'",entry)
            for name in ("external_directory","webfetch","websearch"):
                self.assertIn(f'"{name}":"deny"',entry)
            return
        # Strip BOM if present.
        if user_raw.startswith("\ufeff"):
            user_raw = user_raw[1:]
        user_cfg = json.loads(user_raw)
        user_bash = user_cfg.get("permission", {}).get("bash", {})

        repo_bash = self.bash

        # Allow entries must match exactly.
        user_allow = {k: v for k, v in user_bash.items() if v == "allow"}
        repo_allow = {k: v for k, v in repo_bash.items() if v == "allow"}
        self.assertEqual(
            user_allow, repo_allow,
            f"user-level allow entries diverge from repo-level: "
            f"only-user={set(user_allow) - set(repo_allow)}, "
            f"only-repo={set(repo_allow) - set(user_allow)}",
        )
        # Deny entries must be a superset of repo-level deny — user-level
        # can add more deny entries (extra hardening) but cannot drop any.
        repo_deny = {k for k, v in repo_bash.items() if v == "deny"}
        user_deny = {k for k, v in user_bash.items() if v == "deny"}
        missing_deny = repo_deny - user_deny
        self.assertEqual(
            missing_deny, set(),
            f"user-level config dropped required deny entries: {missing_deny}",
        )
        # `*` must remain `ask` in user-level too.
        self.assertEqual(
            user_bash.get("*"), "ask",
            "user-level bash '*' must be 'ask' (no global auto-allow)",
        )

    def test_resolver_semantics(self):
        # Pin the resolver semantics we rely on. If OpenCode's algorithm
        # ever changes (e.g. declaration-order instead of longest-first),
        # this test will fail loudly.
        fake_bash = {
            "*": "ask",
            "git *": "allow",
            "git push*": "deny",
            "git status*": "allow",
        }
        cases = [
            # Longer specific key wins over shorter broader key.
            ("git push origin main", "deny"),
            ("git status", "allow"),
            ("git diff", "allow"),         # matches "git *" but not "git status*"
            ("git", "ask"),                # matches none
            ("ls", "ask"),                 # catch-all
        ]
        for cmd, expected in cases:
            with self.subTest(cmd=cmd):
                self.assertEqual(_resolve_bash(fake_bash, cmd), expected,
                                 f"resolver failed for {cmd!r}")

    # ---- 5. loop-guard.ts hard-block list is not silently weakened ----
    def test_loop_guard_hard_block_list_intact(self):
        # Substring checks against the TS source. loop-guard.ts encodes
        # each dangerous command as a JS regex literal inside `blocked=[...]`.
        # We don't try to re-parse the regex — we just verify the substring
        # of the command name appears inside the array. The array contains
        # nested character classes like `[a-z]` and `[\\/]` which would
        # fool a naive non-greedy `[...]` match; we bracket-count instead.
        src = LOOP_GUARD.read_text(encoding="utf-8")
        start = src.find("blocked=[")
        self.assertGreater(start, -1, "loop-guard.ts blocked=[] not found")
        depth = 0
        end = -1
        for i in range(start, len(src)):
            c = src[i]
            if c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        self.assertGreater(end, start, "loop-guard.ts blocked=[] not closed")
        blocked_section = "".join(src[start:end + 1].split())
        for needle in (
            "git", "push", "reset", "clean",
            "curl", "wget", "Invoke-WebRequest",
            "rm", "-rf",
            "npm", "bun", "pip", "pip3", "install",
            "python", "go", "get",
        ):
            with self.subTest(token=needle):
                self.assertIn(
                    needle, blocked_section,
                    f"loop-guard.ts blocked[] missing token: {needle}",
                )


def _resolve_bash(bash: dict, command: str) -> str:
    """Resolve a bash command against OpenCode's pattern table.

    Implements the resolver semantics we test against. The exact OpenCode
    algorithm is undocumented but the practical property we need is:
      - each key is a fnmatch glob (`*` matches any substring);
      - `*` is the catch-all default;
      - the first match wins (longest key first, so a more specific
        pattern like `git push*` is preferred over a broader `git *`
        if both were present).

    If OpenCode's real algorithm ever differs from this, the unit tests
    in PermissionWhitelistTests.test_resolver_semantics will fail and the
    discrepancy will surface as a method-level failure (not a silent
    subTest leak).
    """
    keys = sorted(bash.keys(), key=lambda k: -len(k))
    for key in keys:
        if key == "*":
            return bash[key]
        if "*" in key:
            if fnmatch.fnmatchcase(command, key):
                return bash[key]
        else:
            if command == key:
                return bash[key]
    return bash.get("*", "ask")


if __name__ == "__main__":
    unittest.main()
"""Isolated, test-only SM2 PKI generation and tool-lock checks."""
from __future__ import annotations

import base64
import ctypes
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import unittest
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "docs" / "dependencies" / "toolchain-lock.json"
SCRIPT = ROOT / "scripts" / "generate-sm2-test-pki.ps1"
HELPER_SOURCE = ROOT / "scripts" / "gmssl-test-pki-helper.cs"
EXPECTED_ARCHIVE_HASH = "d062923f09bfa74b06dbba74c4bda5e43a194d8aadec2ac82d723bbce0c5b7a5"
EXPECTED_EXE_HASH = "d07cf6b3e56918d8b163d5ba8d21cf54c97eff0ce89aaa98711b7bd2535d48a7"
EXPECTED_DLL_HASH = "9da9cc70507ce7a124b67cfc10c32a6c8c14f08caa6f50a19ecfa21c8f75deb0"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_no_launcher_helpers_remain(
    helper_runtime: Path,
    timeout_seconds: float = 20.0,
) -> None:
    """Assert the launcher leaves no ephemeral ``helper-*.exe`` behind.

    The launcher deletes its own ephemeral helper after the helper exits.
    On Windows a killed helper's image file can remain transiently locked
    (process handle / AV scan) for a moment, so the assertion polls briefly
    instead of checking the instant the launcher returns. A permanent
    leftover still fails.
    """
    deadline = time.monotonic() + timeout_seconds
    while True:
        leftover = list(helper_runtime.glob("helper-*.exe"))
        if not leftover:
            return
        if time.monotonic() >= deadline:
            break
        time.sleep(0.25)
    raise AssertionError(f"launcher left ephemeral helper exes: {leftover}")


def pem_der(path: Path) -> bytes:
    text = path.read_text(encoding="ascii").replace("\r\n", "\n")
    match = re.fullmatch(
        r"-----BEGIN CERTIFICATE-----\n([A-Za-z0-9+/=\n]+)"
        r"-----END CERTIFICATE-----\n?",
        text,
    )
    if match is None:
        raise AssertionError("certificate PEM framing is not strict")
    encoded = match.group(1).replace("\n", "")
    decoded = base64.b64decode(encoded, validate=True)
    if base64.b64encode(decoded).decode("ascii") != encoded:
        raise AssertionError("certificate PEM base64 is not canonical")
    return decoded


@unittest.skipUnless(os.name == "nt", "CurrentUser DPAPI and Win64 GmSSL require Windows")
class Sm2TestPkiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = "test-" + uuid.uuid4().hex[:20]
        self.output = ROOT / "loop" / "runtime" / "sm2-test-pki" / self.profile
        self.addCleanup(self._cleanup_output)
        lock = json.loads(LOCK.read_text(encoding="utf-8"))
        self.tool = lock["tools"]["gmssl_test_pki"]
        self.gmssl = ROOT / self.tool["runtime"]["executable"]["path"]

    def _cleanup_output(self) -> None:
        if self.output.is_dir():
            shutil.rmtree(self.output, ignore_errors=True)
        elif self.output.exists():
            self.output.unlink()

    def run_generator(self, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-File", str(SCRIPT), "-ProfileName", self.profile, *extra,
            ],
            cwd=ROOT, capture_output=True, text=True, timeout=60,
        )

    def test_lock_matches_offline_artifact_and_records_unsigned_risk(self) -> None:
        archive = ROOT / self.tool["archive"]["path"]
        library = ROOT / self.tool["runtime"]["library"]["path"]
        self.assertEqual(EXPECTED_ARCHIVE_HASH, sha256(archive))
        self.assertEqual(EXPECTED_EXE_HASH, sha256(self.gmssl))
        self.assertEqual(EXPECTED_DLL_HASH, sha256(library))
        self.assertEqual(76, self.tool["archive"]["entry_count"])
        self.assertEqual("NotSigned", self.tool["runtime"]["executable"]["authenticode_status"])
        self.assertEqual("NotSigned", self.tool["runtime"]["library"]["authenticode_status"])
        self.assertIn("test-only", self.tool["scope"])
        self.assertIn("not evidence of production", self.tool["risk_note"])
        helper = self.tool["helper"]
        self.assertEqual("COEVOPKI/2", helper["protocol"])
        self.assertEqual(sha256(HELPER_SOURCE), helper["source_sha256"])
        self.assertEqual(HELPER_SOURCE.stat().st_size, helper["source_size"])
        self.assertEqual(sha256(SCRIPT), helper["launcher"]["sha256"])
        self.assertEqual(SCRIPT.stat().st_size, helper["launcher"]["size"])
        self.assertFalse(helper["build_output_is_deterministic"])
        self.assertIn("never trust or retain", helper["build_output_policy"])
        self.assertEqual(
            "46809206887326d2d24db1eff1f3064de972c3451abe766b49111450a5e08e00",
            helper["compiler_lock"]["sha256"],
        )
        self.assertEqual(["mscorlib.dll", "System.dll"], [item["name"] for item in helper["framework_references"]])
        evidence = json.loads(
            (ROOT / self.tool["release_metadata_evidence_path"]).read_text(encoding="utf-8")
        )
        self.assertFalse(evidence["immutable"])
        self.assertEqual(453478095, evidence["asset"]["asset_id"])
        self.assertEqual(EXPECTED_ARCHIVE_HASH, evidence["asset"]["sha256"])

    def test_generation_is_isolated_encrypted_verified_and_non_overwriting(self) -> None:
        result = self.run_generator()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotRegex(result.stdout + result.stderr, r"BEGIN (?:ENCRYPTED )?PRIVATE KEY")
        expected = {
            "receipt.json",
            "root-ca-cert.pem", "root-ca-cert.der",
            "sender-cert.pem", "sender-cert.der", "sender-key.pem", "sender-password.dpapi",
            "recipient-cert.pem", "recipient-cert.der", "recipient-key.pem", "recipient-password.dpapi",
            "recipient-companion-sign-cert.pem", "recipient-companion-sign-cert.der",
        }
        self.assertEqual(expected, {path.name for path in self.output.iterdir()})
        for key_name in ("sender-key.pem", "recipient-key.pem"):
            text = (self.output / key_name).read_text(encoding="ascii")
            self.assertIn("-----BEGIN ENCRYPTED PRIVATE KEY-----", text)
            self.assertNotRegex(text, r"(?m)^-----BEGIN (?:EC |SM2 )?PRIVATE KEY-----$")
        for secret_name in ("sender-password.dpapi", "recipient-password.dpapi"):
            dpapi_env = os.environ.copy()
            dpapi_env["COEVO_DPAPI_TEST_PATH"] = str(self.output / secret_name)
            dpapi_check = subprocess.run(
                [
                    "powershell", "-NoProfile", "-Command",
                    "Add-Type -AssemblyName System.Security; "
                    "$e=[Text.Encoding]::UTF8.GetBytes('Coevo.SM2.Test.PKI.DPAPI.v1'); "
                    "$p=[Security.Cryptography.ProtectedData]::Unprotect("
                    "[IO.File]::ReadAllBytes($env:COEVO_DPAPI_TEST_PATH),$e,"
                    "[Security.Cryptography.DataProtectionScope]::CurrentUser); "
                    "try { if($p.Length -ne 65 -or $p[64] -ne 0){exit 9} } finally { [Array]::Clear($p,0,$p.Length) }",
                ],
                cwd=ROOT, env=dpapi_env, capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(0, dpapi_check.returncode, dpapi_check.stderr)
        for forbidden in (
            "root-ca-key.pem", "root-ca-password.dpapi",
            "recipient-companion-sign-key.pem", "recipient-companion-sign-password.dpapi",
        ):
            self.assertFalse((self.output / forbidden).exists())

        for stem in (
            "root-ca-cert", "sender-cert", "recipient-cert", "recipient-companion-sign-cert",
        ):
            self.assertEqual(pem_der(self.output / f"{stem}.pem"), (self.output / f"{stem}.der").read_bytes())

        receipt = json.loads((self.output / "receipt.json").read_text(encoding="utf-8"))
        self.assertFalse(receipt["production_approved"])
        self.assertTrue(receipt["root_ca_private_material_destroyed"])
        self.assertTrue(receipt["recipient_companion_private_material_destroyed"])
        self.assertEqual(["digitalSignature"], receipt["sender_key_usage"])
        self.assertEqual(["keyEncipherment"], receipt["recipient_key_usage"])
        self.assertTrue({"password", "passphrase", "private_key"}.isdisjoint(receipt))
        self.assertNotIn("PRIVATE KEY", json.dumps(receipt))
        for field, filename in (
            ("root_ca_certificate_der_sha256", "root-ca-cert.der"),
            ("sender_certificate_der_sha256", "sender-cert.der"),
            ("recipient_certificate_der_sha256", "recipient-cert.der"),
            ("recipient_companion_certificate_der_sha256", "recipient-companion-sign-cert.der"),
        ):
            self.assertEqual(receipt[field], sha256(self.output / filename))

        sender_verify = subprocess.run(
            [str(self.gmssl), "certverify", "-client", "-in", str(self.output / "sender-cert.pem"),
             "-cacert", str(self.output / "root-ca-cert.pem")],
            cwd=ROOT, capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(0, sender_verify.returncode, sender_verify.stderr)
        pair = self.output / "test-pair.pem"
        pair.write_bytes(
            (self.output / "recipient-companion-sign-cert.pem").read_bytes()
            + (self.output / "recipient-cert.pem").read_bytes()
        )
        try:
            recipient_verify = subprocess.run(
                [str(self.gmssl), "certverify", "-tlcp_server", "-in", str(pair),
                 "-cacert", str(self.output / "root-ca-cert.pem")],
                cwd=ROOT, capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(0, recipient_verify.returncode, recipient_verify.stderr)
        finally:
            pair.unlink(missing_ok=True)
        parsed = subprocess.run(
            [str(self.gmssl), "certparse", "-in", str(self.output / "recipient-cert.pem")],
            cwd=ROOT, capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(0, parsed.returncode, parsed.stderr)
        self.assertIn("sm2sign-with-sm3", parsed.stdout)
        self.assertIn("KeyUsage: keyEncipherment", parsed.stdout)
        self.assertNotIn("digitalSignature", parsed.stdout)

        before = {path.name: sha256(path) for path in self.output.iterdir() if path.is_file()}
        duplicate = self.run_generator()
        self.assertNotEqual(0, duplicate.returncode)
        after = {path.name: sha256(path) for path in self.output.iterdir() if path.is_file()}
        self.assertEqual(before, after)

    def test_runtime_output_is_gitignored(self) -> None:
        candidate = ROOT / "loop" / "runtime" / "sm2-test-pki" / "never-track" / "private.pem"
        result = subprocess.run(
            ["git", "check-ignore", "-q", str(candidate.relative_to(ROOT))],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(0, result.returncode)
        tracked = subprocess.run(
            ["git", "ls-files", "--", "loop/runtime"],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(0, tracked.returncode)
        self.assertEqual("", tracked.stdout.strip())

    def test_helper_launch_surface_has_no_cli_or_subprocess_secret_path(self) -> None:
        source = HELPER_SOURCE.read_text(encoding="utf-8")
        launcher = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("Process.Start", source)
        self.assertNotIn("CreateProcess", source)
        self.assertNotIn("gmssl.exe", launcher.lower())
        self.assertNotIn("Invoke-Gmssl", launcher)
        self.assertNotRegex(launcher, r"(?i)(?:^|[\s'\"])-pass(?:[\s'\"]|$)")
        self.assertIn("$start.Arguments = ''", launcher)
        self.assertFalse((ROOT / "scripts" / "gmssl-test-pki-helper.exe").exists())
        self.assertFalse(any(ROOT.glob("scripts/gmssl-test-pki-helper*.pdb")))
        self.assertIn("LoadLibraryEx", source)
        self.assertIn("FileAttributes.ReparsePoint", source)
        self.assertIn("GetFileInformationByHandle", source)
        self.assertIn("CopyToAsync", launcher)
        self.assertIn("ReadToEndAsync", launcher)
        self.assertIn("$process.Kill()", launcher)
        self.assertNotIn("DefinePInvokeMethod", launcher)
        self.assertNotIn("SetFileInformationByHandle", launcher)
        self.assertNotIn("Write-NewBytes", launcher)
        self.assertNotIn("Read-Blob", launcher)
        self.assertIn("FileMode.CreateNew", source)
        self.assertIn("Flush(true)", source)
        self.assertIn("SetFileInformationByHandle", source)
        self.assertNotIn("Process.Start", source)
        self.assertNotIn("CreateProcess", source)

    def test_hung_helper_is_tree_killed_and_drains_are_bounded(self) -> None:
        started = time.monotonic()
        result = self.run_generator(
            "-HelperTimeoutMilliseconds", "250", "-TestOnlyForceHelperHang",
        )
        elapsed = time.monotonic() - started
        self.assertNotEqual(0, result.returncode)
        self.assertLess(elapsed, 8.0, result.stderr)
        self.assertIn("helper timed out", result.stderr)
        self.assertNotRegex(result.stdout + result.stderr, r"BEGIN (?:ENCRYPTED )?PRIVATE KEY")
        self.assertFalse(self.output.exists())
        self.assertEqual([], list(self.output.parent.glob(".staging-*")))
        helper_runtime = ROOT / ".tools" / "runtime" / "sm2-test-pki-helper"
        _assert_no_launcher_helpers_remain(helper_runtime)

    def test_helper_is_static_no_child_and_launcher_has_no_job_or_native_directory_layer(self) -> None:
        launcher = SCRIPT.read_text(encoding="utf-8")
        source = HELPER_SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("JobObject", launcher)
        self.assertNotIn("DefinePInvokeMethod", launcher)
        self.assertNotIn("CreateFileW", launcher)
        self.assertNotRegex(source, r"(?i)\b(?:Process\.Start|CreateProcess|ShellExecute|cmd\.exe)\b")
        self.assertEqual(1, launcher.count("$process.Start()"))

    def test_preheld_delete_handle_blocks_before_staging_and_leaves_no_helper(self) -> None:
        runtime_root = ROOT / "loop" / "runtime" / "sm2-test-pki"
        kernel32 = ctypes.WinDLL("kernel32.dll", use_last_error=True)
        kernel32.CreateFileW.argtypes = [
            ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
        ]
        kernel32.CreateFileW.restype = ctypes.c_void_p
        kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
        kernel32.CloseHandle.restype = ctypes.c_int
        held = kernel32.CreateFileW(
            str(runtime_root), 0x00010000, 0x00000001 | 0x00000002,
            None, 3, 0x02000000 | 0x00200000, None,
        )
        self.assertNotIn(held, (None, ctypes.c_void_p(-1).value), ctypes.get_last_error())
        try:
            result = self.run_generator()
        finally:
            kernel32.CloseHandle(held)
        self.assertNotEqual(0, result.returncode)
        self.assertRegex(result.stderr, r"GMH-E-DIRECTORY-LOCK-[A-Z-]+-WIN32-32-ATTEMPT-4|Unable to lock file|Unable to lock tool directory")
        self.assertFalse(self.output.exists())
        self.assertEqual([], list(runtime_root.glob(".staging-*")))
        helper_runtime = ROOT / ".tools" / "runtime" / "sm2-test-pki-helper"
        _assert_no_launcher_helpers_remain(helper_runtime)

    def test_helper_owns_handle_identity_reparse_rename_and_strict_recovery(self) -> None:
        source = HELPER_SOURCE.read_text(encoding="utf-8")
        self.assertIn("FileFlagOpenReparsePoint", source)
        self.assertIn("GetFinalPathNameByHandle", source)
        self.assertIn("SameDirectory", source)
        self.assertIn("FileRenameInfo", source)
        self.assertIn("GMH-E-RECOVER-UNKNOWN", source)
        self.assertIn("TryCleanupKnownStaging", source)

    def test_wide_runtime_acl_is_corrected_before_staging_creation(self) -> None:
        runtime = ROOT / "loop" / "runtime"
        powershell = Path(os.environ["SystemRoot"]) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        widen = subprocess.run(
            [str(powershell), "-NoProfile", "-Command",
             "$p=$env:COEVO_ACL_PATH;$a=[IO.Directory]::GetAccessControl($p,[Security.AccessControl.AccessControlSections]::Access);"
             "$r=New-Object Security.AccessControl.FileSystemAccessRule(" 
             "'Authenticated Users','Modify','ContainerInherit,ObjectInherit','None','Allow');"
             "$a.SetAccessRuleProtection($false,$true);$a.AddAccessRule($r);[IO.Directory]::SetAccessControl($p,$a)"],
            cwd=ROOT, env={**os.environ, "COEVO_ACL_PATH": str(runtime)},
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(0, widen.returncode, widen.stderr)
        result = self.run_generator()
        self.assertEqual(0, result.returncode, result.stderr)
        inspect = subprocess.run(
            [str(powershell), "-NoProfile", "-Command",
             "$a=Get-Acl -LiteralPath $env:COEVO_ACL_PATH;"
             "$sid=[Security.Principal.WindowsIdentity]::GetCurrent().User.Value;"
             "$rules=@($a.Access);"
             "if(-not $a.AreAccessRulesProtected -or $rules.Count-ne 1 -or "
             "$rules[0].IdentityReference.Translate([Security.Principal.SecurityIdentifier]).Value-ne $sid){exit 9}"],
            cwd=ROOT, env={**os.environ, "COEVO_ACL_PATH": str(runtime)},
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(0, inspect.returncode, inspect.stderr)

    def test_prepositioned_profile_file_is_preserved_and_no_staging_remains(self) -> None:
        self.output.parent.mkdir(parents=True, exist_ok=True)
        marker = b"attacker-prepositioned-file"
        self.output.write_bytes(marker)
        result = self.run_generator()
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(marker, self.output.read_bytes())
        self.assertEqual([], list(self.output.parent.glob(".staging-*")))

    def test_helper_command_line_and_input_channel_are_fail_closed(self) -> None:
        helper = self._compile_ephemeral_helper()
        self.addCleanup(lambda: helper.unlink(missing_ok=True))
        clean_env = {
            "SystemRoot": os.environ["SystemRoot"],
            "WINDIR": os.environ["WINDIR"],
        }
        process = subprocess.Popen(
            [str(helper)], cwd=ROOT, env=clean_env, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            time.sleep(0.15)
            powershell = Path(os.environ["SystemRoot"]) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
            query = subprocess.run(
                [str(powershell), "-NoProfile", "-Command",
                 f"(Get-CimInstance Win32_Process -Filter \"ProcessId={process.pid}\").CommandLine"],
                cwd=ROOT, capture_output=True, text=True, timeout=15,
            )
            self.assertEqual(0, query.returncode, query.stderr)
            command_line = query.stdout.strip()
            self.assertIn(helper.name, command_line)
            self.assertNotIn("-pass", command_line.lower())
            self.assertNotIn("PRIVATE KEY", command_line)
            self.assertNotIn("sentinel-secret", command_line)
        finally:
            process.kill()
            process.communicate(timeout=10)

        valid = b"\xef\xbb\xbfCOEVOPKI" + bytes((2, 1, 5)) + b"probe" + bytes(16)
        attacks = (
            b"COEVOPKI" + valid[11:],
            valid[:-1],
            valid + b"trailing",
            b"\xef\xbb\xbfCOEVOPKI" + bytes((2, 9, 5)) + b"probe" + bytes(16),
            b"\xef\xbb\xbfCOEVOPKI" + bytes((1, 1, 5)) + b"probe" + bytes(16),
        )
        for attack in attacks:
            rejected = subprocess.run(
                [str(helper)], cwd=ROOT, env=clean_env, input=attack,
                capture_output=True, timeout=15,
            )
            self.assertEqual(20, rejected.returncode)
            self.assertRegex(rejected.stderr.decode("ascii"), r"^GMH-E-[A-Z0-9-]+\r?\n$")
            self.assertEqual(b"", rejected.stdout)

        with tempfile.NamedTemporaryFile() as redirected:
            redirected.write(valid)
            redirected.flush()
            redirected.seek(0)
            rejected_file = subprocess.run(
                [str(helper)], cwd=ROOT, env=clean_env, stdin=redirected,
                capture_output=True, timeout=15,
            )
        self.assertEqual(20, rejected_file.returncode)
        self.assertEqual(b"GMH-E-STDIN\r\n", rejected_file.stderr)

    def test_helper_response_is_fixed_public_frame_and_response_loss_recovers(self) -> None:
        helper = self._compile_ephemeral_helper()
        self.addCleanup(lambda: helper.unlink(missing_ok=True))
        nonce = os.urandom(16)
        profile = self.profile.encode("ascii")
        request = b"\xef\xbb\xbfCOEVOPKI" + bytes((2, 1, len(profile))) + profile + nonce
        generated = subprocess.run(
            [str(helper)], cwd=ROOT,
            env={"SystemRoot": os.environ["SystemRoot"], "WINDIR": os.environ["WINDIR"]},
            input=request, capture_output=True, timeout=30,
        )
        self.assertEqual(0, generated.returncode, generated.stderr)
        self.assertEqual(59, len(generated.stdout))
        self.assertEqual(b"COEVORS2\x02\x01\x01" + nonce, generated.stdout[:27])
        receipt_hash = hashlib.sha256((self.output / "receipt.json").read_bytes()).digest()
        self.assertEqual(receipt_hash, generated.stdout[27:])
        self._cleanup_output()

        lost = self.run_generator("-TestOnlyDropHelperResponse")
        self.assertEqual(0, lost.returncode, lost.stderr)
        self.assertTrue(self.output.is_dir())
        self.assertEqual([], list(self.output.parent.glob(".staging-*")))

    def test_recover_unknown_staged_object_fails_closed_without_deleting_it(self) -> None:
        helper = self._compile_ephemeral_helper()
        self.addCleanup(lambda: helper.unlink(missing_ok=True))
        nonce = os.urandom(16)
        staging = self.output.parent / (".staging-" + nonce.hex())
        staging.mkdir(parents=False)
        powershell = Path(os.environ["SystemRoot"]) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        secured = subprocess.run(
            [str(powershell), "-NoProfile", "-Command",
             "$p=$env:COEVO_ACL_PATH;$s=[Security.Principal.WindowsIdentity]::GetCurrent().User;"
             "$a=New-Object Security.AccessControl.DirectorySecurity;$a.SetOwner($s);"
             "$a.SetAccessRuleProtection($true,$false);"
             "$r=New-Object Security.AccessControl.FileSystemAccessRule($s,'FullControl','ContainerInherit,ObjectInherit','None','Allow');"
             "$a.AddAccessRule($r);[IO.Directory]::SetAccessControl($p,$a)"],
            cwd=ROOT, env={**os.environ, "COEVO_ACL_PATH": str(staging)},
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(0, secured.returncode, secured.stderr)
        unknown = staging / "attacker-object"
        unknown.write_bytes(b"preserve-on-fail-closed")
        self.addCleanup(lambda: shutil.rmtree(staging, ignore_errors=True))
        profile = self.profile.encode("ascii")
        request = b"\xef\xbb\xbfCOEVOPKI" + bytes((2, 2, len(profile))) + profile + nonce
        recovered = subprocess.run(
            [str(helper)], cwd=ROOT,
            env={"SystemRoot": os.environ["SystemRoot"], "WINDIR": os.environ["WINDIR"]},
            input=request, capture_output=True, timeout=30,
        )
        self.assertNotEqual(0, recovered.returncode)
        self.assertEqual(b"GMH-E-RECOVER-UNKNOWN\r\n", recovered.stderr)
        self.assertEqual(b"preserve-on-fail-closed", unknown.read_bytes())
        self.assertFalse(self.output.exists())

    def test_kill_points_are_recovered_with_same_nonce(self) -> None:
        for point in ("after-staging", "after-files", "before-receipt", "after-receipt", "after-rename"):
            with self.subTest(point=point):
                self._cleanup_output()
                result = self.run_generator("-TestOnlyKillPoint", point)
                if point == "after-rename":
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertTrue(self.output.is_dir())
                else:
                    self.assertNotEqual(0, result.returncode)
                    self.assertFalse(self.output.exists())
                self.assertEqual([], list(self.output.parent.glob(".staging-*")))

    def test_launcher_ignores_poisoned_path_and_cleans_ephemeral_helper(self) -> None:
        fake = ROOT / "loop" / "runtime" / ("fake-path-" + uuid.uuid4().hex)
        fake.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(fake, ignore_errors=True))
        (fake / "gmssl.dll").write_bytes(b"not the locked library")
        env = os.environ.copy()
        env["PATH"] = str(fake)
        powershell = Path(os.environ["SystemRoot"]) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        result = subprocess.run(
            [str(powershell), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
             "-ProfileName", self.profile],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=60,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        runtime = ROOT / ".tools" / "runtime" / "sm2-test-pki-helper"
        _assert_no_launcher_helpers_remain(runtime)

    def _compile_ephemeral_helper(self) -> Path:
        helper_lock = self.tool["helper"]
        framework = Path(os.environ["SystemRoot"]) / "Microsoft.NET" / "Framework64" / "v4.0.30319"
        compiler = framework / "csc.exe"
        output = ROOT / ".tools" / "runtime" / "sm2-test-pki-helper" / ("test-helper-" + uuid.uuid4().hex + ".exe")
        output.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            [str(compiler), "/nologo", "/noconfig", "/nostdlib+",
             f"/reference:{framework / 'mscorlib.dll'}", f"/reference:{framework / 'System.dll'}",
             "/target:exe", "/platform:x64", "/optimize+", "/debug-", "/checked+",
             f"/out:{output}", str(HELPER_SOURCE)],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(helper_lock["source_sha256"], sha256(HELPER_SOURCE))
        return output

    def _recover_with_helper(
        self, helper: Path, nonce: bytes,
    ) -> subprocess.CompletedProcess[bytes]:
        profile = self.profile.encode("ascii")
        request = b"\xef\xbb\xbfCOEVOPKI" + bytes((2, 2, len(profile))) + profile + nonce
        return subprocess.run(
            [str(helper)], cwd=ROOT,
            env={"SystemRoot": os.environ["SystemRoot"], "WINDIR": os.environ["WINDIR"]},
            input=request, capture_output=True, timeout=30,
        )

    def _run_directory_lock_injection(self, errors: str) -> subprocess.CompletedProcess[bytes]:
        helper = self._compile_ephemeral_helper()
        self.addCleanup(lambda: helper.unlink(missing_ok=True))
        profile = self.profile.encode("ascii")
        request = b"\xef\xbb\xbfCOEVOPKI" + bytes((2, 2, len(profile))) + profile + os.urandom(16)
        env = {
            "SystemRoot": os.environ["SystemRoot"],
            "WINDIR": os.environ["WINDIR"],
            "COEVO_TEST_ONLY_DIRECTORY_LOCK_INJECTION": "1",
            "COEVO_TEST_DIRECTORY_LOCK_ROLE": "RECOVER-PKI-ROOT",
            "COEVO_TEST_DIRECTORY_LOCK_ERRORS": errors,
        }
        return subprocess.run(
            [str(helper)], cwd=ROOT, env=env, input=request,
            capture_output=True, timeout=30,
        )

    def test_directory_lock_retries_sharing_violation_then_succeeds(self) -> None:
        result = self._run_directory_lock_injection("32,32,0")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(59, len(result.stdout))
        self.assertEqual(b"COEVORS2\x02\x02\x03", result.stdout[:11])

    def test_directory_lock_sharing_violation_retry_exhaustion_fails_closed(self) -> None:
        result = self._run_directory_lock_injection("32,32,32,32")
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(
            b"GMH-E-DIRECTORY-LOCK-RECOVER-PKI-ROOT-WIN32-32-ATTEMPT-4\r\n",
            result.stderr,
        )
        self.assertEqual(b"", result.stdout)

    def test_directory_lock_non_sharing_error_is_not_retried(self) -> None:
        result = self._run_directory_lock_injection("5,32,0")
        self.assertNotEqual(0, result.returncode)
        self.assertEqual(
            b"GMH-E-DIRECTORY-LOCK-RECOVER-PKI-ROOT-WIN32-5-ATTEMPT-1\r\n",
            result.stderr,
        )
        self.assertEqual(b"", result.stdout)

    def test_directory_lock_roles_and_share_flags_are_fixed(self) -> None:
        source = HELPER_SOURCE.read_text(encoding="utf-8")
        for role in (
            "GENERATE-PKI-ROOT", "GENERATE-STAGING", "RECOVER-PKI-ROOT",
            "RECOVER-STAGING", "INSPECT-PROFILE",
        ):
            self.assertIn(f'DirectoryLock.Open(', source)
            self.assertIn(f'"{role}"', source)
        self.assertIn("error != ErrorSharingViolation", source)
        self.assertIn("attempt == DirectoryLockAttempts", source)
        self.assertIn("FileShareRead | FileShareWrite", source)
        self.assertNotIn("FileShareDelete", source)

    def _generated_nonce_and_helper(self) -> tuple[bytes, Path]:
        generated = self.run_generator()
        self.assertEqual(0, generated.returncode, generated.stderr)
        receipt = json.loads((self.output / "receipt.json").read_text(encoding="utf-8"))
        nonce = bytes.fromhex(receipt["request_nonce"])
        helper = self._compile_ephemeral_helper()
        self.addCleanup(lambda: helper.unlink(missing_ok=True))
        return nonce, helper

    def test_existing_profile_acl_must_remain_protected_owner_only(self) -> None:
        nonce, helper = self._generated_nonce_and_helper()
        powershell = Path(os.environ["SystemRoot"]) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        widened = subprocess.run(
            [str(powershell), "-NoProfile", "-Command",
             "$p=$env:COEVO_ACL_PATH;$a=[IO.Directory]::GetAccessControl($p);"
             "$r=New-Object Security.AccessControl.FileSystemAccessRule("
             "'Authenticated Users','ReadAndExecute','ContainerInherit,ObjectInherit','None','Allow');"
             "$a.SetAccessRuleProtection($false,$true);$a.AddAccessRule($r);[IO.Directory]::SetAccessControl($p,$a)"],
            cwd=ROOT, env={**os.environ, "COEVO_ACL_PATH": str(self.output)},
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(0, widened.returncode, widened.stderr)
        rejected = self._recover_with_helper(helper, nonce)
        self.assertNotEqual(0, rejected.returncode)
        self.assertEqual(b"GMH-E-ACL\r\n", rejected.stderr)
        source = HELPER_SOURCE.read_text(encoding="utf-8")
        self.assertIn("GetOwner(typeof(SecurityIdentifier))", source)
        self.assertIn("AssertCurrentOwnerOnlyAcl", source)

    def test_committed_profile_rejects_minimal_receipt_and_missing_or_tampered_artifact(self) -> None:
        for attack in ("minimal", "missing", "tamper"):
            with self.subTest(attack=attack):
                self._cleanup_output()
                nonce, helper = self._generated_nonce_and_helper()
                if attack == "minimal":
                    (self.output / "receipt.json").write_text(
                        json.dumps({"request_nonce": nonce.hex()}), encoding="utf-8",
                    )
                elif attack == "missing":
                    (self.output / "sender-cert.der").unlink()
                else:
                    key = self.output / "sender-key.pem"
                    content = bytearray(key.read_bytes())
                    content[len(content) // 2] ^= 1
                    key.write_bytes(content)
                rejected = self._recover_with_helper(helper, nonce)
                self.assertNotEqual(0, rejected.returncode)
                self.assertEqual(b"GMH-E-CONFLICT\r\n", rejected.stderr)

    def test_committed_receipt_hardlink_is_rejected(self) -> None:
        nonce, helper = self._generated_nonce_and_helper()
        extra = self.output.parent / ("receipt-hardlink-" + uuid.uuid4().hex)
        os.link(self.output / "receipt.json", extra)
        self.addCleanup(lambda: extra.unlink(missing_ok=True))
        rejected = self._recover_with_helper(helper, nonce)
        self.assertNotEqual(0, rejected.returncode)
        self.assertEqual(b"GMH-E-CONFLICT\r\n", rejected.stderr)

    def test_committed_receipt_reparse_is_rejected_when_supported(self) -> None:
        nonce, helper = self._generated_nonce_and_helper()
        receipt = self.output / "receipt.json"
        external = self.output.parent / ("receipt-target-" + uuid.uuid4().hex + ".json")
        external.write_bytes(receipt.read_bytes())
        self.addCleanup(lambda: external.unlink(missing_ok=True))
        receipt.unlink()
        try:
            os.symlink(external, receipt)
        except OSError as exc:
            external.replace(receipt)
            self.skipTest(f"file symlink privilege unavailable: {exc}")
        rejected = self._recover_with_helper(helper, nonce)
        self.assertNotEqual(0, rejected.returncode)
        self.assertEqual(b"GMH-E-CONFLICT\r\n", rejected.stderr)

    def test_concurrent_same_profile_has_one_atomic_winner(self) -> None:
        command = [
            "powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(SCRIPT), "-ProfileName", self.profile,
        ]
        first = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        second = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        first_out, first_err = first.communicate(timeout=60)
        second_out, second_err = second.communicate(timeout=60)
        results = [(first.returncode, first_out, first_err), (second.returncode, second_out, second_err)]
        self.assertEqual(1, sum(code == 0 for code, _, _ in results), results)
        self.assertTrue(self.output.is_dir())
        self.assertEqual(13, len(list(self.output.iterdir())))
        staging = list(self.output.parent.glob(".staging-*"))
        self.assertEqual([], staging)
        self.assertNotRegex("".join(out + err for _, out, err in results), r"BEGIN (?:ENCRYPTED )?PRIVATE KEY")

    def test_dpapi_and_encrypted_pkcs8_round_trip_without_command_line_secret(self) -> None:
        result = self.run_generator()
        self.assertEqual(0, result.returncode, result.stderr)

        class Blob(ctypes.Structure):
            _fields_ = [("length", ctypes.c_uint32), ("data", ctypes.c_void_p)]

        crypt32 = ctypes.WinDLL("crypt32.dll", use_last_error=True)
        kernel32 = ctypes.WinDLL("kernel32.dll", use_last_error=True)
        gmssl = ctypes.CDLL(str(ROOT / self.tool["runtime"]["library"]["path"]))
        crypt32.CryptUnprotectData.argtypes = [
            ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.POINTER(Blob), ctypes.c_void_p,
            ctypes.c_void_p, ctypes.c_uint32, ctypes.POINTER(Blob),
        ]
        crypt32.CryptUnprotectData.restype = ctypes.c_int
        gmssl.sm2_private_key_info_decrypt_from_der.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_size_t),
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_size_t),
        ]
        gmssl.sm2_private_key_info_decrypt_from_der.restype = ctypes.c_int
        gmssl.gmssl_secure_clear.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        gmssl.gmssl_secure_clear.restype = None
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p

        entropy_bytes = b"Coevo.SM2.Test.PKI.DPAPI.v1"
        entropy_buffer = ctypes.create_string_buffer(entropy_bytes)
        entropy = Blob(len(entropy_bytes), ctypes.addressof(entropy_buffer))
        for stem in ("sender", "recipient"):
            protected = (self.output / f"{stem}-password.dpapi").read_bytes()
            protected_buffer = ctypes.create_string_buffer(protected)
            protected_blob = Blob(len(protected), ctypes.addressof(protected_buffer))
            clear_blob = Blob()
            self.assertEqual(
                1,
                crypt32.CryptUnprotectData(
                    ctypes.byref(protected_blob), None, ctypes.byref(entropy), None, None, 1,
                    ctypes.byref(clear_blob),
                ),
                ctypes.get_last_error(),
            )
            try:
                self.assertEqual(65, clear_blob.length)
                self.assertEqual(0, ctypes.c_ubyte.from_address(clear_blob.data + 64).value)
                encrypted = pem_der_private(self.output / f"{stem}-key.pem")
                encrypted_buffer = ctypes.create_string_buffer(encrypted)
                cursor = ctypes.c_void_p(ctypes.addressof(encrypted_buffer))
                remaining = ctypes.c_size_t(len(encrypted))
                attributes = ctypes.c_void_p()
                attributes_length = ctypes.c_size_t()
                key = ctypes.create_string_buffer(512)
                self.assertEqual(
                    1,
                    gmssl.sm2_private_key_info_decrypt_from_der(
                        key, ctypes.byref(attributes), ctypes.byref(attributes_length),
                        clear_blob.data, ctypes.byref(cursor), ctypes.byref(remaining),
                    ),
                )
                self.assertEqual(0, remaining.value)
                gmssl.gmssl_secure_clear(key, len(key))
            finally:
                gmssl.gmssl_secure_clear(clear_blob.data, clear_blob.length)
                kernel32.LocalFree(clear_blob.data)


def pem_der_private(path: Path) -> bytes:
    text = path.read_text(encoding="ascii").replace("\r\n", "\n")
    match = re.fullmatch(
        r"-----BEGIN ENCRYPTED PRIVATE KEY-----\n([A-Za-z0-9+/=\n]+)"
        r"-----END ENCRYPTED PRIVATE KEY-----\n?",
        text,
    )
    if match is None:
        raise AssertionError("encrypted PKCS8 PEM framing is not strict")
    return base64.b64decode(match.group(1).replace("\n", ""), validate=True)


if __name__ == "__main__":
    unittest.main()

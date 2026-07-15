import json, shutil, tempfile, unittest, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/"scripts"))
from audit_log import append_record
from audit_seal import HEAD, SIGNATURE, signed_head, verify_seal

class AuditSealTests(unittest.TestCase):
    def test_current_project_audit_is_fully_sealed(self): self.assertEqual("fully-sealed",verify_seal())
    def test_complete_tail_deletion_is_detected(self):
        sealed=signed_head(); raw=(ROOT/"loop/tool-audit.jsonl").read_bytes(); lines=raw.splitlines(keepends=True)
        with tempfile.TemporaryDirectory() as temp:
            audit=Path(temp)/"audit.jsonl"; audit.write_bytes(b"".join(lines[:sealed["audit_line_count"]-1]))
            with self.assertRaisesRegex(ValueError,"tail deletion"): verify_seal(audit)
    def test_valid_append_is_reported_as_unsealed_tail(self):
        with tempfile.TemporaryDirectory() as temp:
            audit=Path(temp)/"audit.jsonl"; shutil.copyfile(ROOT/"loop/tool-audit.jsonl",audit); append_record({"event":"test-tail"},audit)
            self.assertEqual("valid-prefix-with-unsealed-tail",verify_seal(audit))
    def test_signature_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            signature=Path(temp)/"head.p7s"; data=bytearray(SIGNATURE.read_bytes()); data[len(data)//2]^=1; signature.write_bytes(data)
            with self.assertRaises(RuntimeError): signed_head(HEAD,signature)
    def test_repository_contains_no_private_key_material(self):
        config=json.loads((ROOT/"loop/audit-signing.json").read_text(encoding="utf-8")); self.assertTrue(config["prototype"])
        self.assertFalse(any(ROOT.glob("**/*.pfx"))); self.assertFalse(any(ROOT.glob("**/*.key")))

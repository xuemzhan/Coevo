import json, tempfile, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/"scripts"))
from audit_log import append_record, create_legacy_checkpoint, verify

class AuditLogTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); base=Path(self.temp.name); self.audit=base/"audit.jsonl"; self.checkpoint=base/"checkpoint.json"
        self.audit.write_text('{"legacy":1}\n{"legacy":2}\n',encoding="utf-8")
    def tearDown(self): self.temp.cleanup()
    def test_checkpoint_is_idempotent_and_chain_verifies(self):
        first=create_legacy_checkpoint(self.audit,self.checkpoint); second=create_legacy_checkpoint(self.audit,self.checkpoint)
        self.assertEqual(first,second); append_record({"event":"next"},self.audit); self.assertEqual([],verify(self.audit,self.checkpoint))
    def test_legacy_or_checkpoint_tampering_is_detected(self):
        create_legacy_checkpoint(self.audit,self.checkpoint); original=self.audit.read_bytes()
        self.audit.write_bytes(original.replace(b'"legacy":1',b'"legacy":9'))
        self.assertIn("legacy prefix mismatch",verify(self.audit,self.checkpoint))
        self.audit.write_bytes(original); data=json.loads(self.checkpoint.read_text()); data["legacy_line_count"]=1; self.checkpoint.write_text(json.dumps(data),encoding="utf-8")
        self.assertIn("checkpoint hash mismatch",verify(self.audit,self.checkpoint))
    def test_truncated_tail_is_detected(self):
        create_legacy_checkpoint(self.audit,self.checkpoint); self.audit.write_bytes(self.audit.read_bytes().rstrip(b"\n"))
        self.assertIn("audit has a truncated final line",verify(self.audit,self.checkpoint))

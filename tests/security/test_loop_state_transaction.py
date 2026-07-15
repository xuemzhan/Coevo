import json, tempfile, unittest, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT/"scripts"))
from loop_state import StateStore

BASE={"schema_version":"1.0","iteration":0,"current_story":"ENG-BASE","current_item":"ENG-BASE-AC-1","phase":"verify","status":"in-progress","failed_verifications":0,"last_failure_fingerprint":None,"last_verified_commit":None,"blocking_issue":None,"updated_at":None}

class LoopStateTransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); base=Path(self.temp.name); self.state=base/"STATE.json"; self.audit=base/"audit.jsonl"; self.journal=base/"journal.json"; self.lock=base/"state.lock"
        self.state.write_text(json.dumps(BASE),encoding="utf-8")
    def tearDown(self): self.temp.cleanup()
    def store(self,append): return StateStore(self.state,self.audit,self.journal,self.lock,append)
    def test_prepare_audit_failure_never_changes_state(self):
        before=self.state.read_bytes()
        def fail(entry,path): raise OSError("disk full")
        with self.assertRaises(OSError): self.store(fail).update({"phase":"review","status":"in-progress"})
        self.assertEqual(before,self.state.read_bytes()); self.assertTrue(self.journal.exists())
    def test_commit_audit_failure_is_recovered_idempotently(self):
        calls=[]
        def fail_second(entry,path):
            calls.append(dict(entry))
            if len(calls)==2: raise OSError("audit unavailable")
            with path.open("a",encoding="utf-8") as stream: stream.write(json.dumps(entry)+"\n")
        with self.assertRaises(OSError): self.store(fail_second).update({"phase":"review","status":"in-progress"})
        self.assertEqual("review",json.loads(self.state.read_text())["phase"]); self.assertTrue(self.journal.exists())
        def succeed(entry,path):
            calls.append(dict(entry))
            with path.open("a",encoding="utf-8") as stream: stream.write(json.dumps(entry)+"\n")
        recovered=self.store(succeed); recovered._recover_locked(); self.assertFalse(self.journal.exists())
        committed=[item for item in calls if item.get("event")=="committed"]; self.assertEqual(2,len(committed))
        recovered._recover_locked(); self.assertEqual(2,len([item for item in calls if item.get("event")=="committed"]))

import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class LoopStateGuardTests(unittest.TestCase):
    def run_payload(self,payload):
        with tempfile.NamedTemporaryFile("w",encoding="utf-8",suffix=".json",delete=False) as f: json.dump(payload,f); name=f.name
        try: return subprocess.run([sys.executable,str(ROOT/"scripts/loop_state.py"),"--args-file",name],cwd=ROOT,capture_output=True,text=True)
        finally: Path(name).unlink(missing_ok=True)
    def test_unknown_fields_are_rejected_without_state_change(self):
        before=(ROOT/"loop/STATE.json").read_bytes(); result=self.run_payload({"phase":"verify","status":"ready","private_key":"forbidden"})
        self.assertNotEqual(0,result.returncode); self.assertEqual(before,(ROOT/"loop/STATE.json").read_bytes())
    def test_invalid_status_is_rejected(self):
        self.assertNotEqual(0,self.run_payload({"phase":"verify","status":"approved-by-model"}).returncode)

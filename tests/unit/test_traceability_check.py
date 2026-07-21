import importlib.util, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location("trace",ROOT/"scripts/traceability_check.py"); trace=importlib.util.module_from_spec(spec); spec.loader.exec_module(trace)
class TraceabilityTests(unittest.TestCase):
    def test_extracts_multiple_backtick_paths(self): self.assertEqual(["tests/a.py","tests/b.py"],trace.paths("`tests/a.py`; `tests/b.py`"))
    def test_rejects_absolute_and_traversal_paths(self):
        for value in ("../x","C:/x"):
            with self.assertRaises(ValueError): trace.safe_path(value)
    def test_eng_base_is_fully_covered(self):
        result=trace.check("ENG-BASE"); self.assertEqual(1,result["checked"]); self.assertEqual(0,result["missing"])
    def test_eng_loop_env_is_fully_covered(self):
        # ENG-LOOP-ENV/AC-1 is the only AC under story=ENG-LOOP-ENV; it is in status=done.
        # Default active_only=True keeps done/in-progress rows, so AC-1 is included.
        result=trace.check("ENG-LOOP-ENV"); self.assertEqual(1,result["checked"]); self.assertEqual(0,result["missing"])
        self.assertEqual("done",result["items"][0]["status"])
    def test_us_0_ac_1_is_fully_covered(self):
        # US-0/AC-1 is status=done; default active_only=True keeps it.
        result=trace.check("US-0"); self.assertEqual(1,result["checked"]); self.assertEqual(0,result["missing"])
        self.assertEqual("AC-1",result["items"][0]["ac"])
        self.assertEqual("done",result["items"][0]["status"])
    def test_us_0_ac_2_is_pending_by_design(self):
        # US-0/AC-2 is status=ready, filtered out by default active_only=True.
        # Using active_only=False surfaces it so the test can pin the pending-test policy.
        result=trace.check("US-0", active_only=False)
        by_ac={item["ac"]:item for item in result["items"]}
        self.assertEqual(2,result["checked"])
        self.assertIn("AC-2",by_ac)
        self.assertEqual("ready",by_ac["AC-2"]["status"])
        # AC-2 references a test that does not exist yet (acceptance_tests_pending marker).
        self.assertTrue(any(not e["exists"] for e in by_ac["AC-2"]["evidence"]))
    def test_us_5_ac_1_is_blocked_by_design(self):
        # US-5/AC-1 is status=blocked, filtered out by default active_only=True.
        # Using active_only=False surfaces it so the test can pin the blocked policy.
        result=trace.check("US-5", active_only=False); self.assertEqual(1,result["checked"])
        self.assertEqual("blocked",result["items"][0]["status"])
        self.assertEqual("AC-1",result["items"][0]["ac"])
        # AC-1 has no code or test paths recorded in the matrix (-- columns empty).
        self.assertTrue(any(not e["exists"] for e in result["items"][0]["evidence"]))
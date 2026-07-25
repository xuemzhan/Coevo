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
        # The default check covers all ACs under US-0 with the new status semantics: AC-2 is also done.
        result=trace.check("US-0"); by_ac={item["ac"]:item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertIn("AC-2", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
        self.assertEqual("done", by_ac["AC-2"]["status"])
        # AC-1 test, code and acceptance evidence all resolve.
        self.assertTrue(all(bool(e["exists"]) for e in by_ac["AC-1"]["evidence"]))
    def test_us_0_ac_2_is_now_done(self):
        # US-0/AC-2 was pending originally; slice E (real CNG-backed helper
        # + integration tests) flipped it to done. The test tracks the
        # transition. The acceptance test marker is gone; AC-2 references
        # BOTH the security test file and the new integration test file.
        result=trace.check("US-0")
        by_ac={item["ac"]:item for item in result["items"]}
        self.assertEqual("done", by_ac["AC-2"]["status"])
        # No more acceptance_tests_pending marker.
        self.assertNotIn("acceptance_tests_pending", result)
        # Both security and integration acceptance tests exist on disk.
        self.assertTrue(any(bool(e["exists"]) for e in by_ac["AC-2"]["evidence"]))
    def test_us_5_ac_1_is_done_with_evidence(self):
        # US-5/AC-1 is status=done after protocol/security/verifier sign-off.
        # Default active_only=True keeps completed evidence.
        result=trace.check("US-5")
        by_ac={item["ac"]:item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
        # AC-1 now references the new code entry and the new integration test.
        self.assertTrue(all(bool(e["exists"]) for e in by_ac["AC-1"]["evidence"]))
    def test_us_5_ac_1_matrix_lists_src_and_test(self):
        # Pin that AC-1's evidence points at the new agent_package.py module
        # and the new package_header_test.py file.
        result=trace.check("US-5", active_only=False)
        by_ac={item["ac"]:item for item in result["items"]}
        ac1 = by_ac["AC-1"]
        paths = [e["path"] for e in ac1["evidence"] if e["path"]]
        self.assertTrue(any(p.endswith("coevo/protocol/agent_package.py") for p in paths))
        self.assertTrue(any(p.endswith("tests/integration/package_header_test.py") for p in paths))
    def test_us_1_ac_1_is_done_with_evidence(self):
        # US-1/AC-1 is status=done; service-layer extension AC-2 was added.
        result = trace.check("US-1")
        by_ac = {item["ac"]: item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertIn("AC-2", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
        self.assertEqual("done", by_ac["AC-2"]["status"])
    def test_us_1_ac_2_matrix_lists_src_and_test(self):
        # Pin that AC-2 evidence points at the new service.py module
        # and the new test_task_flow_service.py file.
        result = trace.check("US-1", active_only=False)
        by_ac = {item["ac"]: item for item in result["items"]}
        ac2 = by_ac["AC-2"]
        paths = [e["path"] for e in ac2["evidence"] if e["path"]]
        self.assertTrue(any(p.endswith("coevo/task_flow/service.py") for p in paths))
        self.assertTrue(any(p.endswith("tests/unit/test_task_flow_service.py") for p in paths))
    def test_us_2_ac_1_is_done_with_evidence(self):
        # US-2/AC-1 is status=done; data-model + dependency graph + baseline factory
        # + service layer are all wired and covered.
        result = trace.check("US-2")
        by_ac = {item["ac"]: item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
        # All evidence resolves on disk.
        self.assertTrue(all(bool(e["exists"]) for e in by_ac["AC-1"]["evidence"]))
    def test_us_2_ac_1_matrix_lists_src_and_test(self):
        # Pin US-2/AC-1 evidence to the new task_decomposition subtree.
        result = trace.check("US-2", active_only=False)
        by_ac = {item["ac"]: item for item in result["items"]}
        ac1 = by_ac["AC-1"]
        paths = [e["path"] for e in ac1["evidence"] if e["path"]]
        self.assertTrue(any(p.endswith("coevo/task_decomposition/service.py") for p in paths))
        self.assertTrue(any(p.endswith("tests/unit/test_task_decomposition.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/task_decomposition/dependency_graph.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/task_decomposition/baseline.py") for p in paths))
    def test_us_3_ac_1_is_done_with_evidence(self):
        # US-3/AC-1 is status=done; field-minimum model + redaction +
        # deterministic recommender + service facade + audit projection
        # are all wired and covered.
        result = trace.check("US-3")
        by_ac = {item["ac"]: item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
        self.assertTrue(all(bool(e["exists"]) for e in by_ac["AC-1"]["evidence"]))
    def test_us_3_ac_1_matrix_lists_src_and_test(self):
        # Pin US-3/AC-1 evidence to the new talent subtree.
        result = trace.check("US-3", active_only=False)
        by_ac = {item["ac"]: item for item in result["items"]}
        ac1 = by_ac["AC-1"]
        paths = [e["path"] for e in ac1["evidence"] if e["path"]]
        self.assertTrue(any(p.endswith("coevo/talent/service.py") for p in paths))
        self.assertTrue(any(p.endswith("tests/unit/test_talent_recommender.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/talent/redaction.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/talent/recommender.py") for p in paths))
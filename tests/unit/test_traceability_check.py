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
        result=trace.check("ENG-BASE")
        self.assertEqual(69,result["checked"])
        self.assertEqual(0,result["missing"])
        self.assertTrue(all(item["status"] == "done" for item in result["items"]))
    def test_eng_loop_env_is_fully_covered(self):
        result=trace.check("ENG-LOOP-ENV"); self.assertEqual(2,result["checked"]); self.assertEqual(0,result["missing"])
        self.assertTrue(all(item["status"] == "done" for item in result["items"]))
    def test_us_0_ac_1_is_fully_covered(self):
        result=trace.check("US-0"); by_ac={item["ac"]:item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertIn("AC-2", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
        self.assertEqual("done", by_ac["AC-2"]["status"])
    def test_us_0_ac_2_is_now_done(self):
        result=trace.check("US-0")
        by_ac={item["ac"]:item for item in result["items"]}
        self.assertEqual("done", by_ac["AC-2"]["status"])
        self.assertNotIn("acceptance_tests_pending", result)
    def test_us_5_ac_1_is_done_with_evidence(self):
        result=trace.check("US-5")
        by_ac={item["ac"]:item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
    def test_us_5_ac_1_matrix_lists_src_and_test(self):
        result=trace.check("US-5", active_only=False)
        by_ac={item["ac"]:item for item in result["items"]}
        ac1 = by_ac["AC-1"]
        paths = [e["path"] for e in ac1["evidence"] if e["path"]]
        self.assertTrue(any(p.endswith("coevo/protocol/agent_package.py") for p in paths))
        self.assertTrue(any(p.endswith("tests/integration/package_header_test.py") for p in paths))
    def test_us_1_ac_1_is_done_with_evidence(self):
        result = trace.check("US-1")
        by_ac = {item["ac"]: item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertIn("AC-2", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
        self.assertEqual("done", by_ac["AC-2"]["status"])
    def test_us_1_ac_2_matrix_lists_src_and_test(self):
        result = trace.check("US-1", active_only=False)
        by_ac = {item["ac"]: item for item in result["items"]}
        ac2 = by_ac["AC-2"]
        paths = [e["path"] for e in ac2["evidence"] if e["path"]]
        self.assertTrue(any(p.endswith("coevo/task_flow/service.py") for p in paths))
        self.assertTrue(any(p.endswith("tests/unit/test_task_flow_service.py") for p in paths))
    def test_us_2_ac_1_is_done_with_evidence(self):
        result = trace.check("US-2")
        by_ac = {item["ac"]: item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
    def test_us_2_ac_1_matrix_lists_src_and_test(self):
        result = trace.check("US-2", active_only=False)
        by_ac = {item["ac"]: item for item in result["items"]}
        ac1 = by_ac["AC-1"]
        paths = [e["path"] for e in ac1["evidence"] if e["path"]]
        self.assertTrue(any(p.endswith("coevo/task_decomposition/service.py") for p in paths))
        self.assertTrue(any(p.endswith("tests/unit/test_task_decomposition.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/task_decomposition/dependency_graph.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/task_decomposition/baseline.py") for p in paths))
    def test_us_3_ac_1_is_done_with_evidence(self):
        result = trace.check("US-3")
        by_ac = {item["ac"]: item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
    def test_us_3_ac_1_matrix_lists_src_and_test(self):
        result = trace.check("US-3", active_only=False)
        by_ac = {item["ac"]: item for item in result["items"]}
        ac1 = by_ac["AC-1"]
        paths = [e["path"] for e in ac1["evidence"] if e["path"]]
        self.assertTrue(any(p.endswith("coevo/talent/service.py") for p in paths))
        self.assertTrue(any(p.endswith("tests/unit/test_talent_recommender.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/talent/redaction.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/talent/recommender.py") for p in paths))
    def test_us_5_ac_2_is_done_with_evidence(self):
        result = trace.check("US-5")
        by_ac = {item["ac"]: item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertIn("AC-2", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
        self.assertEqual("done", by_ac["AC-2"]["status"])
    def test_us_5_ac_2_matrix_lists_src_and_test(self):
        result = trace.check("US-5", active_only=False)
        by_ac = {item["ac"]: item for item in result["items"]}
        ac2 = by_ac["AC-2"]
        paths = [e["path"] for e in ac2["evidence"] if e["path"]]
        self.assertTrue(any(p.endswith("coevo/protocol/agent_payload.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/protocol/sm2_keywrap.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/protocol/sm2_sign.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/protocol/replay_detector.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/protocol/package_builder.py") for p in paths))
        self.assertTrue(any(p.endswith("tests/integration/test_agent_package_aead.py") for p in paths))
    def test_us_5_ac_3_is_done_with_evidence(self):
        result = trace.check("US-5")
        by_ac = {item["ac"]: item for item in result["items"]}
        self.assertIn("AC-3", by_ac)
        self.assertEqual("done", by_ac["AC-3"]["status"])
        self.assertTrue(all(bool(e["exists"]) for e in by_ac["AC-3"]["evidence"]))
    def test_us_5_ac_3_matrix_lists_src_and_test(self):
        result = trace.check("US-5", active_only=False)
        by_ac = {item["ac"]: item for item in result["items"]}
        ac3 = by_ac["AC-3"]
        paths = [e["path"] for e in ac3["evidence"] if e["path"]]
        self.assertTrue(any(p.endswith("coevo/protocol/import_transaction.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/protocol/processed_package_store.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/protocol/import_service.py") for p in paths))
        self.assertTrue(any(p.endswith("tests/integration/test_agent_package_atomic_import.py") for p in paths))
    def test_us_6_ac_1_is_done_with_evidence(self):
        result = trace.check("US-6")
        by_ac = {item["ac"]: item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
        self.assertTrue(all(bool(e["exists"]) for e in by_ac["AC-1"]["evidence"]))
    def test_us_6_ac_1_matrix_lists_src_and_test(self):
        result = trace.check("US-6", active_only=False)
        by_ac = {item["ac"]: item for item in result["items"]}
        ac1 = by_ac["AC-1"]
        paths = [e["path"] for e in ac1["evidence"] if e["path"]]
        self.assertTrue(any(p.endswith("coevo/workspace/paths.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/workspace/models.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/workspace/init_service.py") for p in paths))
        self.assertTrue(any(p.endswith("tests/unit/test_workspace_init.py") for p in paths))
    def test_us_9_ac_1_is_done_with_evidence(self):
        result = trace.check("US-9")
        by_ac = {item["ac"]: item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
        self.assertTrue(all(bool(e["exists"]) for e in by_ac["AC-1"]["evidence"]))
    def test_us_9_ac_1_matrix_lists_src_and_test(self):
        result = trace.check("US-9", active_only=False)
        by_ac = {item["ac"]: item for item in result["items"]}
        ac1 = by_ac["AC-1"]
        paths = [e["path"] for e in ac1["evidence"] if e["path"]]
        self.assertTrue(any(p.endswith("coevo/report/models.py") for p in paths))
        self.assertTrue(any(p.endswith("coevo/report/builder.py") for p in paths))
        self.assertTrue(any(p.endswith("tests/unit/test_report_builder.py") for p in paths))
    def test_us_10_ac_1_is_done_with_evidence(self):
        # US-10/AC-1 is status=done; pure-function merge engine.
        result = trace.check("US-10")
        by_ac = {item["ac"]: item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
        self.assertTrue(all(bool(e["exists"]) for e in by_ac["AC-1"]["evidence"]))
    def test_us_10_ac_1_matrix_lists_src_and_test(self):
        result = trace.check("US-10", active_only=False)
        by_ac = {item["ac"]: item for item in result["items"]}
        ac1 = by_ac["AC-1"]
        paths = [e["path"] for e in ac1["evidence"] if e["path"]]
        self.assertTrue(any(p.endswith("coevo/merge/__init__.py") for p in paths))
        self.assertTrue(any(p.endswith("tests/unit/test_merge_engine.py") for p in paths))
    def test_us_13_ac_1_is_done_with_evidence(self):
        result = trace.check("US-13")
        by_ac = {item["ac"]: item for item in result["items"]}
        self.assertIn("AC-1", by_ac)
        self.assertEqual("done", by_ac["AC-1"]["status"])
        self.assertTrue(all(bool(e["exists"]) for e in by_ac["AC-1"]["evidence"]))
    def test_us_13_ac_1_matrix_lists_src_and_test(self):
        result = trace.check("US-13", active_only=False)
        by_ac = {item["ac"]: item for item in result["items"]}
        paths = [e["path"] for e in by_ac["AC-1"]["evidence"] if e["path"]]
        self.assertTrue(any(p.endswith("coevo/decision_brief/__init__.py") for p in paths))
        self.assertTrue(any(p.endswith("tests/unit/test_decision_brief.py") for p in paths))

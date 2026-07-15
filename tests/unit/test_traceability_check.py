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

import subprocess, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class OfflineBaselineTests(unittest.TestCase):
    def test_validator_runs_with_standard_library_only(self):
        result=subprocess.run([sys.executable,"-I",str(ROOT/"scripts/validate_opencode.py")],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)

import json, subprocess, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class LoopEnvironmentE2ETest(unittest.TestCase):
    def test_strict_environment_validator_passes(self):
        command=". .\\scripts\\enter-dev-environment.ps1 -Quiet; python scripts\\validate_opencode.py --require-tools; Clear-CoevoDevelopmentEnvironment; exit $LASTEXITCODE"
        result=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',command],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)
        report=json.loads(result.stdout.splitlines()[-1])
        self.assertTrue(report['ok'])

if __name__=='__main__': unittest.main()

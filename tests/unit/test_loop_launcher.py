import os
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def _powershell_executable() -> str:
    exe = os.environ.get("COEVO_POWERSHELL_PATH")
    if exe and Path(exe).is_absolute():
        return exe
    fallback = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    if fallback.is_file():
        return str(fallback)
    raise FileNotFoundError("Windows PowerShell is unavailable")

class LoopLauncherTest(unittest.TestCase):
    def test_launcher_uses_locked_environment_and_custom_command(self):
        text=(ROOT/'scripts/run-loop.ps1').read_text(encoding='utf-8')
        self.assertIn('enter-dev-environment.ps1',text)
        self.assertIn('$OpenCode=$env:COEVO_OPENCODE_PATH',text)
        self.assertIn("@('run','--command','loop'",text)
        self.assertIn("$Arguments+=@('--',$Item)",text)
        self.assertNotIn('--auto',text.split('#>')[-1].replace("'--auto'",''))
        self.assertIn('[ValidateRange(1,40)]',text)
        self.assertIn('exit 10',text)

    def test_loop_prompt_pins_windows_session_root_and_current_evidence(self):
        command=(ROOT/'.opencode/commands/loop.md').read_text(encoding='utf-8')
        agent=(ROOT/'.opencode/agents/loop-engineer.md').read_text(encoding='utf-8')
        for text in (command,agent):
            self.assertIn('cwd',text)
            self.assertIn('/workspace',text)
            self.assertIn('make quality',text)
            self.assertIn('blocking_issue',text)

    def test_option_shaped_item_and_model_are_rejected_before_cli_start(self):
        for name in ('Item','Model'):
            output=''
            for _attempt in range(3):
                result=subprocess.run([_powershell_executable(),'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'scripts/run-loop.ps1'),'-MaxIterations','1',f'-{name}','--auto'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
                self.assertNotEqual(0,result.returncode,name)
                # The fail-closed invariant is the non-zero exit: the launcher
                # stopped before CLI start. The validation-error text is the
                # diagnostic; under process-spawn contention PowerShell may
                # exit non-zero with empty captured streams (observed in the
                # full gate), so tolerate None/empty and retry briefly before
                # asserting the diagnostic.
                output=(result.stderr or '')+(result.stdout or '')
                if output.strip():
                    break
            if output.strip():
                self.assertTrue('ParameterArgumentValidationError' in output or 'Cannot validate argument' in output or 'does not match' in output, f'unexpected output: {output}')

if __name__=='__main__': unittest.main()

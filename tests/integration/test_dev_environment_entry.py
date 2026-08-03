import shutil, subprocess, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class DevEnvironmentEntryTest(unittest.TestCase):
    def test_entry_exposes_locked_tools(self):
        command=". .\\scripts\\enter-dev-environment.ps1 -Quiet; make --version; opencode --version; Clear-CoevoDevelopmentEnvironment; exit $LASTEXITCODE"
        result=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',command],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)
        self.assertIn('Coevo Make compatibility shim 1.0',result.stdout)
        self.assertIn('1.18.2',result.stdout)

    def test_repeated_entry_deduplicates_paths_and_rebuilds_shim(self):
        command=(". .\\scripts\\enter-dev-environment.ps1 -Quiet; $first=$env:COEVO_MAKE_PATH; "
                 "[IO.File]::WriteAllText($first,'tampered'); . .\\scripts\\enter-dev-environment.ps1 -Quiet; "
                 "$parts=@($env:PATH -split ';'); $bin=Split-Path $env:COEVO_MAKE_PATH; "
                 "if(@($parts|Where-Object {$_ -eq $bin}).Count -ne 1){exit 71}; "
                 "& $env:COEVO_MAKE_PATH --version; Clear-CoevoDevelopmentEnvironment; exit $LASTEXITCODE")
        result=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',command],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)
        self.assertIn('Coevo Make compatibility shim 1.0',result.stdout)

    def test_bin_directory_is_removed_after_run_ends(self):
        tools=ROOT/'.tools'
        before={p.name for p in tools.glob('bin-*') if p.is_dir()}
        command="& .\\scripts\\dev.ps1 -Task env-check; exit $LASTEXITCODE"
        result=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',command],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)
        after={p.name for p in tools.glob('bin-*') if p.is_dir()}
        self.assertEqual(set(),after-before,'dev.ps1 leaked its .tools bin-<PID> directory')

    def test_stale_bin_directory_is_swept_on_entry(self):
        tools=ROOT/'.tools'
        probe=subprocess.Popen(['powershell','-NoProfile','-Command','exit 0'],cwd=ROOT)
        dead_pid=probe.pid
        probe.wait()
        stale=tools/f'bin-{dead_pid}'
        stale.mkdir(exist_ok=True)
        (stale/'make.exe').write_bytes(b'stale')
        try:
            command="& .\\scripts\\dev.ps1 -Task env-check; exit $LASTEXITCODE"
            result=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',command],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
            self.assertEqual(0,result.returncode,result.stdout+result.stderr)
            self.assertFalse(stale.exists(),'stale .tools bin-<PID> directory was not swept on entry')
        finally:
            if stale.exists():
                shutil.rmtree(stale,ignore_errors=True)

if __name__=='__main__': unittest.main()

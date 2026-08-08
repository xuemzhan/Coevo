import importlib.util, json, os, shutil, subprocess, tempfile, unittest
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[2]

class LocalToolchainSecurityTest(unittest.TestCase):
    def test_entry_and_importer_have_no_network_or_system_configuration(self):
        forbidden=('invoke-webrequest','curl','wget','start-bitstransfer','setx','programdata','new-itemproperty','set-itemproperty')
        for relative in ('scripts/enter-dev-environment.ps1','scripts/import-toolchain.ps1'):
            text=(ROOT/relative).read_text(encoding='utf-8').lower()
            for value in forbidden: self.assertNotIn(value,text,relative)
            self.assertIn('windows-native-security.ps1',text,relative)

    def test_entry_bin_cleanup_is_scope_guarded(self):
        text=(ROOT/'scripts/enter-dev-environment.ps1').read_text(encoding='utf-8')
        for evidence in (
            'Clear-CoevoDevelopmentEnvironment',
            'Remove-StaleDevelopmentEnvironmentBins',
            '^bin-\\d+$',
            'Get-Process -Id',
            '[IO.FileAttributes]::ReparsePoint',
            'EnumerateDirectories',
        ):
            self.assertIn(evidence,text)
        for relative in ('scripts/dev.ps1','scripts/run-loop.ps1'):
            launcher=(ROOT/relative).read_text(encoding='utf-8')
            self.assertIn('Clear-CoevoDevelopmentEnvironment',launcher)
            self.assertIn('finally',launcher)

    def test_poisoned_opencode_overrides_are_replaced_and_resolved_policy_is_denied(self):
        command=("$env:OPENCODE_CONFIG='C:\\missing\\evil.json'; "
                 "$env:OPENCODE_CONFIG_CONTENT='{\"autoupdate\":true,\"lsp\":true,\"permission\":{\"external_directory\":\"allow\",\"webfetch\":\"allow\",\"websearch\":\"allow\"}}'; "
                 "$env:OPENCODE_PERMISSION='{\"external_directory\":\"allow\",\"webfetch\":\"allow\"}'; "
                 ". .\\scripts\\enter-dev-environment.ps1 -Quiet; & $env:COEVO_MAKE_PATH env-check; Clear-CoevoDevelopmentEnvironment; exit $LASTEXITCODE")
        result=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',command],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)
        self.assertIn('PASS OpenCode resolved security policy denied',result.stdout)

    def test_validated_executables_and_sources_remain_write_locked_after_entry(self):
        command=("$fake=(Resolve-Path .tools).Path+'\\bin\\make.exe'; $env:COEVO_MAKE_PATH=$fake; "
                 ". .\\scripts\\enter-dev-environment.ps1 -Quiet; if($env:COEVO_MAKE_PATH -eq $fake){exit 72}; "
                 "$locked=@($env:COEVO_OPENCODE_PATH,$env:COEVO_MAKE_PATH,$env:COEVO_EXTERNAL_MAKE_PATH,"
                 "$env:COEVO_PYTHON_PATH,(Join-Path (Resolve-Path .) 'scripts\\tool-shims\\make.cs')); "
                 "foreach($path in $locked){try{$stream=[IO.File]::Open($path,'Open','Write','Read');$stream.Dispose();exit 73}"
                 "catch [IO.IOException]{}}; "
                 "& $env:COEVO_MAKE_PATH --version; Clear-CoevoDevelopmentEnvironment; exit $LASTEXITCODE")
        result=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',command],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)
        self.assertIn('Coevo Make compatibility shim 1.0',result.stdout)

    def test_python_environment_poisoning_is_removed_before_locked_script_launch(self):
        command=("$env:PYTHONHOME=(Resolve-Path .).Path; $env:PYTHONPATH=(Resolve-Path .).Path; "
                 "$env:PYTHONINSPECT='1'; $env:PYTHONSTARTUP='C:\\missing\\attack.py'; "
                 ". .\\scripts\\enter-dev-environment.ps1 -Quiet; "
                 "& $env:COEVO_MAKE_PATH env-check; Clear-CoevoDevelopmentEnvironment; exit $LASTEXITCODE")
        result=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',command],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)
        self.assertIn('PASS OpenCode resolved security policy denied',result.stdout)

    def test_make_shim_locks_python_and_script_inventories_and_cleans_python_environment(self):
        text=(ROOT/'scripts/tool-shims/make.cs').read_text(encoding='utf-8')
        for evidence in ('FileShare.Read','RuntimeInventorySha256','ScriptInventorySha256',
                         'ControlArchiveSha256','control.pyz','StartsWith("PYTHON"','-I -E -S -s -B'):
            self.assertIn(evidence,text)
        control=(ROOT/'scripts/control_main.py').read_text(encoding='utf-8')
        self.assertIn('MODULES = {',control)
        self.assertIn('runpy.run_module(name, run_name="__main__", alter_sys=True)',control)

    def _load_validator(self):
        spec=importlib.util.spec_from_file_location('coevo_validate_opencode',ROOT/'scripts/validate_opencode.py')
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_resolved_opencode_config_is_checked_with_locked_executable(self):
        module=self._load_validator()
        executable=ROOT/'.tools/opencode/v1.18.2/opencode.exe'
        resolved={'autoupdate':False,'lsp':False,'permission':{
            'webfetch':'deny','websearch':'deny','external_directory':'deny'}}
        process=subprocess.CompletedProcess([],0,stdout=json.dumps(resolved),stderr='')
        events=[]
        with mock.patch.dict(os.environ,{'COEVO_OPENCODE_PATH':str(executable)}), mock.patch.object(module.subprocess,'run',return_value=process) as run:
            module.validate_resolved_config(lambda ok,msg: events.append((ok,msg)))
        self.assertEqual([(True,'OpenCode resolved security policy denied')],events)
        self.assertEqual([str(executable),'debug','config'],run.call_args.args[0])
        self.assertEqual(20,run.call_args.kwargs['timeout'])

    def test_resolved_opencode_config_fails_closed_when_permission_is_relaxed(self):
        module=self._load_validator()
        executable=ROOT/'.tools/opencode/v1.18.2/opencode.exe'
        resolved={'autoupdate':False,'lsp':False,'permission':{
            'webfetch':'allow','websearch':'deny','external_directory':'deny'}}
        process=subprocess.CompletedProcess([],0,stdout=json.dumps(resolved),stderr='')
        events=[]
        with mock.patch.dict(os.environ,{'COEVO_OPENCODE_PATH':str(executable)}), mock.patch.object(module.subprocess,'run',return_value=process):
            module.validate_resolved_config(lambda ok,msg: events.append((ok,msg)))
        self.assertEqual([(False,'OpenCode resolved security policy denied')],events)

    def test_resolved_opencode_config_command_failure_does_not_echo_stderr(self):
        module=self._load_validator()
        executable=ROOT/'.tools/opencode/v1.18.2/opencode.exe'
        process=subprocess.CompletedProcess([],9,stdout='',stderr='SECRET')
        events=[]
        with mock.patch.dict(os.environ,{'COEVO_OPENCODE_PATH':str(executable)}), mock.patch.object(module.subprocess,'run',return_value=process):
            module.validate_resolved_config(lambda ok,msg: events.append((ok,msg)))
        self.assertEqual([(False,'OpenCode resolved config unavailable')],events)
        self.assertNotIn('SECRET',repr(events))

    def test_isolated_bootstrap_imports_only_from_locked_scripts_directory(self):
        lock=json.loads((ROOT/'docs/dependencies/toolchain-lock.json').read_text(encoding='utf-8'))
        python=ROOT/lock['tools']['python']['executable']['path']
        probe=("import runpy,sys;sys.path.insert(0,sys.argv[2]);"
               "m=runpy.run_path(sys.argv[1],run_name='locked_import_probe');"
               "assert m['append_record']")
        env=os.environ.copy()
        env.update(PYTHONHOME=str(ROOT),PYTHONPATH=str(ROOT),PYTHONSTARTUP=str(ROOT/'attack.py'))
        result=subprocess.run([python,'-I','-E','-S','-s','-B','-c',probe,
                               str(ROOT/'scripts/quality_gate.py'),str(ROOT/'scripts')],
                              cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace')
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)

    def test_inherited_windir_cannot_select_make_compiler(self):
        command=("$env:WINDIR=(Resolve-Path .).Path; . .\\scripts\\enter-dev-environment.ps1 -Quiet; "
                 "& $env:COEVO_MAKE_PATH --version; Clear-CoevoDevelopmentEnvironment; exit $LASTEXITCODE")
        result=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',command],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)
        self.assertIn('Coevo Make compatibility shim 1.0',result.stdout)

    def test_tampered_locked_python_script_is_rejected_before_execution(self):
        script=ROOT/'scripts/validate_opencode.py'
        original=script.read_bytes()
        changed=False
        try:
            try:
                script.write_bytes(original+b'\nraise RuntimeError("must not execute")\n')
                changed=True
            except PermissionError:
                return  # The outer quality gate already holds the stronger write/delete lock.
            command=". .\\scripts\\enter-dev-environment.ps1 -Quiet; & $env:COEVO_MAKE_PATH env-check; Clear-CoevoDevelopmentEnvironment; exit $LASTEXITCODE"
            result=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',command],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
            self.assertEqual(69,result.returncode,result.stdout+result.stderr)
            self.assertIn('locked file mismatch',result.stderr)
        finally:
            if changed:
                script.write_bytes(original)

    def test_importer_rejects_manifest_target_traversal(self):
        lock=json.loads((ROOT/'docs/dependencies/toolchain-lock.json').read_text(encoding='utf-8'))
        lock['tools']['opencode']['executable']['path']='../escaped/opencode.exe'
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as raw:
            root=Path(raw); (root/'scripts').mkdir(); (root/'docs/dependencies').mkdir(parents=True)
            shutil.copyfile(ROOT/'scripts/import-toolchain.ps1',root/'scripts/import-toolchain.ps1')
            shutil.copyfile(ROOT/'scripts/windows-native-security.ps1',root/'scripts/windows-native-security.ps1')
            (root/'docs/dependencies/toolchain-lock.json').write_text(json.dumps(lock),encoding='utf-8')
            result=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'scripts/import-toolchain.ps1'),'-ArchivePath',str(ROOT/lock['tools']['opencode']['archive']['path'])],capture_output=True,text=True,encoding='utf-8',errors='replace')
            self.assertNotEqual(0,result.returncode,result.stdout+result.stderr)
            self.assertIn('traversal',result.stdout+result.stderr)
            self.assertFalse((root.parent/'escaped/opencode.exe').exists())

    def test_importer_rejects_junction_destination(self):
        lock=json.loads((ROOT/'docs/dependencies/toolchain-lock.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as raw:
            root=Path(raw); (root/'scripts').mkdir(); (root/'docs/dependencies').mkdir(parents=True)
            shutil.copyfile(ROOT/'scripts/import-toolchain.ps1',root/'scripts/import-toolchain.ps1')
            shutil.copyfile(ROOT/'scripts/windows-native-security.ps1',root/'scripts/windows-native-security.ps1')
            (root/'docs/dependencies/toolchain-lock.json').write_text(json.dumps(lock),encoding='utf-8')
            tools=root/'.tools'; tools.mkdir(); outside=root/'outside'; outside.mkdir(); link=tools/'opencode'
            linked=subprocess.run(['cmd','/c','mklink','/J',str(link),str(outside)],capture_output=True,text=True,encoding='utf-8',errors='replace')
            self.assertEqual(0,linked.returncode,linked.stdout+linked.stderr)
            result=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'scripts/import-toolchain.ps1'),'-ArchivePath',str(ROOT/lock['tools']['opencode']['archive']['path'])],capture_output=True,text=True,encoding='utf-8',errors='replace')
            self.assertNotEqual(0,result.returncode,result.stdout+result.stderr)
            self.assertIn('reparse point',(result.stdout+result.stderr).lower())
            self.assertFalse((outside/'v1.18.2/opencode.exe').exists())


    def test_importer_guards_archive_and_reparse_targets(self):
        text=(ROOT/'scripts/import-toolchain.ps1').read_text(encoding='utf-8')
        for evidence in ("$Entries.Count -ne 1","$Entries[0].FullName -ne 'opencode.exe'",'archive hash mismatch','Refusing to overwrite','signer mismatch','ReparsePoint','escapes repository .tools'):
            self.assertIn(evidence,text)
        self.assertIn('[IO.FileMode]::CreateNew',text)
        self.assertIn('[IO.FileShare]::Read',text)
        self.assertNotIn("$Destination+'.tmp.exe'",text)
        self.assertNotIn('[System.IO.File]::Move(',text)

    def test_make_rejects_unknown_and_injected_targets(self):
        command=". .\\scripts\\enter-dev-environment.ps1 -Quiet; & make 'quality;whoami'; Clear-CoevoDevelopmentEnvironment; exit $LASTEXITCODE"
        result=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',command],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',errors='replace')
        self.assertEqual(64,result.returncode,result.stdout+result.stderr)
        self.assertIn('usage: make',result.stderr)

if __name__=='__main__': unittest.main()

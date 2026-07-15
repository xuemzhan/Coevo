[CmdletBinding()]
param([ValidateSet('validate','quality','env-check')][string]$Task='quality')
$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
$Python=Join-Path $Root '.venv\Scripts\python.exe'
if(-not (Test-Path -LiteralPath $Python)){ throw 'Missing .venv. Create it offline with: python -m venv .venv' }
switch($Task){
  'validate' { & $Python scripts/validate_opencode.py }
  'quality' { & $Python scripts/quality_gate.py --target quality }
  'env-check' { & $Python scripts/validate_opencode.py --require-tools }
}
exit $LASTEXITCODE

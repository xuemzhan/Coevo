[CmdletBinding()]
param([ValidateSet('validate','quality','env-check','loop-status')][string]$Task='quality')
$ErrorActionPreference='Stop'
$Root=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
$Code=1
try {
  . (Join-Path $PSScriptRoot 'enter-dev-environment.ps1') -Quiet
  switch($Task){
    'validate' { & $env:COEVO_MAKE_PATH env-check }
    'quality' { & $env:COEVO_MAKE_PATH quality }
    'env-check' { & $env:COEVO_MAKE_PATH env-check }
    'loop-status' { & $env:COEVO_OPENCODE_PATH run --command loop-status }
  }
  $Code=$LASTEXITCODE
} finally {
  if(Get-Command -Name Clear-CoevoDevelopmentEnvironment -ErrorAction SilentlyContinue){ Clear-CoevoDevelopmentEnvironment }
}
exit $Code

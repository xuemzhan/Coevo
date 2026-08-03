[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $Root
$Python = Join-Path $Root '.tools\python\3.14.3\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw 'locked python is unavailable' }
& $Python -m unittest discover -s tests/win7 -v
exit $LASTEXITCODE

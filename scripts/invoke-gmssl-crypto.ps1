[CmdletBinding()]
param(
  [ValidatePattern('^[a-z0-9][a-z0-9-]{0,31}$')][string]$ProfileName = 'default',
  [ValidateRange(100, 30000)][int]$HelperTimeoutMilliseconds = 10000
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
. (Join-Path $PSScriptRoot 'windows-native-security.ps1')

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$lockPath = Join-Path $root 'docs\dependencies\toolchain-lock.json'
$source = Join-Path $root 'scripts\gmssl-crypto-helper.cs'
$dll = Join-Path $root '.tools\gmssl\3.2.0\GmSSL-3.2.0-win64\bin\gmssl.dll'
$lock = Get-Content -Raw -LiteralPath $lockPath | ConvertFrom-Json
$meta = $lock.tools.gmssl_prototype_provider.helper
function Hash([string]$path) { (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Assert-File([string]$path, [int64]$size, [string]$sha) {
  $item = Get-Item -LiteralPath $path -Force
  if (-not ($item -is [IO.FileInfo]) -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $item.Length -ne $size -or (Hash $path) -ne $sha) { throw 'locked crypto launch chain integrity check failed' }
}
if ($meta.protocol -ne 'COEVOCRYPTO/1' -or $lock.tools.gmssl_prototype_provider.version -ne '3.2.0') { throw 'crypto provider lock metadata is invalid' }
Assert-File $source ([int64]$meta.source_size) ([string]$meta.source_sha256)
Assert-File $dll ([int64]$lock.tools.gmssl_prototype_provider.runtime.library.size) ([string]$lock.tools.gmssl_prototype_provider.runtime.library.sha256)
$compiler = Assert-CoevoLockedCompiler $meta.compiler_lock
$runtime = Join-Path $root '.tools\runtime\gmssl-crypto-helper'
$handles = New-Object System.Collections.ArrayList
$helper = $null
try {
  foreach ($handle in (Enter-CoevoSecureDirectoryChain (Join-Path $root '.tools') $runtime)) { $null = $handles.Add($handle) }
  $compilerProgramData = Join-Path $runtime 'ProgramData'
  foreach ($handle in (Enter-CoevoSecureDirectoryChain (Join-Path $root '.tools') $compilerProgramData)) { $null = $handles.Add($handle) }
  [Environment]::SetEnvironmentVariable('TEMP', $runtime, 'Process')
  [Environment]::SetEnvironmentVariable('TMP', $runtime, 'Process')
  [Environment]::SetEnvironmentVariable('SystemDrive', $runtime, 'Process')
  [Environment]::SetEnvironmentVariable('ProgramData', $compilerProgramData, 'Process')
  $null = $handles.Add((Open-CoevoLockedFile $source ([int64]$meta.source_size) ([string]$meta.source_sha256)))
  $null = $handles.Add((Open-CoevoLockedFile $compiler ([int64]$meta.compiler_lock.size) ([string]$meta.compiler_lock.sha256)))
  $refs = @()
  foreach ($reference in $meta.framework_references) {
    $path = Join-Path (Split-Path -Parent $compiler) ([string]$reference.name)
    Assert-File $path ([int64]$reference.size) ([string]$reference.sha256)
    $null = $handles.Add((Open-CoevoLockedFile $path ([int64]$reference.size) ([string]$reference.sha256)))
    $refs += $path
  }
  $helper = Join-Path $runtime ("helper-$PID-$([Guid]::NewGuid().ToString('N')).exe")
  $global:LASTEXITCODE = 0
  $output = @(& $compiler /nologo /noconfig /nostdlib+ "/reference:$($refs[0])" "/reference:$($refs[1])" /target:exe /platform:x64 /optimize+ /debug- /checked+ "/out:$helper" $source 2>&1)
  for ($probe = 0; $probe -lt 100 -and -not [IO.File]::Exists($helper); $probe++) { [Threading.Thread]::Sleep(10) }
  if ($LASTEXITCODE -ne 0 -or -not [IO.File]::Exists($helper)) { throw 'locked crypto helper compilation failed' }
  $item = Get-Item -LiteralPath $helper -Force
  $null = $handles.Add((Open-CoevoLockedFile $helper ([int64]$item.Length) (Hash $helper)))
  $request = [IO.MemoryStream]::new()
  [Console]::OpenStandardInput().CopyTo($request)
  if ($request.Length -gt 50331648) { throw 'crypto request is too large' }
  $start = [Diagnostics.ProcessStartInfo]::new()
  $start.FileName = $helper; $start.Arguments = ''; $start.WorkingDirectory = $root
  $start.UseShellExecute = $false; $start.CreateNoWindow = $true
  $start.RedirectStandardInput = $true; $start.RedirectStandardOutput = $true; $start.RedirectStandardError = $true
  $start.EnvironmentVariables.Clear()
  $start.EnvironmentVariables['SystemRoot'] = [Environment]::GetEnvironmentVariable('SystemRoot','Process')
  $start.EnvironmentVariables['WINDIR'] = [Environment]::GetEnvironmentVariable('WINDIR','Process')
  $process = [Diagnostics.Process]::new(); $process.StartInfo = $start
  $response = [IO.MemoryStream]::new()
  try {
    if (-not $process.Start()) { throw 'crypto helper failed to start' }
    $stdout = $process.StandardOutput.BaseStream.CopyToAsync($response); $stderr = $process.StandardError.ReadToEndAsync()
    $bytes = $request.ToArray(); $process.StandardInput.BaseStream.Write($bytes,0,$bytes.Length); $process.StandardInput.Close(); [Array]::Clear($bytes,0,$bytes.Length)
    if (-not $process.WaitForExit($HelperTimeoutMilliseconds)) { try { $process.Kill() } catch { }; throw 'crypto helper timed out' }
    if (-not [Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($stdout,$stderr),5000)) { throw 'crypto helper output drain timed out' }
    if ($process.ExitCode -ne 0) {
      if ($stderr.Result -notmatch '(GCP-E-[A-Z0-9-]+)') { throw 'crypto helper failed without stable code' }
      throw $Matches[1]
    }
    # GmSSL writes verification/authentication rejection details to the native
    # stderr stream.  They are intentionally consumed here and never forwarded.
    $out = $response.ToArray(); [Console]::OpenStandardOutput().Write($out,0,$out.Length); [Array]::Clear($out,0,$out.Length)
  } finally { $response.Dispose(); $process.Dispose(); $request.Dispose() }
} finally {
  Close-CoevoDirectoryHandles $handles
  if ($null -ne $helper -and [IO.File]::Exists($helper)) { [IO.File]::Delete($helper) }
}

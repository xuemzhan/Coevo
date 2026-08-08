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
function Test-CachedHelper([string]$exe, [string]$sidecar) {
  # PERF-HELPER-1: a cached helper is trusted only when its sidecar records a
  # 64-hex SHA-256 that matches the binary on disk. Missing/corrupt entries
  # are treated as a cache miss and recompiled (fail-closed, self-healing).
  if (-not [IO.File]::Exists($exe) -or -not [IO.File]::Exists($sidecar)) { return $false }
  $expected = (Get-Content -Raw -LiteralPath $sidecar).Trim()
  if ($expected -notmatch '^[0-9a-f]{64}$') { return $false }
  return (Hash $exe) -eq $expected
}
if ($meta.protocol -ne 'COEVOCRYPTO/1' -or $lock.tools.gmssl_prototype_provider.version -ne '3.2.0') { throw 'crypto provider lock metadata is invalid' }
Assert-File $source ([int64]$meta.source_size) ([string]$meta.source_sha256)
Assert-File $dll ([int64]$lock.tools.gmssl_prototype_provider.runtime.library.size) ([string]$lock.tools.gmssl_prototype_provider.runtime.library.sha256)
$compiler = Assert-CoevoLockedCompiler $meta.compiler_lock
$runtime = Join-Path $root '.tools\runtime\gmssl-crypto-helper'
$cacheDir = Join-Path $runtime 'cache'
$cacheExe = Join-Path $cacheDir ("helper-" + [string]$meta.source_sha256 + ".exe")
$cacheSidecar = "$cacheExe.sha256"
$handles = New-Object System.Collections.ArrayList
$helper = $null
$useCache = $false
try {
  foreach ($handle in (Enter-CoevoSecureDirectoryChain (Join-Path $root '.tools') $runtime)) { $null = $handles.Add($handle) }
  $compilerProgramData = Join-Path $runtime 'ProgramData'
  foreach ($handle in (Enter-CoevoSecureDirectoryChain (Join-Path $root '.tools') $compilerProgramData)) { $null = $handles.Add($handle) }
  foreach ($handle in (Enter-CoevoSecureDirectoryChain (Join-Path $root '.tools') $cacheDir)) { $null = $handles.Add($handle) }
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
  if (Test-CachedHelper $cacheExe $cacheSidecar) {
    # Cache hit: reuse the verified helper for the current call.
    $useCache = $true
    $helper = $cacheExe
    $digest = (Get-Content -Raw -LiteralPath $cacheSidecar).Trim()
    $item = Get-Item -LiteralPath $cacheExe -Force
    $null = $handles.Add((Open-CoevoLockedFile $cacheExe ([int64]$item.Length) $digest))
  } else {
    $helper = Join-Path $runtime ("helper-$PID-$([Guid]::NewGuid().ToString('N')).exe")
    $global:LASTEXITCODE = 0
    $refArgs = foreach ($ref in $refs) { "/reference:$ref" }
    $output = @(& $compiler /nologo /noconfig /nostdlib+ @refArgs /target:exe /platform:x64 /optimize+ /debug- /checked+ "/out:$helper" $source 2>&1)
    # Windows Defender / AV can hold a freshly written helper for a few seconds
    # (the file is invisible to Exists until the scan releases it). Probe for up
    # to 8s instead of 1s so a successful csc run is not misreported as a
    # compile failure (observed as transient GCP-E-LAUNCH).
    for ($probe = 0; $probe -lt 800 -and -not [IO.File]::Exists($helper); $probe++) { [Threading.Thread]::Sleep(10) }
    if ($LASTEXITCODE -ne 0 -or -not [IO.File]::Exists($helper)) { throw 'locked crypto helper compilation failed' }
    $item = Get-Item -LiteralPath $helper -Force
    $null = $handles.Add((Open-CoevoLockedFile $helper ([int64]$item.Length) (Hash $helper)))
    # Best-effort cache install (PERF-HELPER-1): atomically publish a verified
    # copy for later calls. A failed install must never break the current call.
    try {
      $tmpExe = $cacheExe + '.tmp'
      Copy-Item -LiteralPath $helper -Destination $tmpExe -Force
      if ([IO.File]::Exists($tmpExe)) {
        Move-Item -LiteralPath $tmpExe -Destination $cacheExe -Force
        [IO.File]::WriteAllText($cacheSidecar, (Hash $cacheExe))
      }
    } catch {
      # Best-effort only: a cache-install failure never breaks the current call.
    }
  }
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
      throw ($stderr.Result.Trim())
    }
    # GmSSL writes verification/authentication rejection details to the native
    # stderr stream.  They are intentionally consumed here and never forwarded.
    $out = $response.ToArray(); [Console]::OpenStandardOutput().Write($out,0,$out.Length); [Array]::Clear($out,0,$out.Length)
  } finally { $response.Dispose(); $process.Dispose(); $request.Dispose() }
} finally {
  Close-CoevoDirectoryHandles $handles
  if ($null -ne $helper -and -not $useCache -and [IO.File]::Exists($helper)) {
    # The freshly compiled helper may still be held by the AV scanner; a
    # failed cleanup must not turn an already-successful call into a failure.
    for ($retry = 0; $retry -lt 20; $retry++) {
      try { [IO.File]::Delete($helper); break } catch { [Threading.Thread]::Sleep(100) }
    }
  }
}

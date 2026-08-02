[CmdletBinding()]
param(
  [ValidatePattern('^[a-z0-9][a-z0-9-]{0,31}$')]
  [string]$ProfileName = 'default',
  [ValidateRange(100, 45000)]
  [int]$HelperTimeoutMilliseconds = 45000,
  [switch]$TestOnlyForceHelperHang,
  [ValidateSet('', 'after-staging', 'after-files', 'before-receipt', 'after-receipt', 'after-rename')]
  [string]$TestOnlyKillPoint = '',
  [switch]$TestOnlyDropHelperResponse
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
. (Join-Path $PSScriptRoot 'windows-native-security.ps1')

$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$LockPath = Join-Path $Root 'docs\dependencies\toolchain-lock.json'
$HelperSource = Join-Path $Root 'scripts\gmssl-test-pki-helper.cs'
$GmsslDll = Join-Path $Root '.tools\gmssl\3.2.0\GmSSL-3.2.0-win64\bin\gmssl.dll'
$ExpectedDllHash = '9da9cc70507ce7a124b67cfc10c32a6c8c14f08caa6f50a19ecfa21c8f75deb0'

function Get-Sha256([string]$Path) {
  return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Assert-RegularFile([string]$Path, [string]$Label) {
  $item = Get-Item -LiteralPath $Path -Force
  if (-not ($item -is [IO.FileInfo]) -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw "$Label must be a regular non-reparse file" }
}

function Test-FixedTimeEqual([byte[]]$Left, [byte[]]$Right) {
  if ($Left.Length -ne $Right.Length) { return $false }
  $difference = 0
  for ($index = 0; $index -lt $Left.Length; $index++) { $difference = $difference -bor ($Left[$index] -bxor $Right[$index]) }
  return $difference -eq 0
}

function New-HelperRequest([byte]$Action, [byte[]]$Nonce) {
  $profileBytes = [Text.Encoding]::ASCII.GetBytes($ProfileName)
  $request = [IO.MemoryStream]::new()
  $writer = [IO.BinaryWriter]::new($request, [Text.Encoding]::ASCII, $true)
  try {
    $writer.Write([byte[]](0xef, 0xbb, 0xbf))
    $writer.Write([Text.Encoding]::ASCII.GetBytes('COEVOPKI'))
    $writer.Write([byte]2)
    $writer.Write($Action)
    $writer.Write([byte]$profileBytes.Length)
    $writer.Write($profileBytes)
    $writer.Write($Nonce)
    $writer.Flush()
    return $request.ToArray()
  } finally {
    $writer.Dispose()
    $request.Dispose()
    [Array]::Clear($profileBytes, 0, $profileBytes.Length)
  }
}

function Invoke-ZeroArgumentHelper([byte]$Action, [byte[]]$Nonce, [bool]$EnableFaultHooks) {
  $request = New-HelperRequest $Action $Nonce
  $start = [Diagnostics.ProcessStartInfo]::new()
  $start.FileName = $Helper
  $start.Arguments = ''
  $start.WorkingDirectory = $Root
  $start.UseShellExecute = $false
  $start.CreateNoWindow = $true
  $start.RedirectStandardInput = $true
  $start.RedirectStandardOutput = $true
  $start.RedirectStandardError = $true
  $start.EnvironmentVariables.Clear()
  $start.EnvironmentVariables['SystemRoot'] = [Environment]::GetEnvironmentVariable('SystemRoot', 'Process')
  $start.EnvironmentVariables['WINDIR'] = [Environment]::GetEnvironmentVariable('WINDIR', 'Process')
  if ($EnableFaultHooks -and $TestOnlyForceHelperHang) { $start.EnvironmentVariables['COEVO_TEST_ONLY_HELPER_HANG'] = '1' }
  if ($EnableFaultHooks -and $TestOnlyKillPoint.Length -gt 0) { $start.EnvironmentVariables['COEVO_TEST_KILL_POINT'] = $TestOnlyKillPoint }
  if ($EnableFaultHooks -and $TestOnlyDropHelperResponse) { $start.EnvironmentVariables['COEVO_TEST_DROP_RESPONSE'] = '1' }
  $process = [Diagnostics.Process]::new()
  $process.StartInfo = $start
  $responseStream = [IO.MemoryStream]::new()
  try {
    if (-not $process.Start()) { throw 'helper failed to start' }
    $stdoutTask = $process.StandardOutput.BaseStream.CopyToAsync($responseStream)
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $process.StandardInput.BaseStream.Write($request, 0, $request.Length)
    $process.StandardInput.BaseStream.Close()
    if (-not $process.WaitForExit($HelperTimeoutMilliseconds)) {
      try { $process.Kill() } catch { }
      if (-not $process.WaitForExit(5000)) { throw 'helper did not terminate after timeout' }
      if (-not [Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($stdoutTask, $stderrTask), 5000)) { throw 'helper output drain did not terminate' }
      throw 'helper timed out'
    }
    if (-not [Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($stdoutTask, $stderrTask), 5000)) { throw 'helper output drain timed out' }
    $diagnostic = $stderrTask.Result
    if ($process.ExitCode -ne 0) {
      if ($diagnostic -notmatch '^GMH-E-[A-Z0-9-]+\s*$') { throw 'helper failed without a stable error code' }
      throw ('helper failed: ' + $diagnostic.Trim())
    }
    if (-not [string]::IsNullOrEmpty($diagnostic)) { throw 'helper emitted unexpected diagnostics' }
    $response = $responseStream.ToArray()
    if ($response.Length -ne 59) { throw 'helper response length is invalid' }
    $reader = [IO.BinaryReader]::new([IO.MemoryStream]::new($response, $false), [Text.Encoding]::ASCII)
    try {
      if ([Text.Encoding]::ASCII.GetString($reader.ReadBytes(8)) -ne 'COEVORS2' -or $reader.ReadByte() -ne 2) { throw 'helper response header is invalid' }
      if ($reader.ReadByte() -ne $Action) { throw 'helper response action mismatch' }
      $status = $reader.ReadByte()
      if ($status -lt 1 -or $status -gt 3) { throw 'helper response status is invalid' }
      $responseNonce = $reader.ReadBytes(16)
      $receiptHash = $reader.ReadBytes(32)
      if ($responseNonce.Length -ne 16 -or -not (Test-FixedTimeEqual $Nonce $responseNonce)) { throw 'helper response nonce mismatch' }
      if ($receiptHash.Length -ne 32 -or $reader.BaseStream.Position -ne $reader.BaseStream.Length) { throw 'helper response frame is invalid' }
      return [pscustomobject]@{ Status = [int]$status; ReceiptHash = $receiptHash }
    } finally { $reader.Dispose() }
  } finally {
    [Array]::Clear($request, 0, $request.Length)
    $responseStream.Dispose()
    $process.Dispose()
  }
}

if (-not (Test-Path -LiteralPath $LockPath -PathType Leaf)) { throw 'toolchain lock is missing' }
$lock = Get-Content -Raw -LiteralPath $LockPath | ConvertFrom-Json
$tool = $lock.tools.gmssl_test_pki
$helperLock = $tool.helper
if ($null -eq $tool -or $tool.version -ne '3.2.0' -or $tool.scope -notmatch '^test-only' -or $null -eq $helperLock -or
    $helperLock.protocol -ne 'COEVOPKI/2' -or $helperLock.launcher.path -ne 'scripts/generate-sm2-test-pki.ps1') { throw 'GmSSL helper lock metadata is invalid' }
if ((Get-Sha256 $MyInvocation.MyCommand.Path) -ne $helperLock.launcher.sha256 -or (Get-Item -LiteralPath $MyInvocation.MyCommand.Path).Length -ne [int64]$helperLock.launcher.size) { throw 'GmSSL helper launcher source lock mismatch' }
if ($tool.runtime.library.path -ne '.tools/gmssl/3.2.0/GmSSL-3.2.0-win64/bin/gmssl.dll' -or $tool.runtime.library.sha256 -ne $ExpectedDllHash -or [int64]$tool.runtime.library.size -ne 1665024) { throw 'GmSSL library lock metadata mismatch' }
Assert-RegularFile $GmsslDll 'GmSSL library'
Assert-RegularFile $HelperSource 'helper source'
if ((Get-Sha256 $GmsslDll) -ne $ExpectedDllHash -or (Get-Sha256 $HelperSource) -ne $helperLock.source_sha256 -or (Get-Item -LiteralPath $HelperSource).Length -ne [int64]$helperLock.source_size) { throw 'locked helper launch chain integrity check failed' }

$Compiler = Assert-CoevoLockedCompiler $helperLock.compiler_lock
$ToolsRoot = [IO.Path]::GetFullPath((Join-Path $Root '.tools'))
$HelperRuntime = Join-Path $ToolsRoot 'runtime\sm2-test-pki-helper'
$secureHandles = New-Object System.Collections.ArrayList
$Helper = $null
try {
  foreach ($handle in (Enter-CoevoSecureDirectoryChain $ToolsRoot $HelperRuntime)) { $null = $secureHandles.Add($handle) }
  foreach ($staleHelper in @(Get-ChildItem -LiteralPath $HelperRuntime -Filter 'helper-*.exe' -File -Force -ErrorAction SilentlyContinue)) {
    if (($staleHelper.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) { try { [IO.File]::Delete($staleHelper.FullName) } catch [IO.IOException] { } }
  }
  $null = $secureHandles.Add((Open-CoevoLockedFile $HelperSource ([int64]$helperLock.source_size) ([string]$helperLock.source_sha256)))
  $null = $secureHandles.Add((Open-CoevoLockedFile $Compiler ([int64]$helperLock.compiler_lock.size) ([string]$helperLock.compiler_lock.sha256)))
  $frameworkPaths = @()
  foreach ($reference in $helperLock.framework_references) {
    $referencePath = Join-Path (Split-Path -Parent $Compiler) ([string]$reference.name)
    Assert-RegularFile $referencePath 'framework reference'
    $null = $secureHandles.Add((Open-CoevoLockedFile $referencePath ([int64]$reference.size) ([string]$reference.sha256)))
    $frameworkPaths += $referencePath
  }
  $Helper = Join-Path $HelperRuntime ("helper-$PID-$([Guid]::NewGuid().ToString('N')).exe")
  $compilerEnvironment = @{}
  foreach ($name in @('CSC','CscToolPath','CscToolExe','FrameworkPathOverride','LIB','LIBPATH')) {
    $value = [Environment]::GetEnvironmentVariable($name, 'Process')
    if ($null -ne $value) { $compilerEnvironment[$name] = $value }
    [Environment]::SetEnvironmentVariable($name, $null, 'Process')
  }
  try {
    $compilerOutput = @(& $Compiler /nologo /noconfig /nostdlib+ "/reference:$($frameworkPaths[0])" "/reference:$($frameworkPaths[1])" /target:exe /platform:x64 /optimize+ /debug- /checked+ "/out:$Helper" $HelperSource 2>&1)
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $Helper -PathType Leaf)) { throw 'locked helper compilation failed' }
    Assert-RegularFile $Helper 'compiled helper'
    $helperBuiltHash = Get-Sha256 $Helper
    $null = $secureHandles.Add((Open-CoevoLockedFile $Helper ([int64](Get-Item -LiteralPath $Helper).Length) $helperBuiltHash))
  } finally {
    foreach ($name in @('CSC','CscToolPath','CscToolExe','FrameworkPathOverride','LIB','LIBPATH')) { [Environment]::SetEnvironmentVariable($name, $(if ($compilerEnvironment.ContainsKey($name)) { $compilerEnvironment[$name] } else { $null }), 'Process') }
    $compilerOutput = $null
  }

  $nonce = [byte[]]::new(16)
  $random = [Security.Cryptography.RandomNumberGenerator]::Create()
  try { $random.GetBytes($nonce) } finally { $random.Dispose() }
  try {
    $original = $null
    try {
      $result = Invoke-ZeroArgumentHelper 1 $nonce $true
      if ($result.Status -ne 1) { throw 'generate action did not commit' }
    } catch {
      $original = $_
      $recovery = Invoke-ZeroArgumentHelper 2 $nonce $false
      if ($recovery.Status -ne 1) { throw $original }
    }
    Write-Output "Generated isolated test-only SM2 PKI profile '$ProfileName'."
  } finally { [Array]::Clear($nonce, 0, $nonce.Length) }
} finally {
  Close-CoevoDirectoryHandles $secureHandles
  if ($null -ne $Helper -and (Test-Path -LiteralPath $Helper -PathType Leaf)) { [IO.File]::Delete($Helper) }
}

[CmdletBinding()]
param([string]$ArchivePath)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$UtilityModule=Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Utility\Microsoft.PowerShell.Utility.psd1'
$SecurityModule=Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1'
Import-Module $UtilityModule -ErrorAction Stop
Import-Module $SecurityModule -ErrorAction Stop
. (Join-Path $PSScriptRoot 'windows-native-security.ps1')
$Root=[System.IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$ToolsRoot=[System.IO.Path]::GetFullPath((Join-Path $Root '.tools'))
$Lock=Get-Content (Join-Path $Root 'docs\dependencies\toolchain-lock.json') -Raw | ConvertFrom-Json
$Tool=$Lock.tools.opencode

function LockedToolsPath([string]$Relative){
  if([System.IO.Path]::IsPathRooted($Relative)){ throw 'Locked tool target must be relative.' }
  if(@($Relative -split '[\\/]' | Where-Object {$_ -eq '..'}).Count){ throw 'Locked tool target contains traversal.' }
  $Full=[System.IO.Path]::GetFullPath((Join-Path $Root $Relative))
  $Prefix=$ToolsRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar)+[System.IO.Path]::DirectorySeparatorChar
  if(-not $Full.StartsWith($Prefix,[System.StringComparison]::OrdinalIgnoreCase)){ throw 'Locked tool target escapes repository .tools.' }
  return $Full
}
function Assert-NoReparseParent([string]$Path){
  $Current=Split-Path -Parent $Path
  while($Current -and $Current.StartsWith($ToolsRoot,[System.StringComparison]::OrdinalIgnoreCase)){
    if(Test-Path -LiteralPath $Current){
      $Attributes=(Get-Item -LiteralPath $Current -Force).Attributes
      if(($Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0){ throw 'Locked tool target parent is a reparse point.' }
    }
    if($Current -eq $ToolsRoot){ break }
    $Current=Split-Path -Parent $Current
  }
}

$LockedHandles=New-Object System.Collections.ArrayList
try {
if(-not $ArchivePath){ $ArchivePath=LockedToolsPath $Tool.archive.path }
$Archive=(Resolve-Path -LiteralPath $ArchivePath).Path
if((Get-Item -LiteralPath $Archive).Length -ne $Tool.archive.size){ throw 'OpenCode archive size mismatch.' }
if((Get-FileHash -LiteralPath $Archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $Tool.archive.sha256){ throw 'OpenCode archive hash mismatch.' }
$Destination=LockedToolsPath $Tool.executable.path
Assert-NoReparseParent $Destination
$Directory=Split-Path -Parent $Destination
foreach($Handle in (Enter-CoevoSecureDirectoryChain $ToolsRoot $Directory)){ $null=$LockedHandles.Add($Handle) }
if(Test-Path -LiteralPath $Destination){
  $Existing=(Get-FileHash -LiteralPath $Destination -Algorithm SHA256).Hash.ToLowerInvariant()
  if($Existing -ne $Tool.executable.sha256){ throw 'Refusing to overwrite a mismatched OpenCode executable.' }
  Write-Output 'Locked OpenCode executable is already present.'; exit 0
}

Add-Type -AssemblyName System.IO.Compression.FileSystem
$Zip=[System.IO.Compression.ZipFile]::OpenRead($Archive)
try {
  $Entries=@($Zip.Entries)
  if($Entries.Count -ne 1 -or $Entries[0].FullName -ne 'opencode.exe'){ throw 'Unexpected OpenCode archive contents.' }
  if($Entries[0].Length -ne $Tool.executable.size){ throw 'OpenCode executable size mismatch in archive.' }
  Assert-NoReparseParent $Destination
  # Create the final name once and keep an exclusive writer/delete lock from
  # the first byte through hash/signature verification; no later Move pathname exists.
  $Input=$Entries[0].Open()
  $Output=New-Object IO.FileStream($Destination,[IO.FileMode]::CreateNew,[IO.FileAccess]::ReadWrite,[IO.FileShare]::Read)
  try { $Input.CopyTo($Output); $Output.Flush($true) }
  catch {
    $Output.Dispose()
    if(Test-Path -LiteralPath $Destination){ [IO.File]::Delete($Destination) }
    throw
  } finally { $Input.Dispose() }
} finally { $Zip.Dispose() }
try {
  Assert-NoReparseParent $Destination
  $Output.Position=0
  $Hasher=[Security.Cryptography.SHA256]::Create()
  try { $Actual=([BitConverter]::ToString($Hasher.ComputeHash($Output))).Replace('-','').ToLowerInvariant() }
  finally { $Hasher.Dispose() }
  if($Actual -ne $Tool.executable.sha256){ throw 'Extracted OpenCode executable hash mismatch.' }
  $Signature=Get-AuthenticodeSignature -LiteralPath $Destination
  if($Signature.Status -ne 'Valid' -or $Signature.SignerCertificate.Thumbprint -ne $Tool.executable.signer_thumbprint){ throw 'Extracted OpenCode signer mismatch.' }
} catch {
  $Output.Dispose()
  if(Test-Path -LiteralPath $Destination){ [System.IO.File]::Delete($Destination) }
  throw
} finally { if($Output){ $Output.Dispose() } }
Write-Output 'Locked OpenCode executable imported successfully.'
} finally { Close-CoevoDirectoryHandles $LockedHandles }

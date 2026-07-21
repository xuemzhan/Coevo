[CmdletBinding()]
param([switch]$Quiet)

. (Join-Path $PSScriptRoot 'windows-native-security.ps1')

function Initialize-CoevoDevelopmentEnvironment {
  [CmdletBinding()]
  param([switch]$Quiet)
  $ErrorActionPreference='Stop'
  Set-StrictMode -Version Latest
  $UtilityModule=Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Utility\Microsoft.PowerShell.Utility.psd1'
  $SecurityModule=Join-Path $PSHOME 'Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1'
  Import-Module $UtilityModule -ErrorAction Stop
  Import-Module $SecurityModule -ErrorAction Stop
  $Root=Split-Path -Parent $PSScriptRoot
  $ToolsRoot=[IO.Path]::GetFullPath((Join-Path $Root '.tools'))
  function LockedToolPath([string]$Relative){
    if([IO.Path]::IsPathRooted($Relative)){ throw 'Locked tool path must be relative.' }
    if(@($Relative -split '[\\/]' | Where-Object {$_ -eq '..'}).Count){ throw 'Locked tool path contains traversal.' }
    $Full=[IO.Path]::GetFullPath((Join-Path $Root $Relative))
    $Prefix=$ToolsRoot.TrimEnd('\')+'\'
    if(-not $Full.StartsWith($Prefix,[StringComparison]::OrdinalIgnoreCase)){ throw 'Locked tool path escapes repository .tools.' }
    return $Full
  }
  $Previous=Get-Variable -Name CoevoDevelopmentEnvironmentHandles -Scope Global -ErrorAction SilentlyContinue
  if($Previous){ Close-CoevoDirectoryHandles $Previous.Value; Remove-Variable -Name CoevoDevelopmentEnvironmentHandles -Scope Global }
  $LockedHandles=New-Object System.Collections.ArrayList
  $Ready=$false
  try {
  $ManifestPath=Join-Path $Root 'docs\dependencies\toolchain-lock.json'
  if(-not (Test-Path -LiteralPath $ManifestPath)){ throw 'Missing toolchain lock manifest.' }
  $Manifest=Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
  $OpenCode=$Manifest.tools.opencode
  $Archive=LockedToolPath $OpenCode.archive.path
  $Executable=LockedToolPath $OpenCode.executable.path
  foreach($Path in @((Split-Path -Parent $Archive),(Split-Path -Parent $Executable))){ foreach($Handle in (Enter-CoevoSecureDirectoryChain $ToolsRoot $Path)){ $null=$LockedHandles.Add($Handle) } }
  foreach($Item in @(@($Archive,$OpenCode.archive.sha256,$OpenCode.archive.size),@($Executable,$OpenCode.executable.sha256,$OpenCode.executable.size))){
    if(-not (Test-Path -LiteralPath $Item[0] -PathType Leaf)){ throw "Missing locked tool artifact: $($Item[0])" }
    if((Get-Item -LiteralPath $Item[0]).Length -ne $Item[2]){ throw "Tool artifact size mismatch: $($Item[0])" }
    $Actual=(Get-FileHash -LiteralPath $Item[0] -Algorithm SHA256).Hash.ToLowerInvariant()
    if($Actual -ne $Item[1]){ throw "Tool artifact hash mismatch: $($Item[0])" }
  }
  $null=$LockedHandles.Add((Open-CoevoLockedFile $Executable ([int64]$OpenCode.executable.size) ([string]$OpenCode.executable.sha256)))
  $Signature=Get-AuthenticodeSignature -LiteralPath $Executable
  if($Signature.Status -ne 'Valid' -or $Signature.SignerCertificate.Thumbprint -ne $OpenCode.executable.signer_thumbprint){ throw 'OpenCode Authenticode signer validation failed.' }

  $Bin=Join-Path $ToolsRoot ("bin-$PID")
  foreach($Handle in (Enter-CoevoSecureDirectoryChain $ToolsRoot $Bin)){ $null=$LockedHandles.Add($Handle) }
  $MakeSource=Join-Path $Root 'scripts\tool-shims\make.cs'
  $MakeSourceHash=(Get-FileHash -LiteralPath $MakeSource -Algorithm SHA256).Hash.ToLowerInvariant()
  if($MakeSourceHash -ne $Manifest.tools.make_compatibility_shim.source_sha256){ throw 'Make shim source hash mismatch.' }
  $null=$LockedHandles.Add((Open-CoevoLockedFile $MakeSource ([int64](Get-Item -LiteralPath $MakeSource).Length) $MakeSourceHash))
  $Compiler=Assert-CoevoLockedCompiler $Manifest.tools.make_compatibility_shim.compiler_lock
  $null=$LockedHandles.Add((Open-CoevoLockedFile $Compiler ([int64]$Manifest.tools.make_compatibility_shim.compiler_lock.size) ([string]$Manifest.tools.make_compatibility_shim.compiler_lock.sha256)))
  function Install-MakeShim([string]$Target){
    $Temporary=Join-Path $Bin ("make-$PID-$([Guid]::NewGuid().ToString('N')).next.exe")
    try {
      $CompilerOutput=@(& $Compiler /nologo /optimize+ /target:exe "/out:$Temporary" $MakeSource)
      if($LASTEXITCODE -ne 0){ throw 'Failed to build the local make compatibility shim.' }
      $BuiltHash=(Get-FileHash -LiteralPath $Temporary -Algorithm SHA256).Hash.ToLowerInvariant()
      if(Test-Path -LiteralPath $Target){
        $ExistingHash=(Get-FileHash -LiteralPath $Target -Algorithm SHA256).Hash.ToLowerInvariant()
        if($ExistingHash -eq $BuiltHash){ return $BuiltHash }
        [System.IO.File]::Delete($Target)
      }
      [System.IO.File]::Move($Temporary,$Target)
      if((Get-FileHash -LiteralPath $Target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $BuiltHash){ throw 'Make shim atomic installation verification failed.' }
      return $BuiltHash
    } finally { if(Test-Path -LiteralPath $Temporary){ [System.IO.File]::Delete($Temporary) } }
  }
  $Make=Join-Path $Bin 'make.exe'
  $BuiltHash=Install-MakeShim $Make
  $ExternalMake=$Make
  $ExternalMakeHash=$BuiltHash
  $null=$LockedHandles.Add((Open-CoevoLockedFile $Make ([int64](Get-Item -LiteralPath $Make).Length) $BuiltHash))

  $Python=LockedToolPath $Manifest.tools.python.executable.path
  $null=$LockedHandles.Add((Open-CoevoLockedFile $Python ([int64]$Manifest.tools.python.executable.size) ([string]$Manifest.tools.python.executable.sha256)))
  $RuntimeInventory=LockedToolPath $Manifest.tools.python.inventory.path
  $null=$LockedHandles.Add((Open-CoevoLockedFile $RuntimeInventory ([int64]$Manifest.tools.python.inventory.size) ([string]$Manifest.tools.python.inventory.sha256)))
  $Control=LockedToolPath $Manifest.tools.control_archive.path
  $null=$LockedHandles.Add((Open-CoevoLockedFile $Control ([int64]$Manifest.tools.control_archive.size) ([string]$Manifest.tools.control_archive.sha256)))
  $AuditSignature=[IO.Path]::GetFullPath((Join-Path $Root ([string]$Manifest.tools.control_archive.audit_signature_path)))
  if(-not $AuditSignature.StartsWith(([IO.Path]::GetFullPath((Join-Path $Root 'scripts'))+'\'),[StringComparison]::OrdinalIgnoreCase)){ throw 'Audit signature path escapes scripts.' }
  $null=$LockedHandles.Add((Open-CoevoLockedFile $AuditSignature ([int64]$Manifest.tools.control_archive.audit_signature_size) ([string]$Manifest.tools.control_archive.audit_signature_sha256)))

  $Node=LockedToolPath $Manifest.tools.make_compatibility_shim.node.executable.path
  $null=$LockedHandles.Add((Open-CoevoLockedFile $Node ([int64]$Manifest.tools.make_compatibility_shim.node.executable.size) ([string]$Manifest.tools.make_compatibility_shim.node.executable.sha256)))
  $NodeSignature=Get-AuthenticodeSignature -LiteralPath $Node
  if($NodeSignature.Status -ne 'Valid' -or $NodeSignature.SignerCertificate.Thumbprint -ne $Manifest.tools.make_compatibility_shim.node.executable.signer_thumbprint){ throw 'Node.js Authenticode signer validation failed.' }
  $PowerShell=[IO.Path]::GetFullPath((Join-Path (Get-CoevoWindowsDirectory) ([string]$Manifest.tools.make_compatibility_shim.windows_powershell.windows_directory_relative_path)))
  $null=$LockedHandles.Add((Open-CoevoLockedFile $PowerShell ([int64]$Manifest.tools.make_compatibility_shim.windows_powershell.size) ([string]$Manifest.tools.make_compatibility_shim.windows_powershell.sha256)))
  $PowerShellSignature=Get-AuthenticodeSignature -LiteralPath $PowerShell
  if($PowerShellSignature.Status -ne 'Valid' -or $PowerShellSignature.SignerCertificate.Thumbprint -ne $Manifest.tools.make_compatibility_shim.windows_powershell.signer_thumbprint){ throw 'Windows PowerShell Authenticode signer validation failed.' }



  $Runtime=Join-Path $Root '.tools\runtime'
  foreach($Name in ('config','data','cache','config\opencode')){ foreach($Handle in (Enter-CoevoSecureDirectoryChain $ToolsRoot (Join-Path $Runtime $Name))){ $null=$LockedHandles.Add($Handle) } }
  foreach($Name in ('OPENCODE_CONFIG','OPENCODE_CONFIG_DIR','OPENCODE_CONFIG_CONTENT','OPENCODE_PERMISSION','OPENCODE_DISABLE_PROJECT_CONFIG','OPENCODE_PURE','OPENCODE_ENABLE_EXA','OPENCODE_AUTO_SHARE','OPENCODE_DISABLE_CLAUDE_CODE','OPENCODE_DISABLE_EXTERNAL_SKILLS')){ Remove-Item ("Env:"+$Name) -ErrorAction SilentlyContinue }
  $env:XDG_CONFIG_HOME=Join-Path $Runtime 'config'
  $env:XDG_DATA_HOME=Join-Path $Runtime 'data'
  $env:XDG_CACHE_HOME=Join-Path $Runtime 'cache'
  $env:OPENCODE_CONFIG=Join-Path $Root 'opencode.jsonc'
  $env:OPENCODE_CONFIG_DIR=Join-Path $Runtime 'config\opencode'
  $env:OPENCODE_CONFIG_CONTENT='{"autoupdate":false,"lsp":false,"permission":{"external_directory":"deny","webfetch":"deny","websearch":"deny"}}'
  $env:OPENCODE_PERMISSION='{"external_directory":"deny","webfetch":"deny","websearch":"deny"}'
  $env:OPENCODE_DISABLE_AUTOUPDATE='true'
  $env:OPENCODE_DISABLE_LSP_DOWNLOAD='true'
  $env:OPENCODE_ENABLE_EXA='false'
  $env:OPENCODE_AUTO_SHARE='false'
  $env:OPENCODE_DISABLE_CLAUDE_CODE='true'
  $env:OPENCODE_DISABLE_EXTERNAL_SKILLS='true'
  $env:COEVO_OPENCODE_PATH=$Executable
  $env:COEVO_MAKE_PATH=$Make
  $env:COEVO_MAKE_SHA256=$BuiltHash
  $env:COEVO_EXTERNAL_MAKE_PATH=$ExternalMake
  $env:COEVO_EXTERNAL_MAKE_SHA256=$ExternalMakeHash
  $env:COEVO_PYTHON_PATH=$Python
  $env:COEVO_PYTHON_SHA256=[string]$Manifest.tools.python.executable.sha256
  $env:COEVO_NODE_PATH=$Node
  $env:COEVO_NODE_SHA256=[string]$Manifest.tools.make_compatibility_shim.node.executable.sha256
  $env:COEVO_POWERSHELL_PATH=$PowerShell
  $env:COEVO_POWERSHELL_SHA256=[string]$Manifest.tools.make_compatibility_shim.windows_powershell.sha256
  $env:COEVO_REPO_ROOT=$Root

  $OpenCodeBin= Split-Path -Parent $Executable
  $PowerShellDir=[IO.Path]::GetDirectoryName($PowerShell)
  $LockedPathEntries=@($OpenCodeBin,$Bin,$PowerShellDir)
  $GitExe=(Get-Command git.exe -ErrorAction SilentlyContinue)
  $GitDir=$null
  if($GitExe){ $GitDir=[IO.Path]::GetDirectoryName(($GitExe.Source -replace '^& ','')) }
  $ExistingPath=$env:PATH -split ';' | Where-Object { $_ -and $_ -ne $OpenCodeBin -and $_ -ne $Bin -and $_ -ne $PowerShellDir -and $_ -ne $GitDir } | Select-Object -Unique
  if($GitDir){ $LockedPathEntries+=@($GitDir) }
  $CanonicalPath=($LockedPathEntries+$ExistingPath) -join ';'
  Remove-Item -LiteralPath Env:Path -ErrorAction SilentlyContinue
  Remove-Item -LiteralPath Env:PATH -ErrorAction SilentlyContinue
  $env:Path=$CanonicalPath

  Set-Alias -Name make -Value $Make -Scope Global -Force
  Set-Alias -Name opencode -Value $Executable -Scope Global -Force
  $ResolvedMake=Get-Command make
  if($ResolvedMake.CommandType -ne 'Alias' -or $ResolvedMake.Definition -ne $Make){ throw 'Make path shadowing detected.' }
  $env:COEVO_CONTROL_ARCHIVE=$Control
  $env:COEVO_CONTROL_SHA256=[string]$Manifest.tools.control_archive.sha256
  if(-not $Quiet){ Write-Host 'Coevo development environment ready'; & $Executable --version; & $Make --version }
  $Global:CoevoDevelopmentEnvironmentHandles=$LockedHandles.ToArray()
  $Ready=$true
  } finally { if(-not $Ready){ Close-CoevoDirectoryHandles $LockedHandles } }
}

try { Initialize-CoevoDevelopmentEnvironment -Quiet:$Quiet }
finally { Remove-Item Function:\Initialize-CoevoDevelopmentEnvironment -ErrorAction SilentlyContinue }

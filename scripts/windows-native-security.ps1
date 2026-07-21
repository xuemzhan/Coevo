Set-StrictMode -Version Latest

function Initialize-CoevoWindowsNative {
  if(('Coevo.WindowsNative' -as [type])){ return }
  $AssemblyName=New-Object System.Reflection.AssemblyName('Coevo.WindowsNative.Dynamic')
  $Assembly=[AppDomain]::CurrentDomain.DefineDynamicAssembly($AssemblyName,[System.Reflection.Emit.AssemblyBuilderAccess]::Run)
  $Module=$Assembly.DefineDynamicModule('Coevo.WindowsNative.Dynamic')
  $Type=$Module.DefineType('Coevo.WindowsNative','Public,Sealed,Abstract')
  $Attrs=[System.Reflection.MethodAttributes]::Public -bor [System.Reflection.MethodAttributes]::Static -bor [System.Reflection.MethodAttributes]::PinvokeImpl
  $ManagedCall=[System.Reflection.CallingConventions]::Standard
  $Call=[System.Runtime.InteropServices.CallingConvention]::Winapi
  $Unicode=[System.Runtime.InteropServices.CharSet]::Unicode
  $Ansi=[System.Runtime.InteropServices.CharSet]::Auto
  $Create=$Type.DefinePInvokeMethod('CreateFileW','kernel32.dll','CreateFileW',$Attrs,$ManagedCall,[IntPtr],@([string],[uint32],[uint32],[IntPtr],[uint32],[uint32],[IntPtr]),$Call,$Unicode)
  $Create.SetImplementationFlags($Create.GetMethodImplementationFlags() -bor [System.Reflection.MethodImplAttributes]::PreserveSig)
  $Final=$Type.DefinePInvokeMethod('GetFinalPathNameByHandleW','kernel32.dll','GetFinalPathNameByHandleW',$Attrs,$ManagedCall,[uint32],@([IntPtr],[System.Text.StringBuilder],[uint32],[uint32]),$Call,$Unicode)
  $Final.SetImplementationFlags($Final.GetMethodImplementationFlags() -bor [System.Reflection.MethodImplAttributes]::PreserveSig)
  $Control=$Type.DefinePInvokeMethod('DeviceIoControl','kernel32.dll','DeviceIoControl',$Attrs,$ManagedCall,[bool],@([IntPtr],[uint32],[IntPtr],[uint32],[byte[]],[uint32],[uint32].MakeByRefType(),[IntPtr]),$Call,$Ansi)
  $Control.SetImplementationFlags($Control.GetMethodImplementationFlags() -bor [System.Reflection.MethodImplAttributes]::PreserveSig)
  $Close=$Type.DefinePInvokeMethod('CloseHandle','kernel32.dll','CloseHandle',$Attrs,$ManagedCall,[bool],@([IntPtr]),$Call,$Ansi)
  $Close.SetImplementationFlags($Close.GetMethodImplementationFlags() -bor [System.Reflection.MethodImplAttributes]::PreserveSig)
  $Windows=$Type.DefinePInvokeMethod('GetWindowsDirectoryW','kernel32.dll','GetWindowsDirectoryW',$Attrs,$ManagedCall,[uint32],@([System.Text.StringBuilder],[uint32]),$Call,$Unicode)
  $Windows.SetImplementationFlags($Windows.GetMethodImplementationFlags() -bor [System.Reflection.MethodImplAttributes]::PreserveSig)
  $null=$Type.CreateType()
}

function Close-CoevoDirectoryHandles([System.Collections.IEnumerable]$Handles){
  if($null -eq $Handles){ return }
  foreach($Handle in @($Handles)){
    if($Handle -ne [IntPtr]::Zero -and $Handle -ne [IntPtr](-1)){ $null=[Coevo.WindowsNative]::CloseHandle($Handle) }
  }
}

function Get-CoevoHandlePath([IntPtr]$Handle){
  $Buffer=New-Object System.Text.StringBuilder 32768
  $Length=[Coevo.WindowsNative]::GetFinalPathNameByHandleW($Handle,$Buffer,$Buffer.Capacity,0)
  if($Length -eq 0 -or $Length -ge $Buffer.Capacity){ throw 'Unable to resolve locked file handle.' }
  return [IO.Path]::GetFullPath((ConvertFrom-CoevoFinalPath $Buffer.ToString())).TrimEnd('\')
}

function Open-CoevoLockedFile([string]$Path,[Nullable[int64]]$ExpectedSize=$null,[string]$ExpectedSha256=$null){
  Initialize-CoevoWindowsNative
  $Full=[IO.Path]::GetFullPath($Path)
  # GENERIC_READ with FILE_SHARE_READ prevents replacement, deletion, and writes
  # while allowing the validated image to be loaded by a child process.
  $Handle=[Coevo.WindowsNative]::CreateFileW($Full,[uint32]2147483648,1,[IntPtr]::Zero,3,0x00000080,[IntPtr]::Zero)
  if($Handle -eq [IntPtr](-1)){ throw "Unable to lock file: $Full (Win32 $([Runtime.InteropServices.Marshal]::GetLastWin32Error()))." }
  try {
    $Final=Get-CoevoHandlePath $Handle
    if(-not $Final.Equals($Full,[StringComparison]::OrdinalIgnoreCase)){ throw "Locked file resolves outside its approved path: $Full" }
    $Safe=New-Object Microsoft.Win32.SafeHandles.SafeFileHandle($Handle,$false)
    $Stream=New-Object IO.FileStream($Safe,[IO.FileAccess]::Read,1048576)
    try {
      if($null -ne $ExpectedSize -and $Stream.Length -ne [int64]$ExpectedSize){ throw "Locked file size mismatch: $Full" }
      if($ExpectedSha256){
        $Hasher=[Security.Cryptography.SHA256]::Create()
        try { $Actual=([BitConverter]::ToString($Hasher.ComputeHash($Stream))).Replace('-','').ToLowerInvariant() }
        finally { $Hasher.Dispose() }
        if($Actual -ne $ExpectedSha256.ToLowerInvariant()){ throw "Locked file hash mismatch: $Full" }
      }
    } finally { $Stream.Dispose(); $Safe.Dispose() }
    return $Handle
  } catch {
    $null=[Coevo.WindowsNative]::CloseHandle($Handle)
    throw
  }
}

function ConvertFrom-CoevoFinalPath([string]$Path){
  if($Path.StartsWith('\\?\UNC\',[StringComparison]::OrdinalIgnoreCase)){ return '\\'+$Path.Substring(8) }
  if($Path.StartsWith('\\?\',[StringComparison]::OrdinalIgnoreCase)){ return $Path.Substring(4) }
  return $Path
}

function Open-CoevoLockedDirectory([string]$Path){
  Initialize-CoevoWindowsNative
  $Full=[IO.Path]::GetFullPath($Path).TrimEnd('\')
  $Before=Get-Item -LiteralPath $Full -Force -ErrorAction Stop
  if(($Before.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){ throw "Locked tool directory is a reparse point: $Full" }
  $Handle=[Coevo.WindowsNative]::CreateFileW($Full,0,3,[IntPtr]::Zero,3,0x02200000,[IntPtr]::Zero)
  if($Handle -eq [IntPtr](-1)){ throw "Unable to lock tool directory: $Full (Win32 $([Runtime.InteropServices.Marshal]::GetLastWin32Error()))." }
  try {
    # Denying FILE_SHARE_DELETE keeps this directory stable. Re-checking after
    # open closes the attribute-check/open race without trusting a stale path.
    $After=Get-Item -LiteralPath $Full -Force -ErrorAction Stop
    if(($After.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){ throw "Locked tool directory is a reparse point: $Full" }
    $Final=Get-CoevoHandlePath $Handle
    if(-not $Final.Equals($Full,[StringComparison]::OrdinalIgnoreCase)){ throw "Locked tool directory resolves outside its approved path: $Full" }
    return $Handle
  } catch {
    $null=[Coevo.WindowsNative]::CloseHandle($Handle)
    throw
  }
}

function Enter-CoevoSecureDirectoryChain([string]$ToolsRoot,[string]$Directory){
  $Root=[IO.Path]::GetFullPath($ToolsRoot).TrimEnd('\')
  $Target=[IO.Path]::GetFullPath($Directory).TrimEnd('\')
  $Prefix=$Root+'\'
  if($Target -ne $Root -and -not $Target.StartsWith($Prefix,[StringComparison]::OrdinalIgnoreCase)){ throw 'Tool directory escapes repository .tools.' }
  $Handles=New-Object System.Collections.ArrayList
  try {
    if(-not [IO.Directory]::Exists($Root)){ $null=[IO.Directory]::CreateDirectory($Root) }
    $null=$Handles.Add((Open-CoevoLockedDirectory $Root))
    $Current=$Root
    if($Target -ne $Root){
      foreach($Part in $Target.Substring($Prefix.Length).Split('\')){
        $Current=[IO.Path]::Combine($Current,$Part)
        if(-not [IO.Directory]::Exists($Current)){ $null=[IO.Directory]::CreateDirectory($Current) }
        $null=$Handles.Add((Open-CoevoLockedDirectory $Current))
      }
    }
    return ,$Handles.ToArray()
  } catch {
    Close-CoevoDirectoryHandles $Handles
    throw
  }
}

function Get-CoevoWindowsDirectory {
  Initialize-CoevoWindowsNative
  $Buffer=New-Object System.Text.StringBuilder 32768
  $Length=[Coevo.WindowsNative]::GetWindowsDirectoryW($Buffer,$Buffer.Capacity)
  if($Length -eq 0 -or $Length -ge $Buffer.Capacity){ throw 'Unable to resolve the trusted Windows directory.' }
  return [IO.Path]::GetFullPath($Buffer.ToString()).TrimEnd('\')
}

function Assert-CoevoLockedCompiler($CompilerLock){
  $Windows=Get-CoevoWindowsDirectory
  $Compiler=[IO.Path]::GetFullPath((Join-Path $Windows ([string]$CompilerLock.windows_directory_relative_path)))
  $Prefix=$Windows+'\'
  if(-not $Compiler.StartsWith($Prefix,[StringComparison]::OrdinalIgnoreCase)){ throw 'Locked compiler path escapes the Windows directory.' }
  if(-not (Test-Path -LiteralPath $Compiler -PathType Leaf)){ throw 'Missing locked Windows C# compiler.' }
  if((Get-Item -LiteralPath $Compiler -Force).Length -ne [int64]$CompilerLock.size){ throw 'Windows C# compiler size mismatch.' }
  if((Get-FileHash -LiteralPath $Compiler -Algorithm SHA256).Hash.ToLowerInvariant() -ne [string]$CompilerLock.sha256){ throw 'Windows C# compiler hash mismatch.' }
  $Signature=Get-AuthenticodeSignature -LiteralPath $Compiler
  if($Signature.Status -ne 'Valid' -or $Signature.SignerCertificate.Thumbprint -ne [string]$CompilerLock.signer_thumbprint){ throw 'Windows C# compiler Authenticode signer validation failed.' }
  return $Compiler
}

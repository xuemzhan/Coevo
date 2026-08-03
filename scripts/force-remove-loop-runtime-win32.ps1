<#
  Force-removes E:\Workspace\Coevo\loop\runtime using Win32 long-path APIs.
  Continues past locked/unreadable entries and reports failures.
#>
[CmdletBinding()]
param(
    [switch]$Yes
)

$ErrorActionPreference = 'Stop'
$Target = 'E:\Workspace\Coevo\loop\runtime'
$LongTarget = '\\?\' + $Target

if (-not $Yes) {
    $answer = Read-Host "Permanently delete $Target and everything below it? Type DELETE"
    if ($answer -cne 'DELETE') { Write-Host 'Cancelled.'; exit 2 }
}

if (-not [System.IO.Directory]::Exists($LongTarget)) {
    Write-Host "Nothing to delete: $Target"
    exit 0
}

Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.IO;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;

public static class CoevoLongDelete {
    const uint FILE_ATTRIBUTE_READONLY = 1;
    const uint FILE_ATTRIBUTE_REPARSE_POINT = 1024;
    const uint FILE_FLAG_BACKUP_SEMANTICS = 0x02000000;
    const uint FILE_LIST_DIRECTORY = 1;
    const uint FILE_SHARE_READ = 1;
    const uint FILE_SHARE_WRITE = 2;
    const uint FILE_SHARE_DELETE = 4;
    const uint OPEN_EXISTING = 3;
    const int ERROR_NO_MORE_FILES = 18;

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    struct WIN32_FIND_DATA {
        public uint attributes; public System.Runtime.InteropServices.ComTypes.FILETIME creation;
        public System.Runtime.InteropServices.ComTypes.FILETIME access; public System.Runtime.InteropServices.ComTypes.FILETIME write;
        public uint sizeHigh; public uint sizeLow; public uint reserved0; public uint reserved1;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst=260)] public string name;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst=14)] public string alternate;
    }

    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    static extern IntPtr FindFirstFile(string path, out WIN32_FIND_DATA data);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    static extern bool FindNextFile(IntPtr handle, out WIN32_FIND_DATA data);
    [DllImport("kernel32.dll", SetLastError=true)] static extern bool FindClose(IntPtr handle);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] static extern bool DeleteFile(string path);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] static extern bool RemoveDirectory(string path);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] static extern bool SetFileAttributes(string path, uint attrs);

    public static int DeleteTree(string root) {
        int failures = 0; DeleteDirectory(root, ref failures); return failures;
    }

    static void DeleteDirectory(string dir, ref int failures) {
        WIN32_FIND_DATA data; IntPtr h = FindFirstFile(dir + "\\*", out data);
        if (h != new IntPtr(-1)) {
            try {
                do {
                    string n = data.name;
                    if (n == "." || n == "..") continue;
                    string p = dir + "\\" + n;
                    bool reparse = (data.attributes & FILE_ATTRIBUTE_REPARSE_POINT) != 0;
                    try {
                        if (reparse) { SetFileAttributes(p, 0); if (!RemoveDirectory(p)) failures++; }
                        else if ((data.attributes & 0x10) != 0) DeleteDirectory(p, ref failures);
                        else { SetFileAttributes(p, 0); if (!DeleteFile(p)) failures++; }
                    } catch { failures++; }
                } while (FindNextFile(h, out data));
            } finally { FindClose(h); }
        }
        SetFileAttributes(dir, 0);
        if (!RemoveDirectory(dir)) failures++;
    }
}
'@

Write-Host "Deleting: $Target"
$failures = [CoevoLongDelete]::DeleteTree($LongTarget)
if ([System.IO.Directory]::Exists($LongTarget)) {
    throw "Deletion incomplete: target still exists ($failures failed entries): $Target"
}
Write-Host "Verified removed: $Target; failed entries: $failures"

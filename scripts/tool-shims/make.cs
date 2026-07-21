using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;

internal static class CoevoMake
{
    private const string RuntimeInventorySha256 = "829b9f4c69430fe1ed18573bedd828552eca242f8c5d128324ad2b1a844534c2";
    private const string ScriptInventorySha256 = "6f4e6d759b8269101172f09f260fab95f0992f252bd6c3cc6526a7df2c11b07a";
    private const string ControlArchiveSha256 = "7dd50b147a1c9bf336feb1493dfade9a854af19cf892df57391d2ef584dfce02";
    private const string AuditSignatureSha256 = "e87681df0c40d13df675c67794f6f9589bac74edf5ebb1f2996e9ec348212a60";

    private static readonly HashSet<string> Targets = new HashSet<string>(StringComparer.Ordinal)
    {
        "fmt", "lint", "test", "test-security", "test-e2e", "quality",
        "verify-loop-state", "env-check"
    };

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern IntPtr CreateFile(string name, uint access, uint share, IntPtr security,
        uint creation, uint flags, IntPtr template);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool CloseHandle(IntPtr handle);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern uint GetFinalPathNameByHandle(IntPtr handle, StringBuilder path, uint length, uint flags);

    private static string Hex(byte[] value)
    {
        var result = new StringBuilder(value.Length * 2);
        foreach (byte item in value) result.Append(item.ToString("x2", CultureInfo.InvariantCulture));
        return result.ToString();
    }

    private static string Hash(Stream stream)
    {
        stream.Position = 0;
        using (SHA256 algorithm = SHA256.Create()) return Hex(algorithm.ComputeHash(stream));
    }

    private static FileStream OpenLockedFile(string path, long size, string expectedHash)
    {
        var stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read, 1024 * 1024,
            FileOptions.SequentialScan);
        try
        {
            if (stream.Length != size || !String.Equals(Hash(stream), expectedHash, StringComparison.Ordinal))
                throw new InvalidDataException("locked file mismatch: " + path);
            stream.Position = 0;
        var finalPath = new StringBuilder(32768);
        uint finalLength = GetFinalPathNameByHandle(stream.SafeFileHandle.DangerousGetHandle(), finalPath,
            (uint)finalPath.Capacity, 0);
        if (finalLength == 0 || finalLength >= finalPath.Capacity)
        {
            stream.Dispose();
            throw new IOException("unable to resolve locked file: " + path);
        }
        string resolved = finalPath.ToString();
        if (resolved.StartsWith("\\\\?\\")) resolved = resolved.Substring(4);
        if (!String.Equals(Path.GetFullPath(path), Path.GetFullPath(resolved), StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("locked file resolves outside approved path: " + path);
            return stream;
        }
        catch
        {
            stream.Dispose();
            throw;
        }
    }

    private static IntPtr OpenLockedDirectory(string path)
    {
        var before = new DirectoryInfo(path);
        if (!before.Exists || (before.Attributes & FileAttributes.ReparsePoint) != 0)
            throw new InvalidDataException("unsafe locked directory: " + path);
        IntPtr handle = CreateFile(path, 0, 3, IntPtr.Zero, 3, 0x02000000, IntPtr.Zero);
        if (handle == new IntPtr(-1))
            throw new IOException("unable to lock directory: " + path, Marshal.GetLastWin32Error());
        var after = new DirectoryInfo(path);
        if ((after.Attributes & FileAttributes.ReparsePoint) != 0)
        {
            CloseHandle(handle);
            throw new InvalidDataException("unsafe locked directory: " + path);
        }
        return handle;
    }

    private static byte[] ReadBytes(FileStream stream)
    {
        stream.Position = 0;
        var bytes = new byte[checked((int)stream.Length)];
        int offset = 0;
        while (offset < bytes.Length)
        {
            int read = stream.Read(bytes, offset, bytes.Length - offset);
            if (read == 0) throw new EndOfStreamException();
            offset += read;
        }
        return bytes;
    }

    private static void LockDirectoryTree(string root, List<IntPtr> directories)
    {
        var pending = new Queue<string>();
        pending.Enqueue(root);
        while (pending.Count != 0)
        {
            string current = pending.Dequeue();
            directories.Add(OpenLockedDirectory(current));
            foreach (string directory in Directory.GetDirectories(current, "*", SearchOption.TopDirectoryOnly))
            {
                if ((new DirectoryInfo(directory).Attributes & FileAttributes.ReparsePoint) != 0)
                    throw new InvalidDataException("unsafe locked directory: " + directory);
                pending.Enqueue(directory);
            }
        }
    }

    private static void LockInventory(string inventoryPath, string inventoryHash, string basePath, bool enforceComplete,
        List<FileStream> files, List<IntPtr> directories)
    {
        var info = new FileInfo(inventoryPath);
        FileStream inventory = OpenLockedFile(inventoryPath, info.Length, inventoryHash);
        files.Add(inventory);
        string text = new UTF8Encoding(false, true).GetString(ReadBytes(inventory));
        string canonicalBase = Path.GetFullPath(basePath).TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar;
        var expected = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var roots = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (string raw in text.Split(new[] { '\n' }, StringSplitOptions.RemoveEmptyEntries))
        {
            string[] fields = raw.TrimEnd('\r').Split('\t');
            if (fields.Length != 3 || fields[0].Length != 64)
                throw new InvalidDataException("invalid lock inventory line");
            long size;
            if (!Int64.TryParse(fields[1], NumberStyles.None, CultureInfo.InvariantCulture, out size) || size < 0)
                throw new InvalidDataException("invalid locked file size");
            string relative = fields[2].Replace('/', Path.DirectorySeparatorChar);
            if (Path.IsPathRooted(relative) || relative.Split(Path.DirectorySeparatorChar).Length == 0)
                throw new InvalidDataException("unsafe inventory path");
            foreach (string part in relative.Split(Path.DirectorySeparatorChar))
                if (part == ".." || part.Length == 0) throw new InvalidDataException("unsafe inventory path");
            string path = Path.GetFullPath(Path.Combine(basePath, relative));
            if (!path.StartsWith(canonicalBase, StringComparison.OrdinalIgnoreCase))
                throw new InvalidDataException("inventory path escapes root");
            expected.Add(path);
            roots.Add(Path.GetDirectoryName(path));
            files.Add(OpenLockedFile(path, size, fields[0]));
        }
        var expandedRoots = new HashSet<string>(roots, StringComparer.OrdinalIgnoreCase);
        foreach (string root in new List<string>(roots))
        {
            string current = root;
            while (current.StartsWith(canonicalBase, StringComparison.OrdinalIgnoreCase))
            {
                expandedRoots.Add(current);
                current = Path.GetDirectoryName(current);
            }
        }
        foreach (string directory in expandedRoots) directories.Add(OpenLockedDirectory(directory));
        if (enforceComplete)
            foreach (string path in Directory.GetFiles(basePath, "*", SearchOption.AllDirectories))
                if (!expected.Contains(Path.GetFullPath(path))) throw new InvalidDataException("unlocked file in locked tree: " + path);
    }

    private static string Quote(string value)
    {
        return "\"" + value.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
    }

    private static int Main(string[] args)
    {
        if (args.Length == 1 && args[0] == "--version")
        {
            Console.WriteLine("Coevo Make compatibility shim 1.0 (restricted targets)");
            return 0;
        }
        if (args.Length != 1 || !Targets.Contains(args[0]))
        {
            Console.Error.WriteLine("usage: make {fmt|lint|test|test-security|test-e2e|quality|verify-loop-state|env-check}");
            return 64;
        }

        string root = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", ".."));
        string runtime = Path.Combine(root, ".tools", "python", "3.14.3");
        string python = Path.Combine(runtime, "python.exe");
        string runtimeInventory = Path.Combine(root, ".tools", "python", "3.14.3-files.lock");
        string scriptInventory = Path.Combine(root, "docs", "dependencies", "python-script-lock.tsv");
        string control = Path.Combine(root, ".tools", "control", "control.pyz");
        string auditSignature = Path.Combine(root, "scripts", "audit_signature.ps1");
        var files = new List<FileStream>();
        var directories = new List<IntPtr>();
        try
        {
            Console.Error.WriteLine("Coevo gate: locking verified toolchain (5421 runtime files)...");
            LockDirectoryTree(runtime, directories);
            LockInventory(runtimeInventory, RuntimeInventorySha256, runtime, false, files, directories);
            LockInventory(scriptInventory, ScriptInventorySha256, root, false, files, directories);
            files.Add(OpenLockedFile(control, 37387, ControlArchiveSha256));
            files.Add(OpenLockedFile(auditSignature, 5994, AuditSignatureSha256));

            string module;
            string extra;
            if (args[0] == "verify-loop-state")
            {
                module = "check_loop_stop"; extra = "";
            }
            else if (args[0] == "env-check")
            {
                module = "validate_opencode"; extra = " --require-tools";
            }
            else
            {
                module = "quality_gate"; extra = " --target " + args[0];
            }
            var start = new ProcessStartInfo
            {
                FileName = python,
                Arguments = "-I -E -S -s -B " + Quote(control) + " " + module + extra,
                WorkingDirectory = root,
                UseShellExecute = false
            };
            var inherited = new ArrayList(start.EnvironmentVariables.Keys);
            start.EnvironmentVariables["COEVO_CONTROL_ARCHIVE"] = control;
            start.EnvironmentVariables["COEVO_REPO_ROOT"] = root;
            foreach (string name in inherited)
                if (name.StartsWith("PYTHON", StringComparison.OrdinalIgnoreCase)) start.EnvironmentVariables.Remove(name);
            start.EnvironmentVariables["PYTHONNOUSERSITE"] = "1";
            start.EnvironmentVariables["PYTHONDONTWRITEBYTECODE"] = "1";
            string winPsDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), "System32", "WindowsPowerShell", "v1.0");
            string powershellPath = Path.Combine(winPsDir, "powershell.exe");
            start.EnvironmentVariables["COEVO_POWERSHELL_PATH"] = powershellPath;
            string inheritedPath = Environment.GetEnvironmentVariable("PATH") ?? "";
            if (inheritedPath.IndexOf(winPsDir, StringComparison.OrdinalIgnoreCase) < 0)
                inheritedPath = winPsDir + ";" + inheritedPath;
            string pathKey = null;
            foreach (string name in start.EnvironmentVariables.Keys)
                if (String.Equals(name, "PATH", StringComparison.OrdinalIgnoreCase))
                {
                    pathKey = name; break;
                }
            start.EnvironmentVariables[pathKey ?? "PATH"] = inheritedPath;
            Console.Error.WriteLine("Coevo gate: starting controlled Python validation...");
            var process = Process.Start(start);
            process.WaitForExit();
            return process.ExitCode;
        }
        catch (Exception error)
        {
            Console.Error.WriteLine("locked Python launch failed: " + error.Message);
            return 69;
        }
        finally
        {
            foreach (FileStream file in files) file.Dispose();
            foreach (IntPtr directory in directories) if (directory != IntPtr.Zero && directory != new IntPtr(-1)) CloseHandle(directory);
        }
    }
}

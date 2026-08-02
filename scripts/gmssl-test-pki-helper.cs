using System;
using System.Collections.Generic;
using System.IO;
using Microsoft.Win32.SafeHandles;
using System.Runtime.InteropServices;
using System.Security.AccessControl;
using System.Security.Cryptography;
using System.Security.Principal;
using System.Text;
using System.Threading;

internal static class GmsslTestPkiHelper
{
    private const int ExitInput = 20;
    private const int ExitIntegrity = 21;
    private const int ExitCrypto = 22;
    private const int ExitOutput = 23;
    private const byte ActionGenerate = 1;
    private const byte ActionRecover = 2;
    private const byte StatusCommitted = 1;
    private const byte StatusCleaned = 2;
    private const byte StatusNotFound = 3;
    private const uint DeleteAccess = 0x00010000;
    private const uint GenericRead = 0x80000000;
    private const uint FileReadAttributes = 0x00000080;
    private const uint FileShareRead = 0x00000001;
    private const uint FileShareWrite = 0x00000002;
    private const uint OpenExisting = 3;
    private const uint FileFlagBackupSemantics = 0x02000000;
    private const uint FileFlagOpenReparsePoint = 0x00200000;
    private const uint FileAttributeReparsePoint = 0x00000400;
    private const int FileRenameInfo = 3;
    private const int FileDispositionInfo = 4;
    private const int ErrorSharingViolation = 32;
    private const int DirectoryLockAttempts = 4;
    private const int DirectoryLockRetryDelayMilliseconds = 10;
    private const int FileTypePipe = 3;
    private const uint LoadLibrarySearchDllLoadDir = 0x00000100;
    private const uint LoadLibrarySearchSystem32 = 0x00000800;
    private const uint CryptProtectUiForbidden = 0x1;
    private const int OidSm2SignWithSm3 = 16;
    private const int X509VersionV3 = 2;
    private const int X509Critical = 1;
    private const int X509NonCritical = 0;
    private const int KeyUsageDigitalSignature = 1 << 0;
    private const int KeyUsageKeyEncipherment = 1 << 2;
    private const int KeyUsageKeyCertSign = 1 << 5;
    private const int KeyUsageCrlSign = 1 << 6;
    private const int NativeSm2KeyBytes = 512;
    // Locked GmSSL 3.2.0 Win64 ABI. Startup probes this boundary with a
    // trailing canary before any retained secret is generated.
    private const int NativeX509KeyBytes = 23760;
    private const int NameBytes = 1024;
    private const int ExtensionBytes = 4096;
    private const int MaxDerBytes = 65536;
    private const string DllSha256 = "9da9cc70507ce7a124b67cfc10c32a6c8c14f08caa6f50a19ecfa21c8f75deb0";
    // The version-2 helper frame includes an explicit UTF-8 preamble before
    // the ASCII protocol magic. The launcher writes those bytes directly.
    private static readonly byte[] RequestMagic = new byte[] { 0xef, 0xbb, 0xbf, 0x43, 0x4f, 0x45, 0x56, 0x4f, 0x50, 0x4b, 0x49 };
    private static readonly byte[] ResponseMagic = Encoding.ASCII.GetBytes("COEVORS2");
    private static readonly byte[] Entropy = Encoding.ASCII.GetBytes("Coevo.SM2.Test.PKI.DPAPI.v1");
    private static readonly string[] ArtifactNames = new string[] {
        "root-ca-cert.pem", "root-ca-cert.der", "sender-cert.pem", "sender-cert.der", "sender-key.pem", "sender-password.dpapi",
        "recipient-cert.pem", "recipient-cert.der", "recipient-key.pem", "recipient-password.dpapi", "recipient-companion-sign-cert.pem", "recipient-companion-sign-cert.der"
    };
    private static int injectedDirectoryLockAttempt;

    [StructLayout(LayoutKind.Sequential)]
    private struct DataBlob
    {
        internal int Length;
        internal IntPtr Data;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct ByHandleFileInformation
    {
        internal uint FileAttributes;
        internal System.Runtime.InteropServices.ComTypes.FILETIME CreationTime;
        internal System.Runtime.InteropServices.ComTypes.FILETIME LastAccessTime;
        internal System.Runtime.InteropServices.ComTypes.FILETIME LastWriteTime;
        internal uint VolumeSerialNumber;
        internal uint FileSizeHigh;
        internal uint FileSizeLow;
        internal uint NumberOfLinks;
        internal uint FileIndexHigh;
        internal uint FileIndexLow;
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern uint GetFileType(IntPtr handle);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern IntPtr GetStdHandle(int which);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetDefaultDllDirectories(uint flags);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern IntPtr LoadLibraryEx(string path, IntPtr file, uint flags);

    [DllImport("kernel32.dll", CharSet = CharSet.Ansi, SetLastError = true)]
    private static extern IntPtr GetProcAddress(IntPtr module, string name);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern uint GetModuleFileName(IntPtr module, StringBuilder path, int size);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetFileInformationByHandle(IntPtr file, out ByHandleFileInformation info);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern IntPtr CreateFile(string path, uint desiredAccess, uint shareMode, IntPtr securityAttributes, uint creationDisposition, uint flagsAndAttributes, IntPtr templateFile);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern uint GetFinalPathNameByHandle(IntPtr file, StringBuilder path, uint size, uint flags);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetFileInformationByHandle(IntPtr file, int informationClass, IntPtr information, uint size);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool CloseHandle(IntPtr handle);

    [DllImport("kernel32.dll")]
    private static extern void RtlZeroMemory(IntPtr destination, UIntPtr length);

    [DllImport("kernel32.dll")]
    private static extern IntPtr LocalFree(IntPtr value);

    [DllImport("crypt32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool CryptProtectData(
        ref DataBlob input, string description, ref DataBlob entropy, IntPtr reserved,
        IntPtr prompt, uint flags, out DataBlob output);

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int RandBytes(IntPtr output, UIntPtr length);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int Sm2KeyGenerate(IntPtr key);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int X509KeySetSm2Key(IntPtr x509Key, IntPtr sm2Key);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate void X509KeyCleanup(IntPtr x509Key);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int NameSet(IntPtr output, ref UIntPtr outputLength, UIntPtr maximumLength, [MarshalAs(UnmanagedType.LPStr)] string country, IntPtr state, IntPtr locality, [MarshalAs(UnmanagedType.LPStr)] string organization, [MarshalAs(UnmanagedType.LPStr)] string organizationalUnit, [MarshalAs(UnmanagedType.LPStr)] string commonName);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int AddSubjectKeyIdentifier(IntPtr extensions, ref UIntPtr extensionsLength, UIntPtr maximumLength, int critical, IntPtr subjectKey);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int AddAuthorityKeyIdentifier(IntPtr extensions, ref UIntPtr extensionsLength, UIntPtr maximumLength, IntPtr issuerKey);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int AddKeyUsage(IntPtr extensions, ref UIntPtr extensionsLength, UIntPtr maximumLength, int critical, int bits);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int AddBasicConstraints(IntPtr extensions, ref UIntPtr extensionsLength, UIntPtr maximumLength, int critical, int ca, int pathLength);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int CertSignToDer(int version, IntPtr serial, UIntPtr serialLength, int signatureAlgorithm, IntPtr issuer, UIntPtr issuerLength, long notBefore, long notAfter, IntPtr subject, UIntPtr subjectLength, IntPtr subjectPublicKey, IntPtr issuerUniqueId, UIntPtr issuerUniqueIdLength, IntPtr subjectUniqueId, UIntPtr subjectUniqueIdLength, IntPtr extensions, UIntPtr extensionsLength, IntPtr signKey, IntPtr signerId, UIntPtr signerIdLength, ref IntPtr output, ref UIntPtr outputLength);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int CertVerifyByCa(IntPtr cert, UIntPtr certLength, IntPtr caCert, UIntPtr caCertLength, IntPtr signerId, UIntPtr signerIdLength);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int EncryptPrivateKey(IntPtr key, IntPtr password, ref IntPtr output, ref UIntPtr outputLength);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int DecryptPrivateKey(IntPtr key, ref IntPtr attributes, ref UIntPtr attributesLength, IntPtr password, ref IntPtr input, ref UIntPtr inputLength);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int PublicKeyEqual(IntPtr left, IntPtr right);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate void SecureClear(IntPtr pointer, UIntPtr length);

    private sealed class NativeBuffer : IDisposable
    {
        internal readonly IntPtr Pointer;
        internal readonly int Length;
        private bool disposed;

        internal NativeBuffer(int length)
        {
            Length = length;
            Pointer = Marshal.AllocHGlobal(length);
            RtlZeroMemory(Pointer, (UIntPtr)(uint)length);
        }

        public void Dispose()
        {
            if (!disposed)
            {
                RtlZeroMemory(Pointer, (UIntPtr)(uint)Length);
                Marshal.FreeHGlobal(Pointer);
                disposed = true;
            }
        }
    }

    private sealed class NativeApi
    {
        internal readonly RandBytes Random;
        internal readonly Sm2KeyGenerate GenerateKey;
        internal readonly X509KeySetSm2Key SetSm2Key;
        internal readonly X509KeyCleanup CleanupX509Key;
        internal readonly NameSet SetName;
        internal readonly AddSubjectKeyIdentifier AddSubjectId;
        internal readonly AddAuthorityKeyIdentifier AddAuthorityId;
        internal readonly AddKeyUsage AddUsage;
        internal readonly AddBasicConstraints AddConstraints;
        internal readonly CertSignToDer SignCertificate;
        internal readonly CertVerifyByCa VerifyCertificate;
        internal readonly EncryptPrivateKey EncryptKey;
        internal readonly DecryptPrivateKey DecryptKey;
        internal readonly PublicKeyEqual PublicKeysEqual;
        internal readonly SecureClear Clear;

        internal NativeApi(IntPtr module)
        {
            Random = Bind<RandBytes>(module, "rand_bytes");
            GenerateKey = Bind<Sm2KeyGenerate>(module, "sm2_key_generate");
            SetSm2Key = Bind<X509KeySetSm2Key>(module, "x509_key_set_sm2_key");
            CleanupX509Key = Bind<X509KeyCleanup>(module, "x509_key_cleanup");
            SetName = Bind<NameSet>(module, "x509_name_set");
            AddSubjectId = Bind<AddSubjectKeyIdentifier>(module, "x509_exts_add_subject_key_identifier_ex");
            AddAuthorityId = Bind<AddAuthorityKeyIdentifier>(module, "x509_exts_add_default_authority_key_identifier");
            AddUsage = Bind<AddKeyUsage>(module, "x509_exts_add_key_usage");
            AddConstraints = Bind<AddBasicConstraints>(module, "x509_exts_add_basic_constraints");
            SignCertificate = Bind<CertSignToDer>(module, "x509_cert_sign_to_der");
            VerifyCertificate = Bind<CertVerifyByCa>(module, "x509_cert_verify_by_ca_cert");
            EncryptKey = Bind<EncryptPrivateKey>(module, "sm2_private_key_info_encrypt_to_der");
            DecryptKey = Bind<DecryptPrivateKey>(module, "sm2_private_key_info_decrypt_from_der");
            PublicKeysEqual = Bind<PublicKeyEqual>(module, "sm2_public_key_equ");
            Clear = Bind<SecureClear>(module, "gmssl_secure_clear");
            ValidateAbi(this);
        }

        private static T Bind<T>(IntPtr module, string name) where T : class
        {
            IntPtr address = GetProcAddress(module, name);
            if (address == IntPtr.Zero) throw new InvalidOperationException("GMH-E-EXPORT");
            return (T)(object)Marshal.GetDelegateForFunctionPointer(address, typeof(T));
        }

        private static void ValidateAbi(NativeApi api)
        {
            const int CanaryBytes = 4096;
            using (NativeBuffer sm2 = new NativeBuffer(NativeSm2KeyBytes))
            using (NativeBuffer x509 = new NativeBuffer(NativeX509KeyBytes + CanaryBytes))
            {
                for (int i = 0; i < x509.Length; i++) Marshal.WriteByte(x509.Pointer, i, 0xa5);
                if (api.GenerateKey(sm2.Pointer) != 1 || api.SetSm2Key(x509.Pointer, sm2.Pointer) != 1) throw new InvalidOperationException("GMH-E-ABI");
                if (Marshal.ReadByte(x509.Pointer, NativeX509KeyBytes - 1) == 0xa5) throw new InvalidOperationException("GMH-E-ABI");
                for (int i = NativeX509KeyBytes; i < x509.Length; i++) if (Marshal.ReadByte(x509.Pointer, i) != 0xa5) throw new InvalidOperationException("GMH-E-ABI");
                api.CleanupX509Key(x509.Pointer);
                api.Clear(sm2.Pointer, (UIntPtr)(uint)sm2.Length);
            }
        }
    }

    private sealed class KeyMaterial : IDisposable
    {
        internal readonly NativeBuffer Sm2 = new NativeBuffer(NativeSm2KeyBytes);
        internal readonly NativeBuffer X509 = new NativeBuffer(NativeX509KeyBytes);
        internal byte[] EncryptedDer;
        internal byte[] SealedPassword;
        private readonly NativeApi api;

        internal KeyMaterial(NativeApi api)
        {
            this.api = api;
        }

        public void Dispose()
        {
            api.Clear(Sm2.Pointer, (UIntPtr)(uint)Sm2.Length);
            api.CleanupX509Key(X509.Pointer);
            api.Clear(X509.Pointer, (UIntPtr)(uint)X509.Length);
            Sm2.Dispose();
            X509.Dispose();
        }
    }

    private sealed class Request
    {
        internal byte Action;
        internal string Profile;
        internal byte[] Nonce;
    }

    private sealed class DirectoryLock : IDisposable
    {
        internal readonly IntPtr Handle;
        internal readonly string Path;
        internal readonly string Role;
        internal readonly ByHandleFileInformation Identity;
        private bool disposed;

        private DirectoryLock(IntPtr handle, string path, string role, ByHandleFileInformation identity)
        {
            Handle = handle;
            Path = path;
            Role = role;
            Identity = identity;
        }

        internal static DirectoryLock Open(string path, string role)
        {
            if (!IsDirectoryRole(role)) throw new InvalidOperationException("GMH-E-DIRECTORY-ROLE");
            string full = System.IO.Path.GetFullPath(path);
            IntPtr handle = new IntPtr(-1);
            for (int attempt = 1; attempt <= DirectoryLockAttempts; attempt++)
            {
                DirectoryInfo before = new DirectoryInfo(full);
                if (!before.Exists || (before.Attributes & FileAttributes.ReparsePoint) != 0) throw new InvalidOperationException("GMH-E-DIRECTORY-" + role);
                AssertCurrentOwnerOnlyAcl(full);
                int injected = NextInjectedDirectoryLockError(role);
                int error;
                if (injected != 0) error = injected;
                else
                {
                    handle = CreateFile(full, DeleteAccess | FileReadAttributes, FileShareRead | FileShareWrite, IntPtr.Zero, OpenExisting, FileFlagBackupSemantics | FileFlagOpenReparsePoint, IntPtr.Zero);
                    if (handle != new IntPtr(-1)) break;
                    error = Marshal.GetLastWin32Error();
                }
                if (error != ErrorSharingViolation || attempt == DirectoryLockAttempts)
                    throw new InvalidOperationException("GMH-E-DIRECTORY-LOCK-" + role + "-WIN32-" + error.ToString() + "-ATTEMPT-" + attempt.ToString());
                Thread.Sleep(DirectoryLockRetryDelayMilliseconds);
            }
            if (handle == new IntPtr(-1)) throw new InvalidOperationException("GMH-E-DIRECTORY-LOCK-" + role + "-INTERNAL");
            try
            {
                ByHandleFileInformation identity;
                if (!GetFileInformationByHandle(handle, out identity) || (identity.FileAttributes & FileAttributeReparsePoint) != 0) throw new InvalidOperationException("GMH-E-DIRECTORY-IDENTITY-INFO-" + role);
                string final = FinalPath(handle, "GMH-E-DIRECTORY-FINALPATH-" + role);
                if (!String.Equals(NormalizePath(final), NormalizePath(full), StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("GMH-E-DIRECTORY-IDENTITY-PATH-" + role);
                DirectoryInfo after = new DirectoryInfo(full);
                if (!after.Exists || (after.Attributes & FileAttributes.ReparsePoint) != 0) throw new InvalidOperationException("GMH-E-DIRECTORY-IDENTITY-AFTER-" + role);
                AssertCurrentOwnerOnlyAcl(full);
                return new DirectoryLock(handle, full, role, identity);
            }
            catch { CloseHandle(handle); throw; }
        }

        private static bool IsDirectoryRole(string role)
        {
            return role == "GENERATE-PKI-ROOT" || role == "GENERATE-STAGING" || role == "RECOVER-PKI-ROOT" || role == "RECOVER-STAGING" || role == "INSPECT-PROFILE";
        }

        private static int NextInjectedDirectoryLockError(string role)
        {
            if (!String.Equals(Environment.GetEnvironmentVariable("COEVO_TEST_ONLY_DIRECTORY_LOCK_INJECTION"), "1", StringComparison.Ordinal) ||
                !String.Equals(Environment.GetEnvironmentVariable("COEVO_TEST_DIRECTORY_LOCK_ROLE"), role, StringComparison.Ordinal)) return 0;
            string sequence = Environment.GetEnvironmentVariable("COEVO_TEST_DIRECTORY_LOCK_ERRORS");
            if (String.IsNullOrEmpty(sequence)) return 0;
            string[] values = sequence.Split(',');
            int index = Interlocked.Increment(ref injectedDirectoryLockAttempt) - 1;
            if (index < 0 || index >= values.Length) return 0;
            int error;
            if (!Int32.TryParse(values[index], out error) || error < 0 || error > 65535) throw new InvalidOperationException("GMH-E-TEST-INJECTION");
            return error;
        }

        internal void Verify()
        {
            ByHandleFileInformation current;
            if (!GetFileInformationByHandle(Handle, out current)) throw new InvalidOperationException("GMH-E-DIRECTORY-VERIFY-INFO-" + Role + "-WIN32-" + Marshal.GetLastWin32Error().ToString());
            if (!SameDirectory(Identity, current) || (current.FileAttributes & FileAttributeReparsePoint) != 0) throw new InvalidOperationException("GMH-E-DIRECTORY-VERIFY-IDENTITY-" + Role);
            if (!String.Equals(NormalizePath(FinalPath(Handle, "GMH-E-DIRECTORY-FINALPATH-" + Role)), NormalizePath(Path), StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("GMH-E-DIRECTORY-VERIFY-PATH-" + Role);
            AssertCurrentOwnerOnlyAcl(Path);
        }

        public void Dispose()
        {
            if (!disposed) { CloseHandle(Handle); disposed = true; }
        }
    }

    private static int Main(string[] args)
    {
        try
        {
            if (args.Length != 0) return Fail(ExitInput, "GMH-E-ARGS");
            if (GetFileType(GetStdHandle(-10)) != FileTypePipe) return Fail(ExitInput, "GMH-E-STDIN");
            Request request = ReadRequest(Console.OpenStandardInput());
            if (String.Equals(Environment.GetEnvironmentVariable("COEVO_TEST_ONLY_HELPER_HANG"), "1", StringComparison.Ordinal)) Thread.Sleep(Timeout.Infinite);
            string root = Path.GetFullPath(Environment.CurrentDirectory);
            if (!File.Exists(Path.Combine(root, "docs", "dependencies", "toolchain-lock.json"))) return Fail(ExitIntegrity, "GMH-E-ROOT");
            byte status;
            byte[] receiptHash;
            if (request.Action == ActionRecover)
            {
                status = Recover(root, request.Profile, request.Nonce, out receiptHash);
            }
            else
            {
                string dllPath = Path.Combine(root, ".tools", "gmssl", "3.2.0", "GmSSL-3.2.0-win64", "bin", "gmssl.dll");
                NativeApi api = LoadApi(dllPath);
                status = GenerateAndPublish(api, root, request, out receiptHash);
            }
            if (!String.Equals(Environment.GetEnvironmentVariable("COEVO_TEST_DROP_RESPONSE"), "1", StringComparison.Ordinal)) WriteResponse(Console.OpenStandardOutput(), request.Action, status, request.Nonce, receiptHash);
            Clear(receiptHash);
            Clear(request.Nonce);
            return 0;
        }
        catch (InvalidDataException ex) { return Fail(ExitInput, ex.Message.StartsWith("GMH-E-", StringComparison.Ordinal) ? ex.Message : "GMH-E-INPUT"); }
        catch (UnauthorizedAccessException) { return Fail(ExitIntegrity, "GMH-E-INTEGRITY"); }
        catch (CryptographicException) { return Fail(ExitCrypto, "GMH-E-CRYPTO"); }
        catch (InvalidOperationException ex)
        {
            string code = ex.Message.StartsWith("GMH-E-", StringComparison.Ordinal) ? ex.Message : "GMH-E-CRYPTO";
            return Fail(code == "GMH-E-INTEGRITY" ? ExitIntegrity : ExitCrypto, code);
        }
        catch { return Fail(ExitCrypto, "GMH-E-UNEXPECTED"); }
    }

    private static int Fail(int code, string stableCode)
    {
        try { Console.Error.WriteLine(stableCode); } catch { }
        return code;
    }

    private static Request ReadRequest(Stream input)
    {
        byte[] fixedPart = ReadExact(input, RequestMagic.Length + 2);
        for (int i = 0; i < RequestMagic.Length; i++) if (fixedPart[i] != RequestMagic[i]) throw new InvalidDataException("GMH-E-MAGIC");
        if (fixedPart[RequestMagic.Length] != 2) throw new InvalidDataException("GMH-E-VERSION");
        byte action = fixedPart[RequestMagic.Length + 1];
        if (action != ActionGenerate && action != ActionRecover) throw new InvalidDataException("GMH-E-ACTION");
        int profileLength = input.ReadByte();
        if (profileLength < 1 || profileLength > 32) throw new InvalidDataException("GMH-E-PROFILE-LENGTH");
        byte[] profileBytes = ReadExact(input, profileLength);
        byte[] nonce = ReadExact(input, 16);
        if (input.ReadByte() != -1) throw new InvalidDataException("GMH-E-TRAILING");
        string profile = Encoding.ASCII.GetString(profileBytes);
        if (!IsSafeProfile(profile)) throw new InvalidDataException("GMH-E-PROFILE");
        Array.Clear(profileBytes, 0, profileBytes.Length);
        Array.Clear(fixedPart, 0, fixedPart.Length);
        return new Request { Action = action, Profile = profile, Nonce = nonce };
    }

    private static bool IsSafeProfile(string value)
    {
        if (value.Length < 1 || value.Length > 32 || !((value[0] >= 'a' && value[0] <= 'z') || (value[0] >= '0' && value[0] <= '9'))) return false;
        for (int i = 0; i < value.Length; i++)
        {
            char c = value[i];
            if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || (c == '-' && i > 0))) return false;
        }
        return true;
    }

    private static byte[] ReadExact(Stream input, int count)
    {
        byte[] data = new byte[count];
        int offset = 0;
        while (offset < count)
        {
            int read = input.Read(data, offset, count - offset);
            if (read <= 0) throw new InvalidDataException("GMH-E-TRUNCATED");
            offset += read;
        }
        return data;
    }

    private static NativeApi LoadApi(string dllPath)
    {
        FileInfo file = new FileInfo(dllPath);
        if (!file.Exists || (file.Attributes & FileAttributes.ReparsePoint) != 0 || file.Length != 1665024) throw new InvalidOperationException("GMH-E-INTEGRITY");
        DirectoryInfo cursor = file.Directory;
        while (cursor != null)
        {
            if ((cursor.Attributes & FileAttributes.ReparsePoint) != 0) throw new InvalidOperationException("GMH-E-INTEGRITY");
            cursor = cursor.Parent;
        }
        using (FileStream pinned = new FileStream(dllPath, FileMode.Open, FileAccess.Read, FileShare.Read))
        {
            ByHandleFileInformation before;
            if (!GetFileInformationByHandle(pinned.SafeFileHandle.DangerousGetHandle(), out before) || before.NumberOfLinks != 1) throw new InvalidOperationException("GMH-E-INTEGRITY");
            string digest;
            using (SHA256 hash = SHA256.Create()) digest = ToHex(hash.ComputeHash(pinned));
            if (!String.Equals(digest, DllSha256, StringComparison.Ordinal)) throw new InvalidOperationException("GMH-E-INTEGRITY");
            if (!SetDefaultDllDirectories(LoadLibrarySearchSystem32)) throw new InvalidOperationException("GMH-E-INTEGRITY");
            IntPtr module = LoadLibraryEx(dllPath, IntPtr.Zero, LoadLibrarySearchDllLoadDir | LoadLibrarySearchSystem32);
            if (module == IntPtr.Zero) throw new InvalidOperationException("GMH-E-INTEGRITY");
            StringBuilder loaded = new StringBuilder(32768);
            if (GetModuleFileName(module, loaded, loaded.Capacity) == 0 || !String.Equals(Path.GetFullPath(dllPath), Path.GetFullPath(loaded.ToString()), StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("GMH-E-INTEGRITY");
            ByHandleFileInformation after;
            if (!GetFileInformationByHandle(pinned.SafeFileHandle.DangerousGetHandle(), out after) || !SameFile(before, after)) throw new InvalidOperationException("GMH-E-INTEGRITY");
            return new NativeApi(module);
        }
    }

    private static bool SameFile(ByHandleFileInformation a, ByHandleFileInformation b)
    {
        return a.VolumeSerialNumber == b.VolumeSerialNumber && a.FileIndexHigh == b.FileIndexHigh && a.FileIndexLow == b.FileIndexLow && a.FileSizeHigh == b.FileSizeHigh && a.FileSizeLow == b.FileSizeLow;
    }

    private static bool SameDirectory(ByHandleFileInformation a, ByHandleFileInformation b)
    {
        return a.VolumeSerialNumber == b.VolumeSerialNumber && a.FileIndexHigh == b.FileIndexHigh && a.FileIndexLow == b.FileIndexLow;
    }

    private static string FinalPath(IntPtr handle)
    {
        return FinalPath(handle, "GMH-E-FINALPATH");
    }

    private static string FinalPath(IntPtr handle, string stableCode)
    {
        StringBuilder value = new StringBuilder(32768);
        uint length = GetFinalPathNameByHandle(handle, value, (uint)value.Capacity, 0);
        if (length == 0 || length >= value.Capacity) throw new InvalidOperationException(stableCode + "-WIN32-" + Marshal.GetLastWin32Error().ToString());
        return value.ToString();
    }

    private static string NormalizePath(string path)
    {
        string value = path;
        if (value.StartsWith("\\\\?\\UNC\\", StringComparison.OrdinalIgnoreCase)) value = "\\\\" + value.Substring(8);
        else if (value.StartsWith("\\\\?\\", StringComparison.OrdinalIgnoreCase)) value = value.Substring(4);
        return System.IO.Path.GetFullPath(value).TrimEnd(System.IO.Path.DirectorySeparatorChar);
    }

    private static string ToHex(byte[] bytes)
    {
        StringBuilder result = new StringBuilder(bytes.Length * 2);
        for (int i = 0; i < bytes.Length; i++) result.Append(bytes[i].ToString("x2"));
        Array.Clear(bytes, 0, bytes.Length);
        return result.ToString();
    }

    private static byte GenerateAndPublish(NativeApi api, string repositoryRoot, Request request, out byte[] receiptHash)
    {
        receiptHash = new byte[32];
        string runtimeRoot = PrepareRuntimeRoot(repositoryRoot);
        using (DirectoryLock rootLock = DirectoryLock.Open(runtimeRoot, "GENERATE-PKI-ROOT"))
        {
            byte existing = InspectCommitted(runtimeRoot, request.Profile, request.Nonce, out receiptHash);
            if (existing == StatusCommitted) return StatusCommitted;
            if (existing != StatusNotFound) throw new InvalidOperationException("GMH-E-CONFLICT");
            string staging = Path.Combine(runtimeRoot, ".staging-" + Hex(request.Nonce));
            if (Directory.Exists(staging) || File.Exists(staging)) throw new InvalidOperationException("GMH-E-STAGING-CONFLICT");
            CreateOwnerOnlyDirectory(staging);
            using (DirectoryLock stagingLock = DirectoryLock.Open(staging, "GENERATE-STAGING"))
            {
                CrashAt("after-staging");
                try
                {
                    receiptHash = GenerateFiles(api, staging, request);
                    rootLock.Verify();
                    stagingLock.Verify();
                    RenameDirectory(stagingLock, Path.Combine(runtimeRoot, request.Profile));
                    CrashAt("after-rename");
                    return StatusCommitted;
                }
                catch
                {
                    TryCleanupKnownStaging(stagingLock);
                    throw;
                }
            }
        }
    }

    private static byte[] GenerateFiles(NativeApi api, string staging, Request request)
    {
        KeyMaterial root = new KeyMaterial(api);
        KeyMaterial sender = new KeyMaterial(api);
        KeyMaterial recipient = new KeyMaterial(api);
        KeyMaterial companion = new KeyMaterial(api);
        byte[] rootCert = null;
        byte[] senderCert = null;
        byte[] recipientCert = null;
        byte[] companionCert = null;
        try
        {
            GenerateKey(api, root, false);
            GenerateKey(api, sender, true);
            GenerateKey(api, recipient, true);
            GenerateKey(api, companion, false);
            rootCert = CreateCertificate(api, root, root, "Isolated SM2 PKI", "Coevo Test SM2 Root CA", "Isolated SM2 PKI", "Coevo Test SM2 Root CA", KeyUsageKeyCertSign | KeyUsageCrlSign, true, null);
            senderCert = CreateCertificate(api, sender, root, "Package Sender", "Coevo Test Sender", "Isolated SM2 PKI", "Coevo Test SM2 Root CA", KeyUsageDigitalSignature, false, rootCert);
            companionCert = CreateCertificate(api, companion, root, "Package Recipient", "Coevo Test Recipient", "Isolated SM2 PKI", "Coevo Test SM2 Root CA", KeyUsageDigitalSignature, false, rootCert);
            recipientCert = CreateCertificate(api, recipient, root, "Package Recipient", "Coevo Test Recipient", "Isolated SM2 PKI", "Coevo Test SM2 Root CA", KeyUsageKeyEncipherment, false, rootCert);
            Dictionary<string, byte[]> files = new Dictionary<string, byte[]>(StringComparer.OrdinalIgnoreCase);
            files.Add("root-ca-cert.der", rootCert);
            files.Add("root-ca-cert.pem", Pem("CERTIFICATE", rootCert));
            files.Add("sender-cert.der", senderCert);
            files.Add("sender-cert.pem", Pem("CERTIFICATE", senderCert));
            files.Add("recipient-cert.der", recipientCert);
            files.Add("recipient-cert.pem", Pem("CERTIFICATE", recipientCert));
            files.Add("recipient-companion-sign-cert.der", companionCert);
            files.Add("recipient-companion-sign-cert.pem", Pem("CERTIFICATE", companionCert));
            files.Add("sender-key.pem", Pem("ENCRYPTED PRIVATE KEY", sender.EncryptedDer));
            files.Add("sender-password.dpapi", sender.SealedPassword);
            files.Add("recipient-key.pem", Pem("ENCRYPTED PRIVATE KEY", recipient.EncryptedDer));
            files.Add("recipient-password.dpapi", recipient.SealedPassword);
            foreach (KeyValuePair<string, byte[]> item in files) WriteNewFlushed(Path.Combine(staging, item.Key), item.Value);
            CrashAt("after-files");
            string receipt = BuildReceipt(request, files);
            byte[] receiptBytes = new UTF8Encoding(false).GetBytes(receipt);
            try
            {
                CrashAt("before-receipt");
                WriteNewFlushed(Path.Combine(staging, "receipt.json"), receiptBytes);
                CrashAt("after-receipt");
                using (SHA256 sha = SHA256.Create()) return sha.ComputeHash(receiptBytes);
            }
            finally { Clear(receiptBytes); foreach (KeyValuePair<string, byte[]> item in files) if (!Object.ReferenceEquals(item.Value, rootCert) && !Object.ReferenceEquals(item.Value, senderCert) && !Object.ReferenceEquals(item.Value, recipientCert) && !Object.ReferenceEquals(item.Value, companionCert) && !Object.ReferenceEquals(item.Value, sender.EncryptedDer) && !Object.ReferenceEquals(item.Value, sender.SealedPassword) && !Object.ReferenceEquals(item.Value, recipient.EncryptedDer) && !Object.ReferenceEquals(item.Value, recipient.SealedPassword)) Clear(item.Value); }
        }
        finally
        {
            root.Dispose(); sender.Dispose(); recipient.Dispose(); companion.Dispose();
            Clear(rootCert); Clear(senderCert); Clear(recipientCert); Clear(companionCert);
            Clear(sender.EncryptedDer); Clear(sender.SealedPassword); Clear(recipient.EncryptedDer); Clear(recipient.SealedPassword);
        }
    }

    private static string BuildReceipt(Request request, Dictionary<string, byte[]> files)
    {
        Dictionary<string, string> hashes = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        for (int i = 0; i < ArtifactNames.Length; i++) hashes.Add(ArtifactNames[i], Hash(files[ArtifactNames[i]]));
        return BuildReceiptFromHashes(request.Nonce, hashes);
    }

    private static string BuildReceiptFromHashes(byte[] nonce, Dictionary<string, string> hashes)
    {
        StringBuilder manifest = new StringBuilder();
        manifest.Append("  \"artifacts\": {\n");
        for (int i = 0; i < ArtifactNames.Length; i++)
        {
            string name = ArtifactNames[i];
            manifest.Append("    \"").Append(name).Append("\": \"").Append(hashes[name]).Append(i + 1 == ArtifactNames.Length ? "\"\n" : "\",\n");
        }
        manifest.Append("  },\n");
        return "{\n" +
            "  \"schema_version\": \"2.0\",\n" +
            "  \"scope\": \"test-only-isolated-sm2-pki\",\n" +
            "  \"production_approved\": false,\n" +
            "  \"gmssl_version\": \"3.2.0\",\n" +
            "  \"gmssl_library_sha256\": \"" + DllSha256 + "\",\n" +
            "  \"helper_protocol\": \"COEVOPKI/2\",\n" +
            "  \"request_nonce\": \"" + Hex(nonce) + "\",\n" + manifest.ToString() +
            "  \"root_ca_certificate_sha256\": \"" + hashes["root-ca-cert.pem"] + "\",\n" +
            "  \"root_ca_certificate_der_sha256\": \"" + hashes["root-ca-cert.der"] + "\",\n" +
            "  \"root_ca_private_material_destroyed\": true,\n" +
            "  \"sender_certificate_sha256\": \"" + hashes["sender-cert.pem"] + "\",\n" +
            "  \"sender_certificate_der_sha256\": \"" + hashes["sender-cert.der"] + "\",\n" +
            "  \"sender_key_usage\": [\"digitalSignature\"],\n" +
            "  \"sender_private_key_format\": \"password-encrypted-pkcs8\",\n" +
            "  \"sender_password_protection\": \"CurrentUser-DPAPI\",\n" +
            "  \"recipient_certificate_sha256\": \"" + hashes["recipient-cert.pem"] + "\",\n" +
            "  \"recipient_certificate_der_sha256\": \"" + hashes["recipient-cert.der"] + "\",\n" +
            "  \"recipient_key_usage\": [\"keyEncipherment\"],\n" +
            "  \"recipient_private_key_format\": \"password-encrypted-pkcs8\",\n" +
            "  \"recipient_password_protection\": \"CurrentUser-DPAPI\",\n" +
            "  \"recipient_chain_validation\": \"GmSSL DLL direct verification with same-identity companion signing certificate\",\n" +
            "  \"recipient_companion_certificate_der_sha256\": \"" + hashes["recipient-companion-sign-cert.der"] + "\",\n" +
            "  \"recipient_companion_private_material_destroyed\": true,\n" +
            "  \"signature_algorithm\": \"SM2-SM3\"\n" +
            "}\n";
    }

    private static string PrepareRuntimeRoot(string repositoryRoot)
    {
        string loop = Path.Combine(repositoryRoot, "loop");
        if (!Directory.Exists(loop) || (new DirectoryInfo(loop).Attributes & FileAttributes.ReparsePoint) != 0) throw new InvalidOperationException("GMH-E-ROOT");
        string runtime = Path.Combine(loop, "runtime");
        EnsureOwnerOnlyDirectory(runtime);
        string pki = Path.Combine(runtime, "sm2-test-pki");
        EnsureOwnerOnlyDirectory(pki);
        return pki;
    }

    private static void EnsureOwnerOnlyDirectory(string path)
    {
        if (File.Exists(path)) throw new InvalidOperationException("GMH-E-ACL");
        if (!Directory.Exists(path)) CreateOwnerOnlyDirectory(path);
        DirectoryInfo directory = new DirectoryInfo(path);
        if ((directory.Attributes & FileAttributes.ReparsePoint) != 0) throw new InvalidOperationException("GMH-E-ACL");
        DirectorySecurity desired = OwnerOnlyAcl();
        directory.SetAccessControl(desired);
        AssertCurrentOwnerOnlyAcl(path);
    }

    private static void AssertCurrentOwnerOnlyAcl(string path)
    {
        DirectorySecurity actual;
        try { actual = new DirectoryInfo(path).GetAccessControl(AccessControlSections.Owner | AccessControlSections.Access); }
        catch (Exception ex) { if (ex is UnauthorizedAccessException || ex is IOException) throw new InvalidOperationException("GMH-E-ACL"); throw; }
        SecurityIdentifier current = WindowsIdentity.GetCurrent().User;
        if (!current.Equals(actual.GetOwner(typeof(SecurityIdentifier))) || !actual.AreAccessRulesProtected) throw new InvalidOperationException("GMH-E-ACL");
        AuthorizationRuleCollection rules = actual.GetAccessRules(true, false, typeof(SecurityIdentifier));
        if (rules.Count != 1) throw new InvalidOperationException("GMH-E-ACL");
        FileSystemAccessRule rule = rules[0] as FileSystemAccessRule;
        InheritanceFlags requiredInheritance = InheritanceFlags.ContainerInherit | InheritanceFlags.ObjectInherit;
        if (rule == null || !current.Equals(rule.IdentityReference) || rule.AccessControlType != AccessControlType.Allow ||
            (rule.FileSystemRights & FileSystemRights.FullControl) != FileSystemRights.FullControl || rule.InheritanceFlags != requiredInheritance ||
            rule.PropagationFlags != PropagationFlags.None) throw new InvalidOperationException("GMH-E-ACL");
    }

    private static void CreateOwnerOnlyDirectory(string path)
    {
        Directory.CreateDirectory(path, OwnerOnlyAcl());
        EnsureOwnerOnlyDirectory(path);
    }

    private static DirectorySecurity OwnerOnlyAcl()
    {
        SecurityIdentifier owner = WindowsIdentity.GetCurrent().User;
        DirectorySecurity security = new DirectorySecurity();
        security.SetOwner(owner);
        security.SetAccessRuleProtection(true, false);
        security.AddAccessRule(new FileSystemAccessRule(owner, FileSystemRights.FullControl, InheritanceFlags.ContainerInherit | InheritanceFlags.ObjectInherit, PropagationFlags.None, AccessControlType.Allow));
        return security;
    }

    private static byte Recover(string repositoryRoot, string profile, byte[] nonce, out byte[] receiptHash)
    {
        receiptHash = new byte[32];
        string runtimeRoot = PrepareRuntimeRoot(repositoryRoot);
        using (DirectoryLock rootLock = DirectoryLock.Open(runtimeRoot, "RECOVER-PKI-ROOT"))
        {
            byte committed = InspectCommitted(runtimeRoot, profile, nonce, out receiptHash);
            if (committed == StatusCommitted) return StatusCommitted;
            if (committed != StatusNotFound) throw new InvalidOperationException("GMH-E-CONFLICT");
            string staging = Path.Combine(runtimeRoot, ".staging-" + Hex(nonce));
            if (!Directory.Exists(staging))
            {
                if (File.Exists(staging)) throw new InvalidOperationException("GMH-E-RECOVER-UNKNOWN");
                return StatusNotFound;
            }
            using (DirectoryLock stagingLock = DirectoryLock.Open(staging, "RECOVER-STAGING"))
            {
                rootLock.Verify();
                TryCleanupKnownStaging(stagingLock);
                return StatusCleaned;
            }
        }
    }

    private static byte InspectCommitted(string runtimeRoot, string profile, byte[] nonce, out byte[] receiptHash)
    {
        receiptHash = new byte[32];
        string target = Path.Combine(runtimeRoot, profile);
        if (!Directory.Exists(target))
        {
            if (File.Exists(target)) return 0;
            return StatusNotFound;
        }
        using (DirectoryLock targetLock = DirectoryLock.Open(target, "INSPECT-PROFILE"))
        {
            targetLock.Verify();
            if (!HasExactCommittedManifest(target)) return 0;
            SafeFileHandle receiptHandle = null;
            Dictionary<string, SafeFileHandle> artifactHandles = new Dictionary<string, SafeFileHandle>(StringComparer.Ordinal);
            try
            {
                int receiptLength;
                receiptHandle = OpenValidatedRegularFile(Path.Combine(target, "receipt.json"), 16384, out receiptLength);
                for (int i = 0; i < ArtifactNames.Length; i++)
                {
                    int ignored;
                    artifactHandles.Add(ArtifactNames[i], OpenValidatedRegularFile(Path.Combine(target, ArtifactNames[i]), 131072, out ignored));
                }
                if (!HasExactCommittedManifest(target)) return 0;
                targetLock.Verify();
                byte[] bytes = ReadHandle(receiptHandle, receiptLength);
                try
                {
                    Dictionary<string, string> hashes = new Dictionary<string, string>(StringComparer.Ordinal);
                    for (int i = 0; i < ArtifactNames.Length; i++) hashes.Add(ArtifactNames[i], HashHandle(artifactHandles[ArtifactNames[i]]));
                    byte[] expected = new UTF8Encoding(false).GetBytes(BuildReceiptFromHashes(nonce, hashes));
                    try
                    {
                        if (!BytesEqual(bytes, expected)) return 0;
                        using (SHA256 sha = SHA256.Create()) receiptHash = sha.ComputeHash(bytes);
                        return StatusCommitted;
                    }
                    finally { Clear(expected); }
                }
                finally { Clear(bytes); }
            }
            catch (IOException) { return 0; }
            catch (UnauthorizedAccessException) { return 0; }
            catch (InvalidOperationException) { return 0; }
            finally
            {
                if (receiptHandle != null) receiptHandle.Dispose();
                foreach (KeyValuePair<string, SafeFileHandle> item in artifactHandles) item.Value.Dispose();
            }
        }
    }

    private static bool HasExactCommittedManifest(string target)
    {
        Dictionary<string, bool> expected = new Dictionary<string, bool>(StringComparer.Ordinal);
        expected.Add("receipt.json", true);
        for (int i = 0; i < ArtifactNames.Length; i++) expected.Add(ArtifactNames[i], true);
        FileSystemInfo[] entries;
        try { entries = new DirectoryInfo(target).GetFileSystemInfos(); }
        catch (Exception ex) { if (ex is IOException || ex is UnauthorizedAccessException) return false; throw; }
        if (entries.Length != expected.Count) return false;
        for (int i = 0; i < entries.Length; i++)
        {
            if (!expected.ContainsKey(entries[i].Name) || (entries[i].Attributes & (FileAttributes.Directory | FileAttributes.ReparsePoint)) != 0) return false;
        }
        return true;
    }

    private static SafeFileHandle OpenValidatedRegularFile(string path, int maximumLength, out int length)
    {
        string full = Path.GetFullPath(path);
        IntPtr raw = CreateFile(full, GenericRead | FileReadAttributes, FileShareRead, IntPtr.Zero, OpenExisting, FileFlagOpenReparsePoint, IntPtr.Zero);
        if (raw == new IntPtr(-1)) throw new InvalidOperationException("GMH-E-RECEIPT-FILE-LOCK-" + Marshal.GetLastWin32Error().ToString());
        SafeFileHandle handle = new SafeFileHandle(raw, true);
        try
        {
            ByHandleFileInformation info;
            if (!GetFileInformationByHandle(raw, out info) || (info.FileAttributes & (uint)(FileAttributes.Directory | FileAttributes.ReparsePoint)) != 0 || info.NumberOfLinks != 1 ||
                !String.Equals(NormalizePath(FinalPath(raw)), NormalizePath(full), StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("GMH-E-RECEIPT-FILE-IDENTITY");
            ulong size = ((ulong)info.FileSizeHigh << 32) | info.FileSizeLow;
            if (size < 1 || size > (ulong)maximumLength) throw new InvalidOperationException("GMH-E-RECEIPT-FILE-LENGTH");
            length = checked((int)size);
            return handle;
        }
        catch { handle.Dispose(); throw; }
    }

    private static byte[] ReadHandle(SafeFileHandle handle, int length)
    {
        using (SafeFileHandle borrowed = new SafeFileHandle(handle.DangerousGetHandle(), false))
        using (FileStream stream = new FileStream(borrowed, FileAccess.Read, 4096, false))
        {
            stream.Position = 0;
            byte[] bytes = ReadExact(stream, length);
            if (stream.ReadByte() != -1) { Clear(bytes); throw new InvalidOperationException("GMH-E-RECEIPT-FILE-LENGTH"); }
            return bytes;
        }
    }

    private static string HashHandle(SafeFileHandle handle)
    {
        using (SafeFileHandle borrowed = new SafeFileHandle(handle.DangerousGetHandle(), false))
        using (FileStream stream = new FileStream(borrowed, FileAccess.Read, 4096, false))
        using (SHA256 sha = SHA256.Create())
        {
            stream.Position = 0;
            return Hex(sha.ComputeHash(stream));
        }
    }

    private static bool BytesEqual(byte[] left, byte[] right)
    {
        if (left.Length != right.Length) return false;
        int difference = 0;
        for (int i = 0; i < left.Length; i++) difference |= left[i] ^ right[i];
        return difference == 0;
    }

    private static void TryCleanupKnownStaging(DirectoryLock stagingLock)
    {
        stagingLock.Verify();
        Dictionary<string, bool> allowed = new Dictionary<string, bool>(StringComparer.OrdinalIgnoreCase);
        foreach (string name in new string[] {
            "receipt.json", "root-ca-cert.pem", "root-ca-cert.der", "sender-cert.pem", "sender-cert.der", "sender-key.pem", "sender-password.dpapi",
            "recipient-cert.pem", "recipient-cert.der", "recipient-key.pem", "recipient-password.dpapi", "recipient-companion-sign-cert.pem", "recipient-companion-sign-cert.der"
        }) allowed.Add(name, true);
        FileSystemInfo[] entries = new DirectoryInfo(stagingLock.Path).GetFileSystemInfos();
        for (int i = 0; i < entries.Length; i++)
        {
            if (!allowed.ContainsKey(entries[i].Name) || (entries[i].Attributes & (FileAttributes.Directory | FileAttributes.ReparsePoint)) != 0) throw new InvalidOperationException("GMH-E-RECOVER-UNKNOWN");
        }
        for (int i = 0; i < entries.Length; i++) DeleteKnownFileByHandle(entries[i].FullName);
        stagingLock.Verify();
        IntPtr disposition = Marshal.AllocHGlobal(1);
        try
        {
            Marshal.WriteByte(disposition, 1);
            if (!SetFileInformationByHandle(stagingLock.Handle, FileDispositionInfo, disposition, 1)) throw new InvalidOperationException("GMH-E-CLEANUP-" + Marshal.GetLastWin32Error().ToString());
        }
        finally { Marshal.FreeHGlobal(disposition); }
    }

    private static void DeleteKnownFileByHandle(string path)
    {
        string full = Path.GetFullPath(path);
        IntPtr handle = CreateFile(full, DeleteAccess | FileReadAttributes, FileShareRead | FileShareWrite, IntPtr.Zero, OpenExisting, FileFlagOpenReparsePoint, IntPtr.Zero);
        if (handle == new IntPtr(-1)) throw new InvalidOperationException("GMH-E-CLEANUP-FILE-LOCK-" + Marshal.GetLastWin32Error().ToString());
        try
        {
            ByHandleFileInformation info;
            if (!GetFileInformationByHandle(handle, out info) || (info.FileAttributes & (uint)(FileAttributes.Directory | FileAttributes.ReparsePoint)) != 0 ||
                !String.Equals(NormalizePath(FinalPath(handle)), NormalizePath(full), StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("GMH-E-RECOVER-UNKNOWN");
            IntPtr disposition = Marshal.AllocHGlobal(1);
            try
            {
                Marshal.WriteByte(disposition, 1);
                if (!SetFileInformationByHandle(handle, FileDispositionInfo, disposition, 1)) throw new InvalidOperationException("GMH-E-CLEANUP-FILE-" + Marshal.GetLastWin32Error().ToString());
            }
            finally { Marshal.FreeHGlobal(disposition); }
        }
        finally { CloseHandle(handle); }
    }

    private static void RenameDirectory(DirectoryLock stagingLock, string target)
    {
        if (Directory.Exists(target) || File.Exists(target)) throw new InvalidOperationException("GMH-E-CONFLICT");
        byte[] name = Encoding.Unicode.GetBytes(Path.GetFullPath(target));
        // FILE_RENAME_INFO has a trailing WCHAR member. Keep an explicit
        // UTF-16 NUL/padding WCHAR beyond FileNameLength so the native parser
        // never observes allocator residue while consuming the variable tail.
        int informationLength = 20 + name.Length + 2;
        IntPtr info = Marshal.AllocHGlobal(informationLength);
        try
        {
            for (int i = 0; i < informationLength; i++) Marshal.WriteByte(info, i, 0);
            Marshal.WriteByte(info, 0, 0);
            Marshal.WriteIntPtr(info, 8, IntPtr.Zero);
            Marshal.WriteInt32(info, 16, name.Length);
            Marshal.Copy(name, 0, new IntPtr(info.ToInt64() + 20), name.Length);
            if (!SetFileInformationByHandle(stagingLock.Handle, FileRenameInfo, info, (uint)informationLength)) throw new InvalidOperationException("GMH-E-RENAME-" + Marshal.GetLastWin32Error().ToString());
        }
        finally { Clear(name); Marshal.FreeHGlobal(info); }
        if (!String.Equals(NormalizePath(FinalPath(stagingLock.Handle)), NormalizePath(target), StringComparison.OrdinalIgnoreCase)) throw new InvalidOperationException("GMH-E-RENAME-IDENTITY");
    }

    private static void WriteNewFlushed(string path, byte[] bytes)
    {
        using (FileStream output = new FileStream(path, FileMode.CreateNew, FileAccess.Write, FileShare.None, 4096, FileOptions.WriteThrough))
        {
            output.Write(bytes, 0, bytes.Length);
            output.Flush(true);
        }
    }

    private static byte[] Pem(string label, byte[] der)
    {
        string base64 = Convert.ToBase64String(der, Base64FormattingOptions.InsertLineBreaks).Replace("\r\n", "\n");
        return Encoding.ASCII.GetBytes("-----BEGIN " + label + "-----\n" + base64 + "\n-----END " + label + "-----\n");
    }

    private static string Hash(byte[] bytes)
    {
        using (SHA256 sha = SHA256.Create()) return Hex(sha.ComputeHash(bytes));
    }

    private static string Hex(byte[] bytes)
    {
        StringBuilder value = new StringBuilder(bytes.Length * 2);
        for (int i = 0; i < bytes.Length; i++) value.Append(bytes[i].ToString("x2"));
        return value.ToString();
    }

    private static void CrashAt(string point)
    {
        if (String.Equals(Environment.GetEnvironmentVariable("COEVO_TEST_KILL_POINT"), point, StringComparison.Ordinal)) Environment.Exit(90);
    }

    private static void GenerateKey(NativeApi api, KeyMaterial material, bool retain)
    {
        if (api.GenerateKey(material.Sm2.Pointer) != 1 || api.SetSm2Key(material.X509.Pointer, material.Sm2.Pointer) != 1) throw new InvalidOperationException("GMH-E-KEYGEN");
        if (!retain) return;
        using (NativeBuffer random = new NativeBuffer(32))
        using (NativeBuffer password = new NativeBuffer(65))
        {
            if (api.Random(random.Pointer, (UIntPtr)32) != 1) throw new InvalidOperationException("GMH-E-RANDOM");
            const string hex = "0123456789abcdef";
            for (int i = 0; i < 32; i++)
            {
                byte value = Marshal.ReadByte(random.Pointer, i);
                Marshal.WriteByte(password.Pointer, i * 2, (byte)hex[value >> 4]);
                Marshal.WriteByte(password.Pointer, i * 2 + 1, (byte)hex[value & 15]);
            }
            Marshal.WriteByte(password.Pointer, 64, 0);
            material.EncryptedDer = EncodePrivateKey(api, material.Sm2.Pointer, password.Pointer);
            ValidateEncryptedKey(api, material.Sm2.Pointer, material.EncryptedDer, password.Pointer);
            // Include the terminator so later native decrypt calls never read
            // beyond the DPAPI allocation while looking for a C-string end.
            material.SealedPassword = ProtectPassword(password.Pointer, 65);
            api.Clear(password.Pointer, (UIntPtr)65);
            api.Clear(random.Pointer, (UIntPtr)32);
        }
    }

    private static void ValidateEncryptedKey(NativeApi api, IntPtr originalKey, byte[] encryptedDer, IntPtr password)
    {
        using (NativeBuffer decoded = new NativeBuffer(NativeSm2KeyBytes))
        {
            GCHandle encoded = GCHandle.Alloc(encryptedDer, GCHandleType.Pinned);
            try
            {
                IntPtr input = encoded.AddrOfPinnedObject();
                UIntPtr inputLength = (UIntPtr)(uint)encryptedDer.Length;
                IntPtr attributes = IntPtr.Zero;
                UIntPtr attributesLength = UIntPtr.Zero;
                if (api.DecryptKey(decoded.Pointer, ref attributes, ref attributesLength, password, ref input, ref inputLength) != 1 || inputLength.ToUInt64() != 0 || api.PublicKeysEqual(originalKey, decoded.Pointer) != 1) throw new InvalidOperationException("GMH-E-PKCS8-ROUNDTRIP");
            }
            finally
            {
                encoded.Free();
                api.Clear(decoded.Pointer, (UIntPtr)(uint)decoded.Length);
            }
        }
    }

    private static byte[] EncodePrivateKey(NativeApi api, IntPtr key, IntPtr password)
    {
        IntPtr none = IntPtr.Zero;
        UIntPtr length = UIntPtr.Zero;
        if (api.EncryptKey(key, password, ref none, ref length) != 1) throw new InvalidOperationException("GMH-E-PKCS8");
        int size = CheckedSize(length);
        using (NativeBuffer encoded = new NativeBuffer(size))
        {
            IntPtr cursor = encoded.Pointer;
            UIntPtr written = UIntPtr.Zero;
            if (api.EncryptKey(key, password, ref cursor, ref written) != 1 || CheckedSize(written) != size) throw new InvalidOperationException("GMH-E-PKCS8");
            byte[] result = new byte[size];
            Marshal.Copy(encoded.Pointer, result, 0, size);
            return result;
        }
    }

    private static byte[] ProtectPassword(IntPtr password, int length)
    {
        GCHandle entropyHandle = GCHandle.Alloc(Entropy, GCHandleType.Pinned);
        DataBlob input = new DataBlob { Length = length, Data = password };
        DataBlob entropy = new DataBlob { Length = Entropy.Length, Data = entropyHandle.AddrOfPinnedObject() };
        DataBlob output;
        try
        {
            if (!CryptProtectData(ref input, null, ref entropy, IntPtr.Zero, IntPtr.Zero, CryptProtectUiForbidden, out output)) throw new CryptographicException();
            try
            {
                byte[] result = new byte[output.Length];
                Marshal.Copy(output.Data, result, 0, output.Length);
                return result;
            }
            finally
            {
                RtlZeroMemory(output.Data, (UIntPtr)(uint)output.Length);
                LocalFree(output.Data);
            }
        }
        finally { entropyHandle.Free(); }
    }

    private static byte[] CreateCertificate(NativeApi api, KeyMaterial subjectKey, KeyMaterial issuerKey, string subjectUnit, string subjectCommonName, string issuerUnit, string issuerCommonName, int usage, bool ca, byte[] issuerCertificate)
    {
        using (NativeBuffer subject = new NativeBuffer(NameBytes))
        using (NativeBuffer issuer = new NativeBuffer(NameBytes))
        using (NativeBuffer extensions = new NativeBuffer(ExtensionBytes))
        using (NativeBuffer serial = new NativeBuffer(16))
        {
            UIntPtr subjectLength = UIntPtr.Zero;
            UIntPtr issuerLength = UIntPtr.Zero;
            UIntPtr extensionsLength = UIntPtr.Zero;
            if (api.SetName(subject.Pointer, ref subjectLength, (UIntPtr)NameBytes, "CN", IntPtr.Zero, IntPtr.Zero, "Coevo Test Only", subjectUnit, subjectCommonName) != 1) throw new InvalidOperationException("GMH-E-NAME");
            if (api.SetName(issuer.Pointer, ref issuerLength, (UIntPtr)NameBytes, "CN", IntPtr.Zero, IntPtr.Zero, "Coevo Test Only", issuerUnit, issuerCommonName) != 1) throw new InvalidOperationException("GMH-E-NAME");
            if (api.Random(serial.Pointer, (UIntPtr)16) != 1) throw new InvalidOperationException("GMH-E-RANDOM");
            Marshal.WriteByte(serial.Pointer, 0, (byte)(Marshal.ReadByte(serial.Pointer, 0) & 0x7f));
            if (api.AddSubjectId(extensions.Pointer, ref extensionsLength, (UIntPtr)ExtensionBytes, X509NonCritical, subjectKey.X509.Pointer) != 1) throw new InvalidOperationException("GMH-E-EXT");
            if (api.AddAuthorityId(extensions.Pointer, ref extensionsLength, (UIntPtr)ExtensionBytes, issuerKey.X509.Pointer) != 1) throw new InvalidOperationException("GMH-E-EXT");
            if (api.AddUsage(extensions.Pointer, ref extensionsLength, (UIntPtr)ExtensionBytes, X509Critical, usage) != 1) throw new InvalidOperationException("GMH-E-EXT");
            if (api.AddConstraints(extensions.Pointer, ref extensionsLength, (UIntPtr)ExtensionBytes, X509Critical, ca ? 1 : 0, ca ? 0 : -1) != 1) throw new InvalidOperationException("GMH-E-EXT");
            long now = DateTimeOffset.UtcNow.ToUnixTimeSeconds();
            IntPtr none = IntPtr.Zero;
            UIntPtr derLength = UIntPtr.Zero;
            if (api.SignCertificate(X509VersionV3, serial.Pointer, (UIntPtr)16, OidSm2SignWithSm3, issuer.Pointer, issuerLength, now - 300, now + (ca ? 2592000 : 1209600), subject.Pointer, subjectLength, subjectKey.X509.Pointer, IntPtr.Zero, UIntPtr.Zero, IntPtr.Zero, UIntPtr.Zero, extensions.Pointer, extensionsLength, issuerKey.X509.Pointer, IntPtr.Zero, UIntPtr.Zero, ref none, ref derLength) != 1) throw new InvalidOperationException("GMH-E-CERT");
            int size = CheckedSize(derLength);
            using (NativeBuffer der = new NativeBuffer(size))
            {
                IntPtr cursor = der.Pointer;
                UIntPtr written = UIntPtr.Zero;
                if (api.SignCertificate(X509VersionV3, serial.Pointer, (UIntPtr)16, OidSm2SignWithSm3, issuer.Pointer, issuerLength, now - 300, now + (ca ? 2592000 : 1209600), subject.Pointer, subjectLength, subjectKey.X509.Pointer, IntPtr.Zero, UIntPtr.Zero, IntPtr.Zero, UIntPtr.Zero, extensions.Pointer, extensionsLength, issuerKey.X509.Pointer, IntPtr.Zero, UIntPtr.Zero, ref cursor, ref written) != 1 || CheckedSize(written) != size) throw new InvalidOperationException("GMH-E-CERT");
                byte[] result = new byte[size];
                Marshal.Copy(der.Pointer, result, 0, size);
                if (issuerCertificate == null)
                {
                    if (Verify(api, result, result) != 1) throw new InvalidOperationException("GMH-E-VERIFY");
                }
                else if (Verify(api, result, issuerCertificate) != 1) throw new InvalidOperationException("GMH-E-VERIFY");
                return result;
            }
        }
    }

    private static int Verify(NativeApi api, byte[] certificate, byte[] caCertificate)
    {
        GCHandle cert = GCHandle.Alloc(certificate, GCHandleType.Pinned);
        GCHandle ca = GCHandle.Alloc(caCertificate, GCHandleType.Pinned);
        try { return api.VerifyCertificate(cert.AddrOfPinnedObject(), (UIntPtr)(uint)certificate.Length, ca.AddrOfPinnedObject(), (UIntPtr)(uint)caCertificate.Length, IntPtr.Zero, UIntPtr.Zero); }
        finally { cert.Free(); ca.Free(); }
    }

    private static int CheckedSize(UIntPtr value)
    {
        ulong size = value.ToUInt64();
        if (size < 1 || size > MaxDerBytes) throw new InvalidOperationException("GMH-E-LENGTH");
        return checked((int)size);
    }

    private static void WriteResponse(Stream output, byte action, byte status, byte[] nonce, byte[] receiptHash)
    {
        if (receiptHash == null || receiptHash.Length != 32) throw new InvalidOperationException("GMH-E-RESPONSE");
        using (BinaryWriter writer = new BinaryWriter(output, Encoding.ASCII, true))
        {
            writer.Write(ResponseMagic);
            writer.Write((byte)2);
            writer.Write(action);
            writer.Write(status);
            writer.Write(nonce);
            writer.Write(receiptHash);
            writer.Flush();
        }
    }

    private static void Clear(byte[] value)
    {
        if (value != null) Array.Clear(value, 0, value.Length);
    }
}

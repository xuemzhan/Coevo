using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;

internal static class CoevoCryptoHelper
{
    private const int MaxFrame = 16 * 1024 * 1024;
    private const int Sm2KeyBytes = 512;
    private const int X509KeyBytes = 23760;
    private static readonly byte[] Magic = Encoding.ASCII.GetBytes("COEVOCRYPTO/1");
    private static readonly byte[] Reply = Encoding.ASCII.GetBytes("COEVOCRYPTO-R/1");
    private static readonly byte[] Entropy = Encoding.ASCII.GetBytes("Coevo.SM2.Test.PKI.DPAPI.v1");

    [StructLayout(LayoutKind.Sequential)] private struct Blob { public int cb; public IntPtr pb; }
    [DllImport("crypt32.dll", SetLastError=true)] private static extern bool CryptUnprotectData(ref Blob input, IntPtr description, ref Blob entropy, IntPtr reserved, IntPtr prompt, uint flags, out Blob output);
    [DllImport("kernel32.dll")] private static extern IntPtr LocalFree(IntPtr value);
    [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)] private static extern IntPtr LoadLibraryEx(string path, IntPtr file, uint flags);
    [DllImport("kernel32.dll", CharSet=CharSet.Ansi, SetLastError=true)] private static extern IntPtr GetProcAddress(IntPtr module, string name);
    [DllImport("kernel32.dll")] private static extern void RtlZeroMemory(IntPtr p, UIntPtr n);
    private static readonly System.Text.RegularExpressions.Regex KekNameRe = new System.Text.RegularExpressions.Regex("^CoevoSm2Kek-[0-9a-f]{32}$");

    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate void Sm3Init(IntPtr ctx);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate void Sm3Update(IntPtr ctx, IntPtr data, UIntPtr len);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate void Sm3Finish(IntPtr ctx, IntPtr digest);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int Sm2Sign(IntPtr key, IntPtr digest, IntPtr sig, ref UIntPtr siglen);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int Sm2Verify(IntPtr key, IntPtr digest, IntPtr sig, UIntPtr siglen);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int Sm2Encrypt(IntPtr key, IntPtr input, UIntPtr inputLen, IntPtr output, ref UIntPtr outputLen);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int Sm2Decrypt(IntPtr key, IntPtr input, UIntPtr inputLen, IntPtr output, ref UIntPtr outputLen);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int DecryptKey(IntPtr key, ref IntPtr attrs, ref UIntPtr attrsLen, IntPtr password, ref IntPtr input, ref UIntPtr inputLen);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int CertPublic(IntPtr cert, UIntPtr certLen, IntPtr key);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate void Sm4SetKey(IntPtr key, IntPtr raw);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int Sm4GcmEncrypt(IntPtr key, IntPtr iv, UIntPtr ivLen, IntPtr aad, UIntPtr aadLen, IntPtr input, UIntPtr inputLen, IntPtr output, UIntPtr tagLen, IntPtr tag);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int Sm4GcmDecrypt(IntPtr key, IntPtr iv, UIntPtr ivLen, IntPtr aad, UIntPtr aadLen, IntPtr input, UIntPtr inputLen, IntPtr tag, UIntPtr tagLen, IntPtr output);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int GcmInit(IntPtr ctx, IntPtr key, UIntPtr keyLen, IntPtr iv, UIntPtr ivLen, IntPtr aad, UIntPtr aadLen, UIntPtr tagLen);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int GcmUpdate(IntPtr ctx, IntPtr input, UIntPtr inputLen, IntPtr output, ref UIntPtr outputLen);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int GcmFinish(IntPtr ctx, IntPtr output, ref UIntPtr outputLen);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int RandBytes(IntPtr output, UIntPtr len);

    private sealed class Api {
        internal readonly Sm3Init HInit; internal readonly Sm3Update HUpdate; internal readonly Sm3Finish HFinish;
        internal readonly Sm2Sign Sign; internal readonly Sm2Verify Verify; internal readonly Sm2Encrypt Encrypt; internal readonly Sm2Decrypt Decrypt;
        internal readonly DecryptKey DecodeKey; internal readonly CertPublic Public; internal readonly Sm4SetKey SetSm4;
        internal readonly Sm4GcmEncrypt GcmEncrypt; internal readonly Sm4GcmDecrypt GcmDecrypt; internal readonly RandBytes Rand;
        internal readonly GcmInit EncInit, DecInit; internal readonly GcmUpdate EncUpdate, DecUpdate; internal readonly GcmFinish EncFinish, DecFinish;
        internal Api(IntPtr m) { HInit=B<Sm3Init>(m,"sm3_init"); HUpdate=B<Sm3Update>(m,"sm3_update"); HFinish=B<Sm3Finish>(m,"sm3_finish"); Sign=B<Sm2Sign>(m,"sm2_sign"); Verify=B<Sm2Verify>(m,"sm2_verify"); Encrypt=B<Sm2Encrypt>(m,"sm2_encrypt"); Decrypt=B<Sm2Decrypt>(m,"sm2_decrypt"); DecodeKey=B<DecryptKey>(m,"sm2_private_key_info_decrypt_from_der"); Public=B<CertPublic>(m,"x509_cert_get_subject_public_key"); SetSm4=B<Sm4SetKey>(m,"sm4_set_encrypt_key"); GcmEncrypt=B<Sm4GcmEncrypt>(m,"sm4_gcm_encrypt"); GcmDecrypt=B<Sm4GcmDecrypt>(m,"sm4_gcm_decrypt"); EncInit=B<GcmInit>(m,"sm4_gcm_encrypt_init"); EncUpdate=B<GcmUpdate>(m,"sm4_gcm_encrypt_update"); EncFinish=B<GcmFinish>(m,"sm4_gcm_encrypt_finish"); DecInit=B<GcmInit>(m,"sm4_gcm_decrypt_init"); DecUpdate=B<GcmUpdate>(m,"sm4_gcm_decrypt_update"); DecFinish=B<GcmFinish>(m,"sm4_gcm_decrypt_finish"); Rand=B<RandBytes>(m,"rand_bytes"); }
        private static T B<T>(IntPtr m,string n) where T:class { IntPtr p=GetProcAddress(m,n); if(p==IntPtr.Zero) throw new InvalidOperationException("GCP-E-ABI"); return Marshal.GetDelegateForFunctionPointer(p,typeof(T)) as T; }
    }

    private sealed class Native : IDisposable { internal IntPtr P; internal int N; internal Native(int n){N=n;P=Marshal.AllocHGlobal(n);RtlZeroMemory(P,(UIntPtr)n);} public void Dispose(){if(P!=IntPtr.Zero){RtlZeroMemory(P,(UIntPtr)N);Marshal.FreeHGlobal(P);P=IntPtr.Zero;}} }

    [StructLayout(LayoutKind.Sequential)] private struct OaepPaddingInfo { public IntPtr pszAlgId; public IntPtr pbLabel; public int cbLabel; }

    private static int Main(string[] args) {
        try {
            if(args.Length!=0) return Fail("GCP-E-ARGS");
            string root=Path.GetFullPath(Environment.CurrentDirectory);
            if(!File.Exists(Path.Combine(root,"docs","dependencies","toolchain-lock.json"))) return Fail("GCP-E-ROOT");
            string dll=Path.Combine(root,".tools","gmssl","3.2.0","GmSSL-3.2.0-win64","bin","gmssl.dll");
            if(new FileInfo(dll).Length!=1665024 || (new FileInfo(dll).Attributes&FileAttributes.ReparsePoint)!=0) return Fail("GCP-E-INTEGRITY");
            IntPtr module=LoadLibraryEx(dll,IntPtr.Zero,0x100|0x800); if(module==IntPtr.Zero) return Fail("GCP-E-DLL"); Api api=new Api(module);
            using(BinaryReader r=new BinaryReader(Console.OpenStandardInput(),Encoding.ASCII)) {
                if(!Eq(r.ReadBytes(Magic.Length),Magic)) throw new InvalidDataException("GCP-E-MAGIC");
                byte action=r.ReadByte(); int pn=r.ReadByte(); if(pn<1||pn>32) throw new InvalidDataException("GCP-E-PROFILE"); string profile=Encoding.ASCII.GetString(r.ReadBytes(pn)); if(!Safe(profile)) throw new InvalidDataException("GCP-E-PROFILE");
                byte[][] f=new byte[r.ReadByte()][]; for(int i=0;i<f.Length;i++) f[i]=Frame(r); if(r.BaseStream.ReadByte()!=-1) throw new InvalidDataException("GCP-E-TRAILING");
                byte[][] output=Run(api,root,profile,action,f); Write(output); Clear(f); Clear(output);
            }
            return 0;
        } catch(InvalidDataException e){return Fail(e.Message.StartsWith("GCP-E-")?e.Message:"GCP-E-INPUT");} catch(CryptographicException){return Fail("GCP-E-DPAPI");} catch(Exception e){return Fail(e.Message.StartsWith("GCP-E-")?e.Message:"GCP-E-CRYPTO-"+Convert.ToBase64String(Encoding.UTF8.GetBytes(e.GetType().Name+": "+e.Message)));}
    }
    private static byte[][] Run(Api a,string root,string profile,byte action,byte[][] f) {
        if(action==1 && f.Length==1) return new[]{Hash(a,f[0])};
        string dir=Path.Combine(root,"loop","runtime","sm2-test-pki",profile);
        bool needsDir = action>=2 && action<=8;
        if(needsDir && (!Directory.Exists(dir)||(new DirectoryInfo(dir).Attributes&FileAttributes.ReparsePoint)!=0)) throw new InvalidOperationException("GCP-E-HANDLE");
        if(action==2 && f.Length==1) using(Native key=Private(a,dir,"sender")){byte[] d=Hash(a,f[0]);byte[] s=SignDigest(a,key,d);Clear(d);return new[]{s};}
        if(action==3 && f.Length==2) using(Native key=Public(a,dir,"sender")){byte[] d=Hash(a,f[0]);bool ok=VerifyDigest(a,key,d,f[1]);Clear(d);return new[]{new[]{(byte)(ok?1:0)}};}
        if(action==4 && f.Length==3) return Seal(a,dir,f[0],f[1],f[2]);
        if(action==5 && f.Length==5) return Open(a,dir,f[0],f[1],f[2],f[3],f[4]);
        if(action==6 && f.Length==4) return SignWrapped(a,dir,f[0],f[1],f[2],f[3]);
        if(action==7 && f.Length==8) return OpenWrapped(a,dir,f[0],f[1],f[2],f[3],f[4],f[5],f[6],f[7]);
        if(action==8 && f.Length==2) return Protect(dir,f[0],f[1]);
        throw new InvalidDataException("GCP-E-ACTION");
    }
    private static byte[] Hash(Api a,byte[] input){using(Native c=new Native(128))using(Native d=new Native(32)){a.HInit(c.P);CopyCall(input,p=>a.HUpdate(c.P,p,(UIntPtr)input.Length));a.HFinish(c.P,d.P);return Bytes(d.P,32);}}
    private static byte[] SignDigest(Api a,Native k,byte[] d){using(Native dn=Put(d))using(Native s=new Native(80)){UIntPtr n=(UIntPtr)80;if(a.Sign(k.P,dn.P,s.P,ref n)!=1)throw new InvalidOperationException("GCP-E-SIGN");return Bytes(s.P,(int)n);}}
    private static bool VerifyDigest(Api a,Native k,byte[] d,byte[] s){using(Native dn=Put(d))using(Native sn=Put(s)){return a.Verify(IntPtr.Add(k.P,8),dn.P,sn.P,(UIntPtr)s.Length)==1;}}
    private static byte[][] Seal(Api a,string dir,byte[] plain,byte[] aad,byte[] nonce){if(nonce.Length!=12)throw new InvalidDataException("GCP-E-FRAME");byte[] sk=new byte[16],wrapped=null,cipher,tag;using(Native recipient=Public(a,dir,"recipient")){CopyCall(sk,p=>{if(a.Rand(p,(UIntPtr)16)!=1)throw new InvalidOperationException("GCP-E-RAND");Marshal.Copy(p,sk,0,16);});wrapped=EncryptKey(a,recipient,sk);GcmSeal(a,sk,nonce,aad,plain,out cipher,out tag);}Clear(sk);return new[]{wrapped,nonce,cipher,tag};}
    private static byte[][] Open(Api a,string dir,byte[] wrapped,byte[] nonce,byte[] cipher,byte[] tag,byte[] aad){if(nonce.Length!=12||tag.Length!=16)throw new InvalidDataException("GCP-E-FRAME");byte[] sk,plain;using(Native recipient=Private(a,dir,"recipient")){sk=UnwrapKey(a,recipient,wrapped);}if(sk.Length!=16){Clear(sk);throw new InvalidOperationException("GCP-E-UNWRAP");}plain=GcmOpen(a,sk,nonce,aad,cipher,tag);Clear(sk);return new[]{plain};}
    private static void GcmSeal(Api a,byte[] key,byte[] iv,byte[] aad,byte[] plain,out byte[] cipher,out byte[] tag){using(Native ctx=new Native(512))using(Native k=Put(key))using(Native n=Put(iv))using(Native ad=Put(aad))using(Native input=Put(plain))using(Native output=new Native(plain.Length+32)){if(a.EncInit(ctx.P,k.P,(UIntPtr)key.Length,n.P,(UIntPtr)iv.Length,ad.P,(UIntPtr)aad.Length,(UIntPtr)16)!=1)throw new InvalidOperationException("GCP-E-SEAL");UIntPtr first=(UIntPtr)(plain.Length+32);if(a.EncUpdate(ctx.P,input.P,(UIntPtr)plain.Length,output.P,ref first)!=1)throw new InvalidOperationException("GCP-E-SEAL");int used=(int)first;UIntPtr last=(UIntPtr)(plain.Length+32-used);if(a.EncFinish(ctx.P,IntPtr.Add(output.P,used),ref last)!=1)throw new InvalidOperationException("GCP-E-SEAL");int total=used+(int)last;if(total!=plain.Length+16)throw new InvalidOperationException("GCP-E-SEAL-LENGTH");byte[] all=Bytes(output.P,total);cipher=new byte[plain.Length];tag=new byte[16];Buffer.BlockCopy(all,0,cipher,0,cipher.Length);Buffer.BlockCopy(all,cipher.Length,tag,0,16);Clear(all);}}
    private static byte[] GcmOpen(Api a,byte[] key,byte[] iv,byte[] aad,byte[] cipher,byte[] tag){byte[] combined=new byte[cipher.Length+tag.Length];Buffer.BlockCopy(cipher,0,combined,0,cipher.Length);Buffer.BlockCopy(tag,0,combined,cipher.Length,tag.Length);try{using(Native ctx=new Native(512))using(Native k=Put(key))using(Native n=Put(iv))using(Native ad=Put(aad))using(Native input=Put(combined))using(Native output=new Native(cipher.Length+32)){if(a.DecInit(ctx.P,k.P,(UIntPtr)key.Length,n.P,(UIntPtr)iv.Length,ad.P,(UIntPtr)aad.Length,(UIntPtr)16)!=1)throw new InvalidOperationException("GCP-E-AUTH");UIntPtr first=(UIntPtr)(cipher.Length+32);if(a.DecUpdate(ctx.P,input.P,(UIntPtr)combined.Length,output.P,ref first)!=1)throw new InvalidOperationException("GCP-E-AUTH");int used=(int)first;UIntPtr last=(UIntPtr)(cipher.Length+32-used);if(a.DecFinish(ctx.P,IntPtr.Add(output.P,used),ref last)!=1)throw new InvalidOperationException("GCP-E-AUTH");int total=used+(int)last;if(total!=cipher.Length)throw new InvalidOperationException("GCP-E-AUTH");return Bytes(output.P,total);}}finally{Clear(combined);}}
    private static byte[] EncryptKey(Api a,Native x,byte[] sk){using(Native i=Put(sk))using(Native o=new Native(512)){UIntPtr n=(UIntPtr)512;if(a.Encrypt(IntPtr.Add(x.P,8),i.P,(UIntPtr)sk.Length,o.P,ref n)!=1)throw new InvalidOperationException("GCP-E-WRAP");return Bytes(o.P,(int)n);}}
    private static byte[] UnwrapKey(Api a,Native k,byte[] wrapped){using(Native i=Put(wrapped))using(Native o=new Native(512)){UIntPtr n=(UIntPtr)512;if(a.Decrypt(k.P,i.P,(UIntPtr)wrapped.Length,o.P,ref n)!=1)throw new InvalidOperationException("GCP-E-UNWRAP");return Bytes(o.P,(int)n);}}
    private static Native Public(Api a,string dir,string role){byte[] der=Regular(Path.Combine(dir,role+"-cert.der"),65536);Native x=new Native(X509KeyBytes);using(Native d=Put(der)){if(a.Public(d.P,(UIntPtr)der.Length,x.P)!=1){x.Dispose();throw new InvalidOperationException("GCP-E-CERT");}}Clear(der);return x;}
    private static Native Private(Api a,string dir,string role){byte[] pem=Regular(Path.Combine(dir,role+"-key.pem"),65536),sealedPw=Regular(Path.Combine(dir,role+"-password.dpapi"),4096),der=null,pw=null;try{der=Pem(pem);pw=Unprotect(sealedPw);return DecodeKeyFromBytes(a,der,pw);}finally{Clear(pem);Clear(sealedPw);Clear(der);Clear(pw);}}
    private static Native DecodeKeyFromBytes(Api a,byte[] der,byte[] pw){Native key=new Native(Sm2KeyBytes);try{using(Native dn=Put(der))using(Native pn=Put(pw)){IntPtr cur=dn.P,attrs=IntPtr.Zero;UIntPtr left=(UIntPtr)der.Length,attrsLen=UIntPtr.Zero;if(a.DecodeKey(key.P,ref attrs,ref attrsLen,pn.P,ref cur,ref left)!=1||left.ToUInt64()!=0)throw new InvalidOperationException("GCP-E-KEY");}return key;}catch{key.Dispose();throw;}}

    // ---- HANDLE-2: CNG KEK-wrapped SM2 keys (key bytes stay helper-side) ----
    private static byte[] CngRsa(string kekName,bool encrypt,byte[] input){
        if(!KekNameRe.IsMatch(kekName)) throw new InvalidDataException("GCP-E-KEK-NAME");
        CngKey key;
        try{ key=CngKey.Open(kekName,CngProvider.MicrosoftSoftwareKeyStorageProvider,CngKeyOpenOptions.None); }
        catch(CryptographicException){ throw new InvalidOperationException("GCP-E-CNG-KEY"); }
        using(var rsa=new RSACng(key)){
            try{ return encrypt?rsa.Encrypt(input,RSAEncryptionPadding.OaepSHA256):rsa.Decrypt(input,RSAEncryptionPadding.OaepSHA256); }
            catch(CryptographicException){ throw new InvalidOperationException(encrypt?"GCP-E-CNG-WRAP":"GCP-E-CNG-UNWRAP"); }
        }
    }
    private static byte[] CngWrap(string kekName,byte[] input){return CngRsa(kekName,true,input);}
    private static byte[] CngUnwrap(string kekName,byte[] input){return CngRsa(kekName,false,input);}
    private static string Ascii(byte[] value){try{return Encoding.ASCII.GetString(value);}catch{throw new InvalidDataException("GCP-E-KEK-NAME");}}
    private static string RoleName(byte[] role){if(role.Length!=1||(role[0]!=(byte)'s'&&role[0]!=(byte)'r'))throw new InvalidDataException("GCP-E-ROLE");return role[0]==(byte)'s'?"sender":"recipient";}
    private static byte[][] SignWrapped(Api a,string dir,byte[] wrapped,byte[] kekName,byte[] role,byte[] data){
        string roleName=RoleName(role);
        byte[] der=null,pw=null;
        try{ der=Pem(Regular(Path.Combine(dir,roleName+"-key.pem"),65536));
             pw=CngUnwrap(Ascii(kekName),wrapped);
             using(Native key=DecodeKeyFromBytes(a,der,pw)){byte[] d=Hash(a,data);byte[] s=SignDigest(a,key,d);Clear(d);return new[]{s};} }
        finally{ Clear(der);Clear(pw); }
    }
    private static byte[][] OpenWrapped(Api a,string dir,byte[] wrapped,byte[] kekName,byte[] role,byte[] sessionKey,byte[] nonce,byte[] cipher,byte[] tag,byte[] aad){
        if(nonce.Length!=12||tag.Length!=16)throw new InvalidDataException("GCP-E-FRAME");
        string roleName=RoleName(role);
        byte[] der=null,pw=null;
        try{ der=Pem(Regular(Path.Combine(dir,roleName+"-key.pem"),65536));
             pw=CngUnwrap(Ascii(kekName),wrapped);
             using(Native key=DecodeKeyFromBytes(a,der,pw)){byte[] sk=UnwrapKey(a,key,sessionKey);if(sk.Length!=16){Clear(sk);throw new InvalidOperationException("GCP-E-UNWRAP");}byte[] plain=GcmOpen(a,sk,nonce,aad,cipher,tag);Clear(sk);return new[]{plain};} }
        finally{ Clear(der);Clear(pw); }
    }
    private static byte[][] Protect(string dir,byte[] kekName,byte[] role){
        string roleName=RoleName(role);
        byte[] pwBlob=Regular(Path.Combine(dir,roleName+"-password.dpapi"),4096),pw=null;
        try{ pw=Unprotect(pwBlob); byte[] wrapped=CngWrap(Ascii(kekName),pw); return new[]{wrapped}; }
        finally{ Clear(pwBlob);Clear(pw); }
    }
    private static byte[] Unprotect(byte[] input){GCHandle hi=GCHandle.Alloc(input,GCHandleType.Pinned),he=GCHandle.Alloc(Entropy,GCHandleType.Pinned);Blob ib=new Blob{cb=input.Length,pb=hi.AddrOfPinnedObject()},eb=new Blob{cb=Entropy.Length,pb=he.AddrOfPinnedObject()},ob;try{if(!CryptUnprotectData(ref ib,IntPtr.Zero,ref eb,IntPtr.Zero,IntPtr.Zero,1,out ob))throw new CryptographicException();try{return Bytes(ob.pb,ob.cb);}finally{RtlZeroMemory(ob.pb,(UIntPtr)ob.cb);LocalFree(ob.pb);}}finally{hi.Free();he.Free();}}
    private static byte[] Pem(byte[] p){string s=Encoding.ASCII.GetString(p);int a=s.IndexOf('\n')+1,b=s.IndexOf("-----END",StringComparison.Ordinal);if(a<1||b<a)throw new InvalidDataException("GCP-E-PEM");return Convert.FromBase64String(s.Substring(a,b-a).Replace("\r","").Replace("\n",""));}
    private static byte[] Regular(string p,int max){FileInfo f=new FileInfo(p);if(!f.Exists||(f.Attributes&FileAttributes.ReparsePoint)!=0||f.Length<1||f.Length>max)throw new InvalidOperationException("GCP-E-HANDLE");return File.ReadAllBytes(p);}
    private static byte[] Frame(BinaryReader r){int n=ReadI32(r);if(n<0||n>MaxFrame)throw new InvalidDataException("GCP-E-FRAME");byte[] b=r.ReadBytes(n);if(b.Length!=n)throw new InvalidDataException("GCP-E-TRUNCATED");return b;}
    private static int ReadI32(BinaryReader r){byte[] b=r.ReadBytes(4);if(b.Length!=4)throw new InvalidDataException("GCP-E-TRUNCATED");return (b[0]<<24)|(b[1]<<16)|(b[2]<<8)|b[3];}
    private static void Write(byte[][] f){Stream s=Console.OpenStandardOutput();s.Write(Reply,0,Reply.Length);s.WriteByte((byte)f.Length);foreach(byte[] b in f){byte[] n={(byte)((b.Length>>24)&255),(byte)((b.Length>>16)&255),(byte)((b.Length>>8)&255),(byte)(b.Length&255)};s.Write(n,0,4);s.Write(b,0,b.Length);}s.Flush();}
    private static bool Safe(string s){if(s.Length<1||s.Length>32)return false;for(int i=0;i<s.Length;i++){char c=s[i];if(!((c>='a'&&c<='z')||(c>='0'&&c<='9')||(c=='-'&&i>0)))return false;}return true;}
    private static bool Eq(byte[] a,byte[] b){if(a.Length!=b.Length)return false;int x=0;for(int i=0;i<a.Length;i++)x|=a[i]^b[i];return x==0;}
    private static Native Put(byte[] b){Native n=new Native(Math.Max(1,b.Length));if(b.Length>0)Marshal.Copy(b,0,n.P,b.Length);return n;} private static byte[] Bytes(IntPtr p,int n){byte[] b=new byte[n];Marshal.Copy(p,b,0,n);return b;}
    private static void CopyCall(byte[] b,Action<IntPtr> a){using(Native n=Put(b))a(n.P);} private delegate void Five(IntPtr a,IntPtr b,IntPtr c,IntPtr d,IntPtr e); private static void Pin5(byte[] a,byte[] b,byte[] c,byte[] d,byte[] e,Five call){using(Native an=Put(a))using(Native bn=Put(b))using(Native cn=Put(c))using(Native dn=Put(d))using(Native en=Put(e)){call(an.P,bn.P,cn.P,dn.P,en.P);if(d.Length>0)Marshal.Copy(dn.P,d,0,d.Length);if(e.Length>0)Marshal.Copy(en.P,e,0,e.Length);}}
    private static void Clear(byte[] b){if(b!=null)Array.Clear(b,0,b.Length);} private static void Clear(byte[][] a){if(a!=null)foreach(byte[] b in a)Clear(b);} private static int Fail(string c){try{Console.Error.WriteLine(c);}catch{}return 22;}
}

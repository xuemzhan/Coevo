import hashlib, json, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class DevEnvironmentToolsTest(unittest.TestCase):
    def test_toolchain_is_exactly_locked(self):
        lock=json.loads((ROOT/'docs/dependencies/toolchain-lock.json').read_text(encoding='utf-8'))
        self.assertFalse(lock['runtime_downloads_allowed'])
        tool=lock['tools']['opencode']
        self.assertEqual('1.18.2',tool['version'])
        self.assertEqual('MIT',tool['license'])
        self.assertEqual([],tool['external_runtime_dependencies'])
        self.assertTrue((ROOT/tool['license_path']).is_file())
        self.assertRegex(tool['archive']['sha256'],r'^[0-9a-f]{64}$')
        self.assertRegex(tool['executable']['sha256'],r'^[0-9a-f]{64}$')
        self.assertEqual('Valid',tool['executable']['authenticode_status'])
        self.assertIn('O="Anomaly Innovations',tool['executable']['signer_subject'])
        compiler=lock['tools']['make_compatibility_shim']['compiler_lock']
        self.assertEqual('Microsoft.NET/Framework64/v4.0.30319/csc.exe',compiler['windows_directory_relative_path'])
        self.assertEqual(2569832,compiler['size'])
        self.assertRegex(compiler['sha256'],r'^[0-9a-f]{64}$')
        self.assertRegex(compiler['signer_thumbprint'],r'^[0-9A-F]{40}$')
        python=lock['tools']['python']
        self.assertEqual('3.14.3',python['version'])
        self.assertEqual(5421,python['file_count'])
        self.assertEqual(163694479,python['total_size'])
        self.assertEqual('Valid',python['executable']['authenticode_status'])
        self.assertRegex(python['executable']['signer_thumbprint'],r'^[0-9A-F]{40}$')
        self.assertEqual(591052,python['inventory']['size'])
        self.assertRegex(python['inventory']['sha256'],r'^[0-9a-f]{64}$')
        self.assertRegex(lock['tools']['make_compatibility_shim']['script_inventory']['sha256'],r'^[0-9a-f]{64}$')

    def test_official_release_metadata_matches_lock(self):
        lock=json.loads((ROOT/'docs/dependencies/toolchain-lock.json').read_text(encoding='utf-8'))['tools']['opencode']
        evidence=json.loads((ROOT/lock['release_metadata_evidence_path']).read_text(encoding='utf-8'))
        self.assertTrue(evidence['release']['immutable'])
        self.assertEqual('v'+lock['version'],evidence['release']['tag_name'])
        self.assertEqual(lock['archive']['asset_api_id'],evidence['asset']['id'])
        self.assertEqual(lock['archive']['size'],evidence['asset']['size'])
        self.assertEqual('sha256:'+lock['archive']['sha256'],evidence['asset']['digest'])

    def test_present_artifacts_match_lock(self):
        lock=json.loads((ROOT/'docs/dependencies/toolchain-lock.json').read_text(encoding='utf-8'))['tools']['opencode']
        for kind in ('archive','executable'):
            item=lock[kind]; path=ROOT/item['path']
            self.assertTrue(path.is_file(),path)
            self.assertEqual(item['size'],path.stat().st_size)
            digest=hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda:stream.read(1024*1024),b''): digest.update(chunk)
            self.assertEqual(item['sha256'],digest.hexdigest())

    def test_present_python_and_script_inventories_match_lock(self):
        lock=json.loads((ROOT/'docs/dependencies/toolchain-lock.json').read_text(encoding='utf-8'))['tools']
        items=(lock['python']['executable'],lock['python']['inventory'],
               lock['make_compatibility_shim']['script_inventory'])
        for item in items:
            path=ROOT/item['path']
            self.assertTrue(path.is_file(),path)
            self.assertEqual(item['size'],path.stat().st_size)
            digest=hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda:stream.read(1024*1024),b''): digest.update(chunk)
            self.assertEqual(item['sha256'],digest.hexdigest())

if __name__=='__main__': unittest.main()

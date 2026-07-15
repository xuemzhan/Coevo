import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class PermissionTests(unittest.TestCase):
    def test_network_and_install_commands_are_fail_closed(self):
        raw=(ROOT/"opencode.jsonc").read_text(encoding="utf-8")
        self.assertIn('"webfetch": "deny"',raw); self.assertIn('"websearch": "deny"',raw)
        for command in ("git push*","curl *","wget *","pip install*","npm install*"): self.assertIn(f'"{command}": "deny"',raw)
    def test_custom_tools_use_current_typed_api(self):
        for path in (ROOT/".opencode/tools").glob("*.ts"): self.assertIn("export default tool(",path.read_text(encoding="utf-8"))

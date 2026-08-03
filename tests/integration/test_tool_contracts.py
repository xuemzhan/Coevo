import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class ToolContractIntegrationTests(unittest.TestCase):
    def test_custom_tools_reference_existing_controlled_scripts(self):
        contracts={
            "loop_state.ts":"scripts/loop_state.py",
            "quality_gate.ts":"scripts/quality_gate.py",
            "traceability_check.ts":"scripts/traceability_check.py",
        }
        for tool_name,script_name in contracts.items():
            tool=(ROOT/".opencode/tools"/tool_name).read_text(encoding="utf-8")
            self.assertIn("export default tool(",tool)
            self.assertTrue((ROOT/script_name).is_file(),script_name)

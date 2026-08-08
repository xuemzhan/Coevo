"""FRAMEWORK-OPTIMIZE-12: framework-internal canonical functions unify onto canon."""

from __future__ import annotations

import unittest
from pathlib import Path

from src.coevo.canon import canonical_json_bytes
from src.coevo.framework.k8s_listing import (
    ListingInput,
    generate_listing,
    generate_listing_json,
)
from src.coevo.framework.memory import MemoryKind, MemoryRecord, canonical_record_bytes
from src.coevo.framework.policy import get_default_profile
from src.coevo.framework.tools import (
    Tool,
    ToolSideEffect,
    canonical_descriptor_bytes,
    canonical_schema_bytes,
)
from src.coevo.crypto.contract import ProviderScope


ROOT = Path(__file__).resolve().parents[2]


class CanonicalUnificationTests(unittest.TestCase):
    def test_tool_canonical_functions_match_shared_canon(self) -> None:
        schema = {"type": "object", "properties": {"a": {"type": "string"}}}
        descriptor = {"tool_id": "t.1", "version": "1.0", "中文": "字段"}
        self.assertEqual(
            canonical_json_bytes(schema), canonical_schema_bytes(schema)
        )
        self.assertEqual(
            canonical_json_bytes(descriptor),
            canonical_descriptor_bytes(descriptor),
        )

    def test_memory_record_bytes_match_shared_canon(self) -> None:
        record = MemoryRecord(
            record_id="m.1",
            kind=MemoryKind.EPISODIC,
            project_id="PRJ001",
            occurred_at="2026-08-08T00:00:00Z",
            fields=("f",),
            sensitive_fields=(),
            source_ref="ev.1",
        )
        payload = {
            "kind": record.kind.value,
            "project_id": record.project_id,
            "occurred_at": record.occurred_at,
            "fields": list(record.fields),
            "sensitive_fields": list(record.sensitive_fields),
            "source_ref": record.source_ref,
        }
        self.assertEqual(
            canonical_json_bytes(payload), canonical_record_bytes(record)
        )

    def test_k8s_listing_matches_shared_canon(self) -> None:
        listing_input = ListingInput(
            tools=(
                Tool(
                    tool_id="t.1",
                    tool_version="1.0.0",
                    display_name="test tool",
                    description="test tool description",
                    side_effects=ToolSideEffect.PURE,
                    requires_consent=False,
                    timeout_sec=5,
                    size_in_bytes_max=1024,
                    crypto_scope=ProviderScope.MVP_PROTOTYPE,
                    audit_required=True,
                    input_schema={"type": "object"},
                    output_schema={"type": "object"},
                ),
            ),
            policies=(get_default_profile("INTERACTIVE"),),
            generated_at="2026-08-08T00:00:00Z",
        )
        self.assertEqual(
            canonical_json_bytes(generate_listing_json(listing_input)),
            generate_listing(listing_input),
        )


class CanonicalUnificationGuardTests(unittest.TestCase):
    def test_framework_modules_no_longer_serialize_canonical_inline(self) -> None:
        tools = (ROOT / "src" / "coevo" / "framework" / "tools.py").read_text(
            encoding="utf-8"
        )
        memory = (ROOT / "src" / "coevo" / "framework" / "memory.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("json.dumps(", tools)
        self.assertNotIn("json.dumps(", memory)
        self.assertIn("canonical_json_bytes", tools)
        self.assertIn("canonical_json_bytes", memory)

    def test_plan_keeps_enum_default_semantics(self) -> None:
        source = (ROOT / "src" / "coevo" / "framework" / "plan.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("default=_json_default", source)


if __name__ == "__main__":
    unittest.main()

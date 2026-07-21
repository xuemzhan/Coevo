"""Entry point for the immutable Coevo control archive."""
import runpy
import sys

MODULES = {
    "check_loop_stop": "check_loop_stop",
    "audit_log": "audit_log",
    "audit_seal": "audit_seal",
    "traceability_check": "traceability_check",
    "quality_gate": "quality_gate",
    "validate_opencode": "validate_opencode",
}

if len(sys.argv) < 2 or sys.argv[1] not in MODULES:
    raise SystemExit("usage: control.pyz {check_loop_stop|quality_gate|validate_opencode} [args...]")
name = MODULES[sys.argv.pop(1)]
sys.argv[0] = name
runpy.run_module(name, run_name="__main__", alter_sys=True)

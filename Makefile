PYTHON ?= python
.PHONY: fmt lint test test-security test-e2e quality verify-loop-state env-check
fmt lint test test-security test-e2e quality:
	$(PYTHON) scripts/quality_gate.py --target $@
verify-loop-state:
	$(PYTHON) scripts/check_loop_stop.py
env-check:
	$(PYTHON) scripts/validate_opencode.py --require-tools
# No bootstrap target: dependencies must be approved, imported offline and pinned.

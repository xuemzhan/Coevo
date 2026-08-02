"""Offline Coevo demo composition root (MVP closed loop).

This is the application-level wiring the MVP previously lacked: it
composes the pure facades into one runnable offline pipeline:

1. ensure the locked GmSSL test PKI profile exists;
2. run the real five-step orchestration chain (US-1/2/3 + human confirm
   + US-5 package build) against a real encrypted ``.agent`` package;
3. export the encrypted package to an outbox and verify it by parsing,
   decrypting and verifying the signature;
4. snapshot cockpit workspace/role views and (optionally) start the
   local HTTP cockpit;
5. aggregate a knowledge bundle and persist it into a fresh
   ``KnowledgeStore``;
6. publish audit events over an ``AuditStreamHub``.

Demo-only pieces (clearly non-production):
* :class:`DemoSigner` / :class:`DemoFreshnessAuthority` -- in-memory
  stand-ins for the audit anchor signer/freshness authority; production
  uses the Windows CNG-backed implementations and an approved
  private-key handle.
* The GmSSL 3.2.0 prototype provider is used under its locked
  ``mvp-prototype`` scope, never as an approved product."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import subprocess
import sys
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from src.coevo.identity.audit_anchor import AuditAnchorError, canonical

from .demo_support import (DEMO_ACTOR, DEMO_PROFILE, DEMO_REVISION, DemoFreshnessAuthority, DemoSigner, ROOT, _DemoAuditAnchorError, ensure_demo_profile, now_utc_iso_z, sample_project_input)

from .pipeline import (DemoResult, run_demo_pipeline)

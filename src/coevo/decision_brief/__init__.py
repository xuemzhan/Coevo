"""Secure US-13 decision-brief draft boundary.

Candidate risks become usable only after an owner-key confirmation binds them
to the latest verified merge receipt and its frozen snapshot.  Drafts and
revisions are stored through an authoritative CAS repository.  WPS requests
refer only to re-verified, macro-free templates under a controlled root."""

from __future__ import annotations

import datetime as dt
import enum
import hashlib
import json
import os
import stat
import zipfile
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from threading import Lock
from src.coevo.merge.receipt import MergeCommitReceipt, ReceiptSigningAuthority
from src.coevo.merge.repository import MergeReceiptRepository
from src.coevo.risk import Risk, RiskKind, RiskReport, SourceKind

from .models import (ApprovedTemplate, BRIEF_DOMAIN, BRIEF_SCHEMA, BriefConclusion, BriefContent, BriefSourceKind, BriefType, BriefVersion, DecisionBrief, DecisionBriefConflictError, DecisionBriefError, DecisionBriefValidationError, HIGH_RISK_MIN_SEVERITY, MAX_AFFECTED_TASKS_PER_RISK, MAX_BRIEF_CONTENT_BYTES, MAX_CONCLUSIONS_PER_SECTION, MAX_RISK_COUNT, MAX_RISK_REPORT_BYTES, MAX_RISK_STRING_BYTES, MAX_SOURCES_PER_CONCLUSION, MAX_TEMPLATE_BYTES, MAX_TEMPLATE_UNCOMPRESSED_BYTES, MAX_TEMPLATE_ZIP_ENTRIES, RISK_CONFIRMATION_DOMAIN, RiskConfirmation, SourceReference, WPS_TOOL_ID, WpsDocumentRequest, _REPARSE_POINT, _ZERO_DIGEST, _brief_id, _build_content, _clone_brief, _clone_confirmation, _clone_content, _clone_risk_report, _content_digest, _content_plain, _content_sources, _digest, _encode_json, _is_link_or_reparse, _latest_receipt, _make_version, _parse_utc, _risk_conclusion, _risk_digest, _safe_string, _source_sort_key, _stable_sources, _stat_is_reparse, _validate_bound_risk, _validate_content_model, _validate_docx, _validate_risk_report, _validate_stored_brief, _validate_template_ref, _version_digest, _version_digest_values)

from .repositories import (ApprovedTemplateRegistry, DecisionBriefRepository, RiskConfirmationRepository)

from .service import (DecisionBriefService)

__all__ = [
    "BRIEF_DOMAIN",
    "BRIEF_SCHEMA",
    "HIGH_RISK_MIN_SEVERITY",
    "MAX_AFFECTED_TASKS_PER_RISK",
    "MAX_BRIEF_CONTENT_BYTES",
    "MAX_CONCLUSIONS_PER_SECTION",
    "MAX_RISK_COUNT",
    "MAX_RISK_REPORT_BYTES",
    "MAX_RISK_STRING_BYTES",
    "MAX_SOURCES_PER_CONCLUSION",
    "MAX_TEMPLATE_BYTES",
    "MAX_TEMPLATE_ZIP_ENTRIES",
    "WPS_TOOL_ID",
    "ApprovedTemplate",
    "ApprovedTemplateRegistry",
    "BriefConclusion",
    "BriefContent",
    "BriefSourceKind",
    "BriefType",
    "BriefVersion",
    "DecisionBrief",
    "DecisionBriefConflictError",
    "DecisionBriefError",
    "DecisionBriefRepository",
    "DecisionBriefService",
    "DecisionBriefValidationError",
    "RiskConfirmation",
    "RiskConfirmationRepository",
    "SourceReference",
    "WpsDocumentRequest",
]

"""Secure US-13 decision-brief draft boundary.

Candidate risks become usable only after an owner-key confirmation binds them
to the latest verified merge receipt and its frozen snapshot.  Drafts and
revisions are stored through an authoritative CAS repository.  WPS requests
refer only to re-verified, macro-free templates under a controlled root."""

from __future__ import annotations

from .models import (ApprovedTemplate, BRIEF_DOMAIN, BRIEF_SCHEMA, BriefConclusion, BriefContent, BriefSourceKind, BriefType, BriefVersion, DecisionBrief, DecisionBriefConflictError, DecisionBriefError, DecisionBriefValidationError, HIGH_RISK_MIN_SEVERITY, MAX_AFFECTED_TASKS_PER_RISK, MAX_BRIEF_CONTENT_BYTES, MAX_CONCLUSIONS_PER_SECTION, MAX_RISK_COUNT, MAX_RISK_REPORT_BYTES, MAX_RISK_STRING_BYTES, MAX_SOURCES_PER_CONCLUSION, MAX_TEMPLATE_BYTES, MAX_TEMPLATE_UNCOMPRESSED_BYTES, MAX_TEMPLATE_ZIP_ENTRIES, RISK_CONFIRMATION_DOMAIN, RiskConfirmation, SourceReference, WPS_TOOL_ID, WpsDocumentRequest)

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

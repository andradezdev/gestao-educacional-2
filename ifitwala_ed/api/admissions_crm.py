# ifitwala_ed/api/admissions_crm.py

from __future__ import annotations

from importlib import import_module

from ifitwala_ed.admission.api.crm.endpoints import (
    archive_inquiry_from_inbox,
    assign_admission_conversation,
    assign_inquiry_from_inbox,
    confirm_admission_external_identity,
    create_admissions_intake,
    create_inquiry_from_admission_conversation,
    invite_inquiry_to_apply_from_inbox,
    link_admission_conversation,
    log_admission_message,
    mark_inquiry_contacted_from_inbox,
    qualify_inquiry_from_inbox,
    record_admission_crm_activity,
    update_admission_conversation_status,
)

_COMPAT_EXPORTS = {
    "IDEMPOTENCY_TTL_SECONDS": "ifitwala_ed.admission.api.crm.idempotency",
    "_cache": "ifitwala_ed.admission.api.crm.idempotency",
    "_cache_key": "ifitwala_ed.admission.api.crm.idempotency",
    "_lock_key": "ifitwala_ed.admission.api.crm.idempotency",
    "_idempotency_key": "ifitwala_ed.admission.api.crm.idempotency",
    "_run_idempotent": "ifitwala_ed.admission.api.crm.idempotency",
    "_require_doc_read": "ifitwala_ed.admission.api.crm.guards",
    "_assert_scope_allowed": "ifitwala_ed.admission.api.crm.guards",
    "_require_conversation_write": "ifitwala_ed.admission.api.crm.guards",
    "_require_inquiry_write": "ifitwala_ed.admission.api.crm.guards",
    "_validate_crm_assignee": "ifitwala_ed.admission.api.crm.guards",
    "_conversation_summary": "ifitwala_ed.admission.api.crm.summaries",
    "_message_summary": "ifitwala_ed.admission.api.crm.summaries",
    "_activity_summary": "ifitwala_ed.admission.api.crm.summaries",
    "_inquiry_summary": "ifitwala_ed.admission.api.crm.summaries",
    "_applicant_summary": "ifitwala_ed.admission.api.crm.summaries",
    "_apply_identity_defaults": "ifitwala_ed.admission.api.crm.conversations",
    "_candidate_conversation": "ifitwala_ed.admission.api.crm.conversations",
    "_resolve_or_create_conversation": "ifitwala_ed.admission.api.crm.conversations",
    "_valid_inquiry_option": "ifitwala_ed.admission.api.crm.intake",
    "_valid_activity_option": "ifitwala_ed.admission.api.crm.intake",
    "_source_from_channel": "ifitwala_ed.admission.api.crm.intake",
    "_name_parts": "ifitwala_ed.admission.api.crm.intake",
    "_append_if_clean": "ifitwala_ed.admission.api.crm.intake",
    "_inquiry_payload_for_intake": "ifitwala_ed.admission.api.crm.intake",
    "_log_admission_message": "ifitwala_ed.admission.api.crm.messages",
}


def __getattr__(name: str):
    module_name = _COMPAT_EXPORTS.get(name)
    if not module_name:
        raise AttributeError(name)
    return getattr(import_module(module_name), name)


__all__ = [
    "log_admission_message",
    "record_admission_crm_activity",
    "link_admission_conversation",
    "confirm_admission_external_identity",
    "create_admissions_intake",
    "assign_admission_conversation",
    "update_admission_conversation_status",
    "create_inquiry_from_admission_conversation",
    "assign_inquiry_from_inbox",
    "archive_inquiry_from_inbox",
    "mark_inquiry_contacted_from_inbox",
    "qualify_inquiry_from_inbox",
    "invite_inquiry_to_apply_from_inbox",
]

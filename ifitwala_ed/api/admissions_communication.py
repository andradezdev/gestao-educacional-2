# ifitwala_ed/api/admissions_communication.py

from __future__ import annotations

from importlib import import_module

from ifitwala_ed.admission.api.communication.endpoints import (
    get_admissions_case_thread,
    mark_admissions_case_thread_read,
    send_admissions_case_message,
)

_COMPAT_EXPORTS = {
    "ADMISSIONS_APPLICANT_ROLE": "ifitwala_ed.admission.api.communication.constants",
    "ADMISSIONS_FAMILY_ROLE": "ifitwala_ed.admission.api.communication.constants",
    "ALLOWED_STAFF_ROLES": "ifitwala_ed.admission.api.communication.constants",
    "SUPPORTED_CONTEXT_DOCTYPES": "ifitwala_ed.admission.api.communication.constants",
    "MESSAGE_LIMIT": "ifitwala_ed.admission.api.communication.constants",
    "THREAD_COMMUNICATION_TYPE": "ifitwala_ed.admission.api.communication.constants",
    "THREAD_INTERACTION_MODE": "ifitwala_ed.admission.api.communication.constants",
    "THREAD_STATUS": "ifitwala_ed.admission.api.communication.constants",
    "THREAD_PORTAL_SURFACE": "ifitwala_ed.admission.api.communication.constants",
    "INVALID_SESSION_USERS": "ifitwala_ed.admission.api.communication.constants",
    "READ_RECEIPT_REFERENCE_DOCTYPE": "ifitwala_ed.admission.api.communication.constants",
    "_LOCAL_ATTRS_RESET_BY_SET_USER": "ifitwala_ed.admission.api.communication.constants",
    "_MISSING_LOCAL_ATTR": "ifitwala_ed.admission.api.communication.constants",
    "_to_text": "ifitwala_ed.admission.api.communication.context",
    "_snapshot_request_session": "ifitwala_ed.admission.api.communication.admin_context",
    "_restore_request_session": "ifitwala_ed.admission.api.communication.admin_context",
    "_administrator_context_preserving_request_session": "ifitwala_ed.admission.api.communication.admin_context",
    "_session_user": "ifitwala_ed.admission.api.communication.context",
    "_normalize_context": "ifitwala_ed.admission.api.communication.context",
    "_safe_datetime": "ifitwala_ed.admission.api.communication.context",
    "_next_thread_title": "ifitwala_ed.admission.api.communication.threads",
    "_resolve_student_applicant_row": "ifitwala_ed.admission.api.communication.context",
    "_require_actor_context": "ifitwala_ed.admission.api.communication.context",
    "_get_thread_name": "ifitwala_ed.admission.api.communication.threads",
    "_create_thread": "ifitwala_ed.admission.api.communication.threads",
    "_get_or_create_thread": "ifitwala_ed.admission.api.communication.threads",
    "_sender_direction": "ifitwala_ed.admission.api.communication.messages",
    "_truncate_preview": "ifitwala_ed.admission.api.communication.messages",
    "_fetch_latest_entry_for_sender": "ifitwala_ed.admission.api.communication.messages",
    "_save_case_interaction": "ifitwala_ed.admission.api.communication.messages",
    "_serialize_message_row": "ifitwala_ed.admission.api.communication.messages",
    "_get_read_receipt_time": "ifitwala_ed.admission.api.communication.read_receipts",
    "_count_unread_messages": "ifitwala_ed.admission.api.communication.read_receipts",
    "_ensure_applicant_match": "ifitwala_ed.admission.api.communication.context",
    "get_admissions_thread_summaries_for_applicants": "ifitwala_ed.admission.api.communication.summaries",
    "create_interaction_entry": "ifitwala_ed.api.org_communication_interactions",
    "get_latest_org_communication_entry_for_user": "ifitwala_ed.api.org_communication_interactions",
    "upsert_org_communication_read_receipt": "ifitwala_ed.api.org_communication_interactions",
    "ENTRY_DOCTYPE": "ifitwala_ed.setup.doctype.communication_interaction_entry.communication_interaction_entry",
}


def __getattr__(name: str):
    module_name = _COMPAT_EXPORTS.get(name)
    if not module_name:
        raise AttributeError(name)
    return getattr(import_module(module_name), name)


__all__ = [
    "send_admissions_case_message",
    "get_admissions_case_thread",
    "mark_admissions_case_thread_read",
]

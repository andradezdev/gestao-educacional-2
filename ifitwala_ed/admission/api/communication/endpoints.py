# ifitwala_ed/admission/api/communication/endpoints.py

from __future__ import annotations

import frappe


@frappe.whitelist(allow_guest=True)
def send_admissions_case_message(
    *,
    context_doctype: str | None = None,
    context_name: str | None = None,
    body: str | None = None,
    applicant_visible: int | None = 1,
    client_request_id: str | None = None,
):
    from ifitwala_ed.admission.api.communication.messages import send_admissions_case_message_impl

    return send_admissions_case_message_impl(
        context_doctype=context_doctype,
        context_name=context_name,
        body=body,
        applicant_visible=applicant_visible,
        client_request_id=client_request_id,
    )


@frappe.whitelist(allow_guest=True)
def get_admissions_case_thread(
    *,
    context_doctype: str | None = None,
    context_name: str | None = None,
    limit_start: int | None = 0,
    limit: int | None = 60,
):
    from ifitwala_ed.admission.api.communication.messages import get_admissions_case_thread_impl

    return get_admissions_case_thread_impl(
        context_doctype=context_doctype,
        context_name=context_name,
        limit_start=limit_start,
        limit=limit,
    )


@frappe.whitelist(allow_guest=True)
def mark_admissions_case_thread_read(
    *,
    context_doctype: str | None = None,
    context_name: str | None = None,
):
    from ifitwala_ed.admission.api.communication.read_receipts import mark_admissions_case_thread_read_impl

    return mark_admissions_case_thread_read_impl(
        context_doctype=context_doctype,
        context_name=context_name,
    )


send_admissions_case_message.allow_guest = True
get_admissions_case_thread.allow_guest = True
mark_admissions_case_thread_read.allow_guest = True


__all__ = [
    "send_admissions_case_message",
    "get_admissions_case_thread",
    "mark_admissions_case_thread_read",
]

# ifitwala_ed/admission/api/inbox/endpoints.py

from __future__ import annotations

import frappe


@frappe.whitelist()
def get_admissions_inbox_context(
    *,
    organization: str | None = None,
    school: str | None = None,
    limit: int | str | None = None,
) -> dict:
    from ifitwala_ed.admission.api.inbox.context import get_admissions_inbox_context_impl

    return get_admissions_inbox_context_impl(
        organization=organization,
        school=school,
        limit=limit,
    )


@frappe.whitelist()
def search_admissions_inbox_assignees(
    *,
    context_doctype: str | None = None,
    context_name: str | None = None,
    organization: str | None = None,
    school: str | None = None,
    assignment_lane: str | None = None,
    query: str | None = None,
    limit: int | str | None = None,
) -> list[dict]:
    from ifitwala_ed.admission.api.inbox.assignees import search_admissions_inbox_assignees_impl

    return search_admissions_inbox_assignees_impl(
        context_doctype=context_doctype,
        context_name=context_name,
        organization=organization,
        school=school,
        assignment_lane=assignment_lane,
        query=query,
        limit=limit,
    )


__all__ = [
    "get_admissions_inbox_context",
    "search_admissions_inbox_assignees",
]

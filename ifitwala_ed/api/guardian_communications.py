"""Guardian communication center public RPC facade."""

from __future__ import annotations

from typing import Any

import frappe

from ifitwala_ed.students.api import guardian_communications as _impl

RECENT_WINDOW_DAYS = _impl.RECENT_WINDOW_DAYS
SOURCE_FILTERS = _impl.SOURCE_FILTERS
SOURCE_PRIORITY = _impl.SOURCE_PRIORITY


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def get_guardian_communication_center(
    source: str | None = None,
    student: str | None = None,
    start: int = 0,
    page_length: int = 24,
) -> dict[str, Any]:
    return _impl.get_guardian_communication_center(
        source=source,
        student=student,
        start=start,
        page_length=page_length,
    )


def get_guardian_portal_communication_unread_count() -> int:
    return _impl.get_guardian_portal_communication_unread_count()


__all__ = [
    "RECENT_WINDOW_DAYS",
    "SOURCE_FILTERS",
    "SOURCE_PRIORITY",
    "get_guardian_communication_center",
    "get_guardian_portal_communication_unread_count",
]

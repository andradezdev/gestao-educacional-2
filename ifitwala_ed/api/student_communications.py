"""Student communication center public RPC facade."""

from __future__ import annotations

from typing import Any

import frappe

from ifitwala_ed.students.api import student_communications as _impl

RECENT_WINDOW_DAYS = _impl.RECENT_WINDOW_DAYS
SOURCE_FILTERS = _impl.SOURCE_FILTERS


def __getattr__(name: str):
    return getattr(_impl, name)


def get_student_portal_communication_unread_count(student_name: str | None = None) -> int:
    return _impl.get_student_portal_communication_unread_count(student_name=student_name)


def get_student_home_communication_summary(student_name: str) -> dict[str, Any]:
    return _impl.get_student_home_communication_summary(student_name)


def get_student_course_communication_summary(
    student_name: str,
    *,
    course_id: str,
    student_group: str | None = None,
) -> dict[str, Any]:
    return _impl.get_student_course_communication_summary(
        student_name,
        course_id=course_id,
        student_group=student_group,
    )


def get_student_activity_communications(
    student_name: str,
    *,
    activity_program_offering: str | None = None,
    activity_student_group: str | None = None,
    start: int = 0,
    page_length: int = 30,
) -> dict[str, Any]:
    return _impl.get_student_activity_communications(
        student_name,
        activity_program_offering=activity_program_offering,
        activity_student_group=activity_student_group,
        start=start,
        page_length=page_length,
    )


@frappe.whitelist()
def get_student_communication_center(
    source: str | None = None,
    course_id: str | None = None,
    student_group: str | None = None,
    item: str | None = None,
    start: int = 0,
    page_length: int = 24,
) -> dict[str, Any]:
    return _impl.get_student_communication_center(
        source=source,
        course_id=course_id,
        student_group=student_group,
        item=item,
        start=start,
        page_length=page_length,
    )


__all__ = [
    "RECENT_WINDOW_DAYS",
    "SOURCE_FILTERS",
    "get_student_portal_communication_unread_count",
    "get_student_home_communication_summary",
    "get_student_course_communication_summary",
    "get_student_activity_communications",
    "get_student_communication_center",
]

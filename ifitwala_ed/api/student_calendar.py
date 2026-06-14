"""Student Calendar public RPC facade."""

from __future__ import annotations

from typing import Optional

import frappe

from ifitwala_ed.students.api import student_calendar as _impl

CACHE_TTL = _impl.CACHE_TTL
STUDENT_CALENDAR_INVALIDATE_EVENT = _impl.STUDENT_CALENDAR_INVALIDATE_EVENT


def __getattr__(name: str):
    return getattr(_impl, name)


def invalidate_student_calendar_cache(
    *,
    student: str | None = None,
    user: str | None = None,
    users: list[str] | None = None,
) -> None:
    return _impl.invalidate_student_calendar_cache(student=student, user=user, users=users)


def refresh_student_calendar_views(
    *,
    student: str | None = None,
    user: str | None = None,
    users: list[str] | None = None,
    source: str | None = None,
    source_name: str | None = None,
) -> None:
    return _impl.refresh_student_calendar_views(
        student=student,
        user=user,
        users=users,
        source=source,
        source_name=source_name,
    )


@frappe.whitelist()
def get_student_calendar(
    from_datetime: Optional[str] = None,
    to_datetime: Optional[str] = None,
    force_refresh: bool = False,
):
    return _impl.get_student_calendar(
        from_datetime=from_datetime,
        to_datetime=to_datetime,
        force_refresh=force_refresh,
    )


__all__ = [
    "CACHE_TTL",
    "STUDENT_CALENDAR_INVALIDATE_EVENT",
    "invalidate_student_calendar_cache",
    "refresh_student_calendar_views",
    "get_student_calendar",
]

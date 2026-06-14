"""Guardian monitoring public RPC facade."""

from __future__ import annotations

from typing import Any

import frappe

from ifitwala_ed.students.api import guardian_monitoring as _impl

DEFAULT_PAGE_LENGTH = _impl.DEFAULT_PAGE_LENGTH

_resolve_monitoring_context = _impl._resolve_monitoring_context
_coerce_days = _impl._coerce_days
_coerce_start = _impl._coerce_start
_coerce_page_length = _impl._coerce_page_length
_coerce_prioritize_unread = _impl._coerce_prioritize_unread
_plain_guardian_log_text = _impl._plain_guardian_log_text
_empty_page = _impl._empty_page
_serialize_page = _impl._serialize_page
_count_monitoring_logs = _impl._count_monitoring_logs
_get_monitoring_logs = _impl._get_monitoring_logs
_get_monitoring_logs_page = _impl._get_monitoring_logs_page
_get_monitoring_results = _impl._get_monitoring_results
_get_monitoring_results_page = _impl._get_monitoring_results_page


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def get_guardian_monitoring_snapshot(
    student: str | None = None,
    days: int | str = 30,
    page_length: int | str = DEFAULT_PAGE_LENGTH,
    prioritize_unread: bool | int | str | None = None,
) -> dict[str, Any]:
    return _impl.get_guardian_monitoring_snapshot(
        student=student,
        days=days,
        page_length=page_length,
        prioritize_unread=prioritize_unread,
    )


@frappe.whitelist()
def get_guardian_monitoring_student_logs(
    student: str | None = None,
    days: int | str = 30,
    start: int | str = 0,
    page_length: int | str = DEFAULT_PAGE_LENGTH,
    prioritize_unread: bool | int | str | None = None,
) -> dict[str, Any]:
    return _impl.get_guardian_monitoring_student_logs(
        student=student,
        days=days,
        start=start,
        page_length=page_length,
        prioritize_unread=prioritize_unread,
    )


@frappe.whitelist()
def get_guardian_monitoring_published_results(
    student: str | None = None,
    days: int | str = 30,
    start: int | str = 0,
    page_length: int | str = DEFAULT_PAGE_LENGTH,
) -> dict[str, Any]:
    return _impl.get_guardian_monitoring_published_results(
        student=student,
        days=days,
        start=start,
        page_length=page_length,
    )


@frappe.whitelist()
def mark_guardian_student_log_read(log_name: str) -> dict[str, Any]:
    return _impl.mark_guardian_student_log_read(log_name=log_name)


__all__ = [
    "DEFAULT_PAGE_LENGTH",
    "get_guardian_monitoring_snapshot",
    "get_guardian_monitoring_student_logs",
    "get_guardian_monitoring_published_results",
    "mark_guardian_student_log_read",
    "_resolve_monitoring_context",
    "_coerce_days",
    "_coerce_start",
    "_coerce_page_length",
    "_coerce_prioritize_unread",
    "_plain_guardian_log_text",
    "_empty_page",
    "_serialize_page",
    "_count_monitoring_logs",
    "_get_monitoring_logs",
    "_get_monitoring_logs_page",
    "_get_monitoring_results",
    "_get_monitoring_results_page",
]

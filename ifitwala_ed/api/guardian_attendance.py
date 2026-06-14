"""Guardian attendance public RPC facade."""

from __future__ import annotations

import frappe

from ifitwala_ed.students.api import guardian_attendance as _impl

_coerce_days = _impl._coerce_days
_build_attendance_students = _impl._build_attendance_students
_attendance_code_map = _impl._attendance_code_map
_fallback_code_meta = _impl._fallback_code_meta
_detail_sort_key = _impl._detail_sort_key
_resolve_day_state = _impl._resolve_day_state
_public_detail = _impl._public_detail


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def get_guardian_attendance_snapshot(
    student: str | None = None,
    days: int | str = 60,
) -> dict:
    return _impl.get_guardian_attendance_snapshot(student=student, days=days)


__all__ = [
    "get_guardian_attendance_snapshot",
    "_coerce_days",
    "_build_attendance_students",
    "_attendance_code_map",
    "_fallback_code_meta",
    "_detail_sort_key",
    "_resolve_day_state",
    "_public_detail",
]

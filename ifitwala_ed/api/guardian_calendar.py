"""Guardian calendar public RPC facade."""

from __future__ import annotations

from typing import Any

import frappe

from ifitwala_ed.students.api import guardian_calendar as _impl

DEFAULT_HOLIDAY_COLOR = _impl.DEFAULT_HOLIDAY_COLOR
DEFAULT_SCHOOL_EVENT_COLOR = _impl.DEFAULT_SCHOOL_EVENT_COLOR

_serialize_scalar = _impl._serialize_scalar
_coerce_month_start = _impl._coerce_month_start
_month_window = _impl._month_window
_school_filter_options = _impl._school_filter_options
_validate_selected_school = _impl._validate_selected_school
_relevant_students_for_holidays = _impl._relevant_students_for_holidays
_fetch_guardian_holiday_items = _impl._fetch_guardian_holiday_items
_serialize_school_event_items = _impl._serialize_school_event_items
_sort_calendar_items = _impl._sort_calendar_items
_fetch_guardian_school_events = _impl._fetch_guardian_school_events
_ordered_matched_children = _impl._ordered_matched_children
_resolve_guardian_communication_context = _impl._resolve_guardian_communication_context
_validate_selected_student = _impl._validate_selected_student
resolve_school_calendars_for_window = _impl.resolve_school_calendars_for_window
now_datetime = _impl.now_datetime


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def get_guardian_calendar_overlay(
    month_start: str | None = None,
    student: str | None = None,
    school: str | None = None,
    include_holidays: int = 1,
    include_school_events: int = 1,
) -> dict[str, Any]:
    return _impl.get_guardian_calendar_overlay(
        month_start=month_start,
        student=student,
        school=school,
        include_holidays=include_holidays,
        include_school_events=include_school_events,
    )


__all__ = [
    "get_guardian_calendar_overlay",
    "DEFAULT_HOLIDAY_COLOR",
    "DEFAULT_SCHOOL_EVENT_COLOR",
    "_serialize_scalar",
    "_coerce_month_start",
    "_month_window",
    "_school_filter_options",
    "_validate_selected_school",
    "_relevant_students_for_holidays",
    "_fetch_guardian_holiday_items",
    "_serialize_school_event_items",
    "_sort_calendar_items",
]

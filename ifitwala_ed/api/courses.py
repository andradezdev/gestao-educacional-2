from __future__ import annotations

from typing import Any

import frappe

from ifitwala_ed.curriculum.api import courses as _impl

COURSE_PLACEHOLDER = _impl.COURSE_PLACEHOLDER
WORK_BOARD_NOW_LIMIT = _impl.WORK_BOARD_NOW_LIMIT
WORK_BOARD_SOON_LIMIT = _impl.WORK_BOARD_SOON_LIMIT
WORK_BOARD_LATER_LIMIT = _impl.WORK_BOARD_LATER_LIMIT
WORK_BOARD_DONE_LIMIT = _impl.WORK_BOARD_DONE_LIMIT
TIMELINE_HORIZON_DAYS = _impl.TIMELINE_HORIZON_DAYS
NOW_WINDOW_DAYS = _impl.NOW_WINDOW_DAYS
SOON_WINDOW_DAYS = _impl.SOON_WINDOW_DAYS
OPENABLE_LEARNING_SPACE_STATUSES = _impl.OPENABLE_LEARNING_SPACE_STATUSES

_serialize_scalar = _impl._serialize_scalar
_safe_course_image = _impl._safe_course_image
_build_course_href = _impl._build_course_href
_get_student_name_for_user = _impl._get_student_name_for_user
_require_student_name_for_session_user = _impl._require_student_name_for_session_user
_get_academic_years = _impl._get_academic_years
_fetch_enrolled_courses = _impl._fetch_enrolled_courses
_fetch_active_student_groups = _impl._fetch_active_student_groups
_build_student_course_scope = _impl._build_student_course_scope
_student_groups_for_course_year = _impl._student_groups_for_course_year
_fetch_active_class_plan_groups = _impl._fetch_active_class_plan_groups
_fetch_active_course_plan_counts = _impl._fetch_active_course_plan_counts
_serialize_course_learning_space = _impl._serialize_course_learning_space
_attach_course_learning_space_state = _impl._attach_course_learning_space_state
_get_courses_for_year = _impl._get_courses_for_year
_build_student_courses_payload = _impl._build_student_courses_payload
_coerce_datetime = _impl._coerce_datetime
_time_text_to_minutes = _impl._time_text_to_minutes
_extract_class_time_bounds = _impl._extract_class_time_bounds
_build_home_orientation = _impl._build_home_orientation
_fetch_student_hub_task_rows = _impl._fetch_student_hub_task_rows
_is_work_item_done = _impl._is_work_item_done
_build_work_item_href = _impl._build_work_item_href
_build_work_item_status_label = _impl._build_work_item_status_label
_classify_work_item_lane = _impl._classify_work_item_lane
_serialize_work_item = _impl._serialize_work_item
_work_item_sort_key = _impl._work_item_sort_key
_build_work_board_payload = _impl._build_work_board_payload
_task_timeline_item = _impl._task_timeline_item
_class_timeline_item = _impl._class_timeline_item
_build_learning_timeline = _impl._build_learning_timeline


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def get_courses_data(academic_year: str | None = None) -> dict:
    return _impl.get_courses_data(academic_year=academic_year)


@frappe.whitelist()
def get_student_hub_home() -> dict[str, Any]:
    return _impl.get_student_hub_home()


__all__ = [
    "get_courses_data",
    "get_student_hub_home",
    "COURSE_PLACEHOLDER",
    "WORK_BOARD_NOW_LIMIT",
    "WORK_BOARD_SOON_LIMIT",
    "WORK_BOARD_LATER_LIMIT",
    "WORK_BOARD_DONE_LIMIT",
    "TIMELINE_HORIZON_DAYS",
    "NOW_WINDOW_DAYS",
    "SOON_WINDOW_DAYS",
    "OPENABLE_LEARNING_SPACE_STATUSES",
]

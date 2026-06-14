from __future__ import annotations

import frappe

from ifitwala_ed.schedule.api import course_schedule as _impl

COURSE_PLACEHOLDER = _impl.COURSE_PLACEHOLDER
COURSE_SCHEDULE_CACHE_PREFIX = _impl.COURSE_SCHEDULE_CACHE_PREFIX
COURSE_SCHEDULE_TERM_PREFIX = _impl.COURSE_SCHEDULE_TERM_PREFIX
COURSE_SCHEDULE_ROTATION_PREFIX = _impl.COURSE_SCHEDULE_ROTATION_PREFIX
COURSE_SCHEDULE_DEPENDENT_PREFIXES = _impl.COURSE_SCHEDULE_DEPENDENT_PREFIXES
COURSE_SCHEDULE_CACHE_TTL = _impl.COURSE_SCHEDULE_CACHE_TTL
COURSE_SCHEDULE_CACHE_MISS = _impl.COURSE_SCHEDULE_CACHE_MISS
EFFECTIVE_SCHEDULE_AY_PREFIX = _impl.EFFECTIVE_SCHEDULE_AY_PREFIX
EFFECTIVE_SCHEDULE_CALENDAR_PREFIX = _impl.EFFECTIVE_SCHEDULE_CALENDAR_PREFIX
TimeSlot = _impl.TimeSlot

_resolve_current_student = _impl._resolve_current_student
_fetch_student_course_groups = _impl._fetch_student_course_groups
_course_schedule_cache = _impl._course_schedule_cache
_cache_key_for_term = _impl._cache_key_for_term
_cache_key_for_rotation = _impl._cache_key_for_rotation
_cache_shared_value = _impl._cache_shared_value
_get_cached_shared_value = _impl._get_cached_shared_value
_get_term_window = _impl._get_term_window
_within_term = _impl._within_term
_resolve_schedule_name = _impl._resolve_schedule_name
_get_rotation_lookup = _impl._get_rotation_lookup
_rotation_day_for = _impl._rotation_day_for
_delete_cache_prefix = _impl._delete_cache_prefix
_delete_cache_key = _impl._delete_cache_key
_doc_value = _impl._doc_value
_academic_year_for_calendar = _impl._academic_year_for_calendar
_schedule_names_for_calendar = _impl._schedule_names_for_calendar
_calendar_names_for_academic_year = _impl._calendar_names_for_academic_year
_delete_term_window_cache = _impl._delete_term_window_cache
_delete_rotation_caches_for_schedule = _impl._delete_rotation_caches_for_schedule
_delete_rotation_caches_for_calendar = _impl._delete_rotation_caches_for_calendar
_delete_rotation_caches_for_academic_year = _impl._delete_rotation_caches_for_academic_year
_delete_effective_schedule_caches_for_calendar = _impl._delete_effective_schedule_caches_for_calendar
_delete_effective_schedule_caches_for_academic_year = _impl._delete_effective_schedule_caches_for_academic_year
_time_to_str = _impl._time_to_str
_time_to_minutes = _impl._time_to_minutes
_safe_image = _impl._safe_image
_collect_instructors = _impl._collect_instructors


def __getattr__(name: str):
    return getattr(_impl, name)


def invalidate_course_schedule_cache(doc=None, method=None):
    return _impl.invalidate_course_schedule_cache(doc=doc, method=method)


@frappe.whitelist()
def get_today_courses() -> dict:
    return _impl.get_today_courses()


__all__ = [
    "get_today_courses",
    "invalidate_course_schedule_cache",
    "COURSE_PLACEHOLDER",
    "COURSE_SCHEDULE_CACHE_PREFIX",
    "COURSE_SCHEDULE_TERM_PREFIX",
    "COURSE_SCHEDULE_ROTATION_PREFIX",
    "COURSE_SCHEDULE_DEPENDENT_PREFIXES",
    "COURSE_SCHEDULE_CACHE_TTL",
    "COURSE_SCHEDULE_CACHE_MISS",
    "EFFECTIVE_SCHEDULE_AY_PREFIX",
    "EFFECTIVE_SCHEDULE_CALENDAR_PREFIX",
    "TimeSlot",
]

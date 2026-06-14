from __future__ import annotations

import frappe

from ifitwala_ed.students.api import student_demographics_dashboard as _impl

ALLOWED_ANALYTICS_ROLES = _impl.ALLOWED_ANALYTICS_ROLES
SYSTEM_WIDE_ANALYTICS_ROLES = _impl.SYSTEM_WIDE_ANALYTICS_ROLES
MIN_DEMOGRAPHIC_CELL_COUNT = _impl.MIN_DEMOGRAPHIC_CELL_COUNT
SUPPRESSED_BUCKET_LABEL = _impl.SUPPRESSED_BUCKET_LABEL
SUPPRESSED_SERIES_KEY = _impl.SUPPRESSED_SERIES_KEY

_is_system_wide_analytics_user = _impl._is_system_wide_analytics_user
_ensure_demographics_access = _impl._ensure_demographics_access
_get_demographics_access_context = _impl._get_demographics_access_context
_safe_percent = _impl._safe_percent
_suppressed_counter_items = _impl._suppressed_counter_items
_suppressed_fixed_values = _impl._suppressed_fixed_values
_suppressed_residency_kpi_counts = _impl._suppressed_residency_kpi_counts
_normalize_filter_value = _impl._normalize_filter_value
_get_filters = _impl._get_filters
_context_school_scope = _impl._context_school_scope
_requested_school_scope = _impl._requested_school_scope
_get_active_students = _impl._get_active_students
_get_guardian_links = _impl._get_guardian_links
_calculate_age = _impl._calculate_age
_bucket_age = _impl._bucket_age
_build_family_groups = _impl._build_family_groups
_empty_dashboard = _impl._empty_dashboard


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def get_filter_meta():
    return _impl.get_filter_meta()


@frappe.whitelist()
def get_dashboard(filters=None):
    return _impl.get_dashboard(filters=filters)


@frappe.whitelist()
def get_slice_entities(slice_key: str | None = None, filters=None, start: int = 0, page_length: int = 50):
    return _impl.get_slice_entities(
        slice_key=slice_key,
        filters=filters,
        start=start,
        page_length=page_length,
    )


__all__ = [
    "get_filter_meta",
    "get_dashboard",
    "get_slice_entities",
    "ALLOWED_ANALYTICS_ROLES",
    "SYSTEM_WIDE_ANALYTICS_ROLES",
    "MIN_DEMOGRAPHIC_CELL_COUNT",
    "SUPPRESSED_BUCKET_LABEL",
    "SUPPRESSED_SERIES_KEY",
]

# Copyright (c) 2025, François de Ryckel and contributors
# For license information, please see license.txt

"""Student Log dashboard public RPC facade."""

from __future__ import annotations

import frappe

from ifitwala_ed.students.api import student_log_dashboard as _impl

ALLOWED_ANALYTICS_ROLES = _impl.ALLOWED_ANALYTICS_ROLES
FOLLOW_UP_DOCTYPE = _impl.FOLLOW_UP_DOCTYPE
FILTER_META_CACHE_TTL_SECONDS = _impl.FILTER_META_CACHE_TTL_SECONDS


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def get_dashboard_data(filters=None):
    return _impl.get_dashboard_data(filters=filters)


@frappe.whitelist()
def get_distinct_students(filters=None, search_text: str = ""):
    return _impl.get_distinct_students(filters=filters, search_text=search_text)


@frappe.whitelist()
def get_recent_logs(filters=None, start: int = 0, page_length: int = 25):
    return _impl.get_recent_logs(filters=filters, start=start, page_length=page_length)


def get_authorized_schools(user):
    return _impl.get_authorized_schools(user)


@frappe.whitelist()
def get_filter_meta():
    return _impl.get_filter_meta()


__all__ = [
    "ALLOWED_ANALYTICS_ROLES",
    "FOLLOW_UP_DOCTYPE",
    "FILTER_META_CACHE_TTL_SECONDS",
    "get_dashboard_data",
    "get_distinct_students",
    "get_recent_logs",
    "get_authorized_schools",
    "get_filter_meta",
]

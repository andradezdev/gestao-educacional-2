"""Student Groups public RPC facade."""

from __future__ import annotations

import frappe

from ifitwala_ed.students.api import student_groups as _impl

TRIAGE_ROLES = _impl.TRIAGE_ROLES
INSTRUCTOR_SCOPE_OVERRIDE_ROLES = _impl.INSTRUCTOR_SCOPE_OVERRIDE_ROLES


def __getattr__(name: str):
    return getattr(_impl, name)


def _user_roles(user: str) -> set[str]:
    return _impl._user_roles(user)


def _instructor_group_names(user: str) -> set[str]:
    return _impl._instructor_group_names(user)


def _base_group_filters(program=None, course=None, cohort=None) -> dict:
    return _impl._base_group_filters(program=program, course=course, cohort=cohort)


def _has_broad_group_access(roles: set[str]) -> bool:
    return _impl._has_broad_group_access(roles)


@frappe.whitelist()
def fetch_groups(program=None, course=None, cohort=None):
    return _impl.fetch_groups(program=program, course=course, cohort=cohort)


@frappe.whitelist()
def fetch_group_students(student_group: str, start: int = 0, page_length: int = 25):
    return _impl.fetch_group_students(student_group=student_group, start=start, page_length=page_length)


__all__ = [
    "TRIAGE_ROLES",
    "INSTRUCTOR_SCOPE_OVERRIDE_ROLES",
    "_user_roles",
    "_instructor_group_names",
    "_base_group_filters",
    "_has_broad_group_access",
    "fetch_groups",
    "fetch_group_students",
]

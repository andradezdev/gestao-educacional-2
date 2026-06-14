"""Staff attendance tool public RPC facade."""

from __future__ import annotations

import frappe

from ifitwala_ed.students.api import student_attendance as _impl

PORTAL_FULL_ACCESS_ROLES = _impl.PORTAL_FULL_ACCESS_ROLES
PORTAL_GROUP_FIELDS = _impl.PORTAL_GROUP_FIELDS
ATTENDANCE_CONTEXT_TTL = _impl.ATTENDANCE_CONTEXT_TTL


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def fetch_portal_student_groups(school: str | None = None, program: str | None = None):
    return _impl.fetch_portal_student_groups(school=school, program=program)


@frappe.whitelist()
def fetch_school_filter_context():
    return _impl.fetch_school_filter_context()


@frappe.whitelist()
def fetch_active_programs(school: str | None = None):
    return _impl.fetch_active_programs(school=school)


@frappe.whitelist()
def fetch_attendance_ledger_context(
    school: str | None = None,
    program: str | None = None,
    academic_year: str | None = None,
    term: str | None = None,
    student_group: str | None = None,
):
    return _impl.fetch_attendance_ledger_context(
        school=school,
        program=program,
        academic_year=academic_year,
        term=term,
        student_group=student_group,
    )


@frappe.whitelist()
def fetch_attendance_tool_bootstrap(
    school: str | None = None,
    program: str | None = None,
    student_group: str | None = None,
):
    return _impl.fetch_attendance_tool_bootstrap(
        school=school,
        program=program,
        student_group=student_group,
    )


@frappe.whitelist()
def fetch_attendance_tool_group_context(student_group: str):
    return _impl.fetch_attendance_tool_group_context(student_group=student_group)


@frappe.whitelist()
def fetch_attendance_tool_roster_context(student_group: str, attendance_date: str):
    return _impl.fetch_attendance_tool_roster_context(student_group=student_group, attendance_date=attendance_date)


@frappe.whitelist()
def fetch_portal_academic_years(school: str | None = None):
    return _impl.fetch_portal_academic_years(school=school)


@frappe.whitelist()
def fetch_portal_terms(academic_year: str | None = None, school: str | None = None):
    return _impl.fetch_portal_terms(academic_year=academic_year, school=school)


@frappe.whitelist()
def get_weekend_days(student_group: str | None = None) -> list[int]:
    return _impl.get_weekend_days(student_group=student_group)


__all__ = [
    "PORTAL_FULL_ACCESS_ROLES",
    "PORTAL_GROUP_FIELDS",
    "ATTENDANCE_CONTEXT_TTL",
    "fetch_portal_student_groups",
    "fetch_school_filter_context",
    "fetch_active_programs",
    "fetch_attendance_ledger_context",
    "fetch_attendance_tool_bootstrap",
    "fetch_attendance_tool_group_context",
    "fetch_attendance_tool_roster_context",
    "fetch_portal_academic_years",
    "fetch_portal_terms",
    "get_weekend_days",
]

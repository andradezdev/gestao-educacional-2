# Copyright (c) 2025, François de Ryckel and contributors
# For license information, please see license.txt

"""Student Log public RPC facade."""

from __future__ import annotations

import frappe

from ifitwala_ed.students.api import student_log as _impl

LOG_DOCTYPE = _impl.LOG_DOCTYPE
PAGE_LENGTH_DEFAULT = _impl.PAGE_LENGTH_DEFAULT


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def get_student_logs(start: int = 0, page_length: int = PAGE_LENGTH_DEFAULT):
    return _impl.get_student_logs(start=start, page_length=page_length)


@frappe.whitelist()
def get_student_log_detail(log_name: str):
    return _impl.get_student_log_detail(log_name=log_name)


@frappe.whitelist()
def mark_student_log_read(log_name: str):
    return _impl.mark_student_log_read(log_name=log_name)


@frappe.whitelist()
def search_students(**payload):
    return _impl.search_students(**payload)


@frappe.whitelist()
def search_follow_up_users(**payload):
    return _impl.search_follow_up_users(**payload)


@frappe.whitelist()
def get_form_options(**payload):
    return _impl.get_form_options(**payload)


@frappe.whitelist()
def submit_student_log(**payload):
    return _impl.submit_student_log(**payload)


__all__ = [
    "LOG_DOCTYPE",
    "PAGE_LENGTH_DEFAULT",
    "get_student_logs",
    "get_student_log_detail",
    "mark_student_log_read",
    "search_students",
    "search_follow_up_users",
    "get_form_options",
    "submit_student_log",
]

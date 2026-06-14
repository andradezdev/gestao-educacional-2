# Copyright (c) 2026, François de Ryckel and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe

from ifitwala_ed.assessment.api import quiz as _impl


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def list_question_banks(course: str | None = None):
    return _impl.list_question_banks(course=course)


@frappe.whitelist()
def save_question_bank(payload=None, **kwargs):
    return _impl.save_question_bank(payload=payload, **kwargs)


@frappe.whitelist()
def open_session(task_delivery: str):
    return _impl.open_session(task_delivery=task_delivery)


@frappe.whitelist()
def save_attempt(payload=None, **kwargs):
    return _impl.save_attempt(payload=payload, **kwargs)


@frappe.whitelist()
def submit_attempt(payload=None, **kwargs):
    return _impl.submit_attempt(payload=payload, **kwargs)


__all__ = [
    "list_question_banks",
    "save_question_bank",
    "open_session",
    "save_attempt",
    "submit_attempt",
]

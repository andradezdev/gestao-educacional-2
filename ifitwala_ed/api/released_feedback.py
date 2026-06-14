# Copyright (c) 2026, François de Ryckel and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe

from ifitwala_ed.assessment.api import released_feedback as _impl


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def get_student_released_feedback_detail(outcome_id: str):
    return _impl.get_student_released_feedback_detail(outcome_id=outcome_id)


@frappe.whitelist()
def get_guardian_released_feedback_detail(outcome_id: str):
    return _impl.get_guardian_released_feedback_detail(outcome_id=outcome_id)


@frappe.whitelist()
def save_student_feedback_reply(payload=None, **kwargs):
    return _impl.save_student_feedback_reply(payload=payload, **kwargs)


@frappe.whitelist()
def save_student_feedback_thread_state(payload=None, **kwargs):
    return _impl.save_student_feedback_thread_state(payload=payload, **kwargs)


@frappe.whitelist()
def export_student_released_feedback_pdf(outcome_id: str):
    return _impl.export_student_released_feedback_pdf(outcome_id=outcome_id)


__all__ = [
    "get_student_released_feedback_detail",
    "get_guardian_released_feedback_detail",
    "save_student_feedback_reply",
    "save_student_feedback_thread_state",
    "export_student_released_feedback_pdf",
]

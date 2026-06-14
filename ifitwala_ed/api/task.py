# Copyright (c) 2026, François de Ryckel and contributors
# For license information, please see license.txt

# ifitwala_ed/api/task.py

from __future__ import annotations

import frappe

from ifitwala_ed.assessment.api import task as _impl


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def search_tasks(filters=None, query=None, limit=20, start=0):
    return _impl.search_tasks(filters=filters, query=query, limit=limit, start=start)


@frappe.whitelist()
def search_reusable_tasks(student_group=None, course=None, unit_plan=None, query=None, scope=None, limit=20, start=0):
    return _impl.search_reusable_tasks(
        student_group=student_group,
        course=course,
        unit_plan=unit_plan,
        query=query,
        scope=scope,
        limit=limit,
        start=start,
    )


@frappe.whitelist()
def get_task_for_delivery(task, student_group=None, course=None):
    return _impl.get_task_for_delivery(task=task, student_group=student_group, course=course)


@frappe.whitelist()
def list_course_assessment_criteria(student_group=None, course=None):
    return _impl.list_course_assessment_criteria(student_group=student_group, course=course)


@frappe.whitelist()
def get_assessment_setup_for_delivery(student_group=None, course=None):
    return _impl.get_assessment_setup_for_delivery(student_group=student_group, course=course)


@frappe.whitelist()
def create_task_delivery(payload):
    return _impl.create_task_delivery(payload=payload)


__all__ = [
    "search_tasks",
    "search_reusable_tasks",
    "get_task_for_delivery",
    "list_course_assessment_criteria",
    "get_assessment_setup_for_delivery",
    "create_task_delivery",
]

from __future__ import annotations

from typing import Any

import frappe

from ifitwala_ed.students.api import student_log_attachments as _impl


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def get_student_log_attachments(
    student_log: str | None = None,
    audience: str | None = None,
) -> dict[str, Any]:
    return _impl.get_student_log_attachments(student_log=student_log, audience=audience)


@frappe.whitelist()
def upload_student_log_evidence_attachment(
    student_log: str | None = None,
    row_name: str | None = None,
    title: str | None = None,
    description: str | None = None,
    visible_to_student: Any = None,
    visible_to_guardians: Any = None,
    **kwargs,
) -> dict[str, Any]:
    return _impl.upload_student_log_evidence_attachment(
        student_log=student_log,
        row_name=row_name,
        title=title,
        description=description,
        visible_to_student=visible_to_student,
        visible_to_guardians=visible_to_guardians,
        **kwargs,
    )


@frappe.whitelist()
def add_student_log_evidence_link(
    student_log: str | None = None,
    external_url: str | None = None,
    title: str | None = None,
    description: str | None = None,
    visible_to_student: Any = 0,
    visible_to_guardians: Any = 0,
) -> dict[str, Any]:
    return _impl.add_student_log_evidence_link(
        student_log=student_log,
        external_url=external_url,
        title=title,
        description=description,
        visible_to_student=visible_to_student,
        visible_to_guardians=visible_to_guardians,
    )


@frappe.whitelist()
def remove_student_log_evidence_attachment(
    student_log: str | None = None,
    row_name: str | None = None,
) -> dict[str, Any]:
    return _impl.remove_student_log_evidence_attachment(student_log=student_log, row_name=row_name)


__all__ = [
    "get_student_log_attachments",
    "upload_student_log_evidence_attachment",
    "add_student_log_evidence_link",
    "remove_student_log_evidence_attachment",
]

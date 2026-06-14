from __future__ import annotations

from datetime import datetime
from typing import Any

from ifitwala_ed.assessment.api import student_task_status as _impl

DONE_SUBMISSION_STATUSES = _impl.DONE_SUBMISSION_STATUSES
DONE_GRADING_STATUSES = _impl.DONE_GRADING_STATUSES


def __getattr__(name: str):
    return getattr(_impl, name)


def coerce_bool_flag(value: Any) -> bool:
    return _impl.coerce_bool_flag(value)


def is_student_work_done(row: dict[str, Any]) -> bool:
    return _impl.is_student_work_done(row)


def is_student_quiz_state_actionable(quiz_state: dict[str, Any] | None) -> bool:
    return _impl.is_student_quiz_state_actionable(quiz_state=quiz_state)


def is_student_work_actionable(row: dict[str, Any]) -> bool:
    return _impl.is_student_work_actionable(row)


def build_student_task_status_label(row: dict[str, Any], anchor_dt: datetime) -> str:
    return _impl.build_student_task_status_label(row=row, anchor_dt=anchor_dt)


__all__ = [
    "DONE_SUBMISSION_STATUSES",
    "DONE_GRADING_STATUSES",
    "coerce_bool_flag",
    "is_student_work_done",
    "is_student_quiz_state_actionable",
    "is_student_work_actionable",
    "build_student_task_status_label",
]

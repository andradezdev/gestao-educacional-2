# Copyright (c) 2025, François de Ryckel and contributors
# For license information, please see license.txt

"""Student Log Focus action compatibility facade."""

from __future__ import annotations

from ifitwala_ed.students.api import focus_actions_student_log as _impl


def __getattr__(name: str):
    return getattr(_impl, name)


def submit_student_log_follow_up(
    focus_item_id: str,
    follow_up: str,
    client_request_id: str | None = None,
):
    return _impl.submit_student_log_follow_up(
        focus_item_id=focus_item_id,
        follow_up=follow_up,
        client_request_id=client_request_id,
    )


def review_student_log_outcome(
    focus_item_id: str,
    decision: str,
    follow_up_person: str | None = None,
    client_request_id: str | None = None,
):
    return _impl.review_student_log_outcome(
        focus_item_id=focus_item_id,
        decision=decision,
        follow_up_person=follow_up_person,
        client_request_id=client_request_id,
    )


__all__ = [
    "submit_student_log_follow_up",
    "review_student_log_outcome",
]

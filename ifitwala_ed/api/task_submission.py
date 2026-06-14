# Copyright (c) 2026
# For license information, please see license.txt

from __future__ import annotations

import frappe

from ifitwala_ed.assessment.api import task_submission as _impl


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def create_or_resubmit(payload=None, **kwargs):
    return _impl.create_or_resubmit(payload=payload, **kwargs)


@frappe.whitelist()
def get_latest_submission(outcome_id=None):
    return _impl.get_latest_submission(outcome_id=outcome_id)


__all__ = [
    "create_or_resubmit",
    "get_latest_submission",
]

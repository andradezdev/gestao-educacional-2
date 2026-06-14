# Copyright (c) 2026, François de Ryckel and contributors
# For license information, please see license.txt

from __future__ import annotations

import frappe

from ifitwala_ed.assessment.api import task_completion as _impl


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def mark_assign_only_complete(payload=None, **kwargs):
    return _impl.mark_assign_only_complete(payload=payload, **kwargs)


__all__ = [
    "mark_assign_only_complete",
]

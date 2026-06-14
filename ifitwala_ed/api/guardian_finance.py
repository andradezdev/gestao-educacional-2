"""Guardian finance public RPC facade."""

from __future__ import annotations

import frappe

from ifitwala_ed.students.api import guardian_finance as _impl

_resolve_finance_scope = _impl._resolve_finance_scope
_get_invoice_rows = _impl._get_invoice_rows
_get_payment_rows = _impl._get_payment_rows


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def get_guardian_finance_snapshot() -> dict:
    return _impl.get_guardian_finance_snapshot()


__all__ = [
    "get_guardian_finance_snapshot",
    "_resolve_finance_scope",
    "_get_invoice_rows",
    "_get_payment_rows",
]

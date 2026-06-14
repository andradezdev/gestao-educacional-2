# ifitwala_ed/api/guardian_policy.py

from __future__ import annotations

from typing import Any

import frappe

from ifitwala_ed.governance.api import guardian_policy as _impl

_as_bool = _impl._as_bool
_normalize_signature_name = _impl._normalize_signature_name
_expected_guardian_signature_name = _impl._expected_guardian_signature_name
_guardian_has_primary_signer_authority = _impl._guardian_has_primary_signer_authority
_guardian_home_policy_description = _impl._guardian_home_policy_description
_get_guardian_policy_rows = _impl._get_guardian_policy_rows
_children_with_signer_authority = _impl._children_with_signer_authority
_policy_contexts_from_authorized_children = _impl._policy_contexts_from_authorized_children
_resolve_policy_contexts = _impl._resolve_policy_contexts
_resolve_authorized_child_contexts = _impl._resolve_authorized_child_contexts
_query_policy_candidates_for_context = _impl._query_policy_candidates_for_context


@frappe.whitelist()
def get_guardian_policy_overview() -> dict[str, Any]:
    return _impl.get_guardian_policy_overview()


def get_guardian_policy_home_summary(*, guardian_name: str, children: list[dict[str, Any]]) -> dict[str, Any]:
    return _impl.get_guardian_policy_home_summary(guardian_name=guardian_name, children=children)


@frappe.whitelist()
def acknowledge_guardian_policy(
    policy_version: str,
    context_name: str | None = None,
    typed_signature_name: str | None = None,
    attestation_confirmed: int | str | bool | None = None,
    checked_clause_names=None,
) -> dict[str, Any]:
    return _impl.acknowledge_guardian_policy(
        policy_version=policy_version,
        context_name=context_name,
        typed_signature_name=typed_signature_name,
        attestation_confirmed=attestation_confirmed,
        checked_clause_names=checked_clause_names,
    )

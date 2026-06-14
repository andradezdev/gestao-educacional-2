from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _guardian_policy_impl_stub():
    module = ModuleType("ifitwala_ed.governance.api.guardian_policy")

    for name in (
        "_as_bool",
        "_normalize_signature_name",
        "_expected_guardian_signature_name",
        "_guardian_has_primary_signer_authority",
        "_guardian_home_policy_description",
        "_get_guardian_policy_rows",
        "_children_with_signer_authority",
        "_policy_contexts_from_authorized_children",
        "_resolve_policy_contexts",
        "_resolve_authorized_child_contexts",
        "_query_policy_candidates_for_context",
    ):
        setattr(module, name, lambda *args, **kwargs: None)

    return module


class TestGuardianPolicyFacade(TestCase):
    def test_root_guardian_policy_facade_delegates_public_methods(self):
        calls: dict[str, object] = {}
        impl = _guardian_policy_impl_stub()

        def fake_overview():
            calls["overview"] = True
            return {"counts": {"pending_policies": 1}}

        def fake_home_summary(*, guardian_name, children):
            calls["home_summary"] = {"guardian_name": guardian_name, "children": children}
            return {"pending_count": 1}

        def fake_acknowledge(
            *,
            policy_version,
            context_name=None,
            typed_signature_name=None,
            attestation_confirmed=None,
            checked_clause_names=None,
        ):
            calls["acknowledge"] = {
                "policy_version": policy_version,
                "context_name": context_name,
                "typed_signature_name": typed_signature_name,
                "attestation_confirmed": attestation_confirmed,
                "checked_clause_names": checked_clause_names,
            }
            return {"ok": True, "policy_version": policy_version}

        impl.get_guardian_policy_overview = fake_overview
        impl.get_guardian_policy_home_summary = fake_home_summary
        impl.acknowledge_guardian_policy = fake_acknowledge

        with stubbed_frappe(extra_modules={"ifitwala_ed.governance.api.guardian_policy": impl}):
            module = import_fresh("ifitwala_ed.api.guardian_policy")
            children = [{"student": "STU-1"}]

            self.assertEqual(module.get_guardian_policy_overview(), {"counts": {"pending_policies": 1}})
            self.assertEqual(
                module.get_guardian_policy_home_summary(guardian_name="GRD-1", children=children),
                {"pending_count": 1},
            )
            self.assertEqual(
                module.acknowledge_guardian_policy(
                    "VER-1",
                    context_name="STU-1",
                    typed_signature_name="Amina Guardian",
                    attestation_confirmed="1",
                    checked_clause_names=["CLAUSE-1"],
                ),
                {"ok": True, "policy_version": "VER-1"},
            )

        self.assertTrue(calls["overview"])
        self.assertEqual(calls["home_summary"], {"guardian_name": "GRD-1", "children": children})
        self.assertEqual(
            calls["acknowledge"],
            {
                "policy_version": "VER-1",
                "context_name": "STU-1",
                "typed_signature_name": "Amina Guardian",
                "attestation_confirmed": "1",
                "checked_clause_names": ["CLAUSE-1"],
            },
        )
        self.assertIs(module._get_guardian_policy_rows, impl._get_guardian_policy_rows)

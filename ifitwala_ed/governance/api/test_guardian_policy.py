# ifitwala_ed/governance/api/test_guardian_policy.py

from unittest.mock import Mock, patch

import frappe
from frappe.tests.utils import FrappeTestCase

from ifitwala_ed.governance.api.guardian_policy import (
    _children_with_signer_authority,
    _get_guardian_policy_rows,
    _query_policy_candidates_for_context,
    acknowledge_guardian_policy,
    get_guardian_policy_overview,
)


class TestGuardianPolicyPhase2(FrappeTestCase):
    def test_get_guardian_policy_overview_returns_counts_from_rows(self):
        rows = [
            {"policy_version": "VER-1", "is_acknowledged": False},
            {"policy_version": "VER-2", "is_acknowledged": True},
        ]
        children = [{"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"}]

        with (
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.session", frappe._dict({"user": "guardian@example.com"})),
            patch(
                "ifitwala_ed.governance.api.guardian_policy.now_datetime",
                return_value=frappe.utils.get_datetime("2026-03-13 09:00:00"),
            ),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._resolve_guardian_scope",
                return_value=("GRD-0001", children),
            ),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._children_with_signer_authority",
                return_value=children,
            ),
            patch("ifitwala_ed.governance.api.guardian_policy._get_guardian_policy_rows", return_value=rows),
        ):
            payload = get_guardian_policy_overview()

        self.assertEqual(payload["meta"]["guardian"]["name"], "GRD-0001")
        self.assertEqual(payload["family"]["children"], children)
        self.assertEqual(payload["counts"]["total_policies"], 2)
        self.assertEqual(payload["counts"]["acknowledged_policies"], 1)
        self.assertEqual(payload["counts"]["pending_policies"], 1)

    def test_acknowledge_guardian_policy_is_idempotent_when_already_acknowledged(self):
        with (
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.session", frappe._dict({"user": "guardian@example.com"})),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._resolve_guardian_scope",
                return_value=("GRD-0001", [{"student": "STU-1"}]),
            ),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._get_guardian_policy_rows",
                return_value=[{"policy_version": "VER-1"}],
            ),
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.db.get_value", return_value="ACK-0001"),
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.get_doc") as get_doc_mock,
        ):
            result = acknowledge_guardian_policy("VER-1")

        self.assertEqual(result["status"], "already_acknowledged")
        self.assertEqual(result["acknowledgement_name"], "ACK-0001")
        get_doc_mock.assert_not_called()

    def test_acknowledge_guardian_policy_requires_attestation(self):
        with (
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.session", frappe._dict({"user": "guardian@example.com"})),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._resolve_guardian_scope",
                return_value=("GRD-0001", [{"student": "STU-1"}]),
            ),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._get_guardian_policy_rows",
                return_value=[{"policy_version": "VER-1"}],
            ),
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.db.get_value", return_value=None),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._expected_guardian_signature_name",
                return_value="Amina Example Guardian",
            ),
        ):
            with self.assertRaises(frappe.ValidationError):
                acknowledge_guardian_policy(
                    "VER-1",
                    typed_signature_name="Amina Example Guardian",
                    attestation_confirmed=0,
                )

    def test_acknowledge_guardian_policy_creates_acknowledgement_when_missing(self):
        acknowledgement_doc = Mock()
        acknowledgement_doc.name = "ACK-0002"

        with (
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.session", frappe._dict({"user": "guardian@example.com"})),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._resolve_guardian_scope",
                return_value=("GRD-0001", [{"student": "STU-1"}]),
            ),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._get_guardian_policy_rows",
                return_value=[{"policy_version": "VER-1"}],
            ),
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.db.get_value", return_value=None),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._expected_guardian_signature_name",
                return_value="Amina Example Guardian",
            ),
            patch("ifitwala_ed.governance.api.guardian_policy.populate_policy_acknowledgement_evidence") as evidence_mock,
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.get_doc", return_value=acknowledgement_doc) as get_doc_mock,
        ):
            result = acknowledge_guardian_policy(
                "VER-1",
                typed_signature_name="Amina Example Guardian",
                attestation_confirmed=1,
                checked_clause_names=["CLAUSE-1"],
            )

        self.assertEqual(result["status"], "acknowledged")
        self.assertEqual(result["acknowledgement_name"], "ACK-0002")
        acknowledgement_doc.insert.assert_called_once_with()
        evidence_mock.assert_called_once_with(
            acknowledgement_doc,
            typed_signature_name="Amina Example Guardian",
            attestation_confirmed=1,
            checked_clause_names=["CLAUSE-1"],
        )
        payload = get_doc_mock.call_args.args[0]
        self.assertEqual(payload["acknowledged_for"], "Guardian")
        self.assertEqual(payload["context_name"], "GRD-0001")

    def test_acknowledge_guardian_policy_uses_student_context_for_child_mode(self):
        acknowledgement_doc = Mock()
        acknowledgement_doc.name = "ACK-CHILD-1"

        with (
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.session", frappe._dict({"user": "guardian@example.com"})),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._resolve_guardian_scope",
                return_value=("GRD-0001", [{"student": "STU-1"}]),
            ),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._get_guardian_policy_rows",
                return_value=[
                    {
                        "policy_version": "VER-1",
                        "ack_context_doctype": "Student",
                        "ack_context_name": "STU-1",
                    }
                ],
            ),
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.db.get_value", return_value=None),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._expected_guardian_signature_name",
                return_value="Amina Example Guardian",
            ),
            patch("ifitwala_ed.governance.api.guardian_policy.populate_policy_acknowledgement_evidence"),
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.get_doc", return_value=acknowledgement_doc) as get_doc_mock,
        ):
            result = acknowledge_guardian_policy(
                "VER-1",
                context_name="STU-1",
                typed_signature_name="Amina Example Guardian",
                attestation_confirmed=1,
            )

        self.assertEqual(result["status"], "acknowledged")
        payload = get_doc_mock.call_args.args[0]
        self.assertEqual(payload["acknowledged_for"], "Guardian")
        self.assertEqual(payload["context_doctype"], "Student")
        self.assertEqual(payload["context_name"], "STU-1")

    def test_children_with_signer_authority_filters_to_consent_enabled_links(self):
        children = [
            {"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"},
            {"student": "STU-2", "full_name": "Noah Example", "school": "SCHOOL-1"},
        ]

        with (
            patch("ifitwala_ed.governance.api.guardian_policy._guardian_has_primary_signer_authority", return_value=True),
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.db.has_column", return_value=True),
            patch(
                "ifitwala_ed.governance.api.guardian_policy.frappe.get_all",
                return_value=[{"parent": "STU-1"}],
            ),
        ):
            filtered = _children_with_signer_authority(guardian_name="GRD-0001", children=children)

        self.assertEqual(filtered, [children[0]])

    def test_children_with_signer_authority_rejects_non_primary_guardian(self):
        children = [{"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"}]

        with patch("ifitwala_ed.governance.api.guardian_policy._guardian_has_primary_signer_authority", return_value=False):
            filtered = _children_with_signer_authority(guardian_name="GRD-0001", children=children)

        self.assertEqual(filtered, [])

    def test_query_policy_candidates_filters_guardian_rows_in_sql(self):
        with (
            patch(
                "ifitwala_ed.governance.api.guardian_policy.get_organization_ancestors_including_self",
                return_value=["ORG-1"],
            ),
            patch(
                "ifitwala_ed.governance.api.guardian_policy.get_school_ancestors_including_self",
                return_value=["SCHOOL-1"],
            ),
            patch(
                "ifitwala_ed.governance.api.guardian_policy.frappe.db.sql",
                return_value=[
                    {
                        "policy_name": "POL-1",
                        "policy_key": "family_handbook",
                        "policy_title": "Family Handbook",
                        "policy_category": "Handbooks",
                        "description": "",
                        "policy_organization": "ORG-1",
                        "policy_school": "SCHOOL-1",
                        "policy_version": "VER-1",
                        "version_label": "v1",
                        "policy_text": "<p>Policy</p>",
                        "effective_from": None,
                        "effective_to": None,
                        "approved_on": None,
                    }
                ],
            ) as sql_mock,
            patch(
                "ifitwala_ed.governance.api.guardian_policy.select_nearest_policy_rows_by_key",
                side_effect=lambda **kwargs: kwargs["rows"],
            ),
        ):
            rows = _query_policy_candidates_for_context(organization="ORG-1", school="SCHOOL-1")

        self.assertEqual([row["policy_name"] for row in rows], ["POL-1"])
        self.assertIn("tabInstitutional Policy Audience", sql_mock.call_args.args[0])
        self.assertEqual(sql_mock.call_args.args[1][-1], "Guardian")

    def test_get_guardian_policy_rows_sanitizes_policy_text(self):
        children = [{"student": "STU-1", "school": "SCHOOL-1"}]

        with (
            patch("ifitwala_ed.governance.api.guardian_policy.ensure_policy_applies_to_storage", return_value={"ok": True}),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._resolve_authorized_child_contexts",
                return_value=[
                    {
                        "student": "STU-1",
                        "student_label": "STU-1",
                        "organization": "ORG-1",
                        "school": "SCHOOL-1",
                    }
                ],
            ),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._resolve_policy_contexts",
                return_value=[{"organization": "ORG-1", "school": "SCHOOL-1"}],
            ),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._query_policy_candidates_for_context",
                return_value=[
                    {
                        "policy_name": "POL-1",
                        "policy_key": "family_handbook",
                        "policy_title": "Family Handbook",
                        "policy_category": "Handbooks",
                        "policy_version": "VER-1",
                        "version_label": "v1",
                        "policy_organization": "ORG-1",
                        "policy_school": "SCHOOL-1",
                        "description": "Review this handbook.",
                        "policy_text": "<h1>Family Handbook</h1><p>Welcome</p><script>alert(1)</script>",
                        "effective_from": None,
                        "effective_to": None,
                        "approved_on": None,
                    }
                ],
            ),
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.get_all", return_value=[]),
            patch("ifitwala_ed.governance.api.guardian_policy.get_policy_version_acknowledgement_clauses_map", return_value={}),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._expected_guardian_signature_name",
                return_value="Mariam Example",
            ),
        ):
            rows = _get_guardian_policy_rows(guardian_name="GRD-0001", children=children)

        self.assertEqual(len(rows), 1)
        self.assertIn("<h2>Family Handbook</h2>", rows[0]["policy_text"])
        self.assertIn("<p>Welcome</p>", rows[0]["policy_text"])
        self.assertNotIn("<script", rows[0]["policy_text"])

    def test_get_guardian_policy_rows_expands_child_mode_to_one_row_per_student(self):
        children = [
            {"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"},
            {"student": "STU-2", "full_name": "Noah Example", "school": "SCHOOL-1"},
        ]

        with (
            patch("ifitwala_ed.governance.api.guardian_policy.ensure_policy_applies_to_storage", return_value={"ok": True}),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._resolve_authorized_child_contexts",
                return_value=[
                    {
                        "student": "STU-1",
                        "student_label": "Amina Example",
                        "organization": "ORG-1",
                        "school": "SCHOOL-1",
                    },
                    {
                        "student": "STU-2",
                        "student_label": "Noah Example",
                        "organization": "ORG-1",
                        "school": "SCHOOL-1",
                    },
                ],
            ),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._query_policy_candidates_for_context",
                return_value=[
                    {
                        "policy_name": "POL-1",
                        "policy_key": "family_handbook",
                        "policy_title": "Family Handbook",
                        "policy_category": "Handbooks",
                        "policy_version": "VER-1",
                        "version_label": "v1",
                        "guardian_acknowledgement_mode": "Child Acknowledgement",
                        "policy_organization": "ORG-1",
                        "policy_school": "SCHOOL-1",
                        "description": "Review this handbook.",
                        "policy_text": "<p>Policy text</p>",
                        "effective_from": None,
                        "effective_to": None,
                        "approved_on": None,
                    }
                ],
            ),
            patch("ifitwala_ed.governance.api.guardian_policy.frappe.get_all", return_value=[]),
            patch("ifitwala_ed.governance.api.guardian_policy.get_policy_version_acknowledgement_clauses_map", return_value={}),
            patch(
                "ifitwala_ed.governance.api.guardian_policy._expected_guardian_signature_name",
                return_value="Mariam Example",
            ),
        ):
            rows = _get_guardian_policy_rows(guardian_name="GRD-0001", children=children)

        self.assertEqual(len(rows), 2)
        self.assertEqual({row["ack_context_doctype"] for row in rows}, {"Student"})
        self.assertEqual({row["ack_context_name"] for row in rows}, {"STU-1", "STU-2"})
        self.assertEqual({row["scope_label"] for row in rows}, {"Amina Example", "Noah Example"})



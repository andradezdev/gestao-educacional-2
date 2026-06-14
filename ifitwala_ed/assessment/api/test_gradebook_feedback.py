# ifitwala_ed/assessment/api/test_gradebook_feedback.py

from __future__ import annotations

import types
from unittest import TestCase
from urllib.parse import urlparse

from ifitwala_ed.tests.frappe_stubs import StubPermissionError, stubbed_frappe

from ifitwala_ed.assessment.api.gradebook_test_utils import (
    _gradebook_stub_modules,
    _import_fresh_gradebook,
)


class TestGradebookFeedback(TestCase):
    def test_export_feedback_pdf_uses_artifact_service(self):
        captured: dict[str, object] = {}
        artifact_service = types.ModuleType("ifitwala_ed.assessment.task_feedback_artifact_service")

        def fake_export(outcome_id, audience="student", submission_id=None):
            captured["outcome_id"] = outcome_id
            captured["audience"] = audience
            captured["submission_id"] = submission_id
            return {
                "file_id": "FILE-1",
                "file_name": "released-feedback.pdf",
                "task_submission": "TSU-1",
                "submission_version": 2,
                "preview_status": "pending",
                "open_url": "/open/feedback-pdf",
                "preview_url": "/preview/feedback-pdf",
                "attachment_preview": {"kind": "pdf", "preview_mode": "pdf_embed"},
            }

        artifact_service.export_released_feedback_pdf = fake_export

        with stubbed_frappe(
            extra_modules=_gradebook_stub_modules(task_feedback_artifact_service=artifact_service)
        ) as frappe:
            frappe.session.user = "teacher@example.com"
            frappe.get_roles = lambda user=None: ["Academic Admin"]

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Outcome" and name == "OUT-1":
                    return {"task_delivery": "TDL-1"}
                if doctype == "Task Delivery" and name == "TDL-1":
                    return {"name": "TDL-1", "student_group": "GRP-1"}
                return None

            frappe.db.get_value = fake_get_value
            module = _import_fresh_gradebook()
            payload = module.export_feedback_pdf({"outcome_id": "OUT-1", "submission_id": "TSU-1"})

        self.assertEqual(captured["outcome_id"], "OUT-1")
        self.assertEqual(captured["audience"], "student")
        self.assertEqual(captured["submission_id"], "TSU-1")
        self.assertEqual(payload["artifact"]["open_url"], "/open/feedback-pdf")

    def test_get_drawer_selects_requested_submission_version_and_serializes_preview_urls(self):
        with stubbed_frappe(extra_modules=_gradebook_stub_modules()) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Outcome" and name == "OUT-1":
                    return {
                        "name": "OUT-1",
                        "task_delivery": "TDL-1",
                        "student": "STU-1",
                        "grading_status": "Needs Review",
                        "procedural_status": "Submitted",
                        "has_submission": 1,
                        "has_new_submission": 1,
                        "is_complete": 0,
                        "is_published": 0,
                        "published_on": None,
                        "published_by": None,
                        "official_score": 8,
                        "official_grade": "B",
                        "official_grade_value": 8,
                        "official_feedback": "Review latest evidence",
                    }
                if doctype == "Task Delivery" and name == "TDL-1":
                    return {
                        "name": "TDL-1",
                        "task": "TASK-1",
                        "student_group": "GRP-1",
                        "due_date": "2026-04-03 10:00:00",
                        "delivery_mode": "Assess",
                        "grading_mode": "Points",
                        "allow_feedback": 1,
                        "max_points": 20,
                        "quiz_pass_percentage": None,
                        "rubric_version": None,
                        "rubric_scoring_strategy": None,
                    }
                if doctype == "Task" and name == "TASK-1":
                    return {"name": "TASK-1", "title": "Source Analysis", "task_type": "Assignment"}
                return None

            def fake_get_all(doctype, filters=None, fields=None, order_by=None, limit=0, pluck=None):
                if doctype == "Task Submission":
                    self.assertNotIn("attachments", fields or [])
                    return [
                        {
                            "name": "TSU-2026-00002",
                            "version": 2,
                            "submitted_on": "2026-04-02 10:00:00",
                            "submitted_by": "student@example.com",
                            "is_late": 0,
                            "is_cloned": 0,
                            "cloned_from": "",
                            "submission_origin": "Student Upload",
                            "is_stub": 0,
                            "evidence_note": "Latest evidence",
                            "link_url": "",
                            "text_content": "Version 2",
                        },
                        {
                            "name": "TSU-2026-00001",
                            "version": 1,
                            "submitted_on": "2026-04-01 09:00:00",
                            "submitted_by": "student@example.com",
                            "is_late": 0,
                            "is_cloned": 0,
                            "cloned_from": "",
                            "submission_origin": "Student Upload",
                            "is_stub": 0,
                            "evidence_note": "Original evidence",
                            "link_url": "",
                            "text_content": "Version 1",
                        },
                    ]
                if doctype == "Task Contribution":
                    return []
                if doctype == "Attached Document":
                    self.assertEqual(filters.get("parent"), "TSU-2026-00001")
                    return [
                        {
                            "name": "ATT-OLD-1",
                            "file": "/private/files/submission-v1.pdf",
                            "external_url": "",
                            "description": "First upload",
                            "public": 0,
                            "file_name": "submission-v1.pdf",
                            "file_size": 512,
                        }
                    ]
                if doctype == "File":
                    self.assertEqual(filters.get("attached_to_name"), "TSU-2026-00001")
                    return [
                        {
                            "name": "FILE-SUB-0001",
                            "file_url": "/private/files/submission-v1.pdf",
                            "creation": "2026-04-01 09:00:00",
                        }
                    ]
                if doctype == "Drive File":
                    return [
                        {
                            "file": "FILE-SUB-0001",
                            "preview_status": "pending",
                            "current_version": "DFV-SUB-0001",
                        }
                    ]
                if doctype == "Drive File Version":
                    return [{"name": "DFV-SUB-0001", "mime_type": "application/pdf"}]
                return []

            frappe.db.get_value = fake_get_value
            frappe.get_all = fake_get_all

            module = _import_fresh_gradebook()
            module.gradebook_support._can_read_gradebook = lambda: True
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._get_outcome_criteria_map = lambda outcome_ids: {"OUT-1": []}
            module.gradebook_support._select_my_contribution = lambda contributions: None
            module.gradebook_support._get_student_display_map = lambda student_ids: {"STU-1": "Ada Lovelace"}
            module.gradebook_support._get_student_meta_map = lambda student_ids: {
                "STU-1": {
                    "name": "STU-1",
                    "student_id": "S-001",
                    "student_image": None,
                }
            }
            module.gradebook_support._build_delivery_criteria_payload = lambda delivery: []

            payload = module.get_drawer("OUT-1", version="1")

        self.assertEqual(payload["delivery"]["title"], "Source Analysis")
        self.assertEqual(payload["delivery"]["delivery_mode"], "Assess")
        self.assertEqual(payload["student"]["student_name"], "Ada Lovelace")
        self.assertEqual(payload["student"]["student_id"], "S-001")
        self.assertTrue(payload["outcome"]["has_submission"])
        self.assertTrue(payload["outcome"]["has_new_submission"])
        self.assertFalse(payload["outcome"]["is_published"])
        self.assertTrue(payload["allowed_actions"]["can_edit_marking"])
        self.assertEqual(payload["latest_submission"]["submission_id"], "TSU-2026-00002")
        self.assertFalse(payload["latest_submission"]["is_selected"])
        self.assertEqual(payload["selected_submission"]["submission_id"], "TSU-2026-00001")
        self.assertEqual(payload["selected_submission"]["version"], 1)
        self.assertEqual(payload["selected_submission"]["evidence_note"], "Original evidence")
        self.assertNotIn("submissions", payload)
        self.assertEqual(payload["feedback_workspace"]["task_submission"], "TSU-2026-00001")
        self.assertEqual(payload["feedback_workspace"]["publication"]["feedback_visibility"], "hidden")
        self.assertEqual(payload["feedback_artifact"]["task_submission"], "TSU-2026-00001")
        self.assertEqual(payload["feedback_artifact"]["open_url"], "/open/feedback-pdf")
        self.assertEqual(payload["comment_bank"]["entries"], [])
        self.assertEqual(payload["submission_versions"][0]["submission_id"], "TSU-2026-00001")
        self.assertTrue(payload["submission_versions"][0]["is_selected"])
        self.assertFalse(payload["submission_versions"][1]["is_selected"])

        attachment = payload["selected_submission"]["attachments"][0]
        self.assertNotIn("attachment_preview", attachment)
        self.assertNotIn("open_url", attachment)
        self.assertNotIn("preview_url", attachment)
        self.assertNotIn("thumbnail_url", attachment)
        self.assertEqual(attachment["mime_type"], "application/pdf")
        self.assertEqual(attachment["extension"], "pdf")
        attachment_row = attachment["attachment"]
        self.assertEqual(attachment_row["surface"], "task_submission.evidence")
        self.assertEqual(attachment_row["preview_status"], "pending")
        self.assertEqual(attachment_row["owner_doctype"], "Task Submission")
        self.assertEqual(attachment_row["owner_name"], "TSU-2026-00001")
        self.assertEqual(attachment_row["kind"], "pdf")
        self.assertFalse(attachment_row["is_latest_version"])
        self.assertEqual(attachment_row["version_label"], "Version 1")
        self.assertIsNone(attachment_row["preview_url"])
        self.assertIsNone(attachment_row["thumbnail_url"])
        self.assertFalse(attachment_row["can_preview"])
        self.assertEqual(
            urlparse(attachment_row["open_url"]).path,
            "/api/method/ifitwala_ed.api.file_access.download_academic_file",
        )
        self.assertEqual(payload["selected_submission"]["annotation_readiness"]["mode"], "reduced")
        self.assertEqual(
            payload["selected_submission"]["annotation_readiness"]["reason_code"],
            "pdf_preview_pending",
        )
        self.assertIsNone(payload["selected_submission"]["annotation_readiness"]["preview_url"])

    def test_save_feedback_draft_uses_named_feedback_service(self):
        saved_payloads = []

        feedback_service = types.ModuleType("ifitwala_ed.assessment.task_feedback_service")
        feedback_service.build_feedback_workspace_payload = lambda *args, **kwargs: None
        feedback_service.save_feedback_workspace_draft = lambda payload, actor=None: (
            saved_payloads.append((payload, actor))
            or {
                "workspace_id": "TFW-1",
                "task_outcome": payload["outcome_id"],
                "task_submission": payload["submission_id"],
                "submission_version": 2,
                "summary": payload.get("summary") or {},
                "items": payload.get("items") or [],
                "publication": {
                    "feedback_visibility": "hidden",
                    "grade_visibility": "hidden",
                    "derived_from_legacy_outcome": False,
                    "legacy_outcome_published": False,
                    "legacy_published_on": None,
                    "legacy_published_by": None,
                },
                "modified": None,
                "modified_by": actor,
            }
        )
        feedback_service.save_feedback_publication = lambda payload, actor=None: payload

        with stubbed_frappe(extra_modules=_gradebook_stub_modules(task_feedback_service=feedback_service)) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Outcome" and name == "OUT-1":
                    return {"task_delivery": "TDL-1"}
                if doctype == "Task Delivery" and name == "TDL-1":
                    return {
                        "name": "TDL-1",
                        "student_group": "GRP-1",
                        "task": "TASK-1",
                        "delivery_mode": "Assess",
                        "grading_mode": "Points",
                        "allow_feedback": 1,
                    }
                return None

            frappe.db.get_value = fake_get_value

            module = _import_fresh_gradebook()
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None

            response = module.save_feedback_draft(
                {
                    "outcome_id": "OUT-1",
                    "submission_id": "TSU-1",
                    "summary": {"overall": "Prioritise the thesis."},
                    "items": [
                        {
                            "kind": "page",
                            "page": 1,
                            "comment": "Start with a clearer claim.",
                            "intent": "next_step",
                            "workflow_state": "draft",
                            "anchor": {"kind": "page", "page": 1},
                        }
                    ],
                }
            )

        self.assertEqual(saved_payloads[0][0]["submission_id"], "TSU-1")
        self.assertEqual(saved_payloads[0][1], "unit.test@example.com")
        self.assertEqual(response["feedback_workspace"]["workspace_id"], "TFW-1")
        self.assertEqual(response["feedback_workspace"]["summary"]["overall"], "Prioritise the thesis.")

    def test_save_feedback_publication_uses_named_feedback_service(self):
        saved_payloads = []

        feedback_service = types.ModuleType("ifitwala_ed.assessment.task_feedback_service")
        feedback_service.build_feedback_workspace_payload = lambda *args, **kwargs: None
        feedback_service.save_feedback_workspace_draft = lambda payload, actor=None: payload
        feedback_service.save_feedback_publication = lambda payload, actor=None: (
            saved_payloads.append((payload, actor))
            or {
                "workspace_id": "TFW-1",
                "task_outcome": payload["outcome_id"],
                "task_submission": payload["submission_id"],
                "submission_version": 2,
                "summary": {
                    "overall": "",
                    "strengths": "",
                    "improvements": "",
                    "next_steps": "",
                },
                "items": [],
                "publication": {
                    "feedback_visibility": payload["feedback_visibility"],
                    "grade_visibility": payload["grade_visibility"],
                    "derived_from_legacy_outcome": False,
                    "legacy_outcome_published": False,
                    "legacy_published_on": None,
                    "legacy_published_by": None,
                },
                "modified": None,
                "modified_by": actor,
            }
        )

        with stubbed_frappe(extra_modules=_gradebook_stub_modules(task_feedback_service=feedback_service)) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Outcome" and name == "OUT-1":
                    return {"task_delivery": "TDL-1"}
                if doctype == "Task Delivery" and name == "TDL-1":
                    return {
                        "name": "TDL-1",
                        "student_group": "GRP-1",
                        "task": "TASK-1",
                        "delivery_mode": "Assess",
                        "grading_mode": "Points",
                        "allow_feedback": 1,
                    }
                return None

            frappe.db.get_value = fake_get_value

            module = _import_fresh_gradebook()
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None

            response = module.save_feedback_publication(
                {
                    "outcome_id": "OUT-1",
                    "submission_id": "TSU-1",
                    "feedback_visibility": "student",
                    "grade_visibility": "hidden",
                }
            )

        self.assertEqual(saved_payloads[0][0]["feedback_visibility"], "student")
        self.assertEqual(saved_payloads[0][0]["grade_visibility"], "hidden")
        self.assertEqual(saved_payloads[0][1], "unit.test@example.com")
        self.assertEqual(response["feedback_workspace"]["publication"]["feedback_visibility"], "student")

    def test_save_feedback_comment_bank_entry_uses_named_comment_bank_service(self):
        comment_bank_service = types.ModuleType("ifitwala_ed.assessment.task_feedback_comment_bank_service")
        saved_payloads = []
        comment_bank_service.build_comment_bank_payload = lambda outcome_id, actor=None: {"context": {}, "entries": []}
        comment_bank_service.save_comment_bank_entry = lambda payload, actor=None: (
            saved_payloads.append((payload, actor))
            or {
                "context": {
                    "course": "CRS-1",
                    "task": "TASK-1",
                    "task_title": "Essay",
                    "criteria": [],
                },
                "entries": [
                    {
                        "id": "BANK-1",
                        "label": "Use evidence",
                        "body": "Use a stronger quotation here.",
                        "intent": "issue",
                        "scope_mode": "task",
                        "course": "CRS-1",
                        "task": "TASK-1",
                        "assessment_criteria": None,
                        "assessment_criteria_label": None,
                        "match_reasons": ["task"],
                        "match_score": 4,
                    }
                ],
            }
        )

        with stubbed_frappe(
            extra_modules=_gradebook_stub_modules(task_feedback_comment_bank_service=comment_bank_service)
        ) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Outcome" and name == "OUT-1":
                    return {"task_delivery": "TDL-1"}
                if doctype == "Task Delivery" and name == "TDL-1":
                    return {
                        "name": "TDL-1",
                        "student_group": "GRP-1",
                        "task": "TASK-1",
                        "delivery_mode": "Assess",
                        "grading_mode": "Criteria",
                        "allow_feedback": 1,
                    }
                return None

            frappe.db.get_value = fake_get_value

            module = _import_fresh_gradebook()
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None

            response = module.save_feedback_comment_bank_entry(
                {
                    "outcome_id": "OUT-1",
                    "body": "Use a stronger quotation here.",
                    "feedback_intent": "issue",
                    "scope_mode": "task",
                }
            )

        self.assertEqual(saved_payloads[0][0]["outcome_id"], "OUT-1")
        self.assertEqual(saved_payloads[0][1], "unit.test@example.com")
        self.assertEqual(response["comment_bank"]["entries"][0]["scope_mode"], "task")

    def test_submit_contribution_uses_named_service_and_resolves_submission(self):
        submitted_payloads = []

        task_contribution_service = types.ModuleType("ifitwala_ed.assessment.task_contribution_service")
        task_contribution_service.submit_contribution = lambda payload, contributor=None: (
            submitted_payloads.append((payload, contributor))
            or {
                "contribution": "TCO-1",
                "status": "Submitted",
                "task_outcome": payload.get("task_outcome"),
                "task_submission": payload.get("task_submission"),
                "outcome_update": {"outcome": payload.get("task_outcome"), "grading_status": "Finalized"},
            }
        )

        with stubbed_frappe(extra_modules=_gradebook_stub_modules(task_contribution_service=task_contribution_service)):
            module = _import_fresh_gradebook()
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._resolve_or_create_stub_submission_id = lambda outcome_id, data: "SUB-1"

            payload = module.submit_contribution(
                task_outcome="OUT-1",
                score=12,
                feedback="Strong evidence.",
            )

        self.assertEqual(
            submitted_payloads,
            [
                (
                    {
                        "task_outcome": "OUT-1",
                        "score": 12,
                        "feedback": "Strong evidence.",
                        "task_submission": "SUB-1",
                    },
                    "unit.test@example.com",
                )
            ],
        )
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["result"]["task_submission"], "SUB-1")
        self.assertEqual(payload["outcome_update"]["grading_status"], "Finalized")

    def test_moderator_action_requires_adminish_role(self):
        task_contribution_service = types.ModuleType("ifitwala_ed.assessment.task_contribution_service")
        task_contribution_service.apply_moderator_action = lambda payload, contributor=None: {
            "contribution": "TCO-MOD-1",
            "status": "Submitted",
            "task_outcome": payload.get("task_outcome"),
            "task_submission": payload.get("task_submission"),
            "outcome_update": {"outcome": payload.get("task_outcome"), "grading_status": "Moderated"},
        }

        with stubbed_frappe(extra_modules=_gradebook_stub_modules(task_contribution_service=task_contribution_service)):
            module = _import_fresh_gradebook()
            module.gradebook_support._is_academic_adminish = lambda: False

            with self.assertRaises(StubPermissionError):
                module.moderator_action(task_outcome="OUT-1", action="Approve")

    def test_moderator_action_uses_named_service_and_preserves_action(self):
        moderation_payloads = []

        task_contribution_service = types.ModuleType("ifitwala_ed.assessment.task_contribution_service")
        task_contribution_service.apply_moderator_action = lambda payload, contributor=None: (
            moderation_payloads.append((payload, contributor))
            or {
                "contribution": "TCO-MOD-1",
                "status": "Submitted",
                "task_outcome": payload.get("task_outcome"),
                "task_submission": payload.get("task_submission"),
                "outcome_update": {"outcome": payload.get("task_outcome"), "grading_status": "Moderated"},
            }
        )

        with stubbed_frappe(extra_modules=_gradebook_stub_modules(task_contribution_service=task_contribution_service)):
            module = _import_fresh_gradebook()
            module.gradebook_support._is_academic_adminish = lambda: True
            module.gradebook_support._resolve_or_create_stub_submission_id = lambda outcome_id, data: "SUB-MOD-1"

            payload = module.moderator_action(
                task_outcome="OUT-1",
                action="Adjust",
                score=14,
                feedback="Adjusted after review.",
            )

        self.assertEqual(
            moderation_payloads,
            [
                (
                    {
                        "task_outcome": "OUT-1",
                        "action": "Adjust",
                        "score": 14,
                        "feedback": "Adjusted after review.",
                        "task_submission": "SUB-MOD-1",
                    },
                    "unit.test@example.com",
                )
            ],
        )
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["result"]["task_submission"], "SUB-MOD-1")
        self.assertEqual(payload["outcome_update"]["grading_status"], "Moderated")


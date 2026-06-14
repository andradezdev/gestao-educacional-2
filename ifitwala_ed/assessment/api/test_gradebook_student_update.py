# ifitwala_ed/assessment/api/test_gradebook_student_update.py

from __future__ import annotations

import types
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import StubValidationError, stubbed_frappe

from ifitwala_ed.assessment.api.gradebook_test_utils import (
    _gradebook_stub_modules,
    _import_fresh_gradebook,
)


class TestGradebookStudentUpdate(TestCase):
    def test_update_task_student_rejects_feedback_when_comments_disabled(self):
        with stubbed_frappe(extra_modules=_gradebook_stub_modules()) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Outcome":
                    return {"name": "OUT-1", "task_delivery": "TDL-1", "official_score": None}
                if doctype == "Task Delivery":
                    return {
                        "name": "TDL-1",
                        "student_group": "GRP-1",
                        "delivery_mode": "Assess",
                        "grading_mode": "Points",
                        "allow_feedback": 0,
                    }
                return None

            frappe.db.get_value = fake_get_value

            module = _import_fresh_gradebook()
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None

            with self.assertRaises(StubValidationError):
                module.update_task_student("OUT-1", {"feedback": "Needs a stronger explanation."})

    def test_update_task_student_allows_criteria_comment_before_any_rubric_score(self):
        submitted_payloads = []

        task_contribution_service = types.ModuleType("ifitwala_ed.assessment.task_contribution_service")
        task_contribution_service.submit_contribution = lambda payload, contributor=None: (
            submitted_payloads.append((payload, contributor)) or {"contribution": "TCO-1"}
        )

        with stubbed_frappe(
            extra_modules=_gradebook_stub_modules(task_contribution_service=task_contribution_service)
        ) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Outcome":
                    if fieldname == ["name", "task_delivery", "official_score", "grading_status"]:
                        return {
                            "name": "OUT-1",
                            "task_delivery": "TDL-1",
                            "official_score": None,
                            "grading_status": "Not Started",
                            "is_published": 0,
                        }
                    return {
                        "name": "OUT-1",
                        "official_score": None,
                        "official_feedback": "Focus on examples.",
                        "grading_status": "Not Started",
                        "is_complete": 0,
                        "is_published": 0,
                        "modified": "2026-04-02 18:30:00",
                    }
                if doctype == "Task Delivery":
                    return {
                        "name": "TDL-1",
                        "student_group": "GRP-1",
                        "delivery_mode": "Assess",
                        "grading_mode": "Criteria",
                        "allow_feedback": 1,
                    }
                return None

            frappe.db.get_value = fake_get_value
            frappe.db.get_values = lambda *args, **kwargs: []

            module = _import_fresh_gradebook()
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None
            module.gradebook_support._resolve_or_create_stub_submission_id = lambda task_student, payload: "SUB-1"

            payload = module.update_task_student("OUT-1", {"feedback": "Focus on examples."})

        self.assertEqual(
            submitted_payloads,
            [
                (
                    {
                        "task_outcome": "OUT-1",
                        "feedback": "Focus on examples.",
                        "task_submission": "SUB-1",
                    },
                    "unit.test@example.com",
                )
            ],
        )
        self.assertEqual(payload["feedback"], "Focus on examples.")

    def test_update_task_student_routes_assessed_completion_to_contribution_judgment(self):
        submitted_payloads = []

        task_contribution_service = types.ModuleType("ifitwala_ed.assessment.task_contribution_service")
        task_contribution_service.submit_contribution = lambda payload, contributor=None: (
            submitted_payloads.append((payload, contributor)) or {"contribution": "TCO-1"}
        )

        with stubbed_frappe(
            extra_modules=_gradebook_stub_modules(task_contribution_service=task_contribution_service)
        ) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Outcome":
                    if fieldname == ["name", "task_delivery", "official_score", "grading_status"]:
                        return {
                            "name": "OUT-1",
                            "task_delivery": "TDL-1",
                            "official_score": None,
                            "grading_status": "Not Started",
                            "is_published": 0,
                        }
                    return {
                        "name": "OUT-1",
                        "official_score": None,
                        "official_feedback": "Marked complete.",
                        "grading_status": "Finalized",
                        "is_complete": 1,
                        "is_published": 0,
                        "modified": "2026-04-17 18:05:00",
                    }
                if doctype == "Task Delivery":
                    return {
                        "name": "TDL-1",
                        "student_group": "GRP-1",
                        "delivery_mode": "Assess",
                        "grading_mode": "Completion",
                        "allow_feedback": 1,
                    }
                return None

            frappe.db.get_value = fake_get_value

            module = _import_fresh_gradebook()
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None
            module.gradebook_support._resolve_or_create_stub_submission_id = lambda task_student, payload: "SUB-1"

            payload = module.update_task_student("OUT-1", {"complete": 1, "feedback": "Marked complete."})

        self.assertEqual(
            submitted_payloads,
            [
                (
                    {
                        "task_outcome": "OUT-1",
                        "feedback": "Marked complete.",
                        "judgment_code": "complete",
                        "task_submission": "SUB-1",
                    },
                    "unit.test@example.com",
                )
            ],
        )
        self.assertEqual(payload["complete"], 1)
        self.assertEqual(payload["feedback"], "Marked complete.")

    def test_update_task_student_keeps_assign_only_completion_on_direct_outcome_path(self):
        submitted_payloads = []
        completion_calls = []

        task_contribution_service = types.ModuleType("ifitwala_ed.assessment.task_contribution_service")
        task_contribution_service.submit_contribution = lambda payload, contributor=None: submitted_payloads.append(
            (payload, contributor)
        )
        task_outcome_service = types.ModuleType("ifitwala_ed.assessment.task_outcome_service")
        task_outcome_service.set_assign_only_completion = (
            lambda outcome_id, *, is_complete, expected_student=None, ignore_permissions=False: (
                completion_calls.append(
                    {
                        "outcome_id": outcome_id,
                        "is_complete": is_complete,
                        "expected_student": expected_student,
                        "ignore_permissions": ignore_permissions,
                    }
                )
                or {"outcome": outcome_id, "is_complete": is_complete, "completed_on": "2026-04-17 18:10:00"}
            )
        )

        with stubbed_frappe(
            extra_modules=_gradebook_stub_modules(
                task_contribution_service=task_contribution_service,
                task_outcome_service=task_outcome_service,
            )
        ) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Outcome":
                    if fieldname == ["name", "task_delivery", "official_score", "grading_status"]:
                        return {
                            "name": "OUT-1",
                            "task_delivery": "TDL-1",
                            "official_score": None,
                            "grading_status": "Not Started",
                            "is_published": 0,
                        }
                    return {
                        "name": "OUT-1",
                        "official_score": None,
                        "official_feedback": None,
                        "grading_status": "Not Started",
                        "is_complete": 1,
                        "is_published": 0,
                        "modified": "2026-04-17 18:10:00",
                    }
                if doctype == "Task Delivery":
                    return {
                        "name": "TDL-1",
                        "student_group": "GRP-1",
                        "delivery_mode": "Assign Only",
                        "grading_mode": "Completion",
                        "allow_feedback": 0,
                    }
                return None

            frappe.db.get_value = fake_get_value

            module = _import_fresh_gradebook()
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None

            payload = module.update_task_student("OUT-1", {"complete": 1})

        self.assertEqual(submitted_payloads, [])
        self.assertEqual(
            completion_calls,
            [
                {
                    "outcome_id": "OUT-1",
                    "is_complete": 1,
                    "expected_student": None,
                    "ignore_permissions": False,
                }
            ],
        )
        self.assertEqual(payload["complete"], 1)

    def test_update_task_student_rejects_released_status_from_generic_status_save(self):
        with stubbed_frappe(extra_modules=_gradebook_stub_modules()) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Outcome":
                    if fieldname == ["name", "task_delivery", "official_score", "grading_status"]:
                        return {
                            "name": "OUT-1",
                            "task_delivery": "TDL-1",
                            "official_score": None,
                            "grading_status": "Finalized",
                            "is_published": 0,
                        }
                if doctype == "Task Delivery":
                    return {
                        "name": "TDL-1",
                        "student_group": "GRP-1",
                        "delivery_mode": "Assess",
                        "grading_mode": "Points",
                        "allow_feedback": 0,
                    }
                return None

            frappe.db.get_value = fake_get_value

            module = _import_fresh_gradebook()
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None

            with self.assertRaises(StubValidationError):
                module.update_task_student("OUT-1", {"status": "Released"})

    def test_update_task_student_rejects_status_change_while_outcome_is_released(self):
        feedback_service = types.ModuleType("ifitwala_ed.assessment.task_feedback_service")
        feedback_service.build_publication_state_map = lambda outcome_ids: {
            outcome_id: {"is_visible_to_any_audience": True} for outcome_id in outcome_ids or []
        }

        with stubbed_frappe(extra_modules=_gradebook_stub_modules(task_feedback_service=feedback_service)) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Outcome":
                    if fieldname == ["name", "task_delivery", "official_score", "grading_status"]:
                        return {
                            "name": "OUT-1",
                            "task_delivery": "TDL-1",
                            "official_score": None,
                            "grading_status": "Released",
                            "is_published": 1,
                        }
                if doctype == "Task Delivery":
                    return {
                        "name": "TDL-1",
                        "student_group": "GRP-1",
                        "delivery_mode": "Assess",
                        "grading_mode": "Points",
                        "allow_feedback": 0,
                    }
                return None

            frappe.db.get_value = fake_get_value

            module = _import_fresh_gradebook()
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None

            with self.assertRaises(StubValidationError):
                module.update_task_student("OUT-1", {"status": "Needs Review"})

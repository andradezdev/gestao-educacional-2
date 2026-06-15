# ifitwala_ed/assessment/api/test_gradebook_completion.py

from __future__ import annotations

import types
from unittest import TestCase

from ifitwala_ed.assessment.api.gradebook_test_utils import (
    _gradebook_stub_modules,
    _import_fresh_gradebook,
)
from ifitwala_ed.tests.frappe_stubs import StubValidationError, stubbed_frappe


class TestGradebookCompletion(TestCase):
    def test_batch_mark_completion_uses_contributions_for_assessed_completion(self):
        submitted_payloads = []
        task_contribution_service = types.ModuleType("ifitwala_ed.assessment.task_contribution_service")

        def fake_submit_contribution(payload, contributor=None):
            submitted_payloads.append((payload, contributor))
            return {
                "outcome_update": {
                    "outcome": payload.get("task_outcome"),
                    "grading_status": "Finalized",
                }
            }

        task_contribution_service.submit_contribution = fake_submit_contribution
        feedback_service = types.ModuleType("ifitwala_ed.assessment.task_feedback_service")
        feedback_service.build_publication_state_map = lambda outcome_ids: {
            outcome_id: {
                "is_visible_to_any_audience": outcome_id == "OUT-3",
                "visible_to_student": outcome_id == "OUT-3",
                "visible_to_guardian": outcome_id == "OUT-3",
                "feedback_visibility": "student_and_guardian" if outcome_id == "OUT-3" else "hidden",
                "grade_visibility": "student_and_guardian" if outcome_id == "OUT-3" else "hidden",
            }
            for outcome_id in outcome_ids or []
        }

        with stubbed_frappe(
            extra_modules=_gradebook_stub_modules(
                task_contribution_service=task_contribution_service,
                task_feedback_service=feedback_service,
            )
        ) as frappe:
            frappe.session.user = "teacher@example.com"

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Delivery" and name == "TDL-1":
                    return {
                        "name": "TDL-1",
                        "student_group": "GRP-1",
                        "delivery_mode": "Assess",
                        "grading_mode": "Completion",
                    }
                return None

            def fake_get_all(doctype, filters=None, fields=None, order_by=None, limit=0, pluck=None):
                if doctype == "Task Outcome":
                    self.assertEqual(filters["task_delivery"], "TDL-1")
                    self.assertEqual(filters["name"], ["in", ["OUT-1", "OUT-2", "OUT-3"]])
                    return [
                        {"name": "OUT-1", "is_complete": 0, "is_published": 0},
                        {"name": "OUT-2", "is_complete": 1, "is_published": 0},
                        {"name": "OUT-3", "is_complete": 0, "is_published": 1},
                    ]
                return []

            frappe.db.get_value = fake_get_value
            frappe.get_all = fake_get_all

            module = _import_fresh_gradebook()
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None

            payload = module.batch_mark_completion(
                {
                    "task_delivery": "TDL-1",
                    "outcome_ids": ["OUT-1", "OUT-2", "OUT-3"],
                    "target_complete": True,
                }
            )

        self.assertEqual(
            submitted_payloads,
            [
                (
                    {"task_outcome": "OUT-1", "judgment_code": "complete"},
                    "teacher@example.com",
                )
            ],
        )
        self.assertEqual(payload["updated_count"], 1)
        self.assertEqual(payload["already_complete_count"], 1)
        self.assertEqual(payload["skipped_published_count"], 1)
        self.assertEqual(
            payload["updated"],
            [{"outcome": "OUT-1", "is_complete": 1, "grading_status": "Finalized"}],
        )

    def test_batch_mark_completion_uses_assign_only_completion_service(self):
        completion_calls = []
        task_outcome_service = types.ModuleType("ifitwala_ed.assessment.task_outcome_service")

        def fake_set_assign_only_completion(outcome_id, *, is_complete, ignore_permissions=False):
            completion_calls.append((outcome_id, is_complete, ignore_permissions))
            return {"outcome": outcome_id, "is_complete": 1, "completed_on": "2026-04-25 09:00:00"}

        task_outcome_service.set_assign_only_completion = fake_set_assign_only_completion

        with stubbed_frappe(extra_modules=_gradebook_stub_modules(task_outcome_service=task_outcome_service)) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Delivery" and name == "TDL-1":
                    return {
                        "name": "TDL-1",
                        "student_group": "GRP-1",
                        "delivery_mode": "Assign Only",
                        "grading_mode": None,
                    }
                return None

            def fake_get_all(doctype, filters=None, fields=None, order_by=None, limit=0, pluck=None):
                if doctype == "Task Outcome":
                    return [{"name": "OUT-1", "is_complete": 0, "is_published": 0}]
                return []

            frappe.db.get_value = fake_get_value
            frappe.get_all = fake_get_all

            module = _import_fresh_gradebook()
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None

            payload = module.batch_mark_completion({"task_delivery": "TDL-1"})

        self.assertEqual(completion_calls, [("OUT-1", 1, False)])
        self.assertEqual(payload["updated_count"], 1)
        self.assertEqual(
            payload["updated"],
            [
                {
                    "outcome": "OUT-1",
                    "is_complete": 1,
                    "completed_on": "2026-04-25 09:00:00",
                }
            ],
        )

    def test_batch_mark_completion_rejects_non_completion_tasks(self):
        with stubbed_frappe(extra_modules=_gradebook_stub_modules()) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Delivery" and name == "TDL-1":
                    return {
                        "name": "TDL-1",
                        "student_group": "GRP-1",
                        "delivery_mode": "Assess",
                        "grading_mode": "Points",
                    }
                return None

            frappe.db.get_value = fake_get_value

            module = _import_fresh_gradebook()
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None

            with self.assertRaises(StubValidationError):
                module.batch_mark_completion({"task_delivery": "TDL-1"})

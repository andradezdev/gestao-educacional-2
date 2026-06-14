# ifitwala_ed/assessment/api/test_gradebook_grid.py

from __future__ import annotations

import types
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import stubbed_frappe

from ifitwala_ed.assessment.api.gradebook_test_utils import (
    _gradebook_stub_modules,
    _import_fresh_gradebook,
)


class TestGradebookGrid(TestCase):
    def test_get_task_gradebook_includes_submission_status_for_evidence_inbox_routing(self):
        with stubbed_frappe(extra_modules=_gradebook_stub_modules()) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Delivery" and name == "TDL-1":
                    return {
                        "name": "TDL-1",
                        "task": "TASK-1",
                        "student_group": "GRP-1",
                        "due_date": "2026-04-03 10:00:00",
                        "delivery_mode": "Collect Work",
                        "grading_mode": "None",
                        "allow_feedback": 1,
                        "max_points": None,
                        "rubric_version": None,
                        "rubric_scoring_strategy": None,
                    }
                if doctype == "Task" and name == "TASK-1":
                    return {"name": "TASK-1", "title": "Science Journal", "task_type": "Assignment"}
                return None

            def fake_get_all(doctype, filters=None, fields=None, order_by=None, limit=0, pluck=None):
                if doctype == "Task Outcome":
                    return [
                        {
                            "name": "OUT-1",
                            "student": "STU-1",
                            "grading_status": "Not Started",
                            "procedural_status": "Submitted",
                            "submission_status": "Late",
                            "has_submission": 1,
                            "has_new_submission": 1,
                            "is_complete": 0,
                            "official_score": None,
                            "official_feedback": None,
                            "is_published": 0,
                            "modified": "2026-04-18 10:10:00",
                        }
                    ]
                return []

            frappe.db.get_value = fake_get_value
            frappe.get_all = fake_get_all

            module = _import_fresh_gradebook()
            module.gradebook_support._can_read_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None
            module.gradebook_support._get_student_display_map = lambda student_ids: {"STU-1": "Ada Lovelace"}
            module.gradebook_support._get_student_meta_map = lambda student_ids: {
                "STU-1": {"name": "STU-1", "student_id": "S-001", "student_image": None}
            }
            module.gradebook_support._build_delivery_criteria_payload = lambda delivery: []
            module.gradebook_support._get_outcome_criteria_rows = lambda outcome_ids: {}

            payload = module.get_task_gradebook("TDL-1")

        self.assertEqual(payload["task"]["delivery_type"], "Collect Work")
        self.assertEqual(payload["students"][0]["submission_status"], "Late")
        self.assertEqual(payload["students"][0]["has_new_submission"], 1)

    def test_fetch_group_tasks_exposes_grading_mode_and_comment_flag(self):
        with stubbed_frappe(extra_modules=_gradebook_stub_modules()) as frappe:

            def fake_get_all(doctype, filters=None, fields=None, order_by=None, limit=0):
                if doctype == "Task Delivery":
                    return [
                        {
                            "name": "TDL-0001",
                            "task": "TASK-1",
                            "due_date": "2026-04-03 10:00:00",
                            "delivery_mode": "Assess",
                            "grading_mode": "Criteria",
                            "allow_feedback": 1,
                            "max_points": None,
                            "rubric_scoring_strategy": "Separate Criteria",
                        }
                    ]
                if doctype == "Task":
                    return [{"name": "TASK-1", "title": "Rubric reflection", "task_type": "Assignment"}]
                return []

            frappe.get_all = fake_get_all

            module = _import_fresh_gradebook()
            module.gradebook_support._can_read_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None

            payload = module.fetch_group_tasks("GRP-1")

        self.assertEqual(
            payload,
            {
                "tasks": [
                    {
                        "name": "TDL-0001",
                        "title": "Rubric reflection",
                        "due_date": "2026-04-03 10:00:00",
                        "status": None,
                        "grading_mode": "Criteria",
                        "allow_feedback": 1,
                        "rubric_scoring_strategy": "Separate Criteria",
                        "points": 0,
                        "binary": 0,
                        "criteria": 1,
                        "observations": 0,
                        "max_points": None,
                        "task_type": "Assignment",
                        "delivery_type": "Assess",
                    }
                ]
            },
        )

    def test_get_grid_returns_bounded_overview_payload_for_selected_group(self):
        feedback_service = types.ModuleType("ifitwala_ed.assessment.task_feedback_service")
        feedback_service.build_publication_state_map = lambda outcome_ids: {
            outcome_id: {
                "feedback_visibility": "student_and_guardian" if outcome_id == "OUT-2" else "hidden",
                "grade_visibility": "student_and_guardian" if outcome_id == "OUT-2" else "hidden",
                "visible_to_student": outcome_id == "OUT-2",
                "visible_to_guardian": outcome_id == "OUT-2",
                "is_visible_to_any_audience": outcome_id == "OUT-2",
                "derived_from_legacy_outcome": True,
                "legacy_outcome_published": outcome_id == "OUT-2",
                "legacy_published_on": None,
                "legacy_published_by": None,
                "task_submission": None,
                "workspace_id": None,
            }
            for outcome_id in outcome_ids or []
        }

        with stubbed_frappe(extra_modules=_gradebook_stub_modules(task_feedback_service=feedback_service)) as frappe:

            def fake_get_all(doctype, filters=None, fields=None, order_by=None, limit=0, pluck=None):
                if doctype == "Task Delivery":
                    return [
                        {
                            "name": "TDL-0002",
                            "task": "TASK-2",
                            "grading_mode": "Points",
                            "rubric_scoring_strategy": None,
                            "due_date": "2026-04-04 10:00:00",
                            "delivery_mode": "Assess",
                            "allow_feedback": 0,
                            "max_points": 20,
                        },
                        {
                            "name": "TDL-0001",
                            "task": "TASK-1",
                            "grading_mode": "Criteria",
                            "rubric_scoring_strategy": "Separate Criteria",
                            "due_date": "2026-04-03 10:00:00",
                            "delivery_mode": "Assess",
                            "allow_feedback": 1,
                            "max_points": None,
                        },
                    ]
                if doctype == "Task":
                    return [
                        {"name": "TASK-1", "title": "Rubric reflection", "task_type": "Assignment"},
                        {"name": "TASK-2", "title": "Quiz score", "task_type": "Quiz"},
                    ]
                if doctype == "Task Outcome":
                    return [
                        {
                            "name": "OUT-1",
                            "task_delivery": "TDL-0001",
                            "student": "STU-1",
                            "grading_status": "Needs Review",
                            "procedural_status": None,
                            "has_submission": 1,
                            "has_new_submission": 1,
                            "official_score": None,
                            "official_grade": None,
                            "official_grade_value": None,
                            "official_feedback": "Great detail.",
                            "is_complete": 0,
                            "is_published": 0,
                        },
                        {
                            "name": "OUT-2",
                            "task_delivery": "TDL-0002",
                            "student": "STU-1",
                            "grading_status": "Released",
                            "procedural_status": None,
                            "has_submission": 1,
                            "has_new_submission": 0,
                            "official_score": 18,
                            "official_grade": "A",
                            "official_grade_value": "A",
                            "official_feedback": None,
                            "is_complete": 0,
                            "is_published": 1,
                        },
                    ]
                if doctype == "Task Outcome Criterion":
                    return [
                        {
                            "parent": "OUT-1",
                            "assessment_criteria": "CRIT-1",
                            "level": "Secure",
                            "level_points": 4,
                        }
                    ]
                return []

            frappe.get_all = fake_get_all

            module = _import_fresh_gradebook()
            module.gradebook_support._can_read_gradebook = lambda: True
            module.gradebook_support._resolve_gradebook_scope = lambda school, academic_year, course: {
                "courses": [course] if course else [],
                "student_groups": ["GRP-1"],
            }
            module.gradebook_support._assert_group_access = lambda student_group: None
            module.gradebook_support._get_student_display_map = lambda student_ids: {"STU-1": "Ada Lovelace"}
            module.gradebook_support._get_student_meta_map = lambda student_ids: {
                "STU-1": {"student_id": "S-001", "student_image": None}
            }

            payload = module.get_grid(
                {
                    "school": "SCH-1",
                    "academic_year": "2025-2026",
                    "student_group": "GRP-1",
                    "limit": 2,
                }
            )

        self.assertEqual(
            payload["deliveries"],
            [
                {
                    "delivery_id": "TDL-0001",
                    "task_title": "Rubric reflection",
                    "grading_mode": "Criteria",
                    "rubric_scoring_strategy": "Separate Criteria",
                    "due_date": "2026-04-03 10:00:00",
                    "delivery_mode": "Assess",
                    "allow_feedback": 1,
                    "max_points": None,
                    "task_type": "Assignment",
                },
                {
                    "delivery_id": "TDL-0002",
                    "task_title": "Quiz score",
                    "grading_mode": "Points",
                    "rubric_scoring_strategy": None,
                    "due_date": "2026-04-04 10:00:00",
                    "delivery_mode": "Assess",
                    "allow_feedback": 0,
                    "max_points": 20.0,
                    "task_type": "Quiz",
                },
            ],
        )
        self.assertEqual(
            payload["students"],
            [
                {
                    "student": "STU-1",
                    "student_name": "Ada Lovelace",
                    "student_id": "S-001",
                    "student_image": None,
                    "insight_summary": None,
                }
            ],
        )
        self.assertEqual(
            payload["cells"][0]["official"]["criteria"], [{"criteria": "CRIT-1", "level": "Secure", "points": 4}]
        )
        self.assertTrue(payload["cells"][0]["flags"]["has_new_submission"])
        self.assertTrue(payload["cells"][1]["flags"]["is_published"])

    def test_get_grid_filters_by_assessment_scope_on_the_delivery_query(self):
        captured_filters = []

        with stubbed_frappe(extra_modules=_gradebook_stub_modules()) as frappe:

            def fake_get_all(doctype, filters=None, fields=None, order_by=None, limit=0, pluck=None):
                if doctype == "Task Delivery":
                    captured_filters.append(dict(filters or {}))
                return []

            frappe.get_all = fake_get_all

            module = _import_fresh_gradebook()
            module.gradebook_support._can_read_gradebook = lambda: True
            module.gradebook_support._resolve_gradebook_scope = lambda school, academic_year, course: {}
            module.gradebook_support._assert_group_access = lambda student_group: None

            base_filters = {
                "school": "SCH-1",
                "academic_year": "2025-2026",
                "student_group": "GRP-1",
                "limit": 1,
            }
            module.get_grid({**base_filters, "assessment_scope": "graded"})
            module.get_grid({**base_filters, "assessment_scope": "not_graded"})
            module.get_grid({**base_filters, "assessment_scope": "all"})

        self.assertEqual(captured_filters[0]["delivery_mode"], "Assess")
        self.assertEqual(captured_filters[1]["delivery_mode"], ["in", ["Collect Work", "Assign Only"]])
        self.assertNotIn("delivery_mode", captured_filters[2])

    def test_get_grid_hides_grade_value_when_official_grade_is_missing(self):
        with stubbed_frappe(extra_modules=_gradebook_stub_modules()) as frappe:

            def fake_get_all(doctype, filters=None, fields=None, order_by=None, limit=0, pluck=None):
                if doctype == "Task Delivery":
                    return [
                        {
                            "name": "TDL-0001",
                            "task": "TASK-1",
                            "grading_mode": "Points",
                            "rubric_scoring_strategy": None,
                            "due_date": "2026-04-03 10:00:00",
                            "delivery_mode": "Assess",
                            "allow_feedback": 1,
                            "max_points": 20,
                        }
                    ]
                if doctype == "Task":
                    return [{"name": "TASK-1", "title": "Quiz score", "task_type": "Quiz"}]
                if doctype == "Task Outcome":
                    return [
                        {
                            "name": "OUT-1",
                            "task_delivery": "TDL-0001",
                            "student": "STU-1",
                            "grading_status": "Finalized",
                            "procedural_status": None,
                            "has_submission": 1,
                            "has_new_submission": 0,
                            "official_score": 20,
                            "official_grade": None,
                            "official_grade_value": 0,
                            "official_feedback": "",
                            "is_complete": 0,
                            "is_published": 0,
                        }
                    ]
                return []

            frappe.get_all = fake_get_all

            module = _import_fresh_gradebook()
            module.gradebook_support._can_read_gradebook = lambda: True
            module.gradebook_support._resolve_gradebook_scope = lambda school, academic_year, course: {}
            module.gradebook_support._assert_group_access = lambda student_group: None
            module.gradebook_support._get_student_display_map = lambda student_ids: {"STU-1": "Ada Lovelace"}
            module.gradebook_support._get_student_meta_map = lambda student_ids: {
                "STU-1": {"student_id": "S-001", "student_image": None}
            }

            payload = module.get_grid(
                {
                    "school": "SCH-1",
                    "academic_year": "2025-2026",
                    "limit": 1,
                }
            )

        self.assertEqual(payload["cells"][0]["official"]["score"], 20)
        self.assertIsNone(payload["cells"][0]["official"]["grade"])
        self.assertIsNone(payload["cells"][0]["official"]["grade_value"])


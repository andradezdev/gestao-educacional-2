# ifitwala_ed/assessment/api/test_gradebook_quiz_review.py

from __future__ import annotations

from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import stubbed_frappe

from ifitwala_ed.assessment.api.gradebook_test_utils import (
    _gradebook_stub_modules,
    _import_fresh_gradebook,
)


class TestGradebookQuizReview(TestCase):
    def test_get_task_quiz_manual_review_groups_manual_rows_by_question(self):
        with stubbed_frappe(extra_modules=_gradebook_stub_modules()) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Delivery":
                    return {
                        "name": "TDL-1",
                        "task": "TASK-QUIZ-1",
                        "student_group": "GRP-1",
                        "due_date": "2026-04-08 10:00:00",
                        "delivery_mode": "Assess",
                        "grading_mode": "Points",
                        "allow_feedback": 0,
                        "max_points": 4,
                        "rubric_version": None,
                        "rubric_scoring_strategy": None,
                        "quiz_pass_percentage": 75,
                    }
                if doctype == "Task":
                    return {"name": "TASK-QUIZ-1", "title": "Unit Reflection Quiz", "task_type": "Quiz"}
                return None

            def fake_get_all(doctype, filters=None, fields=None, order_by=None, limit=0, pluck=None):
                if doctype == "Task Outcome":
                    return [
                        {"name": "OUT-1", "student": "STU-1", "grading_status": "Needs Review"},
                        {"name": "OUT-2", "student": "STU-2", "grading_status": "Finalized"},
                    ]
                if doctype == "Quiz Attempt":
                    return [
                        {
                            "name": "QAT-1",
                            "task_outcome": "OUT-1",
                            "student": "STU-1",
                            "attempt_number": 1,
                            "status": "Needs Review",
                            "submitted_on": "2026-04-08 10:15:00",
                            "score": None,
                            "percentage": None,
                            "passed": 0,
                            "requires_manual_review": 1,
                        },
                        {
                            "name": "QAT-2",
                            "task_outcome": "OUT-2",
                            "student": "STU-2",
                            "attempt_number": 1,
                            "status": "Submitted",
                            "submitted_on": "2026-04-08 10:25:00",
                            "score": 4,
                            "percentage": 100,
                            "passed": 1,
                            "requires_manual_review": 0,
                        },
                    ]
                if doctype == "Quiz Attempt Item":
                    return [
                        {
                            "name": "QAI-1",
                            "quiz_attempt": "QAT-1",
                            "quiz_question": "QQ-1",
                            "position": 1,
                            "question_type": "Essay",
                            "prompt_html": "<p>Explain your reasoning.</p>",
                            "option_payload": None,
                            "response_text": "Student one response",
                            "response_payload": None,
                            "awarded_score": None,
                            "requires_manual_grading": 1,
                        },
                        {
                            "name": "QAI-2",
                            "quiz_attempt": "QAT-2",
                            "quiz_question": "QQ-1",
                            "position": 1,
                            "question_type": "Essay",
                            "prompt_html": "<p>Explain your reasoning.</p>",
                            "option_payload": None,
                            "response_text": "Student two response",
                            "response_payload": None,
                            "awarded_score": 1,
                            "requires_manual_grading": 0,
                        },
                    ]
                if doctype == "Quiz Question":
                    return [{"name": "QQ-1", "title": "Explain the pattern"}]
                return []

            frappe.db.get_value = fake_get_value
            frappe.get_all = fake_get_all

            module = _import_fresh_gradebook()
            module.gradebook_support._can_read_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None
            module.gradebook_support._get_student_display_map = lambda student_ids: {
                "STU-1": "Ada Lovelace",
                "STU-2": "Grace Hopper",
            }
            module.gradebook_support._get_student_meta_map = lambda student_ids: {
                "STU-1": {"name": "STU-1", "student_id": "S-001", "student_image": None},
                "STU-2": {"name": "STU-2", "student_id": "S-002", "student_image": None},
            }

            payload = module.get_task_quiz_manual_review("TDL-1", view_mode="question")

        self.assertEqual(payload["task"]["title"], "Unit Reflection Quiz")
        self.assertEqual(payload["summary"]["manual_item_count"], 2)
        self.assertEqual(payload["summary"]["pending_item_count"], 1)
        self.assertEqual(payload["view_mode"], "question")
        self.assertEqual(payload["selected_question"], {"quiz_question": "QQ-1", "title": "Explain the pattern"})
        self.assertEqual([row["student_name"] for row in payload["rows"]], ["Ada Lovelace", "Grace Hopper"])
        self.assertEqual(payload["rows"][0]["requires_manual_grading"], 1)
        self.assertEqual(payload["rows"][1]["awarded_score"], 1.0)

    def test_save_task_quiz_manual_review_updates_items_and_refreshes_attempts(self):
        set_value_calls = []
        refresh_calls = []
        modules = _gradebook_stub_modules()
        modules["ifitwala_ed.assessment.quiz_service"].refresh_attempt = lambda attempt_id, **kwargs: (
            refresh_calls.append((attempt_id, kwargs)) or {"attempt": {"name": attempt_id}}
        )

        with stubbed_frappe(extra_modules=modules) as frappe:

            def fake_get_value(doctype, name, fieldname=None, as_dict=False):
                if doctype == "Task Delivery":
                    return {
                        "name": "TDL-1",
                        "task": "TASK-QUIZ-1",
                        "student_group": "GRP-1",
                        "due_date": "2026-04-08 10:00:00",
                        "delivery_mode": "Assess",
                        "grading_mode": "Points",
                        "allow_feedback": 0,
                        "max_points": 4,
                        "rubric_version": None,
                        "rubric_scoring_strategy": None,
                    }
                if doctype == "Task":
                    return {"name": "TASK-QUIZ-1", "title": "Unit Reflection Quiz", "task_type": "Quiz"}
                return None

            def fake_get_all(doctype, filters=None, fields=None, order_by=None, limit=0, pluck=None):
                if doctype == "Quiz Attempt Item":
                    return [
                        {"name": "QAI-1", "quiz_attempt": "QAT-1", "question_type": "Essay"},
                        {"name": "QAI-2", "quiz_attempt": "QAT-2", "question_type": "Essay"},
                    ]
                if doctype == "Quiz Attempt":
                    return [
                        {
                            "name": "QAT-1",
                            "task_delivery": "TDL-1",
                            "student": "STU-1",
                            "status": "Needs Review",
                        },
                        {
                            "name": "QAT-2",
                            "task_delivery": "TDL-1",
                            "student": "STU-2",
                            "status": "Submitted",
                        },
                    ]
                return []

            frappe.db.get_value = fake_get_value
            frappe.get_all = fake_get_all
            frappe.db.set_value = lambda doctype, name, values, update_modified=False: set_value_calls.append(
                (doctype, name, values, update_modified)
            )

            module = _import_fresh_gradebook()
            module.gradebook_support._can_write_gradebook = lambda: True
            module.gradebook_support._assert_group_access = lambda student_group: None

            payload = module.save_task_quiz_manual_review(
                "TDL-1",
                grades=[
                    {"item_id": "QAI-1", "awarded_score": 1},
                    {"item_id": "QAI-2", "awarded_score": 0.5},
                ],
            )

        self.assertEqual(
            set_value_calls,
            [
                ("Quiz Attempt Item", "QAI-1", {"awarded_score": 1.0}, True),
                ("Quiz Attempt Item", "QAI-2", {"awarded_score": 0.5}, True),
            ],
        )
        self.assertEqual(
            refresh_calls,
            [
                (
                    "QAT-1",
                    {"user": "unit.test@example.com", "mark_submitted": True, "student": "STU-1"},
                ),
                (
                    "QAT-2",
                    {"user": "unit.test@example.com", "mark_submitted": True, "student": "STU-2"},
                ),
            ],
        )
        self.assertEqual(payload, {"updated_item_count": 2, "updated_attempt_count": 2})


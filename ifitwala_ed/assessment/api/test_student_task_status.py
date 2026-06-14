from __future__ import annotations

from datetime import datetime, timedelta
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


class TestStudentTaskStatus(TestCase):
    def test_student_work_done_uses_explicit_and_derived_statuses(self):
        with stubbed_frappe():
            module = import_fresh("ifitwala_ed.assessment.api.student_task_status")

        self.assertTrue(module.is_student_work_done({"is_done": 1, "submission_status": ""}))
        self.assertTrue(module.is_student_work_done({"submission_status": "Submitted"}))
        self.assertTrue(module.is_student_work_done({"grading_status": "Released"}))
        self.assertFalse(module.is_student_work_done({"submission_status": "Draft", "grading_status": "In Progress"}))

    def test_student_work_actionable_respects_quiz_state(self):
        with stubbed_frappe():
            module = import_fresh("ifitwala_ed.assessment.api.student_task_status")

        self.assertTrue(module.is_student_work_actionable({"task_type": "Quiz", "quiz_state": {"can_start": 1}}))
        self.assertFalse(module.is_student_work_actionable({"task_type": "Quiz", "quiz_state": {}}))
        self.assertFalse(module.is_student_work_actionable({"submission_status": "Submitted"}))
        self.assertTrue(module.is_student_work_actionable({"submission_status": "Draft"}))

    def test_status_label_prefers_completion_then_due_state(self):
        anchor = datetime(2026, 6, 1, 9, 0, 0)

        with stubbed_frappe():
            module = import_fresh("ifitwala_ed.assessment.api.student_task_status")

        self.assertEqual(module.build_student_task_status_label({"is_complete": 1}, anchor), "Completed")
        self.assertEqual(
            module.build_student_task_status_label({"due_date": anchor - timedelta(days=1)}, anchor),
            "Overdue",
        )
        self.assertEqual(module.build_student_task_status_label({"due_date": anchor}, anchor), "Due Today")
        self.assertEqual(
            module.build_student_task_status_label({"available_from": anchor + timedelta(days=1)}, anchor),
            "Not Yet Open",
        )

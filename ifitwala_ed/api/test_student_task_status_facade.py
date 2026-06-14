from __future__ import annotations

from datetime import datetime
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


class TestStudentTaskStatusFacade(TestCase):
    def test_root_student_task_status_facade_delegates_helpers(self):
        calls: list[tuple[str, object]] = []

        with stubbed_frappe():
            module = import_fresh("ifitwala_ed.api.student_task_status")

            def fake_is_done(row):
                calls.append(("is_student_work_done", row))
                return True

            def fake_is_actionable(row):
                calls.append(("is_student_work_actionable", row))
                return False

            def fake_label(row, anchor_dt):
                calls.append(("build_student_task_status_label", {"row": row, "anchor_dt": anchor_dt}))
                return "Open"

            module._impl.is_student_work_done = fake_is_done
            module._impl.is_student_work_actionable = fake_is_actionable
            module._impl.build_student_task_status_label = fake_label

            done = module.is_student_work_done({"name": "OUT-1"})
            actionable = module.is_student_work_actionable({"name": "OUT-2"})
            label = module.build_student_task_status_label({"name": "OUT-3"}, datetime(2026, 6, 1))

        self.assertTrue(done)
        self.assertFalse(actionable)
        self.assertEqual(label, "Open")
        self.assertEqual(
            [name for name, _payload in calls],
            [
                "is_student_work_done",
                "is_student_work_actionable",
                "build_student_task_status_label",
            ],
        )

    def test_root_student_task_status_facade_exposes_constants(self):
        with stubbed_frappe():
            module = import_fresh("ifitwala_ed.api.student_task_status")

        self.assertIs(module.DONE_SUBMISSION_STATUSES, module._impl.DONE_SUBMISSION_STATUSES)
        self.assertIs(module.DONE_GRADING_STATUSES, module._impl.DONE_GRADING_STATUSES)

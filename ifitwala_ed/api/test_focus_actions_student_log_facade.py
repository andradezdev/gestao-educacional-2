from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


class TestFocusActionsStudentLogFacade(TestCase):
    def test_root_focus_actions_student_log_facade_delegates_actions(self):
        calls: dict[str, object] = {}
        impl = ModuleType("ifitwala_ed.students.api.focus_actions_student_log")

        def fake_submit_student_log_follow_up(focus_item_id, follow_up, client_request_id=None):
            calls["submit"] = {
                "focus_item_id": focus_item_id,
                "follow_up": follow_up,
                "client_request_id": client_request_id,
            }
            return {"status": "created"}

        def fake_review_student_log_outcome(
            focus_item_id,
            decision,
            follow_up_person=None,
            client_request_id=None,
        ):
            calls["review"] = {
                "focus_item_id": focus_item_id,
                "decision": decision,
                "follow_up_person": follow_up_person,
                "client_request_id": client_request_id,
            }
            return {"status": "processed"}

        impl.submit_student_log_follow_up = fake_submit_student_log_follow_up
        impl.review_student_log_outcome = fake_review_student_log_outcome

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.focus_actions_student_log": impl}):
            module = import_fresh("ifitwala_ed.api.focus_actions_student_log")
            submitted = module.submit_student_log_follow_up(
                focus_item_id="focus-1",
                follow_up="Followed up.",
                client_request_id="req-1",
            )
            reviewed = module.review_student_log_outcome(
                focus_item_id="focus-2",
                decision="reassign",
                follow_up_person="teacher@example.com",
                client_request_id="req-2",
            )

        self.assertEqual(submitted, {"status": "created"})
        self.assertEqual(reviewed, {"status": "processed"})
        self.assertEqual(
            calls["submit"],
            {"focus_item_id": "focus-1", "follow_up": "Followed up.", "client_request_id": "req-1"},
        )
        self.assertEqual(
            calls["review"],
            {
                "focus_item_id": "focus-2",
                "decision": "reassign",
                "follow_up_person": "teacher@example.com",
                "client_request_id": "req-2",
            },
        )

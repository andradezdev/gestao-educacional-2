from __future__ import annotations

from unittest import TestCase

from ifitwala_ed.assessment.api.test_released_feedback import _released_feedback_stub_modules
from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


class TestReleasedFeedbackFacade(TestCase):
    def test_root_released_feedback_facade_delegates_detail_reads(self):
        calls: list[tuple[str, str]] = []

        with stubbed_frappe(extra_modules=_released_feedback_stub_modules()):
            module = import_fresh("ifitwala_ed.api.released_feedback")

            def fake_student_detail(outcome_id):
                calls.append(("student", outcome_id))
                return {"audience": "student"}

            def fake_guardian_detail(outcome_id):
                calls.append(("guardian", outcome_id))
                return {"audience": "guardian"}

            module._impl.get_student_released_feedback_detail = fake_student_detail
            module._impl.get_guardian_released_feedback_detail = fake_guardian_detail

            student_payload = module.get_student_released_feedback_detail("OUT-1")
            guardian_payload = module.get_guardian_released_feedback_detail("OUT-2")

        self.assertEqual(student_payload, {"audience": "student"})
        self.assertEqual(guardian_payload, {"audience": "guardian"})
        self.assertEqual(calls, [("student", "OUT-1"), ("guardian", "OUT-2")])

    def test_root_released_feedback_facade_delegates_student_mutations(self):
        calls: list[tuple[str, object]] = []

        with stubbed_frappe(extra_modules=_released_feedback_stub_modules()):
            module = import_fresh("ifitwala_ed.api.released_feedback")

            def fake_reply(payload=None, **kwargs):
                calls.append(("reply", {"payload": payload, "kwargs": kwargs}))
                return {"thread": {"thread_id": "TFT-1"}}

            def fake_state(payload=None, **kwargs):
                calls.append(("state", {"payload": payload, "kwargs": kwargs}))
                return {"thread": {"learner_state": "understood"}}

            def fake_export(outcome_id):
                calls.append(("export", outcome_id))
                return {"artifact": {"file_id": "FILE-1"}}

            module._impl.save_student_feedback_reply = fake_reply
            module._impl.save_student_feedback_thread_state = fake_state
            module._impl.export_student_released_feedback_pdf = fake_export

            reply_payload = module.save_student_feedback_reply(payload={"outcome_id": "OUT-1"}, draft=True)
            state_payload = module.save_student_feedback_thread_state(payload={"outcome_id": "OUT-1"}, state=True)
            export_payload = module.export_student_released_feedback_pdf("OUT-1")

        self.assertEqual(reply_payload, {"thread": {"thread_id": "TFT-1"}})
        self.assertEqual(state_payload, {"thread": {"learner_state": "understood"}})
        self.assertEqual(export_payload, {"artifact": {"file_id": "FILE-1"}})
        self.assertEqual(
            calls,
            [
                ("reply", {"payload": {"outcome_id": "OUT-1"}, "kwargs": {"draft": True}}),
                ("state", {"payload": {"outcome_id": "OUT-1"}, "kwargs": {"state": True}}),
                ("export", "OUT-1"),
            ],
        )

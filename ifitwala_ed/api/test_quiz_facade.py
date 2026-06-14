from __future__ import annotations

from unittest import TestCase

from ifitwala_ed.assessment.api.test_quiz import _quiz_stub_modules
from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


class TestQuizFacade(TestCase):
    def test_root_quiz_facade_delegates_staff_question_bank_reads(self):
        calls: dict[str, object] = {}

        with stubbed_frappe(extra_modules=_quiz_stub_modules()):
            module = import_fresh("ifitwala_ed.api.quiz")

            def fake_list_question_banks(course=None):
                calls["course"] = course
                return [{"name": "QBK-1"}]

            module._impl.list_question_banks = fake_list_question_banks

            payload = module.list_question_banks(course="COURSE-1")

        self.assertEqual(payload, [{"name": "QBK-1"}])
        self.assertEqual(calls["course"], "COURSE-1")

    def test_root_quiz_facade_delegates_staff_question_bank_writes(self):
        calls: dict[str, object] = {}

        with stubbed_frappe(extra_modules=_quiz_stub_modules()):
            module = import_fresh("ifitwala_ed.api.quiz")

            def fake_save_question_bank(payload=None, **kwargs):
                calls["payload"] = payload
                calls["kwargs"] = kwargs
                return {"quiz_question_bank": "QBK-1"}

            module._impl.save_question_bank = fake_save_question_bank

            payload = module.save_question_bank(payload={"bank_title": "Cells"}, expected_modified="v1")

        self.assertEqual(payload, {"quiz_question_bank": "QBK-1"})
        self.assertEqual(calls["payload"], {"bank_title": "Cells"})
        self.assertEqual(calls["kwargs"], {"expected_modified": "v1"})

    def test_root_quiz_facade_delegates_student_runtime_methods(self):
        calls: list[tuple[str, object]] = []

        with stubbed_frappe(extra_modules=_quiz_stub_modules()):
            module = import_fresh("ifitwala_ed.api.quiz")

            def fake_open_session(task_delivery):
                calls.append(("open", task_delivery))
                return {"mode": "attempt"}

            def fake_save_attempt(payload=None, **kwargs):
                calls.append(("save", {"payload": payload, "kwargs": kwargs}))
                return {"attempt": "QAT-1"}

            def fake_submit_attempt(payload=None, **kwargs):
                calls.append(("submit", {"payload": payload, "kwargs": kwargs}))
                return {"attempt": {"name": "QAT-1"}}

            module._impl.open_session = fake_open_session
            module._impl.save_attempt = fake_save_attempt
            module._impl.submit_attempt = fake_submit_attempt

            open_payload = module.open_session(task_delivery="TDL-1")
            save_payload = module.save_attempt(payload={"attempt_id": "QAT-1"}, autosave=True)
            submit_payload = module.submit_attempt(payload={"attempt_id": "QAT-1"}, final=True)

        self.assertEqual(open_payload, {"mode": "attempt"})
        self.assertEqual(save_payload, {"attempt": "QAT-1"})
        self.assertEqual(submit_payload, {"attempt": {"name": "QAT-1"}})
        self.assertEqual(
            calls,
            [
                ("open", "TDL-1"),
                ("save", {"payload": {"attempt_id": "QAT-1"}, "kwargs": {"autosave": True}}),
                ("submit", {"payload": {"attempt_id": "QAT-1"}, "kwargs": {"final": True}}),
            ],
        )

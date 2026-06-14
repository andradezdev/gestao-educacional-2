from __future__ import annotations

from unittest import TestCase

from ifitwala_ed.assessment.api.test_task_submission_unit import _task_submission_stub_modules
from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


class TestTaskSubmissionFacade(TestCase):
    def test_root_task_submission_facade_delegates_create_or_resubmit(self):
        calls: dict[str, object] = {}

        with stubbed_frappe(extra_modules=_task_submission_stub_modules()):
            module = import_fresh("ifitwala_ed.api.task_submission")

            def fake_create_or_resubmit(payload=None, **kwargs):
                calls["payload"] = payload
                calls["kwargs"] = kwargs
                return {"submission_id": "TSU-1", "version": 2}

            module._impl.create_or_resubmit = fake_create_or_resubmit

            payload = module.create_or_resubmit(payload={"task_outcome": "OUT-1"}, upload_source="portal")

        self.assertEqual(payload, {"submission_id": "TSU-1", "version": 2})
        self.assertEqual(calls["payload"], {"task_outcome": "OUT-1"})
        self.assertEqual(calls["kwargs"], {"upload_source": "portal"})

    def test_root_task_submission_facade_delegates_latest_submission(self):
        calls: dict[str, object] = {}

        with stubbed_frappe(extra_modules=_task_submission_stub_modules()):
            module = import_fresh("ifitwala_ed.api.task_submission")

            def fake_get_latest_submission(outcome_id=None):
                calls["outcome_id"] = outcome_id
                return {"submission_id": "TSU-2"}

            module._impl.get_latest_submission = fake_get_latest_submission

            payload = module.get_latest_submission(outcome_id="OUT-2")

        self.assertEqual(payload, {"submission_id": "TSU-2"})
        self.assertEqual(calls["outcome_id"], "OUT-2")

    def test_root_task_submission_facade_exposes_assessment_helper_surface(self):
        with stubbed_frappe(extra_modules=_task_submission_stub_modules()):
            module = import_fresh("ifitwala_ed.api.task_submission")

        self.assertIs(module.serialize_task_submission_evidence, module._impl.serialize_task_submission_evidence)
        self.assertIs(module.select_task_submission_row, module._impl.select_task_submission_row)

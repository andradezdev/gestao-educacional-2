from __future__ import annotations

from unittest import TestCase

from ifitwala_ed.assessment.api.test_task_completion import _task_completion_stub_modules
from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


class TestTaskCompletionFacade(TestCase):
    def test_root_task_completion_facade_delegates_mark_complete(self):
        calls: dict[str, object] = {}

        with stubbed_frappe(extra_modules=_task_completion_stub_modules()):
            module = import_fresh("ifitwala_ed.api.task_completion")

            def fake_mark_assign_only_complete(payload=None, **kwargs):
                calls["payload"] = payload
                calls["kwargs"] = kwargs
                return {"task_outcome": "OUT-1", "is_complete": 1, "completed_on": None}

            module._impl.mark_assign_only_complete = fake_mark_assign_only_complete

            payload = module.mark_assign_only_complete(payload={"task_outcome": "OUT-1"}, autosave=True)

        self.assertEqual(payload, {"task_outcome": "OUT-1", "is_complete": 1, "completed_on": None})
        self.assertEqual(calls["payload"], {"task_outcome": "OUT-1"})
        self.assertEqual(calls["kwargs"], {"autosave": True})

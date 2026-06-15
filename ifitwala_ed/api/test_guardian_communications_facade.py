from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _guardian_communications_impl_stub():
    module = ModuleType("ifitwala_ed.students.api.guardian_communications")
    module.RECENT_WINDOW_DAYS = 90
    module.SOURCE_FILTERS = {"all", "course", "activity", "school", "pastoral", "cohort"}
    module.SOURCE_PRIORITY = ("course", "activity", "pastoral", "cohort", "school")

    def helper():
        return "helper"

    module._resolve_guardian_communication_context = helper
    return module


class TestGuardianCommunicationsFacade(TestCase):
    def test_root_guardian_communications_facade_delegates_public_methods(self):
        calls: dict[str, object] = {}
        impl = _guardian_communications_impl_stub()

        def fake_center(source=None, student=None, start=0, page_length=24):
            calls["center"] = {
                "source": source,
                "student": student,
                "start": start,
                "page_length": page_length,
            }
            return {"items": [{"item_id": "org::COMM-1"}]}

        def fake_unread_count():
            calls["unread"] = True
            return 3

        impl.get_guardian_communication_center = fake_center
        impl.get_guardian_portal_communication_unread_count = fake_unread_count

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.guardian_communications": impl}):
            module = import_fresh("ifitwala_ed.api.guardian_communications")
            self.assertEqual(
                module.get_guardian_communication_center(
                    source="school",
                    student="STU-1",
                    start="5",
                    page_length="10",
                ),
                {"items": [{"item_id": "org::COMM-1"}]},
            )
            self.assertEqual(module.get_guardian_portal_communication_unread_count(), 3)

        self.assertEqual(
            calls["center"],
            {"source": "school", "student": "STU-1", "start": "5", "page_length": "10"},
        )
        self.assertTrue(calls["unread"])
        self.assertEqual(module.RECENT_WINDOW_DAYS, 90)
        self.assertIs(module._resolve_guardian_communication_context, impl._resolve_guardian_communication_context)

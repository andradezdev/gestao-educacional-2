from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _guardian_attendance_impl_stub():
    module = ModuleType("ifitwala_ed.students.api.guardian_attendance")

    for name in (
        "_coerce_days",
        "_build_attendance_students",
        "_attendance_code_map",
        "_fallback_code_meta",
        "_detail_sort_key",
        "_resolve_day_state",
        "_public_detail",
    ):
        setattr(module, name, lambda *args, **kwargs: None)

    return module


class TestGuardianAttendanceFacade(TestCase):
    def test_root_guardian_attendance_facade_delegates_public_method(self):
        calls: dict[str, object] = {}
        impl = _guardian_attendance_impl_stub()

        def fake_get_guardian_attendance_snapshot(student=None, days=60):
            calls["snapshot"] = {"student": student, "days": days}
            return {"students": [{"student": "STU-1"}]}

        impl.get_guardian_attendance_snapshot = fake_get_guardian_attendance_snapshot

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.guardian_attendance": impl}):
            module = import_fresh("ifitwala_ed.api.guardian_attendance")
            self.assertEqual(
                module.get_guardian_attendance_snapshot(student="STU-1", days="30"),
                {"students": [{"student": "STU-1"}]},
            )

        self.assertEqual(calls["snapshot"], {"student": "STU-1", "days": "30"})
        self.assertIs(module._public_detail, impl._public_detail)

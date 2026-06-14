from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _student_attendance_impl_stub():
    module = ModuleType("ifitwala_ed.students.api.student_attendance")
    module.PORTAL_FULL_ACCESS_ROLES = {"Academic Admin"}
    module.PORTAL_GROUP_FIELDS = ["name", "student_group_name"]
    module.ATTENDANCE_CONTEXT_TTL = 300
    return module


class TestStudentAttendanceFacade(TestCase):
    def test_root_student_attendance_facade_delegates_public_methods(self):
        calls: dict[str, object] = {}
        impl = _student_attendance_impl_stub()

        def _record(name, value):
            def _inner(**kwargs):
                calls[name] = kwargs
                return value

            return _inner

        impl.fetch_portal_student_groups = _record("groups", [{"name": "SG-1"}])
        impl.fetch_school_filter_context = lambda: {"schools": []}
        impl.fetch_active_programs = _record("programs", [{"name": "PROG-1"}])
        impl.fetch_attendance_ledger_context = _record("ledger_context", {"student_groups": []})
        impl.fetch_attendance_tool_bootstrap = _record("bootstrap", {"attendance_codes": []})
        impl.fetch_attendance_tool_group_context = _record("group_context", {"meeting_dates": []})
        impl.fetch_attendance_tool_roster_context = _record("roster_context", {"roster": {}})
        impl.fetch_portal_academic_years = _record("academic_years", [{"name": "AY-1"}])
        impl.fetch_portal_terms = _record("terms", [{"name": "TERM-1"}])
        impl.get_weekend_days = _record("weekend_days", [6, 0])

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.student_attendance": impl}):
            module = import_fresh("ifitwala_ed.api.student_attendance")
            self.assertEqual(module.fetch_portal_student_groups(school="SCH-1", program="PROG-1"), [{"name": "SG-1"}])
            self.assertEqual(module.fetch_school_filter_context(), {"schools": []})
            self.assertEqual(module.fetch_active_programs(school="SCH-1"), [{"name": "PROG-1"}])
            self.assertEqual(
                module.fetch_attendance_ledger_context(
                    school="SCH-1",
                    program="PROG-1",
                    academic_year="AY-1",
                    term="TERM-1",
                    student_group="SG-1",
                ),
                {"student_groups": []},
            )
            self.assertEqual(
                module.fetch_attendance_tool_bootstrap(school="SCH-1", program="PROG-1", student_group="SG-1"),
                {"attendance_codes": []},
            )
            self.assertEqual(module.fetch_attendance_tool_group_context("SG-1"), {"meeting_dates": []})
            self.assertEqual(module.fetch_attendance_tool_roster_context("SG-1", "2026-03-12"), {"roster": {}})
            self.assertEqual(module.fetch_portal_academic_years(school="SCH-1"), [{"name": "AY-1"}])
            self.assertEqual(module.fetch_portal_terms(academic_year="AY-1", school="SCH-1"), [{"name": "TERM-1"}])
            self.assertEqual(module.get_weekend_days("SG-1"), [6, 0])

        self.assertEqual(module.PORTAL_FULL_ACCESS_ROLES, {"Academic Admin"})
        self.assertEqual(module.PORTAL_GROUP_FIELDS, ["name", "student_group_name"])
        self.assertEqual(module.ATTENDANCE_CONTEXT_TTL, 300)
        self.assertEqual(calls["groups"], {"school": "SCH-1", "program": "PROG-1"})
        self.assertEqual(calls["programs"], {"school": "SCH-1"})
        self.assertEqual(
            calls["ledger_context"],
            {
                "school": "SCH-1",
                "program": "PROG-1",
                "academic_year": "AY-1",
                "term": "TERM-1",
                "student_group": "SG-1",
            },
        )
        self.assertEqual(calls["bootstrap"], {"school": "SCH-1", "program": "PROG-1", "student_group": "SG-1"})
        self.assertEqual(calls["group_context"], {"student_group": "SG-1"})
        self.assertEqual(calls["roster_context"], {"student_group": "SG-1", "attendance_date": "2026-03-12"})
        self.assertEqual(calls["academic_years"], {"school": "SCH-1"})
        self.assertEqual(calls["terms"], {"academic_year": "AY-1", "school": "SCH-1"})
        self.assertEqual(calls["weekend_days"], {"student_group": "SG-1"})

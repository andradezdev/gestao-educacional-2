from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _student_groups_impl_stub():
    module = ModuleType("ifitwala_ed.students.api.student_groups")
    module.TRIAGE_ROLES = {"Academic Admin"}
    module.INSTRUCTOR_SCOPE_OVERRIDE_ROLES = {"Academic Admin"}
    module._user_roles = lambda user: {"Instructor"} if user else set()
    module._instructor_group_names = lambda user: {"SG-0001"} if user else set()
    module._base_group_filters = lambda program=None, course=None, cohort=None: {
        key: value
        for key, value in {
            "program": program,
            "course": course,
            "cohort": cohort,
        }.items()
        if value
    }
    module._has_broad_group_access = lambda roles: "Academic Admin" in roles
    return module


class TestStudentGroupsFacade(TestCase):
    def test_root_student_groups_facade_delegates_methods_and_helpers(self):
        calls: dict[str, object] = {}
        impl = _student_groups_impl_stub()

        def fake_fetch_groups(program=None, course=None, cohort=None):
            calls["fetch_groups"] = {
                "program": program,
                "course": course,
                "cohort": cohort,
            }
            return [{"name": "SG-0001"}]

        def fake_fetch_group_students(student_group, start=0, page_length=25):
            calls["fetch_group_students"] = {
                "student_group": student_group,
                "start": start,
                "page_length": page_length,
            }
            return {"students": [], "start": start + page_length, "total": 0}

        impl.fetch_groups = fake_fetch_groups
        impl.fetch_group_students = fake_fetch_group_students

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.student_groups": impl}):
            module = import_fresh("ifitwala_ed.api.student_groups")
            groups = module.fetch_groups(program="PYP", course="Math", cohort="2026")
            roster = module.fetch_group_students(student_group="SG-0001", start=5, page_length=10)

        self.assertEqual(groups, [{"name": "SG-0001"}])
        self.assertEqual(roster, {"students": [], "start": 15, "total": 0})
        self.assertEqual(module.TRIAGE_ROLES, {"Academic Admin"})
        self.assertEqual(module.INSTRUCTOR_SCOPE_OVERRIDE_ROLES, {"Academic Admin"})
        self.assertEqual(module._user_roles("teacher@example.com"), {"Instructor"})
        self.assertEqual(module._instructor_group_names("teacher@example.com"), {"SG-0001"})
        self.assertEqual(module._base_group_filters(program="PYP"), {"program": "PYP"})
        self.assertTrue(module._has_broad_group_access({"Academic Admin"}))
        self.assertEqual(
            calls["fetch_groups"],
            {
                "program": "PYP",
                "course": "Math",
                "cohort": "2026",
            },
        )
        self.assertEqual(
            calls["fetch_group_students"],
            {
                "student_group": "SG-0001",
                "start": 5,
                "page_length": 10,
            },
        )

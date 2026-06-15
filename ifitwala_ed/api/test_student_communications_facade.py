from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _student_communications_impl_stub():
    module = ModuleType("ifitwala_ed.students.api.student_communications")
    module.RECENT_WINDOW_DAYS = 90
    module.SOURCE_FILTERS = {"all", "course"}
    return module


class TestStudentCommunicationsFacade(TestCase):
    def test_root_student_communications_facade_delegates_public_methods(self):
        calls: dict[str, object] = {}
        impl = _student_communications_impl_stub()

        def _record(name, value):
            def _inner(*args, **kwargs):
                calls[name] = {"args": args, "kwargs": kwargs}
                return value

            return _inner

        impl.get_student_portal_communication_unread_count = _record("unread", 3)
        impl.get_student_home_communication_summary = _record(
            "home", {"center_href": {"name": "student-communications"}}
        )
        impl.get_student_course_communication_summary = _record("course", {"total_count": 2})
        impl.get_student_activity_communications = _record("activity", {"items": []})
        impl.get_student_communication_center = _record("center", {"items": []})

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.student_communications": impl}):
            module = import_fresh("ifitwala_ed.api.student_communications")
            self.assertEqual(module.get_student_portal_communication_unread_count("STU-1"), 3)
            self.assertEqual(
                module.get_student_home_communication_summary("STU-1"),
                {"center_href": {"name": "student-communications"}},
            )
            self.assertEqual(
                module.get_student_course_communication_summary(
                    "STU-1",
                    course_id="COURSE-1",
                    student_group="SG-1",
                ),
                {"total_count": 2},
            )
            self.assertEqual(
                module.get_student_activity_communications(
                    "STU-1",
                    activity_program_offering="PO-1",
                    activity_student_group="SG-ACT",
                    start=5,
                    page_length=10,
                ),
                {"items": []},
            )
            self.assertEqual(
                module.get_student_communication_center(
                    source="course",
                    course_id="COURSE-1",
                    student_group="SG-1",
                    item="org::COMM-1",
                    start=2,
                    page_length=8,
                ),
                {"items": []},
            )

        self.assertEqual(module.RECENT_WINDOW_DAYS, 90)
        self.assertEqual(module.SOURCE_FILTERS, {"all", "course"})
        self.assertEqual(calls["unread"], {"args": (), "kwargs": {"student_name": "STU-1"}})
        self.assertEqual(calls["home"], {"args": ("STU-1",), "kwargs": {}})
        self.assertEqual(
            calls["course"],
            {
                "args": ("STU-1",),
                "kwargs": {"course_id": "COURSE-1", "student_group": "SG-1"},
            },
        )
        self.assertEqual(
            calls["activity"],
            {
                "args": ("STU-1",),
                "kwargs": {
                    "activity_program_offering": "PO-1",
                    "activity_student_group": "SG-ACT",
                    "start": 5,
                    "page_length": 10,
                },
            },
        )
        self.assertEqual(
            calls["center"],
            {
                "args": (),
                "kwargs": {
                    "source": "course",
                    "course_id": "COURSE-1",
                    "student_group": "SG-1",
                    "item": "org::COMM-1",
                    "start": 2,
                    "page_length": 8,
                },
            },
        )

from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _dashboard_impl_stub():
    module = ModuleType("ifitwala_ed.students.api.student_log_dashboard")
    module.ALLOWED_ANALYTICS_ROLES = {"Pastoral Lead"}
    module.FOLLOW_UP_DOCTYPE = "Student Log Follow Up"
    module.FILTER_META_CACHE_TTL_SECONDS = 300
    return module


class TestStudentLogDashboardFacade(TestCase):
    def test_root_student_log_dashboard_facade_delegates_public_methods_and_helper(self):
        calls: dict[str, object] = {}
        impl = _dashboard_impl_stub()

        def fake_get_dashboard_data(filters=None):
            calls["dashboard"] = filters
            return {"openFollowUps": 1}

        def fake_get_distinct_students(filters=None, search_text=""):
            calls["students"] = {"filters": filters, "search_text": search_text}
            return [{"student": "STU-1"}]

        def fake_get_recent_logs(filters=None, start=0, page_length=25):
            calls["recent"] = {"filters": filters, "start": start, "page_length": page_length}
            return [{"name": "SLOG-1"}]

        def fake_get_authorized_schools(user):
            calls["schools"] = user
            return ["SCH-1"]

        def fake_get_filter_meta():
            calls["meta"] = True
            return {"schools": []}

        impl.get_dashboard_data = fake_get_dashboard_data
        impl.get_distinct_students = fake_get_distinct_students
        impl.get_recent_logs = fake_get_recent_logs
        impl.get_authorized_schools = fake_get_authorized_schools
        impl.get_filter_meta = fake_get_filter_meta

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.student_log_dashboard": impl}):
            module = import_fresh("ifitwala_ed.api.student_log_dashboard")
            dashboard = module.get_dashboard_data(filters={"school": "SCH-1"})
            students = module.get_distinct_students(filters={"program": "PYP"}, search_text="Ada")
            recent = module.get_recent_logs(filters={}, start=25, page_length=50)
            schools = module.get_authorized_schools("teacher@example.com")
            meta = module.get_filter_meta()

        self.assertEqual(dashboard, {"openFollowUps": 1})
        self.assertEqual(students, [{"student": "STU-1"}])
        self.assertEqual(recent, [{"name": "SLOG-1"}])
        self.assertEqual(schools, ["SCH-1"])
        self.assertEqual(meta, {"schools": []})
        self.assertEqual(module.ALLOWED_ANALYTICS_ROLES, {"Pastoral Lead"})
        self.assertEqual(calls["dashboard"], {"school": "SCH-1"})
        self.assertEqual(calls["students"], {"filters": {"program": "PYP"}, "search_text": "Ada"})
        self.assertEqual(calls["recent"], {"filters": {}, "start": 25, "page_length": 50})
        self.assertEqual(calls["schools"], "teacher@example.com")
        self.assertTrue(calls["meta"])

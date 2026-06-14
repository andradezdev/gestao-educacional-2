from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _student_log_impl_stub():
    module = ModuleType("ifitwala_ed.students.api.student_log")
    module.LOG_DOCTYPE = "Student Log"
    module.PAGE_LENGTH_DEFAULT = 20
    module._private_helper = object()
    return module


class TestStudentLogFacade(TestCase):
    def test_root_student_log_facade_delegates_portal_methods(self):
        calls: dict[str, object] = {}
        impl = _student_log_impl_stub()

        def fake_get_student_logs(start=0, page_length=20):
            calls["get_student_logs"] = {"start": start, "page_length": page_length}
            return [{"name": "SLOG-1"}]

        def fake_get_student_log_detail(log_name):
            calls["get_student_log_detail"] = log_name
            return {"name": log_name}

        def fake_mark_student_log_read(log_name):
            calls["mark_student_log_read"] = log_name
            return {"ok": True}

        impl.get_student_logs = fake_get_student_logs
        impl.get_student_log_detail = fake_get_student_log_detail
        impl.mark_student_log_read = fake_mark_student_log_read

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.student_log": impl}):
            module = import_fresh("ifitwala_ed.api.student_log")
            rows = module.get_student_logs(start=5, page_length=10)
            detail = module.get_student_log_detail("SLOG-1")
            read = module.mark_student_log_read("SLOG-1")

        self.assertEqual(rows, [{"name": "SLOG-1"}])
        self.assertEqual(detail, {"name": "SLOG-1"})
        self.assertEqual(read, {"ok": True})
        self.assertEqual(calls["get_student_logs"], {"start": 5, "page_length": 10})
        self.assertEqual(calls["get_student_log_detail"], "SLOG-1")
        self.assertEqual(calls["mark_student_log_read"], "SLOG-1")

    def test_root_student_log_facade_delegates_staff_create_methods_and_helper_surface(self):
        calls: dict[str, object] = {}
        impl = _student_log_impl_stub()

        def fake_search_students(**payload):
            calls["search_students"] = payload
            return [{"student": "STU-1"}]

        def fake_search_follow_up_users(**payload):
            calls["search_follow_up_users"] = payload
            return [{"user": "teacher@example.com"}]

        def fake_get_form_options(**payload):
            calls["get_form_options"] = payload
            return {"log_types": []}

        def fake_submit_student_log(**payload):
            calls["submit_student_log"] = payload
            return {"name": "SLOG-2"}

        impl.search_students = fake_search_students
        impl.search_follow_up_users = fake_search_follow_up_users
        impl.get_form_options = fake_get_form_options
        impl.submit_student_log = fake_submit_student_log

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.student_log": impl}):
            module = import_fresh("ifitwala_ed.api.student_log")
            students = module.search_students(query="ada", limit=5)
            users = module.search_follow_up_users(next_step="Counselor", student="STU-1")
            options = module.get_form_options(student="STU-1")
            submitted = module.submit_student_log(student="STU-1", log="Observed.")

        self.assertEqual(students, [{"student": "STU-1"}])
        self.assertEqual(users, [{"user": "teacher@example.com"}])
        self.assertEqual(options, {"log_types": []})
        self.assertEqual(submitted, {"name": "SLOG-2"})
        self.assertIs(module._private_helper, impl._private_helper)
        self.assertEqual(calls["search_students"], {"query": "ada", "limit": 5})
        self.assertEqual(calls["search_follow_up_users"], {"next_step": "Counselor", "student": "STU-1"})
        self.assertEqual(calls["get_form_options"], {"student": "STU-1"})
        self.assertEqual(calls["submit_student_log"], {"student": "STU-1", "log": "Observed."})

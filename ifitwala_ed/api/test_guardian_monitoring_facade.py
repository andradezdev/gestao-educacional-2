from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _guardian_monitoring_impl_stub():
    module = ModuleType("ifitwala_ed.students.api.guardian_monitoring")
    module.DEFAULT_PAGE_LENGTH = 12

    for name in (
        "_resolve_monitoring_context",
        "_coerce_days",
        "_coerce_start",
        "_coerce_page_length",
        "_coerce_prioritize_unread",
        "_plain_guardian_log_text",
        "_empty_page",
        "_serialize_page",
        "_count_monitoring_logs",
        "_get_monitoring_logs",
        "_get_monitoring_logs_page",
        "_get_monitoring_results",
        "_get_monitoring_results_page",
    ):
        setattr(module, name, lambda *args, **kwargs: None)

    return module


class TestGuardianMonitoringFacade(TestCase):
    def test_root_guardian_monitoring_facade_delegates_public_methods(self):
        calls: dict[str, object] = {}
        impl = _guardian_monitoring_impl_stub()

        def fake_snapshot(student=None, days=30, page_length=12, prioritize_unread=None):
            calls["snapshot"] = {
                "student": student,
                "days": days,
                "page_length": page_length,
                "prioritize_unread": prioritize_unread,
            }
            return {"counts": {"visible_student_logs": 1}}

        def fake_logs(student=None, days=30, start=0, page_length=12, prioritize_unread=None):
            calls["logs"] = {
                "student": student,
                "days": days,
                "start": start,
                "page_length": page_length,
                "prioritize_unread": prioritize_unread,
            }
            return {"items": [{"student_log": "LOG-1"}]}

        def fake_results(student=None, days=30, start=0, page_length=12):
            calls["results"] = {
                "student": student,
                "days": days,
                "start": start,
                "page_length": page_length,
            }
            return {"items": [{"task_outcome": "OUT-1"}]}

        def fake_mark_read(log_name):
            calls["mark_read"] = log_name
            return {"ok": True, "student_log": log_name}

        impl.get_guardian_monitoring_snapshot = fake_snapshot
        impl.get_guardian_monitoring_student_logs = fake_logs
        impl.get_guardian_monitoring_published_results = fake_results
        impl.mark_guardian_student_log_read = fake_mark_read

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.guardian_monitoring": impl}):
            module = import_fresh("ifitwala_ed.api.guardian_monitoring")
            self.assertEqual(
                module.get_guardian_monitoring_snapshot(
                    student="STU-1",
                    days="14",
                    page_length="20",
                    prioritize_unread="1",
                ),
                {"counts": {"visible_student_logs": 1}},
            )
            self.assertEqual(
                module.get_guardian_monitoring_student_logs(
                    student="STU-1",
                    days="14",
                    start="5",
                    page_length="20",
                    prioritize_unread=True,
                ),
                {"items": [{"student_log": "LOG-1"}]},
            )
            self.assertEqual(
                module.get_guardian_monitoring_published_results(
                    student="STU-1",
                    days="14",
                    start="5",
                    page_length="20",
                ),
                {"items": [{"task_outcome": "OUT-1"}]},
            )
            self.assertEqual(
                module.mark_guardian_student_log_read("LOG-1"),
                {"ok": True, "student_log": "LOG-1"},
            )

        self.assertEqual(
            calls["snapshot"],
            {"student": "STU-1", "days": "14", "page_length": "20", "prioritize_unread": "1"},
        )
        self.assertEqual(
            calls["logs"],
            {
                "student": "STU-1",
                "days": "14",
                "start": "5",
                "page_length": "20",
                "prioritize_unread": True,
            },
        )
        self.assertEqual(
            calls["results"],
            {"student": "STU-1", "days": "14", "start": "5", "page_length": "20"},
        )
        self.assertEqual(calls["mark_read"], "LOG-1")
        self.assertEqual(module.DEFAULT_PAGE_LENGTH, 12)
        self.assertIs(module._serialize_page, impl._serialize_page)

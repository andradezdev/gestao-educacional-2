from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _student_calendar_impl_stub():
    module = ModuleType("ifitwala_ed.students.api.student_calendar")
    module.CACHE_TTL = 600
    module.STUDENT_CALENDAR_INVALIDATE_EVENT = "student_calendar:invalidate"
    module._is_student_audience = object()
    return module


class TestStudentCalendarFacade(TestCase):
    def test_root_student_calendar_facade_delegates_feed_and_helpers(self):
        calls: dict[str, object] = {}
        impl = _student_calendar_impl_stub()

        def fake_get_student_calendar(from_datetime=None, to_datetime=None, force_refresh=False):
            calls["get_student_calendar"] = {
                "from_datetime": from_datetime,
                "to_datetime": to_datetime,
                "force_refresh": force_refresh,
            }
            return {"events": [], "meta": {"tz": "Asia/Bangkok"}}

        def fake_invalidate_student_calendar_cache(**payload):
            calls["invalidate"] = payload

        def fake_refresh_student_calendar_views(**payload):
            calls["refresh"] = payload

        impl.get_student_calendar = fake_get_student_calendar
        impl.invalidate_student_calendar_cache = fake_invalidate_student_calendar_cache
        impl.refresh_student_calendar_views = fake_refresh_student_calendar_views

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.student_calendar": impl}):
            module = import_fresh("ifitwala_ed.api.student_calendar")
            feed = module.get_student_calendar(
                from_datetime="2026-02-01T00:00:00",
                to_datetime="2026-02-07T00:00:00",
                force_refresh=True,
            )
            module.invalidate_student_calendar_cache(user="student@example.com")
            module.refresh_student_calendar_views(
                users=["student@example.com"],
                source="meeting",
                source_name="MTG-1",
            )

        self.assertEqual(feed, {"events": [], "meta": {"tz": "Asia/Bangkok"}})
        self.assertEqual(module.CACHE_TTL, 600)
        self.assertEqual(module.STUDENT_CALENDAR_INVALIDATE_EVENT, "student_calendar:invalidate")
        self.assertIs(module._is_student_audience, impl._is_student_audience)
        self.assertEqual(
            calls["get_student_calendar"],
            {
                "from_datetime": "2026-02-01T00:00:00",
                "to_datetime": "2026-02-07T00:00:00",
                "force_refresh": True,
            },
        )
        self.assertEqual(
            calls["invalidate"],
            {"student": None, "user": "student@example.com", "users": None},
        )
        self.assertEqual(
            calls["refresh"],
            {
                "student": None,
                "user": None,
                "users": ["student@example.com"],
                "source": "meeting",
                "source_name": "MTG-1",
            },
        )

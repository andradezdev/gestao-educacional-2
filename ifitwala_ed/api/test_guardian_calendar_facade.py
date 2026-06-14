from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _guardian_calendar_impl_stub():
    module = ModuleType("ifitwala_ed.students.api.guardian_calendar")
    module.DEFAULT_HOLIDAY_COLOR = "#dc2626"
    module.DEFAULT_SCHOOL_EVENT_COLOR = "#2563eb"

    for name in (
        "_serialize_scalar",
        "_coerce_month_start",
        "_month_window",
        "_school_filter_options",
        "_validate_selected_school",
        "_relevant_students_for_holidays",
        "_fetch_guardian_holiday_items",
        "_serialize_school_event_items",
        "_sort_calendar_items",
        "_fetch_guardian_school_events",
        "_ordered_matched_children",
        "_resolve_guardian_communication_context",
        "_validate_selected_student",
        "resolve_school_calendars_for_window",
        "now_datetime",
    ):
        setattr(module, name, lambda *args, **kwargs: None)

    return module


class TestGuardianCalendarFacade(TestCase):
    def test_root_guardian_calendar_facade_delegates_public_method(self):
        calls: dict[str, object] = {}
        impl = _guardian_calendar_impl_stub()

        def fake_get_guardian_calendar_overlay(
            month_start=None,
            student=None,
            school=None,
            include_holidays=1,
            include_school_events=1,
        ):
            calls["overlay"] = {
                "month_start": month_start,
                "student": student,
                "school": school,
                "include_holidays": include_holidays,
                "include_school_events": include_school_events,
            }
            return {"items": [{"kind": "holiday"}]}

        impl.get_guardian_calendar_overlay = fake_get_guardian_calendar_overlay

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.guardian_calendar": impl}):
            module = import_fresh("ifitwala_ed.api.guardian_calendar")
            self.assertEqual(
                module.get_guardian_calendar_overlay(
                    month_start="2026-04-01",
                    student="STU-1",
                    school="SCH-1",
                    include_holidays=1,
                    include_school_events=0,
                ),
                {"items": [{"kind": "holiday"}]},
            )

        self.assertEqual(
            calls["overlay"],
            {
                "month_start": "2026-04-01",
                "student": "STU-1",
                "school": "SCH-1",
                "include_holidays": 1,
                "include_school_events": 0,
            },
        )
        self.assertEqual(module.DEFAULT_HOLIDAY_COLOR, "#dc2626")
        self.assertIs(module._sort_calendar_items, impl._sort_calendar_items)

from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _course_schedule_impl_stub():
    module = ModuleType("ifitwala_ed.schedule.api.course_schedule")
    module.COURSE_PLACEHOLDER = "/placeholder.jpg"
    module.COURSE_SCHEDULE_CACHE_PREFIX = "ifw:course_schedule:"
    module.COURSE_SCHEDULE_TERM_PREFIX = "ifw:course_schedule:term:"
    module.COURSE_SCHEDULE_ROTATION_PREFIX = "ifw:course_schedule:rotation:"
    module.COURSE_SCHEDULE_DEPENDENT_PREFIXES = ("ifw:course_schedule:",)
    module.COURSE_SCHEDULE_CACHE_TTL = 21600
    module.COURSE_SCHEDULE_CACHE_MISS = "__none__"
    module.EFFECTIVE_SCHEDULE_AY_PREFIX = "ifw:eff_sched_ay:"
    module.EFFECTIVE_SCHEDULE_CALENDAR_PREFIX = "effective_schedule::"
    module.TimeSlot = object

    for name in (
        "_resolve_current_student",
        "_fetch_student_course_groups",
        "_course_schedule_cache",
        "_cache_key_for_term",
        "_cache_key_for_rotation",
        "_cache_shared_value",
        "_get_cached_shared_value",
        "_get_term_window",
        "_within_term",
        "_resolve_schedule_name",
        "_get_rotation_lookup",
        "_rotation_day_for",
        "_delete_cache_prefix",
        "_delete_cache_key",
        "_doc_value",
        "_academic_year_for_calendar",
        "_schedule_names_for_calendar",
        "_calendar_names_for_academic_year",
        "_delete_term_window_cache",
        "_delete_rotation_caches_for_schedule",
        "_delete_rotation_caches_for_calendar",
        "_delete_rotation_caches_for_academic_year",
        "_delete_effective_schedule_caches_for_calendar",
        "_delete_effective_schedule_caches_for_academic_year",
        "_time_to_str",
        "_time_to_minutes",
        "_safe_image",
        "_collect_instructors",
    ):
        setattr(module, name, lambda *args, **kwargs: None)

    return module


class TestCourseScheduleFacade(TestCase):
    def test_root_course_schedule_facade_delegates_public_and_hook_methods(self):
        calls: dict[str, object] = {}
        impl = _course_schedule_impl_stub()

        def fake_get_today_courses():
            calls["today"] = True
            return {"courses": [{"course": "COURSE-1"}]}

        def fake_invalidate_course_schedule_cache(doc=None, method=None):
            calls["invalidate"] = {"doc": doc, "method": method}

        impl.get_today_courses = fake_get_today_courses
        impl.invalidate_course_schedule_cache = fake_invalidate_course_schedule_cache
        doc = {"doctype": "Term", "name": "TERM-1"}

        with stubbed_frappe(extra_modules={"ifitwala_ed.schedule.api.course_schedule": impl}):
            module = import_fresh("ifitwala_ed.api.course_schedule")
            self.assertEqual(module.get_today_courses(), {"courses": [{"course": "COURSE-1"}]})
            module.invalidate_course_schedule_cache(doc, "after_save")

        self.assertEqual(calls["today"], True)
        self.assertEqual(calls["invalidate"], {"doc": doc, "method": "after_save"})
        self.assertEqual(module.COURSE_SCHEDULE_CACHE_PREFIX, "ifw:course_schedule:")
        self.assertIs(module._time_to_str, impl._time_to_str)

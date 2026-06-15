from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _courses_impl_stub():
    module = ModuleType("ifitwala_ed.curriculum.api.courses")
    module.COURSE_PLACEHOLDER = "/placeholder.jpg"
    module.WORK_BOARD_NOW_LIMIT = 3
    module.WORK_BOARD_SOON_LIMIT = 6
    module.WORK_BOARD_LATER_LIMIT = 6
    module.WORK_BOARD_DONE_LIMIT = 6
    module.TIMELINE_HORIZON_DAYS = 7
    module.NOW_WINDOW_DAYS = 2
    module.SOON_WINDOW_DAYS = 7
    module.OPENABLE_LEARNING_SPACE_STATUSES = {"ready", "shared_plan_only"}

    for name in (
        "_serialize_scalar",
        "_safe_course_image",
        "_build_course_href",
        "_get_student_name_for_user",
        "_require_student_name_for_session_user",
        "_get_academic_years",
        "_fetch_enrolled_courses",
        "_fetch_active_student_groups",
        "_build_student_course_scope",
        "_student_groups_for_course_year",
        "_fetch_active_class_plan_groups",
        "_fetch_active_course_plan_counts",
        "_serialize_course_learning_space",
        "_attach_course_learning_space_state",
        "_get_courses_for_year",
        "_build_student_courses_payload",
        "_coerce_datetime",
        "_time_text_to_minutes",
        "_extract_class_time_bounds",
        "_build_home_orientation",
        "_fetch_student_hub_task_rows",
        "_is_work_item_done",
        "_build_work_item_href",
        "_build_work_item_status_label",
        "_classify_work_item_lane",
        "_serialize_work_item",
        "_work_item_sort_key",
        "_build_work_board_payload",
        "_task_timeline_item",
        "_class_timeline_item",
        "_build_learning_timeline",
    ):
        setattr(module, name, lambda *args, **kwargs: None)

    return module


class TestCoursesFacade(TestCase):
    def test_root_courses_facade_delegates_public_methods(self):
        calls: dict[str, object] = {}
        impl = _courses_impl_stub()

        def fake_get_courses_data(academic_year=None):
            calls["courses"] = academic_year
            return {"selected_year": academic_year, "courses": []}

        def fake_get_student_hub_home():
            calls["home"] = True
            return {"learning": {"today_classes": []}}

        impl.get_courses_data = fake_get_courses_data
        impl.get_student_hub_home = fake_get_student_hub_home

        with stubbed_frappe(extra_modules={"ifitwala_ed.curriculum.api.courses": impl}):
            module = import_fresh("ifitwala_ed.api.courses")
            self.assertEqual(
                module.get_courses_data(academic_year="2025-2026"), {"selected_year": "2025-2026", "courses": []}
            )
            self.assertEqual(module.get_student_hub_home(), {"learning": {"today_classes": []}})

        self.assertEqual(calls, {"courses": "2025-2026", "home": True})
        self.assertEqual(module.COURSE_PLACEHOLDER, "/placeholder.jpg")
        self.assertIs(module._build_course_href, impl._build_course_href)

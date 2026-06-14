from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _demographics_impl_stub():
    module = ModuleType("ifitwala_ed.students.api.student_demographics_dashboard")
    module.ALLOWED_ANALYTICS_ROLES = {"Academic Admin"}
    module.SYSTEM_WIDE_ANALYTICS_ROLES = {"System Manager"}
    module.MIN_DEMOGRAPHIC_CELL_COUNT = 5
    module.SUPPRESSED_BUCKET_LABEL = "Other / Suppressed"
    module.SUPPRESSED_SERIES_KEY = "suppressed"

    for name in (
        "_is_system_wide_analytics_user",
        "_ensure_demographics_access",
        "_get_demographics_access_context",
        "_safe_percent",
        "_suppressed_counter_items",
        "_suppressed_fixed_values",
        "_suppressed_residency_kpi_counts",
        "_normalize_filter_value",
        "_get_filters",
        "_context_school_scope",
        "_requested_school_scope",
        "_get_active_students",
        "_get_guardian_links",
        "_calculate_age",
        "_bucket_age",
        "_build_family_groups",
        "_empty_dashboard",
    ):
        setattr(module, name, lambda *args, **kwargs: None)

    return module


class TestStudentDemographicsDashboardFacade(TestCase):
    def test_root_student_demographics_dashboard_facade_delegates_public_methods(self):
        calls: dict[str, object] = {}
        impl = _demographics_impl_stub()

        def fake_get_filter_meta():
            calls["meta"] = True
            return {"schools": []}

        def fake_get_dashboard(filters=None):
            calls["dashboard"] = filters
            return {"kpis": {"total_students": 12}}

        def fake_get_slice_entities(slice_key=None, filters=None, start=0, page_length=50):
            calls["slice"] = {
                "slice_key": slice_key,
                "filters": filters,
                "start": start,
                "page_length": page_length,
            }
            return []

        impl.get_filter_meta = fake_get_filter_meta
        impl.get_dashboard = fake_get_dashboard
        impl.get_slice_entities = fake_get_slice_entities

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.student_demographics_dashboard": impl}):
            module = import_fresh("ifitwala_ed.api.student_demographics_dashboard")
            self.assertEqual(module.get_filter_meta(), {"schools": []})
            self.assertEqual(module.get_dashboard(filters={"school": "SCH-1"}), {"kpis": {"total_students": 12}})
            self.assertEqual(
                module.get_slice_entities(
                    slice_key="student:house:Red",
                    filters={"school": "SCH-1"},
                    start=5,
                    page_length=10,
                ),
                [],
            )

        self.assertTrue(calls["meta"])
        self.assertEqual(calls["dashboard"], {"school": "SCH-1"})
        self.assertEqual(
            calls["slice"],
            {
                "slice_key": "student:house:Red",
                "filters": {"school": "SCH-1"},
                "start": 5,
                "page_length": 10,
            },
        )
        self.assertEqual(module.MIN_DEMOGRAPHIC_CELL_COUNT, 5)
        self.assertIs(module._empty_dashboard, impl._empty_dashboard)

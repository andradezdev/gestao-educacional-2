# ifitwala_ed/students/api/test_student_attendance.py

from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime
from types import ModuleType
from unittest import TestCase
from unittest.mock import patch

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


class FrappeDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


def _dict(value=None, **kwargs):
    payload = dict(value or {})
    payload.update(kwargs)
    return FrappeDict(payload)


@contextmanager
def _student_attendance_module():
    frappe_utils = ModuleType("frappe.utils")
    frappe_utils.getdate = lambda value=None: value if isinstance(value, date) else datetime.fromisoformat(str(value)).date()
    frappe_utils.nowdate = lambda: "2026-03-12"

    frappe_utils_caching = ModuleType("frappe.utils.caching")
    frappe_utils_caching.redis_cache = lambda ttl=None: (lambda fn: fn)

    frappe_utils_nestedset = ModuleType("frappe.utils.nestedset")
    frappe_utils_nestedset.get_descendants_of = lambda *args, **kwargs: []

    attendance_utils = ModuleType("ifitwala_ed.schedule.attendance_utils")
    attendance_utils.attendance_recorded_dates = lambda student_group: []
    attendance_utils.fetch_blocks_for_day = lambda student_group, attendance_date: []
    attendance_utils.fetch_existing_attendance = lambda student_group, attendance_date: {}
    attendance_utils.fetch_students = lambda student_group, start=0, page_length=500: {
        "students": [],
        "total": 0,
        "start": start,
    }
    attendance_utils.get_meeting_dates = lambda student_group: []
    attendance_utils.list_attendance_codes = lambda show_in_attendance_tool=1: []
    attendance_utils.previous_status_map = lambda student_group, selected_date: {}
    attendance_utils.resolve_student_group_schedule_name = lambda student_group: None

    schedule_utils = ModuleType("ifitwala_ed.schedule.schedule_utils")
    schedule_utils.get_weekend_days_for_calendar = lambda calendar_name: [6, 0]

    student_groups = ModuleType("ifitwala_ed.students.api.student_groups")
    student_groups._instructor_group_names = lambda user: set()
    student_groups._user_roles = lambda user: set()

    student_insights = ModuleType("ifitwala_ed.students.doctype.student_insight_note.student_insight_note")
    student_insights.build_student_insight_summaries = lambda students: {}

    school_tree = ModuleType("ifitwala_ed.utilities.school_tree")
    school_tree._is_adminish = lambda user=None: False
    school_tree.get_school_lineage = lambda school: [school] if school else []
    school_tree.get_user_default_school = lambda: "SCH-1"

    with stubbed_frappe(
        extra_modules={
            "frappe.utils": frappe_utils,
            "frappe.utils.caching": frappe_utils_caching,
            "frappe.utils.nestedset": frappe_utils_nestedset,
            "ifitwala_ed.schedule.attendance_utils": attendance_utils,
            "ifitwala_ed.schedule.schedule_utils": schedule_utils,
            "ifitwala_ed.students.api.student_groups": student_groups,
            "ifitwala_ed.students.doctype.student_insight_note.student_insight_note": student_insights,
            "ifitwala_ed.utilities.school_tree": school_tree,
        }
    ) as frappe:
        frappe._dict = _dict
        frappe.db.get_value = lambda *args, **kwargs: None
        frappe.db.sql = lambda *args, **kwargs: []
        yield import_fresh("ifitwala_ed.students.api.student_attendance"), frappe


class TestStudentAttendanceApi(TestCase):
    def test_get_weekend_days_uses_effective_schedule_when_group_schedule_missing(self):
        with _student_attendance_module() as (module, _frappe):
            with (
                patch.object(module, "get_weekend_days_for_calendar", return_value=[5, 6]) as get_weekend_days,
                patch.object(module, "resolve_student_group_schedule_name", return_value="SCH-SCHED-FALLBACK") as resolve,
                patch.object(module.frappe.db, "get_value", return_value="CAL-001") as get_value,
            ):
                result = module.get_weekend_days("SG-001")

        self.assertEqual(result, [5, 6])
        resolve.assert_called_once_with("SG-001")
        get_value.assert_called_once_with("School Schedule", "SCH-SCHED-FALLBACK", "school_calendar")
        get_weekend_days.assert_called_once_with("CAL-001")

    def test_fetch_attendance_ledger_context_aggregates_lists(self):
        with _student_attendance_module() as (module, _frappe):
            with (
                patch.object(module, "_cached_context", side_effect=lambda _k, _r, builder: builder()),
                patch.object(
                    module,
                    "fetch_school_filter_context",
                    return_value={"default_school": "SCH-1", "schools": [{"name": "SCH-1", "school_name": "School 1"}]},
                ) as school_context,
                patch.object(module, "fetch_active_programs", return_value=[{"name": "PROG-1", "program_name": "Program 1"}]) as programs,
                patch.object(module, "fetch_portal_student_groups", return_value=[{"name": "SG-1", "academic_year": "AY-2025"}]),
                patch.object(module, "fetch_portal_academic_years", return_value=[]),
                patch.object(module, "fetch_portal_terms", return_value=[{"name": "TERM-1"}]) as terms,
            ):
                payload = module.fetch_attendance_ledger_context(program="PROG-1")

        self.assertEqual(payload["default_school"], "SCH-1")
        self.assertEqual(payload["default_program"], "PROG-1")
        self.assertEqual(payload["default_academic_year"], "AY-2025")
        self.assertEqual(payload["student_groups"], [{"name": "SG-1", "academic_year": "AY-2025"}])
        self.assertEqual(payload["terms"], [{"name": "TERM-1"}])
        school_context.assert_called_once_with()
        programs.assert_called_once_with(school="SCH-1")
        terms.assert_called_once_with(academic_year="AY-2025", school="SCH-1")

    def test_fetch_active_programs_scopes_to_program_offering_lineage_for_selected_school(self):
        with _student_attendance_module() as (module, frappe):
            with (
                patch.object(module, "_expand_school_scope", return_value=["SCH-1"]),
                patch.object(
                    module.frappe.db,
                    "sql",
                    return_value=[
                        frappe._dict({"name": "PROG-PARENT", "program_name": "Parent Program", "is_group": 1}),
                        frappe._dict({"name": "PROG-CHILD", "program_name": "Child Program", "is_group": 0}),
                        frappe._dict({"name": "PROG-SIBLING", "program_name": "Sibling Program", "is_group": 0}),
                    ],
                ) as sql,
            ):
                rows = module.fetch_active_programs(school="SCH-1")

        self.assertEqual([row["name"] for row in rows], ["PROG-PARENT", "PROG-CHILD", "PROG-SIBLING"])
        self.assertIn("FROM `tabProgram Offering` po", sql.call_args.args[0])
        query_params = sql.call_args.args[1]
        self.assertEqual(query_params["school_scope"], ("SCH-1",))

    def test_fetch_active_programs_returns_empty_when_selected_school_is_out_of_scope(self):
        with _student_attendance_module() as (module, _frappe):
            with (
                patch.object(module, "_expand_school_scope", return_value=[]),
                patch.object(module.frappe.db, "sql") as sql,
            ):
                rows = module.fetch_active_programs(school="SCH-1")

        self.assertEqual(rows, [])
        sql.assert_not_called()

    def test_fetch_attendance_tool_bootstrap_auto_picks_single_group(self):
        with _student_attendance_module() as (module, _frappe):
            with (
                patch.object(module, "_cached_context", side_effect=lambda _k, _r, builder: builder()),
                patch.object(
                    module,
                    "fetch_school_filter_context",
                    return_value={"default_school": "SCH-1", "schools": [{"name": "SCH-1", "school_name": "School 1"}]},
                ),
                patch.object(module, "fetch_active_programs", return_value=[{"name": "PROG-1", "program_name": "Program 1"}]) as programs,
                patch.object(module, "fetch_portal_student_groups", return_value=[{"name": "SG-ONLY", "student_group_name": "Only Group"}]),
                patch.object(
                    module,
                    "list_attendance_codes",
                    return_value=[
                        {
                            "name": "P",
                            "attendance_code": "P",
                            "attendance_code_name": "Present",
                            "is_default": 1,
                        }
                    ],
                ),
            ):
                payload = module.fetch_attendance_tool_bootstrap()

        self.assertEqual(payload["default_student_group"], "SG-ONLY")
        self.assertEqual(payload["default_code"], "P")
        self.assertEqual(payload["attendance_codes"][0]["attendance_code_name"], "Present")
        programs.assert_called_once_with(school="SCH-1")

    def test_fetch_attendance_tool_bootstrap_falls_back_to_all_codes_when_tool_filter_is_empty(self):
        with _student_attendance_module() as (module, _frappe):
            with (
                patch.object(module, "_cached_context", side_effect=lambda _k, _r, builder: builder()),
                patch.object(
                    module,
                    "fetch_school_filter_context",
                    return_value={"default_school": "SCH-1", "schools": [{"name": "SCH-1", "school_name": "School 1"}]},
                ),
                patch.object(module, "fetch_active_programs", return_value=[{"name": "PROG-1", "program_name": "Program 1"}]) as programs,
                patch.object(module, "fetch_portal_student_groups", return_value=[{"name": "SG-1", "student_group_name": "Group 1"}]),
                patch.object(
                    module,
                    "list_attendance_codes",
                    side_effect=[
                        [],
                        [{"name": "P", "attendance_code": "P", "attendance_code_name": "Present"}],
                    ],
                ) as codes,
            ):
                payload = module.fetch_attendance_tool_bootstrap()

        self.assertEqual(payload["default_code"], "P")
        self.assertEqual(payload["attendance_codes"][0]["attendance_code"], "P")
        self.assertEqual(codes.call_count, 2)
        self.assertEqual(codes.call_args_list[1].kwargs, {"show_in_attendance_tool": None})
        programs.assert_called_once_with(school="SCH-1")

    def test_fetch_attendance_tool_bootstrap_prefers_code_marked_default(self):
        with _student_attendance_module() as (module, _frappe):
            with (
                patch.object(module, "_cached_context", side_effect=lambda _k, _r, builder: builder()),
                patch.object(
                    module,
                    "fetch_school_filter_context",
                    return_value={"default_school": "SCH-1", "schools": [{"name": "SCH-1", "school_name": "School 1"}]},
                ),
                patch.object(module, "fetch_active_programs", return_value=[{"name": "PROG-1", "program_name": "Program 1"}]) as programs,
                patch.object(module, "fetch_portal_student_groups", return_value=[{"name": "SG-1", "student_group_name": "Group 1"}]),
                patch.object(
                    module,
                    "list_attendance_codes",
                    return_value=[
                        {"name": "A", "attendance_code": "A", "attendance_code_name": "Absent", "is_default": 0},
                        {"name": "P", "attendance_code": "P", "attendance_code_name": "Present", "is_default": 1},
                    ],
                ),
            ):
                payload = module.fetch_attendance_tool_bootstrap()

        self.assertEqual(payload["default_code"], "P")
        programs.assert_called_once_with(school="SCH-1")

    def test_fetch_attendance_tool_group_context_picks_last_past_date(self):
        with _student_attendance_module() as (module, _frappe):
            with (
                patch.object(module, "get_weekend_days", return_value=[6, 0]),
                patch.object(module, "get_meeting_dates", return_value=["2026-03-10", "2026-03-12", "2026-03-15"]),
                patch.object(module, "attendance_recorded_dates", return_value=["2026-03-10"]),
                patch.object(module, "nowdate", return_value="2026-03-12"),
            ):
                payload = module.fetch_attendance_tool_group_context("SG-1")

        self.assertEqual(payload["default_selected_date"], "2026-03-12")
        self.assertEqual(payload["recorded_dates"], ["2026-03-10"])

    def test_fetch_attendance_tool_roster_context_aggregates_day_payload(self):
        with _student_attendance_module() as (module, _frappe):
            with (
                patch.object(module, "fetch_students", return_value={"students": [], "total": 0, "start": 0, "group_info": {}}),
                patch.object(module, "previous_status_map", return_value={"STU-1|-1": "P"}),
                patch.object(module, "fetch_existing_attendance", return_value={"STU-1": {-1: {"code": "P", "remark": ""}}}),
                patch.object(module, "fetch_blocks_for_day", return_value=[-1]),
            ):
                payload = module.fetch_attendance_tool_roster_context("SG-1", "2026-03-12")

        self.assertEqual(payload["roster"]["total"], 0)
        self.assertEqual(payload["prev_map"], {"STU-1|-1": "P"})
        self.assertEqual(payload["existing_map"]["STU-1"][-1]["code"], "P")
        self.assertEqual(payload["blocks"], [-1])

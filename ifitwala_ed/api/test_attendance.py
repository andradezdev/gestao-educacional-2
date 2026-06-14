# ifitwala_ed/api/test_attendance.py

from datetime import date
from unittest import TestCase
from unittest.mock import patch

import frappe

from ifitwala_ed.api.attendance import (
    _clean_optional,
    _get_ledger_payload,
    _hash_list,
    _normalize_heatmap_mode,
    _normalize_thresholds,
)


class TestAttendanceApi(TestCase):
    @patch("ifitwala_ed.api.attendance._resolve_school_threshold_defaults")
    def test_normalize_thresholds_uses_school_defaults_not_client_override(self, mock_defaults):
        mock_defaults.return_value = (92.0, 81.0)

        payload = _normalize_thresholds(
            {"warning": 10, "critical": 5},
            selected_school="SCH-1",
        )

        self.assertEqual(payload, {"warning": 92.0, "critical": 81.0})

    @patch("ifitwala_ed.api.attendance._resolve_school_threshold_defaults")
    def test_normalize_thresholds_swaps_when_warning_below_critical(self, mock_defaults):
        mock_defaults.return_value = (70.0, 85.0)

        payload = _normalize_thresholds(None, selected_school="SCH-1")

        self.assertEqual(payload, {"warning": 85.0, "critical": 70.0})

    def test_normalize_heatmap_mode_defaults_to_block(self):
        self.assertEqual(_normalize_heatmap_mode("day"), "day")
        self.assertEqual(_normalize_heatmap_mode("invalid"), "block")

    def test_clean_optional_and_hash_list_helpers(self):
        self.assertEqual(_clean_optional("  abc  "), "abc")
        self.assertIsNone(_clean_optional("   "))
        self.assertNotEqual(_hash_list(["a", "b"]), _hash_list(["a", "c"]))

    @patch("ifitwala_ed.api.attendance.frappe.get_all")
    @patch("ifitwala_ed.api.attendance.frappe.db.sql")
    def test_get_ledger_payload_returns_canonical_grouped_contract(
        self,
        mock_sql,
        mock_get_all,
    ):
        mock_get_all.return_value = [
            frappe._dict(
                {
                    "name": "ATT-CODE-P",
                    "attendance_code": "P",
                    "attendance_code_name": "Present",
                    "count_as_present": 1,
                    "display_order": 1,
                }
            ),
            frappe._dict(
                {
                    "name": "ATT-CODE-L",
                    "attendance_code": "L",
                    "attendance_code_name": "Late",
                    "count_as_present": 1,
                    "display_order": 2,
                }
            ),
            frappe._dict(
                {
                    "name": "ATT-CODE-A",
                    "attendance_code": "A",
                    "attendance_code_name": "Absent",
                    "count_as_present": 0,
                    "display_order": 3,
                }
            ),
        ]

        def fake_sql(query, params=None, as_dict=False):
            self.assertTrue(as_dict)
            if "LIMIT %(limit)s OFFSET %(offset)s" in query:
                self.assertEqual(params["limit"], 80)
                self.assertEqual(params["offset"], 0)
                self.assertIn("a.school IN %(school_scope)s", query)
                self.assertIn("a.attendance_date IN %(instruction_days)s", query)
                return [
                    frappe._dict(
                        {
                            "student": "STU-1",
                            "student_label": "Amina Dar",
                            "attendance_type": "Course",
                            "course": "COURSE-1",
                            "student_group": "SG-1",
                            "code_p_1": 8,
                            "code_l_2": 1,
                            "code_a_3": 2,
                            "present_count": 9,
                            "total_count": 11,
                            "percentage_present": 81.8,
                            "percentage_late": 11.1,
                        }
                    )
                ]
            if "COUNT(*) AS total_rows" in query:
                return [frappe._dict({"total_rows": 1})]
            if "COUNT(DISTINCT a.student) AS total_students" in query:
                return [
                    frappe._dict(
                        {
                            "raw_records": 11,
                            "total_students": 1,
                            "total_present": 9,
                            "total_late_present": 1,
                            "total_attendance": 11,
                        }
                    )
                ]
            if "SELECT DISTINCT a.course" in query:
                return [frappe._dict({"course": "COURSE-1"})]
            if "SELECT DISTINCT a.instructor" in query:
                return [frappe._dict({"instructor": "EMP-1"})]
            if "AS student_name" in query:
                return [frappe._dict({"student": "STU-1", "student_name": "Amina Dar"})]
            raise AssertionError(f"Unexpected SQL query: {query}")

        mock_sql.side_effect = fake_sql

        ctx = {
            "user": "admin@example.com",
            "role_class": "admin",
            "school_scope": ["SCH-PARENT", "SCH-CHILD"],
            "group_scope": [],
            "student_scope": [],
            "date_from": date(2026, 3, 1),
            "date_to": date(2026, 3, 31),
            "window_source": "selected_term",
            "academic_year": "AY-2026",
            "term": "TERM-1",
            "selected_school": "SCH-PARENT",
            "program": None,
            "program_scope": [],
            "student_group": None,
            "whole_day": 0,
            "activity_only": 0,
        }

        payload = _get_ledger_payload(
            ctx,
            course=None,
            instructor=None,
            student=None,
            attendance_code=None,
            page=1,
            page_length=80,
            sort_by="student_label",
            sort_order="asc",
        )

        self.assertEqual(payload["meta"]["window_source"], "selected_term")
        self.assertEqual(payload["pagination"], {"page": 1, "page_length": 80, "total_rows": 1, "total_pages": 1})
        self.assertEqual(payload["summary"]["percentage_present"], 81.8)
        self.assertEqual(payload["summary"]["percentage_late"], 11.1)
        self.assertEqual(payload["rows"][0]["student_label"], "Amina Dar")
        self.assertEqual(payload["rows"][0]["code_p_1"], 8)
        self.assertEqual(payload["filter_options"]["courses"], ["COURSE-1"])
        self.assertEqual(payload["filter_options"]["instructors"], ["EMP-1"])
        self.assertEqual(payload["filter_options"]["students"], [{"student": "STU-1", "student_name": "Amina Dar"}])
        self.assertEqual(
            payload["codes"],
            [
                {"attendance_code": "P", "attendance_code_name": "Present", "count_as_present": 1},
                {"attendance_code": "L", "attendance_code_name": "Late", "count_as_present": 1},
                {"attendance_code": "A", "attendance_code_name": "Absent", "count_as_present": 0},
            ],
        )
        self.assertEqual(
            [column["fieldname"] for column in payload["columns"][:7]],
            [
                "student_label",
                "attendance_type",
                "course",
                "student_group",
                "code_p_1",
                "code_l_2",
                "code_a_3",
            ],
        )

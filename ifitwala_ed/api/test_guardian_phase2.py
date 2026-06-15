# ifitwala_ed/api/test_guardian_phase2.py

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from ifitwala_ed.students.api.guardian_attendance import get_guardian_attendance_snapshot
from ifitwala_ed.students.api.guardian_finance import _resolve_finance_scope, get_guardian_finance_snapshot
from ifitwala_ed.students.api.guardian_monitoring import (
    _get_monitoring_logs,
    get_guardian_monitoring_published_results,
    get_guardian_monitoring_snapshot,
    get_guardian_monitoring_student_logs,
    mark_guardian_student_log_read,
)


class TestGuardianFinancePhase2(FrappeTestCase):
    def test_finance_scope_authorizes_account_holder_by_email_match(self):
        children = [{"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"}]

        def fake_get_all(doctype, filters=None, fields=None, order_by=None, limit=None):
            if doctype == "Student":
                return [
                    {
                        "name": "STU-1",
                        "student_full_name": "Amina Example",
                        "anchor_school": "SCHOOL-1",
                        "account_holder": "AH-1",
                    }
                ]
            if doctype == "Account Holder":
                self.assertIn("primary_email", fields or [])
                self.assertNotIn("primary_phone", fields or [])
                return [
                    {
                        "name": "AH-1",
                        "account_holder_name": "Example Family",
                        "organization": "ORG-1",
                        "status": "Active",
                        "primary_email": "guardian@example.com",
                        "primary_phone": "",
                    }
                ]
            self.fail(f"Unexpected doctype lookup: {doctype}")

        with (
            patch(
                "ifitwala_ed.students.api.guardian_finance.frappe.db.get_value",
                return_value={"guardian_email": "guardian@example.com", "is_financial_guardian": 0},
            ),
            patch("ifitwala_ed.students.api.guardian_finance.frappe.get_all", side_effect=fake_get_all),
        ):
            scope = _resolve_finance_scope(
                user="guardian@example.com",
                guardian_name="GRD-0001",
                children=children,
            )

        self.assertEqual(scope["authorized_account_holders"], ["AH-1"])
        self.assertEqual(scope["account_holders"][0]["students"][0]["student"], "STU-1")
        self.assertEqual(scope["account_holders"][0]["primary_email_masked"], "g****@example.com")
        self.assertNotIn("primary_email", scope["account_holders"][0])
        self.assertNotIn("primary_phone", scope["account_holders"][0])
        self.assertNotIn("guardian@example.com", str(scope["account_holders"]))
        self.assertEqual(scope["access_reason"], "")

    def test_finance_snapshot_returns_explicit_access_limited_meta(self):
        with (
            patch(
                "ifitwala_ed.students.api.guardian_finance.frappe.session",
                frappe._dict({"user": "guardian@example.com"}),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_finance.now_datetime",
                return_value=frappe.utils.get_datetime("2026-03-13 09:00:00"),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_finance._resolve_guardian_scope",
                return_value=("GRD-0001", [{"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"}]),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_finance._resolve_finance_scope",
                return_value={
                    "children": [],
                    "student_names": [],
                    "authorized_account_holders": [],
                    "account_holders": [],
                    "children_by_holder": {},
                    "access_reason": "no_authorized_account_holders",
                },
            ),
            patch("ifitwala_ed.students.api.guardian_finance._get_invoice_rows", return_value=[]),
            patch("ifitwala_ed.students.api.guardian_finance._get_payment_rows", return_value=[]),
        ):
            payload = get_guardian_finance_snapshot()

        self.assertFalse(payload["meta"]["finance_access"])
        self.assertEqual(payload["meta"]["access_reason"], "no_authorized_account_holders")
        self.assertEqual(payload["counts"]["total_invoices"], 0)


class TestGuardianMonitoringPhase2(FrappeTestCase):
    def test_monitoring_logs_return_full_guardian_visible_note_text(self):
        long_log_text = " ".join(["Detailed guardian-visible note"] * 24)
        row = {
            "name": "LOG-1",
            "student": "STU-1",
            "student_name": "Amina Example",
            "date": frappe.utils.getdate("2026-03-12"),
            "time": None,
            "follow_up_status": "Open",
            "log": f"<p>{long_log_text}</p>",
        }

        with (
            patch(
                "ifitwala_ed.students.api.guardian_monitoring.frappe.utils.getdate",
                return_value=frappe.utils.getdate("2026-03-13"),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_monitoring.frappe.db.sql",
                return_value=[{**row, "is_unread": 1}],
            ),
            patch(
                "ifitwala_ed.students.doctype.student_log.evidence.get_student_log_evidence_map",
                return_value={},
            ),
        ):
            result = _get_monitoring_logs(
                user="guardian@example.com",
                student_names=["STU-1"],
                days=30,
                start=0,
                page_length=12,
            )

        self.assertEqual(result[0]["summary"], long_log_text)
        self.assertGreater(len(result[0]["summary"]), 220)
        self.assertTrue(result[0]["is_unread"])

    def test_monitoring_rejects_out_of_scope_student_filter(self):
        with (
            patch(
                "ifitwala_ed.students.api.guardian_monitoring.frappe.session",
                frappe._dict({"user": "guardian@example.com"}),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_monitoring._resolve_guardian_scope",
                return_value=("GRD-0001", [{"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"}]),
            ),
        ):
            with self.assertRaises(frappe.PermissionError):
                get_guardian_monitoring_snapshot(student="STU-404", days=30)

    def test_monitoring_snapshot_returns_familywide_counts(self):
        children = [
            {"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"},
            {"student": "STU-2", "full_name": "Noah Example", "school": "SCHOOL-1"},
        ]
        student_logs = [
            {
                "student_log": "LOG-1",
                "student": "STU-1",
                "student_name": "Amina Example",
                "date": "2026-03-12",
                "summary": "Needs follow-up",
                "follow_up_status": "Open",
                "is_unread": True,
            }
        ]
        published_results = {
            "items": [
                {
                    "task_outcome": "OUT-1",
                    "student": "STU-2",
                    "student_name": "Noah Example",
                    "title": "Science assessment",
                    "published_on": "2026-03-11 09:00:00",
                }
            ],
            "total_count": 1,
            "unread_total_count": 0,
            "has_more": False,
            "start": 0,
            "page_length": 12,
        }
        student_log_page = {
            "items": student_logs,
            "total_count": 1,
            "unread_total_count": 1,
            "has_more": False,
            "start": 0,
            "page_length": 12,
        }

        with (
            patch(
                "ifitwala_ed.students.api.guardian_monitoring.frappe.session",
                frappe._dict({"user": "guardian@example.com"}),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_monitoring.now_datetime",
                return_value=frappe.utils.get_datetime("2026-03-13 09:00:00"),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_monitoring._resolve_guardian_scope",
                return_value=("GRD-0001", children),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_monitoring._get_monitoring_logs_page", return_value=student_log_page
            ),
            patch(
                "ifitwala_ed.students.api.guardian_monitoring._get_monitoring_results_page",
                return_value=published_results,
            ),
        ):
            payload = get_guardian_monitoring_snapshot(days=30, page_length=12)

        self.assertEqual(payload["counts"]["visible_student_logs"], 1)
        self.assertEqual(payload["counts"]["unread_visible_student_logs"], 1)
        self.assertEqual(payload["counts"]["published_results"], 1)
        self.assertEqual(payload["family"]["children"], children)
        self.assertEqual(payload["student_logs"]["items"], student_logs)
        self.assertEqual(payload["published_results"]["total_count"], 1)

    def test_monitoring_student_logs_endpoint_returns_paged_payload(self):
        children = [{"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"}]
        log_page = {
            "items": [
                {
                    "student_log": "LOG-1",
                    "student": "STU-1",
                    "student_name": "Amina Example",
                    "date": "2026-03-12",
                    "summary": "Needs follow-up",
                    "follow_up_status": "Open",
                    "is_unread": True,
                }
            ],
            "total_count": 3,
            "unread_total_count": 1,
            "has_more": True,
            "start": 1,
            "page_length": 12,
        }

        with (
            patch(
                "ifitwala_ed.students.api.guardian_monitoring.frappe.session",
                frappe._dict({"user": "guardian@example.com"}),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_monitoring._resolve_guardian_scope",
                return_value=("GRD-0001", children),
            ),
            patch("ifitwala_ed.students.api.guardian_monitoring._get_monitoring_logs_page", return_value=log_page),
        ):
            payload = get_guardian_monitoring_student_logs(start=1, page_length=12)

        self.assertEqual(payload["items"], log_page["items"])
        self.assertEqual(payload["total_count"], 3)
        self.assertTrue(payload["has_more"])

    def test_monitoring_published_results_endpoint_returns_paged_payload(self):
        children = [{"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"}]
        result_page = {
            "items": [
                {
                    "task_outcome": "OUT-1",
                    "student": "STU-1",
                    "student_name": "Amina Example",
                    "title": "Science assessment",
                    "published_on": "2026-03-11 09:00:00",
                }
            ],
            "total_count": 2,
            "unread_total_count": 0,
            "has_more": True,
            "start": 1,
            "page_length": 12,
        }

        with (
            patch(
                "ifitwala_ed.students.api.guardian_monitoring.frappe.session",
                frappe._dict({"user": "guardian@example.com"}),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_monitoring._resolve_guardian_scope",
                return_value=("GRD-0001", children),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_monitoring._get_monitoring_results_page", return_value=result_page
            ),
        ):
            payload = get_guardian_monitoring_published_results(start=1, page_length=12)

        self.assertEqual(payload["items"], result_page["items"])
        self.assertEqual(payload["total_count"], 2)
        self.assertTrue(payload["has_more"])

    def test_mark_guardian_student_log_read_persists_seen_state_for_linked_child(self):
        children = [{"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"}]
        log_row = frappe._dict({"name": "LOG-1", "student": "STU-1", "visible_to_guardians": 1})
        read_at = frappe.utils.get_datetime("2026-03-15 11:45:00")

        with (
            patch(
                "ifitwala_ed.students.api.guardian_monitoring.frappe.session",
                frappe._dict({"user": "guardian@example.com"}),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_monitoring._resolve_guardian_scope",
                return_value=("GRD-0001", children),
            ),
            patch("ifitwala_ed.students.api.guardian_monitoring.now_datetime", return_value=read_at),
            patch("ifitwala_ed.students.api.guardian_monitoring.frappe.db.get_value", return_value=log_row),
            patch("ifitwala_ed.students.api.guardian_monitoring._upsert_student_log_read_receipt") as mark_read_mock,
        ):
            result = mark_guardian_student_log_read("LOG-1")

        self.assertEqual(result, {"ok": True, "student_log": "LOG-1", "read_at": read_at})
        mark_read_mock.assert_called_once_with(
            user="guardian@example.com",
            log_name="LOG-1",
            read_at=read_at,
        )

    def test_mark_guardian_student_log_read_rejects_out_of_scope_log(self):
        children = [{"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"}]
        log_row = frappe._dict({"name": "LOG-404", "student": "STU-404", "visible_to_guardians": 1})

        with (
            patch(
                "ifitwala_ed.students.api.guardian_monitoring.frappe.session",
                frappe._dict({"user": "guardian@example.com"}),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_monitoring._resolve_guardian_scope",
                return_value=("GRD-0001", children),
            ),
            patch("ifitwala_ed.students.api.guardian_monitoring.frappe.db.get_value", return_value=log_row),
        ):
            with self.assertRaises(frappe.PermissionError):
                mark_guardian_student_log_read("LOG-404")


class TestGuardianAttendancePhase2(FrappeTestCase):
    def test_attendance_rejects_out_of_scope_student_filter(self):
        with (
            patch(
                "ifitwala_ed.students.api.guardian_attendance.frappe.session",
                frappe._dict({"user": "guardian@example.com"}),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_attendance._resolve_guardian_scope",
                return_value=("GRD-0001", [{"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"}]),
            ),
        ):
            with self.assertRaises(frappe.PermissionError):
                get_guardian_attendance_snapshot(student="STU-404", days=60)

    def test_attendance_snapshot_returns_familywide_rows_and_counts(self):
        children = [
            {"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"},
            {"student": "STU-2", "full_name": "Noah Example", "school": "SCHOOL-1"},
        ]
        attendance_rows = [
            {
                "student": "STU-1",
                "student_name": "Amina Example",
                "summary": {
                    "tracked_days": 2,
                    "present_days": 1,
                    "late_days": 1,
                    "absence_days": 0,
                },
                "days": [
                    {
                        "date": "2026-03-12",
                        "state": "late",
                        "details": [
                            {
                                "attendance": "ATT-1",
                                "time": "08:15",
                                "attendance_code": "L",
                                "attendance_code_name": "Late",
                                "whole_day": False,
                                "course": "Math",
                                "location": None,
                                "remark": "Late bus",
                            }
                        ],
                    }
                ],
            },
            {
                "student": "STU-2",
                "student_name": "Noah Example",
                "summary": {
                    "tracked_days": 1,
                    "present_days": 0,
                    "late_days": 0,
                    "absence_days": 1,
                },
                "days": [
                    {
                        "date": "2026-03-11",
                        "state": "absence",
                        "details": [
                            {
                                "attendance": "ATT-2",
                                "time": None,
                                "attendance_code": "A",
                                "attendance_code_name": "Absent",
                                "whole_day": True,
                                "course": None,
                                "location": "Nurse",
                                "remark": "Sent to nurse",
                            }
                        ],
                    }
                ],
            },
        ]
        counts = {
            "tracked_days": 3,
            "present_days": 1,
            "late_days": 1,
            "absence_days": 1,
        }

        with (
            patch(
                "ifitwala_ed.students.api.guardian_attendance.frappe.session",
                frappe._dict({"user": "guardian@example.com"}),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_attendance.now_datetime",
                return_value=frappe.utils.get_datetime("2026-03-13 09:00:00"),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_attendance._resolve_guardian_scope",
                return_value=("GRD-0001", children),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_attendance._build_attendance_students",
                return_value=(attendance_rows, counts),
            ),
        ):
            payload = get_guardian_attendance_snapshot(days=60)

        self.assertEqual(payload["meta"]["guardian"]["name"], "GRD-0001")
        self.assertEqual(payload["family"]["children"], children)
        self.assertEqual(payload["counts"], counts)
        self.assertEqual(payload["students"], attendance_rows)
        self.assertEqual(payload["meta"]["filters"]["days"], 60)

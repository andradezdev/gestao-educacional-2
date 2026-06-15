# ifitwala_ed/students/api/test_guardian_communications.py

from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from ifitwala_ed.students.api import guardian_communications
from ifitwala_ed.students.api.guardian_communications import get_guardian_communication_center


class TestGuardianCommunicationCenterPhase2(FrappeTestCase):
    def test_communication_center_rejects_out_of_scope_student_filter(self):
        with patch(
            "ifitwala_ed.students.api.guardian_communications._resolve_guardian_communication_context",
            return_value={
                "children": [{"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"}],
                "student_names": ["STU-1"],
            },
        ):
            with self.assertRaises(frappe.PermissionError):
                get_guardian_communication_center(student="STU-404")

    def test_communication_center_returns_familywide_items_and_unread_counts(self):
        children = [
            {"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"},
            {"student": "STU-2", "full_name": "Noah Example", "school": "SCHOOL-1"},
        ]
        org_items = [
            {
                "kind": "org_communication",
                "item_id": "org::COMM-1",
                "sort_at": "2026-04-14T08:00:00",
                "source_type": "school",
                "source_label": "School Update",
                "context_label": "School One",
                "matched_children": children,
                "is_unread": True,
                "org_communication": {
                    "name": "COMM-1",
                    "title": "Whole-school reminder",
                    "communication_type": "Reminder",
                    "status": "Published",
                    "priority": "Normal",
                    "portal_surface": "Guardian Portal",
                    "school": "SCHOOL-1",
                    "organization": "ORG-1",
                    "publish_from": "2026-04-14T08:00:00",
                    "publish_to": None,
                    "brief_start_date": None,
                    "brief_end_date": None,
                    "interaction_mode": "Student Q&A",
                    "allow_private_notes": 0,
                    "allow_public_thread": 1,
                    "snippet": "Bring the signed form tomorrow.",
                    "has_active_thread": 1,
                },
            },
            {
                "kind": "org_communication",
                "item_id": "org::COMM-2",
                "sort_at": "2026-04-13T10:00:00",
                "source_type": "course",
                "source_label": "Class Update",
                "context_label": "Biology A",
                "matched_children": [children[0]],
                "is_unread": False,
                "org_communication": {
                    "name": "COMM-2",
                    "title": "Biology checkpoint",
                    "communication_type": "Information",
                    "status": "Published",
                    "priority": "High",
                    "portal_surface": "Portal Feed",
                    "school": "SCHOOL-1",
                    "organization": "ORG-1",
                    "publish_from": "2026-04-13T10:00:00",
                    "publish_to": None,
                    "brief_start_date": None,
                    "brief_end_date": None,
                    "interaction_mode": "Student Q&A",
                    "allow_private_notes": 0,
                    "allow_public_thread": 1,
                    "snippet": "Study the microscope lab notes.",
                    "has_active_thread": 1,
                },
            },
        ]
        school_event_items = [
            {
                "kind": "school_event",
                "item_id": "event::EVENT-1",
                "sort_at": "2026-04-15T09:00:00",
                "source_type": "school",
                "source_label": "School Event",
                "context_label": "SCHOOL-1",
                "matched_children": children,
                "school_event": {
                    "name": "EVENT-1",
                    "subject": "Spring Showcase",
                    "school": "SCHOOL-1",
                    "location": "Main Hall",
                    "event_type": "Performance",
                    "event_category": "Other",
                    "description": "Families are welcome.",
                    "snippet": "Families are welcome.",
                    "starts_on": "2026-04-15T09:00:00",
                    "ends_on": "2026-04-15T11:00:00",
                    "all_day": 0,
                },
            }
        ]

        with (
            patch(
                "ifitwala_ed.students.api.guardian_communications.now_datetime",
                return_value=frappe.utils.get_datetime("2026-04-15 09:00:00"),
            ),
            patch(
                "ifitwala_ed.students.api.guardian_communications._resolve_guardian_communication_context",
                return_value={
                    "children": children,
                    "student_names": ["STU-1", "STU-2"],
                },
            ) as context_mock,
            patch(
                "ifitwala_ed.students.api.guardian_communications._fetch_guardian_org_communications",
                return_value=org_items,
            ) as fetch_org_mock,
            patch(
                "ifitwala_ed.students.api.guardian_communications._fetch_guardian_school_events",
                return_value=school_event_items,
            ) as fetch_event_mock,
        ):
            payload = get_guardian_communication_center(student="STU-1", page_length=10)

        fetch_org_mock.assert_called_once_with(context_mock.return_value, selected_student="STU-1")
        fetch_event_mock.assert_called_once_with(context_mock.return_value, selected_student="STU-1")
        self.assertEqual(payload["meta"]["student"], "STU-1")
        self.assertEqual(payload["summary"]["total_items"], 3)
        self.assertEqual(payload["summary"]["unread_items"], 1)
        self.assertEqual(payload["summary"]["source_counts"], {"school": 2, "course": 1})
        self.assertEqual(payload["family"]["children"], children)
        self.assertEqual(payload["items"], school_event_items + org_items)

    def test_fetch_candidate_rows_includes_organization_guardian_audiences(self):
        captured: dict[str, object] = {}

        def fake_sql(sql, values, as_dict=False):
            captured["sql"] = sql
            captured["values"] = values
            return []

        with (
            patch("ifitwala_ed.students.api.guardian_communications._recent_start_date", return_value="2026-01-10"),
            patch.object(guardian_communications.frappe.db, "sql", side_effect=fake_sql),
        ):
            rows = guardian_communications._fetch_candidate_rows(
                target_groups=set(),
                school_targets=set(),
                organization_targets={"ORG-ROOT"},
            )

        self.assertEqual(rows, [])
        self.assertIn("a.target_mode = 'Organization'", str(captured.get("sql") or ""))
        self.assertEqual((captured.get("values") or {}).get("organization_targets"), ("ORG-ROOT",))

    def test_matched_students_for_audience_allows_organization_targets(self):
        matched_students, matched_groups = guardian_communications._matched_students_for_audience(
            {
                "target_mode": "Organization",
                "to_guardians": 1,
            },
            context={
                "student_names": ["STU-1", "STU-2"],
                "eligible_organization_targets_by_student": {
                    "STU-1": {"ORG-CHILD", "ORG-ROOT"},
                    "STU-2": {"ORG-SIBLING"},
                },
            },
            selected_student=None,
            descendants_cache={},
            comm_organization="ORG-ROOT",
        )

        self.assertEqual(matched_students, {"STU-1"})
        self.assertEqual(matched_groups, set())

    def test_fetch_guardian_school_events_does_not_query_missing_event_type_column(self):
        children = [
            {"student": "STU-1", "full_name": "Amina Example", "school": "SCHOOL-1"},
            {"student": "STU-2", "full_name": "Noah Example", "school": "SCHOOL-2"},
        ]
        context = {
            "user": "guardian@example.com",
            "children": children,
            "child_by_student": {row["student"]: row for row in children},
            "student_names": ["STU-1", "STU-2"],
            "student_school_names": {
                "STU-1": {"SCHOOL-1"},
                "STU-2": {"SCHOOL-2"},
            },
            "membership_by_student": {
                "STU-1": {"GROUP-1"},
                "STU-2": {"GROUP-2"},
            },
        }
        captured: dict[str, object] = {}

        def fake_sql(sql, values, as_dict=False):
            captured["sql"] = sql
            captured["values"] = values
            return [
                {
                    "name": "SE-0001",
                    "subject": "Assembly",
                    "school": "SCHOOL-1",
                    "location": "Hall",
                    "event_category": "Other",
                    "description": "<p>Bring your planner.</p>",
                    "starts_on": "2026-04-10 08:00:00",
                    "ends_on": "2026-04-10 09:00:00",
                    "all_day": 0,
                    "creation": "2026-04-09 12:00:00",
                }
            ]

        def fake_get_all(doctype, filters=None, fields=None):
            if doctype == "School Event Audience":
                return [
                    {
                        "parent": "SE-0001",
                        "audience_type": "Students in Student Group",
                        "student_group": "GROUP-1",
                        "include_guardians": 1,
                        "include_students": 0,
                    }
                ]
            if doctype == "School Event Participant":
                return []
            self.fail(f"Unexpected doctype fetch: {doctype}")

        with (
            patch("ifitwala_ed.students.api.guardian_communications._recent_start_date", return_value="2026-01-10"),
            patch.object(guardian_communications.frappe.db, "sql", side_effect=fake_sql),
            patch.object(guardian_communications.frappe, "get_all", side_effect=fake_get_all),
        ):
            items = guardian_communications._fetch_guardian_school_events(context)

        self.assertNotIn("se.event_type", str(captured.get("sql") or ""))
        self.assertEqual(
            captured.get("values"),
            {
                "window_start": "2026-01-10",
                "user": "guardian@example.com",
                "target_schools": ("SCHOOL-1", "SCHOOL-2"),
            },
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["school_event"]["subject"], "Assembly")
        self.assertIsNone(items[0]["school_event"]["event_type"])
        self.assertEqual(items[0]["matched_children"], [children[0]])

    def test_fetch_guardian_school_events_matches_parent_school_events_to_descendant_school_children(self):
        children = [
            {"student": "STU-1", "full_name": "Amina Example", "school": "IHS"},
        ]
        context = {
            "user": "guardian@example.com",
            "children": children,
            "child_by_student": {row["student"]: row for row in children},
            "student_names": ["STU-1"],
            "student_school_names": {
                "STU-1": {"IHS"},
            },
            "eligible_school_targets_by_student": {
                "STU-1": {"IHS", "ISS"},
            },
            "membership_by_student": {
                "STU-1": {"GROUP-1"},
            },
        }
        captured: dict[str, object] = {}

        def fake_sql(sql, values, as_dict=False):
            captured["values"] = values
            return [
                {
                    "name": "SE-ISS-0001",
                    "subject": "ISS Parent Workshop",
                    "school": "ISS",
                    "location": "Hall",
                    "event_category": "Parent Engagement",
                    "description": "<p>Parents only.</p>",
                    "starts_on": "2026-04-10 08:00:00",
                    "ends_on": "2026-04-10 09:00:00",
                    "all_day": 0,
                    "creation": "2026-04-09 12:00:00",
                }
            ]

        def fake_get_all(doctype, filters=None, fields=None):
            if doctype == "School Event Audience":
                return [
                    {
                        "parent": "SE-ISS-0001",
                        "audience_type": "All Guardians",
                        "student_group": None,
                        "include_guardians": 0,
                        "include_students": 0,
                    }
                ]
            if doctype == "School Event Participant":
                return []
            self.fail(f"Unexpected doctype fetch: {doctype}")

        with (
            patch("ifitwala_ed.students.api.guardian_communications._recent_start_date", return_value="2026-01-10"),
            patch.object(guardian_communications.frappe.db, "sql", side_effect=fake_sql),
            patch.object(guardian_communications.frappe, "get_all", side_effect=fake_get_all),
        ):
            items = guardian_communications._fetch_guardian_school_events(context)

        self.assertEqual((captured.get("values") or {}).get("target_schools"), ("IHS", "ISS"))
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["school_event"]["school"], "ISS")
        self.assertEqual(items[0]["matched_children"], children)

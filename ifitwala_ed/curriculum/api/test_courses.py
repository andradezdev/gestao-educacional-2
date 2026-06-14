from datetime import datetime
from types import ModuleType, SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _parse_datetime(value):
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace(" ", "T"))


def _student_work_done(row):
    return bool(
        int(row.get("is_complete") or 0)
        or str(row.get("submission_status") or "") == "Submitted"
        or str(row.get("grading_status") or "") == "Released"
    )


def _student_task_status_label(row, anchor_dt):
    if str(row.get("grading_status") or "") == "Released" or int(row.get("is_complete") or 0):
        return "Completed"
    if str(row.get("submission_status") or "") == "Submitted" or int(row.get("has_submission") or 0):
        return "Submitted"

    available_from = row.get("available_from")
    if available_from and _parse_datetime(available_from) > anchor_dt:
        return "Not Yet Open"

    due_date = row.get("due_date")
    if due_date and _parse_datetime(due_date) < anchor_dt:
        return "Overdue"

    return "Upcoming"


def _courses_stub_modules():
    frappe_utils = ModuleType("frappe.utils")
    frappe_utils.get_datetime = _parse_datetime
    frappe_utils.now_datetime = lambda: datetime(2026, 3, 12, 10, 0, 0)

    course_schedule = ModuleType("ifitwala_ed.schedule.api.course_schedule")
    course_schedule.get_today_courses = lambda: {"date": "2026-03-12", "weekday": "Thursday", "courses": []}

    portal = ModuleType("ifitwala_ed.api.portal")
    portal.get_student_portal_identity = lambda: {
        "display_name": "Amina",
        "student": "STU-001",
        "user": "student@example.com",
    }

    family_consent = ModuleType("ifitwala_ed.api.family_consent")
    family_consent.get_student_consent_home_summary = lambda student_name: {"pending_count": 0, "items": []}

    student_policy = ModuleType("ifitwala_ed.api.student_policy")
    student_policy.get_student_policy_home_summary = lambda student_name: {"pending_count": 0, "items": []}

    student_task_status = ModuleType("ifitwala_ed.assessment.api.student_task_status")
    student_task_status.build_student_task_status_label = _student_task_status_label
    student_task_status.is_student_work_done = _student_work_done

    student_communications = ModuleType("ifitwala_ed.students.api.student_communications")
    student_communications.get_student_home_communication_summary = lambda student_name: {
        "center_href": {"name": "student-communications"},
        "latest_course_update": None,
        "latest_activity_update": None,
        "latest_school_update": None,
    }

    return {
        "frappe.utils": frappe_utils,
        "ifitwala_ed.schedule.api.course_schedule": course_schedule,
        "ifitwala_ed.api.course_schedule": course_schedule,
        "ifitwala_ed.api.portal": portal,
        "ifitwala_ed.api.family_consent": family_consent,
        "ifitwala_ed.api.student_policy": student_policy,
        "ifitwala_ed.assessment.api.student_task_status": student_task_status,
        "ifitwala_ed.students.api.student_communications": student_communications,
    }


class TestCoursesApi(TestCase):
    def setUp(self):
        self._frappe_context = stubbed_frappe(extra_modules=_courses_stub_modules())
        self.frappe = self._frappe_context.__enter__()
        self.frappe.db.sql = lambda *args, **kwargs: []
        self.frappe.db.get_value = lambda *args, **kwargs: None
        self.courses_api = import_fresh("ifitwala_ed.curriculum.api.courses")

    def tearDown(self):
        self._frappe_context.__exit__(None, None, None)

    def test_get_courses_data_includes_learning_space_readiness(self):
        with (
            patch.object(self.courses_api.frappe, "session", SimpleNamespace(user="student@example.com")),
            patch.object(self.courses_api.frappe, "get_roles", return_value=["Student"]),
            patch.object(self.courses_api, "_get_student_name_for_user", return_value="STU-001"),
            patch.object(self.courses_api, "_get_academic_years", return_value=["2025-2026"]),
            patch.object(
                self.courses_api,
                "_build_student_course_scope",
                return_value={
                    "COURSE-1": {
                        "student_groups": [
                            {
                                "student_group": "GROUP-1",
                                "student_group_name": "Biology A",
                                "academic_year": "2025-2026",
                            }
                        ]
                    },
                    "COURSE-2": {"student_groups": []},
                    "COURSE-3": {
                        "student_groups": [
                            {
                                "student_group": "GROUP-3",
                                "student_group_name": "History A",
                                "academic_year": "2025-2026",
                            }
                        ]
                    },
                },
            ),
            patch.object(
                self.courses_api,
                "_get_courses_for_year",
                return_value=[
                    {
                        "course": "COURSE-1",
                        "course_name": "Biology",
                        "course_group": "Science",
                        "course_image": "/files/biology.jpg",
                        "href": {"name": "student-course-detail", "params": {"course_id": "COURSE-1"}},
                    },
                    {
                        "course": "COURSE-2",
                        "course_name": "Design",
                        "course_group": "Arts",
                        "course_image": "/files/design.jpg",
                        "href": {"name": "student-course-detail", "params": {"course_id": "COURSE-2"}},
                    },
                    {
                        "course": "COURSE-3",
                        "course_name": "History",
                        "course_group": "Humanities",
                        "course_image": "/files/history.jpg",
                        "href": {"name": "student-course-detail", "params": {"course_id": "COURSE-3"}},
                    },
                ],
            ),
            patch.object(self.courses_api, "_fetch_active_class_plan_groups", return_value={"GROUP-1"}),
            patch.object(
                self.courses_api,
                "_fetch_active_course_plan_counts",
                return_value={"COURSE-1": 0, "COURSE-2": 1, "COURSE-3": 0},
            ),
        ):
            payload = self.courses_api.get_courses_data("2025-2026")

        self.assertEqual(payload["courses"][0]["learning_space"]["status"], "ready")
        self.assertEqual(payload["courses"][0]["learning_space"]["cta_label"], "Open class")
        self.assertEqual(payload["courses"][1]["learning_space"]["status"], "shared_plan_only")
        self.assertEqual(payload["courses"][1]["learning_space"]["cta_label"], "Open shared plan")
        self.assertEqual(payload["courses"][2]["learning_space"]["status"], "awaiting_class_plan")
        self.assertEqual(payload["courses"][2]["learning_space"]["can_open"], 0)
        self.assertIsNone(payload["courses"][2]["href"])

    def test_get_student_hub_home_prefers_today_class_for_next_step(self):
        anchor = datetime(2026, 3, 12, 8, 45, 0)
        with (
            patch("ifitwala_ed.curriculum.api.courses._require_student_name_for_session_user", return_value="STU-001"),
            patch("ifitwala_ed.curriculum.api.courses._build_student_course_scope", return_value={"COURSE-1": {}}),
            patch("ifitwala_ed.curriculum.api.courses.now_datetime", return_value=anchor),
            patch(
                "ifitwala_ed.curriculum.api.courses.get_student_policy_home_summary",
                return_value={"pending_count": 1, "items": [{"policy_version": "VER-1"}]},
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses.portal_api.get_student_portal_identity",
                return_value={"display_name": "Amina", "student": "STU-001", "user": "student@example.com"},
            ),
            patch.object(
                self.courses_api.student_communications_api,
                "get_student_home_communication_summary",
                return_value={
                    "center_href": {"name": "student-communications"},
                    "latest_course_update": None,
                    "latest_activity_update": None,
                    "latest_school_update": None,
                },
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses.course_schedule_api.get_today_courses",
                return_value={
                    "date": "2026-03-12",
                    "weekday": "Thursday",
                    "courses": [
                        {
                            "course": "COURSE-1",
                            "course_name": "Biology",
                            "time_slots": [
                                {
                                    "from_time": "10:00",
                                    "to_time": "11:00",
                                    "time_range": "10:00 - 11:00",
                                }
                            ],
                            "href": {"name": "student-course-detail", "params": {"course_id": "COURSE-1"}},
                        }
                    ],
                },
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses.get_courses_data",
                return_value={"selected_year": "2025-2026", "courses": []},
            ),
        ):
            payload = self.courses_api.get_student_hub_home()

        self.assertEqual(payload["identity"]["display_name"], "Amina")
        self.assertEqual(payload["policies"]["pending_count"], 1)
        self.assertEqual(payload["learning"]["today_classes"][0]["course"], "COURSE-1")
        self.assertEqual(payload["learning"]["next_learning_step"]["kind"], "scheduled_class")
        self.assertEqual(payload["learning"]["next_learning_step"]["title"], "Biology")
        self.assertEqual(payload["communications"]["center_href"]["name"], "student-communications")

    def test_get_student_hub_home_falls_back_to_first_accessible_course(self):
        with (
            patch("ifitwala_ed.curriculum.api.courses._require_student_name_for_session_user", return_value="STU-001"),
            patch(
                "ifitwala_ed.curriculum.api.courses.get_student_policy_home_summary",
                return_value={"pending_count": 0, "items": []},
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses._build_student_course_scope",
                return_value={"COURSE-1": {}, "COURSE-2": {}},
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses.portal_api.get_student_portal_identity",
                return_value={"display_name": "Amina", "student": "STU-001", "user": "student@example.com"},
            ),
            patch.object(
                self.courses_api.student_communications_api,
                "get_student_home_communication_summary",
                return_value={
                    "center_href": {"name": "student-communications"},
                    "latest_course_update": None,
                    "latest_activity_update": None,
                    "latest_school_update": None,
                },
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses.course_schedule_api.get_today_courses",
                return_value={"date": "2026-03-12", "weekday": "Thursday", "courses": []},
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses._build_student_courses_payload",
                return_value=(
                    {
                        "selected_year": "2025-2026",
                        "courses": [
                            {
                                "course": "COURSE-2",
                                "course_name": "History",
                                "href": {"name": "student-course-detail", "params": {"course_id": "COURSE-2"}},
                                "learning_space": {
                                    "status": "shared_plan_only",
                                    "status_label": "Shared Plan",
                                    "summary": "Open the shared course plan for now.",
                                    "cta_label": "Open shared plan",
                                    "can_open": 1,
                                    "href": {"name": "student-course-detail", "params": {"course_id": "COURSE-2"}},
                                },
                            }
                        ],
                    },
                    {"COURSE-1": {}, "COURSE-2": {}},
                ),
            ),
        ):
            payload = self.courses_api.get_student_hub_home()

        self.assertEqual(payload["learning"]["next_learning_step"]["kind"], "course")
        self.assertEqual(payload["learning"]["next_learning_step"]["title"], "History")
        self.assertEqual(payload["learning"]["accessible_courses_count"], 2)

    def test_get_student_hub_home_prefers_first_openable_course_when_first_course_is_blocked(self):
        with (
            patch("ifitwala_ed.curriculum.api.courses._require_student_name_for_session_user", return_value="STU-001"),
            patch(
                "ifitwala_ed.curriculum.api.courses.get_student_policy_home_summary",
                return_value={"pending_count": 0, "items": []},
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses._build_student_courses_payload",
                return_value=(
                    {
                        "selected_year": "2025-2026",
                        "courses": [
                            {
                                "course": "COURSE-1",
                                "course_name": "Biology",
                                "href": None,
                                "learning_space": {
                                    "status": "awaiting_class_assignment",
                                    "status_label": "Class Assignment Pending",
                                    "summary": "Your class is still being assigned.",
                                    "cta_label": "Not ready yet",
                                    "can_open": 0,
                                    "href": None,
                                },
                            },
                            {
                                "course": "COURSE-2",
                                "course_name": "History",
                                "href": {"name": "student-course-detail", "params": {"course_id": "COURSE-2"}},
                                "learning_space": {
                                    "status": "shared_plan_only",
                                    "status_label": "Shared Plan",
                                    "summary": "Open the shared course plan for now.",
                                    "cta_label": "Open shared plan",
                                    "can_open": 1,
                                    "href": {
                                        "name": "student-course-detail",
                                        "params": {"course_id": "COURSE-2"},
                                    },
                                },
                            },
                        ],
                    },
                    {"COURSE-1": {}, "COURSE-2": {}},
                ),
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses.portal_api.get_student_portal_identity",
                return_value={"display_name": "Amina", "student": "STU-001", "user": "student@example.com"},
            ),
            patch.object(
                self.courses_api.student_communications_api,
                "get_student_home_communication_summary",
                return_value={
                    "center_href": {"name": "student-communications"},
                    "latest_course_update": None,
                    "latest_activity_update": None,
                    "latest_school_update": None,
                },
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses.course_schedule_api.get_today_courses",
                return_value={"date": "2026-03-12", "weekday": "Thursday", "courses": []},
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses._fetch_student_hub_task_rows",
                return_value=[],
            ),
        ):
            payload = self.courses_api.get_student_hub_home()

        self.assertEqual(payload["learning"]["next_learning_step"]["title"], "History")
        self.assertEqual(payload["learning"]["next_learning_step"]["cta_label"], "Open shared plan")
        self.assertEqual(payload["learning"]["next_learning_step"]["status_label"], "Shared Plan")
        self.assertEqual(payload["learning"]["next_learning_step"]["can_open"], 1)

    def test_build_home_orientation_finds_current_and_next_class(self):
        anchor = datetime(2026, 3, 13, 9, 15, 0)
        orientation = self.courses_api._build_home_orientation(
            [
                {
                    "course": "COURSE-1",
                    "course_name": "Biology",
                    "time_slots": [{"from_time": "08:30", "to_time": "09:30"}],
                },
                {
                    "course": "COURSE-2",
                    "course_name": "History",
                    "time_slots": [{"from_time": "10:00", "to_time": "11:00"}],
                },
            ],
            anchor,
        )

        self.assertEqual(orientation["current_class"]["course"], "COURSE-1")
        self.assertEqual(orientation["next_class"]["course"], "COURSE-2")

    def test_build_work_board_payload_sorts_open_and_done_lanes(self):
        anchor = datetime(2026, 3, 13, 9, 0, 0)
        board = self.courses_api._build_work_board_payload(
            [
                {
                    "task_delivery": "TD-OVERDUE",
                    "task": "TASK-1",
                    "title": "Overdue essay",
                    "course": "COURSE-1",
                    "course_name": "Biology",
                    "due_date": "2026-03-12 09:00:00",
                    "submission_status": "Not Submitted",
                    "grading_status": "Not Started",
                    "has_submission": 0,
                    "is_complete": 0,
                },
                {
                    "task_delivery": "TD-SOON",
                    "task": "TASK-2",
                    "title": "Quiz review",
                    "course": "COURSE-1",
                    "course_name": "Biology",
                    "due_date": "2026-03-18 09:00:00",
                    "submission_status": "Not Submitted",
                    "grading_status": "Not Started",
                    "has_submission": 0,
                    "is_complete": 0,
                },
                {
                    "task_delivery": "TD-LATER",
                    "task": "TASK-3",
                    "title": "Long-term project",
                    "course": "COURSE-2",
                    "course_name": "History",
                    "due_date": "2026-03-28 09:00:00",
                    "submission_status": "Not Submitted",
                    "grading_status": "Not Started",
                    "has_submission": 0,
                    "is_complete": 0,
                },
                {
                    "task_delivery": "TD-DONE",
                    "task": "TASK-4",
                    "title": "Submitted report",
                    "course": "COURSE-2",
                    "course_name": "History",
                    "submission_status": "Submitted",
                    "grading_status": "Not Started",
                    "has_submission": 1,
                    "is_complete": 0,
                    "completed_on": "2026-03-13 08:00:00",
                },
            ],
            anchor,
        )

        self.assertEqual([item["task_delivery"] for item in board["now"]], ["TD-OVERDUE"])
        self.assertEqual([item["task_delivery"] for item in board["soon"]], ["TD-SOON"])
        self.assertEqual([item["task_delivery"] for item in board["later"]], ["TD-LATER"])
        self.assertEqual([item["task_delivery"] for item in board["done"]], ["TD-DONE"])
        self.assertEqual(board["now"][0]["status_label"], "Overdue")
        self.assertEqual(board["soon"][0]["status_label"], "Upcoming")
        self.assertEqual(board["later"][0]["status_label"], "Upcoming")
        self.assertEqual(board["done"][0]["status_label"], "Submitted")

    def test_build_work_item_status_label_hides_internal_grading_states(self):
        anchor = datetime(2026, 3, 13, 9, 0, 0)

        self.assertEqual(
            self.courses_api._build_work_item_status_label(
                {
                    "grading_status": "Released",
                    "submission_status": "Not Submitted",
                    "is_complete": 0,
                },
                anchor,
            ),
            "Completed",
        )
        self.assertEqual(
            self.courses_api._build_work_item_status_label(
                {
                    "available_from": "2026-03-13 11:00:00",
                    "due_date": "2026-03-15 09:00:00",
                    "submission_status": "Not Submitted",
                    "grading_status": "Not Started",
                    "is_complete": 0,
                },
                anchor,
            ),
            "Not Yet Open",
        )

    def test_get_student_hub_home_includes_board_and_timeline(self):
        anchor = datetime(2026, 3, 13, 8, 45, 0)
        with (
            patch("ifitwala_ed.curriculum.api.courses._require_student_name_for_session_user", return_value="STU-001"),
            patch(
                "ifitwala_ed.curriculum.api.courses._build_student_course_scope",
                return_value={
                    "COURSE-1": {
                        "student_groups": [{"student_group": "GROUP-1"}],
                    }
                },
            ),
            patch("ifitwala_ed.curriculum.api.courses.now_datetime", return_value=anchor),
            patch(
                "ifitwala_ed.curriculum.api.courses.get_student_policy_home_summary",
                return_value={"pending_count": 2, "items": [{"policy_version": "VER-1"}]},
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses.portal_api.get_student_portal_identity",
                return_value={"display_name": "Amina", "student": "STU-001", "user": "student@example.com"},
            ),
            patch.object(
                self.courses_api.student_communications_api,
                "get_student_home_communication_summary",
                return_value={
                    "center_href": {"name": "student-communications"},
                    "latest_course_update": None,
                    "latest_activity_update": None,
                    "latest_school_update": None,
                },
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses.course_schedule_api.get_today_courses",
                return_value={
                    "date": "2026-03-13",
                    "weekday": "Friday",
                    "courses": [
                        {
                            "course": "COURSE-1",
                            "course_name": "Biology",
                            "student_group": "GROUP-1",
                            "student_group_name": "Biology 8A",
                            "time_slots": [{"from_time": "10:00", "to_time": "11:00", "time_range": "10:00 - 11:00"}],
                            "href": {"name": "student-course-detail", "params": {"course_id": "COURSE-1"}},
                        }
                    ],
                },
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses.get_courses_data",
                return_value={"selected_year": "2025-2026", "courses": []},
            ),
            patch(
                "ifitwala_ed.curriculum.api.courses._fetch_student_hub_task_rows",
                return_value=[
                    {
                        "task_delivery": "TD-1",
                        "task": "TASK-1",
                        "title": "Lab notes",
                        "course": "COURSE-1",
                        "course_name": "Biology",
                        "student_group": "GROUP-1",
                        "delivery_mode": "Collect Work",
                        "requires_submission": 1,
                        "require_grading": 1,
                        "due_date": "2026-03-14 09:00:00",
                        "unit_plan": "LU-1",
                        "class_session": "CLASS-SESSION-1",
                        "submission_status": "Not Submitted",
                        "grading_status": "Not Started",
                        "has_submission": 0,
                        "has_new_submission": 0,
                        "is_complete": 0,
                    }
                ],
            ),
        ):
            payload = self.courses_api.get_student_hub_home()

        self.assertIn("orientation", payload["learning"])
        self.assertEqual(payload["policies"]["pending_count"], 2)
        self.assertIn("work_board", payload["learning"])
        self.assertIn("timeline", payload["learning"])
        self.assertEqual(payload["learning"]["work_board"]["now"][0]["task_delivery"], "TD-1")
        self.assertEqual(
            payload["learning"]["work_board"]["now"][0]["href"]["query"]["student_group"],
            "GROUP-1",
        )
        self.assertEqual(
            payload["learning"]["work_board"]["now"][0]["href"]["query"]["class_session"],
            "CLASS-SESSION-1",
        )
        self.assertEqual(
            payload["learning"]["work_board"]["now"][0]["href"]["query"]["task_delivery"],
            "TD-1",
        )
        self.assertEqual(payload["learning"]["work_board"]["now"][0]["status_label"], "Upcoming")
        self.assertEqual(payload["learning"]["timeline"][1]["items"][0]["status_label"], "Upcoming")
        self.assertEqual(payload["learning"]["timeline"][0]["items"][0]["kind"], "scheduled_class")

    def test_build_work_item_href_preserves_class_session_context(self):
        href = self.courses_api._build_work_item_href(
            {
                "course": "COURSE-1",
                "student_group": "GROUP-1",
                "unit_plan": "UNIT-1",
                "class_session": "SESSION-3",
                "task_delivery": "TD-17",
            }
        )

        self.assertEqual(
            href,
            {
                "name": "student-course-detail",
                "params": {"course_id": "COURSE-1"},
                "query": {
                    "student_group": "GROUP-1",
                    "unit_plan": "UNIT-1",
                    "class_session": "SESSION-3",
                    "task_delivery": "TD-17",
                },
            },
        )

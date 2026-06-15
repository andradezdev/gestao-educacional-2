from __future__ import annotations

import types
from unittest import TestCase

from ifitwala_ed.assessment.api.test_task import _task_service_stub
from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _task_facade_stub_modules():
    planning_module = types.ModuleType("ifitwala_ed.curriculum.planning")
    planning_module.assert_can_manage_course_curriculum = lambda *args, **kwargs: None
    planning_module.assert_can_read_course_curriculum = lambda *args, **kwargs: None
    return {
        "ifitwala_ed.curriculum.planning": planning_module,
        "ifitwala_ed.assessment.task_delivery_service": _task_service_stub(),
    }


class TestTaskFacade(TestCase):
    def test_root_task_facade_delegates_search_methods(self):
        calls: list[tuple[str, object]] = []

        with stubbed_frappe(extra_modules=_task_facade_stub_modules()):
            module = import_fresh("ifitwala_ed.api.task")

            def fake_search_tasks(filters=None, query=None, limit=20, start=0):
                calls.append(("search_tasks", {"filters": filters, "query": query, "limit": limit, "start": start}))
                return [{"name": "TASK-1"}]

            def fake_search_reusable_tasks(
                student_group=None, course=None, unit_plan=None, query=None, scope=None, limit=20, start=0
            ):
                calls.append(
                    (
                        "search_reusable_tasks",
                        {
                            "student_group": student_group,
                            "course": course,
                            "unit_plan": unit_plan,
                            "query": query,
                            "scope": scope,
                            "limit": limit,
                            "start": start,
                        },
                    )
                )
                return [{"name": "TASK-2"}]

            module._impl.search_tasks = fake_search_tasks
            module._impl.search_reusable_tasks = fake_search_reusable_tasks

            search_payload = module.search_tasks(filters={"course": "COURSE-1"}, query="essay", limit=5, start=2)
            reusable_payload = module.search_reusable_tasks(
                student_group="GRP-1",
                course="COURSE-1",
                unit_plan="UNIT-1",
                query="lab",
                scope="shared",
                limit=7,
                start=3,
            )

        self.assertEqual(search_payload, [{"name": "TASK-1"}])
        self.assertEqual(reusable_payload, [{"name": "TASK-2"}])
        self.assertEqual(calls[0][0], "search_tasks")
        self.assertEqual(calls[0][1]["filters"], {"course": "COURSE-1"})
        self.assertEqual(calls[1][0], "search_reusable_tasks")
        self.assertEqual(calls[1][1]["student_group"], "GRP-1")

    def test_root_task_facade_delegates_delivery_setup_methods(self):
        calls: list[tuple[str, object]] = []

        with stubbed_frappe(extra_modules=_task_facade_stub_modules()):
            module = import_fresh("ifitwala_ed.api.task")

            def fake_get_task_for_delivery(task, student_group=None, course=None):
                calls.append(
                    ("get_task_for_delivery", {"task": task, "student_group": student_group, "course": course})
                )
                return {"name": task}

            def fake_list_course_assessment_criteria(student_group=None, course=None):
                calls.append(("list_course_assessment_criteria", {"student_group": student_group, "course": course}))
                return [{"assessment_criteria": "CRIT-1"}]

            def fake_get_assessment_setup_for_delivery(student_group=None, course=None):
                calls.append(("get_assessment_setup_for_delivery", {"student_group": student_group, "course": course}))
                return {"course": course}

            def fake_create_task_delivery(payload):
                calls.append(("create_task_delivery", payload))
                return {"task_delivery": "TDL-1"}

            module._impl.get_task_for_delivery = fake_get_task_for_delivery
            module._impl.list_course_assessment_criteria = fake_list_course_assessment_criteria
            module._impl.get_assessment_setup_for_delivery = fake_get_assessment_setup_for_delivery
            module._impl.create_task_delivery = fake_create_task_delivery

            task_payload = module.get_task_for_delivery("TASK-1", student_group="GRP-1", course="COURSE-1")
            criteria_payload = module.list_course_assessment_criteria(student_group="GRP-1", course="COURSE-1")
            setup_payload = module.get_assessment_setup_for_delivery(student_group="GRP-1", course="COURSE-1")
            delivery_payload = module.create_task_delivery({"task": "TASK-1"})

        self.assertEqual(task_payload, {"name": "TASK-1"})
        self.assertEqual(criteria_payload, [{"assessment_criteria": "CRIT-1"}])
        self.assertEqual(setup_payload, {"course": "COURSE-1"})
        self.assertEqual(delivery_payload, {"task_delivery": "TDL-1"})
        self.assertEqual(
            [name for name, _payload in calls],
            [
                "get_task_for_delivery",
                "list_course_assessment_criteria",
                "get_assessment_setup_for_delivery",
                "create_task_delivery",
            ],
        )

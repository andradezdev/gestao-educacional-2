from __future__ import annotations

from unittest import TestCase

from ifitwala_ed.curriculum.api.test_materials import _materials_stub_modules
from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


class TestMaterialsFacade(TestCase):
    def test_root_materials_facade_delegates_task_material_methods(self):
        calls: list[tuple[str, object]] = []

        with stubbed_frappe(extra_modules=_materials_stub_modules()):
            module = import_fresh("ifitwala_ed.api.materials")

            def fake_list_task_materials(task):
                calls.append(("list_task_materials", task))
                return {"task": task, "materials": []}

            def fake_create_task_reference_material(payload=None, **kwargs):
                calls.append(("create_task_reference_material", {"payload": payload, "kwargs": kwargs}))
                return {"material": "MAT-1"}

            def fake_upload_task_material_file(
                task=None,
                title=None,
                description=None,
                modality=None,
                usage_role=None,
                placement_note=None,
            ):
                calls.append(
                    (
                        "upload_task_material_file",
                        {
                            "task": task,
                            "title": title,
                            "description": description,
                            "modality": modality,
                            "usage_role": usage_role,
                            "placement_note": placement_note,
                        },
                    )
                )
                return {"material": "MAT-2"}

            def fake_remove_task_material(payload=None, **kwargs):
                calls.append(("remove_task_material", {"payload": payload, "kwargs": kwargs}))
                return {"removed": 1}

            module._impl.list_task_materials = fake_list_task_materials
            module._impl.create_task_reference_material = fake_create_task_reference_material
            module._impl.upload_task_material_file = fake_upload_task_material_file
            module._impl.remove_task_material = fake_remove_task_material

            list_payload = module.list_task_materials("TASK-1")
            reference_payload = module.create_task_reference_material(payload={"task": "TASK-1"}, origin="task")
            upload_payload = module.upload_task_material_file(
                task="TASK-1",
                title="Lab guide",
                description="Read first.",
                modality="Reading",
                usage_role="Reference",
                placement_note="Before class",
            )
            remove_payload = module.remove_task_material(payload={"task": "TASK-1"}, placement="PLACEMENT-1")

        self.assertEqual(list_payload, {"task": "TASK-1", "materials": []})
        self.assertEqual(reference_payload, {"material": "MAT-1"})
        self.assertEqual(upload_payload, {"material": "MAT-2"})
        self.assertEqual(remove_payload, {"removed": 1})
        self.assertEqual(
            [name for name, _payload in calls],
            [
                "list_task_materials",
                "create_task_reference_material",
                "upload_task_material_file",
                "remove_task_material",
            ],
        )
        self.assertEqual(calls[1][1]["payload"], {"task": "TASK-1"})
        self.assertEqual(calls[1][1]["kwargs"], {"origin": "task"})
        self.assertEqual(calls[2][1]["placement_note"], "Before class")
        self.assertEqual(calls[3][1]["kwargs"], {"placement": "PLACEMENT-1"})

    def test_root_materials_facade_exposes_curriculum_helper_surface(self):
        with stubbed_frappe(extra_modules=_materials_stub_modules()):
            module = import_fresh("ifitwala_ed.api.materials")

        self.assertIs(module._serialize_task_material, module._impl._serialize_task_material)
        self.assertIs(
            module._assert_supported_task_attachment_upload,
            module._impl._assert_supported_task_attachment_upload,
        )

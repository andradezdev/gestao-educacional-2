from __future__ import annotations

import frappe

from ifitwala_ed.curriculum.api import materials as _impl


def __getattr__(name: str):
    return getattr(_impl, name)


@frappe.whitelist()
def list_task_materials(task: str):
    return _impl.list_task_materials(task=task)


@frappe.whitelist()
def create_task_reference_material(payload=None, **kwargs):
    return _impl.create_task_reference_material(payload=payload, **kwargs)


@frappe.whitelist()
def upload_task_material_file(
    task: str | None = None,
    title: str | None = None,
    description: str | None = None,
    modality: str | None = None,
    usage_role: str | None = None,
    placement_note: str | None = None,
):
    return _impl.upload_task_material_file(
        task=task,
        title=title,
        description=description,
        modality=modality,
        usage_role=usage_role,
        placement_note=placement_note,
    )


@frappe.whitelist()
def remove_task_material(payload=None, **kwargs):
    return _impl.remove_task_material(payload=payload, **kwargs)


__all__ = [
    "list_task_materials",
    "create_task_reference_material",
    "upload_task_material_file",
    "remove_task_material",
]

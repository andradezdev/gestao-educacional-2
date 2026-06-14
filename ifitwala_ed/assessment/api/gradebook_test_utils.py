# ifitwala_ed/assessment/api/gradebook_test_utils.py

from __future__ import annotations

import types

from ifitwala_ed.tests.frappe_stubs import import_fresh


def _gradebook_stub_modules(
    task_contribution_service=None,
    task_feedback_service=None,
    task_feedback_artifact_service=None,
    task_feedback_comment_bank_service=None,
    task_feedback_thread_service=None,
    task_outcome_service=None,
):
    image_utils = types.ModuleType("ifitwala_ed.utilities.image_utils")
    image_utils.PROFILE_IMAGE_DERIVATIVE_SLOTS = (
        "profile_image_thumb",
        "profile_image_card",
        "profile_image_medium",
    )
    image_utils.apply_preferred_student_images = lambda rows: rows
    quiz_service = types.ModuleType("ifitwala_ed.assessment.quiz_service")
    quiz_service.MANUAL_TYPES = {"Essay"}
    quiz_service.refresh_attempt = lambda *args, **kwargs: {"attempt": {"name": args[0] if args else "QAT-1"}}
    feedback_service = task_feedback_service or types.ModuleType("ifitwala_ed.assessment.task_feedback_service")
    if not hasattr(feedback_service, "build_feedback_workspace_payload"):
        feedback_service.build_feedback_workspace_payload = lambda outcome_id, submission_id, include_defaults=True: {
            "workspace_id": None,
            "task_outcome": outcome_id,
            "task_submission": submission_id,
            "submission_version": 1,
            "summary": {
                "overall": "",
                "strengths": "",
                "improvements": "",
                "next_steps": "",
            },
            "priorities": [],
            "items": [],
            "publication": {
                "feedback_visibility": "hidden",
                "grade_visibility": "hidden",
                "derived_from_legacy_outcome": True,
                "legacy_outcome_published": False,
                "legacy_published_on": None,
                "legacy_published_by": None,
            },
            "modified": None,
            "modified_by": None,
        }
    if not hasattr(feedback_service, "build_publication_state_map"):
        feedback_service.build_publication_state_map = lambda outcome_ids: {
            outcome_id: {
                "feedback_visibility": "hidden",
                "grade_visibility": "hidden",
                "visible_to_student": False,
                "visible_to_guardian": False,
                "is_visible_to_any_audience": False,
                "derived_from_legacy_outcome": True,
                "legacy_outcome_published": False,
                "legacy_published_on": None,
                "legacy_published_by": None,
                "task_submission": None,
                "workspace_id": None,
            }
            for outcome_id in outcome_ids or []
        }
    if not hasattr(feedback_service, "save_feedback_workspace_draft"):
        feedback_service.save_feedback_workspace_draft = lambda payload, actor=None: payload
    if not hasattr(feedback_service, "save_feedback_publication"):
        feedback_service.save_feedback_publication = lambda payload, actor=None: payload
    artifact_service = task_feedback_artifact_service or types.ModuleType(
        "ifitwala_ed.assessment.task_feedback_artifact_service"
    )
    if not hasattr(artifact_service, "export_released_feedback_pdf"):
        artifact_service.export_released_feedback_pdf = lambda outcome_id, audience="student": {
            "file_id": "FILE-1",
            "file_name": "released-feedback.pdf",
            "task_submission": "TSU-1",
            "submission_version": 1,
            "preview_status": "pending",
            "open_url": "/open/feedback-pdf",
            "preview_url": "/preview/feedback-pdf",
            "attachment_preview": {"kind": "pdf", "preview_mode": "pdf_embed"},
        }
    if not hasattr(artifact_service, "get_current_released_feedback_pdf_artifact"):
        artifact_service.get_current_released_feedback_pdf_artifact = (
            lambda outcome_id, audience="student", submission_id=None, detail=None: {
                "file_id": "FILE-1",
                "file_name": "released-feedback.pdf",
                "task_submission": submission_id or "TSU-1",
                "submission_version": 1,
                "preview_status": "ready",
                "open_url": "/open/feedback-pdf",
                "preview_url": "/preview/feedback-pdf",
                "attachment_preview": {"kind": "pdf", "preview_mode": "pdf_embed"},
            }
        )
    comment_bank_service = task_feedback_comment_bank_service or types.ModuleType(
        "ifitwala_ed.assessment.task_feedback_comment_bank_service"
    )
    if not hasattr(comment_bank_service, "build_comment_bank_payload"):
        comment_bank_service.build_comment_bank_payload = lambda outcome_id, actor=None: {
            "context": {
                "course": None,
                "task": None,
                "task_title": None,
                "criteria": [],
            },
            "entries": [],
        }
    if not hasattr(comment_bank_service, "save_comment_bank_entry"):
        comment_bank_service.save_comment_bank_entry = lambda payload, actor=None: {
            "context": {
                "course": None,
                "task": None,
                "task_title": None,
                "criteria": [],
            },
            "entries": [],
        }
    thread_service = task_feedback_thread_service or types.ModuleType(
        "ifitwala_ed.assessment.task_feedback_thread_service"
    )
    if not hasattr(thread_service, "build_feedback_thread_payloads"):
        thread_service.build_feedback_thread_payloads = lambda **kwargs: []
    if not hasattr(thread_service, "save_instructor_reply"):
        thread_service.save_instructor_reply = lambda payload, actor=None: {"thread": None}
    if not hasattr(thread_service, "save_instructor_thread_state"):
        thread_service.save_instructor_thread_state = lambda payload, actor=None: {"thread": None}
    student_insight_note = types.ModuleType("ifitwala_ed.students.doctype.student_insight_note.student_insight_note")
    student_insight_note.build_student_insight_summaries = lambda student_names, user=None: {}
    file_access = types.ModuleType("ifitwala_ed.api.file_access")
    file_access.resolve_academic_file_open_url = (
        lambda *, file_name, file_url, context_doctype=None, context_name=None, **kwargs: (
            f"/api/method/ifitwala_ed.api.file_access.download_academic_file?file={file_name}&context_doctype={context_doctype}&context_name={context_name}"
            if file_name
            else file_url
        )
    )
    file_access.resolve_academic_file_preview_url = (
        lambda *, file_name, file_url, context_doctype=None, context_name=None, **kwargs: (
            f"/api/method/ifitwala_ed.api.file_access.preview_academic_file?file={file_name}&context_doctype={context_doctype}&context_name={context_name}"
            if file_name
            else file_url
        )
    )

    def resolve_thumbnail_url(*, file_name, file_url, context_doctype=None, context_name=None, **kwargs):
        if file_name:
            if not kwargs.get("thumbnail_ready"):
                return None
            return (
                f"/api/method/ifitwala_ed.api.file_access.thumbnail_academic_file?file={file_name}"
                f"&context_doctype={context_doctype}&context_name={context_name}"
            )
        return file_url

    file_access.resolve_academic_file_thumbnail_url = resolve_thumbnail_url
    file_access.get_drive_file_thumbnail_ready_map = lambda file_names: {
        file_name: False for file_name in (file_names or []) if file_name
    }

    return {
        "ifitwala_ed.api.file_access": file_access,
        "ifitwala_ed.assessment.quiz_service": quiz_service,
        "ifitwala_ed.assessment.task_contribution_service": task_contribution_service
        or types.ModuleType("ifitwala_ed.assessment.task_contribution_service"),
        "ifitwala_ed.assessment.task_feedback_artifact_service": artifact_service,
        "ifitwala_ed.assessment.task_feedback_comment_bank_service": comment_bank_service,
        "ifitwala_ed.assessment.task_feedback_service": feedback_service,
        "ifitwala_ed.assessment.task_feedback_thread_service": thread_service,
        "ifitwala_ed.assessment.task_outcome_service": task_outcome_service
        or types.ModuleType("ifitwala_ed.assessment.task_outcome_service"),
        "ifitwala_ed.assessment.task_submission_service": types.ModuleType(
            "ifitwala_ed.assessment.task_submission_service"
        ),
        "ifitwala_ed.students.doctype.student_insight_note.student_insight_note": student_insight_note,
        "ifitwala_ed.utilities.image_utils": image_utils,
    }


def _import_fresh_gradebook():
    import_fresh("ifitwala_ed.assessment.api.gradebook.reads")
    import_fresh("ifitwala_ed.assessment.api.gradebook.writes")
    import_fresh("ifitwala_ed.assessment.api.gradebook.support")
    return import_fresh("ifitwala_ed.assessment.api.gradebook.endpoints")


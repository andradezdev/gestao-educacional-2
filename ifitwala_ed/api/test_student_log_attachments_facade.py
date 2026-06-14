from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


class TestStudentLogAttachmentsFacade(TestCase):
    def test_root_student_log_attachments_facade_delegates_all_methods(self):
        calls: dict[str, object] = {}
        impl = ModuleType("ifitwala_ed.students.api.student_log_attachments")

        def fake_get_student_log_attachments(student_log=None, audience=None):
            calls["get"] = {"student_log": student_log, "audience": audience}
            return {"attachments": []}

        def fake_upload_student_log_evidence_attachment(**payload):
            calls["upload"] = payload
            return {"attachment": {"id": "row-1"}}

        def fake_add_student_log_evidence_link(**payload):
            calls["add"] = payload
            return {"attachment": {"id": "row-link"}}

        def fake_remove_student_log_evidence_attachment(student_log=None, row_name=None):
            calls["remove"] = {"student_log": student_log, "row_name": row_name}
            return {"ok": True}

        impl.get_student_log_attachments = fake_get_student_log_attachments
        impl.upload_student_log_evidence_attachment = fake_upload_student_log_evidence_attachment
        impl.add_student_log_evidence_link = fake_add_student_log_evidence_link
        impl.remove_student_log_evidence_attachment = fake_remove_student_log_evidence_attachment

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.student_log_attachments": impl}):
            module = import_fresh("ifitwala_ed.api.student_log_attachments")
            fetched = module.get_student_log_attachments(student_log="SLOG-1", audience="guardian")
            uploaded = module.upload_student_log_evidence_attachment(
                student_log="SLOG-1",
                row_name="row-1",
                title="Evidence",
                description="Context",
                visible_to_student=1,
                extra_ignored_by_facade="kept",
            )
            linked = module.add_student_log_evidence_link(student_log="SLOG-1", external_url="https://example.edu")
            removed = module.remove_student_log_evidence_attachment(student_log="SLOG-1", row_name="row-1")

        self.assertEqual(fetched, {"attachments": []})
        self.assertEqual(uploaded, {"attachment": {"id": "row-1"}})
        self.assertEqual(linked, {"attachment": {"id": "row-link"}})
        self.assertEqual(removed, {"ok": True})
        self.assertEqual(calls["get"], {"student_log": "SLOG-1", "audience": "guardian"})
        self.assertEqual(calls["upload"]["student_log"], "SLOG-1")
        self.assertEqual(calls["upload"]["extra_ignored_by_facade"], "kept")
        self.assertEqual(calls["add"]["external_url"], "https://example.edu")
        self.assertEqual(calls["remove"], {"student_log": "SLOG-1", "row_name": "row-1"})

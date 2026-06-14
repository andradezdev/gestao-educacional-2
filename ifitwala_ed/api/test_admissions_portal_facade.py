# ifitwala_ed/api/test_admissions_portal_facade.py

from __future__ import annotations

import types
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _record_whitelisted_methods(frappe):
    frappe.whitelisted = set()

    def whitelist(*args, **kwargs):
        def decorator(fn):
            frappe.whitelisted.add(fn)
            if kwargs.get("allow_guest"):
                fn.allow_guest = True
            return fn

        if args and callable(args[0]) and len(args) == 1 and not kwargs:
            return decorator(args[0])
        return decorator

    frappe.whitelist = whitelist


class TestAdmissionsPortalFacade(TestCase):
    def test_portal_facade_reexports_admission_owned_endpoints(self):
        with stubbed_frappe() as frappe:
            _record_whitelisted_methods(frappe)
            endpoints = import_fresh("ifitwala_ed.admission.api.portal.endpoints")
            admissions_portal = import_fresh("ifitwala_ed.api.admissions_portal")

            self.assertEqual(admissions_portal.__all__, endpoints.__all__)
            for method_name in admissions_portal.__all__:
                with self.subTest(method=method_name):
                    self.assertIs(getattr(admissions_portal, method_name), getattr(endpoints, method_name))
                    self.assertFalse(bool(getattr(getattr(admissions_portal, method_name), "allow_guest", False)))

    def test_public_portal_methods_remain_whitelisted(self):
        with stubbed_frappe() as frappe:
            _record_whitelisted_methods(frappe)
            admissions_portal = import_fresh("ifitwala_ed.api.admissions_portal")

            for method_name in admissions_portal.__all__:
                method = getattr(admissions_portal, method_name)
                with self.subTest(method=method.__name__):
                    self.assertIn(method, frappe.whitelisted)

    def test_upload_applicant_document_delegates_to_domain_implementation(self):
        calls: dict[str, object] = {}
        documents = types.ModuleType("ifitwala_ed.admission.api.portal.documents")

        def fake_upload_applicant_document_impl(
            *,
            student_applicant=None,
            document_type=None,
            applicant_document_item=None,
            item_key=None,
            item_label=None,
            client_request_id=None,
            file_name=None,
            content=None,
        ):
            calls.update(
                {
                    "student_applicant": student_applicant,
                    "document_type": document_type,
                    "applicant_document_item": applicant_document_item,
                    "item_key": item_key,
                    "item_label": item_label,
                    "client_request_id": client_request_id,
                    "file_name": file_name,
                    "content": content,
                }
            )
            return {"ok": True}

        documents.upload_applicant_document_impl = fake_upload_applicant_document_impl

        with stubbed_frappe(extra_modules={"ifitwala_ed.admission.api.portal.documents": documents}) as frappe:
            _record_whitelisted_methods(frappe)
            admissions_portal = import_fresh("ifitwala_ed.api.admissions_portal")

            result = admissions_portal.upload_applicant_document(
                student_applicant="APP-1",
                document_type="Passport",
                applicant_document_item="ITEM-1",
                item_key="passport-1",
                item_label="Passport",
                client_request_id="REQ-1",
                file_name="passport.pdf",
                content="base64",
            )

        self.assertEqual(result, {"ok": True})
        self.assertEqual(
            calls,
            {
                "student_applicant": "APP-1",
                "document_type": "Passport",
                "applicant_document_item": "ITEM-1",
                "item_key": "passport-1",
                "item_label": "Passport",
                "client_request_id": "REQ-1",
                "file_name": "passport.pdf",
                "content": "base64",
            },
        )

    def test_upload_profile_images_delegate_to_domain_implementation(self):
        calls: dict[str, object] = {}
        profile_images = types.ModuleType("ifitwala_ed.admission.api.portal.profile_images")

        def fake_upload_applicant_profile_image_impl(*, student_applicant=None, file_name=None, content=None):
            calls["applicant"] = (student_applicant, file_name, content)
            return {"image_url": "/api/applicant-image"}

        def fake_upload_applicant_guardian_image_impl(
            *,
            student_applicant=None,
            guardian_row_name=None,
            file_name=None,
            content=None,
        ):
            calls["guardian"] = (student_applicant, guardian_row_name, file_name, content)
            return {"guardian_image": "/api/guardian-image"}

        profile_images.upload_applicant_profile_image_impl = fake_upload_applicant_profile_image_impl
        profile_images.upload_applicant_guardian_image_impl = fake_upload_applicant_guardian_image_impl

        with stubbed_frappe(extra_modules={"ifitwala_ed.admission.api.portal.profile_images": profile_images}) as frappe:
            _record_whitelisted_methods(frappe)
            admissions_portal = import_fresh("ifitwala_ed.api.admissions_portal")

            applicant_result = admissions_portal.upload_applicant_profile_image(
                student_applicant="APP-1",
                file_name="applicant.png",
                content="image-bytes",
            )
            guardian_result = admissions_portal.upload_applicant_guardian_image(
                student_applicant="APP-1",
                guardian_row_name="ROW-1",
                file_name="guardian.png",
                content="guardian-bytes",
            )

        self.assertEqual(applicant_result, {"image_url": "/api/applicant-image"})
        self.assertEqual(guardian_result, {"guardian_image": "/api/guardian-image"})
        self.assertEqual(calls["applicant"], ("APP-1", "applicant.png", "image-bytes"))
        self.assertEqual(calls["guardian"], ("APP-1", "ROW-1", "guardian.png", "guardian-bytes"))

    def test_compatibility_exports_resolve_lazily(self):
        access = types.ModuleType("ifitwala_ed.admission.access")
        access.ADMISSIONS_APPLICANT_ROLE = "Admissions Applicant"

        with stubbed_frappe(extra_modules={"ifitwala_ed.admission.access": access}) as frappe:
            _record_whitelisted_methods(frappe)
            admissions_portal = import_fresh("ifitwala_ed.api.admissions_portal")

            self.assertEqual(admissions_portal.ADMISSIONS_ROLE, "Admissions Applicant")
            self.assertEqual(admissions_portal._as_text(None), "")
            self.assertEqual(admissions_portal._as_text("  keep spacing  "), "  keep spacing  ")

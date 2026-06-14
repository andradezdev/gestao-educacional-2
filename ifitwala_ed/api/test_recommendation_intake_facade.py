# ifitwala_ed/api/test_recommendation_intake_facade.py

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


def _recommendation_helper_modules():
    status_module = types.ModuleType("ifitwala_ed.admission.api.recommendation_intake.status")
    templates_module = types.ModuleType("ifitwala_ed.admission.api.recommendation_intake.templates")

    status_module.get_recommendation_status_batch_for_applicants = lambda *args, **kwargs: {}
    status_module.get_recommendation_status_for_applicant = lambda *args, **kwargs: {}
    templates_module.get_recommendation_template_rows_for_applicant = lambda *args, **kwargs: []

    return {
        "ifitwala_ed.admission.api.recommendation_intake.status": status_module,
        "ifitwala_ed.admission.api.recommendation_intake.templates": templates_module,
    }


class TestRecommendationIntakeFacade(TestCase):
    def test_facade_reexports_admission_owned_endpoints_and_helpers(self):
        with stubbed_frappe(extra_modules=_recommendation_helper_modules()) as frappe:
            _record_whitelisted_methods(frappe)
            endpoints = import_fresh("ifitwala_ed.admission.api.recommendation_intake.endpoints")
            recommendation_intake = import_fresh("ifitwala_ed.api.recommendation_intake")

            for method_name in endpoints.__all__:
                self.assertIs(getattr(recommendation_intake, method_name), getattr(endpoints, method_name))

            self.assertTrue(callable(recommendation_intake.get_recommendation_template_rows_for_applicant))
            self.assertTrue(callable(recommendation_intake.get_recommendation_status_batch_for_applicants))
            self.assertTrue(callable(recommendation_intake.get_recommendation_status_for_applicant))

    def test_facade_preserves_public_method_delegation(self):
        calls: dict[str, object] = {}
        templates_module = types.ModuleType("ifitwala_ed.admission.api.recommendation_intake.templates")

        def fake_list_recommendation_templates(*, student_applicant=None):
            calls["student_applicant"] = student_applicant
            return {"templates": []}

        templates_module.list_recommendation_templates = fake_list_recommendation_templates
        templates_module.get_recommendation_template_rows_for_applicant = lambda *args, **kwargs: []

        extra_modules = {
            **_recommendation_helper_modules(),
            "ifitwala_ed.admission.api.recommendation_intake.templates": templates_module,
        }
        with stubbed_frappe(extra_modules=extra_modules) as frappe:
            _record_whitelisted_methods(frappe)
            recommendation_intake = import_fresh("ifitwala_ed.api.recommendation_intake")

            self.assertEqual(
                recommendation_intake.list_recommendation_templates(student_applicant="APP-0001"),
                {"templates": []},
            )

        self.assertEqual(calls["student_applicant"], "APP-0001")

    def test_public_guest_intake_methods_remain_whitelisted(self):
        with stubbed_frappe(extra_modules=_recommendation_helper_modules()) as frappe:
            _record_whitelisted_methods(frappe)
            recommendation_intake = import_fresh("ifitwala_ed.api.recommendation_intake")

            self.assertIn(recommendation_intake.get_recommendation_intake_payload, frappe.whitelisted)
            self.assertIn(recommendation_intake.send_recommendation_otp, frappe.whitelisted)
            self.assertIn(recommendation_intake.verify_recommendation_otp, frappe.whitelisted)
            self.assertIn(recommendation_intake.submit_recommendation, frappe.whitelisted)
            self.assertTrue(getattr(recommendation_intake.get_recommendation_intake_payload, "allow_guest", False))
            self.assertTrue(getattr(recommendation_intake.send_recommendation_otp, "allow_guest", False))
            self.assertTrue(getattr(recommendation_intake.verify_recommendation_otp, "allow_guest", False))
            self.assertTrue(getattr(recommendation_intake.submit_recommendation, "allow_guest", False))

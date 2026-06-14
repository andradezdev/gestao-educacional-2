# ifitwala_ed/api/test_admission_cockpit_facade.py

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


class TestAdmissionCockpitFacade(TestCase):
    def test_cockpit_facade_reexports_admission_owned_endpoints(self):
        with stubbed_frappe() as frappe:
            _record_whitelisted_methods(frappe)
            endpoints = import_fresh("ifitwala_ed.admission.api.cockpit.endpoints")
            admission_cockpit = import_fresh("ifitwala_ed.api.admission_cockpit")

            self.assertEqual(admission_cockpit.__all__, endpoints.__all__)
            for method_name in admission_cockpit.__all__:
                self.assertIs(getattr(admission_cockpit, method_name), getattr(endpoints, method_name))
                self.assertFalse(bool(getattr(getattr(admission_cockpit, method_name), "allow_guest", False)))

    def test_public_cockpit_methods_remain_whitelisted(self):
        with stubbed_frappe() as frappe:
            _record_whitelisted_methods(frappe)
            admission_cockpit = import_fresh("ifitwala_ed.api.admission_cockpit")

            for method_name in admission_cockpit.__all__:
                method = getattr(admission_cockpit, method_name)
                with self.subTest(method=method.__name__):
                    self.assertIn(method, frappe.whitelisted)

    def test_cockpit_data_delegates_to_domain_implementation(self):
        calls: dict[str, object] = {}
        data_module = types.ModuleType("ifitwala_ed.admission.api.cockpit.data")

        def fake_get_admissions_cockpit_data_impl(filters=None):
            calls["filters"] = filters
            return {"columns": []}

        data_module.get_admissions_cockpit_data_impl = fake_get_admissions_cockpit_data_impl

        with stubbed_frappe(extra_modules={"ifitwala_ed.admission.api.cockpit.data": data_module}) as frappe:
            _record_whitelisted_methods(frappe)
            admission_cockpit = import_fresh("ifitwala_ed.api.admission_cockpit")

            self.assertEqual(
                admission_cockpit.get_admissions_cockpit_data(filters={"school": "SCH-1"}), {"columns": []}
            )

        self.assertEqual(calls["filters"], {"school": "SCH-1"})

    def test_cockpit_actions_delegate_to_domain_implementation(self):
        calls: dict[str, object] = {}
        actions_module = types.ModuleType("ifitwala_ed.admission.api.cockpit.actions")

        def fake_offer_plan_impl(student_applicant: str):
            calls["student_applicant"] = student_applicant
            return {"ok": True, "student_applicant": student_applicant}

        def fake_send_offer_impl(applicant_enrollment_plan: str):
            calls["applicant_enrollment_plan"] = applicant_enrollment_plan
            return {"ok": True, "applicant_enrollment_plan": applicant_enrollment_plan}

        actions_module.get_or_create_admissions_cockpit_offer_plan_impl = fake_offer_plan_impl
        actions_module.send_admissions_cockpit_offer_impl = fake_send_offer_impl

        with stubbed_frappe(extra_modules={"ifitwala_ed.admission.api.cockpit.actions": actions_module}) as frappe:
            _record_whitelisted_methods(frappe)
            admission_cockpit = import_fresh("ifitwala_ed.api.admission_cockpit")

            self.assertEqual(
                admission_cockpit.get_or_create_admissions_cockpit_offer_plan("APP-1"),
                {"ok": True, "student_applicant": "APP-1"},
            )
            self.assertEqual(
                admission_cockpit.send_admissions_cockpit_offer("AEP-1"),
                {"ok": True, "applicant_enrollment_plan": "AEP-1"},
            )

        self.assertEqual(calls["student_applicant"], "APP-1")
        self.assertEqual(calls["applicant_enrollment_plan"], "AEP-1")

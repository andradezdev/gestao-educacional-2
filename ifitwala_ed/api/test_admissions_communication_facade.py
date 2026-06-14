# ifitwala_ed/api/test_admissions_communication_facade.py

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


class TestAdmissionsCommunicationFacade(TestCase):
    def test_case_thread_facade_reexports_admission_owned_endpoints(self):
        with stubbed_frappe() as frappe:
            _record_whitelisted_methods(frappe)
            endpoints = import_fresh("ifitwala_ed.admission.api.communication.endpoints")
            admissions_communication = import_fresh("ifitwala_ed.api.admissions_communication")

            self.assertEqual(admissions_communication.__all__, endpoints.__all__)
            for method_name in admissions_communication.__all__:
                self.assertIs(getattr(admissions_communication, method_name), getattr(endpoints, method_name))

    def test_case_thread_endpoints_allow_guest_to_reach_auth_guard(self):
        with stubbed_frappe() as frappe:
            _record_whitelisted_methods(frappe)
            admissions_communication = import_fresh("ifitwala_ed.api.admissions_communication")

            self.assertIn(admissions_communication.send_admissions_case_message, frappe.whitelisted)
            self.assertIn(admissions_communication.get_admissions_case_thread, frappe.whitelisted)
            self.assertIn(admissions_communication.mark_admissions_case_thread_read, frappe.whitelisted)
            self.assertTrue(
                bool(getattr(admissions_communication.send_admissions_case_message, "allow_guest", False))
            )
            self.assertTrue(bool(getattr(admissions_communication.get_admissions_case_thread, "allow_guest", False)))
            self.assertTrue(
                bool(getattr(admissions_communication.mark_admissions_case_thread_read, "allow_guest", False))
            )

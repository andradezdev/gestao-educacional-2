# ifitwala_ed/api/test_admissions_crm_facade.py

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


class TestAdmissionsCrmFacade(TestCase):
    def test_crm_facade_reexports_admission_owned_endpoints(self):
        with stubbed_frappe() as frappe:
            _record_whitelisted_methods(frappe)
            endpoints = import_fresh("ifitwala_ed.admission.api.crm.endpoints")
            admissions_crm = import_fresh("ifitwala_ed.api.admissions_crm")

            self.assertEqual(admissions_crm.__all__, endpoints.__all__)
            for method_name in admissions_crm.__all__:
                self.assertIs(getattr(admissions_crm, method_name), getattr(endpoints, method_name))
                self.assertFalse(bool(getattr(getattr(admissions_crm, method_name), "allow_guest", False)))

    def test_public_crm_methods_remain_whitelisted(self):
        with stubbed_frappe() as frappe:
            _record_whitelisted_methods(frappe)
            admissions_crm = import_fresh("ifitwala_ed.api.admissions_crm")

            for method_name in admissions_crm.__all__:
                method = getattr(admissions_crm, method_name)
                with self.subTest(method=method.__name__):
                    self.assertIn(method, frappe.whitelisted)

    def test_inbox_assignment_delegates_to_domain_implementation(self):
        calls: dict[str, object] = {}
        inquiry_actions = types.ModuleType("ifitwala_ed.admission.api.crm.inquiry_actions")

        def fake_assign_inquiry_from_inbox_impl(
            *,
            inquiry=None,
            assigned_to=None,
            assignment_lane=None,
            client_request_id=None,
        ):
            calls["inquiry"] = inquiry
            calls["assigned_to"] = assigned_to
            calls["assignment_lane"] = assignment_lane
            calls["client_request_id"] = client_request_id
            return {"inquiry": inquiry}

        inquiry_actions.assign_inquiry_from_inbox_impl = fake_assign_inquiry_from_inbox_impl

        with stubbed_frappe(extra_modules={"ifitwala_ed.admission.api.crm.inquiry_actions": inquiry_actions}) as frappe:
            _record_whitelisted_methods(frappe)
            admissions_crm = import_fresh("ifitwala_ed.api.admissions_crm")

            self.assertEqual(
                admissions_crm.assign_inquiry_from_inbox(
                    inquiry="INQ-1",
                    assigned_to="staff@example.com",
                    assignment_lane="Admissions",
                    client_request_id="REQ-1",
                ),
                {"inquiry": "INQ-1"},
            )

        self.assertEqual(calls["inquiry"], "INQ-1")
        self.assertEqual(calls["assigned_to"], "staff@example.com")
        self.assertEqual(calls["assignment_lane"], "Admissions")
        self.assertEqual(calls["client_request_id"], "REQ-1")

    def test_compatibility_exports_resolve_lazily(self):
        idempotency = types.ModuleType("ifitwala_ed.admission.api.crm.idempotency")
        idempotency.IDEMPOTENCY_TTL_SECONDS = 600

        with stubbed_frappe(extra_modules={"ifitwala_ed.admission.api.crm.idempotency": idempotency}) as frappe:
            _record_whitelisted_methods(frappe)
            admissions_crm = import_fresh("ifitwala_ed.api.admissions_crm")

            self.assertEqual(admissions_crm.IDEMPOTENCY_TTL_SECONDS, 600)

# ifitwala_ed/api/test_inquiry_facade.py

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


class TestInquiryFacade(TestCase):
    def test_inquiry_facade_reexports_admission_owned_endpoints(self):
        with stubbed_frappe() as frappe:
            _record_whitelisted_methods(frappe)
            endpoints = import_fresh("ifitwala_ed.admission.api.inquiry.endpoints")
            inquiry = import_fresh("ifitwala_ed.api.inquiry")

            self.assertEqual(inquiry.__all__, endpoints.__all__)
            for method_name in inquiry.__all__:
                self.assertIs(getattr(inquiry, method_name), getattr(endpoints, method_name))

    def test_public_guest_link_queries_remain_whitelisted(self):
        with stubbed_frappe() as frappe:
            _record_whitelisted_methods(frappe)
            inquiry = import_fresh("ifitwala_ed.api.inquiry")

            self.assertIn(inquiry.inquiry_organization_link_query, frappe.whitelisted)
            self.assertIn(inquiry.inquiry_school_link_query, frappe.whitelisted)
            self.assertIn(inquiry.get_inquiry_acknowledgement_context, frappe.whitelisted)
            self.assertTrue(getattr(inquiry.inquiry_organization_link_query, "allow_guest", False))
            self.assertTrue(getattr(inquiry.inquiry_school_link_query, "allow_guest", False))
            self.assertTrue(getattr(inquiry.get_inquiry_acknowledgement_context, "allow_guest", False))

    def test_inquiry_facade_preserves_public_method_delegation(self):
        lookups_module = types.ModuleType("ifitwala_ed.admission.api.inquiry.lookups")
        calls: dict[str, object] = {}

        def fake_get_inquiry_types():
            calls["get_inquiry_types"] = True
            return ["Admissions"]

        def fake_inquiry_school_link_query(doctype=None, txt=None, searchfield=None, start=0, page_len=20, filters=None):
            calls["school_query"] = {
                "doctype": doctype,
                "txt": txt,
                "searchfield": searchfield,
                "start": start,
                "page_len": page_len,
                "filters": filters,
            }
            return [["SCH-1", "School One"]]

        lookups_module.get_inquiry_types = fake_get_inquiry_types
        lookups_module.inquiry_school_link_query = fake_inquiry_school_link_query

        with stubbed_frappe(extra_modules={"ifitwala_ed.admission.api.inquiry.lookups": lookups_module}) as frappe:
            _record_whitelisted_methods(frappe)
            inquiry = import_fresh("ifitwala_ed.api.inquiry")

            self.assertEqual(inquiry.get_inquiry_types(), ["Admissions"])
            self.assertEqual(
                inquiry.inquiry_school_link_query(
                    doctype="School",
                    txt="north",
                    searchfield="name",
                    start=5,
                    page_len=10,
                    filters={"organization": "ORG-1"},
                ),
                [["SCH-1", "School One"]],
            )

        self.assertTrue(calls["get_inquiry_types"])
        self.assertEqual(
            calls["school_query"],
            {
                "doctype": "School",
                "txt": "north",
                "searchfield": "name",
                "start": 5,
                "page_len": 10,
                "filters": {"organization": "ORG-1"},
            },
        )

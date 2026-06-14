# ifitwala_ed/api/test_admissions_inbox_facade.py

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


class TestAdmissionsInboxFacade(TestCase):
    def test_inbox_facade_reexports_admission_owned_endpoints(self):
        with stubbed_frappe() as frappe:
            _record_whitelisted_methods(frappe)
            endpoints = import_fresh("ifitwala_ed.admission.api.inbox.endpoints")
            admissions_inbox = import_fresh("ifitwala_ed.api.admissions_inbox")

            self.assertEqual(admissions_inbox.__all__, endpoints.__all__)
            for method_name in admissions_inbox.__all__:
                self.assertIs(getattr(admissions_inbox, method_name), getattr(endpoints, method_name))
                self.assertFalse(bool(getattr(getattr(admissions_inbox, method_name), "allow_guest", False)))

    def test_inbox_context_endpoint_remains_whitelisted(self):
        with stubbed_frappe() as frappe:
            _record_whitelisted_methods(frappe)
            admissions_inbox = import_fresh("ifitwala_ed.api.admissions_inbox")

            self.assertIn(admissions_inbox.get_admissions_inbox_context, frappe.whitelisted)
            self.assertIn(admissions_inbox.search_admissions_inbox_assignees, frappe.whitelisted)

    def test_inbox_context_delegates_to_domain_implementation(self):
        calls: dict[str, object] = {}
        context_module = types.ModuleType("ifitwala_ed.admission.api.inbox.context")

        def fake_get_admissions_inbox_context_impl(*, organization=None, school=None, limit=None):
            calls["organization"] = organization
            calls["school"] = school
            calls["limit"] = limit
            return {"queues": []}

        context_module.get_admissions_inbox_context_impl = fake_get_admissions_inbox_context_impl

        with stubbed_frappe(extra_modules={"ifitwala_ed.admission.api.inbox.context": context_module}) as frappe:
            _record_whitelisted_methods(frappe)
            admissions_inbox = import_fresh("ifitwala_ed.api.admissions_inbox")

            self.assertEqual(
                admissions_inbox.get_admissions_inbox_context(
                    organization="ORG-1",
                    school="SCH-1",
                    limit="20",
                ),
                {"queues": []},
            )

        self.assertEqual(calls["organization"], "ORG-1")
        self.assertEqual(calls["school"], "SCH-1")
        self.assertEqual(calls["limit"], "20")

    def test_assignee_search_delegates_to_domain_implementation(self):
        calls: dict[str, object] = {}
        assignees_module = types.ModuleType("ifitwala_ed.admission.api.inbox.assignees")

        def fake_search_admissions_inbox_assignees_impl(
            *,
            context_doctype=None,
            context_name=None,
            organization=None,
            school=None,
            assignment_lane=None,
            query=None,
            limit=None,
        ):
            calls["context_doctype"] = context_doctype
            calls["context_name"] = context_name
            calls["organization"] = organization
            calls["school"] = school
            calls["assignment_lane"] = assignment_lane
            calls["query"] = query
            calls["limit"] = limit
            return [{"value": "staff@example.com"}]

        assignees_module.search_admissions_inbox_assignees_impl = fake_search_admissions_inbox_assignees_impl

        with stubbed_frappe(extra_modules={"ifitwala_ed.admission.api.inbox.assignees": assignees_module}) as frappe:
            _record_whitelisted_methods(frappe)
            admissions_inbox = import_fresh("ifitwala_ed.api.admissions_inbox")

            self.assertEqual(
                admissions_inbox.search_admissions_inbox_assignees(
                    context_doctype="Inquiry",
                    context_name="INQ-1",
                    organization="ORG-1",
                    school="SCH-1",
                    assignment_lane="Staff",
                    query="staff",
                    limit="20",
                ),
                [{"value": "staff@example.com"}],
            )

        self.assertEqual(calls["context_doctype"], "Inquiry")
        self.assertEqual(calls["context_name"], "INQ-1")
        self.assertEqual(calls["organization"], "ORG-1")
        self.assertEqual(calls["school"], "SCH-1")
        self.assertEqual(calls["assignment_lane"], "Staff")
        self.assertEqual(calls["query"], "staff")
        self.assertEqual(calls["limit"], "20")

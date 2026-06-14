from __future__ import annotations

from types import ModuleType
from unittest import TestCase

from ifitwala_ed.tests.frappe_stubs import import_fresh, stubbed_frappe


def _guardian_finance_impl_stub():
    module = ModuleType("ifitwala_ed.students.api.guardian_finance")

    for name in (
        "_resolve_finance_scope",
        "_get_invoice_rows",
        "_get_payment_rows",
    ):
        setattr(module, name, lambda *args, **kwargs: None)

    return module


class TestGuardianFinanceFacade(TestCase):
    def test_root_guardian_finance_facade_delegates_public_method(self):
        calls: dict[str, bool] = {}
        impl = _guardian_finance_impl_stub()

        def fake_get_guardian_finance_snapshot():
            calls["snapshot"] = True
            return {"meta": {"finance_access": True}}

        impl.get_guardian_finance_snapshot = fake_get_guardian_finance_snapshot

        with stubbed_frappe(extra_modules={"ifitwala_ed.students.api.guardian_finance": impl}):
            module = import_fresh("ifitwala_ed.api.guardian_finance")
            self.assertEqual(module.get_guardian_finance_snapshot(), {"meta": {"finance_access": True}})

        self.assertTrue(calls["snapshot"])
        self.assertIs(module._resolve_finance_scope, impl._resolve_finance_scope)

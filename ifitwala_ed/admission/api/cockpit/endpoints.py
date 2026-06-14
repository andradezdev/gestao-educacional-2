# ifitwala_ed/admission/api/cockpit/endpoints.py

from __future__ import annotations

import frappe


@frappe.whitelist()
def get_or_create_admissions_cockpit_offer_plan(student_applicant: str):
    from ifitwala_ed.admission.api.cockpit.actions import get_or_create_admissions_cockpit_offer_plan_impl

    return get_or_create_admissions_cockpit_offer_plan_impl(student_applicant=student_applicant)


@frappe.whitelist()
def promote_admissions_cockpit_applicant(student_applicant: str):
    from ifitwala_ed.admission.api.cockpit.actions import promote_admissions_cockpit_applicant_impl

    return promote_admissions_cockpit_applicant_impl(student_applicant=student_applicant)


@frappe.whitelist()
def send_admissions_cockpit_offer(applicant_enrollment_plan: str):
    from ifitwala_ed.admission.api.cockpit.actions import send_admissions_cockpit_offer_impl

    return send_admissions_cockpit_offer_impl(applicant_enrollment_plan=applicant_enrollment_plan)


@frappe.whitelist()
def hydrate_admissions_cockpit_request(applicant_enrollment_plan: str):
    from ifitwala_ed.admission.api.cockpit.actions import hydrate_admissions_cockpit_request_impl

    return hydrate_admissions_cockpit_request_impl(applicant_enrollment_plan=applicant_enrollment_plan)


@frappe.whitelist()
def generate_admissions_cockpit_deposit_invoice(applicant_enrollment_plan: str):
    from ifitwala_ed.admission.api.cockpit.actions import generate_admissions_cockpit_deposit_invoice_impl

    return generate_admissions_cockpit_deposit_invoice_impl(applicant_enrollment_plan=applicant_enrollment_plan)


@frappe.whitelist()
def get_admissions_cockpit_data(filters=None):
    from ifitwala_ed.admission.api.cockpit.data import get_admissions_cockpit_data_impl

    return get_admissions_cockpit_data_impl(filters=filters)


__all__ = [
    "get_or_create_admissions_cockpit_offer_plan",
    "promote_admissions_cockpit_applicant",
    "send_admissions_cockpit_offer",
    "hydrate_admissions_cockpit_request",
    "generate_admissions_cockpit_deposit_invoice",
    "get_admissions_cockpit_data",
]

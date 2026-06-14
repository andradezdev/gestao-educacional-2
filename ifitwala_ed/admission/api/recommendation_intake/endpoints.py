# ifitwala_ed/admission/api/recommendation_intake/endpoints.py

from __future__ import annotations

import frappe


@frappe.whitelist()
def list_recommendation_templates(*, student_applicant: str | None = None):
    from ifitwala_ed.admission.api.recommendation_intake.templates import (
        list_recommendation_templates as list_recommendation_templates_impl,
    )

    return list_recommendation_templates_impl(student_applicant=student_applicant)


@frappe.whitelist()
def create_recommendation_request(payload=None, **kwargs):
    from ifitwala_ed.admission.api.recommendation_intake.staff_requests import (
        create_recommendation_request as create_recommendation_request_impl,
    )

    return create_recommendation_request_impl(payload=payload, **kwargs)


@frappe.whitelist()
def resend_recommendation_request(
    *,
    recommendation_request: str | None = None,
    expires_in_days: int | None = None,
):
    from ifitwala_ed.admission.api.recommendation_intake.staff_requests import (
        resend_recommendation_request as resend_recommendation_request_impl,
    )

    return resend_recommendation_request_impl(
        recommendation_request=recommendation_request,
        expires_in_days=expires_in_days,
    )


@frappe.whitelist()
def revoke_recommendation_request(*, recommendation_request: str | None = None):
    from ifitwala_ed.admission.api.recommendation_intake.staff_requests import (
        revoke_recommendation_request as revoke_recommendation_request_impl,
    )

    return revoke_recommendation_request_impl(recommendation_request=recommendation_request)


@frappe.whitelist()
def list_recommendation_requests(*, student_applicant: str | None = None):
    from ifitwala_ed.admission.api.recommendation_intake.staff_requests import (
        list_recommendation_requests as list_recommendation_requests_impl,
    )

    return list_recommendation_requests_impl(student_applicant=student_applicant)


@frappe.whitelist()
def get_recommendation_request_summary(*, student_applicant: str | None = None):
    from ifitwala_ed.admission.api.recommendation_intake.staff_requests import (
        get_recommendation_request_summary as get_recommendation_request_summary_impl,
    )

    return get_recommendation_request_summary_impl(student_applicant=student_applicant)


@frappe.whitelist()
def get_recommendation_review_payload(
    *,
    student_applicant: str | None = None,
    recommendation_request: str | None = None,
    recommendation_submission: str | None = None,
    applicant_document_item: str | None = None,
):
    from ifitwala_ed.admission.api.recommendation_intake.review_payload import (
        get_recommendation_review_payload as get_recommendation_review_payload_impl,
    )

    return get_recommendation_review_payload_impl(
        student_applicant=student_applicant,
        recommendation_request=recommendation_request,
        recommendation_submission=recommendation_submission,
        applicant_document_item=applicant_document_item,
    )


@frappe.whitelist(allow_guest=True)
def get_recommendation_intake_payload(*, token: str | None = None):
    from ifitwala_ed.admission.api.recommendation_intake.guest_intake import (
        get_recommendation_intake_payload as get_recommendation_intake_payload_impl,
    )

    return get_recommendation_intake_payload_impl(token=token)


get_recommendation_intake_payload.allow_guest = True


@frappe.whitelist(allow_guest=True)
def send_recommendation_otp(*, token: str | None = None):
    from ifitwala_ed.admission.api.recommendation_intake.guest_intake import (
        send_recommendation_otp as send_recommendation_otp_impl,
    )

    return send_recommendation_otp_impl(token=token)


send_recommendation_otp.allow_guest = True


@frappe.whitelist(allow_guest=True)
def verify_recommendation_otp(*, token: str | None = None, otp_code: str | None = None):
    from ifitwala_ed.admission.api.recommendation_intake.guest_intake import (
        verify_recommendation_otp as verify_recommendation_otp_impl,
    )

    return verify_recommendation_otp_impl(token=token, otp_code=otp_code)


verify_recommendation_otp.allow_guest = True


@frappe.whitelist(allow_guest=True)
def submit_recommendation(payload=None, **kwargs):
    from ifitwala_ed.admission.api.recommendation_intake.guest_intake import (
        submit_recommendation as submit_recommendation_impl,
    )

    return submit_recommendation_impl(payload=payload, **kwargs)


submit_recommendation.allow_guest = True


__all__ = [
    "list_recommendation_templates",
    "create_recommendation_request",
    "resend_recommendation_request",
    "revoke_recommendation_request",
    "list_recommendation_requests",
    "get_recommendation_request_summary",
    "get_recommendation_review_payload",
    "get_recommendation_intake_payload",
    "send_recommendation_otp",
    "verify_recommendation_otp",
    "submit_recommendation",
]

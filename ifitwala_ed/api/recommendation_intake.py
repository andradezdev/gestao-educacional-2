# ifitwala_ed/api/recommendation_intake.py

from __future__ import annotations

from ifitwala_ed.admission.api.recommendation_intake.endpoints import (
    create_recommendation_request,
    get_recommendation_intake_payload,
    get_recommendation_request_summary,
    get_recommendation_review_payload,
    list_recommendation_requests,
    list_recommendation_templates,
    resend_recommendation_request,
    revoke_recommendation_request,
    send_recommendation_otp,
    submit_recommendation,
    verify_recommendation_otp,
)
from ifitwala_ed.admission.api.recommendation_intake.status import (
    get_recommendation_status_batch_for_applicants,
    get_recommendation_status_for_applicant,
)
from ifitwala_ed.admission.api.recommendation_intake.templates import (
    get_recommendation_template_rows_for_applicant,
)

__all__ = [
    "create_recommendation_request",
    "get_recommendation_intake_payload",
    "get_recommendation_request_summary",
    "get_recommendation_review_payload",
    "get_recommendation_status_batch_for_applicants",
    "get_recommendation_status_for_applicant",
    "get_recommendation_template_rows_for_applicant",
    "list_recommendation_requests",
    "list_recommendation_templates",
    "resend_recommendation_request",
    "revoke_recommendation_request",
    "send_recommendation_otp",
    "submit_recommendation",
    "verify_recommendation_otp",
]

# ifitwala_ed/api/admission_cockpit.py

from __future__ import annotations

from ifitwala_ed.admission.api.cockpit.endpoints import (
    generate_admissions_cockpit_deposit_invoice,
    get_admissions_cockpit_data,
    get_or_create_admissions_cockpit_offer_plan,
    hydrate_admissions_cockpit_request,
    promote_admissions_cockpit_applicant,
    send_admissions_cockpit_offer,
)

__all__ = [
    "get_or_create_admissions_cockpit_offer_plan",
    "promote_admissions_cockpit_applicant",
    "send_admissions_cockpit_offer",
    "hydrate_admissions_cockpit_request",
    "generate_admissions_cockpit_deposit_invoice",
    "get_admissions_cockpit_data",
]

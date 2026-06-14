# ifitwala_ed/api/inquiry.py

from __future__ import annotations

from ifitwala_ed.admission.api.inquiry.access import ALLOWED_ANALYTICS_ROLES
from ifitwala_ed.admission.api.inquiry.endpoints import (
    academic_year_link_query,
    admission_user_link_query,
    get_dashboard_data,
    get_inquiry_acknowledgement_context,
    get_inquiry_organizations,
    get_inquiry_schools,
    get_inquiry_sources,
    get_inquiry_types,
    get_zero_lost_lead_context,
    inquiry_organization_link_query,
    inquiry_school_link_query,
)

__all__ = [
    "get_dashboard_data",
    "get_zero_lost_lead_context",
    "get_inquiry_organizations",
    "get_inquiry_schools",
    "academic_year_link_query",
    "inquiry_organization_link_query",
    "inquiry_school_link_query",
    "get_inquiry_acknowledgement_context",
    "admission_user_link_query",
    "get_inquiry_types",
    "get_inquiry_sources",
]

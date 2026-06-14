# ifitwala_ed/admission/api/inquiry/endpoints.py

from __future__ import annotations

import frappe


@frappe.whitelist()
def get_dashboard_data(filters=None):
    from ifitwala_ed.admission.api.inquiry.dashboard import get_dashboard_data as get_dashboard_data_impl

    return get_dashboard_data_impl(filters=filters)


@frappe.whitelist()
def get_zero_lost_lead_context(filters=None, active_view: str | None = None, start=0, limit=25):
    from ifitwala_ed.admission.api.inquiry.zero_lost import get_zero_lost_lead_context as get_zero_lost_lead_context_impl

    return get_zero_lost_lead_context_impl(
        filters=filters,
        active_view=active_view,
        start=start,
        limit=limit,
    )


@frappe.whitelist()
def get_inquiry_organizations():
    from ifitwala_ed.admission.api.inquiry.lookups import get_inquiry_organizations as get_inquiry_organizations_impl

    return get_inquiry_organizations_impl()


@frappe.whitelist()
def get_inquiry_schools():
    from ifitwala_ed.admission.api.inquiry.lookups import get_inquiry_schools as get_inquiry_schools_impl

    return get_inquiry_schools_impl()


@frappe.whitelist()
def academic_year_link_query(doctype=None, txt=None, searchfield=None, start=0, page_len=20, filters=None):
    from ifitwala_ed.admission.api.inquiry.lookups import academic_year_link_query as academic_year_link_query_impl

    return academic_year_link_query_impl(
        doctype=doctype,
        txt=txt,
        searchfield=searchfield,
        start=start,
        page_len=page_len,
        filters=filters,
    )


@frappe.whitelist(allow_guest=True)
@frappe.validate_and_sanitize_search_inputs
def inquiry_organization_link_query(doctype=None, txt=None, searchfield=None, start=0, page_len=20, filters=None):
    from ifitwala_ed.admission.api.inquiry.lookups import (
        inquiry_organization_link_query as inquiry_organization_link_query_impl,
    )

    return inquiry_organization_link_query_impl(
        doctype=doctype,
        txt=txt,
        searchfield=searchfield,
        start=start,
        page_len=page_len,
        filters=filters,
    )


inquiry_organization_link_query.allow_guest = True


@frappe.whitelist(allow_guest=True)
@frappe.validate_and_sanitize_search_inputs
def inquiry_school_link_query(doctype=None, txt=None, searchfield=None, start=0, page_len=20, filters=None):
    from ifitwala_ed.admission.api.inquiry.lookups import inquiry_school_link_query as inquiry_school_link_query_impl

    return inquiry_school_link_query_impl(
        doctype=doctype,
        txt=txt,
        searchfield=searchfield,
        start=start,
        page_len=page_len,
        filters=filters,
    )


inquiry_school_link_query.allow_guest = True


@frappe.whitelist(allow_guest=True)
def get_inquiry_acknowledgement_context(organization=None, school=None, type_of_inquiry=None):
    from ifitwala_ed.admission.api.inquiry.lookups import (
        get_inquiry_acknowledgement_context as get_inquiry_acknowledgement_context_impl,
    )

    return get_inquiry_acknowledgement_context_impl(
        organization=organization,
        school=school,
        type_of_inquiry=type_of_inquiry,
    )


get_inquiry_acknowledgement_context.allow_guest = True


@frappe.whitelist()
def admission_user_link_query(doctype=None, txt=None, searchfield=None, start=0, page_len=20, filters=None):
    from ifitwala_ed.admission.api.inquiry.lookups import admission_user_link_query as admission_user_link_query_impl

    return admission_user_link_query_impl(
        doctype=doctype,
        txt=txt,
        searchfield=searchfield,
        start=start,
        page_len=page_len,
        filters=filters,
    )


@frappe.whitelist()
def get_inquiry_types():
    from ifitwala_ed.admission.api.inquiry.lookups import get_inquiry_types as get_inquiry_types_impl

    return get_inquiry_types_impl()


@frappe.whitelist()
def get_inquiry_sources():
    from ifitwala_ed.admission.api.inquiry.lookups import get_inquiry_sources as get_inquiry_sources_impl

    return get_inquiry_sources_impl()


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

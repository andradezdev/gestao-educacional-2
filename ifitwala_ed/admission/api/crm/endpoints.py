# ifitwala_ed/admission/api/crm/endpoints.py

from __future__ import annotations

import frappe


@frappe.whitelist()
def log_admission_message(
    *,
    conversation: str | None = None,
    inquiry: str | None = None,
    student_applicant: str | None = None,
    external_identity: str | None = None,
    channel_account: str | None = None,
    organization: str | None = None,
    school: str | None = None,
    assigned_to: str | None = None,
    direction: str | None = "Inbound",
    body: str | None = None,
    message_type: str | None = "Text",
    delivery_status: str | None = None,
    message_at: str | None = None,
    external_message_id: str | None = None,
    external_conversation_id: str | None = None,
    dedupe_key: str | None = None,
    provider_payload_json: str | None = None,
    media_provider_id: str | None = None,
    media_mime_type: str | None = None,
    media_file_name: str | None = None,
    media_size: int | None = None,
    media_status: str | None = None,
    client_request_id: str | None = None,
):
    from ifitwala_ed.admission.api.crm.messages import log_admission_message_impl

    return log_admission_message_impl(
        conversation=conversation,
        inquiry=inquiry,
        student_applicant=student_applicant,
        external_identity=external_identity,
        channel_account=channel_account,
        organization=organization,
        school=school,
        assigned_to=assigned_to,
        direction=direction,
        body=body,
        message_type=message_type,
        delivery_status=delivery_status,
        message_at=message_at,
        external_message_id=external_message_id,
        external_conversation_id=external_conversation_id,
        dedupe_key=dedupe_key,
        provider_payload_json=provider_payload_json,
        media_provider_id=media_provider_id,
        media_mime_type=media_mime_type,
        media_file_name=media_file_name,
        media_size=media_size,
        media_status=media_status,
        client_request_id=client_request_id,
    )


@frappe.whitelist()
def record_admission_crm_activity(
    *,
    conversation: str | None = None,
    activity_type: str | None = None,
    outcome: str | None = None,
    note: str | None = None,
    next_action_on: str | None = None,
    activity_at: str | None = None,
    client_request_id: str | None = None,
):
    from ifitwala_ed.admission.api.crm.activities import record_admission_crm_activity_impl

    return record_admission_crm_activity_impl(
        conversation=conversation,
        activity_type=activity_type,
        outcome=outcome,
        note=note,
        next_action_on=next_action_on,
        activity_at=activity_at,
        client_request_id=client_request_id,
    )


@frappe.whitelist()
def link_admission_conversation(
    *,
    conversation: str | None = None,
    inquiry: str | None = None,
    student_applicant: str | None = None,
    external_identity: str | None = None,
    channel_account: str | None = None,
    client_request_id: str | None = None,
):
    from ifitwala_ed.admission.api.crm.conversations import link_admission_conversation_impl

    return link_admission_conversation_impl(
        conversation=conversation,
        inquiry=inquiry,
        student_applicant=student_applicant,
        external_identity=external_identity,
        channel_account=channel_account,
        client_request_id=client_request_id,
    )


@frappe.whitelist()
def confirm_admission_external_identity(
    *,
    external_identity: str | None = None,
    contact: str | None = None,
    guardian: str | None = None,
    inquiry: str | None = None,
    student_applicant: str | None = None,
    match_status: str | None = "Confirmed",
    client_request_id: str | None = None,
):
    from ifitwala_ed.admission.api.crm.identities import confirm_admission_external_identity_impl

    return confirm_admission_external_identity_impl(
        external_identity=external_identity,
        contact=contact,
        guardian=guardian,
        inquiry=inquiry,
        student_applicant=student_applicant,
        match_status=match_status,
        client_request_id=client_request_id,
    )


@frappe.whitelist()
def create_admissions_intake(
    *,
    organization: str | None = None,
    school: str | None = None,
    type_of_inquiry: str | None = None,
    source: str | None = None,
    activity_channel: str | None = None,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    phone_number: str | None = None,
    student_first_name: str | None = None,
    student_last_name: str | None = None,
    intended_academic_year: str | None = None,
    grade_level_interest: str | None = None,
    program_interest: str | None = None,
    student_name_or_id: str | None = None,
    relationship_to_student: str | None = None,
    organization_name: str | None = None,
    partnership_context: str | None = None,
    message: str | None = None,
    activity_type: str | None = None,
    outcome: str | None = None,
    note: str | None = None,
    next_action_on: str | None = None,
    assigned_to: str | None = None,
    assignment_lane: str | None = None,
    client_request_id: str | None = None,
):
    from ifitwala_ed.admission.api.crm.intake import create_admissions_intake_impl

    return create_admissions_intake_impl(
        organization=organization,
        school=school,
        type_of_inquiry=type_of_inquiry,
        source=source,
        activity_channel=activity_channel,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        student_first_name=student_first_name,
        student_last_name=student_last_name,
        intended_academic_year=intended_academic_year,
        grade_level_interest=grade_level_interest,
        program_interest=program_interest,
        student_name_or_id=student_name_or_id,
        relationship_to_student=relationship_to_student,
        organization_name=organization_name,
        partnership_context=partnership_context,
        message=message,
        activity_type=activity_type,
        outcome=outcome,
        note=note,
        next_action_on=next_action_on,
        assigned_to=assigned_to,
        assignment_lane=assignment_lane,
        client_request_id=client_request_id,
    )


@frappe.whitelist()
def assign_admission_conversation(
    *,
    conversation: str | None = None,
    assigned_to: str | None = None,
    client_request_id: str | None = None,
):
    from ifitwala_ed.admission.api.crm.conversations import assign_admission_conversation_impl

    return assign_admission_conversation_impl(
        conversation=conversation,
        assigned_to=assigned_to,
        client_request_id=client_request_id,
    )


@frappe.whitelist()
def update_admission_conversation_status(
    *,
    conversation: str | None = None,
    status: str | None = None,
    note: str | None = None,
    client_request_id: str | None = None,
):
    from ifitwala_ed.admission.api.crm.conversations import update_admission_conversation_status_impl

    return update_admission_conversation_status_impl(
        conversation=conversation,
        status=status,
        note=note,
        client_request_id=client_request_id,
    )


@frappe.whitelist()
def create_inquiry_from_admission_conversation(
    *,
    conversation: str | None = None,
    type_of_inquiry: str | None = None,
    source: str | None = None,
    message: str | None = None,
    client_request_id: str | None = None,
):
    from ifitwala_ed.admission.api.crm.intake import create_inquiry_from_admission_conversation_impl

    return create_inquiry_from_admission_conversation_impl(
        conversation=conversation,
        type_of_inquiry=type_of_inquiry,
        source=source,
        message=message,
        client_request_id=client_request_id,
    )


@frappe.whitelist()
def assign_inquiry_from_inbox(
    *,
    inquiry: str | None = None,
    assigned_to: str | None = None,
    assignment_lane: str | None = None,
    client_request_id: str | None = None,
):
    from ifitwala_ed.admission.api.crm.inquiry_actions import assign_inquiry_from_inbox_impl

    return assign_inquiry_from_inbox_impl(
        inquiry=inquiry,
        assigned_to=assigned_to,
        assignment_lane=assignment_lane,
        client_request_id=client_request_id,
    )


@frappe.whitelist()
def archive_inquiry_from_inbox(
    *,
    inquiry: str | None = None,
    reason: str | None = None,
    client_request_id: str | None = None,
):
    from ifitwala_ed.admission.api.crm.inquiry_actions import archive_inquiry_from_inbox_impl

    return archive_inquiry_from_inbox_impl(inquiry=inquiry, reason=reason, client_request_id=client_request_id)


@frappe.whitelist()
def mark_inquiry_contacted_from_inbox(
    *,
    inquiry: str | None = None,
    complete_todo: int | str | None = 0,
    client_request_id: str | None = None,
):
    from ifitwala_ed.admission.api.crm.inquiry_actions import mark_inquiry_contacted_from_inbox_impl

    return mark_inquiry_contacted_from_inbox_impl(
        inquiry=inquiry,
        complete_todo=complete_todo,
        client_request_id=client_request_id,
    )


@frappe.whitelist()
def qualify_inquiry_from_inbox(
    *,
    inquiry: str | None = None,
    client_request_id: str | None = None,
):
    from ifitwala_ed.admission.api.crm.inquiry_actions import qualify_inquiry_from_inbox_impl

    return qualify_inquiry_from_inbox_impl(inquiry=inquiry, client_request_id=client_request_id)


@frappe.whitelist()
def invite_inquiry_to_apply_from_inbox(
    *,
    inquiry: str | None = None,
    school: str | None = None,
    organization: str | None = None,
    client_request_id: str | None = None,
):
    from ifitwala_ed.admission.api.crm.inquiry_actions import invite_inquiry_to_apply_from_inbox_impl

    return invite_inquiry_to_apply_from_inbox_impl(
        inquiry=inquiry,
        school=school,
        organization=organization,
        client_request_id=client_request_id,
    )


__all__ = [
    "log_admission_message",
    "record_admission_crm_activity",
    "link_admission_conversation",
    "confirm_admission_external_identity",
    "create_admissions_intake",
    "assign_admission_conversation",
    "update_admission_conversation_status",
    "create_inquiry_from_admission_conversation",
    "assign_inquiry_from_inbox",
    "archive_inquiry_from_inbox",
    "mark_inquiry_contacted_from_inbox",
    "qualify_inquiry_from_inbox",
    "invite_inquiry_to_apply_from_inbox",
]

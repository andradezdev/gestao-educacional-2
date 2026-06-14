# ifitwala_ed/api/admissions_portal.py

from __future__ import annotations

from importlib import import_module

from ifitwala_ed.admission.api.portal.endpoints import (
    __all__ as _ENDPOINT_EXPORTS,
    accept_enrollment_offer,
    acknowledge_policy,
    decline_enrollment_offer,
    get_admissions_portal_invite_options,
    get_admissions_session,
    get_applicant_enrollment_choices,
    get_applicant_health,
    get_applicant_policies,
    get_applicant_profile,
    get_applicant_snapshot,
    get_family_invite_options,
    get_invite_email_options,
    invite_applicant,
    invite_family_collaborator,
    list_applicant_document_types,
    list_applicant_documents,
    submit_application,
    update_applicant_enrollment_choices,
    update_applicant_health,
    update_applicant_profile,
    upload_applicant_document,
    upload_applicant_guardian_image,
    upload_applicant_profile_image,
    withdraw_application,
)


def _as_text(value) -> str:
    if value is None:
        return ""
    return str(value)


_COMPAT_EXPORTS = {
    **{
        name: "ifitwala_ed.admission.api.common.request_payload"
        for name in (
            "_as_bool",
            "_as_check",
            "_has_bound_value",
            "_parse_request_payload",
            "_request_form_value",
            "_request_json_payload",
        )
    },
    **{
        name: "ifitwala_ed.admission.api.portal.access"
        for name in (
            "_ensure_applicant_match",
            "_get_applicant_for_user",
            "_require_admissions_applicant",
            "_require_admissions_portal_user",
            "_session_user",
        )
    },
    **{
        name: "ifitwala_ed.admission.api.portal.contacts"
        for name in (
            "_applicant_contact_prefill_payload",
            "_get_inquiry_contact_for_applicant",
            "_resolve_applicant_contact",
        )
    },
    **{
        name: "ifitwala_ed.admission.api.portal.documents"
        for name in (
            "_load_drive_version_mime_map",
            "_portal_document_requirement_state",
            "_portal_required_document_count",
            "_recommendation_target_document_types_for_applicant",
            "_serialize_applicant_document_attachment",
            "list_applicant_document_types_impl",
            "list_applicant_documents_impl",
            "upload_applicant_document_impl",
        )
    },
    **{
        name: "ifitwala_ed.admission.api.portal.enrollment"
        for name in (
            "PORTAL_EDITABLE_STATUSES",
            "PORTAL_STATUS_MAP",
            "READ_ONLY_REASON_MAP",
            "_empty_applicant_enrollment_choice_state",
            "_portal_status_for",
            "_read_only_for",
            "_serialize_enrollment_offer",
            "accept_enrollment_offer_impl",
            "decline_enrollment_offer_impl",
            "get_applicant_enrollment_choices_impl",
            "update_applicant_enrollment_choices_impl",
        )
    },
    **{
        name: "ifitwala_ed.admission.api.portal.guardians"
        for name in (
            "APPLICANT_CONTACT_GUARDIAN_ROW",
            "APPLICANT_GUARDIAN_CHECK_FIELDS",
            "APPLICANT_GUARDIAN_EMPLOYMENT_SECTOR_OPTIONS",
            "APPLICANT_GUARDIAN_FIELDS",
            "APPLICANT_GUARDIAN_GENDER_OPTIONS",
            "APPLICANT_GUARDIAN_INVITE_REQUIRED_FIELDS",
            "APPLICANT_GUARDIAN_RELATIONSHIP_OPTIONS",
            "APPLICANT_GUARDIAN_REQUIRED_FIELDS",
            "APPLICANT_GUARDIAN_TEXT_FIELDS",
            "_applicant_guardian_required_field_label",
            "_apply_guardians_to_applicant",
            "_contact_is_linked_to_applicant",
            "_create_or_update_guardian_contact",
            "_guardian_contact_name_from_guardian_email",
            "_guardian_row_display_name",
            "_guardian_row_is_empty",
            "_guardian_salutation_options",
            "_guardian_signer_flag_from_primary_guardian",
            "_guardians_feature_enabled",
            "_hydrate_guardian_row_from_applicant_contact",
            "_hydrate_guardian_row_from_guardian_doc",
            "_normalize_guardian_row",
            "_parse_guardians_payload",
            "_serialize_applicant_guardians",
            "_set_contact_primary_email",
            "_set_contact_primary_mobile",
            "_update_contact_identity_from_guardian_row",
            "_validate_guardian_profile_row",
        )
    },
    **{
        name: "ifitwala_ed.admission.api.portal.health"
        for name in (
            "APPLICANT_HEALTH_FIELDS",
            "APPLICANT_HEALTH_VACCINATION_FIELDS",
            "_coerce_vaccination_date",
            "_decode_base64_content",
            "_default_health_payload",
            "_has_health_declaration_column",
            "_normalize_vaccinations",
            "_portal_health_state",
            "_serialize_health_doc",
            "_upload_vaccination_proof",
            "get_applicant_health_impl",
            "update_applicant_health_impl",
        )
    },
    **{
        name: "ifitwala_ed.admission.api.portal.invites"
        for name in (
            "_applicant_invite_options_payload",
            "_applicant_self_invite_blocked_reason",
            "_bootstrap_applicant_contact_guardian_row",
            "_call_user_method_if_available",
            "_canonical_applicant_contact_for_invite",
            "_clear_applicant_self_login_for_family_conversion",
            "_contact_linked_to_applicant",
            "_contact_linked_to_user",
            "_ensure_admissions_applicant_role",
            "_ensure_admissions_family_role",
            "_ensure_family_guardian_user",
            "_family_invite_options_payload",
            "_get_applicant_guardian_row",
            "_invite_contact_email_options",
            "_invite_contact_primary_email",
            "_remove_admissions_applicant_role",
            "_require_family_workspace_mode",
            "_require_scoped_staff_applicant_access",
            "_required_family_acknowledgement_policy_labels",
            "_send_applicant_invite_email",
            "get_admissions_portal_invite_options_impl",
            "get_family_invite_options_impl",
            "get_invite_email_options_impl",
            "invite_applicant_impl",
            "invite_family_collaborator_impl",
        )
    },
    **{
        name: "ifitwala_ed.admission.api.portal.policies"
        for name in (
            "_family_policy_blocked_reason",
            "_find_family_guardian_context",
            "_normalize_signature_name",
            "_resolve_family_guardian_context",
            "acknowledge_policy_impl",
            "get_applicant_policies_impl",
        )
    },
    **{
        name: "ifitwala_ed.admission.api.portal.profile"
        for name in (
            "APPLICANT_PROFILE_FIELDS",
            "APPLICANT_PROFILE_GENDER_OPTIONS",
            "APPLICANT_PROFILE_REQUIRED_FIELD_LABELS",
            "APPLICANT_PROFILE_RESIDENCY_OPTIONS",
            "_application_context_payload",
            "_assert_record_modified_matches",
            "_build_profile_payload",
            "_default_profile_payload",
            "_normalize_record_modified",
            "_profile_completeness",
            "_profile_reference_options",
            "_serialize_applicant_profile",
            "get_applicant_profile_impl",
            "update_applicant_profile_impl",
        )
    },
    **{
        name: "ifitwala_ed.admission.api.portal.profile_images"
        for name in (
            "_CURRENT_PROFILE_IMAGE_STATUSES",
            "PROFILE_IMAGE_ALLOWED_ACCEPT_LABEL",
            "PROFILE_IMAGE_ALLOWED_EXTENSIONS",
            "PROFILE_IMAGE_MAX_BYTES",
            "PROFILE_IMAGE_MAX_PIXELS",
            "_applicant_image_open_url",
            "_build_admissions_profile_image_urls",
            "_collect_guardian_image_authority_map",
            "_decode_profile_image_content",
            "_file_is_scoped_to_applicant",
            "_guardian_image_open_url",
            "_guardian_profile_image_slot",
            "_normalize_profile_image_bytes",
            "_prepare_profile_image_upload",
            "_profile_image_allowed_formats_message",
            "_profile_image_extension",
            "_profile_image_extension_mismatch_message",
            "_profile_image_invalid_content_message",
            "_profile_image_output_filename",
            "_profile_image_pixel_limit_message",
            "_profile_image_size_limit_message",
            "_profile_image_to_rgb",
            "_resolve_applicant_profile_image_authority",
            "_resolve_applicant_profile_image_drive_file",
            "_resolve_applicant_profile_image_file",
            "_resolve_guardian_image_authority",
            "_resolve_guardian_image_drive_file",
            "_resolve_guardian_image_file",
            "_resolve_profile_image_drive_file_from_file_row",
            "_sniff_profile_image_format",
            "upload_applicant_guardian_image_impl",
            "upload_applicant_profile_image_impl",
        )
    },
    **{
        name: "ifitwala_ed.admission.api.portal.session"
        for name in (
            "_applicant_summary_payload",
            "_build_applicant_display_name",
            "get_admissions_session_impl",
        )
    },
    **{
        name: "ifitwala_ed.admission.api.portal.snapshot"
        for name in (
            "_completion_state_for_health",
            "_completion_state_for_interviews",
            "_completion_state_for_recommendations",
            "_completion_state_for_requirement",
            "_derive_next_actions",
            "get_applicant_snapshot_impl",
        )
    },
    **{
        name: "ifitwala_ed.admission.api.portal.submission"
        for name in ("submit_application_impl", "withdraw_application_impl")
    },
    **{
        name: "ifitwala_ed.admission.access"
        for name in (
            "ADMISSIONS_ACCESS_MODE_FAMILY",
            "ADMISSIONS_FAMILY_ROLE",
            "get_admissions_access_mode",
            "is_family_workspace_enabled",
        )
    },
    **{
        name: "ifitwala_ed.admission.admission_utils"
        for name in (
            "ensure_admissions_permission",
            "ensure_contact_dynamic_link",
            "ensure_contact_for_email",
            "get_contact_primary_email",
            "normalize_email_value",
            "sync_student_applicant_contact_binding",
            "upsert_contact_email",
        )
    },
    **{
        name: "ifitwala_ed.contacts.contact_privacy"
        for name in (
            "assert_user_can_access_student_applicant_contact",
            "get_raw_contact_email_options_for_applicant_invite",
        )
    },
    **{
        name: "ifitwala_ed.governance.policy_utils"
        for name in (
            "ADMISSIONS_POLICY_MODE_FAMILY",
            "get_applicant_policy_status",
        )
    },
    "ADMISSIONS_ROLE": ("ifitwala_ed.admission.access", "ADMISSIONS_APPLICANT_ROLE"),
}


def __getattr__(name: str):
    target = _COMPAT_EXPORTS.get(name)
    if not target:
        raise AttributeError(name)
    if isinstance(target, tuple):
        module_name, attribute = target
    else:
        module_name, attribute = target, name
    return getattr(import_module(module_name), attribute)


__all__ = list(_ENDPOINT_EXPORTS)

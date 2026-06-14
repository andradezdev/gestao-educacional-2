# ifitwala_ed/admission/api/portal/endpoints.py

from __future__ import annotations

import frappe


@frappe.whitelist()
def get_admissions_session(student_applicant: str | None = None):
    from ifitwala_ed.admission.api.portal.session import get_admissions_session_impl

    return get_admissions_session_impl(student_applicant=student_applicant)


@frappe.whitelist()
def get_applicant_snapshot(student_applicant: str | None = None):
    from ifitwala_ed.admission.api.portal.snapshot import get_applicant_snapshot_impl

    return get_applicant_snapshot_impl(student_applicant=student_applicant)


@frappe.whitelist()
def get_applicant_enrollment_choices(student_applicant: str | None = None):
    from ifitwala_ed.admission.api.portal.enrollment import get_applicant_enrollment_choices_impl

    return get_applicant_enrollment_choices_impl(student_applicant=student_applicant)


@frappe.whitelist()
def update_applicant_enrollment_choices(*, student_applicant: str | None = None, courses=None):
    from ifitwala_ed.admission.api.portal.enrollment import update_applicant_enrollment_choices_impl

    return update_applicant_enrollment_choices_impl(student_applicant=student_applicant, courses=courses)


@frappe.whitelist()
def accept_enrollment_offer(student_applicant: str | None = None):
    from ifitwala_ed.admission.api.portal.enrollment import accept_enrollment_offer_impl

    return accept_enrollment_offer_impl(student_applicant=student_applicant)


@frappe.whitelist()
def decline_enrollment_offer(student_applicant: str | None = None):
    from ifitwala_ed.admission.api.portal.enrollment import decline_enrollment_offer_impl

    return decline_enrollment_offer_impl(student_applicant=student_applicant)


@frappe.whitelist()
def get_applicant_profile(student_applicant: str | None = None):
    from ifitwala_ed.admission.api.portal.profile import get_applicant_profile_impl

    return get_applicant_profile_impl(student_applicant=student_applicant)


@frappe.whitelist()
def update_applicant_profile(
    *,
    student_applicant: str | None = None,
    expected_modified: str | None = None,
    student_preferred_name: str | None = None,
    student_date_of_birth: str | None = None,
    student_gender: str | None = None,
    student_mobile_number: str | None = None,
    student_joining_date: str | None = None,
    student_first_language: str | None = None,
    student_second_language: str | None = None,
    student_nationality: str | None = None,
    student_second_nationality: str | None = None,
    residency_status: str | None = None,
    address_line1: str | None = None,
    address_line2: str | None = None,
    city: str | None = None,
    state: str | None = None,
    postal_code: str | None = None,
    country: str | None = None,
    previous_school_name: str | None = None,
    previous_grade_level: str | None = None,
    previous_curriculum: str | None = None,
    previous_school_city: str | None = None,
    previous_school_country: str | None = None,
    previous_language_of_instruction: str | None = None,
    previous_school_year_completed: str | None = None,
    previous_school_notes: str | None = None,
    learning_support_status: str | None = None,
    learning_needs: str | None = None,
    effective_supports: str | None = None,
    existing_support_plans: str | None = None,
    social_emotional_needs: str | None = None,
    physical_access_needs: str | None = None,
    family_support_priorities: str | None = None,
    student_strengths: str | None = None,
    student_interests: str | None = None,
    student_activities: str | None = None,
    student_achievements: str | None = None,
    student_motivators: str | None = None,
    student_relationship_notes: str | None = None,
    student_voice_notes: str | None = None,
    guardians=None,
):
    from ifitwala_ed.admission.api.portal.profile import update_applicant_profile_impl

    return update_applicant_profile_impl(
        student_applicant=student_applicant,
        expected_modified=expected_modified,
        student_preferred_name=student_preferred_name,
        student_date_of_birth=student_date_of_birth,
        student_gender=student_gender,
        student_mobile_number=student_mobile_number,
        student_joining_date=student_joining_date,
        student_first_language=student_first_language,
        student_second_language=student_second_language,
        student_nationality=student_nationality,
        student_second_nationality=student_second_nationality,
        residency_status=residency_status,
        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        state=state,
        postal_code=postal_code,
        country=country,
        previous_school_name=previous_school_name,
        previous_grade_level=previous_grade_level,
        previous_curriculum=previous_curriculum,
        previous_school_city=previous_school_city,
        previous_school_country=previous_school_country,
        previous_language_of_instruction=previous_language_of_instruction,
        previous_school_year_completed=previous_school_year_completed,
        previous_school_notes=previous_school_notes,
        learning_support_status=learning_support_status,
        learning_needs=learning_needs,
        effective_supports=effective_supports,
        existing_support_plans=existing_support_plans,
        social_emotional_needs=social_emotional_needs,
        physical_access_needs=physical_access_needs,
        family_support_priorities=family_support_priorities,
        student_strengths=student_strengths,
        student_interests=student_interests,
        student_activities=student_activities,
        student_achievements=student_achievements,
        student_motivators=student_motivators,
        student_relationship_notes=student_relationship_notes,
        student_voice_notes=student_voice_notes,
        guardians=guardians,
    )


@frappe.whitelist()
def upload_applicant_profile_image(
    *,
    student_applicant: str | None = None,
    file_name: str | None = None,
    content: str | None = None,
):
    from ifitwala_ed.admission.api.portal.profile_images import upload_applicant_profile_image_impl

    return upload_applicant_profile_image_impl(
        student_applicant=student_applicant,
        file_name=file_name,
        content=content,
    )


@frappe.whitelist()
def upload_applicant_guardian_image(
    *,
    student_applicant: str | None = None,
    guardian_row_name: str | None = None,
    file_name: str | None = None,
    content: str | None = None,
):
    from ifitwala_ed.admission.api.portal.profile_images import upload_applicant_guardian_image_impl

    return upload_applicant_guardian_image_impl(
        student_applicant=student_applicant,
        guardian_row_name=guardian_row_name,
        file_name=file_name,
        content=content,
    )


@frappe.whitelist()
def get_applicant_health(student_applicant: str | None = None):
    from ifitwala_ed.admission.api.portal.health import get_applicant_health_impl

    return get_applicant_health_impl(student_applicant=student_applicant)


@frappe.whitelist()
def update_applicant_health(
    *,
    student_applicant: str | None = None,
    expected_modified: str | None = None,
    blood_group: str | None = None,
    allergies=None,
    food_allergies: str | None = None,
    insect_bites: str | None = None,
    medication_allergies: str | None = None,
    asthma: str | None = None,
    bladder__bowel_problems: str | None = None,
    diabetes: str | None = None,
    headache_migraine: str | None = None,
    high_blood_pressure: str | None = None,
    seizures: str | None = None,
    bone_joints_scoliosis: str | None = None,
    blood_disorder_info: str | None = None,
    fainting_spells: str | None = None,
    hearing_problems: str | None = None,
    recurrent_ear_infections: str | None = None,
    speech_problem: str | None = None,
    birth_defect: str | None = None,
    dental_problems: str | None = None,
    g6pd: str | None = None,
    heart_problems: str | None = None,
    recurrent_nose_bleeding: str | None = None,
    vision_problem: str | None = None,
    diet_requirements: str | None = None,
    medical_surgeries__hospitalizations: str | None = None,
    other_medical_information: str | None = None,
    applicant_health_declared_complete=None,
    vaccinations=None,
):
    from ifitwala_ed.admission.api.portal.health import update_applicant_health_impl

    return update_applicant_health_impl(
        student_applicant=student_applicant,
        expected_modified=expected_modified,
        blood_group=blood_group,
        allergies=allergies,
        food_allergies=food_allergies,
        insect_bites=insect_bites,
        medication_allergies=medication_allergies,
        asthma=asthma,
        bladder__bowel_problems=bladder__bowel_problems,
        diabetes=diabetes,
        headache_migraine=headache_migraine,
        high_blood_pressure=high_blood_pressure,
        seizures=seizures,
        bone_joints_scoliosis=bone_joints_scoliosis,
        blood_disorder_info=blood_disorder_info,
        fainting_spells=fainting_spells,
        hearing_problems=hearing_problems,
        recurrent_ear_infections=recurrent_ear_infections,
        speech_problem=speech_problem,
        birth_defect=birth_defect,
        dental_problems=dental_problems,
        g6pd=g6pd,
        heart_problems=heart_problems,
        recurrent_nose_bleeding=recurrent_nose_bleeding,
        vision_problem=vision_problem,
        diet_requirements=diet_requirements,
        medical_surgeries__hospitalizations=medical_surgeries__hospitalizations,
        other_medical_information=other_medical_information,
        applicant_health_declared_complete=applicant_health_declared_complete,
        vaccinations=vaccinations,
    )


@frappe.whitelist()
def list_applicant_documents(student_applicant: str | None = None):
    from ifitwala_ed.admission.api.portal.documents import list_applicant_documents_impl

    return list_applicant_documents_impl(student_applicant=student_applicant)


@frappe.whitelist()
def list_applicant_document_types(student_applicant: str | None = None):
    from ifitwala_ed.admission.api.portal.documents import list_applicant_document_types_impl

    return list_applicant_document_types_impl(student_applicant=student_applicant)


@frappe.whitelist()
def upload_applicant_document(
    *,
    student_applicant: str | None = None,
    document_type: str | None = None,
    applicant_document_item: str | None = None,
    item_key: str | None = None,
    item_label: str | None = None,
    client_request_id: str | None = None,
    file_name: str | None = None,
    content: str | None = None,
):
    from ifitwala_ed.admission.api.portal.documents import upload_applicant_document_impl

    return upload_applicant_document_impl(
        student_applicant=student_applicant,
        document_type=document_type,
        applicant_document_item=applicant_document_item,
        item_key=item_key,
        item_label=item_label,
        client_request_id=client_request_id,
        file_name=file_name,
        content=content,
    )


@frappe.whitelist()
def get_applicant_policies(student_applicant: str | None = None):
    from ifitwala_ed.admission.api.portal.policies import get_applicant_policies_impl

    return get_applicant_policies_impl(student_applicant=student_applicant)


@frappe.whitelist()
def acknowledge_policy(
    *,
    policy_version: str | None = None,
    student_applicant: str | None = None,
    typed_signature_name: str | None = None,
    attestation_confirmed: int | str | bool | None = None,
    checked_clause_names=None,
):
    from ifitwala_ed.admission.api.portal.policies import acknowledge_policy_impl

    return acknowledge_policy_impl(
        policy_version=policy_version,
        student_applicant=student_applicant,
        typed_signature_name=typed_signature_name,
        attestation_confirmed=attestation_confirmed,
        checked_clause_names=checked_clause_names,
    )


@frappe.whitelist()
def submit_application(student_applicant: str | None = None):
    from ifitwala_ed.admission.api.portal.submission import submit_application_impl

    return submit_application_impl(student_applicant=student_applicant)


@frappe.whitelist()
def withdraw_application(
    *,
    student_applicant: str | None = None,
    reason: str | None = None,
):
    from ifitwala_ed.admission.api.portal.submission import withdraw_application_impl

    return withdraw_application_impl(student_applicant=student_applicant, reason=reason)


@frappe.whitelist()
def get_family_invite_options(*, student_applicant: str | None = None) -> dict:
    from ifitwala_ed.admission.api.portal.invites import get_family_invite_options_impl

    return get_family_invite_options_impl(student_applicant=student_applicant)


@frappe.whitelist()
def invite_family_collaborator(
    *,
    student_applicant: str | None = None,
    guardian_row: str | None = None,
    email: str | None = None,
) -> dict:
    from ifitwala_ed.admission.api.portal.invites import invite_family_collaborator_impl

    return invite_family_collaborator_impl(
        student_applicant=student_applicant,
        guardian_row=guardian_row,
        email=email,
    )


@frappe.whitelist()
def get_invite_email_options(*, student_applicant: str | None = None) -> dict:
    from ifitwala_ed.admission.api.portal.invites import get_invite_email_options_impl

    return get_invite_email_options_impl(student_applicant=student_applicant)


@frappe.whitelist()
def get_admissions_portal_invite_options(*, student_applicant: str | None = None) -> dict:
    from ifitwala_ed.admission.api.portal.invites import get_admissions_portal_invite_options_impl

    return get_admissions_portal_invite_options_impl(student_applicant=student_applicant)


@frappe.whitelist()
def invite_applicant(*, student_applicant: str | None = None, email: str | None = None) -> dict:
    from ifitwala_ed.admission.api.portal.invites import invite_applicant_impl

    return invite_applicant_impl(student_applicant=student_applicant, email=email)


__all__ = [
    "get_admissions_session",
    "get_applicant_snapshot",
    "get_applicant_enrollment_choices",
    "update_applicant_enrollment_choices",
    "accept_enrollment_offer",
    "decline_enrollment_offer",
    "get_applicant_profile",
    "update_applicant_profile",
    "upload_applicant_profile_image",
    "upload_applicant_guardian_image",
    "get_applicant_health",
    "update_applicant_health",
    "list_applicant_documents",
    "list_applicant_document_types",
    "upload_applicant_document",
    "get_applicant_policies",
    "acknowledge_policy",
    "submit_application",
    "withdraw_application",
    "get_family_invite_options",
    "invite_family_collaborator",
    "get_invite_email_options",
    "get_admissions_portal_invite_options",
    "invite_applicant",
]

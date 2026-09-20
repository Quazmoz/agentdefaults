"""AdMob read, reporting, capability, and risk-gated mutation MCP tools."""

from __future__ import annotations

from typing import Any, Callable

from . import admob as admob_module, redaction
from . import config, human_approval


def _publisher_id(profile: str | None, publisher_id: str | None) -> str | None:
    if publisher_id:
        return publisher_id
    if profile:
        return config.load_profile(profile).admob_publisher_id
    return None


def _client(profile: str | None, publisher_id: str | None) -> admob_module.AdMobClient:
    return admob_module.AdMobClient(_publisher_id(profile, publisher_id))


def _tag(result: dict, risk: str = "contained", approved: bool = False) -> dict:
    return {**result, "_mra": {"risk": risk, "human_approved": approved}}


def _access_payload(
    error: admob_module.AdMobError,
    risk: str = "observe",
    approved: bool = False,
) -> dict:
    if isinstance(error, admob_module.AdMobAccessDenied):
        status = "denied_by_account"
        hint = "Google documents this method as limited-access; use the manual handoff path."
    elif isinstance(error, admob_module.AdMobAuthenticationError):
        status = "authentication_error"
        hint = "Run `mra admob login` and verify the intended Google account."
    elif isinstance(error, admob_module.AdMobPermissionDenied):
        status = "permission_denied"
        hint = "Check OAuth scopes, AdMob account access, and API enablement."
    else:
        status = "error"
        hint = "Inspect the AdMob API detail and retry only after resolving the cause."
    return {
        "status": status,
        "platform": "admob",
        "detail": redaction.redact_text(str(error)),
        "hint": hint,
        # A vendor failure must not erase the fact that a local operator
        # approved an irreversible action; that record is the audit trail.
        "_mra": {"risk": risk, "human_approved": approved},
    }


def _read(operation: Callable[[], Any]) -> Any:
    try:
        return operation()
    except admob_module.AdMobError as error:
        return _access_payload(error)


def _gate(title: str, detail: str) -> tuple[bool, dict[str, Any]]:
    decision = human_approval.request(title, detail)
    if decision.get("approved"):
        return True, decision
    return False, {
        "status": "human_approval_required",
        "risk": "high",
        "approval": decision,
        "detail": "High-risk AdMob action was not executed.",
    }


def admob_probe_access(profile: str | None = None, publisher_id: str | None = None) -> dict:
    """Probe limited-access mediation reads without creating anything."""
    return _client(profile, publisher_id).probe_monetization_access()


def admob_capabilities(profile: str | None = None, publisher_id: str | None = None) -> Any:
    """Return the observed/documented AdMob capability matrix for this account."""
    return _read(lambda: _client(profile, publisher_id).capability_matrix())


def admob_list_apps(profile: str | None = None, publisher_id: str | None = None) -> Any:
    """List AdMob apps, including appApprovalState."""
    return _read(lambda: _client(profile, publisher_id).list_apps())


def admob_app_approval_summary(
    profile: str | None = None, publisher_id: str | None = None
) -> Any:
    """Summarize APPROVED/IN_REVIEW/ACTION_REQUIRED apps."""
    return _read(lambda: _client(profile, publisher_id).app_approval_summary())


def admob_list_ad_units(profile: str | None = None, publisher_id: str | None = None) -> Any:
    """List AdMob ad units."""
    return _read(lambda: _client(profile, publisher_id).list_ad_units())


def admob_list_ad_sources(profile: str | None = None, publisher_id: str | None = None) -> Any:
    """List mediation ad sources available to this AdMob account."""
    return _read(lambda: _client(profile, publisher_id).list_ad_sources())


def admob_list_adapters(
    ad_source_id: str,
    profile: str | None = None,
    publisher_id: str | None = None,
) -> Any:
    """List adapters and required adapter configuration metadata for an ad source."""
    return _read(lambda: _client(profile, publisher_id).list_adapters(ad_source_id))


def admob_list_mediation_groups(
    profile: str | None = None,
    publisher_id: str | None = None,
    filter_expression: str | None = None,
) -> Any:
    """List mediation groups where Google's account gate permits it."""
    return _read(
        lambda: _client(profile, publisher_id).list_mediation_groups(filter_expression)
    )


def admob_list_ad_unit_mappings(
    ad_unit_id: str,
    profile: str | None = None,
    publisher_id: str | None = None,
    filter_expression: str | None = None,
) -> Any:
    """List third-party mappings for one ad unit where account access permits it."""
    return _read(
        lambda: _client(profile, publisher_id).list_ad_unit_mappings(
            ad_unit_id, filter_expression
        )
    )


def admob_network_report(
    report_spec: dict,
    profile: str | None = None,
    publisher_id: str | None = None,
) -> Any:
    """Generate an AdMob Network report from a caller-supplied report spec."""
    return _read(lambda: _client(profile, publisher_id).generate_network_report(report_spec))


def admob_mediation_report(
    report_spec: dict,
    profile: str | None = None,
    publisher_id: str | None = None,
) -> Any:
    """Generate an AdMob Mediation report from a caller-supplied report spec."""
    return _read(lambda: _client(profile, publisher_id).generate_mediation_report(report_spec))


def admob_campaign_report(
    report_spec: dict,
    profile: str | None = None,
    publisher_id: str | None = None,
) -> Any:
    """Generate an AdMob campaign report."""
    return _read(lambda: _client(profile, publisher_id).generate_campaign_report(report_spec))


def admob_monetization_health(
    start_date: str,
    end_date: str,
    profile: str | None = None,
    publisher_id: str | None = None,
    app_ids: list[str] | None = None,
    currency_code: str = "USD",
) -> Any:
    """Report request/match/show/earnings health by app version, SDK, restriction and format."""
    return _read(
        lambda: _client(profile, publisher_id).monetization_health_report(
            start_date,
            end_date,
            app_ids=app_ids,
            currency_code=currency_code,
        )
    )


def admob_create_app(
    display_name: str,
    platform: str = "ANDROID",
    app_store_id: str | None = None,
    profile: str | None = None,
    publisher_id: str | None = None,
) -> dict:
    """Create one AdMob app; irreversible store linking requires local approval."""
    approved = False
    risk = "contained"
    if app_store_id:
        risk = "high"
        approved, refusal = _gate(
            "Approve irreversible AdMob app linking",
            f"App: {display_name}\nPlatform: {platform}\nStore ID: {app_store_id}\n"
            "AdMob documents app-store linking as irreversible.",
        )
        if not approved:
            return refusal
    try:
        result = _client(profile, publisher_id).create_app(display_name, platform, app_store_id)
        return _tag(result, risk, approved)
    except admob_module.AdMobError as error:
        return _access_payload(error, risk, approved)


def admob_create_ad_unit(
    app_id: str,
    display_name: str,
    ad_format: str,
    ad_types: list[str] | None = None,
    profile: str | None = None,
    publisher_id: str | None = None,
) -> dict:
    """Create one AdMob ad unit where the account has limited-access permission."""
    try:
        result = _client(profile, publisher_id).create_ad_unit(
            app_id, display_name, ad_format, ad_types
        )
        return _tag(result)
    except admob_module.AdMobError as error:
        return _access_payload(error, "contained")


def admob_create_mediation_group(
    body: dict,
    profile: str | None = None,
    publisher_id: str | None = None,
) -> dict:
    """Create a mediation group; high-risk and account-gated."""
    approved, refusal = _gate(
        "Approve AdMob mediation group creation",
        "Create a live mediation group. Review targeting, ad units, lines and CPM settings before approving.",
    )
    if not approved:
        return refusal
    try:
        return _tag(_client(profile, publisher_id).create_mediation_group(body), "high", True)
    except admob_module.AdMobError as error:
        return _access_payload(error, "high", True)


def admob_patch_mediation_group(
    resource_name: str,
    update_mask: str,
    body: dict,
    profile: str | None = None,
    publisher_id: str | None = None,
) -> dict:
    """Update selected mediation-group fields; high-risk and account-gated."""
    approved, refusal = _gate(
        "Approve AdMob mediation group change",
        f"Resource: {resource_name}\nUpdate mask: {update_mask}",
    )
    if not approved:
        return refusal
    try:
        result = _client(profile, publisher_id).patch_mediation_group(
            resource_name, update_mask, body
        )
        return _tag(result, "high", True)
    except admob_module.AdMobError as error:
        return _access_payload(error, "high", True)


def admob_create_ad_unit_mapping(
    ad_unit_id: str,
    body: dict,
    profile: str | None = None,
    publisher_id: str | None = None,
) -> dict:
    """Create a mediation mapping; high-risk and account-gated."""
    approved, refusal = _gate(
        "Approve AdMob ad-unit mapping",
        f"Ad unit: {ad_unit_id}\nThis changes live mediation configuration.",
    )
    if not approved:
        return refusal
    try:
        result = _client(profile, publisher_id).create_ad_unit_mapping(ad_unit_id, body)
        return _tag(result, "high", True)
    except admob_module.AdMobError as error:
        return _access_payload(error, "high", True)


def admob_batch_create_ad_unit_mappings(
    requests: list[dict],
    profile: str | None = None,
    publisher_id: str | None = None,
) -> dict:
    """Batch-create up to 100 mediation mappings after one exact local approval."""
    approved, refusal = _gate(
        "Approve AdMob mapping batch",
        f"Create {len(requests)} ad-unit mapping(s). This changes live mediation configuration.",
    )
    if not approved:
        return refusal
    try:
        result = _client(profile, publisher_id).batch_create_ad_unit_mappings(requests)
        return _tag(result, "high", True)
    except admob_module.AdMobError as error:
        return _access_payload(error, "high", True)


def admob_create_mediation_experiment(
    mediation_group_id: str,
    body: dict,
    profile: str | None = None,
    publisher_id: str | None = None,
) -> dict:
    """Create a mediation A/B experiment after local approval."""
    approved, refusal = _gate(
        "Approve AdMob mediation experiment",
        f"Mediation group: {mediation_group_id}\nCreate a live mediation A/B experiment.",
    )
    if not approved:
        return refusal
    try:
        result = _client(profile, publisher_id).create_mediation_experiment(
            mediation_group_id, body
        )
        return _tag(result, "high", True)
    except admob_module.AdMobError as error:
        return _access_payload(error, "high", True)


def admob_stop_mediation_experiment(
    experiment_name: str,
    variant_choice: str,
    profile: str | None = None,
    publisher_id: str | None = None,
) -> dict:
    """Stop an experiment and choose a winning variant after local approval."""
    approved, refusal = _gate(
        "Approve stopping AdMob experiment",
        f"Experiment: {experiment_name}\nWinning variant: {variant_choice}",
    )
    if not approved:
        return refusal
    try:
        result = _client(profile, publisher_id).stop_mediation_experiment(
            experiment_name, variant_choice
        )
        return _tag(result, "high", True)
    except admob_module.AdMobError as error:
        return _access_payload(error, "high", True)


def register(server) -> None:
    for tool in (
        admob_probe_access,
        admob_capabilities,
        admob_list_apps,
        admob_app_approval_summary,
        admob_list_ad_units,
        admob_list_ad_sources,
        admob_list_adapters,
        admob_list_mediation_groups,
        admob_list_ad_unit_mappings,
        admob_network_report,
        admob_mediation_report,
        admob_campaign_report,
        admob_monetization_health,
        admob_create_app,
        admob_create_ad_unit,
        admob_create_mediation_group,
        admob_patch_mediation_group,
        admob_create_ad_unit_mapping,
        admob_batch_create_ad_unit_mappings,
        admob_create_mediation_experiment,
        admob_stop_mediation_experiment,
    ):
        server.tool()(tool)

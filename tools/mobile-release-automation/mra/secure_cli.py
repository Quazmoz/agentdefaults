"""Agent-facing CLI with local credential/profile diagnostics.

This surface performs read-only platform calls plus local credential/profile
binding. RevenueCat authentication is delegated to the official RevenueCat CLI
and its browser OAuth session; MRA never prints or stores RevenueCat OAuth tokens.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import admob_credentials, auth, config, play_credentials, revenuecat_cli
from . import revenuecat as rc_module
from . import secrets as secret_provider


def emit(payload) -> int:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True, default=str)
    sys.stdout.write("\n")
    return 0


def note(message: str) -> None:
    print(message, file=sys.stderr)


def _auth_profile(slug: str) -> config.Profile:
    return config.load_profile(slug)


def _project_profile(slug: str) -> config.Profile:
    profile = _auth_profile(slug)
    if not profile.revenuecat_project_id:
        raise config.ConfigError(f"profile {slug!r} has no revenuecat_project_id")
    return profile


def _client(profile: config.Profile) -> rc_module.RevenueCatClient:
    del profile
    return rc_module.RevenueCatClient()


def _probe(probe) -> dict:
    try:
        return probe()
    except (config.ConfigError, revenuecat_cli.RevenueCatCliError) as error:
        return {"status": "not-ready", "detail": str(error)}


def _revenuecat_api_status() -> dict:
    return revenuecat_cli.auth_status()


def cmd_doctor(args: argparse.Namespace) -> int:
    profiles = config.load_profiles()
    legacy_bindings = sorted(
        slug for slug, profile in profiles.items() if profile.revenuecat_secret_id
    )
    return emit(
        {
            "bitwarden": secret_provider.bitwarden_status(),
            "google_play_publisher": _probe(play_credentials.publisher_status),
            "revenuecat_google_play": _probe(play_credentials.revenuecat_status),
            "revenuecat_api": _probe(_revenuecat_api_status),
            "admob": _probe(admob_credentials.status),
            "legacy_revenuecat_key_bindings": legacy_bindings,
            "platform_mutations": "risk-gated on MCP; explicit on operator mra CLI",
        }
    )


def _deprecated_revenuecat_binding(kind: str) -> int:
    return emit(
        {
            "status": "deprecated",
            "binding": kind,
            "detail": (
                "RevenueCat API-key binding is no longer used by MRA. "
                "Install the official RevenueCat CLI and run `rc auth login` "
                "with browser OAuth instead. Existing stored key references are ignored."
            ),
        }
    )


def cmd_bind_revenuecat(args: argparse.Namespace) -> int:
    del args
    return _deprecated_revenuecat_binding("revenuecat-profile-api-key")


def cmd_bind_play(args: argparse.Namespace) -> int:
    path = config.save_secret_refs(
        config.SecretRefs(play_service_account_secret_id=args.secret_id)
    )
    return emit(
        {
            "saved": str(path),
            "binding": "google-play-publisher",
            "secret_id": config.load_secret_refs().play_service_account_secret_id,
        }
    )


def cmd_bind_revenuecat_play(args: argparse.Namespace) -> int:
    path = config.save_secret_refs(
        config.SecretRefs(revenuecat_play_service_account_secret_id=args.secret_id)
    )
    return emit(
        {
            "saved": str(path),
            "binding": "revenuecat-google-play",
            "secret_id": config.load_secret_refs().revenuecat_play_service_account_secret_id,
        }
    )


def cmd_bind_revenuecat_bootstrap(args: argparse.Namespace) -> int:
    del args
    return _deprecated_revenuecat_binding("revenuecat-bootstrap-api-key")


def cmd_bind_admob(args: argparse.Namespace) -> int:
    path = config.save_secret_refs(
        config.SecretRefs(admob_oauth_client_secret_id=args.secret_id)
    )
    return emit(
        {
            "saved": str(path),
            "binding": "admob-oauth-client",
            "secret_id": config.load_secret_refs().admob_oauth_client_secret_id,
        }
    )


def cmd_rc_projects(args: argparse.Namespace) -> int:
    profile = _auth_profile(args.profile)
    return emit(_client(profile).list_projects())


def cmd_rc_apps(args: argparse.Namespace) -> int:
    profile = _project_profile(args.profile)
    return emit(_client(profile).list_apps(profile.revenuecat_project_id))


def cmd_rc_products(args: argparse.Namespace) -> int:
    profile = _project_profile(args.profile)
    return emit(_client(profile).list_products(profile.revenuecat_project_id))


def _add_profile(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--profile", required=True, help="profile slug from profiles.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mra-agent",
        description="Read-only platform surface plus local credential-reference binding.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="check OAuth and local credential bindings").set_defaults(
        func=cmd_doctor
    )

    auth_parser = subparsers.add_parser(
        "auth", help="bind external credential references; does not mutate vendor state"
    ).add_subparsers(dest="auth_command", required=True)

    bind_play = auth_parser.add_parser(
        "bind-play", help="bind the Google Play publisher credential UUID"
    )
    bind_play.add_argument("--secret-id", required=True)
    bind_play.set_defaults(func=cmd_bind_play)

    bind_rc_play = auth_parser.add_parser(
        "bind-revenuecat-play",
        help="bind the dedicated Google Play credential UUID used by RevenueCat",
    )
    bind_rc_play.add_argument("--secret-id", required=True)
    bind_rc_play.set_defaults(func=cmd_bind_revenuecat_play)

    bind_rc_bootstrap = auth_parser.add_parser(
        "bind-revenuecat-bootstrap",
        help="deprecated compatibility command; RevenueCat now uses official CLI OAuth",
    )
    bind_rc_bootstrap.add_argument("--secret-id", required=True)
    bind_rc_bootstrap.set_defaults(func=cmd_bind_revenuecat_bootstrap)

    bind_admob = auth_parser.add_parser(
        "bind-admob", help="bind the AdMob Desktop OAuth client JSON UUID"
    )
    bind_admob.add_argument("--secret-id", required=True)
    bind_admob.set_defaults(func=cmd_bind_admob)

    profile = subparsers.add_parser("profile", help="manage local app profiles").add_subparsers(
        dest="profile_command", required=True
    )
    bind = profile.add_parser(
        "bind-revenuecat",
        help="deprecated compatibility command; RevenueCat now uses official CLI OAuth",
    )
    _add_profile(bind)
    bind.add_argument("--secret-id", required=True)
    bind.set_defaults(func=cmd_bind_revenuecat)

    rc = subparsers.add_parser("rc", help="RevenueCat OAuth-backed read-only tools").add_subparsers(
        dest="rc_command", required=True
    )

    projects = rc.add_parser("projects", help="list projects visible to the OAuth account")
    _add_profile(projects)
    projects.set_defaults(func=cmd_rc_projects)

    apps = rc.add_parser("apps", help="list apps in the profile's RevenueCat project")
    _add_profile(apps)
    apps.set_defaults(func=cmd_rc_apps)

    products = rc.add_parser("products", help="list products in the profile's RevenueCat project")
    _add_profile(products)
    products.set_defaults(func=cmd_rc_products)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except config.ConfigError as error:
        note(f"configuration error: {error}")
        return 3
    except (rc_module.RevenueCatError, revenuecat_cli.RevenueCatCliError) as error:
        note(f"platform error: {error}")
        return 4


if __name__ == "__main__":
    raise SystemExit(main())

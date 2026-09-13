"""Agent-facing CLI with profile-bound secret resolution.

This surface is intentionally narrower than the general `mra` CLI. RevenueCat
commands require an app profile so the project id and Bitwarden secret reference
are selected together. Secret values are never printed.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

from . import auth, config
from . import revenuecat as rc_module
from . import secrets as secret_provider


def emit(payload) -> int:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True, default=str)
    sys.stdout.write("\n")
    return 0


def note(message: str) -> None:
    print(message, file=sys.stderr)


def _profile(slug: str) -> config.Profile:
    profile = config.load_profile(slug)
    if not profile.revenuecat_project_id:
        raise config.ConfigError(f"profile {slug!r} has no revenuecat_project_id")
    if not profile.revenuecat_secret_id:
        raise config.ConfigError(f"profile {slug!r} has no revenuecat_secret_id")
    return profile


def _client(profile: config.Profile) -> rc_module.RevenueCatClient:
    return rc_module.RevenueCatClient(api_key=auth.revenuecat_key(profile))


def _confirm(args: argparse.Namespace, description: str) -> None:
    if args.yes:
        return
    raise SystemExit(
        f"refusing to {description} without --yes.\n"
        "This command changes live platform state. Re-run with --yes to authorize it."
    )


def cmd_doctor(args: argparse.Namespace) -> int:
    profiles = config.load_profiles()
    secured = {
        slug: {
            "revenuecat_project_id": profile.revenuecat_project_id,
            "revenuecat_secret_id": profile.revenuecat_secret_id,
        }
        for slug, profile in profiles.items()
        if profile.revenuecat_secret_id
    }
    return emit(
        {
            "bitwarden": secret_provider.bitwarden_status(),
            "secured_profiles": secured,
        }
    )


def cmd_bind_revenuecat(args: argparse.Namespace) -> int:
    path = config.save_profile(
        config.Profile(slug=args.profile, revenuecat_secret_id=args.secret_id)
    )
    return emit(
        {
            "saved": str(path),
            "profile": vars(config.load_profile(args.profile)),
        }
    )


def cmd_rc_projects(args: argparse.Namespace) -> int:
    profile = _profile(args.profile)
    return emit(_client(profile).list_projects())


def cmd_rc_apps(args: argparse.Namespace) -> int:
    profile = _profile(args.profile)
    return emit(_client(profile).list_apps(profile.revenuecat_project_id))


def cmd_rc_products(args: argparse.Namespace) -> int:
    profile = _profile(args.profile)
    return emit(_client(profile).list_products(profile.revenuecat_project_id))


def cmd_rc_create_play_app(args: argparse.Namespace) -> int:
    _confirm(args, f"create RevenueCat app {args.name!r}")
    profile = _profile(args.profile)
    if not profile.package_name:
        raise config.ConfigError(f"profile {profile.slug!r} has no package_name")
    key_path = config.require_file(config.PLAY_SERVICE_ACCOUNT, auth.PLAY_HINT)
    note(
        "sending the Play service account key to RevenueCat so it can validate "
        "Play purchases; this is the documented setup path"
    )
    return emit(
        _client(profile).create_play_app(
            profile.revenuecat_project_id,
            args.name,
            profile.package_name,
            key_path.read_text(encoding="utf-8"),
        )
    )


def cmd_rc_create_product(args: argparse.Namespace) -> int:
    _confirm(args, f"create RevenueCat product {args.store_identifier!r}")
    profile = _profile(args.profile)
    return emit(
        _client(profile).create_product(
            profile.revenuecat_project_id,
            args.app_id,
            args.store_identifier,
            args.type,
            args.display_name,
        )
    )


def _add_profile(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--profile", required=True, help="profile slug from profiles.json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mra-agent",
        description="Agent-safe MRA surface with profile-bound secret resolution.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="check Bitwarden bootstrap and profile refs").set_defaults(
        func=cmd_doctor
    )

    profile = subparsers.add_parser("profile", help="manage secret references").add_subparsers(
        dest="profile_command", required=True
    )
    bind = profile.add_parser("bind-revenuecat", help="bind a Bitwarden secret UUID to a profile")
    _add_profile(bind)
    bind.add_argument("--secret-id", required=True)
    bind.set_defaults(func=cmd_bind_revenuecat)

    rc = subparsers.add_parser("rc", help="RevenueCat API v2").add_subparsers(
        dest="rc_command", required=True
    )

    projects = rc.add_parser("projects", help="list projects visible to the profile key")
    _add_profile(projects)
    projects.set_defaults(func=cmd_rc_projects)

    apps = rc.add_parser("apps", help="list apps in the profile's RevenueCat project")
    _add_profile(apps)
    apps.set_defaults(func=cmd_rc_apps)

    products = rc.add_parser("products", help="list products in the profile's RevenueCat project")
    _add_profile(products)
    products.set_defaults(func=cmd_rc_products)

    create_app = rc.add_parser("create-play-app", help="create the profile's Play app")
    _add_profile(create_app)
    create_app.add_argument("--name", required=True)
    create_app.add_argument("--yes", action="store_true")
    create_app.set_defaults(func=cmd_rc_create_play_app)

    create_product = rc.add_parser("create-product", help="register a store product")
    _add_profile(create_product)
    create_product.add_argument("--app-id", required=True)
    create_product.add_argument("--store-identifier", required=True)
    create_product.add_argument("--type", required=True, choices=rc_module.PRODUCT_TYPES)
    create_product.add_argument("--display-name")
    create_product.add_argument("--yes", action="store_true")
    create_product.set_defaults(func=cmd_rc_create_product)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except config.ConfigError as error:
        note(f"configuration error: {error}")
        return 3
    except rc_module.RevenueCatError as error:
        note(f"platform error: {error}")
        return 4


if __name__ == "__main__":
    raise SystemExit(main())

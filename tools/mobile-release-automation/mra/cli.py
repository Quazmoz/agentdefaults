"""Command line entrypoint.

Every command prints JSON on stdout so an agent can consume the result without
scraping prose. Diagnostics go to stderr. Mutating commands refuse to run
without --yes so that an agent cannot mutate a live store by accident.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable
import argparse
import json
import sys

from . import admob as admob_module
from . import admob_credentials, auth, config, play_credentials, revenuecat_cli
from . import play as play_module
from . import play_reporting
from . import revenuecat as rc_module

MUTATING = "mutating"


def emit(payload: Any) -> int:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True, default=str)
    sys.stdout.write("\n")
    return 0


def note(message: str) -> None:
    print(message, file=sys.stderr)


def confirm(args: argparse.Namespace, description: str) -> None:
    if getattr(args, "yes", False):
        return
    raise SystemExit(
        f"refusing to {description} without --yes.\n"
        "This command changes live platform state. Re-run with --yes to authorize it."
    )


def resolve_package(args: argparse.Namespace) -> str:
    if getattr(args, "package", None):
        return args.package
    if getattr(args, "profile", None):
        profile = config.load_profile(args.profile)
        if not profile.package_name:
            raise SystemExit(f"profile {args.profile!r} has no package_name")
        return profile.package_name
    raise SystemExit("pass --package or --profile")


def resolve_project(args: argparse.Namespace) -> str:
    if getattr(args, "project", None):
        return args.project
    if getattr(args, "profile", None):
        profile = config.load_profile(args.profile)
        if not profile.revenuecat_project_id:
            raise SystemExit(f"profile {args.profile!r} has no revenuecat_project_id")
        return profile.revenuecat_project_id
    raise SystemExit("pass --project or --profile")


def rc_client(args: argparse.Namespace) -> rc_module.RevenueCatClient:
    """Return the OAuth-backed RevenueCat client; profile only supplies identity."""
    if getattr(args, "profile", None):
        config.load_profile(args.profile)  # validate the local profile exists
    return rc_module.RevenueCatClient()


def parse_notes(values: list[str] | None) -> dict[str, str] | None:
    """Parse repeated --notes LANG=TEXT into the release notes mapping."""
    if not values:
        return None
    notes: dict[str, str] = {}
    for value in values:
        language, separator, text = value.partition("=")
        if not separator:
            raise SystemExit(f"--notes expects LANG=TEXT, got {value!r}")
        notes[language.strip()] = text
    return notes


# ---- doctor ----------------------------------------------------------------


def cmd_doctor(args: argparse.Namespace) -> int:
    report: dict[str, Any] = {"credential_home": str(config.home()), "checks": {}}

    def record(name: str, probe: Callable[[], Any]) -> None:
        try:
            report["checks"][name] = {"status": "ok", "detail": probe()}
        except Exception as error:  # noqa: BLE001 - doctor reports, never raises
            report["checks"][name] = {"status": "fail", "detail": str(error)}

    record("play_service_account", play_credentials.publisher_status)
    record("revenuecat_oauth", revenuecat_cli.auth_status)
    record("admob", admob_credentials.status)
    record("profiles", lambda: sorted(config.load_profiles()))

    failed = [name for name, check in report["checks"].items() if check["status"] == "fail"]
    report["status"] = "fail" if failed else "ok"
    report["failed_checks"] = failed
    emit(report)
    return 1 if failed else 0


# ---- play ------------------------------------------------------------------


def cmd_play_tracks(args: argparse.Namespace) -> int:
    return emit(play_module.track_status(resolve_package(args)))


def cmd_play_publish(args: argparse.Namespace) -> int:
    if not args.dry_run:
        confirm(args, f"publish to the {args.track!r} track")
    return emit(
        play_module.publish_bundle(
            resolve_package(args),
            Path(args.aab).expanduser(),
            track=args.track,
            status=args.status,
            release_notes=parse_notes(args.notes),
            user_fraction=args.user_fraction,
            release_name=args.release_name,
            dry_run=args.dry_run,
            changes_not_sent_for_review=args.changes_not_sent_for_review,
        )
    )


def cmd_play_promote(args: argparse.Namespace) -> int:
    if not args.dry_run:
        confirm(args, f"promote {args.source!r} to {args.target!r}")
    return emit(
        play_module.promote(
            resolve_package(args),
            from_track=args.source,
            to_track=args.target,
            version_codes=args.version_code,
            status=args.status,
            user_fraction=args.user_fraction,
            release_notes=parse_notes(args.notes),
            dry_run=args.dry_run,
        )
    )


def cmd_play_freshness(args: argparse.Namespace) -> int:
    """Read-only: how current each official Play reporting surface actually is."""
    return emit(
        play_reporting.freshness(
            args.profile, include_financial=not args.skip_financial
        )
    )


def cmd_play_products(args: argparse.Namespace) -> int:
    client = play_module.PlayClient(resolve_package(args))
    return emit(
        {
            "subscriptions": client.list_subscriptions(),
            "in_app_products": client.list_in_app_products(),
        }
    )


def cmd_play_create_subscription(args: argparse.Namespace) -> int:
    confirm(args, f"create subscription {args.product_id!r} in Play")
    body = json.loads(Path(args.body).expanduser().read_text(encoding="utf-8"))
    client = play_module.PlayClient(resolve_package(args))
    return emit(client.create_subscription(args.product_id, body, args.regions_version))


# ---- admob -----------------------------------------------------------------


def cmd_admob_login(args: argparse.Namespace) -> int:
    auth.admob_session(include_monetization=not args.read_only, allow_consent=True)
    return emit(
        {
            "status": "authorized",
            "credentials": admob_credentials.status(),
            "scopes": auth.admob_scopes(include_monetization=not args.read_only),
        }
    )


def cmd_admob_probe(args: argparse.Namespace) -> int:
    result = admob_module.AdMobClient(args.publisher_id).probe_monetization_access()
    emit(result)
    return 0 if result["monetization_access"] == "likely" else 2


def cmd_admob_apps(args: argparse.Namespace) -> int:
    return emit(admob_module.AdMobClient(args.publisher_id).list_apps())


def cmd_admob_adunits(args: argparse.Namespace) -> int:
    return emit(admob_module.AdMobClient(args.publisher_id).list_ad_units())


def cmd_admob_create_app(args: argparse.Namespace) -> int:
    confirm(args, f"create AdMob app {args.name!r}")
    return emit(
        admob_module.AdMobClient(args.publisher_id).create_app(
            args.name, args.platform, args.app_store_id
        )
    )


def cmd_admob_create_adunit(args: argparse.Namespace) -> int:
    confirm(args, f"create AdMob ad unit {args.name!r}")
    return emit(
        admob_module.AdMobClient(args.publisher_id).create_ad_unit(
            args.app_id, args.name, args.format, args.type
        )
    )


# ---- revenuecat ------------------------------------------------------------


def cmd_rc_projects(args: argparse.Namespace) -> int:
    return emit(rc_client(args).list_projects())


def cmd_rc_apps(args: argparse.Namespace) -> int:
    return emit(rc_client(args).list_apps(resolve_project(args)))


def cmd_rc_create_play_app(args: argparse.Namespace) -> int:
    confirm(args, f"create RevenueCat app {args.name!r}")
    note(
        "sending the dedicated RevenueCat Google Play service credential to RevenueCat "
        "so it can validate Play purchases"
    )
    return emit(
        rc_client(args).create_play_app(
            resolve_project(args),
            args.name,
            args.package_name or resolve_package(args),
            play_credentials.revenuecat_json(),
        )
    )


def cmd_rc_products(args: argparse.Namespace) -> int:
    return emit(rc_client(args).list_products(resolve_project(args)))


def cmd_rc_create_product(args: argparse.Namespace) -> int:
    confirm(args, f"create RevenueCat product {args.store_identifier!r}")
    return emit(
        rc_client(args).create_product(
            resolve_project(args),
            args.app_id,
            args.store_identifier,
            args.type,
            args.display_name,
        )
    )


# ---- profile ---------------------------------------------------------------


def cmd_profile_list(args: argparse.Namespace) -> int:
    return emit({slug: vars(profile) for slug, profile in config.load_profiles().items()})


def cmd_profile_set(args: argparse.Namespace) -> int:
    profile = config.Profile(
        slug=args.slug,
        package_name=args.package_name,
        admob_app_id=args.admob_app_id,
        admob_publisher_id=args.admob_publisher_id,
        revenuecat_project_id=args.revenuecat_project_id,
        revenuecat_app_id=args.revenuecat_app_id,
        play_reporting_bucket=args.play_reporting_bucket,
    )
    path = config.save_profile(profile)
    return emit({"saved": str(path), "profile": vars(config.load_profile(args.slug))})


# ---- parser ----------------------------------------------------------------


def add_target(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--profile", help="profile slug from profiles.json")
    parser.add_argument("--package", help="Play package name, overrides the profile")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mra",
        description="Local automation for Google Play, AdMob, and RevenueCat.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="authorize commands that change live platform state",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="check local credentials and OAuth").set_defaults(
        func=cmd_doctor
    )

    # play
    play = subparsers.add_parser("play", help="Google Play Developer API").add_subparsers(
        dest="play_command", required=True
    )

    tracks = play.add_parser("tracks", help="list track state")
    add_target(tracks)
    tracks.set_defaults(func=cmd_play_tracks)

    publish = play.add_parser("publish", help=f"upload an .aab to a track [{MUTATING}]")
    add_target(publish)
    publish.add_argument("--aab", required=True, help="path to the app bundle")
    publish.add_argument("--track", default="internal")
    publish.add_argument("--status", default="completed", choices=play_module.RELEASE_STATUSES)
    publish.add_argument("--notes", action="append", metavar="LANG=TEXT")
    publish.add_argument("--user-fraction", type=float, help="staged rollout fraction")
    publish.add_argument("--release-name")
    publish.add_argument("--dry-run", action="store_true", help="validate then discard the edit")
    publish.add_argument(
        "--changes-not-sent-for-review",
        action="store_true",
        help="commit without sending pending changes for review",
    )
    publish.set_defaults(func=cmd_play_publish)

    promote = play.add_parser("promote", help=f"promote a release between tracks [{MUTATING}]")
    add_target(promote)
    promote.add_argument("--source", required=True, help="source track")
    promote.add_argument("--target", required=True, help="target track")
    promote.add_argument("--version-code", action="append", type=int)
    promote.add_argument("--status", default="completed", choices=play_module.RELEASE_STATUSES)
    promote.add_argument("--user-fraction", type=float)
    promote.add_argument("--notes", action="append", metavar="LANG=TEXT")
    promote.add_argument("--dry-run", action="store_true")
    promote.set_defaults(func=cmd_play_promote)

    freshness = play.add_parser(
        "freshness", help="report how current each official Play reporting surface is"
    )
    freshness.add_argument("--profile", required=True, help="profile slug from profiles.json")
    freshness.add_argument(
        "--skip-financial",
        action="store_true",
        help="skip the estimated-sales and earnings exports",
    )
    freshness.set_defaults(func=cmd_play_freshness)

    products = play.add_parser("products", help="list Play monetization products")
    add_target(products)
    products.set_defaults(func=cmd_play_products)

    subscription = play.add_parser(
        "create-subscription", help=f"create a Play subscription [{MUTATING}]"
    )
    add_target(subscription)
    subscription.add_argument("--product-id", required=True)
    subscription.add_argument("--body", required=True, help="path to a Subscription JSON body")
    subscription.add_argument("--regions-version", default="2022/02")
    subscription.set_defaults(func=cmd_play_create_subscription)

    # admob
    admob = subparsers.add_parser("admob", help="AdMob API").add_subparsers(
        dest="admob_command", required=True
    )
    login = admob.add_parser("login", help="run the one-time browser consent")
    login.add_argument(
        "--read-only",
        action="store_true",
        help="request only read scopes, skipping admob.monetization",
    )
    login.set_defaults(func=cmd_admob_login)

    probe = admob.add_parser("probe", help="test whether monetization access is granted")
    probe.add_argument("--publisher-id")
    probe.set_defaults(func=cmd_admob_probe)

    admob_apps = admob.add_parser("apps", help="list AdMob apps")
    admob_apps.add_argument("--publisher-id")
    admob_apps.set_defaults(func=cmd_admob_apps)

    adunits = admob.add_parser("adunits", help="list AdMob ad units")
    adunits.add_argument("--publisher-id")
    adunits.set_defaults(func=cmd_admob_adunits)

    create_app = admob.add_parser(
        "create-app", help=f"create an AdMob app, limited access [{MUTATING}]"
    )
    create_app.add_argument("--publisher-id")
    create_app.add_argument("--name", required=True)
    create_app.add_argument("--platform", default="ANDROID", choices=admob_module.PLATFORMS)
    create_app.add_argument("--app-store-id", help="Play package name, links the store listing")
    create_app.set_defaults(func=cmd_admob_create_app)

    create_adunit = admob.add_parser(
        "create-adunit", help=f"create an AdMob ad unit, limited access [{MUTATING}]"
    )
    create_adunit.add_argument("--publisher-id")
    create_adunit.add_argument("--app-id", required=True)
    create_adunit.add_argument("--name", required=True)
    create_adunit.add_argument("--format", required=True, choices=admob_module.AD_FORMATS)
    create_adunit.add_argument("--type", action="append", choices=admob_module.AD_TYPES)
    create_adunit.set_defaults(func=cmd_admob_create_adunit)

    # revenuecat
    rc = subparsers.add_parser("rc", help="RevenueCat API v2 via official CLI OAuth").add_subparsers(
        dest="rc_command", required=True
    )

    rc_projects = rc.add_parser("projects", help="list RevenueCat projects")
    rc_projects.add_argument("--profile")
    rc_projects.set_defaults(func=cmd_rc_projects)

    rc_apps = rc.add_parser("apps", help="list apps in a project")
    rc_apps.add_argument("--project")
    rc_apps.add_argument("--profile")
    rc_apps.set_defaults(func=cmd_rc_apps)

    rc_create_app = rc.add_parser(
        "create-play-app", help=f"create a Play app in RevenueCat [{MUTATING}]"
    )
    rc_create_app.add_argument("--project")
    add_target(rc_create_app)
    rc_create_app.add_argument("--name", required=True)
    rc_create_app.add_argument("--package-name")
    rc_create_app.set_defaults(func=cmd_rc_create_play_app)

    rc_products = rc.add_parser("products", help="list RevenueCat products")
    rc_products.add_argument("--project")
    rc_products.add_argument("--profile")
    rc_products.set_defaults(func=cmd_rc_products)

    rc_create_product = rc.add_parser(
        "create-product", help=f"register a store product with RevenueCat [{MUTATING}]"
    )
    rc_create_product.add_argument("--project")
    rc_create_product.add_argument("--profile")
    rc_create_product.add_argument("--app-id", required=True)
    rc_create_product.add_argument("--store-identifier", required=True)
    rc_create_product.add_argument("--type", required=True, choices=rc_module.PRODUCT_TYPES)
    rc_create_product.add_argument("--display-name")
    rc_create_product.set_defaults(func=cmd_rc_create_product)

    # profile
    profile = subparsers.add_parser("profile", help="local app identity mapping").add_subparsers(
        dest="profile_command", required=True
    )
    profile.add_parser("list", help="list profiles").set_defaults(func=cmd_profile_list)

    profile_set = profile.add_parser("set", help="create or update a profile")
    profile_set.add_argument("--slug", required=True)
    profile_set.add_argument("--package-name")
    profile_set.add_argument("--admob-app-id")
    profile_set.add_argument("--admob-publisher-id")
    profile_set.add_argument("--revenuecat-project-id")
    profile_set.add_argument("--revenuecat-app-id")
    profile_set.add_argument(
        "--play-reporting-bucket",
        help="Play bulk-report Cloud Storage bucket id from Play Console; not a secret",
    )
    profile_set.set_defaults(func=cmd_profile_set)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (config.ConfigError, play_reporting.ReportingError) as error:
        note(f"configuration error: {error}")
        return 3
    except (play_module.PlayError, admob_module.AdMobError, rc_module.RevenueCatError) as error:
        note(f"platform error: {error}")
        return 4


if __name__ == "__main__":
    raise SystemExit(main())

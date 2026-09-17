"""Credential and profile resolution.

Credentials live outside the repository by default. Nothing in this module ever
writes a secret into the working tree. Profiles and global credential bindings
may store immutable references to external secret-manager objects, but never
secret values.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import json
import os
import stat

DEFAULT_HOME = Path.home() / ".config" / "mobile-release-automation"

PLAY_SERVICE_ACCOUNT = "play-service-account.json"
ADMOB_OAUTH_CLIENT = "admob-oauth-client.json"
ADMOB_TOKEN = "admob-token.json"
REVENUECAT_KEY = "revenuecat-v2-secret.key"  # legacy compatibility only
PROFILES = "profiles.json"
SECRET_REFS = "secret-refs.json"
REVENUECAT_OAUTH_MARKER = "oauth-cli"


class ConfigError(RuntimeError):
    """Raised when required local credential material is missing or unsafe."""


def home() -> Path:
    """Return the credential directory, honouring MRA_HOME."""
    return Path(os.environ.get("MRA_HOME", DEFAULT_HOME)).expanduser()


def path_for(name: str) -> Path:
    return home() / name


def require_file(name: str, hint: str) -> Path:
    path = path_for(name)
    if not path.is_file():
        raise ConfigError(f"missing {path}\n  fix: {hint}")
    _require_private(path)
    return path


def _require_private(path: Path) -> None:
    """Refuse to read credential material that is group/world readable."""
    mode = path.stat().st_mode
    if mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise ConfigError(
            f"{path} is group/world accessible.\n"
            f"  fix: chmod 600 {path}"
        )


def read_secret(name: str, env_var: str, hint: str) -> str:
    """Read a secret from an environment variable, else from the credential dir."""
    value = os.environ.get(env_var, "").strip()
    if value:
        return value
    return require_file(name, hint).read_text(encoding="utf-8").strip()


def ensure_home() -> Path:
    directory = home()
    directory.mkdir(parents=True, exist_ok=True)
    directory.chmod(0o700)
    return directory


@dataclass(frozen=True)
class SecretRefs:
    """Global immutable references to externally stored credential material.

    `revenuecat_bootstrap_secret_id` is retained only so existing local config
    files from MRA 1.6.1 continue to load. It is ignored by current RevenueCat
    automation, which uses the official RevenueCat CLI OAuth session instead.
    """

    play_service_account_secret_id: str | None = None
    revenuecat_play_service_account_secret_id: str | None = None
    revenuecat_bootstrap_secret_id: str | None = None
    admob_oauth_client_secret_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> "SecretRefs":
        known = set(cls.__dataclass_fields__)
        unknown = sorted(set(data) - known)
        if unknown:
            raise ConfigError(f"secret refs have unknown keys: {', '.join(unknown)}")
        return cls(**data)


def load_secret_refs() -> SecretRefs:
    path = path_for(SECRET_REFS)
    if not path.is_file():
        return SecretRefs()
    _require_private(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ConfigError(f"{path} must contain a JSON object")
    return SecretRefs.from_dict(raw)


def save_secret_refs(refs: SecretRefs) -> Path:
    """Persist or merge global secret references, never secret values."""
    ensure_home()
    path = path_for(SECRET_REFS)
    if path.is_file():
        _require_private(path)
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ConfigError(f"{path} must contain a JSON object")
    else:
        raw = {}
    updates = {key: value for key, value in vars(refs).items() if value is not None}
    raw = {**raw, **updates}
    SecretRefs.from_dict(raw)
    path.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)
    return path


@dataclass(frozen=True)
class Profile:
    """A single app's identity across all three platforms.

    `revenuecat_secret_id` is a deprecated compatibility field. MRA no longer
    resolves RevenueCat API keys from it, but old profile files remain readable.
    """

    slug: str
    package_name: str | None = None
    admob_app_id: str | None = None
    admob_publisher_id: str | None = None
    revenuecat_project_id: str | None = None
    revenuecat_app_id: str | None = None
    revenuecat_secret_id: str | None = None

    @classmethod
    def from_dict(cls, slug: str, data: dict) -> "Profile":
        known = {field for field in cls.__dataclass_fields__ if field != "slug"}
        unknown = sorted(set(data) - known)
        if unknown:
            raise ConfigError(f"profile {slug!r} has unknown keys: {', '.join(unknown)}")
        return cls(slug=slug, **data)


def load_profiles() -> dict[str, Profile]:
    """Load persisted profiles exactly as stored."""
    path = path_for(PROFILES)
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {slug: Profile.from_dict(slug, data) for slug, data in raw.items()}


def load_profile(slug: str) -> Profile:
    """Load one profile with an in-memory RevenueCat OAuth compatibility marker.

    Several older reconciliation call sites use `revenuecat_secret_id` only as a
    boolean "RevenueCat auth is configured" marker. New MRA versions authenticate
    through the official RevenueCat CLI, so profiles without a legacy key receive
    the non-secret `oauth-cli` marker in memory. It is never persisted.
    """
    profiles = load_profiles()
    if slug not in profiles:
        known = ", ".join(sorted(profiles)) or "(none defined)"
        raise ConfigError(f"unknown profile {slug!r}. known profiles: {known}")
    profile = profiles[slug]
    if profile.revenuecat_secret_id:
        return profile
    return replace(profile, revenuecat_secret_id=REVENUECAT_OAUTH_MARKER)


def save_profile(profile: Profile) -> Path:
    """Persist or merge one profile, preserving fields the caller left unset."""
    ensure_home()
    path = path_for(PROFILES)
    raw = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    existing = raw.get(profile.slug, {})
    updates = {
        field: value
        for field, value in vars(profile).items()
        if field != "slug" and value is not None and value != REVENUECAT_OAUTH_MARKER
    }
    raw[profile.slug] = {**existing, **updates}
    path.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)
    return path


def public_profile(profile: Profile) -> dict[str, str | None]:
    """Return only non-secret cross-platform identifiers for agent-visible output."""
    return {
        "slug": profile.slug,
        "package_name": profile.package_name,
        "admob_app_id": profile.admob_app_id,
        "admob_publisher_id": profile.admob_publisher_id,
        "revenuecat_project_id": profile.revenuecat_project_id,
        "revenuecat_app_id": profile.revenuecat_app_id,
    }


def update_profile_identifiers(
    slug: str,
    *,
    package_name: str | None = None,
    admob_app_id: str | None = None,
    admob_publisher_id: str | None = None,
    revenuecat_project_id: str | None = None,
    revenuecat_app_id: str | None = None,
) -> Profile:
    """Safely reconcile non-secret identifiers for an existing profile."""
    load_profile(slug)  # refuse accidental creation of a partial profile
    values = {
        "package_name": package_name,
        "admob_app_id": admob_app_id,
        "admob_publisher_id": admob_publisher_id,
        "revenuecat_project_id": revenuecat_project_id,
        "revenuecat_app_id": revenuecat_app_id,
    }
    updates = {}
    for field, value in values.items():
        if value is None:
            continue
        normalized = value.strip()
        if not normalized:
            raise ConfigError(f"profile identifier {field} cannot be blank")
        updates[field] = normalized
    if not updates:
        raise ConfigError("no profile identifiers supplied")

    save_profile(Profile(slug=slug, **updates))
    return load_profile(slug)

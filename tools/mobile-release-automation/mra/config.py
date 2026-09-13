"""Credential and profile resolution.

Credentials live outside the repository by default. Nothing in this module ever
writes a secret into the working tree. Profiles may store immutable references to
external secret-manager objects, but never secret values.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os
import stat

DEFAULT_HOME = Path.home() / ".config" / "mobile-release-automation"

PLAY_SERVICE_ACCOUNT = "play-service-account.json"
ADMOB_OAUTH_CLIENT = "admob-oauth-client.json"
ADMOB_TOKEN = "admob-token.json"
REVENUECAT_KEY = "revenuecat-v2-secret.key"
PROFILES = "profiles.json"


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
class Profile:
    """A single app's identity across all three platforms."""

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
    path = path_for(PROFILES)
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {slug: Profile.from_dict(slug, data) for slug, data in raw.items()}


def load_profile(slug: str) -> Profile:
    profiles = load_profiles()
    if slug not in profiles:
        known = ", ".join(sorted(profiles)) or "(none defined)"
        raise ConfigError(f"unknown profile {slug!r}. known profiles: {known}")
    return profiles[slug]


def save_profile(profile: Profile) -> Path:
    """Persist or merge one profile, preserving fields the caller left unset."""
    ensure_home()
    path = path_for(PROFILES)
    raw = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    existing = raw.get(profile.slug, {})
    updates = {
        field: value
        for field, value in vars(profile).items()
        if field != "slug" and value is not None
    }
    raw[profile.slug] = {**existing, **updates}
    path.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)
    return path

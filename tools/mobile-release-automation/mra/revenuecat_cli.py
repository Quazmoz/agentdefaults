"""OAuth-backed RevenueCat execution through the official RevenueCat CLI.

MRA deliberately does not implement its own RevenueCat OAuth client. RevenueCat
requires OAuth clients to be registered/allowlisted, while the official `rc` CLI
already implements browser OAuth, token refresh, secure local credential storage,
and a stable JSON/agent surface.

All MRA RevenueCat API traffic therefore goes through `rc api`. API-key
environment overrides are removed from the child process so a stale project-scoped
`sk_...` key cannot silently take precedence over OAuth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
import json
import os
import shutil
import subprocess

from . import config, redaction

DEFAULT_TIMEOUT_SECONDS = 90
OAUTH_METHOD = "oauth"


class RevenueCatCliError(RuntimeError):
    """Raised when the official RevenueCat CLI is unavailable or a call fails."""

    def __init__(self, message: str, *, exit_code: int | None = None) -> None:
        super().__init__(message)
        self.exit_code = exit_code


@dataclass(frozen=True)
class CommandResult:
    payload: Any
    stdout: str


def _binary() -> str:
    path = shutil.which("rc") or shutil.which("revenuecat")
    if path:
        return path
    raise config.ConfigError(
        "official RevenueCat CLI is not installed.\n"
        "  fix: brew install RevenueCat/tap/rc\n"
        "  then run: rc auth login"
    )


def _environment() -> dict[str, str]:
    """Return a child environment that forces stored OAuth over API-key overrides."""
    env = dict(os.environ)
    env.pop("RC_API_KEY", None)
    env.pop("REVENUECAT_V2_SECRET_KEY", None)
    return env


def _global_args() -> list[str]:
    args = ["--json", "--no-input"]
    profile = os.environ.get("MRA_REVENUECAT_CLI_PROFILE", "").strip()
    if profile:
        args.extend(["--profile", profile])
    return args


def _run(
    args: list[str],
    *,
    stdin: str | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> CommandResult:
    command = [_binary(), *_global_args(), *args]
    completed = subprocess.run(
        command,
        input=stdin,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=_environment(),
        check=False,
    )
    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    payload: Any = {}
    if stdout:
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            payload = {"output": redaction.redact_text(stdout)}

    if completed.returncode != 0:
        detail = stderr or stdout or f"RevenueCat CLI exited with code {completed.returncode}"
        raise RevenueCatCliError(
            redaction.redact_text(detail),
            exit_code=completed.returncode,
        )
    return CommandResult(payload=payload, stdout=stdout)


def auth_status() -> dict[str, Any]:
    """Return OAuth authentication state without exposing tokens."""
    result = _run(["auth", "status"])
    payload = result.payload if isinstance(result.payload, dict) else {}
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    authenticated = bool(data.get("authenticated"))
    method = str(data.get("method") or "").strip().lower()
    credential_source = str(data.get("credential_source") or "").strip().lower()
    # RevenueCat CLI 0.1.2 decorates the human-readable method with expiry,
    # e.g. "oauth (expires 2026-09-18 19:04)", while credential_source remains
    # the stable machine-readable discriminator. Accept either representation.
    is_oauth = credential_source == OAUTH_METHOD or method == OAUTH_METHOD or method.startswith(
        f"{OAUTH_METHOD} ("
    )
    if not authenticated:
        raise config.ConfigError(
            "RevenueCat CLI is not authenticated.\n"
            "  fix: run `rc auth login` and complete the browser OAuth flow"
        )
    if not is_oauth:
        raise config.ConfigError(
            "RevenueCat CLI is authenticated with an API key, not OAuth.\n"
            "  fix: run `rc auth logout` and then `rc auth login`; choose browser OAuth"
        )
    return {
        "status": "ready",
        "source": "official-revenuecat-cli-oauth",
        "authenticated": True,
        "method": OAUTH_METHOD,
        "account_email": data.get("account_email"),
        "account_name": data.get("account_name"),
    }


def require_oauth() -> None:
    auth_status()


def api_call(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    body: Any | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Any:
    """Call RevenueCat API v2 through the official OAuth-authenticated CLI."""
    require_oauth()
    normalized = path if path.startswith("/") else f"/{path}"
    if params:
        encoded = urlencode(
            [(key, value) for key, value in params.items() if value is not None],
            doseq=True,
        )
        if encoded:
            normalized = f"{normalized}?{encoded}"

    args = ["api", method.upper(), normalized]
    stdin = None
    if body is not None:
        args.extend(["--body", "@-"])
        stdin = json.dumps(body, separators=(",", ":"))

    return _run(args, stdin=stdin, timeout=timeout).payload

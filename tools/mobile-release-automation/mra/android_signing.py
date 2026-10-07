"""macOS Keychain-backed Android release signing.

This module gives local agents a narrow way to build signed Android App Bundles
without receiving keystore passwords. Non-secret identity metadata lives under
MRA_HOME; passwords live only in the OS credential store.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import time

from . import config

ANDROID_SIGNING_KEYCHAIN_SERVICE = "com.quazmoz.mobile-release-automation.android-signing"
ANDROID_SIGNING_CONFIG = "android-signing.json"
DEFAULT_IDENTITY = "play-upload"

_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_MODULE_PART_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_SHA256_RE = re.compile(r"SHA256:\s*([0-9A-Fa-f:]{32,})")


@dataclass(frozen=True)
class SigningIdentity:
    name: str
    keystore_path: str
    key_alias: str
    certificate_sha256: str

    @classmethod
    def from_dict(cls, name: str, data: dict) -> "SigningIdentity":
        if not isinstance(data, dict):
            raise config.ConfigError(f"signing identity {name!r} must be a JSON object")
        expected = {"keystore_path", "key_alias", "certificate_sha256"}
        unknown = sorted(set(data) - expected)
        missing = sorted(expected - set(data))
        if unknown:
            raise config.ConfigError(
                f"signing identity {name!r} has unknown keys: {', '.join(unknown)}"
            )
        if missing:
            raise config.ConfigError(
                f"signing identity {name!r} is missing keys: {', '.join(missing)}"
            )
        return cls(name=name, **data)


def _normalize_name(name: str) -> str:
    value = name.strip()
    if not value or not _NAME_RE.fullmatch(value):
        raise config.ConfigError(
            "signing identity name must contain only letters, numbers, dot, underscore, or hyphen"
        )
    return value


def _config_path() -> Path:
    return config.path_for(ANDROID_SIGNING_CONFIG)


def _load_raw() -> dict:
    path = _config_path()
    if not path.is_file():
        return {}
    if path.stat().st_mode & (stat.S_IRWXG | stat.S_IRWXO):
        raise config.ConfigError(f"{path} is group/world accessible; fix with chmod 600 {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise config.ConfigError(f"{path} must contain a JSON object")
    return raw


def load_identities() -> dict[str, SigningIdentity]:
    return {name: SigningIdentity.from_dict(name, value) for name, value in _load_raw().items()}


def load_identity(name: str = DEFAULT_IDENTITY) -> SigningIdentity:
    normalized = _normalize_name(name)
    identities = load_identities()
    if normalized not in identities:
        known = ", ".join(sorted(identities)) or "(none configured)"
        raise config.ConfigError(
            f"unknown Android signing identity {normalized!r}; configured: {known}"
        )
    return identities[normalized]


def _save_identity(identity: SigningIdentity) -> Path:
    config.ensure_home()
    path = _config_path()
    raw = _load_raw()
    raw[identity.name] = {
        key: value for key, value in asdict(identity).items() if key != "name"
    }
    path.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    path.chmod(0o600)
    return path


def _account(name: str, kind: str) -> str:
    return f"{name}:{kind}"


def _set_secret(name: str, kind: str, value: str) -> None:
    if not value:
        raise config.ConfigError(f"refusing to store an empty Android signing {kind}")
    try:
        import keyring
        keyring.set_password(ANDROID_SIGNING_KEYCHAIN_SERVICE, _account(name, kind), value)
    except Exception as error:  # noqa: BLE001
        raise config.ConfigError(
            f"could not store Android signing {kind} in the OS credential store"
        ) from error


def _get_secret(name: str, kind: str) -> str | None:
    try:
        import keyring
        value = keyring.get_password(ANDROID_SIGNING_KEYCHAIN_SERVICE, _account(name, kind))
    except Exception as error:  # noqa: BLE001
        raise config.ConfigError(
            f"could not read Android signing {kind} from the OS credential store"
        ) from error
    return value if value else None


def _java_tool(name: str) -> str:
    java_home = os.environ.get("JAVA_HOME", "").strip()
    candidates: list[Path] = []
    if java_home:
        candidates.append(Path(java_home) / "bin" / name)
    if os.sys.platform == "darwin":
        candidates.append(
            Path("/Applications/Android Studio.app/Contents/jbr/Contents/Home/bin") / name
        )
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    resolved = shutil.which(name)
    if resolved:
        return resolved
    raise config.ConfigError(
        f"{name} was not found; set JAVA_HOME to the Android Studio/JDK toolchain"
    )


def _normalize_fingerprint(value: str) -> str:
    return value.replace(":", "").strip().upper()


def _extract_sha256(text: str) -> str:
    match = _SHA256_RE.search(text)
    if not match:
        raise config.ConfigError("could not read a SHA-256 certificate fingerprint")
    return _normalize_fingerprint(match.group(1))


def _keystore_fingerprint(keystore_path: Path, key_alias: str, store_password: str) -> str:
    completed = subprocess.run(
        [
            _java_tool("keytool"),
            "-list",
            "-v",
            "-keystore",
            str(keystore_path),
            "-alias",
            key_alias,
        ],
        input=store_password + "\n",
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise config.ConfigError(
            "could not verify the Android keystore/alias; check the local password and alias"
        )
    return _extract_sha256(completed.stdout + "\n" + completed.stderr)


def configure_identity(
    name: str,
    keystore_path: str | Path,
    key_alias: str,
    *,
    store_password: str,
    key_password: str,
) -> dict:
    """Store passwords in Keychain and persist only non-secret identity metadata."""
    normalized = _normalize_name(name)
    path = Path(keystore_path).expanduser().resolve()
    alias = key_alias.strip()
    if not path.is_file():
        raise config.ConfigError(f"Android keystore does not exist: {path}")
    if not alias:
        raise config.ConfigError("Android signing key alias cannot be blank")

    fingerprint = _keystore_fingerprint(path, alias, store_password)
    _set_secret(normalized, "store-password", store_password)
    _set_secret(normalized, "key-password", key_password)
    saved = _save_identity(
        SigningIdentity(
            name=normalized,
            keystore_path=str(path),
            key_alias=alias,
            certificate_sha256=fingerprint,
        )
    )
    return {
        "status": "ready",
        "identity": normalized,
        "keystore_path": str(path),
        "key_alias": alias,
        "certificate_sha256": fingerprint,
        "secret_source": "os-keychain",
        "metadata_path": str(saved),
    }


def _identity_secrets(name: str) -> tuple[str, str]:
    store_password = _get_secret(name, "store-password")
    key_password = _get_secret(name, "key-password")
    if not store_password or not key_password:
        raise config.ConfigError(
            f"Android signing identity {name!r} is missing password material in the OS Keychain"
        )
    return store_password, key_password


def identity_status(name: str = DEFAULT_IDENTITY) -> dict:
    """Return only non-secret readiness and certificate identity."""
    try:
        identity = load_identity(name)
    except config.ConfigError as error:
        return {
            "status": "not-configured",
            "identity": _normalize_name(name),
            "ready": False,
            "detail": str(error),
        }

    path = Path(identity.keystore_path)
    store_password = _get_secret(identity.name, "store-password")
    key_password = _get_secret(identity.name, "key-password")
    result = {
        "identity": identity.name,
        "keystore_path": identity.keystore_path,
        "key_alias": identity.key_alias,
        "configured_certificate_sha256": identity.certificate_sha256,
        "keystore_exists": path.is_file(),
        "passwords_ready": bool(store_password and key_password),
        "secret_source": "os-keychain",
        "ready": False,
    }
    if not path.is_file() or not store_password or not key_password:
        result["status"] = "not-ready"
        return result

    try:
        observed = _keystore_fingerprint(path, identity.key_alias, store_password)
    except config.ConfigError as error:
        result["status"] = "not-ready"
        result["detail"] = str(error)
        return result

    result["observed_certificate_sha256"] = observed
    result["certificate_matches"] = observed == identity.certificate_sha256
    result["ready"] = bool(result["certificate_matches"])
    result["status"] = "ready" if result["ready"] else "certificate-mismatch"
    return result


def all_identity_statuses() -> list[dict]:
    try:
        names = sorted(load_identities())
    except config.ConfigError as error:
        return [{"status": "error", "ready": False, "detail": str(error)}]
    return [identity_status(name) for name in names]


def _run(args: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)


def _git_state(repo: Path) -> dict[str, str]:
    top = _run(["git", "rev-parse", "--show-toplevel"], cwd=repo)
    if top.returncode != 0:
        raise config.ConfigError(f"{repo} is not a Git worktree")
    resolved_top = Path(top.stdout.strip()).resolve()
    if resolved_top != repo.resolve():
        raise config.ConfigError(f"repo_path must be the Git worktree root: expected {resolved_top}")

    status = _run(["git", "status", "--porcelain=v1", "--untracked-files=normal"], cwd=repo)
    if status.returncode != 0:
        raise config.ConfigError(f"could not inspect Git status in {repo}")
    if status.stdout.strip():
        raise config.ConfigError(
            "refusing to resolve Android signing secrets for a dirty worktree"
        )

    sha = _run(["git", "rev-parse", "HEAD"], cwd=repo)
    branch = _run(["git", "branch", "--show-current"], cwd=repo)
    if sha.returncode != 0 or branch.returncode != 0:
        raise config.ConfigError("could not resolve current Git candidate identity")
    return {"git_sha": sha.stdout.strip(), "branch": branch.stdout.strip()}


def _normalize_module(module: str) -> str:
    raw = module.strip().strip(":")
    parts = raw.split(":") if raw else []
    if not parts or any(not _MODULE_PART_RE.fullmatch(part) for part in parts):
        raise config.ConfigError(f"invalid Android module name: {module!r}")
    return ":".join(parts)


def _module_dir(repo: Path, module: str) -> Path:
    target = repo.joinpath(*module.split(":")).resolve()
    try:
        target.relative_to(repo.resolve())
    except ValueError as error:
        raise config.ConfigError("Android module path escapes the repository") from error
    if not target.is_dir():
        raise config.ConfigError(f"Android module directory does not exist: {target}")
    return target


def _redact_text(text: str, secrets: Iterable[str]) -> str:
    result = text
    for secret in sorted({value for value in secrets if value}, key=len, reverse=True):
        result = result.replace(secret, "<redacted>")
    return result


def _build_log_path(repo: Path) -> Path:
    directory = config.ensure_home() / "build-logs"
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    directory.chmod(0o700)
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", repo.name) or "android"
    path = directory / f"{int(time.time())}-{safe_name}.log"
    path.touch(mode=0o600, exist_ok=False)
    return path


def _run_gradle(
    repo: Path,
    tasks: list[str],
    env: dict[str, str],
    secrets: tuple[str, str],
) -> Path:
    gradlew = repo / "gradlew"
    if not gradlew.is_file():
        raise config.ConfigError(f"Gradle wrapper not found: {gradlew}")

    log_path = _build_log_path(repo)
    process = subprocess.Popen(
        [str(gradlew), "--no-daemon", *tasks],
        cwd=repo,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert process.stdout is not None
    with process.stdout, log_path.open("w", encoding="utf-8") as log:
        for line in process.stdout:
            log.write(_redact_text(line, secrets))
    log_path.chmod(0o600)
    code = process.wait()
    if code != 0:
        raise config.ConfigError(
            f"Gradle release bundle build failed with exit code {code}; sanitized log: {log_path}"
        )
    return log_path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bundle_signer_fingerprint(bundle: Path) -> str:
    verify = subprocess.run(
        [_java_tool("jarsigner"), "-verify", str(bundle)],
        capture_output=True,
        text=True,
        check=False,
    )
    verification_text = verify.stdout + "\n" + verify.stderr
    if verify.returncode != 0 or "jar verified" not in verification_text.lower():
        raise config.ConfigError(f"release bundle is not a verified signed JAR: {bundle}")

    cert = subprocess.run(
        [_java_tool("keytool"), "-printcert", "-jarfile", str(bundle)],
        capture_output=True,
        text=True,
        check=False,
    )
    if cert.returncode != 0:
        raise config.ConfigError(f"could not inspect release bundle signer: {bundle}")
    return _extract_sha256(cert.stdout + "\n" + cert.stderr)


def _artifacts_for_module(repo: Path, module: str) -> list[Path]:
    output = _module_dir(repo, module) / "build" / "outputs" / "bundle" / "release"
    bundles = sorted(output.glob("*.aab"))
    if not bundles:
        raise config.ConfigError(
            f"bundleRelease completed but no release AAB was found for :{module}"
        )
    return bundles


def build_signed_bundles(
    repo_path: str | Path,
    modules: list[str],
    *,
    identity_name: str = DEFAULT_IDENTITY,
) -> dict:
    """Build release AABs using Android Studio-compatible injected signing properties."""
    repo = Path(repo_path).expanduser().resolve()
    if not repo.is_dir():
        raise config.ConfigError(f"repository does not exist: {repo}")

    # Establish candidate trust before reading any Keychain secret.
    git_state = _git_state(repo)
    normalized_modules = [_normalize_module(module) for module in modules]
    if not normalized_modules:
        raise config.ConfigError("at least one Android application module is required")

    identity = load_identity(identity_name)
    status = identity_status(identity.name)
    if not status.get("ready"):
        raise config.ConfigError(
            f"Android signing identity {identity.name!r} is not ready: {status.get('status')}"
        )
    store_password, key_password = _identity_secrets(identity.name)
    secrets = (store_password, key_password)

    # Materialize a fresh bundle output while retaining Gradle caches/test evidence.
    for module in normalized_modules:
        output = _module_dir(repo, module) / "build" / "outputs" / "bundle" / "release"
        if output.exists():
            shutil.rmtree(output)

    env = os.environ.copy()
    env.update(
        {
            "ORG_GRADLE_PROJECT_android.injected.signing.store.file": identity.keystore_path,
            "ORG_GRADLE_PROJECT_android.injected.signing.store.password": store_password,
            "ORG_GRADLE_PROJECT_android.injected.signing.key.alias": identity.key_alias,
            "ORG_GRADLE_PROJECT_android.injected.signing.key.password": key_password,
        }
    )
    tasks = [f":{module}:bundleRelease" for module in normalized_modules]
    log_path = _run_gradle(repo, tasks, env, secrets)

    artifacts = []
    for module in normalized_modules:
        for bundle in _artifacts_for_module(repo, module):
            signer = _bundle_signer_fingerprint(bundle)
            if signer != identity.certificate_sha256:
                raise config.ConfigError(
                    f"release bundle signer does not match configured upload key: {bundle}"
                )
            artifacts.append(
                {
                    "module": module,
                    "aab_path": str(bundle),
                    "aab_sha256": _sha256(bundle),
                    "signing_certificate_sha256": signer,
                    "signing_identity": identity.name,
                    "signed": True,
                }
            )

    return {
        "status": "built",
        "repository": str(repo),
        **git_state,
        "gradle_tasks": tasks,
        "gradle_daemon": "disabled-for-signing-secret-isolation",
        "sanitized_log": str(log_path),
        "artifacts": artifacts,
    }

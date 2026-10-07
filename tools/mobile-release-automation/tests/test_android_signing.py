"""Security and behavior coverage for Keychain-backed Android signing."""

from __future__ import annotations

from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import android_signing, config  # noqa: E402


class AndroidSigningTest(unittest.TestCase):
    def test_configure_persists_only_non_secret_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir, patch.dict(
            os.environ, {"MRA_HOME": tempdir}
        ):
            keystore = Path(tempdir) / "upload.jks"
            keystore.write_bytes(b"fake")
            stored: dict[tuple[str, str], str] = {}
            with patch.object(
                android_signing, "_keystore_fingerprint", return_value="A1B2C3"
            ), patch.object(
                android_signing,
                "_set_secret",
                side_effect=lambda name, kind, value: stored.__setitem__((name, kind), value),
            ):
                result = android_signing.configure_identity(
                    "play-upload",
                    keystore,
                    "my-key-alias",
                    store_password="store-secret",
                    key_password="key-secret",
                )
            persisted = (Path(tempdir) / android_signing.ANDROID_SIGNING_CONFIG).read_text()

        self.assertEqual(result["certificate_sha256"], "A1B2C3")
        self.assertNotIn("store-secret", persisted)
        self.assertNotIn("key-secret", persisted)
        self.assertEqual(stored[("play-upload", "store-password")], "store-secret")
        self.assertEqual(stored[("play-upload", "key-password")], "key-secret")

    def test_status_never_returns_passwords(self) -> None:
        identity = android_signing.SigningIdentity(
            name="play-upload",
            keystore_path="/tmp/upload.jks",
            key_alias="alias",
            certificate_sha256="AABB",
        )
        with patch.object(android_signing, "load_identity", return_value=identity), patch.object(
            Path, "is_file", return_value=True
        ), patch.object(
            android_signing,
            "_get_secret",
            side_effect=["store-secret", "key-secret"],
        ), patch.object(
            android_signing, "_keystore_fingerprint", return_value="AABB"
        ):
            result = android_signing.identity_status("play-upload")

        rendered = repr(result)
        self.assertTrue(result["ready"])
        self.assertNotIn("store-secret", rendered)
        self.assertNotIn("key-secret", rendered)

    def test_dirty_repo_blocks_before_secret_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            repo = Path(tempdir)
            with patch.object(
                android_signing,
                "_git_state",
                side_effect=config.ConfigError("dirty worktree"),
            ), patch.object(android_signing, "_identity_secrets") as secrets:
                with self.assertRaises(config.ConfigError):
                    android_signing.build_signed_bundles(repo, ["app"])
        secrets.assert_not_called()

    def test_gradle_log_redacts_signing_passwords(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir, patch.dict(
            os.environ, {"MRA_HOME": str(Path(tempdir) / "mra")}
        ):
            repo = Path(tempdir) / "repo"
            repo.mkdir()
            gradlew = repo / "gradlew"
            gradlew.write_text(
                "#!/usr/bin/env python3\n"
                "import os\n"
                'print(os.environ["ORG_GRADLE_PROJECT_android.injected.signing.store.password"])\n'
                'print(os.environ["ORG_GRADLE_PROJECT_android.injected.signing.key.password"])\n',
                encoding="utf-8",
            )
            gradlew.chmod(0o700)
            env = os.environ.copy()
            env["ORG_GRADLE_PROJECT_android.injected.signing.store.password"] = "store-secret"
            env["ORG_GRADLE_PROJECT_android.injected.signing.key.password"] = "key-secret"
            log = android_signing._run_gradle(
                repo,
                [":app:bundleRelease"],
                env,
                ("store-secret", "key-secret"),
            )
            text = log.read_text(encoding="utf-8")

        self.assertNotIn("store-secret", text)
        self.assertNotIn("key-secret", text)
        self.assertGreaterEqual(text.count("<redacted>"), 2)

    def test_module_names_cannot_escape_repository(self) -> None:
        for value in ("../app", "app/../../tmp", ""):
            with self.subTest(value=value), self.assertRaises(config.ConfigError):
                android_signing._normalize_module(value)


if __name__ == "__main__":
    unittest.main()

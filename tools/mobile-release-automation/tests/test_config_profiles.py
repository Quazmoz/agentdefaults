"""Profile reconciliation must preserve secrets and expose only public identifiers."""

from __future__ import annotations

from pathlib import Path
import os
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import config  # noqa: E402


class ProfileIdentifierUpdateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.previous_home = os.environ.get("MRA_HOME")
        os.environ["MRA_HOME"] = self.tempdir.name
        config.save_profile(
            config.Profile(
                slug="motionguard",
                package_name="com.quazmoz.motionguard",
                revenuecat_project_id="proj_old",
                revenuecat_secret_id="4adde104-2d89-44ba-9808-b4c40115849c",
            )
        )

    def tearDown(self) -> None:
        if self.previous_home is None:
            os.environ.pop("MRA_HOME", None)
        else:
            os.environ["MRA_HOME"] = self.previous_home
        self.tempdir.cleanup()

    def test_update_preserves_secret_binding(self) -> None:
        updated = config.update_profile_identifiers(
            "motionguard",
            admob_publisher_id="pub-1229681629360299",
            admob_app_id="ca-app-pub-1229681629360299~7070793420",
            revenuecat_project_id="projd9eed903",
            revenuecat_app_id="app7ddcf92588",
        )
        self.assertEqual(updated.revenuecat_secret_id, "4adde104-2d89-44ba-9808-b4c40115849c")
        self.assertEqual(updated.revenuecat_app_id, "app7ddcf92588")

    def test_public_profile_excludes_secret_reference(self) -> None:
        public = config.public_profile(config.load_profile("motionguard"))
        self.assertNotIn("revenuecat_secret_id", public)
        self.assertEqual(public["package_name"], "com.quazmoz.motionguard")

    def test_update_refuses_unknown_profile(self) -> None:
        with self.assertRaises(config.ConfigError):
            config.update_profile_identifiers("missing", admob_app_id="ca-app-pub-1~2")

    def test_update_refuses_blank_identifier(self) -> None:
        with self.assertRaises(config.ConfigError):
            config.update_profile_identifiers("motionguard", revenuecat_app_id="   ")

    def test_update_requires_at_least_one_identifier(self) -> None:
        with self.assertRaises(config.ConfigError):
            config.update_profile_identifiers("motionguard")


if __name__ == "__main__":
    unittest.main()

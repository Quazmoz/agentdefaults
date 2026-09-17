"""Desired-state planning tests that do not require live vendor credentials."""

from __future__ import annotations

from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import config, reconcile  # noqa: E402


class ReconcilePlanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"MRA_HOME": self.tempdir.name})
        self.env.start()
        config.save_profile(
            config.Profile(
                slug="example",
                package_name="com.example.app",
                admob_app_id="ca-app-pub-1~2",
                admob_publisher_id="pub-1",
                revenuecat_project_id="proj-1",
                revenuecat_app_id="app-1",
                revenuecat_secret_id="00000000-0000-0000-0000-000000000001",
            )
        )

    def tearDown(self) -> None:
        self.env.stop()
        self.tempdir.cleanup()

    @staticmethod
    def snapshot() -> dict:
        return {
            "profile": {},
            "play": {
                "status": "ready",
                "data": {
                    "listings": [
                        {
                            "language": "en-US",
                            "title": "Old title",
                            "shortDescription": "Short",
                            "fullDescription": "Full",
                        }
                    ]
                },
            },
            "revenuecat": {
                "status": "ready",
                "data": {
                    "projects": [{"id": "proj-1"}],
                    "apps": [
                        {
                            "id": "app-1",
                            "play_store": {"package_name": "com.example.app"},
                        }
                    ],
                    "products": [],
                    "entitlements": [],
                    "offerings": [],
                    "webhooks": [],
                },
            },
            "admob": {
                "status": "ready",
                "data": {
                    "apps": [
                        {
                            "appId": "ca-app-pub-1~2",
                            "linkedAppInfo": {"appStoreId": "com.example.app"},
                        }
                    ],
                    "ad_units": [],
                    "approval": {},
                    "capabilities": {},
                },
            },
        }

    def test_plan_spans_all_three_platforms(self) -> None:
        desired = {
            "play": {
                "listing": {
                    "language": "en-US",
                    "title": "New title",
                    "short_description": "Short",
                    "full_description": "Full",
                }
            },
            "revenuecat": {
                "project": {"name": "Example"},
                "app": {"name": "Example Android"},
                "products": [
                    {
                        "store_identifier": "lifetime",
                        "type": "non_consumable",
                        "display_name": "Lifetime",
                    }
                ],
            },
            "admob": {
                "app": {
                    "display_name": "Example",
                    "linked_package": "com.example.app",
                },
                "ad_units": [
                    {"display_name": "rewarded_unlock", "format": "REWARDED"}
                ],
            },
        }
        result = reconcile.plan_profile("example", desired, snapshot=self.snapshot())
        actions = {item["id"]: item for item in result["actions"]}

        self.assertEqual(actions["play.listing.en-US"]["status"], "needed")
        self.assertEqual(actions["revenuecat.project"]["status"], "satisfied")
        self.assertEqual(actions["revenuecat.app"]["status"], "satisfied")
        self.assertEqual(actions["revenuecat.product.lifetime"]["status"], "needed")
        self.assertEqual(actions["admob.app"]["status"], "satisfied")
        self.assertEqual(actions["admob.ad_unit.rewarded_unlock"]["status"], "needed")
        self.assertFalse(result["converged"])

    def test_literal_secret_fields_are_rejected(self) -> None:
        for desired in (
            {"revenuecat": {"webhooks": [{"authorization_header": "Bearer secret"}]}},
            {"api_key": "sk_secret"},
            {"nested": {"private_key": "canary"}},
        ):
            with self.subTest(desired=desired):
                with self.assertRaises(reconcile.ReconcileError):
                    reconcile.validate_desired_state(desired)

    def test_secret_reference_is_allowed(self) -> None:
        reconcile.validate_desired_state(
            {
                "revenuecat": {
                    "webhooks": [
                        {
                            "name": "events",
                            "url": "https://example.com/hook",
                            "authorization_header_secret_id": "00000000-0000-0000-0000-000000000002",
                        }
                    ]
                }
            }
        )


if __name__ == "__main__":
    unittest.main()

"""Desired-state planning tests that do not require live vendor credentials."""

from __future__ import annotations

from pathlib import Path
import os
import sys
import tempfile
import json
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
                    "wiring": {"entitlements": [], "offerings": []},
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

    @staticmethod
    def wired_snapshot() -> dict:
        snapshot = ReconcilePlanTest.snapshot()
        snapshot["revenuecat"]["data"].update(
            {
                "products": [
                    {
                        "id": "prod-1",
                        "store_identifier": "lifetime",
                        "type": "non_consumable",
                    }
                ],
                "entitlements": [
                    {"id": "ent-1", "lookup_key": "pro", "display_name": "Pro"}
                ],
                "offerings": [
                    {
                        "id": "ofr-1",
                        "lookup_key": "default",
                        "display_name": "Default",
                        "is_current": False,
                    }
                ],
                "wiring": {
                    "entitlements": [
                        {
                            "id": "ent-1",
                            "lookup_key": "pro",
                            "products": [],
                        }
                    ],
                    "offerings": [
                        {
                            "id": "ofr-1",
                            "lookup_key": "default",
                            "is_current": False,
                            "packages": [
                                {
                                    "id": "pkg-1",
                                    "lookup_key": "$rc_lifetime",
                                    "display_name": "Lifetime",
                                    "products": [],
                                }
                            ],
                        }
                    ],
                },
            }
        )
        return snapshot

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

    def test_revenuecat_graph_plans_current_offering_and_missing_wiring(self) -> None:
        desired = {
            "revenuecat": {
                "entitlements": [
                    {
                        "lookup_key": "pro",
                        "display_name": "Pro",
                        "products": ["lifetime"],
                    }
                ],
                "offerings": [
                    {
                        "lookup_key": "default",
                        "display_name": "Default",
                        "is_current": True,
                        "packages": [
                            {
                                "lookup_key": "$rc_lifetime",
                                "display_name": "Lifetime",
                                "products": [
                                    {
                                        "store_identifier": "lifetime",
                                        "eligibility_criteria": "all",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        }
        result = reconcile.plan_profile("example", desired, snapshot=self.wired_snapshot())
        actions = {item["id"]: item for item in result["actions"]}

        self.assertEqual(actions["revenuecat.entitlement.pro"]["status"], "satisfied")
        entitlement_wiring = actions["revenuecat.entitlement.pro.products"]
        self.assertEqual(entitlement_wiring["status"], "needed")
        self.assertEqual(entitlement_wiring["risk"], "high")
        self.assertEqual(entitlement_wiring["params"]["product_ids"], ["prod-1"])

        offering = actions["revenuecat.offering.default"]
        self.assertEqual(offering["status"], "needed")
        self.assertEqual(offering["operation"], "update_offering")
        self.assertEqual(offering["risk"], "high")

        package = actions["revenuecat.offering.default.package.$rc_lifetime"]
        self.assertEqual(package["status"], "satisfied")
        package_wiring = actions[
            "revenuecat.offering.default.package.$rc_lifetime.products"
        ]
        self.assertEqual(package_wiring["status"], "needed")
        self.assertEqual(package_wiring["risk"], "high")
        self.assertEqual(
            package_wiring["params"]["products"],
            [{"product_id": "prod-1", "eligibility_criteria": "all"}],
        )

    def test_existing_product_links_are_additive_not_destructively_replaced(self) -> None:
        snapshot = self.wired_snapshot()
        snapshot["revenuecat"]["data"]["wiring"]["entitlements"][0]["products"] = [
            {"id": "legacy-product"},
            {"id": "prod-1"},
        ]
        # RevenueCat returns package products as wrappers, not flat product objects.
        snapshot["revenuecat"]["data"]["wiring"]["offerings"][0]["packages"][0][
            "products"
        ] = [
            {"eligibility_criteria": "all", "product": {"id": "legacy-product"}},
            {"eligibility_criteria": "all", "product": {"id": "prod-1"}},
        ]
        desired = {
            "revenuecat": {
                "entitlements": [
                    {"lookup_key": "pro", "display_name": "Pro", "products": ["lifetime"]}
                ],
                "offerings": [
                    {
                        "lookup_key": "default",
                        "display_name": "Default",
                        "packages": [
                            {
                                "lookup_key": "$rc_lifetime",
                                "display_name": "Lifetime",
                                "products": ["lifetime"],
                            }
                        ],
                    }
                ],
            }
        }
        result = reconcile.plan_profile("example", desired, snapshot=snapshot)
        actions = {item["id"]: item for item in result["actions"]}
        self.assertEqual(
            actions["revenuecat.entitlement.pro.products"]["status"], "satisfied"
        )
        self.assertEqual(
            actions["revenuecat.offering.default.package.$rc_lifetime.products"]["status"],
            "satisfied",
        )

    def test_attached_package_product_in_real_wrapper_shape_is_satisfied(self) -> None:
        """RevenueCat wraps a package product as {eligibility_criteria, product}.

        Reading a flat item["id"] never matched, so attach_products_to_package
        stayed "needed" forever: a fully wired project never converged and every
        mra_apply re-fired a high-risk approval to re-attach what was there.
        """
        snapshot = self.wired_snapshot()
        snapshot["revenuecat"]["data"]["wiring"]["offerings"][0]["packages"][0][
            "products"
        ] = [{"eligibility_criteria": "google_sdk_ge_6", "product": {"id": "prod-1"}}]
        desired = {
            "revenuecat": {
                "offerings": [
                    {
                        "lookup_key": "default",
                        "display_name": "Default",
                        "packages": [
                            {
                                "lookup_key": "$rc_lifetime",
                                "display_name": "Lifetime",
                                "products": [
                                    {
                                        "store_identifier": "lifetime",
                                        "eligibility_criteria": "google_sdk_ge_6",
                                    }
                                ],
                            }
                        ],
                    }
                ]
            }
        }
        actions = {
            item["id"]: item
            for item in reconcile.plan_profile("example", desired, snapshot=snapshot)["actions"]
        }
        self.assertEqual(
            actions["revenuecat.offering.default.package.$rc_lifetime.products"]["status"],
            "satisfied",
        )

        # A genuine eligibility difference must still be reported, not absorbed.
        drifted = json.loads(json.dumps(desired).replace("google_sdk_ge_6", "all"))
        drifted_actions = {
            item["id"]: item
            for item in reconcile.plan_profile("example", drifted, snapshot=snapshot)["actions"]
        }
        self.assertEqual(
            drifted_actions["revenuecat.offering.default.package.$rc_lifetime.products"]["status"],
            "needed",
        )

    def test_invalid_package_eligibility_is_rejected(self) -> None:
        desired = {
            "revenuecat": {
                "offerings": [
                    {
                        "lookup_key": "default",
                        "display_name": "Default",
                        "packages": [
                            {
                                "lookup_key": "$rc_lifetime",
                                "display_name": "Lifetime",
                                "products": [
                                    {
                                        "store_identifier": "lifetime",
                                        "eligibility_criteria": "future_sdk_only",
                                    }
                                ],
                            }
                        ],
                    }
                ]
            }
        }
        with self.assertRaises(reconcile.ReconcileError):
            reconcile.plan_profile("example", desired, snapshot=self.wired_snapshot())

    def test_unrelated_vendor_error_does_not_block_partial_desired_state(self) -> None:
        snapshot = self.snapshot()
        snapshot["play"]["data"]["listings"][0]["title"] = "Old title"
        snapshot["admob"] = {
            "status": "error",
            "error_type": "AdMobError",
            "detail": "OAuth unavailable",
        }
        desired = {
            "play": {
                "listing": {
                    "language": "en-US",
                    "title": "Old title",
                    "short_description": "Short",
                    "full_description": "Full",
                }
            }
        }
        result = reconcile.plan_profile("example", desired, snapshot=snapshot)
        self.assertTrue(result["converged"])
        self.assertEqual(result["snapshot_errors"], {})

    def test_package_only_snapshot_does_not_probe_unconfigured_vendors(self) -> None:
        config.save_profile(
            config.Profile(slug="play-only", package_name="com.example.playonly")
        )
        with patch.object(
            reconcile,
            "_safe",
            return_value={"status": "ready", "data": {}},
        ) as safe:
            snapshot = reconcile.snapshot_profile("play-only")

        self.assertEqual(safe.call_count, 1)
        self.assertEqual(snapshot["play"]["status"], "ready")
        self.assertEqual(snapshot["revenuecat"]["status"], "not_configured")
        self.assertEqual(snapshot["admob"]["status"], "not_configured")

    def test_requested_unbound_vendors_can_still_be_discovered(self) -> None:
        config.save_profile(
            config.Profile(slug="bootstrap", package_name="com.example.bootstrap")
        )
        with patch.object(
            reconcile,
            "_safe",
            return_value={"status": "ready", "data": {}},
        ) as safe:
            snapshot = reconcile.snapshot_profile(
                "bootstrap", platforms={"revenuecat", "admob"}
            )

        self.assertEqual(safe.call_count, 2)
        self.assertEqual(snapshot["play"]["status"], "not_configured")
        self.assertEqual(snapshot["revenuecat"]["status"], "ready")
        self.assertEqual(snapshot["admob"]["status"], "ready")

    def test_plan_requests_only_vendors_named_in_desired_state(self) -> None:
        desired = {"play": {}}
        with patch.object(
            reconcile,
            "snapshot_profile",
            return_value=self.snapshot(),
        ) as snapshot_profile:
            reconcile.plan_profile("example", desired)

        snapshot_profile.assert_called_once_with("example", platforms={"play"})

    def test_explicit_null_admob_linking_requests_manual_app(self) -> None:
        snapshot = self.snapshot()
        snapshot["admob"]["data"]["apps"] = []
        desired = {
            "admob": {
                "app": {
                    "display_name": "Example Manual",
                    "platform": "ANDROID",
                    "linked_package": None,
                }
            }
        }
        result = reconcile.plan_profile("example", desired, snapshot=snapshot)
        action = result["actions"][0]
        self.assertEqual(action["status"], "needed")
        self.assertEqual(action["risk"], "contained")
        self.assertIsNone(action["params"]["app_store_id"])

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

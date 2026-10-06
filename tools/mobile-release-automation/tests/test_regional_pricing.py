"""Regional pricing planning, integrity, drift, and read-back verification."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import play, regional_pricing  # noqa: E402
from tests.fakes import FakeResponse, FakeSession  # noqa: E402

PACKAGE = "com.example.app"
PRODUCT = "pro"
OPTION = "buy"


def money(currency: str, units: str, nanos: int = 0) -> dict:
    result = {"currencyCode": currency, "units": units}
    if nanos:
        result["nanos"] = nanos
    return result


def initial_product() -> dict:
    return {
        "packageName": PACKAGE,
        "productId": PRODUCT,
        "purchaseOptions": [
            {
                "purchaseOptionId": OPTION,
                "state": "ACTIVE",
                "buyOption": {"legacyCompatible": True},
                "regionalPricingAndAvailabilityConfigs": [
                    {
                        "regionCode": "US",
                        "availability": "AVAILABLE",
                        "price": money("USD", "2", 490_000_000),
                    },
                    {
                        "regionCode": "IN",
                        "availability": "AVAILABLE",
                        "price": money("INR", "249"),
                    },
                    {
                        "regionCode": "GB",
                        "availability": "AVAILABLE",
                        "price": money("GBP", "2", 190_000_000),
                    },
                ],
            }
        ],
        "regionsVersion": {"version": "2026/10"},
    }


class StatefulPlay:
    def __init__(self) -> None:
        self.product = initial_product()

        def get_product(**_):
            return FakeResponse(200, deepcopy(self.product))

        def convert(**kwargs):
            request_price = kwargs["json"]["price"]
            # Planning uses the reduced USD reference. Apply preflight uses the
            # original reference; only the regionVersion matters in that call.
            if request_price.get("units") == "0":
                converted = {"IN": {"regionCode": "IN", "price": money("INR", "79")}}
            else:
                converted = {"IN": {"regionCode": "IN", "price": money("INR", "249")}}
            return FakeResponse(
                200,
                {
                    "convertedRegionPrices": converted,
                    "regionVersion": {"version": "2026/10"},
                },
            )

        def patch(**kwargs):
            body = kwargs["json"]
            self.product["purchaseOptions"] = deepcopy(body["purchaseOptions"])
            # The GET surface returns state even though patch must omit it.
            for option in self.product["purchaseOptions"]:
                option["state"] = "ACTIVE"
            return FakeResponse(200, deepcopy(self.product))

        self.session = FakeSession(
            {
                ("GET", "/oneTimeProducts/pro"): get_product,
                ("POST", "/pricing:convertRegionPrices"): convert,
                ("PATCH", "/onetimeproducts/pro"): patch,
            }
        )
        self.client = play.PlayClient(PACKAGE, session=self.session)


class RegionalPricingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.previous = os.environ.get("MRA_HOME")
        os.environ["MRA_HOME"] = self.tempdir.name
        self.live = StatefulPlay()

    def tearDown(self) -> None:
        if self.previous is None:
            os.environ.pop("MRA_HOME", None)
        else:
            os.environ["MRA_HOME"] = self.previous
        self.tempdir.cleanup()

    def plan(self) -> dict:
        return regional_pricing.create_one_time_product_plan(
            PACKAGE,
            PRODUCT,
            OPTION,
            profile="example",
            target_regions=["IN"],
            client=self.live.client,
        )

    def test_plan_is_read_only_persisted_and_reviewable(self) -> None:
        plan = self.plan()
        self.assertEqual(plan["status"], "planned")
        self.assertEqual(len(plan["changes"]), 1)
        change = plan["changes"][0]
        self.assertEqual(change["region_code"], "IN")
        self.assertEqual(change["factor"], "0.35")
        self.assertEqual(change["current_price"], money("INR", "249"))
        self.assertEqual(change["proposed_price"], money("INR", "79"))
        self.assertFalse(self.live.session.urls("PATCH"))

        path = Path(plan["plan_path"])
        self.assertTrue(path.is_file())
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(regional_pricing.load_plan(plan["plan_id"])["plan_id"], plan["plan_id"])

    def test_apply_uses_plan_id_only_and_verifies_read_back(self) -> None:
        plan = self.plan()
        result = regional_pricing.apply_one_time_product_plan(
            PACKAGE,
            plan["plan_id"],
            profile="example",
            client=self.live.client,
        )
        self.assertEqual(result["status"], "applied")
        self.assertTrue(result["verified"])
        self.assertEqual(
            regional_pricing._regions(  # noqa: SLF001 - verification helper
                regional_pricing._purchase_option(  # noqa: SLF001
                    self.live.product, OPTION
                )
            )["IN"]["price"],
            money("INR", "79"),
        )
        patch = self.live.session.body_for("PATCH", "/onetimeproducts/pro")
        self.assertNotIn("state", patch["purchaseOptions"][0])

    def test_stale_source_state_refuses_to_apply(self) -> None:
        plan = self.plan()
        self.live.product["purchaseOptions"][0]["regionalPricingAndAvailabilityConfigs"][1][
            "price"
        ] = money("INR", "199")
        with self.assertRaises(regional_pricing.PricingError) as caught:
            regional_pricing.apply_one_time_product_plan(
                PACKAGE,
                plan["plan_id"],
                profile="example",
                client=self.live.client,
            )
        self.assertIn("stale", str(caught.exception))
        self.assertFalse(self.live.session.urls("PATCH"))

    def test_read_back_rejects_unapproved_purchase_option_changes(self) -> None:
        plan = self.plan()
        patch = self.live.client.upsert_one_time_product
        before = deepcopy(self.live.product)
        for drift in ("US", "GB", "availability", "buy_option"):
            with self.subTest(drift=drift):
                self.live.product = deepcopy(before)

                def patch_with_drift(*args, **kwargs):
                    result = patch(*args, **kwargs)
                    option = self.live.product["purchaseOptions"][0]
                    regions = option["regionalPricingAndAvailabilityConfigs"]
                    if drift in ("US", "GB"):
                        protected = next(r for r in regions if r["regionCode"] == drift)
                        protected["price"] = money(protected["price"]["currencyCode"], "1")
                    elif drift == "availability":
                        regions[1]["availability"] = "NO_LONGER_AVAILABLE"
                    else:
                        option["buyOption"]["legacyCompatible"] = False
                    return result

                self.live.client.upsert_one_time_product = patch_with_drift
                with self.assertRaisesRegex(regional_pricing.PricingError, "read-back"):
                    regional_pricing.apply_one_time_product_plan(
                        PACKAGE, plan["plan_id"], profile="example", client=self.live.client
                    )

    def test_already_applied_rejects_unapproved_protected_price(self) -> None:
        plan = self.plan()
        regions = self.live.product["purchaseOptions"][0]["regionalPricingAndAvailabilityConfigs"]
        regions[1]["price"] = deepcopy(plan["changes"][0]["proposed_price"])
        regions[0]["price"] = money("USD", "1")
        with self.assertRaisesRegex(regional_pricing.PricingError, "stale"):
            regional_pricing.apply_one_time_product_plan(
                PACKAGE, plan["plan_id"], profile="example", client=self.live.client
            )
        self.assertFalse(self.live.session.urls("PATCH"))

    def test_already_applied_verifies_preserved_purchase_option_state(self) -> None:
        plan = self.plan()
        regions = self.live.product["purchaseOptions"][0]["regionalPricingAndAvailabilityConfigs"]
        regions[1]["price"] = deepcopy(plan["changes"][0]["proposed_price"])
        result = regional_pricing.apply_one_time_product_plan(
            PACKAGE, plan["plan_id"], profile="example", client=self.live.client
        )
        self.assertEqual(result["status"], "already_applied")
        self.assertTrue(result["verified"])
        self.assertFalse(self.live.session.urls("PATCH"))

    def test_tampered_plan_fails_integrity_check(self) -> None:
        plan = self.plan()
        path = Path(plan["plan_path"])
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["changes"][0]["proposed_price"] = money("INR", "1")
        path.write_text(json.dumps(payload), encoding="utf-8")
        path.chmod(0o600)
        with self.assertRaises(regional_pricing.PricingError) as caught:
            regional_pricing.load_plan(plan["plan_id"])
        self.assertIn("integrity", str(caught.exception))

    def test_reference_market_cannot_be_targeted(self) -> None:
        with self.assertRaises(regional_pricing.PricingError):
            regional_pricing.create_one_time_product_plan(
                PACKAGE,
                PRODUCT,
                OPTION,
                target_regions=["US"],
                client=self.live.client,
            )


if __name__ == "__main__":
    unittest.main()

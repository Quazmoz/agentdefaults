"""Google Play catalog reads use the current monetization publishing API."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import play  # noqa: E402
from tests.fakes import FakeResponse, FakeSession  # noqa: E402

PACKAGE = "com.example.app"


class CatalogReadTest(unittest.TestCase):
    def test_one_time_products_use_new_endpoint_and_follow_pagination(self) -> None:
        def page(**kwargs):
            token = kwargs.get("params", {}).get("pageToken")
            if token == "next-1":
                return FakeResponse(
                    200,
                    {"oneTimeProducts": [{"productId": "pro"}]},
                )
            return FakeResponse(
                200,
                {
                    "oneTimeProducts": [{"productId": "remove_ads"}],
                    "nextPageToken": "next-1",
                },
            )

        session = FakeSession({("GET", "/oneTimeProducts"): page})
        client = play.PlayClient(PACKAGE, session=session)

        products = client.list_in_app_products()

        self.assertEqual(
            [product["productId"] for product in products],
            ["remove_ads", "pro"],
        )
        self.assertEqual(len(session.calls), 2)
        self.assertTrue(all("/oneTimeProducts" in call["url"] for call in session.calls))
        self.assertTrue(all("/inappproducts" not in call["url"] for call in session.calls))
        self.assertEqual(session.calls[0]["params"], {"pageSize": 1000})
        self.assertEqual(
            session.calls[1]["params"],
            {"pageSize": 1000, "pageToken": "next-1"},
        )

    def test_subscriptions_follow_the_same_pagination_contract(self) -> None:
        def page(**kwargs):
            token = kwargs.get("params", {}).get("pageToken")
            if token == "next-2":
                return FakeResponse(200, {"subscriptions": [{"productId": "annual"}]})
            return FakeResponse(
                200,
                {
                    "subscriptions": [{"productId": "monthly"}],
                    "nextPageToken": "next-2",
                },
            )

        session = FakeSession({("GET", "/subscriptions"): page})
        client = play.PlayClient(PACKAGE, session=session)

        subscriptions = client.list_subscriptions()

        self.assertEqual(
            [subscription["productId"] for subscription in subscriptions],
            ["monthly", "annual"],
        )
        self.assertEqual(len(session.calls), 2)
        self.assertEqual(session.calls[0]["params"], {"pageSize": 1000})
        self.assertEqual(
            session.calls[1]["params"],
            {"pageSize": 1000, "pageToken": "next-2"},
        )


if __name__ == "__main__":
    unittest.main()


class OneTimeProductUpsertTest(unittest.TestCase):
    """Google rejects updateMask "*" with 400 Invalid update_mask: [*]."""

    def upsert(self, body: dict, **kwargs):
        session = FakeSession(
            {("PATCH", "/onetimeproducts/pro"): lambda **_: FakeResponse(200, {"productId": "pro"})}
        )
        client = play.PlayClient(PACKAGE, session=session)
        client.upsert_one_time_product("pro", body, "2025/03", **kwargs)
        return session.calls[-1]

    def test_mask_is_derived_from_supplied_fields_not_a_wildcard(self) -> None:
        call = self.upsert({"listings": [], "purchaseOptions": []})
        self.assertEqual(call["params"]["updateMask"], "listings,purchaseOptions")
        self.assertEqual(call["params"]["regionsVersion.version"], "2025/03")

    def test_identity_fields_never_enter_the_mask(self) -> None:
        # packageName/productId are identity and regionsVersion is output-only;
        # masking any of them would be rejected or would clear real state.
        call = self.upsert(
            {"listings": [], "packageName": "x", "productId": "y", "regionsVersion": {"version": "z"}}
        )
        self.assertEqual(call["params"]["updateMask"], "listings")
        self.assertNotIn("regionsVersion", call["json"])

    def test_explicit_mask_is_preserved(self) -> None:
        call = self.upsert({"listings": []}, update_mask="listings,taxAndComplianceSettings")
        self.assertEqual(call["params"]["updateMask"], "listings,taxAndComplianceSettings")

    def test_body_with_no_updatable_field_is_refused_before_the_request(self) -> None:
        with self.assertRaises(play.PlayError):
            self.upsert({})


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

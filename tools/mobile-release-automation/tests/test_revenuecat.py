"""RevenueCat v2 request shaping and pagination."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import revenuecat  # noqa: E402
from tests.fakes import FakeResponse, FakeSession, fail, ok  # noqa: E402

PROJECT = "proj_123"


def client(routes: dict) -> tuple[revenuecat.RevenueCatClient, FakeSession]:
    session = FakeSession(routes)
    return revenuecat.RevenueCatClient(api_key="sk_test", session=session), session


class AuthTest(unittest.TestCase):
    def test_key_is_sent_as_a_bearer_token(self) -> None:
        _, session = client({})
        self.assertEqual(session.headers["Authorization"], "Bearer sk_test")


class PaginationTest(unittest.TestCase):
    def test_follows_pages_until_next_page_is_absent(self) -> None:
        pages = [
            FakeResponse(200, {"items": [{"id": "a"}, {"id": "b"}], "next_page": "/more"}),
            FakeResponse(200, {"items": [{"id": "c"}], "next_page": None}),
        ]
        calls: list[dict] = []

        def handler(**kwargs):
            calls.append(kwargs)
            return pages[len(calls) - 1]

        api, _ = client({("GET", "/products"): handler})
        products = api.list_products(PROJECT)

        self.assertEqual([item["id"] for item in products], ["a", "b", "c"])
        self.assertEqual(calls[1]["params"]["starting_after"], "b")

    def test_empty_first_page_stops_immediately(self) -> None:
        api, session = client({("GET", "/products"): ok({"items": [], "next_page": "/more"})})
        self.assertEqual(api.list_products(PROJECT), [])
        self.assertEqual(len(session.calls), 1)


class CreateAppTest(unittest.TestCase):
    def test_play_app_body_carries_package_and_credentials(self) -> None:
        api, session = client({("POST", "/apps"): ok({"id": "app_1"})})
        api.create_play_app(PROJECT, "Example", "com.example.app", '{"type":"service_account"}')

        body = session.body_for("POST", "/apps")
        self.assertEqual(body["type"], "play_store")
        self.assertEqual(body["play_store"]["package_name"], "com.example.app")
        self.assertEqual(
            body["play_store"]["play_service_account_credentials_json"],
            '{"type":"service_account"}',
        )

    def test_url_targets_the_project_scope(self) -> None:
        api, session = client({("POST", "/apps"): ok({"id": "app_1"})})
        api.create_play_app(PROJECT, "Example", "com.example.app", "{}")
        self.assertIn(f"/v2/projects/{PROJECT}/apps", session.urls("POST")[0])


class CreateProductTest(unittest.TestCase):
    def test_rejects_unknown_product_type_before_calling_the_api(self) -> None:
        api, session = client({})
        with self.assertRaises(revenuecat.RevenueCatError):
            api.create_product(PROJECT, "app_1", "premium_monthly", "lifetime")
        self.assertEqual(session.calls, [])

    def test_display_name_is_omitted_when_not_supplied(self) -> None:
        api, session = client({("POST", "/products"): ok({"id": "prod_1"})})
        api.create_product(PROJECT, "app_1", "premium_monthly", "subscription")
        self.assertNotIn("display_name", session.body_for("POST", "/products"))


class AttachTest(unittest.TestCase):
    def test_entitlement_attach_uses_product_ids(self) -> None:
        api, session = client({("POST", "/actions/attach_products"): ok({})})
        api.attach_products_to_entitlement(PROJECT, "ent_1", ["prod_1", "prod_2"])
        body = session.body_for("POST", "/actions/attach_products")
        self.assertEqual(body, {"product_ids": ["prod_1", "prod_2"]})

    def test_package_attach_uses_product_objects(self) -> None:
        api, session = client({("POST", "/actions/attach_products"): ok({})})
        api.attach_products_to_package(
            PROJECT, "pkg_1", [{"product_id": "prod_1", "eligibility_criteria": "all"}]
        )
        body = session.body_for("POST", "/actions/attach_products")
        self.assertEqual(body["products"][0]["product_id"], "prod_1")


class ErrorTest(unittest.TestCase):
    def test_http_error_includes_status_and_body(self) -> None:
        api, _ = client({("GET", "/products"): fail(401, {"message": "bad key"})})
        with self.assertRaises(revenuecat.RevenueCatError) as caught:
            api.list_products(PROJECT)
        self.assertIn("401", str(caught.exception))
        self.assertIn("bad key", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

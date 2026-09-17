"""RevenueCat project/webhook management and secret-boundary tests."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import redaction, revenuecat, revenuecat_management  # noqa: E402
from tests.fakes import FakeSession, ok  # noqa: E402

PROJECT = "proj_example"
WEBHOOK = "wh_example"


def management(routes: dict) -> tuple[revenuecat_management.RevenueCatManagementClient, FakeSession]:
    session = FakeSession(routes)
    client = revenuecat.RevenueCatClient(api_key="sk_test_canary", session=session)
    return revenuecat_management.RevenueCatManagementClient(client), session


class ProjectTest(unittest.TestCase):
    def test_create_project_uses_documented_endpoint(self) -> None:
        api, session = management({("POST", "/projects"): ok({"id": "proj_new", "name": "New App"})})
        result = api.create_project(" New App ")
        self.assertEqual(result["id"], "proj_new")
        self.assertEqual(session.body_for("POST", "/projects"), {"name": "New App"})


class OfferingTest(unittest.TestCase):
    def test_current_offering_update_uses_offering_resource(self) -> None:
        api, session = management(
            {
                ("POST", "/offerings/ofr_1"): ok(
                    {"id": "ofr_1", "is_current": True}
                )
            }
        )
        result = api.update_offering(PROJECT, "ofr_1", is_current=True)
        self.assertTrue(result["is_current"])
        self.assertEqual(
            session.body_for("POST", "/offerings/ofr_1"), {"is_current": True}
        )

    def test_empty_offering_update_is_rejected(self) -> None:
        api, session = management({})
        with self.assertRaises(revenuecat.RevenueCatError):
            api.update_offering(PROJECT, "ofr_1")
        self.assertEqual(session.calls, [])


class WebhookTest(unittest.TestCase):
    def test_create_never_returns_signing_secret(self) -> None:
        api, session = management(
            {
                ("POST", "/integrations/webhooks"): ok(
                    {
                        "id": WEBHOOK,
                        "url": "https://example.com/hook",
                        "signing_secret": "signing-canary",
                    }
                )
            }
        )
        result = api.create_webhook(
            PROJECT,
            name="Events",
            url="https://example.com/hook",
            authorization_header="Bearer auth-canary",
            environment="production",
        )
        self.assertEqual(result["signing_secret"], redaction.REDACTED)
        body = session.body_for("POST", "/integrations/webhooks")
        self.assertEqual(body["authorization_header"], "Bearer auth-canary")
        self.assertNotIn("auth-canary", str(result))

    def test_list_redacts_vendor_signing_secrets(self) -> None:
        api, _ = management(
            {
                ("GET", "/integrations/webhooks"): ok(
                    {
                        "items": [
                            {
                                "id": WEBHOOK,
                                "signing_secret": "signing-canary",
                                "url": "https://example.com/hook",
                            }
                        ],
                        "next_page": None,
                    }
                )
            }
        )
        result = api.list_webhooks(PROJECT)
        self.assertEqual(result[0]["signing_secret"], redaction.REDACTED)

    def test_update_uses_post_and_can_clear_nullable_fields(self) -> None:
        api, session = management(
            {
                ("POST", f"/integrations/webhooks/{WEBHOOK}"): ok(
                    {"id": WEBHOOK, "environment": None}
                )
            }
        )
        api.update_webhook(PROJECT, WEBHOOK, clear_environment=True)
        body = session.body_for("POST", f"/integrations/webhooks/{WEBHOOK}")
        self.assertIsNone(body["environment"])

    def test_invalid_environment_fails_before_request(self) -> None:
        api, session = management({})
        with self.assertRaises(revenuecat.RevenueCatError):
            api.create_webhook(
                PROJECT,
                name="Events",
                url="https://example.com/hook",
                environment="staging",
            )
        self.assertEqual(session.calls, [])


class RedactionTest(unittest.TestCase):
    def test_nested_credentials_and_bearer_text_are_redacted(self) -> None:
        payload = {
            "authorization_header": "Bearer abcdefghijklmnop",
            "nested": {
                "private_key": "private-canary",
                "message": "Authorization: Bearer qwertyuiopasdfgh",
            },
            "error": "RevenueCat key sk_1234567890abcdef was rejected",
        }
        result = redaction.redact(payload)
        serialized = str(result)
        for canary in (
            "abcdefghijklmnop",
            "private-canary",
            "qwertyuiopasdfgh",
            "sk_1234567890abcdef",
        ):
            self.assertNotIn(canary, serialized)
        self.assertEqual(result["authorization_header"], redaction.REDACTED)


if __name__ == "__main__":
    unittest.main()

"""AdMob behaviour, access classification, reporting, and capability discovery."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import admob  # noqa: E402
from tests.fakes import FakeSession, fail, ok  # noqa: E402

PUB = "pub-1234567890123456"


def client(routes: dict, publisher_id: str | None = PUB) -> tuple[admob.AdMobClient, FakeSession]:
    session = FakeSession(routes)
    return admob.AdMobClient(publisher_id=publisher_id, session=session), session


class AccessDenialTest(unittest.TestCase):
    def test_create_app_403_raises_account_gate_error(self) -> None:
        api, _ = client({("POST", "/apps"): fail(403)})
        with self.assertRaises(admob.AdMobAccessDenied) as caught:
            api.create_app("Example", "ANDROID", "com.example.app")
        message = str(caught.exception)
        self.assertIn("limited-access", message)
        self.assertIn("account manager", message)

    def test_create_ad_unit_403_raises_account_gate_error(self) -> None:
        api, _ = client({("POST", "/adUnits"): fail(403)})
        with self.assertRaises(admob.AdMobAccessDenied):
            api.create_ad_unit("ca-app-pub-1~2", "Rewarded", "REWARDED")

    def test_normal_read_403_is_not_mislabeled_as_account_gate(self) -> None:
        api, _ = client({("GET", "/apps"): fail(403)})
        with self.assertRaises(admob.AdMobPermissionDenied) as caught:
            api.list_apps()
        self.assertNotIsInstance(caught.exception, admob.AdMobAccessDenied)
        self.assertIn("OAuth scopes", str(caught.exception))

    def test_401_is_authentication_error(self) -> None:
        api, _ = client({("GET", "/apps"): fail(401)})
        with self.assertRaises(admob.AdMobAuthenticationError):
            api.list_apps()

    def test_non_403_failure_is_a_plain_error(self) -> None:
        api, _ = client({("POST", "/adUnits"): fail(500)})
        with self.assertRaises(admob.AdMobError) as caught:
            api.create_ad_unit("ca-app-pub-1~2", "Rewarded", "REWARDED")
        self.assertNotIsInstance(caught.exception, admob.AdMobAccessDenied)


class ProbeTest(unittest.TestCase):
    def test_denied_probe_reports_denied_without_mutating(self) -> None:
        api, session = client({("GET", "/mediationGroups"): fail(403)})
        result = api.probe_monetization_access()
        self.assertEqual(result["monetization_access"], "denied")
        self.assertEqual(session.urls("POST"), [], "a probe must never create anything")

    def test_successful_probe_is_reported_as_likely_not_certain(self) -> None:
        api, _ = client({("GET", "/mediationGroups"): ok({"mediationGroups": []})})
        result = api.probe_monetization_access()
        self.assertEqual(result["monetization_access"], "likely")
        self.assertIn("separately gated", result["detail"])

    def test_probe_without_publisher_id_resolves_the_account(self) -> None:
        routes = {
            ("GET", "/accounts"): ok({"account": [{"publisherId": PUB}]}),
            ("GET", "/mediationGroups"): ok({"mediationGroups": []}),
        }
        api, _ = client(routes, publisher_id=None)
        self.assertEqual(api.probe_monetization_access()["publisher_id"], PUB)


class InputValidationTest(unittest.TestCase):
    def test_rejects_unknown_ad_format_before_calling_the_api(self) -> None:
        api, session = client({})
        with self.assertRaises(admob.AdMobError):
            api.create_ad_unit("ca-app-pub-1~2", "Bad", "POPUP")
        self.assertEqual(session.calls, [])

    def test_rejects_unknown_ad_type(self) -> None:
        api, session = client({})
        with self.assertRaises(admob.AdMobError):
            api.create_ad_unit("ca-app-pub-1~2", "Bad", "BANNER", ["HOLOGRAM"])
        self.assertEqual(session.calls, [])

    def test_rejects_unknown_platform(self) -> None:
        api, session = client({})
        with self.assertRaises(admob.AdMobError):
            api.create_app("Example", "WINDOWS_PHONE")
        self.assertEqual(session.calls, [])

    def test_mapping_batch_is_limited_to_google_maximum(self) -> None:
        api, session = client({})
        with self.assertRaises(admob.AdMobError):
            api.batch_create_ad_unit_mappings([{}] * 101)
        self.assertEqual(session.calls, [])


class AppLinkingTest(unittest.TestCase):
    def test_app_store_id_produces_a_linked_app_without_output_only_name(self) -> None:
        api, session = client({("POST", "/apps"): ok({"appId": "ca-app-pub-1~2"})})
        api.create_app("Example", "ANDROID", "com.example.app")
        body = session.body_for("POST", "/apps")
        self.assertEqual(body["linkedAppInfo"], {"appStoreId": "com.example.app"})
        self.assertNotIn("manualAppInfo", body)

    def test_without_app_store_id_the_app_is_manual(self) -> None:
        api, session = client({("POST", "/apps"): ok({"appId": "ca-app-pub-1~2"})})
        api.create_app("Example", "ANDROID")
        body = session.body_for("POST", "/apps")
        self.assertEqual(body["manualAppInfo"]["displayName"], "Example")
        self.assertNotIn("linkedAppInfo", body)


class ReportingTest(unittest.TestCase):
    def test_network_report_uses_stable_v1_and_preserves_stream_payload(self) -> None:
        payload = [{"header": {}}, {"row": {"metricValues": {}}}, {"footer": {}}]
        api, session = client({("POST", "/networkReport:generate"): ok(payload)})
        result = api.generate_network_report({"metrics": ["IMPRESSIONS"]})
        self.assertEqual(result, payload)
        self.assertIn("/v1/accounts/", session.urls("POST")[0])

    def test_health_report_includes_regression_dimensions(self) -> None:
        api, session = client({("POST", "/networkReport:generate"): ok([])})
        api.monetization_health_report("2026-09-01", "2026-09-02", app_ids=["app-1"])
        body = session.body_for("POST", "/networkReport:generate")["reportSpec"]
        self.assertIn("GMA_SDK_VERSION", body["dimensions"])
        self.assertIn("APP_VERSION_NAME", body["dimensions"])
        self.assertIn("SERVING_RESTRICTION", body["dimensions"])
        self.assertIn("MATCH_RATE", body["metrics"])
        self.assertIn("SHOW_RATE", body["metrics"])
        self.assertEqual(
            body["dimensionFilters"][0]["matchesAny"]["values"], [{"value": "app-1"}]
        )


class CapabilityTest(unittest.TestCase):
    def test_capability_matrix_distinguishes_public_reads_from_gated_mediation(self) -> None:
        routes = {
            ("GET", "/apps"): ok({"apps": []}),
            ("GET", "/adSources"): ok({"adSources": []}),
            ("GET", "/mediationGroups"): fail(403),
        }
        api, _ = client(routes)
        result = api.capability_matrix()
        self.assertEqual(result["capabilities"]["admob.inventory.read"], "ready")
        self.assertEqual(result["capabilities"]["admob.ad_sources.read"], "ready")
        self.assertEqual(result["capabilities"]["admob.mediation.read"], "denied_by_account")
        self.assertEqual(result["capabilities"]["admob.apps.create"], "account_gated_unknown")

    def test_approval_summary_surfaces_actionable_states(self) -> None:
        routes = {
            ("GET", "/apps"): ok(
                {
                    "apps": [
                        {"appId": "a", "appApprovalState": "APPROVED"},
                        {"appId": "b", "appApprovalState": "ACTION_REQUIRED"},
                        {"appId": "c", "appApprovalState": "IN_REVIEW"},
                    ]
                }
            )
        }
        api, _ = client(routes)
        result = api.app_approval_summary()
        self.assertEqual(result["states"]["APPROVED"], 1)
        self.assertEqual([app["appId"] for app in result["action_required"]], ["b"])


class AmbiguousAccountTest(unittest.TestCase):
    def test_multiple_accounts_require_an_explicit_publisher_id(self) -> None:
        routes = {
            ("GET", "/accounts"): ok(
                {"account": [{"publisherId": "pub-1"}, {"publisherId": "pub-2"}]}
            )
        }
        api, _ = client(routes, publisher_id=None)
        with self.assertRaises(admob.AdMobError) as caught:
            _ = api.publisher_id
        self.assertIn("--publisher-id", str(caught.exception))

    def test_no_account_explains_the_likely_cause(self) -> None:
        api, _ = client({("GET", "/accounts"): ok({"account": []})}, publisher_id=None)
        with self.assertRaises(admob.AdMobError) as caught:
            _ = api.publisher_id
        self.assertIn("admob login", str(caught.exception))


if __name__ == "__main__":
    unittest.main()

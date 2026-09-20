"""AdMob behaviour, access classification, reporting, and capability discovery."""

from __future__ import annotations

from pathlib import Path
from unittest import mock
import os
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import admob, human_approval, mcp_admob_tools  # noqa: E402
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


class ConfigurationFailureReportingTest(unittest.TestCase):
    """A local setup mistake must reach the agent as a structured AdMob payload.

    Every AdMob MCP tool resolves its client through `_client`, where both the
    profile lookup and credential loading raise `ConfigError`. When that escaped,
    the MCP host reported only "Error executing tool <name>" with no detail, so the
    actionable message ("unknown profile 'x'. known profiles: ...") was lost.
    """

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.previous_home = os.environ.get("MRA_HOME")
        os.environ["MRA_HOME"] = self.tempdir.name

    def tearDown(self) -> None:
        if self.previous_home is None:
            os.environ.pop("MRA_HOME", None)
        else:
            os.environ["MRA_HOME"] = self.previous_home
        self.tempdir.cleanup()

    def assert_configuration_payload(self, result: object) -> dict:
        self.assertIsInstance(result, dict, "config failure must not escape as an exception")
        assert isinstance(result, dict)
        self.assertEqual(result["status"], "configuration_error")
        self.assertEqual(result["platform"], "admob")
        self.assertIn("unknown profile", result["detail"])
        self.assertIn("nonexistent-profile", result["detail"])
        return result

    def test_read_tool_returns_structured_configuration_error(self) -> None:
        self.assert_configuration_payload(
            mcp_admob_tools.admob_list_apps(profile="nonexistent-profile")
        )

    def test_probe_access_returns_structured_configuration_error(self) -> None:
        # probe_access was the one read tool that bypassed the shared handler.
        self.assert_configuration_payload(
            mcp_admob_tools.admob_probe_access(profile="nonexistent-profile")
        )

    def test_configuration_error_is_not_reported_as_an_account_gate(self) -> None:
        result = mcp_admob_tools.admob_list_ad_units(profile="nonexistent-profile")
        self.assertNotEqual(result["status"], "denied_by_account")
        self.assertNotEqual(result["status"], "permission_denied")
        self.assertIn("never called", result["hint"])

    def test_unapproved_mutation_reports_configuration_error_without_calling_admob(self) -> None:
        result = mcp_admob_tools.admob_create_app(
            display_name="Example", platform="ANDROID", profile="nonexistent-profile"
        )
        self.assert_configuration_payload(result)
        self.assertIs(result["_mra"]["human_approved"], False)

    def test_configuration_failure_preserves_operator_approval_evidence(self) -> None:
        # A local approval of an irreversible action is audit evidence; a later
        # failure must not erase it, whatever the failure's cause.
        approved = {"approved": True, "status": "approved", "mode": "macos-native-dialog"}
        with mock.patch.object(human_approval, "request", return_value=approved):
            result = mcp_admob_tools.admob_create_app(
                display_name="Example",
                platform="ANDROID",
                app_store_id="com.example.app",
                profile="nonexistent-profile",
            )
        self.assert_configuration_payload(result)
        self.assertIs(result["_mra"]["human_approved"], True)
        self.assertEqual(result["_mra"]["risk"], "high")


if __name__ == "__main__":
    unittest.main()

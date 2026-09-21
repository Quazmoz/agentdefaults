"""Play reporting freshness: parsing, selection, time zones, and failure classes.

Every case here is offline. No test may reach Google or need a credential.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import io
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import config, play_reporting  # noqa: E402
from tests.fakes import FakeResponse, FakeSession, fail, ok, raw  # noqa: E402

PACKAGE = "com.quazmoz.motionguard"
BUCKET = "pubsite_prod_rev_0123456789"
NOW = datetime(2026, 9, 21, 18, 0, tzinfo=timezone.utc)


def utf16(text: str) -> bytes:
    """Encode as Play does: UTF-16 with a byte order mark."""
    return text.encode("utf-16")


def freshness_payload(year: int, month: int, day: int, zone: str = "America/Los_Angeles") -> dict:
    return {
        "name": f"apps/{PACKAGE}/anrRateMetricSet",
        "freshnessInfo": {
            "freshnesses": [
                {
                    "aggregationPeriod": "DAILY",
                    "latestEndTime": {
                        "year": year,
                        "month": month,
                        "day": day,
                        "timeZone": {"id": zone},
                    },
                },
                {
                    "aggregationPeriod": "HOURLY",
                    "latestEndTime": {
                        "year": year,
                        "month": month,
                        "day": day,
                        "hours": 14,
                        "timeZone": {"id": zone},
                    },
                },
            ]
        },
    }


INSTALLS_CSV = (
    "Date,Package Name,Daily Device Installs,Daily Device Uninstalls,Daily User Installs\r\n"
    "2026-09-17,com.quazmoz.motionguard,4,1,4\r\n"
    "2026-09-18,com.quazmoz.motionguard,7,0,6\r\n"
    "2026-09-19,com.quazmoz.motionguard,9,2,8\r\n"
)

# The column spelling Play actually writes, taken from a live 2026-09 report.
LEGACY_STORE_CSV = (
    "Date,Package name,Store listing acquisitions,Store listing visitors,"
    "Store listing conversion rate\r\n"
    "2026-09-18,com.quazmoz.motionguard,20,200,0.1\r\n"
    "2026-09-19,com.quazmoz.motionguard,25,250,0.1\r\n"
)

CLICK_STORE_CSV = (
    "Date,Package Name,Unique User Install Clicks,Store Listing Click-through Rate\r\n"
    "2026-09-19,com.quazmoz.motionguard,31,0.12\r\n"
)

SALES_CSV = (
    "Order Number,Order Charged Date,Financial Status,Product Title,City of Buyer,"
    "Country of Buyer,Charged Amount\r\n"
    "GPA.1,2026-09-15,Charged,Pro,Austin,US,4.99\r\n"
    "GPA.2,2026-09-16,Refunded,Pro,Lisbon,PT,-4.99\r\n"
    "GPA.3,2026-09-17,Charged,Pro,Austin,US,4.99\r\n"
)


def storage_object(name: str, updated: str, size: int = 512) -> dict:
    return {"name": name, "updated": updated, "size": str(size)}


class DeveloperReportingFreshnessTest(unittest.TestCase):
    def test_parses_every_granularity_and_ages_it_against_the_stated_zone(self) -> None:
        session = FakeSession({("GET", "anrRateMetricSet"): ok(freshness_payload(2026, 9, 20))})
        result = play_reporting.developer_reporting_freshness(
            PACKAGE, session=session, now=NOW, metric_sets=("anrRateMetricSet",)
        )

        self.assertTrue(result["available"])
        daily = result["metrics"]["anrRateMetricSet"]["granularities"]["DAILY"]
        # 2026-09-20T00:00 Pacific is 07:00Z; NOW is 2026-09-21T18:00Z => 35h.
        self.assertEqual(daily["latest_end_time"], "2026-09-20T00:00:00-07:00")
        self.assertEqual(daily["lag_hours"], 35.0)
        self.assertIn("HOURLY", result["metrics"]["anrRateMetricSet"]["granularities"])

    def test_names_the_datasets_this_api_does_not_expose(self) -> None:
        session = FakeSession({("GET", "anrRateMetricSet"): ok(freshness_payload(2026, 9, 20))})
        result = play_reporting.developer_reporting_freshness(
            PACKAGE, session=session, now=NOW, metric_sets=("anrRateMetricSet",)
        )
        self.assertEqual(result["exposes"], "android-vitals-only")
        for absent in ("installs", "acquisitions", "subscriptions", "refunds"):
            self.assertIn(absent, result["does_not_expose"])

    def test_missing_freshness_block_is_reported_not_guessed(self) -> None:
        session = FakeSession({("GET", "crashRateMetricSet"): ok({"name": "x"})})
        result = play_reporting.developer_reporting_freshness(
            PACKAGE, session=session, now=NOW, metric_sets=("crashRateMetricSet",)
        )
        entry = result["metrics"]["crashRateMetricSet"]
        self.assertEqual(entry["status"], "no_freshness_published")
        self.assertFalse(result["available"])

    def test_classifies_each_failure_separately(self) -> None:
        cases = {
            401: "authentication_failed",
            403: "permission_denied",
            404: "not_found",
            429: "rate_limited",
            503: "server_error",
        }
        for status, expected in cases.items():
            session = FakeSession({("GET", "anrRateMetricSet"): fail(status)})
            result = play_reporting.developer_reporting_freshness(
                PACKAGE, session=session, now=NOW, metric_sets=("anrRateMetricSet",)
            )
            self.assertEqual(result["metrics"]["anrRateMetricSet"]["status"], expected, status)
            self.assertFalse(result["available"])

    def test_disabled_api_is_not_reported_as_a_missing_permission(self) -> None:
        payload = {
            "error": {
                "code": 403,
                "status": "PERMISSION_DENIED",
                "message": (
                    "Play Developer Reporting API has not been used in project 1234 "
                    "before or it is disabled."
                ),
                "details": [{"reason": "SERVICE_DISABLED"}],
            }
        }
        session = FakeSession({("GET", "anrRateMetricSet"): fail(403, payload)})
        result = play_reporting.developer_reporting_freshness(
            PACKAGE, session=session, now=NOW, metric_sets=("anrRateMetricSet",)
        )
        self.assertEqual(result["metrics"]["anrRateMetricSet"]["status"], "api_not_enabled")

    def test_rejects_a_package_name_that_could_reshape_the_request_path(self) -> None:
        with self.assertRaises(play_reporting.ReportingError):
            play_reporting.developer_reporting_freshness("../../evil", session=FakeSession({}))

    def test_redacts_a_credential_echoed_in_an_error_body(self) -> None:
        payload = {"error": {"message": "denied for Authorization: Bearer ya29.SECRETVALUE"}}
        session = FakeSession({("GET", "anrRateMetricSet"): fail(403, payload)})
        result = play_reporting.developer_reporting_freshness(
            PACKAGE, session=session, now=NOW, metric_sets=("anrRateMetricSet",)
        )
        detail = result["metrics"]["anrRateMetricSet"]["detail"]
        self.assertNotIn("ya29.SECRETVALUE", detail)
        self.assertIn("<redacted>", detail)


class ObjectListingTest(unittest.TestCase):
    def test_follows_pagination_to_the_end(self) -> None:
        pages = [
            {"items": [storage_object("stats/installs/a.csv", "2026-09-20T01:00:00Z")],
             "nextPageToken": "p2"},
            {"items": [storage_object("stats/installs/b.csv", "2026-09-21T01:00:00Z")]},
        ]
        served: list[dict] = []

        def handler(**kwargs):
            served.append(kwargs)
            return FakeResponse(200, pages[len(served) - 1])

        session = FakeSession({("GET", "/o"): handler})
        items = play_reporting.list_objects(BUCKET, "stats/installs/", session=session)

        self.assertEqual([item["name"] for item in items],
                         ["stats/installs/a.csv", "stats/installs/b.csv"])
        self.assertEqual(served[1]["params"]["pageToken"], "p2")

    def test_rejects_a_bucket_id_that_is_not_a_bucket_id(self) -> None:
        for bad in ("../other-bucket", "pubsite prod", "a/b", ""):
            with self.assertRaises(play_reporting.ReportingError):
                play_reporting.list_objects(bad, "stats/", session=FakeSession({}))


class ReportSelectionTest(unittest.TestCase):
    def test_prefers_the_current_month_overview_file(self) -> None:
        items = [
            storage_object("stats/installs/installs_p_202608_overview.csv", "2026-09-01T00:00:00Z"),
            storage_object("stats/installs/installs_p_202609_country.csv", "2026-09-21T02:00:00Z"),
            storage_object("stats/installs/installs_p_202609_overview.csv", "2026-09-21T01:00:00Z"),
        ]
        chosen = play_reporting._pick_object(items, ["202609", "202608"])
        self.assertEqual(chosen["name"], "stats/installs/installs_p_202609_overview.csv")

    def test_falls_back_to_the_previous_month_before_this_month_exists(self) -> None:
        items = [
            storage_object("stats/installs/installs_p_202608_overview.csv", "2026-09-04T00:00:00Z"),
        ]
        chosen = play_reporting._pick_object(items, ["202609", "202608"])
        self.assertEqual(chosen["name"], "stats/installs/installs_p_202608_overview.csv")

    def test_reports_no_recent_month_rather_than_reading_a_stale_file(self) -> None:
        self.assertIsNone(play_reporting._pick_object(
            [storage_object("stats/installs/installs_p_202401_overview.csv", "2024-02-01T00:00:00Z")],
            ["202609", "202608"],
        ))

    def test_months_walks_backwards_across_a_year_boundary(self) -> None:
        self.assertEqual(
            play_reporting._months(datetime(2026, 1, 3, tzinfo=timezone.utc)),
            ["202601", "202512"],
        )


class CsvParsingTest(unittest.TestCase):
    def test_decodes_the_utf16_encoding_play_actually_writes(self) -> None:
        self.assertEqual(play_reporting.decode_report(utf16(INSTALLS_CSV)), INSTALLS_CSV)

    def test_decodes_plain_utf8_too(self) -> None:
        self.assertEqual(
            play_reporting.decode_report(INSTALLS_CSV.encode("utf-8")), INSTALLS_CSV
        )

    def test_takes_the_maximum_date_not_the_last_row(self) -> None:
        shuffled = (
            "Date,Daily Device Installs\r\n"
            "2026-09-19,9\r\n"
            "2026-09-17,4\r\n"
            "2026-09-18,7\r\n"
        )
        result = play_reporting.read_csv_freshness(shuffled)
        self.assertEqual(result["latest_data_date"], "2026-09-19")
        self.assertEqual(result["rows"], 3)

    def test_parses_the_pacific_earnings_date_format(self) -> None:
        text = "Description,Transaction Date,Amount\r\nx,\"Sep 14, 2026\",1.00\r\n"
        result = play_reporting.read_csv_freshness(text)
        self.assertEqual(result["latest_data_date"], "2026-09-14")
        self.assertEqual(result["date_column"], "Transaction Date")

    def test_header_only_report_is_empty_not_broken(self) -> None:
        result = play_reporting.read_csv_freshness("Date,Daily Device Installs\r\n")
        self.assertEqual(result["status"], "empty_report")

    def test_completely_blank_object_is_empty(self) -> None:
        self.assertEqual(play_reporting.read_csv_freshness("")["status"], "empty_report")

    def test_report_without_a_date_column_is_named_as_such(self) -> None:
        result = play_reporting.read_csv_freshness("Package,Installs\r\ncom.x,4\r\n")
        self.assertEqual(result["status"], "no_date_column")

    def test_unparsable_dates_do_not_become_a_fabricated_date(self) -> None:
        result = play_reporting.read_csv_freshness("Date,Installs\r\nnot-a-date,4\r\n")
        self.assertEqual(result["status"], "no_parsable_dates")
        self.assertNotIn("latest_data_date", result)

    def test_ragged_rows_do_not_abort_the_probe(self) -> None:
        malformed = (
            "Date,Installs,Uninstalls\r\n"
            "2026-09-18,7\r\n"
            "2026-09-19,9,2,extra,fields\r\n"
        )
        result = play_reporting.read_csv_freshness(malformed)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["latest_data_date"], "2026-09-19")


class LagTest(unittest.TestCase):
    def test_a_pacific_day_is_aged_from_its_own_midnight(self) -> None:
        lag = play_reporting._lag_from_date(
            datetime(2026, 9, 19).date(), "America/Los_Angeles", NOW
        )
        # 2026-09-20T00:00 Pacific == 07:00Z, so NOW (2026-09-21T18:00Z) is 35h later.
        self.assertEqual(lag["lag_hours"], 35.0)
        self.assertEqual(lag["lag_days"], 2)

    def test_the_same_date_stated_in_utc_is_older_by_the_offset(self) -> None:
        pacific = play_reporting._lag_from_date(
            datetime(2026, 9, 19).date(), "America/Los_Angeles", NOW
        )
        utc = play_reporting._lag_from_date(datetime(2026, 9, 19).date(), "UTC", NOW)
        self.assertEqual(utc["lag_hours"] - pacific["lag_hours"], 7.0)

    def test_an_unknown_zone_yields_no_lag_rather_than_a_wrong_one(self) -> None:
        lag = play_reporting._lag_from_date(
            datetime(2026, 9, 19).date(), "Mars/Olympus_Mons", NOW
        )
        self.assertIsNone(lag["lag_hours"])
        self.assertEqual(lag["timezone_status"], "unavailable")


class ConversionRateTest(unittest.TestCase):
    def test_legacy_columns_convert_within_one_date(self) -> None:
        parsed = play_reporting.read_csv_freshness(LEGACY_STORE_CSV)
        conversion = play_reporting.store_listing_conversion(parsed)
        self.assertEqual(conversion["model"], "legacy_visitors_acquisitions")
        self.assertEqual(conversion["conversion_rate"], 0.1)
        self.assertEqual(conversion["rows_aggregated"], 1)
        # Google publishes its own rate column; it is echoed, not recomputed.
        self.assertEqual(conversion["reported_conversion_rate_column"],
                         "Store listing conversion rate")
        self.assertEqual(conversion["reported_conversion_rate"], 0.1)

    def test_a_breakdown_report_is_summed_across_its_newest_date(self) -> None:
        # Play writes no overview file for store performance, only country and
        # traffic-source breakdowns, so one row is one country, not the app.
        country = (
            "Date,Country / region,Store listing acquisitions,Store listing visitors,"
            "Store listing conversion rate\r\n"
            "2026-09-18,US,9,10,0.9\r\n"
            "2026-09-19,US,30,300,0.1\r\n"
            "2026-09-19,GB,20,100,0.2\r\n"
        )
        conversion = play_reporting.store_listing_conversion(
            play_reporting.read_csv_freshness(country)
        )
        self.assertEqual(conversion["rows_aggregated"], 2)
        # 50/400, not the mean of 0.1 and 0.2, which would ignore country size.
        self.assertEqual(conversion["conversion_rate"], 0.125)
        self.assertIsNone(conversion["reported_conversion_rate"])
        self.assertIn("2026-09-19", conversion["formula"])

    def test_the_2026_click_model_is_reported_not_recombined(self) -> None:
        parsed = play_reporting.read_csv_freshness(CLICK_STORE_CSV)
        conversion = play_reporting.store_listing_conversion(parsed)
        self.assertEqual(conversion["model"], "click_intent_2026")
        self.assertIsNone(conversion["conversion_rate"])

    def test_a_zero_denominator_does_not_invent_a_rate(self) -> None:
        parsed = play_reporting.read_csv_freshness(
            "Date,Store Listing Visitors,Store Listing Acquisitions\r\n2026-09-19,0,0\r\n"
        )
        self.assertIsNone(play_reporting.store_listing_conversion(parsed)["conversion_rate"])

    def test_a_single_click_column_is_listed_once(self) -> None:
        parsed = play_reporting.read_csv_freshness(
            "Date,Store listing click-through rate\r\n2026-09-19,0.12\r\n"
        )
        conversion = play_reporting.store_listing_conversion(parsed)
        self.assertEqual(conversion["model"], "click_intent_2026")
        self.assertEqual(conversion["available_columns"],
                         ["Store listing click-through rate"])

    def test_an_unrecognised_schema_reports_unknown(self) -> None:
        parsed = play_reporting.read_csv_freshness("Date,Something\r\n2026-09-19,1\r\n")
        self.assertEqual(play_reporting.store_listing_conversion(parsed)["model"], "unknown")


class FinancialSummaryTest(unittest.TestCase):
    def test_returns_aggregates_and_never_a_buyer_row(self) -> None:
        summary = play_reporting.summarize_financial(SALES_CSV)
        self.assertEqual(summary["latest_data_date"], "2026-09-17")
        self.assertEqual(
            summary["transaction_class_counts"]["Financial Status"],
            {"Charged": 2, "Refunded": 1},
        )
        self.assertNotIn("latest_row", summary)
        body = repr(summary)
        for leaked in ("Austin", "Lisbon", "GPA.1"):
            self.assertNotIn(leaked, body)


class ProbeReportTest(unittest.TestCase):
    def _session(self, object_name: str, body: bytes, size: int = 512) -> FakeSession:
        return FakeSession(
            {
                ("GET", "/o"): ok({"items": [storage_object(object_name, "2026-09-21T06:00:00Z", size)]}),
                ("GET", "/o/" + object_name.replace("/", "%2F")): raw(body),
            }
        )

    def test_reads_a_utf16_installs_report_end_to_end(self) -> None:
        name = "stats/installs/installs_com.quazmoz.motionguard_202609_overview.csv"
        result = play_reporting._probe_report(
            BUCKET,
            "stats/installs/",
            "installs_com.quazmoz.motionguard_",
            "America/Los_Angeles",
            "assumed",
            ["202609", "202608"],
            self._session(name, utf16(INSTALLS_CSV)),
            NOW,
            financial=False,
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["latest_data_date"], "2026-09-19")
        self.assertEqual(result["object_updated_at"], "2026-09-21T06:00:00Z")
        self.assertEqual(result["lag_days"], 2)
        self.assertIn("Daily Device Uninstalls", result["columns"])
        self.assertEqual(result["latest_rows"], [{
            "Date": "2026-09-19",
            "Package Name": "com.quazmoz.motionguard",
            "Daily Device Installs": "9",
            "Daily Device Uninstalls": "2",
            "Daily User Installs": "8",
        }])

    def test_an_absent_report_is_named_rather_than_treated_as_a_denial(self) -> None:
        session = FakeSession({("GET", "/o"): ok({"items": []})})
        result = play_reporting._probe_report(
            BUCKET, "sales/", "salesreport_", "UTC", "assumed",
            ["202609"], session, NOW, financial=True,
        )
        self.assertEqual(result["status"], "report_not_generated")

    def test_a_bucket_denial_is_classified_as_a_permission_problem(self) -> None:
        session = FakeSession({("GET", "/o"): fail(403, {"error": {"message": "no access"}})})
        result = play_reporting._probe_report(
            BUCKET, "stats/installs/", "installs_x_", "UTC", "assumed",
            ["202609"], session, NOW, financial=False,
        )
        self.assertEqual(result["status"], "permission_denied")
        self.assertEqual(result["surface"], "bulk_reports")

    def test_a_missing_bucket_is_a_404_not_a_permission_problem(self) -> None:
        session = FakeSession({("GET", "/o"): fail(404, {"error": {"message": "Not Found"}})})
        result = play_reporting._probe_report(
            BUCKET, "stats/installs/", "installs_x_", "UTC", "assumed",
            ["202609"], session, NOW, financial=False,
        )
        self.assertEqual(result["status"], "not_found")

    def test_an_oversized_object_is_refused_before_it_is_downloaded(self) -> None:
        name = "sales/salesreport_202609.zip"
        session = FakeSession(
            {("GET", "/o"): ok({"items": [storage_object(name, "2026-09-21T06:00:00Z",
                                                         play_reporting.MAX_OBJECT_BYTES + 1)]})}
        )
        result = play_reporting._probe_report(
            BUCKET, "sales/", "salesreport_", "UTC", "assumed",
            ["202609"], session, NOW, financial=True,
        )
        self.assertEqual(result["status"], "report_too_large")

    def test_reads_the_newest_member_of_a_financial_zip(self) -> None:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("salesreport_202609.csv", utf16(SALES_CSV))
        name = "sales/salesreport_202609.zip"
        result = play_reporting._probe_report(
            BUCKET, "sales/", "salesreport_", "UTC", "assumed",
            ["202609"], self._session(name, buffer.getvalue()), NOW, financial=True,
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["latest_data_date"], "2026-09-17")
        self.assertEqual(result["members"], ["salesreport_202609.csv"])
        self.assertNotIn("Austin", repr(result))

    def test_a_corrupt_zip_is_reported_not_raised(self) -> None:
        name = "sales/salesreport_202609.zip"
        result = play_reporting._probe_report(
            BUCKET, "sales/", "salesreport_", "UTC", "assumed",
            ["202609"], self._session(name, b"not-a-zip"), NOW, financial=True,
        )
        self.assertEqual(result["status"], "malformed_report")


class FreshnessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.previous_home = os.environ.get("MRA_HOME")
        self.previous_bucket = os.environ.get(play_reporting.BUCKET_ENV)
        os.environ["MRA_HOME"] = self.tempdir.name
        os.environ.pop(play_reporting.BUCKET_ENV, None)
        config.save_profile(config.Profile(slug="motionguard", package_name=PACKAGE))

    def tearDown(self) -> None:
        for name, previous in (
            ("MRA_HOME", self.previous_home),
            (play_reporting.BUCKET_ENV, self.previous_bucket),
        ):
            if previous is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = previous
        self.tempdir.cleanup()

    def test_an_unconfigured_bucket_fails_closed_with_the_manual_step(self) -> None:
        session = FakeSession(
            {("GET", "MetricSet"): ok(freshness_payload(2026, 9, 20))}
        )
        result = play_reporting.freshness("motionguard", session=session, now=NOW)

        self.assertEqual(result["sources"]["bulk_reports"]["status"], "bucket_not_configured")
        self.assertFalse(result["sources"]["financial"]["available"])
        self.assertIn("Download reports", result["sources"]["bulk_reports"]["detail"])
        # The vitals surface still answers, because it needs no bucket.
        self.assertTrue(result["sources"]["developer_reporting"]["available"])

    def test_never_claims_to_know_the_console_cutoff(self) -> None:
        session = FakeSession({("GET", "MetricSet"): ok(freshness_payload(2026, 9, 20))})
        result = play_reporting.freshness("motionguard", session=session, now=NOW)
        self.assertEqual(result["console_visible_through"], "operator_input_required")
        self.assertTrue(result["operator_comparison_instructions"])
        self.assertEqual(result["mutations"], "none")

    def test_reads_every_surface_when_a_bucket_is_configured(self) -> None:
        os.environ[play_reporting.BUCKET_ENV] = BUCKET
        listing = ok({"items": [storage_object(
            "stats/installs/installs_com.quazmoz.motionguard_202609_overview.csv",
            "2026-09-21T06:00:00Z",
        )]})
        session = FakeSession(
            {
                ("GET", "MetricSet"): ok(freshness_payload(2026, 9, 20)),
                ("GET", "/o"): listing,
                ("GET", "/o/stats"): raw(utf16(INSTALLS_CSV)),
            }
        )
        result = play_reporting.freshness("motionguard", session=session, now=NOW)

        bulk = result["sources"]["bulk_reports"]
        self.assertEqual(bulk["bucket"], BUCKET)
        installs = bulk["reports"]["installs"]
        self.assertEqual(installs["latest_data_date"], "2026-09-19")
        self.assertEqual(bulk["months_checked"], ["202609", "202608"])
        # The retained rows are collapsed before they leave the probe.
        self.assertNotIn("latest_rows", installs)
        self.assertEqual(installs["latest_rows_count"], 1)
        self.assertEqual(installs["latest_row"]["Daily Device Installs"], "9")

    def test_financial_can_be_skipped_without_touching_the_financial_prefixes(self) -> None:
        os.environ[play_reporting.BUCKET_ENV] = BUCKET
        session = FakeSession(
            {
                ("GET", "MetricSet"): ok(freshness_payload(2026, 9, 20)),
                ("GET", "/o"): ok({"items": []}),
            }
        )
        result = play_reporting.freshness(
            "motionguard", session=session, now=NOW, include_financial=False
        )
        self.assertEqual(result["sources"]["financial"]["status"], "skipped_by_caller")
        self.assertFalse(any("sales/" in call.get("params", {}).get("prefix", "")
                             for call in session.calls))

    def test_a_profile_bucket_outranks_the_account_default(self) -> None:
        os.environ[play_reporting.BUCKET_ENV] = "pubsite_prod_rev_account_default"
        config.save_profile(
            config.Profile(slug="motionguard", play_reporting_bucket="pubsite_prod_rev_profile")
        )
        self.assertEqual(
            play_reporting.reporting_bucket(config.load_profile("motionguard")),
            "pubsite_prod_rev_profile",
        )

    def test_a_malformed_configured_bucket_is_refused(self) -> None:
        os.environ[play_reporting.BUCKET_ENV] = "../somebody-elses-bucket"
        with self.assertRaises(play_reporting.ReportingError):
            play_reporting.reporting_bucket(config.load_profile("motionguard"))


if __name__ == "__main__":
    unittest.main()

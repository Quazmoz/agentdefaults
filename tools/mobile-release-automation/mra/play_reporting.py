"""Read-only freshness probes for the official Google Play reporting surfaces.

Two official Google surfaces carry Play data programmatically, and they carry
different things:

* Play Developer Reporting API (``playdeveloperreporting.googleapis.com``) -
  Android vitals metric sets only. It publishes no installs, acquisitions,
  store-listing, subscription, or revenue metric set, so it cannot answer an
  acquisition question no matter which scope is granted.
* The developer's Play bulk-report Cloud Storage bucket - installs, store
  performance, acquisition, subscriptions, and financial exports, written as
  monthly CSV files whose rows are daily.

Everything here observes. Nothing mutates Play state, nothing writes report
content to disk, and financial reports are summarized rather than returned,
because their rows carry buyer location data.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Iterable, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import codecs
import csv
import io
import os
import re
import zipfile

from . import auth, config, redaction

REPORTING_BASE = "https://playdeveloperreporting.googleapis.com/v1beta1"
STORAGE_BASE = "https://storage.googleapis.com/storage/v1"

REQUEST_TIMEOUT_SECONDS = 60

# A monthly bulk report is normally well under a megabyte. The cap keeps a
# surprising object from being pulled into memory just to read one date.
MAX_OBJECT_BYTES = 50 * 1024 * 1024
MAX_ROWS = 200_000
MAX_LIST_PAGES = 20

BUCKET_ENV = "MRA_PLAY_REPORTING_BUCKET"

# Google Cloud Storage bucket naming, narrowed. The value is interpolated into a
# request path, so anything outside this shape is refused rather than sent.
_BUCKET_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{1,221}$")
_PACKAGE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)+$")

# Every metric set the Play Developer Reporting API publishes, all under vitals.
# errorCountMetricSet is listed last because it is the only one whose absence is
# unremarkable on an app with no error reports.
VITALS_METRIC_SETS = (
    "anrRateMetricSet",
    "crashRateMetricSet",
    "excessiveWakeupRateMetricSet",
    "stuckBackgroundWakelockRateMetricSet",
    "slowStartRateMetricSet",
    "slowRenderingRateMetricSet",
    "lmkRateMetricSet",
    "anonRssAndSwapMemoryUsageMetricSet",
    "bitmapMemoryUsageMetricSet",
    "errorCountMetricSet",
)

# (directory prefix, filename prefix, timezone, timezone basis).
#
# Google documents a timezone for the subscriptions report (UTC) and the
# earnings report (Pacific), and documents the acquisition reports as Pacific in
# the acquisition-and-retention help page. It does not state one for the
# statistics family, so that assumption is labelled rather than presented as
# documented.
BULK_REPORTS: dict[str, tuple[str, str, str, str]] = {
    "installs": ("stats/installs/", "installs_{package}_", "America/Los_Angeles", "assumed"),
    "store_performance": (
        "stats/store_performance/",
        "store_performance_{package}_",
        "America/Los_Angeles",
        "assumed",
    ),
    "ratings": ("stats/ratings/", "ratings_{package}_", "America/Los_Angeles", "assumed"),
    "crashes": ("stats/crashes/", "crashes_{package}_", "America/Los_Angeles", "assumed"),
    "retained_installers": (
        "acquisition/retained_installers/",
        "retained_installers_{package}_",
        "America/Los_Angeles",
        "documented",
    ),
    "buyers_7d": (
        "acquisition/buyers_7d/",
        "buyers_7d_{package}_",
        "America/Los_Angeles",
        "documented",
    ),
    "subscriptions": (
        "financial-stats/subscriptions/",
        "subscriptions_{package}_",
        "UTC",
        "documented",
    ),
}

# Financial exports are account-wide zips, not per-package files.
FINANCIAL_REPORTS: dict[str, tuple[str, str, str, str]] = {
    "estimated_sales": ("sales/", "salesreport_", "UTC", "assumed"),
    "earnings": ("earnings/", "earnings_", "America/Los_Angeles", "documented"),
}

CONSOLE_COMPARISON = [
    "Play Console > Statistics: note the newest date with a non-empty installs "
    "value and report it as the installs console cutoff.",
    "Play Console > Acquisition > Store listing performance: note the newest "
    "date shown and whether the page reports clicks/CTR (July 2026 model) or "
    "the legacy visitors/acquisitions/conversion-rate model.",
    "Play Console > Financial reports > Estimated sales: note the newest "
    "transaction date shown.",
    "Play Console > Android vitals > ANR rate: note the newest date plotted.",
]


class ReportingError(ValueError):
    """Raised for a caller mistake, never for a remote failure.

    It subclasses ValueError so the MCP read wrapper reports it as a bad
    argument rather than letting it surface as an opaque server fault.
    """


# ---- shared plumbing -------------------------------------------------------


def _require_package(package_name: str) -> str:
    value = (package_name or "").strip()
    if not _PACKAGE_RE.match(value):
        raise ReportingError(f"invalid Android package name: {package_name!r}")
    return value


def _require_bucket(bucket: str) -> str:
    value = (bucket or "").strip()
    if not _BUCKET_RE.match(value):
        raise ReportingError(
            f"invalid Play reporting bucket id: {bucket!r}. Expected the bucket "
            "name shown by Play Console > Download reports, such as "
            "pubsite_prod_rev_0123456789"
        )
    return value


def reporting_bucket(profile: config.Profile) -> str | None:
    """Resolve the non-secret Play bulk-report bucket for one profile.

    The bucket id identifies a developer account, not an app, so a single
    environment default covers a whole account and the per-profile field exists
    for operators who publish under more than one.
    """
    for candidate in (profile.play_reporting_bucket, os.environ.get(BUCKET_ENV)):
        value = (candidate or "").strip()
        if value:
            return _require_bucket(value)
    return None


def reporting_session(session=None):
    """One authorized session covering both read-only reporting surfaces."""
    return session or auth.play_session(auth.PLAY_REPORTING_SCOPES)


def classify_reporting_failure(status_code: int, payload: Any) -> str:
    """Separate the failure classes an operator would act on differently."""
    message = ""
    reason = ""
    if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
        error = payload["error"]
        message = str(error.get("message", ""))
        reason = str(error.get("status", ""))
        for detail in error.get("details", []) or []:
            if isinstance(detail, dict) and detail.get("reason"):
                reason = f"{reason} {detail['reason']}"
        for item in error.get("errors", []) or []:
            if isinstance(item, dict) and item.get("reason"):
                reason = f"{reason} {item['reason']}"
    haystack = f"{reason} {message}".lower()

    if status_code == 401:
        return "authentication_failed"
    if status_code == 403:
        if (
            "accessnotconfigured" in haystack
            or "service_disabled" in haystack
            or "has not been used in project" in haystack
            or "is disabled" in haystack
        ):
            return "api_not_enabled"
        return "permission_denied"
    if status_code == 404:
        return "not_found"
    if status_code == 429:
        return "rate_limited"
    if 500 <= status_code < 600:
        return "server_error"
    return "request_failed"


def _failure(response, *, surface: str) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError:
        payload = None
    message = ""
    if isinstance(payload, dict) and isinstance(payload.get("error"), dict):
        message = str(payload["error"].get("message", ""))
    return {
        "status": classify_reporting_failure(response.status_code, payload),
        "surface": surface,
        "http_status": response.status_code,
        "detail": redaction.redact_text(message or (response.text or "")[:400]),
    }


# ---- time ------------------------------------------------------------------


def _zone(name: str) -> ZoneInfo | None:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, KeyError, ValueError):
        return None


def _lag_from_date(latest: date, tz_name: str, now: datetime) -> dict[str, Any]:
    """Age a daily report row correctly for the zone that row is stated in.

    A row dated D is only complete once D has ended in the report's own
    timezone, so lag is measured from the end of D, not from D itself. Comparing
    the bare date against a UTC clock would misreport a Pacific-stated report by
    up to eight hours.
    """
    zone = _zone(tz_name)
    if zone is None:
        return {"lag_hours": None, "lag_days": None, "timezone_status": "unavailable"}
    end_of_day = datetime.combine(latest + timedelta(days=1), time.min, tzinfo=zone)
    return {
        "lag_hours": round((now - end_of_day).total_seconds() / 3600, 1),
        "lag_days": (now.astimezone(zone).date() - latest).days,
        "timezone_status": "resolved",
    }


def _google_datetime(value: Any) -> datetime | None:
    """Build an aware instant from a google.type.DateTime payload."""
    if not isinstance(value, dict) or "year" not in value:
        return None
    zone: Any = timezone.utc
    named = value.get("timeZone")
    if isinstance(named, dict) and named.get("id"):
        zone = _zone(str(named["id"])) or timezone.utc
    offset = value.get("utcOffset")
    if isinstance(offset, str) and offset.endswith("s"):
        try:
            zone = timezone(timedelta(seconds=int(offset[:-1])))
        except ValueError:
            zone = timezone.utc
    try:
        return datetime(
            int(value["year"]),
            int(value.get("month", 1)),
            int(value.get("day", 1)),
            int(value.get("hours", 0)),
            int(value.get("minutes", 0)),
            int(value.get("seconds", 0)),
            tzinfo=zone,
        )
    except (TypeError, ValueError):
        return None


# ---- Play Developer Reporting API ------------------------------------------


def developer_reporting_freshness(
    package_name: str,
    session=None,
    *,
    now: datetime | None = None,
    metric_sets: Sequence[str] = VITALS_METRIC_SETS,
) -> dict[str, Any]:
    """Read the published freshness of every vitals metric set for one app."""
    package = _require_package(package_name)
    http = reporting_session(session)
    moment = now or datetime.now(timezone.utc)

    metrics: dict[str, Any] = {}
    for metric_set in metric_sets:
        url = f"{REPORTING_BASE}/apps/{package}/{metric_set}"
        response = http.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        if not response.ok:
            metrics[metric_set] = _failure(response, surface="developer_reporting")
            continue
        payload = response.json() if response.content else {}
        entry: dict[str, Any] = {"status": "ok", "granularities": {}}
        freshnesses = (payload.get("freshnessInfo") or {}).get("freshnesses") or []
        for freshness in freshnesses:
            period = str(freshness.get("aggregationPeriod", "UNKNOWN"))
            latest = _google_datetime(freshness.get("latestEndTime"))
            entry["granularities"][period] = {
                "latest_end_time": latest.isoformat() if latest else None,
                "lag_hours": (
                    round((moment - latest).total_seconds() / 3600, 1) if latest else None
                ),
            }
        if not entry["granularities"]:
            entry["status"] = "no_freshness_published"
        metrics[metric_set] = entry

    classes = {entry.get("status") for entry in metrics.values()}
    available = "ok" in classes
    result: dict[str, Any] = {
        "available": available,
        "surface": "play-developer-reporting-api-v1beta1",
        "scope": auth.PLAY_DEVELOPER_REPORTING_SCOPE,
        "exposes": "android-vitals-only",
        "does_not_expose": [
            "installs",
            "uninstalls",
            "acquisitions",
            "store_listing_visitors_or_clicks",
            "in_app_purchases",
            "refunds",
            "subscriptions",
        ],
        "metrics": metrics,
    }
    if not available:
        result["failure_classes"] = sorted(c for c in classes if c)
    return result


# ---- Cloud Storage bulk reports --------------------------------------------


def list_objects(bucket: str, prefix: str, session=None) -> list[dict[str, Any]]:
    """List one bucket prefix, following pagination, metadata only."""
    name = _require_bucket(bucket)
    http = reporting_session(session)
    url = f"{STORAGE_BASE}/b/{name}/o"
    items: list[dict[str, Any]] = []
    page_token: str | None = None
    # ponytail: capped at MAX_LIST_PAGES pages (20k objects) per prefix. Cloud
    # Storage lists lexicographically, so a truncation would drop the newest
    # months first; raise the cap or list per month if a prefix ever gets close.
    for _ in range(MAX_LIST_PAGES):
        params: dict[str, Any] = {
            "prefix": prefix,
            "maxResults": 1000,
            "fields": "items(name,updated,size),nextPageToken",
        }
        if page_token:
            params["pageToken"] = page_token
        response = http.get(url, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        if not response.ok:
            raise _StorageFailure(_failure(response, surface="bulk_reports"))
        payload = response.json() if response.content else {}
        items.extend(payload.get("items", []) or [])
        page_token = payload.get("nextPageToken")
        if not page_token:
            break
    return items


class _StorageFailure(Exception):
    """Carries an already-classified storage failure back to the caller."""

    def __init__(self, payload: dict[str, Any]) -> None:
        super().__init__(payload.get("status", "request_failed"))
        self.payload = payload


def _download(bucket: str, object_name: str, session=None) -> bytes:
    http = reporting_session(session)
    url = f"{STORAGE_BASE}/b/{_require_bucket(bucket)}/o/{_quote(object_name)}"
    response = http.get(url, params={"alt": "media"}, timeout=REQUEST_TIMEOUT_SECONDS)
    if not response.ok:
        raise _StorageFailure(_failure(response, surface="bulk_reports"))
    return response.content


def _quote(object_name: str) -> str:
    from urllib.parse import quote

    return quote(object_name, safe="")


def _months(now: datetime, count: int = 2) -> list[str]:
    """Current month first, then the previous ones, as YYYYMM tokens."""
    tokens = []
    year, month = now.year, now.month
    for _ in range(count):
        tokens.append(f"{year:04d}{month:02d}")
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    return tokens


def _pick_object(items: Sequence[dict[str, Any]], months: Sequence[str]) -> dict[str, Any] | None:
    """Choose the newest month present, preferring its dimensionless overview.

    The overview file is the one whose rows are per-date rather than per-date
    per-dimension, so it answers a freshness question without a breakdown that
    could be summed into a metric that does not mean what it looks like.
    """
    for month in months:
        candidates = [item for item in items if f"_{month}" in item.get("name", "")]
        if not candidates:
            continue
        overview = [item for item in candidates if item.get("name", "").endswith("_overview.csv")]
        pool = overview or candidates
        return max(pool, key=lambda item: (item.get("updated", ""), item.get("name", "")))
    return None


# ---- CSV ------------------------------------------------------------------


def decode_report(raw: bytes) -> str:
    """Decode a Play bulk CSV, which Cloud Storage serves as UTF-16."""
    if raw.startswith(codecs.BOM_UTF16_LE) or raw.startswith(codecs.BOM_UTF16_BE):
        return raw.decode("utf-16")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("utf-16", errors="replace")


_DATE_FORMATS = ("%Y-%m-%d", "%b %d, %Y", "%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y")


def _parse_date(value: str) -> date | None:
    text = (value or "").strip().strip('"')
    if not text:
        return None
    # An ISO timestamp is a date with extra precision; take the date part.
    head = text.split("T")[0].split(" ")[0] if "T" in text else text
    for candidate in (head, text):
        for fmt in _DATE_FORMATS:
            try:
                return datetime.strptime(candidate, fmt).date()
            except ValueError:
                continue
    return None


def _date_columns(fieldnames: Iterable[str] | None) -> list[str]:
    return [name for name in (fieldnames or []) if name and "date" in name.lower()]


def read_csv_freshness(text: str) -> dict[str, Any]:
    """Find the newest logical data date a report CSV contains."""
    reader = csv.DictReader(io.StringIO(text))
    columns = [name for name in (reader.fieldnames or []) if name]
    if not columns:
        return {"status": "empty_report", "columns": [], "rows": 0}

    candidates = _date_columns(columns)
    if not candidates:
        return {"status": "no_date_column", "columns": columns, "rows": 0}

    latest: date | None = None
    latest_rows: list[dict[str, str]] = []
    used = ""
    rows = 0
    for row in reader:
        rows += 1
        if rows > MAX_ROWS:
            break
        for column in candidates:
            parsed = _parse_date(row.get(column) or "")
            if not parsed:
                continue
            # Every row sharing the newest date is kept, not just the first one
            # seen. A dimension-broken-down report has one row per dimension
            # value per date, and a rate derived from a single one of those rows
            # would describe one country, not the app.
            if latest is None or parsed > latest:
                latest, used, latest_rows = parsed, column, [row]
            elif parsed == latest:
                latest_rows.append(row)
            break

    if latest is None:
        status = "empty_report" if rows == 0 else "no_parsable_dates"
        return {"status": status, "columns": columns, "rows": rows}
    return {
        "status": "ok",
        "columns": columns,
        "rows": rows,
        "latest_data_date": latest.isoformat(),
        "date_column": used,
        "latest_rows": latest_rows,
    }


_NON_NUMERIC = re.compile(r"[^0-9.\-]")


def _number(value: str | None) -> float | None:
    if value is None:
        return None
    cleaned = _NON_NUMERIC.sub("", str(value).strip())
    if cleaned in ("", "-", ".", "-."):
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def store_listing_conversion(csv_result: dict[str, Any]) -> dict[str, Any]:
    """Derive a store-listing conversion rate only where one row supports it.

    Google replaced store-listing acquisitions with click-based reporting on
    10 July 2026, so a file can carry either column family. The numerator and
    denominator are taken from the same row of the same report - same date,
    same cohort, same model - and nothing is combined across the two models.
    """
    columns = csv_result.get("columns") or []
    rows = csv_result.get("latest_rows") or []
    lowered = {name.lower(): name for name in columns}

    def find(*needles: str) -> str | None:
        for lower, original in lowered.items():
            if all(needle in lower for needle in needles):
                return original
        return None

    visitors = find("visitor")
    acquisitions = find("acquisition")
    reported = find("conversion", "rate")
    clicks = find("click")
    ctr = find("click-through") or find("ctr")

    if visitors and acquisitions:
        numerator = sum(_number(row.get(acquisitions)) or 0.0 for row in rows)
        denominator = sum(_number(row.get(visitors)) or 0.0 for row in rows)
        rate = round(numerator / denominator, 6) if denominator else None
        return {
            "model": "legacy_visitors_acquisitions",
            "formula": (
                f"sum({acquisitions}) / sum({visitors}) over the "
                f"{len(rows)} row(s) of this report dated "
                f"{csv_result.get('latest_data_date')}"
            ),
            "numerator_column": acquisitions,
            "denominator_column": visitors,
            "rows_aggregated": len(rows),
            "conversion_rate": rate,
            # Google publishes a per-row rate of its own. It is echoed rather
            # than recomputed for a single row, and for a breakdown the summed
            # ratio above is reported instead, because averaging per-row rates
            # would weight a country with five visitors like one with five
            # thousand.
            "reported_conversion_rate_column": reported,
            "reported_conversion_rate": (
                _number(rows[0].get(reported)) if reported and len(rows) == 1 else None
            ),
            "validity": (
                "Both values come from one date of one report, so they share a "
                "cohort and a reporting model. Summing across the rows of a "
                "breakdown is only correct where that breakdown partitions the "
                "population, as country and traffic source do; check the named "
                "object before reusing the figure."
            ),
        }
    if clicks or ctr:
        return {
            "model": "click_intent_2026",
            "formula": "not computed",
            "available_columns": list(dict.fromkeys(name for name in (ctr, clicks) if name)),
            "conversion_rate": None,
            "detail": (
                "Since 10 July 2026 Play reports store-listing performance as "
                "unique install/open/pre-registration clicks and a click-through "
                "rate. Those are intent metrics, not installs, so they are not "
                "interchangeable with the retired acquisition conversion rate "
                "and are reported rather than recombined."
            ),
        }
    return {
        "model": "unknown",
        "formula": "not computed",
        "conversion_rate": None,
        "detail": "no visitor/acquisition or click column found in this report",
    }


# ---- financial -------------------------------------------------------------

_FINANCIAL_STATUS_COLUMNS = ("financial status", "transaction type", "refund type")


def summarize_financial(text: str) -> dict[str, Any]:
    """Summarize a financial export without returning any buyer row.

    Estimated-sales and earnings rows carry buyer city, region, and postal code.
    Only the newest transaction date, a row count, and transaction-class counts
    cross the agent boundary.
    """
    result = read_csv_freshness(text)
    result.pop("latest_rows", None)
    if result.get("status") != "ok":
        return result
    reader = csv.DictReader(io.StringIO(text))
    classes: dict[str, dict[str, int]] = {}
    for column in reader.fieldnames or []:
        if column and column.strip().lower() in _FINANCIAL_STATUS_COLUMNS:
            classes[column] = {}
    rows = 0
    for row in reader:
        rows += 1
        if rows > MAX_ROWS:
            break
        for column, counts in classes.items():
            key = (row.get(column) or "").strip() or "(blank)"
            counts[key] = counts.get(key, 0) + 1
    result["transaction_class_counts"] = classes
    result["pii_policy"] = "aggregates-only; buyer rows are never returned"
    return result


def _zip_reports(raw: bytes) -> list[tuple[str, str]]:
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        members = [info for info in archive.infolist() if not info.is_dir()]
        return [
            (info.filename, decode_report(archive.read(info)))
            for info in sorted(members, key=lambda info: info.filename)
            if info.file_size <= MAX_OBJECT_BYTES
        ]


# ---- one report family -----------------------------------------------------


def _probe_report(
    bucket: str,
    directory: str,
    filename_prefix: str,
    tz_name: str,
    tz_basis: str,
    months: Sequence[str],
    session,
    now: datetime,
    *,
    financial: bool,
) -> dict[str, Any]:
    prefix = f"{directory}{filename_prefix}"
    try:
        items = list_objects(bucket, prefix, session=session)
    except _StorageFailure as failure:
        return failure.payload

    if not items:
        return {
            "status": "report_not_generated",
            "prefix": prefix,
            "detail": "the bucket is readable but holds no object with this prefix",
        }

    chosen = _pick_object(items, months)
    if chosen is None:
        newest = max(items, key=lambda item: item.get("updated", ""))
        return {
            "status": "report_not_generated_for_recent_months",
            "prefix": prefix,
            "months_checked": list(months),
            "newest_object": newest.get("name"),
            "newest_object_updated_at": newest.get("updated"),
        }

    size = int(chosen.get("size") or 0)
    if size > MAX_OBJECT_BYTES:
        return {
            "status": "report_too_large",
            "object": chosen.get("name"),
            "object_size_bytes": size,
        }

    try:
        raw = _download(bucket, chosen["name"], session=session)
    except _StorageFailure as failure:
        payload = dict(failure.payload)
        payload["object"] = chosen.get("name")
        return payload

    name = chosen.get("name", "")
    if name.endswith(".zip"):
        try:
            members = _zip_reports(raw)
        except zipfile.BadZipFile:
            return {"status": "malformed_report", "object": name, "detail": "not a readable zip"}
        parsed = [summarize_financial(text) for _, text in members]
        usable = [entry for entry in parsed if entry.get("status") == "ok"]
        result = (
            max(usable, key=lambda entry: entry["latest_data_date"])
            if usable
            else (parsed[0] if parsed else {"status": "empty_report"})
        )
        result = dict(result)
        result["members"] = [member for member, _ in members]
    else:
        text = decode_report(raw)
        result = summarize_financial(text) if financial else read_csv_freshness(text)

    result["object"] = name
    result["object_updated_at"] = chosen.get("updated")
    result["object_size_bytes"] = size
    result["timezone"] = tz_name
    result["timezone_basis"] = tz_basis

    latest = result.get("latest_data_date")
    if latest:
        result.update(_lag_from_date(date.fromisoformat(latest), tz_name, now))
    return result


def _compact(entry: dict[str, Any]) -> dict[str, Any]:
    """Collapse the retained newest-date rows into something worth reading."""
    rows = entry.pop("latest_rows", None)
    if rows is None:
        return entry
    entry["latest_rows_count"] = len(rows)
    if len(rows) == 1:
        entry["latest_row"] = rows[0]
    return entry


# ---- top level -------------------------------------------------------------


def freshness(
    profile_slug: str,
    *,
    session=None,
    now: datetime | None = None,
    include_financial: bool = True,
) -> dict[str, Any]:
    """Probe every official Play reporting surface for one profile, read-only."""
    profile = config.load_profile(profile_slug)
    package = _require_package(profile.package_name or "")
    moment = now or datetime.now(timezone.utc)
    http = reporting_session(session)

    report: dict[str, Any] = {
        "profile": profile.slug,
        "package_name": package,
        "checked_at": moment.isoformat(),
        "mutations": "none",
        "console_visible_through": "operator_input_required",
        "operator_comparison_instructions": CONSOLE_COMPARISON,
        "sources": {},
    }

    report["sources"]["developer_reporting"] = developer_reporting_freshness(
        package, session=http, now=moment
    )

    bucket = reporting_bucket(profile)
    if not bucket:
        unavailable = {
            "available": False,
            "status": "bucket_not_configured",
            "detail": (
                "Play publishes bulk reports to a per-developer Cloud Storage "
                "bucket whose id no public API exposes. Read it from Play "
                "Console > Download reports (the Cloud Storage URI, such as "
                "pubsite_prod_rev_0123456789) and set it with "
                f"`mra profile set --slug {profile.slug} --play-reporting-bucket <id>` "
                f"or the {BUCKET_ENV} environment variable. The bucket id is not a secret."
            ),
        }
        report["sources"]["bulk_reports"] = dict(unavailable)
        report["sources"]["financial"] = dict(unavailable)
        return report

    months = _months(moment)
    bulk: dict[str, Any] = {
        "available": True,
        "surface": "play-bulk-reports-cloud-storage",
        "scope": auth.GCS_READ_SCOPE,
        "bucket": bucket,
        "months_checked": list(months),
        "reports": {},
    }
    for name, (directory, filename, tz_name, tz_basis) in BULK_REPORTS.items():
        bulk["reports"][name] = _probe_report(
            bucket,
            directory,
            filename.format(package=package),
            tz_name,
            tz_basis,
            months,
            http,
            moment,
            financial=(name == "subscriptions"),
        )
    store = bulk["reports"].get("store_performance", {})
    if store.get("status") == "ok":
        store["store_listing_conversion"] = store_listing_conversion(store)
    for entry in bulk["reports"].values():
        _compact(entry)
    bulk["available"] = any(
        entry.get("status") not in ("authentication_failed", "permission_denied", "api_not_enabled")
        for entry in bulk["reports"].values()
    )
    report["sources"]["bulk_reports"] = bulk

    if not include_financial:
        report["sources"]["financial"] = {"available": False, "status": "skipped_by_caller"}
        return report

    financial: dict[str, Any] = {
        "available": True,
        "surface": "play-financial-reports-cloud-storage",
        "bucket": bucket,
        "pii_policy": "aggregates-only; buyer rows are never returned",
        "reports": {},
    }
    for name, (directory, filename, tz_name, tz_basis) in FINANCIAL_REPORTS.items():
        financial["reports"][name] = _probe_report(
            bucket,
            directory,
            filename,
            tz_name,
            tz_basis,
            months,
            http,
            moment,
            financial=True,
        )
        _compact(financial["reports"][name])
    financial["available"] = any(
        entry.get("status") not in ("authentication_failed", "permission_denied", "api_not_enabled")
        for entry in financial["reports"].values()
    )
    report["sources"]["financial"] = financial
    return report

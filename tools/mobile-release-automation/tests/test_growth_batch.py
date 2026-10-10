"""Single-approval Play growth batch validation and fail-closed execution."""

from __future__ import annotations

from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
import hashlib
import io
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import cli, growth_batch, play  # noqa: E402


def listing(locale: str, name: str) -> dict:
    return {
        "language": locale, "title": name, "shortDescription": f"{name} short",
        "fullDescription": f"{name} full description",
    }


def create(locale: str, name: str) -> dict:
    return {"kind": "listing-create", "profile": "demo",
            "package_name": "com.example.app", "language": locale,
            "desired": listing(locale, name)}


def update(locale: str, old: str, new: str) -> dict:
    return {"kind": "listing-update", "profile": "demo",
            "package_name": "com.example.app", "language": locale,
            "expected_current": listing(locale, old), "desired": listing(locale, new)}


def manifest(actions: list[dict]) -> dict:
    now = datetime.now(timezone.utc)
    fmt = lambda t: t.isoformat(timespec="seconds").replace("+00:00", "Z")
    return {
        "schema_version": 1, "created_at": fmt(now - timedelta(minutes=1)),
        "expires_at": fmt(now + timedelta(days=1)), "actions": actions,
    }


def write_manifest(directory: str, value: dict) -> tuple[str, str]:
    path = Path(directory) / "approved.json"
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return str(path), hashlib.sha256(path.read_bytes()).hexdigest()


class MemoryPlayManagement:
    def __init__(self, initial: list[dict] | None = None):
        self.listings = {i["language"]: dict(i) for i in (initial or [])}
        self.writes: list[tuple] = []
        self.fail_update = False

    def list_listings(self):
        return [{"language": language} for language in self.listings]

    def get_listing(self, language):
        if language not in self.listings:
            raise play.PlayError("listing not found")
        return dict(self.listings[language])

    def create_listing(self, language, *, title, short_description, full_description,
                       dry_run=True):
        if language in self.listings:
            raise play.PlayError("already exists")
        self.listings[language] = {
            "language": language, "title": title,
            "shortDescription": short_description, "fullDescription": full_description,
        }
        self.writes.append(("create", language))
        return {"committed": not dry_run}

    def update_listing(self, language, *, title, short_description, full_description,
                       dry_run=True, expected_current=None, video=None):
        if self.fail_update:
            raise play.PlayError("simulated backend error")
        current = self.listings[language]
        for field in ("title", "shortDescription", "fullDescription"):
            if current[field] != expected_current[field]:
                raise play.PlayError("stale")
        self.listings[language] = {
            "language": language, "title": title,
            "shortDescription": short_description, "fullDescription": full_description,
        }
        if video:
            self.listings[language]["video"] = video
        self.writes.append(("update", language))
        return {"committed": not dry_run}


class BatchValidationTest(unittest.TestCase):
    def test_exact_hash_and_expiry(self):
        with tempfile.TemporaryDirectory() as directory:
            path, digest = write_manifest(directory, manifest([create("es-ES", "Dados")]))
            self.assertEqual(len(growth_batch.load_manifest(path, digest)["actions"]), 1)
            with self.assertRaisesRegex(growth_batch.BatchError, "differ"):
                growth_batch.load_manifest(path, "a" * 64)
            Path(path).write_text(Path(path).read_text() + " ")
            with self.assertRaisesRegex(growth_batch.BatchError, "differ"):
                growth_batch.load_manifest(path, digest)
            expired = manifest([create("es-ES", "Dados")])
            expired["expires_at"] = "2020-01-01T00:00:00Z"
            path2, sha2 = write_manifest(directory, expired)
            with self.assertRaises(growth_batch.BatchError):
                growth_batch.load_manifest(path2, sha2)

    def test_duplicate_locale_and_unsupported_action_fail(self):
        for actions in (
            [create("es-ES", "A"), create("es-ES", "B")],
            [dict(create("es-ES", "A"), kind="release")],
            [dict(create("es-ES", "A"), extra="unexpected")],
        ):
            with self.subTest(actions=actions), tempfile.TemporaryDirectory() as directory:
                path, sha = write_manifest(directory, manifest(actions))
                with self.assertRaises(growth_batch.BatchError):
                    growth_batch.load_manifest(path, sha)

    def test_utf16_validation_and_locale_safety(self):
        for item in (
            dict(create("es-ES", "A"), language="../en-US"),
            dict(create("es-ES", "A"), desired=listing("es-ES", "😀" * 16)),
            dict(create("es-ES", "A"), desired=dict(listing("es-ES", "A"), video="x")),
        ):
            with self.subTest(item=item), tempfile.TemporaryDirectory() as directory:
                path, sha = write_manifest(directory, manifest([item]))
                with self.assertRaises(growth_batch.BatchError):
                    growth_batch.load_manifest(path, sha)


class BatchExecutionTest(unittest.TestCase):
    def setUp(self):
        self.profile_patch = mock.patch.object(
            growth_batch.config, "load_profile",
            return_value=SimpleNamespace(package_name="com.example.app"),
        )
        self.profile_patch.start()

    def tearDown(self):
        self.profile_patch.stop()

    def test_all_actions_preflight_then_applied_without_dialogs(self):
        manager = MemoryPlayManagement([listing("de-DE", "Alt")])
        actions = [create("es-ES", "Dados"), update("de-DE", "Alt", "Neu")]
        with mock.patch.object(
            growth_batch.play_management, "PlayManagementClient", return_value=manager
        ), mock.patch.object(growth_batch, "_apply_action", wraps=growth_batch._apply_action):
            result = growth_batch.apply(manifest(actions))
        self.assertEqual(result["status"], "verified")
        self.assertEqual(manager.writes, [("create", "es-ES"), ("update", "de-DE")])
        self.assertEqual([r["verified"] for r in result["results"]], [True, True])

    def test_preflight_drift_prevents_every_write(self):
        manager = MemoryPlayManagement([listing("de-DE", "Someone else")])
        with mock.patch.object(
            growth_batch.play_management, "PlayManagementClient", return_value=manager
        ):
            with self.assertRaisesRegex(growth_batch.BatchError, "drifted"):
                growth_batch.apply(manifest([
                    create("es-ES", "Dados"), update("de-DE", "Alt", "Neu"),
                ]))
        self.assertEqual(manager.writes, [])

    def test_partial_failure_stops_and_keeps_reconciled_actions(self):
        manager = MemoryPlayManagement([listing("de-DE", "Alt")])
        manager.fail_update = True
        with mock.patch.object(
            growth_batch.play_management, "PlayManagementClient", return_value=manager
        ):
            result = growth_batch.apply(manifest([
                create("es-ES", "Dados"),
                update("de-DE", "Alt", "Neu"),
                create("it-IT", "Dadi"),
            ]))
        self.assertEqual(result["status"], "partial_failure")
        self.assertEqual(result["stopped_at"], 1)
        self.assertEqual(manager.writes, [("create", "es-ES")])
        # A retry with the exact approved plan reads live state first and skips
        # the already-verified creation; it does not reissue the same PUT.
        manager.fail_update = False
        with mock.patch.object(
            growth_batch.play_management, "PlayManagementClient", return_value=manager
        ):
            resumed = growth_batch.apply(manifest([
                create("es-ES", "Dados"),
                update("de-DE", "Alt", "Neu"),
                create("it-IT", "Dadi"),
            ]))
        self.assertEqual(resumed["status"], "verified")
        self.assertEqual(resumed["results"][0]["status"], "already_applied")
        self.assertEqual(manager.writes, [
            ("create", "es-ES"), ("update", "de-DE"), ("create", "it-IT")
        ])

    def test_manifest_profile_mismatch_prevents_writes(self):
        manager = MemoryPlayManagement()
        with mock.patch.object(growth_batch.config, "load_profile",
                               return_value=SimpleNamespace(package_name="com.wrong.app")):
            with mock.patch.object(
                growth_batch.play_management, "PlayManagementClient", return_value=manager
            ):
                with self.assertRaisesRegex(growth_batch.BatchError, "profile/package mismatch"):
                    growth_batch.apply(manifest([create("es-ES", "Dados")]))
        self.assertFalse(manager.writes)

    def test_pricing_plan_is_only_applied_by_exact_plan_id(self):
        plan_id = "a" * 64
        product = {"purchaseOptions": []}
        plan = {
            "plan_id": plan_id, "package_name": "com.example.app", "profile": "demo",
            "product_id": "pro", "purchase_option_id": "buy",
            "source_fingerprint": "f", "regions_version": "2026/10",
            "changes": [{"region_code": "IN", "current_price": {"units": "200"},
                         "proposed_price": {"units": "70"}}],
        }
        action = {"kind": "pricing-apply", "profile": "demo",
                  "package_name": "com.example.app", "plan_id": plan_id}
        with mock.patch.object(growth_batch.regional_pricing, "load_plan", return_value=plan), \
             mock.patch.object(growth_batch.play_module, "PlayClient") as client, \
             mock.patch.object(growth_batch.regional_pricing, "_matches_plan", return_value=False), \
             mock.patch.object(growth_batch.regional_pricing, "_source_fingerprint", return_value="f"), \
             mock.patch.object(growth_batch.regional_pricing, "_current_region_version", return_value="2026/10"), \
             mock.patch.object(growth_batch.regional_pricing, "apply_one_time_product_plan",
                               return_value={"status": "applied", "verified": True}) as apply:
            client.return_value.get_one_time_product.return_value = product
            result = growth_batch.apply(manifest([action]))
        self.assertEqual(result["status"], "verified")
        apply.assert_called_once_with("com.example.app", plan_id, profile="demo")


class BatchCliGateTest(unittest.TestCase):
    def test_single_apply_gate_requires_yes_and_exact_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            path, sha = write_manifest(directory, manifest([create("es-ES", "Dados")]))
            args = cli.build_parser().parse_args(
                ["play", "growth-batch-apply", "--manifest", path, "--sha256", sha]
            )
            with mock.patch.object(cli.growth_batch, "apply") as execute:
                with self.assertRaisesRegex(SystemExit, "without --yes"):
                    args.func(args)
            execute.assert_not_called()

    def test_exact_approved_plan_applies_once_without_native_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            path, sha = write_manifest(directory, manifest([create("es-ES", "Dados")]))
            args = cli.build_parser().parse_args(
                ["--yes", "play", "growth-batch-apply",
                 "--manifest", path, "--sha256", sha]
            )
            with mock.patch.object(cli.growth_batch, "apply",
                                   return_value={"status": "verified", "results": []}) as execute:
                with redirect_stdout(io.StringIO()) as stdout:
                    code = args.func(args)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["manifest_sha256"], sha)
        execute.assert_called_once()


if __name__ == "__main__":
    unittest.main()

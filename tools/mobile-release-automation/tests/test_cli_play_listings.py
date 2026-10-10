"""CLI parser coverage for read-only Play listing commands."""

from __future__ import annotations

from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock
import hashlib
import io
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import cli  # noqa: E402


class PlayListingCliTest(unittest.TestCase):
    def test_listings_command_routes_to_read_only_handler(self) -> None:
        args = cli.build_parser().parse_args(["play", "listings", "--profile", "medtick"])
        self.assertEqual(args.profile, "medtick")
        self.assertIs(args.func, cli.cmd_play_listings)

    def test_listing_command_accepts_locale(self) -> None:
        args = cli.build_parser().parse_args(
            ["play", "listing", "--profile", "medtick", "--language", "de-DE"]
        )
        self.assertEqual(args.profile, "medtick")
        self.assertEqual(args.language, "de-DE")
        self.assertIs(args.func, cli.cmd_play_listing)

    def test_listing_defaults_to_en_us(self) -> None:
        args = cli.build_parser().parse_args(["play", "listing", "--profile", "medtick"])
        self.assertEqual(args.language, "en-US")

    def test_publish_accepts_multiple_aabs_for_one_atomic_release(self) -> None:
        args = cli.build_parser().parse_args(
            [
                "--yes",
                "play",
                "publish",
                "--profile",
                "wristbridge",
                "--aab",
                "/tmp/phone.aab",
                "--aab",
                "/tmp/wear.aab",
            ]
        )
        self.assertEqual(args.aab, ["/tmp/phone.aab", "/tmp/wear.aab"])
        self.assertIs(args.func, cli.cmd_play_publish)

    def test_publish_set_accepts_separate_phone_and_wear_tracks(self) -> None:
        args = cli.build_parser().parse_args(
            [
                "--yes",
                "play",
                "publish-set",
                "--profile",
                "jetlag",
                "--track-aab",
                "internal=/tmp/phone.aab",
                "--track-aab",
                "wear:internal=/tmp/wear.aab",
            ]
        )
        self.assertEqual(
            args.track_aab,
            ["internal=/tmp/phone.aab", "wear:internal=/tmp/wear.aab"],
        )
        self.assertIs(args.func, cli.cmd_play_publish_set)

    def test_listing_create_routes_to_guarded_handler(self) -> None:
        args = cli.build_parser().parse_args(
            ["play", "listing-create", "--profile", "wristrandom",
             "--language", "es-ES", "--body", "/tmp/es-ES.json",
             "--sha256", "a" * 64, "--dry-run"]
        )
        self.assertIs(args.func, cli.cmd_play_listing_create)
        self.assertTrue(args.dry_run)
        self.assertFalse(args.yes)

    def test_listing_update_routes_to_mutating_handler(self) -> None:
        args = cli.build_parser().parse_args(
            [
                "--yes",
                "play",
                "listing-update",
                "--package",
                "com.example.app",
                "--language",
                "de-DE",
                "--body",
                "/tmp/desired.json",
                "--expected-current",
                "/tmp/current.json",
            ]
        )
        self.assertTrue(args.yes)
        self.assertEqual(args.language, "de-DE")
        self.assertIs(args.func, cli.cmd_play_listing_update)


class PlayListingUpdateCliTest(unittest.TestCase):
    CURRENT = {
        "language": "en-US",
        "title": "Old",
        "shortDescription": "Short",
        "fullDescription": "Full",
    }
    DESIRED = {
        "language": "en-US",
        "title": "New",
        "shortDescription": "Short",
        "fullDescription": "Full",
    }

    def _files(self, directory: str) -> tuple[str, str]:
        expected = Path(directory) / "expected.json"
        desired = Path(directory) / "desired.json"
        expected.write_text(json.dumps(self.CURRENT), encoding="utf-8")
        desired.write_text(json.dumps(self.DESIRED), encoding="utf-8")
        return str(expected), str(desired)

    def test_preauthorized_listing_update_reads_back_exact_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            expected, desired = self._files(directory)
            args = cli.build_parser().parse_args(
                [
                    "--yes",
                    "play",
                    "listing-update",
                    "--package",
                    "com.example.app",
                    "--language",
                    "en-US",
                    "--body",
                    desired,
                    "--expected-current",
                    expected,
                ]
            )
            client = mock.Mock()
            client.get_listing.side_effect = [dict(self.CURRENT), dict(self.DESIRED)]
            client.update_listing.return_value = {"committed": True}
            with mock.patch.object(
                cli.play_management, "PlayManagementClient", return_value=client
            ), redirect_stdout(io.StringIO()):
                code = args.func(args)

        self.assertEqual(code, 0)
        client.update_listing.assert_called_once_with(
            "en-US",
            title="New",
            short_description="Short",
            full_description="Full",
            dry_run=False,
        )
        self.assertEqual(client.get_listing.call_count, 2)

    def test_listing_update_refuses_drift_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            expected, desired = self._files(directory)
            args = cli.build_parser().parse_args(
                [
                    "--yes",
                    "play",
                    "listing-update",
                    "--package",
                    "com.example.app",
                    "--language",
                    "en-US",
                    "--body",
                    desired,
                    "--expected-current",
                    expected,
                ]
            )
            client = mock.Mock()
            drifted = dict(self.CURRENT)
            drifted["title"] = "Someone changed this"
            client.get_listing.return_value = drifted
            with mock.patch.object(
                cli.play_management, "PlayManagementClient", return_value=client
            ), redirect_stdout(io.StringIO()):
                code = args.func(args)

        self.assertEqual(code, 2)
        client.update_listing.assert_not_called()

class PlayListingCreateCliTest(unittest.TestCase):
    DESIRED = {
        "language": "es-ES",
        "title": "Dados",
        "shortDescription": "Dados en tu reloj",
        "fullDescription": "Lanza dados en tu reloj.",
    }

    def _args(self, directory: str, *, dry_run: bool = False, digest: str | None = None):
        path = Path(directory) / "es-ES.json"
        path.write_text(json.dumps(self.DESIRED, ensure_ascii=False), encoding="utf-8")
        approved = digest or hashlib.sha256(path.read_bytes()).hexdigest()
        parts = [
            "play", "listing-create", "--package", "com.example.app",
            "--language", "es-ES", "--body", str(path), "--sha256", approved,
        ]
        if dry_run:
            parts.append("--dry-run")
        else:
            parts.insert(0, "--yes")
        return cli.build_parser().parse_args(parts)

    def test_create_verified_exact_payload(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = self._args(directory)
            client = mock.Mock()
            client.create_listing.return_value = {"committed": True}
            client.get_listing.return_value = dict(self.DESIRED)
            with mock.patch.object(
                cli.play_management, "PlayManagementClient", return_value=client
            ), redirect_stdout(io.StringIO()) as output:
                code = args.func(args)
            response = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(response["status"], "verified")
        self.assertEqual(response["publication_state"], "not_verified_by_api")
        client.create_listing.assert_called_once_with(
            "es-ES", title="Dados", short_description="Dados en tu reloj",
            full_description="Lanza dados en tu reloj.", dry_run=False
        )
        client.get_listing.assert_called_once_with("es-ES")

    def test_invalid_sha_refuses_before_any_platform_call(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = self._args(directory, digest="0" * 64)
            with mock.patch.object(
                cli.play_management, "PlayManagementClient"
            ) as factory:
                with self.assertRaisesRegex(SystemExit, "SHA-256 differs"):
                    args.func(args)
        factory.assert_not_called()

    def test_create_needs_explicit_yes_or_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = self._args(directory)
            args.yes = False
            with mock.patch.object(
                cli.play_management, "PlayManagementClient"
            ) as factory:
                with self.assertRaisesRegex(SystemExit, "without --yes"):
                    args.func(args)
        factory.assert_not_called()

    def test_create_dry_run_does_not_claim_publication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = self._args(directory, dry_run=True)
            client = mock.Mock()
            client.create_listing.return_value = {"committed": False}
            with mock.patch.object(
                cli.play_management, "PlayManagementClient", return_value=client
            ), redirect_stdout(io.StringIO()) as output:
                code = args.func(args)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "validated")
        client.get_listing.assert_not_called()

    def test_create_blocks_invalid_locale_and_overlong_copy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = self._args(directory)
            args.language = "../en-US"
            with self.assertRaisesRegex(SystemExit, "invalid Play listing locale"):
                args.func(args)
            args.language = "es-ES"
            path = Path(args.body)
            changed = dict(self.DESIRED, title="X" * 31)
            path.write_text(json.dumps(changed), encoding="utf-8")
            args.sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(SystemExit, "invalid title"):
                args.func(args)

    def test_existing_listing_update_preserves_optional_video(self) -> None:
        current = {
            "language": "en-US", "title": "Old", "shortDescription": "Short",
            "fullDescription": "Full", "video": "https://youtu.be/abc123",
        }
        desired = dict(current, title="New")
        desired.pop("video")
        with tempfile.TemporaryDirectory() as directory:
            before = Path(directory) / "before.json"
            after = Path(directory) / "after.json"
            before.write_text(json.dumps({k: v for k, v in current.items() if k != "video"}))
            after.write_text(json.dumps(desired))
            args = cli.build_parser().parse_args(
                ["--yes", "play", "listing-update", "--package", "com.example.app",
                 "--language", "en-US", "--body", str(after),
                 "--expected-current", str(before)]
            )
            client = mock.Mock()
            client.get_listing.side_effect = [current, dict(desired, video=current["video"])]
            client.update_listing.return_value = {"committed": True}
            with mock.patch.object(
                cli.play_management, "PlayManagementClient", return_value=client
            ), redirect_stdout(io.StringIO()):
                code = args.func(args)
        self.assertEqual(code, 0)
        self.assertEqual(
            client.update_listing.call_args.kwargs["video"], "https://youtu.be/abc123"
        )



if __name__ == "__main__":
    unittest.main()

"""CLI parser coverage for read-only Play listing commands."""

from __future__ import annotations

from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock
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


if __name__ == "__main__":
    unittest.main()

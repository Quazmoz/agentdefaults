"""CLI parser coverage for read-only Play listing commands."""

from __future__ import annotations

from pathlib import Path
import sys
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


if __name__ == "__main__":
    unittest.main()

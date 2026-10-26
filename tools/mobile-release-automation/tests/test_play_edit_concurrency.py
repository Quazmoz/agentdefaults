"""Concurrent MRA calls must not invalidate each other's Play edits.

Play allows one open edit per identity per app and deletes the older one when
another is created. These tests stand in for Play with a fake that enforces that
rule, then race real PlayClient edits against it.
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mra import play, play_management  # noqa: E402
from tests.fakes import FakeResponse, FakeSession, ok  # noqa: E402


class OneEditPerAppPlay:
    """Fake Play edits API: a new edit for an app deletes that app's open edit."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.open: dict[str, str] = {}  # package -> edit id
        self.counter = 0
        self.invalidated = 0

    def session(self, package: str) -> FakeSession:
        def create(url, **_):
            with self.lock:
                self.counter += 1
                edit_id = f"{package}-e{self.counter}"
                if package in self.open:
                    self.invalidated += 1
                self.open[package] = edit_id
            return FakeResponse(200, {"id": edit_id})

        def use(url, **_):
            edit_id = url.split("/edits/")[1].split("/")[0].split(":")[0]
            time.sleep(0.02)  # widen the race window
            with self.lock:
                alive = self.open.get(package) == edit_id
            if not alive:
                return FakeResponse(400, {"error": {
                    "code": 400, "message": "This Edit has been deleted.",
                    "status": "FAILED_PRECONDITION"}})
            return FakeResponse(200, {"listings": [{"language": "en-US"}], "tracks": []})

        def delete(url, **_):
            edit_id = url.split("/edits/")[1]
            with self.lock:
                if self.open.get(package) == edit_id:
                    del self.open[package]
            return FakeResponse(200, {})

        return FakeSession({
            ("POST", "/edits"): create,
            ("GET", "/edits/"): use,
            ("DELETE", "/edits/"): delete,
        })


def read_listings(fake: OneEditPerAppPlay, package: str, errors: list) -> None:
    client = play.PlayClient(package, session=fake.session(package))
    try:
        play_management.PlayManagementClient(package, client=client).list_listings()
    except play.PlayError as error:
        errors.append(error)


class ConcurrentEditTest(unittest.TestCase):
    def race(self, packages: list[str]) -> tuple[OneEditPerAppPlay, list]:
        fake, errors = OneEditPerAppPlay(), []
        threads = [threading.Thread(target=read_listings, args=(fake, p, errors)) for p in packages]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        return fake, errors

    def test_competing_reads_for_one_app_take_turns(self) -> None:
        fake, errors = self.race(["com.example.app"] * 6)
        self.assertEqual(errors, [])
        self.assertEqual(fake.invalidated, 0)

    def test_reads_for_different_apps_still_overlap(self) -> None:
        inside = threading.Barrier(2, timeout=5)
        errors: list = []

        def hold(package: str) -> None:
            client = play.PlayClient(package, session=OneEditPerAppPlay().session(package))
            try:
                with client.edit(commit=False, validate=False):
                    inside.wait()  # deadlocks (BrokenBarrierError) if edits were globally serialized
            except threading.BrokenBarrierError as error:
                errors.append(error)

        threads = [threading.Thread(target=hold, args=(p,)) for p in ("com.example.one", "com.example.two")]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertEqual(errors, [])

    def test_lock_is_released_when_the_edit_body_fails(self) -> None:
        fake = OneEditPerAppPlay()
        client = play.PlayClient("com.example.app", session=fake.session("com.example.app"))
        with self.assertRaises(RuntimeError):
            with client.edit(commit=False, validate=False):
                raise RuntimeError("body failed")
        done = threading.Event()
        threading.Thread(target=lambda: (read_listings(fake, "com.example.app", []), done.set())).start()
        self.assertTrue(done.wait(5), "lock leaked after a failed edit")

    def test_separate_mra_processes_take_turns(self) -> None:
        # Portfolio reads run as separate `mra` processes, so the lock must hold across them.
        holder = (
            "import sys, time; sys.path.insert(0, sys.argv[1]); from mra import play\n"
            "with play._package_edit_lock('com.example.app'):\n"
            "    print('in', time.monotonic(), flush=True); time.sleep(0.3)\n"
            "    print('out', time.monotonic(), flush=True)\n"
        )
        root = str(Path(__file__).resolve().parents[1])
        procs = [subprocess.Popen([sys.executable, "-c", holder, root], stdout=subprocess.PIPE, text=True)
                 for _ in range(2)]
        events = sorted((float(t), kind) for p in procs
                        for kind, t in (line.split() for line in p.communicate(timeout=10)[0].splitlines()))
        self.assertEqual([kind for _, kind in events], ["in", "out", "in", "out"])

    def test_package_name_cannot_escape_the_lock_directory(self) -> None:
        session = FakeSession({})
        for bad in ("../../etc/passwd", "com.example/../x", "", "noseparator"):
            with self.assertRaises(play.PlayError):
                with play.PlayClient(bad, session=session).edit(commit=False):
                    pass
        self.assertEqual(session.calls, [])  # refused before any Play request


class EditFailureClassificationTest(unittest.TestCase):
    def test_deleted_edit_is_not_reported_as_a_malformed_request(self) -> None:
        classification, checks = play.classify_play_failure(
            400, "FAILED_PRECONDITION", "This Edit has been deleted.")
        self.assertEqual(classification, "edit_invalidated")
        self.assertTrue(any("re-read live state" in check for check in checks))

    def test_review_submission_blocked(self) -> None:
        message = ("Changes cannot be sent for review automatically. Please set the "
                   "query parameter changesNotSentForReview to true.")
        classification, checks = play.classify_play_failure(400, "FAILED_PRECONDITION", message)
        self.assertEqual(classification, "review_submission_blocked")
        self.assertTrue(any("operator decision" in check for check in checks))

    def test_changes_already_in_review(self) -> None:
        message = ("You already have changes in review. Cancel this review or wait for it "
                   "to complete before you try again.")
        classification, _ = play.classify_play_failure(400, "FAILED_PRECONDITION", message)
        self.assertEqual(classification, "changes_in_review")


class ListingCommitReviewBehaviorTest(unittest.TestCase):
    def routes(self) -> dict:
        return {
            ("POST", "/edits"): ok({"id": "edit-1"}),
            ("GET", "edit-1/listings/de-DE"): ok({"language": "de-DE", "title": "a",
                                                  "shortDescription": "b", "fullDescription": "c"}),
            ("GET", "edit-1/listings"): ok({"listings": [{"language": "en-US"}]}),
            ("PUT", "/listings/"): ok({"language": "de-DE"}),
            ("POST", ":validate"): ok({}),
            ("POST", ":commit"): ok({}),
            ("DELETE", "/edits/"): ok({}),
        }

    def commit_params(self, session: FakeSession) -> dict:
        return next(c for c in session.calls if c["url"].endswith(":commit"))["params"]

    def test_listing_create_and_update_never_cancel_a_review(self) -> None:
        fields = {"title": "T", "short_description": "S", "full_description": "F", "dry_run": False}
        for write in ("create", "update"):
            session = FakeSession(self.routes())
            manager = play_management.PlayManagementClient(
                "com.example.app", client=play.PlayClient("com.example.app", session=session))
            if write == "create":
                manager.create_listing("de-DE", **fields)
            else:
                manager.update_listing("de-DE", **fields, expected_current={
                    "title": "a", "shortDescription": "b", "fullDescription": "c", "video": None})
            self.assertEqual(self.commit_params(session),
                             {"changesInReviewBehavior": "ERROR_IF_IN_REVIEW"}, write)


if __name__ == "__main__":
    unittest.main()

"""Native human approval for high-risk local MCP actions.

The model cannot satisfy this gate by passing a boolean. On macOS a real local
operator must click Approve in a native dialog. On unsupported/headless hosts the
action is refused rather than silently downgraded.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from typing import Any

APPLESCRIPT = r'''
on run argv
    set dialogTitle to item 1 of argv
    set dialogText to item 2 of argv
    try
        set response to display dialog dialogText with title dialogTitle buttons {"Cancel", "Approve"} default button "Cancel" cancel button "Cancel" with icon caution giving up after 120
        if gave up of response then return "timeout"
        if button returned of response is "Approve" then return "approved"
        return "cancelled"
    on error number -128
        return "cancelled"
    end try
end run
'''


def status() -> dict[str, str]:
    if sys.platform == "darwin" and shutil.which("osascript"):
        return {"status": "ready", "mode": "macos-native-dialog"}
    return {
        "status": "unavailable",
        "mode": "deny-high-risk",
        "detail": "high-risk MCP mutations require a local macOS approval dialog",
    }


def request(title: str, detail: str) -> dict[str, Any]:
    """Request a real local approval without exposing an agent-controlled bypass."""
    current = status()
    if current["status"] != "ready":
        return {"approved": False, **current}

    try:
        result = subprocess.run(
            ["osascript", "-e", APPLESCRIPT, title, detail],
            capture_output=True,
            text=True,
            timeout=130,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return {
            "approved": False,
            "status": "unavailable",
            "mode": "deny-high-risk",
            "detail": "native approval prompt could not be completed",
        }

    outcome = result.stdout.strip().lower()
    if result.returncode == 0 and outcome == "approved":
        return {"approved": True, "status": "approved", "mode": "macos-native-dialog"}
    if outcome == "timeout":
        return {"approved": False, "status": "timeout", "mode": "macos-native-dialog"}
    return {"approved": False, "status": "cancelled", "mode": "macos-native-dialog"}

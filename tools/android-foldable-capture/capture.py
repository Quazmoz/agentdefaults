#!/usr/bin/env python3
"""Stage native, traceable PNGs from the two official Android foldable AVDs."""

import argparse
import hashlib
import json
import re
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

# Profile, emulator console posture, SurfaceFlinger display index, native raster.
CATEGORIES = {
    "inner-1x1": ("foldable_1_1", "unfold", 0, (2106, 2106)),
    "inner-4x3": ("foldable_4_3", "unfold", 0, (2688, 2016)),
    "outer-10x16": ("foldable_4_3", "fold", 1, (1260, 2016)),
}


def run(*args, **kwargs):
    return subprocess.check_output(args, timeout=kwargs.pop("timeout", 30), **kwargs)


def poll(probe, description, timeout=60):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            result = probe()
            if result:
                return result
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
        time.sleep(1)
    raise ValueError(f"Timed out waiting for {description}")


def foreground(adb, package):
    windows = adb("shell", "dumpsys", "window", "displays").decode()
    return any(f" {package}/" in line for line in windows.splitlines() if "mCurrentFocus=" in line)


def prepare(adb, args):
    if not args.apk.is_file():
        raise ValueError(f"APK does not exist: {args.apk}")
    installed = adb("install", "--no-incremental", "-r", str(args.apk), timeout=120).decode()
    if "Success" not in installed.splitlines():
        raise ValueError(installed)
    component = args.component
    if component is None:
        resolved = adb("shell", "cmd", "package", "resolve-activity", "--brief",
                       "-a", "android.intent.action.MAIN", "-c", "android.intent.category.LAUNCHER",
                       "-p", args.package).decode()
        component = resolved.strip().rpartition("\n")[2]
    if not component.startswith(args.package + "/"):
        raise ValueError(f"Could not resolve a launcher activity for {args.package}")
    adb("shell", "am", "start", "-W", "-n", component)
    poll(lambda: foreground(adb, args.package), f"{args.package} to become focused")


def set_posture(adb, category):
    profile, posture, _, _ = CATEGORIES[category]
    actual_profile = adb("emu", "avd", "name").decode().splitlines()[0]
    if actual_profile != profile:
        raise ValueError(f"{category} requires {profile}; found {actual_profile}")
    adb("shell", "settings", "put", "system", "fold_lock_behavior_setting", "stay_awake_on_fold_key")
    reply = adb("emu", posture).decode().splitlines()
    if reply[-1:] != ["OK"]:
        raise ValueError(f"Emulator did not accept {posture}: {reply}")
    adb("shell", "wm", "user-rotation", "lock", "0")
    adb("shell", "input", "keyevent", "KEYCODE_WAKEUP")
    adb("shell", "wm", "dismiss-keyguard")


def device_posture(adb):
    output = adb("shell", "dumpsys", "device_state").decode()
    state = re.search(r"^\s*mCommittedState=.*?identifier=(\d+), name='([^']+)'", output, re.M)
    return (state[1], state[2]) if state else None


def active_display(adb, display_index, posture):
    state = device_posture(adb)
    expected_state = "CLOSED" if posture == "fold" else "OPENED"
    if state is None or state[1] != expected_state:
        return None
    displays = re.findall(r"^Display (\d+)", adb("shell", "dumpsys", "SurfaceFlinger", "--display-id").decode(), re.M)
    if len(displays) != 2:
        return None
    display = displays[display_index]
    power = adb("shell", "dumpsys", "display").decode()
    # DisplayDeviceInfo exposes the same physical ID as SurfaceFlinger.
    return display if any(
        f'local:{display}' in line and re.search(r'\bstate ON\b', line)
        for line in power.splitlines() if "DisplayDeviceInfo{" in line
    ) else None


def validate(path, category):
    result = run("magick", "-regard-warnings", str(path), "-format", "%m %w %h %[opaque]", "info:").decode().split()
    expected = CATEGORIES[category][3]
    if len(result) != 4 or result[0] != "PNG" or tuple(map(int, result[1:3])) != expected or result[3].lower() != "true":
        raise ValueError(f"Expected opaque native {expected[0]}×{expected[1]} PNG; found {' '.join(result)}")
    return expected


def capture(adb, args):
    profile, posture, display_index, _ = CATEGORIES[args.category]
    actual_profile = adb("emu", "avd", "name").decode().splitlines()[0]
    if actual_profile != profile:
        raise ValueError(f"{args.category} requires {profile}; found {actual_profile}")
    display = poll(lambda: active_display(adb, display_index, posture), f"{profile} {posture} display")
    poll(lambda: foreground(adb, args.package), f"{args.package} to become focused")
    if not re.fullmatch(r"[0-9a-f]{40}", args.source_sha):
        raise ValueError("Supply the full Git SHA used to build the installed APK")
    package_info = adb("shell", "dumpsys", "package", args.package).decode()
    version = dict(re.findall(r"^\s+(versionName|versionCode)=(\S+)", package_info, re.M))
    if version.keys() != {"versionName", "versionCode"}:
        raise ValueError("Could not read the installed app version")
    directory = args.output / args.category
    directory.mkdir(parents=True, exist_ok=True)
    output = directory / f"{args.name}.png"
    manifest = output.with_suffix(".json")
    if output.exists() or manifest.exists():
        raise ValueError(f"Capture already exists: {output}")
    with tempfile.TemporaryDirectory(dir=directory) as stage:
        candidate = Path(stage) / output.name
        frame = adb("exec-out", "screencap", "-p", "-d", display)
        native = Path(stage) / "native.png"
        native.write_bytes(frame)
        width, height = validate(native, args.category)
        if frame[24:26] == bytes((8, 2)):  # PNG IHDR: 8 bits per channel, RGB.
            native.rename(candidate)
        else:
            # Play requires RGB even when the capture's alpha channel is fully opaque.
            run("magick", "-regard-warnings", str(native), "PNG24:" + str(candidate))
            run("magick", "compare", "-metric", "AE", str(native), str(candidate),
                "null:", stderr=subprocess.DEVNULL)
        if candidate.stat().st_size > 8_000_000:
            raise ValueError("PNG exceeds the 8 MB Play screenshot limit")
        if active_display(adb, display_index, posture) != display or not foreground(adb, args.package):
            raise ValueError("Display posture or focused app changed during capture")
        metadata = {"source_sha": args.source_sha, "package": args.package,
                    "variant": args.variant, **version, "profile": profile, "serial": args.serial,
                    "api": adb("shell", "getprop", "ro.build.version.sdk").decode().strip(),
                    "device_state": " ".join(device_posture(adb)),
                    "posture": "folded" if posture == "fold" else "unfolded",
                    "physical_display": display, "width": width, "height": height,
                    "locale": args.locale, "theme": args.theme, "screen": args.name,
                    "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "native_sha256": hashlib.sha256(frame).hexdigest(),
                    "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(), "visual_review": "pending"}
        temp_manifest = Path(stage) / manifest.name
        temp_manifest.write_text(json.dumps(metadata, indent=2) + "\n")
        candidate.rename(output)
        temp_manifest.rename(manifest)
    print(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serial", required=True, help="ADB serial of a dedicated emulator")
    commands = parser.add_subparsers(dest="command", required=True)
    install = commands.add_parser("prepare", help="wait for boot, then install and launch an APK")
    install.add_argument("apk", type=Path)
    install.add_argument("package")
    install.add_argument("--component")
    posture = commands.add_parser("posture", help="switch to the requested native foldable display")
    posture.add_argument("category", choices=CATEGORIES)
    grab = commands.add_parser("capture", help="validate and stage one image and its provenance")
    grab.add_argument("category", choices=CATEGORIES)
    grab.add_argument("package")
    grab.add_argument("name", help="descriptive kebab-case filename stem")
    grab.add_argument("--source-sha", required=True)
    grab.add_argument("--variant", required=True)
    grab.add_argument("--locale", required=True)
    grab.add_argument("--theme", required=True, choices=("light", "dark"))
    grab.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    def adb(*command, **kwargs):
        return run("adb", "-s", args.serial, *command, **kwargs)

    try:
        poll(lambda: adb("shell", "getprop", "sys.boot_completed", timeout=5).strip() == b"1",
             f"{args.serial} to boot", 180)
        if args.command == "prepare":
            prepare(adb, args)
        elif args.command == "posture":
            set_posture(adb, args.category)
            _, switch, index, _ = CATEGORIES[args.category]
            poll(lambda: active_display(adb, index, switch), args.category)
        else:
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.name):
                raise ValueError("Capture name must be kebab-case")
            capture(adb, args)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()

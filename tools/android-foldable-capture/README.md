# Android foldable capture

Stages native PNGs and one provenance JSON file per image on macOS or Linux.
Requires Python 3, `adb`, ImageMagick 7 (`magick`), and the official
`foldable_1_1` and `foldable_4_3` profiles. Start the AVDs with Android CLI or
Android Studio. Google documents the SDK requirements, posture controls and
native resolutions in its [screenshot guide](https://developer.android.com/google/play/requirements/screenshots-android-cli).

1. Use a dedicated AVD with the listing locale and theme configured. Select its
   serial with `adb devices -l`.
2. Run `capture.py --serial emulator-5554 prepare APP.apk PACKAGE` with an APK
   built from a recorded commit. If the app has a first-run system dialog,
   handle it on the QA emulator before capturing.
3. Run `capture.py --serial emulator-5554 posture inner-1x1`. The 4:3 AVD
   supports `inner-4x3` and `outer-10x16`. Choose the app screen and load
   deterministic sample data using the app's normal UI or existing fixture.
4. Stage the result in an output directory outside the app checkout.

```sh
python3 capture.py --serial emulator-5554 capture inner-1x1 com.example.app dashboard \
  --source-sha "$(git rev-parse HEAD)" --variant release \
  --locale en-US --theme light --output "$PWD/capture-review"
```

With a named file already staged, use a new name for a revision. This preserves
reviewed captures across resumed runs. The metadata records the installed
version and observed device state. The caller supplies the build SHA, variant,
locale, and theme. Review the full image for truthful content, readability and
privacy before copying it to the listing directory. The tool records visual
review as pending. When ADB returns opaque RGBA, the tool exports 24-bit RGB for
Play and checks that every pixel is identical. It records both PNG hashes.
Track behavioral adaptive QA for the same commit separately.

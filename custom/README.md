# 12 Armoured (QGroundControl custom build)

This `custom/` folder rebrands QGroundControl as **12 Armoured**. It is branding
only: no flight, MAVLink, mission, parameter or firmware-plugin behaviour changes.
QGroundControl picks the folder up automatically (it must be named `custom`, at the
repo root).

Built against QGroundControl `master` commit `6eb58f0` (6 Nov 2026).

## What changes

| Area | Value | Where |
|---|---|---|
| On-screen name | **12 Armoured** (window title, menus, messages, Android/desktop launcher label) | `TWELVEA_DISPLAY_NAME` in `cmake/CustomOverrides.cmake` |
| Executable / bundle name | `TwelveArmoured` (`QGC_APP_NAME`; must have no spaces) | `cmake/CustomOverrides.cmake` |
| Organization | 12 Armoured, `twelvearmoured.com` (placeholder) | `cmake/CustomOverrides.cmake` |
| Package / bundle id | `com.twelvearmoured.groundcontrol` (Android, iOS, macOS, Windows, Linux) | `cmake/CustomOverrides.cmake` |
| Copyright metadata | "© YEAR 12 Armoured. Based on QGroundControl…" | `cmake/CustomOverrides.cmake` |
| In-app logos | Barasinghas badge: toolbar, app menu, settings (single-color version), GCS marker on the map | `res/Images/QGCLogo*.svg` |
| Android | Launcher icons, adaptive icon, splash icon, app label | `android/` (merged over upstream `android/`) |
| Windows / macOS / Linux | App icons, installer header, `.desktop`, AppStream metadata | `deploy/` |
| Fly view toolbar | "12 Armoured" shown beside the logo (top-left of the main screen); tapping it opens the same menu as the logo | `qml/FlyViewToolBar.qml` |
| Home (Fly view) screen | While no vehicle is connected, a 12 ARMOURED brand screen covers the map and flight widgets: badge with "12 ARMOURED", the status "DISCONNECTED – CLICK TO MANUALLY CONNECT" (charcoal, bronze border) in the exact centre (opens the usual connect panel), "GROUND CONTROL STATION" and a "Based on QGroundControl" credit. The toolbar status pill is hidden meanwhile. On connect, the map and widgets return unchanged | `qml/FlyViewCustomLayer.qml`, `qml/FlyViewToolBar.qml` |
| Startup animation | The badge zooms up from the Android launch-screen size, then fades into the app (~1.9 s, tap to skip) | `qml/TwelveASplash.qml`, `res/Images/SplashBadge.png`, `CustomPlugin::createRootWindow` |
| Update prompt | Off (custom builds never check QGC's server); "Update" link → your domain | `src/CustomPlugin.h` |

Search for `TODO(12A)` to find the remaining placeholders (domain, AppStream screenshot).

## Changes outside this folder

QGroundControl has one name setting for both the executable and the on-screen name,
so three tiny core edits make the UI use the display name. Stock QGC behaves exactly
as before (its display name defaults to its app name):

- `src/QmlControls/QGroundControlQmlGlobal.cc`: `appName()` returns `applicationDisplayName()`
- `src/QGCApplication.cc`: default message-dialog title and the settings-reset message use `applicationDisplayName()`
- `.github/workflows/android.yml`: CI artifact name `TwelveArmoured`, emulator test uses the new package id

These are also in `12armoured-core.patch`.

## Known leftovers (by design)

- About 15 rare C++ error/warning messages (mission file loading, parameter download,
  duplicate system id) say "TwelveArmoured", because they use the internal app name
  and live in mission/parameter/comms code that this rebrand doesn't touch.
- 13 hard-coded "QGroundControl" mentions remain in RTK/GPS receiver help text, the PX4
  old-firmware warning, the WiFi-bridge note and the video recordings page. Changing
  them means editing core translatable strings.
- The Help page still links to QGroundControl's user guide and Discord.
- `.plan` files still say `"groundStation": "QGroundControl"` (file-format field, kept for compatibility).
- Settings and saved files live in a separate `TwelveArmoured` / `12 Armoured` folder,
  so an existing QGroundControl install's settings are not shared.
- iOS app icons are not overridable from `custom/` (the path is fixed in core). Not needed for Android.

## Build the Android APK (GitHub Actions)

1. Fork https://github.com/mavlink/qgroundcontrol.
2. Copy `custom/` and the three changed files into your fork (same paths) and push.
3. **Actions** tab → enable workflows → **Android** → **Run workflow**.
4. When it finishes, download `TwelveArmoured-linux-…` from the run's **Artifacts**.

The configure log should print `QGC: Adding 12 Armoured custom plugin` and
`QGC: 12 Armoured Android overlay found`. The APK is signed with a debug key
on a fork (fine for sideloading; use your own keystore for Play Store).

## Logo artwork

Every logo and icon is generated from one photo of the Barasinghas badge
(`tools/badge_source.jpg`) by `tools/gen_brand_from_image.py`. The script cuts the shield
out of the photo, embeds it as a PNG inside the in-app SVGs (Qt's VectorImage and QtSvg
both render embedded images), makes a single-color silhouette for the tinted Settings
icon, and writes every platform icon. To change the logo, replace the photo and rerun:

```bash
python3 custom/tools/gen_brand_from_image.py custom/tools/badge_source.jpg custom /tmp/brand
```

(needs opencv-python, numpy, Pillow, fontTools and `rsvg-convert`). A vector (SVG) master
of the badge would give sharper results at very small and very large sizes than a photo.
You can also replace files directly at the same paths, sizes and formats:

| File | Format / size |
|---|---|
| `res/Images/QGCLogoFull.svg`, `QGCLogoWhite.svg` (white silhouette), `QGCLogoArrow.svg` | SVG, square (arrow points up) |
| `res/icons/qgroundcontrol.ico` | ICO 16, 32, 48, 64, 128, 256 |
| `android/res/mipmap-*/ic_launcher.png`, `drawable-*/icon.png` | PNG ldpi 48, mdpi 48, hdpi 72, xhdpi 96, xxhdpi 144, xxxhdpi 144 |
| `android/res/drawable/ic_launcher_foreground.xml` + `drawable-*dpi/ic_launcher_foreground_img.png` | adaptive icon foreground: PNG 108/162/216/324/432 px (108dp), art inside the central 66dp |
| `android/res/values/ic_launcher_colors.xml` | adaptive icon background color |
| `deploy/windows/WindowsQGC.ico` | ICO 16, 20, 24, 32, 40, 48, 64 |
| `deploy/windows/installheader.bmp` | BMP 150×57 |
| `deploy/macos/TwelveArmoured.icns` | ICNS 16–1024 |
| `deploy/linux/TwelveArmoured_256.png`, `TwelveArmoured.svg` | PNG 256, SVG |
| `res/icons/store_512x512.png` | PNG 512 (Play Store listing) |
| `res/Images/SplashBadge.png` | PNG, 768 px tall (startup zoom) |

## Updating to a newer QGroundControl

Two files are copies of upstream with a small addition. After pulling a new QGC, re-copy
them and re-apply the change:

- `android/AndroidManifest.xml`: only the two `android:label` values differ.
- `qml/FlyViewToolBar.qml` (from `src/Toolbar/FlyViewToolBar.qml`): adds
  `import QGroundControl.Toolbar` and the two changes marked "12 Armoured".

`qml/FlyViewCustomLayer.qml` replaces upstream's empty customization layer; keep its three
interface properties in step with upstream's `src/FlyView/FlyViewCustomLayer.qml`.

If you skip this, the app still builds, but those files won't get upstream fixes. Re-apply
`12armoured-core.patch` if the three core edits don't merge cleanly.

## License

QGroundControl is dual-licensed Apache-2.0 / GPLv3. All upstream license files and
headers are unchanged; keep them, and keep the "Based on QGroundControl" credit.

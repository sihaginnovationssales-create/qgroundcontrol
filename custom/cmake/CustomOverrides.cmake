# ============================================================================
# 12 Armoured - branding overrides for QGroundControl
#
# Loaded by the root CMakeLists.txt after cmake/CustomOptions.cmake, so every
# value here replaces the stock QGroundControl default. Branding only: no
# feature, protocol or firmware-plugin option is changed.
#
# Placeholders to review before release are marked TODO(12A).
# ============================================================================

set(_12a_dir "${CMAKE_SOURCE_DIR}/${QGC_CUSTOM_DIR}")

# ----------------------------------------------------------------------------
# Names and identity
# ----------------------------------------------------------------------------
# QGC_APP_NAME becomes the CMake project / executable / bundle name, so it must be a
# safe identifier (no spaces, no leading digit). The on-screen name "12 Armoured" is
# set at runtime by CustomPlugin (QGuiApplication::applicationDisplayName).
set(QGC_APP_NAME        "TwelveArmoured"                    CACHE STRING "App Name" FORCE)
set(TWELVEA_DISPLAY_NAME "12 Armoured"                      CACHE STRING "On-screen app name" FORCE)
set(QGC_ORG_NAME        "12 Armoured"                       CACHE STRING "Organization name" FORCE)
set(QGC_ORG_DOMAIN      "twelvearmoured.com"                CACHE STRING "Organization domain" FORCE)  # TODO(12A): real domain
set(QGC_APP_DESCRIPTION "12 Armoured Ground Control Station" CACHE STRING "Application description" FORCE)
string(TIMESTAMP _12a_year "%Y")
set(QGC_APP_COPYRIGHT
    "Copyright (c) ${_12a_year} 12 Armoured. Based on QGroundControl (c) QGroundControl Development Team, dual-licensed Apache-2.0 / GPLv3."
    CACHE STRING "Copyright notice" FORCE)

# Package / bundle identifiers. Segments may not start with a digit, hence "twelvearmoured".
# Decide before publishing: an Android package id can never change once on the Play Store.
set(QGC_PACKAGE_NAME "com.twelvearmoured.groundcontrol" CACHE STRING "Package identifier" FORCE)
# These two were already defaulted from the stock QGC_PACKAGE_NAME in CustomOptions.cmake,
# so they must be forced too or they keep org.mavlink.qgroundcontrol.
set(QGC_ANDROID_PACKAGE_NAME "${QGC_PACKAGE_NAME}" CACHE STRING "Android package identifier" FORCE)
set(QGC_MACOS_BUNDLE_ID      "${QGC_PACKAGE_NAME}" CACHE STRING "macOS bundle identifier" FORCE)

# ----------------------------------------------------------------------------
# Icons and packaging artwork (generated from the badge by tools/gen_brand_from_image.py)
# ----------------------------------------------------------------------------
set(QGC_MACOS_ICON_PATH              "${_12a_dir}/deploy/macos/TwelveArmoured.icns"   CACHE FILEPATH "macOS Icon Path" FORCE)
set(QGC_WINDOWS_ICON_PATH            "${_12a_dir}/deploy/windows/WindowsQGC.ico"      CACHE FILEPATH "Windows Icon Path" FORCE)
set(QGC_WINDOWS_INSTALL_HEADER_PATH  "${_12a_dir}/deploy/windows/installheader.bmp"   CACHE FILEPATH "Windows Install Header Path" FORCE)
set(QGC_APPIMAGE_ICON_256_PATH       "${_12a_dir}/deploy/linux/TwelveArmoured_256.png" CACHE FILEPATH "AppImage 256 Icon Path" FORCE)
set(QGC_APPIMAGE_ICON_SCALABLE_PATH  "${_12a_dir}/deploy/linux/TwelveArmoured.svg"    CACHE FILEPATH "AppImage SVG Icon Path" FORCE)
set(QGC_APPIMAGE_DESKTOP_ENTRY_PATH  "${_12a_dir}/deploy/linux/twelvearmoured.desktop.in"     CACHE FILEPATH "Desktop entry" FORCE)
set(QGC_APPIMAGE_METADATA_PATH       "${_12a_dir}/deploy/linux/twelvearmoured.appdata.xml.in" CACHE FILEPATH "AppStream metadata" FORCE)
set(QGC_APPIMAGE_APPDATA_DEVELOPER   "twelvearmoured"                                  CACHE STRING "AppStream developer id suffix (no spaces)" FORCE)

# Flight stacks: unchanged from stock (PX4 and ArduPilot both available).

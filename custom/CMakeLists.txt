# ============================================================================
# 12 Armoured - QGroundControl custom overlay (branding only)
# Structure follows custom-example/CMakeLists.txt, without its demo features.
# ============================================================================

message(STATUS "QGC: Adding 12 Armoured custom plugin")

# ============================================================================
# Android package template: upstream android/ with this folder's android/ on top
# (launcher icons, adaptive icon, splash icon, app label).
# ============================================================================

if(ANDROID)
    set(CUSTOM_ANDROID_DIR "${CMAKE_CURRENT_SOURCE_DIR}/android")
    if(IS_DIRECTORY "${CUSTOM_ANDROID_DIR}")
        set(DEFAULT_ANDROID_DIR "${CMAKE_SOURCE_DIR}/android")
        set(FINAL_ANDROID_DIR "${CMAKE_BINARY_DIR}/${QGC_CUSTOM_DIR}/android")

        # Recreate the merge so removed source files cannot remain stale.
        file(REMOVE_RECURSE "${FINAL_ANDROID_DIR}")
        file(COPY "${DEFAULT_ANDROID_DIR}/" DESTINATION "${FINAL_ANDROID_DIR}")

        # Overlay file by file with COPY_FILE: file(COPY) skips a file whose destination has
        # the same timestamp, which is the case for every file in a fresh CI checkout, so
        # overlay files replacing upstream ones (manifest, icon XML, colors) were dropped.
        # CONFIGURE_DEPENDS also re-runs configure when an overlay file changes.
        file(GLOB_RECURSE _12a_android_files CONFIGURE_DEPENDS LIST_DIRECTORIES FALSE
            RELATIVE "${CUSTOM_ANDROID_DIR}" "${CUSTOM_ANDROID_DIR}/*")
        foreach(_12a_file IN LISTS _12a_android_files)
            get_filename_component(_12a_dest_dir "${FINAL_ANDROID_DIR}/${_12a_file}" DIRECTORY)
            file(MAKE_DIRECTORY "${_12a_dest_dir}")
            file(COPY_FILE "${CUSTOM_ANDROID_DIR}/${_12a_file}" "${FINAL_ANDROID_DIR}/${_12a_file}")
        endforeach()

        set(QGC_ANDROID_PACKAGE_SOURCE_DIR "${FINAL_ANDROID_DIR}")
        set(QGC_ANDROID_PACKAGE_SOURCE_DIR "${FINAL_ANDROID_DIR}" PARENT_SCOPE)
        message(STATUS "QGC: 12 Armoured Android overlay found -> ${QGC_ANDROID_PACKAGE_SOURCE_DIR}")
    endif()
endif()

# ============================================================================
# Brand images. CustomPlugin's URL interceptor serves qrc:/Custom/<path> in place
# of qrc:/<path>, so these replace /res/QGCLogo*.svg everywhere in the UI
# (toolbar, app menu, settings, GCS marker on the map) and the window icon.
# ============================================================================

set(TWELVEA_BRAND_RESOURCES
    "${CMAKE_CURRENT_SOURCE_DIR}/res/Images/QGCLogoFull.svg"
    "${CMAKE_CURRENT_SOURCE_DIR}/res/Images/QGCLogoWhite.svg"
    "${CMAKE_CURRENT_SOURCE_DIR}/res/Images/QGCLogoArrow.svg"
    "${CMAKE_CURRENT_SOURCE_DIR}/res/icons/qgroundcontrol.ico"
)
qgc_set_qt_resource_alias(${TWELVEA_BRAND_RESOURCES})
qt_add_resources(${CMAKE_PROJECT_NAME} twelvea_brand
    PREFIX "/Custom/res"
    FILES ${TWELVEA_BRAND_RESOURCES}
)

# ============================================================================
# Custom plugin sources (picked up by src/CMakeLists.txt)
# ============================================================================

set(CUSTOM_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/src/CustomPlugin.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/src/CustomPlugin.h
    PARENT_SCOPE
)

set(CUSTOM_INCLUDE_DIRECTORIES
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    PARENT_SCOPE
)

set(CUSTOM_DEFINITIONS
    QGC_CUSTOM_BUILD
    CUSTOMHEADER="CustomPlugin.h"
    CUSTOMCLASS=CustomPlugin
    TWELVEA_DISPLAY_NAME="${TWELVEA_DISPLAY_NAME}"
    TWELVEA_DOWNLOAD_URL="https://${QGC_ORG_DOMAIN}"
    PARENT_SCOPE
)

set(CUSTOM_QT_COMPONENTS
    Core
    PARENT_SCOPE
)

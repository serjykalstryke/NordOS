cmake_minimum_required(VERSION 3.22)
project(NordOSCore VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_INCLUDE_CURRENT_DIR ON)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)
find_package(CutefishToolkit REQUIRED)

include(GNUInstallDirs)
include(cmake/NordOSLayout.cmake)
include_directories("${NORDOS_LIBRARY_DIR}")

if(NOT CMAKE_SYSTEM_NAME STREQUAL "Linux")
    message(FATAL_ERROR "The initial NordOS platform implementation requires Linux.")
endif()

add_subdirectory(system/platform/linux)
add_subdirectory(system/library/core)
add_subdirectory(system/desktop/session)
add_subdirectory(system/services/applications/runtime)
add_subdirectory(system/services/applications/placement)
add_subdirectory(system/services/locales)
add_subdirectory(system/services/privacy)
add_subdirectory(system/services/session)
add_subdirectory(system/services/capture)
add_subdirectory(system/desktop/authorization)
add_subdirectory(system/services/desktop)

configure_file(system/services/session/cutefish-wayland.desktop
               session-input/cutefish-wayland.desktop @ONLY)
cutefish_add_translations(cutefish-core SOURCES system/services/desktop system/services/session
                          DESKTOP_FILES ${CMAKE_CURRENT_BINARY_DIR}/session-input/cutefish-wayland.desktop)
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/cutefish-wayland.desktop DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/wayland-sessions/)

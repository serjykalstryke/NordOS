# Shared by the main build and independently configured test projects.
include_guard(GLOBAL)
get_filename_component(NORDOS_SOURCE_ROOT "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
set(NORDOS_SYSTEM_DIR "${NORDOS_SOURCE_ROOT}/system")
set(NORDOS_LIBRARY_DIR "${NORDOS_SYSTEM_DIR}/library")
set(NORDOS_SERVICES_DIR "${NORDOS_SYSTEM_DIR}/services")
set(NORDOS_DESKTOP_DIR "${NORDOS_SYSTEM_DIR}/desktop")
set(NORDOS_PLATFORM_DIR "${NORDOS_SYSTEM_DIR}/platform")

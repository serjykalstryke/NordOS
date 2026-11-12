# The desktop implementations selected for this system build. Replacements
# must implement the inherited readiness, private-connection and service APIs.
include(GNUInstallDirs)
set(NORDOS_COMPOSITOR "${CMAKE_INSTALL_FULL_BINDIR}/cutefish-compositor" CACHE STRING "Session compositor executable")
set(NORDOS_FILE_SURFACE "cutefish-filemanager" CACHE STRING "Resident desktop/file application executable")
set(NORDOS_AUTHORIZATION_AGENT "cutefish-polkit-agent" CACHE STRING "Session authorization UI executable")
set(NORDOS_APPLICATION_RUNTIME "cutefish-appruntime" CACHE STRING "Application execution service executable")
set(NORDOS_DESKTOP_SERVICES "cutefish-services" CACHE STRING "Desktop services executable")

foreach(role COMPOSITOR FILE_SURFACE AUTHORIZATION_AGENT APPLICATION_RUNTIME DESKTOP_SERVICES)
    if(NOT NORDOS_${role} MATCHES "^[A-Za-z0-9_./+-]+$")
        message(FATAL_ERROR "NORDOS_${role} must be an executable path or name, without arguments.")
    endif()
    get_filename_component(role_name "${NORDOS_${role}}" NAME)
    if(NORDOS_${role} MATCHES "/$" OR role_name STREQUAL "." OR role_name STREQUAL "..")
        message(FATAL_ERROR "NORDOS_${role} must name an executable, not a directory.")
    endif()
endforeach()

set(composition_include "${CMAKE_CURRENT_BINARY_DIR}/include")
configure_file(composition.h.in "${composition_include}/desktop/session/composition.h" @ONLY)
add_library(nordos-session-composition INTERFACE)
target_include_directories(nordos-session-composition INTERFACE "${composition_include}")

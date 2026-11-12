project(cutefish-session)
set(TARGET cutefish-session)

pkg_check_modules(Systemd REQUIRED IMPORTED_TARGET libsystemd)

set(SOURCES
    application.cpp
    autostartentries.cpp
    journalstream.cpp
    main.cpp
    processmanager.cpp
    restartpolicy.cpp
    compositorprocess.cpp
    xwaylandenvironment.cpp
    shellprocess.cpp
    shellconnection.cpp
    userdirectories.cpp
)

add_executable(${TARGET} ${SOURCES})
target_link_libraries(${TARGET}
        cutefish-core-common
        nordos-platform-linux-power
        nordos-session-composition
        Cutefish::ToolkitBase
        PkgConfig::Systemd
)

install(TARGETS ${TARGET} DESTINATION ${CMAKE_INSTALL_BINDIR})
configure_file(cutefish-wayland-session cutefish-wayland-session @ONLY)
install(PROGRAMS ${CMAKE_CURRENT_BINARY_DIR}/cutefish-wayland-session DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES document-portal-stop.conf
        DESTINATION /usr/lib/systemd/user/xdg-document-portal.service.d
        RENAME cutefish-session.conf)

cmake_minimum_required(VERSION 3.22)
project(session_composition_test LANGUAGES CXX)

set(NORDOS_COMPOSITOR "/opt/nordos/bin/nordos-test-compositor" CACHE STRING "Test compositor")
set(NORDOS_FILE_SURFACE "nordos-test-file-surface" CACHE STRING "Test file surface")
set(NORDOS_AUTHORIZATION_AGENT "nordos-test-authorization-agent" CACHE STRING "Test authorization agent")
set(NORDOS_APPLICATION_RUNTIME "nordos-test-runtime" CACHE STRING "Test application runtime")
add_subdirectory(../../system/desktop/session composition)

find_package(CutefishToolkit REQUIRED)
set(session_dir "${CMAKE_CURRENT_SOURCE_DIR}/../../system/services/session")
add_executable(session_composition_test session_composition_test.cpp "${session_dir}/autostartentries.cpp")
target_compile_features(session_composition_test PRIVATE cxx_std_20)
target_include_directories(session_composition_test PRIVATE "${session_dir}")
target_link_libraries(session_composition_test PRIVATE nordos-session-composition Cutefish::ToolkitBase)

enable_testing()
add_test(NAME session_composition_test COMMAND session_composition_test)
add_test(NAME session_composition_invalid_values
    COMMAND "${CMAKE_COMMAND}" "-DTEST_SOURCE_DIR=${CMAKE_CURRENT_SOURCE_DIR}"
        "-DTEST_BINARY_DIR=${CMAKE_CURRENT_BINARY_DIR}/invalid-config"
        -P "${CMAKE_CURRENT_SOURCE_DIR}/expect_invalid_composition.cmake")

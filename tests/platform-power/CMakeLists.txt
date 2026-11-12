cmake_minimum_required(VERSION 3.22)
project(platform_power_test LANGUAGES CXX)

find_package(CutefishToolkit REQUIRED)
find_package(Threads REQUIRED)
find_program(DBUS_RUN_SESSION dbus-run-session REQUIRED)

add_subdirectory(../../system/platform/linux platform-linux)
add_executable(platform_power_test platform_power_test.cpp)
target_compile_features(platform_power_test PRIVATE cxx_std_20)
target_link_libraries(platform_power_test PRIVATE nordos-platform-linux-power Cutefish::ToolkitBase Threads::Threads)

enable_testing()
add_test(NAME platform_power_test COMMAND "${DBUS_RUN_SESSION}" -- $<TARGET_FILE:platform_power_test>)
set_tests_properties(platform_power_test PROPERTIES TIMEOUT 15)

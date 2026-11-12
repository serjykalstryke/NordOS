add_library(nordos-platform-linux-power STATIC power.cpp)
target_include_directories(nordos-platform-linux-power PUBLIC "${CMAKE_CURRENT_LIST_DIR}/../../library")
target_compile_features(nordos-platform-linux-power PRIVATE cxx_std_20)
target_link_libraries(nordos-platform-linux-power PRIVATE Cutefish::ToolkitBase)

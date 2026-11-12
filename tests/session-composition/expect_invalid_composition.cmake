foreach(invalid IN ITEMS "" "/usr/bin/compositor --debug" "compositor;second" "compositor\"second" "." ".." "/usr/bin/")
    execute_process(
        COMMAND "${CMAKE_COMMAND}" -S "${TEST_SOURCE_DIR}" -B "${TEST_BINARY_DIR}"
            "-DNORDOS_COMPOSITOR:STRING=${invalid}"
        RESULT_VARIABLE result
        OUTPUT_VARIABLE output
        ERROR_VARIABLE error)
    if(result EQUAL 0 OR NOT error MATCHES "NORDOS_COMPOSITOR must (be an executable path or name|name an executable)")
        message(FATAL_ERROR "Expected an invalid compositor value to be rejected: '${invalid}'\n${output}\n${error}")
    endif()
endforeach()

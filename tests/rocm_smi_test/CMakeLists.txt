# Required Defines first:
option(INSTALL_GTEST "Install GTest (only useful if GTest is not already installed)" OFF)

# Try to find googletest
find_package(GTest 1.12.0)

# GTest_FOUND is set to TRUE if ANY version is found
# GTest_VERSION is set if 1.11.0 or newer version is found
if(NOT GTest_FOUND STREQUAL "TRUE" OR NOT DEFINED GTest_VERSION)
    # Google Test wasn't found. Download and compile ourselves
    include(FetchContent)
    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG release-1.12.0)
    FetchContent_MakeAvailable(googletest)
endif()

enable_testing()

if(WIN32)
    message("amd_smi library test suite is not supported on Windows platform")
    return()
endif()

#
# Print out the build configuration being used:
#
#   Build Src directory
#   Build Binary directory
#   Build Type: Debug Vs Release, 32 Vs 64
#   Compiler Version, etc
#
message("")
message("Build Configuration:")
message("-------------IS64BIT: " ${IS64BIT})
message("-----------BuildType: " ${BUILD_TYPE})
message("------------Compiler: " ${CMAKE_CXX_COMPILER})
message("-------------Version: " ${CMAKE_CXX_COMPILER_VERSION})
message("--------Proj Src Dir: " ${PROJECT_SOURCE_DIR})
message("--------Proj Bld Dir: " ${PROJECT_BINARY_DIR})
message("--------Proj Lib Dir: " ${PROJECT_BINARY_DIR}/lib)
message("--------Proj Exe Dir: " ${PROJECT_BINARY_DIR}/bin)
message("--------RSMI Lib Dir: " ${RSMI_LIB_DIR})
message("")


# Other source directories
aux_source_directory(${CMAKE_CURRENT_SOURCE_DIR}/functional functionalSources)

link_directories(${RSMI_LIB_DIR})

set(RSMITST "rsmitst64")

# Source files
aux_source_directory(${CMAKE_CURRENT_SOURCE_DIR} rsmitstSources)

# Header file include path
include_directories(${RSMI_INC_DIR})
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/..)

# Build rules
add_executable(${RSMITST} ${rsmitstSources} ${functionalSources})

target_link_libraries(${RSMITST} amd_smi64 c stdc++ pthread GTest::gtest_main)

install(
    TARGETS ${RSMITST}
    ARCHIVE DESTINATION ${PROJECT_BINARY_DIR}/lib
    LIBRARY DESTINATION ${PROJECT_BINARY_DIR}/lib
    RUNTIME DESTINATION ${PROJECT_BINARY_DIR}/bin)

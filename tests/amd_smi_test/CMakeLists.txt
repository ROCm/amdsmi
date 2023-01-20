# Required Defines first:
option(INSTALL_GTEST "Install GTest (only useful if GTest is not already installed)" OFF)

# Help tests find libraries at runtime
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,--enable-new-dtags")
set(CMAKE_INSTALL_RPATH
    "\$ORIGIN:\$ORIGIN/../../../lib"
    CACHE STRING "RUNPATH for tests. Helps find libgtest.so and libamd_smi.so")

# Try to find googletest
find_package(GTest 1.11.0)

# GTest_FOUND is set to TRUE if ANY version is found
# GTest_VERSION is set if 1.11.0 or newer version is found
if(NOT GTest_FOUND STREQUAL "TRUE" OR NOT DEFINED GTest_VERSION)
    # Google Test wasn't found. Download and compile ourselves
    include(FetchContent)
    FetchContent_Declare(
        googletest
        GIT_REPOSITORY https://github.com/google/googletest.git
        GIT_TAG release-1.11.0)
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
#   Build Type: Debug Vs Release
#   Compiler Version, etc
#
message("")
message("Build Configuration:")
message("-----------BuildType: " ${CMAKE_BUILD_TYPE})
message("------------Compiler: " ${CMAKE_CXX_COMPILER})
message("-------------Version: " ${CMAKE_CXX_COMPILER_VERSION})
message("--------Proj Src Dir: " ${PROJECT_SOURCE_DIR})
message("--------Proj Bld Dir: " ${PROJECT_BINARY_DIR})
message("--------Proj Lib Dir: " ${PROJECT_BINARY_DIR}/lib)
message("--------Proj Exe Dir: " ${PROJECT_BINARY_DIR}/bin)
message("")

# Other source directories
aux_source_directory(${CMAKE_CURRENT_SOURCE_DIR}/functional functionalSources)

set(TEST "amdsmitst")

# Source files
aux_source_directory(${CMAKE_CURRENT_SOURCE_DIR} tstSources)

# Header file include path
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/..)

# Build rules
add_executable(${TEST} ${tstSources} ${functionalSources})

target_link_libraries(${TEST} amd_smi c stdc++ pthread GTest::gtest_main)

# Install tests and gtest
# TODO: Remove GTest from here in the future and rely on INSTALL_GTEST?
install(
    TARGETS ${TEST} gtest gtest_main
    DESTINATION ${SHARE_INSTALL_PREFIX}/tests
    COMPONENT tests)

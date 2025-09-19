# Copyright (c) Advanced Micro Devices, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

cmake_minimum_required(VERSION 3.25)

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
  message(
    FATAL_ERROR
      "Do not build in-source. Please remove CMakeCache.txt and the CMakeFiles/ directory. Then build out-of-source."
  )
endif()

# Get version number from file
file(READ ${CMAKE_CURRENT_SOURCE_DIR}/version.json VERSION_JSON_STRING)
string(JSON PACKAGE_VERSION GET ${VERSION_JSON_STRING} package-version)
string(REGEX MATCH "(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*" BASE_VERSION ${PACKAGE_VERSION})

# Parse version components for header generation
string(REPLACE "." ";" VERSION_LIST ${PACKAGE_VERSION})
list(GET VERSION_LIST 0 AMDSMI_LIB_VERSION_MAJOR)
list(GET VERSION_LIST 1 AMDSMI_LIB_VERSION_MINOR)
list(LENGTH VERSION_LIST VERSION_LIST_LENGTH)
if(VERSION_LIST_LENGTH GREATER 2)
    list(GET VERSION_LIST 2 AMDSMI_LIB_VERSION_RELEASE)
else()
    set(AMDSMI_LIB_VERSION_RELEASE 0)
endif()

# Set version string for template substitution
set(amd_smi_lib_VERSION_STRING ${PACKAGE_VERSION})

# Generate VERSION file for Python setuptools dynamic versioning
file(WRITE ${CMAKE_CURRENT_SOURCE_DIR}/VERSION ${PACKAGE_VERSION})

# Generate amdsmi.h from template with dynamic version
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/include/amd_smi/amdsmi.h.in
    ${CMAKE_CURRENT_SOURCE_DIR}/include/amd_smi/amdsmi.h
    @ONLY
)

project(
  "amdsmi"
  VERSION ${BASE_VERSION}
  LANGUAGES C CXX
)

include(CMakeDependentOption)
include(FindPkgConfig)

set(SOVERSION 1)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS 1)

# Enable position independent code for shared libraries
if(NOT WIN32)
  set(CMAKE_POSITION_INDEPENDENT_CODE ON)
endif()

# Build options
option(AMDSMI_BUILD_SHARED_LIBS "Build shared library (.so)" ON)
option(AMDSMI_BUILD_STATIC_LIBS "Build static library (.a)" OFF)
option(AMDSMI_BUILD_TESTS "Enable building tests" OFF)
option(AMDSMI_BUILD_PYTHON_BINDINGS "Enable Python bindings" ON)

# Set build flags based on options
set(AMDSMI_BUILD_DYNAMIC ${AMDSMI_BUILD_SHARED_LIBS})
set(AMDSMI_BUILD_STATIC ${AMDSMI_BUILD_STATIC_LIBS})

# Include our custom CMake modules
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/build_tools/cmake")
include(amdsmi_component)
include(amdsmi_library)

# Set library name for linking
if(AMDSMI_BUILD_DYNAMIC)
  set(AMDSMI_LINK_LIBRARY_NAME "amdsmi")
else()
  set(AMDSMI_LINK_LIBRARY_NAME "amdsmi-static")
endif()

# Find system dependencies
find_package(Threads REQUIRED)
find_package(PkgConfig REQUIRED)

# Check for required libraries
pkg_check_modules(DRM REQUIRED libdrm)

# Optional dependencies
find_library(RT_LIB rt)
find_library(DL_LIB dl)

# Build ROCm SMI library (required by AMDSMI)
add_subdirectory(rocm_smi)

# Create components for different parts of the library
add_subdirectory(src)

# Build Python bindings if requested
if(AMDSMI_BUILD_PYTHON_BINDINGS)
  add_subdirectory(python)
  add_subdirectory(amdsmi_cli)
endif()

# Build tests if requested
if(AMDSMI_BUILD_TESTS)
  enable_testing()
  add_subdirectory(tests)
endif()

# Configure package config
include(CMakePackageConfigHelpers)

configure_package_config_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/amd_smi-config.cmake.in"
  "${CMAKE_CURRENT_BINARY_DIR}/amd_smi-config.cmake"
  INSTALL_DESTINATION lib/cmake/amd_smi
)

write_basic_package_version_file(
  "${CMAKE_CURRENT_BINARY_DIR}/amd_smi-config-version.cmake"
  VERSION ${PROJECT_VERSION}
  COMPATIBILITY SameMajorVersion
)

# Installation rules
if(AMDSMI_BUILD_DYNAMIC)
  install(TARGETS amdsmi
    EXPORT amd_smi-targets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
  )
endif()

if(AMDSMI_BUILD_STATIC)
  install(TARGETS amdsmi-static
    EXPORT amd_smi-targets
    ARCHIVE DESTINATION lib
  )
endif()

install(DIRECTORY include/
  DESTINATION include
  FILES_MATCHING PATTERN "*.h"
)

install(FILES
  "${CMAKE_CURRENT_BINARY_DIR}/amd_smi-config.cmake"
  "${CMAKE_CURRENT_BINARY_DIR}/amd_smi-config-version.cmake"
  DESTINATION lib/cmake/amd_smi
)

install(EXPORT amd_smi-targets
  FILE amd_smi-targets.cmake
  NAMESPACE amd_smi::
  DESTINATION lib/cmake/amd_smi
)
# Copyright (c) Advanced Micro Devices, Inc. All rights reserved.

if(NOT AMDSMI_BUILD_PYTHON_BINDINGS)
  return()
endif()

# Find Python and nanobind
find_package(Python COMPONENTS Interpreter Development.Module REQUIRED)

# Try to find nanobind via CMake
find_package(nanobind CONFIG QUIET)
if(NOT nanobind_FOUND)
  # Fall back to pip install
  execute_process(
    COMMAND ${Python_EXECUTABLE} -m pip install --break-system-packages nanobind
    RESULT_VARIABLE _pip_result
  )
  if(NOT _pip_result EQUAL 0)
    message(FATAL_ERROR "Failed to install nanobind via pip")
  endif()
  execute_process(
    COMMAND ${Python_EXECUTABLE} -c "import nanobind; print(nanobind.cmake_dir())"
    OUTPUT_VARIABLE _nanobind_cmake_dir
    OUTPUT_STRIP_TRAILING_WHITESPACE
  )
  find_package(nanobind CONFIG REQUIRED HINTS ${_nanobind_cmake_dir})
endif()

# Create the Python extension module
nanobind_add_module(
  _amdsmi_impl
  NB_STATIC
  STABLE_ABI
  _amdsmi_impl.cpp
)

target_link_libraries(_amdsmi_impl PRIVATE ${AMDSMI_LINK_LIBRARY_NAME})
target_compile_definitions(_amdsmi_impl PRIVATE VERSION_INFO=${PROJECT_VERSION})

# Set output directory to match Python package structure
set_target_properties(_amdsmi_impl PROPERTIES
  LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/amdsmi
)

# Copy Python package files
configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi/__init__.py
  ${CMAKE_CURRENT_BINARY_DIR}/amdsmi/__init__.py
  COPYONLY
)

configure_file(
  ${CMAKE_CURRENT_SOURCE_DIR}/_amdsmi/__init__.py
  ${CMAKE_CURRENT_BINARY_DIR}/_amdsmi/__init__.py
  COPYONLY
)
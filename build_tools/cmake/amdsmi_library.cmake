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

set(AMDSMI_DEFAULT_COPTS
  # General clang and GCC options applicable to C and C++.
  $<$<C_COMPILER_ID:AppleClang,Clang,GNU>:
  -Wall
  # Temporarily disable -Werror for modernization
  >

  # General MSVC options applicable to C and C++.
  $<$<C_COMPILER_ID:MSVC>:
  /W4
  # Temporarily disable /WX for modernization
  >
)

function(amdsmi_public_library)
  cmake_parse_arguments(
    _RULE
    ""
    "NAME;LINUX_LD_SCRIPT"
    "SRCS;COMPONENTS;USAGE_DEPS"
    ${ARGN}
  )

  # Get usage requirements from requested USAGE_DEPS and forward them from the
  # public library. This is because the contents of the libraries stop at the
  # public library vs propagating to callers. So we must manually control
  # the combined usage requirements of the aggregate library.
  set(_usage_include_directories)
  set(_usage_compile_definitions)
  foreach(_usage_dep _amdsmi_defs ${_RULE_USAGE_DEPS})
    get_target_property(_value ${_usage_dep} INTERFACE_INCLUDE_DIRECTORIES)
    if(_value)
      list(APPEND _usage_include_directories ${_value})
    endif()
    get_target_property(_value ${_usage_dep} INTERFACE_COMPILE_DEFINITIONS)
    if(_value)
      list(APPEND _usage_compile_definitions ${_value})
    endif()
  endforeach()

  if(AMDSMI_BUILD_STATIC)
    # Static library.
    amdsmi_components_to_static_libs(_STATIC_COMPONENTS ${_RULE_COMPONENTS})
    add_library("${_RULE_NAME}-static" STATIC ${_RULE_SRCS})
    target_compile_definitions("${_RULE_NAME}-static" INTERFACE
      ${_usage_compile_definitions}
    )
    target_include_directories("${_RULE_NAME}-static" INTERFACE ${_usage_include_directories})
    target_link_libraries(
      "${_RULE_NAME}-static"
      PRIVATE ${_STATIC_COMPONENTS}
    )
  endif()

  if(AMDSMI_BUILD_DYNAMIC)
    # Shared library.
    amdsmi_components_to_dynamic_libs(_DYLIB_COMPONENTS ${_RULE_COMPONENTS})
    add_library("${_RULE_NAME}" SHARED ${_RULE_SRCS})
    target_compile_definitions("${_RULE_NAME}" INTERFACE
      _AMDSMI_USING_DYLIB
      ${_usage_compile_definitions}
    )
    target_include_directories("${_RULE_NAME}" INTERFACE ${_usage_include_directories})
    if(_RULE_LINUX_LD_SCRIPT)
      target_link_options("${_RULE_NAME}" PRIVATE
        "$<$<PLATFORM_ID:Linux>:-Wl,--version-script=${_RULE_LINUX_LD_SCRIPT}>"
      )
    endif()
    target_link_libraries(
      "${_RULE_NAME}"
      PRIVATE ${_DYLIB_COMPONENTS}
    )
    set_target_properties("${_RULE_NAME}" PROPERTIES
      VERSION ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}.${PROJECT_VERSION_PATCH}
      SOVERSION ${SOVERSION}
    )
  endif()
endfunction()

function(amdsmi_cc_component)
  cmake_parse_arguments(
    _RULE
    ""
    "NAME"
    "HDRS;SRCS;DEFINES;DEPS;COMPONENTS"
    ${ARGN}
  )
  if(AMDSMI_BUILD_STATIC)
    # Static object library.
    set(_STATIC_OBJECTS_NAME "${_RULE_NAME}.objects")
    amdsmi_components_to_static_libs(_STATIC_COMPONENTS ${_RULE_COMPONENTS})
    add_library(${_STATIC_OBJECTS_NAME} OBJECT)
    target_sources(${_STATIC_OBJECTS_NAME}
      PRIVATE
        ${_RULE_SRCS}
        ${_RULE_HDRS}
    )
    target_compile_options(${_STATIC_OBJECTS_NAME} PRIVATE ${AMDSMI_DEFAULT_COPTS})
    target_link_libraries(${_STATIC_OBJECTS_NAME}
      PUBLIC
        _amdsmi_defs
        ${_STATIC_COMPONENTS}
        ${_RULE_DEPS}
    )
    target_compile_definitions(${_STATIC_OBJECTS_NAME} PUBLIC ${_RULE_DEFINES})
  endif()

  if(AMDSMI_BUILD_DYNAMIC)
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)
    set(_DYLIB_OBJECTS_NAME "${_RULE_NAME}.dylib.objects")
    amdsmi_components_to_dynamic_libs(_DYLIB_COMPONENTS ${_RULE_COMPONENTS})
    # Dylib object library.
    add_library(${_DYLIB_OBJECTS_NAME} OBJECT)
    target_sources(${_DYLIB_OBJECTS_NAME}
      PRIVATE
        ${_RULE_SRCS}
        ${_RULE_HDRS}
    )
    target_compile_options(${_DYLIB_OBJECTS_NAME} PRIVATE ${AMDSMI_DEFAULT_COPTS})
    target_link_libraries(${_DYLIB_OBJECTS_NAME}
      PUBLIC
        _amdsmi_defs
        ${_DYLIB_COMPONENTS}
        ${_RULE_DEPS}
    )
    set_target_properties(
      ${_DYLIB_OBJECTS_NAME} PROPERTIES
      CXX_VISIBILITY_PRESET hidden
      C_VISIBILITY_PRESET hidden
      VISIBILITY_INLINES_HIDDEN ON
    )
    target_compile_definitions(${_DYLIB_OBJECTS_NAME}
      PRIVATE
        _AMDSMI_BUILDING_DYLIB
    )
    target_compile_definitions(${_DYLIB_OBJECTS_NAME} PUBLIC ${_RULE_DEFINES})
  endif()
endfunction()

function(amdsmi_components_to_static_libs out_static_libs)
  set(_LIBS ${ARGN})
  list(TRANSFORM _LIBS APPEND ".objects")
  set(${out_static_libs} ${_LIBS} PARENT_SCOPE)
endfunction()

function(amdsmi_components_to_dynamic_libs out_dynamic_libs)
  set(_LIBS ${ARGN})
  list(TRANSFORM _LIBS APPEND ".dylib.objects")
  set(${out_dynamic_libs} "${_LIBS}" PARENT_SCOPE)
endfunction()

function(amdsmi_gtest_test)
  cmake_parse_arguments(
    _RULE
    ""
    "NAME"
    "SRCS;DEPS"
    ${ARGN}
  )

  if(NOT AMDSMI_BUILD_TESTS)
    return()
  endif()

  add_executable(${_RULE_NAME} ${_RULE_SRCS})
  target_link_libraries(${_RULE_NAME} PRIVATE
    ${_RULE_DEPS}
    ${AMDSMI_LINK_LIBRARY_NAME}
    GTest::gmock
    GTest::gtest_main
  )
  gtest_discover_tests(
    ${_RULE_NAME}
    WORKING_DIRECTORY "${CMAKE_BINARY_DIR}"
  )
endfunction()

# Make changes to the global compile flags and properties before including
# bundled deps. This configures various options aimed at making the bundled
# dependencies private.
macro(amdsmi_push_bundled_lib_options)
  set(AMDSMI_ORIG_CXX_VISIBILITY_PRESET "${CMAKE_CXX_VISIBILITY_PRESET}")
  set(AMDSMI_ORIG_C_VISIBILITY_PRESET "${CMAKE_C_VISIBILITY_PRESET}")
  set(AMDSMI_ORIG_VISIBILITY_INLINES_HIDDEN "${CMAKE_VISIBILITY_INLINES_HIDDEN}")
  set(AMDSMI_ORIG_CXX_FLAGS "${CMAKE_CXX_FLAGS}")

  # Callers get a known state for visibility controls and can make changes from there.
  set(CMAKE_C_VISIBILITY_PRESET "default")
  set(CMAKE_CXX_VISIBILITY_PRESET "default")
  set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)
endmacro()

macro(amdsmi_pop_bundled_lib_options)
  set(CMAKE_CXX_VISIBILITY_PRESET ${AMDSMI_ORIG_CXX_VISIBILITY_PRESET})
  set(CMAKE_C_VISIBILITY_PRESET ${AMDSMI_ORIG_C_VISIBILITY_PRESET})
  set(CMAKE_VISIBILITY_INLINES_HIDDEN ${AMDSMI_ORIG_VISIBILITY_INLINES_HIDDEN})
  set(CMAKE_CXX_FLAGS "${AMDSMI_ORIG_CXX_FLAGS}")
endmacro()
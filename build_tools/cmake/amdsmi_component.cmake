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

# Define global definitions target for AMDSMI
add_library(_amdsmi_defs INTERFACE)

target_include_directories(_amdsmi_defs INTERFACE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include/amd_smi>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/rocm_smi/include>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/third_party/shared_mutex>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
  $<INSTALL_INTERFACE:include>
)

target_compile_definitions(_amdsmi_defs INTERFACE
  # Standard definitions for AMDSMI library
  AMDSMI_BUILD
)

# Set C++ standard requirements
target_compile_features(_amdsmi_defs INTERFACE
  cxx_std_17
)

# Add platform-specific definitions
if(WIN32)
  target_compile_definitions(_amdsmi_defs INTERFACE
    WIN32_LEAN_AND_MEAN
    NOMINMAX
  )
elseif(UNIX)
  target_compile_definitions(_amdsmi_defs INTERFACE
    _GNU_SOURCE
  )
endif()

# Debug/Release specific definitions
target_compile_definitions(_amdsmi_defs INTERFACE
  $<$<CONFIG:Debug>:AMDSMI_DEBUG>
  $<$<CONFIG:Release>:NDEBUG>
)
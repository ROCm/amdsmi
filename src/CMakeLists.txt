# Copyright (c) Advanced Micro Devices, Inc. All rights reserved.

# Core library components
amdsmi_cc_component(
  NAME core
  SRCS
    amd_smi/amd_smi.cc
    amd_smi/amd_smi_common.cc
    amd_smi/amd_smi_utils.cc
    amd_smi/amd_smi_uuid.cc
  HDRS
    ${CMAKE_CURRENT_SOURCE_DIR}/../include/amd_smi/amdsmi.h
    ${CMAKE_CURRENT_SOURCE_DIR}/../include/amd_smi/impl/amd_smi_common.h
    ${CMAKE_CURRENT_SOURCE_DIR}/../include/amd_smi/impl/amd_smi_utils.h
  DEPS
    Threads::Threads
    ${DRM_LIBRARIES}
    ${DL_LIB}
    ${RT_LIB}
)

# GPU-specific components
amdsmi_cc_component(
  NAME gpu
  SRCS
    amd_smi/amd_smi_gpu_device.cc
    amd_smi/amd_smi_drm.cc
    amd_smi/fdinfo.cc
  HDRS
    ${CMAKE_CURRENT_SOURCE_DIR}/../include/amd_smi/impl/amd_smi_gpu_device.h
    ${CMAKE_CURRENT_SOURCE_DIR}/../include/amd_smi/impl/amd_smi_drm.h
  COMPONENTS
    core
)

# System-level components
amdsmi_cc_component(
  NAME system
  SRCS
    amd_smi/amd_smi_system.cc
    amd_smi/amd_smi_socket.cc
    amd_smi/amd_smi_cper.cc
  HDRS
    ${CMAKE_CURRENT_SOURCE_DIR}/../include/amd_smi/impl/amd_smi_system.h
    ${CMAKE_CURRENT_SOURCE_DIR}/../include/amd_smi/impl/amd_smi_socket.h
  COMPONENTS
    core
)

# Support utilities
amdsmi_cc_component(
  NAME support
  SRCS
    amd_smi/amd_smi_lib_loader.cc
    amd_smi/scoped_fd.cc
    rocm_smi_properties.cc
  HDRS
    ${CMAKE_CURRENT_SOURCE_DIR}/../include/amd_smi/impl/amd_smi_lib_loader.h
  COMPONENTS
    core
  DEPS
    rocm_smi64
)

# Assemble the main library
amdsmi_public_library(
  NAME amdsmi
  COMPONENTS
    core
    gpu
    system
    support
  USAGE_DEPS
    Threads::Threads
)
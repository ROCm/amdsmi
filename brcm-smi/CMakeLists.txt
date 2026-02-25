# BRCM SMI Library integration
# This file is included when ENABLE_BRCM_SMI is set in the main CMakeLists.txt

# Note: CMAKE_CXX_STANDARD and other global settings are inherited from parent

# BRCM SMI source and include directories
set(BRCM_SMI_INC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")
set(BRCM_SMI_SRC_DIR "${CMAKE_CURRENT_SOURCE_DIR}/src")

# Include directories
include_directories(${BRCM_SMI_INC_DIR})

# Source files
set(BRCM_SMI_SOURCES
    ${BRCM_SMI_SRC_DIR}/brcm_smi.cc
    ${BRCM_SMI_SRC_DIR}/brcm_smi_discovery.cc
    ${BRCM_SMI_SRC_DIR}/brcm_smi_device.cc
    ${BRCM_SMI_SRC_DIR}/brcm_smi_utils.cc
    ${BRCM_SMI_SRC_DIR}/brcm_smi_nic_device.cc
    ${BRCM_SMI_SRC_DIR}/brcm_smi_switch_device.cc
    ${BRCM_SMI_SRC_DIR}/brcm_smi_no_drm_nic.cc
    ${BRCM_SMI_SRC_DIR}/brcm_smi_no_drm_switch.cc
    ${BRCM_SMI_SRC_DIR}/brcm_smi_lspci_commands.cc
    ${BRCM_SMI_SRC_DIR}/brcm_smi_socket.cc
    ${BRCM_SMI_SRC_DIR}/brcm_smi_processor.cc
    ${BRCM_SMI_SRC_DIR}/brcm_smi_system.cc
)

# Header files
set(BRCM_SMI_HEADERS
    ${BRCM_SMI_INC_DIR}/brcm_smi/brcmsmi.h
    ${BRCM_SMI_INC_DIR}/brcm_smi/brcm_smi_device.h
    ${BRCM_SMI_INC_DIR}/brcm_smi/brcm_smi_utils.h
    ${BRCM_SMI_INC_DIR}/brcm_smi/impl/brcm_smi_nic_device.h
    ${BRCM_SMI_INC_DIR}/brcm_smi/impl/brcm_smi_switch_device.h
    ${BRCM_SMI_INC_DIR}/brcm_smi/impl/brcm_smi_no_drm_nic.h
    ${BRCM_SMI_INC_DIR}/brcm_smi/impl/brcm_smi_no_drm_switch.h
    ${BRCM_SMI_INC_DIR}/brcm_smi/impl/brcm_smi_utils.h
    ${BRCM_SMI_INC_DIR}/brcm_smi/impl/brcm_smi_lspci_commands.h
    ${BRCM_SMI_INC_DIR}/brcm_smi/impl/brcm_smi_processor.h
    ${BRCM_SMI_INC_DIR}/brcm_smi/impl/brcm_smi_socket.h
    ${BRCM_SMI_INC_DIR}/brcm_smi/impl/brcm_smi_system.h
)

# Add BRCM SMI sources to the main AMD SMI library
# The BRCM SMI functionality will be integrated into the main amd_smi library

# Add BRCM SMI sources to the main source list
list(APPEND CMN_SRC_LIST ${BRCM_SMI_SOURCES})

# Add BRCM SMI headers to the main header list  
list(APPEND CMN_INC_LIST ${BRCM_SMI_HEADERS})

# Add BRCM SMI compile definition
add_definitions("-DENABLE_BRCM_SMI=1")

message(STATUS "BRCM SMI sources added to main library: ${BRCM_SMI_SOURCES}")
message(STATUS "BRCM SMI headers added to main library: ${BRCM_SMI_HEADERS}")

# Install BRCM SMI headers alongside AMD SMI headers
install(DIRECTORY ${BRCM_SMI_INC_DIR}/
    DESTINATION include
    COMPONENT dev
    FILES_MATCHING PATTERN "*.h"
)

# Optional: Add BRCM SMI CLI tools if they exist
if(BUILD_CLI AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/cli")
    message(STATUS "Adding BRCM SMI CLI tools")
    add_subdirectory(cli)
endif()

# Optional: Add BRCM SMI tests if they exist and BUILD_TESTS is enabled
if(BUILD_TESTS AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/tests")
    message(STATUS "Adding BRCM SMI tests")
    add_subdirectory(tests)
endif()
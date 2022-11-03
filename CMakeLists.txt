#
# Minimum version of cmake required
#
cmake_minimum_required(VERSION 3.11)

set(AMD_SMI_LIBS_TARGET "amd_smi_libraries")

set(BUILD_SHARED_LIBS
    ON
    CACHE BOOL "Build shared library (.so) or not.")

set(CMAKE_MODULE_PATH
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake_modules/"
    CACHE INTERNAL "Default module path.")
## Include common cmake modules
include(utils)
include(GNUInstallDirs)
find_package(PkgConfig)

if(NOT DEFINED CPACK_RESOURCE_FILE_LICENSE)
    set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/License.txt")
endif()

set(ROCM_SMI "amd_smi")
set(ROCM_SMI_COMPONENT "lib${ROCM_SMI}")
set(ROCM_SMI_TARGET "${ROCM_SMI}64")
set(ROCM_SMI_LIB_NAME "lib${ROCM_SMI_TARGET}")

# provide git to utilities
find_program(GIT NAMES git)

## Setup the package version based on git tags.
set(PKG_VERSION_GIT_TAG_PREFIX "rsmi_pkg_ver")
get_package_version_number("1.0.0" ${PKG_VERSION_GIT_TAG_PREFIX} GIT)
message("Package version: ${PKG_VERSION_STR}")
set(${AMD_SMI_LIBS_TARGET}_VERSION_MAJOR "${VERSION_MAJOR}")
set(${AMD_SMI_LIBS_TARGET}_VERSION_MINOR "${VERSION_MINOR}")
set(${AMD_SMI_LIBS_TARGET}_VERSION_PATCH "0")
set(${AMD_SMI_LIBS_TARGET}_VERSION_BUILD "0")

# The following default version values should be updated as appropriate for
# ABI breaks (update MAJOR and MINOR), and ABI/API additions (update MINOR).
# Until ABI stabilizes VERSION_MAJOR will be 0. This should be over-ridden
# by git tags (through "git describe") when they are present.
set(PKG_VERSION_MAJOR 1)
set(PKG_VERSION_MINOR 0)
set(PKG_VERSION_PATCH 0)
set(PKG_VERSION_NUM_COMMIT 0)

## Define default variable and variables for the optional build target
##  amd_smi_lib-dev
set(CMAKE_INSTALL_PREFIX
    "/opt/rocm"
    CACHE STRING "Default installation directory.")
set(ROCM_SMI_PACKAGE amd-smi-lib)

project(${AMD_SMI_LIBS_TARGET})

option(CMAKE_VERBOSE_MAKEFILE "Enable verbose output" ON)

option(CMAKE_EXPORT_COMPILE_COMMANDS "Export compile commands for linters and autocompleters" ON)

option(BUILD_TESTS "Build test suite" OFF)

if(CMAKE_COMPILER_IS_GNUCC AND CMAKE_CXX_COMPILER_VERSION VERSION_LESS 5.4.0)
    message("Compiler version is " ${CMAKE_CXX_COMPILER_VERSION})
    message(FATAL_ERROR "Require at least gcc-5.4.0")
endif()

## Compiler flags
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -fno-rtti -m64 -msse -msse2 -std=c++11")
# Security options
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wconversion -Wcast-align")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wformat=2 -fno-common -Wstrict-overflow")
# Intentionally leave out -Wsign-promo. It causes spurious warnings.
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Woverloaded-virtual -Wreorder")

# Clang does not set the build-id
if(CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    set(CMAKE_SHARED_LINKER_FLAGS "-Wl,--build-id=sha1")
endif()

## Address Sanitize Flag
if(${ADDRESS_SANITIZER})
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address -g")
    set(CMAKE_EXE_LINKER_FLAGS -fsanitize=address)

    if(BUILD_SHARED_LIBS})
        set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -shared-libsan")
    else()
        set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -static-libsan")
    endif()
else()
    ## Security breach mitigation flags
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DFORTIFY_SOURCE=2 -fstack-protector-all -Wcast-align")
    ## More security breach mitigation flags
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wl,-z,noexecstack -Wl,-znoexecheap -Wl,-z,relro")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wtrampolines -Wl,-z,now -fPIE")
endif()

# Use this instead of above for 32 bit
# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -m32")

if("${CMAKE_BUILD_TYPE}" STREQUAL Release)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2")
else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -ggdb -O0 -DDEBUG")
endif()

set(COMMON_SRC_DIR "${PROJECT_SOURCE_DIR}/src")
set(ROCM_SRC_DIR "${PROJECT_SOURCE_DIR}/rocm_smi/src")
set(AMDSMI_SRC_DIR "${PROJECT_SOURCE_DIR}/src/amd_smi")
set(COMMON_INC_DIR "${PROJECT_SOURCE_DIR}/include/amd_smi")
set(AMDSMI_INC_DIR "${PROJECT_SOURCE_DIR}/include/amd_smi")
set(ROCM_INC_DIR "${PROJECT_SOURCE_DIR}/rocm_smi/include/rocm_smi")
set(SHR_MUTEX_DIR "${PROJECT_SOURCE_DIR}/third_party/shared_mutex")

pkg_check_modules(DRM REQUIRED libdrm)
pkg_check_modules(AMDGPU_DRM REQUIRED libdrm_amdgpu)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include ${CMAKE_CURRENT_SOURCE_DIR}/third_party/shared_mutex
                    ${CMAKE_CURRENT_SOURCE_DIR}/amd_smi/include ${DRM_INCLUDE_DIRS})

set(CMN_SRC_LIST
    "${AMDSMI_SRC_DIR}/amd_smi.cc"
    "${AMDSMI_SRC_DIR}/amd_smi_common.cc"
    "${AMDSMI_SRC_DIR}/amd_smi_drm.cc"
    "${AMDSMI_SRC_DIR}/amd_smi_gpu_device.cc"
    "${AMDSMI_SRC_DIR}/amd_smi_lib_loader.cc"
    "${AMDSMI_SRC_DIR}/amd_smi_socket.cc"
    "${AMDSMI_SRC_DIR}/amd_smi_system.cc"
    "${AMDSMI_SRC_DIR}/amd_smi_utils.cc"
    "${AMDSMI_SRC_DIR}/amd_smi_uuid.cc"
    "${AMDSMI_SRC_DIR}/fdinfo.cc"
    "${ROCM_SRC_DIR}/rocm_smi.cc"
    "${ROCM_SRC_DIR}/rocm_smi_counters.cc"
    "${ROCM_SRC_DIR}/rocm_smi_device.cc"
    "${ROCM_SRC_DIR}/rocm_smi_gpu_metrics.cc"
    "${ROCM_SRC_DIR}/rocm_smi_io_link.cc"
    "${ROCM_SRC_DIR}/rocm_smi_kfd.cc"
    "${ROCM_SRC_DIR}/rocm_smi_main.cc"
    "${ROCM_SRC_DIR}/rocm_smi_monitor.cc"
    "${ROCM_SRC_DIR}/rocm_smi_power_mon.cc"
    "${ROCM_SRC_DIR}/rocm_smi_utils.cc"
    "${SHR_MUTEX_DIR}/shared_mutex.cc")

set(CMN_INC_LIST
    "${COMMON_INC_DIR}/amd_smi.h"
    "${COMMON_INC_DIR}/impl/amd_smi_common.h"
    "${COMMON_INC_DIR}/impl/amd_smi_device.h"
    "${COMMON_INC_DIR}/impl/amd_smi_drm.h"
    "${COMMON_INC_DIR}/impl/amd_smi_gpu_device.h"
    "${COMMON_INC_DIR}/impl/amd_smi_lib_loader.h"
    "${COMMON_INC_DIR}/impl/amd_smi_socket.h"
    "${COMMON_INC_DIR}/impl/amd_smi_system.h"
    "${ROCM_INC_DIR}/rocm_smi.h"
    "${ROCM_INC_DIR}/rocm_smi_common.h"
    "${ROCM_INC_DIR}/rocm_smi_counters.h"
    "${ROCM_INC_DIR}/rocm_smi_device.h"
    "${ROCM_INC_DIR}/rocm_smi_exception.h"
    "${ROCM_INC_DIR}/rocm_smi_io_link.h"
    "${ROCM_INC_DIR}/rocm_smi_kfd.h"
    "${ROCM_INC_DIR}/rocm_smi_main.h"
    "${ROCM_INC_DIR}/rocm_smi_monitor.h"
    "${ROCM_INC_DIR}/rocm_smi_power_mon.h"
    "${ROCM_INC_DIR}/rocm_smi_utils.h"
    "${SHR_MUTEX_DIR}/shared_mutex.h")

add_subdirectory("rocm_smi")

if(BUILD_TESTS)
    add_subdirectory("tests/rocm_smi_test")
    add_subdirectory("tests/amd_smi_test")
endif()

# Examples and docs
set(SMI_EXAMPLE_EXE "amd_smi_drm_ex")
add_executable(${SMI_EXAMPLE_EXE} "example/amd_smi_drm_example.cc")
target_link_libraries(${SMI_EXAMPLE_EXE} ${ROCM_SMI_TARGET})
add_dependencies(${SMI_EXAMPLE_EXE} ${ROCM_SMI_TARGET})

set(SMI_NODRM_EXAMPLE_EXE "amd_smi_nodrm_ex")
add_executable(${SMI_NODRM_EXAMPLE_EXE} "example/amd_smi_nodrm_example.cc")
target_link_libraries(${SMI_NODRM_EXAMPLE_EXE} ${ROCM_SMI_TARGET})
add_dependencies(${SMI_NODRM_EXAMPLE_EXE} ${ROCM_SMI_TARGET})

# Generate Doxygen documentation
find_package(Doxygen)
find_package(LATEX COMPONENTS PDFLATEX)

if(DOXYGEN_FOUND AND LATEX_FOUND)
    set(RSMI_MANUAL_NAME "AMD_SMI_Manual")
    configure_file(${CMAKE_CURRENT_SOURCE_DIR}/docs/amd_smi_doxygen.cfg ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile @ONLY)

    add_custom_command(
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/latex/refman.tex
        COMMAND ${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/docs/amd_smi_doxygen.cfg "${AMDSMI_INC_DIR}/amd_smi.h"
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
    add_custom_command(
        OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/latex/refman.pdf
        COMMAND make > /dev/null
        COMMAND cp ${CMAKE_CURRENT_BINARY_DIR}/latex/refman.pdf
                ${CMAKE_CURRENT_SOURCE_DIR}/docs/${RSMI_MANUAL_NAME}_new.pdf
        DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/latex/refman.tex
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/latex)

    add_custom_target(amdsmi_docs DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/latex/refman.pdf)

    add_dependencies(${ROCM_SMI_TARGET} amdsmi_docs)
    install(
        FILES ${CMAKE_CURRENT_BINARY_DIR}/latex/refman.pdf
        DESTINATION share/doc/${ROCM_SMI}
        RENAME ${RSMI_MANUAL_NAME}.pdf)
    install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/README.md DESTINATION share/doc/${ROCM_SMI}/)
else()
    message("Doxygen or Latex is not found. Will not generate documents.")
endif(DOXYGEN_FOUND AND LATEX_FOUND)

# Generate python_wrapper and package targets
find_program(PYTHON3 "python3")
find_program(PIP3 "pip3")

if(PYTHON3 AND PIP3)
    add_custom_command(
        OUTPUT clang_tools_extract
        COMMAND mkdir -p ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper
        COMMAND pip3 download ctypeslib2==2.3.2 -d ${CMAKE_CURRENT_BINARY_DIR}/dl
        COMMAND pip3 download clang==10.0.1 -d ${CMAKE_CURRENT_BINARY_DIR}/dl
        COMMAND unzip -o ${CMAKE_CURRENT_BINARY_DIR}/dl/ctypeslib2-2.3.2-py3-none-any.whl -d
                ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper
        COMMAND unzip -o ${CMAKE_CURRENT_BINARY_DIR}/dl/clang-10.0.1-py3-none-any.whl -d
                ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})

    add_custom_target(
        python_wrapper
        DEPENDS clang_tools_extract
        COMMAND mkdir -p ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper
        COMMAND cp -r ${CMAKE_CURRENT_SOURCE_DIR}/include/amd_smi/amd_smi.h ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper
        COMMAND mkdir -p ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper/rocm_smi
        COMMAND cp ${CMAKE_CURRENT_SOURCE_DIR}/rocm_smi/include/rocm_smi/kfd_ioctl.h
                ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper/rocm_smi/
        COMMAND
            python3 ${CMAKE_CURRENT_SOURCE_DIR}/tools/generator.py ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper/amd_smi.h
            ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper/ ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper/
        COMMAND cp ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper/amdsmi_wrapper.py
                ${CMAKE_CURRENT_SOURCE_DIR}/py-interface/
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper)

    set(PY_INTERFACE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/py-interface")
    set(PACKAGE_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/python_package/amdsmi")

    add_custom_target(
        python_package
        DEPENDS python_wrapper
        COMMAND mkdir -p ${PACKAGE_OUTPUT_DIR}
        COMMAND cp ${PY_INTERFACE_DIR}/__init__.py ${PACKAGE_OUTPUT_DIR}
        COMMAND cp ${PY_INTERFACE_DIR}/amdsmi_exception.py ${PACKAGE_OUTPUT_DIR}
        COMMAND cp ${PY_INTERFACE_DIR}/amdsmi_interface.py ${PACKAGE_OUTPUT_DIR}
        COMMAND cp ${PY_INTERFACE_DIR}/amdsmi_wrapper.py ${PACKAGE_OUTPUT_DIR}
        COMMAND cp ${PY_INTERFACE_DIR}/README.md ${PACKAGE_OUTPUT_DIR}
        COMMAND cp ${CMAKE_CURRENT_BINARY_DIR}/rocm_smi/libamd_smi64.so ${PACKAGE_OUTPUT_DIR}
        COMMAND cp ${CMAKE_CURRENT_SOURCE_DIR}/LICENSE ${PACKAGE_OUTPUT_DIR}
        COMMAND echo ${PACKAGE_OUTPUT_DIR})

else()
    message("Python3 or Pip3 not found.")
endif(PYTHON3 AND PIP3)

include(CMakePackageConfigHelpers)

configure_package_config_file(amd_smi-config.cmake.in ${CMAKE_CURRENT_BINARY_DIR}/amd_smi-config.cmake
                              INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/amd_smi)

write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/amd_smi-config-version.cmake
    VERSION
        "${AMD_SMI_LIBS_TARGET_VERSION_MAJOR}.${AMD_SMI_LIBS_TARGET_VERSION_MINOR}.${AMD_SMI_LIBS_TARGET_VERSION_PATCH}"
    COMPATIBILITY SameMajorVersion)

install(
    FILES ${CMAKE_CURRENT_BINARY_DIR}/amd_smi-config.cmake ${CMAKE_CURRENT_BINARY_DIR}/amd_smi-config-version.cmake
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/${ROCM_SMI}
    COMPONENT dev)

# Create cmake target
# Add all targets to the build-tree export set
export(TARGETS ${ROCM_SMI_TARGET} FILE "${PROJECT_BINARY_DIR}/rcom_smi_target.cmake")

# Export the package for use from the build-tree
# (this registers the build-tree with a global CMake-registry)
export(PACKAGE amd_smi)
# Create the amd_smiConfig.cmake and amd_smiConfigVersion files
# ... for the build tree
install(
    EXPORT rocm_smiTargets
    DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${ROCM_SMI}"
    COMPONENT dev)

#License file
set(CPACK_RPM_PACKAGE_LICENSE "NCSA")
install(
    FILES ${CPACK_RESOURCE_FILE_LICENSE}
    DESTINATION share/doc/${ROCM_SMI}
    RENAME LICENSE.txt)

###########################
# Packaging directives
###########################
set(CPACK_GENERATOR
    "DEB;RPM"
    CACHE STRING "Default packaging generators.")
set(CPACK_PACKAGING_INSTALL_PREFIX
    "${CMAKE_INSTALL_PREFIX}"
    CACHE STRING "Default packaging prefix.")
set(ENABLE_LDCONFIG
    ON
    CACHE BOOL "Set library links and caches using ldconfig.")
set(CPACK_PACKAGE_NAME ${ROCM_SMI_PACKAGE})
set(CPACK_PACKAGE_VENDOR "Advanced Micro Devices, Inc.")
set(CPACK_PACKAGE_CONTACT "RocmSMILib Support <rocm-smi.support@amd.com>")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "AMD System Management libraries")

#Make proper version for appending
#Default Value is 99999, setting it first
set(ROCM_VERSION_FOR_PACKAGE "99999")
if(DEFINED ENV{ROCM_LIBPATCH_VERSION})
    set(ROCM_VERSION_FOR_PACKAGE $ENV{ROCM_LIBPATCH_VERSION})
endif()

#Debian package specific variables
set(CPACK_DEBIAN_PACKAGE_HOMEPAGE
    ${CPACK_DEBIAN_PACKAGE_HOMEPAGE}
    CACHE STRING "https://github.com/RadeonOpenCompute/ROCm")
if(DEFINED ENV{CPACK_DEBIAN_PACKAGE_RELEASE})
    set(CPACK_DEBIAN_PACKAGE_RELEASE $ENV{CPACK_DEBIAN_PACKAGE_RELEASE})
else()
    set(CPACK_DEBIAN_PACKAGE_RELEASE "local")
endif()
set(CPACK_DEBIAN_PACKAGE_PROVIDES "rocm-smi")
set(CPACK_DEBIAN_PACKAGE_SUGGESTS "sudo")
set(CPACK_DEBIAN_PACKAGE_DEPENDS "python3, rocm-core")

## Process the Debian install/remove scripts to update the CPACK variables
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/DEBIAN/postinst.in DEBIAN/postinst @ONLY)
configure_file(${CMAKE_CURRENT_SOURCE_DIR}/DEBIAN/prerm.in DEBIAN/prerm @ONLY)
set(CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA "DEBIAN/postinst;DEBIAN/prerm")

# RPM package specific variables
set(CPACK_RPM_EXCLUDE_FROM_AUTO_FILELIST_ADDITION
    "${CPACK_PACKAGING_INSTALL_PREFIX} ${CPACK_PACKAGING_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}")
if(DEFINED ENV{CPACK_RPM_PACKAGE_RELEASE})
    set(CPACK_RPM_PACKAGE_RELEASE $ENV{CPACK_RPM_PACKAGE_RELEASE})
else()
    set(CPACK_RPM_PACKAGE_RELEASE "local")
endif()
#Set rpm distro
if(CPACK_RPM_PACKAGE_RELEASE)
    set(CPACK_RPM_PACKAGE_RELEASE_DIST ON)
endif()
set(CPACK_RPM_PACKAGE_PROVIDES "rocm-smi")
set(CPACK_RPM_PACKAGE_REQUIRES "python3, rocm-core")

# The line below doesn't currently work; it may be this issue:
# https://bugzilla.redhat.com/show_bug.cgi?id=1811358
# set(CPACK_RPM_PACKAGE_SUGGESTS "sudo")

#Prepare final version for the CPACK use
set(CPACK_PACKAGE_VERSION
    "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}.${CPACK_PACKAGE_VERSION_PATCH}.${ROCM_VERSION_FOR_PACKAGE}"
)

## Process the Rpm install/remove scripts to update the CPACK variables
configure_file("${CMAKE_CURRENT_SOURCE_DIR}/RPM/post.in" RPM/post @ONLY)
configure_file("${CMAKE_CURRENT_SOURCE_DIR}/RPM/postun.in" RPM/postun @ONLY)
set(CPACK_RPM_POST_INSTALL_SCRIPT_FILE "${CMAKE_CURRENT_BINARY_DIR}/RPM/post")
set(CPACK_RPM_POST_UNINSTALL_SCRIPT_FILE "${CMAKE_CURRENT_BINARY_DIR}/RPM/postun")

#Set the names now using CPACK utility
set(CPACK_DEBIAN_FILE_NAME "DEB-DEFAULT")
set(CPACK_RPM_FILE_NAME "RPM-DEFAULT")
# Remove dependency on rocm-core if -DROCM_DEP_ROCMCORE=ON not given to cmake
if(NOT ROCM_DEP_ROCMCORE)
    string(REGEX REPLACE ",? ?rocm-core" "" CPACK_RPM_PACKAGE_REQUIRES ${CPACK_RPM_PACKAGE_REQUIRES})
    string(REGEX REPLACE ",? ?rocm-core" "" CPACK_DEBIAN_PACKAGE_DEPENDS ${CPACK_DEBIAN_PACKAGE_DEPENDS})
endif()

include(CPack)

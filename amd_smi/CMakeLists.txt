#
# Minimum version of cmake required
#

message("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
message("                    CMake AMD SMI (Library)                       ")
message("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")

## Verbose output.
set(CMAKE_VERBOSE_MAKEFILE on)

# Required Defines first:

message("")
message("Build Configuration:")
message("--------Proj Src Dir: " ${PROJECT_SOURCE_DIR})

# Will still use the rocm_smi lib for now.
set(ROCM_SMI "rocm_smi")
set(ROCM_SMI_COMPONENT "lib${ROCM_SMI}")
set(ROCM_SMI_TARGET "${ROCM_SMI}64")

set(SMI_EXAMPLE_EXE "amd_smi_ex")
add_executable(${SMI_EXAMPLE_EXE} "example/amd_smi_example.cc")
target_link_libraries(${SMI_EXAMPLE_EXE} ${ROCM_SMI_TARGET})

# Generate Doxygen documentation
find_package(Doxygen)
find_package(LATEX COMPONENTS PDFLATEX)

if (DOXYGEN_FOUND AND LATEX_FOUND)
  set (RSMI_MANUAL_NAME "AMD_SMI_Manual")
  configure_file(${CMAKE_CURRENT_SOURCE_DIR}/docs/amd_smi_doxygen.cfg
                                   ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile @ONLY)

  add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/latex/refman.tex
        COMMAND ${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile
        DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/docs/amd_smi_doxygen.cfg
                "${AMDSMI_INC_DIR}/amd_smi.h"
         WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})
  add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/latex/refman.pdf
         COMMAND make  > /dev/null
         COMMAND cp  ${CMAKE_CURRENT_BINARY_DIR}/latex/refman.pdf
                  ${CMAKE_CURRENT_SOURCE_DIR}/docs/${RSMI_MANUAL_NAME}_new.pdf
         DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/latex/refman.tex
         WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/latex)

  add_custom_target(amdsmi_docs DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/latex/refman.pdf)

  add_dependencies(${ROCM_SMI_TARGET} amdsmi_docs)
  install(FILES ${CMAKE_CURRENT_BINARY_DIR}/latex/refman.pdf
                         DESTINATION share/doc/${ROCM_SMI} RENAME ${RSMI_MANUAL_NAME}.pdf)
  install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/../README.md
                          DESTINATION share/doc/${ROCM_SMI}/)
else()
  message("Doxygen or Latex is not found. Will not generate documents.")
endif(DOXYGEN_FOUND AND LATEX_FOUND)


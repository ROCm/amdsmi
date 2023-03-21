message("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
message("                     CMake AMDSMI CLI Install                      ")
message("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")


# Set CLI Build Directory
set(PY_PACKAGE_DIR "amdsmi_cli")
set(PY_CLI_INSTALL_DIR
    "${CMAKE_INSTALL_LIBEXECDIR}" CACHE STRING
    "CLI tool installation directory")

# if Python3 is found but the version is below 3.7 - Python3_FOUND is set to FALSE
find_package(Python3 3.7 COMPONENTS Interpreter Development)

# WARN: This is a HACK to pass compile on AMD rhel8 and centos7 CI systems!
#       Those still use python3.6 which is too old for this project!
# TODO: Promote to an error when python3.7 or above is installed on CI
if(NOT Python3_FOUND)
    message(AUTHOR_WARNING "Python3 DOESN'T EXIST OR VERSION IS TOO OLD!: ${Python3_VERSION}")
    message(AUTHOR_WARNING "The CLI tool will not be created and the project will not be packaged!")
    # WARN: EXIT CURRENT CMAKE FILE
    return()
endif()

# hard-linking instead of copying avoids unnecessarry regeneration of packaged files
add_custom_command(
    OUTPUT ${PY_PACKAGE_DIR}/__init__.py
           ${PY_PACKAGE_DIR}/_version.py
           ${PY_PACKAGE_DIR}/amdsmi_cli.py
           ${PY_PACKAGE_DIR}/amdsmi_commands.py
           ${PY_PACKAGE_DIR}/amdsmi_helpers.py
           ${PY_PACKAGE_DIR}/amdsmi_init.py
           ${PY_PACKAGE_DIR}/amdsmi_logger.py
           ${PY_PACKAGE_DIR}/amdsmi_parser.py
           ${PY_PACKAGE_DIR}/BDF.py
    DEPENDS amdsmi_cli
    COMMAND mkdir -p ${PY_PACKAGE_DIR}/
    COMMAND ln -Pf ${CMAKE_CURRENT_SOURCE_DIR}/__init__.py ${PY_PACKAGE_DIR}/
    COMMAND ln -Pf ${CMAKE_CURRENT_SOURCE_DIR}/_version.py ${PY_PACKAGE_DIR}/
    COMMAND ln -Pf ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_cli.py ${PY_PACKAGE_DIR}/
    COMMAND ln -Pf ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_commands.py ${PY_PACKAGE_DIR}/
    COMMAND ln -Pf ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_helpers.py ${PY_PACKAGE_DIR}/
    COMMAND ln -Pf ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_init.py ${PY_PACKAGE_DIR}/
    COMMAND ln -Pf ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_logger.py ${PY_PACKAGE_DIR}/
    COMMAND ln -Pf ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_parser.py ${PY_PACKAGE_DIR}/
    COMMAND ln -Pf ${CMAKE_CURRENT_SOURCE_DIR}/BDF.py ${PY_PACKAGE_DIR}/)

# The CLI requires the python amdsmi wrapper to be installed
add_custom_target(
    amdsmi_cli ALL
    DEPENDS python_package
            ${PY_PACKAGE_DIR}/__init__.py
            ${PY_PACKAGE_DIR}/_version.py
            ${PY_PACKAGE_DIR}/amdsmi_cli.py
            ${PY_PACKAGE_DIR}/amdsmi_commands.py
            ${PY_PACKAGE_DIR}/amdsmi_helpers.py
            ${PY_PACKAGE_DIR}/amdsmi_init.py
            ${PY_PACKAGE_DIR}/amdsmi_logger.py
            ${PY_PACKAGE_DIR}/amdsmi_parser.py
            ${PY_PACKAGE_DIR}/BDF.py)

install(
    DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${PY_PACKAGE_DIR}
    DESTINATION ${PY_CLI_INSTALL_DIR})

install(
    PROGRAMS ${CMAKE_CURRENT_BINARY_DIR}/${PY_PACKAGE_DIR}/amdsmi_cli.py
    DESTINATION ${PY_CLI_INSTALL_DIR}/${PY_PACKAGE_DIR})

file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bin)

# symlink amdsmi_cli.py to amd-smi
add_custom_target(
    link_amdsmi_cli ALL
    DEPENDS amdsmi_cli
    BYPRODUCTS ${CMAKE_CURRENT_BINARY_DIR}/bin/amd-smi
           ${CMAKE_CURRENT_BINARY_DIR}/bin/gpuv-smi
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMAND ${CMAKE_COMMAND} -E create_symlink
            ../${PY_CLI_INSTALL_DIR}/${PY_PACKAGE_DIR}/amdsmi_cli.py
            ${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_INSTALL_BINDIR}/amd-smi
    COMMAND ${CMAKE_COMMAND} -E create_symlink
            amd-smi
            ${CMAKE_CURRENT_BINARY_DIR}/bin/gpuv-smi)

install(
    FILES ${CMAKE_CURRENT_BINARY_DIR}/bin/amd-smi
          ${CMAKE_CURRENT_BINARY_DIR}/bin/gpuv-smi
    DESTINATION ${CMAKE_INSTALL_BINDIR})

message("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
message("                     CMake AMDSMI CLI Install                      ")
message("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")


# Set CLI Build Directory
set(CLI_BUILD_DIR "amdsmi_cli" CACHE STRING "")
set(SHARE_WHL_LOCATION "${SHARE_INSTALL_PREFIX}/${AMD_SMI}/amdsmi-0.1-py3-none-any.whl")

# The CLI requires the python amdsmi wrapper whl file to exist
add_custom_target(
    amdsmi_cli
    DEPENDS SHARE_WHL_LOCATION)

# if Python3 is found but the version is below 3.7 - Python3_FOUND is set to FALSE
find_package(Python3 3.7 COMPONENTS Interpreter)

# WARN: This is a HACK to pass compile on AMD rhel8 CI systems!
#       Those still use python3.6 which is too old for this project!
if(NOT Python3_FOUND)
    message(AUTHOR_WARNING "Python3 DOESN'T EXIST OR VERSION IS TOO OLD!: ${Python3_VERSION}")
    # WARN: EXIT CURRENT CMAKE FILE
    return()
endif()

add_custom_target(
    amdsmi_whl_install
    COMMAND ${Python3_EXECUTABLE} -m pip install --upgrade --force-reinstall SHARE_WHL_LOCATION)

# symlinking instead of copying avoids unnecessarry regeneration of packaged files
add_custom_command(
    OUTPUT ${CLI_BUILD_DIR}/pyproject.toml
           ${CLI_BUILD_DIR}/__init__.py
           ${CLI_BUILD_DIR}/_version.py
           ${CLI_BUILD_DIR}/amdsmi_cli.py
           ${CLI_BUILD_DIR}/amdsmi_commands.py
           ${CLI_BUILD_DIR}/amdsmi_helpers.py
           ${CLI_BUILD_DIR}/amdsmi_logger.py
           ${CLI_BUILD_DIR}/amdsmi_parser.py
           ${CLI_BUILD_DIR}/BDF.py
    DEPENDS amdsmi_cli
            amdsmi_whl_install
    COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/pyproject.toml ${CLI_BUILD_DIR}/
    COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/__init__.py ${CLI_BUILD_DIR}/
    COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/_version.py ${CLI_BUILD_DIR}/
    COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_cli.py ${CLI_BUILD_DIR}/
    COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_commands.py ${CLI_BUILD_DIR}/
    COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_helpers.py ${CLI_BUILD_DIR}/
    COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_logger.py ${CLI_BUILD_DIR}/
    COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_parser.py ${CLI_BUILD_DIR}/
    COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/BDF.py ${CLI_BUILD_DIR}/)

install(
    FILES _version.py
          amdsmi_commands.py
          amdsmi_helpers.py
          amdsmi_init.py
          amdsmi_logger.py
          amdsmi_parser.py
          BDF.py
    DESTINATION ${CMAKE_INSTALL_LIBEXECDIR}/${AMD_SMI}/amdsmi_cli)

install(
    FILES ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_cli.py
    PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ
    GROUP_WRITE GROUP_EXECUTE WORLD_READ WORLD_EXECUTE
    DESTINATION ${CMAKE_INSTALL_LIBEXECDIR}/${AMD_SMI}/amdsmi_cli)
install(
    FILES ${CMAKE_CURRENT_BINARY_DIR}/bin/amd-smi
    DESTINATION ${CMAKE_INSTALL_BINDIR})
install(
    FILES ${CMAKE_CURRENT_BINARY_DIR}/bin/gpuv-smi
    DESTINATION ${CMAKE_INSTALL_BINDIR})

# symlink amdsmi_cli.py to amd-smi
file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/bin)
add_custom_target(
    link_amdsmi_cli ALL
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMAND ${CMAKE_COMMAND} -E create_symlink
            ../${CMAKE_INSTALL_LIBEXECDIR}/${AMD_SMI}/amdsmi_cli/amdsmi_cli.py
            ${CMAKE_CURRENT_BINARY_DIR}/bin/amd-smi)

add_custom_target(
    link_gpuvsmi_cli ALL
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMAND ${CMAKE_COMMAND} -E create_symlink
            ../${CMAKE_INSTALL_LIBEXECDIR}/${AMD_SMI}/amdsmi_cli/amdsmi_cli.py
            ${CMAKE_CURRENT_BINARY_DIR}/bin/gpuv-smi)

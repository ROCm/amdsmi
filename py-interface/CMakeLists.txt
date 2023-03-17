# Generate py-interface and package targets

# match this version to your clang
# too new won't work, too old won't work either
set(clang_ver 14.0)
set(ctypeslib_ver 2.3.2)

set(PY_BUILD_DIR "python_package" CACHE STRING "")
# amdsmi part of this string is the directory containing all python files
# additionally defined in pyproject.toml
set(PY_PACKAGE_DIR "${PY_BUILD_DIR}/amdsmi" CACHE STRING "")

# if Python3 is found but the version is below 3.7 - Python3_FOUND is set to FALSE
find_package(Python3 3.7 COMPONENTS Interpreter)

# WARN: This is a HACK to pass compile on AMD rhel8 CI systems!
#       Those still use python3.6 which is too old for this project!
# TODO: drop python3.6 support
if(NOT Python3_FOUND)
    message(AUTHOR_WARNING "Python3 DOESN'T EXIST OR VERSION IS TOO OLD!: ${Python3_VERSION}")
    message(AUTHOR_WARNING "The wrapper will not be created and the project will not be packaged!")
    # WARN: EXIT CURRENT CMAKE FILE
    return()
endif()

# check if virtualenv is installed
execute_process(COMMAND "${Python3_EXECUTABLE}" -m pip show virtualenv
    ERROR_VARIABLE VIRTUALENV_NOT_FOUND)
if(VIRTUALENV_NOT_FOUND)
    message(FATAL_ERROR "Python virtualenv is not installed!
${VIRTUALENV_NOT_FOUND}
Please run:
${Python3_EXECUTABLE} -m pip install virtualenv")
endif()


# set up the Python environment
execute_process(COMMAND "${Python3_EXECUTABLE}" -m venv "${CMAKE_CURRENT_BINARY_DIR}/venv")

# venv trick borrowed from:
# https://discourse.cmake.org/t/possible-to-create-a-python-virtual-env-from-cmake-and-then-find-it-with-findpython3/1132
# update the environment with VIRTUAL_ENV variable(mimic the activate script)
set(ENV{VIRTUAL_ENV} "${CMAKE_CURRENT_BINARY_DIR}/venv")
# change the context of the search
set(Python3_FIND_VIRTUALENV FIRST)
# unset Python3_EXECUTABLE because it is also an input variable(see documentation, Artifacts Specification section)
unset(Python3_EXECUTABLE)
# launch a new search
find_package(Python3 3.7 COMPONENTS Interpreter Development REQUIRED)

add_custom_target(
    python_pre_reqs
    COMMAND ${Python3_EXECUTABLE} -m pip install clang==${clang_ver} ctypeslib2==${ctypeslib_ver})

# TODO: Figure out how python-clang and clang are related
#       Currently only a very specific combination works

# try to find clang of the right version
set(GOOD_CLANG_FOUND FALSE)
find_program(clang NAMES clang)
if(clang STREQUAL "clang-NOTFOUND")
    message(AUTHOR_WARNING "NO CLANG FOUND!")
else()
    # extract clang version manually because find_package(clang) doesn't work
    execute_process(COMMAND ${clang} --version OUTPUT_VARIABLE clang_full_version_string)
    string (REGEX REPLACE ".*clang version ([0-9]+\\.[0-9]+).*" "\\1" CLANG_VERSION_STRING ${clang_full_version_string})
    if(CLANG_VERSION_STRING VERSION_EQUAL clang_ver)
        message("GOOD CLANG VERSION: ${CLANG_VERSION_STRING}")
        set(GOOD_CLANG_FOUND TRUE)
    else()
        message(AUTHOR_WARNING "${clang} VERSION TOO OLD!: ${CLANG_VERSION_STRING}")
    endif()
endif()
if(NOT GOOD_CLANG_FOUND)
    # keep old wrapper because no clang found
    message(AUTHOR_WARNING "A wrapper will not be generated! Using old wrapper instead.")
    add_custom_command(
        OUTPUT amdsmi_wrapper.py
               ${PY_PACKAGE_DIR}/amdsmi_wrapper.py
        DEPENDS ${AMD_SMI}
                ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_wrapper.py
        COMMAND cp -f ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_wrapper.py ${CMAKE_CURRENT_BINARY_DIR}/
        # hacky alternative to configure_file that will run at MAKE compile instead of CMake configure
        COMMAND sed -i
                s:"@CPACK_PACKAGING_INSTALL_PREFIX@/@CMAKE_INSTALL_LIBDIR@":"${CPACK_PACKAGING_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}":g
                ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper.py
        COMMAND mkdir -p ${PY_PACKAGE_DIR}
        COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper.py ${PY_PACKAGE_DIR}/)
else()
    # generate new wrapper
    configure_file(${PROJECT_SOURCE_DIR}/tools/generator.py generator.py @ONLY COPYONLY)
    add_custom_command(
        OUTPUT amdsmi.h
               ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_wrapper.py
               amdsmi_wrapper.py
               ${PY_PACKAGE_DIR}/amdsmi_wrapper.py
        DEPENDS ${AMD_SMI}
                python_pre_reqs
                generator.py
                ${PROJECT_SOURCE_DIR}/include/amd_smi/amdsmi.h
        COMMAND cp ${PROJECT_SOURCE_DIR}/include/amd_smi/amdsmi.h ./
        COMMAND ${Python3_EXECUTABLE} generator.py -i amdsmi.h -l ${PROJECT_BINARY_DIR}/src/libamd_smi.so -o ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_wrapper.py
        COMMAND cp -f ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_wrapper.py ${CMAKE_CURRENT_BINARY_DIR}/
        # hacky alternative to configure_file that will run at MAKE compile instead of CMake configure
        COMMAND sed -i
                s:"@CPACK_PACKAGING_INSTALL_PREFIX@/@CMAKE_INSTALL_LIBDIR@":"${CPACK_PACKAGING_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}":g
                ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper.py
        COMMAND mkdir -p ${PY_PACKAGE_DIR}
        COMMAND ln -sf ${CMAKE_CURRENT_BINARY_DIR}/amdsmi_wrapper.py ${PY_PACKAGE_DIR}/)
endif()

add_custom_target(
    python_wrapper
    DEPENDS amdsmi_wrapper.py)

# symlinking instead of copying avoids unnecessarry regeneration of packaged files
add_custom_command(
    OUTPUT ${PY_BUILD_DIR}/pyproject.toml
           ${PY_PACKAGE_DIR}/__init__.py
           ${PY_PACKAGE_DIR}/amdsmi_exception.py
           ${PY_PACKAGE_DIR}/amdsmi_interface.py
           ${PY_PACKAGE_DIR}/README.md
           ${PY_PACKAGE_DIR}/LICENSE
    DEPENDS python_wrapper
    COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/pyproject.toml ${PY_BUILD_DIR}/
    COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/__init__.py ${PY_PACKAGE_DIR}/
    COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_exception.py ${PY_PACKAGE_DIR}/
    COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/amdsmi_interface.py ${PY_PACKAGE_DIR}/
    COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/README.md ${PY_PACKAGE_DIR}/
    COMMAND ln -sf ${PROJECT_SOURCE_DIR}/LICENSE ${PY_PACKAGE_DIR}/)

# NOTE: changing this does not change the generated file!
# it WILL break
set(PY_PACKAGE "${PY_BUILD_DIR}/amdsmi-0.1-py3-none-any.whl")

add_custom_command(
    OUTPUT ${PY_PACKAGE}
    DEPENDS ${PY_BUILD_DIR}/pyproject.toml
            ${PY_PACKAGE_DIR}/__init__.py
            ${PY_PACKAGE_DIR}/amdsmi_exception.py
            ${PY_PACKAGE_DIR}/amdsmi_interface.py
            ${PY_PACKAGE_DIR}/README.md
            ${PY_PACKAGE_DIR}/LICENSE
    COMMAND ${Python3_EXECUTABLE} -m pip install wheel
    COMMAND ${Python3_EXECUTABLE} -m pip wheel ./${PY_BUILD_DIR} --wheel-dir=${PY_BUILD_DIR})

add_custom_target(
    python_package ALL
    DEPENDS ${PY_PACKAGE})

install(
    PROGRAMS ${CMAKE_CURRENT_BINARY_DIR}/${PY_PACKAGE}
    DESTINATION ${SHARE_INSTALL_PREFIX})


#
# Copyright (C) 2022 Advanced Micro Devices. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import sys
import re
import os
from ctypes import *
from subprocess import call
from subprocess import check_output

sys.path.append(os.getcwd())

import ctypeslib
from ctypeslib.clang2py import main as clang2py

INTERFACE_SPECIFICATION = sys.argv[1]
OUTPUT_DIRECTORY = sys.argv[2]
LIBRARY_BINARY = sys.argv[3]
OUTPUT_FILE = "amdsmi_wrapper.py"
SMI_LIB_CTYPES = "amdsmi_lib_ctypes.py"
SMI_LIB_RET = "amdsmi_lib_ret.py"

INTERFACE_FUNCTIONS = os.path.join(OUTPUT_DIRECTORY, "amdsmi_functions.h")

API_REGEX_MATCHER = r"(\w+\s*\w*[\s\*]+)\s*(\w+)\(([^)]*)\);"
API_REGEX_TYPEDEF = r"typedef\s*(\w+)\s*(.*);"

# Pointer statuses
NO_POINTER = 0
SINGLE_POINTER = 1
DOUBLE_POINTER = 2
TRIPLE_POINTER = 3

clang_include_dir = "/usr/include/"
try:
    clang_include_dir = os.path.join(
        check_output(["clang", "-print-resource-dir"]).decode("utf-8").strip(),
        "include/",
    )
except Exception as e:
    print(
        "Clang not found on the system. The script might not work properly. {}".format(
            e
        )
    )


def ParseHeaderFile() -> bool:
    """
    This function will parse the data from the main header file, create separate
    temporary files which will then be used as arguments for clang2py(). Afterwards,
    when the generator successfully completes wrapper generation - these temporary
    files will be removed.

    `Parameters`: None.

    `Returns`:
        `bool`: True if success, False if failed.
    """

    if not os.path.exists(INTERFACE_SPECIFICATION):
        return False

    lib_types = ""
    type_read_enablers = [
        "#include <stdlib.h>",
        "typedef enum amdsmi_init_flags {",
        "typedef enum amdsmi_clk_type {",
    ]
    type_read_disablers = [
        " * @brief Initialization flags",
        "} device_type_t;",
        "} amdsmi_func_id_value_t;",
    ]
    reader_mask = False

    with open(INTERFACE_SPECIFICATION, "r") as types:
        for i, line in enumerate(types):
            if line.strip() in type_read_enablers:
                reader_mask = True
            if reader_mask:
                lib_types += line
            if line.strip() in type_read_disablers:
                reader_mask = False

    with open(os.path.join(OUTPUT_DIRECTORY, "amdsmi_lib_types.h"), "w") as file_saver:
        file_saver.write(lib_types)

    lib_ret_out = ""
    ret_reader_enablers = ["#include <stdlib.h>", "typedef enum amdsmi_status_t {"]
    ret_reader_disablers = [" * @brief Initialization flags", "} amdsmi_status_t;"]
    reader_mask = False
    with open(INTERFACE_SPECIFICATION, "r") as ret_out:
        for idx, line in enumerate(ret_out):
            if line.strip() in ret_reader_enablers:
                reader_mask = True
            if reader_mask:
                lib_ret_out += line
            if line.strip() in ret_reader_disablers:
                reader_mask = False
    with open(os.path.join(OUTPUT_DIRECTORY, "amdsmi_lib_ret.h"), "w") as file_saver:
        file_saver.write(lib_ret_out)

    functions_out = ""
    functions_reader_enablers = [
        "#include <stdlib.h>",
        "amdsmi_status_t amdsmi_init(uint64_t init_flags);",
    ]
    functions_reader_disablers = [
        "typedef enum amdsmi_init_flags {",
        "amdsmi_get_ecc_error_count(amdsmi_device_handle dev, amdsmi_error_count_t *ec);",
    ]
    reader_mask = False
    with open(INTERFACE_SPECIFICATION, "r") as ret_out:
        for idx, line in enumerate(ret_out):
            if line.strip() in functions_reader_enablers:
                reader_mask = True
            if reader_mask:
                functions_out += line
            if line.strip() in functions_reader_disablers:
                reader_mask = False
    with open(INTERFACE_FUNCTIONS, "w") as file_saver:
        file_saver.write(functions_out)

    sys.argv = [
        "generator.py",
        "--clang-args=-I" + clang_include_dir,
        os.path.join(OUTPUT_DIRECTORY, "amdsmi_lib_types.h"),
        "-o",
        os.path.join(OUTPUT_DIRECTORY, "amdsmi_lib_ctypes.py"),
    ]
    clang2py()

    sys.argv = [
        "generator.py",
        os.path.join(OUTPUT_DIRECTORY, "amdsmi_lib_ret.h"),
        "-o",
        os.path.join(OUTPUT_DIRECTORY, "amdsmi_lib_ret.py"),
    ]
    clang2py()

    return True


def DeducePointerStatus(variable: str) -> int:
    """
    Function used to deduce pointer status of a specific variable.

    `Parameters`:
        * variable (`str`): Variable string for which the pointer status
        is to be deduced.

    `Returns`:
        `int`: Degree of pointer deduced (0 for no pointer status found
        and 3 for a triple pointer).
    """
    if ("***" in variable) or ("**" in variable and "[]" in variable):
        return TRIPLE_POINTER
    elif ("**" in variable) or ("*" in variable and "[]" in variable):
        return DOUBLE_POINTER
    elif "*" in variable or "[]" in variable:
        return SINGLE_POINTER
    return NO_POINTER


def TypeCast(cxxtype: str, ptr_status=0) -> str:
    """
    Function used to type cast a cxx type to the corresponding ctypes
    type.

    `Parameters`:
        * cxxtype (`str`): String containing the cxx type.
        * ptr_status (`int`): Integer describing pointer status of the
        cxx type.

    `Returns`:
        `str`: String containing the corresponding ctypes type.
    """
    if cxxtype == "void" and ptr_status:
        return "c_void_p"
    elif cxxtype == "char" and ptr_status:
        return "c_char_p"
    elif cxxtype == "int":
        return "c_int"
    elif cxxtype == "unsigned int":
        return "c_uint"
    elif cxxtype == "unsigned":
        return "c_uint"
    elif cxxtype == "uint8_t":
        return "c_uint8"
    elif cxxtype == "uint16_t":
        return "c_uint16"
    elif cxxtype == "uint32_t":
        return "c_uint32"
    elif cxxtype == "size_t":
        return "c_uint64"
    elif cxxtype == "uint64_t":
        return "c_uint64"
    elif cxxtype == "int8_t":
        return "c_int8"
    elif cxxtype == "int16_t":
        return "c_int16"
    elif cxxtype == "int32_t":
        return "c_int32"
    elif cxxtype == "int64_t":
        return "c_int64"
    elif cxxtype == "float":
        return "c_float"
    elif cxxtype == "double":
        return "c_double"
    elif cxxtype == "char":
        return "c_char"
    elif cxxtype == "bool":
        return "c_bool"
    elif cxxtype == "void":
        return ""
    else:
        return cxxtype


def GetType(cxxtype: str, ptr_status=0) -> str:
    """
    Function used to retrieve ctypes type of a cxx type.

    `Parameters`:
        * cxxtype (`str`): String containing the cxx type.
        * ptr_status (`int`): Integer representing the pointer
        status of the cxx type.

    `Returns`:
        `str`: String of the ctypes type that was retrieved.
    """
    if cxxtype == "void" and ptr_status == 2:
        return "POINTER(" + TypeCast(cxxtype, ptr_status=1) + ")"
    elif cxxtype == "void" and ptr_status == 1:
        return TypeCast(cxxtype, ptr_status)
    elif cxxtype == "char" and ptr_status == 2:
        return "POINTER(" + TypeCast(cxxtype, ptr_status=1) + ")"
    elif cxxtype == "char" and ptr_status == 1:
        return TypeCast(cxxtype, ptr_status)
    elif ptr_status == 2:
        return "POINTER(POINTER(" + TypeCast(cxxtype) + "))"
    elif ptr_status == 1:
        return "POINTER(" + TypeCast(cxxtype) + ")"
    else:
        return TypeCast(cxxtype)


def DetectOpaquePointer(variable_type: str, variable: str, ptr_status=0) -> bool:
    """
    Function used to check whether a variable is an opaque pointer.

    `Parameters`:
        * variable_type (`str`): String containing the variable type.
        * variable (`str`): String containing the variable name.
        * ptr_status (`int`): Integer representing the pointer status found.

    `Returns`:
        `bool`: Bool representing whether an opaque pointer was deduced or not.
    """
    if variable_type == "struct" and len(variable.split(" ")) > 1 and ptr_status == 1:
        return True
    return False


def TypeDefConvert(variable_type: str, variable: str) -> str:
    """
    Function used to break down a typedef down and extract the cxx type.
    This type will then further be converted to a ctypes type.

    `Parameters`:
        * variable_type (`str`): String containing the variable type.
        * variable (`str`): String containing the variable name.

    `Returns`:
        `str`: Finalized string containing the proper definition with ctypes
        type.
    """
    ptr_status = DeducePointerStatus(variable)
    variable = variable.replace("*", " ").strip()
    cxxtypedef = str()
    if DetectOpaquePointer(variable_type, variable, ptr_status):
        variables = variable.split(" ")
        cxxtypedef = variables[2] + " = ctypes." + GetType(variables[0], ptr_status)
    else:
        cxxtypedef = variable + " = ctypes." + GetType(variable_type, ptr_status)

    return cxxtypedef


def ParseParameters(parameters: str) -> list:
    """
    Function that parses function parameters and returns a list containing
    ctypes types for the given parameters.

    An example return value:
    [smi_device_handle, POINTER(smi_device_handle), POINTER(smi_vf_config)]

    `Parameters`:
        * parameters (`str`): String containing the parameters for parsing.

    `Returns`:
        `list`: List containing ctypes types for the given parameters.
    """
    if parameters == "":
        return []

    parameter_array = parameters.split(",")

    result = []
    for param in parameter_array:
        ptr_status = DeducePointerStatus(param)
        param = param.strip().split(" ")

        while "const" in param:
            param.remove("const")

        if param[0] == "unsigned" and len(param) == 3:
            input = param[0] + " " + param[1]
            result.append(GetType(input, ptr_status))
        elif param[0] == "struct" or param[0] == "union" or param[0] == "enum":
            result.append(GetType(param[1], ptr_status))
        else:
            result.append(GetType(param[0], ptr_status))

    return "[{}]".format(",".join(result))


def CleanTempFiles() -> None:
    """
    This function cleans up the temporary files created by the generator.

    `Parameters`: None.

    `Returns`: None.
    """
    os.remove(INTERFACE_FUNCTIONS)
    os.remove(os.path.join(OUTPUT_DIRECTORY, "amdsmi_lib_ret.h"))
    os.remove(os.path.join(OUTPUT_DIRECTORY, "amdsmi_lib_types.h"))


def main() -> str:
    """
    Py wrapper generator.

    `Parameters`: None.

    `Returns`:
        `str`: String containing status message.
    """
    api = []
    api_expose = []
    typedef_list = []
    typedef_expose = []

    if not ParseHeaderFile():
        return "Error - header file missing."

    format_code = ["clang-format", "-i", INTERFACE_FUNCTIONS]
    try:
        ret = call(format_code)
        if ret < 0:
            print("Clang-format failed to run")
    except Exception as e:
        print(
            "Clang-format not found on the system. The script might not work properly. {}".format(
                e
            )
        )

    with open(INTERFACE_FUNCTIONS) as specification:
        file_specification = specification.read()
        # find all typedefs and construct typedef_list in format [{typedef_name} = {ctypes_type}]
        # typedef_expose is the list containing only the names of typedefs [{typedef_name}]
        for variable_type, variable in re.findall(
            API_REGEX_TYPEDEF, file_specification
        ):
            typedef_list.append(TypeDefConvert(variable_type, variable))
            typedef_expose.append(variable.replace("*", ""))

        # Get all components from function declaration(return type, function name, parameters) and
        # append to api list
        # api = [{return_type} = {ctypes_type}, {function_name} = {name}, {args} = [{ctypes_type}]]
        for returnType, functionName, parameters in re.findall(
            API_REGEX_MATCHER, file_specification
        ):
            ptr_status = DeducePointerStatus(returnType)

            returnType = returnType.replace("*", " ").strip()
            returnedType = GetType(returnType, ptr_status)

            api.append(
                {
                    "return_type": returnedType,
                    "function_name": functionName,
                    "args": ParseParameters(parameters),
                }
            )
            # api_expose is the list of all functions(function names) in the interface
            api_expose.append(functionName)

    api_string = ""
    for method in api:
        api_string += """
_lib.{function_name}.argtypes = {argument_array}
_lib.{function_name}.restype = {return_type}
{function_name} = _lib.{function_name}
""".format(
            function_name=method["function_name"],
            argument_array=method["args"],
            return_type=method["return_type"],
        )

    typedef_list_out = ""
    for typedef_item in typedef_list:
        typedef_list_out += typedef_item + "\n"

    smi_lib_ctypes_out = ""
    with open(os.path.join(OUTPUT_DIRECTORY, SMI_LIB_CTYPES), "r") as smi_lib_ctypes:
        smi_lib_ctypes_out = smi_lib_ctypes.read()
        smi_lib_ctypes_out = smi_lib_ctypes_out.replace("struct_", "")
        smi_lib_ctypes_out = smi_lib_ctypes_out.replace("union_", "")
        smi_lib_ctypes_out = smi_lib_ctypes_out.replace("POINTER(None)", "c_void_p")

    smi_lib_ret_out = ""
    with open(os.path.join(OUTPUT_DIRECTORY, SMI_LIB_RET), "r") as smi_lib_ret:
        smi_lib_ret_out = smi_lib_ret.read()
    smi_lib_ret_out = smi_lib_ret_out.replace("__all__ =", "__all__ +=")

    with open(os.path.join(OUTPUT_DIRECTORY, OUTPUT_FILE), "w") as out:
        out.write(
            """
#
# Copyright (C) 2022 Advanced Micro Devices. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from ctypes import *
from ctypes import POINTER
from subprocess import run
from subprocess import PIPE
import os

{SMI_LIB_TYPES}
{SMI_LIB_RET}
{TYPEDEF_LIST}

__all__ += {API_EXPOSE}
__all__ += {TYPEDEF_EXPOSE}

_lib = CDLL(os.path.join(os.path.dirname(__file__), "libamd_smi64.so"))

{API}
""".format(
                SMI_LIB_TYPES=smi_lib_ctypes_out,
                SMI_LIB_RET=smi_lib_ret_out,
                TYPEDEF_LIST=typedef_list_out,
                API_EXPOSE=api_expose,
                TYPEDEF_EXPOSE=typedef_expose,
                BINARY=LIBRARY_BINARY,
                API=api_string,
            )
        )
    CleanTempFiles()
    return "Success - wrapper generated."


if __name__ == "__main__":
    status = main()
    print(status)

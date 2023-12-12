import os
import ctypes
from pathlib import Path

# Get the ROCm version for rocm-core library
def get_rocm_version():
    try:
        librocm_core_file =  Path(__file__).resolve().parent.parent.parent / "lib" / "librocm-core.so"
        if not librocm_core_file.is_file():
            return "N/A"

        # python binding
        librocm_core = ctypes.CDLL(librocm_core_file)
        VerErrors = ctypes.c_uint32
        get_rocm_core_version = librocm_core.getROCmVersion
        get_rocm_core_version.restype = VerErrors
        get_rocm_core_version.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint32)]

        # call the function
        major =  ctypes.c_uint32()
        minor =  ctypes.c_uint32()
        patch =  ctypes.c_uint32()

        if get_rocm_core_version(ctypes.byref(major), ctypes.byref(minor),ctypes.byref(patch)) == 0:
           return "%d.%d.%d" % (major.value, minor.value, patch.value)
        return "N/A"
    except:
        return "N/A"


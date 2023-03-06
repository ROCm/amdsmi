#
# Copyright (C) 2023 Advanced Micro Devices. All rights reserved.
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

from enum import IntEnum
from . import amdsmi_wrapper

class AmdSmiRetCode(IntEnum):
    SUCCESS = amdsmi_wrapper.AMDSMI_STATUS_SUCCESS
    ERR_INVAL = amdsmi_wrapper.AMDSMI_STATUS_INVAL
    ERR_NOT_SUPPORTED = amdsmi_wrapper.AMDSMI_STATUS_NOT_SUPPORTED
    FILE_ERROR = amdsmi_wrapper.AMDSMI_STATUS_FILE_ERROR
    ERR_NO_PERM = amdsmi_wrapper.AMDSMI_STATUS_NO_PERM
    ERR_OUT_OF_RESOURCES = amdsmi_wrapper.AMDSMI_STATUS_OUT_OF_RESOURCES
    INTERNAL_EXCEPTION = amdsmi_wrapper.AMDSMI_STATUS_INTERNAL_EXCEPTION
    INPUT_OUT_OF_BOUNDS = amdsmi_wrapper.AMDSMI_STATUS_INPUT_OUT_OF_BOUNDS
    INIT_ERROR = amdsmi_wrapper.AMDSMI_STATUS_INIT_ERROR
    NOT_IMPLEMENTED = amdsmi_wrapper.AMDSMI_STATUS_NOT_YET_IMPLEMENTED
    ERR_NOT_FOUND = amdsmi_wrapper.AMDSMI_STATUS_NOT_FOUND
    INSUFFICIENT_SIZE = amdsmi_wrapper.AMDSMI_STATUS_INSUFFICIENT_SIZE
    INTERRUPT = amdsmi_wrapper.AMDSMI_STATUS_INTERRUPT
    UNEXPECTED_SIZE = amdsmi_wrapper.AMDSMI_STATUS_UNEXPECTED_SIZE
    NO_DATA = amdsmi_wrapper.AMDSMI_STATUS_NO_DATA
    UNEXPECTED_DATA = amdsmi_wrapper.AMDSMI_STATUS_UNEXPECTED_DATA
    ERR_BUSY = amdsmi_wrapper.AMDSMI_STATUS_BUSY
    REFCOUNT_OVERFLOW = amdsmi_wrapper.AMDSMI_STATUS_REFCOUNT_OVERFLOW
    FAIL_LOAD_MODULE = amdsmi_wrapper.AMDSMI_STATUS_FAIL_LOAD_MODULE
    FAIL_LOAD_SYMBOL = amdsmi_wrapper.AMDSMI_STATUS_FAIL_LOAD_SYMBOL
    DRM_ERROR = amdsmi_wrapper.AMDSMI_STATUS_DRM_ERROR
    ERR_IO = amdsmi_wrapper.AMDSMI_STATUS_IO
    API_FAILED = amdsmi_wrapper.AMDSMI_STATUS_API_FAILED
    TIMEOUT = amdsmi_wrapper.AMDSMI_STATUS_TIMEOUT
    NO_SLOT = amdsmi_wrapper.AMDSMI_STATUS_NO_SLOT
    RETRY = amdsmi_wrapper.AMDSMI_STATUS_RETRY
    NOT_INIT = amdsmi_wrapper.AMDSMI_STATUS_NOT_INIT
    UNKNOWN_ERROR = amdsmi_wrapper.AMDSMI_STATUS_UNKNOWN_ERROR


class AmdSmiException(Exception):
    """Base smi exception class"""

    pass


class AmdSmiLibraryException(AmdSmiException):
    def __init__(self, err_code):
        err_code = abs(err_code)
        super().__init__(err_code)
        self.err_code = err_code
        self.set_err_info()

    def __str__(self):
        return "An error occured with code: {err_code}({err_info})".format(
            err_code=self.err_code, err_info=self.err_info
        )

    def get_error_info(self):
        return self.err_info

    def get_error_code(self):
        return self.err_code

    def set_err_info(self):
        switch = {
            AmdSmiRetCode.ERR_INVAL: "AMDSMI_STATUS_INVAL - Invalid parameters",
            AmdSmiRetCode.ERR_NOT_SUPPORTED: "AMDSMI_STATUS_NOT_SUPPORTED - Feature not supported",
            AmdSmiRetCode.FILE_ERROR: "AMDSMI_STATUS_FILE_ERROR - Error opening file",
            AmdSmiRetCode.ERR_OUT_OF_RESOURCES: "AMDSMI_STATUS_OUT_OF_RESOURCES - Not enough memory",
            AmdSmiRetCode.INTERNAL_EXCEPTION: "AMDSMI_STATUS_INTERNAL_EXCEPTION -  Internal error",
            AmdSmiRetCode.ERR_NO_PERM: "AMDSMI_STATUS_NO_PERM - Permission Denied",
            AmdSmiRetCode.INPUT_OUT_OF_BOUNDS: "AMDSMI_STATUS_INPUT_OUT_OF_BOUNDS - Out of bounds",
            AmdSmiRetCode.INIT_ERROR: "AMDSMI_STATUS_INIT_ERROR - Initialization error",
            AmdSmiRetCode.ERR_BUSY: "AMDSMI_STATUS_BUSY - Device busy",
            AmdSmiRetCode.ERR_NOT_FOUND: "AMDSMI_STATUS_NOT_FOUND - Device Not found",
            AmdSmiRetCode.ERR_IO: "AMDSMI_STATUS_IO - I/O Error",
            AmdSmiRetCode.NOT_IMPLEMENTED: "AMDSMI_STATUS_NOT_YET_IMPLEMENTED - Feature not yet implemented",
            AmdSmiRetCode.INSUFFICIENT_SIZE: "AMDSMI_STATUS_INSUFFICIENT_SIZE - Insufficient size for operation",
            AmdSmiRetCode.INTERRUPT: "AMDSMI_STATUS_INTERRUPT - Interrupt ocurred during execution",
            AmdSmiRetCode.UNEXPECTED_SIZE: "AMDSMI_STATUS_UNEXPECTED_SIZE - unexpected size of data was read",
            AmdSmiRetCode.NO_DATA: "AMDSMI_STATUS_NO_DATA - No data was found for given input",
            AmdSmiRetCode.UNEXPECTED_DATA: "AMDSMI_STATUS_UNEXPECTED_DATA - The data read or provided was unexpected",
            AmdSmiRetCode.REFCOUNT_OVERFLOW: "AMDSMI_STATUS_REFCOUNT_OVERFLOW - Internal reference counter exceeded INT32_MAX",
            AmdSmiRetCode.FAIL_LOAD_MODULE: "AMDSMI_STATUS_FAIL_LOAD_MODULE - Fail to load lib",
            AmdSmiRetCode.FAIL_LOAD_SYMBOL: "AMDSMI_STATUS_FAIL_LOAD_SYMBOL - Fail to load symbol",
            AmdSmiRetCode.DRM_ERROR: "AMDSMI_STATUS_DRM_ERROR - Error when called libdrm",
            AmdSmiRetCode.API_FAILED: "AMDSMI_STATUS_API_FAILED - API call failed",
            AmdSmiRetCode.TIMEOUT: "AMDSMI_STATUS_TIMEOUT - Timeout in API call",
            AmdSmiRetCode.NO_SLOT: "AMDSMI_STATUS_NO_SLOT - No more free slot",
            AmdSmiRetCode.RETRY: "AMDSMI_STATUS_RETRY - Retry operation",
            AmdSmiRetCode.NOT_INIT: "AMDSMI_STATUS_NOT_INIT - Device not initialized",
        }

        self.err_info = switch.get(self.err_code, "AMDSMI_STATUS_UNKNOWN_ERROR - An unknown error occurred")


class AmdSmiRetryException(AmdSmiLibraryException):
    def __init__(self):
        super().__init__(AmdSmiRetCode.RETRY)


class AmdSmiTimeoutException(AmdSmiLibraryException):
    def __init__(self):
        super().__init__(AmdSmiRetCode.TIMEOUT)


class AmdSmiParameterException(AmdSmiException):
    def __init__(self, receivedValue, expectedType, msg=None):
        super().__init__(msg)
        self.actualType = type(receivedValue)
        self.expectedType = expectedType
        self.set_err_msg()
        if msg is not None:
            self.err_msg = msg

    def set_err_msg(self):
        self.err_msg = (
            "Invalid parameter:\n"
            + "Actual type: {actualType}\n".format(actualType=self.actualType)
            + "Expected type: {expectedType}".format(expectedType=self.expectedType)
        )

    def __str__(self):
        return self.err_msg


class AmdSmiKeyException(AmdSmiException):
    def __init__(self, key):
        super().__init__()
        self.key = key
        self.set_err_msg()

    def set_err_msg(self):
        self.err_msg = "Key " + self.key + " is missing from dictionary"

    def __str__(self):
        return self.err_msg


class AmdSmiBdfFormatException(AmdSmiException):
    def __init__(self, bdf):
        super().__init__()
        self.bdf = bdf

    def __str__(self):
        return (
            "Wrong BDF format: {}. \n"
            + "BDF string should be: <domain>:<bus>:<device>.<function>\n"
            + " or <bus>:<device>.<function> in hexcode format.\n"
            + "Where:\n\t<domain> is 4 hex digits long from 0000-FFFF interval\n"
            + "\t<bus> is 2 hex digits long from 00-FF interval\n"
            + "\t<device> is 2 hex digits long from 00-1F interval\n"
            + "\t<function> is 1 hex digit long from 0-7 interval"
        ).format(self.bdf)

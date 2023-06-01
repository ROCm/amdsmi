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
    STATUS_INVAL = amdsmi_wrapper.AMDSMI_STATUS_INVAL
    STATUS_NOT_SUPPORTED = amdsmi_wrapper.AMDSMI_STATUS_NOT_SUPPORTED
    STATUS_FILE_ERROR = amdsmi_wrapper.AMDSMI_STATUS_FILE_ERROR
    STATUS_NO_PERM = amdsmi_wrapper.AMDSMI_STATUS_NO_PERM
    STATUS_OUT_OF_RESOURCES = amdsmi_wrapper.AMDSMI_STATUS_OUT_OF_RESOURCES
    STATUS_INTERNAL_EXCEPTION = amdsmi_wrapper.AMDSMI_STATUS_INTERNAL_EXCEPTION
    STATUS_INPUT_OUT_OF_BOUNDS = amdsmi_wrapper.AMDSMI_STATUS_INPUT_OUT_OF_BOUNDS
    STATUS_INIT_ERROR = amdsmi_wrapper.AMDSMI_STATUS_INIT_ERROR
    STATUS_NOT_YET_IMPLEMENTED = amdsmi_wrapper.AMDSMI_STATUS_NOT_YET_IMPLEMENTED
    STATUS_NOT_FOUND = amdsmi_wrapper.AMDSMI_STATUS_NOT_FOUND
    STATUS_INSUFFICIENT_SIZE = amdsmi_wrapper.AMDSMI_STATUS_INSUFFICIENT_SIZE
    STATUS_INTERRUPT = amdsmi_wrapper.AMDSMI_STATUS_INTERRUPT
    STATUS_UNEXPECTED_SIZE = amdsmi_wrapper.AMDSMI_STATUS_UNEXPECTED_SIZE
    STATUS_NO_DATA = amdsmi_wrapper.AMDSMI_STATUS_NO_DATA
    STATUS_UNEXPECTED_DATA = amdsmi_wrapper.AMDSMI_STATUS_UNEXPECTED_DATA
    STATUS_BUSY = amdsmi_wrapper.AMDSMI_STATUS_BUSY
    STATUS_REFCOUNT_OVERFLOW = amdsmi_wrapper.AMDSMI_STATUS_REFCOUNT_OVERFLOW
    STATUS_FAIL_LOAD_MODULE = amdsmi_wrapper.AMDSMI_STATUS_FAIL_LOAD_MODULE
    STATUS_FAIL_LOAD_SYMBOL = amdsmi_wrapper.AMDSMI_STATUS_FAIL_LOAD_SYMBOL
    STATUS_DRM_ERROR = amdsmi_wrapper.AMDSMI_STATUS_DRM_ERROR
    STATUS_IO = amdsmi_wrapper.AMDSMI_STATUS_IO
    STATUS_API_FAILED = amdsmi_wrapper.AMDSMI_STATUS_API_FAILED
    STATUS_TIMEOUT = amdsmi_wrapper.AMDSMI_STATUS_TIMEOUT
    STATUS_NO_SLOT = amdsmi_wrapper.AMDSMI_STATUS_NO_SLOT
    STATUS_RETRY = amdsmi_wrapper.AMDSMI_STATUS_RETRY
    STATUS_NOT_INIT = amdsmi_wrapper.AMDSMI_STATUS_NOT_INIT
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
            AmdSmiRetCode.STATUS_INVAL: "AMDSMI_STATUS_INVAL - Invalid parameters",
            AmdSmiRetCode.STATUS_NOT_SUPPORTED: "AMDSMI_STATUS_NOT_SUPPORTED - Feature not supported",
            AmdSmiRetCode.STATUS_FILE_ERROR: "AMDSMI_STATUS_FILE_ERROR - Error opening file",
            AmdSmiRetCode.STATUS_OUT_OF_RESOURCES: "AMDSMI_STATUS_OUT_OF_RESOURCES - Not enough memory",
            AmdSmiRetCode.STATUS_INTERNAL_EXCEPTION: "AMDSMI_STATUS_INTERNAL_EXCEPTION -  Internal error",
            AmdSmiRetCode.STATUS_NO_PERM: "AMDSMI_STATUS_NO_PERM - Permission Denied",
            AmdSmiRetCode.STATUS_INPUT_OUT_OF_BOUNDS: "AMDSMI_STATUS_INPUT_OUT_OF_BOUNDS - Out of bounds",
            AmdSmiRetCode.STATUS_INIT_ERROR: "AMDSMI_STATUS_INIT_ERROR - Initialization error",
            AmdSmiRetCode.STATUS_BUSY: "AMDSMI_STATUS_BUSY - Device busy",
            AmdSmiRetCode.STATUS_NOT_FOUND: "AMDSMI_STATUS_NOT_FOUND - Device Not found",
            AmdSmiRetCode.STATUS_IO: "AMDSMI_STATUS_IO - I/O Error",
            AmdSmiRetCode.STATUS_NOT_YET_IMPLEMENTED: "AMDSMI_STATUS_NOT_YET_IMPLEMENTED - Feature not yet implemented",
            AmdSmiRetCode.STATUS_INSUFFICIENT_SIZE: "AMDSMI_STATUS_INSUFFICIENT_SIZE - Insufficient size for operation",
            AmdSmiRetCode.STATUS_INTERRUPT: "AMDSMI_STATUS_INTERRUPT - Interrupt ocurred during execution",
            AmdSmiRetCode.STATUS_UNEXPECTED_SIZE: "AMDSMI_STATUS_UNEXPECTED_SIZE - unexpected size of data was read",
            AmdSmiRetCode.STATUS_NO_DATA: "AMDSMI_STATUS_NO_DATA - No data was found for given input",
            AmdSmiRetCode.STATUS_UNEXPECTED_DATA: "AMDSMI_STATUS_UNEXPECTED_DATA - The data read or provided was unexpected",
            AmdSmiRetCode.STATUS_REFCOUNT_OVERFLOW: "AMDSMI_STATUS_REFCOUNT_OVERFLOW - Internal reference counter exceeded INT32_MAX",
            AmdSmiRetCode.STATUS_FAIL_LOAD_MODULE: "AMDSMI_STATUS_FAIL_LOAD_MODULE - Fail to load lib",
            AmdSmiRetCode.STATUS_FAIL_LOAD_SYMBOL: "AMDSMI_STATUS_FAIL_LOAD_SYMBOL - Fail to load symbol",
            AmdSmiRetCode.STATUS_DRM_ERROR: "AMDSMI_STATUS_DRM_ERROR - Error when called libdrm",
            AmdSmiRetCode.STATUS_API_FAILED: "AMDSMI_STATUS_API_FAILED - API call failed",
            AmdSmiRetCode.STATUS_TIMEOUT: "AMDSMI_STATUS_TIMEOUT - Timeout in API call",
            AmdSmiRetCode.STATUS_NO_SLOT: "AMDSMI_STATUS_NO_SLOT - No more free slot",
            AmdSmiRetCode.STATUS_RETRY: "AMDSMI_STATUS_RETRY - Retry operation",
            AmdSmiRetCode.STATUS_NOT_INIT: "AMDSMI_STATUS_NOT_INIT - Device not initialized",
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

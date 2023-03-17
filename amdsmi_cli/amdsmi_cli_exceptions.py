
import json
import sys

AMDSMI_ERROR_MESSAGES = {
    0: "Sucess",
    1: "Invalid parameters",
    2: "Command not supported",
    3: "Command not yet implemented",
    4: "Failed load module",
    5: "Failed load symbole",
    6: "Drm error",
    7: "API call failed",
    8: "Timeout in API call",
    9: "Retry operation",
    10: "Permission Denied",
    11: "Interrupt ocurred during execution",
    12: "I/O Error",
    13: "Address fault",
    14: "Error opening file",
    15: "Not enough memory",
    16: "Internal error",
    17: "Out of bounds",
    18: "Initialization error",
    19: "Internal reference counter exceeded",

    30: "Device busy",
    31: "Device Not found",
    32: "Device not initialized",
    33: "No more free slot",

    40: "No data was found for given input",
    41: "Insufficient size for operation",
    42: "Unexpected size of data was read",
    43: "The data read or provided was unexpected",
}

def _get_error_message(error_code):
    if abs(error_code) in AMDSMI_ERROR_MESSAGES:
        return AMDSMI_ERROR_MESSAGES[abs(error_code)]
    return "Generic error"

class AmdSmiException(Exception):
    def __str__(self):
        return self.message


class AmdSmiInvalidCommandException(AmdSmiException):
    def __init__(self, command, outputformat):
        self.value = -1
        self.command = command
        if outputformat == "json":
            values = {}
            values["error"] = "Command '{}' is invalid. Run '--help' for more info.".format(self.command)
            values["code"] = self.value
            self.message = json.dumps(values)
        elif outputformat == "csv":
            self.message = "error,code\n" + "Command '{}' is invalid. Run '--help' for more info.,".format(self.command) + str(self.value)
        else:
            self.message = "Command '{}' is invalid. Run '--help' for more info. Error code: {}".format(self.command, self.value)



class AmdSmiInvalidParameterException(AmdSmiException):
    def __init__(self, command, outputformat):
        self.value = -2
        self.command = command
        if outputformat == "json":
            values = {}
            values["error"] = "Parameter '{}' is invalid. Run '--help' for more info.".format(self.command)
            values["code"] = self.value
            self.message = json.dumps(values)
        elif outputformat == "csv":
            self.message = "error,code\n" + "Parameter '{}' is invalid. Run '--help' for more info.,".format(self.command) + str(self.value)
        else:
            self.message = "Parameter '{}' is invalid. Run '--help' for more info. Error code: {}".format(self.command, self.value)


class AmdSmiDeviceNotFoundException(AmdSmiException):
    def __init__(self, command, outputformat):
        self.value = -3
        self.command = command
        if outputformat == "json":
            values = {}
            values["error"] = "GPU Device with GPU_INDEX '{}' cannot be found on the system.".format(self.command)
            values["code"] = self.value
            self.message = json.dumps(values)
        elif outputformat == "csv":
            self.message = "error,code\n" + "GPU Device with GPU_INDEX '{}' cannot be found on the system.,".format(self.command) + str(self.value)
        else:
            self.message = "GPU Device with GPU_INDEX '{}' cannot be found on the system. Error code: {}".format(self.command, self.value)


class AmdSmiInvalidFilePathException(AmdSmiException):
    def __init__(self, command, outputformat):
        self.value = -4
        self.command = command
        if outputformat == "json":
            values = {}
            values["error"] = "Path '{}' cannot be found.".format(self.command)
            values["code"] = self.value
            self.message = json.dumps(values)
        elif outputformat == "csv":
            self.message = "error,code\n" + "Path '{}' cannot be found.,".format(self.command) + str(self.value)
        else:
            self.message = "Path '{}' cannot be found. Error code: {}".format(self.command, self.value)


class AmdSmiInvalidParameterValueException(AmdSmiException):
    def __init__(self, command, outputformat):
        self.value = -5
        self.command = command
        if outputformat == "json":
            values = {}
            values["error"] = "Value '{}' is not of valid type or format. Run '--help' for more info.".format(self.command)
            values["code"] = self.value
            self.message = json.dumps(values)
        elif outputformat == "csv":
            self.message = "error,code\n" + "Value '{}' is not of valid type or format. Run '--help' for more info.,".format(self.command) + str(self.value)
        else:
            self.message = "Value '{}' is not of valid type or format. Run '--help' for more info. Error code: {}".format(self.command, self.value)


class AmdSmiMissingParameterValueException(AmdSmiException):
    def __init__(self, command, outputformat):
        self.value = -6
        self.command = command
        if outputformat == "json":
            values = {}
            values["error"] = "Parameter '{}' requires a value. Run '--help' for more info.".format(self.command)
            values["code"] = self.value
            self.message = json.dumps(values)
        elif outputformat == "csv":
            self.message = "error,code\n" + "Parameter '{}' requires a value. Run '--help' for more info.,".format(self.command) + str(self.value)
        else:
            self.message = "Parameter '{}' requires a value. Run '--help' for more info. Error code: {}".format(self.command, self.value)

class AmdSmiParameterNotSupportedException(AmdSmiException):
    def __init__(self, command, outputformat):
        self.value = -8
        self.command = command
        if outputformat == "json":
            values = {}
            values["error"] = "Parameter '{}' is not supported on the system. Run '--help' for more info.".format(self.command)
            values["code"] = self.value
            self.message = json.dumps(values)
        elif outputformat == "csv":
            self.message = "error,code\n" + "Parameter '{}' is not supported on the system. Run '--help' for more info.,".format(self.command) + str(self.value)
        else:
            self.message = "Parameter '{}' is not supported on the system. Run '--help' for more info. Error code: {}".format(self.command, self.value)


class AmdSmiUnknownErrorException(AmdSmiException):
    def __init__(self, command, outputformat):
        self.value = -100
        self.command = command
        if outputformat == "json":
            values = {}
            values["error"] = "An unknown error has occurred. Run 'help' for more info."
            values["code"] = self.value
            self.message = json.dumps(values)
        elif outputformat == "csv":
            self.message = "error,code\n" + "An unknown error has occurred. Run 'help' for more info.," + str(self.value)
        else:
            self.message = "An unknown error has occurred. Run 'help' for more info. Error code: {}".format(self.value)


class AmdSmiAMDSMIErrorException(AmdSmiException):
    def __init__(self, outputformat, error_code):
        self.value = -1000 - abs(error_code)
        self.smilibcode = error_code

        if outputformat == "json":
            values = {}
            values["error"] = "AMDSMI has returned error '{}' - '{}'".format(self.value, 
                                AMDSMI_ERROR_MESSAGES[abs(self.smilibcode)])
            values["code"] = self.value
            self.message = json.dumps(values)
        elif outputformat == "csv":
            self.message = "error,code\n" + "AMDSMI has returned error '{}' - '{}',".format(self.value, _get_error_message(self.smilibcode)) + str(self.value)
        else:
            self.message = "AMDSMI has returned error '{}' - '{}' Error code: {}".format(self.value, _get_error_message(self.smilibcode), self.value)

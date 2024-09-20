#!/usr/bin/env python3
#
# Copyright (C) 2024 Advanced Micro Devices. All rights reserved.
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

### Handle safe initialization for amdsmi

import atexit
import logging
import signal
import sys

from pathlib import Path

sys.path.append(f"{Path(__file__).resolve().parent}/../../share/amd_smi")

# If the python library is installed, it will overwrite the path above
from amdsmi import amdsmi_interface
from amdsmi import amdsmi_exception

# Using basic python logging for user errors and development
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.ERROR) # User level logging
# This traceback limit only affects this file, once the code hit's the cli portion it get's reset to the user's preference
sys.tracebacklimit = -1 # Disable traceback when raising errors

# On initial import set initialized variable
AMDSMI_INITIALIZED = False
AMDSMI_INIT_FLAG = amdsmi_interface.AmdSmiInitFlags.INIT_ALL_PROCESSORS
AMD_VENDOR_ID = 4098

def check_amdgpu_driver():
    """ Returns true if amdgpu is found in the list of initialized modules """
    amd_gpu_status_file = Path("/sys/module/amdgpu/initstate")
    if amd_gpu_status_file.exists():
        if amd_gpu_status_file.read_text(encoding="ascii").strip() == "live":
            return True
    return False


def check_amd_hsmp_driver():
    """ Returns true if amd_hsmp is found in the list of initialized modules """
    amd_cpu_status_file = Path("/sys/module/amd_hsmp/initstate")
    if amd_cpu_status_file.exists():
        if amd_cpu_status_file.read_text(encoding="ascii").strip() == "live":
            return True
    return False


def amdsmi_cli_init():
    """ Initializes AMDSMI Library for the CLI

    Checks for the presence of the amdgpu and amd_hsmp drivers and initializes the
    AMD SMI library based on the live drivers found.

    Return:
        init_flag: the flag used to initialize the AMD SMI library without error

    Raises:
        err: AmdSmiLibraryException if not successful in initializing any drivers
    """
    init_flag = amdsmi_interface.AmdSmiInitFlags.INIT_ALL_PROCESSORS
    if check_amdgpu_driver() and check_amd_hsmp_driver():
        init_flag = amdsmi_interface.AmdSmiInitFlags.INIT_AMD_APUS
        logging.debug("Both amdgpu and amd_hsmp driver's initstate is live")
        try:
            amdsmi_interface.amdsmi_init(init_flag)
        except (amdsmi_interface.AmdSmiLibraryException, amdsmi_interface.AmdSmiParameterException) as e:
            if e.err_code in (amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NOT_INIT,
                              amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_DRIVER_NOT_LOADED):
                logging.error("Drivers not loaded (amdgpu and amd_hsmp drivers not found in modules)")
                sys.exit(-1)
            else:
                raise e
    elif check_amdgpu_driver():
        init_flag = amdsmi_interface.AmdSmiInitFlags.INIT_AMD_GPUS
        logging.debug("amdgpu driver initstate is live")
        try:
            amdsmi_interface.amdsmi_init(init_flag)
        except (amdsmi_interface.AmdSmiLibraryException, amdsmi_interface.AmdSmiParameterException) as e:
            if e.err_code in (amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NOT_INIT,
                                amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_DRIVER_NOT_LOADED):
                logging.error("Driver not loaded (amdgpu not found in modules)")
                sys.exit(-1)
            else:
                raise e
        logging.debug("amdgpu driver initialized successfully, but amd_hsmp initstate was not live")
    elif check_amd_hsmp_driver():
        init_flag = amdsmi_interface.AmdSmiInitFlags.INIT_AMD_CPUS
        logging.debug("amd_hsmp driver initstate is live")
        try:
            amdsmi_interface.amdsmi_init(init_flag)
        except (amdsmi_interface.AmdSmiLibraryException, amdsmi_interface.AmdSmiParameterException) as e:
            if e.err_code in (amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NOT_INIT,
                              amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_DRIVER_NOT_LOADED):
                logging.error("Driver not loaded (amd_hsmp not found in modules)")
                sys.exit(-1)
            else:
                raise e
        logging.debug("amd_hsmp driver initialized successfully, but amdgpu initstate was not live")

    logging.debug(f"AMDSMI initialized with atleast one driver successfully | init flag: {init_flag}")

    return init_flag

def amdsmi_cli_shutdown():
    """Shutdown AMDSMI instance

    Raises:
        err: AmdSmiLibraryException if not successful
    """
    try:
        amdsmi_interface.amdsmi_shut_down()
    except amdsmi_exception.AmdSmiLibraryException as e:
        logging.error("Unable to cleanly shut down amd-smi-lib")
        raise e


def signal_handler(sig, frame):
    logging.debug(f"Handling signal: {sig}")
    sys.exit(0)


if not AMDSMI_INITIALIZED:
    AMDSMI_INIT_FLAG = amdsmi_cli_init()
    AMDSMI_INITIALIZED = True
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(amdsmi_cli_shutdown)

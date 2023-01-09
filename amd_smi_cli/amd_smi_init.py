#!/usr/bin/python3

### Handle init singularly
# Python imports module does not re-execute code on import

import atexit
import logging
import signal
import sys

from pathlib import Path

# Handle bindings for windows, Hyper-v and KVM seperately
from amdsmiBindings import *

# Using basic python logging for user errors and development
# logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG) # Logging for Development
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR) # User level logging

# On initial import set initialized variable
amd_smi_initialized = False

def check_return(return_code, error_statment): #@TODO would raising an exception be better?
    if return_code != amdsmi_status.AMDSMI_STATUS_SUCCESS:
        logging.error(error_statment)
        sys.exit(return_code)


def check_amdgpu_driver(): #@TODO Handle KVM logic
    """ Returns true if amdgpu is found in the list of initialized modules """
    amd_gpu_status_file = Path("/sys/module/amdgpu/initstate")

    if amd_gpu_status_file.exists():
        if amd_gpu_status_file.read_text().strip() == 'live':
            return True

    return False


def init_amd_smi(flag=amdsmi_init_flags.AMD_SMI_INIT_AMD_GPUS):
    """ Initializes AMD-SMI """
    # Check if amdgpu driver is up
    if check_amdgpu_driver():
        # Only init AMD GPUs for now, waiting for future support for AMD CPUs 
        init_status = amdsmi.amdsmi_init(flag)
        check_return(return_code=init_status, error_statment=f'AMD SMI initialization returned {init_status} (the expected value is {amdsmi_status_t.AMDSMI_STATUS_SUCCESS})')
        logging.info('amd-smi initialized successfully')
    else:
        logging.error('Driver not initialized (amdgpu not found in modules)')
        exit(-1)


def amdsmi_shut_down():
    """ Shutdown AMD-SMI """
    # Only init AMD GPUs for now, waiting for future support for AMD CPUs 
    shut_down_status = amdsmi.amdsmi_shut_down()
    check_return(return_code=shut_down_status, error_statment=f'AMD SMI Shutdown code returned {shut_down_status} (the expected value is {amdsmi_status_t.AMDSMI_STATUS_SUCCESS})')
    logging.debug('amd-smi shutdown successfully')
    

def signal_handler(sig, frame):
    logging.debug(f'Handling signal: {sig}')
    sys.exit(0)


if not amd_smi_initialized:
    init_amd_smi()
    amd_smi_initialized = True
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(amdsmi_shut_down)

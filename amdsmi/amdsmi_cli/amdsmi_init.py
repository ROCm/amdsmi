#!/usr/bin/python3

### Handle init singularly
# Python imports module does not re-execute code on import

import atexit
import logging
import signal
import sys

from pathlib import Path

# Handle bindings for windows, Hyper-v and KVM seperately
import amdsmi_interface


# Using basic python logging for user errors and development
# logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG) # Logging for Development
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.ERROR) # User level logging

# On initial import set initialized variable
amd_smi_initialized = False


def check_amdgpu_driver(): #@TODO Handle KVM logic
    """ Returns true if amdgpu is found in the list of initialized modules """
    amd_gpu_status_file = Path("/sys/module/amdgpu/initstate")

    if amd_gpu_status_file.exists():
        if amd_gpu_status_file.read_text().strip() == 'live':
            return True

    return False


def init_amd_smi(flag=amdsmi_interface.AmdSmiInitFlags.AMD_GPUS):
    """ Initializes AMD-SMI """
    # Check if amdgpu driver is up & Handle error gracefully
    if check_amdgpu_driver():
        # Only init AMD GPUs for now, waiting for future support for AMD CPUs 
        amdsmi_interface.amdsmi_init(flag)
        logging.info('amd-smi initialized successfully') # without errors really
    else:
        logging.error('Driver not initialized (amdgpu not found in modules)')
        exit(-1)


def signal_handler(sig, frame):
    logging.info(f'Handling signal: {sig}')
    sys.exit(0)


if not amd_smi_initialized:
    init_amd_smi()
    amd_smi_initialized = True
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(amdsmi_interface.amdsmi_shut_down)

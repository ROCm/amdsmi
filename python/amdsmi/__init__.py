# Copyright (c) Advanced Micro Devices, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

"""
AMDSMI - AMD System Management Interface

A Python library for monitoring and managing AMD GPUs and CPUs.
"""

__version__ = "26.1.0"

# Import runtime module
from .. import _amdsmi as _runtime

# Exception classes
class AmdSmiException(Exception):
    """Base exception for AMDSMI errors."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

class AmdSmiParameterException(AmdSmiException):
    """Exception for invalid parameters."""
    pass

class AmdSmiLibraryException(AmdSmiException):
    """Exception for library errors."""
    pass

# Re-export enums and constants
InitFlags = _runtime.InitFlags
ProcessorType = _runtime.ProcessorType
ContainerType = _runtime.ContainerType
Status = _runtime.Status

# Constants
MAX_STRING_LENGTH = _runtime.MAX_STRING_LENGTH
MAX_DEVICES = _runtime.MAX_DEVICES
GPU_UUID_SIZE = _runtime.GPU_UUID_SIZE
NUM_HBM_INSTANCES = _runtime.NUM_HBM_INSTANCES

# Core functions with exception handling
def amdsmi_init(flags=InitFlags.INIT_AMD_GPUS):
    """Initialize the AMDSMI library.

    Args:
        flags: Initialization flags specifying which processors to initialize

    Raises:
        AmdSmiException: If initialization fails
    """
    try:
        _runtime.init(flags)
    except Exception as e:
        raise AmdSmiLibraryException(f"Failed to initialize AMDSMI: {e}")

def amdsmi_shut_down():
    """Shutdown the AMDSMI library.

    Raises:
        AmdSmiException: If shutdown fails
    """
    try:
        _runtime.shut_down()
    except Exception as e:
        raise AmdSmiLibraryException(f"Failed to shutdown AMDSMI: {e}")

def amdsmi_get_processor_count():
    """Get the number of processors in the system.

    Returns:
        int: Number of processors

    Raises:
        AmdSmiException: If unable to get processor count
    """
    try:
        return _runtime.get_processor_count()
    except Exception as e:
        raise AmdSmiLibraryException(f"Failed to get processor count: {e}")

def amdsmi_get_processor_handles():
    """Get handles for all processors in the system.

    Returns:
        list[int]: List of processor handles

    Raises:
        AmdSmiException: If unable to get processor handles
    """
    try:
        return _runtime.get_processor_handles()
    except Exception as e:
        raise AmdSmiLibraryException(f"Failed to get processor handles: {e}")

def amdsmi_get_processor_type(processor_handle):
    """Get the type of a processor.

    Args:
        processor_handle: Handle to the processor

    Returns:
        ProcessorType: Type of the processor

    Raises:
        AmdSmiException: If unable to get processor type
    """
    try:
        return _runtime.get_processor_type(processor_handle)
    except Exception as e:
        raise AmdSmiLibraryException(f"Failed to get processor type: {e}")

def amdsmi_get_processor_info(processor_handle):
    """Get information about a processor.

    Args:
        processor_handle: Handle to the processor

    Returns:
        str: Processor information string

    Raises:
        AmdSmiException: If unable to get processor info
    """
    try:
        return _runtime.get_processor_info(processor_handle)
    except Exception as e:
        raise AmdSmiLibraryException(f"Failed to get processor info: {e}")

# GPU-specific functions
def amdsmi_get_gpu_device_uuid(processor_handle):
    """Get the UUID of a GPU device.

    Args:
        processor_handle: Handle to the GPU

    Returns:
        str: GPU UUID

    Raises:
        AmdSmiException: If unable to get GPU UUID
    """
    try:
        return _runtime.get_gpu_device_uuid(processor_handle)
    except Exception as e:
        raise AmdSmiLibraryException(f"Failed to get GPU UUID: {e}")

def amdsmi_get_gpu_id(processor_handle):
    """Get the ID of a GPU device.

    Args:
        processor_handle: Handle to the GPU

    Returns:
        int: GPU ID

    Raises:
        AmdSmiException: If unable to get GPU ID
    """
    try:
        return _runtime.get_gpu_id(processor_handle)
    except Exception as e:
        raise AmdSmiLibraryException(f"Failed to get GPU ID: {e}")

def amdsmi_get_gpu_vendor_name(processor_handle):
    """Get the vendor name of a GPU.

    Args:
        processor_handle: Handle to the GPU

    Returns:
        str: GPU vendor name

    Raises:
        AmdSmiException: If unable to get GPU vendor name
    """
    try:
        return _runtime.get_gpu_vendor_name(processor_handle)
    except Exception as e:
        raise AmdSmiLibraryException(f"Failed to get GPU vendor name: {e}")

def amdsmi_get_gpu_memory_usage(processor_handle):
    """Get GPU memory usage information.

    Args:
        processor_handle: Handle to the GPU

    Returns:
        tuple[int, int]: (used_memory, total_memory) in bytes

    Raises:
        AmdSmiException: If unable to get memory usage
    """
    try:
        return _runtime.get_gpu_memory_usage(processor_handle)
    except Exception as e:
        raise AmdSmiLibraryException(f"Failed to get GPU memory usage: {e}")

def amdsmi_get_lib_version():
    """Get the AMDSMI library version.

    Returns:
        tuple[int, int, int]: (major, minor, release) version numbers

    Raises:
        AmdSmiException: If unable to get library version
    """
    try:
        return _runtime.get_lib_version()
    except Exception as e:
        raise AmdSmiLibraryException(f"Failed to get library version: {e}")

# Convenience functions for common use cases
def get_gpu_list():
    """Get a list of all GPU handles in the system.

    Returns:
        list[int]: List of GPU processor handles
    """
    handles = amdsmi_get_processor_handles()
    gpu_handles = []

    for handle in handles:
        try:
            proc_type = amdsmi_get_processor_type(handle)
            if proc_type == ProcessorType.AMD_GPU:
                gpu_handles.append(handle)
        except AmdSmiException:
            # Skip processors we can't query
            continue

    return gpu_handles

def get_gpu_info(processor_handle):
    """Get comprehensive information about a GPU.

    Args:
        processor_handle: Handle to the GPU

    Returns:
        dict: Dictionary with GPU information
    """
    info = {}

    try:
        info['uuid'] = amdsmi_get_gpu_device_uuid(processor_handle)
        info['id'] = amdsmi_get_gpu_id(processor_handle)
        info['vendor'] = amdsmi_get_gpu_vendor_name(processor_handle)
        info['processor_info'] = amdsmi_get_processor_info(processor_handle)

        memory_used, memory_total = amdsmi_get_gpu_memory_usage(processor_handle)
        info['memory'] = {
            'used': memory_used,
            'total': memory_total,
            'utilization': memory_used / memory_total if memory_total > 0 else 0.0
        }
    except AmdSmiException:
        # Add what we can get
        pass

    return info

# Export main functions
__all__ = [
    # Exceptions
    'AmdSmiException',
    'AmdSmiParameterException',
    'AmdSmiLibraryException',

    # Enums
    'InitFlags',
    'ProcessorType',
    'ContainerType',
    'Status',

    # Constants
    'MAX_STRING_LENGTH',
    'MAX_DEVICES',
    'GPU_UUID_SIZE',
    'NUM_HBM_INSTANCES',

    # Core functions
    'amdsmi_init',
    'amdsmi_shut_down',
    'amdsmi_get_processor_count',
    'amdsmi_get_processor_handles',
    'amdsmi_get_processor_type',
    'amdsmi_get_processor_info',

    # GPU functions
    'amdsmi_get_gpu_device_uuid',
    'amdsmi_get_gpu_id',
    'amdsmi_get_gpu_vendor_name',
    'amdsmi_get_gpu_memory_usage',

    # Version functions
    'amdsmi_get_lib_version',

    # Convenience functions
    'get_gpu_list',
    'get_gpu_info',
]
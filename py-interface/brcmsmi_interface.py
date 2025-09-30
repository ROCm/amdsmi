#!/usr/bin/env python3
"""
BRCM SMI Python Interface

This module provides a Python ctypes interface to the BRCM SMI library.
It handles library loading, initialization, and provides methods for
interacting with BRCM devices.
"""

import ctypes
from pathlib import Path


# Handle type definitions
brcmsmi_socket_handle = ctypes.c_uint32
brcmsmi_processor_handle = ctypes.c_uint32

# Device type enumeration
class BrcmsmiProcessorType(ctypes.c_uint32):
    BRCMSMI_PROCESSOR_TYPE_NIC = 0
    BRCMSMI_PROCESSOR_TYPE_SWITCH = 1

# BDF (Bus:Device:Function) structure
class BrcmsmiBdf(ctypes.Structure):
    _fields_ = [
        ("domain", ctypes.c_uint64),
        ("bus", ctypes.c_uint64),
        ("device", ctypes.c_uint64),
        ("function", ctypes.c_uint64),
    ]


class BrcmSmiInterface:
    """BRCM SMI Python Interface Class"""
    
    def __init__(self):
        """Initialize the BRCM SMI interface and load the library"""
        self.lib = None
        self._load_library()
    
    def _load_library(self):
        """Load the BRCM SMI library"""
        # Determine library path
        script_dir = Path(__file__).parent
        lib_path = script_dir.parent / "brcm_smi_lib" / "build" / "libbrcm_smi.so.1.0.0"
        
        if not lib_path.exists():
            raise FileNotFoundError(f"Library not found at {lib_path}. "
                                  "Please build the library first: "
                                  "cd ../brcm_smi_lib && ./build_standalone.sh")
        
        # Load the BRCM SMI library
        print(f"Loading library from: {lib_path}")
        self.lib = ctypes.CDLL(str(lib_path))
        print("✅ Library loaded successfully")
    
    def initialize(self, flags=0):
        """Initialize the BRCM SMI library"""
        if self.lib is None:
            raise RuntimeError("Library not loaded")
        
        init_func = self.lib.brcmsmi_init
        init_func.argtypes = [ctypes.c_uint64]
        init_func.restype = ctypes.c_uint32
        
        return init_func(flags)
    
    def shutdown(self):
        """Shutdown the BRCM SMI library"""
        if self.lib is None:
            raise RuntimeError("Library not loaded")
        
        shutdown_func = self.lib.brcmsmi_shutdown
        shutdown_func.restype = ctypes.c_uint32
        
        return shutdown_func()
    
    def get_socket_handles(self):
        """Get socket handles and count"""
        if self.lib is None:
            raise RuntimeError("Library not loaded")
        
        get_socket_handles = self.lib.brcmsmi_get_socket_handles
        get_socket_handles.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p]
        get_socket_handles.restype = ctypes.c_uint32
        
        socket_count = ctypes.c_uint32(0)
        result = get_socket_handles(ctypes.byref(socket_count), None)
        
        return result, socket_count.value
    
    def discover_devices(self):
        """Discover BRCM devices"""
        if self.lib is None:
            raise RuntimeError("Library not loaded")
        
        # Define discovery result structure
        class BrcmsmiDiscoveryResult(ctypes.Structure):
            _fields_ = [
                ("nic_count", ctypes.c_uint32),
                ("switch_count", ctypes.c_uint32),
                ("total_count", ctypes.c_uint32),
            ]
        
        discover_devices = self.lib.brcmsmi_discover_devices
        discover_devices.argtypes = [ctypes.POINTER(BrcmsmiDiscoveryResult)]
        discover_devices.restype = ctypes.c_uint32
        
        discovery_result = BrcmsmiDiscoveryResult()
        result = discover_devices(ctypes.byref(discovery_result))
        
        return result, discovery_result
    
    def get_socket_handles_with_array(self, max_sockets=16):
        """Get socket handles with actual handle array"""
        if self.lib is None:
            raise RuntimeError("Library not loaded")
        
        get_socket_handles = self.lib.brcmsmi_get_socket_handles
        get_socket_handles.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(brcmsmi_socket_handle)]
        get_socket_handles.restype = ctypes.c_uint32
        
        socket_count = ctypes.c_uint32(0)
        socket_handles = (brcmsmi_socket_handle * max_sockets)()
        
        result = get_socket_handles(ctypes.byref(socket_count), socket_handles)
        
        # Convert to Python list
        handles_list = [socket_handles[i] for i in range(socket_count.value)]
        
        return result, socket_count.value, handles_list
    
    def get_nic_processor_handles(self, socket_handle, max_processors=16):
        """Get NIC processor handles for a given socket"""
        if self.lib is None:
            raise RuntimeError("Library not loaded")
        
        get_nic_handles = self.lib.brcmsmi_get_nic_processor_handles
        get_nic_handles.argtypes = [brcmsmi_socket_handle, ctypes.POINTER(ctypes.c_uint32), 
                                   ctypes.POINTER(brcmsmi_processor_handle)]
        get_nic_handles.restype = ctypes.c_uint32
        
        processor_count = ctypes.c_uint32(0)
        processor_handles = (brcmsmi_processor_handle * max_processors)()
        
        result = get_nic_handles(socket_handle, ctypes.byref(processor_count), processor_handles)
        
        # Convert to Python list
        handles_list = [processor_handles[i] for i in range(processor_count.value)]
        
        return result, processor_count.value, handles_list
    
    def get_switch_processor_handles(self, socket_handle, max_processors=16):
        """Get switch processor handles for a given socket"""
        if self.lib is None:
            raise RuntimeError("Library not loaded")
        
        get_switch_handles = self.lib.brcmsmi_get_switch_processor_handles
        get_switch_handles.argtypes = [brcmsmi_socket_handle, ctypes.POINTER(ctypes.c_uint32), 
                                      ctypes.POINTER(brcmsmi_processor_handle)]
        get_switch_handles.restype = ctypes.c_uint32
        
        processor_count = ctypes.c_uint32(0)
        processor_handles = (brcmsmi_processor_handle * max_processors)()
        
        result = get_switch_handles(socket_handle, ctypes.byref(processor_count), processor_handles)
        
        # Convert to Python list
        handles_list = [processor_handles[i] for i in range(processor_count.value)]
        
        return result, processor_count.value, handles_list
    
    def get_brcm_processor_handles(self, socket_index, device_type, max_processors=16):
        """Get BRCM processor handles for AMD SMI compatibility"""
        if self.lib is None:
            raise RuntimeError("Library not loaded")
        
        get_brcm_handles = self.lib.brcmsmi_get_brcm_processor_handles
        get_brcm_handles.argtypes = [ctypes.c_uint32, BrcmsmiProcessorType, 
                                    ctypes.POINTER(ctypes.c_uint32), 
                                    ctypes.POINTER(brcmsmi_processor_handle)]
        get_brcm_handles.restype = ctypes.c_uint32
        
        processor_count = ctypes.c_uint32(0)
        processor_handles = (brcmsmi_processor_handle * max_processors)()
        
        result = get_brcm_handles(socket_index, device_type, ctypes.byref(processor_count), processor_handles)
        
        # Convert to Python list
        handles_list = [processor_handles[i] for i in range(processor_count.value)]
        
        return result, processor_count.value, handles_list
    
    def get_brcm_processor_handles_by_type(self, socket_handle, device_type, max_processors=16):
        """Get BRCM processor handles by device type"""
        if self.lib is None:
            raise RuntimeError("Library not loaded")
        
        get_handles_by_type = self.lib.brcmsmi_get_brcm_processor_handles_by_type
        get_handles_by_type.argtypes = [brcmsmi_socket_handle, BrcmsmiProcessorType, 
                                       ctypes.POINTER(ctypes.c_uint32), 
                                       ctypes.POINTER(brcmsmi_processor_handle)]
        get_handles_by_type.restype = ctypes.c_uint32
        
        processor_count = ctypes.c_uint32(0)
        processor_handles = (brcmsmi_processor_handle * max_processors)()
        
        result = get_handles_by_type(socket_handle, device_type, ctypes.byref(processor_count), processor_handles)
        
        # Convert to Python list
        handles_list = [processor_handles[i] for i in range(processor_count.value)]
        
        return result, processor_count.value, handles_list
    
    def get_brcm_processor_handles_by_bdf(self, socket_handle, bdf, max_processors=16):
        """Get BRCM processor handles by BDF (Bus:Device:Function)"""
        if self.lib is None:
            raise RuntimeError("Library not loaded")
        
        get_handles_by_bdf = self.lib.brcmsmi_get_brcm_processor_handles_by_bdf
        get_handles_by_bdf.argtypes = [brcmsmi_socket_handle, BrcmsmiBdf, 
                                      ctypes.POINTER(ctypes.c_uint32), 
                                      ctypes.POINTER(brcmsmi_processor_handle)]
        get_handles_by_bdf.restype = ctypes.c_uint32
        
        processor_count = ctypes.c_uint32(0)
        processor_handles = (brcmsmi_processor_handle * max_processors)()
        
        result = get_handles_by_bdf(socket_handle, bdf, ctypes.byref(processor_count), processor_handles)
        
        # Convert to Python list
        handles_list = [processor_handles[i] for i in range(processor_count.value)]
        
        return result, processor_count.value, handles_list
    
    def create_bdf(self, domain, bus, device, function):
        """Create a BDF structure"""
        bdf = BrcmsmiBdf()
        bdf.domain = domain
        bdf.bus = bus
        bdf.device = device
        bdf.function = function
        return bdf
    
    def generic_call(self, function_name, *args):
        """Make a generic call to the library"""
        if self.lib is None:
            raise RuntimeError("Library not loaded")
        
        generic_call = self.lib.brcmsmi_generic_call
        generic_call.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        generic_call.restype = ctypes.c_uint32
        
        # Convert function name to bytes if it's a string
        if isinstance(function_name, str):
            function_name = function_name.encode('utf-8')
        
        # Pad args to 4 parameters with None
        padded_args = list(args) + [None] * (4 - len(args))
        padded_args = padded_args[:4]  # Ensure exactly 4 args
        
        return generic_call(function_name, *padded_args)


#==============================================================================
# BRCM SMI BDF Functions
#==============================================================================

def amdsmi_get_brcm_nic_device_bdf(processor_handle) -> str:
    """
    Get NIC device BDF (Bus:Device:Function) information.
    
    Parameters:
        processor_handle: NIC processor handle
        
    Returns:
        str: BDF string in format "domain:bus:device.function"
        
    Raises:
        Exception: If getting BDF fails
    """
    import ctypes
    import os
    
    # Load library and get function
    lib_path = os.environ.get('LD_LIBRARY_PATH', '').split(':')[0] + '/libamd_smi.so'
    if not os.path.exists(lib_path):
        lib_path = 'libamd_smi.so'  # Fallback to system library
    
    lib = ctypes.CDLL(lib_path)
    
    # Define the NIC info structure (matching C structure exactly)
    class BrcmsmiNicInfo(ctypes.Structure):
        _fields_ = [
            ("nic_device_name", ctypes.c_char * 256),  # BRCMSMI_MAX_STRING_LENGTH
            ("nic_part_number", ctypes.c_char * 256),
            ("nic_firmware_version", ctypes.c_char * 256),
            ("nic_uuid", ctypes.c_char * 256),
            ("nic_bdf", BrcmsmiBdf),
        ]
    
    # Try the nic info function that contains BDF
    try:
        brcmsmi_get_nic_info = lib.brcmsmi_get_nic_info
        brcmsmi_get_nic_info.argtypes = [ctypes.c_uint32, ctypes.POINTER(BrcmsmiNicInfo)]
        brcmsmi_get_nic_info.restype = ctypes.c_uint32
        
        # Call function
        info_struct = BrcmsmiNicInfo()
        handle_uint32 = ctypes.c_uint32(int(processor_handle))
        result = brcmsmi_get_nic_info(handle_uint32, ctypes.byref(info_struct))
        
        if result == 0:
            bdf = info_struct.nic_bdf
            # Check if we got valid BDF values
            if bdf.domain != 0 or bdf.bus != 0 or bdf.device != 0 or bdf.function != 0:
                return f"{bdf.domain:04x}:{bdf.bus:02x}:{bdf.device:02x}.{bdf.function}"
    except Exception as e:
        pass  # Try fallback method
    
    # Try the dedicated BDF function as fallback
    try:
        brcmsmi_get_nic_device_bdf = lib.brcmsmi_get_nic_device_bdf
        brcmsmi_get_nic_device_bdf.argtypes = [ctypes.c_uint32, ctypes.POINTER(BrcmsmiBdf)]
        brcmsmi_get_nic_device_bdf.restype = ctypes.c_uint32
        
        # Call function
        bdf_struct = BrcmsmiBdf()
        handle_uint32 = ctypes.c_uint32(int(processor_handle))
        result = brcmsmi_get_nic_device_bdf(handle_uint32, ctypes.byref(bdf_struct))
        
        if result == 0:
            # Check if we got valid BDF values
            if bdf_struct.domain != 0 or bdf_struct.bus != 0 or bdf_struct.device != 0 or bdf_struct.function != 0:
                return f"{bdf_struct.domain:04x}:{bdf_struct.bus:02x}:{bdf_struct.device:02x}.{bdf_struct.function}"
    except Exception as e:
        pass
    
    # If we get here, the library returned zeros or failed
    raise Exception(f"Library returned invalid BDF values (all zeros) for handle {processor_handle}")

def amdsmi_get_brcm_switch_device_bdf(processor_handle) -> str:
    """
    Get Switch device BDF (Bus:Device:Function) information.
    
    Parameters:
        processor_handle: Switch processor handle
        
    Returns:
        str: BDF string in format "domain:bus:device.function"
        
    Raises:
        Exception: If getting BDF fails
    """
    import ctypes
    import os
    
    # Load library and get function
    lib_path = os.environ.get('LD_LIBRARY_PATH', '').split(':')[0] + '/libamd_smi.so'
    if not os.path.exists(lib_path):
        lib_path = 'libamd_smi.so'  # Fallback to system library
    
    lib = ctypes.CDLL(lib_path)
    
    # Define the Switch info structure (complete structure matching C header)
    class BrcmsmiSwitchInfo(ctypes.Structure):
        _fields_ = [
            ("switch_device_name", ctypes.c_char * 256),  # BRCMSMI_MAX_STRING_LENGTH
            ("switch_part_number", ctypes.c_char * 256),
            ("switch_firmware_version", ctypes.c_char * 256),
            ("switch_uuid", ctypes.c_char * 256),
            ("switch_bdf", BrcmsmiBdf),
            ("switch_vendor_id", ctypes.c_char * 256),
            ("switch_device_id", ctypes.c_char * 256),
            ("switch_subsystem_vendor", ctypes.c_char * 256),
            ("switch_subsystem_device", ctypes.c_char * 256),
            ("switch_class", ctypes.c_char * 256),
            ("switch_revision", ctypes.c_char * 256),
            ("switch_irq", ctypes.c_char * 256),
            ("switch_numa_node", ctypes.c_char * 256),
            ("switch_current_link_speed", ctypes.c_char * 256),
            ("switch_max_link_speed", ctypes.c_char * 256),
            ("switch_current_link_width", ctypes.c_char * 256),
            ("switch_max_link_width", ctypes.c_char * 256),
            ("switch_power_control", ctypes.c_char * 256),
            ("switch_power_runtime_status", ctypes.c_char * 256),
            ("switch_power_runtime_enabled", ctypes.c_char * 256),
        ]
    
    # Try the switch info function that contains BDF
    try:
        brcmsmi_get_switch_info = lib.brcmsmi_get_switch_info
        brcmsmi_get_switch_info.argtypes = [ctypes.c_uint32, ctypes.POINTER(BrcmsmiSwitchInfo)]
        brcmsmi_get_switch_info.restype = ctypes.c_uint32
        
        # Call function
        info_struct = BrcmsmiSwitchInfo()
        handle_uint32 = ctypes.c_uint32(int(processor_handle))
        result = brcmsmi_get_switch_info(handle_uint32, ctypes.byref(info_struct))
        
        if result == 0:
            bdf = info_struct.switch_bdf
            # Check if we got valid BDF values
            if bdf.domain != 0 or bdf.bus != 0 or bdf.device != 0 or bdf.function != 0:
                return f"{bdf.domain:04x}:{bdf.bus:02x}:{bdf.device:02x}.{bdf.function}"
    except Exception as e:
        pass  # Try fallback method
    
    # Try the dedicated BDF function as fallback
    try:
        brcmsmi_get_switch_device_bdf = lib.brcmsmi_get_switch_device_bdf
        brcmsmi_get_switch_device_bdf.argtypes = [ctypes.c_uint32, ctypes.POINTER(BrcmsmiBdf)]
        brcmsmi_get_switch_device_bdf.restype = ctypes.c_uint32
        
        # Call function
        bdf_struct = BrcmsmiBdf()
        handle_uint32 = ctypes.c_uint32(int(processor_handle))
        result = brcmsmi_get_switch_device_bdf(handle_uint32, ctypes.byref(bdf_struct))
        
        if result == 0:
            # Check if we got valid BDF values
            if bdf_struct.domain != 0 or bdf_struct.bus != 0 or bdf_struct.device != 0 or bdf_struct.function != 0:
                return f"{bdf_struct.domain:04x}:{bdf_struct.bus:02x}:{bdf_struct.device:02x}.{bdf_struct.function}"
    except Exception as e:
        pass
    
    # If we get here, the library returned zeros or failed
    raise Exception(f"Library returned invalid BDF values (all zeros) for handle {processor_handle}")

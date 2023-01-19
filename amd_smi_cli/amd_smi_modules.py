#!/usr/bin/python3

import argparse
import platform
import signal
import subprocess
import sys
import time
import traceback

from pathlib import Path

import BDF
from amd_smi_init import *

class AMD_SMI_Modules(object):
    def __init__(self) -> None:
        pass


    def get_socket_handles(self):
        ### Returns tuple of (int, list of ctypes: socket_handles)
        socket_count = c_uint32(0)
        return_code = amdsmi.amdsmi_get_socket_handles(byref(socket_count), None)
        check_return(return_code=return_code, error_statment="Invalid get_socket_handles request")

        sockets = [0] * socket_count.value # 1
        socket_handles = (c_void_p * socket_count.value)(*sockets) # That is a pointer, not a multiplication
        return_code = amdsmi.amdsmi_get_socket_handles(byref(socket_count), socket_handles)
        check_return(return_code=return_code, error_statment=f"Invalid get_socket_handles with {socket_count.value} sockets")
        return (socket_count.value, socket_handles)


    def get_device_handles(self, socket_handle):
        """Gets the Device Handles that are in the current socket"""
        ### Returns tuple of (int, list of ctypes: device_handles)
        device_count = c_uint32(0)
        return_code = amdsmi.amdsmi_get_device_handles(socket_handle, byref(device_count), None)
        check_return(return_code=return_code, error_statment="Invalid get_device_handles request")

        devices = [0] * device_count.value
        device_handles = (c_void_p * len(devices))(*devices)
        return_code = amdsmi.amdsmi_get_device_handles(socket_handle, byref(device_count), byref(device_handles))
        check_return(return_code=return_code, error_statment=f"Invalid get_device_handles with {device_count.value} devices")
        return (device_count.value, device_handles)


    def get_socket_info(self, socket_handle):
        """ Given a socket_handle, return the socket_info, which is just a BDF object"""
        socket_info = create_string_buffer(128) # createstringbuffer or something??? c_char_p
        return_code = amdsmi.amdsmi_get_socket_info(socket_handle, byref(socket_info), c_size_t(128))
        check_return(return_code=return_code, error_statment="Invalid get_socket_info request")
        socket_bdf = BDF.BDF(socket_info.value.decode())
        return(socket_bdf)


    def get_device_type(self, device_handle, format=True):
        # format: True for string; False for int 
        # Returns device_type string for the given device_handle
        dev_type = c_int(0)
        return_code = amdsmi.amdsmi_get_device_type(device_handle, byref(dev_type))
        check_return(return_code=return_code, error_statment="Invalid get_device_type request")

        if format == True: # Return string
            return device_type__enumvalues[dev_type.value]

        return dev_type.value # Return int


    def get_device_bdf(self, device_handle):

    # class amdsmi_bdf_t (Union):
    # _fields_ = [
    #     ('bdf_submodule', bdf_submodule),
    #     ('as_uint', c_uint64)
    # ]
        bdf = amdsmi_bdf_t()
        # bdf.bdf_submodule
    


        return_code = amdsmi.amdsmi_get_device_bdf(device_handle, bdf)
        check_return(return_code=return_code, error_statment="Invalid amdsmi_get_device_bdf request")
        return (bdf)


    def get_device_handle_from_bdf(self, bdf):
        pass


    def get_fan_speed(self, bdf):
        pass

    def show_retired_pages(self):
    #         num_pages = c_uint32()
    # records = rsmi_retired_page_record_t()
        pass
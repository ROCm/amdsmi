#!/usr/bin/python3
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

import logging
import platform
import time

from pathlib import Path

from amdsmi_init import *
from BDF import BDF


class AMDSMIHelpers():
    """Helper functions that aren't apart of the AMDSMI API
    Useful for determining platform and device identifiers

    Functions:
        os_info: tuple ()
    """

    def __init__(self) -> None:
        self.operating_system = platform.system()

        self._is_hypervisor = False
        self._is_virtual_os = False
        self._is_baremetal = False

        self._is_linux = False
        self._is_windows = False

        if self.operating_system.startswith("Linux"):
            self._is_linux = True
            logging.debug(f"AMDSMIHelpers: Platform is linux:{self._is_linux}")

            product_name = ""
            product_name_path = Path("/sys/class/dmi/id/product_name")
            if product_name_path.exists():
                product_name = product_name_path.read_text().strip()

            if product_name == "":
                # Unable to determine product_name default to baremetal
                self._is_baremetal = True

            # Determine if a system is baremetal by deduction
            self._is_baremetal = not self._is_hypervisor and not self._is_virtual_os


    def os_info(self, string_format=True):
        """Return operating_system and type information ex. (Linux, Baremetal)
        params:
            string_format (bool) True to return in string format, False to return Tuple
        returns:
            str or (str, str)
        """
        operating_system = ""
        if self._is_linux:
            operating_system = "Linux"
        elif self._is_windows:
            operating_system = "Windows"
        else:
            operating_system = "Unknown"

        operating_system_type = ""
        if self._is_baremetal:
            operating_system_type = "Baremetal"
        elif self._is_virtual_os:
            operating_system_type = "Guest"
        elif self._is_hypervisor:
            operating_system_type = "Hypervisor"
        else:
            operating_system_type = "Unknown"

        if string_format:
            return f"{operating_system} {operating_system_type}"
        else:
            return (operating_system, operating_system_type)


    def is_virtual_os(self):
        return self._is_virtual_os


    def is_hypervisor(self):
        # Returns True if hypervisor is enabled on the system
        return self._is_hypervisor


    def is_baremetal(self):
        # Returns True if system is baremetal, if system is hypervisor this should return False
        return self._is_baremetal


    def is_linux(self):
        return self._is_linux


    def is_windows(self):
        return self._is_windows


    def get_gpu_choices(self):
        """Return dictionary of possible GPU choices and string of the output:
            Dictionary will be in format: gpus[ID] : (BDF, UUID, Device Handle)
            String output will be in format:
                "ID:0  | BDF:0000:23:00.0 | UUID:ffffffff-0000-1000-0000-000000000000"
        params:
            None
        return:
            (dict, str) : (gpu_choices, gpu_choices_str)
        """
        gpu_choices = {}
        gpu_choices_str = ""

        # amdsmi_get_device_handles returns the device_handles storted by gpu_id
        device_handles = amdsmi_interface.amdsmi_get_device_handles()
        for gpu_id, device_handle in enumerate(device_handles):
            bdf = amdsmi_interface.amdsmi_get_device_bdf(device_handle)
            uuid = amdsmi_interface.amdsmi_get_device_uuid(device_handle)
            gpu_choices[str(gpu_id)] = {
                "BDF": bdf,
                "UUID": uuid,
                "Device Handle": device_handle,
            }
            gpu_choices_str += f"ID:{gpu_id:<2} | BDF:{bdf} | UUID:{uuid}"

        return (gpu_choices, gpu_choices_str)


    def get_device_handles_from_gpu_selections(self, gpu_selections, gpu_choices=None):
        """Convert provided gpu_selections to device_handles

        Args:
            gpu_selections (list[str]): This will be the GPU ID, BDF, or UUID:
                    ex: ID:0  | BDF:0000:23:00.0 | UUID:ffffffff-0000-1000-0000-000000000000
            gpu_choices (dict{gpu_choices}): This is a dictionary of the possible gpu_choices
        Returns:
            (True, list[device_handles]): Returns a list of all the gpu_selections converted to
                amdsmi device_handles
            (False, str): Return False, and the first input that failed to be converted
        """
        if isinstance(gpu_selections, str):
            gpu_selections = [gpu_selections]

        if gpu_choices is None:
            gpu_choices = self.get_gpu_choices()[0]

        selected_device_handles = []
        for gpu_selection in gpu_selections:
            valid_gpu_choice = False

            for gpu_id, gpu_info in gpu_choices.items():
                bdf = gpu_info['BDF']
                uuid = gpu_info['UUID']
                device_handle = gpu_info['Device Handle']

                # Check if passed gpu is a gpu ID or UUID
                if gpu_selection == gpu_id or gpu_selection.lower() == uuid:
                    selected_device_handles.append(device_handle)
                    valid_gpu_choice = True
                    break
                else:  # Check if gpu passed is a BDF object
                    try:
                        if BDF(gpu_selection) == BDF(bdf):
                            selected_device_handles.append(device_handle)
                            valid_gpu_choice = True
                            break
                    except Exception:
                        # Ignore exception when checking if the gpu_choice is a BDF
                        pass

            if not valid_gpu_choice:
                logging.debug(f"AMDSMIHelpers.get_device_handles_from_gpu_selections - Unable to convert {gpu_selection}")
                return False, gpu_selection
        return True, selected_device_handles


    def handle_watch(self, args, subcommand):
        """This function will run the subcommand multiple times based
            on the passed watch, watch_time, and iterations passed in.
        params:
            args - argparser args to pass to subcommand
            subcommand (AMDSMICommands) - Function that can handle
                watching output (Currently: metric & process)
        return:
            Nothing
        """
        # Set the values for watching as the args will cleared
        watch = args.watch
        watch_time = args.watch_time
        iterations = args.iterations

        # Set the args values to None so we don't loop recursively
        args.watch = None
        args.watch_time = None
        args.iterations = None

        if watch_time:  # Run for set amount of time
            iterations_ran = 0
            end_time = time.time() + watch_time
            while time.time() <= end_time:
                subcommand(args, watching_output=True)
                # Handle iterations limit
                iterations_ran += 1
                if iterations:
                    if iterations >= iterations_ran:
                        break
                time.sleep(watch)
        elif iterations:  # Run for a set amount of iterations
            for iteration in range(iterations):
                subcommand(args, watching_output=True)
                if iteration == iterations - 1:  # Break on iteration completion
                    break
                time.sleep(watch)
        else:  # Run indefinitely as watch_time and iterations are not set
            while True:
                subcommand(args, watching_output=True)
                time.sleep(watch)

        return 1


    def get_gpu_id_from_device_handle(self, input_device_handle):
        """Get the gpu index from the device_handle.
        amdsmi_get_device_handles() returns the list of device_handles in order of gpu_index
        """
        device_handles = amdsmi_interface.amdsmi_get_device_handles()
        for gpu_index, device_handle in enumerate(device_handles):
            if input_device_handle.value == device_handle.value:
                return gpu_index
        raise IndexError("Unable to find gpu ID from device_handle")


    def get_amd_gpu_bdfs(self):
        """Return a list of GPU BDFs visibile to amdsmi

        Returns:
            list[BDF]: List of GPU BDFs
        """
        gpu_bdfs = []
        device_handles = amdsmi_interface.amdsmi_get_device_handles()

        for device_handle in device_handles:
            bdf = amdsmi_interface.amdsmi_get_device_bdf(device_handle)
            gpu_bdfs.append(bdf)

        return gpu_bdfs


    # def get_amd_cpu_bdfs(self):
    #     pass


    def is_amd_device(self, device_handle):
        """ Return whether the specified device is an AMD device or not

        param device: DRM device identifier
        """
        # Get card vendor id
        asic_info = amdsmi_interface.amdsmi_get_asic_info(device_handle)
        return asic_info['vendor_id'] == AMD_VENDOR_ID

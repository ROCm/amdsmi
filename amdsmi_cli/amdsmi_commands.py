#!/usr/bin/env python3
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

import threading
import time

from _version import __version__
from amdsmi_helpers import AMDSMIHelpers
from amdsmi_logger import AMDSMILogger
from amdsmi import amdsmi_interface
from amdsmi import amdsmi_exception


class AMDSMICommands():
    """This class contains all the commands corresponding to AMDSMIParser
    Each command function will interact with AMDSMILogger to handle
    displaying the output to the specified compatibility, format, and
    destination.
    """
    def __init__(self, compatibility='amdsmi',
                    format='human_readable',
                    destination='stdout') -> None:
        self.helpers = AMDSMIHelpers()
        self.logger = AMDSMILogger(compatibility=compatibility,
                                    format=format,
                                    destination=destination)
        try:
            self.device_handles = amdsmi_interface.amdsmi_get_processor_handles()
        except amdsmi_exception.AmdSmiLibraryException as e:
            raise e
        self.stop = ''
        self.all_arguments = False


    def version(self, args):
        """Print Version String

        Args:
            args (Namespace): Namespace containing the parsed CLI args
        """
        try:
            amdsmi_lib_version = amdsmi_interface.amdsmi_get_lib_version()
            amdsmi_lib_version_str = f"{amdsmi_lib_version['year']}.{amdsmi_lib_version['major']}.{amdsmi_lib_version['minor']}.{amdsmi_lib_version['release']}"
        except amdsmi_exception.AmdSmiLibraryException as e:
            amdsmi_lib_version_str = e.get_error_info()

        self.logger.output['tool'] = 'AMDSMI Tool'
        self.logger.output['version'] = f'{__version__}'
        self.logger.output['amdsmi_library_version'] = f'{amdsmi_lib_version_str}'

        if self.logger.is_human_readable_format():
            print(f'AMDSMI Tool: {__version__} | '\
                    f'AMDSMI Library version: {amdsmi_lib_version_str}')
        elif self.logger.is_json_format() or self.logger.is_csv_format():
            self.logger.print_output()


    def list(self, args, multiple_devices=False, gpu=None):
        """List information for target gpu

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            gpu (device_handle, optional): device_handle for target device. Defaults to None.

        Raises:
            IndexError: Index error if gpu list is empty

        Returns:
            None: Print output via AMDSMILogger to destination
        """
        # Set args.* to passed in arguments
        if gpu:
            args.gpu = gpu

        # Handle No GPU passed
        if args.gpu == None:
            args.gpu = self.device_handles

        # Handle multiple GPUs
        handled_multiple_gpus, device_handle = self.helpers.handle_gpus(args, self.logger, self.list)
        if handled_multiple_gpus:
            return # This function is recursive

        args.gpu = device_handle

        try:
            bdf = amdsmi_interface.amdsmi_get_gpu_device_bdf(args.gpu)
        except amdsmi_exception.AmdSmiLibraryException as e:
            bdf = e.get_error_info()

        try:
            uuid = amdsmi_interface.amdsmi_get_gpu_device_uuid(args.gpu)
        except amdsmi_exception.AmdSmiLibraryException as e:
            uuid = e.get_error_info()

        # Store values based on format
        if self.logger.is_human_readable_format():
            self.logger.store_output(args.gpu, 'AMDSMI_SPACING_REMOVAL', {'bdf':bdf, 'uuid':uuid})
        else:
            self.logger.store_output(args.gpu, 'bdf', bdf)
            self.logger.store_output(args.gpu, 'uuid', uuid)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        # compatibility with gpuvsmi needs a list for single gpu
        if self.logger.is_gpuvsmi_compatibility() and not multiple_devices:
            self.logger.store_multiple_device_output()
            self.logger.print_output(multiple_device_enabled=True)
        else:
            self.logger.print_output()


    def static(self, args, multiple_devices=False, gpu=None, asic=None,
                bus=None, vbios=None, limit=None, driver=None,
                ras=None, board=None, numa=None):
        """Get Static information for target gpu

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            gpu (device_handle, optional): device_handle for target device. Defaults to None.
            asic (bool, optional): Value override for args.asic. Defaults to None.
            bus (bool, optional): Value override for args.bus. Defaults to None.
            vbios (bool, optional): Value override for args.vbios. Defaults to None.
            limit (bool, optional): Value override for args.limit. Defaults to None.
            driver (bool, optional): Value override for args.driver. Defaults to None.
            ras (bool, optional): Value override for args.ras. Defaults to None.
            board (bool, optional): Value override for args.board. Defaults to None.
            numa (bool, optional): Value override for args.numa. Defaults to None.

        Raises:
            IndexError: Index error if gpu list is empty

        Returns:
            None: Print output via AMDSMILogger to destination
        """
        # Set args.* to passed in arguments
        if gpu:
            args.gpu = gpu
        if asic:
            args.asic = asic
        if bus:
            args.bus = bus
        if vbios:
            args.vbios = vbios
        if driver:
            args.driver = driver
        if numa:
            args.numa = numa
        if self.helpers.is_linux() and self.helpers.is_baremetal():
            if ras:
                args.ras = ras
            if limit:
                args.limit = limit
            if board:
                args.board = board

        # Handle No GPU passed
        if args.gpu == None:
            args.gpu = self.device_handles

        # Handle multiple GPUs
        handled_multiple_gpus, device_handle = self.helpers.handle_gpus(args, self.logger, self.static)
        if handled_multiple_gpus:
            return # This function is recursive
        args.gpu = device_handle

        # If all arguments are False, it means that no argument was passed and the entire static should be printed
        if self.helpers.is_linux() and self.helpers.is_baremetal():
            if not any([args.asic, args.bus, args.vbios, args.limit, args.driver, args.ras, args.board, args.numa]):
                args.asic = args.bus = args.vbios = args.limit = args.driver = args.ras = args.board = args.numa = self.all_arguments = True
        if self.helpers.is_linux() and self.helpers.is_virtual_os():
            if not any([args.asic, args.bus, args.vbios, args.driver]):
                args.asic = args.bus = args.vbios = args.driver = self.all_arguments = True

        static_dict = {}

        if args.asic:
            try:
                asic_info = amdsmi_interface.amdsmi_get_gpu_asic_info(args.gpu)
                asic_info['vendor_id'] = hex(asic_info['vendor_id'])
                asic_info['device_id'] = hex(asic_info['device_id'])
                asic_info['rev_id'] = hex(asic_info['rev_id'])
                if asic_info['asic_serial'] != '':
                    asic_info['asic_serial'] = hex(int(asic_info['asic_serial'], base=16))

                static_dict['asic'] = asic_info
            except amdsmi_exception.AmdSmiLibraryException as e:
                static_dict['asic'] = e.get_error_info()
                if not self.all_arguments:
                    raise e
        if args.bus:
            bus_output_info = {}

            try:
                bus_info = amdsmi_interface.amdsmi_get_pcie_link_caps(args.gpu)
                if bus_info['max_pcie_speed'] % 1000 != 0:
                    pcie_speed_GTs_value = round(bus_info['max_pcie_speed'] / 1000, 1)
                else:
                    pcie_speed_GTs_value = round(bus_info['max_pcie_speed'] / 1000)

                bus_info['max_pcie_speed'] = pcie_speed_GTs_value

                try:
                    pcie_slot_type = amdsmi_interface.amdsmi_topo_get_link_type(args.gpu, args.gpu)['type']
                except amdsmi_exception.AmdSmiLibraryException as e:
                    pcie_slot_type = e.get_error_info()

                if self.logger.is_human_readable_format():
                    unit ='GT/s'
                    bus_info['max_pcie_speed'] = f"{bus_info['max_pcie_speed']} {unit}"

                    if bus_info['pcie_interface_version'] > 0:
                        bus_info['pcie_interface_version'] = f"Gen {bus_info['pcie_interface_version']}"

                    bus_info['pcie_slot_type'] = 'XXXX'
                    if isinstance(pcie_slot_type, int):
                        if pcie_slot_type == amdsmi_interface.amdsmi_wrapper.AMDSMI_IOLINK_TYPE_UNDEFINED:
                            bus_info['pcie_slot_type'] = "UNKNOWN"
                        elif pcie_slot_type == amdsmi_interface.amdsmi_wrapper.AMDSMI_IOLINK_TYPE_PCIEXPRESS:
                            bus_info['pcie_slot_type'] = "PCIE"
                        elif pcie_slot_type == amdsmi_interface.amdsmi_wrapper.AMDSMI_IOLINK_TYPE_XGMI:
                            bus_info['pcie_slot_type'] = "XGMI"

            except amdsmi_exception.AmdSmiLibraryException as e:
                bus_info = e.get_error_info()
                if not self.all_arguments:
                    raise e

            try:
                bus_output_info['bdf'] = amdsmi_interface.amdsmi_get_gpu_device_bdf(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                bus_output_info['bdf'] = e.get_error_info()
                if not self.all_arguments:
                    raise e

            bus_output_info.update(bus_info)
            static_dict['bus'] = bus_output_info
        if args.vbios:
            try:
                vbios_info = amdsmi_interface.amdsmi_get_gpu_vbios_info(args.gpu)
                if self.logger.is_gpuvsmi_compatibility():
                    vbios_info['version'] = vbios_info.pop('version')
                    vbios_info['build_date'] = vbios_info.pop('build_date')
                    vbios_info['part_number'] = vbios_info.pop('part_number')

                static_dict['vbios'] = vbios_info
            except amdsmi_exception.AmdSmiLibraryException as e:
                static_dict['vbios'] = e.get_error_info()
                if not self.all_arguments:
                    raise e
        if self.helpers.is_linux() and self.helpers.is_baremetal():
            if args.board:
                try:
                    board_info = amdsmi_interface.amdsmi_get_gpu_board_info(args.gpu)
                    board_info['serial_number'] = hex(board_info['serial_number'])
                    board_info['model_number'] = board_info['model_number'].strip()
                    board_info['product_name'] = board_info['product_name'].strip()
                    board_info['manufacturer_name'] = board_info['manufacturer_name'].strip()
                    board_info.pop('product_serial')
                    board_info.pop('manufacturer_name')

                    static_dict['board'] = board_info
                except amdsmi_exception.AmdSmiLibraryException as e:
                    static_dict['board'] = e.get_error_info()
                    if not self.all_arguments:
                        raise e
            if args.limit:
                # Power limits
                try:
                    power_limit_error = False
                    power_info = amdsmi_interface.amdsmi_get_power_cap_info(args.gpu)
                    max_power_limit = power_info['max_power_cap']
                    current_power_limit = power_info['power_cap']
                except amdsmi_exception.AmdSmiLibraryException as e:
                    power_limit_error = True
                    max_power_limit = e.get_error_info()
                    current_power_limit = e.get_error_info()
                    if not self.all_arguments:
                        raise e

                # Edge temperature limits
                try:
                    slowdown_temp_edge_limit_error = False
                    slowdown_temp_edge_limit = amdsmi_interface.amdsmi_get_temp_metric(args.gpu,
                        amdsmi_interface.AmdSmiTemperatureType.EDGE, amdsmi_interface.AmdSmiTemperatureMetric.CRITICAL)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    slowdown_temp_edge_limit_error = True
                    slowdown_temp_edge_limit = e.get_error_info()
                    if not self.all_arguments:
                        raise e

                if slowdown_temp_edge_limit == 0:
                    slowdown_temp_edge_limit_error = True
                    slowdown_temp_edge_limit = 'N/A'

                try:
                    shutdown_temp_edge_limit_error = False
                    shutdown_temp_edge_limit = amdsmi_interface.amdsmi_get_temp_metric(args.gpu,
                        amdsmi_interface.AmdSmiTemperatureType.EDGE, amdsmi_interface.AmdSmiTemperatureMetric.EMERGENCY)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    shutdown_temp_edge_limit_error = True
                    shutdown_temp_edge_limit = e.get_error_info()
                    if not self.all_arguments:
                        raise e

                if shutdown_temp_edge_limit == 0:
                    shutdown_temp_edge_limit_error = True
                    shutdown_temp_edge_limit = 'N/A'

                # Hotspot/Junction temperature limits
                try:
                    slowdown_temp_hotspot_limit_error = False
                    slowdown_temp_hotspot_limit = amdsmi_interface.amdsmi_get_temp_metric(args.gpu,
                        amdsmi_interface.AmdSmiTemperatureType.HOTSPOT, amdsmi_interface.AmdSmiTemperatureMetric.CRITICAL)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    slowdown_temp_hotspot_limit_error = True
                    slowdown_temp_hotspot_limit = e.get_error_info()
                    if not self.all_arguments:
                        raise e

                try:
                    shutdown_temp_hotspot_limit_error = False
                    shutdown_temp_hotspot_limit = amdsmi_interface.amdsmi_get_temp_metric(args.gpu,
                        amdsmi_interface.AmdSmiTemperatureType.HOTSPOT, amdsmi_interface.AmdSmiTemperatureMetric.EMERGENCY)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    shutdown_temp_hotspot_limit_error = True
                    shutdown_temp_hotspot_limit = e.get_error_info()
                    if not self.all_arguments:
                        raise e

                # VRAM temperature limits
                try:
                    slowdown_temp_vram_limit_error = False
                    slowdown_temp_vram_limit = amdsmi_interface.amdsmi_get_temp_metric(args.gpu,
                        amdsmi_interface.AmdSmiTemperatureType.VRAM, amdsmi_interface.AmdSmiTemperatureMetric.CRITICAL)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    slowdown_temp_vram_limit_error = True
                    slowdown_temp_vram_limit = e.get_error_info()
                    if not self.all_arguments:
                        raise e

                try:
                    shutdown_temp_vram_limit_error = False
                    shutdown_temp_vram_limit = amdsmi_interface.amdsmi_get_temp_metric(args.gpu,
                        amdsmi_interface.AmdSmiTemperatureType.VRAM, amdsmi_interface.AmdSmiTemperatureMetric.EMERGENCY)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    shutdown_temp_vram_limit_error = True
                    shutdown_temp_vram_limit = e.get_error_info()
                    if not self.all_arguments:
                        raise e

                if self.logger.is_human_readable_format():
                    unit = 'W'
                    if not power_limit_error:
                        max_power_limit = f"{max_power_limit} {unit}"
                        current_power_limit = f"{current_power_limit} {unit}"

                    unit = '\N{DEGREE SIGN}C'
                    if not slowdown_temp_edge_limit_error:
                        slowdown_temp_edge_limit = f"{slowdown_temp_edge_limit} {unit}"
                    if not slowdown_temp_hotspot_limit_error:
                        slowdown_temp_hotspot_limit = f"{slowdown_temp_hotspot_limit} {unit}"
                    if not slowdown_temp_vram_limit_error:
                        slowdown_temp_vram_limit = f"{slowdown_temp_vram_limit} {unit}"
                    if not shutdown_temp_edge_limit_error:
                        shutdown_temp_edge_limit = f"{shutdown_temp_edge_limit} {unit}"
                    if not shutdown_temp_hotspot_limit_error:
                        shutdown_temp_hotspot_limit = f"{shutdown_temp_hotspot_limit} {unit}"
                    if not shutdown_temp_vram_limit_error:
                        shutdown_temp_vram_limit = f"{shutdown_temp_vram_limit} {unit}"

                limit_info = {}
                # Power limits
                limit_info['max_power'] = max_power_limit
                limit_info['current_power'] = current_power_limit

                # Shutdown limits
                limit_info['slowdown_edge_temperature'] = slowdown_temp_edge_limit
                limit_info['slowdown_hotspot_temperature'] = slowdown_temp_hotspot_limit
                limit_info['slowdown_vram_temperature'] = slowdown_temp_vram_limit
                limit_info['shutdown_edge_temperature'] = shutdown_temp_edge_limit
                limit_info['shutdown_hotspot_temperature'] = shutdown_temp_hotspot_limit
                limit_info['shutdown_vram_temperature'] = shutdown_temp_vram_limit
                static_dict['limit'] = limit_info
        if args.driver:
            try:
                driver_info = {}
                driver_info = amdsmi_interface.amdsmi_get_gpu_driver_info(args.gpu)

                static_dict['driver'] = driver_info
            except amdsmi_exception.AmdSmiLibraryException as e:
                static_dict['driver'] = e.get_error_info()
                if not self.all_arguments:
                    raise e
        if self.helpers.is_linux() and self.helpers.is_baremetal():
            if args.ras:
                try:
                    static_dict['ras'] = amdsmi_interface.amdsmi_get_gpu_ras_block_features_enabled(args.gpu)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NOT_SUPPORTED:
                        static_dict['ras'] = 'N/A'
                    else:
                        static_dict['ras'] = e.get_error_info()
                    if not self.all_arguments:
                        raise e
        if (self.helpers.is_linux() and self.helpers.is_baremetal()):
            if args.numa:
                try:
                    numa_node_number = amdsmi_interface.amdsmi_topo_get_numa_node_number(args.gpu)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    numa_node_number = e.get_error_info()
                    if not self.all_arguments:
                        raise e

                try:
                    numa_affinity = amdsmi_interface.amdsmi_get_gpu_topo_numa_affinity(args.gpu)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    numa_affinity = e.get_error_info()
                    if not self.all_arguments:
                        raise e

                static_dict['numa'] = {'node' : numa_node_number,
                                        'affinity' : numa_affinity}

        multiple_devices_csv_override = False
        # Convert and store output by pid for csv format
        if self.logger.is_csv_format():
            # expand if ras blocks are populated
            if self.helpers.is_linux() and self.helpers.is_baremetal() and args.ras:
                if isinstance(static_dict['ras'], list):
                    ras_dicts = static_dict.pop('ras')
                    multiple_devices_csv_override = True
                    for ras_dict in ras_dicts:
                        for key, value in ras_dict.items():
                            self.logger.store_output(args.gpu, key, value)
                        self.logger.store_output(args.gpu, 'values', static_dict)
                        self.logger.store_multiple_device_output()
                else:
                    # Store values if ras has an error
                    self.logger.store_output(args.gpu, 'values', static_dict)
                if self.helpers.is_linux() and self.helpers.is_virtual_os():
                    self.logger.store_output(args.gpu, 'values', static_dict)
            else:
                self.logger.store_output(args.gpu, 'values', static_dict)
        else:
            # Store values in logger.output
            self.logger.store_output(args.gpu, 'values', static_dict)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output(multiple_device_enabled=multiple_devices_csv_override)


    def firmware(self, args, multiple_devices=False, gpu=None, fw_list=True):
        """ Get Firmware information for target gpu

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            gpu (device_handle, optional): device_handle for target device. Defaults to None.
            fw_list (bool, optional): True to get list of all firmware information
        Raises:
            IndexError: Index error if gpu list is empty

        Returns:
            None: Print output via AMDSMILogger to destination
        """
        if gpu:
            args.gpu = gpu
        if fw_list: # Currently a compatiblity option of gpuv-smi
            args.fw_list = fw_list

        # Handle No GPU passed
        if args.gpu == None:
            args.gpu = self.device_handles

        # Handle multiple GPUs
        handled_multiple_gpus, device_handle = self.helpers.handle_gpus(args, self.logger, self.firmware)
        if handled_multiple_gpus:
            return # This function is recursive

        args.gpu = device_handle

        fw_list = {}
        if args.fw_list:
            try:
                fw_info = amdsmi_interface.amdsmi_get_fw_info(args.gpu)

                for fw_index, fw_entry in enumerate(fw_info['fw_list']):
                    # Change fw_name to fw_id
                    fw_entry['fw_id'] = fw_entry.pop('fw_name').name.strip('FW_ID_')
                    fw_entry['fw_version'] = fw_entry.pop('fw_version')
                    firmware_identifier = 'FW'

                    if self.logger.is_gpuvsmi_compatibility():
                        firmware_identifier = 'UCODE'
                        fw_entry['name'] = fw_entry.pop('fw_id')
                        fw_entry['version'] = fw_entry.pop('fw_version')

                    # Add custom human readable formatting
                    if self.logger.is_human_readable_format():
                        fw_info['fw_list'][fw_index] = {f'{firmware_identifier} {fw_index}': fw_entry}
                    else:
                        fw_info['fw_list'][fw_index] = fw_entry

                if self.logger.is_gpuvsmi_compatibility():
                    fw_info['ucode_list'] = fw_info.pop('fw_list')

                fw_list.update(fw_info)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise e

        multiple_devices_csv_override = False
        # Convert and store output by pid for csv format
        if self.logger.is_csv_format():
            if self.logger.is_gpuvsmi_compatibility():
                fw_key = 'ucode_list'
            else:
                fw_key = 'fw_list'

            for fw_info_dict in fw_list[fw_key]:
                for key, value in fw_info_dict.items():
                    multiple_devices_csv_override = True
                    self.logger.store_output(args.gpu, key, value)
                self.logger.store_multiple_device_output()
        else:
            # Store values in logger.output
            self.logger.store_output(args.gpu, 'values', fw_list)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output(multiple_device_enabled=multiple_devices_csv_override)


    def bad_pages(self, args, multiple_devices=False, gpu=None, retired=None, pending=None, un_res=None):
        """ Get bad pages information for target gpu

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            gpu (device_handle, optional): device_handle for target device. Defaults to None.
            retired (bool, optional) - Value override for args.retired
            pending (bool, optional) - Value override for args.pending/
            un_res (bool, optional) - Value override for args.un_res

        Raises:
            IndexError: Index error if gpu list is empty

        Returns:
            None: Print output via AMDSMILogger to destination
        """
        # Set args.* to passed in arguments
        if gpu:
            args.gpu = gpu
        if retired:
            args.retired = retired
        if pending:
            args.pending = pending
        if un_res:
            args.un_res = un_res

        # Handle No GPU passed
        if args.gpu == None:
            args.gpu = self.device_handles

        # Handle multiple GPUs
        handled_multiple_gpus, device_handle = self.helpers.handle_gpus(args, self.logger, self.bad_pages)
        if handled_multiple_gpus:
            return # This function is recursive

        args.gpu = device_handle

        # If all arguments are False, the print all bad_page information
        if not any([args.retired, args.pending, args.un_res]):
            args.retired = args.pending = args.un_res = True

        values_dict = {}
        bad_page_err_output = ''

        try:
            bad_page_info = amdsmi_interface.amdsmi_get_gpu_bad_page_info(args.gpu)
            bad_page_error = False
        except amdsmi_exception.AmdSmiLibraryException as e:
            bad_page_err_output = e.get_error_info()
            bad_page_error = True
            raise e

        if bad_page_info == "No bad pages found.":
            bad_page_error = True
            bad_page_err_output = bad_page_info

        if args.retired:
            if bad_page_error:
                bad_page_info_output = bad_page_err_output
            else:
                bad_page_info_output = []
                for bad_page in bad_page_info:
                    if bad_page["status"] == amdsmi_interface.AmdSmiMemoryPageStatus.RESERVED:
                        bad_page_info_entry = {}
                        bad_page_info_entry["page_address"] = bad_page["page_address"]
                        bad_page_info_entry["page_size"] = bad_page["page_size"]
                        bad_page_info_entry["status"] = bad_page["status"].name

                        bad_page_info_output.append(bad_page_info_entry)
                # Remove brackets if there is only one value
                if len(bad_page_info_output) == 1:
                    bad_page_info_output = bad_page_info_output[0]

            values_dict['retired'] = bad_page_info_output

        if args.pending:
            if bad_page_error:
                bad_page_info_output = bad_page_err_output
            else:
                bad_page_info_output = []
                for bad_page in bad_page_info:
                    if bad_page["status"] == amdsmi_interface.AmdSmiMemoryPageStatus.PENDING:
                        bad_page_info_entry = {}
                        bad_page_info_entry["page_address"] = bad_page["page_address"]
                        bad_page_info_entry["page_size"] = bad_page["page_size"]
                        bad_page_info_entry["status"] = bad_page["status"].name

                        bad_page_info_output.append(bad_page_info_entry)
                # Remove brackets if there is only one value
                if len(bad_page_info_output) == 1:
                    bad_page_info_output = bad_page_info_output[0]

            values_dict['pending'] = bad_page_info_output

        if args.un_res:
            if bad_page_error:
                bad_page_info_output = bad_page_err_output
            else:
                bad_page_info_output = []
                for bad_page in bad_page_info:
                    if bad_page["status"] == amdsmi_interface.AmdSmiMemoryPageStatus.UNRESERVABLE:
                        bad_page_info_entry = {}
                        bad_page_info_entry["page_address"] = bad_page["page_address"]
                        bad_page_info_entry["page_size"] = bad_page["page_size"]
                        bad_page_info_entry["status"] = bad_page["status"].name

                        bad_page_info_output.append(bad_page_info_entry)
                # Remove brackets if there is only one value
                if len(bad_page_info_output) == 1:
                    bad_page_info_output = bad_page_info_output[0]

            values_dict['un_res'] = bad_page_info_output

        # Store values in logger.output
        self.logger.store_output(args.gpu, 'values', values_dict)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output()


    def metric(self, args, multiple_devices=False, watching_output=False, gpu=None,
                usage=None, watch=None, watch_time=None, iterations=None, fb_usage=None, power=None,
                clock=None, temperature=None, ecc=None, ecc_block=None, pcie=None,
                fan=None, voltage_curve=None, overdrive=None, perf_level=None,
                replay_count=None, xgmi_err=None, energy=None, mem_usage=None):
        """Get Metric information for target gpu

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            watching_output (bool, optional): True if watch option has been set. Defaults to False.
            gpu (device_handle, optional): device_handle for target device. Defaults to None.
            usage (bool, optional): Value override for args.usage. Defaults to None.
            watch (Positive int, optional): Value override for args.watch. Defaults to None.
            watch_time (Positive int, optional): Value override for args.watch_time. Defaults to None.
            iterations (Positive int, optional): Value override for args.iterations. Defaults to None.
            fb_usage (bool, optional): Value override for args.fb_usage. Defaults to None.
            power (bool, optional): Value override for args.power. Defaults to None.
            clock (bool, optional): Value override for args.clock. Defaults to None.
            temperature (bool, optional): Value override for args.temperature. Defaults to None.
            ecc (bool, optional): Value override for args.ecc. Defaults to None.
            ecc_block (bool, optional): Value override for args.ecc. Defaults to None.
            pcie (bool, optional): Value override for args.pcie. Defaults to None.
            fan (bool, optional): Value override for args.fan. Defaults to None.
            voltage_curve (bool, optional): Value override for args.voltage_curve. Defaults to None.
            overdrive (bool, optional): Value override for args.overdrive. Defaults to None.
            perf_level (bool, optional): Value override for args.perf_level. Defaults to None.
            replay_count (bool, optional): Value override for args.replay_count. Defaults to None.
            xgmi_err (bool, optional): Value override for args.xgmi_err. Defaults to None.
            energy (bool, optional): Value override for args.energy. Defaults to None.
            mem_usage (bool, optional): Value override for args.mem_usage. Defaults to None.

        Raises:
            IndexError: Index error if gpu list is empty

        Returns:
            None: Print output via AMDSMILogger to destination
        """
        # Set args.* to passed in arguments
        if gpu:
            args.gpu = gpu
        if watch:
            args.watch = watch
        if watch_time:
            args.watch_time = watch_time
        if iterations:
            args.iterations = iterations
        if fb_usage:
            args.fb_usage = fb_usage
        if mem_usage:
            args.mem_usage = mem_usage

        if not self.helpers.is_virtual_os():
            if replay_count:
               args.replay_count = replay_count

        if self.helpers.is_linux() and self.helpers.is_baremetal():
            if usage:
                args.usage = usage
            if power:
                args.power = power
            if clock:
                args.clock = clock
            if temperature:
                args.temperature = temperature
            if ecc:
                args.ecc = ecc
            if ecc_block:
                args.ecc_block = ecc_block
            if pcie:
                args.pcie = pcie
            if fan:
                args.fan = fan
            if voltage_curve:
                args.voltage_curve = voltage_curve
            if overdrive:
                args.overdrive = overdrive
            if perf_level:
                args.perf_level = perf_level
            if xgmi_err:
                args.xgmi_err = xgmi_err
            if energy:
                args.energy = energy

        # Handle No GPU passed
        if args.gpu == None:
            args.gpu = self.device_handles

        # Handle watch logic, will only enter this block once
        if args.watch:
            self.helpers.handle_watch(args=args, subcommand=self.metric, logger=self.logger)
            return

        # Handle multiple GPUs
        if isinstance(args.gpu, list):
            if len(args.gpu) > 1:
                # Deepcopy gpus as recursion will destroy the gpu list
                stored_gpus = []
                for gpu in args.gpu:
                    stored_gpus.append(gpu)

                # Store output from multiple devices
                for device_handle in args.gpu:
                    self.metric(args, multiple_devices=True, watching_output=watching_output, gpu=device_handle)

                # Reload original gpus
                args.gpu = stored_gpus

                # Print multiple device output
                self.logger.print_output(multiple_device_enabled=True, watching_output=watching_output)

                # Add output to total watch output and clear multiple device output
                if watching_output:
                    self.logger.store_watch_output(multiple_device_enabled=True)

                    # Flush the watching output
                    self.logger.print_output(multiple_device_enabled=True, watching_output=watching_output)

                return
            elif len(args.gpu) == 1:
                args.gpu = args.gpu[0]
            else:
                raise IndexError("args.gpu should not be an empty list")

        # Check if any of the options have been set, if not then set them all to true
        if self.helpers.is_linux() and self.helpers.is_virtual_os():
            if not any([args.fb_usage, args.mem_usage]):
                args.fb_usage = args.mem_usage = self.all_arguments = True

        if self.helpers.is_linux() and self.helpers.is_baremetal():
            if not any([args.usage, args.fb_usage, args.power, args.clock, args.temperature,
                        args.ecc,  args.ecc_block, args.pcie, args.fan, args.voltage_curve,
                        args.overdrive, args.perf_level, args.replay_count, args.xgmi_err,
                        args.energy, args.mem_usage]):
                args.usage = args.fb_usage = args.power = args.clock = args.temperature = \
                    args.ecc = args.ecc_block = args.pcie = args.fan = args.voltage_curve = \
                    args.overdrive = args.perf_level = args.replay_count = args.xgmi_err = \
                    args.energy = args.mem_usage = self.all_arguments = True

        # Add timestamp and store values for specified arguments
        values_dict = {}
        if self.helpers.is_linux() and self.helpers.is_baremetal():
            if args.usage:
                try:
                    engine_usage = amdsmi_interface.amdsmi_get_gpu_activity(args.gpu)

                    if self.logger.is_gpuvsmi_compatibility():
                        engine_usage['gfx_usage'] = engine_usage.pop('gfx_activity')
                        engine_usage['mem_usage'] = engine_usage.pop('umc_activity')
                        engine_usage['mm_usage_list'] = engine_usage.pop('mm_activity')

                    if self.logger.is_human_readable_format():
                        unit = '%'
                        for usage_name, usage_value in engine_usage.items():
                            engine_usage[usage_name] = f"{usage_value} {unit}"

                    values_dict['usage'] = engine_usage
                except amdsmi_exception.AmdSmiLibraryException as e:
                    values_dict['usage'] = e.get_error_info()
                    if not self.all_arguments:
                        raise e

        if args.fb_usage:
            try:
                vram_usage = amdsmi_interface.amdsmi_get_gpu_vram_usage(args.gpu)

                if self.logger.is_gpuvsmi_compatibility():
                    vram_usage['fb_total'] = vram_usage.pop('vram_total')
                    vram_usage['fb_used'] = vram_usage.pop('vram_used')

                if self.logger.is_human_readable_format():
                    unit = 'MB'
                    for vram_name, vram_value in vram_usage.items():
                        vram_usage[vram_name] = f"{vram_value} {unit}"

                values_dict['fb_usage'] = vram_usage
            except amdsmi_exception.AmdSmiLibraryException as e:
                values_dict['fb_usage'] = e.get_error_info()
                if not self.all_arguments:
                    raise e

        if self.helpers.is_linux() and self.helpers.is_baremetal():
            if args.power:
                power_dict = {}
                try:
                    power_measure = amdsmi_interface.amdsmi_get_power_info(args.gpu)
                    power_dict = {'average_socket_power': power_measure['average_socket_power'],
                                    'gfx_voltage': power_measure['gfx_voltage'],
                                    'soc_voltage': amdsmi_exception.AmdSmiLibraryException(amdsmi_exception.AmdSmiRetCode.STATUS_NOT_YET_IMPLEMENTED).err_info,
                                    'mem_voltage': amdsmi_exception.AmdSmiLibraryException(amdsmi_exception.AmdSmiRetCode.STATUS_NOT_YET_IMPLEMENTED).err_info,
                                    'power_limit': power_measure['power_limit']}

                    if self.logger.is_human_readable_format():
                        power_dict['average_socket_power'] = f"{power_dict['average_socket_power']} W"
                        power_dict['gfx_voltage'] = f"{power_dict['gfx_voltage']} mV"
                        power_dict['soc_voltage'] = amdsmi_exception.AmdSmiLibraryException(amdsmi_exception.AmdSmiRetCode.STATUS_NOT_YET_IMPLEMENTED).err_info
                        power_dict['mem_voltage'] = amdsmi_exception.AmdSmiLibraryException(amdsmi_exception.AmdSmiRetCode.STATUS_NOT_YET_IMPLEMENTED).err_info
                        power_dict['power_limit'] = f"{power_dict['power_limit']} W"

                except amdsmi_exception.AmdSmiLibraryException as e:
                    power_dict = {'average_socket_power': e.get_error_info(),
                                    'gfx_voltage': e.get_error_info(),
                                    'soc_voltage': e.get_error_info(),
                                    'mem_voltage': e.get_error_info(),
                                    'power_limit': e.get_error_info()}

                    if not self.all_arguments:
                        raise e

                if self.logger.is_gpuvsmi_compatibility():
                    power_dict['current_power'] = power_dict.pop('average_socket_power')
                    power_dict['current_voltage'] = power_dict.pop('gfx_voltage')
                    power_dict['current_soc_voltage'] = power_dict.pop('soc_voltage')
                    power_dict['current_mem_voltage'] = power_dict.pop('mem_voltage')

                    try:
                        power_dict['current_fan_rpm'] = amdsmi_interface.amdsmi_get_gpu_fan_rpms(args.gpu, 0)
                        if self.logger.is_human_readable_format():
                            power_dict['current_fan_rpm'] = f"{power_dict['current_fan_rpm']} RPM"
                    except amdsmi_exception.AmdSmiLibraryException as e:
                        power_dict['current_fan_rpm'] = e.get_error_info()
                        if not self.all_arguments:
                            raise e

                values_dict['power'] = power_dict
            if args.clock:
                try:
                    clock_gfx = amdsmi_interface.amdsmi_get_clock_info(args.gpu, amdsmi_interface.AmdSmiClkType.GFX)
                    clock_mem = amdsmi_interface.amdsmi_get_clock_info(args.gpu, amdsmi_interface.AmdSmiClkType.MEM)

                    clocks = {'gfx': clock_gfx,
                            'mem': clock_mem}

                    if self.logger.is_human_readable_format():
                        unit = 'MHz'
                        for clock_target, clock_metric_values in clocks.items():
                            for clock_type, clock_value in clock_metric_values.items():
                                clocks[clock_target][clock_type] = f"{clock_value} {unit}"

                    values_dict['clock'] = clocks
                except amdsmi_exception.AmdSmiLibraryException as e:
                    values_dict['clock'] = e.get_error_info()
                    if not self.all_arguments:
                        raise e
            if args.temperature:
                try:
                    temperature_edge_current = amdsmi_interface.amdsmi_get_temp_metric(
                        args.gpu, amdsmi_interface.AmdSmiTemperatureType.EDGE, amdsmi_interface.AmdSmiTemperatureMetric.CURRENT)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    temperature_edge_current = e.get_error_info()

                try:
                    temperature_edge_limit = amdsmi_interface.amdsmi_get_temp_metric(
                        args.gpu, amdsmi_interface.AmdSmiTemperatureType.EDGE, amdsmi_interface.AmdSmiTemperatureMetric.CRITICAL)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    temperature_edge_limit = e.get_error_info()

                try:
                    temperature_hotspot_current = amdsmi_interface.amdsmi_get_temp_metric(
                        args.gpu, amdsmi_interface.AmdSmiTemperatureType.HOTSPOT, amdsmi_interface.AmdSmiTemperatureMetric.CURRENT)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    temperature_hotspot_current = e.get_error_info()

                try:
                    temperature_vram_current = amdsmi_interface.amdsmi_get_temp_metric(
                        args.gpu, amdsmi_interface.AmdSmiTemperatureType.VRAM, amdsmi_interface.AmdSmiTemperatureMetric.CURRENT)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    temperature_vram_current = e.get_error_info()

                # If edge limit is reporting 0 then set the current edge temp to N/A
                if temperature_edge_limit == 0:
                    temperature_edge_current = 'N/A'

                temperatures = {'edge': temperature_edge_current,
                                'hotspot': temperature_hotspot_current,
                                'mem': temperature_vram_current}

                if self.logger.is_gpuvsmi_compatibility():
                    temperatures = {'edge_temperature': temperature_edge_current,
                                    'hotspot_temperature': temperature_hotspot_current,
                                    'mem_temperature': temperature_vram_current}

                if self.logger.is_human_readable_format():
                    unit = '\N{DEGREE SIGN}C'
                    if self.logger.is_gpuvsmi_compatibility():
                        unit = 'C'
                    for temperature_key, temperature_value in temperatures.items():
                        if 'AMD_SMI_STATUS' not in str(temperature_value):
                            temperatures[temperature_key] = f"{temperature_value} {unit}"

                values_dict['temperature'] = temperatures

            if args.ecc:
                ecc_count = {}
                try:
                    ecc_count = amdsmi_interface.amdsmi_get_gpu_total_ecc_count(args.gpu)
                    ecc_count['correctable'] = ecc_count.pop('correctable_count')
                    ecc_count['uncorrectable'] = ecc_count.pop('uncorrectable_count')

                    values_dict['ecc'] = ecc_count
                except amdsmi_exception.AmdSmiLibraryException as e:
                    if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NOT_SUPPORTED:
                        ecc_count['correctable'] = 'N/A'
                        ecc_count['uncorrectable'] = 'N/A'
                        values_dict['ecc'] = ecc_count
                    else:
                        values_dict['ecc'] = e.get_error_info()
                    if not self.all_arguments:
                        raise e
            if args.ecc_block:
                ecc_dict = {}
                try:
                    ras_states = amdsmi_interface.amdsmi_get_gpu_ras_block_features_enabled(args.gpu)
                    for state in ras_states:
                        if state['status'] == amdsmi_interface.AmdSmiRasErrState.ENABLED.name:
                            gpu_block = amdsmi_interface.AmdSmiGpuBlock[state['block']]
                            try:
                                ecc_count = amdsmi_interface.amdsmi_get_gpu_ecc_count(args.gpu, gpu_block)
                                ecc_dict[state['block']] = {'correctable' : ecc_count['correctable_count'],
                                                            'uncorrectable': ecc_count['uncorrectable_count']}
                            except amdsmi_exception.AmdSmiLibraryException as e:
                                ecc_count = e.get_error_info()
                                if self.logger.is_gpuvsmi_compatibility():
                                    ecc_count = "N/A"

                                ecc_dict[state['block']] = {'correctable' : ecc_count,
                                                            'uncorrectable': ecc_count}
                    values_dict['ecc_block'] = ecc_dict
                except amdsmi_exception.AmdSmiLibraryException as e:
                    values_dict['ecc_block'] = e.get_error_info()
                    if not self.all_arguments:
                        raise e
            if args.pcie:
                try:
                    pcie_link_status = amdsmi_interface.amdsmi_get_pcie_link_status(args.gpu)

                    if pcie_link_status['pcie_speed'] % 1000 != 0:
                        pcie_speed_GTs_value = round(pcie_link_status['pcie_speed'] / 1000, 1)
                    else:
                        pcie_speed_GTs_value = round(pcie_link_status['pcie_speed'] / 1000)

                    pcie_link_status['pcie_speed'] = pcie_speed_GTs_value
                    # The interface version should not be displayed as it is based on the current speed
                    del pcie_link_status['pcie_interface_version']

                    if self.logger.is_human_readable_format():
                        unit = 'GT/s'
                        pcie_link_status['pcie_speed'] = f"{pcie_link_status['pcie_speed']} {unit}"
                        pcie_link_status['current_width'] = pcie_link_status.pop('pcie_lanes')
                        pcie_link_status['current_speed'] = pcie_link_status.pop('pcie_speed')

                    values_dict['pcie'] = pcie_link_status
                except amdsmi_exception.AmdSmiLibraryException as e:
                    values_dict['pcie'] = e.get_error_info()
                    if not self.all_arguments:
                        raise e
            if args.fan:
                try:
                    fan_speed = amdsmi_interface.amdsmi_get_gpu_fan_speed(args.gpu, 0)
                    fan_speed_error = False
                except amdsmi_exception.AmdSmiLibraryException as e:
                    fan_speed = e.get_error_info()
                    fan_speed_error = True

                try:
                    fan_max = amdsmi_interface.amdsmi_get_gpu_fan_speed_max(args.gpu, 0)
                    if not fan_speed_error and fan_max > 0:
                        fan_percent = round((float(fan_speed) / float(fan_max)) * 100, 2)
                        if self.logger.is_human_readable_format():
                            unit = '%'
                            fan_percent = f"{fan_percent} {unit}"
                    else:
                        fan_percent = 'Unable to detect fan speed'
                except amdsmi_exception.AmdSmiLibraryException as e:
                    fan_max = e.get_error_info()
                    fan_percent = 'Unable to detect fan speed'

                try:
                    fan_rpm = amdsmi_interface.amdsmi_get_gpu_fan_rpms(args.gpu, 0)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    fan_rpm = e.get_error_info()

                values_dict['fan'] = {'speed': fan_speed,
                                        'max' : fan_max,
                                        'rpm' : fan_rpm,
                                        'usage' : fan_percent}
            if args.voltage_curve:
                try:
                    od_volt = amdsmi_interface.amdsmi_get_gpu_od_volt_info(args.gpu)

                    voltage_point_dict = {}

                    for point in range(3):
                        if isinstance(od_volt, dict):
                            frequency = int(od_volt["curve.vc_points"][point].frequency / 1000000)
                            voltage = int(od_volt["curve.vc_points"][point].voltage)
                        else:
                            frequency = 0
                            voltage = 0
                        voltage_point_dict[f'voltage_point_{point}'] = f"{frequency} Mhz {voltage} mV"

                    values_dict['voltage_curve'] = voltage_point_dict
                except amdsmi_exception.AmdSmiLibraryException as e:
                    values_dict['voltage_curve'] = e.get_error_info()
                    if not self.all_arguments:
                        raise e
            if args.overdrive:
                try:
                    overdrive_level = amdsmi_interface.amdsmi_get_gpu_overdrive_level(args.gpu)

                    if self.logger.is_human_readable_format():
                        unit = '%'
                        overdrive_level = f"{overdrive_level} {unit}"

                    values_dict['overdrive'] = overdrive_level
                except amdsmi_exception.AmdSmiLibraryException as e:
                    values_dict['overdrive'] = e.get_error_info()
                    if not self.all_arguments:
                        raise e
            if args.perf_level:
                try:
                    perf_level = amdsmi_interface.amdsmi_get_gpu_perf_level(args.gpu)
                    values_dict['perf_level'] = perf_level
                except amdsmi_exception.AmdSmiLibraryException as e:
                    values_dict['perf_level'] = e.get_error_info()
                    if not self.all_arguments:
                        raise e

        if not self.helpers.is_virtual_os():
            if args.replay_count:
                try:
                    pci_replay_counter = amdsmi_interface.amdsmi_get_gpu_pci_replay_counter(args.gpu)
                    values_dict['replay_count'] = pci_replay_counter
                except amdsmi_exception.AmdSmiLibraryException as e:
                    values_dict['replay_count'] = e.get_error_info()
                    if not self.all_arguments:
                        raise e

        if self.helpers.is_linux() and self.helpers.is_baremetal():
            if args.xgmi_err:
                try:
                    values_dict['xgmi_err'] = amdsmi_interface.amdsmi_gpu_xgmi_error_status(args.gpu)
                except amdsmi_interface.AmdSmiLibraryException as e:
                    if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NOT_SUPPORTED:
                        values_dict['xgmi_err'] = 'N/A'
                    elif not self.all_arguments:
                        raise e
            if args.energy:
                pass

        if args.mem_usage:
            memory_total = {}
            try:
                memory_total_vram = amdsmi_interface.amdsmi_get_gpu_memory_total(args.gpu, amdsmi_interface.AmdSmiMemoryType.VRAM)
                memory_total_vis_vram = amdsmi_interface.amdsmi_get_gpu_memory_total(args.gpu, amdsmi_interface.AmdSmiMemoryType.VIS_VRAM)
                memory_total_gtt = amdsmi_interface.amdsmi_get_gpu_memory_total(args.gpu, amdsmi_interface.AmdSmiMemoryType.GTT)

                # Convert mem_usage to megabytes
                memory_total['vram'] = memory_total_vram // (1024*1024)
                memory_total['vis_vram'] = memory_total_vis_vram // (1024*1024)
                memory_total['gtt'] = memory_total_gtt // (1024*1024)

                if self.logger.is_human_readable_format():
                    unit = 'MB'
                    energy = f"{energy} {unit}"
                    memory_total['vram'] = f"{memory_total['vram']} {unit}"
                    memory_total['vis_vram'] = f"{memory_total['vis_vram']} {unit}"
                    memory_total['gtt'] = f"{memory_total['gtt']} {unit}"

            except amdsmi_exception.AmdSmiLibraryException as e:
                memory_total['vram'] = e.get_error_info()
                memory_total['vis_vram'] = e.get_error_info()
                memory_total['gtt'] = e.get_error_info()
                if not self.all_arguments:
                    raise e

            try:
                total_used_vram = amdsmi_interface.amdsmi_get_gpu_memory_usage(args.gpu, amdsmi_interface.AmdSmiMemoryType.VRAM)
                total_used_vis_vram = amdsmi_interface.amdsmi_get_gpu_memory_usage(args.gpu, amdsmi_interface.AmdSmiMemoryType.VIS_VRAM)
                total_used_gtt = amdsmi_interface.amdsmi_get_gpu_memory_usage(args.gpu, amdsmi_interface.AmdSmiMemoryType.GTT)

                # Convert mem_usage to megabytes
                memory_total['used_vram'] = total_used_vram // (1024*1024)
                memory_total['used_vis_vram'] = total_used_vis_vram // (1024*1024)
                memory_total['used_gtt'] = total_used_gtt // (1024*1024)

                if self.logger.is_human_readable_format():
                    memory_total['used_vram'] = f"{memory_total['used_vram']} {unit}"
                    memory_total['used_vis_vram'] = f"{memory_total['used_vis_vram']} {unit}"
                    memory_total['used_gtt'] = f"{memory_total['used_gtt']} {unit}"

            except amdsmi_exception.AmdSmiLibraryException as e:
                memory_total['used_vram'] = e.get_error_info()
                memory_total['used_vis_vram'] = e.get_error_info()
                memory_total['used_gtt'] = e.get_error_info()
                if not self.all_arguments:
                    raise e

            values_dict['mem_usage'] = memory_total

        # Store timestamp first if watching_output is enabled
        if watching_output:
            self.logger.store_output(args.gpu, 'timestamp', int(time.time()))
        self.logger.store_output(args.gpu, 'values', values_dict)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output(watching_output=watching_output)

        if watching_output: # End of single gpu add to watch_output
            self.logger.store_watch_output(multiple_device_enabled=False)


    def process(self, args, multiple_devices=False, watching_output=False,
                gpu=None, general=None, engine=None, pid=None, name=None,
                watch=None, watch_time=None, iterations=None):
        """Get Process Information from the target GPU

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            watching_output (bool, optional): True if watch option has been set. Defaults to False.
            gpu (device_handle, optional): device_handle for target device. Defaults to None.
            general (bool, optional): Value override for args.general. Defaults to None.
            engine (bool, optional): Value override for args.engine. Defaults to None.
            pid (Positive int, optional): Value override for args.pid. Defaults to None.
            name (str, optional): Value override for args.name. Defaults to None.
            watch (Positive int, optional): Value override for args.watch. Defaults to None.
            watch_time (Positive int, optional): Value override for args.watch_time. Defaults to None.
            iterations (Positive int, optional): Value override for args.iterations. Defaults to None.

        Raises:
            IndexError: Index error if gpu list is empty

        Returns:
            None: Print output via AMDSMILogger to destination
        """
        # Set args.* to passed in arguments
        if gpu:
            args.gpu = gpu
        if general:
            args.general = general
        if engine:
            args.engine = engine
        if pid:
            args.pid = pid
        if name:
            args.name = name
        if watch:
            args.watch = watch
        if watch_time:
            args.watch_time = watch_time
        if iterations:
            args.iterations = iterations

        # Handle No GPU passed
        if args.gpu == None:
            args.gpu = self.device_handles

        # Handle watch logic, will only enter this block once
        if args.watch:
            self.helpers.handle_watch(args=args, subcommand=self.process, logger=self.logger)
            return

        # Handle multiple GPUs
        if isinstance(args.gpu, list):
            if len(args.gpu) > 1:
                # Deepcopy gpus as recursion will destroy the gpu list
                stored_gpus = []
                for gpu in args.gpu:
                    stored_gpus.append(gpu)

                # Store output from multiple devices
                for device_handle in args.gpu:
                    self.process(args, multiple_devices=True, watching_output=watching_output, gpu=device_handle)

                # Reload original gpus
                args.gpu = stored_gpus

                # Print multiple device output
                self.logger.print_output(multiple_device_enabled=True, watching_output=watching_output)

                # Add output to total watch output and clear multiple device output
                if watching_output:
                    self.logger.store_watch_output(multiple_device_enabled=True)

                    # Flush the watching output
                    self.logger.print_output(multiple_device_enabled=True, watching_output=watching_output)

                return
            elif len(args.gpu) == 1:
                args.gpu = args.gpu[0]
            else:
                raise IndexError("args.gpu should not be an empty list")

        # Populate initial processes
        try:
            process_list = amdsmi_interface.amdsmi_get_gpu_process_list(args.gpu)
        except amdsmi_exception.AmdSmiLibraryException as e:
            raise e

        filtered_process_values = []
        for process_handle in process_list:
            try:
                process_info = amdsmi_interface.amdsmi_get_gpu_process_info(args.gpu, process_handle)
            except amdsmi_exception.AmdSmiLibraryException as e:
                process_info = e.get_error_info()
                filtered_process_values.append({'process_info': process_info})
                continue

            process_info['mem_usage'] = process_info.pop('mem')
            process_info['usage'] = process_info.pop('engine_usage')

            if self.logger.is_human_readable_format():
                process_info['mem_usage'] = self.helpers.convert_bytes_to_readable(process_info['mem_usage'])

                engine_usage_unit = "ns"
                for usage_metric in process_info['usage']:
                    process_info['usage'][usage_metric] = f"{process_info['usage'][usage_metric]} {engine_usage_unit}"

                for usage_metric in process_info['memory_usage']:
                    process_info['memory_usage'][usage_metric] = self.helpers.convert_bytes_to_readable(process_info['memory_usage'][usage_metric])

            filtered_process_values.append({'process_info': process_info})

        # Arguments will filter the populated processes
        # General and Engine to expose process_info values
        if args.general or args.engine:
            for process_info in filtered_process_values:
                if args.general and args.engine:
                    del process_info['process_info']['memory_usage']
                elif args.general:
                    del process_info['process_info']['memory_usage']
                    del process_info['process_info']['usage'] # Used in engine
                elif args.engine:
                    del process_info['process_info']['memory_usage']
                    del process_info['process_info']['mem_usage'] # Used in general

        # Filter out non specified pids
        if args.pid:
            process_pids = []
            for process_info in filtered_process_values:
                pid = str(process_info['process_info']['pid'])
                if str(args.pid) == pid:
                    process_pids.append(process_info)
            filtered_process_values = process_pids

        # Filter out non specified process names
        if args.name:
            process_names = []
            for process_info in filtered_process_values:
                process_name = str(process_info['process_info']['name']).lower()
                if str(args.name).lower() == process_name:
                    process_names.append(process_info)
            filtered_process_values = process_names

        multiple_devices_csv_override = False
        # Convert and store output by pid for csv format
        if self.logger.is_csv_format():
            for process_info in filtered_process_values:
                for key, value in process_info['process_info'].items():
                    multiple_devices_csv_override = True

                    if watching_output:
                        self.logger.store_output(args.gpu, 'timestamp', int(time.time()))
                    self.logger.store_output(args.gpu, key, value)

                self.logger.store_multiple_device_output()
        else:
            # Remove brackets if there is only one value
            if len(filtered_process_values) == 1:
                filtered_process_values = filtered_process_values[0]

            if watching_output:
                self.logger.store_output(args.gpu, 'timestamp', int(time.time()))

            # Store values in logger.output
            if filtered_process_values == []:
                self.logger.store_output(args.gpu, 'values', {'process_info': 'Not Found'})
            else:
                self.logger.store_output(args.gpu, 'values', filtered_process_values)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output(multiple_device_enabled=multiple_devices_csv_override, watching_output=watching_output)

        if watching_output: # End of single gpu add to watch_output
            self.logger.store_watch_output(multiple_device_enabled=multiple_devices_csv_override)


    def profile(self, args):
        """Not applicable to linux baremetal"""
        print('Not applicable to linux baremetal')


    def event(self, args):
        print('EVENT LISTENING:\n')
        print('Press q and hit ENTER when you want to stop (listening will stop inside 10 seconds)')

        threads = []
        for i in range(len(self.device_handles)):
            x = threading.Thread(target=self._event_thread, args=(self, i))
            threads.append(x)
            x.start()

        while self.stop!= 'q':
            self.stop = input("")

        for thread in threads:
            thread.join()


    def topology(self, args, multiple_devices=False, gpu=None, access=None,
                weight=None, hops=None, link_type=None, numa_bw=None):
        """ Get topology information for target gpus
            The compatibility mode for this will only be in amdsmi & rocm-smi
            params:
                args - argparser args to pass to subcommand
                multiple_devices (bool) - True if checking for multiple devices
                gpu (device_handle) - device_handle for target device
                access (bool) - Value override for args.access
                weight (bool) - Value override for args.weight
                hops (bool) - Value override for args.hops
                type (bool) - Value override for args.type
                numa_bw (bool) - Value override for args.numa_bw
            return:
                Nothing
        """
        # Set args.* to passed in arguments
        if gpu:
            args.gpu = gpu
        if access:
            args.access = access
        if weight:
            args.weight = weight
        if hops:
            args.hops = hops
        if link_type:
            args.link_type = link_type
        if numa_bw:
            args.numa_bw = numa_bw

        # Handle No GPU passed
        if args.gpu == None:
            args.gpu = self.device_handles

        if not isinstance(args.gpu, list):
            args.gpu = [args.gpu]

        # Handle all args being false
        if not any([args.access, args.weight, args.hops, args.link_type, args.numa_bw]):
            args.access = args.weight = args.hops = args.link_type= args.numa_bw = True

        # Populate the possible gpus
        topo_values = []
        for gpu in args.gpu:
            gpu_id = self.helpers.get_gpu_id_from_device_handle(gpu)
            topo_values.append({"gpu" : gpu_id})

        if args.access:
            for src_gpu_index, src_gpu in enumerate(args.gpu):
                src_gpu_links = {}
                for dest_gpu in args.gpu:
                    dest_gpu_id = self.helpers.get_gpu_id_from_device_handle(dest_gpu)
                    dest_gpu_key = f'gpu_{dest_gpu_id}'

                    try:
                        dest_gpu_link_status = amdsmi_interface.amdsmi_is_P2P_accessible(src_gpu, dest_gpu)
                        src_gpu_links[dest_gpu_key] = bool(dest_gpu_link_status)
                    except amdsmi_exception.AmdSmiLibraryException as e:
                        src_gpu_links[dest_gpu_key] = e.get_error_info()

                topo_values[src_gpu_index]['link_accessibility'] = src_gpu_links

        if args.weight:
            for src_gpu_index, src_gpu in enumerate(args.gpu):
                src_gpu_weight = {}
                for dest_gpu in args.gpu:
                    dest_gpu_id = self.helpers.get_gpu_id_from_device_handle(dest_gpu)
                    dest_gpu_key = f'gpu_{dest_gpu_id}'

                    if src_gpu == dest_gpu:
                        src_gpu_weight[dest_gpu_key] = 0
                        continue

                    try:
                        dest_gpu_link_weight = amdsmi_interface.amdsmi_topo_get_link_weight(src_gpu, dest_gpu)
                        src_gpu_weight[dest_gpu_key] = dest_gpu_link_weight
                    except amdsmi_exception.AmdSmiLibraryException as e:
                        src_gpu_weight[dest_gpu_key] = e.get_error_info()

                topo_values[src_gpu_index]['weight'] = src_gpu_weight

        if args.hops:
            for src_gpu_index, src_gpu in enumerate(args.gpu):
                src_gpu_hops = {}
                for dest_gpu in args.gpu:
                    dest_gpu_id = self.helpers.get_gpu_id_from_device_handle(dest_gpu)
                    dest_gpu_key = f'gpu_{dest_gpu_id}'

                    if src_gpu == dest_gpu:
                        src_gpu_hops[dest_gpu_key] = 0
                        continue

                    try:
                        dest_gpu_hops = amdsmi_interface.amdsmi_topo_get_link_type(src_gpu, dest_gpu)['hops']
                        src_gpu_hops[dest_gpu_key] = dest_gpu_hops
                    except amdsmi_exception.AmdSmiLibraryException as e:
                        src_gpu_hops[dest_gpu_key] = e.get_error_info()

                topo_values[src_gpu_index]['hops'] = src_gpu_hops

        if args.link_type:
            for src_gpu_index, src_gpu in enumerate(args.gpu):
                src_gpu_link_type = {}
                for dest_gpu in args.gpu:
                    dest_gpu_id = self.helpers.get_gpu_id_from_device_handle(dest_gpu)
                    dest_gpu_key = f'gpu_{dest_gpu_id}'

                    if src_gpu == dest_gpu:
                        src_gpu_link_type[dest_gpu_key] = "SELF"
                        continue
                    try:
                        link_type = amdsmi_interface.amdsmi_topo_get_link_type(src_gpu, dest_gpu)['type']
                        if isinstance(link_type, int):
                            if link_type == amdsmi_interface.amdsmi_wrapper.AMDSMI_IOLINK_TYPE_UNDEFINED:
                                src_gpu_link_type[dest_gpu_key] = "UNKNOWN"
                            elif link_type == amdsmi_interface.amdsmi_wrapper.AMDSMI_IOLINK_TYPE_PCIEXPRESS:
                                src_gpu_link_type[dest_gpu_key] = "PCIE"
                            elif link_type == amdsmi_interface.amdsmi_wrapper.AMDSMI_IOLINK_TYPE_XGMI:
                                src_gpu_link_type[dest_gpu_key] = "XGMI"
                    except amdsmi_exception.AmdSmiLibraryException as e:
                        src_gpu_link_type[dest_gpu_key] = e.get_error_info()

                topo_values[src_gpu_index]['link_type'] = src_gpu_link_type

        if args.numa_bw:
            for src_gpu_index, src_gpu in enumerate(args.gpu):
                src_gpu_link_type = {}
                for dest_gpu in args.gpu:
                    dest_gpu_id = self.helpers.get_gpu_id_from_device_handle(dest_gpu)
                    dest_gpu_key = f'gpu_{dest_gpu_id}'

                    if src_gpu == dest_gpu:
                        src_gpu_link_type[dest_gpu_key] = 'N/A'
                        continue

                    try:
                        link_type = amdsmi_interface.amdsmi_topo_get_link_type(src_gpu, dest_gpu)['type']
                        if isinstance(link_type, int):
                            if link_type != 2:
                                non_xgmi = True
                                src_gpu_link_type[dest_gpu_key] = 'N/A'
                                continue
                    except amdsmi_exception.AmdSmiLibraryException as e:
                        src_gpu_link_type[dest_gpu_key] = e.get_error_info()

                    try:
                        min_bw = amdsmi_interface.amdsmi_get_minmax_bandwidth_between_processors(src_gpu, dest_gpu)['min_bandwidth']
                        max_bw = amdsmi_interface.amdsmi_get_minmax_bandwidth_between_processors(src_gpu, dest_gpu)['max_bandwidth']

                        src_gpu_link_type[dest_gpu_key] = f'{min_bw}-{max_bw}'
                    except amdsmi_exception.AmdSmiLibraryException as e:
                        src_gpu_link_type[dest_gpu_key] =  e.get_error_info()

                topo_values[src_gpu_index]['numa_bandwidth'] = src_gpu_link_type

        self.logger.multiple_device_output = topo_values

        if self.logger.is_csv_format():
            new_output = []
            for elem in self.logger.multiple_device_output:
                new_output.append(self.logger.flatten_dict(elem, topology_override=True))
            self.logger.multiple_device_output = new_output

        self.logger.print_output(multiple_device_enabled=True)


    def set_value(self, args, multiple_devices=False, gpu=None, fan=None, perflevel=None,
                  profile=None, perfdeterminism=None):
        """Issue reset commands to target gpu(s)

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            gpu (device_handle, optional): device_handle for target device. Defaults to None.
            fan (int, optional): Value override for args.fan. Defaults to None.
            perflevel (amdsmi_interface.AmdSmiDevPerfLevel, optional): Value override for args.perflevel. Defaults to None.
            profile (bool, optional): Value override for args.profile. Defaults to None.
            perfdeterminism (int, optional): Value override for args.perfdeterminism. Defaults to None.

        Raises:
            ValueError: Value error if no gpu value is provided
            IndexError: Index error if gpu list is empty

        Return:
            Nothing
        """
        # Set args.* to passed in arguments
        if gpu:
            args.gpu = gpu
        if fan:
            args.fan = fan
        if perflevel:
            args.perflevel = perflevel
        if profile:
            args.profile = profile
        if perfdeterminism:
            args.perfdeterminism = perfdeterminism

        # Handle No GPU passed
        if args.gpu == None:
            raise ValueError('No GPU provided, specific GPU target(s) are needed')

        # Handle multiple GPUs
        handled_multiple_gpus, device_handle = self.helpers.handle_gpus(args, self.logger, self.set_value)
        if handled_multiple_gpus:
            return # This function is recursive

        args.gpu = device_handle

        # Build GPU string for errors
        try:
            gpu_bdf = amdsmi_interface.amdsmi_get_gpu_device_bdf(args.gpu)
        except amdsmi_exception.AmdSmiLibraryException:
            gpu_bdf = f'BDF Unavailable for {args.gpu}'
        try:
            gpu_id = self.helpers.get_gpu_id_from_device_handle(args.gpu)
        except IndexError:
            gpu_id = f'ID Unavailable for {args.gpu}'
        gpu_string = f"GPU ID: {gpu_id} BDF:{gpu_bdf}"

        # Handle args
        if isinstance(args.fan, int):
            try:
                amdsmi_interface.amdsmi_set_gpu_fan_speed(args.gpu, 0, args.fan)
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                raise ValueError(f"Unable to set fan speed {args.fan} on {gpu_string}") from e

            self.logger.store_output(args.gpu, 'fan', f"Successfully set fan speed {args.fan}")
        if args.perflevel:
            perf_level = amdsmi_interface.AmdSmiDevPerfLevel[args.perflevel]
            try:
                amdsmi_interface.amdsmi_set_gpu_perf_level(args.gpu, perf_level)
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                raise ValueError(f"Unable to set performance level {args.perflevel} on {gpu_string}") from e

            self.logger.store_output(args.gpu, 'perflevel', f"Successfully set performance level {args.perflevel}")
        if args.profile:
            self.logger.store_output(args.gpu, 'profile', "Not Yet Implemented")
        if isinstance(args.perfdeterminism, int):
            try:
                amdsmi_interface.amdsmi_set_gpu_perf_determinism_mode(args.gpu, args.perfdeterminism)
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                raise ValueError(f"Unable to set performance determinism and clock frequency to {args.perfdeterminism} on {gpu_string}") from e

            self.logger.store_output(args.gpu, 'perfdeterminism', f"Successfully enabled performance determinism and set GFX clock frequency to {args.perfdeterminism}")

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output()


    def reset(self, args, multiple_devices=False, gpu=None, gpureset=None,
                clocks=None, fans=None, profile=None, xgmierr=None, perfdeterminism=None):
        """Issue reset commands to target gpu(s)

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            gpu (device_handle, optional): device_handle for target device. Defaults to None.
            gpureset (bool, optional): Value override for args.gpureset. Defaults to None.
            clocks (bool, optional): Value override for args.clocks. Defaults to None.
            fans (bool, optional): Value override for args.fans. Defaults to None.
            profile (bool, optional): Value override for args.profile. Defaults to None.
            xgmierr (bool, optional): Value override for args.xgmierr. Defaults to None.
            perfdeterminism (bool, optional): Value override for args.perfdeterminism. Defaults to None.

        Raises:
            ValueError: Value error if no gpu value is provided
            IndexError: Index error if gpu list is empty

        Return:
            Nothing
        """
        # Set args.* to passed in arguments
        if gpu:
            args.gpu = gpu
        if gpureset:
            args.gpureset = gpureset
        if clocks:
            args.clocks = clocks
        if fans:
            args.fans = fans
        if profile:
            args.profile = profile
        if xgmierr:
            args.xgmierr = xgmierr
        if perfdeterminism:
            args.perfdeterminism = perfdeterminism

        # Handle No GPU passed
        if args.gpu == None:
            raise ValueError('No GPU provided, specific GPU target(s) are needed')

        # Handle multiple GPUs
        handled_multiple_gpus, device_handle = self.helpers.handle_gpus(args, self.logger, self.reset)
        if handled_multiple_gpus:
            return # This function is recursive

        args.gpu = device_handle

        if args.gpureset:
            if self.helpers.is_amd_device(args.gpu):
                try:
                    amdsmi_interface.amdsmi_reset_gpu(args.gpu)
                    result = 'Successfully reset GPU'
                except amdsmi_exception.AmdSmiLibraryException as e:
                    if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NO_PERM:
                        raise PermissionError('Command requires elevation') from e
                    result = e.get_error_info()
            else:
                result = 'Unable to reset non-amd GPU'

            self.logger.store_output(args.gpu, 'gpu_reset', result)
        if args.clocks:
            reset_clocks_results = {'overdrive' : '',
                                    'clocks' : '',
                                    'performance': ''}
            try:
                amdsmi_interface.amdsmi_set_gpu_overdrive_level(args.gpu, 0)
                reset_clocks_results['overdrive'] = 'Overdrive set to 0'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                reset_clocks_results['overdrive'] = e.get_error_info()

            try:
                level_auto = amdsmi_interface.AmdSmiDevPerfLevel.AUTO
                amdsmi_interface.amdsmi_set_gpu_perf_level(args.gpu, level_auto)
                reset_clocks_results['clocks'] = 'Successfully reset clocks'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                reset_clocks_results['clocks'] = e.get_error_info()

            try:
                level_auto = amdsmi_interface.AmdSmiDevPerfLevel.AUTO
                amdsmi_interface.amdsmi_set_gpu_perf_level(args.gpu, level_auto)
                reset_clocks_results['performance'] = 'Performance level reset to auto'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                reset_clocks_results['performance'] = e.get_error_info()

            self.logger.store_output(args.gpu, 'reset_clocks', reset_clocks_results)
        if args.fans:
            try:
                amdsmi_interface.amdsmi_reset_gpu_fan(args.gpu, 0)
                result = 'Successfully reset fan speed to driver control'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                result = e.get_error_info()

            self.logger.store_output(args.gpu, 'reset_fans', result)
        if args.profile:
            reset_profile_results = {'power_profile' : '',
                                     'performance_level': ''}
            try:
                power_profile_mask = amdsmi_interface.AmdSmiPowerProfilePresetMasks.BOOTUP_DEFAULT
                amdsmi_interface.amdsmi_set_gpu_power_profile(args.gpu, 0, power_profile_mask)
                reset_profile_results['power_profile'] = 'Successfully reset Power Profile'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                reset_profile_results['power_profile'] = e.get_error_info()

            try:
                level_auto = amdsmi_interface.AmdSmiDevPerfLevel.AUTO
                amdsmi_interface.amdsmi_set_gpu_perf_level(args.gpu, level_auto)
                reset_profile_results['performance_level'] = 'Successfully reset Performance Level'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                reset_profile_results['performance_level'] = e.get_error_info()

            self.logger.store_output(args.gpu, 'reset_profile', reset_profile_results)
        if args.xgmierr:
            try:
                amdsmi_interface.amdsmi_reset_gpu_xgmi_error(args.gpu)
                result = 'Successfully reset XGMI Error count'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                result = e.get_error_info()
            self.logger.store_output(args.gpu, 'reset_xgmi_err', result)
        if args.perfdeterminism:
            try:
                level_auto = amdsmi_interface.AmdSmiDevPerfLevel.AUTO
                amdsmi_interface.amdsmi_set_gpu_perf_level(args.gpu, level_auto)
                result = 'Successfully disabled performance determinism'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_exception.AmdSmiRetCode.STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                result = e.get_error_info()

            self.logger.store_output(args.gpu, 'reset_perf_determinism', result)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output()


    def rocm_smi(self, args):
        print("Placeholder for rocm-smi legacy commands")


    def _event_thread(self, commands, i):
        devices = commands.device_handles
        if len(devices) == 0:
            print("No GPUs on machine")
            return

        device = devices[i]
        listener = amdsmi_interface.AmdSmiEventReader(device, amdsmi_interface.AmdSmiEvtNotificationType.GPU_PRE_RESET,
                            amdsmi_interface.AmdSmiEvtNotificationType.GPU_POST_RESET)
        values_dict = {}

        while self.stop!='q':
            try:
                events = listener.read(10000)
                for event in events:
                    values_dict["event"] = event["event"]
                    values_dict["message"] = event["message"]
                    commands.logger.store_output(device, 'values', values_dict)
                    commands.logger.print_output()
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.err_code != amdsmi_exception.AmdSmiRetCode.STATUS_NO_DATA:
                    print(e)
            except Exception as e:
                print(e)

        listener.stop()

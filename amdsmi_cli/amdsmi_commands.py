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

import logging
import sys
import threading
import time

from _version import __version__
from amdsmi_helpers import AMDSMIHelpers
from amdsmi_logger import AMDSMILogger
from amdsmi_cli_exceptions import AmdSmiRequiredCommandException
from amdsmi import amdsmi_interface
from amdsmi import amdsmi_exception


class AMDSMICommands():
    """This class contains all the commands corresponding to AMDSMIParser
    Each command function will interact with AMDSMILogger to handle
    displaying the output to the specified format and destination.
    """
    def __init__(self, format='human_readable', destination='stdout') -> None:
        self.helpers = AMDSMIHelpers()
        self.logger = AMDSMILogger(format=format, destination=destination)
        try:
            self.device_handles = amdsmi_interface.amdsmi_get_processor_handles()
        except amdsmi_exception.AmdSmiLibraryException as e:
            if e.err_code in (amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NOT_INIT,
                              amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_DRIVER_NOT_LOADED):
                logging.error('Unable to get devices, driver not initialized (amdgpu not found in modules)')
                sys.exit(-1)
            else:
                raise e

        if len(self.device_handles) == 0:
            logging.error('Unable to detect any devices, check if driver is initialized (amdgpu not found in modules)')
            sys.exit(-1)

        self.stop = ''


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

        self.logger.print_output()


    def static(self, args, multiple_devices=False, gpu=None, asic=None,
                bus=None, vbios=None, limit=None, driver=None, ras=None,
                board=None, numa=None, vram=None, cache=None, partition=None,
                dfc_ucode=None, fb_info=None, num_vf=None):
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
            vram (bool, optional): Value override for args.vram. Defaults to None.
            cache (bool, optional): Value override for args.cache. Defaults to None.
            partition (bool, optional): Value override for args.partition. Defaults to None.
            dfc_ucode (bool, optional): Value override for args.dfc_ucode. Defaults to None.
            fb_info (bool, optional): Value override for args.fb_info. Defaults to None.
            num_vf (bool, optional): Value override for args.num_vf. Defaults to None.

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
        if board:
            args.board = board
        if driver:
            args.driver = driver
        if vram:
            args.vram = vram
        if cache:
            args.cache = cache

        # Store args that are applicable to the current platform
        current_platform_args = ["asic", "bus", "vbios", "driver", "vram", "cache", "board"]
        current_platform_values = [args.asic, args.bus, args.vbios, args.driver, args.vram, args.cache, args.board]

        if self.helpers.is_linux() and self.helpers.is_baremetal():
            if ras:
                args.ras = ras
            if partition:
                args.partition = partition
            if limit:
                args.limit = limit
            current_platform_args += ["ras", "limit", "partition"]
            current_platform_values += [args.ras, args.limit, args.partition]

        if self.helpers.is_linux() and not self.helpers.is_virtual_os():
            if numa:
                args.numa = numa
            current_platform_args += ["numa"]
            current_platform_values += [args.numa]

        if self.helpers.is_hypervisor():
            if dfc_ucode:
                args.dfc_ucode = dfc_ucode
            if fb_info:
                args.fb_info = fb_info
            if num_vf:
                args.num_vf = num_vf
            current_platform_args += ["dfc_ucode", "fb_info", "num_vf"]
            current_platform_values += [args.dfc_ucode, args.fb_info, args.num_vf]

        # Handle No GPU passed
        if args.gpu == None:
            args.gpu = self.device_handles

        # Handle multiple GPUs
        handled_multiple_gpus, device_handle = self.helpers.handle_gpus(args, self.logger, self.static)
        if handled_multiple_gpus:
            return # This function is recursive
        args.gpu = device_handle

        # Get gpu_id for logging
        gpu_id = self.helpers.get_gpu_id_from_device_handle(args.gpu)

        logging.debug(f"Static Arg information for GPU {gpu_id} on {self.helpers.os_info()}")
        logging.debug(f"Applicable Args: {current_platform_args}")
        logging.debug(f"Arg Values:      {current_platform_values}")
        # Set the platform applicable args to True if no args are set
        if not any(current_platform_values):
            for arg in current_platform_args:
                setattr(args, arg, True)

        static_dict = {}

        if args.asic:
            try:
                asic_info = amdsmi_interface.amdsmi_get_gpu_asic_info(args.gpu)
                asic_info['vendor_id'] = hex(asic_info['vendor_id'])
                asic_info['vendor_name'] = asic_info['vendor_name'].replace(',', '')
                asic_info['device_id'] = hex(asic_info['device_id'])
                asic_info['rev_id'] = hex(asic_info['rev_id'])
                if asic_info['asic_serial'] != '':
                    asic_info['asic_serial'] = hex(int(asic_info['asic_serial'], base=16))
                if asic_info['oam_id'] == 0xFFFF: # uint 16 max
                    asic_info['oam_id'] = "N/A"
                static_dict['asic'] = asic_info
            except amdsmi_exception.AmdSmiLibraryException as e:
                static_dict['asic'] = "N/A"
                logging.debug("Failed to get asic info for gpu %s | %s", gpu_id, e.get_error_info())
        if args.bus:
            bus_info = {}

            try:
                bus_info['bdf'] = amdsmi_interface.amdsmi_get_gpu_device_bdf(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                bus_info['bdf'] = "N/A"
                logging.debug("Failed to get bdf for gpu %s | %s", gpu_id, e.get_error_info())

            try:
                link_caps = amdsmi_interface.amdsmi_get_pcie_link_caps(args.gpu)
                bus_info.update(link_caps)
                if bus_info['max_pcie_speed'] % 1000 != 0:
                    pcie_speed_GTs_value = round(bus_info['max_pcie_speed'] / 1000, 1)
                else:
                    pcie_speed_GTs_value = round(bus_info['max_pcie_speed'] / 1000)

                bus_info['max_pcie_speed'] = pcie_speed_GTs_value

                slot_type = bus_info.pop('pcie_slot_type')
                if isinstance(slot_type, int):
                    slot_types = amdsmi_interface.amdsmi_wrapper.amdsmi_pcie_slot_type_t__enumvalues
                    if slot_type in slot_types:
                        bus_info['slot_type'] = slot_types[slot_type].replace("AMDSMI_SLOT_TYPE__", "")
                    else:
                        bus_info['slot_type'] = "Unknown"
                else:
                    bus_info['slot_type'] = "N/A"

                if self.logger.is_human_readable_format():
                    unit ='GT/s'
                    bus_info['max_pcie_speed'] = f"{bus_info['max_pcie_speed']} {unit}"
                    if bus_info['pcie_interface_version'] > 0:
                        bus_info['pcie_interface_version'] = f"Gen {bus_info['pcie_interface_version']}"
            except amdsmi_exception.AmdSmiLibraryException as e:
                bus_info = "N/A"
                logging.debug("Failed to get bus info for gpu %s | %s", gpu_id, e.get_error_info())

            static_dict['bus'] = bus_info
        if args.vbios:
            try:
                vbios_info = amdsmi_interface.amdsmi_get_gpu_vbios_info(args.gpu)
                for key, value in vbios_info.items():
                    if isinstance(value, str):
                        if value.strip() == '':
                            vbios_info[key] = "N/A"
                static_dict['vbios'] = vbios_info
            except amdsmi_exception.AmdSmiLibraryException as e:
                static_dict['vbios'] = "N/A"
                logging.debug("Failed to get vbios info for gpu %s | %s", gpu_id, e.get_error_info())
        if args.board:
            static_dict['board'] = {"model_number": "N/A",
                                    "product_serial": "N/A",
                                    "fru_id": "N/A",
                                    "manufacturer_name": "N/A",
                                    "product_name": "N/A"}
            try:
                board_info = amdsmi_interface.amdsmi_get_gpu_board_info(args.gpu)
                for key, value in board_info.items():
                    if isinstance(value, str):
                        if value.strip() == '':
                            board_info[key] = "N/A"
                static_dict['board'] = board_info
            except amdsmi_exception.AmdSmiLibraryException as e:
                logging.debug("Failed to get board info for gpu %s | %s", gpu_id, e.get_error_info())
        if 'limit' in current_platform_args:
            if args.limit:
                # Power limits
                try:
                    power_limit_error = False
                    power_cap_info = amdsmi_interface.amdsmi_get_power_cap_info(args.gpu)
                    max_power_limit = power_cap_info['max_power_cap']
                    current_power_limit = power_cap_info['power_cap']
                except amdsmi_exception.AmdSmiLibraryException as e:
                    power_limit_error = True
                    max_power_limit = "N/A"
                    current_power_limit = "N/A"
                    logging.debug("Failed to get power cap info for gpu %s | %s", gpu_id, e.get_error_info())

                # Edge temperature limits
                try:
                    slowdown_temp_edge_limit_error = False
                    slowdown_temp_edge_limit = amdsmi_interface.amdsmi_get_temp_metric(args.gpu,
                        amdsmi_interface.AmdSmiTemperatureType.EDGE, amdsmi_interface.AmdSmiTemperatureMetric.CRITICAL)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    slowdown_temp_edge_limit_error = True
                    slowdown_temp_edge_limit = "N/A"
                    logging.debug("Failed to get edge temperature slowdown metric for gpu %s | %s", gpu_id, e.get_error_info())

                if slowdown_temp_edge_limit == 0:
                    slowdown_temp_edge_limit_error = True
                    slowdown_temp_edge_limit = "N/A"

                try:
                    shutdown_temp_edge_limit_error = False
                    shutdown_temp_edge_limit = amdsmi_interface.amdsmi_get_temp_metric(args.gpu,
                        amdsmi_interface.AmdSmiTemperatureType.EDGE, amdsmi_interface.AmdSmiTemperatureMetric.EMERGENCY)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    shutdown_temp_edge_limit_error = True
                    shutdown_temp_edge_limit = "N/A"
                    logging.debug("Failed to get edge temperature shutdown metrics for gpu %s | %s", gpu_id, e.get_error_info())

                if shutdown_temp_edge_limit == 0:
                    shutdown_temp_edge_limit_error = True
                    shutdown_temp_edge_limit = "N/A"

                # Hotspot/Junction temperature limits
                try:
                    slowdown_temp_hotspot_limit_error = False
                    slowdown_temp_hotspot_limit = amdsmi_interface.amdsmi_get_temp_metric(args.gpu,
                        amdsmi_interface.AmdSmiTemperatureType.HOTSPOT, amdsmi_interface.AmdSmiTemperatureMetric.CRITICAL)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    slowdown_temp_hotspot_limit_error = True
                    slowdown_temp_hotspot_limit = "N/A"
                    logging.debug("Failed to get hotspot temperature slowdown metrics for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    shutdown_temp_hotspot_limit_error = False
                    shutdown_temp_hotspot_limit = amdsmi_interface.amdsmi_get_temp_metric(args.gpu,
                        amdsmi_interface.AmdSmiTemperatureType.HOTSPOT, amdsmi_interface.AmdSmiTemperatureMetric.EMERGENCY)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    shutdown_temp_hotspot_limit_error = True
                    shutdown_temp_hotspot_limit = "N/A"
                    logging.debug("Failed to get hotspot temperature shutdown metrics for gpu %s | %s", gpu_id, e.get_error_info())


                # VRAM temperature limits
                try:
                    slowdown_temp_vram_limit_error = False
                    slowdown_temp_vram_limit = amdsmi_interface.amdsmi_get_temp_metric(args.gpu,
                        amdsmi_interface.AmdSmiTemperatureType.VRAM, amdsmi_interface.AmdSmiTemperatureMetric.CRITICAL)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    slowdown_temp_vram_limit_error = True
                    slowdown_temp_vram_limit = "N/A"
                    logging.debug("Failed to get vram temperature slowdown metrics for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    shutdown_temp_vram_limit_error = False
                    shutdown_temp_vram_limit = amdsmi_interface.amdsmi_get_temp_metric(args.gpu,
                        amdsmi_interface.AmdSmiTemperatureType.VRAM, amdsmi_interface.AmdSmiTemperatureMetric.EMERGENCY)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    shutdown_temp_vram_limit_error = True
                    shutdown_temp_vram_limit = "N/A"
                    logging.debug("Failed to get vram temperature shutdown metrics for gpu %s | %s", gpu_id, e.get_error_info())

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
            driver_info = {"driver_name" : "N/A",
                           "driver_version" : "N/A"
                           }

            try:
                driver_info = amdsmi_interface.amdsmi_get_gpu_driver_info(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                logging.debug("Failed to get driver info for gpu %s | %s", gpu_id, e.get_error_info())

            static_dict['driver'] = driver_info
        if args.vram:
            try:
                vram_info = amdsmi_interface.amdsmi_get_gpu_vram_info(args.gpu)

                # Get vram type string
                vram_type_enum = vram_info['vram_type']
                if vram_type_enum == amdsmi_interface.amdsmi_wrapper.VRAM_TYPE_GDDR6:
                    vram_type = "GDDR6"
                else:
                    vram_type = amdsmi_interface.amdsmi_wrapper.amdsmi_vram_type_t__enumvalues[vram_type_enum]
                    # Remove amdsmi enum prefix
                    vram_type = vram_type.replace('VRAM_TYPE_', '').replace('_', '')

                # Get vram vendor string
                vram_vendor_enum = vram_info['vram_vendor']
                vram_vendor = amdsmi_interface.amdsmi_wrapper.amdsmi_vram_vendor_type_t__enumvalues[vram_vendor_enum]
                if "PLACEHOLDER" in vram_vendor:
                    vram_vendor = "N/A"
                else:
                    # Remove amdsmi enum prefix
                    vram_vendor = vram_vendor.replace('AMDSMI_VRAM_VENDOR__', '')

                vram_info['vram_type'] = vram_type
                vram_info['vram_vendor'] = vram_vendor
                if self.logger.is_human_readable_format():
                    vram_info['vram_size_mb'] = f"{vram_info['vram_size_mb']} MB"

            except amdsmi_exception.AmdSmiLibraryException as e:
                vram_info = "N/A"
                logging.debug("Failed to get vram info for gpu %s | %s", gpu_id, e.get_error_info())

            static_dict['vram'] = vram_info
        if args.cache:
            try:
                cache_info = amdsmi_interface.amdsmi_get_gpu_cache_info(args.gpu)
                for cache_key, cache_dict in cache_info.items():
                    for key, value in cache_dict.items():
                        if key == 'cache_size' or key == 'cache_level' or \
                            key == 'max_num_cu_shared' or key == 'num_cache_instance':
                            continue
                        if value:
                            cache_info[cache_key][key] = "ENABLED"
                if self.logger.is_human_readable_format():
                    for _ , cache_values in cache_info.items():
                        cache_values['cache_size'] = f"{cache_values['cache_size']} KB"

            except amdsmi_exception.AmdSmiLibraryException as e:
                cache_info = "N/A"
                logging.debug("Failed to get cache info for gpu %s | %s", gpu_id, e.get_error_info())

            static_dict['cache'] = cache_info
        if 'ras' in current_platform_args:
            if args.ras:
                ras_dict = {"eeprom_version": "N/A",
                            "parity_schema" : "N/A",
                            "single_bit_schema" : "N/A",
                            "double_bit_schema" : "N/A",
                            "poison_schema" : "N/A",
                            "ecc_block_state": "N/A"}

                try:
                    ras_info = amdsmi_interface.amdsmi_get_gpu_ras_feature_info(args.gpu)
                    for key, value in ras_info.items():
                        if isinstance(value, int):
                            if value == 65535:
                                logging.debug(f"Failed to get ras {key} for gpu {gpu_id}")
                                ras_info[key] = "N/A"
                                continue
                        if key != "eeprom_version":
                            if value:
                                ras_info[key] = "ENABLED"
                            else:
                                ras_info[key] = "DISABLED"

                    ras_dict.update(ras_info)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get ras info for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    ras_dict["ecc_block_state"] = amdsmi_interface.amdsmi_get_gpu_ras_block_features_enabled(args.gpu)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get ras block features for gpu %s | %s", gpu_id, e.get_error_info())

                static_dict["ras"] = ras_dict
        if 'partition' in current_platform_args:
            if args.partition:
                try:
                    compute_partition = amdsmi_interface.amdsmi_get_gpu_compute_partition(args.gpu)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    compute_partition = "N/A"
                    logging.debug("Failed to get compute partition info for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    memory_partition = amdsmi_interface.amdsmi_get_gpu_memory_partition(args.gpu)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    memory_partition = "N/A"
                    logging.debug("Failed to get memory partition info for gpu %s | %s", gpu_id, e.get_error_info())

                static_dict['partition'] = {"compute_partition": compute_partition,
                                            "memory_partition": memory_partition}
        if 'numa' in current_platform_args:
            if args.numa:
                try:
                    numa_node_number = amdsmi_interface.amdsmi_topo_get_numa_node_number(args.gpu)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    numa_node_number = "N/A"
                    logging.debug("Failed to get numa node number for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    numa_affinity = amdsmi_interface.amdsmi_get_gpu_topo_numa_affinity(args.gpu)
                    # -1 means No numa node is assigned to the GPU, so there is no numa affinity
                    if self.logger.is_human_readable_format() and numa_affinity == -1:
                        numa_affinity = "NONE"
                except amdsmi_exception.AmdSmiLibraryException as e:
                    numa_affinity = "N/A"
                    logging.debug("Failed to get numa affinity for gpu %s | %s", gpu_id, e.get_error_info())

                static_dict['numa'] = {'node' : numa_node_number,
                                        'affinity' : numa_affinity}

        multiple_devices_csv_override = False
        # Convert and store output by pid for csv format
        if self.logger.is_csv_format():
            # expand if ras blocks are populated
            if self.helpers.is_linux() and self.helpers.is_baremetal() and args.ras:
                if isinstance(static_dict['ras']['ecc_block_state'], list):
                    ecc_block_dicts = static_dict['ras'].pop('ecc_block_state')
                    multiple_devices_csv_override = True
                    for ecc_block_dict in ecc_block_dicts:
                        for key, value in ecc_block_dict.items():
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
        if fw_list:
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

        # Get gpu_id for logging
        gpu_id = self.helpers.get_gpu_id_from_device_handle(args.gpu)

        if args.fw_list:
            try:
                fw_info = amdsmi_interface.amdsmi_get_fw_info(args.gpu)

                for fw_index, fw_entry in enumerate(fw_info['fw_list']):
                    # Change fw_name to fw_id
                    fw_entry['fw_id'] = fw_entry.pop('fw_name').name.replace("FW_ID_", "")
                    fw_entry['fw_version'] = fw_entry.pop('fw_version') # popping to ensure order

                    # Add custom human readable formatting
                    if self.logger.is_human_readable_format():
                        fw_info['fw_list'][fw_index] = {f'FW {fw_index}': fw_entry}
                    else:
                        fw_info['fw_list'][fw_index] = fw_entry

                fw_list.update(fw_info)
            except amdsmi_exception.AmdSmiLibraryException as e:
                fw_list['fw_list'] = "N/A"
                logging.debug("Failed to get firmware info for gpu %s | %s", gpu_id, e.get_error_info())

        multiple_devices_csv_override = False
        # Convert and store output by pid for csv format
        if self.logger.is_csv_format():
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

        # Get gpu_id for logging
        gpu_id = self.helpers.get_gpu_id_from_device_handle(args.gpu)

        try:
            bad_page_info = amdsmi_interface.amdsmi_get_gpu_bad_page_info(args.gpu)
        except amdsmi_exception.AmdSmiLibraryException as e:
            bad_page_info = "N/A"
            logging.debug("Failed to get bad page info for gpu %s | %s", gpu_id, e.get_error_info())

        if bad_page_info == "N/A" or bad_page_info == "No bad pages found.":
            bad_page_error = True

        if args.retired:
            if bad_page_error:
                values_dict['retired'] = bad_page_info
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
                values_dict['pending'] = bad_page_info
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
                values_dict['un_res'] = bad_page_info
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
                usage=None, watch=None, watch_time=None, iterations=None, power=None,
                clock=None, temperature=None, ecc=None, ecc_block=None, pcie=None,
                fan=None, voltage_curve=None, overdrive=None, perf_level=None,
                xgmi_err=None, energy=None, mem_usage=None, schedule=None,
                guard=None, guest_data=None, fb_usage=None, xgmi=None,):
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
            xgmi_err (bool, optional): Value override for args.xgmi_err. Defaults to None.
            energy (bool, optional): Value override for args.energy. Defaults to None.
            mem_usage (bool, optional): Value override for args.mem_usage. Defaults to None.
            schedule (bool, optional): Value override for args.schedule. Defaults to None.
            guard (bool, optional): Value override for args.guard. Defaults to None.
            guest_data (bool, optional): Value override for args.guest_data. Defaults to None.
            fb_usage (bool, optional): Value override for args.fb_usage. Defaults to None.
            xgmi (bool, optional): Value override for args.xgmi. Defaults to None.

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

        # Store args that are applicable to the current platform
        current_platform_args = []
        current_platform_values = []

        if not self.helpers.is_hypervisor() and not self.helpers.is_windows():
            if mem_usage:
                args.mem_usage = mem_usage
            current_platform_args += ["mem_usage"]
            current_platform_values += [args.mem_usage]

        if self.helpers.is_hypervisor() or self.helpers.is_baremetal():
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
            if pcie:
                args.pcie = pcie
            current_platform_args += ["usage", "power", "clock", "temperature", "ecc", "pcie"]
            current_platform_values += [args.usage, args.power, args.clock, args.temperature, args.ecc, args.pcie]

        if self.helpers.is_baremetal() and self.helpers.is_linux():
            if ecc_block:
                args.ecc_block = ecc_block
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
            current_platform_args += ["ecc_block", "fan", "voltage_curve", "overdrive", "perf_level", "xgmi_err", "energy"]
            current_platform_values += [args.ecc_block, args.fan, args.voltage_curve, args.overdrive, args.perf_level, args.xgmi_err, args.energy]

        if self.helpers.is_hypervisor():
            if schedule:
                args.schedule = schedule
            if guard:
                args.guard = guard
            if guest_data:
                args.guest_data = guest_data
            if fb_usage:
                args.fb_usage = fb_usage
            if xgmi:
                args.xgmi = xgmi
            current_platform_args += ["schedule", "guard", "guest_data", "fb_usage", "xgmi"]
            current_platform_values += [args.schedule, args.guard, args.guest_data, args.fb_usage, args.xgmi]

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

        # Get gpu_id for logging
        gpu_id = self.helpers.get_gpu_id_from_device_handle(args.gpu)

        # Put the metrics table in the debug logs
        try:
            logging.debug("GPU Metrics table for %s | %s", gpu_id, amdsmi_interface.amdsmi_get_gpu_metrics_info(args.gpu))
        except amdsmi_exception.AmdSmiLibraryException as e:
            logging.debug("Unabled to load GPU Metrics table for %s | %s", gpu_id, e.err_info)

        logging.debug(f"Metric Arg information for GPU {gpu_id} on {self.helpers.os_info()}")
        logging.debug(f"Args:   {current_platform_args}")
        logging.debug(f"Values: {current_platform_values}")
        # Set the platform applicable args to True if no args are set
        if not any(current_platform_values):
            for arg in current_platform_args:
                setattr(args, arg, True)

        # Add timestamp and store values for specified arguments
        values_dict = {}

        if "usage" in current_platform_args:
            if args.usage:
                try:
                    engine_usage = amdsmi_interface.amdsmi_get_gpu_activity(args.gpu)
                    engine_usage['gfx_usage'] = engine_usage.pop('gfx_activity')
                    engine_usage['mem_usage'] = engine_usage.pop('umc_activity')
                    engine_usage['mm_ip_usage'] = engine_usage.pop('mm_activity')

                    for key, value in engine_usage.items():
                        if value == 65535:
                            engine_usage[key] = "N/A"

                        if self.logger.is_human_readable_format():
                            if engine_usage[key] != "N/A":
                                unit = '%'
                                engine_usage[key] = f"{value} {unit}"

                    values_dict['usage'] = engine_usage
                except amdsmi_exception.AmdSmiLibraryException as e:
                    values_dict['usage'] = "N/A"
                    logging.debug("Failed to get gpu activity for gpu %s | %s", gpu_id, e.get_error_info())
        if "power" in current_platform_args:
            if args.power:
                power_dict = {'current_power': "N/A",
                              'current_gfx_voltage': "N/A",
                              'current_soc_voltage': "N/A",
                              'current_mem_voltage': "N/A",
                              'power_limit': "N/A",
                              'power_management': "N/A",
                              'throttle_status': "N/A"}

                try:
                    power_info = amdsmi_interface.amdsmi_get_power_info(args.gpu)
                    for key, value in power_info.items():
                        if value == 0xFFFF:
                            power_info[key] = "N/A"
                        elif self.logger.is_human_readable_format():
                            if "voltage" in key:
                                power_info[key] = f"{value} mV"
                            elif "power" in key:
                                power_info[key] = f"{value} W"

                    power_dict['current_power'] = power_info['current_socket_power']

                    if power_dict['current_power'] == "N/A":
                        power_dict['current_power'] = power_info['average_socket_power']

                    power_dict['current_gfx_voltage'] = power_info['gfx_voltage']
                    power_dict['current_soc_voltage'] = power_info['soc_voltage']
                    power_dict['current_mem_voltage'] = power_info['mem_voltage']
                    power_dict['power_limit'] = power_info['power_limit']

                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get power info for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    is_power_management_enabled = amdsmi_interface.amdsmi_is_gpu_power_management_enabled(args.gpu)
                    if is_power_management_enabled:
                        power_dict['power_management'] = "ENABLED"
                    else:
                        power_dict['power_management'] = "DISABLED"
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get power management status for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    throttle_status = amdsmi_interface.amdsmi_get_gpu_metrics_throttle_status(args.gpu)
                    if throttle_status:
                        power_dict['throttle_status'] = "THROTTLED"
                    else:
                        power_dict['throttle_status'] = "UNTHROTTLED"
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get throttle status for gpu %s | %s", gpu_id, e.get_error_info())


                values_dict['power'] = power_dict
        if "clock" in current_platform_args:
            if args.clock:
                clocks = {}
                clock_types = [amdsmi_interface.AmdSmiClkType.GFX,
                                amdsmi_interface.AmdSmiClkType.MEM,
                                amdsmi_interface.AmdSmiClkType.VCLK0,
                                amdsmi_interface.AmdSmiClkType.VCLK1]
                for clock_type in clock_types:
                    clock_name = amdsmi_interface.amdsmi_wrapper.amdsmi_clk_type_t__enumvalues[clock_type].replace("CLK_TYPE_", "")
                    # Ensure that gfx is the clock_name instead of another macro
                    if clock_type == amdsmi_interface.AmdSmiClkType.GFX:
                        clock_name = "gfx"

                    # Store the clock_name for vclk0
                    vlck0_clock_name = None
                    if clock_type == amdsmi_interface.AmdSmiClkType.VCLK0:
                        vlck0_clock_name = clock_name

                    try:
                        clock_info = amdsmi_interface.amdsmi_get_clock_info(args.gpu, clock_type)
                        if clock_info['sleep_clk'] == 0xFFFFFFFF:
                            clock_info['sleep_clk'] = "N/A"

                        if self.logger.is_human_readable_format():
                            unit = 'MHz'
                            for key, value in clock_info.items():
                                if isinstance(value, int):
                                    clock_info[key] = f"{value} {unit}"

                        clocks[clock_name] = clock_info
                    except amdsmi_exception.AmdSmiLibraryException as e:
                        # Handle the case where VCLK1 is not enaled in sysfs on all GPUs
                        if clock_type == amdsmi_interface.AmdSmiClkType.VCLK1:
                            # Check if VCLK0 was retrieved successfully
                            if vlck0_clock_name in clocks:
                                # Since VCLK0 exists, do not error
                                logging.debug("VLCK0 exists, not adding %s clock info to output for gpu %s | %s", clock_name, gpu_id, e.get_error_info())
                                continue
                        else:
                            # Handle all other failed to get clock info
                            clocks[clock_name] = {"cur_clk": "N/A",
                                                  "max_clk": "N/A",
                                                  "min_clk": "N/A",
                                                  "sleep_clk": "N/A"}
                            logging.debug("Failed to get %s clock info for gpu %s | %s", clock_name, gpu_id, e.get_error_info())

                try:
                    is_clk_locked = amdsmi_interface.amdsmi_get_gpu_metrics_gfxclk_lock_status(args.gpu)
                    if self.logger.is_human_readable_format():
                        if is_clk_locked:
                            is_clk_locked = "LOCKED"
                        else:
                            is_clk_locked = "UNLOCKED"
                except amdsmi_exception.AmdSmiLibraryException as e:
                    is_clk_locked = "N/A"
                    logging.debug("Failed to get gfx clock lock status info for gpu %s | %s", gpu_id, e.get_error_info())

                if "gfx" in clocks:
                    if isinstance(clocks['gfx'], dict):
                        clocks['gfx']['is_clk_locked'] = is_clk_locked
                    else:
                        clocks['gfx'] = {"is_clk_locked": is_clk_locked}

                values_dict['clock'] = clocks
        if "temperature" in current_platform_args:
            if args.temperature:
                try:
                    temperature_edge_current = amdsmi_interface.amdsmi_get_temp_metric(
                        args.gpu, amdsmi_interface.AmdSmiTemperatureType.EDGE, amdsmi_interface.AmdSmiTemperatureMetric.CURRENT)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    temperature_edge_current = "N/A"
                    logging.debug("Failed to get current edge temperature for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    temperature_edge_limit = amdsmi_interface.amdsmi_get_temp_metric(
                        args.gpu, amdsmi_interface.AmdSmiTemperatureType.EDGE, amdsmi_interface.AmdSmiTemperatureMetric.CRITICAL)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    temperature_edge_limit = "N/A"
                    logging.debug("Failed to get edge temperature limit for gpu %s | %s", gpu_id, e.get_error_info())

                # If edge limit is reporting 0 then set the current edge temp to N/A
                if temperature_edge_limit == 0:
                    temperature_edge_current = "N/A"

                try:
                    temperature_hotspot_current = amdsmi_interface.amdsmi_get_temp_metric(
                        args.gpu, amdsmi_interface.AmdSmiTemperatureType.HOTSPOT, amdsmi_interface.AmdSmiTemperatureMetric.CURRENT)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    temperature_hotspot_current = "N/A"
                    logging.debug("Failed to get current hotspot temperature for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    temperature_vram_current = amdsmi_interface.amdsmi_get_temp_metric(
                        args.gpu, amdsmi_interface.AmdSmiTemperatureType.VRAM, amdsmi_interface.AmdSmiTemperatureMetric.CURRENT)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    temperature_vram_current = "N/A"
                    logging.debug("Failed to get current vram temperature for gpu %s | %s", gpu_id, e.get_error_info())

                temperatures = {'edge': temperature_edge_current,
                                'hotspot': temperature_hotspot_current,
                                'mem': temperature_vram_current}

                if self.logger.is_human_readable_format():
                    unit = '\N{DEGREE SIGN}C'
                    for temperature_key, temperature_value in temperatures.items():
                        if 'N/A' not in str(temperature_value):
                            temperatures[temperature_key] = f"{temperature_value} {unit}"

                values_dict['temperature'] = temperatures
        if "ecc" in current_platform_args:
            if args.ecc:
                ecc_count = {}
                try:
                    ecc_count = amdsmi_interface.amdsmi_get_gpu_total_ecc_count(args.gpu)
                    ecc_count['total_correctable'] = ecc_count.pop('correctable_count')
                    ecc_count['total_uncorrectable'] = ecc_count.pop('uncorrectable_count')
                except amdsmi_exception.AmdSmiLibraryException as e:
                    ecc_count['total_correctable'] = "N/A"
                    ecc_count['total_uncorrectable'] = "N/A"
                    ecc_count['cache_correctable'] = "N/A"
                    ecc_count['cache_uncorrectable'] = "N/A"
                    logging.debug("Failed to get total ecc count for gpu %s | %s", gpu_id, e.get_error_info())

                if ecc_count['total_correctable'] != "N/A":
                    # Get the UMC error count for getting total cache correctable errors
                    umc_block = amdsmi_interface.AmdSmiGpuBlock['UMC']
                    try:
                        umc_count = amdsmi_interface.amdsmi_get_gpu_ecc_count(args.gpu, umc_block)
                        ecc_count['cache_correctable'] = ecc_count['total_correctable'] - umc_count['correctable_count']
                        ecc_count['cache_uncorrectable'] = ecc_count['total_uncorrectable'] - umc_count['uncorrectable_count']
                    except amdsmi_exception.AmdSmiLibraryException as e:
                        ecc_count['cache_correctable'] = "N/A"
                        ecc_count['cache_uncorrectable'] = "N/A"
                        logging.debug("Failed to get cache ecc count for gpu %s at block %s | %s", gpu_id, umc_block, e.get_error_info())

                values_dict['ecc'] = ecc_count
        if "pcie" in current_platform_args:
            if args.pcie:
                pcie_dict = {"current_lanes": "N/A",
                             "current_speed": "N/A",
                             "replay_count" : "N/A",
                             "l0_to_recovery_count" : "N/A",
                             "replay_roll_over_count" : "N/A",
                             "nak_sent_count" : "N/A",
                             "nak_received_count" : "N/A",
                             "current_bandwidth_sent": "N/A",
                             "current_bandwidth_received": "N/A",
                             "max_packet_size": "N/A"}

                try:
                    pcie_link_status = amdsmi_interface.amdsmi_get_pcie_link_status(args.gpu)

                    if pcie_link_status['pcie_speed'] % 1000 != 0:
                        pcie_speed_GTs_value = round(pcie_link_status['pcie_speed'] / 1000, 1)
                    else:
                        pcie_speed_GTs_value = round(pcie_link_status['pcie_speed'] / 1000)

                    pcie_dict['current_speed'] = pcie_speed_GTs_value
                    pcie_dict['current_lanes'] = pcie_link_status['pcie_lanes']

                    if self.logger.is_human_readable_format():
                        unit = 'GT/s'
                        pcie_link_status['current_speed'] = f"{pcie_link_status['pcie_speed']} {unit}"
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get pcie link status for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    pci_replay_counter = amdsmi_interface.amdsmi_get_gpu_metrics_pcie_replay_count_acc(args.gpu)
                    pcie_dict['replay_count'] = pci_replay_counter
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get pci replay counter for gpu %s | %s", gpu_id, e.get_error_info())
                    logging.debug("Falling back to sysfs pci replay counter for gpu %s | %s", gpu_id, e.get_error_info())
                    try:
                        pci_replay_counter = amdsmi_interface.amdsmi_get_gpu_pci_replay_counter(args.gpu)
                        pcie_dict['replay_count'] = pci_replay_counter
                    except amdsmi_exception.AmdSmiLibraryException as err:
                        pcie_dict['replay_count'] = "N/A"
                        logging.debug("Failed to get sysfs fallback pci replay counter for gpu %s | %s", gpu_id, err.get_error_info())

                try:
                    l0_to_recovery_counter = amdsmi_interface.amdsmi_get_gpu_metrics_pcie_l0_recov_count_acc(args.gpu)
                    pcie_dict['l0_to_recovery_count'] = l0_to_recovery_counter
                except amdsmi_exception.AmdSmiLibraryException as e:
                    pcie_dict['l0_to_recovery_count'] = "N/A"
                    logging.debug("Failed to get pcie l0 to recovery counter for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    pci_replay_rollover_counter = amdsmi_interface.amdsmi_get_gpu_metrics_pcie_replay_rover_count_acc(args.gpu)
                    pcie_dict['replay_rollover_count'] = pci_replay_rollover_counter
                except amdsmi_exception.AmdSmiLibraryException as e:
                    pcie_dict['replay_roll_over_count'] = "N/A"
                    logging.debug("Failed to get pcie replay rollover counter for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    # nak_info = amdsmi_interface.amdsmi_get_gpu_pci_nak_info(args.gpu)
                    # pcie_dict['nak_sent_count'] = nak_info['nak_sent_count']
                    # pcie_dict['nak_received_count'] = nak_info['nak_received_count']
                    pcie_dict['nak_sent_count'] = "N/A"
                    pcie_dict['nak_received_count'] = "N/A"
                except amdsmi_exception.AmdSmiLibraryException as e:
                    pcie_dict['nak_sent_count'] = "N/A"
                    pcie_dict['nak_received_count'] = "N/A"
                    logging.debug("Failed to get pcie nak info for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    pcie_bw = amdsmi_interface.amdsmi_get_gpu_pci_throughput(args.gpu)
                    sent = pcie_bw['sent'] * pcie_bw['max_pkt_sz']
                    received = pcie_bw['received'] * pcie_bw['max_pkt_sz']

                    if self.logger.is_human_readable_format():
                        if sent > 0:
                            sent = sent // 1024 // 1024
                        sent = f"{sent} MB/s"

                        if received > 0:
                            received = received // 1024 // 1024
                        received = f"{received} MB/s"
                        pcie_bw['max_pkt_sz'] = f"{pcie_bw['max_pkt_sz']} B"

                    pcie_dict['current_bandwidth_sent'] = sent
                    pcie_dict['current_bandwidth_received'] = received
                    pcie_dict['max_packet_size'] = pcie_bw['max_pkt_sz']
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get pcie bandwidth for gpu %s | %s", gpu_id, e.get_error_info())

                values_dict['pcie'] = pcie_dict
        if "ecc_block" in current_platform_args:
            if args.ecc_block:
                ecc_dict = {}
                uncountable_blocks = ["ATHUB", "DF", "SMN", "SEM", "MP0", "MP1", "FUSE"]
                try:
                    ras_states = amdsmi_interface.amdsmi_get_gpu_ras_block_features_enabled(args.gpu)
                    for state in ras_states:
                        if state['status'] == amdsmi_interface.AmdSmiRasErrState.ENABLED.name:
                            gpu_block = amdsmi_interface.AmdSmiGpuBlock[state['block']]
                            # if the blocks are uncountable do not add them at all.
                            if gpu_block.name not in uncountable_blocks:
                                try:
                                    ecc_count = amdsmi_interface.amdsmi_get_gpu_ecc_count(args.gpu, gpu_block)
                                    ecc_dict[state['block']] = {'correctable' : ecc_count['correctable_count'],
                                                                'uncorrectable': ecc_count['uncorrectable_count']}
                                except amdsmi_exception.AmdSmiLibraryException as e:
                                    ecc_dict[state['block']] = {'correctable' : "N/A",
                                                                'uncorrectable': "N/A"}
                                    logging.debug("Failed to get ecc count for gpu %s at block %s | %s", gpu_id, gpu_block, e.get_error_info())

                    values_dict['ecc_block'] = ecc_dict
                except amdsmi_exception.AmdSmiLibraryException as e:
                    values_dict['ecc_block'] = "N/A"
                    logging.debug("Failed to get ecc block features for gpu %s | %s", gpu_id, e.get_error_info())
        if "fan" in current_platform_args:
            if args.fan:
                fan_dict = {"speed" : "N/A",
                            "max" : "N/A",
                            "rpm" : "N/A",
                            "usage" : "N/A"}

                try:
                    fan_speed = amdsmi_interface.amdsmi_get_gpu_fan_speed(args.gpu, 0)
                    fan_dict["speed"] = fan_speed
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get fan speed for gpu %s | %s", args.gpu, e.get_error_info())

                try:
                    fan_max = amdsmi_interface.amdsmi_get_gpu_fan_speed_max(args.gpu, 0)
                    fan_usage = "N/A"
                    if fan_max > 0 and fan_dict["speed"] != "N/A":
                        fan_usage = round((float(fan_speed) / float(fan_max)) * 100, 2)
                        if self.logger.is_human_readable_format():
                            unit = '%'
                            fan_usage = f"{fan_usage} {unit}"
                    fan_dict["max"] = fan_max
                    fan_dict["usage"] = fan_usage
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get fan max speed for gpu %s | %s", args.gpu, e.get_error_info())

                try:
                    fan_rpm = amdsmi_interface.amdsmi_get_gpu_fan_rpms(args.gpu, 0)
                    fan_dict["rpm"] = fan_rpm
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get fan rpms for gpu %s | %s", args.gpu, e.get_error_info())

                values_dict["fan"] = fan_dict
        if "voltage_curve" in current_platform_args:
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
                    values_dict['voltage_curve'] = "N/A"
                    logging.debug("Failed to get voltage curve for gpu %s | %s", gpu_id, e.get_error_info())
        if "overdrive" in current_platform_args:
            if args.overdrive:
                try:
                    overdrive_level = amdsmi_interface.amdsmi_get_gpu_overdrive_level(args.gpu)

                    if self.logger.is_human_readable_format():
                        unit = '%'
                        overdrive_level = f"{overdrive_level} {unit}"

                    values_dict['overdrive'] = overdrive_level
                except amdsmi_exception.AmdSmiLibraryException as e:
                    values_dict['overdrive'] = "N/A"
                    logging.debug("Failed to get overdrive level for gpu %s | %s", gpu_id, e.get_error_info())
        if "perf_level" in current_platform_args:
            if args.perf_level:
                try:
                    perf_level = amdsmi_interface.amdsmi_get_gpu_perf_level(args.gpu)
                    values_dict['perf_level'] = perf_level
                except amdsmi_exception.AmdSmiLibraryException as e:
                    values_dict['perf_level'] = "N/A"
                    logging.debug("Failed to get perf level for gpu %s | %s", gpu_id, e.get_error_info())
        if "xgmi_err" in current_platform_args:
            if args.xgmi_err:
                try:
                    xgmi_err_status = amdsmi_interface.amdsmi_gpu_xgmi_error_status(args.gpu)
                    values_dict['xgmi_err'] = amdsmi_interface.amdsmi_wrapper.amdsmi_xgmi_status_t__enumvalues[xgmi_err_status]
                except amdsmi_exception.AmdSmiLibraryException as e:
                    values_dict['xgmi_err'] = "N/A"
                    logging.debug("Failed to get xgmi error status for gpu %s | %s", gpu_id, e.get_error_info())
        if "energy" in current_platform_args:
            if args.energy:
                try:
                    energy_dict = amdsmi_interface.amdsmi_get_energy_count(args.gpu)

                    energy = energy_dict['power'] * round(energy_dict['counter_resolution'], 1)
                    energy /= 1000000
                    energy = round(energy, 3)

                    if self.logger.is_human_readable_format():
                        unit = 'J'
                        energy = f"{energy} {unit}"

                    values_dict['energy'] = {"total_energy_consumption" : energy}
                except amdsmi_interface.AmdSmiLibraryException as e:
                    values_dict['energy'] = "N/A"
                    logging.debug("Failed to get energy usage for gpu %s | %s", args.gpu, e.get_error_info())
        if "mem_usage" in current_platform_args:
            if args.mem_usage:
                unit = 'MB'
                memory_usage = {'total_vram': "N/A",
                                'used_vram': "N/A",
                                'free_vram': "N/A",
                                'total_visible_vram': "N/A",
                                'used_visible_vram': "N/A",
                                'free_visible_vram': "N/A",
                                'total_gtt': "N/A",
                                'used_gtt': "N/A",
                                'free_gtt': "N/A"}

                # Total VRAM
                try:
                    total_vram = amdsmi_interface.amdsmi_get_gpu_memory_total(args.gpu, amdsmi_interface.AmdSmiMemoryType.VRAM)
                    memory_usage['total_vram'] = total_vram // (1024*1024)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get total VRAM memory for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    total_visible_vram = amdsmi_interface.amdsmi_get_gpu_memory_total(args.gpu, amdsmi_interface.AmdSmiMemoryType.VIS_VRAM)
                    memory_usage['total_visible_vram'] = total_visible_vram // (1024*1024)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get total VIS VRAM memory for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    total_gtt = amdsmi_interface.amdsmi_get_gpu_memory_total(args.gpu, amdsmi_interface.AmdSmiMemoryType.GTT)
                    memory_usage['total_gtt'] = total_gtt // (1024*1024)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get total GTT memory for gpu %s | %s", gpu_id, e.get_error_info())

                # Used VRAM
                try:
                    used_vram = amdsmi_interface.amdsmi_get_gpu_memory_usage(args.gpu, amdsmi_interface.AmdSmiMemoryType.VRAM)
                    memory_usage['used_vram'] = used_vram // (1024*1024)

                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get used VRAM memory for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    used_visible_vram = amdsmi_interface.amdsmi_get_gpu_memory_usage(args.gpu, amdsmi_interface.AmdSmiMemoryType.VIS_VRAM)
                    memory_usage['used_visible_vram'] = used_visible_vram // (1024*1024)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get used VIS VRAM memory for gpu %s | %s", gpu_id, e.get_error_info())

                try:
                    used_gtt = amdsmi_interface.amdsmi_get_gpu_memory_usage(args.gpu, amdsmi_interface.AmdSmiMemoryType.GTT)
                    memory_usage['used_gtt'] = used_gtt // (1024*1024)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("Failed to get used GTT memory for gpu %s | %s", gpu_id, e.get_error_info())

                # Free VRAM
                if memory_usage['total_vram'] != "N/A" and memory_usage['used_vram'] != "N/A":
                    memory_usage['free_vram'] = memory_usage['total_vram'] - memory_usage['used_vram']

                if memory_usage['total_visible_vram'] != "N/A" and memory_usage['used_visible_vram'] != "N/A":
                    memory_usage['free_visible_vram'] = memory_usage['total_visible_vram'] - memory_usage['used_visible_vram']

                if memory_usage['total_gtt'] != "N/A" and memory_usage['used_gtt'] != "N/A":
                    memory_usage['free_gtt'] = memory_usage['total_gtt'] - memory_usage['used_gtt']

                if self.logger.is_human_readable_format():
                    for key, value in memory_usage.items():
                        if value != "N/A":
                            memory_usage[key] = f"{value} {unit}"

                values_dict['mem_usage'] = memory_usage

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

        # Get gpu_id for logging
        gpu_id = self.helpers.get_gpu_id_from_device_handle(args.gpu)

        # Populate initial processes
        try:
            process_list = amdsmi_interface.amdsmi_get_gpu_process_list(args.gpu)
        except amdsmi_exception.AmdSmiLibraryException as e:
            logging.debug("Failed to get process list for gpu %s | %s", gpu_id, e.get_error_info())
            raise e

        filtered_process_values = []
        for process_handle in process_list:
            try:
                process_info = amdsmi_interface.amdsmi_get_gpu_process_info(args.gpu, process_handle)
            except amdsmi_exception.AmdSmiLibraryException as e:
                process_info = "N/A"
                logging.debug("Failed to get process info for gpu %s on process_handle %s | %s", gpu_id, process_handle, e.get_error_info())
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


    def event(self, args, gpu=None):
        """ Get event information for target gpus

        Args:
            args (Namespace): argparser args to pass to subcommand
            gpu (device_handle, optional): device_handle for target device. Defaults to None.

        Return:
            stdout event information for target gpus
        """
        if args.gpu:
            gpu = args.gpu

        if gpu == None:
            args.gpu = self.device_handles

        if not isinstance(args.gpu, list):
            args.gpu = [args.gpu]

        print('EVENT LISTENING:\n')
        print('Press q and hit ENTER when you want to stop (listening will stop within 10 seconds)')

        threads = []
        for device_handle in range(len(args.gpu)):
            x = threading.Thread(target=self._event_thread, args=(self, device_handle))
            threads.append(x)
            x.start()

        while self.stop!= 'q':
            self.stop = input("")

        for thread in threads:
            thread.join()


    def topology(self, args, multiple_devices=False, gpu=None, access=None,
                weight=None, hops=None, link_type=None, numa_bw=None):
        """ Get topology information for target gpus
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
                        if dest_gpu_link_status:
                            src_gpu_links[dest_gpu_key] = "ENABLED"
                        else:
                            src_gpu_links[dest_gpu_key] = "DISABLED"
                    except amdsmi_exception.AmdSmiLibraryException as e:
                        src_gpu_links[dest_gpu_key] = "N/A"
                        logging.debug("Failed to get link status for %s to %s | %s",
                                        self.helpers.get_gpu_id_from_device_handle(src_gpu),
                                        self.helpers.get_gpu_id_from_device_handle(dest_gpu),
                                        e.get_error_info())

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
                        src_gpu_weight[dest_gpu_key] = "N/A"
                        logging.debug("Failed to get link weight for %s to %s | %s",
                                        self.helpers.get_gpu_id_from_device_handle(src_gpu),
                                        self.helpers.get_gpu_id_from_device_handle(dest_gpu),
                                        e.get_error_info())

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
                        src_gpu_hops[dest_gpu_key] = "N/A"
                        logging.debug("Failed to get link hops for %s to %s | %s",
                                        self.helpers.get_gpu_id_from_device_handle(src_gpu),
                                        self.helpers.get_gpu_id_from_device_handle(dest_gpu),
                                        e.get_error_info())

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
                        src_gpu_link_type[dest_gpu_key] = "N/A"
                        logging.debug("Failed to get link type for %s to %s | %s",
                                        self.helpers.get_gpu_id_from_device_handle(src_gpu),
                                        self.helpers.get_gpu_id_from_device_handle(dest_gpu),
                                        e.get_error_info())

                topo_values[src_gpu_index]['link_type'] = src_gpu_link_type

        if args.numa_bw:
            for src_gpu_index, src_gpu in enumerate(args.gpu):
                src_gpu_link_type = {}
                for dest_gpu in args.gpu:
                    dest_gpu_id = self.helpers.get_gpu_id_from_device_handle(dest_gpu)
                    dest_gpu_key = f'gpu_{dest_gpu_id}'

                    if src_gpu == dest_gpu:
                        src_gpu_link_type[dest_gpu_key] = "N/A"
                        continue

                    try:
                        link_type = amdsmi_interface.amdsmi_topo_get_link_type(src_gpu, dest_gpu)['type']
                        if isinstance(link_type, int):
                            if link_type != 2:
                                # non_xgmi = True
                                src_gpu_link_type[dest_gpu_key] = "N/A"
                                continue
                    except amdsmi_exception.AmdSmiLibraryException as e:
                        src_gpu_link_type[dest_gpu_key] = "N/A"
                        logging.debug("Failed to get link type for %s to %s | %s",
                                        self.helpers.get_gpu_id_from_device_handle(src_gpu),
                                        self.helpers.get_gpu_id_from_device_handle(dest_gpu),
                                        e.get_error_info())

                    try:
                        bw_dict = amdsmi_interface.amdsmi_get_minmax_bandwidth_between_processors(src_gpu, dest_gpu)
                        src_gpu_link_type[dest_gpu_key] = f"{bw_dict['min_bandwidth']}-{bw_dict['max_bandwidth']}"
                    except amdsmi_exception.AmdSmiLibraryException as e:
                        src_gpu_link_type[dest_gpu_key] =  e.get_error_info()
                        logging.debug("Failed to get min max bandwidth for %s to %s | %s",
                                        self.helpers.get_gpu_id_from_device_handle(src_gpu),
                                        self.helpers.get_gpu_id_from_device_handle(dest_gpu),
                                        e.get_error_info())

                topo_values[src_gpu_index]['numa_bandwidth'] = src_gpu_link_type

        self.logger.multiple_device_output = topo_values

        if self.logger.is_csv_format():
            new_output = []
            for elem in self.logger.multiple_device_output:
                new_output.append(self.logger.flatten_dict(elem, topology_override=True))
            self.logger.multiple_device_output = new_output

        self.logger.print_output(multiple_device_enabled=True)


    def set_value(self, args, multiple_devices=False, gpu=None, fan=None, perf_level=None,
                  profile=None, perf_determinism=None, compute_partition=None,
                  memory_partition=None, power_cap=None):
        """Issue reset commands to target gpu(s)

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            gpu (device_handle, optional): device_handle for target device. Defaults to None.
            fan (int, optional): Value override for args.fan. Defaults to None.
            perf_level (amdsmi_interface.AmdSmiDevPerfLevel, optional): Value override for args.perf_level. Defaults to None.
            profile (bool, optional): Value override for args.profile. Defaults to None.
            perf_determinism (int, optional): Value override for args.perf_determinism. Defaults to None.
            compute_partition (amdsmi_interface.AmdSmiComputePartitionType, optional): Value override for args.compute_partition. Defaults to None.
            memory_partition (amdsmi_interface.AmdSmiMemoryPartitionType, optional): Value override for args.memory_partition. Defaults to None.
            power_cap (int, optional): Value override for args.power_cap. Defaults to None.

        Raises:
            ValueError: Value error if no gpu value is provided
            IndexError: Index error if gpu list is empty

        Return:
            Nothing
        """
        # Set args.* to passed in arguments
        if gpu:
            args.gpu = gpu
        if fan is not None:
            args.fan = fan
        if perf_level:
            args.perf_level = perf_level
        if profile:
            args.profile = profile
        if perf_determinism is not None:
            args.perf_determinism = perf_determinism
        if compute_partition:
            args.compute_partition = compute_partition
        if memory_partition:
            args.memory_partition = memory_partition
        if power_cap:
            args.power_cap = power_cap

        # Handle No GPU passed
        if args.gpu == None:
            raise ValueError('No GPU provided, specific GPU target(s) are needed')

        # Handle multiple GPUs
        handled_multiple_gpus, device_handle = self.helpers.handle_gpus(args, self.logger, self.set_value)
        if handled_multiple_gpus:
            return # This function is recursive

        args.gpu = device_handle

        # Error if no subcommand args are passed
        if not any([args.fan is not None,
                    args.perf_level,
                    args.profile,
                    args.compute_partition,
                    args.memory_partition,
                    args.perf_determinism is not None,
                    args.power_cap]):
            command = " ".join(sys.argv[1:])
            raise AmdSmiRequiredCommandException(command, self.logger.format)

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
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                raise ValueError(f"Unable to set fan speed {args.fan} on {gpu_string}") from e

            self.logger.store_output(args.gpu, 'fan', f"Successfully set fan speed {args.fan}")
        if args.perf_level:
            perf_level = amdsmi_interface.AmdSmiDevPerfLevel[args.perf_level]
            try:
                amdsmi_interface.amdsmi_set_gpu_perf_level(args.gpu, perf_level)
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                raise ValueError(f"Unable to set performance level {args.perf_level} on {gpu_string}") from e

            self.logger.store_output(args.gpu, 'perflevel', f"Successfully set performance level {args.perf_level}")
        if args.profile:
            self.logger.store_output(args.gpu, 'profile', "Not Yet Implemented")
        if isinstance(args.perf_determinism, int):
            try:
                amdsmi_interface.amdsmi_set_gpu_perf_determinism_mode(args.gpu, args.perf_determinism)
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                raise ValueError(f"Unable to set performance determinism and clock frequency to {args.perf_determinism} on {gpu_string}") from e

            self.logger.store_output(args.gpu, 'perfdeterminism', f"Successfully enabled performance determinism and set GFX clock frequency to {args.perf_determinism}")
        if args.compute_partition:
            compute_partition = amdsmi_interface.AmdSmiComputePartitionType[args.compute_partition]
            try:
                amdsmi_interface.amdsmi_set_gpu_compute_partition(args.gpu, compute_partition)
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                raise ValueError(f"Unable to set compute partition to {args.compute_partition} on {gpu_string}") from e
            self.logger.store_output(args.gpu, 'computepartition', f"Successfully set compute partition to {args.compute_partition}")
        if args.memory_partition:
            memory_partition = amdsmi_interface.AmdSmiMemoryPartitionType[args.memory_partition]
            try:
                amdsmi_interface.amdsmi_set_gpu_memory_partition(args.gpu, memory_partition)
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                raise ValueError(f"Unable to set memory partition to {args.memory_partition} on {gpu_string}") from e
            self.logger.store_output(args.gpu, 'memorypartition', f"Successfully set memory partition to {args.memory_partition}")
        if isinstance(args.power_cap, int):
            try:
                power_cap_info = amdsmi_interface.amdsmi_get_power_cap_info(args.gpu)
                logging.debug(f"Power cap info for gpu {gpu_id} | {power_cap_info}")
                min_power_cap = power_cap_info["min_power_cap"]
                max_power_cap = power_cap_info["max_power_cap"]
                current_power_cap = power_cap_info["power_cap"]
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(f"Unable to get power cap info from {gpu_string}") from e

            if args.power_cap == current_power_cap:
                self.logger.store_output(args.gpu, 'powercap', f"Power cap is already set to {args.power_cap}")
            elif args.power_cap >= min_power_cap and args.power_cap <= max_power_cap:
                try:
                    amdsmi_interface.amdsmi_set_power_cap(args.gpu, 0, args.power_cap * 1000000)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                        raise PermissionError('Command requires elevation') from e
                    raise ValueError(f"Unable to set power cap to {args.power_cap} on {gpu_string}") from e
                self.logger.store_output(args.gpu, 'powercap', f"Successfully set power cap to {args.power_cap}")
            else:
                # setting power cap to 0 will return the current power cap so the technical minimum value is 1
                if min_power_cap == 0:
                    min_power_cap = 1
                self.logger.store_output(args.gpu, 'powercap', f"Power cap must be between {min_power_cap} and {max_power_cap}")

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output()


    def reset(self, args, multiple_devices=False, gpu=None, gpureset=None,
                clocks=None, fans=None, profile=None, xgmierr=None, perf_determinism=None,
                compute_partition=None, memory_partition=None, power_cap=None):
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
            perf_determinism (bool, optional): Value override for args.perf_determinism. Defaults to None.
            compute_partition (bool, optional): Value override for args.compute_partition. Defaults to None.
            memory_partition (bool, optional): Value override for args.memory_partition. Defaults to None.
            power_cap (int, optional): Value override for args.power_cap. Defaults to None.

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
        if perf_determinism:
            args.perf_determinism = perf_determinism
        if compute_partition:
            args.compute_partition = compute_partition
        if memory_partition:
            args.memory_partition = memory_partition
        if power_cap:
            args.power_cap = power_cap

        # Handle No GPU passed
        if args.gpu == None:
            raise ValueError('No GPU provided, specific GPU target(s) are needed')

        # Handle multiple GPUs
        handled_multiple_gpus, device_handle = self.helpers.handle_gpus(args, self.logger, self.reset)
        if handled_multiple_gpus:
            return # This function is recursive

        args.gpu = device_handle

        # Get gpu_id for logging
        gpu_id = self.helpers.get_gpu_id_from_device_handle(args.gpu)

        # Error if no subcommand args are passed
        if not any([args.gpureset, args.clocks, args.fans, args.profile, args.xgmierr, \
                    args.perf_determinism, args.compute_partition, args.memory_partition, \
                    args.power_cap]):
            command = " ".join(sys.argv[1:])
            raise AmdSmiRequiredCommandException(command, self.logger.format)

        if args.gpureset:
            if self.helpers.is_amd_device(args.gpu):
                try:
                    amdsmi_interface.amdsmi_reset_gpu(args.gpu)
                    result = 'Successfully reset GPU'
                except amdsmi_exception.AmdSmiLibraryException as e:
                    if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                        raise PermissionError('Command requires elevation') from e
                    result = "Failed to reset GPU"
            else:
                result = 'Unable to reset non-amd GPU'

            self.logger.store_output(args.gpu, 'gpu_reset', result)
        if args.clocks:
            reset_clocks_results = {'overdrive': '',
                                    'clocks': '',
                                    'performance': ''}
            try:
                amdsmi_interface.amdsmi_set_gpu_overdrive_level(args.gpu, 0)
                reset_clocks_results['overdrive'] = 'Overdrive set to 0'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                reset_clocks_results['overdrive'] = "N/A"
                logging.debug("Failed to reset overdrive on gpu %s | %s", gpu_id, e.get_error_info())

            try:
                level_auto = amdsmi_interface.AmdSmiDevPerfLevel.AUTO
                amdsmi_interface.amdsmi_set_gpu_perf_level(args.gpu, level_auto)
                reset_clocks_results['clocks'] = 'Successfully reset clocks'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                reset_clocks_results['clocks'] = "N/A"
                logging.debug("Failed to reset perf level on gpu %s | %s", gpu_id, e.get_error_info())

            try:
                level_auto = amdsmi_interface.AmdSmiDevPerfLevel.AUTO
                amdsmi_interface.amdsmi_set_gpu_perf_level(args.gpu, level_auto)
                reset_clocks_results['performance'] = 'Performance level reset to auto'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                reset_clocks_results['performance'] = "N/A"
                logging.debug("Failed to reset perf level on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.store_output(args.gpu, 'reset_clocks', reset_clocks_results)
        if args.fans:
            try:
                amdsmi_interface.amdsmi_reset_gpu_fan(args.gpu, 0)
                result = 'Successfully reset fan speed to driver control'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                result = "N/A"
                logging.debug("Failed to reset fans on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.store_output(args.gpu, 'reset_fans', result)
        if args.profile:
            reset_profile_results = {'power_profile' : '',
                                     'performance_level': ''}
            try:
                power_profile_mask = amdsmi_interface.AmdSmiPowerProfilePresetMasks.BOOTUP_DEFAULT
                amdsmi_interface.amdsmi_set_gpu_power_profile(args.gpu, 0, power_profile_mask)
                reset_profile_results['power_profile'] = 'Successfully reset Power Profile'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                reset_profile_results['power_profile'] = "N/A"
                logging.debug("Failed to reset power profile on gpu %s | %s", gpu_id, e.get_error_info())

            try:
                level_auto = amdsmi_interface.AmdSmiDevPerfLevel.AUTO
                amdsmi_interface.amdsmi_set_gpu_perf_level(args.gpu, level_auto)
                reset_profile_results['performance_level'] = 'Successfully reset Performance Level'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                reset_profile_results['performance_level'] = "N/A"
                logging.debug("Failed to reset perf level on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.store_output(args.gpu, 'reset_profile', reset_profile_results)
        if args.xgmierr:
            try:
                amdsmi_interface.amdsmi_reset_gpu_xgmi_error(args.gpu)
                result = 'Successfully reset XGMI Error count'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                result = "N/A"
                logging.debug("Failed to reset xgmi error count on gpu %s | %s", gpu_id, e.get_error_info())
            self.logger.store_output(args.gpu, 'reset_xgmi_err', result)
        if args.perf_determinism:
            try:
                level_auto = amdsmi_interface.AmdSmiDevPerfLevel.AUTO
                amdsmi_interface.amdsmi_set_gpu_perf_level(args.gpu, level_auto)
                result = 'Successfully disabled performance determinism'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                result = "N/A"
                logging.debug("Failed to set perf level on gpu %s | %s", gpu_id, e.get_error_info())
            self.logger.store_output(args.gpu, 'reset_perf_determinism', result)
        if args.compute_partition:
            try:
                amdsmi_interface.amdsmi_reset_gpu_compute_partition(args.gpu)
                result = 'Successfully reset compute partition'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                result = "N/A"
                logging.debug("Failed to reset compute partition on gpu %s | %s", gpu_id, e.get_error_info())
            self.logger.store_output(args.gpu, 'reset_compute_partition', result)
        if args.memory_partition:
            try:
                amdsmi_interface.amdsmi_reset_gpu_memory_partition(args.gpu)
                result = 'Successfully reset memory partition'
            except amdsmi_exception.AmdSmiLibraryException as e:
                if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                    raise PermissionError('Command requires elevation') from e
                result = "N/A"
                logging.debug("Failed to reset memory partition on gpu %s | %s", gpu_id, e.get_error_info())
            self.logger.store_output(args.gpu, 'reset_memory_partition', result)
        if args.power_cap:
            try:
                power_cap_info = amdsmi_interface.amdsmi_get_power_cap_info(args.gpu)
                logging.debug(f"Power cap info for gpu {gpu_id} | {power_cap_info}")
                default_power_cap = power_cap_info["default_power_cap"]
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(f"Unable to get power cap info from {gpu_id}") from e

            if args.power_cap == default_power_cap:
                self.logger.store_output(args.gpu, 'powercap', f"Power cap is already set to {default_power_cap}")
            else:
                try:
                    amdsmi_interface.amdsmi_set_power_cap(args.gpu, 0, default_power_cap * 1000000)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    if e.get_error_code() == amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_PERM:
                        raise PermissionError('Command requires elevation') from e
                    raise ValueError(f"Unable to reset power cap to {default_power_cap} on GPU {gpu_id}") from e
                self.logger.store_output(args.gpu, 'powercap', f"Successfully set power cap to {default_power_cap}")

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output()


    def monitor(self, args, multiple_devices=False, watching_output=False, gpu=None,
                  watch=None, watch_time=None, iterations=None, power_usage=None,
                  temperature=None, gfx_util=None, mem_util=None, encoder=None, decoder=None,
                  throttle_status=None, ecc=None, vram_usage=None, pcie=None):
        """ Populate a table with each GPU as an index to rows of targeted data

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            gpu (device_handle, optional): device_handle for target device. Defaults to None.
            watch (bool, optional): Value override for args.watch. Defaults to None.
            watch_time (int, optional): Value override for args.watch_time. Defaults to None.
            iterations (int, optional): Value override for args.iterations. Defaults to None.
            power_usage (bool, optional): Value override for args.power_usage. Defaults to None.
            temperature (bool, optional): Value override for args.temperature. Defaults to None.
            gfx (bool, optional): Value override for args.gfx. Defaults to None.
            mem (bool, optional): Value override for args.mem. Defaults to None.
            encoder (bool, optional): Value override for args.encoder. Defaults to None.
            decoder (bool, optional): Value override for args.decoder. Defaults to None.
            throttle_status (bool, optional): Value override for args.throttle_status. Defaults to None.
            ecc (bool, optional): Value override for args.ecc. Defaults to None.
            vram_usage (bool, optional): Value override for args.vram_usage. Defaults to None.
            pcie (bool, optional): Value override for args.pcie. Defaults to None.

        Raises:
            ValueError: Value error if no gpu value is provided
            IndexError: Index error if gpu list is empty

        Return:
            Nothing
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

        # monitor args
        if power_usage:
            args.power_usage = power_usage
        if temperature:
            args.temperature = temperature
        if gfx_util:
            args.gfx = gfx_util
        if mem_util:
            args.mem = mem_util
        if encoder:
            args.encoder = encoder
        if decoder:
            args.decoder = decoder
        if throttle_status:
            args.throttle_status = throttle_status
        if ecc:
            args.ecc = ecc
        if vram_usage:
            args.vram_usage = vram_usage
        if pcie:
            args.pcie = pcie

        # Handle No GPU passed
        if args.gpu == None:
            args.gpu = self.device_handles

        # If all arguments are False, the print all values
        if not any([args.power_usage, args.temperature, args.gfx, args.mem,
                    args.encoder, args.decoder, args.throttle_status, args.ecc,
                    args.vram_usage, args.pcie]):
            args.power_usage = args.temperature = args.gfx = args.mem = \
                args.encoder = args.decoder = args.throttle_status = args.ecc = \
                args.vram_usage = args.pcie = True

        # Handle watch logic, will only enter this block once
        if args.watch:
            self.helpers.handle_watch(args=args, subcommand=self.monitor, logger=self.logger)
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
                    self.monitor(args, multiple_devices=True, watching_output=watching_output, gpu=device_handle)

                # Reload original gpus
                args.gpu = stored_gpus

                # Print multiple device output
                self.logger.print_output(multiple_device_enabled=True, watching_output=watching_output, tabular=True)

                # Add output to total watch output and clear multiple device output
                if watching_output:
                    self.logger.store_watch_output(multiple_device_enabled=True)

                    # Flush the watching output
                    self.logger.print_output(multiple_device_enabled=True, watching_output=watching_output, tabular=True)

                return
            elif len(args.gpu) == 1:
                args.gpu = args.gpu[0]
            else:
                raise IndexError("args.gpu should not be an empty list")

        monitor_values = {}

        # Get gpu_id for logging
        gpu_id = self.helpers.get_gpu_id_from_device_handle(args.gpu)

        # Clear the table header; TODO make this a function
        self.logger.table_header = ''

        # Store timestamp for watch output
        if watching_output:
            self.logger.store_output(args.gpu, 'timestamp', int(time.time()))
            self.logger.table_header += 'TIMESTAMP'.rjust(10)

        self.logger.table_header += 'GPU'.rjust(3)

        if args.power_usage:
            try:
                gpu_metrics_info = amdsmi_interface.amdsmi_get_gpu_metrics_info(args.gpu)
                power_usage = gpu_metrics_info['current_socket_power']
                if power_usage >= 0xFFFFFFFF:
                    power_usage = gpu_metrics_info['average_socket_power']
                    if power_usage >= 0xFFFFFFFF:
                        power_usage = "N/A"
                monitor_values['power_usage'] = power_usage
                if self.logger.is_human_readable_format() and monitor_values['power_usage'] != "N/A":
                    monitor_values['power_usage'] = f"{monitor_values['power_usage']} W"
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['power_usage'] = "N/A"
                logging.debug("Failed to get power usage on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.table_header += 'POWER'.rjust(7)
        if args.temperature:
            try:
                temperature = amdsmi_interface.amdsmi_get_gpu_metrics_info(args.gpu)['temperature_hotspot']
                monitor_values['hotspot_temperature'] = temperature
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['hotspot_temperature'] = "N/A"
                logging.debug("Failed to get hotspot temperature on gpu %s | %s", gpu_id, e.get_error_info())

            try:
                temperature = amdsmi_interface.amdsmi_get_gpu_metrics_temp_mem(args.gpu)
                monitor_values['memory_temperature'] = temperature
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['memory_temperature'] = "N/A"
                logging.debug("Failed to get memory temperature on gpu %s | %s", gpu_id, e.get_error_info())

            if self.logger.is_human_readable_format() and monitor_values['hotspot_temperature'] != "N/A":
                monitor_values['hotspot_temperature'] = f"{monitor_values['hotspot_temperature']} \N{DEGREE SIGN}C"

            if self.logger.is_human_readable_format() and monitor_values['memory_temperature'] != "N/A":
                monitor_values['memory_temperature'] = f"{monitor_values['memory_temperature']} \N{DEGREE SIGN}C"

            self.logger.table_header += 'GPU_TEMP'.rjust(10)
            self.logger.table_header += 'MEM_TEMP'.rjust(10)
        if args.gfx:
            try:
                gfx_util = amdsmi_interface.amdsmi_get_gpu_metrics_avg_gfx_activity(args.gpu)
                monitor_values['gfx'] = gfx_util
                if self.logger.is_human_readable_format():
                    monitor_values['gfx'] = f"{monitor_values['gfx']} %"
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['gfx'] = "N/A"
                logging.debug("Failed to get gfx utilization on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.table_header += 'GFX_UTIL'.rjust(10)

            try:
                gfx_clock = amdsmi_interface.amdsmi_get_gpu_metrics_info(args.gpu)['current_gfxclk']
                monitor_values['gfx_clock'] = gfx_clock
                if self.logger.is_human_readable_format():
                    monitor_values['gfx_clock'] = f"{monitor_values['gfx_clock']} MHz"
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['gfx_clock'] = "N/A"
                logging.debug("Failed to get gfx clock on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.table_header += 'GFX_CLOCK'.rjust(11)
        if args.mem:
            try:
                mem_util = amdsmi_interface.amdsmi_get_gpu_metrics_avg_umc_activity(args.gpu)
                monitor_values['mem'] = mem_util
                if self.logger.is_human_readable_format():
                    monitor_values['mem'] = f"{monitor_values['mem']} %"
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['mem'] = "N/A"
                logging.debug("Failed to get mem utilization on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.table_header += 'MEM_UTIL'.rjust(10)

            try:
                mem_clock = amdsmi_interface.amdsmi_get_gpu_metrics_info(args.gpu)['current_uclk']
                monitor_values['mem_clock'] = mem_clock
                if self.logger.is_human_readable_format():
                    monitor_values['mem_clock'] = f"{monitor_values['mem_clock']} MHz"
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['mem_clock'] = "N/A"
                logging.debug("Failed to get mem clock on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.table_header += 'MEM_CLOCK'.rjust(11)
        if args.encoder:
            try:
                # Get List of vcn activity values
                encoder_util = amdsmi_interface.amdsmi_get_gpu_metrics_vcn_activity(args.gpu)
                encoding_activity_avg = []
                for value in encoder_util:
                    if value < 150: # each encoder chiplet's value range should be a percent
                        encoding_activity_avg.append(value)
                # Averaging the possible encoding activity values
                if encoding_activity_avg:
                    encoding_activity_avg = sum(encoding_activity_avg) / len(encoding_activity_avg)
                else:
                    encoding_activity_avg = "N/A"
                monitor_values['encoder'] = encoding_activity_avg
                if self.logger.is_human_readable_format() and monitor_values['encoder'] != "N/A":
                    monitor_values['encoder'] = f"{monitor_values['encoder']} %"
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['encoder'] = "N/A"
                logging.debug("Failed to get encoder utilization on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.table_header += 'ENC_UTIL'.rjust(10)

            try:
                encoder_clock = amdsmi_interface.amdsmi_get_gpu_metrics_info(args.gpu)['current_vclk0']
                monitor_values['encoder_clock'] = encoder_clock
                if self.logger.is_human_readable_format():
                    monitor_values['encoder_clock'] = f"{monitor_values['encoder_clock']} MHz"
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['encoder_clock'] = "N/A"
                logging.debug("Failed to get encoder clock on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.table_header += 'ENC_CLOCK'.rjust(11)
        if args.decoder:
            try:
                decoder_util = "N/A" # Not yet implemented
                monitor_values['decoder'] = decoder_util
                # if self.logger.is_human_readable_format():
                #     monitor_values['decoder'] = f"{monitor_values['decoder']} %"
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['decoder'] = "N/A"
                logging.debug("Failed to get decoder utilization on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.table_header += 'DEC_UTIL'.rjust(10)

            try:
                decoder_clock = amdsmi_interface.amdsmi_get_gpu_metrics_info(args.gpu)['current_dclk0']
                monitor_values['decoder_clock'] = decoder_clock
                if self.logger.is_human_readable_format():
                    monitor_values['decoder_clock'] = f"{monitor_values['decoder_clock']} MHz"
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['decoder_clock'] = "N/A"
                logging.debug("Failed to get decoder clock on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.table_header += 'DEC_CLOCK'.rjust(11)
        if args.throttle_status:
            try:
                throttle_status = amdsmi_interface.amdsmi_get_gpu_metrics_throttle_status(args.gpu)
                if throttle_status:
                    throttle_status = "THROTTLED"
                else:
                    throttle_status = "UNTHROTTLED"
                monitor_values['throttle_status'] = throttle_status
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['throttle_status'] = "N/A"
                logging.debug("Failed to get throttle status on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.table_header += 'THROTTLE'.rjust(13)
        if args.ecc:
            try:
                ecc = amdsmi_interface.amdsmi_get_gpu_total_ecc_count(args.gpu)
                monitor_values['single_bit_ecc'] = ecc['correctable_count']
                monitor_values['double_bit_ecc'] = ecc['uncorrectable_count']
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['ecc'] = "N/A"
                logging.debug("Failed to get ecc on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.table_header += 'SINGLE_ECC'.rjust(12)
            self.logger.table_header += 'DOUBLE_ECC'.rjust(12)

            try:
                pcie_replay = amdsmi_interface.amdsmi_get_gpu_pci_replay_counter(args.gpu)
                monitor_values['pcie_replay'] = pcie_replay
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['pcie_replay'] = "N/A"
                logging.debug("Failed to get pcie replay counter on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.table_header += 'PCIE_REPLAY'.rjust(13)
        if args.vram_usage:
            try:
                vram_usage = amdsmi_interface.amdsmi_get_gpu_vram_usage(args.gpu)
                monitor_values['vram_used'] = vram_usage['vram_used']
                monitor_values['vram_total'] = vram_usage['vram_total']
                if self.logger.is_human_readable_format():
                    monitor_values['vram_used'] = f"{monitor_values['vram_used']} MB"
                    monitor_values['vram_total'] = f"{monitor_values['vram_total']} MB"
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['vram_used'] = "N/A"
                monitor_values['vram_total'] = "N/A"
                logging.debug("Failed to get vram memory usage on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.table_header += 'VRAM_USED'.rjust(11)
            self.logger.table_header += 'VRAM_TOTAL'.rjust(12)
        if args.pcie:
            try:
                pcie_bw = amdsmi_interface.amdsmi_get_gpu_pci_throughput(args.gpu)
                sent = pcie_bw['sent'] * pcie_bw['max_pkt_sz']
                received = pcie_bw['received'] * pcie_bw['max_pkt_sz']

                if self.logger.is_human_readable_format():
                    if sent > 0:
                        sent = sent // 1024 // 1024
                    sent = f"{sent} MB/s"

                    if received > 0:
                        received = received // 1024 // 1024
                    received = f"{received} MB/s"
                    pcie_bw['max_pkt_sz'] = f"{pcie_bw['max_pkt_sz']} B"

                monitor_values['pcie_tx'] = sent
                monitor_values['pcie_rx'] = received
            except amdsmi_exception.AmdSmiLibraryException as e:
                monitor_values['pcie_tx'] = "N/A"
                monitor_values['pcie_rx'] = "N/A"
                logging.debug("Failed to get pci throughput on gpu %s | %s", gpu_id, e.get_error_info())

            self.logger.table_header += 'PCIE_TX'.rjust(10)
            self.logger.table_header += 'PCIE_RX'.rjust(10)

        self.logger.store_output(args.gpu, 'values', monitor_values)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output(watching_output=watching_output, tabular=True)

        if watching_output: # End of single gpu add to watch_output
            self.logger.store_watch_output(multiple_device_enabled=False)


    def rocm_smi(self, args):
        print("Placeholder for rocm-smi legacy commands")


    def _event_thread(self, commands, i):
        devices = commands.device_handles
        if len(devices) == 0:
            print("No GPUs on machine")
            return

        device = devices[i]
        listener = amdsmi_interface.AmdSmiEventReader(device,
                                        amdsmi_interface.AmdSmiEvtNotificationType)
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
                if e.err_code != amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_NO_DATA:
                    print(e)
            except Exception as e:
                print(e)

        listener.stop()

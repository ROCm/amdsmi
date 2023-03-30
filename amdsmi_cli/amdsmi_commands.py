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

"""AMDSMICommands

This class contains all the commands corresponding to AMDSMIParser
Each command function will interact with AMDSMILogger to handle
displaying the output to the specified compatibility, format, and
destination.

"""

import threading

from _version import __version__
from amdsmi_helpers import AMDSMIHelpers
from amdsmi_logger import AMDSMILogger
from amdsmi import amdsmi_interface
from amdsmi import amdsmi_exception


class AMDSMICommands():
    def __init__(self, compatibility='amdsmi',
                    format='human_readable',
                    destination='stdout') -> None:
        self.helpers = AMDSMIHelpers()
        self.logger = AMDSMILogger(compatibility=compatibility,
                                    format=format,
                                    destination=destination)
        try:
            self.device_handles = amdsmi_interface.amdsmi_get_device_handles()
        except amdsmi_exception.AmdSmiLibraryException as e:
            raise e
        self.stop = ''

    def version(self, args):
        """Print Version String

        Args:
            args (Namespace): Namespace containing the parsed CLI args
        """
        kernel_component = amdsmi_interface.AmdSmiSwComponent.DRIVER

        try:
            kernel_version = amdsmi_interface.amdsmi_get_version_str(sw_component=kernel_component)
        except amdsmi_exception.AmdSmiLibraryException as e:
            kernel_version = e.get_error_info()

        try:
            amdsmi_lib_version = amdsmi_interface.amdsmi_get_version()
        except amdsmi_exception.AmdSmiLibraryException as e:
            amdsmi_lib_version = e.get_error_info()

        major = amdsmi_lib_version["major"]
        minor = amdsmi_lib_version["minor"]
        patch = amdsmi_lib_version["patch"]
        amdsmi_lib_version_str = f'{major}.{minor}.{patch}'

        self.logger.output['tool'] = 'AMDSMI Tool'
        self.logger.output['version'] = f'{__version__}'
        self.logger.output['amdsmi_library_version'] = f'{amdsmi_lib_version_str}'
        self.logger.output['kernel_version'] = f'{kernel_version}'

        if self.logger.is_human_readable_format():
            print(f'AMDSMI Tool: {__version__} | '\
                    f'AMDSMI Library version: {amdsmi_lib_version_str} | '\
                    f'Kernel version: {kernel_version}')
        elif self.logger.is_json_format() or self.logger.is_csv_format():
            self.logger.print_output()


    def discovery(self, args, multiple_devices=False, gpu=None):
        """Get Discovery information for target gpu

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
        if args.gpu is None:
            args.gpu = self.device_handles

        # Handle multiple GPUs
        handled_multiple_gpus, device_handle = self.helpers.handle_gpus(args, self.logger, self.discovery)
        if handled_multiple_gpus:
            return # This function is recursive

        args.gpu = device_handle

        try:
            bdf = amdsmi_interface.amdsmi_get_device_bdf(args.gpu)
        except amdsmi_exception.AmdSmiLibraryException as e:
            bdf = e.get_error_info()

        try:
            uuid = amdsmi_interface.amdsmi_get_device_uuid(args.gpu)
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
            self.logger.print_output(multiple_device_output=True)
        else:
            self.logger.print_output()


    def static(self, args, multiple_devices=False, gpu=None, asic=None,
                bus=None, vbios=None, limit=None, driver=None, caps=None,
                ras=None, board=None):
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
            caps (bool, optional): Value override for args.caps. Defaults to None.
            ras (bool, optional): Value override for args.ras. Defaults to None.
            board (bool, optional): Value override for args.board. Defaults to None.

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
        if limit:
            args.limit = limit
        if driver:
            args.driver = driver
        if caps:
            args.caps = caps
        if ras:
            args.ras = ras
        if board:
            args.board = board

        # Handle No GPU passed
        if args.gpu is None:
            args.gpu = self.device_handles

        # Handle multiple GPUs
        handled_multiple_gpus, device_handle = self.helpers.handle_gpus(args, self.logger, self.static)
        if handled_multiple_gpus:
            return # This function is recursive

        args.gpu = device_handle

        # If all arguments are False, it means that no argument was passed and the entire static should be printed
        if not any([args.asic, args.bus, args.vbios, args.limit, args.driver, args.caps, args.ras, args.board]):
            args.asic = args.bus = args.vbios = args.limit = args.driver = args.caps = args.ras = args.board = True

        values_dict = {}

        if args.asic:
            try:
                asic_info = amdsmi_interface.amdsmi_get_asic_info(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                asic_info = e.get_error_info()

            asic_info['family'] = hex(asic_info['family'])
            asic_info['vendor_id'] = hex(asic_info['vendor_id'])
            asic_info['device_id'] = hex(asic_info['device_id'])
            asic_info['rev_id'] = hex(asic_info['rev_id'])
            if asic_info['asic_serial'] != '':
                asic_info['asic_serial'] = '0x' + asic_info['asic_serial']

            values_dict['asic'] = asic_info
        if args.bus:
            try:
                bus_info = amdsmi_interface.amdsmi_get_pcie_link_caps(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                bus_info = e.get_error_info()

            if self.logger.is_human_readable_format():
                unit ='MT/s'
                bus_info['pcie_speed'] = f"{bus_info['pcie_speed']} {unit}"

            bus_output_info = {}
            try:
                bus_output_info['bdf'] = amdsmi_interface.amdsmi_get_device_bdf(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                bus_output_info['bdf'] = e.get_error_info()

            bus_output_info.update(bus_info)

            values_dict['bus'] = bus_output_info
        if args.vbios:
            try:
                vbios_info = amdsmi_interface.amdsmi_get_vbios_info(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                vbios_info = e.get_error_info()


            if self.logger.is_gpuvsmi_compatibility():
                vbios_info['version'] = vbios_info.pop('vbios_version_string')
                vbios_info['build_date'] = vbios_info.pop('build_date')
                vbios_info['part_number'] = vbios_info.pop('part_number')
                vbios_info['vbios_version'] = vbios_info.pop('vbios_version')

            values_dict['vbios'] = vbios_info
        if args.board:
            try:
                board_info = amdsmi_interface.amdsmi_get_board_info(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                board_info = e.get_error_info()

            board_info['serial_number'] = hex(board_info['serial_number'])
            board_info['product_serial'] = '0x' + board_info['product_serial']
            board_info['product_name'] = board_info['product_name'].strip()

            if self.logger.is_gpuvsmi_compatibility():
                board_info['product_number'] = board_info.pop('product_serial')

            values_dict['board'] = board_info
        if args.limit:
            try:
                power_limit = amdsmi_interface.amdsmi_get_power_measure(args.gpu)['power_limit']
            except amdsmi_exception.AmdSmiLibraryException as e:
                power_limit = e.get_error_info()

            try:
                temp_edge_limit = amdsmi_interface.amdsmi_dev_get_temp_metric(args.gpu,
                    amdsmi_interface.AmdSmiTemperatureType.EDGE, amdsmi_interface.AmdSmiTemperatureMetric.CRITICAL)
            except amdsmi_exception.AmdSmiLibraryException as e:
                temp_edge_limit = e.get_error_info()

            try:
                temp_junction_limit = amdsmi_interface.amdsmi_dev_get_temp_metric(args.gpu,
                    amdsmi_interface.AmdSmiTemperatureType.JUNCTION, amdsmi_interface.AmdSmiTemperatureMetric.CRITICAL)
            except amdsmi_exception.AmdSmiLibraryException as e:
                temp_junction_limit = e.get_error_info()

            try:
                temp_vram_limit = amdsmi_interface.amdsmi_dev_get_temp_metric(args.gpu,
                    amdsmi_interface.AmdSmiTemperatureType.VRAM, amdsmi_interface.AmdSmiTemperatureMetric.CRITICAL)
            except amdsmi_exception.AmdSmiLibraryException as e:
                temp_vram_limit = e.get_error_info()

            if self.logger.is_human_readable_format():
                unit = 'W'
                power_limit = f"{power_limit} {unit}"

                unit = 'C'
                temp_edge_limit = f"{temp_edge_limit} {unit}"
                temp_junction_limit = f"{temp_junction_limit} {unit}"
                temp_vram_limit = f"{temp_vram_limit} {unit}"

            limit_info = {}
            limit_info['power'] = power_limit
            limit_info['temperature_edge'] = temp_edge_limit
            limit_info['temperature_junction'] = temp_junction_limit
            limit_info['temperature_vram'] = temp_vram_limit

            values_dict['limit'] = limit_info
        if args.driver:
            driver_info = {}
            try:
                driver_info['driver_version'] = amdsmi_interface.amdsmi_get_driver_version(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                driver_info['driver_version'] = e.get_error_info()

            values_dict['driver'] = driver_info
        if args.ras:
            try:
                values_dict['ras'] = amdsmi_interface.amdsmi_get_ras_block_features_enabled(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                values_dict['ras'] = e.get_error_info()

        if args.caps:
            try:
                caps_info = amdsmi_interface.amdsmi_get_caps_info(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                caps_info = e.get_error_info()

            if self.logger.is_gpuvsmi_compatibility():
                del caps_info['ras_supported']
                caps_info['gfx'] = caps_info.pop('gfx')

            if self.logger.is_human_readable_format():
                for capability_name, capability_value in caps_info.items():
                    if isinstance(capability_value, list):
                        caps_info[capability_name] = f"{capability_value}"

            values_dict['caps'] = caps_info

        # Store values in logger.output
        self.logger.store_output(args.gpu, 'values', values_dict)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output()


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
        if args.gpu is None:
            args.gpu = self.device_handles

        # Handle multiple GPUs
        handled_multiple_gpus, device_handle = self.helpers.handle_gpus(args, self.logger, self.firmware)
        if handled_multiple_gpus:
            return # This function is recursive

        args.gpu = device_handle

        values_dict = {}

        if args.fw_list:
            try:
                fw_info = amdsmi_interface.amdsmi_get_fw_info(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                fw_info = e.get_error_info()

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

            values_dict.update(fw_info)

        # Store values in logger.output
        self.logger.store_output(args.gpu, 'values', values_dict)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output()


    def bad_pages(self, args, multiple_devices=False, gpu=None, retired=None, pending=None, un_res=None):
        """ Get bad pages information for target gpu

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            gpu (device_handle, optional): device_handle for target device. Defaults to None.
            retired (bool, optional) - Value override for args.retired
            pending (bool, optional) - Value override for args.pending
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
        if args.gpu is None:
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
            bad_page_info = amdsmi_interface.amdsmi_get_bad_page_info(args.gpu)
            bad_page_error = False
        except amdsmi_exception.AmdSmiLibraryException as e:
            bad_page_info = ""
            bad_page_err_output = e.get_error_info()
            bad_page_error = True

        if isinstance(bad_page_info, str):
            pass
        else:
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
                clock=None, temperature=None, ecc=None, pcie=None, voltage=None, fan=None,
                pcie_usage=None, voltage_curve=None, overdrive=None, mem_overdrive=None,
                perf_level=None, replay_count=None, xgmi_err=None, energy=None, mem_usage=None):
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
            pcie (bool, optional): Value override for args.pcie. Defaults to None.
            voltage (bool, optional): Value override for args.voltage. Defaults to None.
            fan (bool, optional): Value override for args.fan. Defaults to None.
            pcie_usage (bool, optional): Value override for args.pcie_usage. Defaults to None.
            voltage_curve (bool, optional): Value override for args.voltage_curve. Defaults to None.
            overdrive (bool, optional): Value override for args.overdrive. Defaults to None.
            mem_overdrive (bool, optional): Value override for args.mem_overdrive. Defaults to None.
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
        if usage:
            args.usage = usage
        if watch:
            args.watch = watch
        if watch_time:
            args.watch_time = watch_time
        if iterations:
            args.iterations = iterations
        if fb_usage:
            args.fb_usage = fb_usage
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
        if voltage:
            args.voltage = voltage
        if fan:
            args.fan = fan
        if pcie_usage:
            args.pcie_usage = pcie_usage
        if voltage_curve:
            args.voltage_curve = voltage_curve
        if overdrive:
            args.overdrive = overdrive
        if mem_overdrive:
            args.mem_overdrive = mem_overdrive
        if perf_level:
            args.perf_level = perf_level
        if replay_count:
            args.replay_count = replay_count
        if xgmi_err:
            args.xgmi_err = xgmi_err
        if energy:
            args.energy = energy
        if mem_usage:
            args.mem_usage = mem_usage

        # Handle No GPU passed
        if args.gpu is None:
            args.gpu = self.device_handles

        # Handle watch logic, will only enter this block once
        if args.watch:
            self.helpers.handle_watch(args=args, subcommand=self.metric)
            self.logger.print_output(watch_output=True) # Print at the end of watch ( final flush )

        # Handle multiple GPUs
        if isinstance(args.gpu, list):
            if len(args.gpu) > 1:
                for device_handle in args.gpu:
                    # Handle multiple_devices to print all output at once
                    self.metric(args, multiple_devices=True, watching_output=False, gpu=device_handle)
                self.logger.print_output(multiple_device_output=True)

                # End of multiple gpus add to watch_output
                if watching_output:
                    self.logger.store_watch_output(multiple_devices=True)

                return
            elif len(args.gpu) == 1:
                args.gpu = args.gpu[0]
            else:
                raise IndexError("args.gpu should not be an empty list")

        # Check if any of the options have been set, if not then set them all to true
        if not any([args.usage, args.fb_usage, args.power, args.clock, args.temperature, args.ecc, args.pcie, args.voltage, args.fan,
                    args.pcie_usage, args.voltage_curve, args.overdrive, args.mem_overdrive, args.perf_level,
                    args.replay_count, args.xgmi_err, args.energy, args.mem_usage]):
            args.usage = args.fb_usage = args.power = args.clock = args.temperature = args.ecc = args.pcie = args.voltage = args.fan = \
            args.pcie_usage = args.voltage_curve = args.overdrive = args.mem_overdrive = args.perf_level = \
            args.replay_count = args.xgmi_err = args.energy = args.mem_usage = True

        # Add timestamp and store values for specified arguments
        values_dict = {}
        if args.usage:
            try:
                engine_usage = amdsmi_interface.amdsmi_get_gpu_activity(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                engine_usage = e.get_error_info()

            if self.logger.is_gpuvsmi_compatibility():
                engine_usage['gfx_usage'] = engine_usage.pop('gfx_activity')
                engine_usage['mem_usage'] = engine_usage.pop('umc_activity')
                engine_usage['mm_usage_list'] = engine_usage.pop('mm_activity')

            if self.logger.is_human_readable_format():
                unit = '%'
                for usage_name, usage_value in engine_usage.items():
                    engine_usage[usage_name] = f"{usage_value} {unit}"

            values_dict['usage'] = engine_usage
        if args.fb_usage:
            try:
                vram_usage = amdsmi_interface.amdsmi_get_vram_usage(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                vram_usage = e.get_error_info()

            if self.logger.is_gpuvsmi_compatibility():
                vram_usage['fb_total'] = vram_usage.pop('vram_total')
                vram_usage['fb_used'] = vram_usage.pop('vram_used')

            if self.logger.is_human_readable_format():
                unit = 'MB'
                for vram_name, vram_value in vram_usage.items():
                    vram_usage[vram_name] = f"{vram_value} {unit}"

            values_dict['fb_usage'] = vram_usage
        if args.power:
            try:
                average_socket_power = amdsmi_interface.amdsmi_get_power_measure(args.gpu)['average_socket_power']
            except amdsmi_exception.AmdSmiLibraryException as e:
                average_socket_power = e.get_error_info()

            if self.logger.is_gpuvsmi_compatibility():
                pass

            if self.logger.is_human_readable_format():
                unit = 'W'
                average_socket_power = f"{average_socket_power} {unit}"

            values_dict['power'] = average_socket_power
        if args.clock:
            try:
                clock_gfx = amdsmi_interface.amdsmi_get_clock_measure(args.gpu, amdsmi_interface.AmdSmiClkType.GFX)
            except amdsmi_exception.AmdSmiLibraryException as e:
                clock_gfx = e.get_error_info()

            try:
                clock_mem = amdsmi_interface.amdsmi_get_clock_measure(args.gpu, amdsmi_interface.AmdSmiClkType.MEM)
            except amdsmi_exception.AmdSmiLibraryException as e:
                clock_mem = e.get_error_info()

            clocks = {'gfx': clock_gfx,
                     'mem': clock_mem}

            if self.logger.is_human_readable_format():
                unit = 'MHz'
                for clock_target, clock_metric_values in clocks.items():
                    for clock_type, clock_value in clock_metric_values.items():
                        clocks[clock_target][clock_type] = f"{clock_value} {unit}"

            values_dict['clock'] = clocks
        if args.temperature:
            try:
                temperature_edge_current = amdsmi_interface.amdsmi_dev_get_temp_metric(
                    args.gpu, amdsmi_interface.AmdSmiTemperatureType.EDGE, amdsmi_interface.AmdSmiTemperatureMetric.CURRENT)
            except amdsmi_exception.AmdSmiLibraryException as e:
                temperature_edge_current = e.get_error_info()

            try:
                temperature_junction_current = amdsmi_interface.amdsmi_dev_get_temp_metric(
                    args.gpu, amdsmi_interface.AmdSmiTemperatureType.JUNCTION, amdsmi_interface.AmdSmiTemperatureMetric.CURRENT)
            except amdsmi_exception.AmdSmiLibraryException as e:
                temperature_junction_current = e.get_error_info()

            try:
                temperature_vram_current = amdsmi_interface.amdsmi_dev_get_temp_metric(
                    args.gpu, amdsmi_interface.AmdSmiTemperatureType.VRAM, amdsmi_interface.AmdSmiTemperatureMetric.CURRENT)
            except amdsmi_exception.AmdSmiLibraryException as e:
                temperature_vram_current = e.get_error_info()

            temperatures = { 'edge': temperature_edge_current,
                             'hotspot': temperature_junction_current,
                             'mem': temperature_vram_current}

            if self.logger.is_gpuvsmi_compatibility():
                temperatures = { 'edge_temperature': temperature_edge_current,
                                'hotspot_temperature': temperature_junction_current,
                                'mem_temperature': temperature_vram_current}

            if self.logger.is_human_readable_format():
                unit = '\N{DEGREE SIGN}C'
                for temperature_value in temperatures:
                    temperatures[temperature_value] = f"{temperatures[temperature_value]} {unit}"

            values_dict['temperature'] = temperatures
        if args.ecc:
            try:
                values_dict['ecc'] = amdsmi_interface.amdsmi_get_ecc_error_count(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                values_dict['ecc'] = e.get_error_info()

        if args.pcie:
            try:
                pcie_link_status = amdsmi_interface.amdsmi_get_pcie_link_caps(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                pcie_link_status = e.get_error_info()

            if self.logger.is_human_readable_format():
                unit ='MT/s'
                pcie_link_status['pcie_speed'] = f"{pcie_link_status['pcie_speed']} {unit}"

            if self.logger.is_gpuvsmi_compatibility():
                pcie_link_status['current_width'] = pcie_link_status.pop('pcie_lanes')
                pcie_link_status['current_speed'] = pcie_link_status.pop('pcie_speed')

            values_dict['pcie'] = pcie_link_status
        if args.voltage:
            try:
                volt_metric = amdsmi_interface.amdsmi_dev_get_volt_metric(
                    args.gpu, amdsmi_interface.AmdSmiVoltageType.VDDGFX, amdsmi_interface.AmdSmiVoltageMetric.CURRENT)
            except amdsmi_exception.AmdSmiLibraryException as e:
                volt_metric = e.get_error_info()

            if self.logger.is_human_readable_format():
                unit = 'mV'
                volt_metric = f"{volt_metric} {unit}"

            values_dict['voltage'] = volt_metric
        if args.fan:
            try:
                fan_speed = amdsmi_interface.amdsmi_dev_get_fan_speed(args.gpu, 0)
            except amdsmi_exception.AmdSmiLibraryException as e:
                fan_speed = e.get_error_info()

            try:
                fan_max = amdsmi_interface.amdsmi_dev_get_fan_speed_max(args.gpu, 0)
                if isinstance(fan_speed, int) and fan_max > 0:
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
                fan_rpm = amdsmi_interface.amdsmi_dev_get_fan_rpms(args.gpu, 0)
            except amdsmi_exception.AmdSmiLibraryException as e:
                fan_rpm = e.get_error_info()

            values_dict['fan'] = {'speed': fan_speed,
                                    'max' : fan_max,
                                    'rpm' : fan_rpm,
                                    'usage' : fan_percent}
        if args.pcie_usage:
            try:
                pcie_link_status = amdsmi_interface.amdsmi_get_pcie_link_status(args.gpu)
                pcie_link_status_call = True
            except amdsmi_exception.AmdSmiLibraryException as e:
                pcie_link_status = e.get_error_info()
                pcie_link_status_call = False

            if self.logger.is_human_readable_format() and pcie_link_status_call:
                unit ='MT/s'
                pcie_link_status['pcie_speed'] = f"{pcie_link_status['pcie_speed']} {unit}"

            values_dict['pcie_usage'] = pcie_link_status
        if args.voltage_curve:
            try:
                od_volt = amdsmi_interface.amdsmi_dev_get_od_volt_info(args.gpu)
                voltage_curve_error = False
            except amdsmi_exception.AmdSmiLibraryException as e:
                od_volt = None
                values_dict["voltage_curve"] = e.get_error_info()
                voltage_curve_error = True

            if not voltage_curve_error:
                voltage_point_dict = {}

                for point in range(3):
                    if isinstance(od_volt, dict):
                        frequency = int(od_volt["curve.vc_points"][point].frequency / 1000000)
                        voltage = int(od_volt["curve.vc_points"][point].voltage)
                    else:
                        frequency = 0
                        voltage = 0
                    voltage_point_dict[f'voltage_point_{point}'] = f"{frequency}Mhz {voltage}mV"

                values_dict['voltage_curve'] = voltage_point_dict
        if args.overdrive:
            try:
                overdrive_level = amdsmi_interface.amdsmi_dev_get_overdrive_level(args.gpu)
                if self.logger.is_human_readable_format():
                    unit = '%'
                    overdrive_level = f"{overdrive_level} {unit}"
            except amdsmi_exception.AmdSmiLibraryException as e:
                overdrive_level = e.get_error_info()

            values_dict['overdrive'] = overdrive_level
        if args.mem_overdrive:
            values_dict['mem_overdrive'] = amdsmi_interface.AmdSmiRetCode.NOT_IMPLEMENTED

        if args.perf_level:
            try:
                values_dict['perf_level'] = amdsmi_interface.amdsmi_dev_get_perf_level(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                values_dict['perf_level'] = e.get_error_info()

        if args.replay_count:
            try:
                values_dict['replay_count'] = amdsmi_interface.amdsmi_dev_get_pci_replay_counter(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                values_dict['replay_count'] = e.get_error_info()

        if args.xgmi_err:
            try:
                values_dict['xgmi_err'] = amdsmi_interface.amdsmi_dev_xgmi_error_status(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                values_dict['xgmi_err'] = e.get_error_info()

        if args.energy:
            try:
                energy = amdsmi_interface.amdsmi_get_power_measure(args.gpu)['energy_accumulator']
                if self.logger.is_human_readable_format():
                    unit = 'J'
                    energy = f"{energy} {unit}"
            except amdsmi_exception.AmdSmiLibraryException as e:
                energy = e.get_error_info()

            values_dict['energy'] = energy
        if args.mem_usage:
            unit = 'MB'
            memory_total = {}

            try:
                total_vram = amdsmi_interface.amdsmi_dev_get_memory_total(args.gpu, amdsmi_interface.AmdSmiMemoryType.VRAM)
                memory_total['vram'] = total_vram // (1024*1024)
                if self.logger.is_human_readable_format():
                    memory_total['vram'] = f"{memory_total['vram']} {unit}"
            except amdsmi_exception.AmdSmiLibraryException as e:
                memory_total['vram'] = e.get_error_info()

            try:
                total_vis_vram = amdsmi_interface.amdsmi_dev_get_memory_total(args.gpu, amdsmi_interface.AmdSmiMemoryType.VIS_VRAM)
                memory_total['vis_vram'] = total_vis_vram // (1024*1024)
                if self.logger.is_human_readable_format():
                    memory_total['vis_vram'] = f"{memory_total['vis_vram']} {unit}"
            except amdsmi_exception.AmdSmiLibraryException as e:
                memory_total['vis_vram'] = e.get_error_info()

            try:
                total_gtt = amdsmi_interface.amdsmi_dev_get_memory_total(args.gpu, amdsmi_interface.AmdSmiMemoryType.GTT)
                memory_total['gtt'] = total_gtt // (1024*1024)
                if self.logger.is_human_readable_format():
                    memory_total['gtt'] = f"{memory_total['gtt']} {unit}"
            except amdsmi_exception.AmdSmiLibraryException as e:
                memory_total['gtt'] = e.get_error_info()

            try:
                total_used_vram = amdsmi_interface.amdsmi_dev_get_memory_usage(args.gpu, amdsmi_interface.AmdSmiMemoryType.VRAM)
                memory_total['used_vram'] = total_used_vram // (1024*1024)
                if self.logger.is_human_readable_format():
                    memory_total['used_vram'] = f"{memory_total['used_vram']} {unit}"
            except amdsmi_exception.AmdSmiLibraryException as e:
                memory_total['used_vram'] = e.get_error_info()

            try:
                total_used_vis_vram = amdsmi_interface.amdsmi_dev_get_memory_usage(args.gpu, amdsmi_interface.AmdSmiMemoryType.VIS_VRAM)
                memory_total['used_vis_vram'] = total_used_vis_vram // (1024*1024)
                if self.logger.is_human_readable_format():
                    memory_total['used_vis_vram'] = f"{memory_total['used_vis_vram']} {unit}"
            except amdsmi_exception.AmdSmiLibraryException as e:
                memory_total['used_vis_vram'] = e.get_error_info()

            try:
                total_used_gtt = amdsmi_interface.amdsmi_dev_get_memory_usage(args.gpu, amdsmi_interface.AmdSmiMemoryType.GTT)
                memory_total['used_gtt'] = total_used_gtt // (1024*1024)
                if self.logger.is_human_readable_format():
                    memory_total['used_gtt'] = f"{memory_total['used_gtt']} {unit}"
            except amdsmi_exception.AmdSmiLibraryException as e:
                memory_total['used_gtt'] = e.get_error_info()

            values_dict['mem_usage'] = memory_total

        # Store values in logger.output
        self.logger.store_output(args.gpu, 'values', values_dict)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output()

        if watching_output: # End of single gpu add to watch_output
            self.logger.store_watch_output(multiple_devices=False)


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
        if args.gpu is None:
            args.gpu = self.device_handles

        # Handle watch logic, will only enter this block once
        if args.watch:
            args = self.helpers.handle_watch(args=args, subcommand=self.process)
            self.logger.print_output(watch_output=True) # Print at the end of watch ( final flush )
            return

        # Handle multiple GPUs
        if isinstance(args.gpu, list):
            if len(args.gpu) > 1:
                for device_handle in args.gpu:
                    # Handle multiple_devices to print all output at once
                    self.process(args, multiple_devices=True, watching_output=False, gpu=device_handle)
                self.logger.print_output(multiple_device_output=True)

                # End of multiple gpus add to watch_output
                if watching_output:
                    self.logger.store_watch_output(multiple_devices=True)

                return
            elif len(args.gpu) == 1:
                args.gpu = args.gpu[0]
            else:
                raise IndexError("args.gpu should not be an empty list")

        # Populate initial processes
        try:
            process_list = amdsmi_interface.amdsmi_get_process_list(args.gpu)
        except amdsmi_exception.AmdSmiLibraryException as e:
            raise e

        filtered_process_values = []
        for process_handle in process_list:
            try:
                process_info = amdsmi_interface.amdsmi_get_process_info(args.gpu, process_handle)
            except amdsmi_exception.AmdSmiLibraryException as e:
                process_info = e.get_error_info()
                filtered_process_values.append({'process_info': process_info})
                continue

            process_info['mem_usage'] = process_info.pop('mem')
            process_info['usage'] = process_info.pop('engine_usage')

            # Convert mem_usage to megabytes

            mem_usage_mb = (process_info['mem_usage']//1024) // 1024
            if mem_usage_mb < 0:
                process_info['mem_usage'] = (process_info['mem_usage']//1024)
                mem_usage_unit = 'B'
            else:
                process_info['mem_usage'] = mem_usage_mb

            if self.logger.is_human_readable_format():
                mem_usage_unit = 'MB'
                engine_usage_unit = '%'
                process_info['mem_usage'] = f"{process_info['mem_usage']} {mem_usage_unit}"

                for usage_metric in process_info['usage']:
                    process_info['usage'][usage_metric] = f"{process_info['usage'][usage_metric]} {engine_usage_unit}"
                for usage_metric in process_info['memory_usage']:
                    process_info['memory_usage'][usage_metric] = f"{process_info['memory_usage'][usage_metric]} {engine_usage_unit}"

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

        # Remove brackets if there is only one value
        if len(filtered_process_values) == 1:
            filtered_process_values = filtered_process_values[0]

        # Store values in logger.output
        if filtered_process_values == []:
            self.logger.store_output(args.gpu, 'values', {'process_info': 'Not Found'})
        else:
            self.logger.store_output(args.gpu, 'values', filtered_process_values)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output()

        if watching_output: # End of single gpu add to watch_output
            self.logger.store_watch_output(multiple_devices=False)


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
                weight=None, hops=None, type=None, numa=None, numa_bw=None):
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
                numa (bool) - Value override for args.numa
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
        if type:
            args.type = type
        if numa:
            args.numa = numa
        if numa_bw:
            args.numa_bw = numa_bw

        # Handle No GPU passed
        if args.gpu is None:
            args.gpu = self.device_handles

        # Handle all args being false

        # If all arguments are False, it means that no argument was passed and the entire topology should be printed
        # if not any([args.asic, args.bus, args.vbios, args.limit, args.driver, args.caps, args.ras, args.board]):
        #     args.asic = args.bus = args.vbios = args.limit = args.driver = args.caps = args.ras = args.board = True

        if not any([args.access, args.weight, args.hops, args.type, args.numa, args.numa_bw]):
            args.access = args.weight = args.hops = args.type = args.numa = args.numa_bw = True

        topo_json = {}
        topo_table = []

        if args.access:
            pass
        if args.weight:
            pass
        if args.hops:
            pass
        if args.type:
            pass
        if args.numa:
            pass
            # numa_numbers = c_uint32()
            # for device in deviceList:
            #     ret = rocmsmi.rsmi_get_numa_node_number(device, byref(numa_numbers))
            #     if rsmi_ret_ok(ret, device):
            #         printLog(device, "(Topology) Numa Node", numa_numbers.value)
            #     else:
            #         printErrLog(device, "Cannot read Numa Node")

            #     ret = rocmsmi.rsmi_numa_affinity_get(device, byref(numa_numbers))
            #     if rsmi_ret_ok(ret):
            #         printLog(device, "(Topology) Numa Affinity", numa_numbers.value)
            #     else:
            #         printErrLog(device, 'Cannot read Numa Affinity')
        if args.numa_bw:
            pass

    def set_value(self, args, multiple_devices=False, gpu=None, clock=None, sclk=None, mclk=None,
                    pcie=None, slevel=None, mlevel=None, vc=None, srange=None, mrange=None,
                    fan=None, perflevel=None, overdrive=None, memoverdrive=None,
                    poweroverdrive=None, profile=None, perfdeterminism=None):
        """Issue reset commands to target gpu(s)

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            gpu (device_handle, optional): device_handle for target device. Defaults to None.
            clock (bool, optional): Value over ride for args.clock. Defaults to None.
            sclk (bool, optional): Value over ride for args.sclk. Defaults to None.
            mclk (bool, optional): Value over ride for args.mclk. Defaults to None.
            pcie (bool, optional): Value over ride for args.pcie. Defaults to None.
            slevel (bool, optional): Value over ride for args.slevel. Defaults to None.
            mlevel (bool, optional): Value over ride for args.mlevel. Defaults to None.
            vc (bool, optional): Value over ride for args.vc. Defaults to None.
            srange (bool, optional): Value over ride for args.srange. Defaults to None.
            mrange (bool, optional): Value over ride for args.mrange. Defaults to None.
            fan (bool, optional): Value over ride for args.fan. Defaults to None.
            perflevel (bool, optional): Value over ride for args.perflevel. Defaults to None.
            overdrive (bool, optional): Value over ride for args.overdrive. Defaults to None.
            memoverdrive (bool, optional): Value over ride for args.memoverdrive. Defaults to None.
            poweroverdrive (bool, optional): Value over ride for args.poweroverdrive. Defaults to None.
            profile (bool, optional): Value over ride for args.profile. Defaults to None.
            perfdeterminism (bool, optional): Value over ride for args.perfdeterminism. Defaults to None.

        Raises:
            ValueError: Value error if no gpu value is provided
            IndexError: Index error if gpu list is empty

        Return:
            Nothing
        """
        # Set args.* to passed in arguments
        if gpu:
            args.gpu = gpu
        if clock:
            args.clock = clock
        if sclk:
            args.sclk = sclk
        if mclk:
            args.mclk = mclk
        if pcie:
            args.pcie = pcie
        if slevel:
            args.slevel = slevel
        if mlevel:
            args.mlevel = mlevel
        if vc:
            args.vc = vc
        if srange:
            args.srange = srange
        if mrange:
            args.mrange = mrange
        if fan:
            args.fan = fan
        if perflevel:
            args.perflevel = perflevel
        if overdrive:
            args.overdrive = overdrive
        if memoverdrive:
            args.memoverdrive = memoverdrive
        if poweroverdrive:
            args.poweroverdrive = poweroverdrive
        if profile:
            args.profile = profile
        if perfdeterminism:
            args.perfdeterminism = perfdeterminism

        # Handle No GPU passed
        if args.gpu is None:
            raise ValueError('No GPU provided, specific GPU target(s) are needed')

        # Handle multiple GPUs
        handled_multiple_gpus, device_handle = self.helpers.handle_gpus(args, self.logger, self.set_value)
        if handled_multiple_gpus:
            return # This function is recursive

        args.gpu = device_handle

        if args.clock:
            clock_type, freq_bitmask = args.clock

            # Check if the performance level is manual, if not then set it to manual
            try:
                perf_level = amdsmi_interface.amdsmi_dev_get_perf_level(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to get performance level of {args.gpu}")

            if 'manual' in perf_level.lower():
                try:
                    amdsmi_interface.amdsmi_dev_set_perf_level_v1(args.gpu, amdsmi_interface.AmdSmiDevPerfLevel.MANUAL.value)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    raise ValueError(self, f"Unable to set the performance level of {args.gpu} to manual")

            if clock_type != amdsmi_interface.AmdSmiClkType.PCIE.value:
                try:
                    amdsmi_interface.amdsmi_dev_set_clk_freq(args.gpu, clock_type, freq_bitmask)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    clock_type = amdsmi_interface.AmdSmiClkType(clock_type)
                    raise ValueError(self, f"Unable to set the {clock_type} clock frequency on {args.gpu}")
                print(f'Successfully set frequency bitmask on {args.gpu}')
            else:
                try:
                    amdsmi_interface.amdsmi_dev_set_pci_bandwidth(args.gpu, freq_bitmask)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    clock_type = amdsmi_interface.AmdSmiClkType(clock_type)
                    raise ValueError(self, f"Unable to set the {clock_type} clock frequency on {args.gpu}")
                print(f'Successfully set frequency bitmask on {args.gpu}')

        if args.sclk:
            freq_bitmask = args.sclk
            clock_type = amdsmi_interface.AmdSmiClkType.SYS
            # Check if the performance level is manual, if not then set it to manual
            try:
                perf_level = amdsmi_interface.amdsmi_dev_get_perf_level(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to get performance level of {args.gpu}")

            if 'manual' in perf_level.lower():
                try:
                    amdsmi_interface.amdsmi_dev_set_perf_level_v1(args.gpu, amdsmi_interface.AmdSmiDevPerfLevel.MANUAL.value)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    raise ValueError(self, f"Unable to set the performance level of {args.gpu} to manual")

            try:
                amdsmi_interface.amdsmi_dev_set_clk_freq(args.gpu, clock_type.value, freq_bitmask)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to set the {clock_type} clock frequency on {args.gpu}")
            print(f'Successfully set frequency bitmask on {args.gpu}')

        if args.mclk:
            freq_bitmask = args.sclk
            clock_type = amdsmi_interface.AmdSmiClkType.MEM
            # Check if the performance level is manual, if not then set it to manual
            try:
                perf_level = amdsmi_interface.amdsmi_dev_get_perf_level(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to get performance level of {args.gpu}")

            if 'manual' in perf_level.lower():
                try:
                    amdsmi_interface.amdsmi_dev_set_perf_level_v1(args.gpu, amdsmi_interface.AmdSmiDevPerfLevel.MANUAL.value)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    raise ValueError(self, f"Unable to set the performance level of {args.gpu} to manual")

            try:
                amdsmi_interface.amdsmi_dev_set_clk_freq(args.gpu, clock_type.value, freq_bitmask)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to set the {clock_type} clock frequency on {args.gpu}")
            print(f'Successfully set frequency bitmask on {args.gpu}')

        if args.pcie:
            freq_bitmask = args.sclk
            clock_type = amdsmi_interface.AmdSmiClkType.PCIE
            # Check if the performance level is manual, if not then set it to manual
            try:
                perf_level = amdsmi_interface.amdsmi_dev_get_perf_level(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to get performance level of {args.gpu}")

            if 'manual' in perf_level.lower():
                try:
                    amdsmi_interface.amdsmi_dev_set_perf_level_v1(args.gpu, amdsmi_interface.AmdSmiDevPerfLevel.MANUAL.value)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    raise ValueError(self, f"Unable to set the performance level of {args.gpu} to manual")
            try:
                amdsmi_interface.amdsmi_dev_set_pci_bandwidth(args.gpu, freq_bitmask)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to set the {clock_type} clock frequency on {args.gpu}")
            print(f'Successfully set frequency bitmask on {args.gpu}')

        if args.slevel:
            level, value = args.slevel
            level = amdsmi_interface.AmdSmiFreqInd(level).value
            clock_type = amdsmi_interface.AmdSmiClkType.SYS
            try:
                amdsmi_interface.amdsmi_dev_set_od_clk_info(args.gpu, level, value, clock_type.value)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to change the {clock_type} clock frequency in the PowerPlay table on {args.gpu}")
            print(f'Successfully changed clock frequency on {args.gpu}')

        if args.mlevel:
            level, value = args.mlevel
            level = amdsmi_interface.AmdSmiFreqInd(level).value
            clock_type = amdsmi_interface.AmdSmiClkType.MEM
            try:
                amdsmi_interface.amdsmi_dev_set_od_clk_info(args.gpu, level, value, clock_type.value)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to change the {clock_type} clock frequency in the PowerPlay table on {args.gpu}")
            print(f'Successfully changed clock frequency on {args.gpu}')

        if args.vc:
            point, clk, volt = args.vc
            try:
                amdsmi_interface.amdsmi_dev_set_od_volt_info(args.gpu, point, clk, volt)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to set the Voltage Curve point {point} to {clk}(MHz) {volt}(mV) on {args.gpu}")
            print(f'Successfully set voltage point {point} to {clk}(MHz) {volt}(mV) on {args.gpu}')

        if args.srange:
            min_value, max_value = args.srange
            clock_type = amdsmi_interface.AmdSmiClkType.SYS
            try:
                amdsmi_interface.amdsmi_dev_set_clk_range(args.gpu, min_value, max_value, clock_type.value)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to set {clock_type} from {min_value}(MHz) to {max_value}(MHz) on {args.gpu}")
            print(f"Successfully set {clock_type} from {min_value}(MHz) to {max_value}(MHz) on {args.gpu}")

        if args.mrange:
            min_value, max_value = args.srange
            clock_type = amdsmi_interface.AmdSmiClkType.MEM
            try:
                amdsmi_interface.amdsmi_dev_set_clk_range(args.gpu, min_value, max_value, clock_type.value)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to set {clock_type} from {min_value}(MHz) to {max_value}(MHz) on {args.gpu}")
            print(f"Successfully set {clock_type} from {min_value}(MHz) to {max_value}(MHz) on {args.gpu}")

        if args.fan:
            try:
                amdsmi_interface.amdsmi_dev_set_fan_speed(args.gpu, 0, args.fan)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to set fan speed {args.fan} on {args.gpu}")
            print(f"Successfully set fan speed {args.fan} on {args.gpu}")

        if args.perflevel:
            perf_levels = amdsmi_interface.amdsmi_wrapper.amdsmi_dev_perf_level_t__enumvalues
            for value in perf_levels:
                if args.perflevel.lower() in perf_levels[value]:
                    try:
                        amdsmi_interface.amdsmi_dev_set_perf_level_v1(args.gpu, value)
                    except amdsmi_exception.AmdSmiLibraryException as e:
                        raise ValueError(self, f"Unable to set performance level {args.perflevel} on {args.gpu}")
                    print(f"Successfully set performance level {args.perflevel} on {args.gpu}")
                    break

        if args.overdrive or args.overdrive == 0:
            # Check if the performance level is manual, if not then set it to manual
            try:
                perf_level = amdsmi_interface.amdsmi_dev_get_perf_level(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to get performance level of {args.gpu}")

            if 'manual' in perf_level.lower():
                try:
                    amdsmi_interface.amdsmi_dev_set_perf_level_v1(args.gpu, amdsmi_interface.AmdSmiDevPerfLevel.MANUAL)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    raise ValueError(self, f"Unable to set the performance level of {args.gpu} to manual")

            try:
                amdsmi_interface.amdsmi_dev_set_overdrive_level_v1(args.gpu, args.overdrive)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to set overdrive {args.overdrive} to {args.gpu}")
            print(f"Successfully to set overdrive {args.overdrive} to {args.gpu}")

        if args.memoverdrive or args.memoverdrive == 0:
            # Check if the performance level is manual, if not then set it to manual
            try:
                perf_level = amdsmi_interface.amdsmi_dev_get_perf_level(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to get performance level of {args.gpu}")

            if 'manual' in perf_level.lower():
                try:
                    amdsmi_interface.amdsmi_dev_set_perf_level_v1(args.gpu, amdsmi_interface.AmdSmiDevPerfLevel.MANUAL.value)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    raise ValueError(self, f"Unable to set the performance level of {args.gpu} to manual")

        if args.poweroverdrive:
            overdrive_power_cap = args.poweroverdrive
            try:
                power_caps = amdsmi_interface.amdsmi_get_power_cap_info(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to get the power cap info for {args.gpu}")
            if overdrive_power_cap == 0:
                overdrive_power_cap = power_caps['power_cap_default']
            else:
                overdrive_power_cap *= 1000000

            if overdrive_power_cap < power_caps['min_power_cap']:
                raise ValueError(self, f"Requested power cap: {overdrive_power_cap} is lower than the min power cap: {power_caps['min_power_cap']}")

            if overdrive_power_cap > power_caps['max_power_cap']:
                raise ValueError(self, f"Requested power cap: {overdrive_power_cap} is greater than the max power cap: {power_caps['max_power_cap']}")

            if overdrive_power_cap == power_caps['power_cap']:
                raise ValueError(self, f"Requested power cap: {overdrive_power_cap} is the same as the current power cap: {power_caps['power_cap']}")

            try:
                amdsmi_interface.amdsmi_dev_set_power_cap(args.gpu, 0, overdrive_power_cap)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to set power cap to {overdrive_power_cap} on {args.gpu}")

            try:
                power_caps = amdsmi_interface.amdsmi_get_power_cap_info(args.gpu)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to get the power cap info for {args.gpu} post set")

            if power_caps['power_cap'] == overdrive_power_cap:
                print(f"Successfully set the power cap {overdrive_power_cap} on {args.gpu}")
            else:
                raise ValueError(self, f"Power cap: {overdrive_power_cap} set failed on {args.gpu}")

        if args.profile:
            print(amdsmi_interface.AmdSmiRetCode.NOT_IMPLEMENTED)

        if args.perfdeterminism:
            try:
                amdsmi_interface.amdsmi_set_perf_determinism_mode(args.gpu, args.perfdeterminism)
            except amdsmi_exception.AmdSmiLibraryException as e:
                raise ValueError(self, f"Unable to set performance determinism and clock frequency to {args.perfdeterminism} on {args.gpu}")
            print(f"Successfully enabled performance determinism and set GFX clock frequency to {args.perfdeterminism} on {args.gpu}")


    def reset(self, args, multiple_devices=False, gpu=None, gpureset=None,
                clocks=None, fans=None, profile=None,
                poweroverdrive=None, xgmierr=None, perfdeterminism=None):
        """Issue reset commands to target gpu(s)

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            gpu (device_handle, optional): device_handle for target device. Defaults to None.
            gpureset (bool, optional): Value over ride for args.gpureset. Defaults to None.
            clocks (bool, optional): Value over ride for args.clocks. Defaults to None.
            fans (bool, optional): Value over ride for args.fans. Defaults to None.
            profile (bool, optional): Value over ride for args.profile. Defaults to None.
            poweroverdrive (bool, optional): Value over ride for args.poweroverdrive. Defaults to None.
            xgmierr (bool, optional): Value over ride for args.xgmierr. Defaults to None.
            perfdeterminism (bool, optional): Value over ride for args.perfdeterminism. Defaults to None.

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
        if poweroverdrive:
            args.poweroverdrive = poweroverdrive
        if xgmierr:
            args.xgmierr = xgmierr
        if perfdeterminism:
            args.perfdeterminism = perfdeterminism

        # Handle No GPU passed
        if args.gpu is None:
            raise ValueError('No GPU provided, specific GPU target(s) are needed')

        # Handle multiple GPUs
        handled_multiple_gpus, device_handle = self.helpers.handle_gpus(args, self.logger, self.reset)
        if handled_multiple_gpus:
            return # This function is recursive

        args.gpu = device_handle

        if args.gpureset:
            if self.helpers.is_amd_device(args.gpu):
                try:
                    amdsmi_interface.amdsmi_dev_reset_gpu(args.gpu)
                    result = 'Successfully reset GPU'
                except amdsmi_exception.AmdSmiLibraryException as e:
                    result = e.get_error_info()
            else:
                result = 'Unable to reset non-amd GPU'

            self.logger.store_output(args.gpu, 'gpu_reset', result)
        if args.clocks:
            # rsmi_string = ' Reset Clocks '
            reset_clocks_results = {'overdrive' : '',
                                    'clocks' : '',
                                    'performance': ''}
            try:
                amdsmi_interface.amdsmi_dev_set_overdrive_level_v1(args.gpu, 0)
                reset_clocks_results['overdrive'] = 'Overdrive set to 0'
            except amdsmi_exception.AmdSmiLibraryException as e:
                reset_clocks_results['overdrive'] = e.get_error_info()

            try:
                level_auto = amdsmi_interface.AmdSmiDevPerfLevel.AUTO
                amdsmi_interface.amdsmi_dev_set_perf_level_v1(args.gpu, level_auto)
                reset_clocks_results['clocks'] = 'Successfully reset clocks'
            except amdsmi_exception.AmdSmiLibraryException as e:
                reset_clocks_results['clocks'] = e.get_error_info()

            try:
                level_auto = amdsmi_interface.AmdSmiDevPerfLevel.AUTO
                amdsmi_interface.amdsmi_dev_set_perf_level_v1(args.gpu, level_auto)
                reset_clocks_results['performance'] = 'Performance level reset to auto'
            except amdsmi_exception.AmdSmiLibraryException as e:
                reset_clocks_results['performance'] = e.get_error_info()

            self.logger.store_output(args.gpu, 'reset_clocks', reset_clocks_results)
        if args.fans:
            try:
                amdsmi_interface.amdsmi_dev_reset_fan(args.gpu, 0)
                result = 'Successfully reset fan speed to driver control'
            except amdsmi_exception.AmdSmiLibraryException as e:
                result = e.get_error_info()

            self.logger.store_output(args.gpu, 'reset_fans', result)
        if args.profile:
            reset_profile_results = {'power_profile' : '',
                                     'performance_level': ''}
            try:
                power_profile_mask = amdsmi_interface.AmdSmiPowerProfilePresetMasks.BOOTUP_DEFAULT
                amdsmi_interface.amdsmi_dev_set_power_profile(args.gpu, 0, power_profile_mask)
                reset_profile_results['power_profile'] = 'Successfully reset Power Profile'
            except amdsmi_exception.AmdSmiLibraryException as e:
                reset_profile_results['power_profile'] = e.get_error_info()

            try:
                level_auto = amdsmi_interface.AmdSmiDevPerfLevel.AUTO
                amdsmi_interface.amdsmi_dev_set_perf_level_v1(args.gpu, level_auto)
                reset_profile_results['performance_level'] = 'Successfully reset Performance Level'
            except amdsmi_exception.AmdSmiLibraryException as e:
                reset_profile_results['performance_level'] = e.get_error_info()

            self.logger.store_output(args.gpu, 'reset_profile', reset_profile_results)
        if args.xgmierr:
            try:
                amdsmi_interface.amdsmi_dev_reset_xgmi_error(args.gpu)
                result = 'Successfully reset XGMI Error count'
            except amdsmi_exception.AmdSmiLibraryException as e:
                result = e.get_error_info()
            self.logger.store_output(args.gpu, 'reset_xgmi_err', result)
        if args.perfdeterminism:
            try:
                level_auto = amdsmi_interface.AmdSmiDevPerfLevel.AUTO
                amdsmi_interface.amdsmi_dev_set_perf_level_v1(args.gpu, level_auto)
                result = 'Successfully disabled performance determinism'
            except amdsmi_exception.AmdSmiLibraryException as e:
                result = e.get_error_info()

            self.logger.store_output(args.gpu, 'reset_perf_determinism', result)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return # Skip printing when there are multiple devices

        self.logger.print_output()


    def rocm_smi(self, args):
        print("Placeholder for rocm-smi legacy commandss")


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
                if e.err_code != amdsmi_exception.AmdSmiRetCode.NO_DATA:
                    print(e)
            except Exception as e:
                print(e)

        listener.stop()

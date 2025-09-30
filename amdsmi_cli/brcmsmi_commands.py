#!/usr/bin/env python3
#
# Copyright (C) Advanced Micro Devices. All rights reserved.
#
#  Developed by:
#            Broadcom Inc
#
#            www.broadcom.com
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

"""
BRCM SMI Commands Module

This module contains all NIC and Switch related CLI commands for BRCM SMI devices.
It is conditionally imported only when BRCM SMI support is available.
"""

import json
import logging
import os
import contextlib
import subprocess
from amdsmi import amdsmi_exception, amdsmi_interface

# Try to import brcmsmi_interface, but handle gracefully if not available
try:
    from amdsmi import brcmsmi_interface
    BRCM_SMI_AVAILABLE = True
except ImportError:
    brcmsmi_interface = None
    BRCM_SMI_AVAILABLE = False

class BRCMSMICommands:
    """
    BRCM SMI Commands class containing all NIC and Switch related functionality.
    This class is only instantiated when BRCM SMI support is available.
    """
    
    def __init__(self, helpers, logger):
        """
        Initialize BRCM SMI Commands.
        
        Args:
            helpers: AMDSMIHelpers instance
            logger: AMDSMILogger instance
        """
        self.helpers = helpers
        self.logger = logger
        
        # Initialize BRCM SMI device handles
        self.device_handles_nics = []
        self.device_handles_switchs = []
    
        try:
            # Check if BRCM SMI support is available
            if not amdsmi_interface.is_brcm_smi_supported():
                logging.warning("BRCM SMI support not available in this build")
                return
                
            # Initialize BRCM SMI and discover devices with stderr suppression to avoid cosmetic error messages
            stderr_fd = os.dup(2)
            devnull_fd = os.open(os.devnull, os.O_WRONLY)
            try:
                os.dup2(devnull_fd, 2)
                amdsmi_interface.amdsmi_brcm_init()
                # Get socket handles
                socket_handles = amdsmi_interface.amdsmi_get_brcm_socket_handles()
            finally:
                os.dup2(stderr_fd, 2)
                os.close(devnull_fd)
                os.close(stderr_fd)
            
            if socket_handles:
                socket_handle = socket_handles[0]  # Use first socket
                
                # Get NIC handles (type conversion handled in amdsmi_interface)
                try:
                    self.device_handles_nics = amdsmi_interface.amdsmi_get_brcm_nic_processor_handles(socket_handle)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("No NIC devices found: %s", e.get_error_info())
                    self.device_handles_nics = []
                
                # Get Switch handles (type conversion handled in amdsmi_interface) 
                try:
                    self.device_handles_switchs = amdsmi_interface.amdsmi_get_brcm_switch_processor_handles(socket_handle)
                except amdsmi_exception.AmdSmiLibraryException as e:
                    logging.debug("No Switch devices found: %s", e.get_error_info())
                    self.device_handles_switchs = []
                    
        except amdsmi_exception.AmdSmiLibraryException as e:
            logging.error('Unable to initialize BRCM SMI: %s', e.get_error_info())
            self.device_handles_nics = []
            self.device_handles_switchs = []

    def get_nic_handles(self):
        """Get NIC device handles."""
        return self.device_handles_nics
    
    def get_switch_handles(self):
        """Get Switch device handles."""
        return self.device_handles_switchs

    def list_nic(self, args, multiple_devices=False, nic=None):
        """List information for target nic

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            nic (device_handle, optional): device_handle for target device. Defaults to None.

        Raises:
            IndexError: Index error if nic list is empty

        Returns:
            None: Print output via AMDSMILogger to destination
        """
        # Set args.* to passed in arguments
        if nic:
            args.nic = nic

        # Handle No NIC passed - set to all available NICs
        if args.nic == None:
            args.nic = self.device_handles_nics

        # Handle multiple NICs
        handled_multiple_nics, device_handle = self.helpers.handle_nics(args, self.logger, self.list_nic)
        if handled_multiple_nics:
            return # This function is recursive

        args.nic = device_handle

        # Get nic_id for logging
        nic_id = self.helpers.get_nic_id_from_device_handle(args.nic)

        # Get nic info using getString method
        try:
            # Get NIC basic info (JSON format)
            nic_info_raw = amdsmi_interface.amdsmi_brcm_getString(args.nic, "get_nic_info", 1024)
            
            # Parse JSON response to extract individual fields
            import json
            info_dict = json.loads(nic_info_raw)
            device_name = info_dict.get('nic_device_name', 'N/A')
            part_number = info_dict.get('nic_part_number', 'N/A')
            firmware_version = info_dict.get('nic_firmware_version', 'N/A')
            
            # Get BDF using dedicated BDF function
            if BRCM_SMI_AVAILABLE and brcmsmi_interface:
                bdf = brcmsmi_interface.amdsmi_get_brcm_nic_device_bdf(args.nic)
            else:
                bdf = "N/A"
            
            # Get UUID separately
            uuid = amdsmi_interface.amdsmi_brcm_getString(args.nic, "get_nic_device_uuid", 1024)

        except (amdsmi_exception.AmdSmiLibraryException, json.JSONDecodeError, ValueError, Exception) as e:
            bdf = uuid = device_name = part_number = firmware_version = "N/A"
            logging.debug("Failed to get info for nic %s | %s", nic_id, str(e))

        # CSV format is intentionally aligned with Host
        if self.logger.is_csv_format():
            self.logger.store_nic_output(args.nic, 'nic_bdf', bdf)
            self.logger.store_nic_output(args.nic, 'device_name', device_name)
            self.logger.store_nic_output(args.nic, 'part_number', part_number)
            self.logger.store_nic_output(args.nic, 'firmware_version', firmware_version)
            self.logger.store_nic_output(args.nic, 'nic_uuid', uuid)
        else:
            self.logger.store_nic_output(args.nic, 'bdf', bdf)
            self.logger.store_nic_output(args.nic, 'device_name', device_name)
            self.logger.store_nic_output(args.nic, 'part_number', part_number)
            self.logger.store_nic_output(args.nic, 'firmware_version', firmware_version)
            self.logger.store_nic_output(args.nic, 'uuid', uuid)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return

        self.logger.print_output()

    def list_switch(self, args, multiple_devices=False, switch=None):
        """List information for target switch

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            switch (device_handle, optional): device_handle for target device. Defaults to None.

        Raises:
            IndexError: Index error if switch list is empty

        Returns:
            None: Print output via AMDSMILogger to destination
        """
        # Set args.* to passed in arguments
        if switch:
            args.switch = switch

        # Handle No Switch passed - set to all available Switches
        if args.switch == None:
            args.switch = self.device_handles_switchs

        # Handle multiple Switchs
        handled_multiple_switchs, device_handle = self.helpers.handle_switchs(args, self.logger, self.list_switch)
        if handled_multiple_switchs:
            return # This function is recursive

        args.switch = device_handle

        # Get switch_id for logging  
        switch_id = self.helpers.get_switch_id_from_device_handle(args.switch)
        
        try:
            # Get Switch BDF using dedicated BDF function
            if BRCM_SMI_AVAILABLE and brcmsmi_interface:
                bdf = brcmsmi_interface.amdsmi_get_brcm_switch_device_bdf(args.switch)
            else:
                bdf = "N/A"
            
            # Get UUID separately
            uuid = amdsmi_interface.amdsmi_brcm_getString(args.switch, "get_switch_device_uuid", 1024)

        except (amdsmi_exception.AmdSmiLibraryException, json.JSONDecodeError, ValueError, Exception) as e:
            bdf = uuid = "N/A"
            logging.debug("Failed to get info for switch %s | %s", switch_id, str(e))

        # CSV format is intentionally aligned with Host
        if self.logger.is_csv_format():
            self.logger.store_switch_output(args.switch, 'switch_bdf', bdf)
            self.logger.store_switch_output(args.switch, 'switch_uuid', uuid)
        else:
            self.logger.store_switch_output(args.switch, 'bdf', bdf)
            self.logger.store_switch_output(args.switch, 'uuid', uuid)

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return

        self.logger.print_output()

    def firmware_nic(self, args, multiple_devices=False, nic=None, fw_list=True):
        """ Get Firmware information for target nic

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            nic (device_handle, optional): device_handle for target device. Defaults to None.
            fw_list (bool, optional): True to get list of all firmware information
        Raises:
            IndexError: Index error if nic list is empty

        Returns:
            None: Print output via AMDSMILogger to destination
        """
        if fw_list:
            args.fw_list = fw_list
        if nic:
           args.nic = nic

        # Handle No NIC passed
        if args.nic==None:
            args.nic = self.device_handles_nics

        # Handle multiple NICs
        if args.nic != None:
            handled_multiple_nics, device_handle = self.helpers.handle_nics(args, self.logger, self.firmware_nic)
            if handled_multiple_nics:
                return # This function is recursive

        args.nic = device_handle

        try:
            firmware_info = amdsmi_interface.amdsmi_brcm_getString(args.nic, "get_nic_firmware_info", 1024)
            import json
            fw_dict = json.loads(firmware_info)
            
            # Store firmware information
            for key, value in fw_dict.items():
                self.logger.store_nic_output(args.nic, key, value)
                
        except amdsmi_exception.AmdSmiLibraryException as e:
            logging.debug("Failed to get firmware info for nic | %s", e.get_error_info())
            self.logger.store_nic_output(args.nic, 'firmware_error', e.get_error_info())

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return

        self.logger.print_output()

    def metric_nic(self, args, multiple_devices=False, watching_output=False, watch=None, watch_time=None,
                   iterations=None, nic=None, nic_power=None, nic_temperature=None, nic_errors=None):
        """Get comprehensive metric information for target NIC with hierarchical output

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            watching_output (bool, optional): True if watch flag is enabled. Defaults to False.
            watch (int, optional): Number of seconds to wait between updates. Defaults to None.
            watch_time (int, optional): Number of seconds to watch. Defaults to None.
            iterations (int, optional): Number of iterations to run. Defaults to None.
            nic (device_handle, optional): device_handle for target device. Defaults to None.

        Raises:
            IndexError: Index error if nic list is empty

        Returns:
            None: Print output via AMDSMILogger to destination
        """
        if not self.device_handles_nics:
            logging.debug("No BRCM NIC devices found")
            return

        # Set args.* to passed in arguments
        if nic:
            args.nic = nic

        # Handle No NIC passed
        if args.nic == None:
            args.nic = self.device_handles_nics

        # Handle multiple NICs
        handled_multiple_nics, device_handle = self.helpers.handle_nics(args, self.logger, self.metric_nic)
        if handled_multiple_nics:
            return # This function is recursive

        args.nic = device_handle

        # Get device ID from the handle index
        try:
            device_id = self.device_handles_nics.index(device_handle) if device_handle in self.device_handles_nics else 0
        except (ValueError, AttributeError):
            device_id = 0

        # Collect all metric data
        power_data = {}
        temperature_data = {}
        error_data = {}

        try:
            # Get power metrics
            power_info = amdsmi_interface.amdsmi_brcm_getString(device_handle, "get_nic_power", 1024)
            power_data = json.loads(power_info)
        except amdsmi_exception.AmdSmiLibraryException as e:
            logging.debug("Failed to get power info for NIC %s | %s", device_handle, e.get_error_info())
            power_data = {
                "nic_power_async": "N/A",
                "nic_power_control": "AUTO",
                "nic_power_runtime_active_time": 0,
                "nic_power_runtime_status": "UNSUPPORTED",
                "nic_power_runtime_usage": "N/A",
                "nic_power_runtime_active_kids": "N/A",
                "nic_power_runtime_enabled": "N/A",
                "nic_power_runtime_suspended_time": 0
            }

        try:
            # Get temperature metrics
            temp_info = amdsmi_interface.amdsmi_brcm_getString(device_handle, "get_nic_temperature", 1024)
            temperature_data = json.loads(temp_info)
            
            # Alarm values are now read directly from the library JSON response
            # No manual calculation needed - hardware provides actual alarm status
            
        except amdsmi_exception.AmdSmiLibraryException as e:
            logging.debug("Failed to get temperature info for NIC %s | %s", device_handle, e.get_error_info())
            temperature_data = {
                "nic_temp_crit_alarm": 0,
                "nic_temp_emergency_alarm": 0,
                "nic_temp_shutdown_alarm": 0,
                "nic_temp_max_alarm": 0,
                "nic_temp_crit": "N/A",
                "nic_temp_emergency": "N/A",
                "nic_temp_input": "N/A",
                "nic_temp_max": "N/A",
                "nic_temp_shutdown": "N/A"
            }

        try:
            # Get error metrics
            error_info = amdsmi_interface.amdsmi_brcm_getString(device_handle, "get_nic_errors", 1024)
            error_data = json.loads(error_info)
        except amdsmi_exception.AmdSmiLibraryException as e:
            logging.debug("Failed to get error info for NIC %s | %s", device_handle, e.get_error_info())
            error_data = {
                "nic_dev_correctable": {"rxerr": 0},
                "nic_dev_fatal": {"undefined": 0},
                "nic_dev_nonfatal": {"undefined": 0}
            }

        # Format and display the hierarchical output for human-readable format
        if not (self.logger.is_json_format() or self.logger.is_csv_format()):
            print(f"BRCM_NIC: {device_id}")
            
            # Power section
            print("    NIC_POWER:")
            print(f"        NIC_POWER_ASYNC: {power_data.get('nic_power_async', 'N/A')}")
            print(f"        NIC_POWER_CONTROL: {power_data.get('nic_power_control', 'N/A')}")
            print(f"        NIC_POWER_RUNTIME_ACTIVE_TIME: {power_data.get('nic_power_runtime_active_time', 'N/A')}")
            print(f"        NIC_POWER_RUNTIME_STATUS: {power_data.get('nic_power_runtime_status', 'N/A')}")
            print(f"        NIC_POWER_RUNTIME_USAGE: {power_data.get('nic_power_runtime_usage', 'N/A')}")
            print(f"        NIC_POWER_RUNTIME_ACTIVE_KIDS: {power_data.get('nic_power_runtime_active_kids', 'N/A')}")
            print(f"        NIC_POWER_RUNTIME_ENABLED: {power_data.get('nic_power_runtime_enabled', 'N/A')}")
            print(f"        NIC_POWER_RUNTIME_SUSPENDED_TIME: {power_data.get('nic_power_runtime_suspended_time', 'N/A')}")
            
            # Temperature section
            print("    NIC_TEMPERATURE:")
            # Display temperature values in specific order
            temp_order = [
                'nic_temp_crit_alarm', 'nic_temp_emergency_alarm', 'nic_temp_shutdown_alarm', 'nic_temp_max_alarm',
                'nic_temp_crit', 'nic_temp_emergency', 'nic_temp_input', 'nic_temp_max', 'nic_temp_shutdown'
            ]
            
            for key in temp_order:
                value = temperature_data.get(key, 'N/A')
                if key.startswith('nic_temp_'):
                    try:
                        # Convert from millidegrees to degrees for temperature values (not alarms)
                        if 'alarm' not in key.lower() and str(value).isdigit():
                            value_celsius = int(value) // 1000
                            formatted_value = f"{value_celsius} °C"
                        else:
                            # For alarm values, just show the value as is (directly from hardware)
                            formatted_value = value
                        print(f"        {key.upper()}: {formatted_value}")
                    except (ValueError, TypeError):
                        print(f"        {key.upper()}: {value}")
                else:
                    print(f"        {key.upper()}: {value}")
            
            # Error section
            print("    NIC_ERRORS:")
            error_correctable = error_data.get('nic_dev_correctable', {})
            error_fatal = error_data.get('nic_dev_fatal', {})
            error_nonfatal = error_data.get('nic_dev_nonfatal', {})
            
            print("        NIC_DEV_CORRECTABLE:")
            for key, value in error_correctable.items():
                print(f"            {key.upper()}: {value}")
            
            print("        NIC_DEV_FATAL:")
            for key, value in error_fatal.items():
                print(f"            {key.upper()}: {value}")
            
            print("        NIC_DEV_NONFATAL:")
            for key, value in error_nonfatal.items():
                print(f"            {key.upper()}: {value}")

        # Handle different output formats
        if self.logger.is_json_format() or self.logger.is_csv_format():
            # Store data in logger only for JSON/CSV formats
            # Power data
            for key, value in power_data.items():
                self.logger._store_nic_output_amdsmi(device_id, f'NIC_POWER_{key.upper().replace("NIC_POWER_", "")}', value)
            
            # Temperature data
            for key, value in temperature_data.items():
                if key.startswith('nic_temp_') and value != 'N/A':
                    try:
                        if 'alarm' not in key.lower() and str(value).isdigit():
                            value_celsius = int(value) // 1000
                            formatted_value = f"{value_celsius} °C"
                        else:
                            # Alarm values are read directly from hardware
                            formatted_value = value
                        self.logger._store_nic_output_amdsmi(device_id, key.upper(), formatted_value)
                    except (ValueError, TypeError):
                        self.logger._store_nic_output_amdsmi(device_id, key.upper(), value)
                else:
                    self.logger._store_nic_output_amdsmi(device_id, key.upper(), value)
            
            # Error data
            error_correctable = error_data.get('nic_dev_correctable', {})
            error_fatal = error_data.get('nic_dev_fatal', {})
            error_nonfatal = error_data.get('nic_dev_nonfatal', {})
            
            for error_type, error_dict in [('CORRECTABLE', error_correctable), ('FATAL', error_fatal), ('NONFATAL', error_nonfatal)]:
                for key, value in error_dict.items():
                    self.logger._store_nic_output_amdsmi(device_id, f'NIC_DEV_{error_type}_{key.upper()}', value)

            # Print JSON/CSV output
            if multiple_devices:
                self.logger.store_multiple_device_output()
            else:
                self.logger.print_output()

    def metric_switch(self, args, multiple_devices=False, watching_output=False, watch=None, watch_time=None,
                      iterations=None,  switch=None, switch_power=None, switch_errors=None):
        """Get Metric information for target switch

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            watching_output (bool, optional): True if watch flag is enabled. Defaults to False.
            watch (int, optional): Number of seconds to wait between updates. Defaults to None.
            watch_time (int, optional): Number of seconds to watch. Defaults to None.
            iterations (int, optional): Number of iterations to run. Defaults to None.
            switch (device_handle, optional): device_handle for target device. Defaults to None.

        Raises:
            IndexError: Index error if switch list is empty

        Returns:
            None: Print output via AMDSMILogger to destination
        """
        # Set args.* to passed in arguments
        if switch:
            args.switch = switch

        # Handle No Switch passed
        if args.switch == None:
            args.switch = self.device_handles_switchs

        # Handle multiple Switches
        handled_multiple_switchs, device_handle = self.helpers.handle_switchs(args, self.logger, self.metric_switch)
        if handled_multiple_switchs:
            return # This function is recursive

        args.switch = device_handle

        # Get device ID from the handle index
        try:
            device_id = self.device_handles_switchs.index(device_handle) if device_handle in self.device_handles_switchs else 0
        except (ValueError, AttributeError):
            device_id = 0

        # Collect all metric data
        device_data = {}
        power_data = {}
        error_data = {}

        try:
            # Get comprehensive Switch metrics (larger buffer for all fields)
            metrics = amdsmi_interface.amdsmi_brcm_getString(args.switch, "get_switch_metrics", 8192)
            import json
            metrics_dict = json.loads(metrics)
            
            # Organize metrics into categories
            for key, value in metrics_dict.items():
                if key.startswith('brcm_power_'):
                    power_data[key] = value
                elif 'aer_dev_' in key:
                    error_data[key] = value
                else:
                    device_data[key] = value
                
        except amdsmi_exception.AmdSmiLibraryException as e:
            logging.debug("Failed to get metrics for switch | %s", e.get_error_info())
            device_data = {"metrics_error": e.get_error_info()}
            power_data = {}
            error_data = {}
        except Exception as e:
            logging.debug("General exception getting switch metrics: %s", e)
            device_data = {"general_error": str(e)}
            power_data = {}
            error_data = {}

        # Format and display the hierarchical output for human-readable format
        if not (self.logger.is_json_format() or self.logger.is_csv_format()):
            print(f"BRCM_SWITCH: {device_id}")
            
            # Device Information section
            print("    SWITCH_DEVICE_INFO:")
            device_order = [
                'brcm_device_class', 'brcm_device_vendor', 'brcm_device_device', 'brcm_device_revision',
                'brcm_device_subsystem_vendor', 'brcm_device_subsystem_device',
                'brcm_device_current_link_speed', 'brcm_device_max_link_speed',
                'brcm_device_current_link_width', 'brcm_device_max_link_width',
                'brcm_device_numa_node', 'brcm_device_local_cpulist', 'brcm_device_local_cpus',
                'brcm_device_irq', 'brcm_device_enable', 'brcm_device_power_state',
                'brcm_device_ari_enabled', 'brcm_device_broken_parity_status',
                'brcm_device_d3cold_allowed', 'brcm_device_msi_bus',
                'brcm_device_dma_mask_bits', 'brcm_device_consistent_dma_mask_bits',
                'brcm_device_driver_override', 'brcm_device_reset_method',
                'brcm_device_modalias', 'brcm_device_pools', 'brcm_device_resource',
                'brcm_device_uevent', 'brcm_device_config'
            ]
            
            for key in device_order:
                value = device_data.get(key, 'N/A')
                print(f"        {key.upper()}: {value}")
            
            # Power Management section
            print("    SWITCH_POWER:")
            power_order = [
                'brcm_power_async', 'brcm_power_control',
                'brcm_power_runtime_active_time', 'brcm_power_runtime_status', 
                'brcm_power_runtime_usage', 'brcm_power_runtime_active_kids',
                'brcm_power_runtime_enabled', 'brcm_power_runtime_suspended_time',
                'brcm_power_wakeup', 'brcm_power_wakeup_active', 'brcm_power_wakeup_count',
                'brcm_power_wakeup_active_count', 'brcm_power_wakeup_abort_count',
                'brcm_power_wakeup_expire_count', 'brcm_power_wakeup_last_time_ms',
                'brcm_power_wakeup_max_time_ms', 'brcm_power_wakeup_total_time_ms'
            ]
            
            for key in power_order:
                value = power_data.get(key, 'N/A')
                # Handle nested objects with value/unit structure
                if isinstance(value, dict) and 'value' in value:
                    display_value = value['value']
                    # Sanitize the extracted value
                    if isinstance(display_value, str):
                        try:
                            if all(ord(c) >= 32 and ord(c) <= 126 for c in display_value):
                                sanitized_value = display_value
                            else:
                                sanitized_value = 'N/A (Corrupted Data)'
                        except (TypeError, ValueError):
                            sanitized_value = 'N/A (Corrupted Data)'
                    else:
                        sanitized_value = display_value
                elif isinstance(value, str):
                    # Handle simple string values with proper sanitization
                    try:
                        # Check if string contains only printable characters
                        if all(ord(c) >= 32 and ord(c) <= 126 for c in value):
                            # Empty strings are valid for wakeup fields (they should show as "0")
                            if len(value.strip()) == 0:
                                # For wakeup fields, empty means "0" or "disabled"
                                if 'wakeup' in key.lower():
                                    sanitized_value = '0'
                                else:
                                    sanitized_value = 'N/A'
                            else:
                                sanitized_value = value
                        else:
                            sanitized_value = 'N/A (Corrupted Data)'
                    except (TypeError, ValueError):
                        sanitized_value = 'N/A (Corrupted Data)'
                else:
                    sanitized_value = value
                print(f"        {key.upper()}: {sanitized_value}")
            
            # Error Information section
            print("    SWITCH_ERRORS:")
            error_order = ['brcm_device_aer_dev_correctable', 'brcm_device_aer_dev_fatal', 'brcm_device_aer_dev_nonfatal']
            
            for key in error_order:
                value = error_data.get(key, 'N/A')
                print(f"        {key.upper()}: {value}")

        # Handle different output formats
        if self.logger.is_json_format() or self.logger.is_csv_format():
            # Store all data in logger for JSON/CSV formats
            all_metrics = {**device_data, **power_data, **error_data}
            for key, value in all_metrics.items():
                # Handle nested objects for JSON/CSV output
                if isinstance(value, dict) and 'value' in value:
                    # For JSON/CSV, we want to preserve the nested structure
                    sanitized_value = value
                elif isinstance(value, str):
                    try:
                        # Check if string contains only printable characters
                        if all(ord(c) >= 32 and ord(c) <= 126 for c in value):
                            # Empty strings are valid for wakeup fields (they should show as "0")
                            if len(value.strip()) == 0:
                                # For wakeup fields, empty means "0" or "disabled"
                                if 'wakeup' in key.lower():
                                    sanitized_value = '0'
                                else:
                                    sanitized_value = 'N/A'
                            else:
                                sanitized_value = value
                        else:
                            sanitized_value = 'N/A (Corrupted Data)'
                    except (TypeError, ValueError):
                        sanitized_value = 'N/A (Corrupted Data)'
                else:
                    sanitized_value = value
                self.logger._store_switch_output_amdsmi(device_id, key.upper(), sanitized_value)

            # Print JSON/CSV output
            if multiple_devices:
                self.logger.store_multiple_device_output()
            else:
                self.logger.print_output()
        elif multiple_devices:
            self.logger.store_multiple_device_output()

    def topology_nic(self, args, multiple_devices=False, gpu=None, nic=None, 
                nic_topo=None, nic_switch=None, multiple_device_enabled=None, switch=None):
        """Get topology information for NIC devices

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool, optional): True if checking for multiple devices. Defaults to False.
            nic (device_handle, optional): device_handle for target device. Defaults to None.

        Returns:
            None: Print output via AMDSMILogger to destination
        """
        if nic:
            args.nic = nic

        if args.nic == None:
            args.nic = self.device_handles_nics

        # Handle multiple NICs
        handled_multiple_nics, device_handle = self.helpers.handle_nics(args, self.logger, self.topology_nic)
        if handled_multiple_nics:
            return # This function is recursive

        args.nic = device_handle

        try:
            # Get topology info
            topo_info = amdsmi_interface.amdsmi_brcm_getString(args.nic, "get_nic_topology", 1024)
            import json
            topo_dict = json.loads(topo_info)
            
            for key, value in topo_dict.items():
                self.logger.store_nic_output(args.nic, key, value)
                
        except amdsmi_exception.AmdSmiLibraryException as e:
            logging.debug("Failed to get topology info for nic | %s", e.get_error_info())
            self.logger.store_nic_output(args.nic, 'topology_error', e.get_error_info())

        if multiple_devices:
            self.logger.store_multiple_device_output()
            return

        self.logger.print_output()

    def execute_and_save(self, command: str, output_file: str) -> None:
        """Execute a command and save its output to a file."""
        try:
            output = subprocess.check_output(command, shell=True, text=True)
            with open(output_file, "a") as file:
                file.write(f"# Command: {command}\n{output}\n\n")
        except subprocess.CalledProcessError as error:
            print(f"Failed to execute command: {error}")
            print(f"Stderr: {error.stderr}")

    def dump_nic_switch(self, args, nic=None, switch=None):
        """Dump NIC and Switch information to a file.

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            nic (device_handle, optional): NIC device handle. Defaults to None.
            switch (device_handle, optional): Switch device handle. Defaults to None.
        """

        if not args.file:
            args.file = 'dump.txt'

        isNICReq = False
        isSwitchReq = False

        """Handle empty args"""
        if not args.brcm_nic and not args.brcm_switch:
            isNICReq = True
            isSwitchReq = True

        if args.brcm_nic:
            isNICReq = True
        if args.brcm_switch:
            isSwitchReq = True
        
        format = ''
        format_name = 'human-readable'
        if args.json:
            format = ' --json'
            format_name = 'JSON'
        elif args.csv:
            format = ' --csv'
            format_name = 'CSV'

        # Determine what's being dumped
        dump_targets = []
        if isNICReq:
            dump_targets.append("NIC")
        if isSwitchReq:
            dump_targets.append("Switch")
        
        target_str = " and ".join(dump_targets) if dump_targets else "All"
        
        # Print start message
        print(f"Starting BRCM {target_str} dump to '{args.file}' ({format_name} format)...")

        with open(args.file, 'w') as file:
            file.write('')

        # Collect basic system information
        print("  Collecting system information...")
        self.execute_and_save('amd-smi', args.file)
        self.execute_and_save('amd-smi list' + format, args.file)
        
        # Collect topology information
        if isNICReq or isSwitchReq:
            print("  Collecting topology information...")
        if isNICReq:
            self.execute_and_save('amd-smi topology -nic' + format, args.file)
        if isSwitchReq: 
            self.execute_and_save('amd-smi topology -nic_switch' + format, args.file)
        
        # Collect monitoring data
        if isNICReq or isSwitchReq:
            print("  Collecting monitoring data...")
        if isNICReq:
            self.execute_and_save('amd-smi monitor -nic' + format, args.file)
        if isSwitchReq:
            self.execute_and_save('amd-smi monitor -switch' + format, args.file)
        
        # Collect metrics data
        if isNICReq or isSwitchReq:
            print("  Collecting metrics data...")
        if isNICReq:
            self.execute_and_save('amd-smi metric -nic' + format, args.file)
        if isSwitchReq:
            self.execute_and_save('amd-smi metric -switch' + format, args.file)
        
        # Collect firmware information
        if isNICReq:
            print("  Collecting firmware information...")
            self.execute_and_save('amd-smi firmware -nic' + format, args.file)
        
        # Collect PCI information
        print("  Collecting PCI device information...")
        self.execute_and_save('lspci -tvvv', args.file)

        # Get BDFs for NIC and Switch devices
        bdfs = []
        if isNICReq and self.device_handles_nics:
            devices = [nic] if nic else self.device_handles_nics
            for device in devices:
                try:
                    # Get NIC BDF using dedicated BDF function
                    if BRCM_SMI_AVAILABLE and brcmsmi_interface:
                        bdf = brcmsmi_interface.amdsmi_get_brcm_nic_device_bdf(device)
                    else:
                        bdf = "N/A"
                    if bdf and bdf != 'N/A':
                        bdfs.append(bdf)
                except Exception as e:
                    print(f"    Warning: Failed to get BDF for NIC device: {e}")

        if isSwitchReq and self.device_handles_switchs:
            devices = [switch] if switch else self.device_handles_switchs
            for device in devices:
                try:
                    # Get Switch BDF using dedicated BDF function
                    if BRCM_SMI_AVAILABLE and brcmsmi_interface:
                        bdf = brcmsmi_interface.amdsmi_get_brcm_switch_device_bdf(device)
                    else:
                        bdf = "N/A"
                    if bdf and bdf != 'N/A':
                        bdfs.append(bdf)
                except Exception as e:
                    print(f"    Warning: Failed to get BDF for Switch device: {e}")

        # Collect detailed device information
        if bdfs:
            print(f"  Collecting detailed device information for {len(bdfs)} device(s)...")
            for bdf in bdfs:
                self.execute_and_save(f'lspci -s {bdf} -vv', args.file)
                sysfs_path = f'/sys/bus/pci/devices/{bdf}'
                if os.path.exists(sysfs_path):
                    for root, dirs, files in os.walk(sysfs_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r') as the_file:
                                    contents = the_file.read()
                                    self.execute_and_save(
                                        f'cat {file_path}',
                                        args.file
                                    )
                            except Exception as e:
                                pass # since we know some known exceptions will ignore errors

        # Print final success message with summary
        file_size = os.path.getsize(args.file) if os.path.exists(args.file) else 0
        file_size_kb = file_size / 1024
        
        # Count devices
        nic_count = len(self.device_handles_nics) if hasattr(self, 'device_handles_nics') and self.device_handles_nics else 0
        switch_count = len(self.device_handles_switchs) if hasattr(self, 'device_handles_switchs') and self.device_handles_switchs else 0
        
        print(f"\n✅ Dump completed successfully!")
        print(f"   File: {args.file}")
        print(f"   Size: {file_size_kb:.1f} KB")
        print(f"   Format: {format_name}")
        if isNICReq and isSwitchReq:
            print(f"   Devices: {nic_count} NICs, {switch_count} Switches")
        elif isNICReq:
            print(f"   Devices: {nic_count} NICs")
        elif isSwitchReq:
            print(f"   Devices: {switch_count} Switches")
        print(f"   BDFs processed: {len(bdfs)}")
        print(f"\nUse 'cat {args.file}' or your preferred text editor to view the dump file.")

    def monitor_nic(self, args, multiple_devices=False, watching_output=False, nic=None,
                    watch=None, watch_time=None, iterations=None, temperature=None, brcm_nic=None):
        """Monitor BRCM NIC devices with formatted temperature and alarm status output.

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool): Whether we're monitoring multiple devices
            watching_output (bool): Whether this is a watch operation
            nic (device_handle, optional): Specific NIC device handle. Defaults to None.
            watch (int, optional): Watch interval in seconds. Defaults to None.
            watch_time (int, optional): Total watch time. Defaults to None.
            iterations (int, optional): Number of iterations. Defaults to None.
            temperature (bool, optional): Monitor temperature. Defaults to None.
            brcm_nic (bool, optional): Monitor BRCM NIC. Defaults to None.
        """
        if not self.device_handles_nics:
            logging.debug("No BRCM NIC devices found")
            return

        # Collect temperature data for all NICs
        nic_data = []
        
        devices_to_monitor = [nic] if nic else self.device_handles_nics
        
        for device_handle in devices_to_monitor:
            try:
                # Get temperature metrics for this NIC
                temp_info = amdsmi_interface.amdsmi_brcm_getString(device_handle, "get_nic_temperature", 1024)
                import json
                temp_dict = json.loads(temp_info)
                
                # Get device ID from the handle index - use try/except for watch mode robustness
                try:
                    device_id = self.device_handles_nics.index(device_handle) if device_handle in self.device_handles_nics else 0
                except (ValueError, AttributeError):
                    # Fallback for watch mode - use the loop index
                    device_id = self.device_handles_nics.index(device_handle) if self.device_handles_nics else devices_to_monitor.index(device_handle)
                
                # Extract temperature values (convert from millidegrees to degrees)
                temp_current = int(temp_dict.get('nic_temp_input', 0)) // 1000
                
                # Get alarm status directly from hardware (no calculation needed)
                crit_alarm = temp_dict.get('nic_temp_crit_alarm', 0)
                emergency_alarm = temp_dict.get('nic_temp_emergency_alarm', 0)
                shutdown_alarm = temp_dict.get('nic_temp_shutdown_alarm', 0)
                max_alarm = temp_dict.get('nic_temp_max_alarm', 0)
                
                nic_data.append({
                    'id': device_id,
                    'temp_current': temp_current,
                    'crit_alarm': crit_alarm,
                    'emergency_alarm': emergency_alarm,
                    'shutdown_alarm': shutdown_alarm,
                    'max_alarm': max_alarm
                })
                
            except amdsmi_exception.AmdSmiLibraryException as e:
                logging.debug("Failed to get temperature info for NIC %s | %s", device_handle, e.get_error_info())
                # Add default values for failed devices
                device_id = self.device_handles_nics.index(device_handle) if device_handle in self.device_handles_nics else 0
                nic_data.append({
                    'id': device_id,
                    'temp_current': 0,
                    'crit_alarm': 0,
                    'emergency_alarm': 0,
                    'shutdown_alarm': 0,
                    'max_alarm': 0
                })

        # Store data in logger for all formats
        for nic in nic_data:
            self.logger._store_nic_output_amdsmi(nic['id'], 'NIC_TEMP_CURRENT', f"{nic['temp_current']} °C")
            self.logger._store_nic_output_amdsmi(nic['id'], 'NIC_TEMP_CRIT_ALARM', nic['crit_alarm'])
            self.logger._store_nic_output_amdsmi(nic['id'], 'NIC_TEMP_EMERGENCY_ALARM', nic['emergency_alarm'])
            self.logger._store_nic_output_amdsmi(nic['id'], 'NIC_TEMP_SHUTDOWN_ALARM', nic['shutdown_alarm'])
            self.logger._store_nic_output_amdsmi(nic['id'], 'NIC_TEMP_MAX_ALARM', nic['max_alarm'])
            
            # Store each NIC's data separately for JSON/CSV output
            if self.logger.is_json_format() or self.logger.is_csv_format():
                if len(nic_data) > 1:  # Multiple NICs
                    self.logger.store_multiple_device_output()

        # Handle different output formats
        if self.logger.is_json_format() or self.logger.is_csv_format():
            # For JSON/CSV output, use logger system
            if len(nic_data) > 1:  # Multiple NICs
                self.logger.print_output(multiple_device_enabled=True)
            elif multiple_devices:
                self.logger.store_multiple_device_output()
            else:
                self.logger.print_output()
        else:
            # For human-readable output, use tabular format
            print("BRCM_NIC:")
            print("NIC     NIC_TEMP_CURRENT  NIC_TEMP_CRIT_ALARM  NIC_TEMP_EMERGENCY_ALARM  NIC_TEMP_SHUTDOWN_ALARM  NIC_TEMP_MAX_ALARM")
            
            for nic in nic_data:
                print(f"  {nic['id']:<7} {nic['temp_current']:>10} °C {nic['crit_alarm']:>20} {nic['emergency_alarm']:>23} {nic['shutdown_alarm']:>23} {nic['max_alarm']:>18}")

        if multiple_devices and not (self.logger.is_json_format() or self.logger.is_csv_format()):
            self.logger.store_multiple_device_output()
            return

    def monitor_switch(self, args, multiple_devices=False, watching_output=False, switch=None,
                       watch=None, watch_time=None, iterations=None, pcie=None, brcm_switch=None):
        """Monitor BRCM Switch devices with formatted link speed and width output.

        Args:
            args (Namespace): Namespace containing the parsed CLI args
            multiple_devices (bool): Whether we're monitoring multiple devices
            watching_output (bool): Whether this is a watch operation
            switch (device_handle, optional): Specific switch device handle. Defaults to None.
            watch (int, optional): Watch interval in seconds. Defaults to None.
            watch_time (int, optional): Total watch time. Defaults to None.
            iterations (int, optional): Number of iterations. Defaults to None.
            pcie (bool, optional): Monitor PCIe info. Defaults to None.
            brcm_switch (bool, optional): Monitor BRCM Switch. Defaults to None.
        """
        if not self.device_handles_switchs:
            logging.debug("No BRCM Switch devices found")
            return

        # Collect link info data for all switches
        switch_data = []
        
        devices_to_monitor = [switch] if switch else self.device_handles_switchs
        
        for device_handle in devices_to_monitor:
            try:
                # Get link info metrics for this switch
                link_info = amdsmi_interface.amdsmi_brcm_getString(device_handle, "get_switch_link_info", 1024)
                import json
                link_dict = json.loads(link_info)
                
                # Get device ID from the handle index - use try/except for watch mode robustness
                try:
                    device_id = self.device_handles_switchs.index(device_handle) if device_handle in self.device_handles_switchs else 0
                except (ValueError, AttributeError):
                    # Fallback for watch mode - use the loop index
                    device_id = self.device_handles_switchs.index(device_handle) if self.device_handles_switchs else devices_to_monitor.index(device_handle)
                
                # Extract link info values
                current_link_speed = link_dict.get('current_link_speed', 'N/A')
                max_link_speed = link_dict.get('max_link_speed', 'N/A')
                current_link_width = link_dict.get('current_link_width', 'N/A')
                max_link_width = link_dict.get('max_link_width', 'N/A')
                
                switch_data.append({
                    'id': device_id,
                    'current_link_speed': current_link_speed,
                    'max_link_speed': max_link_speed,
                    'current_link_width': current_link_width,
                    'max_link_width': max_link_width
                })
                
            except amdsmi_exception.AmdSmiLibraryException as e:
                logging.debug("Failed to get link info for Switch %s | %s", device_handle, e.get_error_info())
                # Add default values for failed devices
                device_id = self.device_handles_switchs.index(device_handle) if device_handle in self.device_handles_switchs else 0
                switch_data.append({
                    'id': device_id,
                    'current_link_speed': 'N/A',
                    'max_link_speed': 'N/A',
                    'current_link_width': 'N/A',
                    'max_link_width': 'N/A'
                })

        # Store data in logger for all formats
        for switch in switch_data:
            self.logger._store_switch_output_amdsmi(switch['id'], 'CURRENT_LINK_SPEED', switch['current_link_speed'])
            self.logger._store_switch_output_amdsmi(switch['id'], 'MAX_LINK_SPEED', switch['max_link_speed'])
            self.logger._store_switch_output_amdsmi(switch['id'], 'CURRENT_LINK_WIDTH', switch['current_link_width'])
            self.logger._store_switch_output_amdsmi(switch['id'], 'MAX_LINK_WIDTH', switch['max_link_width'])
            
            # Store each switch's data separately for JSON/CSV output
            if self.logger.is_json_format() or self.logger.is_csv_format():
                if len(switch_data) > 1:  # Multiple switches
                    self.logger.store_multiple_device_output()

        # Handle different output formats
        if self.logger.is_json_format() or self.logger.is_csv_format():
            # For JSON/CSV output, use logger system
            if len(switch_data) > 1:  # Multiple switches
                self.logger.print_output(multiple_device_enabled=True)
            elif multiple_devices:
                self.logger.store_multiple_device_output()
            else:
                self.logger.print_output()
        else:
            # For human-readable output, use tabular format
            print("BRCM_SWITCH:")
            print("SWITCH  CURRENT_LINK_SPEED      MAX_LINK_SPEED  CURRENT_LINK_WIDTH      MAX_LINK_WIDTH")
            
            for switch in switch_data:
                print(f"  {switch['id']:<5} {switch['current_link_speed']:>16} {switch['max_link_speed']:>21} {switch['current_link_width']:>18} {switch['max_link_width']:>15}")

        if multiple_devices and not (self.logger.is_json_format() or self.logger.is_csv_format()):
            self.logger.store_multiple_device_output()
            return

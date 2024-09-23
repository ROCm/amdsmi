#!/usr/bin/env python3
#
# Copyright (C) 2024 Advanced Micro Devices. All rights reserved.
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


import argparse
import errno
import os
import sys
import time
import collections
from typing import Optional
from typing import Union

from pathlib import Path

from _version import __version__
from amdsmi_helpers import AMDSMIHelpers
from rocm_version import get_rocm_version
import amdsmi_cli_exceptions


# Custom Help Formatter for increasing the action max length
class AMDSMIParserHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog=prog,
                         indent_increment=2,
                         max_help_position=24,
                         width=90)
        self._action_max_length = 20


# Custom Help Formatter for not duplicating the metavar in the subparsers
class AMDSMISubparserHelpFormatter(argparse.RawTextHelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=80, width=90)

    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ', '.join(action.option_strings) + ' ' + args_string


class AMDSMIParser(argparse.ArgumentParser):
    """Unified Parser for AMDSMI CLI.
        This parser doesn't access amdsmi's lib directly,but via AMDSMIHelpers,
        this allows for us to use this parser with future OS & Platform integration.

    Args:
        argparse (ArgumentParser): argparse.ArgumentParser
    """
    def __init__(self, version, list, static, firmware, bad_pages, metric,
                 process, profile, event, topology, set_value, reset, monitor,
                 rocmsmi, xgmi):

        # Helper variables
        self.helpers = AMDSMIHelpers()

        # Get choices based on driver initialized
        if self.helpers.is_amdgpu_initialized():
            self.gpu_choices, self.gpu_choices_str = self.helpers.get_gpu_choices()
        else:
            self.gpu_choices = {}
            self.gpu_choices_str = ""

        if self.helpers.is_amd_hsmp_initialized():
            self.cpu_choices, self.cpu_choices_str = self.helpers.get_cpu_choices()
            self.core_choices, self.core_choices_str = self.helpers.get_core_choices()
        else:
            self.cpu_choices = {}
            self.cpu_choices_str = ""
            self.core_choices = {}
            self.core_choices_str = ""

        self.vf_choices = ['3', '2', '1']

        version_string = f"Version: {__version__}"
        platform_string = f"Platform: {self.helpers.os_info()}"
        rocm_version = get_rocm_version()
        rocm_version_string = f"ROCm version: {rocm_version}"
        program_name = 'amd-smi'

        # Adjust argument parser options
        super().__init__(
            formatter_class= lambda prog: AMDSMIParserHelpFormatter(prog),
            description=f"AMD System Management Interface | {version_string} | {rocm_version_string} | {platform_string}",
            add_help=True,
            prog=program_name)

        # Setup subparsers
        self.subparsers = self.add_subparsers(
            title="AMD-SMI Commands",
            parser_class=argparse.ArgumentParser,
            help="Descriptions:",
            metavar='')

        # Store possible subcommands & aliases for later errors
        self.possible_commands = ['version', 'list', 'static', 'firmware', 'ucode', 'bad-pages',
                                  'metric', 'process', 'profile', 'event', 'topology', 'set',
                                  'reset', 'monitor', 'dmon', 'xgmi']

        # Add all subparsers
        self._add_version_parser(self.subparsers, version)
        self._add_list_parser(self.subparsers, list)
        self._add_static_parser(self.subparsers, static)
        self._add_firmware_parser(self.subparsers, firmware)
        self._add_bad_pages_parser(self.subparsers, bad_pages)
        self._add_metric_parser(self.subparsers, metric)
        self._add_process_parser(self.subparsers, process)
        self._add_profile_parser(self.subparsers, profile)
        self._add_event_parser(self.subparsers, event)
        self._add_topology_parser(self.subparsers, topology)
        self._add_set_value_parser(self.subparsers, set_value)
        self._add_reset_parser(self.subparsers, reset)
        self._add_monitor_parser(self.subparsers, monitor)
        self._add_rocm_smi_parser(self.subparsers, rocmsmi)
        self._add_xgmi_parser(self.subparsers, xgmi)


    def _not_negative_int(self, int_value):
        # Argument type validator
        if int_value.isdigit():  # Is digit doesn't work on negative numbers
            return int(int_value)

        outputformat = self.helpers.get_output_format()
        if int_value == "":
            raise amdsmi_cli_exceptions.AmdSmiMissingParameterValueException(int_value, outputformat)
        else:
            raise amdsmi_cli_exceptions.AmdSmiInvalidParameterValueException(int_value, outputformat)


    def _positive_int(self, int_value):
        # Argument type validator
        if int_value.isdigit():  # Is digit doesn't work on negative numbers
            if int(int_value) > 0:
                return int(int_value)

        outputformat = self.helpers.get_output_format()
        if int_value == "":
            raise amdsmi_cli_exceptions.AmdSmiMissingParameterValueException(int_value, outputformat)
        else:
            raise amdsmi_cli_exceptions.AmdSmiInvalidParameterValueException(int_value, outputformat)


    def _is_valid_string(self, string_value):
        # Argument type validator
        # This is for triggering a cli exception if an empty string is detected
        if string_value:
            return string_value

        outputformat = self.helpers.get_output_format()
        if string_value == "":
            raise amdsmi_cli_exceptions.AmdSmiMissingParameterValueException(string_value, outputformat)
        else:
            raise amdsmi_cli_exceptions.AmdSmiInvalidParameterValueException(string_value, outputformat)


    def _limit_select(self):
        """Custom action for setting clock limits"""
        output_format = self.helpers.get_output_format()

        class AMDSMILimitArgs(argparse.Action):
            def __call__(self, parser: AMDSMIParser, namespace: argparse.Namespace,
                         values: Union[str, list, None], option_string: Optional[str] = None) -> None:
                # valid values
                valid_clk_types = ('sclk', 'mclk')
                valid_lim_types = ('min', 'max')
                clk_type, lim_type, val = values
                if clk_type not in valid_clk_types:
                    raise amdsmi_cli_exceptions.AmdSmiInvalidParameterValueException(clk_type, output_format)
                if lim_type not in valid_lim_types:
                    raise amdsmi_cli_exceptions.AmdSmiInvalidParameterValueException(lim_type, output_format)
                val = int(val)
                clk_limit_args = collections.namedtuple('clk_limit_args', ['clk_type', 'lim_type', 'val'])
                setattr(namespace, self.dest, clk_limit_args(clk_type, lim_type, val))
        return AMDSMILimitArgs


    def _check_output_file_path(self):
        """ Argument action validator:
            Returns a path to a file from the output file path provided.
            If the path is a directory then create a file within it and return that file path
            If the path is a file and it exists return the file path
            If the path is a file and it doesn't exist create and return the file path
        """
        class CheckOutputFilePath(argparse.Action):
            outputformat = self.helpers.get_output_format()
            # Checks the values
            def __call__(self, parser, args, values, option_string=None):
                path = Path(values)
                if not path.exists():
                    if path.parent.is_dir():
                        path.touch()
                    else:
                        raise amdsmi_cli_exceptions.AmdSmiInvalidFilePathException(path, CheckOutputFilePath.outputformat)

                if path.is_dir():
                    file_name = f"{int(time.time())}-amdsmi-output"
                    if args.json:
                        file_name += ".json"
                    elif args.csv:
                        file_name += ".csv"
                    else:
                        file_name += ".txt"
                    path = path / file_name
                    path.touch()
                    setattr(args, self.dest, path)
                elif path.is_file():
                    path.touch()
                    setattr(args, self.dest, path)
                else:
                    raise amdsmi_cli_exceptions.AmdSmiInvalidFilePathException(path, CheckOutputFilePath.outputformat)
        return CheckOutputFilePath


    def _check_input_file_path(self):
        """ Argument action validator:
            Returns a path to a file from the input file path provided.
            If the file doesn't exist or is empty raise error
        """
        class _CheckInputFilePath(argparse.Action):
            # Checks the values
            def __call__(self, parser, args, values, option_string=None):
                path = Path(values)
                if not path.exists():
                    raise FileNotFoundError(
                        errno.ENOENT, os.strerror(errno.ENOENT), values)

                if path.is_dir():
                    raise argparse.ArgumentTypeError(
                        f"Invalid Path: {path} is directory when it needs to be a specific file")

                if path.is_file():
                    if os.stat(values).st_size == 0:
                        raise argparse.ArgumentTypeError(f"Invalid Path: {path} Input file is empty")
                    setattr(args, self.dest, path)
                else:
                    raise argparse.ArgumentTypeError(
                        f"Invalid path:{path} Could not determine if value given is a valid path")
        return _CheckInputFilePath


    def _check_watch_selected(self):
        """ Validate that the -w/--watch argument was selected
            This is because -W/--watch_time and -i/--iterations are dependent on watch
        """
        class WatchSelectedAction(argparse.Action):
            # Checks the values
            def __call__(self, parser, args, values, option_string=None):
                if args.watch is None:
                    raise argparse.ArgumentError(self, f"invalid argument: '{self.dest}' needs to be paired with -w/--watch")
                else:
                    setattr(args, self.dest, values)
        return WatchSelectedAction


    def _gpu_select(self, gpu_choices):
        """ Custom argparse action to return the device handle(s) for the gpu(s) selected
            This will set the destination (args.gpu) to a list of 1 or more device handles
            If 1 or more device handles are not found then raise an ArgumentError for the first invalid gpu seen
        """

        amdsmi_helpers = self.helpers
        class _GPUSelectAction(argparse.Action):
            ouputformat=self.helpers.get_output_format()
            # Checks the values
            def __call__(self, parser, args, values, option_string=None):
                if "all" in gpu_choices:
                    del gpu_choices["all"]
                status, gpu_format, selected_device_handles = amdsmi_helpers.get_device_handles_from_gpu_selections(gpu_selections=values,
                                                                                                         gpu_choices=gpu_choices)
                if status:
                    setattr(args, self.dest, selected_device_handles)
                else:
                    if selected_device_handles == '':
                        raise amdsmi_cli_exceptions.AmdSmiMissingParameterValueException("--gpu", _GPUSelectAction.ouputformat)
                    elif not gpu_format:
                        raise amdsmi_cli_exceptions.AmdSmiInvalidParameterValueException(selected_device_handles,
                                                                                         _GPUSelectAction.ouputformat)
                    else:
                        raise amdsmi_cli_exceptions.AmdSmiDeviceNotFoundException(selected_device_handles,
                                                                                  _GPUSelectAction.ouputformat,
                                                                                  True, False, False)

        return _GPUSelectAction


    def _cpu_select(self, cpu_choices):
        """ Custom argparse action to return the device handle(s) for the cpu(s) selected
        This will set the destination (args.cpu) to a list of 1 or more device handles
        If 1 or more device handles are not found then raise an ArgumentError for the first invalid cpu seen
        """
        amdsmi_helpers = self.helpers
        class _CPUSelectAction(argparse.Action):
            ouputformat=self.helpers.get_output_format()
            # Checks the values
            def __call__(self, parser, args, values, option_string=None):
                if "all" in cpu_choices:
                    del cpu_choices["all"]
                status, cpu_format, selected_device_handles = amdsmi_helpers.get_device_handles_from_cpu_selections(cpu_selections=values,
                                                                                                        cpu_choices=cpu_choices)
                if status:
                    setattr(args, self.dest, selected_device_handles)
                else:
                    if selected_device_handles == '':
                        raise amdsmi_cli_exceptions.AmdSmiMissingParameterValueException("--cpu", _CPUSelectAction.ouputformat)
                    elif not cpu_format:
                        raise amdsmi_cli_exceptions.AmdSmiInvalidParameterValueException(selected_device_handles,
                                                                                         _CPUSelectAction.ouputformat)
                    else:
                        raise amdsmi_cli_exceptions.AmdSmiDeviceNotFoundException(selected_device_handles,
                                                                                  _CPUSelectAction.ouputformat,
                                                                                  False, True, False)
        return _CPUSelectAction


    def _core_select(self, core_choices):
        """ Custom argparse action to return the device handle(s) for the core(s) selected
        This will set the destination (args.core) to a list of 1 or more device handles
        If 1 or more device handles are not found then raise an ArgumentError for the first invalid core seen
        """
        amdsmi_helpers = self.helpers
        class _CoreSelectAction(argparse.Action):
            ouputformat=self.helpers.get_output_format()
            # Checks the values
            def __call__(self, parser, args, values, option_string=None):
                if "all" in core_choices:
                    del core_choices["all"]
                status, core_format, selected_device_handles = amdsmi_helpers.get_device_handles_from_core_selections(core_selections=values,
                                                                                                        core_choices=core_choices)
                if status:
                    setattr(args, self.dest, selected_device_handles)
                else:
                    if selected_device_handles == '':
                        raise amdsmi_cli_exceptions.AmdSmiMissingParameterValueException("--core", _CoreSelectAction.ouputformat)
                    elif not core_format:
                        raise amdsmi_cli_exceptions.AmdSmiInvalidParameterValueException(selected_device_handles,
                                                                                         _CoreSelectAction.ouputformat)
                    else:
                        raise amdsmi_cli_exceptions.AmdSmiDeviceNotFoundException(selected_device_handles,
                                                                                  _CoreSelectAction.ouputformat,
                                                                                  False, False, True)
        return _CoreSelectAction


    def _add_command_modifiers(self, subcommand_parser):
        json_help = "Displays output in JSON format (human readable by default)."
        csv_help = "Displays output in CSV format (human readable by default)."
        file_help = "Saves output into a file on the provided path (stdout by default)."
        loglevel_choices = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        loglevel_choices_str = ", ".join(loglevel_choices)
        loglevel_help = f"Set the logging level from the possible choices:\n\t{loglevel_choices_str}"

        command_modifier_group = subcommand_parser.add_argument_group('Command Modifiers')

        # Output Format options
        logging_args = command_modifier_group.add_mutually_exclusive_group()
        logging_args.add_argument('--json', action='store_true', required=False, help=json_help)
        logging_args.add_argument('--csv', action='store_true', required=False, help=csv_help)

        command_modifier_group.add_argument('--file', action=self._check_output_file_path(), type=str, required=False, help=file_help)
        # Placing loglevel outside the subcommands so it can be used with any subcommand
        command_modifier_group.add_argument('--loglevel', action='store', type=str.upper, required=False, help=loglevel_help, default='ERROR', metavar='LEVEL',
                                            choices=loglevel_choices)


    def _add_watch_arguments(self, subcommand_parser):
        # Device arguments help text
        watch_help = "Reprint the command in a loop of INTERVAL seconds"
        watch_time_help = "The total TIME to watch the given command"
        iterations_help = "Total number of ITERATIONS to loop on the given command"

        # Mutually Exclusive Args within the subparser
        subcommand_parser.add_argument('-w', '--watch', action='store', metavar='INTERVAL',
             type=self._positive_int, required=False, help=watch_help)
        subcommand_parser.add_argument('-W', '--watch_time', action=self._check_watch_selected(), metavar='TIME',
            type=self._positive_int, required=False, help=watch_time_help)
        subcommand_parser.add_argument('-i', '--iterations', action=self._check_watch_selected(), metavar='ITERATIONS',
            type=self._positive_int, required=False, help=iterations_help)


    def _validate_cpu_core(self, value):
        if value == '':
            outputformat = self.helpers.get_output_format()
            raise amdsmi_cli_exceptions.AmdSmiMissingParameterValueException(value, outputformat)
        if isinstance(value, str):
            if value.lower() == "all":
                return value
            if value.isdigit():
                if int(value) < 0:
                    outputformat = self.helpers.get_output_format()
                    raise amdsmi_cli_exceptions.AmdSmiInvalidParameterValueException(value, outputformat)
            else:
                outputformat = self.helpers.get_output_format()
                raise amdsmi_cli_exceptions.AmdSmiInvalidParameterValueException(value, outputformat)

        if isinstance(value, int):
            if int(value) < 0:
                outputformat = self.helpers.get_output_format()
                raise amdsmi_cli_exceptions.AmdSmiInvalidParameterValueException(value, outputformat)

        return value


    def _add_device_arguments(self, subcommand_parser, required=False):
        # Device arguments help text
        gpu_help = f"Select a GPU ID, BDF, or UUID from the possible choices:\n{self.gpu_choices_str}"
        vf_help = "Gets general information about the specified VF (timeslice, fb info, …).\
                    \nAvailable only on virtualization OSs"
        cpu_help = f"Select a CPU ID from the possible choices:\n{self.cpu_choices_str}"
        core_help = f"Select a Core ID from the possible choices:\n{self.core_choices_str}"


        # Mutually Exclusive Args within the subparser
        device_args = subcommand_parser.add_mutually_exclusive_group(required=required)

        if self.helpers.is_amdgpu_initialized():
            device_args.add_argument('-g', '--gpu', action=self._gpu_select(self.gpu_choices),
                                        nargs='+', help=gpu_help)

        if self.helpers.is_amd_hsmp_initialized():
            device_args.add_argument('-U', '--cpu', type=self._validate_cpu_core,
                                        action=self._cpu_select(self.cpu_choices),
                                        nargs='+', help=cpu_help)
            if subcommand_parser._optionals.title != "Static Arguments":
                device_args.add_argument('-O', '--core', type=self._validate_cpu_core,
                                            action=self._core_select(self.core_choices),
                                            nargs='+', help=core_help)

        if self.helpers.is_hypervisor():
            device_args.add_argument('-v', '--vf', action='store', nargs='+',
                                        help=vf_help, choices=self.vf_choices)


    def _validate_set_clock(self, validate_clock_type=True):
        """ Validate Clock input"""
        amdsmi_helpers = self.helpers
        class _ValidateClockType(argparse.Action):
            # Checks the clock type and clock values
            def __call__(self, parser, args, values, option_string=None):
                if validate_clock_type:
                    clock_type = values[0]
                    clock_types = amdsmi_helpers.get_clock_types()[0]
                    valid_clock_type, amdsmi_clock_type = amdsmi_helpers.validate_clock_type(input_clock_type=clock_type)
                    if not valid_clock_type:
                        raise argparse.ArgumentError(self, f"Invalid argument: '{clock_type}' needs to be a valid clock type:{clock_types}")

                    clock_levels = values[1:]
                else:
                    clock_levels = values

                freq_bitmask = 0
                for level in clock_levels:
                    if level > 63:
                        raise argparse.ArgumentError(self, f"Invalid argument: '{level}' needs to be a valid clock level 0-63")
                    freq_bitmask |= (1 << level)

                if validate_clock_type:
                    setattr(args, self.dest, (amdsmi_clock_type, freq_bitmask))
                else:
                    setattr(args, self.dest, freq_bitmask)
        return _ValidateClockType


    def _prompt_spec_warning(self):
        """ Prompt out of spec warning"""
        amdsmi_helpers = self.helpers
        class _PromptSpecWarning(argparse.Action):
            # Checks the values
            def __call__(self, parser, args, values, option_string=None):
                amdsmi_helpers.confirm_out_of_spec_warning()
                setattr(args, self.dest, values)
        return _PromptSpecWarning


    def _validate_fan_speed(self):
        """ Validate fan speed input"""
        amdsmi_helpers = self.helpers
        class _ValidateFanSpeed(argparse.Action):
            # Checks the values
            def __call__(self, parser, args, values, option_string=None):
                if isinstance(values, str):
                    # Convert percentage to fan level
                    if '%' in values:
                        try:
                            amdsmi_helpers.confirm_out_of_spec_warning()
                            values = int(int(values[:-1]) / 100 * 255)
                            setattr(args, self.dest, values)
                        except ValueError as e:
                            raise argparse.ArgumentError(self, f"Invalid argument: '{values}' needs to be 0-100%")
                    else: # Store the fan level as fan_speed
                        values = int(values)
                        if 0 <= values <= 255:
                            amdsmi_helpers.confirm_out_of_spec_warning()
                            setattr(args, self.dest, values)
                        else:
                            raise argparse.ArgumentError(self, f"Invalid argument: '{values}' needs to be 0-255")
                else:
                    raise argparse.ArgumentError(self, f"Invalid argument: '{values}' needs to be 0-255 or 0-100%")
        return _ValidateFanSpeed


    def _validate_overdrive_percent(self):
        """ Validate overdrive percentage input"""
        amdsmi_helpers = self.helpers
        class _ValidateOverdrivePercent(argparse.Action):
            # Checks the values
            def __call__(self, parser, args, values, option_string=None):
                if isinstance(values, str):
                    try:
                        if values[-1] == '%':
                            over_drive_percent = int(values[:-1])
                        else:
                            over_drive_percent = int(values)

                        if 0 <= over_drive_percent <= 20:
                            amdsmi_helpers.confirm_out_of_spec_warning()
                            setattr(args, self.dest, over_drive_percent)
                        else:
                            raise argparse.ArgumentError(self, f"Invalid argument: '{values}' needs to be within range 0-20 or 0-20%")
                    except ValueError:
                        raise argparse.ArgumentError(self, f"Invalid argument: '{values}' needs to be 0-20 or 0-20%")
                else:
                    raise argparse.ArgumentError(self, f"Invalid argument: '{values}' needs to be 0-20 or 0-20%")
        return _ValidateOverdrivePercent


    def _add_version_parser(self, subparsers, func):
        # Subparser help text
        version_help = "Display version information"

        # Create version subparser
        version_parser = subparsers.add_parser('version', help=version_help, description=None)
        version_parser._optionals.title = None
        version_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        version_parser.set_defaults(func=func)

        # Add Universal Arguments
        self._add_command_modifiers(version_parser)


    def _add_list_parser(self, subparsers, func):
        if not self.helpers.is_amdgpu_initialized():
            # The list subcommand is only applicable to systems with amdgpu initialized
            return

        # Subparser help text
        list_help = "List GPU information"
        list_subcommand_help = "Lists all detected devices on the system\
                            \nLists the BDF, UUID, KFD_ID, and NODE_ID for each GPU and/or CPUs\
                            \nIn virtualization environments, it can also list VFs associated to each\
                            \nGPU with some basic information for each VF."

        # Create list subparser
        list_parser = subparsers.add_parser('list', help=list_help, description=list_subcommand_help)
        list_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        list_parser.set_defaults(func=func)

        # Add Universal Arguments
        self._add_command_modifiers(list_parser)
        self._add_device_arguments(list_parser, required=False)


    def _add_static_parser(self, subparsers, func):
        # Subparser help text
        static_help = "Gets static information about the specified GPU"
        static_subcommand_help = "If no GPU is specified, returns static information for all GPUs on the system.\
                                \nIf no static argument is provided, all static information will be displayed."
        static_optionals_title = "Static Arguments"

        # Optional arguments help text
        asic_help = "All asic information"
        bus_help = "All bus information"
        vbios_help = "All video bios information (if available)"
        limit_help = "All limit metric values (i.e. power and thermal limits)"
        driver_help = "Displays driver version"
        vram_help = "All vram information"
        cache_help = "All cache information"
        board_help = "All board information"
        soc_pstate_help = "The available soc pstate policy"
        xgmi_plpd_help = "The available XGMI per-link power down policy"
        process_isolation_help = "The process isolation status"

        # Options arguments help text for Hypervisors and Baremetal
        ras_help = "Displays RAS features information"
        numa_help = "All numa node information" # Linux Baremetal only
        partition_help = "Partition information"

        # Options arguments help text for Hypervisors
        dfc_help = "All DFC FW table information"
        fb_help = "Displays Frame Buffer information"
        num_vf_help = "Displays number of supported and enabled VFs"

        # Options arguments help text for CPUs
        smu_help = "All SMU FW information"
        interface_help = "Displays hsmp interface version"

        # Create static subparser
        static_parser = subparsers.add_parser('static', help=static_help, description=static_subcommand_help)
        static_parser._optionals.title = static_optionals_title
        static_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        static_parser.set_defaults(func=func)

        # Add Universal Arguments
        self._add_device_arguments(static_parser, required=False)

        # Handle GPU Options
        if self.helpers.is_amdgpu_initialized():
            static_parser.add_argument('-a', '--asic', action='store_true', required=False, help=asic_help)
            static_parser.add_argument('-b', '--bus', action='store_true', required=False, help=bus_help)
            static_parser.add_argument('-V', '--vbios', action='store_true', required=False, help=vbios_help)
            static_parser.add_argument('-d', '--driver', action='store_true', required=False, help=driver_help)
            static_parser.add_argument('-v', '--vram', action='store_true', required=False, help=vram_help)
            static_parser.add_argument('-c', '--cache', action='store_true', required=False, help=cache_help)
            static_parser.add_argument('-B', '--board', action='store_true', required=False, help=board_help)
            static_parser.add_argument('-R', '--process-isolation', action='store_true', required=False, help=process_isolation_help)
            static_parser.add_argument('-r', '--ras', action='store_true', required=False, help=ras_help)

            # Options to display on Hypervisors and Baremetal
            if self.helpers.is_hypervisor() or self.helpers.is_baremetal():
                static_parser.add_argument('-p', '--partition', action='store_true', required=False, help=partition_help)
                static_parser.add_argument('-l', '--limit', action='store_true', required=False, help=limit_help)
                static_parser.add_argument('-P', '--soc-pstate', action='store_true', required=False, help=soc_pstate_help)
                static_parser.add_argument('-x', '--xgmi-plpd', action='store_true', required=False, help=xgmi_plpd_help)

            if self.helpers.is_linux() and not self.helpers.is_virtual_os():
                static_parser.add_argument('-u', '--numa', action='store_true', required=False, help=numa_help)

            # Options to only display on a Hypervisor TODO: Add hypervisor driver check
            if self.helpers.is_hypervisor():
                static_parser.add_argument('-d', '--dfc-ucode', action='store_true', required=False, help=dfc_help)
                static_parser.add_argument('-f', '--fb-info', action='store_true', required=False, help=fb_help)
                static_parser.add_argument('-n', '--num-vf', action='store_true', required=False, help=num_vf_help)

        # Handle CPU Options
        if self.helpers.is_amd_hsmp_initialized():
            cpu_group = static_parser.add_argument_group("CPU Arguments")
            cpu_group.add_argument('-s', '--smu', action='store_true', required=False, help=smu_help)
            cpu_group.add_argument('-i', '--interface-ver', action='store_true', required=False, help=interface_help)

        # Add command modifiers to the bottom
        self._add_command_modifiers(static_parser)


    def _add_firmware_parser(self, subparsers, func):
        if not self.helpers.is_amdgpu_initialized():
            # The firmware subcommand is only applicable to systems with amdgpu initialized
            return

        # Subparser help text
        firmware_help = "Gets firmware information about the specified GPU"
        firmware_subcommand_help = "If no GPU is specified, return firmware information for all GPUs on the system."
        firmware_optionals_title = "Firmware Arguments"

        # Optional arguments help text
        fw_list_help = "All FW list information"
        err_records_help = "All error records information"

        # Create firmware subparser
        firmware_parser = subparsers.add_parser('firmware', help=firmware_help, description=firmware_subcommand_help, aliases=['ucode'])
        firmware_parser._optionals.title = firmware_optionals_title
        firmware_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        firmware_parser.set_defaults(func=func)

        # Add Universal Arguments
        self._add_command_modifiers(firmware_parser)
        self._add_device_arguments(firmware_parser, required=False)

        # Optional Args
        firmware_parser.add_argument('-f', '--ucode-list', '--fw-list', dest='fw_list', action='store_true', required=False, help=fw_list_help, default=True)

        # Options to only display on a Hypervisor
        if self.helpers.is_hypervisor():
            firmware_parser.add_argument('-e', '--error-records', action='store_true', required=False, help=err_records_help)


    def _add_bad_pages_parser(self, subparsers, func):
        if not (self.helpers.is_baremetal() and self.helpers.is_linux()):
            # The bad_pages subcommand is only applicable to Linux Baremetal systems
            return

        if not self.helpers.is_amdgpu_initialized():
            # The bad_pages subcommand is only applicable to systems with amdgpu initialized
            return


        # Subparser help text
        bad_pages_help = "Gets bad page information about the specified GPU"
        bad_pages_subcommand_help = "If no GPU is specified, return bad page information for all GPUs on the system."
        bad_pages_optionals_title = "Bad Pages Arguments"

        # Optional arguments help text
        pending_help = "Displays all pending retired pages"
        retired_help = "Displays retired pages"
        un_res_help = "Displays unreservable pages"

        # Create bad_pages subparser
        bad_pages_parser = subparsers.add_parser('bad-pages', help=bad_pages_help, description=bad_pages_subcommand_help)
        bad_pages_parser._optionals.title = bad_pages_optionals_title
        bad_pages_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        bad_pages_parser.set_defaults(func=func)

        # Add Universal Arguments
        self._add_command_modifiers(bad_pages_parser)
        self._add_device_arguments(bad_pages_parser, required=False)

        # Optional Args
        bad_pages_parser.add_argument('-p', '--pending', action='store_true', required=False, help=pending_help)
        bad_pages_parser.add_argument('-r', '--retired', action='store_true', required=False, help=retired_help)
        bad_pages_parser.add_argument('-u', '--un-res', action='store_true', required=False, help=un_res_help)


    def _add_metric_parser(self, subparsers, func):
        # Subparser help text
        metric_help = "Gets metric/performance information about the specified GPU"
        metric_subcommand_help = "If no GPU is specified, returns metric information for all GPUs on the system.\
                                \nIf no metric argument is provided all metric information will be displayed."
        metric_optionals_title = "Metric arguments"

        # Optional arguments help text
        usage_help = "Displays engine usage information"

        # Help text for Arguments only Available on Linux Virtual OS and Baremetal platforms
        mem_usage_help = "Memory usage per block"

        # Help text for Arguments only on Hypervisor and Baremetal platforms
        power_help = "Current power usage"
        clock_help = "Average, max, and current clock frequencies"
        temperature_help = "Current temperatures"
        ecc_help = "Total number of ECC errors"
        ecc_blocks_help = "Number of ECC errors per block"
        pcie_help = "Current PCIe speed, width, and replay count"

        # Help text for Arguments only on Linux Baremetal platforms
        fan_help = "Current fan speed"
        vc_help = "Display voltage curve"
        overdrive_help = "Current GPU clock overdrive and GPU memory clock overdrive level"
        perf_level_help = "Current DPM performance level"
        xgmi_err_help = "XGMI error information since last read"
        energy_help = "Amount of energy consumed"

        # Help text for Arguments only on Hypervisors
        schedule_help = "All scheduling information"
        guard_help = "All guard information"
        guest_data_help = "All guest data information"
        fb_usage_help = "Displays total and used Frame Buffer usage information"
        xgmi_help = "Table of current XGMI metrics information"

        # Help text for cpu options
        cpu_power_metrics_help = "CPU power metrics"
        cpu_proc_help = "Displays prochot status"
        cpu_freq_help = "Displays currentFclkMemclk frequencies and cclk frequency limit"
        cpu_c0_res_help = "Displays C0 residency"
        cpu_lclk_dpm_help = "Displays lclk dpm level range. Requires socket ID and NBOID as inputs"
        cpu_pwr_svi_telemtry_rails_help = "Displays svi based telemetry for all rails"
        cpu_io_bandwidth_help = "Displays current IO bandwidth for the selected CPU.\
        \n input parameters are bandwidth type(1) and link ID encodings\
        \n i.e. P2, P3, G0 - G7"
        cpu_xgmi_bandwidth_help = "Displays current XGMI bandwidth for the selected CPU\
        \n input parameters are bandwidth type(1,2,4) and link ID encodings\
        \n i.e. P2, P3, G0 - G7"
        cpu_metrics_ver_help = "Displays metrics table version"
        cpu_metrics_table_help = "Displays metric table"
        cpu_socket_energy_help = "Displays socket energy for the selected CPU socket"
        cpu_ddr_bandwidth_help = "Displays per socket max ddr bw, current utilized bw,\
        \n and current utilized ddr bw in percentage"
        cpu_temp_help = "Displays cpu socket temperature"
        cpu_dimm_temp_range_rate_help = "Displays dimm temperature range and refresh rate"
        cpu_dimm_pow_consumption_help = "Displays dimm power consumption"
        cpu_dimm_thermal_sensor_help = "Displays dimm thermal sensor"

        # Help text for core options
        core_energy_help = "Displays core energy for the selected core"
        core_boost_limit_help = "Get boost limit for the selected cores"
        core_curr_active_freq_core_limit_help = "Get Current CCLK limit set per Core"

        # Create metric subparser
        metric_parser = subparsers.add_parser('metric', help=metric_help, description=metric_subcommand_help)
        metric_parser._optionals.title = metric_optionals_title
        metric_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        metric_parser.set_defaults(func=func)

        # Add Universal Arguments
        self._add_device_arguments(metric_parser, required=False)

        # Add Watch args
        self._add_watch_arguments(metric_parser)

        # Optional Args for Linux Virtual OS and Baremetal systems
        if not self.helpers.is_hypervisor() and not self.helpers.is_windows():
            metric_parser.add_argument('-m', '--mem-usage', action='store_true', required=False, help=mem_usage_help)

        if self.helpers.is_amdgpu_initialized():
            # Optional Args for Hypervisors and Baremetal systems
            if self.helpers.is_hypervisor() or self.helpers.is_baremetal() or self.helpers.is_linux():
                metric_parser.add_argument('-u', '--usage', action='store_true', required=False, help=usage_help)
                metric_parser.add_argument('-p', '--power', action='store_true', required=False, help=power_help)
                metric_parser.add_argument('-c', '--clock', action='store_true', required=False, help=clock_help)
                metric_parser.add_argument('-t', '--temperature', action='store_true', required=False, help=temperature_help)
                metric_parser.add_argument('-P', '--pcie', action='store_true', required=False, help=pcie_help)

            # Options that only apply to Hypervisors and Baremetal Linux
            if self.helpers.is_hypervisor() or (self.helpers.is_baremetal() and self.helpers.is_linux()):
                metric_parser.add_argument('-e', '--ecc', action='store_true', required=False, help=ecc_help)
                metric_parser.add_argument('-k', '--ecc-blocks', action='store_true', required=False, help=ecc_blocks_help)

            # Optional Args for Linux Baremetal Systems
            if self.helpers.is_baremetal() and self.helpers.is_linux():
                metric_parser.add_argument('-f', '--fan', action='store_true', required=False, help=fan_help)
                metric_parser.add_argument('-C', '--voltage-curve', action='store_true', required=False, help=vc_help)
                metric_parser.add_argument('-o', '--overdrive', action='store_true', required=False, help=overdrive_help)
                metric_parser.add_argument('-l', '--perf-level', action='store_true', required=False, help=perf_level_help)
                metric_parser.add_argument('-x', '--xgmi-err', action='store_true', required=False, help=xgmi_err_help)
                metric_parser.add_argument('-E', '--energy', action='store_true', required=False, help=energy_help)

            # Options to only display to Hypervisors
            if self.helpers.is_hypervisor():
                metric_parser.add_argument('-s', '--schedule', action='store_true', required=False, help=schedule_help)
                metric_parser.add_argument('-G', '--guard', action='store_true', required=False, help=guard_help)
                metric_parser.add_argument('-u', '--guest-data', action='store_true', required=False, help=guest_data_help)
                metric_parser.add_argument('-f', '--fb-usage', action='store_true', required=False, help=fb_usage_help)
                metric_parser.add_argument('-m', '--xgmi', action='store_true', required=False, help=xgmi_help)

        if self.helpers.is_amd_hsmp_initialized():
            # Optional Args for CPUs
            cpu_group = metric_parser.add_argument_group("CPU Arguments")
            cpu_group.add_argument('--cpu-power-metrics', action='store_true', required=False, help=cpu_power_metrics_help)
            cpu_group.add_argument('--cpu-prochot', action='store_true', required=False, help=cpu_proc_help)
            cpu_group.add_argument('--cpu-freq-metrics', action='store_true', required=False, help=cpu_freq_help)
            cpu_group.add_argument('--cpu-c0-res', action='store_true', required=False, help=cpu_c0_res_help)
            cpu_group.add_argument('--cpu-lclk-dpm-level', action='append', required=False, type=self._not_negative_int,
                                    nargs=1, metavar=("NBIOID"), help=cpu_lclk_dpm_help)
            cpu_group.add_argument('--cpu-pwr-svi-telemtry-rails', action='store_true', required=False,
                                    help=cpu_pwr_svi_telemtry_rails_help)
            cpu_group.add_argument('--cpu-io-bandwidth', action='append', required=False, nargs=2,
                                    metavar=("IO_BW", "LINKID_NAME"), help=cpu_io_bandwidth_help)
            cpu_group.add_argument('--cpu-xgmi-bandwidth', action='append', required=False, nargs=2,
                                    metavar=("XGMI_BW", "LINKID_NAME"), help=cpu_xgmi_bandwidth_help)
            cpu_group.add_argument('--cpu-metrics-ver', action='store_true', required=False, help=cpu_metrics_ver_help)
            cpu_group.add_argument('--cpu-metrics-table', action='store_true', required=False, help=cpu_metrics_table_help)
            cpu_group.add_argument('--cpu-socket-energy', action='store_true', required=False, help=cpu_socket_energy_help)
            cpu_group.add_argument('--cpu-ddr-bandwidth', action='store_true', required=False, help=cpu_ddr_bandwidth_help)
            cpu_group.add_argument('--cpu-temp', action='store_true', required=False, help=cpu_temp_help)
            cpu_group.add_argument('--cpu-dimm-temp-range-rate', action='append', required=False, type=lambda x: int(x, 0),
                                    nargs=1, metavar=("DIMM_ADDR"), help=cpu_dimm_temp_range_rate_help)
            cpu_group.add_argument('--cpu-dimm-pow-consumption', action='append', required=False, type=lambda x: int(x, 0),
                                    nargs=1, metavar=("DIMM_ADDR"), help=cpu_dimm_pow_consumption_help)
            cpu_group.add_argument('--cpu-dimm-thermal-sensor', action='append', required=False, type=lambda x: int(x, 0),
                                    nargs=1, metavar=("DIMM_ADDR"), help=cpu_dimm_thermal_sensor_help)

            # Optional Args for CPU cores
            core_group = metric_parser.add_argument_group("CPU Core Arguments")
            core_group.add_argument('--core-boost-limit', action='store_true', required=False, help=core_boost_limit_help)
            core_group.add_argument('--core-curr-active-freq-core-limit', action='store_true', required=False,
                                    help=core_curr_active_freq_core_limit_help)
            core_group.add_argument('--core-energy', action='store_true', required=False, help=core_energy_help)

        # Add command modifiers to the bottom
        self._add_command_modifiers(metric_parser)


    def _add_process_parser(self, subparsers, func):
        if self.helpers.is_hypervisor():
            # Don't add this subparser on Hypervisors
            # This subparser is only available to Guest and Baremetal systems
            return

        if not self.helpers.is_amdgpu_initialized():
            # The process subcommand is currently only applicable to systems with amdgpu initialized
            return

        # Subparser help text
        process_help = "Lists general process information running on the specified GPU"
        process_subcommand_help = "If no GPU is specified, returns information for all GPUs on the system.\
                                \nIf no process argument is provided all process information will be displayed."
        process_optionals_title = "Process arguments"

        # Optional Arguments help text
        general_help = "pid, process name, memory usage"
        engine_help = "All engine usages"
        pid_help = "Gets all process information about the specified process based on Process ID"
        name_help = "Gets all process information about the specified process based on Process Name.\
                    \nIf multiple processes have the same name information is returned for all of them."


        # Create process subparser
        process_parser = subparsers.add_parser('process', help=process_help, description=process_subcommand_help)
        process_parser._optionals.title = process_optionals_title
        process_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        process_parser.set_defaults(func=func)

        # Add Universal Arguments
        self._add_command_modifiers(process_parser)
        self._add_device_arguments(process_parser, required=False)

        # Add Watch args
        self._add_watch_arguments(process_parser)

        # Optional Args
        process_parser.add_argument('-G', '--general', action='store_true', required=False, help=general_help)
        process_parser.add_argument('-e', '--engine', action='store_true', required=False, help=engine_help)
        process_parser.add_argument('-p', '--pid', action='store', type=self._not_negative_int, required=False, help=pid_help)
        process_parser.add_argument('-n', '--name', action='store', type=self._is_valid_string, required=False, help=name_help)


    def _add_profile_parser(self, subparsers, func):
        if not (self.helpers.is_windows() and self.helpers.is_hypervisor()):
            # This subparser only applies to Hypervisors
            return

        # Subparser help text
        profile_help = "Displays information about all profiles and current profile"
        profile_subcommand_help = "If no GPU is specified, returns information for all GPUs on the system."
        profile_optionals_title = "Profile Arguments"

        # Create profile subparser
        profile_parser = subparsers.add_parser('profile', help=profile_help, description=profile_subcommand_help)
        profile_parser._optionals.title = profile_optionals_title
        profile_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        profile_parser.set_defaults(func=func)

        # Add Universal Arguments
        self._add_command_modifiers(profile_parser)
        self._add_device_arguments(profile_parser, required=False)


    def _add_event_parser(self, subparsers, func):
        if not self.helpers.is_amdgpu_initialized():
            # The event subcommand is only applicable to systems with amdgpu initialized
            return

        # Subparser help text
        event_help = "Displays event information for the given GPU"
        event_subcommand_help = "If no GPU is specified, returns event information for all GPUs on the system."
        event_optionals_title = "Event Arguments"

        # Create event subparser
        event_parser = subparsers.add_parser('event', help=event_help, description=event_subcommand_help)
        event_parser._optionals.title = event_optionals_title
        event_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        event_parser.set_defaults(func=func)

        # Add Universal Arguments
        self._add_command_modifiers(event_parser)
        self._add_device_arguments(event_parser, required=False)


    def _add_topology_parser(self, subparsers, func):
        if not(self.helpers.is_baremetal() and self.helpers.is_linux()):
            # This subparser is only applicable to Baremetal Linux
            return

        if not self.helpers.is_amdgpu_initialized():
            # The topology subcommand is only applicable to systems with amdgpu initialized
            return

        # Subparser help text
        topology_help = "Displays topology information of the devices"
        topology_subcommand_help = "If no GPU is specified, returns information for all GPUs on the system.\
                                \nIf no topology argument is provided all topology information will be displayed."
        topology_optionals_title = "Topology arguments"

        # Help text for Arguments only on Guest and BM platforms
        access_help = "Displays link accessibility between GPUs"
        weight_help = "Displays relative weight between GPUs"
        hops_help = "Displays the number of hops between GPUs"
        link_type_help = "Displays the link type between GPUs"
        numa_bw_help = "Display max and min bandwidth between nodes"
        coherent_help = "Display cache coherant (or non-coherant) link capability between nodes"
        atomics_help = "Display 32 and 64-bit atomic io link capability between nodes"
        dma_help = "Display P2P direct memory access (DMA) link capability between nodes"
        bi_dir_help = "Display P2P bi-directional link capability between nodes"

        # Create topology subparser
        topology_parser = subparsers.add_parser('topology', help=topology_help, description=topology_subcommand_help)
        topology_parser._optionals.title = topology_optionals_title
        topology_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        topology_parser.set_defaults(func=func)

        # Add Universal Arguments
        self._add_command_modifiers(topology_parser)
        self._add_device_arguments(topology_parser, required=False)

        # Optional Args
        topology_parser.add_argument('-a', '--access', action='store_true', required=False, help=access_help)
        topology_parser.add_argument('-w', '--weight', action='store_true', required=False, help=weight_help)
        topology_parser.add_argument('-o', '--hops', action='store_true', required=False, help=hops_help)
        topology_parser.add_argument('-t', '--link-type', action='store_true', required=False, help=link_type_help)
        topology_parser.add_argument('-b', '--numa-bw', action='store_true', required=False, help=numa_bw_help)
        topology_parser.add_argument('-c', '--coherent', action='store_true', required=False, help=coherent_help)
        topology_parser.add_argument('-n', '--atomics', action='store_true', required=False, help=atomics_help)
        topology_parser.add_argument('-d', '--dma', action='store_true', required=False, help=dma_help)
        topology_parser.add_argument('-z', '--bi-dir', action='store_true', required=False, help=bi_dir_help)


    def _add_set_value_parser(self, subparsers, func):
        if not self.helpers.is_linux():
            # This subparser is only applicable to Linux
            return

        # Subparser help text
        set_value_help = "Set options for devices"
        set_value_subcommand_help = "A GPU must be specified to set a configuration.\
                                    \nA set argument must be provided; Multiple set arguments are accepted"
        set_value_optionals_title = "Set Arguments"

        # Help text for Arguments only on BM platforms
        set_fan_help = "Set GPU fan speed (0-255 or 0-100%%)"
        set_perf_level_help = "Set performance level"
        set_profile_help = "Set power profile level (#) or a quoted string of custom profile attributes"
        set_perf_det_help = "Set GPU clock frequency limit and performance level to determinism to get minimal performance variation"
        compute_partition_choices_str = ", ".join(self.helpers.get_compute_partition_types())
        memory_partition_choices_str = ", ".join(self.helpers.get_memory_partition_types())
        set_compute_partition_help = f"Set one of the following the compute partition modes:\n\t{compute_partition_choices_str}"
        set_memory_partition_help = f"Set one of the following the memory partition modes:\n\t{memory_partition_choices_str}"
        set_power_cap_help = "Set power capacity limit"
        set_soc_pstate_help = "Set the GPU soc pstate policy using policy id\n"
        set_xgmi_plpd_help = "Set the GPU XGMI per-link power down policy using policy id\n"
        set_process_isolation_help = "Enable or disable the GPU process isolation: 0 for disable and 1 for enable.\n"
        set_clk_limit_help = "Sets the sclk (aka gfxclk) or mclk minimum and maximum frequencies. \nOf form: amd-smi set -L (sclk | mclk) (min | max) value"

        # Help text for CPU set options
        set_cpu_pwr_limit_help = "Set power limit for the given socket. Input parameter is power limit value."
        set_cpu_xgmi_link_width_help = "Set max and Min linkwidth. Input parameters are min and max link width values"
        set_cpu_lclk_dpm_level_help = "Sets the max and min dpm level on a given NBIO.\
        \n Input parameters are die_index, min dpm, max dpm."
        set_cpu_pwr_eff_mode_help = "Sets the power efficency mode policy. Input parameter is mode."
        set_cpu_gmi3_link_width_help = "Sets max and min gmi3 link width range"
        set_cpu_pcie_link_rate_help = "Sets pcie link rate"
        set_cpu_df_pstate_range_help = "Sets max and min df-pstates"
        set_cpu_enable_apb_help = "Enables the DF p-state performance boost algorithm"
        set_cpu_disable_apb_help = "Disables the DF p-state performance boost algorithm. Input parameter is DFPstate (0-3)"
        set_soc_boost_limit_help = "Sets the boost limit for the given socket. Input parameter is socket BOOST_LIMIT value"

        # Help text for CPU Core set options
        set_core_boost_limit_help = "Sets the boost limit for the given core. Input parameter is core BOOST_LIMIT value"

        # Create set_value subparser
        set_value_parser = subparsers.add_parser('set', help=set_value_help, description=set_value_subcommand_help)
        set_value_parser._optionals.title = set_value_optionals_title
        set_value_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        set_value_parser.set_defaults(func=func)

        # Device args are required as safeguard from the user applying the operation to all gpus unintentionally
        self._add_device_arguments(set_value_parser, required=True)

        if self.helpers.is_amdgpu_initialized():
            if self.helpers.is_baremetal():
                # Optional GPU Args
                set_value_parser.add_argument('-f', '--fan', action=self._validate_fan_speed(), required=False, help=set_fan_help, metavar='%')
                set_value_parser.add_argument('-l', '--perf-level', action='store', choices=self.helpers.get_perf_levels()[0], type=str.upper, required=False, help=set_perf_level_help, metavar='LEVEL')
                set_value_parser.add_argument('-P', '--profile', action='store', required=False, help=set_profile_help, metavar='SETPROFILE')
                set_value_parser.add_argument('-d', '--perf-determinism', action='store', type=self._not_negative_int, required=False, help=set_perf_det_help, metavar='SCLKMAX')
                set_value_parser.add_argument('-C', '--compute-partition', action='store', choices=self.helpers.get_compute_partition_types(), type=str.upper, required=False, help=set_compute_partition_help, metavar='PARTITION')
                set_value_parser.add_argument('-M', '--memory-partition', action='store', choices=self.helpers.get_memory_partition_types(), type=str.upper, required=False, help=set_memory_partition_help, metavar='PARTITION')
                set_value_parser.add_argument('-o', '--power-cap', action='store', type=self._positive_int, required=False, help=set_power_cap_help, metavar='WATTS')
                set_value_parser.add_argument('-p', '--soc-pstate', action='store', required=False,  type=self._not_negative_int, help=set_soc_pstate_help, metavar='POLICY_ID')
                set_value_parser.add_argument('-x', '--xgmi-plpd', action='store', required=False,  type=self._not_negative_int, help=set_xgmi_plpd_help, metavar='POLICY_ID')
                set_value_parser.add_argument('-L', '--clk-limit', action=self._limit_select(), nargs=3, required=False, help=set_clk_limit_help, metavar=('CLK_TYPE', 'LIM_TYPE', 'VALUE'))

            set_value_parser.add_argument('-R', '--process-isolation', action='store', choices=[0,1], type=self._not_negative_int, required=False, help=set_process_isolation_help, metavar='STATUS')

        if self.helpers.is_amd_hsmp_initialized():
            if self.helpers.is_baremetal():
                # Optional CPU Args
                cpu_group = set_value_parser.add_argument_group("CPU Arguments")
                cpu_group.add_argument('--cpu-pwr-limit', action='append', required=False, type=self._positive_int, nargs=1, metavar=("PWR_LIMIT"), help=set_cpu_pwr_limit_help)
                cpu_group.add_argument('--cpu-xgmi-link-width', action='append', required=False, type=self._not_negative_int, nargs=2, metavar=("MIN_WIDTH", "MAX_WIDTH"), help=set_cpu_xgmi_link_width_help)
                cpu_group.add_argument('--cpu-lclk-dpm-level', action='append', required=False, type=self._not_negative_int, nargs=3, metavar=("NBIOID", "MIN_DPM", "MAX_DPM"), help=set_cpu_lclk_dpm_level_help)
                cpu_group.add_argument('--cpu-pwr-eff-mode', action='append', required=False, type=self._not_negative_int, nargs=1, metavar=("MODE"), help=set_cpu_pwr_eff_mode_help)
                cpu_group.add_argument('--cpu-gmi3-link-width', action='append', required=False, type=self._not_negative_int, nargs=2, metavar=("MIN_LW", "MAX_LW"), help=set_cpu_gmi3_link_width_help)
                cpu_group.add_argument('--cpu-pcie-link-rate', action='append', required=False, type=self._not_negative_int, nargs=1, metavar=("LINK_RATE"), help=set_cpu_pcie_link_rate_help)
                cpu_group.add_argument('--cpu-df-pstate-range', action='append', required=False, type=self._not_negative_int, nargs=2, metavar=("MAX_PSTATE", "MIN_PSTATE"), help=set_cpu_df_pstate_range_help)
                cpu_group.add_argument('--cpu-enable-apb', action='store_true', required=False, help=set_cpu_enable_apb_help)
                cpu_group.add_argument('--cpu-disable-apb', action='append', required=False, type=self._not_negative_int, nargs=1, metavar=("DF_PSTATE"), help=set_cpu_disable_apb_help)
                cpu_group.add_argument('--soc-boost-limit', action='append', required=False, type=self._positive_int, nargs=1, metavar=("BOOST_LIMIT"), help=set_soc_boost_limit_help)

                # Optional CPU Core Args
                core_group = set_value_parser.add_argument_group("CPU Core Arguments")
                core_group.add_argument('--core-boost-limit', action='append', required=False, type=self._positive_int, nargs=1, metavar=("BOOST_LIMIT"), help=set_core_boost_limit_help)

        # Add command modifiers to the bottom
        self._add_command_modifiers(set_value_parser)


    def _add_reset_parser(self, subparsers, func):
        if not self.helpers.is_linux():
            # This subparser is only applicable to Linux
            return

        if not self.helpers.is_amdgpu_initialized():
            # The reset subcommand is only applicable to systems with amdgpu initialized
            return

        # Subparser help text
        reset_help = "Reset options for devices"
        reset_subcommand_help = "A GPU must be specified to reset a configuration.\
                                \nA reset argument must be provided; Multiple reset arguments are accepted"
        reset_optionals_title = "Reset Arguments"

        # Help text for Arguments only on Guest and BM platforms
        gpureset_help = "Reset the specified GPU"
        reset_clocks_help = "Reset clocks and overdrive to default"
        reset_fans_help = "Reset fans to automatic (driver) control"
        reset_profile_help = "Reset power profile back to default"
        reset_xgmierr_help = "Reset XGMI error counts"
        reset_perf_det_help = "Disable performance determinism"
        reset_compute_help = "Reset compute partitions on the specified GPU"
        reset_memory_help = "Reset memory partitions on the specified GPU"
        reset_power_cap_help = "Reset power capacity limit to max capable"
        reset_gpu_clean_local_data_help = "Clean up local data in LDS/GPRs"

        # Create reset subparser
        reset_parser = subparsers.add_parser('reset', help=reset_help, description=reset_subcommand_help)
        reset_parser._optionals.title = reset_optionals_title
        reset_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        reset_parser.set_defaults(func=func)

        # Add Universal Arguments
        self._add_command_modifiers(reset_parser)
        # Device args are required as safeguard from the user applying the operation to all gpus unintentionally
        self._add_device_arguments(reset_parser, required=True)

        if self.helpers.is_baremetal():
            # Add Baremetal reset arguments
            reset_parser.add_argument('-G', '--gpureset', action='store_true', required=False, help=gpureset_help)
            reset_parser.add_argument('-c', '--clocks', action='store_true', required=False, help=reset_clocks_help)
            reset_parser.add_argument('-f', '--fans', action='store_true', required=False, help=reset_fans_help)
            reset_parser.add_argument('-p', '--profile', action='store_true', required=False, help=reset_profile_help)
            reset_parser.add_argument('-x', '--xgmierr', action='store_true', required=False, help=reset_xgmierr_help)
            reset_parser.add_argument('-d', '--perf-determinism', action='store_true', required=False, help=reset_perf_det_help)
            reset_parser.add_argument('-C', '--compute-partition', action='store_true', required=False, help=reset_compute_help)
            reset_parser.add_argument('-M', '--memory-partition', action='store_true', required=False, help=reset_memory_help)
            reset_parser.add_argument('-o', '--power-cap', action='store_true', required=False, help=reset_power_cap_help)

        # Add Baremetal and Virtual OS reset arguments
        reset_parser.add_argument('-l', '--clean-local-data', action='store_true', required=False, help=reset_gpu_clean_local_data_help)


    def _add_monitor_parser(self, subparsers, func):
        if not self.helpers.is_linux():
            # This subparser is only applicable to Linux
            return

        if not self.helpers.is_amdgpu_initialized():
            # The monitor subcommand is only applicable to systems with amdgpu initialized
            return

        # Subparser help text
        monitor_help = "Monitor metrics for target devices"
        monitor_subcommand_help = "Monitor a target device for the specified arguments.\
                                  \nIf no arguments are provided, all arguments will be enabled.\
                                  \nUse the watch arguments to run continuously"
        monitor_optionals_title = "Monitor Arguments"

        # Help text for Arguments only on Guest and BM platforms
        power_usage_help = "Monitor power usage in Watts"
        temperature_help = "Monitor temperature in Celsius"
        gfx_util_help = "Monitor graphics utilization (%%) and clock (MHz)"
        mem_util_help = "Monitor memory utilization (%%) and clock (MHz)"
        encoder_util_help = "Monitor encoder utilization (%%) and clock (MHz)"
        decoder_util_help = "Monitor decoder utilization (%%) and clock (MHz)"
        ecc_help = "Monitor ECC single bit, ECC double bit, and PCIe replay error counts"
        mem_usage_help = "Monitor memory usage in MB"
        pcie_bandwidth_help = "Monitor PCIe bandwidth in Mb/s"
        process_help = "Enable Process information table below monitor output"

        # Create monitor subparser
        monitor_parser = subparsers.add_parser('monitor', help=monitor_help, description=monitor_subcommand_help, aliases=["dmon"])
        monitor_parser._optionals.title = monitor_optionals_title
        monitor_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        monitor_parser.set_defaults(func=func)

        # Add Universal Arguments
        self._add_command_modifiers(monitor_parser)
        self._add_device_arguments(monitor_parser, required=False)
        self._add_watch_arguments(monitor_parser)

        # Add monitor arguments
        monitor_parser.add_argument('-p', '--power-usage', action='store_true', required=False, help=power_usage_help)
        monitor_parser.add_argument('-t', '--temperature', action='store_true', required=False, help=temperature_help)
        monitor_parser.add_argument('-u', '--gfx', action='store_true', required=False, help=gfx_util_help)
        monitor_parser.add_argument('-m', '--mem', action='store_true', required=False, help=mem_util_help)
        monitor_parser.add_argument('-n', '--encoder', action='store_true', required=False, help=encoder_util_help)
        monitor_parser.add_argument('-d', '--decoder', action='store_true', required=False, help=decoder_util_help)
        monitor_parser.add_argument('-e', '--ecc', action='store_true', required=False, help=ecc_help)
        monitor_parser.add_argument('-v', '--vram-usage', action='store_true', required=False, help=mem_usage_help)
        monitor_parser.add_argument('-r', '--pcie', action='store_true', required=False, help=pcie_bandwidth_help)
        monitor_parser.add_argument('-q', '--process', action='store_true', required=False, help=process_help)


    def _add_rocm_smi_parser(self, subparsers, func):
        return
        # Subparser help text
        rocm_smi_help = "Legacy rocm_smi commands ported for backward compatibility"
        rocm_smi_subcommand_help = "If no GPU is specified, returns showall and print the information for all\
                                  GPUs on the system."
        rocm_smi_optionals_title = "rocm_smi Arguments"

        # Optional arguments help text
        load_help = "Load clock, fan, performance, and profile settings from a given file."
        save_help = "Save clock, fan, performance, and profile settings to a given file."
        showtempgraph_help = "Show Temperature Graph"
        showmclkrange_help = "Show mclk range"
        showsclkrange_help = "Show sclk range"
        showmaxpower_help = "Show maximum graphics package power this GPU will consume"
        showmemvendor_help = "Show GPU memory vendor"
        showproductname_help = "Show SKU/Vendor name"
        showclkvolt_help = "Show supported GPU and Memory Clocks and Voltages"
        showclkfrq_help = "Show supported GPU and Memory Clock"

        # Create rocm_smi subparser
        rocm_smi_parser = subparsers.add_parser('rocm-smi', help=rocm_smi_help, description=rocm_smi_subcommand_help)
        rocm_smi_parser._optionals.title = rocm_smi_optionals_title
        rocm_smi_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        rocm_smi_parser.set_defaults(func=func)
        self._add_command_modifiers(rocm_smi_parser)

        # Add Device args
        self._add_device_arguments(rocm_smi_parser, required=False)

        # Optional Args
        rocm_smi_parser.add_argument('-l', '--load', action=self._check_input_file_path(), type=str, required=False, help=load_help)
        rocm_smi_parser.add_argument('-s', '--save', action=self._check_output_file_path(), type=str, required=False, help=save_help)

        rocm_smi_parser.add_argument('-b', '--showbw', action='store_true', required=False, help=showbw_help)
        rocm_smi_parser.add_argument('-t', '--showtempgraph', action='store_true', required=False, help=showtempgraph_help)
        rocm_smi_parser.add_argument('-m', '--showmclkrange', action='store_true', required=False, help=showmclkrange_help)
        rocm_smi_parser.add_argument('-c', '--showsclkrange', action='store_true', required=False, help=showsclkrange_help)
        rocm_smi_parser.add_argument('-P', '--showmaxpower', action='store_true', required=False, help=showmaxpower_help)
        rocm_smi_parser.add_argument('-M', '--showmemvendor', action='store_true', required=False, help=showmemvendor_help)
        rocm_smi_parser.add_argument('-p', '--showproductname', action='store_true', required=False, help=showproductname_help)
        rocm_smi_parser.add_argument('-v', '--showclkvolt', action='store_true', required=False, help=showclkvolt_help)
        rocm_smi_parser.add_argument('-f', '--showclkfrq', action='store_true', required=False, help=showclkfrq_help)


    def _add_xgmi_parser(self, subparsers, func):
        if not self.helpers.is_amdgpu_initialized():
            # The xgmi subcommand is only applicable to systems with amdgpu initialized
            return

        # Subparser help text
        xgmi_help = "Displays xgmi information of the devices"
        xgmi_subcommand_help = "If no GPU is specified, returns information for all GPUs on the system.\
                                \nIf no xgmi argument is provided all xgmi information will be displayed."
        xgmi_optionals_title = "XGMI arguments"

        # Help text for Arguments only on Guest and BM platforms
        metrics_help = "Metric XGMI information"

        # Create xgmi subparser
        xgmi_parser = subparsers.add_parser('xgmi', help=xgmi_help, description=xgmi_subcommand_help)
        xgmi_parser._optionals.title = xgmi_optionals_title
        xgmi_parser.formatter_class=lambda prog: AMDSMISubparserHelpFormatter(prog)
        xgmi_parser.set_defaults(func=func)

        # Add Universal Arguments
        self._add_command_modifiers(xgmi_parser)
        self._add_device_arguments(xgmi_parser, required=False)

        # Optional Args
        xgmi_parser.add_argument('-m', '--metric', action='store_true', required=False, help=metrics_help)


    def error(self, message):
        outputformat = self.helpers.get_output_format()

        if "argument : invalid choice: " in message:
            l = len("argument : invalid choice: ") + 1
            message = message[l:]
            message = message.split("'")[0]
            # Check if the command is possible in other system configurations and error accordingly
            if message in self.possible_commands:
                raise amdsmi_cli_exceptions.AmdSmiCommandNotSupportedException(message, outputformat)
            raise amdsmi_cli_exceptions.AmdSmiInvalidCommandException(message, outputformat)
        elif "unrecognized arguments: " in message:
            l = len("unrecognized arguments: ")
            message = message[l:]
            raise amdsmi_cli_exceptions.AmdSmiInvalidParameterException(message, outputformat)
        else:
            print(message)

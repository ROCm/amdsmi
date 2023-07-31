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


import argparse
import errno
import os
import time
from pathlib import Path
import sys

from _version import __version__
from amdsmi_helpers import AMDSMIHelpers
import amdsmi_cli_exceptions


class AMDSMIParser(argparse.ArgumentParser):
    """Unified Parser for AMDSMI CLI.
        This parser doesn't access amdsmi's lib directly,but via AMDSMIHelpers,
        this allows for us to use this parser with future OS & Platform integration.

    Args:
        argparse (ArgumentParser): argparse.ArgumentParser
    """
    def __init__(self, version, discovery, static, firmware, bad_pages, metric,
                 process, profile, event, topology, set_value, reset, rocmsmi):

        # Helper variables
        self.helpers = AMDSMIHelpers()
        self.gpu_choices, self.gpu_choices_str = self.helpers.get_gpu_choices()
        self.vf_choices = ['3', '2', '1']

        version_string = f"Version: {__version__}"
        platform_string = f"Platform: {self.helpers.os_info()}"

        program_name = 'amd-smi'
        if 'gpuv-smi' in sys.argv[0]:
            program_name = 'gpuv-smi'

        # Adjust argument parser options
        super().__init__(
            formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog,
                                                                       max_help_position=80,
                                                                       width=90),
            description=f"AMD System Management Interface | {version_string} | {platform_string}",
            add_help=True,
            prog=program_name)

        # Setup subparsers
        subparsers = self.add_subparsers(
            title="AMD-SMI Commands",
            parser_class=argparse.ArgumentParser,
            help="Descriptions:",
            metavar='')

        # Add all subparsers
        self._add_version_parser(subparsers, version)
        self._add_discovery_parser(subparsers, discovery)
        self._add_static_parser(subparsers, static)
        self._add_firmware_parser(subparsers, firmware)
        self._add_bad_pages_parser(subparsers, bad_pages)
        self._add_metric_parser(subparsers, metric)
        self._add_process_parser(subparsers, process)
        self._add_profile_parser(subparsers, profile)
        self._add_event_parser(subparsers, event)
        self._add_topology_parser(subparsers, topology)
        self._add_set_value_parser(subparsers, set_value)
        self._add_reset_parser(subparsers, reset)
        self._add_rocm_smi_parser(subparsers, rocmsmi)


    def _positive_int(self, int_value):
        # Argument type validator
        if int_value.isdigit():  # Is digit works only on positive numbers
            return int(int_value)
        else:
            outputformat = self.helpers.get_output_format()
            raise amdsmi_cli_exceptions.AmdSmiInvalidParameterValueException(int_value, outputformat)


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
                    file_name = str(path)
                    if args.json and str(path).split('.')[-1].lower() != 'json':
                        file_name += ".json"
                    elif args.csv and str(path).split('.')[-1].lower() != 'csv':
                        file_name += ".csv"
                    elif str(path).split('.')[-1].lower() != 'txt':
                        file_name += ".txt"
                    path = Path(file_name)
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
                status, selected_device_handles = amdsmi_helpers.get_device_handles_from_gpu_selections(gpu_selections=values,
                                                                                                         gpu_choices=gpu_choices)
                if status:
                    setattr(args, self.dest, selected_device_handles)
                else:
                    if selected_device_handles == '':
                        raise amdsmi_cli_exceptions.AmdSmiMissingParameterValueException("--gpu", _GPUSelectAction.ouputformat)
                    else:
                        raise amdsmi_cli_exceptions.AmdSmiDeviceNotFoundException(selected_device_handles, _GPUSelectAction.ouputformat)

        return _GPUSelectAction


    def _add_command_modifiers(self, subcommand_parser, rocm_smi=True, gpuv_smi=True):
        json_help = "Displays output in JSON format (human readable by default)."
        csv_help = "Displays output in CSV format (human readable by default)."
        file_help = "Saves output into a file on the provided path (stdout by default)."
        loglevel_help = "Set the logging level for the parser commands"

        command_modifier_group = subcommand_parser.add_argument_group('Command Modifiers')

        # Output Format options
        logging_args = command_modifier_group.add_mutually_exclusive_group()
        logging_args.add_argument('--json', action='store_true', required=False, help=json_help)
        logging_args.add_argument('--csv', action='store_true', required=False, help=csv_help)

        command_modifier_group.add_argument('--file', action=self._check_output_file_path(), type=str, required=False, help=file_help)
        # Placing loglevel outside the subcommands so it can be used with any subcommand
        command_modifier_group.add_argument('--loglevel', action='store', required=False, help=loglevel_help, default='ERROR',
                                            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])


    def _add_watch_arguments(self, subcommand_parser):
        # Device arguments help text
        watch_help = "Reprint the command in a loop of Interval seconds"
        watch_time_help = "The total time to watch the given command"
        iterations_help = "Total number of iterations to loop on the given command"

        # Mutually Exclusive Args within the subparser
        subcommand_parser.add_argument('-w', '--watch', action='store', metavar='loop_time',
             type=self._positive_int, required=False, help=watch_help)
        subcommand_parser.add_argument('-W', '--watch_time', action=self._check_watch_selected(), metavar='total_loop_time',
            type=self._positive_int, required=False, help=watch_time_help)
        subcommand_parser.add_argument('-i', '--iterations', action=self._check_watch_selected(), metavar='number_of_iterations',
            type=self._positive_int, required=False, help=iterations_help)


    def _add_device_arguments(self, subcommand_parser, required=False):
        # Device arguments help text
        gpu_help = f"Select a GPU ID, BDF, or UUID from the possible choices:\n{self.gpu_choices_str}"
        vf_help = "Gets general information about the specified VF (timeslice, fb info, …).\
                    \nAvailable only on virtualization OSs"

        # Mutually Exclusive Args within the subparser
        device_args = subcommand_parser.add_mutually_exclusive_group(required=required)
        device_args.add_argument('-g', '--gpu', action=self._gpu_select(self.gpu_choices),
                                    nargs='+', help=gpu_help)

        if self.helpers.is_hypervisor():
            device_args.add_argument('-v', '--vf', action='store', nargs='+',
                                        help=vf_help, choices=self.vf_choices)


    def _add_version_parser(self, subparsers, func):
        # Subparser help text
        version_help = "Display version information"

        # Create version subparser
        version_parser = subparsers.add_parser('version', help=version_help, description=None)
        version_parser._optionals.title = None
        version_parser.formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=80, width=90)
        version_parser.set_defaults(func=func)
        self._add_command_modifiers(version_parser)


    def _add_discovery_parser(self, subparsers, func):
        # Subparser help text
        discovery_help = "Display discovery information"
        discovery_subcommand_help = "Lists all the devices on the system and the links between devices.\
                            \nLists all the sockets and for each socket, GPUs and/or CPUs associated to\
                            \nthat socket alongside some basic information for each device.\
                            \nIn virtualization environments, it can also list VFs associated to each\
                            \nGPU with some basic information for each VF."

        # Create discovery subparser
        discovery_parser = subparsers.add_parser('discovery', help=discovery_help, description=discovery_subcommand_help, aliases=['list'])
        discovery_parser.formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=80, width=90)
        discovery_parser.set_defaults(func=func)

        # Add Command Modifiers
        self._add_command_modifiers(discovery_parser)

        # Add Device args
        self._add_device_arguments(discovery_parser, required=False)


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

        # Options arguments help text for Hypervisors and Baremetal
        ras_help = "Displays RAS features information"
        board_help = "All board information" # Linux Baremetal only
        numa_help = "All numa node information" # Linux Baremetal only

        # Options arguments help text for Hypervisors
        dfc_help = "All DFC FW table information"
        fb_help = "Displays Frame Buffer information"
        num_vf_help = "Displays number of supported and enabled VFs"

        # Create static subparser
        static_parser = subparsers.add_parser('static', help=static_help, description=static_subcommand_help)
        static_parser._optionals.title = static_optionals_title
        static_parser.formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=80, width=90)
        static_parser.set_defaults(func=func)
        self._add_command_modifiers(static_parser)

        # Add Device args
        self._add_device_arguments(static_parser, required=False)

        # Optional Args
        static_parser.add_argument('-a', '--asic', action='store_true', required=False, help=asic_help)
        static_parser.add_argument('-b', '--bus', action='store_true', required=False, help=bus_help)
        static_parser.add_argument('-V', '--vbios', action='store_true', required=False, help=vbios_help)
        static_parser.add_argument('-d', '--driver', action='store_true', required=False, help=driver_help)

        # Options to display on Hypervisors and Baremetal
        if self.helpers.is_hypervisor() or self.helpers.is_baremetal():
            static_parser.add_argument('-r', '--ras', action='store_true', required=False, help=ras_help)
            if self.helpers.is_linux():
                static_parser.add_argument('-B', '--board', action='store_true', required=False, help=board_help)
                static_parser.add_argument('-l', '--limit', action='store_true', required=False, help=limit_help)
                static_parser.add_argument('-u', '--numa', action='store_true', required=False, help=numa_help)

        # Options to only display on a Hypervisor
        if self.helpers.is_hypervisor():
            static_parser.add_argument('-d', '--dfc-ucode', action='store_true', required=False, help=dfc_help)
            static_parser.add_argument('-f', '--fb-info', action='store_true', required=False, help=fb_help)
            static_parser.add_argument('-n', '--num-vf', action='store_true', required=False, help=num_vf_help)


    def _add_firmware_parser(self, subparsers, func):
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
        firmware_parser.formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=80, width=90)
        firmware_parser.set_defaults(func=func)
        self._add_command_modifiers(firmware_parser)

        # Add Device args
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
        bad_pages_parser.formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=80, width=90)
        bad_pages_parser.set_defaults(func=func)
        self._add_command_modifiers(bad_pages_parser)

        # Add Device args
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

        # Help text for Arguments only Available on Virtual OS and Baremetal platforms
        fb_usage_help = "Total and used framebuffer"

        # Help text for Arguments only on Hypervisor and Baremetal platforms
        power_help = "Current power usage"
        clock_help = "Average, max, and current clock frequencies"
        temperature_help = "Current temperatures"
        ecc_help = "Number of ECC errors"
        ecc_block_help = "Number of ECC errors per block"
        pcie_help = "Current PCIe speed and width"

        # Help text for Arguments only on Linux Baremetal platforms
        fan_help = "Current fan speed"
        vc_help = "Display voltage curve"
        overdrive_help = "Current GPU clock overdrive level"
        perf_level_help = "Current DPM performance level"
        replay_count_help = "PCIe replay count"
        xgmi_err_help = "XGMI error information since last read"
        energy_help = "Amount of energy consumed"
        mem_usage_help = "Memory usage per block"

        # Help text for Arguments only on Hypervisors
        schedule_help = "All scheduling information"
        guard_help = "All guard information"
        guest_help = "All guest data information"

        # Create metric subparser
        metric_parser = subparsers.add_parser('metric', help=metric_help, description=metric_subcommand_help)
        metric_parser._optionals.title = metric_optionals_title
        metric_parser.formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=80, width=90)
        metric_parser.set_defaults(func=func)
        self._add_command_modifiers(metric_parser)

        # Add Device args
        self._add_device_arguments(metric_parser, required=False)

        # Add Watch args
        self._add_watch_arguments(metric_parser)

        # Optional Args for Virtual OS and Baremetal systems
        if self.helpers.is_virtual_os() or self.helpers.is_baremetal():
            metric_parser.add_argument('-b', '--fb-usage', action='store_true', required=False, help=fb_usage_help)
            metric_parser.add_argument('-m', '--mem-usage', action='store_true', required=False, help=mem_usage_help)

        # Optional Args for Hypervisors and Baremetal systems
        if self.helpers.is_hypervisor() or self.helpers.is_baremetal():
            metric_parser.add_argument('-p', '--power', action='store_true', required=False, help=power_help)
            metric_parser.add_argument('-c', '--clock', action='store_true', required=False, help=clock_help)
            metric_parser.add_argument('-t', '--temperature', action='store_true', required=False, help=temperature_help)
            metric_parser.add_argument('-e', '--ecc', action='store_true', required=False, help=ecc_help)
            metric_parser.add_argument('-k', '--ecc-block', action='store_true', required=False, help=ecc_block_help)
            metric_parser.add_argument('-r', '--replay-count', action='store_true', required=False, help=replay_count_help)
            metric_parser.add_argument('-P', '--pcie', action='store_true', required=False, help=pcie_help)
            metric_parser.add_argument('-u', '--usage', action='store_true', required=False, help=usage_help)

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
            metric_parser.add_argument('-u', '--guest', action='store_true', required=False, help=guest_help)


    def _add_process_parser(self, subparsers, func):
        if self.helpers.is_hypervisor():
            # Don't add this subparser on Hypervisors
            # This subparser is only available to Guest and Baremetal systems
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
        process_parser.formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=80, width=90)
        process_parser.set_defaults(func=func)
        self._add_command_modifiers(process_parser)

        # Add Device args
        self._add_device_arguments(process_parser, required=False)

        # Add Watch args
        self._add_watch_arguments(process_parser)

        # Optional Args
        process_parser.add_argument('-G', '--general', action='store_true', required=False, help=general_help)
        process_parser.add_argument('-e', '--engine', action='store_true', required=False, help=engine_help)
        process_parser.add_argument('-p', '--pid', action='store', type=self._positive_int, required=False, help=pid_help)
        process_parser.add_argument('-n', '--name', action='store', required=False, help=name_help)


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
        profile_parser.formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=80, width=90)
        profile_parser.set_defaults(func=func)
        self._add_command_modifiers(profile_parser)

        # Add Device args
        self._add_device_arguments(profile_parser, required=False)


    def _add_event_parser(self, subparsers, func):
        if self.helpers.is_linux() and not self.helpers.is_virtual_os():
            # This subparser only applies to Linux Hypervisors, NOT Linux Guest
            return

        # Subparser help text
        event_help = "Displays event information for the given GPU"
        event_subcommand_help = "If no GPU is specified, returns event information for all GPUs on the system."
        event_optionals_title = "Event Arguments"

        # Create event subparser
        event_parser = subparsers.add_parser('event', help=event_help, description=event_subcommand_help)
        event_parser._optionals.title = event_optionals_title
        event_parser.formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=80, width=90)
        event_parser.set_defaults(func=func)
        self._add_command_modifiers(event_parser)

        # Add Device args
        self._add_device_arguments(event_parser, required=False)


    def _add_topology_parser(self, subparsers, func):
        if not(self.helpers.is_baremetal() and self.helpers.is_linux()):
            # This subparser is only applicable to Baremetal Linux
            return

        # Subparser help text
        topology_help = "Displays topology information of the devices."
        topology_subcommand_help = "If no GPU is specified, returns information for all GPUs on the system.\
                                \nIf no topology argument is provided all topology information will be displayed."
        topology_optionals_title = "Topology arguments"

        # Help text for Arguments only on Guest and BM platforms
        access_help = "Displays link accessibility between GPUs"
        weight_help = "Displays relative weight between GPUs"
        hops_help = "Displays the number of hops between GPUs"
        link_type_help = "Displays the link type between GPUs"
        numa_bw_help = "Display max and min bandwidth between nodes"

        # Create topology subparser
        topology_parser = subparsers.add_parser('topology', help=topology_help, description=topology_subcommand_help)
        topology_parser._optionals.title = topology_optionals_title
        topology_parser.formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=80, width=90)
        topology_parser.set_defaults(func=func)
        self._add_command_modifiers(topology_parser)

        # Add Device args
        self._add_device_arguments(topology_parser, required=False)

        # Optional Args
        topology_parser.add_argument('-a', '--access', action='store_true', required=False, help=access_help)
        topology_parser.add_argument('-w', '--weight', action='store_true', required=False, help=weight_help)
        topology_parser.add_argument('-o', '--hops', action='store_true', required=False, help=hops_help)
        topology_parser.add_argument('-t', '--link-type', action='store_true', required=False, help=link_type_help)
        topology_parser.add_argument('-b', '--numa-bw', action='store_true', required=False, help=numa_bw_help)


    def _add_set_value_parser(self, subparsers, func):
        if not(self.helpers.is_baremetal() and self.helpers.is_linux()):
            # This subparser is only applicable to Baremetal Linux
            return

        # Subparser help text
        set_value_help = "Set options for devices."
        set_value_subcommand_help = "A GPU must be specified to set a configuration.\
                                    \nA set argument must be provided; Multiple set arguments are accepted"
        set_value_optionals_title = "Set Arguments"

        # Help text for Arguments only on Guest and BM platforms
        set_fan_help = "Sets GPU fan speed (0-255 or 0-100%%)"
        set_perf_level_help = "Sets performance level"
        set_profile_help = "Set power profile level (#) or a quoted string of custom profile attributes"
        set_perf_det_help = "Sets GPU clock frequency limit and performance level to determinism to get minimal performance variation"

        # Create set_value subparser
        set_value_parser = subparsers.add_parser('set', help=set_value_help, description=set_value_subcommand_help)
        set_value_parser._optionals.title = set_value_optionals_title
        set_value_parser.formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=80, width=90)
        set_value_parser.set_defaults(func=func)
        self._add_command_modifiers(set_value_parser)

        # Device args are required as safeguard from the user applying the operation to all gpus unintentionally
        self._add_device_arguments(set_value_parser, required=True)

        # Optional Args
        set_value_parser.add_argument('-f', '--fan', action=self._validate_fan_speed(), required=False, help=set_fan_help, metavar='%')
        set_value_parser.add_argument('-l', '--perflevel', action='store', choices=self.helpers.get_perf_levels()[0], type=str.upper, required=False, help=set_perf_level_help, metavar='LEVEL')
        set_value_parser.add_argument('-P', '--profile', action='store', required=False, help=set_profile_help, metavar='SETPROFILE')
        set_value_parser.add_argument('-d', '--perfdeterminism', action='store', type=self._positive_int, required=False, help=set_perf_det_help, metavar='SCLKMAX')


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


    def _add_reset_parser(self, subparsers, func):
        if not(self.helpers.is_baremetal() and self.helpers.is_linux()):
            # This subparser is only applicable to Baremetal Linux
            return

        # Subparser help text
        reset_help = "Reset options for devices."
        reset_subcommand_help = "A GPU must be specified to reset a configuration.\
                                \nA reset argument must be provided; Multiple reset arguments are accepted"
        reset_optionals_title = "Reset Arguments"

        # Help text for Arguments only on Guest and BM platforms
        gpureset_help = "Reset the specified GPU"
        resetclocks_help = "Reset clocks and overdrive to default"
        resetfans_help = "Reset fans to automatic (driver) control"
        resetprofile_help = "Reset power profile back to default"
        resetxgmierr_help = "Reset XGMI error counts"
        resetperfdet_help = "Disable performance determinism"

        # Create reset subparser
        reset_parser = subparsers.add_parser('reset', help=reset_help, description=reset_subcommand_help)
        reset_parser._optionals.title = reset_optionals_title
        reset_parser.formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=80, width=90)
        reset_parser.set_defaults(func=func)
        self._add_command_modifiers(reset_parser)

        # Device args are required as safeguard from the user applying the operation to all gpus unintentionally
        self._add_device_arguments(reset_parser, required=True)

        # Optional Args
        reset_parser.add_argument('-G', '--gpureset', action='store_true', required=False, help=gpureset_help)
        reset_parser.add_argument('-c', '--clocks', action='store_true', required=False, help=resetclocks_help)
        reset_parser.add_argument('-f', '--fans', action='store_true', required=False, help=resetfans_help)
        reset_parser.add_argument('-p', '--profile', action='store_true', required=False, help=resetprofile_help)
        reset_parser.add_argument('-x', '--xgmierr', action='store_true', required=False, help=resetxgmierr_help)
        reset_parser.add_argument('-d', '--perfdeterminism', action='store_true', required=False, help=resetperfdet_help)


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
        rocm_smi_parser.formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=80, width=90)
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


    def error(self, message):
        outputformat = self.helpers.get_output_format()

        if "argument : invalid choice: " in message:
            l = len("argument : invalid choice: ") + 1
            message = message[l:]
            message = message.split("'")[0]
            raise amdsmi_cli_exceptions.AmdSmiInvalidCommandException(message, outputformat)
        elif "unrecognized arguments: " in message:
            l = len("unrecognized arguments: ")
            message = message[l:]
            raise amdsmi_cli_exceptions.AmdSmiInvalidParameterException(message, outputformat)
        else:
            print(message)

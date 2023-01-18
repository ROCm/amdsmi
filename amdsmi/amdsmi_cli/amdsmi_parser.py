#!/usr/bin/python3

import argparse
import platform

from _version import __version__
from amdsmi_helpers import AMD_SMI_Helpers

# sudo /src/out/ubuntu-20.04/20.04/bin/rocm-smi -bc --json | python -m json.tool

class AMD_SMI_Parser(argparse.ArgumentParser):

    def __init__(self, version, discovery, static, firmware, bad_pages, metric,
                    process, profile, event,topology, set_value, reset, misc, gpu_v):

        # Helper variables
        self.amd_smi_helpers = AMD_SMI_Helpers()
        self.gpu_choices = self.amd_smi_helpers.get_gpu_choices()
        self.vf_choices = ['3','2','1']

        # Adjust argument parser options
        super().__init__(
            formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90),
            # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description=f'AMD System Management Interface | Version: {__version__}', #@TODO add the enviornment
            add_help=True,
            prog='amd-smi')

        # Setup subparsers
        subparsers = self.add_subparsers(
            title="AMD-SMI Commands",
            parser_class=argparse.ArgumentParser,
            required=True,
            help='Descriptions:',
            # dest='cmd',
            metavar="")

        # Add all subparsers
        # Add --json, --csv,--file,--loglevel, watch, watch_time, & iterations && backwards compatability --gpuvsmi --rocmsmi
        self.add_version_parser(subparsers, version)
        self.add_discovery_parser(subparsers, discovery)
        self.add_static_parser(subparsers, static)
        self.add_firmware_parser(subparsers, firmware)
        self.add_bad_pages_parser(subparsers, bad_pages)
        self.add_metric_parser(subparsers, metric)
        self.add_process_parser(subparsers, process)
        self.add_profile_parser(subparsers, profile)
        self.add_event_parser(subparsers, event)
        self.add_topology_parser(subparsers, topology)
        # self.add_set_value_parser(subparsers, set_value)
        self.add_reset_parser(subparsers, reset)
        self.add_misc_parser(subparsers, misc)
        # self.add_gpu_v_parser(subparsers, misc)


    def add_version_parser(self, subparsers, func):
        # Subparser help text
        version_help = "Display version information"

        # Create version subparser
        version_parser = subparsers.add_parser('version', help=version_help, description=None)
        version_parser._optionals.title = None
        version_parser.formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90)
        version_parser.set_defaults(func=func)


    def add_discovery_parser(self, subparsers, func):
        # Subparser help text
        discovery_help = "Display discovery information"
        discovery_subcommand_help = """Lists all the devices on the system and the links between devices.
                            Lists all the sockets and for each socket, GPUs and/or CPUs associated to
                            that socket alongside some basic information for each device.
                            In virtualization environment, it can also list VFs associated to each
                            GPU with some basic information for each VF."""

        # Create discovery subparser
        discovery_parser = subparsers.add_parser('discovery', help=discovery_help, description=discovery_subcommand_help)
        discovery_parser.formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90)
        discovery_parser.set_defaults(func=func)


    def add_static_parser(self, subparsers, func):
        # Subparser help text
        static_help = "Gets static information about the specified GPU"
        static_subcommand_help = """If no argument is provided, return static information for all GPUs on the system.
                                        If no static argument is specified all static information will be displayed."""
        static_optionals_title = "Static Arguments"

        # Optional arguments help text
        gpu_help = "Select a GPU from the possible choices"
        vf_help = """Gets general information about the specified VF (timeslice, fb info, …).
                    Available only on virtualization OSs"""
        asic_help = "All asic information"
        bus_help = "All bus information"
        vbios_help = "All video bios information (if available)"
        limit_help = "All limit metric values (i.e. power and thermal limits)"
        driver_help = "Displays driver version"
        caps_help = "All caps information"

        # Options arguments help text for Hypervisors and Baremetal
        ras_help = "Displays RAS features information"
        board_help = "All board information" # Linux Baremetal only @TODO is applicable to Azure

        # Options arguments help text for Hypervisors
        dfc_help = "All DFC FW table information"
        fb_help = "Displays Frame Buffer information"
        num_vf_help = "Displays number of supported and enabled VFs"

        # Create static subparser
        static_parser = subparsers.add_parser('static', help=static_help, description=static_subcommand_help)
        static_parser._optionals.title = static_optionals_title
        static_parser.formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90)
        static_parser.set_defaults(func=func)

        # Mutually Exclusive Args within the subparser
        device_args = static_parser.add_mutually_exclusive_group()
        device_args.add_argument('--gpu', action='store', help=gpu_help, choices=self.gpu_choices)

        # Optional Args
        static_parser.add_argument('-a', '--asic', action='store_true', required=False, help=asic_help)
        static_parser.add_argument('-b', '--bus', action='store_true', required=False, help=bus_help)
        static_parser.add_argument('-v', '--vbios', action='store_true', required=False, help=vbios_help)
        static_parser.add_argument('-l', '--limit', action='store_true', required=False, help=limit_help)
        static_parser.add_argument('-d', '--driver', action='store_true', required=False, help=driver_help)
        static_parser.add_argument('-c', '--caps', action='store_true', required=False, help=caps_help)

        # Options to display on Hypervisors and Baremetal
        if self.amd_smi_helpers.is_hypervisor() or self.amd_smi_helpers.is_baremetal():
            static_parser.add_argument('-r', '--ras', action='store_true', required=False, help=ras_help)
            if self.amd_smi_helpers.is_linux(): #@TODO Check if applicable to Azure
                static_parser.add_argument('-B', '--board', action='store_true', required=False, help=board_help)

        # Options to only display on a Hypervisor
        if self.amd_smi_helpers.is_hypervisor():
            device_args.add_argument('--vf', action='store', help=vf_help, choices=self.vf_choices)
            static_parser.add_argument('-du', '--dfc-ucode', action='store_true', required=False, help=dfc_help)
            static_parser.add_argument('-f', '--fb-info', action='store_true', required=False, help=fb_help)
            static_parser.add_argument('-n', '--num-vf', action='store_true', required=False, help=num_vf_help)


    def add_firmware_parser(self, subparsers, func):
        # Subparser help text
        firmware_help = "Gets firmware information about the specified GPU"
        firmware_subcommand_help = "If no argument is provided, return firmware information for all GPUs on the system."
        firmware_optionals_title = "Firmware Arguments"

        # Optional arguments help text
        gpu_help = "Select a GPU from the possible choices"
        vf_help = """Gets general information about the specified VF (timeslice, fb info, …).
                    Available only on virtualization OSs"""
        fw_list_help = "All FW list information"
        err_records_help = "All error records information"

        # Create firmware subparser
        firmware_parser = subparsers.add_parser('firmware', help=firmware_help, description=firmware_subcommand_help)
        firmware_parser._optionals.title = firmware_optionals_title
        firmware_parser.formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90)
        firmware_parser.set_defaults(func=func)

        # Mutually Exclusive Args within the subparser
        device_args = firmware_parser.add_mutually_exclusive_group()
        device_args.add_argument('--gpu', action='store', help=gpu_help, choices=self.gpu_choices)

        # Optional Args
        firmware_parser.add_argument('-f', '--fw-list', action='store_true', required=False, help=fw_list_help) # Redundant?

        # Options to only display on a Hypervisor
        if self.amd_smi_helpers.is_hypervisor():
            device_args.add_argument('--vf', action='store', help=vf_help, choices=self.vf_choices)
            firmware_parser.add_argument('-e', '--error-records', action='store_true', required=False, help=err_records_help)


    def add_bad_pages_parser(self, subparsers, func): #@TODO Retired pages?
        if not (self.amd_smi_helpers.is_baremetal() and self.amd_smi_helpers.is_linux()):
            # The bad_pages subcommand is only applicable to Linux Baremetal systems
            return

        # Subparser help text
        bad_pages_help = "Gets bad page information about the specified GPU"
        bad_pages_subcommand_help = "If no argument is provided, return bad page information for all GPUs on the system."
        bad_pages_optionals_title = "Bad pages Arguments"

        # Optional arguments help text
        gpu_help = "Select a GPU from the possible choices"
        pending_help = "Displays all pending retired pages"
        retired_help = "Displays retired pages" #@TODO Wording
        un_res_help = "Displays unreservable pages"

        # Create bad_pages subparser
        bad_pages_parser = subparsers.add_parser('bad_pages', help=bad_pages_help, description=bad_pages_subcommand_help)
        bad_pages_parser._optionals.title = bad_pages_optionals_title
        bad_pages_parser.formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90)
        bad_pages_parser.set_defaults(func=func)

        # Mutually Exclusive Args within the subparser
        device_args = bad_pages_parser.add_mutually_exclusive_group()
        device_args.add_argument('--gpu', action='store', help=gpu_help, choices=self.gpu_choices)

        # Optional Args
        bad_pages_parser.add_argument('-p', '--pending', action='store_true', required=False, help=pending_help)
        bad_pages_parser.add_argument('-r', '--retired', action='store_true', required=False, help=retired_help)
        bad_pages_parser.add_argument('-u', '--un-res', action='store_true', required=False, help=un_res_help)


    def add_metric_parser(self, subparsers, func):
        # Subparser help text
        metric_help = "Gets metric/performance information about the specified GPU"
        metric_subcommand_help = """If no argument is provided, return metric information for all GPUs on the system.
                        If no metric argument is specified all metric information will be displayed."""
        metric_optionals_title = "Metric arguments"

        # Optional arguments help text
        gpu_help = "Select a GPU from the possible choices"
        vf_help = """Gets general information about the specified VF (timeslice, fb info, …).
                    Available only on virtualization OSs"""
        usage_help = "All metrics usage information"

        # Help text for Arguments only Available on Virtual OS and Baremetal platforms
        fb_usage_help = "Total and used framebuffer"

        # Help text for Arguments only on Hypervisor and Baremetal platforms
        power_help = "Current power usage"
        clock_help = "Average, max, and current clock frequencies"
        temperature_help = "Current temperatures"
        ecc_help = "Number of ECC errors"
        pcie_help = "Current PCIe speed and width"
        voltage_help = "Current GPU voltages"

        # Help text for Arguments only on Linux Baremetal platforms
        fan_help = "Current fan speed"
        pcie_usage_help = "Estimated PCIe link usage"
        vc_help = "Display voltage curve"
        overdrive_help = "Current GPU clock overdrive level"
        mo_help = "Current memory clock overdrive level"
        perf_level_help = "Current DPM performance level"
        replay_count_help = "PCIe replay count"
        xgmi_err_help = "XGMI error information since last read"
        energy_help = "Amount of energy consumed" #@TODO ? Available only on host Linux Baremetal platforms

        # Help text for Arguments only on Hypervisors
        schedule_help = "All scheduling information"
        guard_help = "All guard information"
        guest_help = "All guest data information"

        # Create metric subparser
        metric_parser = subparsers.add_parser('metric', help=metric_help, description=metric_subcommand_help)
        metric_parser._optionals.title = metric_optionals_title
        metric_parser.formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90)
        metric_parser.set_defaults(func=func)

        # Mutually Exclusive Args within the subparser
        device_args = metric_parser.add_mutually_exclusive_group()
        device_args.add_argument('--gpu', action='store', help=gpu_help, choices=self.gpu_choices)

        # Optional Args
        metric_parser.add_argument('-u', '--usage', action='store_true', required=False, help=usage_help)

        # Optional Args for Virtual OS and Baremetal systems
        if self.amd_smi_helpers.is_virtual_os() or self.amd_smi_helpers.is_baremetal():
            metric_parser.add_argument('-b', '--fb-usage', action='store_true', required=False, help=fb_usage_help)

        # Optional Args for Hypervisors and Baremetal systems
        if self.amd_smi_helpers.is_hypervisor() or self.amd_smi_helpers.is_baremetal():
            metric_parser.add_argument('-p', '--power', action='store_true', required=False, help=power_help)
            metric_parser.add_argument('-c', '--clock', action='store_true', required=False, help=clock_help)
            metric_parser.add_argument('-t', '--temperature', action='store_true', required=False, help=temperature_help)
            metric_parser.add_argument('-e', '--ecc', action='store_true', required=False, help=ecc_help)
            metric_parser.add_argument('-P', '--pcie', action='store_true', required=False, help=pcie_help)
            metric_parser.add_argument('-v', '--voltage', action='store_true', required=False, help=voltage_help)

        # Optional Args for Linux Baremetal Systems #@TODO Discuss logic if Linux Hypervisors would be allowed to have this
        if self.amd_smi_helpers.is_baremetal() and self.amd_smi_helpers.is_linux():
            metric_parser.add_argument('-f', '--fan', action='store_true', required=False, help=fan_help)
            metric_parser.add_argument('-s', '--pcie-usage', action='store_true', required=False, help=pcie_usage_help)
            metric_parser.add_argument('-V', '--voltage-curve', action='store_true', required=False, help=vc_help)
            metric_parser.add_argument('-o', '--overdrive', action='store_true', required=False, help=overdrive_help)
            metric_parser.add_argument('-m', '--mem-overdrive', action='store_true', required=False, help=mo_help)
            metric_parser.add_argument('-l', '--perf-level', action='store_true', required=False, help=perf_level_help)
            metric_parser.add_argument('-r', '--replay-count', action='store_true', required=False, help=replay_count_help)
            metric_parser.add_argument('-x', '--xgmi-err', action='store_true', required=False, help=xgmi_err_help)
            metric_parser.add_argument('-E', '--energy', action='store_true', required=False, help=energy_help)

        # Options to only display to Hypervisors
        if self.amd_smi_helpers.is_hypervisor():
            device_args.add_argument('--vf', action='store', help=vf_help, choices=self.vf_choices)
            metric_parser.add_argument('-s', '--schedule', action='store_true', required=False, help=schedule_help)
            metric_parser.add_argument('-g', '--guard', action='store_true', required=False, help=guard_help)
            metric_parser.add_argument('-G', '--guest', action='store_true', required=False, help=guest_help)


    def add_process_parser(self, subparsers, func):
        if self.amd_smi_helpers.is_hypervisor():
            # Don't add this subparser on Hypervisors
            return

        # Subparser help text
        process_help = "Lists general process information running on the specified GPU"
        process_subcommand_help = """If no argument is provided, returns information for all GPUs on the system.
                                        If no argument is provided all process information will be displayed."""
        process_optionals_title = "Process arguments"

        # Required arguments help text
        gpu_help = "Select a GPU from the possible choices"

        # Help text for Arguments only on Guest and BM platforms
        general_help = "pid, process name, memory usage"
        engine_help = "All engine usages"
        pid_help = "Gets all process information about the specified process based on Process ID"
        name_help = """Gets all process information about the specified process based on Process Name.
                        If multiple processes have the same name information is returned for all of them.""" #@TODO wording

        # Create process subparser
        process_parser = subparsers.add_parser('process', help=process_help, description=process_subcommand_help)
        process_parser._optionals.title = process_optionals_title
        process_parser.formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90)
        process_parser.set_defaults(func=func)

        # Mutually Exclusive Args within the subparser
        device_args = process_parser.add_mutually_exclusive_group()
        device_args.add_argument('--gpu', action='store', help=gpu_help, choices=self.gpu_choices)

        # Optional Args
        process_parser.add_argument('-g', '--general', action='store_true', required=False, help=general_help)
        process_parser.add_argument('-e', '--engine', action='store_true', required=False, help=engine_help)
        process_parser.add_argument('-p', '--pid', action='store', required=False, help=pid_help)
        process_parser.add_argument('-n', '--name', action='store', required=False, help=name_help)


    def add_profile_parser(self, subparsers, func):
        if not (self.amd_smi_helpers.is_windows() and self.amd_smi_helpers.is_hypervisor()):
            # This subparser only applies to Azure Hyper-V systems
            return

        # Subparser help text
        profile_help = "Displays information about all profiles and current profile"
        profile_subcommand_help = "If no argument is provided, returns information for all GPUs on the system."
        profile_optionals_title = "Profile Arguments"

        # Required arguments help text
        gpu_help = "Select a GPU from the possible choices"

        # Create profile subparser
        profile_parser = subparsers.add_parser('profile', help=profile_help, description=profile_subcommand_help)
        profile_parser._optionals.title = profile_optionals_title
        profile_parser.formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90)
        profile_parser.set_defaults(func=func)

        # Mutually Exclusive Args within the subparser
        device_args = profile_parser.add_mutually_exclusive_group()
        device_args.add_argument('--gpu', action='store', help=gpu_help, choices=self.gpu_choices)


    def add_event_parser(self, subparsers, func):
        if self.amd_smi_helpers.is_linux() and not self.amd_smi_helpers.is_virtual_os():
            # This subparser only applies to Linux BareMetal & Linux Hypervisors
            return

        # Subparser help text
        event_help = "Displays event information for the given GPU"
        event_subcommand_help = "If no argument is provided, returns event information for all GPUs on the system."
        event_optionals_title = "Event Arguments"

        # Required arguments help text
        gpu_help = "Select a GPU from the possible choices"

        # Create event subparser
        event_parser = subparsers.add_parser('event', help=event_help, description=event_subcommand_help)
        event_parser._optionals.title = event_optionals_title
        event_parser.formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90)
        event_parser.set_defaults(func=func)

        # Mutually Exclusive Args within the subparser
        device_args = event_parser.add_mutually_exclusive_group()
        device_args.add_argument('--gpu', action='store', help=gpu_help, choices=self.gpu_choices)


    def add_topology_parser(self, subparsers, func):
        if not(self.amd_smi_helpers.is_baremetal() and self.amd_smi_helpers.is_linux()):
            # This subparser is only applicable to Baremetal Linux @TODO confirm how KVM should work
            return

        # Subparser help text
        topology_help = "Displays topology information of the devices."
        topology_subcommand_help = "If no argument is provided, returns information for all GPUs on the system."
        topology_optionals_title = "Topology arguments"

        # Required arguments help text
        gpu_help = "Select a GPU from the possible choices"

        # Help text for Arguments only on Guest and BM platforms
        topo_access_help = "Displays link accessibility between GPUs"
        topo_weight_help = "Displays relative weight between GPUs"
        topo_hops_help = "Displays the number of hops between GPUs"
        topo_type_help = "Displays the link type between GPUs."
        topo_numa_help = "Displays the numa nodes."

        # Create topology subparser
        topology_parser = subparsers.add_parser('topology', help=topology_help, description=topology_subcommand_help)
        topology_parser._optionals.title = topology_optionals_title
        topology_parser.formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90)
        topology_parser.set_defaults(func=func)

        # Mutually Exclusive Args within the subparser
        device_args = topology_parser.add_mutually_exclusive_group()
        device_args.add_argument('--gpu', action='store', help=gpu_help, choices=self.gpu_choices)

        # Optional Args
        topology_parser.add_argument('-a', '--topo-access', action='store_true', required=False, help=topo_access_help)
        topology_parser.add_argument('-w', '--topo-weight', action='store_true', required=False, help=topo_weight_help)
        topology_parser.add_argument('-o', '--topo-hops', action='store_true', required=False, help=topo_hops_help)
        topology_parser.add_argument('-t', '--topo-type', action='store_true', required=False, help=topo_type_help)
        topology_parser.add_argument('-n', '--topo-numa', action='store_true', required=False, help=topo_numa_help)


    def add_set_value_parser(self, subparsers, func):
        if not(self.amd_smi_helpers.is_baremetal() and self.amd_smi_helpers.is_linux()):
            # This subparser is only applicable to Baremetal Linux @TODO confirm how KVM should work
            return

        # Subparser help text
        set_value_help = "Set options for devices."
        set_value_subcommand_help = "The user must specify one of the options for the set configuration."
        set_value_optionals_title = "Set Arguments"

        # Required arguments help text
        gpu_help = "Select a GPU from the possible choices"

        # Help text for Arguments only on Guest and BM platforms
        set_clk_help = "Sets clock frequency levels for specified clocks"
        set_sclk_help = "Sets GPU clock frequency levels"
        set_mclk_help = "Sets memory clock frequency levels"
        set_pcie_help = "Sets PCIe clock frequency levels"
        set_slevel_help = "Change GPU clock frequency and voltage for a specific level"
        set_mlevel_help = "Change GPU memory frequency and voltage for a specific level"
        set_vc_help = "Change SCLK voltage curve for a specified point"
        set_srange_help = "Sets min and max SCLK speed"
        set_mrange_help = "Sets min and max MCLK speed"
        set_fan_help = "Sets GPU fan speed (level or %)"
        set_perf_level_help = "Sets performance level"
        set_overdrive_help = "Set GPU overdrive level"
        set_mem_overdrive_help = "Set memory overclock overdrive level"
        set_power_overdrive_help = "Set the maximum GPU power using power overdrive in Watts"
        set_profile_help = "Set power profile level (#) or a quoted string of custom profile attributes"
        set_perf_det_help = "Set GPU clock frequency limit to get minimal performance variation"
        ras_enable_help = "Enable RAS for specified block and error type"
        ras_disable_help = "Disable RAS for specified block and error type."
        ras_inject_help = "Inject RAS poison for specified block"

# -c, --setclk <type> <level>
# .
# -s, --setsclk <level>
# .
# -m, --setmclk <type> <level>
# .
# -p, --setpcie <level>
# .
# -S, --setslevel <sclk_level> <sclk> <svolt>
# .
# -M, --setmlevel <mclk_level> <mclk> <mvolt>
# .
# -v, --setvc <point> <sclk> <svolt>
# .
# -r, --setsrange <sclk_min> <sclk_max>
# 
# -R, --setmrange <mclk_min> <mclk_max>
# .
# -f, --setfan <level>
# 
# -pl, --setperflevel <level>
# 
# -o, --setoverdrive %
# Set GPU overdrive level.
# -O, --setmemoverdrive %
# Set memory overclock overdrive level.
# -po, --setpoweroverdrive <power>
# Set the maximum GPU power using power overdrive in Watts.
# -P, --setprofile <profile>
# Set power profile level (#) or a quoted string of custom profile attributes (“ # # # # “)
# -pd, --setperfdet <sclk>
# Set GPU clock frequency limit to get minimal performance variation.
# -re, --rasenable <block> <err_type>
# Enable RAS for specified block and error type.
# -rd, --rasdisable <block> <err_type>
# Disable RAS for specified block and error type.
# -ri, --rasinject <block>
# Inject RAS poison for specified block

        # Create set_value subparser
        set_value_parser = subparsers.add_parser('set', help=set_value_help, description=set_value_subcommand_help)
        set_value_parser._optionals.title = set_value_optionals_title
        set_value_parser.formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90)
        set_value_parser.set_defaults(func=func)

        # Mutually Exclusive Args within the subparser
        device_args = set_value_parser.add_mutually_exclusive_group(required=True)
        device_args.add_argument('--gpu', action='store', help=gpu_help, choices=self.gpu_choices)

        # Optional Args
        set_value_parser.add_argument('-c', '--setclk', action='store', required=False, help=topo_access_help)
        set_value_parser.add_argument('-s', '--topo-weight', action='store', required=False, help=topo_weight_help)
        set_value_parser.add_argument('-m', '--topo-hops', action='store', required=False, help=topo_hops_help)
        set_value_parser.add_argument('-p', '--topo-type', action='store', required=False, help=topo_type_help)
        set_value_parser.add_argument('-S', '--topo-numa', action='store', required=False, help=topo_numa_help)
        set_value_parser.add_argument('-M', '--topo-numa', action='store', required=False, help=topo_numa_help)
        set_value_parser.add_argument('-v', '--topo-numa', action='store', required=False, help=topo_numa_help)
        set_value_parser.add_argument('-r', '--topo-numa', action='store', required=False, help=topo_numa_help)
        set_value_parser.add_argument('-R', '--topo-numa', action='store', required=False, help=topo_numa_help)
        set_value_parser.add_argument('-f', '--topo-numa', action='store', required=False, help=topo_numa_help)
        set_value_parser.add_argument('-pl', '--topo-numa', action='store', required=False, help=topo_numa_help)
        set_value_parser.add_argument('-o' '--topo-numa', action='store', required=False, help=topo_numa_help)
        set_value_parser.add_argument('-O', '--topo-numa', action='store', required=False, help=topo_numa_help)
        set_value_parser.add_argument('-po', '--topo-numa', action='store', required=False, help=topo_numa_help)
        set_value_parser.add_argument('-P', '--topo-numa', action='store', required=False, help=topo_numa_help)
        set_value_parser.add_argument('-pd', '--topo-numa', action='store', required=False, help=topo_numa_help)
        set_value_parser.add_argument('-re', '--topo-numa', action='store', required=False, help=topo_numa_help)
        set_value_parser.add_argument('-rd', '--topo-numa', action='store', required=False, help=topo_numa_help)
        set_value_parser.add_argument('-ri', '--topo-numa', action='store', required=False, help=topo_numa_help)


    def add_reset_parser(self, subparsers, func):
        if not(self.amd_smi_helpers.is_baremetal() and self.amd_smi_helpers.is_linux()):
            # This subparser is only applicable to Baremetal Linux @TODO confirm how KVM should work
            return

        # Subparser help text
        reset_help = "Reset options for devices."
        reset_subcommand_help = "The user must specify one of the options to reset devices."
        reset_optionals_title = "Reset Arguments"

        # Required arguments help text
        gpu_help = "Select a GPU from the possible choices"

        # Help text for Arguments only on Guest and BM platforms
        gpureset_help = "Reset the specified GPU"
        resetclk_help = "Reset clocks and overdrive to default"
        resetfans_help = "Reset fans to automatic (driver) control"
        resetprofile_help = "Reset power profile back to default"
        resetpoweroverdrive_help = "Set the maximum GPU power back to the device default state"
        resetxgmierr_help = "Reset XGMI error counts"
        resetperfdet_help = "Disable performance determinism"

        # Create reset subparser
        reset_parser = subparsers.add_parser('reset', help=reset_help, description=reset_subcommand_help)
        reset_parser._optionals.title = reset_optionals_title
        reset_parser.formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90)
        reset_parser.set_defaults(func=func)

        # Mutually Exclusive Args within the subparser
        device_args = reset_parser.add_mutually_exclusive_group(required=True)
        device_args.add_argument('--gpu', action='store', help=gpu_help, choices=self.gpu_choices)

        # Optional Args
        reset_parser.add_argument('-g', '--gpureset', action='store_true', required=False, help=gpureset_help)
        reset_parser.add_argument('-c', '--resetclk', action='store_true', required=False, help=resetclk_help)
        reset_parser.add_argument('-f', '--resetfans', action='store_true', required=False, help=resetfans_help)
        reset_parser.add_argument('-p', '--resetprofile', action='store_true', required=False, help=resetprofile_help)
        reset_parser.add_argument('-o', '--resetpoweroverdrive', action='store_true', required=False, help=resetpoweroverdrive_help)
        reset_parser.add_argument('-x', '--resetxgmierr', action='store_true', required=False, help=resetxgmierr_help)
        reset_parser.add_argument('-d', '--resetperfdet', action='store_true', required=False, help=resetperfdet_help)


    def add_misc_parser(self, subparsers, func):
        if not(self.amd_smi_helpers.is_baremetal() and self.amd_smi_helpers.is_linux()):
            # This subparser is only applicable to Baremetal Linux @TODO confirm how KVM should work
            return

        # Subparser help text
        misc_help = "The miscellaneous options"
        misc_subcommand_help = "The user must specify one of the options to reset devices."
        misc_optionals_title = "Misc Arguments"

        # Optional arguments help text
        gpu_help = "Select a GPU from the possible choices"
        load_help = "Load clock, fan, performance, and profile settings from a given file."
        save_help = "Save clock, fan, performance, and profile settings to a given file."

        # Create misc subparser
        misc_parser = subparsers.add_parser('misc', help=misc_help, description=misc_subcommand_help)
        misc_parser._optionals.title = misc_optionals_title
        misc_parser.formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90)
        misc_parser.set_defaults(func=func)

        # Mutually Exclusive Args within the subparser
        device_args = misc_parser.add_mutually_exclusive_group(required=True)
        device_args.add_argument('--gpu', action='store', help=gpu_help, choices=self.gpu_choices)

        # Optional Args
        misc_parser.add_argument('-l', '--load', action='store', type=open, required=False, help=load_help)
        misc_parser.add_argument('-s', '--save', action='store', type=open, required=False, help=save_help)


    # def add_gpu_v_parser(self, subparsers, func):
    #     if not(self.amd_smi_helpers.is_baremetal() and self.amd_smi_helpers.is_linux()):
    #         # This subparser is only applicable to Baremetal Linux @TODO confirm how KVM should work
    #         return

    #     # Subparser help text
    #     gpu_v_help = "The gpu_v options"
    #     gpu_v_subcommand_help = "The user must specify one of the options to reset devices."
    #     gpu_v_optionals_title = "gpu_v Arguments"

    #     # Optional arguments help text
    #     gpu_help = "Select a GPU from the possible choices"
    #     load_help = "Load clock, fan, performance, and profile settings from a given file."
    #     save_help = "Save clock, fan, performance, and profile settings to a given file."

    #     # Create gpu_v subparser
    #     gpu_v_parser = subparsers.add_parser('gpu_v', help=gpu_v_help, description=gpu_v_subcommand_help)
    #     gpu_v_parser._optionals.title = gpu_v_optionals_title
    #     gpu_v_parser.formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=80, width=90)
    #     gpu_v_parser.set_defaults(func=func)

    #     # Mutually Exclusive Args within the subparser
    #     device_args = gpu_v_parser.add_mutually_exclusive_group(required=True)
    #     device_args.add_argument('--gpu', action='store', help=gpu_help, choices=self.gpu_choices)

    #     # Optional Args
    #     gpu_v_parser.add_argument('-l', '--load', action='store', type=open, required=False, help=load_help)
    #     gpu_v_parser.add_argument('-s', '--save', action='store', type=open, required=False, help=save_help)

#!/usr/bin/python3

# from amd_smi_init import *

from amd_smi_commands import AMD_SMI_Commands
from amd_smi_parser import AMD_SMI_Parser


# sudo /src/out/ubuntu-20.04/20.04/bin/rocm-smi -bc --json | python -m json.tool


if __name__ == "__main__":
    amd_smi_commands = AMD_SMI_Commands()
    amd_smi_parser = AMD_SMI_Parser(amd_smi_commands.version,
                                    amd_smi_commands.discovery,
                                    amd_smi_commands.static,
                                    amd_smi_commands.firmware,
                                    amd_smi_commands.bad_pages,
                                    amd_smi_commands.metric,
                                    amd_smi_commands.process,
                                    amd_smi_commands.profile,
                                    amd_smi_commands.event,
                                    amd_smi_commands.topology,
                                    amd_smi_commands.set_value,
                                    amd_smi_commands.reset,
                                    amd_smi_commands.misc,
                                    amd_smi_commands.gpu_v)

    args = amd_smi_parser.parse_args()
    args.func(args) # This needs to be there to handle subparsers with no subcommands
    # AMDSMI logger print out json, csv, or string

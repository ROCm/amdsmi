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
import sys

from amdsmi_commands import AMDSMICommands
from amdsmi_parser import AMDSMIParser


if __name__ == "__main__":
    amd_smi_commands = AMDSMICommands()
    amd_smi_parser = AMDSMIParser(amd_smi_commands.version,
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
                                    amd_smi_commands.rocm_smi)

    args = amd_smi_parser.parse_args(args=None if sys.argv[1:] else ['--help'])

    # Handle command modifiers before subcommand execution
    if args.json:
        amd_smi_commands.logger.format = amd_smi_commands.logger.LoggerFormat.json.value
    if args.csv:
        amd_smi_commands.logger.format = amd_smi_commands.logger.LoggerFormat.csv.value
    if args.file:
        amd_smi_commands.logger.destination = args.file
    if args.loglevel:
        logging_dict = {'DEBUG' : logging.DEBUG,
                        'INFO' : logging.INFO,
                        'WARNING': logging.WARNING,
                        'ERROR': logging.ERROR,
                        'CRITICAL': logging.CRITICAL}
        logging.basicConfig(format='%(levelname)s: %(message)s', level=logging_dict[args.loglevel])
    if args.compatibility:
        amd_smi_commands.logger.compatibility = args.compatibility

    # Execute subcommands
    args.func(args)

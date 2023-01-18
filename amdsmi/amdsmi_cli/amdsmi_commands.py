#!/usr/bin/python3

import platform
import signal
import subprocess
import sys
import time
import traceback

from pathlib import Path

# from amd_smi_init import *
from BDF import BDF
from _version import __version__

from amdsmi_logger import AMD_SMI_Logger
from amdsmi_helpers import *

class AMD_SMI_Commands(object):
    # def __init__(self, amd_smi_logger) -> None:
    #     logger = amd_smi_logger
    #     # Make an AMD-SMI-Object-Logger only with the commands object on init
    #     # Call the logger when we want to store a print: 
    #     # self.logger.store_output(gpu_id, string) # store in ordered dict
          # Every function prints the logger at the end 
          # logger.printoutput(args.json, args.csv) # Which in Logger handles and checks for json or csv
    #     Check if init can accept args given, if so then init can be used to call watch functions for looping


    def version(self, args):
        kernel_version = 123
        amdsmi_lib_version = amdsmi_interface.amdsmi_get_version()
        {'major': 1, 'minor': 0, 'patch': 0, 'build': '0'}
        amdsmi_lib_version_str = f'{amdsmi_lib_version["major"]}.{amdsmi_lib_version["minor"]}.{amdsmi_lib_version["patch"]}'
        print(f'AMD-SMI Tool: {__version__} | AMD-SMI Library version: {amdsmi_lib_version_str} |  Kernel version: {kernel_version}')

    def discovery(self, args):
        print('discovery test')


    def static(self, args):
        #This is where the arg handling comes through
        print(args.asic)
        print(args.bus)
        print(args.driver)
        print('static test')


    def firmware(self, args):
        for elem in range(100000):
            time.sleep(1)


    def bad_pages(self, args):
        # Retired Pages
        print('Bad Pages test')


    def metric(self, args):
        print('Metric test')


    def process(self, args):
        print('Process Test')


    def profile(self, args):
        print('Profile test')


    def event(self, args):
        print('event test')


    def topology(self, args):
        print('topology test')


    def set_value(self, args):
        print('set_value test')


    def reset(self, args):
        print('reset test')


    def misc(self, args):
        print('misc test')


    def gpu_v(self, args):
        print('misc test')


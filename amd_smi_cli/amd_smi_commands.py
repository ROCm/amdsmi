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

from amd_smi_logger import AMD_SMI_Logger



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
        print(f'AMD-SMI version: {__version__}  |  Kernel version: {kernel_version}')


    def discovery(self, args):
        print('discovery test')


    def static(self, args):
        #This is where the arg handling comes through
        print(args.asic)
        print(args.bus)
        print(args.driver)
        print('static test')


    def firmware(self, args):
        print('firmware test')


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


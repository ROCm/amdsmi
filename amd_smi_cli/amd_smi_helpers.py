#!/usr/bin/python3

import argparse
import platform
import signal
import subprocess
import sys
import time
import traceback
import logging

from pathlib import Path

from BDF import BDF
from amd_smi_init import *


class AMD_SMI_Helpers(object):
    def __init__(self) -> None:
        # implement basic config for debug logs
        self.operating_system = platform.system()
        self._is_hypervisor = False
        self._is_virtual_os = False
        self._is_baremetal = False
        self._is_linux = False
        self._is_windows = False

        self.virtual_operating_systems_product_names = ['KVM', 'VirtualBox', 'VMware'] #@TODO get KVM example

        if self.operating_system.startswith('Linux'):
            self._is_linux = True
            # logging.debug(f'whatever:{self._is_linux}')
            # KVM hypervisor check @TODO

            product_name = ''
            product_name_path = Path('/sys/class/dmi/id/product_name')
            if product_name_path.exists():
                product_name = product_name_path.read_text().strip()

            if product_name == '':
                # Unable to determine product_name default to baremetal
                self._is_baremetal = True
            else:
                for vm_os in self.virtual_operating_systems_product_names:
                    if product_name.startswith(vm_os):
                        # Log that this is a virtual OS 
                        self._is_virtual_os = True
                        break
            
            # The current way I determine if a system is baremetal by deduction of the other two arguments
            self._is_baremetal = not self._is_hypervisor and not self._is_virtual_os
            

        if self.operating_system.startswith('VMkernel'):
            self._is_hypervisor = True


        if self.operating_system.startswith('Window'):
            # Check Powershell for Hyper-V enablement
            self._is_windows = True

        # Get-CimInstance -ClassName Win32_ComputerSystem Manufacturer
        

        # if self.product_name == '' and not self._is_hypervisor:
        #     self._is_virtual_os = any(self.product_name.startswith(virtual_os) for virtual_os in self.virtual_operating_systems)


        # self.operating_system = ''


    def os_info(self):
        # Return OS info
        # operating_system = 
        
        
        # if sys.platform.startswith('win'):

        # elif sys.platform.startswith('linux'):

        return True


    def is_virtual_os(self):
        return self._is_virtual_os


    def is_hypervisor(self):
        # Returns True if hypervisor is enabled on the system
        return self._is_hypervisor


    def is_baremetal(self):
        # Returns True if system is baremetal, if system is hypervisor this should return False
        return self._is_baremetal



    def is_linux(self):
        return self._is_linux


    def is_windows(self):
        return self._is_windows


    def get_gpu_choices(self):
        # Return in format {gpu_index : (BDF, UUID)}

        gpu_choices = {}
        gpu_index = '1'
        gpu_bdf = BDF('0000:23:00.0')
        gpu_uuid = '1234'
        gpu_choices[gpu_index] = (gpu_bdf, gpu_uuid)
        return gpu_choices
        

    def get_devices(self):
        pass


    def get_device_from_socket(self):
        pass


    def get_amd_gpu_bdfs(self):
        pass


    def get_amd_cpu_bdfs(self):
        pass



    # def getBus(device):
    #     """ Return the bus identifier of a given device

    #     @param device: DRM device identifier
    #     """
    #     bdfid = c_uint64(0)
    #     ret = rocmsmi.rsmi_dev_pci_id_get(device, byref(bdfid))

    #     # BDFID = ((DOMAIN & 0xffffffff) << 32) | ((BUS & 0xff) << 8) |((DEVICE & 0x1f) <<3 ) | (FUNCTION & 0x7)
    #     domain = (bdfid.value >> 32) & 0xffffffff
    #     bus = (bdfid.value >> 8) & 0xff
    #     device = (bdfid.value >> 3) & 0x1f
    #     function = bdfid.value & 0x7

    #     pic_id = '{:04X}:{:02X}:{:02X}.{:0X}'.format(domain, bus, device, function)
    #     if rsmi_ret_ok(ret, device):
    #         return pic_id

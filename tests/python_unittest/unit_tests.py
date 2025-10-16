#!/usr/bin/env python3
#
# Copyright (c) Advanced Micro Devices, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

'''
In Unit Testing, what is specifically tested within these units includes:
1. Correctness of logic: Ensuring that the code performs its intended operations
   accurately and produces the expected results.
2. Edge cases and boundary conditions: Testing how the unit behaves with extreme
   or unusual inputs, such as null values, empty strings, maximum/minimum values,
   or invalid data.
3. Error handling: Verifying that the unit correctly handles errors and exceptions,
   including throwing appropriate exceptions or returning specific error codes.
4. State changes: For classes or objects, testing that their internal state is modified
   as expected after method calls.
5. Interactions with dependencies (mocked): While unit tests aim for isolation, units
   often have dependencies on other parts of the system or external resources. In unit
   testing, these dependencies are typically "mocked" or "stubbed" to control their
   behavior and ensure the test focuses solely on the unit under examination.
'''

import ctypes
import inspect
import json
import os
import sys
import unittest
sys.path.append("/opt/rocm/libexec/amdsmi_cli/")

try:
    import amdsmi
except ImportError as exc:
    raise ImportError("Could not import /opt/rocm/libexec/amdsmi_cli/amdsmi_cli.py") from exc

not_supported_error_codes = \
[
    ( '2', 'AMDSMI_STATUS_NOT_SUPPORTED'),
    ( '3', 'AMDSMI_STATUS_NOT_YET_IMPLEMENTED'),
    ('49', 'AMDSMI_STATUS_NO_HSMP_MSG_SUP')
]

error_map = \
{
    '0': 'AMDSMI_STATUS_SUCCESS',
    '1': 'AMDSMI_STATUS_INVAL',
    '2': 'AMDSMI_STATUS_NOT_SUPPORTED',
    '3': 'AMDSMI_STATUS_NOT_YET_IMPLEMENTED',
    '4': 'AMDSMI_STATUS_FAIL_LOAD_MODULE',
    '5': 'AMDSMI_STATUS_FAIL_LOAD_SYMBOL',
    '6': 'AMDSMI_STATUS_DRM_ERROR',
    '7': 'AMDSMI_STATUS_API_FAILED',
    '8': 'AMDSMI_STATUS_TIMEOUT',
    '9': 'AMDSMI_STATUS_RETRY',
    '10': 'AMDSMI_STATUS_NO_PERM',
    '11': 'AMDSMI_STATUS_INTERRUPT',
    '12': 'AMDSMI_STATUS_IO',
    '13': 'AMDSMI_STATUS_ADDRESS_FAULT',
    '14': 'AMDSMI_STATUS_FILE_ERROR',
    '15': 'AMDSMI_STATUS_OUT_OF_RESOURCES',
    '16': 'AMDSMI_STATUS_INTERNAL_EXCEPTION',
    '17': 'AMDSMI_STATUS_INPUT_OUT_OF_BOUNDS',
    '18': 'AMDSMI_STATUS_INIT_ERROR',
    '19': 'AMDSMI_STATUS_REFCOUNT_OVERFLOW',
    '30': 'AMDSMI_STATUS_BUSY',
    '31': 'AMDSMI_STATUS_NOT_FOUND',
    '32': 'AMDSMI_STATUS_NOT_INIT',
    '33': 'AMDSMI_STATUS_NO_SLOT',
    '34': 'AMDSMI_STATUS_DRIVER_NOT_LOADED',
    '39': 'AMDSMI_STATUS_MORE_DATA',
    '40': 'AMDSMI_STATUS_NO_DATA',
    '41': 'AMDSMI_STATUS_INSUFFICIENT_SIZE',
    '42': 'AMDSMI_STATUS_UNEXPECTED_SIZE',
    '43': 'AMDSMI_STATUS_UNEXPECTED_DATA',
    '44': 'AMDSMI_STATUS_NON_AMD_CPU',
    '45': 'AMDSMI_STATUS_NO_ENERGY_DRV',
    '46': 'AMDSMI_STATUS_NO_MSR_DRV',
    '47': 'AMDSMI_STATUS_NO_HSMP_DRV',
    '48': 'AMDSMI_STATUS_NO_HSMP_SUP',
    '49': 'AMDSMI_STATUS_NO_HSMP_MSG_SUP',
    '50': 'AMDSMI_STATUS_HSMP_TIMEOUT',
    '51': 'AMDSMI_STATUS_NO_DRV',
    '52': 'AMDSMI_STATUS_FILE_NOT_FOUND',
    '53': 'AMDSMI_STATUS_ARG_PTR_NULL',
    '54': 'AMDSMI_STATUS_AMDGPU_RESTART_ERR',
    '55': 'AMDSMI_STATUS_SETTING_UNAVAILABLE',
    '56': 'AMDSMI_STATUS_CORRUPTED_EEPROM',
    '0xFFFFFFFE': 'AMDSMI_STATUS_MAP_ERROR',
    '0xFFFFFFFF': 'AMDSMI_STATUS_UNKNOWN_ERROR'
}

verbose=1
if '-q' in sys.argv or '--quiet' in sys.argv:
    verbose=0
elif '-v' in sys.argv or '--verbose' in sys.argv:
    verbose=2
has_info_printed = False


class TestAmdSmiPythonBDF(unittest.TestCase):
    valid_bdfs = {
        "00:00.0": [0, 0, 0, 0],
        "01:01.1": [0, 1, 1, 1],
        "FF:1F.7": [0, 255, 31, 7],
        "FF:00.7": [0, 255, 0, 7],
        "11:01.2": [0, 17, 1, 2],
        "11:0a.2": [0, 17, 10, 2],
        "0000:FF:1F.7": [0, 255, 31, 7],
        "0001:ff:1F.7": [1, 255, 31, 7],
        "ffff:FF:1f.7": [65535, 255, 31, 7],
    }

    invalid_bdfs = {
        # invalid bdf strings, expect None
        None: None,
        "": None,
        "00:00:0": None,
        "00.00:0": None,
        "00:00.Z": None,
        "00:0Z.0": None,
        "0Z:00.0": None,
        "Z00:00.0": None,
        "A00:00.0": None,
        "0A00:00.0": None,
        "00:00.07": None,
        "00:00.8": None,
        "00:00.10": None,
        "00:00.11": None,
        "00:00.-1": None,
        "00:00.*-1": None,
        "00:00.123": None,
        "00:20.0": None,
        "00:45.0": None,
        "00:200.0": None,
        "00:002.0": None,
        "100:00.0": None,
        "0100:00.0": None,
        "00100:00.0": None,
        "0101:00.0": None,
        "00001:00.0": None,
        "10001:00.0": None,
        "45:0.0": None,
        ".00:00.0": None,
        "00.00.0": None,
        "00.0.0": None,
        "0.00.0": None,
        "000.00.0": None,
        "00 00 0": None,
        " 00:00.0": None,
        "00:00.0 ": None,
        "0000:00.00.0": None,
        "000:00:00.0": None,
        "00:00:00.1": None,
        "0:00:00.1": None,
        "0000 00 00 0": None,
        "-1-1:00:00.0": None,
        "AAAA:00:AA.0": None,
        "*1*1:00:00.0": None,
        "0000:00:00.07": None,
        "0000:00:00.8": None,
        "0000:00:00.10": None,
        "0000:00:00.11": None,
        "0000:00:00.-1": None,
        "0000:00:00.*-1": None,
        "0000:00:00.123": None,
        "0000:00:20.0": None,
        "0000:00:45.0": None,
        "0000:00:200.0": None,
        "0000:00:002.0": None,
        "0000:100:00.0": None,
        "0000:0100:00.0": None,
        "0000:00100:00.0": None,
        "0000:0101:00.0": None,
        "0000:00001:00.0": None,
        "0000:10001:00.0": None,
        "0000:45:0.0": None,
        ".0000.00:00.0": None,
        "0000.00.0.0": None,
        " 0000:00:00.0": None,
        "0000:00:00.0 ": None,
    }

    def test_parse_bdf(self):
        # go through all bdfs
        expectations = self.valid_bdfs.copy()
        expectations.update(self.invalid_bdfs)
        for bdf in expectations:
            expected = expectations[bdf]
            result = amdsmi.amdsmi_interface._parse_bdf(bdf)
            self.assertEqual(result, expected,
                             "Expected {} for bdf {}, but got {}".format(
                                 expected, bdf, result))

    @classmethod
    def _convert_bdf_to_long(cls, bdf):
        if len(bdf) == 12:
            return bdf
        if len(bdf) == 7:
            return "0000:" + bdf
        return None

    def test_format_bdf(self):
        # go through valid bdfs
        expectations = self.valid_bdfs.copy()
        for bdf_string in expectations:
            # use key as result and value as input
            bdf_list = expectations[bdf_string]
            smi_bdf = amdsmi.amdsmi_interface._make_amdsmi_bdf_from_list(bdf_list)
            expected = TestAmdSmiPythonBDF._convert_bdf_to_long(bdf_string)
            if expected:
                expected = expected.lower()
            if smi_bdf:
                result = amdsmi.amdsmi_interface._format_bdf(smi_bdf)
            else:
                result = "None"
            self.assertEqual(result, expected,
                             "Expected {} for bdf {}, but got {}".format(
                                 expected, bdf_string, result))

    def test_check_res(self):
        # expect retry error to raise SmiRetryException
        with self.assertRaises(amdsmi.AmdSmiRetryException) as retry_test:
            amdsmi.amdsmi_interface._check_res(
                (lambda: amdsmi.amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_RETRY)())
        # except retry error to have AMDSMI_STATUS_RETRY error code
        self.assertEqual(retry_test.exception.get_error_code(),
                         amdsmi.amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_RETRY)

        # expect timeout error to raise SmiTimeoutException
        with self.assertRaises(amdsmi.AmdSmiTimeoutException) as timeout_test:
            amdsmi.amdsmi_interface._check_res(
                (lambda: amdsmi.amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_TIMEOUT)())
        # except timeout error to have AMDSMI_STATUS_RETRY error code
        self.assertEqual(timeout_test.exception.get_error_code(),
                         amdsmi.amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_TIMEOUT)

        # expect invalid args error to raise AmdSmiLibraryException
        with self.assertRaises(amdsmi.AmdSmiLibraryException) as inval_test:
            amdsmi.amdsmi_interface._check_res(
                (lambda: amdsmi.amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_INVAL)())
        # expect invalid args error to have AMDSMI_STATUS_INVAL error code
        self.assertEqual(inval_test.exception.get_error_code(),
                         amdsmi.amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_INVAL)

class TestAmdSmiPython(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        global has_info_printed
        if verbose and has_info_printed is False:
            # Execute the following to print the asic and board info once
            # per test run
            has_info_printed = True
            self.setUp()
            for i, gpu in enumerate(self.processors):
                # Print asic info
                msg = f'asic info(gpu={i})'
                try:
                    ret = amdsmi.amdsmi_get_gpu_asic_info(gpu)
                    self._print(msg, ret)
                except amdsmi.AmdSmiLibraryException as e:
                    raise e
            for i, gpu in enumerate(self.processors):
                # Print board info
                msg = f'board info(gpu={i})'
                try:
                    ret = amdsmi.amdsmi_get_gpu_board_info(gpu)
                    self._print(msg, ret)
                except amdsmi.AmdSmiLibraryException as e:
                    raise e
            self.tearDown()
        return

    max_num_physical_devices = amdsmi.amdsmi_interface.AMDSMI_MAX_NUM_XCP * amdsmi.amdsmi_interface.AMDSMI_MAX_DEVICES
    PASS = 'AMDSMI_STATUS_SUCCESS'
    FAIL = 'AMDSMI_STATUS_INVAL'

    # Tests marked wtih either of these flags will be skipped
    # and need to be implemented later.
    TODO_SKIP_FAIL = True
    TODO_SKIP_NOT_COMPLETE = True

    status_types = \
    [
        ('SUCCESS', amdsmi.AmdSmiStatus.SUCCESS, PASS),
        ('INVAL', amdsmi.AmdSmiStatus.INVAL, PASS),
        ('NOT_SUPPORTED', amdsmi.AmdSmiStatus.NOT_SUPPORTED, PASS),
        ('NOT_YET_IMPLEMENTED', amdsmi.AmdSmiStatus.NOT_YET_IMPLEMENTED, PASS),
        ('FAIL_LOAD_MODULE', amdsmi.AmdSmiStatus.FAIL_LOAD_MODULE, PASS),
        ('FAIL_LOAD_SYMBOL', amdsmi.AmdSmiStatus.FAIL_LOAD_SYMBOL, PASS),
        ('DRM_ERROR', amdsmi.AmdSmiStatus.DRM_ERROR, PASS),
        ('API_FAILED', amdsmi.AmdSmiStatus.API_FAILED, PASS),
        ('TIMEOUT', amdsmi.AmdSmiStatus.TIMEOUT, PASS),
        ('RETRY', amdsmi.AmdSmiStatus.RETRY, PASS),
        ('NO_PERM', amdsmi.AmdSmiStatus.NO_PERM, PASS),
        ('INTERRUPT', amdsmi.AmdSmiStatus.INTERRUPT, PASS),
        ('IO', amdsmi.AmdSmiStatus.IO, PASS),
        ('ADDRESS_FAULT', amdsmi.AmdSmiStatus.ADDRESS_FAULT, PASS),
        ('FILE_ERROR', amdsmi.AmdSmiStatus.FILE_ERROR, PASS),
        ('OUT_OF_RESOURCES', amdsmi.AmdSmiStatus.OUT_OF_RESOURCES, PASS),
        ('INTERNAL_EXCEPTION', amdsmi.AmdSmiStatus.INTERNAL_EXCEPTION, PASS),
        ('INPUT_OUT_OF_BOUNDS', amdsmi.AmdSmiStatus.INPUT_OUT_OF_BOUNDS, PASS),
        ('INIT_ERROR', amdsmi.AmdSmiStatus.INIT_ERROR, PASS),
        ('REFCOUNT_OVERFLOW', amdsmi.AmdSmiStatus.REFCOUNT_OVERFLOW, PASS),
        ('DIRECTORY_NOT_FOUND', amdsmi.AmdSmiStatus.DIRECTORY_NOT_FOUND, PASS),
        ('BUSY', amdsmi.AmdSmiStatus.BUSY, PASS),
        ('NOT_FOUND', amdsmi.AmdSmiStatus.NOT_FOUND, PASS),
        ('NOT_INIT', amdsmi.AmdSmiStatus.NOT_INIT, PASS),
        ('NO_SLOT', amdsmi.AmdSmiStatus.NO_SLOT, PASS),
        ('DRIVER_NOT_LOADED', amdsmi.AmdSmiStatus.DRIVER_NOT_LOADED, PASS),
        ('MORE_DATA', amdsmi.AmdSmiStatus.MORE_DATA, PASS),
        ('NO_DATA', amdsmi.AmdSmiStatus.NO_DATA, PASS),
        ('INSUFFICIENT_SIZE', amdsmi.AmdSmiStatus.INSUFFICIENT_SIZE, PASS),
        ('UNEXPECTED_SIZE', amdsmi.AmdSmiStatus.UNEXPECTED_SIZE, PASS),
        ('UNEXPECTED_DATA', amdsmi.AmdSmiStatus.UNEXPECTED_DATA, PASS),
        ('NON_AMD_CPU', amdsmi.AmdSmiStatus.NON_AMD_CPU, PASS),
        ('NO_ENERGY_DRV', amdsmi.AmdSmiStatus.NO_ENERGY_DRV, PASS),
        ('NO_MSR_DRV', amdsmi.AmdSmiStatus.NO_MSR_DRV, PASS),
        ('NO_HSMP_DRV', amdsmi.AmdSmiStatus.NO_HSMP_DRV, PASS),
        ('NO_HSMP_SUP', amdsmi.AmdSmiStatus.NO_HSMP_SUP, PASS),
        ('NO_HSMP_MSG_SUP', amdsmi.AmdSmiStatus.NO_HSMP_MSG_SUP, PASS),
        ('HSMP_TIMEOUT', amdsmi.AmdSmiStatus.HSMP_TIMEOUT, PASS),
        ('NO_DRV', amdsmi.AmdSmiStatus.NO_DRV, PASS),
        ('FILE_NOT_FOUND', amdsmi.AmdSmiStatus.FILE_NOT_FOUND, PASS),
        ('ARG_PTR_NULL', amdsmi.AmdSmiStatus.ARG_PTR_NULL, PASS),
        ('AMDGPU_RESTART_ERR', amdsmi.AmdSmiStatus.AMDGPU_RESTART_ERR, PASS),
        ('SETTING_UNAVAILABLE', amdsmi.AmdSmiStatus.SETTING_UNAVAILABLE, PASS),
        ('CORRUPTED_EEPROM', amdsmi.AmdSmiStatus.CORRUPTED_EEPROM, PASS),
        ('MAP_ERROR', amdsmi.AmdSmiStatus.MAP_ERROR, PASS),
        ('UNKNOWN_ERROR', amdsmi.AmdSmiStatus.UNKNOWN_ERROR, PASS)
    ]

    clk_types = \
    [
        ('SYS', amdsmi.AmdSmiClkType.SYS, PASS),
        ('GFX', amdsmi.AmdSmiClkType.GFX, PASS),
        ('DF', amdsmi.AmdSmiClkType.DF, PASS),
        ('DCEF', amdsmi.AmdSmiClkType.DCEF, [PASS, FAIL]),
        ('SOC', amdsmi.AmdSmiClkType.SOC, PASS),
        ('MEM', amdsmi.AmdSmiClkType.MEM, PASS),
        ('PCIE', amdsmi.AmdSmiClkType.PCIE, [PASS, FAIL]),
        ('VCLK0', amdsmi.AmdSmiClkType.VCLK0, PASS),
        ('VCLK1', amdsmi.AmdSmiClkType.VCLK1, PASS),
        ('DCLK0', amdsmi.AmdSmiClkType.DCLK0, PASS),
        ('DCLK1', amdsmi.AmdSmiClkType.DCLK1, PASS)
    ]

    clk_limit_types = \
    [
        ('MIN', amdsmi.AmdSmiClkLimitType.MIN, PASS),
        ('MAX', amdsmi.AmdSmiClkLimitType.MAX, PASS)
    ]

    io_bw_encodings = \
    [
        ('AGG_BW0', amdsmi.amdsmi_interface.amdsmi_wrapper.AGG_BW0, PASS),
        ('RD_BW0', amdsmi.amdsmi_interface.amdsmi_wrapper.RD_BW0, PASS),
        ('WR_BW0', amdsmi.amdsmi_interface.amdsmi_wrapper.WR_BW0, PASS)
    ]

    gpu_blocks = \
    [
        ('INVALID', amdsmi.AmdSmiGpuBlock.INVALID, FAIL),
        ('UMC', amdsmi.AmdSmiGpuBlock.UMC, PASS),
        ('SDMA', amdsmi.AmdSmiGpuBlock.SDMA, PASS),
        ('GFX', amdsmi.AmdSmiGpuBlock.GFX, PASS),
        ('MMHUB', amdsmi.AmdSmiGpuBlock.MMHUB, PASS),
        ('ATHUB', amdsmi.AmdSmiGpuBlock.ATHUB, PASS),
        ('PCIE_BIF', amdsmi.AmdSmiGpuBlock.PCIE_BIF, PASS),
        ('HDP', amdsmi.AmdSmiGpuBlock.HDP, PASS),
        ('XGMI_WAFL', amdsmi.AmdSmiGpuBlock.XGMI_WAFL, PASS),
        ('DF', amdsmi.AmdSmiGpuBlock.DF, PASS),
        ('SMN', amdsmi.AmdSmiGpuBlock.SMN, PASS),
        ('SEM', amdsmi.AmdSmiGpuBlock.SEM, PASS),
        ('MP0', amdsmi.AmdSmiGpuBlock.MP0, PASS),
        ('MP1', amdsmi.AmdSmiGpuBlock.MP1, PASS),
        ('FUSE', amdsmi.AmdSmiGpuBlock.FUSE, PASS),
        ('MCA', amdsmi.AmdSmiGpuBlock.MCA, PASS),
        ('VCN', amdsmi.AmdSmiGpuBlock.VCN, PASS),
        ('JPEG', amdsmi.AmdSmiGpuBlock.JPEG, PASS),
        ('IH', amdsmi.AmdSmiGpuBlock.IH, PASS),
        ('MPIO', amdsmi.AmdSmiGpuBlock.MPIO, PASS),
        ('RESERVED', amdsmi.AmdSmiGpuBlock.RESERVED, FAIL)
    ]

    memory_types = \
    [
        ('VRAM', amdsmi.AmdSmiMemoryType.VRAM, PASS),
        ('VIS_VRAM', amdsmi.AmdSmiMemoryType.VIS_VRAM, PASS),
        ('GTT', amdsmi.AmdSmiMemoryType.GTT, PASS)
    ]

    reg_types = \
    [
        ('XGMI', amdsmi.AmdSmiRegType.XGMI, PASS),
        ('WAFL', amdsmi.AmdSmiRegType.WAFL, PASS),
        ('PCIE', amdsmi.AmdSmiRegType.PCIE, PASS),
        ('USR', amdsmi.AmdSmiRegType.USR, PASS),
        ('USR1', amdsmi.AmdSmiRegType.USR1, PASS)
    ]

    voltage_metrics = \
    [
        ('CURRENT', amdsmi.AmdSmiVoltageMetric.CURRENT, PASS),
        ('MAX', amdsmi.AmdSmiVoltageMetric.MAX, PASS),
        ('MIN_CRIT', amdsmi.AmdSmiVoltageMetric.MIN_CRIT, PASS),
        ('MIN', amdsmi.AmdSmiVoltageMetric.MIN, PASS),
        ('MAX_CRIT', amdsmi.AmdSmiVoltageMetric.MAX_CRIT, PASS),
        ('AVERAGE', amdsmi.AmdSmiVoltageMetric.AVERAGE, PASS),
        ('LOWEST', amdsmi.AmdSmiVoltageMetric.LOWEST, PASS),
        ('HIGHEST', amdsmi.AmdSmiVoltageMetric.HIGHEST, PASS)
    ]

    voltage_types = \
    [
        ('VDDGFX', amdsmi.AmdSmiVoltageType.VDDGFX, PASS),
        ('VDDBOARD', amdsmi.AmdSmiVoltageType.VDDBOARD, PASS),
        ('INVALID', amdsmi.AmdSmiVoltageType.INVALID, FAIL)
    ]

    link_types = \
    [
        ('AMDSMI_LINK_TYPE_INTERNAL', amdsmi.AmdSmiLinkType.AMDSMI_LINK_TYPE_INTERNAL, PASS),
        ('AMDSMI_LINK_TYPE_XGMI', amdsmi.AmdSmiLinkType.AMDSMI_LINK_TYPE_XGMI, PASS),
        ('AMDSMI_LINK_TYPE_PCIE', amdsmi.AmdSmiLinkType.AMDSMI_LINK_TYPE_PCIE, PASS),
        ('AMDSMI_LINK_TYPE_NOT_APPLICABLE', amdsmi.AmdSmiLinkType.AMDSMI_LINK_TYPE_NOT_APPLICABLE, FAIL),
        ('AMDSMI_LINK_TYPE_UNKNOWN', amdsmi.AmdSmiLinkType.AMDSMI_LINK_TYPE_UNKNOWN, FAIL)
    ]

    temperature_types = \
    [
        ('EDGE', amdsmi.AmdSmiTemperatureType.EDGE, PASS),
        ('HOTSPOT', amdsmi.AmdSmiTemperatureType.HOTSPOT, PASS),
        ('JUNCTION', amdsmi.AmdSmiTemperatureType.JUNCTION, PASS),
        ('VRAM', amdsmi.AmdSmiTemperatureType.VRAM, PASS),
        ('HBM_0', amdsmi.AmdSmiTemperatureType.HBM_0, PASS),
        ('HBM_1', amdsmi.AmdSmiTemperatureType.HBM_1, PASS),
        ('HBM_2', amdsmi.AmdSmiTemperatureType.HBM_2, PASS),
        ('HBM_3', amdsmi.AmdSmiTemperatureType.HBM_3, PASS),
        ('PLX', amdsmi.AmdSmiTemperatureType.PLX, PASS)
    ]

    temperature_metrics = \
    [
        ('CURRENT', amdsmi.AmdSmiTemperatureMetric.CURRENT, PASS),
        ('MAX', amdsmi.AmdSmiTemperatureMetric.MAX, PASS),
        ('MIN', amdsmi.AmdSmiTemperatureMetric.MIN, PASS),
        ('MAX_HYST', amdsmi.AmdSmiTemperatureMetric.MAX_HYST, PASS),
        ('MIN_HYST', amdsmi.AmdSmiTemperatureMetric.MIN_HYST, PASS),
        ('CRITICAL', amdsmi.AmdSmiTemperatureMetric.CRITICAL, PASS),
        ('CRITICAL_HYST', amdsmi.AmdSmiTemperatureMetric.CRITICAL_HYST, PASS),
        ('EMERGENCY', amdsmi.AmdSmiTemperatureMetric.EMERGENCY, PASS),
        ('EMERGENCY_HYST', amdsmi.AmdSmiTemperatureMetric.EMERGENCY_HYST, PASS),
        ('CRIT_MIN', amdsmi.AmdSmiTemperatureMetric.CRIT_MIN, PASS),
        ('CRIT_MIN_HYST', amdsmi.AmdSmiTemperatureMetric.CRIT_MIN_HYST, PASS),
        ('OFFSET', amdsmi.AmdSmiTemperatureMetric.OFFSET, PASS),
        ('LOWEST', amdsmi.AmdSmiTemperatureMetric.LOWEST, PASS),
        ('HIGHEST', amdsmi.AmdSmiTemperatureMetric.HIGHEST, PASS)
    ]

    utilization_counter_types = \
    [
        ('COARSE_GRAIN_GFX_ACTIVITY', amdsmi.AmdSmiUtilizationCounterType.COARSE_GRAIN_GFX_ACTIVITY, PASS),
        ('COARSE_GRAIN_MEM_ACTIVITY', amdsmi.AmdSmiUtilizationCounterType.COARSE_GRAIN_MEM_ACTIVITY, PASS),
        ('COARSE_DECODER_ACTIVITY', amdsmi.AmdSmiUtilizationCounterType.COARSE_DECODER_ACTIVITY, PASS),
        ('FINE_GRAIN_GFX_ACTIVITY', amdsmi.AmdSmiUtilizationCounterType.FINE_GRAIN_GFX_ACTIVITY, PASS),
        ('FINE_GRAIN_MEM_ACTIVITY', amdsmi.AmdSmiUtilizationCounterType.FINE_GRAIN_MEM_ACTIVITY, PASS),
        ('FINE_DECODER_ACTIVITY', amdsmi.AmdSmiUtilizationCounterType.FINE_DECODER_ACTIVITY, PASS),
        ('UTILIZATION_COUNTER_FIRST', amdsmi.AmdSmiUtilizationCounterType.UTILIZATION_COUNTER_FIRST, PASS),
        ('UTILIZATION_COUNTER_LAST', amdsmi.AmdSmiUtilizationCounterType.UTILIZATION_COUNTER_LAST, PASS),
        ('UTILIZATION_COUNTER_BAD', 100, FAIL)
    ]

    event_groups = \
    [
        ('XGMI', amdsmi.AmdSmiEventGroup.XGMI, PASS),
        ('XGMI_DATA_OUT', amdsmi.AmdSmiEventGroup.XGMI_DATA_OUT, PASS),
        ('GRP_INVALID', amdsmi.AmdSmiEventGroup.GRP_INVALID, FAIL)
    ]

    event_types = \
    [
        ('XGMI_0_NOP_TX', amdsmi.AmdSmiEventType.XGMI_0_NOP_TX, PASS),
        ('XGMI_0_REQUEST_TX', amdsmi.AmdSmiEventType.XGMI_0_REQUEST_TX, PASS),
        ('XGMI_0_RESPONSE_TX', amdsmi.AmdSmiEventType.XGMI_0_RESPONSE_TX, PASS),
        ('XGMI_0_BEATS_TX', amdsmi.AmdSmiEventType.XGMI_0_BEATS_TX, PASS),
        ('XGMI_1_NOP_TX', amdsmi.AmdSmiEventType.XGMI_1_NOP_TX, PASS),
        ('XGMI_1_REQUEST_TX', amdsmi.AmdSmiEventType.XGMI_1_REQUEST_TX, PASS),
        ('XGMI_1_RESPONSE_TX', amdsmi.AmdSmiEventType.XGMI_1_RESPONSE_TX, PASS),
        ('XGMI_1_BEATS_TX', amdsmi.AmdSmiEventType.XGMI_1_BEATS_TX, PASS),
        ('XGMI_DATA_OUT_0', amdsmi.AmdSmiEventType.XGMI_DATA_OUT_0, PASS),
        ('XGMI_DATA_OUT_1', amdsmi.AmdSmiEventType.XGMI_DATA_OUT_1, PASS),
        ('XGMI_DATA_OUT_2', amdsmi.AmdSmiEventType.XGMI_DATA_OUT_2, PASS),
        ('XGMI_DATA_OUT_3', amdsmi.AmdSmiEventType.XGMI_DATA_OUT_3, PASS),
        ('XGMI_DATA_OUT_4', amdsmi.AmdSmiEventType.XGMI_DATA_OUT_4, PASS),
        ('XGMI_DATA_OUT_5', amdsmi.AmdSmiEventType.XGMI_DATA_OUT_5, PASS)
    ]

    counter_commands = \
    [
        ('CMD_START', amdsmi.AmdSmiCounterCommand.CMD_START, PASS),
        ('CMD_STOP', amdsmi.AmdSmiCounterCommand.CMD_STOP, PASS)
    ]

    compute_partition_types = \
    [
        ('SPX', amdsmi.AmdSmiComputePartitionType.SPX, PASS),
        ('DPX', amdsmi.AmdSmiComputePartitionType.DPX, PASS),
        ('TPX', amdsmi.AmdSmiComputePartitionType.TPX, PASS),
        ('QPX', amdsmi.AmdSmiComputePartitionType.QPX, PASS),
        ('CPX', amdsmi.AmdSmiComputePartitionType.CPX, PASS),
        ('INVALID', amdsmi.AmdSmiComputePartitionType.INVALID, FAIL)
    ]

    memory_partition_types = \
    [
        ('NPS1', amdsmi.AmdSmiMemoryPartitionType.NPS1, PASS),
        ('NPS2', amdsmi.AmdSmiMemoryPartitionType.NPS2, PASS),
        ('NPS4', amdsmi.AmdSmiMemoryPartitionType.NPS4, PASS),
        ('NPS8', amdsmi.AmdSmiMemoryPartitionType.NPS8, PASS),
        ('UNKNOWN', amdsmi.AmdSmiMemoryPartitionType.UNKNOWN, FAIL)
    ]

    freq_inds = \
    [
        ('MIN', amdsmi.AmdSmiFreqInd.MIN, PASS),
        ('MAX', amdsmi.AmdSmiFreqInd.MAX, PASS),
        ('INVALID', amdsmi.AmdSmiFreqInd.INVALID, FAIL)
    ]

    power_profile_preset_masks = \
    [
        ('CUSTOM_MASK', amdsmi.AmdSmiPowerProfilePresetMasks.CUSTOM_MASK, PASS),
        ('VIDEO_MASK', amdsmi.AmdSmiPowerProfilePresetMasks.VIDEO_MASK, PASS),
        ('POWER_SAVING_MASK', amdsmi.AmdSmiPowerProfilePresetMasks.POWER_SAVING_MASK, PASS),
        ('COMPUTE_MASK', amdsmi.AmdSmiPowerProfilePresetMasks.COMPUTE_MASK, PASS),
        ('VR_MASK', amdsmi.AmdSmiPowerProfilePresetMasks.VR_MASK, PASS),
        ('THREE_D_FULL_SCR_MASK', amdsmi.AmdSmiPowerProfilePresetMasks.THREE_D_FULL_SCR_MASK, PASS),
        ('BOOTUP_DEFAULT', amdsmi.AmdSmiPowerProfilePresetMasks.BOOTUP_DEFAULT, PASS)
    ]

    def _print(self, msg, data=None):
        if verbose == 2:
            if data is None:
                print(msg, flush=True)
            elif any(data in value for value in not_supported_error_codes):
                print(f'{msg} {data}', flush=True)
            else:
                if isinstance(data, str) and data in error_map.values():
                    print(msg, end='')
                else:
                    print(msg)
                if isinstance(data, str) or isinstance(data, int):
                    print(data)
                else:
                    print(json.dumps(data, sort_keys=False, indent=4), flush=True)
        return

    def _print_func_name(self, msg=None):
        if verbose == 2:
            stk = inspect.stack()
            if stk[1].function == '_callSetUp':
                return
            print(f'\n## {stk[1].function}()', flush=True)
            if msg:
                print(msg, flush=True)
        return

    def get_error_code(self, e):
        error_code = e.get_error_code()
        return error_map[error_code]

    def _check_ret(self, msg, _e, expected_code=None, printit=True):
        if hasattr(_e, 'get_error_code'):
            error_code_int = int(_e.get_error_code())
            error_code = str(error_code_int)
            if error_code in error_map:
                error_code_name = error_map[error_code]
            else:
                error_code_name = 'UNKNOWN_ERROR'
        else:
            error_code = str(_e).split(':')[0]
            error_code_name = 'AMDSMI_STATUS_INVAL'

        # Check for when there are multiple passing conditions
        if isinstance(expected_code, list):
            for ec in expected_code:
                rc = self._check_ret(msg, _e, ec, False)  # Do not print msg, otherwise multiple msgs printed
                if not rc:
                    rc = self._check_ret(msg, _e, ec) # Call check again so msg is printed
                    return rc

            # No expected results found
            print(f'{msg}\nTest FAILED with expected results {expected_code} but received {error_code_name}', flush=True)
            return True

        # Check for single passing condition
        if any(error_code in value for value in not_supported_error_codes):
            if verbose == 2 and printit:
                print(f'{msg}\nTest SKIPPED with result {error_code_name}', flush=True)
        elif error_code_name == expected_code:
            if verbose == 2 and printit:
                print(f'{msg}\nTest PASSED with expected result {expected_code}', flush=True)
        else:
            if verbose == 2 and printit:
                print(f'{msg}\nTest FAILED with expected result {expected_code} but received {error_code_name}', flush=True)
            return True
        return False

    def setUp(self):
        # Called before each test by unittest framework
        self.raise_exception = None
        amdsmi.amdsmi_init()
        self.processors = amdsmi.amdsmi_get_processor_handles()
        self.assertGreaterEqual(len(self.processors), 1)
        self.assertLessEqual(len(self.processors), self.max_num_physical_devices)
        return

    def tearDown(self):
        # Called after each test by unittest framework
        amdsmi.amdsmi_shut_down()
        return

    def RunFunc0(self, **kwargs):
        '''
            Arguments:
            func_name=func
        '''
        iterator = iter(kwargs.items())
        func_name, func = next(iterator)
        param1_name, param1_value = next(iterator, (None, None))

        if not param1_name:
            msg = f'### {func_name}()'
        else:
            msg = f'### {func_name}({param1_name}={param1_value})'
        try:
            if param1_name:
                data = func(param1_value)
            else:
                data = func()
            self._print(msg, data)
        except (amdsmi.AmdSmiLibraryException, amdsmi.AmdSmiParameterException) as e:
            if self._check_ret(msg, e, self.PASS):
                self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    def RunFunc1(self, **kwargs):
        '''
            Arguments:
                func_name=func
            Optional:
                param1_name=param1_value
                param2_name=param2_value
                param3_name=param3_value
        '''
        iterator = iter(kwargs.items())
        func_name, func = next(iterator)
        param1_name, param1_value = next(iterator, (None, None))
        param2_name = None
        param3_name = None
        if param1_name:
            param2_name, param2_value = next(iterator, (None, None))
            if param2_name:
                param3_name, param3_value = next(iterator, (None, None))

        for i, gpu in enumerate(self.processors):
            if param3_name:
                msg = f'### {func_name}(gpu={i}, {param1_name}={param1_value}, {param2_name}={param2_value}, {param3_name}={param3_value})'
            elif param2_name:
                msg = f'### {func_name}(gpu={i}, {param1_name}={param1_value}, {param2_name}={param2_value})'
            elif param1_name:
                msg = f'### {func_name}(gpu={i}, {param1_name}={param1_value})'
            else:
                msg = f'### {func_name}(gpu={i})'
            try:
                if param3_name:
                    data = func(gpu, param1_value, param2_value, param3_value)
                elif param2_name:
                    data = func(gpu, param1_value, param2_value)
                elif param1_name:
                    data = func(gpu, param1_value)
                else:
                    data = func(gpu)
                self._print(msg, data)
            except (amdsmi.AmdSmiLibraryException, amdsmi.AmdSmiParameterException) as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    def RunFunc2(self, **kwargs):
        '''
            Arguments:
                func_name=func
                value1_name=[(value_name, value, value_cond), ...]
            Optional:
                param1_name=param1_value
                param2_name=param2_value
        '''
        iterator = iter(kwargs.items())
        func_name, func = next(iterator)
        name1, values1 = next(iterator, (None, None))
        param1_name, param1_value = next(iterator, (None, None))
        if param1_name:
            param2_name, param2_value = next(iterator, (None, None))
        else:
            param2_name = None

        for i, gpu in enumerate(self.processors):
            for value1_name, value1, value1_cond in values1:
                if param2_name:
                    msg = f'### {func_name}(gpu={i}, {name1}={value1_name}, {param1_name}={param1_name}, {param2_name}={param2_name})'
                elif param1_name:
                    msg = f'### {func_name}(gpu={i}, {name1}={value1_name}, {param1_name}={param1_name})'
                else:
                    msg = f'### {func_name}(gpu={i}, {name1}={value1_name})'
                try:
                    if param2_name:
                        data = func(gpu, value1, param1_value, param2_value)
                    elif param1_name:
                        data = func(gpu, value1, param1_value)
                    else:
                        data = func(gpu, value1)
                    self._print(msg, data)
                except (amdsmi.AmdSmiLibraryException, amdsmi.AmdSmiParameterException) as e:
                    if not value1_cond == self.PASS:
                        if self._check_ret(msg, e, value1_cond):
                            self.raise_exception = e
                    else:
                        if self._check_ret(msg, e, self.PASS):
                            self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return


    def RunFunc3(self, **kwargs):
        '''
            Arguments:
                func_name=func
                value1_name=[(value_name value, value_cond), ...]
                value2_name=[(value_name, value, value_cond), ...]
            Optional:
                param1_name=param1_value
                param2_name=param2_value
        '''
        iterator = iter(kwargs.items())
        func_name, func = next(iterator)
        name1, values1 = next(iterator, (None, None))
        name2, values2 = next(iterator, (None, None))
        param1_name, param1_value = next(iterator, (None, None))
        if param1_name:
            param2_name, param2_value = next(iterator, (None, None))
        else:
            param2_name = None

        for i, gpu in enumerate(self.processors):
            for value1_name, value1, value1_cond in values1:
                for value2_name, value2, value2_cond in values2:
                    if param2_name:
                        msg = f'### {func_name}(gpu={i}, {name1}={value1_name}, {name2}={value2_name}, {param1_name}={param1_value}, {param2_name}={param2_value})'
                    elif param1_name:
                        msg = f'### {func_name}(gpu={i}, {name1}={value1_name}, {name2}={value2_name}, {param1_name}={param1_value})'
                    else:
                        msg = f'### {func_name}(gpu={i}, {name1}={value1_name}, {name2}={value2_name})'
                    try:
                        if param2_name:
                            data = func(gpu, value1, value2, param1_value, param2_value)
                        elif param1_name:
                            data = func(gpu, value1, value2, param1_value)
                        else:
                            data = func(gpu, value1, value2)
                        self._print(msg, data)
                    except (amdsmi.AmdSmiLibraryException, amdsmi.AmdSmiParameterException) as e:
                        if not value1_cond == self.PASS:
                            if self._check_ret(msg, e, value1_cond):
                                self.raise_exception = e
                        elif not value2_cond == self.PASS:
                            if self._check_ret(msg, e, value2_cond):
                                self.raise_exception = e
                        else:
                            if self._check_ret(msg, e, self.PASS):
                                self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    def RunFunc1Gpu(self, **kwargs):
        '''
            Arguments:
                func_name=func
            Optional:
                param1_name=param1_value
                param2_name=param2_value
        '''
        iterator = iter(kwargs.items())
        func_name, func = next(iterator)
        param1_name, param1_value = next(iterator, (None, None))
        if param1_name:
            param2_name, param2_value = next(iterator, (None, None))
        else:
            param2_name = None

        for i, gpu_i in enumerate(self.processors):
            for j, gpu_j in enumerate(self.processors):
                if param2_name:
                    msg = f'### {func_name}(gpu={i}, gpu={j}, {param1_name}={param1_value}, {param2_name}={param2_value})'
                elif param1_name:
                    msg = f'### {func_name}(gpu={i}, gpu={j}, {param1_name}={param1_value})'
                else:
                    msg = f'### {func_name}(gpu={i}, gpu={j})'
                try:
                    if param2_name:
                        data = func(gpu_i, gpu_j, param1_value, param2_value)
                    elif param1_name:
                        data = func(gpu_i, gpu_j, param1_value)
                    else:
                        data = func(gpu_i, gpu_j)
                    self._print(msg, data)
                except (amdsmi.AmdSmiLibraryException, amdsmi.AmdSmiParameterException) as e:
                    if i == j:
                        if self._check_ret(msg, e, self.FAIL):
                            self.raise_exception = e
                    else:
                        if self._check_ret(msg, e, self.PASS):
                            self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    def test_clean_gpu_local_data(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_clean_gpu_local_data=amdsmi.amdsmi_clean_gpu_local_data)
        return

    def test_cpu_apb_disable(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_cpu_apb_disable=amdsmi.amdsmi_cpu_apb_disable, pstate=0)
        return

    def test_cpu_apb_enable(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_cpu_apb_enable=amdsmi.amdsmi_cpu_apb_enable)
        return

    def test_first_online_core_on_cpu_socket(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_first_online_core_on_cpu_socket as it fails (IO Error).")
        self.RunFunc1(amdsmi_first_online_core_on_cpu_socket=amdsmi.amdsmi_first_online_core_on_cpu_socket)
        return

    def test_get_clk_freq(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_clk_freq as it fails (MI350X, AMDSMI_STATUS_UNEXPECTED_DATA).")
        self.RunFunc1(amdsmi_get_clk_freq=amdsmi.amdsmi_get_clk_freq)
        return

    def test_get_clock_info(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_clock_info as it fails (MI350X, AMDSMI_STATUS_UNEXPECTED_DATA).")
        self.RunFunc1(amdsmi_get_clock_info=amdsmi.amdsmi_get_clock_info)
        return

    def test_get_cpu_cclk_limit(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_cpu_cclk_limit=amdsmi.amdsmi_get_cpu_cclk_limit)
        return

    def test_get_cpu_core_current_freq_limit(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_cpu_core_current_freq_limit=amdsmi.amdsmi_get_cpu_core_current_freq_limit)
        return

    def test_get_cpu_core_energy(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_cpu_core_energy as it fails (IO Error).")
        self.RunFunc1(amdsmi_get_cpu_core_energy=amdsmi.amdsmi_get_cpu_core_energy)
        return

    # no gpu but have list
    def test_get_cpu_current_io_bandwidth(self):
        self._print_func_name('')
        for i, gpu in enumerate(self.processors):
            for encoding_name, encoding, encoding_cond in self.io_bw_encodings:
                msg = f'### amdsmi_get_cpu_current_io_bandwidth(gpu={i}, encoding={encoding} encoding_name={encoding_name}):'
                try:
                    ret = amdsmi.amdsmi_get_cpu_current_io_bandwidth(gpu, encoding, encoding_name)
                    self._print(msg, ret)
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, encoding_cond):
                        self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    def test_get_cpu_ddr_bw(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_cpu_ddr_bw=amdsmi.amdsmi_get_cpu_ddr_bw)
        return

    def test_get_cpu_dimm_power_consumption(self):
        self._print_func_name('')
        # TODO Find better way to get dimm_addr
        dimm_addr = 0
        self.RunFunc1(amdsmi_get_cpu_dimm_power_consumption=amdsmi.amdsmi_get_cpu_dimm_power_consumption, dimm_addr=dimm_addr)
        return

    def test_get_cpu_dimm_temp_range_and_refresh_rate(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_cpu_dimm_temp_range_and_refresh_rate as it fails.")
        # TODO Find better way to get dimm_addr
        dimm_addr = 0
        self.RunFunc1(amdsmi_get_cpu_dimm_temp_range_and_refresh_rate=amdsmi.amdsmi_get_cpu_dimm_temp_range_and_refresh_rate, dimm_addr=dimm_addr)
        return

    def test_get_cpu_dimm_thermal_sensor(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_cpu_dimm_thermal_sensor as it fails.")
        # TODO Find better way to get dimm_addr
        dimm_addr = 0
        self.RunFunc1(amdsmi_get_cpu_dimm_thermal_sensor=amdsmi.amdsmi_get_cpu_dimm_thermal_sensor, dimm_addr=dimm_addr)
        return

    def test_get_cpu_family(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_cpu_family as it fails (IO Error).")
        self.RunFunc0(amdsmi_get_cpu_family=amdsmi.amdsmi_get_cpu_family)
        return

    def test_get_cpu_fclk_mclk(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_cpu_fclk_mclk=amdsmi.amdsmi_get_cpu_fclk_mclk)
        return

    def test_get_cpu_handles(self):
        self._print_func_name('')
        self.RunFunc0(amdsmi_get_cpu_handles=amdsmi.amdsmi_get_cpu_handles)
        return

    def test_get_cpu_hsmp_driver_version(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_cpu_hsmp_driver_version as it fails (IO Error).")
        self.RunFunc1(amdsmi_get_cpu_hsmp_driver_version=amdsmi.amdsmi_get_cpu_hsmp_driver_version)
        return

    def test_get_cpu_hsmp_proto_ver(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_cpu_hsmp_proto_ver as it fails (IO Error).")
        self.RunFunc1(amdsmi_get_cpu_hsmp_proto_ver=amdsmi.amdsmi_get_cpu_hsmp_proto_ver)
        return

    def test_get_cpu_model(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_cpu_model as it fails (IO Error).")
        self.RunFunc0(amdsmi_get_cpu_model=amdsmi.amdsmi_get_cpu_model)
        return

    def test_get_cpu_prochot_status(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_cpu_prochot_status=amdsmi.amdsmi_get_cpu_prochot_status)
        return

    def test_get_cpu_pwr_svi_telemetry_all_rails(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_cpu_pwr_svi_telemetry_all_rails=amdsmi.amdsmi_get_cpu_pwr_svi_telemetry_all_rails)
        return

    def test_get_cpu_smu_fw_version(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_cpu_smu_fw_version=amdsmi.amdsmi_get_cpu_smu_fw_version)
        return

    def test_get_cpu_socket_c0_residency(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_cpu_socket_c0_residency=amdsmi.amdsmi_get_cpu_socket_c0_residency)
        return

    def test_get_cpu_socket_current_active_freq_limit(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_cpu_socket_current_active_freq_limit=amdsmi.amdsmi_get_cpu_socket_current_active_freq_limit)
        return

    def test_get_cpu_socket_energy(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_cpu_socket_energy as it fails (IO Error).")
        self.RunFunc1(amdsmi_get_cpu_socket_energy=amdsmi.amdsmi_get_cpu_socket_energy)
        return

    def test_get_cpu_socket_freq_range(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_cpu_socket_freq_range=amdsmi.amdsmi_get_cpu_socket_freq_range)
        return

    def test_get_cpu_socket_lclk_dpm_level(self):
        self._print_func_name('')
        # TODO nbio_id = 0
        nbio_id = 0
        self.RunFunc1(amdsmi_get_cpu_socket_lclk_dpm_level=amdsmi.amdsmi_get_cpu_socket_lclk_dpm_level, nbio_id=nbio_id)
        return

    def test_get_cpu_socket_power(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_cpu_socket_power=amdsmi.amdsmi_get_cpu_socket_power)
        return

    def test_get_cpu_socket_power_cap(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_cpu_socket_power_cap=amdsmi.amdsmi_get_cpu_socket_power_cap)
        return

    def test_get_cpu_socket_power_cap_max(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_cpu_socket_power_cap_max=amdsmi.amdsmi_get_cpu_socket_power_cap_max)
        return

    def test_get_cpu_socket_temperature(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_cpu_socket_temperature=amdsmi.amdsmi_get_cpu_socket_temperature)
        return

    def test_get_energy_count(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_energy_count as it fails (MI350X, AMDSMI_STATUS_UNEXPECTED_DATA).")
        self.RunFunc1(amdsmi_get_energy_count=amdsmi.amdsmi_get_energy_count)
        return

    # no gpu but have list
    def test_get_esmi_err_msg(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_esmi_err_msg as it fails (Unknown Error).")
        for status_type_name, status_type, status_cond in self.status_types:
            msg = f'### amdsmi_get_esmi_err_msg(status_type={status_type}):'
            try:
                ret = amdsmi.amdsmi_get_esmi_err_msg(status_type)
                self._print(msg, ret)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, status_cond):
                    self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    def test_get_fw_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_fw_info=amdsmi.amdsmi_get_fw_info)
        return

    def test_get_gpu_accelerator_partition_profile(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_accelerator_partition_profile=amdsmi.amdsmi_get_gpu_accelerator_partition_profile)
        return

    def test_get_gpu_accelerator_partition_profile_config(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_accelerator_partition_profile_config=amdsmi.amdsmi_get_gpu_accelerator_partition_profile_config)
        return

    def test_get_gpu_activity(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_gpu_activity as it fails (MI350X, AMDSMI_STATUS_UNEXPECTED_DATA).")
        self.RunFunc1(amdsmi_get_gpu_activity=amdsmi.amdsmi_get_gpu_activity)
        return

    def test_get_gpu_asic_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_asic_info=amdsmi.amdsmi_get_gpu_asic_info)
        return

    def test_get_gpu_bad_page_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_bad_page_info=amdsmi.amdsmi_get_gpu_bad_page_info)
        return

    def test_get_gpu_bad_page_threshold(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_bad_page_threshold=amdsmi.amdsmi_get_gpu_bad_page_threshold)
        return

    def test_get_gpu_bad_page_threshold(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_bad_page_threshold=amdsmi.amdsmi_get_gpu_bad_page_threshold)
        return

    def test_get_gpu_bdf_id(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_bdf_id=amdsmi.amdsmi_get_gpu_bdf_id)
        return

    def test_get_gpu_board_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_board_info=amdsmi.amdsmi_get_gpu_board_info)
        return

    def test_get_gpu_cache_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_cache_info=amdsmi.amdsmi_get_gpu_cache_info)
        return

    def test_get_gpu_compute_partition(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_compute_partition=amdsmi.amdsmi_get_gpu_compute_partition)
        return

    def test_get_gpu_compute_process_gpus(self):
        self._print_func_name('')
        if self.TODO_SKIP_NOT_COMPLETE:
            self.skipTest("Skipping test_get_gpu_compute_process_gpus as it is not complete (Inval Error).")
        self.RunFunc1(amdsmi_get_gpu_compute_process_gpus=amdsmi.amdsmi_get_gpu_compute_process_gpus)
        return

    def test_get_gpu_compute_process_info(self):
        self._print_func_name('')
        self.RunFunc0(amdsmi_get_gpu_compute_process_info=amdsmi.amdsmi_get_gpu_compute_process_info)
        return

    def test_get_gpu_compute_process_info_by_pid(self):
        self._print_func_name('')
        if self.TODO_SKIP_NOT_COMPLETE:
            self.skipTest("Skipping test_get_gpu_compute_process_info_by_pid as it not complete (Device not found).")
        #TODO pid = 0
        pid = 0
        self.RunFunc0(amdsmi_get_gpu_compute_process_info_by_pid=amdsmi.amdsmi_get_gpu_compute_process_info_by_pid, pid=pid)
        return

    def test_get_gpu_device_bdf(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_device_bdf=amdsmi.amdsmi_get_gpu_device_bdf)
        return

    def test_get_gpu_device_uuid(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_device_uuid=amdsmi.amdsmi_get_gpu_device_uuid)
        return

    def test_get_gpu_driver_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_driver_info=amdsmi.amdsmi_get_gpu_driver_info)
        return

    def test_get_gpu_ecc_count(self):
        self._print_func_name('')
        self.RunFunc2(amdsmi_get_gpu_ecc_count=amdsmi.amdsmi_get_gpu_ecc_count, gpu_block=self.gpu_blocks)
        return

    def test_get_gpu_ecc_enabled(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_ecc_enabled=amdsmi.amdsmi_get_gpu_ecc_enabled)
        return

    def test_get_gpu_ecc_status(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_gpu_ecc_status as it fails.")
        self.RunFunc2(amdsmi_get_gpu_ecc_status=amdsmi.amdsmi_get_gpu_ecc_status, gpu_block=self.gpu_blocks)
        return

    def test_get_gpu_enumeration_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_enumeration_info=amdsmi.amdsmi_get_gpu_enumeration_info)
        return

    def test_get_gpu_fan_rpms(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_fan_rpms=amdsmi.amdsmi_get_gpu_fan_rpms, index=0)
        return

    def test_get_gpu_id(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_id=amdsmi.amdsmi_get_gpu_id)
        return

    def test_get_gpu_kfd_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_kfd_info=amdsmi.amdsmi_get_gpu_kfd_info)
        return

    def test_get_gpu_mem_overdrive_level(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_mem_overdrive_level=amdsmi.amdsmi_get_gpu_mem_overdrive_level)
        return

    def test_get_gpu_memory_partition(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_memory_partition=amdsmi.amdsmi_get_gpu_memory_partition)
        return

    def test_get_gpu_memory_partition_config(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_gpu_memory_partition_config as it fails on MI300.")
        self.RunFunc1(amdsmi_get_gpu_memory_partition_config=amdsmi.amdsmi_get_gpu_memory_partition_config)
        return

    def test_get_gpu_memory_reserved_pages(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_memory_reserved_pages=amdsmi.amdsmi_get_gpu_memory_reserved_pages)
        return

    def test_get_gpu_memory_total(self):
        self._print_func_name('')
        self.RunFunc2(amdsmi_get_gpu_memory_total=amdsmi.amdsmi_get_gpu_memory_total, memory_type=self.memory_types)
        return

    def test_get_gpu_memory_usage(self):
        self._print_func_name('')
        self.RunFunc2(amdsmi_get_gpu_memory_usage=amdsmi.amdsmi_get_gpu_memory_usage, memory_type=self.memory_types)
        return

    def test_get_gpu_metrics_header_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_metrics_header_info=amdsmi.amdsmi_get_gpu_metrics_header_info)
        return

    def test_get_gpu_metrics_info(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_gpu_metrics_info as it fails (MI350X, AMDSMI_STATUS_UNEXPECTED_DATA).")
        self.RunFunc1(amdsmi_get_gpu_metrics_info=amdsmi.amdsmi_get_gpu_metrics_info)
        return

    def test_get_gpu_od_volt_curve_regions(self):
        self._print_func_name('')
        #TODO num_region = 10
        num_region = 10
        self.RunFunc1(amdsmi_get_gpu_od_volt_curve_regions=amdsmi.amdsmi_get_gpu_od_volt_curve_regions, num_region=num_region)
        return

    def test_get_gpu_od_volt_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_od_volt_info=amdsmi.amdsmi_get_gpu_od_volt_info)
        return

    def test_get_gpu_overdrive_level(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_overdrive_level=amdsmi.amdsmi_get_gpu_overdrive_level)
        return

    def test_get_gpu_pci_bandwidth(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_gpu_pci_bandwidth as it fails (MI350X, AMDSMI_STATUS_UNEXPECTED_DATA).")
        self.RunFunc1(amdsmi_get_gpu_pci_bandwidth=amdsmi.amdsmi_get_gpu_pci_bandwidth)
        return

    def test_get_gpu_pci_replay_counter(self):
        self._print_func_name('')
        # TODO Check test_get_gpu_pci_replay_counter
        self.RunFunc1(amdsmi_get_gpu_pci_replay_counter=amdsmi.amdsmi_get_gpu_pci_replay_counter)
        return

    def test_get_gpu_pci_replay_counter(self):
        self._print_func_name('')
        # TODO Check test_get_gpu_pci_replay_counter
        self.RunFunc1(amdsmi_get_gpu_pci_replay_counter=amdsmi.amdsmi_get_gpu_pci_replay_counter)
        return

    def test_get_gpu_pci_throughput(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_pci_throughput=amdsmi.amdsmi_get_gpu_pci_throughput)
        return

    def test_get_gpu_perf_level(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_perf_level=amdsmi.amdsmi_get_gpu_perf_level)
        return

    def test_get_gpu_pm_metrics_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_pm_metrics_info=amdsmi.amdsmi_get_gpu_pm_metrics_info)
        return

    def test_get_gpu_power_profile_presets(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_power_profile_presets=amdsmi.amdsmi_get_gpu_power_profile_presets, index=0)
        return

    def test_get_gpu_process_isolation(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_process_isolation=amdsmi.amdsmi_get_gpu_process_isolation)
        return

    def test_get_gpu_process_list(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_process_list=amdsmi.amdsmi_get_gpu_process_list)
        return

    def test_get_gpu_ras_block_features_enabled(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_ras_block_features_enabled=amdsmi.amdsmi_get_gpu_ras_block_features_enabled)
        return

    def test_get_gpu_ras_feature_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_ras_feature_info=amdsmi.amdsmi_get_gpu_ras_feature_info)
        return

    def test_get_gpu_reg_table_info(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_gpu_reg_table_info as it fails on MI300.")
        self.RunFunc2(amdsmi_get_gpu_reg_table_info=amdsmi.amdsmi_get_gpu_reg_table_info, reg_type=self.reg_types)
        return

    def test_get_gpu_revision(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_revision=amdsmi.amdsmi_get_gpu_revision)
        return

    def test_get_gpu_subsystem_id(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_subsystem_id=amdsmi.amdsmi_get_gpu_subsystem_id)
        return

    def test_get_gpu_subsystem_name(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_subsystem_name=amdsmi.amdsmi_get_gpu_subsystem_name)
        return

    def test_get_gpu_topo_numa_affinity(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_topo_numa_affinity=amdsmi.amdsmi_get_gpu_topo_numa_affinity)
        return

    def test_get_gpu_total_ecc_count(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_total_ecc_count=amdsmi.amdsmi_get_gpu_total_ecc_count)
        return

    def test_get_gpu_vbios_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_vbios_info=amdsmi.amdsmi_get_gpu_vbios_info)
        return

    def test_get_gpu_vendor_name(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_vendor_name=amdsmi.amdsmi_get_gpu_vendor_name)
        return

    def test_get_gpu_virtualization_mode(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_virtualization_mode=amdsmi.amdsmi_get_gpu_virtualization_mode)
        return

    def test_get_gpu_volt_metric(self):
        self._print_func_name('')
        self.RunFunc3(amdsmi_get_gpu_volt_metric=amdsmi.amdsmi_get_gpu_volt_metric,
                      voltage_type=self.voltage_types,
                      voltage_metric=self.voltage_metrics)
        return

    def test_get_gpu_vram_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_vram_info=amdsmi.amdsmi_get_gpu_vram_info)
        return

    def test_get_gpu_vram_usage(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_vram_usage=amdsmi.amdsmi_get_gpu_vram_usage)
        return

    def test_get_gpu_vram_vendor(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_vram_vendor=amdsmi.amdsmi_get_gpu_vram_vendor)
        return

    def test_get_gpu_xcd_counter(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_gpu_xcd_counter as it fails (MI350, AMDSMI_STATUS_UNEXPECTED_DATA).")
        self.RunFunc1(amdsmi_get_gpu_xcd_counter=amdsmi.amdsmi_get_gpu_xcd_counter)
        return

    def test_get_gpu_xgmi_link_status(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_gpu_xgmi_link_status as it fails (MI350, AMDSMI_STATUS_UNEXPECTED_DATA).")
        self.RunFunc1(amdsmi_get_gpu_xgmi_link_status=amdsmi.amdsmi_get_gpu_xgmi_link_status)
        return

    def test_get_hsmp_metrics_table(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_hsmp_metrics_table=amdsmi.amdsmi_get_hsmp_metrics_table)
        return

    def test_get_hsmp_metrics_table_version(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_hsmp_metrics_table_version=amdsmi.amdsmi_get_hsmp_metrics_table_version)
        return

    def test_get_lib_version(self):
        self._print_func_name('')
        self.RunFunc0(amdsmi_get_lib_version=amdsmi.amdsmi_get_lib_version)
        return

    def test_get_link_metrics(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_link_metrics as it fails (MI350X, AMDSMI_STATUS_UNEXPECTED_DATA).")
        self.RunFunc1(amdsmi_get_link_metrics=amdsmi.amdsmi_get_link_metrics)
        return

    def test_get_link_topology_nearest(self):
        self._print_func_name('')
        self.RunFunc2(amdsmi_get_link_topology_nearest=amdsmi.amdsmi_get_link_topology_nearest, link_type=self.link_types)
        return

    def test_get_minmax_bandwidth_between_processors(self):
        self._print_func_name('')
        self.RunFunc1Gpu(amdsmi_get_minmax_bandwidth_between_processors=amdsmi.amdsmi_get_minmax_bandwidth_between_processors)
        return

    def test_get_pcie_info(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_pcie_info as it fails (MI350X, AMDSMI_STATUS_UNEXPECTED_DATA).")
        self.RunFunc1(amdsmi_get_pcie_info=amdsmi.amdsmi_get_pcie_info)
        return

    def test_set_cpu_pcie_link_rate(self):
        self._print_func_name('')
        if self.TODO_SKIP_NOT_COMPLETE:
            self.skipTest("Skipping test_set_cpu_pcie_link_rate as it is not complete.")
        # TODO rate_ctrl = 0
        rate_ctrl = 0
        self.RunFunc1(amdsmi_set_cpu_pcie_link_rate=amdsmi.amdsmi_set_cpu_pcie_link_rate, rate_ctrl=rate_ctrl)
        return

    def test_get_power_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_power_info=amdsmi.amdsmi_get_power_info)
        return

    def test_get_power_cap_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_power_cap_info=amdsmi.amdsmi_get_power_cap_info)
        return

    def test_get_processor_count_from_handles(self):
        self._print_func_name('')
        self.RunFunc0(amdsmi_get_processor_count_from_handles=amdsmi.amdsmi_get_processor_count_from_handles, processors=self.processors)
        return

    # print data issues
    def test_get_processor_handles(self):
        self._print_func_name('')
        msg = f'### amdsmi_get_processor_handles():'
        try:
            procs = amdsmi.amdsmi_get_processor_handles()
            self._print(msg, [id(addr) for addr in procs])
        except amdsmi.AmdSmiLibraryException as e:
            if self._check_ret(msg, e, self.PASS):
                self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    def test_get_processor_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_processor_info=amdsmi.amdsmi_get_processor_info)
        return

    def test_get_processor_type(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_processor_type=amdsmi.amdsmi_get_processor_type)
        return

    # data print issues
    def test_get_socket_handles(self):
        self._print_func_name('')
        msg = f'### amdsmi_get_socket_handles():'
        try:
            ret = amdsmi.amdsmi_get_socket_handles()
            self._print(msg, [id(addr) for addr in ret])
        except amdsmi.AmdSmiLibraryException as e:
            if self._check_ret(msg, e, self.PASS):
                self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    def test_get_temp_metric(self):
        self._print_func_name('')
        self.RunFunc3(amdsmi_get_temp_metric=amdsmi.amdsmi_get_temp_metric,
                      temperature_type=self.temperature_types,
                      temperature_metric=self.temperature_metrics)
        return

    def test_get_threads_per_core(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_threads_per_core as it fails (IO Error).")
        self.RunFunc0(amdsmi_get_threads_per_core=amdsmi.amdsmi_get_threads_per_core)
        return

    def test_get_utilization_count(self):
        self._print_func_name('')
        if False:
            if self.TODO_SKIP_FAIL:
                self.skipTest("Skipping test_get_utilization_count as it fails (MI350X, AMDSMI_STATUS_UNEXPECTED_DATA).")
        self.RunFunc2(amdsmi_get_utilization_count=amdsmi.amdsmi_get_utilization_count, utilization_counter_type=self.utilization_counter_types)
        return

    def test_get_violation_status(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_get_violation_status as it fails (MI350X, AMDSMI_STATUS_UNEXPECTED_DATA).")
        self.RunFunc1(amdsmi_get_violation_status=amdsmi.amdsmi_get_violation_status)
        return

    def test_get_xgmi_info(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_xgmi_info=amdsmi.amdsmi_get_xgmi_info)
        return

    def test_gpu_counter_group_supported(self):
        self._print_func_name('')
        self.RunFunc2(amdsmi_gpu_counter_group_supported=amdsmi.amdsmi_gpu_counter_group_supported, event_group=self.event_groups)
        return

    def test_get_gpu_available_counters(self):
        self._print_func_name('')
        self.RunFunc2(amdsmi_get_gpu_available_counters=amdsmi.amdsmi_get_gpu_available_counters, event_group=self.event_groups)
        return

    def test_gpu_validate_ras_eeprom(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_gpu_validate_ras_eepromas it fails (File Error).")
        self.RunFunc1(amdsmi_gpu_validate_ras_eeprom=amdsmi.amdsmi_gpu_validate_ras_eeprom)
        return

    def test_gpu_xgmi_error_status(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_gpu_xgmi_error_status as it fails on MI300.")
        self.RunFunc1(amdsmi_gpu_xgmi_error_status=amdsmi.amdsmi_gpu_xgmi_error_status)
        return

    def test_init(self):
        self._print_func_name('')
        self.RunFunc0(amdsmi_init=amdsmi.amdsmi_init)
        return

    def test_shut_down(self):
        self._print_func_name('')
        self.RunFunc0(amdsmi_shut_down=amdsmi.amdsmi_shut_down)
        return

    def test_is_P2P_accessible(self):
        self._print_func_name('')
        self.RunFunc1Gpu(amdsmi_is_P2P_accessible=amdsmi.amdsmi_is_P2P_accessible)
        return


    def test_is_gpu_power_management_enabled(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_is_gpu_power_management_enabled=amdsmi.amdsmi_is_gpu_power_management_enabled)
        return

    def test_reset_gpu(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_reset_gpu as it fails (MI350X, Hang).")
        self.RunFunc1(amdsmi_reset_gpu=amdsmi.amdsmi_reset_gpu)
        return

    def test_reset_gpu_fan(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_reset_gpu_fan=amdsmi.amdsmi_reset_gpu_fan, index=0)
        return

    def test_reset_gpu_xgmi_error(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_reset_gpu_xgmi_error as it fails on MI300.")
        self.RunFunc1(amdsmi_reset_gpu_xgmi_error=amdsmi.amdsmi_reset_gpu_xgmi_error)
        return

    def test_set_cpu_df_pstate_range(self):
        self._print_func_name('')
        if self.TODO_SKIP_NOT_COMPLETE:
            self.skipTest("Skipping test_set_cpu_df_pstate_range as it is not complete.")
        # TODO max_pstate = 0, min_pstate = 0
        max_pstate = 0
        min_pstate = 0
        self.RunFunc1(amdsmi_set_cpu_df_pstate_range=amdsmi.amdsmi_set_cpu_df_pstate_range, max_pstate=max_pstate, min_pstate=min_pstate)
        return

    def test_set_cpu_gmi3_link_width_range(self):
        self._print_func_name('')
        if self.TODO_SKIP_NOT_COMPLETE:
            self.skipTest("Skipping test_set_cpu_gmi3_link_width_range as it is not complete.")
        # TODO min_link_width = 0, max_link_width = 0
        min_link_width = 0
        max_link_width = 0
        self.RunFunc1(amdsmi_set_cpu_gmi3_link_width_range=amdsmi.amdsmi_set_cpu_gmi3_link_width_range, min_link_width=min_link_width, max_link_width=max_link_width)
        return

    # param modes
    def test_set_cpu_pwr_efficiency_mode(self):
        self._print_func_name('')
        modes = [0, 1, 2]
        for i, gpu in enumerate(self.processors):
            for mode in modes:
                msg = f'### amdsmi_set_cpu_pwr_efficiency_mode(gpu={i}, mode={mode}):'
                try:
                    amdsmi.amdsmi_set_cpu_pwr_efficiency_mode(gpu, mode)
                    self._print(msg, '')
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, self.PASS):
                        self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    def test_cpu_socket_boostlimit(self):
        self._print_func_name('')
        if self.TODO_SKIP_NOT_COMPLETE:
            self.skipTest("Skipping test_cpu_socket_boostlimit as it is not complete.")
        # TODO boost_limit = 0
        boost_limit = 0
        self.RunFunc1(amdsmi_cpu_socket_boostlimit=amdsmi.amdsmi_cpu_socket_boostlimit, boost_limit=boost_limit)
        return

    def test_set_cpu_socket_lclk_dpm_level(self):
        self._print_func_name('')
        if self.TODO_SKIP_NOT_COMPLETE:
            self.skipTest("Skipping test_set_cpu_socket_lclk_dpm_level as it is not complete.")
        # TODO nbio_id = 0, min_val = 0, max_val = 0
        nbio_id = 0
        min_val = 0
        max_val = 0
        self.RunFunc1(amdsmi_set_cpu_socket_lclk_dpm_level=amdsmi.amdsmi_set_cpu_socket_lclk_dpm_level, nbio_id=nbio_id, min_val=min_val, max_val=max_val)
        return

    def test_set_cpu_xgmi_width(self):
        self._print_func_name('')
        if self.TODO_SKIP_NOT_COMPLETE:
            self.skipTest("Skipping test_set_cpu_xgmi_width as it is not complete.")
        # TODO min_width = 0, max_width = 0
        min_width = 0
        max_width = 0
        self.RunFunc1(amdsmi_set_cpu_xgmi_width=amdsmi.amdsmi_set_cpu_xgmi_width, min_width=min_width, max_width=max_width)
        return

    def test_set_gpu_accelerator_partition_profile(self):
        self._print_func_name('')
        if self.TODO_SKIP_NOT_COMPLETE:
            self.skipTest("Skipping test_set_gpu_accelerator_partition_profile as it is not complete.")
        # TODO profile_index = 0
        profile_index = 0
        self.RunFunc1(amdsmi_set_gpu_accelerator_partition_profile=amdsmi.amdsmi_set_gpu_accelerator_partition_profile, profile_index=profile_index)
        return

    # Uses clk_type_name instead of clk_type
    # Uses clk_limit_type_name instead of clk_limit_type
    def test_set_gpu_clk_limit(self):
        self._print_func_name('')
        if self.TODO_SKIP_NOT_COMPLETE:
            self.skipTest("Skipping test_set_gpu_clk_limit as it is not complete.")
        # TODO Find better way to set value
        value = 0
        for i, gpu in enumerate(self.processors):
            for clk_type_name, clk_type, clk_cond in self.clk_types:
                for clk_limit_type_name, clk_limit_type, clk_limit_cond in self.clk_limit_types:
                    msg = f'### amdsmi_set_gpu_clk_limit(gpu={i}, clk_type={clk_type_name}, clk_limit_type={clk_limit_type_name}, value={value}):'
                    try:
                        amdsmi.amdsmi_set_gpu_clk_limit(gpu, clk_type_name, clk_limit_type_name, value)
                        self._print(msg, '')
                    except amdsmi.AmdSmiLibraryException as e:
                        if not clk_cond == self.PASS:
                            self._check_ret(msg, e, clk_cond)
                            self.raise_exception = e
                        elif not clk_limit_type == self.PASS:
                            self._check_ret(msg, e, clk_limit_type)
                            self.raise_exception = e
                        else:
                            self._check_ret(msg, e, self.PASS)
                            self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    # out of order; min_clk_value, max_clk_value then clk_type
    def test_set_gpu_clk_range(self):
        self._print_func_name('')
        # TODO Find better way to set min_clk_value, max_clk_value
        min_clk_value = 100
        max_clk_value = 200
        for i, gpu in enumerate(self.processors):
            for clk_type_name, clk_type, clk_cond in self.clk_types:
                msg = f'### amdsmi_set_gpu_clk_range(gpu={i}, min_clk_value={min_clk_value}, max_clk_value={max_clk_value}, clk_type={clk_type}):'
                try:
                    amdsmi.amdsmi_set_gpu_clk_range(gpu, min_clk_value, max_clk_value, clk_type)
                    self._print(msg, '')
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, clk_cond):
                        self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    def test_set_gpu_memory_partition(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_set_gpu_memory_partition as it fails (MI350X, AMDSMI_STATUS_UNEXPECTED_DATA).")
        self.RunFunc2(amdsmi_set_gpu_memory_partition=amdsmi.amdsmi_set_gpu_memory_partition, memory_partition_type=self.memory_partition_types)
        return

    def test_set_gpu_memory_partition_mode(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_set_gpu_memory_partition_mode as it fails (MI350X, AMDSMI_STATUS_UNEXPECTED_DATA).")
        self.RunFunc1(amdsmi_set_gpu_memory_partition_mode=amdsmi.amdsmi_set_gpu_memory_partition_mode, memory_partition_type=self.memory_partition_types)
        return

    # out of order freq_ind then value then clk_type
    def test_set_gpu_od_clk_info(self):
        self._print_func_name('')
        if self.TODO_SKIP_NOT_COMPLETE:
            self.skipTest("Skipping test_set_gpu_od_clk_info as it is not complete.")
        # TODO value = 0
        value = 200
        for i, gpu in enumerate(self.processors):
            for freq_ind_name, freq_ind, freq_ind_cond in self.freq_inds:
                for clk_type_name, clk_type, clk_cond in self.clk_types:
                    msg = f'### amdsmi_set_gpu_od_clk_info(gpu={i}, freq_ind={freq_ind_name}, value={value}, clk_type={clk_type_name}):'
                    try:
                        amdsmi.amdsmi_set_gpu_od_clk_info(gpu, freq_ind, value, clk_type)
                        self._print(msg, '')
                    except amdsmi.AmdSmiLibraryException as e:
                        if not freq_ind_cond == self.PASS:
                            self._check_ret(msg, e, freq_ind_cond)
                            self.raise_exception = e
                        elif not clk_cond == self.PASS:
                            self._check_ret(msg, e, clk_cond)
                            self.raise_exception = e
                        else:
                            self._check_ret(msg, e, self.PASS)
                            self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    def test_set_gpu_od_volt_info(self):
        self._print_func_name('')
        if self.TODO_SKIP_NOT_COMPLETE:
            self.skipTest("Skipping test_set_gpu_od_volt_info as it is not complete.")
        # TODO vpoint = 0 clk_value = 0 volt_value = 0
        vpoint = 0
        clk_value = 0
        volt_value = 0
        self.RunFunc1(amdsmi_set_gpu_od_volt_info=amdsmi.amdsmi_set_gpu_od_volt_info, vpoint=vpoint, clk_value=clk_value, volt_value=volt_value)
        return

    def test_set_gpu_perf_determinism_mode(self):
        self._print_func_name('')
        if self.TODO_SKIP_NOT_COMPLETE:
            self.skipTest("Skipping test_set_gpu_perf_determinism_mode as it is not complete.")
        # TODO clk_value = 0
        clk_value = 0
        self.RunFunc1(amdsmi_set_gpu_perf_determinism_mode=amdsmi.amdsmi_set_gpu_perf_determinism_mode, clk_value=clk_value)
        return

    # out of order: 0 then power_profile_preset_mask
    def test_set_gpu_power_profile(self):
        self._print_func_name('')
        for i, gpu in enumerate(self.processors):
            for power_profile_preset_mask_name, power_profile_preset_mask, power_profile_preset_masks_cond in self.power_profile_preset_masks:
                msg = f'### amdsmi_set_gpu_power_profile(gpu={i}, power_profile_preset_mask={power_profile_preset_mask_name}):'
                try:
                    amdsmi.amdsmi_set_gpu_power_profile(gpu, 0, power_profile_preset_mask)
                    self._print(msg, '')
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, power_profile_preset_masks_cond):
                        self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    # pisolates
    def test_set_gpu_process_isolation(self):
        self._print_func_name('')
        pisolates = [1, 0]
        for i, gpu in enumerate(self.processors):
            for pisolate in pisolates:
                msg = f'### amdsmi_set_gpu_process_isolation(gpu={i}, pisolate={pisolate}):'
                try:
                    amdsmi.amdsmi_set_gpu_process_isolation(gpu, pisolate)
                    self._print(msg)
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, self.PASS):
                        self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    # handle error_map list
    def test_status_code_to_string(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_status_code_to_string as it fails (Unhashable type).")
        for error_num, error_name in error_map.items():
            msg = f'### amdsmi_status_code_to_string(error_num={error_num}):'
            try:
                ret = amdsmi.amdsmi_status_code_to_string(ctypes.c_uint32(int(error_num)))
                self._print(msg, ret)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    def test_topo_get_link_type(self):
        self._print_func_name('')
        self.RunFunc1Gpu(amdsmi_topo_get_link_type=amdsmi.amdsmi_topo_get_link_type)
        return

    def test_topo_get_link_weight(self):
        self._print_func_name('')
        self.RunFunc1Gpu(amdsmi_topo_get_link_weight=amdsmi.amdsmi_topo_get_link_weight)
        return

    def test_topo_get_numa_node_number(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_topo_get_numa_node_number=amdsmi.amdsmi_topo_get_numa_node_number)
        return

    def test_topo_get_p2p_status(self):
        self._print_func_name('')
        self.RunFunc1Gpu(amdsmi_topo_get_p2p_status=amdsmi.amdsmi_topo_get_p2p_status)
        return

    def test_get_gpu_busy_percent(self):
        self._print_func_name('')
        self.RunFunc1(amdsmi_get_gpu_busy_percent=amdsmi.amdsmi_get_gpu_busy_percent)
        return

if __name__ == '__main__':
    verbose=1
    if '-q' in sys.argv or '--quiet' in sys.argv:
        verbose=0
    elif '-v' in sys.argv or '--verbose' in sys.argv:
        verbose=2
    has_info_printed = False

    if verbose:
        print("AMD SMI Unit Tests")

    # Detect if ran without sudo or root privileges
    if os.geteuid() != 0:
        print("Warning: Some tests may require elevated privileges (sudo/root) to run completely.\n")
        print("Please relaunch with elevated privileges.\n")
        sys.exit(1)

    runner = unittest.TextTestRunner(verbosity=verbose)
    unittest.main(testRunner=runner)
    sys.exit(0)


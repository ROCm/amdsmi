#!/usr/bin/env python3
#
# Copyright (C) Advanced Micro Devices. All rights reserved.
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

'''
In integration testing, what is specifically tested:
1. Module Interfaces: The primary focus is on the connections and data exchange points
   (interfaces) between individual software modules or components.
2. Data Flow: How data is passed between modules, ensuring it is formatted correctly and
   transferred without loss or corruption.
3. System Logic: The integrated logic across multiple modules is checked to confirm that
   the combined functionality aligns with requirements and produces the expected outcomes.
4. External Dependencies: Interactions with external systems like databases, file servers,
   or other applications (via APIs) are tested to ensure seamless operation.
5. Cohesion: Whether the various integrated units function as a single, cohesive unit to
   achieve a broader system goal
'''

import json
import inspect
import multiprocessing
import os
import sys
import threading
import unittest


# Default path for AMDSMI_CLI_PATH is "/opt/rocm/libexec/amdsmi_cli/"
amdsmi_cli_path = os.environ.get("AMDSMI_CLI_PATH", "/opt/rocm/libexec/amdsmi_cli/")
if not os.path.exists(amdsmi_cli_path):
    raise FileNotFoundError(f"AMDSMI_CLI_PATH '{amdsmi_cli_path}' does not exist. Please set the correct path in your environment.")
sys.path.append(amdsmi_cli_path)
try:
    import amdsmi, amdsmi.amdsmi_wrapper
except ImportError:
    raise ImportError(f"Could not import the 'amdsmi' module from '{amdsmi_cli_path}'")

# same as unit_test
not_supported_error_codes = \
[
    ( '2', 'AMDSMI_STATUS_NOT_SUPPORTED'),
    ( '3', 'AMDSMI_STATUS_NOT_YET_IMPLEMENTED'),
    ('49', 'AMDSMI_STATUS_NO_HSMP_MSG_SUP')
]

# same as unit_test
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

if False: # Tested in Unit Tests
    class TestAmdSmiInit(unittest.TestCase):
        def test_init(self):
            self._print_func_name('')
            amdsmi.amdsmi_init()
            amdsmi.amdsmi_shut_down()

class TestAmdSmiPythonInterface(unittest.TestCase):

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

    # Same as unit_test
    max_num_physical_devices = amdsmi.amdsmi_interface.AMDSMI_MAX_NUM_XCP * amdsmi.amdsmi_interface.AMDSMI_MAX_DEVICES
    PASS = 'AMDSMI_STATUS_SUCCESS'
    FAIL = 'AMDSMI_STATUS_INVAL'

    # Same as unit_test
    # Tests marked wtih either of these flags will be skipped
    # and need to be implemented later.
    TODO_SKIP_FAIL = True
    TODO_SKIP_NOT_COMPLETE = True

    processor_types = \
    [
        ('UNKNOWN', amdsmi.AmdSmiProcessorType.UNKNOWN, FAIL),
        ('AMD_GPU', amdsmi.AmdSmiProcessorType.AMD_GPU, PASS),
        ('AMD_CPU', amdsmi.AmdSmiProcessorType.AMD_CPU, PASS),
        ('NON_AMD_GPU', amdsmi.AmdSmiProcessorType.NON_AMD_GPU, PASS),
        ('NON_AMD_CPU', amdsmi.AmdSmiProcessorType.NON_AMD_CPU, PASS),
        ('AMD_CPU_CORE', amdsmi.AmdSmiProcessorType.AMD_CPU_CORE, PASS),
        ('AMD_APU', amdsmi.AmdSmiProcessorType.AMD_APU, PASS)
    ]

    dev_perf_levels = \
    [
        ('AUTO', amdsmi.AmdSmiDevPerfLevel.AUTO, PASS),
        ('LOW', amdsmi.AmdSmiDevPerfLevel.LOW, PASS),
        ('HIGH', amdsmi.AmdSmiDevPerfLevel.HIGH, PASS),
        ('MANUAL', amdsmi.AmdSmiDevPerfLevel.MANUAL, PASS),
        ('STABLE_STD', amdsmi.AmdSmiDevPerfLevel.STABLE_STD, PASS),
        ('STABLE_PEAK', amdsmi.AmdSmiDevPerfLevel.STABLE_PEAK, PASS),
        ('STABLE_MIN_MCLK', amdsmi.AmdSmiDevPerfLevel.STABLE_MIN_MCLK, PASS),
        ('STABLE_MIN_SCLK', amdsmi.AmdSmiDevPerfLevel.STABLE_MIN_SCLK, PASS),
        ('DETERMINISM', amdsmi.AmdSmiDevPerfLevel.DETERMINISM, PASS),
        ('UNKNOWN', amdsmi.AmdSmiDevPerfLevel.UNKNOWN, FAIL)
    ]

    # Same as unit_test
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

    # Same as unit_test
    def _print_func_name(self, msg):
        if verbose == 2:
            stk = inspect.stack()
            if stk[1].function == '_callSetUp':
                return
            print(msg, flush=True)
            print(f'## {stk[1].function}()', flush=True)
        return

    # Same as unit_test
    def get_error_code(self, e):
        error_code = e.get_error_code()
        return error_map[error_code]

    # Same as unit_test
    def _check_ret(self, msg, _e, expected_code=None, printit=True):
        error_code_int = int(_e.get_error_code())
        error_code = str(error_code_int)
        if error_code in error_map:
            error_code_name = error_map[error_code]
        else:
            error_code_name = 'UNKNOWN_ERROR'

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

    def _check_exception(self, e):
        error_code = e.get_error_code()
        if error_code == amdsmi.amdsmi_wrapper.AMDSMI_STATUS_NOT_SUPPORTED:
            print("  Not Supported, skipping...")
            return
        else:
            raise e

    def setUp(self):
        # Called before each test by unittest framework
        self.raise_exception = None
        amdsmi.amdsmi_init()
        self.processors = amdsmi.amdsmi_get_processor_handles()
        self.assertGreaterEqual(len(self.processors), 1)
        self.assertLessEqual(len(self.processors), self.max_num_physical_devices)

    def tearDown(self):
        # Called after each test by unittest framework
        amdsmi.amdsmi_shut_down()

    # integration
    def test_get_processor_handle_from_bdf(self):
        self._print_func_name('')
        for i, gpu in enumerate(self.processors):
            msg = f'### amdsmi_get_gpu_device_bdf(gpu={i}):'
            try:
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(gpu)
                self._print(msg, bdf)
                self._print(gpu.value)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                continue

            msg = f'### amdsmi_get_processor_handle_from_bdf(bdf={bdf}):'
            try:
                ret = amdsmi.amdsmi_get_processor_handle_from_bdf(bdf)
                self._print(msg, ret.value)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                continue

            if gpu.value != ret.value:
                msg += f'gpu={i}: Expected: {gpu.value}, Received: {ret.value}'
                self.raise_exception = amdsmi.AmdSmiLibraryException(amdsmi.amdsmi_interface.amdsmi_wrapper.AMDSMI_STATUS_API_FAIL)

        if self.raise_exception:
            raise self.raise_exception
        return

    def test_get_socket_info(self):
        self._print_func_name('')
        msg = f'### amdsmi_get_socket_handles():'
        try:
            sockets = amdsmi.amdsmi_get_socket_handles()
            self._print(msg, [id(addr) for addr in sockets])
        except amdsmi.AmdSmiLibraryException as e:
            if self._check_ret(msg, e, self.PASS):
                raise e
        for i, socket in enumerate(sockets):
            msg = f'### amdsmi_get_socket_info(socket={i}):'
            try:
                ret = amdsmi.amdsmi_get_socket_info(socket)
                self._print(msg, ret)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                    continue
        if self.raise_exception:
            raise self.raise_exception
        return

    def test_get_processor_handles_by_type(self):
        self._print_func_name('')
        msg = f'### amdsmi_get_socket_handles():'
        try:
            sockets = amdsmi.amdsmi_get_socket_handles()
            self._print(msg, [id(addr) for addr in sockets])
        except amdsmi.AmdSmiLibraryException as e:
            if self._check_ret(msg, e, self.PASS):
                raise e
        for i, socket in enumerate(sockets):
            for processor_name, processor_type, processor_cond in self.processor_types:
                msg = f'### amdsmi_get_processor_handles_by_type(socket={socket.value}, processor_type={processor_name}):'
                try:
                    ret = amdsmi.amdsmi_get_processor_handles_by_type(socket, processor_type)
                    self._print(msg, ret)
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, processor_cond):
                        self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    # data print issues
    # integration
    def test_get_socket_info(self):
        self._print_func_name('')

        msg = f'### amdsmi_get_socket_handles():'
        try:
            sockets = amdsmi.amdsmi_get_socket_handles()
            self._print(msg, [id(addr) for addr in sockets])
        except amdsmi.AmdSmiLibraryException as e:
            if self._check_ret(msg, e, self.PASS):
                raise e
        self.assertGreaterEqual(len(sockets), 1)
        self.assertLessEqual(len(sockets), self.max_num_physical_devices)

        for i, socket in enumerate(sockets):
            msg = f'### amdsmi_get_socket_info(socket={i}):'
            try:
                ret = amdsmi.amdsmi_get_socket_info(socket)
                self._print(msg, ret)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    def test_utilization_count(self):
        self._print_func_name('')

        processors = amdsmi.amdsmi_get_processor_handles()
        self.assertGreaterEqual(len(processors), 1)
        self.assertLessEqual(len(processors), self.max_num_physical_devices)
        for i in range(0, len(processors)):
            bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
            print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
            print("\n###Test amdsmi_get_utilization_count \n")
            utilization_counter_types = [
                amdsmi.AmdSmiUtilizationCounterType.COARSE_GRAIN_GFX_ACTIVITY,
                amdsmi.AmdSmiUtilizationCounterType.COARSE_GRAIN_MEM_ACTIVITY,
                amdsmi.AmdSmiUtilizationCounterType.COARSE_DECODER_ACTIVITY
            ]
            try:
                utilization_count = amdsmi.amdsmi_get_utilization_count(processors[i], utilization_counter_types)
            except amdsmi.AmdSmiLibraryException as e:
                self._check_exception(e)
                continue
            print("  Timestamp: {}".format(
                utilization_count[0]['timestamp']))
            print("  Utilization count for {} is: {}".format(
                utilization_count[1]['type'], utilization_count[1]['value']))
            print("  Utilization count for {} is: {}".format(
                utilization_count[2]['type'], utilization_count[2]['value']))
            print("  Utilization count for {} is: {}".format(
                utilization_count[3]['type'], utilization_count[3]['value']))
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            print("\n")
            utilization_counter_types = [
                amdsmi.AmdSmiUtilizationCounterType.FINE_GRAIN_GFX_ACTIVITY,
                amdsmi.AmdSmiUtilizationCounterType.FINE_GRAIN_MEM_ACTIVITY,
                amdsmi.AmdSmiUtilizationCounterType.FINE_DECODER_ACTIVITY
            ]
            try:
                utilization_count = amdsmi.amdsmi_get_utilization_count(processors[i], utilization_counter_types)
            except amdsmi.AmdSmiLibraryException as e:
                self._check_exception(e)
                continue
            print("  Timestamp: {}".format(
                utilization_count[0]['timestamp']))
            print("  Utilization count for {} is: {}".format(
                utilization_count[1]['type'], utilization_count[1]['value']))
            print("  Utilization count for {} is: {}".format(
                utilization_count[2]['type'], utilization_count[2]['value']))
            print("  Utilization count for {} is: {}".format(
                utilization_count[3]['type'], utilization_count[3]['value']))
        print("\n")

    # integration
    def test_gpu_counter(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_gpu_counter as it fails (Error opening file).")
        for i, gpu in enumerate(self.processors):
            for event_type_name, event_type, event_type_cond in self.event_types:
                # Create
                msg = f'### amdsmi_gpu_create_counter(gpu={i}, event_type={event_type_name}):'
                try:
                    event_handle = amdsmi.amdsmi_gpu_create_counter(gpu, event_type)
                    self._print(msg, event_handle)
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, event_type_cond):
                        self.raise_exception = e
                    # if any exception occurs, skip the rest of the loop
                    continue

                # Read
                msg = f'### amdsmi_gpu_read_counter(event_handle={event_handle}):'
                try:
                    ret = amdsmi.amdsmi_gpu_read_counter(event_handle)
                    self._print(msg, ret)
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, event_type_cond):
                        self.raise_exception = e

                # Control
                for counter_command_name, counter_command, counter_commands_cond in self.counter_commands:
                    msg = f'### amdsmi_gpu_control_counter(event_handle={event_handle_name}, counter_command={counter_command_name}):'
                    try:
                        amdsmi.amdsmi_gpu_control_counter(event_handle, counter_command)
                        self._print(msg, '')
                    except amdsmi.AmdSmiLibraryException as e:
                        if self._check_ret(msg, e, counter_commands_cond):
                            self.raise_exception = e

                # Destroy
                msg = f'### amdsmi_gpu_destroy_counter(event_handle={event_handle}):'
                try:
                    amdsmi.amdsmi_gpu_destroy_counter(event_handle)
                    self._print(msg, '')
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, event_type_cond):
                        self.raise_exception = e

        if self.raise_exception:
            raise self.raise_exception
        return

    # integration
    def test_gpu_event(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_gpu_event as it fails (File Error).")
        mask = 1 << (amdsmi.AmdSmiEvtNotificationType.GPU_PRE_RESET -1) | \
               1 << (amdsmi.AmdSmiEvtNotificationType.GPU_POST_RESET -1)
        timeout_ms = 1000
        for i, gpu in enumerate(self.processors):
            msg = f'### amdsmi_init_gpu_event_notification(gpu={i}):'

            # Init
            try:
                amdsmi.amdsmi_init_gpu_event_notification(gpu)
                self._print(msg, ret)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                # Skip remaining tests on any exception when initializing
                continue

            # Set Mask
            msg = f'### amdsmi_set_gpu_event_notification_mask(gpu={i}, mask={mask}):'
            try:
                amdsmi.amdsmi_set_gpu_event_notification_mask(gpu, mask)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

            # Get
            msg = f'### amdsmi_get_gpu_event_notification(timeout_ms={timeout_ms}):'
            try:
                ret = amdsmi.amdsmi_get_gpu_event_notification(timeout_ms)
                self._print(msg, ret)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

            # Stop
            msg = f'### amdsmi_stop_gpu_event_notification(gpu={i}):'
            try:
                amdsmi.amdsmi_stop_gpu_event_notification(gpu)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

        if self.raise_exception:
            raise self.raise_exception
        return

    # integration
    def test_set_clk_freq(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_set_clk_freq as it fails (Perm failure).")

        for i, gpu in enumerate(self.processors):
            for clk_type_name, clk_type, clk_cond in self.clk_types:

                # Set invalid clock frequency
                try:
                    freq_bitmask = 0x1234
                    msg = f'### amdsmi_set_clk_freq(gpu={i}, clk_type={clk_type_name}, freq_bitmask={freq_bitmask}):'
                    amdsmi.amdsmi_set_clk_freq(gpu, clk_type_name, freq_bitmask)
                    self._print(msg, '')
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, self.FAIL):
                        self.raise_exception = e

                # Get clock frequency info
                msg = f'### amdsmi_get_clk_freq(gpu={i}, clk_type={clk_type_name}):'
                try:
                    clk_freq_info = amdsmi.amdsmi_get_clk_freq(gpu, clk_type_name)
                    self._print(msg, clk_freq_info)

                    current = clk_freq_info['current']
                    num_supported = clk_freq_info['num_supported']
                    frequencies = clk_freq_info['frequency']
                    if num_supported == 0:
                        self._print(f'No supported frequencies for clk_type={clk_type_name}')
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, clk_cond):
                        self.raise_exception = e
                        continue

                for index in range(0, num_supported):

                    # Set clock frequency for each frequency supported
                    try:
                        freq_bitmask = frequencies[index]
                        msg = f'### amdsmi_set_clk_freq(gpu={i}, clk_type={clk_type_name}, freq_bitmask={freq_bitmask}):'
                        amdsmi.amdsmi_set_clk_freq(gpu, clk_type_name, freq_bitmask)
                        self._print(msg, '')
                    except amdsmi.AmdSmiLibraryException as e:
                        if self._check_ret(msg, e, clk_cond):
                            self.raise_exception = e
                            continue

                # Set clock frequency back
                try:
                    freq_bitmask = frequencies[current]
                    msg = f'### amdsmi_set_clk_freq(gpu={i}, clk_type={clk_type_name}, freq_bitmask={freq_bitmask}):'
                    amdsmi.amdsmi_set_clk_freq(gpu, clk_type_name, freq_bitmask)
                    self._print(msg, '')
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, clk_cond):
                        self.raise_exception = e

        if self.raise_exception:
            raise self.raise_exception
        return

    # integration
    def test_cpu_core_boostlimit(self):
        self._print_func_name('')
        for i, gpu in enumerate(self.processors):

            found_error = False

            # Set invalid boostlimit
            boost_limit = 0
            msg = f'### amdsmi_set_cpu_core_boostlimit(gpu={i}, boost_limit={boost_limit}):'
            try:
                amdsmi.amdsmi_set_cpu_core_boostlimit(gpu, boost_limit)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.FAIL):
                    self.raise_exception = e

            # Get current boostlimit
            msg = f'### amdsmi_get_cpu_core_boostlimit(gpu={i}):'
            try:
                boost_limit_orig = amdsmi.amdsmi_get_cpu_core_boostlimit(gpu)
                self._print(msg, boost_limit_orig)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                found_error = True

            if found_error:
                continue

            # Set boostlimit back
            msg = f'### amdsmi_set_cpu_core_boostlimit(gpu={i}, boost_limit={boost_limit_orig}):'
            try:
                amdsmi.amdsmi_set_cpu_core_boostlimit(gpu, boost_limit_orig)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    # integration
    def test_cpu_socket_power_cap(self):
        self._print_func_name('')
        for i, gpu in enumerate(self.processors):

            found_error = False

            # Set cpu socket power to invalid number
            power_cap = 0
            msg = f'### amdsmi_set_cpu_socket_power_cap(gpu={i}, power_cap={power_cap}):'
            try:
                amdsmi.amdsmi_set_cpu_socket_power_cap(gpu, power_cap)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.FAIL):
                    self.raise_exception = e

            # Get cpu socket power
            msg = f'### amdsmi_get_cpu_socket_power_cap(gpu={i}):'
            try:
                power_cap_orig = amdsmi.amdsmi_get_cpu_socket_power_cap(gpu)
                self._print(msg, power_cap_orig)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                    found_error = True

            # Get cpu socket power to max
            msg = f'### amdsmi_get_cpu_socket_power_cap_max(gpu={i}):'
            try:
                power_cap_max = amdsmi.amdsmi_get_cpu_socket_power_cap_max(gpu)
                self._print(msg, power_cap_max)

                # Convert power_cap_max from string that has units to an integer
                # Ex.  power_cap_max = "5000 mW"  to   power_cap_max = 5000
                power_cap_max = int(power_cap_max.split()[0])
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                found_error = True

            if found_error:
                continue

            # Set cpu socket power to max
            msg = f'### amdsmi_set_cpu_socket_power_cap(gpu={i}, power_cap={power_cap_max}):'
            try:
                amdsmi.amdsmi_set_cpu_socket_power_cap(gpu, power_cap_max)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

            # Set cpu socket power back
            msg = f'### amdsmi_set_cpu_socket_power_cap(gpu={i}, power_cap={power_cap_orig}):'
            try:
                amdsmi.amdsmi_set_cpu_socket_power_cap(gpu, power_cap_orig)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

        if self.raise_exception:
            raise self.raise_exception
        return

    # integration
    def test_set_gpu_compute_partition(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_set_gpu_compute_partition as it fails on MI300.")
        for i, gpu in enumerate(self.processors):
            default_compute_partition_type = self.compute_partition_types[0][1]
            msg = f'### amdsmi_get_gpu_compute_partition(gpu={i}):'
            try:
                default_compute_partition_name = amdsmi.amdsmi_get_gpu_compute_partition(gpu)
                self._print(msg, default_compute_partition_name)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                continue

            for compute_partition_type_name, compute_partition_type, compute_partition_type_cond in self.compute_partition_types:
                if default_compute_partition_name == compute_partition_type_name:
                    default_compute_partition_type = compute_partition_type
                msg = f'### amdsmi_set_gpu_compute_partition(gpu={i}, compute_partition_type={compute_partition_type_name}):'
                try:
                    amdsmi.amdsmi_set_gpu_compute_partition(gpu, compute_partition_type)
                    self._print(msg, '')
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, compute_partition_type_cond):
                        self.raise_exception = e

            msg = f'### amdsmi_set_gpu_compute_partition(gpu={i}, default_compute_partition={default_compute_partition_name}):'
            try:
                amdsmi.amdsmi_set_gpu_compute_partition(gpu, default_compute_partition_type)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                continue
        if self.raise_exception:
            raise self.raise_exception
        return

    # integration
    def test_gpu_fan_speed(self):
        self._print_func_name('')
        for i, gpu in enumerate(self.processors):

            found_error = False

            # Set invalid fan speed
            fan_speed = -1
            msg = f'### amdsmi_set_gpu_fan_speed(gpu={i}, index=0, fan_speed={fan_speed}):'
            try:
                amdsmi.amdsmi_set_gpu_fan_speed(gpu, 0, fan_speed)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

            # Get current fan speed
            msg = f'### amdsmi_get_gpu_fan_speed(gpu={i}, index=0):'
            try:
                fan_speed_orig = amdsmi.amdsmi_get_gpu_fan_speed(gpu, 0)
                self._print(msg, fan_speed_orig)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                found_error = True

            # Determine max fan speed
            msg = f'### amdsmi_get_gpu_fan_speed_max(gpu={i}, index=0):'
            try:
                fan_speed_max = amdsmi.amdsmi_get_gpu_fan_speed_max(gpu, 0)
                self._print(msg, fan_speed_max)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                found_error = True

            if found_error:
                continue

            if fan_speed_orig == fan_speed_max:
                fan_speed = int(fan_speed_max/2)
            else:
                fan_speed = fan_speed_max

            # Set fan speed
            msg = f'### amdsmi_set_gpu_fan_speed(gpu={i}, index=0, fan_speed={fan_speed}):'
            try:
                amdsmi.amdsmi_set_gpu_fan_speed(gpu, 0, fan_speed)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

            # Set to original fan speed
            msg = f'### amdsmi_set_gpu_fan_speed(gpu={i}, index=0, fan_speed_current={fan_speed_orig}):'
            try:
                amdsmi.amdsmi_set_gpu_fan_speed(gpu, 0, fan_speed_orig)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

        if self.raise_exception:
            raise self.raise_exception
        return

    # integration
    def test_set_gpu_overdrive_level(self):
        self._print_func_name('')
        for i, gpu in enumerate(self.processors):
            # Find current overdrive value
            msg = f'### amdsmi_get_gpu_overdrive_level(gpu={i}):'
            try:
                overdrive_value_current = amdsmi.amdsmi_get_gpu_overdrive_level(gpu)
                self._print(msg, overdrive_value_current)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                continue

            if overdrive_value_current != 1:
                overdrive_value = 1
            else:
                overdrive_value = 2

            # Set overdrive value
            msg = f'### amdsmi_set_gpu_overdrive_level(gpu={i}, overdrive_value={overdrive_value}):'
            try:
                amdsmi.amdsmi_set_gpu_overdrive_level(gpu, overdrive_value)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

            # Set back to original overdrive value
            msg = f'### amdsmi_set_gpu_overdrive_level(gpu={i}, overdrive_value={overdrive_value_current}):'
            try:
                amdsmi.amdsmi_set_gpu_overdrive_level(gpu, overdrive_value_current)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

        if self.raise_exception:
            raise self.raise_exception
        return

    # integration
    def test_set_gpu_pci_bandwidth(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_set_gpu_pci_bandwidth as it fails (MI350X, AMDSMI_STATUS_UNEXPECTED_DATA).")
        for i, gpu in enumerate(self.processors):
            # Get current PCI bandwidth info
            msg = f'### amdsmi_get_gpu_pci_bandwidth(gpu={i}):'
            try:
                bandwidth_info = amdsmi.amdsmi_get_gpu_pci_bandwidth(gpu)
                self._print(msg, bandwidth_info)

                current_bandwidth_index = bandwidth_info['transfer_rate']['current']
                if current_bandwidth_index > 0:
                    bitmask = 1 << (current_bandwidth_index - 1)
                else:
                    bitmask = 1 << (current_bandwidth_index)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                continue

            # Set PCI bandwidth
            msg = f'### amdsmi_set_gpu_pci_bandwidth(gpu={i}, bitmask={bitmask}):'
            try:
                amdsmi.amdsmi_set_gpu_pci_bandwidth(gpu, bitmask)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                continue

            # Set back to original PCI bandwidth
            msg = f'### amdsmi_set_gpu_pci_bandwidth(gpu={i}, bitmask={bitmask}):'
            try:
                bitmask = 1 << (current_bandwidth_index)
                amdsmi.amdsmi_set_gpu_pci_bandwidth(gpu, bitmask)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

        if self.raise_exception:
            raise self.raise_exception
        return

    # integration
    def test_set_gpu_perf_level(self):
        self._print_func_name('')
        dev_perf_level_current = self.dev_perf_levels[0][1]
        for i, gpu in enumerate(self.processors):
            msg = f'### amdsmi_get_gpu_perf_level(gpu={i}):'
            try:
                dev_perf_level_name_current = amdsmi.amdsmi_get_gpu_perf_level(gpu)
                self._print(msg, '')

                items = dev_perf_level_name_current.split('_')
                dev_perf_level_name_current = items[-1]
            except amdsmi.AmdSmiLibraryException as e:
                self._print(msg, e)
                continue

            for dev_perf_level_name, dev_perf_level, dev_perf_level_cond in self.dev_perf_levels:
                msg = f'### amdsmi_set_gpu_perf_level(gpu={i}, dev_perf_level={dev_perf_level_name}):'
                try:
                    if dev_perf_level_name_current == dev_perf_level_name:
                        dev_perf_level_current = dev_perf_level
                    amdsmi.amdsmi_set_gpu_perf_level(gpu, dev_perf_level)
                    self._print(msg, '')
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, dev_perf_level_cond):
                        self.raise_exception = e

            msg = f'### amdsmi_set_gpu_perf_level(gpu={i}, dev_perf_level={dev_perf_level_name}):'
            try:
                amdsmi.amdsmi_set_gpu_perf_level(gpu, dev_perf_level_current)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, dev_perf_level_cond):
                    self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    # integration
    def test_power_cap(self):
        self._print_func_name('')
        for i, gpu in enumerate(self.processors):
            # Get Power Cap Info
            msg = f'### amdsmi_get_power_cap_info(gpu={i}):'
            try:
                power_cap_info = amdsmi.amdsmi_get_power_cap_info(gpu)
                self._print(msg, power_cap_info)
                cap =  int((power_cap_info['max_power_cap'] + power_cap_info['min_power_cap']) / 2)
                current_cap = power_cap_info['power_cap']
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                # Have to be able to get info before setting
                continue

            # Set to Average Power Cap
            msg = f'### amdsmi_set_power_cap(gpu={i}, index=0, power_cap={cap}):'
            try:
                amdsmi.amdsmi_set_power_cap(gpu, 0, cap)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

            # Restore Power Cap
            msg = f'### amdsmi_set_power_cap(gpu={i}, index=0, power_cap={current_cap}):'
            try:
                amdsmi.amdsmi_set_power_cap(gpu, 0, current_cap)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

        if self.raise_exception:
            raise self.raise_exception
        return

    # integration
    def test_soc_pstate(self):
        self._print_func_name('')
        for i, gpu in enumerate(self.processors):
            # Get current policy info
            msg = f'### amdsmi_get_soc_pstate(gpu={i}):'
            try:
                policy_info = amdsmi.amdsmi_get_soc_pstate(gpu)
                self._print(msg, '')

                num_supported = policy_info['num_supported']
                if not isinstance(num_supported, int):
                    self._print('Cannot determine num_supported={num_supported}', '')
                    continue
                policy_id_current = policy_info['current_id']
                if not isinstance(policy_id_current, int):
                    self._print('Cannot determine policy_id_current={policy_id_current}', '')
                    continue
                policy_id_orig = policy_info['policies'][policy_id_current]['policy_id']
                if not isinstance(policy_id_orig, int):
                    self._print('Cannot determine orig policy_id={policy_id_orig}', '')
                    continue

                index = 0
                if num_supported >= 2:
                    if policy_id_current != 0:
                        index = 1
                policy_id = policy_info['policies'][index]['policy_id']
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                continue

            # Set SOC Pstate policy
            msg = f'### amdsmi_set_soc_pstate(gpu={i}):'
            try:
                amdsmi.amdsmi_set_soc_pstate(gpu, policy_id)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                continue

            # Set back to original policy
            msg = f'### amdsmi_set_soc_pstate(gpu={i}, policy_id={policy_id_orig}):'
            try:
                amdsmi.amdsmi_set_soc_pstate(gpu, policy_id_orig)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

        if self.raise_exception:
            raise self.raise_exception
        return

    # integration
    def test_xgmi_plpd(self):
        self._print_func_name('')
        if self.TODO_SKIP_FAIL:
            self.skipTest("Skipping test_set_xgmi_plpd as it fails on MI300.")
        for i, gpu in enumerate(self.processors):
            msg = f'gpu({i}):'

            # Get current policy info
            msg = f'### amdsmi_get_xgmi_plpd(gpu={i}):'
            try:
                policy_info = amdsmi.amdsmi_get_xgmi_plpd(gpu)
                self._print(msg, '')

                num_supported = policy_info['num_supported']
                if not isinstance(num_supported, int):
                    self._print('Cannot determine num_supported={num_supported}', '')
                    continue
                policy_id_current = policy_info['current_id']
                if not isinstance(policy_id_current, int):
                    self._print('Cannot determine policy_id_current={policy_id_current}', '')
                    continue
                policy_id_orig = policy_info['policies'][policy_id_current]['policy_id']
                if not isinstance(policy_id_orig, int):
                    self._print('Cannot determine orig policy_id={policy_id_orig}', '')
                    continue
                index = 0
                if num_supported >= 2:
                    if policy_id_current != 0:
                        index = 1
                policy_id = policy_info['policies'][index]['policy_id']
                if not isinstance(policy_id, int):
                    self._print('Cannot determine policy_id={policy_id}', '')
                    continue
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
                continue

            # Set policy
            msg = f'### amdsmi_set_xgmi_plpd(gpu={i}, policy_id={policy_id}):'
            try:
                amdsmi.amdsmi_set_xgmi_plpd(gpu, policy_id)
                self._print(msg, '')
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e

            # Set back to original policy
            msg = f'### amdsmi_set_xgmi_plpd(gpu={i}, policy_id={policy_id_orig}):'
            try:
                amdsmi.amdsmi_set_xgmi_plpd(gpu, policy_id_orig)
            except amdsmi.AmdSmiLibraryException as e:
                if self._check_ret(msg, e, self.PASS):
                    self.raise_exception = e
        if self.raise_exception:
            raise self.raise_exception
        return

    if False: # Tested in Unit Tests
        def _print_vbios_info(self, vbios_info):
            print(f"  vbios_info['part_number'] is: {vbios_info['part_number']}")
            print(f"  vbios_info['build_date'] is: {vbios_info['build_date']}")
            print(f"  vbios_info['name'] is: {vbios_info['name']}")
            print(f"  vbios_info['version'] is: {vbios_info['version']}")
            if 'boot_firmware' in vbios_info:
                print(f"  vbios_info['boot_firmware'] is: {vbios_info['boot_firmware']}")
            else:
                print("  vbios_info['boot_firmware'] is: N/A")
            return

    if False: # tested in unit_tests
        def test_asic_kfd_info(self):
            self._print_func_name('')
            for i, gpu in enumerate(self.processors):
                msg = f'### amdsmi_get_gpu_device_bdf(gpu={i})'
                try:
                    bdf = amdsmi.amdsmi_get_gpu_device_bdf(gpu)
                    self._print(msg, bdf)
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, self.PASS):
                        self.raise_exception = e

                msg = f'### amdsmi_get_gpu_asic_info(gpu={i})'
                try:
                    asic_info = amdsmi.amdsmi_get_gpu_asic_info(gpu)
                    self._print(msg, asic_info)
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, self.PASS):
                        self.raise_exception = e

                msg = f'### amdsmi_get_gpu_kfd_info(gpu={i})'
                try:
                    kfd_info = amdsmi.amdsmi_get_gpu_kfd_info(gpu)
                    self._print(msg, kfd_info)
                except amdsmi.AmdSmiLibraryException as e:
                    if self._check_ret(msg, e, self.PASS):
                        self.raise_exception = e
            if self.raise_exception:
                raise self.raise_exception
            return

    if False: # Tested in unit_tests
        # amdsmi_get_vram_info should be supported on all ASICs
        def test_get_vram_info(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))

                vram_types = {
                    amdsmi.AmdSmiVramType.UNKNOWN: "UNKNOWN",
                    amdsmi.AmdSmiVramType.HBM:     "HBM",
                    amdsmi.AmdSmiVramType.HBM2:    "HBM2",
                    amdsmi.AmdSmiVramType.HBM2E:   "HBM2E",
                    amdsmi.AmdSmiVramType.HBM3:    "HBM3",
                    amdsmi.AmdSmiVramType.DDR2:    "DDR2",
                    amdsmi.AmdSmiVramType.DDR3:    "DDR3",
                    amdsmi.AmdSmiVramType.DDR4:    "DDR4",
                    amdsmi.AmdSmiVramType.GDDR1:   "GDDR1",
                    amdsmi.AmdSmiVramType.GDDR2:   "GDDR2",
                    amdsmi.AmdSmiVramType.GDDR3:   "GDDR3",
                    amdsmi.AmdSmiVramType.GDDR4:   "GDDR4",
                    amdsmi.AmdSmiVramType.GDDR5:   "GDDR5",
                    amdsmi.AmdSmiVramType.GDDR6:   "GDDR6",
                    amdsmi.AmdSmiVramType.GDDR7:   "GDDR7",
                    amdsmi.AmdSmiVramType.MAX:     "MAX"
                }

                try:
                    print("\n###Test amdsmi_get_gpu_vram_info \n")
                    vram_info = amdsmi.amdsmi_get_gpu_vram_info(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  vram_info['vram_type'] is: {}".format(
                    vram_types[vram_info['vram_type']]))
                print("  vram_info['vram_vendor'] is: {}".format(
                    vram_info['vram_vendor']))
                print("  vram_info['vram_size'] is: {} MB".format(
                    vram_info['vram_size']))
                print("  vram_info['vram_bit_width'] is: {}".format(
                    vram_info['vram_bit_width']))
                print("  vram_info['vram_max_bandwidth'] is: {} GB/s".format(
                    vram_info['vram_max_bandwidth']))

    if False: # Tested in Unit Tests
        # amdsmi_get_gpu_xcd_counter should be supported on all ASICs
        def test_get_xcd_counter(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_gpu_xcd_counter \n")
                    xcd_count = amdsmi.amdsmi_get_gpu_xcd_counter(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  xcd_counter['counter'] is: {}".format(
                    xcd_count))

    if False: # Tested in Unit Tests
        # amdsmi_get_gpu_bad_page_info is not supported in Navi2x, Navi3x
        def test_bad_page_info(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                try:
                    print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                    processor = amdsmi.amdsmi_get_processor_handle_from_bdf(bdf)
                    print("\n###Test amdsmi_get_gpu_bad_page_info \n")
                    bad_page_info = amdsmi.amdsmi_get_gpu_bad_page_info(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("bad_page_info: " + str(bad_page_info))
                print("Number of bad pages: {}".format(len(bad_page_info)))
                j = 0
                for table_record in bad_page_info:
                    print("\ntable_record[\"value\"]" + str(table_record["value"]))
                    print("Page: {}".format(j))
                    print("Page Address: " + str(table_record["page_address"]))
                    print("Page Size: " + str(table_record["page_size"]))
                    print("Status: " + str(table_record["status"]))
                    print("\n")
                    j += 1
            print("\n")

    if False: # Tested in Unit Tests
        def test_gpu_cache_info(self):
            self._print_func_name('')
            print("\n\n###Test amdsmi_interface.amdsmi_get_gpu_cache_info")
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                print("\n\n###Test Processor {}, bdf: {}".format(i, amdsmi.amdsmi_get_gpu_device_bdf(processors[i])))
                try:
                    print("\n###Test amdsmi_interface.amdsmi_get_gpu_cache_info \n")
                    cache_info = amdsmi.amdsmi_interface.amdsmi_get_gpu_cache_info(processors[i])
                except Exception as e:
                    print(f"  Exception in amdsmi_get_gpu_cache_info: {e}")
                    self.fail(f"Test failed due to exception: {e}")

                if isinstance(cache_info, dict):
                    for key, value in cache_info.items():
                        print(f"{key}: {value}")
                    for cache_entry in cache_info.get('cache', []):
                        self.assertIn('cache_size', cache_entry)
                        self.assertIn('cache_level', cache_entry)
                        self.assertIn('num_cache_instance', cache_entry)
                        self.assertIn('max_num_cu_shared', cache_entry)
                else:
                    self.assertIsInstance(cache_info, dict)

    if False: # Tested in Unit Tests
        def test_get_gpu_compute_partition(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreater(len(processors), 0)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                try:
                    result = amdsmi.amdsmi_get_gpu_compute_partition(processors[i])
                    self.assertIsInstance(result, str)
                    self.assertTrue(len(result) > 0)
                    print(f"\nCompute partition for handle {bdf}: {result}")
                except Exception as e:
                    print(f"\nCompute partition not supported for handle {bdf}: {e}")
                    continue
            print("\n")

    if False: # Tested in Unit Tests
        def test_board_info(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_gpu_board_info \n")
                    board_info = amdsmi.amdsmi_get_gpu_board_info(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  board_info['model_number'] is: {}".format(
                    board_info['model_number']))
                print("  board_info['product_serial'] is: {}".format(
                    board_info['product_serial']))
                print("  board_info['fru_id'] is: {}".format(
                    board_info['fru_id']))
                print("  board_info['manufacturer_name'] is: {}".format(
                    board_info['manufacturer_name']))
                print("  board_info['product_name'] is: {}".format(
                    board_info['product_name']))
            print("\n")

    if False: # Tested in Unit Tests
        def test_clock_frequency(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_clk_freq \n")
                    clock_frequency = amdsmi.amdsmi_get_clk_freq(processors[i], amdsmi.AmdSmiClkType.SYS)
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  SYS clock_frequency['num_supported']: {}".format(
                    clock_frequency['num_supported']))
                print("  SYS clock_frequency['current']: {}".format(
                    clock_frequency['current']))
                print("  SYS clock_frequency['frequency']: {}".format(
                    clock_frequency['frequency']))
                try:
                    clock_frequency = amdsmi.amdsmi_get_clk_freq(processors[i], amdsmi.AmdSmiClkType.DF)
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  DF clock_frequency['num_supported']: {}".format(
                    clock_frequency['num_supported']))
                print("  DF clock_frequency['current']: {}".format(
                    clock_frequency['current']))
                print("  DF clock_frequency['frequency']: {}".format(
                    clock_frequency['frequency']))
            print("\n")

    if False: # Tested in Unit Tests
        # amdsmi_get_clk_freq with AmdSmiClkType.DCEF is not supported in MI210, MI300A
        def test_clock_frequency_DCEF(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_clk_freq \n")
                    clock_frequency = amdsmi.amdsmi_get_clk_freq(processors[i], amdsmi.AmdSmiClkType.DCEF)
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  DCEF clock_frequency['num_supported']: {}".format(
                    clock_frequency['num_supported']))
                print("  DCEF clock_frequency['current']: {}".format(
                    clock_frequency['current']))
                print("  DCEF clock_frequency['frequency']: {}".format(
                    clock_frequency['frequency']))
            print("\n")

    if False: # Tested in Unit Tests
        def test_clock_info(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_clock_info \n")
                    clock_measure = amdsmi.amdsmi_get_clock_info(processors[i], amdsmi.AmdSmiClkType.GFX)
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  Current clock for domain GFX is: {}".format(
                    clock_measure['clk']))
                print("  Max clock for domain GFX is: {}".format(
                    clock_measure['max_clk']))
                print("  Min clock for domain GFX is: {}".format(
                    clock_measure['min_clk']))
                print("  Is GFX clock locked: {}".format(
                    clock_measure['clk_locked']))
                print("  Is GFX clock in deep sleep: {}".format(
                    clock_measure['clk_deep_sleep']))
                try:
                    clock_measure = amdsmi.amdsmi_get_clock_info(processors[i], amdsmi.AmdSmiClkType.MEM)
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  Current clock for domain MEM is: {}".format(
                    clock_measure['clk']))
                print("  Max clock for domain MEM is: {}".format(
                    clock_measure['max_clk']))
                print("  Min clock for domain MEM is: {}".format(
                    clock_measure['min_clk']))
                print("  Is MEM clock in deep sleep: {}".format(
                    clock_measure['clk_deep_sleep']))
            print("\n")

    if False: # Tested in Unit Tests
        # AmdSmiClkType.VCLK0 and DCLK0 are not supported in MI210
        def test_clock_info_vclk0_dclk0(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_clock_info \n")
                    clock_measure = amdsmi.amdsmi_get_clock_info(processors[i], amdsmi.AmdSmiClkType.VCLK0)
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  Current clock for domain VCLK0 is: {}".format(
                    clock_measure['clk']))
                print("  Max clock for domain VCLK0 is: {}".format(
                    clock_measure['max_clk']))
                print("  Min clock for domain VCLK0 is: {}".format(
                    clock_measure['min_clk']))
                print("  Is VCLK0 clock in deep sleep: {}".format(
                    clock_measure['clk_deep_sleep']))
                try:
                    clock_measure = amdsmi.amdsmi_get_clock_info(processors[i], amdsmi.AmdSmiClkType.DCLK0)
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  Current clock for domain DCLK0 is: {}".format(
                    clock_measure['clk']))
                print("  Max clock for domain DCLK0 is: {}".format(
                    clock_measure['max_clk']))
                print("  Min clock for domain DCLK0 is: {}".format(
                    clock_measure['min_clk']))
                print("  Is DCLK0 clock in deep sleep: {}".format(
                    clock_measure['clk_deep_sleep']))
            print("\n")


    if False: # Tested in Unit Tests
        # AmdSmiClkType.VCLK1 and DCLK1 are not supported in MI210, MI300A, MI300X
        def test_clock_info_vclk1_dclk1(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_clock_info \n")
                    clock_measure = amdsmi.amdsmi_get_clock_info(processors[i], amdsmi.AmdSmiClkType.VCLK1)
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  Current clock for domain VCLK1 is: {}".format(
                    clock_measure['clk']))
                print("  Max clock for domain VCLK1 is: {}".format(
                    clock_measure['max_clk']))
                print("  Min clock for domain VCLK1 is: {}".format(
                    clock_measure['min_clk']))
                print("  Is VCLK1 clock in deep sleep: {}".format(
                    clock_measure['clk_deep_sleep']))
                try:
                    clock_measure = amdsmi.amdsmi_get_clock_info(processors[i], amdsmi.AmdSmiClkType.DCLK1)
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  Current clock for domain DCLK1 is: {}".format(
                    clock_measure['clk']))
                print("  Max clock for domain DCLK1 is: {}".format(
                    clock_measure['max_clk']))
                print("  Min clock for domain DCLK1 is: {}".format(
                    clock_measure['min_clk']))
                print("  Is DCLK1 clock in deep sleep: {}".format(
                    clock_measure['clk_deep_sleep']))
            print("\n")


    if False: # Tested in Unit Tests
        def test_driver_info(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_gpu_driver_info \n")
                    driver_info = amdsmi.amdsmi_get_gpu_driver_info(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("Driver info:  {}".format(driver_info))
            print("\n")


    if False: # Tested in Unit Tests
        # amdsmi_get_gpu_ecc_count is not supported in Navi2x, Navi3x, MI210, MI300A
        def test_ecc_count_block(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            gpu_blocks = {
                "INVALID": amdsmi.AmdSmiGpuBlock.INVALID,
                "UMC": amdsmi.AmdSmiGpuBlock.UMC,
                "SDMA": amdsmi.AmdSmiGpuBlock.SDMA,
                "GFX": amdsmi.AmdSmiGpuBlock.GFX,
                "MMHUB": amdsmi.AmdSmiGpuBlock.MMHUB,
                "ATHUB": amdsmi.AmdSmiGpuBlock.ATHUB,
                "PCIE_BIF": amdsmi.AmdSmiGpuBlock.PCIE_BIF,
                "HDP": amdsmi.AmdSmiGpuBlock.HDP,
                "XGMI_WAFL": amdsmi.AmdSmiGpuBlock.XGMI_WAFL,
                "DF": amdsmi.AmdSmiGpuBlock.DF,
                "SMN": amdsmi.AmdSmiGpuBlock.SMN,
                "SEM": amdsmi.AmdSmiGpuBlock.SEM,
                "MP0": amdsmi.AmdSmiGpuBlock.MP0,
                "MP1": amdsmi.AmdSmiGpuBlock.MP1,
                "FUSE": amdsmi.AmdSmiGpuBlock.FUSE,
                "MCA": amdsmi.AmdSmiGpuBlock.MCA,
                "VCN": amdsmi.AmdSmiGpuBlock.VCN,
                "JPEG": amdsmi.AmdSmiGpuBlock.JPEG,
                "IH": amdsmi.AmdSmiGpuBlock.IH,
                "MPIO": amdsmi.AmdSmiGpuBlock.MPIO,
                "RESERVED": amdsmi.AmdSmiGpuBlock.RESERVED
            }
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                print("\n###Test amdsmi_get_gpu_ecc_count \n")
                for block_name, block_code in gpu_blocks.items():
                    try:
                        ecc_count = amdsmi.amdsmi_get_gpu_ecc_count(processors[i], block_code)
                    except amdsmi.AmdSmiLibraryException as e:
                        self._check_exception(e)
                        continue
                    print("  Number of uncorrectable errors for {}: {}".format(
                        block_name, ecc_count['uncorrectable_count']))
                    print("  Number of correctable errors for {}: {}".format(
                        block_name, ecc_count['correctable_count']))
                    print("  Number of deferred errors for {}: {}".format(
                        block_name, ecc_count['deferred_count']))
                    self.assertGreaterEqual(ecc_count['uncorrectable_count'], 0)
                    self.assertGreaterEqual(ecc_count['correctable_count'], 0)
                    self.assertGreaterEqual(ecc_count['deferred_count'], 0)
                print("\n")
            print("\n")


    if False: # Tested in Unit Tests
        def test_ecc_count_total(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_gpu_total_ecc_count \n")
                    ecc_info = amdsmi.amdsmi_get_gpu_total_ecc_count(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("Number of uncorrectable errors: {}".format(
                    ecc_info['uncorrectable_count']))
                print("Number of correctable errors: {}".format(
                    ecc_info['correctable_count']))
                print("Number of deferred errors: {}".format(
                    ecc_info['deferred_count']))
                self.assertGreaterEqual(ecc_info['uncorrectable_count'], 0)
                self.assertGreaterEqual(ecc_info['correctable_count'], 0)
                self.assertGreaterEqual(ecc_info['deferred_count'], 0)
            print("\n")


    if False: # Tested in Unit Tests
        def test_fw_info(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_fw_info \n")
                    fw_info = amdsmi.amdsmi_get_fw_info(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                num_fw_blocks = len(fw_info['fw_list'])
                self.assertLessEqual(num_fw_blocks, len(amdsmi.AmdSmiFwBlock))
                for fw in fw_info['fw_list']:
                    # Skip firmware blocks with version 0 as they are not valid or not present
                    if fw['fw_version'] != 0:
                        print("  FW name:           {}".format(
                            str(fw['fw_name'])))
                        print("  FW version:        {}".format(
                            fw['fw_version']))
            print("\n")


    if False: # Tested in Unit Tests
        def test_gpu_activity(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_gpu_activity \n")
                    engine_usage = amdsmi.amdsmi_get_gpu_activity(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  engine_usage['gfx_activity'] is: {} %".format(
                    engine_usage['gfx_activity']))
                print("  engine_usage['umc_activity'] is: {} %".format(
                    engine_usage['umc_activity']))
                print("  engine_usage['mm_activity'] is: {} %".format(
                    engine_usage['mm_activity']))
            print("\n")


    if False: # Tested in Unit Tests
        def test_memory_usage(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_gpu_memory_usage \n")
                    memory_usage = amdsmi.amdsmi_get_gpu_memory_usage(processors[i], amdsmi.AmdSmiMemoryType.VRAM)
                    print("  memory_usage for VRAM is: {}".format(memory_usage))
                    memory_usage = amdsmi.amdsmi_get_gpu_memory_usage(processors[i], amdsmi.AmdSmiMemoryType.VIS_VRAM)
                    print("  memory_usage for VIS_VRAM is: {}".format(memory_usage))
                    memory_usage = amdsmi.amdsmi_get_gpu_memory_usage(processors[i], amdsmi.AmdSmiMemoryType.GTT)
                    print("  memory_usage for GTT is: {}".format(memory_usage))
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
            print("\n")


    if False: # Tested in Unit Tests
        def test_pcie_info(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_pcie_info \n")
                    pcie_info = amdsmi.amdsmi_get_pcie_info(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  pcie_info['pcie_metric']['pcie_width'] is: {}".format(
                    pcie_info['pcie_metric']['pcie_width']))
                print("  pcie_info['pcie_static']['max_pcie_width'] is: {} ".format(
                    pcie_info['pcie_static']['max_pcie_width']))
                print("  pcie_info['pcie_metric']['pcie_speed'] is: {} MT/s".format(
                    pcie_info['pcie_metric']['pcie_speed']))
                print("  pcie_info['pcie_static']['max_pcie_speed'] is: {} ".format(
                    pcie_info['pcie_static']['max_pcie_speed']))
                print("  pcie_info['pcie_static']['pcie_interface_version'] is: {}".format(
                    pcie_info['pcie_static']['pcie_interface_version']))
                print("  pcie_info['pcie_static']['slot_type'] is: {}".format(
                    pcie_info['pcie_static']['slot_type']))
                print("  pcie_info['pcie_metric']['pcie_replay_count'] is: {}".format(
                    pcie_info['pcie_metric']['pcie_replay_count']))
                print("  pcie_info['pcie_metric']['pcie_bandwidth'] is: {}".format(
                    pcie_info['pcie_metric']['pcie_bandwidth']))
                print("  pcie_info['pcie_metric']['pcie_l0_to_recovery_count'] is: {}".format(
                    pcie_info['pcie_metric']['pcie_l0_to_recovery_count']))
                print("  pcie_info['pcie_metric']['pcie_replay_roll_over_count'] is: {}".format(
                    pcie_info['pcie_metric']['pcie_replay_roll_over_count']))
                print("  pcie_info['pcie_metric']['pcie_nak_sent_count'] is: {}".format(
                    pcie_info['pcie_metric']['pcie_nak_sent_count']))
                print("  pcie_info['pcie_metric']['pcie_nak_received_count'] is: {}".format(
                    pcie_info['pcie_metric']['pcie_nak_received_count']))
                print("  pcie_info['pcie_metric']['pcie_lc_perf_other_end_recovery_count'] is: {}".format(
                    pcie_info['pcie_metric']['pcie_lc_perf_other_end_recovery_count']))
            print("\n")


    if False: # Tested in Unit Tests
        def test_power_info(self):
            self._print_func_name('')
            for i, gpu in enumerate(self.processors):
                try:
                    print("\n###Test amdsmi_get_power_info \n")
                    power_info = amdsmi.amdsmi_get_power_info(gpu)
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  power_info['current_socket_power'] is: {}".format(
                    power_info['current_socket_power']))
                print("  power_info['average_socket_power'] is: {}".format(
                    power_info['average_socket_power']))
                print("  power_info['gfx_voltage'] is: {}".format(
                    power_info['gfx_voltage']))
                print("  power_info['soc_voltage'] is: {}".format(
                    power_info['soc_voltage']))
                print("  power_info['mem_voltage'] is: {}".format(
                    power_info['mem_voltage']))
                print("  power_info['power_limit'] is: {}".format(
                    power_info['power_limit']))
                try:
                    print("\n###Test amdsmi_get_power_cap_info \n")
                    power_cap_info = amdsmi.amdsmi_get_power_cap_info(gpu)
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  power_info['dpm_cap'] is: {}".format(
                    power_cap_info['dpm_cap']))
                print("  power_info['power_cap'] is: {}".format(
                    power_cap_info['power_cap']))
                try:
                    print("\n###Test amdsmi_is_gpu_power_management_enabled \n")
                    is_power_management_enabled = amdsmi.amdsmi_is_gpu_power_management_enabled(gpu)
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  Power management enabled: {}".format(
                    is_power_management_enabled))
            print("\n")


    if False: # Tested in Unit Tests
        def test_process_list(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_gpu_process_list \n")
                    process_list = amdsmi.amdsmi_get_gpu_process_list(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  Process list: {}".format(process_list))
            print("\n")

    if False: # Tested in Unit Tests
        def test_processor_type(self):
            self._print_func_name('')
            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_processor_type \n")
                    processor_type = amdsmi.amdsmi_get_processor_type(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                if isinstance(processor_type, dict) and 'processor_type' in processor_type:
                    print("  Processor type is: {}".format(processor_type['processor_type']))
                else:
                    print("  Processor type (non-dict): {}".format(processor_type))
                    self.assertIsInstance(processor_type, (str, int), "Unexpected processor_type type")
            print("\n")

    if False: # Tested in Unit Tests
        # amdsmi_get_gpu_ras_block_features_enabled is not supported in Navi2x, Navi3x
        def test_ras_block_features_enabled(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_gpu_ras_block_features_enabled \n")
                    ras_enabled = amdsmi.amdsmi_get_gpu_ras_block_features_enabled(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                for j in range(0, len(ras_enabled)):
                    print("  RAS status for {} is: {}".format(ras_enabled[j]['block'], ras_enabled[j]['status']))
            print("\n")


    if False: # Tested in Unit Tests
        # amdsmi_get_gpu_ras_feature_info is not supported in Navi2x, Navi3x
        def test_ras_feature_info(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_gpu_ras_feature_info \n")
                    ras_feature = amdsmi.amdsmi_get_gpu_ras_feature_info(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                if ras_feature != None:
                    print("RAS eeprom version: {}".format(ras_feature['eeprom_version']))
                    print("RAS parity schema: {}".format(ras_feature['parity_schema']))
                    print("RAS single bit schema: {}".format(ras_feature['single_bit_schema']))
                    print("RAS double bit schema: {}".format(ras_feature['double_bit_schema']))
                    print("Poisoning supported: {}".format(ras_feature['poison_schema']))
            print("\n")



    if False: # Tested in Unit Tests
        def test_temperature_metric(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_temp_metric \n")
                    temperature_measure = amdsmi.amdsmi_get_temp_metric(
                        processors[i], amdsmi.AmdSmiTemperatureType.HOTSPOT, amdsmi.AmdSmiTemperatureMetric.CURRENT)
                    print("  Current temperature for HOTSPOT is: {}".format(
                        temperature_measure))
                    temperature_measure = amdsmi.amdsmi_get_temp_metric(
                        processors[i], amdsmi.AmdSmiTemperatureType.VRAM, amdsmi.AmdSmiTemperatureMetric.CURRENT)
                    print("  Current temperature for VRAM is: {}".format(
                        temperature_measure))
                    print("\n###Test amdsmi_get_temp_metric \n")
                    temperature_measure = amdsmi.amdsmi_get_temp_metric(
                        processors[i], amdsmi.AmdSmiTemperatureType.HOTSPOT, amdsmi.AmdSmiTemperatureMetric.CRITICAL)
                    print("  Limit (critical) temperature for HOTSPOT is: {}".format(
                        temperature_measure))
                    temperature_measure = amdsmi.amdsmi_get_temp_metric(
                        processors[i], amdsmi.AmdSmiTemperatureType.VRAM, amdsmi.AmdSmiTemperatureMetric.CRITICAL)
                    print("  Limit (critical) temperature for VRAM is: {}".format(
                        temperature_measure))
                    print("\n###Test amdsmi_get_temp_metric \n")
                    temperature_measure = amdsmi.amdsmi_get_temp_metric(
                        processors[i], amdsmi.AmdSmiTemperatureType.HOTSPOT, amdsmi.AmdSmiTemperatureMetric.EMERGENCY)
                    print("  Shutdown (emergency) temperature for HOTSPOT is: {}".format(
                        temperature_measure))
                    temperature_measure = amdsmi.amdsmi_get_temp_metric(
                        processors[i], amdsmi.AmdSmiTemperatureType.VRAM, amdsmi.AmdSmiTemperatureMetric.EMERGENCY)
                    print("  Shutdown (emergency) temperature for VRAM is: {}".format(
                        temperature_measure))
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
            print("\n")


    if False: # Tested in Unit Tests
        # AmdSmiTemperatureType.EDGE is not supported in MI300A, MI300X
        def test_temperature_metric_edge(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_temp_metric \n")
                    temperature_measure = amdsmi.amdsmi_get_temp_metric(
                        processors[i], amdsmi.AmdSmiTemperatureType.EDGE, amdsmi.AmdSmiTemperatureMetric.CURRENT)
                    print("  Current temperature for EDGE is: {}".format(
                        temperature_measure))
                    temperature_measure = amdsmi.amdsmi_get_temp_metric(
                        processors[i], amdsmi.AmdSmiTemperatureType.EDGE, amdsmi.AmdSmiTemperatureMetric.CRITICAL)
                    print("  Limit (critical) temperature for EDGE is: {}".format(
                        temperature_measure))
                    temperature_measure = amdsmi.amdsmi_get_temp_metric(
                        processors[i], amdsmi.AmdSmiTemperatureType.EDGE, amdsmi.AmdSmiTemperatureMetric.EMERGENCY)
                    print("  Shutdown (emergency) temperature for EDGE is: {}".format(
                        temperature_measure))
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
            print("\n")


    if False: # Tested in Unit Tests
        def test_temperature_metric_plx(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_temp_metric \n")
                    temperature_measure = amdsmi.amdsmi_get_temp_metric(
                        processors[i], amdsmi.AmdSmiTemperatureType.PLX, amdsmi.AmdSmiTemperatureMetric.CURRENT)
                    print("  Current temperature for PLX is: {}".format(
                        temperature_measure))
                    temperature_measure = amdsmi.amdsmi_get_temp_metric(
                        processors[i], amdsmi.AmdSmiTemperatureType.PLX, amdsmi.AmdSmiTemperatureMetric.CRITICAL)
                    print("  Limit (critical) temperature for PLX is: {}".format(
                        temperature_measure))
                    temperature_measure = amdsmi.amdsmi_get_temp_metric(
                        processors[i], amdsmi.AmdSmiTemperatureType.PLX, amdsmi.AmdSmiTemperatureMetric.EMERGENCY)
                    print("  Shutdown (emergency) temperature for PLX is: {}".format(
                        temperature_measure))
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
            print("\n")


    if False: # Tested in Unit Tests
        # AmdSmiTemperatureType.HBM_0, HBM_1, HBM_2, HBM_3 are not supported in Navi2x, Navi3x, MI210, MI300A
        def test_temperature_metric_hbm(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            temp_types = {
                "HBM_0": amdsmi.AmdSmiTemperatureType.HBM_0,
                "HBM_1": amdsmi.AmdSmiTemperatureType.HBM_1,
                "HBM_2": amdsmi.AmdSmiTemperatureType.HBM_2,
                "HBM_3": amdsmi.AmdSmiTemperatureType.HBM_3,
            }
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                print("\n###Test amdsmi_get_temp_metric \n")
                for temp_type_name, temp_type_code in temp_types.items():
                    try:
                        temperature_measure = amdsmi.amdsmi_get_temp_metric(
                            processors[i], temp_type_code, amdsmi.AmdSmiTemperatureMetric.CURRENT)
                        print("  Current temperature for {} is: {}".format(
                            temp_type_name, temperature_measure))
                        temperature_measure = amdsmi.amdsmi_get_temp_metric(
                            processors[i], temp_type_code, amdsmi.AmdSmiTemperatureMetric.CRITICAL)
                        print("  Limit (critical) temperature for {} is: {}".format(
                            temp_type_name, temperature_measure))
                        temperature_measure = amdsmi.amdsmi_get_temp_metric(
                            processors[i], temp_type_code, amdsmi.AmdSmiTemperatureMetric.EMERGENCY)
                        print("  Shutdown (emergency) temperature for {} is: {}".format(
                            temp_type_name, temperature_measure))
                    except amdsmi.AmdSmiLibraryException as e:
                        self._check_exception(e)
                        continue
            print("\n")


    if False: # Tested in Unit Tests
        def test_vbios_info(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_gpu_vbios_info \n")
                    vbios_info = amdsmi.amdsmi_get_gpu_vbios_info(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                self._print_vbios_info(vbios_info)
            print("\n")

    if False: # Tested in Unit Tests
        def test_vendor_name(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_gpu_vendor_name \n")
                    vendor_name = amdsmi.amdsmi_get_gpu_vendor_name(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  Vendor name is: {}".format(vendor_name))
            print("\n")

    if False: # Tested in Unit Tests
        # @unittest.SkipTest
        def test_accelerator_partition_profile(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_gpu_accelerator_partition_profile \n")
                    accelerator_partition = amdsmi.amdsmi_get_gpu_accelerator_partition_profile(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  Current partition id: {}".format(
                    accelerator_partition['partition_id']))
                print("  Profile_type: {}".format(
                    accelerator_partition['partition_profile']['profile_type']))
                print("  profile_index: {}".format(
                    accelerator_partition['partition_profile']['profile_index']))
                print("  memory_caps: {}".format(
                    accelerator_partition['partition_profile']['memory_caps']))
                print("  num_resources: {}".format(
                    accelerator_partition['partition_profile']['num_resources']))
            print("\n")


    if False: # Tested in Unit Tests
        # Requires sudo (to see full resource/config detail).
        # Should only be supported on MI300+ ASICs
        def test_accelerator_partition_profile_config(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_gpu_accelerator_partition_profile_config \n")
                    profile_config = amdsmi.amdsmi_get_gpu_accelerator_partition_profile_config(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  num_profiles: {}".format(profile_config['num_profiles']))
                print("  num_resource_profiles: {}".format(profile_config['num_resource_profiles']))
                print("  default_profile_index: {}".format(profile_config['default_profile_index']))
                for p in profile_config['profiles']:
                    print("\t\t  profile_type: {}".format(p['profile_type']))
                    print("\t\t  num_partitions: {}".format(p['num_partitions']))
                    print("\t\t  profile_index: {}".format(p['profile_index']))
                    print("\t\t  num_resources: {}".format(p['num_resources']))
                    for r in range(0, p['num_resources']):
                        print("\t\t\t  profile_index: {}".format(p['resources'][r]['profile_index']))
                        print("\t\t\t  resource_type: {}".format(p['resources'][r]['resource_type']))
                        print("\t\t\t  partition_resource: {}".format(p['resources'][r]['partition_resource']))
                        print("\t\t\t  num_partitions_share_resource: {}".format(
                            p['resources'][r]['num_partitions_share_resource']))
            print("\n")


    if False: # Tested in Unit Tests
        # amdsmi_get_violation_status is only supported on MI300+ ASICs
        # We should expect a not supported status for Navi / MI100 / MI2x ASICs
        def test_get_violation_status(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
                try:
                    print("\n###Test amdsmi_get_violation_status \n")
                    violation_status = amdsmi.amdsmi_get_violation_status(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  Reference Timestamp: {}".format(
                    violation_status['reference_timestamp']))
                print("  Violation Timestamp: {}".format(
                    violation_status['violation_timestamp']))

                print(" Current Prochot Thrm Accumulated (Count): {}".format(
                    violation_status['acc_prochot_thrm']))
                print(" Current PVIOL (acc_ppt_pwr) Accumulated (Count): {}".format(
                    violation_status['acc_ppt_pwr']))
                print(" Current TVIOL (acc_socket_thrm) Accumulated (Count): {}".format(
                    violation_status['acc_socket_thrm']))
                print(" Current VR_THRM Accumulated (Count): {}".format(
                    violation_status['acc_vr_thrm']))
                print(" Current HBM Thrm Accumulated (Count): {}".format(
                    violation_status['acc_hbm_thrm']))
                print(" Current GFX CLK Below Host Limit Accumulated (Count): {}".format(
                    violation_status['acc_gfx_clk_below_host_limit']))

                print(" Prochot Thrm Violation (%): {}".format(
                    violation_status['per_prochot_thrm']))
                print(" PVIOL (per_ppt_pwr) (%): {}".format(
                    violation_status['per_ppt_pwr']))
                print(" TVIOL (per_socket_thrm) (%): {}".format(
                    violation_status['per_socket_thrm']))
                print(" VR_THRM Violation (%): {}".format(
                    violation_status['per_vr_thrm']))
                print(" HBM Thrm Violation (%): {}".format(
                    violation_status['per_hbm_thrm']))
                print(" GFX CLK Below Host Limit Violation (%): {}".format(
                    violation_status['per_gfx_clk_below_host_limit']))

                print(" Prochot Thrm Violation (bool): {}".format(
                    violation_status['active_prochot_thrm']))
                print(" PVIOL (active_ppt_pwr) (bool): {}".format(
                    violation_status['active_ppt_pwr']))
                print(" TVIOL (active_socket_thrm) (bool): {}".format(
                    violation_status['active_socket_thrm']))
                print(" VR_THRM Violation (bool): {}".format(
                    violation_status['active_vr_thrm']))
                print(" HBM Thrm Violation (bool): {}".format(
                    violation_status['active_hbm_thrm']))
                print(" GFX CLK Below Host Limit Violation (bool): {}".format(
                    violation_status['active_gfx_clk_below_host_limit']))
            print("\n")


    if False: # Tested in Unit Tests
        # Add test for amdsmi_get_gpu_reg_table_info
        def test_gpu_reg_table_info(self):
            self._print_func_name('')

            print("\n\n###Test amdsmi_get_gpu_reg_table_info")
            processors = amdsmi.amdsmi_get_processor_handles()
            for i in range(0, len(processors)):
                print("\n\n###Test Processor {}".format(i))
                try:
                    print("\n###Test amdsmi_get_gpu_reg_table_info \n")
                    reg_table_info = amdsmi.amdsmi_get_gpu_reg_table_info(processors[i], amdsmi.amdsmi_interface.AmdSmiRegType.PCIE)
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  reg_table_info['reg_table'] is: {}".format(
                    reg_table_info))
            print("\n")


    if False: # Tested in Unit Tests
        def test_get_gpu_revision(self):
            self._print_func_name('')

            processors = amdsmi.amdsmi_get_processor_handles()
            self.assertGreaterEqual(len(processors), 1)
            self.assertLessEqual(len(processors), self.max_num_physical_devices)
            for i in range(0, len(processors)):
                bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
                print(f"\n\n###Test Processor {i}, bdf: {bdf}")
                try:
                    print("\n###Test amdsmi_get_gpu_revision \n")
                    revision = amdsmi.amdsmi_get_gpu_revision(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print(f"  GPU revision is: {revision}")
            print("\n")


    if False: # Tested in Unit Tests
        # Add test for amdsmi_get_gpu_pm_metrics_info
        def test_gpu_pm_metrics_info(self):
            self._print_func_name('')

            print("\n\n###Test amdsmi_get_gpu_pm_metrics_info")
            processors = amdsmi.amdsmi_get_processor_handles()
            for i in range(0, len(processors)):
                print("\n\n###Test Processor {}".format(i))
                try:
                    print("\n###Test amdsmi_get_gpu_pm_metrics_info \n")
                    pm_metrics_info = amdsmi.amdsmi_get_gpu_pm_metrics_info(processors[i])
                except amdsmi.AmdSmiLibraryException as e:
                    self._check_exception(e)
                    continue
                print("  pm_metrics_info['pm_metrics'] is: {}".format(
                    pm_metrics_info))
            print("\n")


    if False: # Tested in Unit Tests
        def test_walkthrough(self):
            self._print_func_name('')
            print("\n\n#######################################################################")
            print("========> test_walkthrough start <========\n")
            self.test_asic_kfd_info()
            self.test_power_info()
            self.test_vbios_info()
            self.test_board_info()
            self.test_fw_info()
            self.test_driver_info()
            print("\n========> test_walkthrough end <========")
            print("#######################################################################\n")

    # Unstable on workstation cards
    # def test_walkthrough_multiprocess(self):
    #     print("\n\n========> test_walkthrough_multiprocess start <========\n")
    #     processors = amdsmi.amdsmi_get_processor_handles()
    #     self.assertGreaterEqual(len(processors), 1)
    #     self.assertLessEqual(len(processors), self.max_num_physical_devices)
    #     p0 = multiprocessing.Process(target=walk_through, args=[self])
    #     p1 = multiprocessing.Process(target=walk_through, args=[self])
    #     p2 = multiprocessing.Process(target=walk_through, args=[self])
    #     p3 = multiprocessing.Process(target=walk_through, args=[self])
    #     p0.start()
    #     p1.start()
    #     p2.start()
    #     p3.start()
    #     p0.join()
    #     p1.join()
    #     p2.join()
    #     p3.join()
    #     print("\n========> test_walkthrough_multiprocess end <========\n")

    # Unstable on workstation cards
    # def test_walkthrough_multithread(self):
    #     print("\n\n========> test_walkthrough_multithread start <========\n")
    #     processors = amdsmi.amdsmi_get_processor_handles()
    #     self.assertGreaterEqual(len(processors), 1)
    #     self.assertLessEqual(len(processors), self.max_num_physical_devices)
    #     t0 = threading.Thread(target=walk_through, args=[self])
    #     t1 = threading.Thread(target=walk_through, args=[self])
    #     t2 = threading.Thread(target=walk_through, args=[self])
    #     t3 = threading.Thread(target=walk_through, args=[self])
    #     t0.start()
    #     t1.start()
    #     t2.start()
    #     t3.start()
    #     t0.join()
    #     t1.join()
    #     t2.join()
    #     t3.join()
    #     print("\n========> test_walkthrough_multithread end <========\n")

    # # Unstable - do not run
    # def test_z_gpureset_asicinfo_multithread(self):
    #     def get_asic_info(processor):
    #         try:
    #             print("\n###Test amdsmi_get_gpu_asic_info \n")
    #             asic_info = amdsmi.amdsmi_get_gpu_asic_info(processor)
    #         except amdsmi.AmdSmiLibraryException as e:
    #             self._check_exception(e)
    #             continue
    #         print("  asic_info['market_name'] is: {}".format(
    #             asic_info['market_name']))
    #         print("  asic_info['vendor_id'] is: {}".format(
    #             asic_info['vendor_id']))
    #         print("  asic_info['vendor_name'] is: {}".format(
    #             asic_info['vendor_name']))
    #         print("  asic_info['device_id'] is: {}".format(
    #             asic_info['device_id']))
    #         print("  asic_info['rev_id'] is: {}".format(
    #             asic_info['rev_id']))
    #         print("  asic_info['asic_serial'] is: {}".format(
    #             asic_info['asic_serial']))
    #         print("  asic_info['oam_id'] is: {}\n".format(
    #             asic_info['oam_id']))
    #     def gpu_reset(processor):
    #         print("\n###Test amdsmi_reset_gpu \n")
    #         amdsmi.amdsmi_reset_gpu(processor)
    #         print("  GPU reset completed.\n")
    #     print("\n\n========> test_z_gpureset_asicinfo_multithread start <========\n")
    #     processors = amdsmi.amdsmi_get_processor_handles()
    #     self.assertGreaterEqual(len(processors), 1)
    #     self.assertLessEqual(len(processors), self.max_num_physical_devices)
    #     for i in range(0, len(processors)):
    #         bdf = amdsmi.amdsmi_get_gpu_device_bdf(processors[i])
    #         print("\n\n###Test Processor {}, bdf: {}".format(i, bdf))
    #         t0 = threading.Thread(target=get_asic_info, args=[processors[i]])
    #         t1 = threading.Thread(target=gpu_reset, args=[processors[i]])
    #         # t2 = threading.Thread(target=walk_through, args=[self])
    #         # t3 = threading.Thread(target=walk_through, args=[self])
    #         t0.start()
    #         t1.start()
    #         # t2.start()
    #         # t3.start()
    #         t0.join()
    #         t1.join()
    #         # t2.join()
    #         # t3.join()
    #     print("\n========> test_z_gpureset_asicinfo_multithread end <========\n")


def print_test_ids(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            print_test_ids(test)
        else:
            print(" -", test.id())

if __name__ == '__main__':
    verbose=1
    if '-q' in sys.argv or '--quiet' in sys.argv:
        verbose=0
    elif '-v' in sys.argv or '--verbose' in sys.argv:
        verbose=2
    has_info_printed = False

    if verbose:
        print("AMD SMI Integration Tests")

    if False:
        # If no -k or --keyword argument is given, print all available tests
        if not ('-k' in sys.argv or '--keyword' in sys.argv):
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(sys.modules[__name__])
            print("==============================================================")
            print("Available tests:")
            print_test_ids(suite)

        # Provide Legend for test results, otherwise it is not clear what the output means
        print("==============================================================")
        print("Legend: . = pass, s = skipped, F = fail, E = error")
        print("==============================================================")
        print("Running tests...\n")

    # Detect if ran without sudo or root privileges
    if os.geteuid() != 0:
        print("Warning: Some tests may require elevated privileges (sudo/root) to run completely.\n")
        print("Please relaunch with elevated privileges.\n")
        sys.exit(1)

    runner = unittest.TextTestRunner(verbosity=verbose)
    unittest.main(testRunner=runner)
    sys.exit(0)


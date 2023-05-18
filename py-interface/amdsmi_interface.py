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

import ctypes
import re
from typing import Union, Any, Dict, List, Tuple
from enum import IntEnum
from collections.abc import Iterable

from . import amdsmi_wrapper
from .amdsmi_exception import *

class AmdSmiInitFlags(IntEnum):
    ALL_DEVICES = amdsmi_wrapper.AMDSMI_INIT_ALL_DEVICES
    AMD_CPUS = amdsmi_wrapper.AMDSMI_INIT_AMD_CPUS
    AMD_GPUS = amdsmi_wrapper.AMDSMI_INIT_AMD_GPUS
    NON_AMD_CPUS = amdsmi_wrapper.AMDSMI_INIT_NON_AMD_CPUS
    NON_AMD_GPUS = amdsmi_wrapper.AMDSMI_INIT_NON_AMD_GPUS


class AmdSmiContainerTypes(IntEnum):
    LXC = amdsmi_wrapper.CONTAINER_LXC
    DOCKER = amdsmi_wrapper.CONTAINER_DOCKER


class AmdSmiDeviceType(IntEnum):
    UNKNOWN_DEVICE = amdsmi_wrapper.UNKNOWN
    AMD_GPU_DEVICE = amdsmi_wrapper.AMD_GPU
    AMD_CPU_DEVICE = amdsmi_wrapper.AMD_CPU
    NON_AMD_GPU_DEVICE = amdsmi_wrapper.NON_AMD_GPU
    NON_AMD_CPU_DEVICE = amdsmi_wrapper.NON_AMD_CPU


class AmdSmiMmIp(IntEnum):
    UVD = amdsmi_wrapper.AMDSMI_MM_UVD
    VCE = amdsmi_wrapper.AMDSMI_MM_VCE
    VCN = amdsmi_wrapper.AMDSMI_MM_VCN


class AmdSmiFwBlock(IntEnum):
    FW_ID_SMU = amdsmi_wrapper.FW_ID_SMU
    FW_ID_CP_CE = amdsmi_wrapper.FW_ID_CP_CE
    FW_ID_CP_PFP = amdsmi_wrapper.FW_ID_CP_PFP
    FW_ID_CP_ME = amdsmi_wrapper.FW_ID_CP_ME
    FW_ID_CP_MEC_JT1 = amdsmi_wrapper.FW_ID_CP_MEC_JT1
    FW_ID_CP_MEC_JT2 = amdsmi_wrapper.FW_ID_CP_MEC_JT2
    FW_ID_CP_MEC1 = amdsmi_wrapper.FW_ID_CP_MEC1
    FW_ID_CP_MEC2 = amdsmi_wrapper.FW_ID_CP_MEC2
    FW_ID_RLC = amdsmi_wrapper.FW_ID_RLC
    FW_ID_SDMA0 = amdsmi_wrapper.FW_ID_SDMA0
    FW_ID_SDMA1 = amdsmi_wrapper.FW_ID_SDMA1
    FW_ID_SDMA2 = amdsmi_wrapper.FW_ID_SDMA2
    FW_ID_SDMA3 = amdsmi_wrapper.FW_ID_SDMA3
    FW_ID_SDMA4 = amdsmi_wrapper.FW_ID_SDMA4
    FW_ID_SDMA5 = amdsmi_wrapper.FW_ID_SDMA5
    FW_ID_SDMA6 = amdsmi_wrapper.FW_ID_SDMA6
    FW_ID_SDMA7 = amdsmi_wrapper.FW_ID_SDMA7
    FW_ID_VCN = amdsmi_wrapper.FW_ID_VCN
    FW_ID_UVD = amdsmi_wrapper.FW_ID_UVD
    FW_ID_VCE = amdsmi_wrapper.FW_ID_VCE
    FW_ID_ISP = amdsmi_wrapper.FW_ID_ISP
    FW_ID_DMCU_ERAM = amdsmi_wrapper.FW_ID_DMCU_ERAM
    FW_ID_DMCU_ISR = amdsmi_wrapper.FW_ID_DMCU_ISR
    FW_ID_RLC_RESTORE_LIST_GPM_MEM = amdsmi_wrapper.FW_ID_RLC_RESTORE_LIST_GPM_MEM
    FW_ID_RLC_RESTORE_LIST_SRM_MEM = amdsmi_wrapper.FW_ID_RLC_RESTORE_LIST_SRM_MEM
    FW_ID_RLC_RESTORE_LIST_CNTL = amdsmi_wrapper.FW_ID_RLC_RESTORE_LIST_CNTL
    FW_ID_RLC_V = amdsmi_wrapper.FW_ID_RLC_V
    FW_ID_MMSCH = amdsmi_wrapper.FW_ID_MMSCH
    FW_ID_PSP_SYSDRV = amdsmi_wrapper.FW_ID_PSP_SYSDRV
    FW_ID_PSP_SOSDRV = amdsmi_wrapper.FW_ID_PSP_SOSDRV
    FW_ID_PSP_TOC = amdsmi_wrapper.FW_ID_PSP_TOC
    FW_ID_PSP_KEYDB = amdsmi_wrapper.FW_ID_PSP_KEYDB
    FW_ID_DFC = amdsmi_wrapper.FW_ID_DFC
    FW_ID_PSP_SPL = amdsmi_wrapper.FW_ID_PSP_SPL
    FW_ID_DRV_CAP = amdsmi_wrapper.FW_ID_DRV_CAP
    FW_ID_MC = amdsmi_wrapper.FW_ID_MC
    FW_ID_PSP_BL = amdsmi_wrapper.FW_ID_PSP_BL
    FW_ID_CP_PM4 = amdsmi_wrapper.FW_ID_CP_PM4
    FW_ID_ASD = amdsmi_wrapper.FW_ID_ASD
    FW_ID_TA_RAS = amdsmi_wrapper.FW_ID_TA_RAS
    FW_ID_XGMI = amdsmi_wrapper.FW_ID_XGMI
    FW_ID_RLC_SRLG = amdsmi_wrapper.FW_ID_RLC_SRLG
    FW_ID_RLC_SRLS = amdsmi_wrapper.FW_ID_RLC_SRLS
    FW_ID_SMC = amdsmi_wrapper.FW_ID_SMC
    FW_ID_DMCU = amdsmi_wrapper.FW_ID_DMCU


class AmdSmiClkType(IntEnum):
    SYS = amdsmi_wrapper.CLK_TYPE_SYS
    GFX = amdsmi_wrapper.CLK_TYPE_GFX
    DF = amdsmi_wrapper.CLK_TYPE_DF
    DCEF = amdsmi_wrapper.CLK_TYPE_DCEF
    SOC = amdsmi_wrapper.CLK_TYPE_SOC
    MEM = amdsmi_wrapper.CLK_TYPE_MEM
    PCIE = amdsmi_wrapper.CLK_TYPE_PCIE
    VCLK0 = amdsmi_wrapper.CLK_TYPE_VCLK0
    VCLK1 = amdsmi_wrapper.CLK_TYPE_VCLK1
    DCLK0 = amdsmi_wrapper.CLK_TYPE_DCLK0
    DCLK1 = amdsmi_wrapper.CLK_TYPE_DCLK1


class AmdSmiTemperatureType(IntEnum):
    EDGE = amdsmi_wrapper.TEMPERATURE_TYPE_EDGE
    JUNCTION = amdsmi_wrapper.TEMPERATURE_TYPE_JUNCTION
    VRAM = amdsmi_wrapper.TEMPERATURE_TYPE_VRAM
    HBM_0 = amdsmi_wrapper.TEMPERATURE_TYPE_HBM_0
    HBM_1 = amdsmi_wrapper.TEMPERATURE_TYPE_HBM_1
    HBM_2 = amdsmi_wrapper.TEMPERATURE_TYPE_HBM_2
    HBM_3 = amdsmi_wrapper.TEMPERATURE_TYPE_HBM_3
    PLX = amdsmi_wrapper.TEMPERATURE_TYPE_PLX


class AmdSmiDevPerfLevel(IntEnum):
    AUTO = amdsmi_wrapper.AMDSMI_DEV_PERF_LEVEL_AUTO
    LOW = amdsmi_wrapper.AMDSMI_DEV_PERF_LEVEL_LOW
    HIGH = amdsmi_wrapper.AMDSMI_DEV_PERF_LEVEL_HIGH
    MANUAL = amdsmi_wrapper.AMDSMI_DEV_PERF_LEVEL_MANUAL
    STABLE_STD = amdsmi_wrapper.AMDSMI_DEV_PERF_LEVEL_STABLE_STD
    STABLE_PEAK = amdsmi_wrapper.AMDSMI_DEV_PERF_LEVEL_STABLE_PEAK
    STABLE_MIN_MCLK = amdsmi_wrapper.AMDSMI_DEV_PERF_LEVEL_STABLE_MIN_MCLK
    STABLE_MIN_SCLK = amdsmi_wrapper.AMDSMI_DEV_PERF_LEVEL_STABLE_MIN_SCLK
    DETERMINISM = amdsmi_wrapper.AMDSMI_DEV_PERF_LEVEL_DETERMINISM
    UNKNOWN = amdsmi_wrapper.AMDSMI_DEV_PERF_LEVEL_UNKNOWN


class AmdSmiSwComponent(IntEnum):
    DRIVER = amdsmi_wrapper.AMDSMI_SW_COMP_DRIVER


class AmdSmiEventGroup(IntEnum):
    XGMI = amdsmi_wrapper.AMDSMI_EVNT_GRP_XGMI
    XGMI_DATA_OUT = amdsmi_wrapper.AMDSMI_EVNT_GRP_XGMI_DATA_OUT
    GRP_INVALID = amdsmi_wrapper.AMDSMI_EVNT_GRP_INVALID


class AmdSmiEventType(IntEnum):
    XGMI_0_NOP_TX = amdsmi_wrapper.AMDSMI_EVNT_XGMI_0_NOP_TX
    XGMI_0_REQUEST_TX = amdsmi_wrapper.AMDSMI_EVNT_XGMI_0_REQUEST_TX
    XGMI_0_RESPONSE_TX = amdsmi_wrapper.AMDSMI_EVNT_XGMI_0_RESPONSE_TX
    XGMI_0_BEATS_TX = amdsmi_wrapper.AMDSMI_EVNT_XGMI_0_BEATS_TX
    XGMI_1_NOP_TX = amdsmi_wrapper.AMDSMI_EVNT_XGMI_1_NOP_TX
    XGMI_1_REQUEST_TX = amdsmi_wrapper.AMDSMI_EVNT_XGMI_1_REQUEST_TX
    XGMI_1_RESPONSE_TX = amdsmi_wrapper.AMDSMI_EVNT_XGMI_1_RESPONSE_TX
    XGMI_1_BEATS_TX = amdsmi_wrapper.AMDSMI_EVNT_XGMI_1_BEATS_TX
    XGMI_DATA_OUT_0 = amdsmi_wrapper.AMDSMI_EVNT_XGMI_DATA_OUT_0
    XGMI_DATA_OUT_1 = amdsmi_wrapper.AMDSMI_EVNT_XGMI_DATA_OUT_1
    XGMI_DATA_OUT_2 = amdsmi_wrapper.AMDSMI_EVNT_XGMI_DATA_OUT_2
    XGMI_DATA_OUT_3 = amdsmi_wrapper.AMDSMI_EVNT_XGMI_DATA_OUT_3
    XGMI_DATA_OUT_4 = amdsmi_wrapper.AMDSMI_EVNT_XGMI_DATA_OUT_4
    XGMI_DATA_OUT_5 = amdsmi_wrapper.AMDSMI_EVNT_XGMI_DATA_OUT_5


class AmdSmiCounterCommand(IntEnum):
    CMD_START = amdsmi_wrapper.AMDSMI_CNTR_CMD_START
    CMD_STOP = amdsmi_wrapper.AMDSMI_CNTR_CMD_STOP


class AmdSmiEvtNotificationType(IntEnum):
    VMFAULT = amdsmi_wrapper.AMDSMI_EVT_NOTIF_VMFAULT
    THERMAL_THROTTLE = amdsmi_wrapper.AMDSMI_EVT_NOTIF_THERMAL_THROTTLE
    GPU_PRE_RESET = amdsmi_wrapper.AMDSMI_EVT_NOTIF_GPU_PRE_RESET
    GPU_POST_RESET = amdsmi_wrapper.AMDSMI_EVT_NOTIF_GPU_POST_RESET


class AmdSmiTemperatureMetric(IntEnum):
    CURRENT = amdsmi_wrapper.AMDSMI_TEMP_CURRENT
    MAX = amdsmi_wrapper.AMDSMI_TEMP_MAX
    MIN = amdsmi_wrapper.AMDSMI_TEMP_MIN
    MAX_HYST = amdsmi_wrapper.AMDSMI_TEMP_MAX_HYST
    MIN_HYST = amdsmi_wrapper.AMDSMI_TEMP_MIN_HYST
    CRITICAL = amdsmi_wrapper.AMDSMI_TEMP_CRITICAL
    CRITICAL_HYST = amdsmi_wrapper.AMDSMI_TEMP_CRITICAL_HYST
    EMERGENCY = amdsmi_wrapper.AMDSMI_TEMP_EMERGENCY
    EMERGENCY_HYST = amdsmi_wrapper.AMDSMI_TEMP_EMERGENCY_HYST
    CRIT_MIN = amdsmi_wrapper.AMDSMI_TEMP_CRIT_MIN
    CRIT_MIN_HYST = amdsmi_wrapper.AMDSMI_TEMP_CRIT_MIN_HYST
    OFFSET = amdsmi_wrapper.AMDSMI_TEMP_OFFSET
    LOWEST = amdsmi_wrapper.AMDSMI_TEMP_LOWEST
    HIGHEST = amdsmi_wrapper.AMDSMI_TEMP_HIGHEST


class AmdSmiVoltageMetric(IntEnum):
    CURRENT = amdsmi_wrapper.AMDSMI_VOLT_CURRENT
    MAX = amdsmi_wrapper.AMDSMI_VOLT_MAX
    MIN_CRIT = amdsmi_wrapper.AMDSMI_VOLT_MIN_CRIT
    MIN = amdsmi_wrapper.AMDSMI_VOLT_MIN
    MAX_CRIT = amdsmi_wrapper.AMDSMI_VOLT_MAX_CRIT
    AVERAGE = amdsmi_wrapper.AMDSMI_VOLT_AVERAGE
    LOWEST = amdsmi_wrapper.AMDSMI_VOLT_LOWEST
    HIGHEST = amdsmi_wrapper.AMDSMI_VOLT_HIGHEST


class AmdSmiVoltageType(IntEnum):
    VDDGFX = amdsmi_wrapper.AMDSMI_VOLT_TYPE_VDDGFX
    INVALID = amdsmi_wrapper.AMDSMI_VOLT_TYPE_INVALID


class AmdSmiPowerProfilePresetMasks(IntEnum):
    CUSTOM_MASK = amdsmi_wrapper.AMDSMI_PWR_PROF_PRST_CUSTOM_MASK
    VIDEO_MASK = amdsmi_wrapper.AMDSMI_PWR_PROF_PRST_VIDEO_MASK
    POWER_SAVING_MASK = amdsmi_wrapper.AMDSMI_PWR_PROF_PRST_POWER_SAVING_MASK
    COMPUTE_MASK = amdsmi_wrapper.AMDSMI_PWR_PROF_PRST_COMPUTE_MASK
    VR_MASK = amdsmi_wrapper.AMDSMI_PWR_PROF_PRST_VR_MASK
    THREE_D_FULL_SCR_MASK = amdsmi_wrapper.AMDSMI_PWR_PROF_PRST_3D_FULL_SCR_MASK
    BOOTUP_DEFAULT = amdsmi_wrapper.AMDSMI_PWR_PROF_PRST_BOOTUP_DEFAULT
    INVALID = amdsmi_wrapper.AMDSMI_PWR_PROF_PRST_INVALID


class AmdSmiGpuBlock(IntEnum):
    INVALID = amdsmi_wrapper.AMDSMI_GPU_BLOCK_INVALID
    UMC = amdsmi_wrapper.AMDSMI_GPU_BLOCK_UMC
    SDMA = amdsmi_wrapper.AMDSMI_GPU_BLOCK_SDMA
    GFX = amdsmi_wrapper.AMDSMI_GPU_BLOCK_GFX
    MMHUB = amdsmi_wrapper.AMDSMI_GPU_BLOCK_MMHUB
    ATHUB = amdsmi_wrapper.AMDSMI_GPU_BLOCK_ATHUB
    PCIE_BIF = amdsmi_wrapper.AMDSMI_GPU_BLOCK_PCIE_BIF
    HDP = amdsmi_wrapper.AMDSMI_GPU_BLOCK_HDP
    XGMI_WAFL = amdsmi_wrapper.AMDSMI_GPU_BLOCK_XGMI_WAFL
    DF = amdsmi_wrapper.AMDSMI_GPU_BLOCK_DF
    SMN = amdsmi_wrapper.AMDSMI_GPU_BLOCK_SMN
    SEM = amdsmi_wrapper.AMDSMI_GPU_BLOCK_SEM
    MP0 = amdsmi_wrapper.AMDSMI_GPU_BLOCK_MP0
    MP1 = amdsmi_wrapper.AMDSMI_GPU_BLOCK_MP1
    FUSE = amdsmi_wrapper.AMDSMI_GPU_BLOCK_FUSE
    RESERVED = amdsmi_wrapper.AMDSMI_GPU_BLOCK_RESERVED


class AmdSmiRasErrState(IntEnum):
    NONE = amdsmi_wrapper.AMDSMI_RAS_ERR_STATE_NONE
    DISABLED = amdsmi_wrapper.AMDSMI_RAS_ERR_STATE_DISABLED
    PARITY = amdsmi_wrapper.AMDSMI_RAS_ERR_STATE_PARITY
    SING_C = amdsmi_wrapper.AMDSMI_RAS_ERR_STATE_SING_C
    MULT_UC = amdsmi_wrapper.AMDSMI_RAS_ERR_STATE_MULT_UC
    POISON = amdsmi_wrapper.AMDSMI_RAS_ERR_STATE_POISON
    ENABLED = amdsmi_wrapper.AMDSMI_RAS_ERR_STATE_ENABLED
    INVALID = amdsmi_wrapper.AMDSMI_RAS_ERR_STATE_INVALID


class AmdSmiMemoryType(IntEnum):
    VRAM = amdsmi_wrapper.AMDSMI_MEM_TYPE_VRAM
    VIS_VRAM = amdsmi_wrapper.AMDSMI_MEM_TYPE_VIS_VRAM
    GTT = amdsmi_wrapper.AMDSMI_MEM_TYPE_GTT


class AmdSmiFreqInd(IntEnum):
    MIN = amdsmi_wrapper.AMDSMI_FREQ_IND_MIN
    MAX = amdsmi_wrapper.AMDSMI_FREQ_IND_MAX
    INVALID = amdsmi_wrapper.AMDSMI_FREQ_IND_INVALID


class AmdSmiXgmiStatus(IntEnum):
    NO_ERRORS = amdsmi_wrapper.AMDSMI_XGMI_STATUS_NO_ERRORS
    ERROR = amdsmi_wrapper.AMDSMI_XGMI_STATUS_ERROR
    MULTIPLE_ERRORS = amdsmi_wrapper.AMDSMI_XGMI_STATUS_MULTIPLE_ERRORS


class AmdSmiMemoryPageStatus(IntEnum):
    RESERVED = amdsmi_wrapper.AMDSMI_MEM_PAGE_STATUS_RESERVED
    PENDING = amdsmi_wrapper.AMDSMI_MEM_PAGE_STATUS_PENDING
    UNRESERVABLE = amdsmi_wrapper.AMDSMI_MEM_PAGE_STATUS_UNRESERVABLE


class AmdSmiIoLinkType(IntEnum):
    UNDEFINED = amdsmi_wrapper.AMDSMI_IOLINK_TYPE_UNDEFINED
    PCIEXPRESS = amdsmi_wrapper.AMDSMI_IOLINK_TYPE_PCIEXPRESS
    XGMI = amdsmi_wrapper.AMDSMI_IOLINK_TYPE_XGMI
    NUMIOLINKTYPES = amdsmi_wrapper.AMDSMI_IOLINK_TYPE_NUMIOLINKTYPES
    SIZE = amdsmi_wrapper.AMDSMI_IOLINK_TYPE_SIZE


class AmdSmiUtilizationCounterType(IntEnum):
    COARSE_GRAIN_GFX_ACTIVITY = amdsmi_wrapper.AMDSMI_COARSE_GRAIN_GFX_ACTIVITY
    COARSE_GRAIN_MEM_ACTIVITY = amdsmi_wrapper.AMDSMI_COARSE_GRAIN_MEM_ACTIVITY


class AmdSmiEventReader:
    def __init__(
        self, device_handle: amdsmi_wrapper.amdsmi_device_handle, *event_types
    ):
        if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
            raise AmdSmiParameterException(
                device_handle, amdsmi_wrapper.amdsmi_device_handle
            )
        if not isinstance(event_types, Iterable):
            raise AmdSmiParameterException(
                event_types, Iterable
            )

        for event_type in event_types:
            if not isinstance(event_type, AmdSmiEvtNotificationType):
                raise AmdSmiParameterException(
                    event_type, AmdSmiEvtNotificationType
                )

        self.device_handle = device_handle
        mask = 0
        for event_type in event_types:
            mask |= (1 << (int(event_type) - 1))

        _check_res(amdsmi_wrapper.amdsmi_init_event_notification(device_handle))
        _check_res(amdsmi_wrapper. amdsmi_set_event_notification_mask(
            device_handle, ctypes.c_uint64(mask)))

    def read(self, timestamp, num_elem=10):
        self.event_info = (
            amdsmi_wrapper.amdsmi_evt_notification_data_t * num_elem)()
        _check_res(
            amdsmi_wrapper. amdsmi_get_event_notification(
                ctypes.c_int(timestamp),
                ctypes.byref(ctypes.c_uint32(num_elem)),
                self.event_info,
            )
        )

        ret = list()
        for i in range(0, num_elem):
            if self.event_info[i].event in set(
                event.value for event in AmdSmiEvtNotificationType
            ):
                ret.append(
                    {
                        "device_handle": self.event_info[i].device_handle,
                        "event": AmdSmiEvtNotificationType(
                            self.event_info[i].event
                        ).name,
                        "message": self.event_info[i].message.decode("utf-8"),
                    }
                )

        return ret

    def stop(self):
        _check_res(amdsmi_wrapper.amdsmi_stop_event_notification(
            self.device_handle))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()


_AMDSMI_MAX_DRIVER_VERSION_LENGTH = 80
_AMDSMI_GPU_UUID_SIZE = 38
_AMDSMI_STRING_LENGTH = 80


def _format_bad_page_info(bad_page_info, bad_page_count: ctypes.c_uint32) -> List[Dict]:
    """
    Format bad page info data retrieved.

    Parameters:
        bad_page_info(`POINTER(amdsmi_retired_page_record_t)`): Pointer to bad page info
        retrieved.
        bad_page_count(`c_uint32`): Bad page count.

    Returns:
        `list`: List containing formatted bad pages.
    """
    if not isinstance(
        bad_page_info, ctypes.POINTER(
            amdsmi_wrapper.amdsmi_retired_page_record_t)
    ):
        raise AmdSmiParameterException(
            bad_page_info, ctypes.POINTER(
                amdsmi_wrapper.amdsmi_retired_page_record_t)
        )

    table_records = list()
    for i in range(bad_page_count.value):
        table_records.append(
            {
                "value": i,
                "page_address": bad_page_info[i].page_address,
                "page_size": bad_page_info[i].page_size,
                "status": bad_page_info[i].status,
            }
        )
    return table_records


def _format_bdf(amdsmi_bdf: amdsmi_wrapper.amdsmi_bdf_t) -> str:
    """
    Format BDF struct to readable data.

    Parameters:
        amdsmi_bdf(`amdsmi_bdf_t`): Struct containing BDF data that
        will be formatted.

    Returns:
        `str`: String containing BDF data in a readable format.
    """
    domain = hex(amdsmi_bdf.c__UA_amdsmi_bdf_t_0.domain_number)[2:].zfill(4)
    bus = hex(amdsmi_bdf.c__UA_amdsmi_bdf_t_0.bus_number)[2:].zfill(2)
    device = hex(amdsmi_bdf.c__UA_amdsmi_bdf_t_0.device_number)[2:].zfill(2)
    function = hex(amdsmi_bdf.c__UA_amdsmi_bdf_t_0.function_number)[2:]

    return domain + ":" + bus + ":" + device + "." + function


def _check_res(ret_code) -> None:
    """
    Wrapper for amdsmi function calls. Checks the status returned
    by the call. Raises exceptions if the status was inappropriate.

    Parameters:
        ret_code(`amdsmi_status_t`): Status code returned by function
        call.

    Returns:
        `None`.
    """
    if ret_code == amdsmi_wrapper.AMDSMI_STATUS_RETRY:
        raise AmdSmiRetryException()

    if ret_code == amdsmi_wrapper.AMDSMI_STATUS_TIMEOUT:
        raise AmdSmiTimeoutException()

    if ret_code != amdsmi_wrapper.AMDSMI_STATUS_SUCCESS:
        raise AmdSmiLibraryException(ret_code)


def _parse_bdf(bdf):
    if bdf is None:
        return None
    extended_regex = re.compile(
        r'^([0-9a-fA-F]{4}):([0-9a-fA-F]{2}):([0-1][0-9a-fA-F])\.([0-7])$')
    if extended_regex.match(bdf) is None:
        simple_regex = re.compile(
            r'^([0-9a-fA-F]{2}):([0-1][0-9a-fA-F])\.([0-7])$')
        if simple_regex.match(bdf) is None:
            return None
        else:
            return [0] + [int(x, 16) for x in simple_regex.match(bdf).groups()]
    else:
        return [int(x, 16) for x in extended_regex.match(bdf).groups()]


def _make_amdsmi_bdf_from_list(bdf):
    if len(bdf) != 4:
        return None
    amdsmi_bdf = amdsmi_wrapper.amdsmi_bdf_t()
    amdsmi_bdf.c__UA_amdsmi_bdf_t_0.function_number = bdf[3]
    amdsmi_bdf.c__UA_amdsmi_bdf_t_0.device_number = bdf[2]
    amdsmi_bdf.c__UA_amdsmi_bdf_t_0.bus_number = bdf[1]
    amdsmi_bdf.c__UA_amdsmi_bdf_t_0.domain_number = bdf[0]
    return amdsmi_bdf


def amdsmi_get_socket_handles() -> List[amdsmi_wrapper.amdsmi_socket_handle]:
    """
    Function that gets socket handles. Wraps the same named function call.

    Parameters:
        `None`.

    Returns:
        `List`: List containing all of the found socket handles.
    """
    socket_count = ctypes.c_uint32(0)
    null_ptr = ctypes.POINTER(amdsmi_wrapper.amdsmi_socket_handle)()
    _check_res(
        amdsmi_wrapper.amdsmi_get_socket_handles(
            ctypes.byref(socket_count), null_ptr)
    )
    socket_handles = (amdsmi_wrapper.amdsmi_socket_handle *
                      socket_count.value)()
    _check_res(
        amdsmi_wrapper.amdsmi_get_socket_handles(
            ctypes.byref(socket_count), socket_handles)
    )
    sockets = [
        amdsmi_wrapper.amdsmi_socket_handle(socket_handles[sock_idx])
        for sock_idx in range(socket_count.value)
    ]

    return sockets


def amdsmi_get_socket_info(socket_handle):
    if not isinstance(socket_handle, amdsmi_wrapper.amdsmi_socket_handle):
        raise AmdSmiParameterException(
            socket_handle, amdsmi_wrapper.amdsmi_socket_handle)
    socket_info = ctypes.create_string_buffer(128)

    _check_res(
        amdsmi_wrapper.amdsmi_get_socket_info(
            socket_handle, socket_info, ctypes.c_size_t(128))
    )

    return socket_info.value.decode()

def amdsmi_get_device_handles() -> List[amdsmi_wrapper.amdsmi_device_handle]:
    socket_handles = amdsmi_get_socket_handles()
    devices = []
    for socket in socket_handles:
        device_count = ctypes.c_uint32()
        null_ptr = ctypes.POINTER(amdsmi_wrapper.amdsmi_device_handle)()
        _check_res(
            amdsmi_wrapper.amdsmi_get_device_handles(
                socket,
                ctypes.byref(device_count),
                null_ptr,
            )
        )
        device_handles = (
            amdsmi_wrapper.amdsmi_device_handle * device_count.value)()
        _check_res(
            amdsmi_wrapper.amdsmi_get_device_handles(
                socket,
                ctypes.byref(device_count),
                device_handles,
            )
        )
        devices.extend(
            [
                amdsmi_wrapper.amdsmi_device_handle(device_handles[dev_idx])
                for dev_idx in range(device_count.value)
            ]
        )

    return devices


def amdsmi_init(flag=AmdSmiInitFlags.AMD_GPUS):
    if not isinstance(flag, AmdSmiInitFlags):
        raise AmdSmiParameterException(flag, AmdSmiInitFlags)
    _check_res(amdsmi_wrapper.amdsmi_init(flag))


def amdsmi_shut_down():
    _check_res(amdsmi_wrapper.amdsmi_shut_down())


def amdsmi_get_device_type(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> ctypes.c_uint32:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    dev_type = amdsmi_wrapper.device_type_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_device_type(
            device_handle, ctypes.byref(dev_type))
    )
    return dev_type.value


def amdsmi_get_device_bdf(device_handle: amdsmi_wrapper.amdsmi_device_handle) -> str:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    bdf_info = amdsmi_wrapper.amdsmi_bdf_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_device_bdf(
            device_handle, ctypes.byref(bdf_info))
    )

    return _format_bdf(bdf_info)


def amdsmi_get_asic_info(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    asic_info = amdsmi_wrapper.amdsmi_asic_info_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_asic_info(
            device_handle, ctypes.byref(asic_info))
    )

    return {
        "market_name": asic_info.market_name.decode("utf-8"),
        "family": asic_info.family,
        "vendor_id": asic_info.vendor_id,
        "device_id": asic_info.device_id,
        "rev_id": asic_info.rev_id,
        "asic_serial": asic_info.asic_serial.decode("utf-8"),
    }


def amdsmi_get_power_cap_info(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    power_info = amdsmi_wrapper.amdsmi_power_cap_info_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_power_cap_info(
            device_handle, ctypes.c_uint32(0), ctypes.byref(power_info)
        )
    )

    return {"power_cap": power_info.power_cap,
            "dpm_cap": power_info.dpm_cap,
            "power_cap_default": power_info.default_power_cap,
            "min_power_cap": power_info.min_power_cap,
            "max_power_cap": power_info.max_power_cap}


def amdsmi_get_caps_info(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    gpu_caps = amdsmi_wrapper.amdsmi_gpu_caps_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_caps_info(
            device_handle, ctypes.byref(gpu_caps))
    )

    return {
        "gfx": {
            "gfxip_major": gpu_caps.gfx.gfxip_major,
            "gfxip_minor": gpu_caps.gfx.gfxip_minor,
            "gfxip_cu_count": gpu_caps.gfx.gfxip_cu_count,
        },
        "mm_ip_list": list(gpu_caps.mm.mm_ip_list),
        "ras_supported": gpu_caps.ras_supported,
        "gfx_ip_count": gpu_caps.gfx_ip_count,
        "dma_ip_count": gpu_caps.dma_ip_count,
    }


def amdsmi_get_vbios_info(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    vbios_info = amdsmi_wrapper.amdsmi_vbios_info_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_vbios_info(
            device_handle, ctypes.byref(vbios_info))
    )

    return {
        "name": vbios_info.name.decode("utf-8"),
        "vbios_version_string": vbios_info.vbios_version_string.decode("utf-8"),
        "build_date": vbios_info.build_date.decode("utf-8"),
        "part_number": vbios_info.part_number.decode("utf-8"),
        "vbios_version": vbios_info.vbios_version,
    }


def amdsmi_get_gpu_activity(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    engine_usage = amdsmi_wrapper.amdsmi_engine_usage_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_gpu_activity(
            device_handle, ctypes.byref(engine_usage)
        )
    )

    return {
        "gfx_activity": engine_usage.gfx_activity,
        "umc_activity": engine_usage.umc_activity,
        "mm_activity": list(engine_usage.mm_activity),
    }


def amdsmi_get_clock_measure(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    clock_type: amdsmi_wrapper.amdsmi_clk_type_t,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(clock_type, AmdSmiClkType):
        raise AmdSmiParameterException(clock_type, AmdSmiClkType)

    clock_measure = amdsmi_wrapper.amdsmi_clk_measure_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_clock_measure(
            device_handle,
            amdsmi_wrapper.amdsmi_clk_type_t(clock_type),
            ctypes.byref(clock_measure),
        )
    )

    return {
        "cur_clk": clock_measure.cur_clk,
        "avg_clk": clock_measure.avg_clk,
        "min_clk": clock_measure.min_clk,
        "max_clk": clock_measure.max_clk,
    }


def amdsmi_get_bad_page_info(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Union[list, str]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    num_pages = ctypes.c_uint32()
    retired_page_record = ctypes.POINTER(
        amdsmi_wrapper.amdsmi_retired_page_record_t)()
    _check_res(
        amdsmi_wrapper.amdsmi_get_bad_page_info(
            device_handle, ctypes.byref(num_pages), retired_page_record
        )
    )
    table_records = _format_bad_page_info(retired_page_record, num_pages)
    if num_pages.value == 0:
        return "No bad pages found."
    else:
        table_records = _format_bad_page_info(retired_page_record, num_pages)

    return table_records


def amdsmi_get_target_frequency_range(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    clock_type: amdsmi_wrapper.amdsmi_clk_type_t,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(clock_type, AmdSmiClkType):
        raise AmdSmiParameterException(clock_type, AmdSmiClkType)

    freq_range = amdsmi_wrapper.amdsmi_frequency_range_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_target_frequency_range(
            device_handle,
            amdsmi_wrapper.amdsmi_clk_type_t(clock_type),
            ctypes.byref(freq_range),
        )
    )

    return {
        "supported_upper_bound": freq_range.supported_freq_range.upper_bound,
        "supported_lower_bound": freq_range.supported_freq_range.lower_bound,
        "current_upper_bound": freq_range.current_freq_range.upper_bound,
        "current_lower_bound": freq_range.current_freq_range.lower_bound,
    }


def amdsmi_get_ecc_error_count(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    error_count = amdsmi_wrapper.amdsmi_error_count_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_ecc_error_count(
            device_handle, ctypes.byref(error_count)
        )
    )

    return {
        "correctable_count": error_count.correctable_count,
        "uncorrectable_count": error_count.uncorrectable_count,
    }


def amdsmi_get_board_info(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    board_info = amdsmi_wrapper.amdsmi_board_info_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_board_info(
            device_handle, ctypes.byref(board_info))
    )

    return {
        "serial_number": board_info.serial_number,
        "model_number": board_info.model_number.decode("utf-8"),
        "product_serial": board_info.product_serial.decode("utf-8"),
        "product_name": board_info.product_name.decode("utf-8"),
        "manufacturer_name" : board_info.product_name.decode("utf-8")
    }


def amdsmi_get_ras_block_features_enabled(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> List[Dict[str, str]]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    ras_state = amdsmi_wrapper.amdsmi_ras_err_state_t()
    ras_states = []
    for gpu_block in AmdSmiGpuBlock:
        if gpu_block.name == "RESERVED" or gpu_block.name == "INVALID":
            continue
        if gpu_block.name == "LAST":
            gpu_block.name = "FUSE"
        _check_res(
            amdsmi_wrapper.amdsmi_get_ras_block_features_enabled(
                device_handle,
                amdsmi_wrapper.amdsmi_gpu_block_t(gpu_block.value),
                ctypes.byref(ras_state),
            )
        )
        ras_states.append(
            {
                "block": gpu_block.name,
                "status": AmdSmiRasErrState(ras_state.value).name,
            }
        )

    return ras_states


def amdsmi_get_process_list(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> List[amdsmi_wrapper.amdsmi_process_handle]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    max_processes = ctypes.c_uint32(0)
    process_list = (amdsmi_wrapper.amdsmi_process_handle *
                    max_processes.value)()
    _check_res(
        amdsmi_wrapper.amdsmi_get_process_list(
            device_handle, process_list, ctypes.byref(max_processes)
        )
    )

    process_list = (amdsmi_wrapper.amdsmi_process_handle *
                    max_processes.value)()
    _check_res(
        amdsmi_wrapper.amdsmi_get_process_list(
            device_handle, process_list, ctypes.byref(max_processes)
        )
    )

    return [amdsmi_wrapper.amdsmi_process_handle(x) for x in list(process_list)]


def amdsmi_get_process_info(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    process: amdsmi_wrapper.amdsmi_process_handle,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(process, amdsmi_wrapper.amdsmi_process_handle):
        raise AmdSmiParameterException(
            process, amdsmi_wrapper.amdsmi_process_handle)

    info = amdsmi_wrapper.amdsmi_proc_info_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_process_info(
            device_handle, process, ctypes.byref(info)
        )
    )

    return {
        "name": info.name.decode("utf-8"),
        "pid": info.pid,
        "mem": info.mem,
        "engine_usage": {
            "gfx": info.engine_usage.gfx,
            "compute": info.engine_usage.compute,
            "dma": info.engine_usage.dma,
            "enc": info.engine_usage.enc,
            "dec": info.engine_usage.dec,
        },
        "memory_usage": {
            "gtt_mem": info.memory_usage.gtt_mem,
            "cpu_mem": info.memory_usage.cpu_mem,
            "vram_mem": info.memory_usage.vram_mem,
        },
    }


def amdsmi_get_device_uuid(device_handle: amdsmi_wrapper.amdsmi_device_handle) -> str:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    uuid = ctypes.create_string_buffer(_AMDSMI_GPU_UUID_SIZE)

    uuid_length = ctypes.c_uint32()
    uuid_length.value = _AMDSMI_GPU_UUID_SIZE

    _check_res(
        amdsmi_wrapper.amdsmi_get_device_uuid(
            device_handle, ctypes.byref(uuid_length), uuid
        )
    )

    return uuid.value.decode("utf-8")


def amdsmi_get_driver_version(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> str:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    length = ctypes.c_int()
    length.value = _AMDSMI_MAX_DRIVER_VERSION_LENGTH

    version = ctypes.create_string_buffer(_AMDSMI_MAX_DRIVER_VERSION_LENGTH)

    _check_res(
        amdsmi_wrapper.amdsmi_get_driver_version(
            device_handle, ctypes.byref(length), version
        )
    )

    return version.value.decode("utf-8")


def amdsmi_get_power_measure(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    power_measure = amdsmi_wrapper.amdsmi_power_measure_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_power_measure(
            device_handle, ctypes.byref(power_measure)
        )
    )

    return {
        "average_socket_power": power_measure.average_socket_power,
        "voltage_gfx": power_measure.voltage_gfx,
        "energy_accumulator": power_measure.energy_accumulator,
        "power_limit" : power_measure.power_limit,
    }


def amdsmi_get_fw_info(
    device_handle: amdsmi_wrapper.amdsmi_device_handle
) -> List[Dict[str, Any]]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle)
    fw_info = amdsmi_wrapper.amdsmi_fw_info_t()
    _check_res(amdsmi_wrapper.amdsmi_get_fw_info(
        device_handle, ctypes.byref(fw_info)))
    firmwares = list()
    for i in range(0, fw_info.num_fw_info):
        firmwares.append({
            'fw_name': AmdSmiFwBlock(fw_info.fw_info_list[i].fw_id),
            'fw_version':  fw_info.fw_info_list[i].fw_version,
        })
    return {
        'fw_list': firmwares
    }


def amdsmi_get_vram_usage(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    vram_info = amdsmi_wrapper.amdsmi_vram_info_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_vram_usage(
            device_handle, ctypes.byref(vram_info))
    )

    return {"vram_total": vram_info.vram_total, "vram_used": vram_info.vram_used}


def amdsmi_get_pcie_link_status(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    pcie_info = amdsmi_wrapper.amdsmi_pcie_info_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_pcie_link_status(
            device_handle, ctypes.byref(pcie_info)
        )
    )

    return {"pcie_lanes": pcie_info.pcie_lanes, "pcie_speed": pcie_info.pcie_speed}


def amdsmi_get_pcie_link_caps(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    pcie_info = amdsmi_wrapper.amdsmi_pcie_info_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_pcie_link_caps(
            device_handle, ctypes.byref(pcie_info))
    )

    return {"pcie_lanes": pcie_info.pcie_lanes, "pcie_speed": pcie_info.pcie_speed}


def amdsmi_get_device_handle_from_bdf(bdf):
    bdf = _parse_bdf(bdf)
    if bdf is None:
        raise AmdSmiBdfFormatException(bdf)
    amdsmi_bdf = _make_amdsmi_bdf_from_list(bdf)
    device_handle = amdsmi_wrapper.amdsmi_device_handle()
    _check_res(amdsmi_wrapper.amdsmi_get_device_handle_from_bdf(
        amdsmi_bdf, ctypes.byref(device_handle)))
    return device_handle


def amdsmi_dev_get_vendor_name(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> str:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    length = ctypes.c_uint64()
    length.value = _AMDSMI_STRING_LENGTH

    vendor_name = ctypes.create_string_buffer(_AMDSMI_STRING_LENGTH)

    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_vendor_name(
            device_handle, vendor_name, length)
    )

    return vendor_name.value.decode("utf-8")


def amdsmi_dev_get_id(device_handle: amdsmi_wrapper.amdsmi_device_handle):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    id = ctypes.c_uint16()

    _check_res(amdsmi_wrapper.amdsmi_dev_get_id(
        device_handle, ctypes.byref(id)))

    return id.value


def amdsmi_dev_get_vram_vendor(device_handle: amdsmi_wrapper.amdsmi_device_handle):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    length = ctypes.c_uint32()
    length.value = _AMDSMI_STRING_LENGTH

    vram_vendor = ctypes.create_string_buffer(_AMDSMI_STRING_LENGTH)

    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_vram_vendor(
            device_handle, vram_vendor, length)
    )

    return vram_vendor.value.decode("utf-8")


def amdsmi_dev_get_drm_render_minor(device_handle: amdsmi_wrapper.amdsmi_device_handle):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    minor = ctypes.c_uint32()

    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_drm_render_minor(
            device_handle, ctypes.byref(minor)
        )
    )

    return minor.value


def amdsmi_dev_get_subsystem_id(device_handle: amdsmi_wrapper.amdsmi_device_handle):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    id = ctypes.c_uint16()

    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_subsystem_id(
            device_handle, ctypes.byref(id))
    )

    return id.value


def amdsmi_dev_get_subsystem_name(device_handle: amdsmi_wrapper.amdsmi_device_handle):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    length = ctypes.c_uint64()
    length.value = _AMDSMI_STRING_LENGTH

    name = ctypes.create_string_buffer(_AMDSMI_STRING_LENGTH)

    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_subsystem_name(
            device_handle, name, length)
    )

    return name.value.decode("utf-8")


def amdsmi_get_version():
    version = amdsmi_wrapper.amdsmi_version_t()

    _check_res(amdsmi_wrapper.amdsmi_get_version(ctypes.byref(version)))

    return {
        "major": version.major,
        "minor": version.minor,
        "patch": version.patch,
        "build": version.build.contents.value.decode("utf-8"),
    }


def amdsmi_get_version_str(sw_component: AmdSmiSwComponent):
    if not isinstance(sw_component, AmdSmiSwComponent):
        raise AmdSmiParameterException(sw_component, AmdSmiSwComponent)

    length = ctypes.c_uint32()
    length.value = _AMDSMI_STRING_LENGTH

    ver_str = ctypes.create_string_buffer(_AMDSMI_STRING_LENGTH)

    _check_res(amdsmi_wrapper.amdsmi_get_version_str(
        sw_component, ver_str, length))

    return ver_str.value.decode("utf-8")


def amdsmi_topo_get_numa_node_number(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    numa_node_number = ctypes.c_uint32()

    _check_res(
        amdsmi_wrapper.amdsmi_topo_get_numa_node_number(
            device_handle, ctypes.byref(numa_node_number)
        )
    )

    return numa_node_number.value


def amdsmi_topo_get_link_weight(
    device_handle_src: amdsmi_wrapper.amdsmi_device_handle,
    device_handle_dst: amdsmi_wrapper.amdsmi_device_handle,
):
    if not isinstance(device_handle_src, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle_src, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(device_handle_dst, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle_dst, amdsmi_wrapper.amdsmi_device_handle
        )

    weight = ctypes.c_uint64()

    _check_res(
        amdsmi_wrapper.amdsmi_topo_get_link_weight(
            device_handle_src, device_handle_dst, ctypes.byref(weight)
        )
    )

    return weight.value


def amdsmi_get_minmax_bandwidth(
    device_handle_src: amdsmi_wrapper.amdsmi_device_handle,
    device_handle_dst: amdsmi_wrapper.amdsmi_device_handle,
):
    if not isinstance(device_handle_src, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle_src, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(device_handle_dst, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle_dst, amdsmi_wrapper.amdsmi_device_handle
        )

    min_bandwidth = ctypes.c_uint64()
    max_bandwidth = ctypes.c_uint64()

    _check_res(
        amdsmi_wrapper. amdsmi_get_minmax_bandwidth(
            device_handle_src,
            device_handle_dst,
            ctypes.byref(min_bandwidth),
            ctypes.byref(max_bandwidth),
        )
    )

    return {"min_bandwidth": min_bandwidth.value, "max_bandwidth": max_bandwidth.value}


def amdsmi_topo_get_link_type(
    device_handle_src: amdsmi_wrapper.amdsmi_device_handle,
    device_handle_dst: amdsmi_wrapper.amdsmi_device_handle,
):
    if not isinstance(device_handle_src, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle_src, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(device_handle_dst, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle_dst, amdsmi_wrapper.amdsmi_device_handle
        )

    hops = ctypes.c_uint64()
    #type = AmdSmiIoLinkType()
    type = ctypes.c_uint32()

    _check_res(
        amdsmi_wrapper.amdsmi_topo_get_link_type(
            #device_handle_src, device_handle_dst, ctypes.byref(hops), type
            device_handle_src, device_handle_dst, ctypes.byref(
                hops), ctypes.byref(type)
        )
    )

    return {"hops": hops.value, "type": type.value}


def amdsmi_is_P2P_accessible(
    device_handle_src: amdsmi_wrapper.amdsmi_device_handle,
    device_handle_dst: amdsmi_wrapper.amdsmi_device_handle,
):
    if not isinstance(device_handle_src, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle_src, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(device_handle_dst, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle_dst, amdsmi_wrapper.amdsmi_device_handle
        )

    accessible = ctypes.c_bool()

    _check_res(
        amdsmi_wrapper.amdsmi_is_P2P_accessible(
            device_handle_src, device_handle_dst, ctypes.byref(accessible)
        )
    )

    return accessible.value


def amdsmi_get_xgmi_info(device_handle: amdsmi_wrapper.amdsmi_device_handle):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    xgmi_info = amdsmi_wrapper.amdsmi_xgmi_info_t()

    _check_res(amdsmi_wrapper.amdsmi_get_xgmi_info(device_handle, xgmi_info))

    return {
        "xgmi_lanes": xgmi_info.xgmi_lanes,
        "xgmi_hive_id": xgmi_info.xgmi_hive_id,
        "xgmi_node_id": xgmi_info.xgmi_node_id,
        "index": xgmi_info.index,
    }


def amdsmi_dev_counter_group_supported(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    event_group: AmdSmiEventGroup,
):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(event_group, AmdSmiEventGroup):
        raise AmdSmiParameterException(event_group, AmdSmiEventGroup)

    _check_res(
        amdsmi_wrapper.amdsmi_dev_counter_group_supported(
            device_handle, event_group)
    )


def amdsmi_dev_create_counter(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    event_type: AmdSmiEventType,
) -> amdsmi_wrapper.amdsmi_event_handle_t:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(event_type, AmdSmiEventType):
        raise AmdSmiParameterException(event_type, AmdSmiEventType)

    event_handle = amdsmi_wrapper.amdsmi_event_handle_t()
    _check_res(
        amdsmi_wrapper.amdsmi_dev_create_counter(
            device_handle, event_type, ctypes.byref(event_handle)
        )
    )

    return event_handle


def amdsmi_dev_destroy_counter(event_handle: amdsmi_wrapper.amdsmi_event_handle_t):
    if not isinstance(event_handle, amdsmi_wrapper.amdsmi_event_handle_t):
        raise AmdSmiParameterException(
            event_handle, amdsmi_wrapper.amdsmi_event_handle_t
        )
    _check_res(amdsmi_wrapper.amdsmi_dev_destroy_counter(event_handle))


def amdsmi_control_counter(
    event_handle: amdsmi_wrapper.amdsmi_event_handle_t,
    counter_command: AmdSmiCounterCommand,
):
    if not isinstance(event_handle, amdsmi_wrapper.amdsmi_event_handle_t):
        raise AmdSmiParameterException(
            event_handle, amdsmi_wrapper.amdsmi_event_handle_t
        )
    if not isinstance(counter_command, AmdSmiCounterCommand):
        raise AmdSmiParameterException(counter_command, AmdSmiCounterCommand)
    command_args = ctypes.c_void_p()

    _check_res(
        amdsmi_wrapper.amdsmi_control_counter(
            event_handle, counter_command, command_args
        )
    )


def amdsmi_read_counter(
    event_handle: amdsmi_wrapper.amdsmi_event_handle_t,
) -> Dict[str, Any]:
    if not isinstance(event_handle, amdsmi_wrapper.amdsmi_event_handle_t):
        raise AmdSmiParameterException(
            event_handle, amdsmi_wrapper.amdsmi_event_handle_t
        )

    counter_value = amdsmi_wrapper.amdsmi_counter_value_t()

    _check_res(
        amdsmi_wrapper.amdsmi_read_counter(
            event_handle, ctypes.byref(counter_value))
    )

    return {
        "value": counter_value.value,
        "time_enabled": counter_value.time_enabled,
        "time_running": counter_value.time_running,
    }


def amdsmi_counter_get_available_counters(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    event_group: AmdSmiEventGroup,
) -> int:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(event_group, AmdSmiEventGroup):
        raise AmdSmiParameterException(event_group, AmdSmiEventGroup)
    available = ctypes.c_uint32()

    _check_res(
        amdsmi_wrapper. amdsmi_counter_get_available_counters(
            device_handle, event_group, ctypes.byref(available)
        )
    )

    return available.value


def amdsmi_dev_set_perf_level(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    perf_level: AmdSmiDevPerfLevel,
):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(perf_level, AmdSmiDevPerfLevel):
        raise AmdSmiParameterException(perf_level, AmdSmiDevPerfLevel)

    _check_res(amdsmi_wrapper. amdsmi_dev_set_perf_level(
        device_handle, perf_level))


def amdsmi_dev_get_power_profile_presets(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, sensor_idx: int
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(sensor_idx, int):
        raise AmdSmiParameterException(sensor_idx, int)

    sensor_idx = ctypes.c_uint32(sensor_idx)
    status = amdsmi_wrapper.amdsmi_power_profile_status_t()

    _check_res(
        amdsmi_wrapper. amdsmi_dev_get_power_profile_presets(
            device_handle, sensor_idx, ctypes.byref(status)
        )
    )

    return {
        "available_profiles": status.available_profiles,
        "current": status.current,
        "num_profiles": status.num_profiles,
    }


def amdsmi_dev_reset_gpu(device_handle: amdsmi_wrapper.amdsmi_device_handle):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    _check_res(amdsmi_wrapper.amdsmi_dev_reset_gpu(device_handle))


def amdsmi_set_perf_determinism_mode(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, clock_value: int
):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(clock_value, int):
        raise AmdSmiParameterException(clock_value, int)
    clock_value = ctypes.c_uint64(clock_value)

    _check_res(
        amdsmi_wrapper.amdsmi_set_perf_determinism_mode(
            device_handle, clock_value)
    )


def amdsmi_dev_set_fan_speed(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, sensor_idx: int, fan_speed: int
):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(sensor_idx, int):
        raise AmdSmiParameterException(sensor_idx, int)
    if not isinstance(fan_speed, int):
        raise AmdSmiParameterException(fan_speed, int)
    sensor_idx = ctypes.c_uint32(sensor_idx)
    fan_speed = ctypes.c_uint64(fan_speed)

    _check_res(
        amdsmi_wrapper.amdsmi_dev_set_fan_speed(
            device_handle, sensor_idx, fan_speed)
    )


def amdsmi_dev_reset_fan(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, sensor_idx: int
):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(sensor_idx, int):
        raise AmdSmiParameterException(sensor_idx, int)
    sensor_idx = ctypes.c_uint32(sensor_idx)

    _check_res(amdsmi_wrapper.amdsmi_dev_reset_fan(device_handle, sensor_idx))


def amdsmi_dev_set_clk_freq(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    clk_type: AmdSmiClkType,
    freq_bitmask: int,
):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(clk_type, AmdSmiClkType):
        raise AmdSmiParameterException(clk_type, AmdSmiParameterException)
    if not isinstance(freq_bitmask, int):
        raise AmdSmiParameterException(freq_bitmask, int)
    freq_bitmask = ctypes.c_uint64(freq_bitmask)
    _check_res(
        amdsmi_wrapper. amdsmi_dev_set_clk_freq(
            device_handle, clk_type, freq_bitmask
        )
    )


def amdsmi_dev_set_overdrive_level_v1(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, overdrive_value: int
):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(overdrive_value, int):
        raise AmdSmiParameterException(overdrive_value, int)
    overdrive_value = ctypes.c_uint32(overdrive_value)

    _check_res(
        amdsmi_wrapper. amdsmi_dev_set_overdrive_level_v1(
            device_handle, overdrive_value)
    )


def amdsmi_dev_set_overdrive_level(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, overdrive_value: int
):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(overdrive_value, int):
        raise AmdSmiParameterException(overdrive_value, int)
    overdrive_value = ctypes.c_uint32(overdrive_value)

    _check_res(
        amdsmi_wrapper. amdsmi_dev_set_overdrive_level(
            device_handle, overdrive_value)
    )


def amdsmi_dev_open_supported_func_iterator(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> amdsmi_wrapper.amdsmi_func_id_iter_handle_t:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    obj_handle = amdsmi_wrapper.amdsmi_func_id_iter_handle_t()
    _check_res(
        amdsmi_wrapper.amdsmi_dev_open_supported_func_iterator(
            device_handle, ctypes.byref(obj_handle)
        )
    )

    return obj_handle


def amdsmi_dev_get_pci_id(device_handle: amdsmi_wrapper.amdsmi_device_handle):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    bdfid = ctypes.c_uint64()
    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_pci_id(
            device_handle, ctypes.byref(bdfid))
    )

    return bdfid.value


def amdsmi_dev_open_supported_variant_iterator(
    obj_handle: amdsmi_wrapper.amdsmi_func_id_iter_handle_t,
) -> amdsmi_wrapper.amdsmi_func_id_iter_handle_t:
    if not isinstance(obj_handle, amdsmi_wrapper.amdsmi_func_id_iter_handle_t):
        raise AmdSmiParameterException(
            obj_handle, amdsmi_wrapper.amdsmi_func_id_iter_handle_t
        )

    var_iter = amdsmi_wrapper.amdsmi_func_id_iter_handle_t()
    _check_res(
        amdsmi_wrapper.amdsmi_dev_open_supported_variant_iterator(
            obj_handle, ctypes.byref(var_iter)
        )
    )

    return var_iter


def amdsmi_dev_close_supported_func_iterator(
    obj_handle: amdsmi_wrapper.amdsmi_func_id_iter_handle_t,
) -> None:
    if not isinstance(obj_handle, amdsmi_wrapper.amdsmi_func_id_iter_handle_t):
        raise AmdSmiParameterException(
            obj_handle, amdsmi_wrapper.amdsmi_func_id_iter_handle_t
        )

    _check_res(
        amdsmi_wrapper.amdsmi_dev_close_supported_func_iterator(
            obj_handle, ctypes.byref(obj_handle)
        )
    )


def amdsmi_next_func_iter(
    obj_handle: amdsmi_wrapper.amdsmi_func_id_iter_handle_t,
) -> amdsmi_wrapper.amdsmi_func_id_iter_handle_t:
    if not isinstance(obj_handle, amdsmi_wrapper.amdsmi_func_id_iter_handle_t):
        raise AmdSmiParameterException(
            obj_handle, amdsmi_wrapper.amdsmi_func_id_iter_handle_t
        )

    _check_res(amdsmi_wrapper.amdsmi_next_func_iter(obj_handle))

    return obj_handle


def amdsmi_get_func_iter_value(
    obj_handle: amdsmi_wrapper.amdsmi_func_id_iter_handle_t,
) -> amdsmi_wrapper.amdsmi_func_id_value_t:
    if not isinstance(obj_handle, amdsmi_wrapper.amdsmi_func_id_iter_handle_t):
        raise AmdSmiParameterException(
            obj_handle, amdsmi_wrapper.amdsmi_func_id_iter_handle_t
        )

    value = amdsmi_wrapper.amdsmi_func_id_value_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_func_iter_value(
            obj_handle, ctypes.byref(value))
    )

    return {
        "id": value.id,
        "name": amdsmi_wrapper.string_cast(value.name),
        "amd_id_0": {
            "memory_type": value.amd_id_0.memory_type,
            "temp_metric": value.amd_id_0.temp_metric,
            "evnt_type": value.amd_id_0.evnt_type,
            "evnt_group": value.amd_id_0.evnt_group,
            "clk_type": value.amd_id_0.clk_type,
            "fw_block": value.amd_id_0.fw_block,
            "gpu_block_type": value.amd_id_0.gpu_block_type,
        },
    }


def amdsmi_dev_set_pci_bandwidth(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, bitmask: int
) -> None:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(bitmask, int):
        raise AmdSmiParameterException(bitmask, int)

    _check_res(
        amdsmi_wrapper. amdsmi_dev_set_pci_bandwidth(
            device_handle, ctypes.c_uint64(bitmask)
        )
    )


def _format_transfer_rate(transfer_rate):
    return {
        'num_supported': transfer_rate.num_supported,
        'current': transfer_rate.current,
        'frequency': list(transfer_rate.frequency)
    }


def amdsmi_dev_get_pci_bandwidth(device_handle: amdsmi_wrapper.amdsmi_device_handle):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    bandwidth = amdsmi_wrapper.amdsmi_pcie_bandwidth_t()

    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_pci_bandwidth(
            device_handle, ctypes.byref(bandwidth))
    )

    transfer_rate = _format_transfer_rate(bandwidth.transfer_rate)

    return {
        'transfer_rate': transfer_rate,
        'lanes': list(bandwidth.lanes)
    }


def amdsmi_dev_get_pci_throughput(device_handle: amdsmi_wrapper.amdsmi_device_handle):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    sent = ctypes.c_uint64()
    received = ctypes.c_uint64()
    max_pkt_sz = ctypes.c_uint64()

    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_pci_throughput(device_handle, ctypes.byref(
            sent), ctypes.byref(received), ctypes.byref(max_pkt_sz))
    )

    return {
        'sent': sent.value,
        'received': received.value,
        'max_pkt_sz': max_pkt_sz.value
    }


def amdsmi_dev_get_pci_replay_counter(device_handle: amdsmi_wrapper.amdsmi_device_handle):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    counter = ctypes.c_uint64()

    _check_res(
        amdsmi_wrapper. amdsmi_dev_get_pci_replay_counter(
            device_handle, ctypes.byref(counter))
    )

    return counter.value


def amdsmi_topo_get_numa_affinity(device_handle: amdsmi_wrapper.amdsmi_device_handle):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    numa_node = ctypes.c_uint32()

    _check_res(
        amdsmi_wrapper.amdsmi_topo_get_numa_affinity(
            device_handle, ctypes.byref(numa_node))
    )

    return numa_node.value


def amdsmi_dev_set_power_cap(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, sensor_ind: int, cap: int
) -> None:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(sensor_ind, int):
        raise AmdSmiParameterException(sensor_ind, int)

    if not isinstance(cap, int):
        raise AmdSmiParameterException(cap, int)

    _check_res(
        amdsmi_wrapper. amdsmi_dev_set_power_cap(
            device_handle, ctypes.c_uint32(sensor_ind), ctypes.c_uint64(cap)
        )
    )


def amdsmi_dev_get_power_ave(device_handle: amdsmi_wrapper.amdsmi_device_handle, sensor_id: ctypes.c_uint32):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    power = ctypes.c_uint64()

    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_power_ave(
            device_handle, sensor_id, ctypes.byref(power))
    )

    return power.value


def amdsmi_dev_set_power_profile(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    reserved: int,
    profile: AmdSmiPowerProfilePresetMasks,
) -> None:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(reserved, int):
        raise AmdSmiParameterException(reserved, int)

    if not isinstance(profile, AmdSmiPowerProfilePresetMasks):
        raise AmdSmiParameterException(profile, AmdSmiPowerProfilePresetMasks)

    _check_res(
        amdsmi_wrapper. amdsmi_dev_set_power_profile(
            device_handle, ctypes.c_uint32(reserved), profile
        )
    )


def amdsmi_dev_get_energy_count(device_handle: amdsmi_wrapper.amdsmi_device_handle):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    power = ctypes.c_uint64()
    counter_resolution = ctypes.c_float()
    timestamp = ctypes.c_uint64()

    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_energy_count(device_handle, ctypes.byref(
            power), ctypes.byref(counter_resolution), ctypes.byref(timestamp))
    )

    return {
        'power': power.value,
        'counter_resolution': counter_resolution.value,
        'timestamp': timestamp.value,
    }


def amdsmi_dev_set_clk_range(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    min_clk_value: int,
    max_clk_value: int,
    clk_type: AmdSmiClkType,
) -> None:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(min_clk_value, int):
        raise AmdSmiParameterException(min_clk_value, int)

    if not isinstance(max_clk_value, int):
        raise AmdSmiParameterException(min_clk_value, int)

    if not isinstance(clk_type, AmdSmiClkType):
        raise AmdSmiParameterException(clk_type, AmdSmiClkType)

    _check_res(
        amdsmi_wrapper.amdsmi_dev_set_clk_range(
            device_handle,
            ctypes.c_uint64(min_clk_value),
            ctypes.c_uint64(max_clk_value),
            clk_type,
        )
    )


def amdsmi_dev_get_memory_total(device_handle: amdsmi_wrapper.amdsmi_device_handle, mem_type: AmdSmiMemoryType):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(mem_type, AmdSmiMemoryType):
        raise AmdSmiParameterException(
            mem_type, AmdSmiMemoryType
        )

    total = ctypes.c_uint64()

    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_memory_total(
            device_handle, mem_type, ctypes.byref(total))
    )

    return total.value


def amdsmi_dev_set_od_clk_info(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    level: AmdSmiFreqInd,
    value: int,
    clk_type: AmdSmiClkType,
) -> None:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(level, AmdSmiFreqInd):
        raise AmdSmiParameterException(level, AmdSmiFreqInd)

    if not isinstance(value, int):
        raise AmdSmiParameterException(value, int)

    if not isinstance(clk_type, AmdSmiClkType):
        raise AmdSmiParameterException(clk_type, AmdSmiClkType)

    _check_res(
        amdsmi_wrapper. amdsmi_dev_set_od_clk_info(
            device_handle, level, ctypes.c_uint64(value), clk_type
        )
    )


def amdsmi_dev_get_memory_usage(device_handle: amdsmi_wrapper.amdsmi_device_handle, mem_type: AmdSmiMemoryType):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(mem_type, AmdSmiMemoryType):
        raise AmdSmiParameterException(
            mem_type, AmdSmiMemoryType
        )

    used = ctypes.c_uint64()

    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_memory_usage(
            device_handle, mem_type, ctypes.byref(used))
    )

    return used.value


def amdsmi_dev_set_od_volt_info(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    vpoint: int,
    clk_value: int,
    volt_value: int,
) -> None:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(vpoint, int):
        raise AmdSmiParameterException(vpoint, int)

    if not isinstance(clk_value, int):
        raise AmdSmiParameterException(clk_value, int)

    if not isinstance(volt_value, int):
        raise AmdSmiParameterException(volt_value, int)

    _check_res(
        amdsmi_wrapper. amdsmi_dev_set_od_volt_info(
            device_handle,
            ctypes.c_uint32(vpoint),
            ctypes.c_uint64(clk_value),
            ctypes.c_uint64(volt_value),
        )
    )


def amdsmi_dev_get_memory_busy_percent(device_handle: amdsmi_wrapper.amdsmi_device_handle):
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    busy_percent = ctypes.c_uint32()

    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_memory_busy_percent(
            device_handle, ctypes.byref(busy_percent))
    )

    return busy_percent.value


def amdsmi_dev_set_perf_level_v1(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    perf_lvl: AmdSmiDevPerfLevel,
) -> None:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(perf_lvl, AmdSmiDevPerfLevel):
        raise AmdSmiParameterException(perf_lvl, AmdSmiDevPerfLevel)

    _check_res(amdsmi_wrapper. amdsmi_dev_set_perf_level_v1(
        device_handle, perf_lvl))


def amdsmi_dev_get_fan_rpms(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, sensor_idx: int
) -> int:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(sensor_idx, int):
        raise AmdSmiParameterException(sensor_idx, int)
    fan_speed = ctypes.c_int64()
    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_fan_rpms(
            device_handle, sensor_idx, ctypes.byref(fan_speed)
        )
    )

    return fan_speed.value


def amdsmi_dev_get_fan_speed(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, sensor_idx: int
) -> int:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(sensor_idx, int):
        raise AmdSmiParameterException(sensor_idx, int)
    fan_speed = ctypes.c_int64()
    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_fan_speed(
            device_handle, sensor_idx, ctypes.byref(fan_speed)
        )
    )

    return fan_speed.value


def amdsmi_dev_get_fan_speed_max(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, sensor_idx: int
) -> int:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(sensor_idx, int):
        raise AmdSmiParameterException(sensor_idx, int)
    fan_speed = ctypes.c_uint64()
    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_fan_speed_max(
            device_handle, sensor_idx, ctypes.byref(fan_speed)
        )
    )

    return fan_speed.value


def amdsmi_dev_get_temp_metric(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    sensor_type: AmdSmiTemperatureType,
    metric: AmdSmiTemperatureMetric,
) -> int:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(sensor_type, AmdSmiTemperatureType):
        raise AmdSmiParameterException(sensor_type, AmdSmiTemperatureType)
    if not isinstance(metric, AmdSmiTemperatureMetric):
        raise AmdSmiParameterException(metric, AmdSmiTemperatureMetric)

    temp_value = ctypes.c_int64()
    _check_res(
        amdsmi_wrapper. amdsmi_dev_get_temp_metric(
            device_handle, sensor_type, metric, ctypes.byref(temp_value)
        )
    )

    return temp_value.value


def amdsmi_dev_get_volt_metric(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    sensor_type: AmdSmiVoltageType,
    metric: AmdSmiVoltageMetric,
) -> int:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(sensor_type, AmdSmiVoltageType):
        raise AmdSmiParameterException(sensor_type, AmdSmiVoltageType)
    if not isinstance(metric, AmdSmiVoltageMetric):
        raise AmdSmiParameterException(metric, AmdSmiVoltageMetric)

    voltage = ctypes.c_int64()
    _check_res(
        amdsmi_wrapper. amdsmi_dev_get_volt_metric(
            device_handle, sensor_type, metric, ctypes.byref(voltage)
        )
    )

    return voltage.value


def amdsmi_dev_get_busy_percent(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> int:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    busy_percent = ctypes.c_uint32()
    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_busy_percent(
            device_handle, ctypes.byref(busy_percent)
        )
    )

    return busy_percent.value


def amdsmi_get_utilization_count(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
    *counter_types: Tuple[AmdSmiUtilizationCounterType]
) -> List[Dict[str, Any]]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not len(counter_types):
        raise AmdSmiLibraryException(amdsmi_wrapper.AMDSMI_STATUS_INVAL)
    counters = []
    for counter_type in counter_types:
        if not isinstance(counter_type, AmdSmiUtilizationCounterType):
            raise AmdSmiParameterException(
                counter_type, AmdSmiUtilizationCounterType)
        counter = amdsmi_wrapper.amdsmi_utilization_counter_t()
        counter.type = counter_type
        counters.append(counter)

    count = ctypes.c_uint32(len(counters))
    timestamp = ctypes.c_uint64()
    util_counter_list = (amdsmi_wrapper.amdsmi_utilization_counter_t * len(counters))(
        *counters
    )

    _check_res(
        amdsmi_wrapper.amdsmi_get_utilization_count(
            device_handle, util_counter_list, count, ctypes.byref(timestamp)
        )
    )
    if count.value != len(counters):
        raise AmdSmiLibraryException(amdsmi_wrapper.AMDSMI_STATUS_API_FAILED)

    result = [{"timestamp": timestamp.value}]
    for idx in range(count.value):
        counter_type = amdsmi_wrapper.c__EA_AMDSMI_UTILIZATION_COUNTER_TYPE__enumvalues[
            util_counter_list[idx].type
        ]
        if counter_type == "AMDSMI_UTILIZATION_COUNTER_LAST":
            counter_type = "AMDSMI_COARSE_GRAIN_MEM_ACTIVITY"
        result.append(
            {"type": counter_type, "value": util_counter_list[idx].value})

    return result


def amdsmi_dev_get_perf_level(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> str:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    perf = amdsmi_wrapper.amdsmi_dev_perf_level_t()

    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_perf_level(
            device_handle, ctypes.byref(perf))
    )

    result = amdsmi_wrapper.c__EA_amdsmi_dev_perf_level_t__enumvalues[perf.value]
    if result == "AMDSMI_DEV_PERF_LEVEL_FIRST":
        result = "AMDSMI_DEV_PERF_LEVEL_AUTO"
    if result == "AMDSMI_DEV_PERF_LEVEL_LAST":
        result = "AMDSMI_DEV_PERF_LEVEL_DETERMINISM"

    return result


def amdsmi_dev_get_overdrive_level(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> int:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    od_level = ctypes.c_uint32()
    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_overdrive_level(
            device_handle, ctypes.byref(od_level)
        )
    )

    return od_level.value


def amdsmi_dev_get_gpu_clk_freq(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, clk_type: AmdSmiClkType
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(clk_type, AmdSmiClkType):
        raise AmdSmiParameterException(clk_type, AmdSmiClkType)

    freq = amdsmi_wrapper.amdsmi_frequencies_t()
    _check_res(
        amdsmi_wrapper. amdsmi_dev_get_gpu_clk_freq(
            device_handle, clk_type, ctypes.byref(freq)
        )
    )

    return {
        "num_supported": freq.num_supported,
        "current": freq.current,
        "frequency": list(freq.frequency)[: freq.num_supported - 1],
    }


def amdsmi_dev_get_od_volt_info(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    freq_data = amdsmi_wrapper.amdsmi_od_volt_freq_data_t()
    _check_res(
        amdsmi_wrapper. amdsmi_dev_get_od_volt_info(
            device_handle, ctypes.byref(freq_data)
        )
    )

    return {
        "curr_sclk_range": {
            "lower_bound": freq_data.curr_sclk_range.lower_bound,
            "upper_bound": freq_data.curr_sclk_range.upper_bound,
        },
        "curr_mclk_range": {
            "lower_bound": freq_data.curr_mclk_range.lower_bound,
            "upper_bound": freq_data.curr_mclk_range.upper_bound,
        },
        "sclk_freq_limits": {
            "lower_bound": freq_data.sclk_freq_limits.lower_bound,
            "upper_bound": freq_data.sclk_freq_limits.upper_bound,
        },
        "mclk_freq_limits": {
            "lower_bound": freq_data.mclk_freq_limits.lower_bound,
            "upper_bound": freq_data.mclk_freq_limits.upper_bound,
        },
        "curve.vc_points": list(freq_data.curve.vc_points),
        "num_regions": freq_data.num_regions,
    }


def amdsmi_dev_get_gpu_metrics_info(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Dict[str, Any]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    gpu_metrics = amdsmi_wrapper.amdsmi_gpu_metrics_t()
    _check_res(
        amdsmi_wrapper. amdsmi_dev_get_gpu_metrics_info(
            device_handle, ctypes.byref(gpu_metrics)
        )
    )

    return {
        "temperature_edge": gpu_metrics.temperature_edge,
        "temperature_hotspot": gpu_metrics.temperature_hotspot,
        "temperature_mem": gpu_metrics.temperature_mem,
        "temperature_vrgfx": gpu_metrics.temperature_vrgfx,
        "temperature_vrsoc": gpu_metrics.temperature_vrsoc,
        "temperature_vrmem": gpu_metrics.temperature_vrmem,
        "average_gfx_activity": gpu_metrics.average_gfx_activity,
        "average_umc_activity": gpu_metrics.average_umc_activity,
        "average_mm_activity": gpu_metrics.average_mm_activity,
        "average_socket_power": gpu_metrics.average_socket_power,
        "energy_accumulator": gpu_metrics.energy_accumulator,
        "system_clock_counter": gpu_metrics.system_clock_counter,
        "average_gfxclk_frequency": gpu_metrics.average_gfxclk_frequency,
        "average_socclk_frequency": gpu_metrics.average_socclk_frequency,
        "average_uclk_frequency": gpu_metrics.average_uclk_frequency,
        "average_vclk0_frequency": gpu_metrics.average_vclk0_frequency,
        "average_dclk0_frequency": gpu_metrics.average_dclk0_frequency,
        "average_vclk1_frequency": gpu_metrics.average_vclk1_frequency,
        "average_dclk1_frequency": gpu_metrics.average_dclk1_frequency,
        "current_gfxclk": gpu_metrics.current_gfxclk,
        "current_socclk": gpu_metrics.current_socclk,
        "current_uclk": gpu_metrics.current_uclk,
        "current_vclk0": gpu_metrics.current_vclk0,
        "current_dclk0": gpu_metrics.current_dclk0,
        "current_vclk1": gpu_metrics.current_vclk1,
        "current_dclk1": gpu_metrics.current_dclk1,
        "throttle_status": gpu_metrics.throttle_status,
        "current_fan_speed": gpu_metrics.current_fan_speed,
        "pcie_link_width": gpu_metrics.pcie_link_width,
        "pcie_link_speed": gpu_metrics.pcie_link_speed,
        "padding": gpu_metrics.padding,
        "gfx_activity_acc": gpu_metrics.gfx_activity_acc,
        "mem_actvity_acc": gpu_metrics.mem_actvity_acc,
        "temperature_hbm": list(gpu_metrics.temperature_hbm),
    }


def amdsmi_dev_get_od_volt_curve_regions(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, num_regions: int
) -> List[Dict[str, Any]]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )
    if not isinstance(num_regions, int):
        raise AmdSmiParameterException(num_regions, int)

    region_count = ctypes.c_uint32(num_regions)
    buffer = (amdsmi_wrapper.amdsmi_freq_volt_region_t * num_regions)()
    _check_res(
        amdsmi_wrapper. amdsmi_dev_get_od_volt_curve_regions(
            device_handle, ctypes.byref(region_count), buffer
        )
    )

    result = []

    for idx in range(region_count.value):
        result.extend(
            [
                {
                    "freq_range": {
                        "lower_bound": buffer[idx].freq_range.lower_bound,
                        "upper_bound": buffer[idx].freq_range.upper_bound,
                    },
                    "volt_range": {
                        "lower_bound": buffer[idx].volt_range.lower_bound,
                        "upper_bound": buffer[idx].volt_range.upper_bound,
                    },
                }
            ]
        )

    return result


def amdsmi_dev_get_ecc_count(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, block: AmdSmiGpuBlock
) -> Dict[str, int]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(block, AmdSmiGpuBlock):
        raise AmdSmiParameterException(block, AmdSmiGpuBlock)

    ec = amdsmi_wrapper.amdsmi_error_count_t()
    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_ecc_count(
            device_handle, block, ctypes.byref(ec))
    )

    return {
        "correctable_count": ec.correctable_count,
        "uncorrectable_count": ec.uncorrectable_count,
    }


def amdsmi_dev_get_ecc_enabled(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> int:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    blocks = ctypes.c_uint64(0)
    _check_res(
        amdsmi_wrapper. amdsmi_dev_get_ecc_enabled(
            device_handle, ctypes.byref(blocks))
    )

    return blocks.value


def amdsmi_dev_get_ecc_status(
    device_handle: amdsmi_wrapper.amdsmi_device_handle, block: AmdSmiGpuBlock
) -> AmdSmiRasErrState:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    if not isinstance(block, AmdSmiGpuBlock):
        raise AmdSmiParameterException(block, AmdSmiGpuBlock)

    state = amdsmi_wrapper.amdsmi_ras_err_state_t()
    _check_res(
        amdsmi_wrapper. amdsmi_dev_get_ecc_status(
            device_handle, block, ctypes.byref(state)
        )
    )

    return AmdSmiRasErrState(state.value)


def amdsmi_status_string(status: amdsmi_wrapper.amdsmi_status_t) -> str:
    if not isinstance(status, amdsmi_wrapper.amdsmi_status_t):
        raise AmdSmiParameterException(status, amdsmi_wrapper.amdsmi_status_t)

    status_string_p_p = ctypes.pointer(ctypes.pointer(ctypes.c_char()))

    _check_res(amdsmi_wrapper.amdsmi_status_string(
        status, status_string_p_p))

    return amdsmi_wrapper.string_cast(status_string_p_p.contents)


def amdsmi_get_compute_process_info() -> List[Dict[str, int]]:
    num_items = ctypes.c_uint32(0)
    nullptr = ctypes.POINTER(amdsmi_wrapper.amdsmi_process_info_t)()
    _check_res(
        amdsmi_wrapper.amdsmi_get_compute_process_info(
            nullptr, ctypes.byref(num_items))
    )

    procs = (amdsmi_wrapper.amdsmi_process_info_t * num_items.value)()
    _check_res(
        amdsmi_wrapper.amdsmi_get_compute_process_info(
            procs, ctypes.byref(num_items))
    )

    return [
        {
            "process_id": proc.process_id,
            "pasid": proc.pasid,
            "vram_usage": proc.vram_usage,
            "sdma_usage": proc.sdma_usage,
            "cu_occupancy": proc.cu_occupancy,
        }
        for proc in procs
    ]


def amdsmi_get_compute_process_info_by_pid(pid: int) -> Dict[str, int]:
    if not isinstance(pid, int):
        raise AmdSmiParameterException(pid, int)

    proc = amdsmi_wrapper.amdsmi_process_info_t()
    _check_res(
        amdsmi_wrapper.amdsmi_get_compute_process_info_by_pid(
            ctypes.c_uint32(pid), ctypes.byref(proc)
        )
    )

    return {
        "process_id": proc.process_id,
        "pasid": proc.pasid,
        "vram_usage": proc.vram_usage,
        "sdma_usage": proc.sdma_usage,
        "cu_occupancy": proc.cu_occupancy,
    }


def amdsmi_get_compute_process_gpus(pid: int) -> List[int]:
    if not isinstance(pid, int):
        raise AmdSmiParameterException(pid, int)

    num_devices = ctypes.c_uint32(0)
    nullptr = ctypes.POINTER(ctypes.c_uint32)()
    _check_res(
        amdsmi_wrapper.amdsmi_get_compute_process_gpus(
            pid, nullptr, ctypes.byref(num_devices)
        )
    )

    dv_indices = (ctypes.c_uint32 * num_devices.value)()
    _check_res(
        amdsmi_wrapper.amdsmi_get_compute_process_gpus(
            pid, dv_indices, ctypes.byref(num_devices)
        )
    )

    return [dv_index.value for dv_index in dv_indices]


def amdsmi_dev_xgmi_error_status(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> AmdSmiXgmiStatus:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    status = amdsmi_wrapper.amdsmi_xgmi_status_t()
    _check_res(
        amdsmi_wrapper.amdsmi_dev_xgmi_error_status(
            device_handle, ctypes.byref(status))
    )

    return AmdSmiXgmiStatus(status.value)


def amdsmi_dev_reset_xgmi_error(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> None:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    _check_res(amdsmi_wrapper.amdsmi_dev_reset_xgmi_error(device_handle))


def amdsmi_dev_get_memory_reserved_pages(
    device_handle: amdsmi_wrapper.amdsmi_device_handle,
) -> Union[list, str]:
    if not isinstance(device_handle, amdsmi_wrapper.amdsmi_device_handle):
        raise AmdSmiParameterException(
            device_handle, amdsmi_wrapper.amdsmi_device_handle
        )

    num_pages = ctypes.c_uint32()
    retired_page_record = ctypes.POINTER(
        amdsmi_wrapper.amdsmi_retired_page_record_t)()
    _check_res(
        amdsmi_wrapper.amdsmi_dev_get_memory_reserved_pages(
            device_handle, ctypes.byref(num_pages), retired_page_record
        )
    )

    table_records = _format_bad_page_info(retired_page_record, num_pages)
    if num_pages.value == 0:
        return "No bad pages found."
    else:
        table_records = _format_bad_page_info(retired_page_record, num_pages)

    return table_records

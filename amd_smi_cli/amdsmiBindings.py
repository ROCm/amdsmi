#!/usr/bin/env python3
"""! @brief AMD_SMI FFI"""

from ctypes import *
from enum import Enum
import os


path_amdsmi = '/opt/rocm/lib/libamd_smi64.so' #@TODO make this dynamic

try:
    cdll.LoadLibrary(path_amdsmi)
    amdsmi = CDLL(path_amdsmi)
except OSError:
    print("Unable to load libamd_smi64.so library\n")
    exit(1)

##
# @brief Initialization flags
#
#  may be OR'd together and passed to smi.amdsmi_init()
##

class amdsmi_init_flags(c_int):
    AMD_SMI_INIT_ALL_DEVICES = 0x0  # Default option
    AMD_SMI_INIT_AMD_CPUS = (1 << 0)
    AMD_SMI_INIT_AMD_GPUS = (1 << 1)
    AMD_SMI_INIT_NON_AMD_CPUS = (1 << 2)
    AMD_SMI_INIT_NON_AMD_GPUS = (1 << 3)

# Maximum size definitions GPUVSMI
AMDSMI_MAX_MM_IP_COUNT = 8
AMDSMI_MAX_DATE_LENGTH = 32  # YYYY-MM-DD:HH:MM:SS.MSC #
AMDSMI_MAX_STRING_LENGTH = 64
AMDSMI_NORMAL_STRING_LENGTH = 32
AMDSMI_MAX_DEVICES = 32
AMDSMI_MAX_NAME = 32
AMDSMI_MAX_DRIVER_VERSION_LENGTH = 80
AMDSMI_PRODUCT_NAME_LENGTH = 128
AMDSMI_MAX_CONTAINER_TYPE = 2

AMDSMI_GPU_UUID_SIZE = 38


class amdsmi_mm_ip(c_int):
    MM_UVD = 0
    MM_VCE = 1
    MM_VCN = 2
    MM__MAX = 3


class amdsmi_container_types(c_int):
    CONTAINER_LXC = 0
    CONTAINER_DOCKER = 1

#  ! opaque handler point to underlying implementation
amdsmi_device_handle = POINTER(c_uint)
amdsmi_socket_handle = POINTER(c_uint)

class device_type(c_int):
    UNKNOWN = 0
    AMD_GPU = 1
    AMD_CPU = 2
    NON_AMD_GPU = 3
    NON_AMD_CPU = 4

device_type__enumvalues = {
    0: 'UNKNOWN',
    1: 'AMD_GPU',
    2: 'AMD_CPU',
    3: 'NON_AMD_GPU',
    4: 'NON_AMD_CPU',
}

#Error codes retured by amd_smi_lib functions
class amdsmi_status(c_int):
    AMDSMI_STATUS_SUCCESS = 0  # Call succeeded
    AMDSMI_STATUS_INVAL = 1  # Invalid parameters
    AMDSMI_STATUS_NOT_SUPPORTED = 2  # Command not supported
    AMDSMI_STATUS_FILE_ERROR = 3 # Problem accessing a file.
    AMDSMI_STATUS_NO_PERM = 4  # Permission Denied
    AMDSMI_STATUS_OUT_OF_RESOURCES = 5  # Not enough memory
    AMDSMI_STATUS_INTERNAL_EXCEPTION = 6  # An internal exception was caught
    AMDSMI_STATUS_INPUT_OUT_OF_BOUNDS = 7 # The provided input is out of allowable or safe range
    AMDSMI_STATUS_INIT_ERROR = 8 # An error occurred when initializing internal data structures
    AMDSMI_STATUS_NOT_YET_IMPLEMENTED = 9 # Not implemented yet
    AMDSMI_STATUS_NOT_FOUND = 10  # Device Not found
    AMDSMI_STATUS_INSUFFICIENT_SIZE = 11 # Not enough resources were available for the operation
    AMDSMI_STATUS_INTERRUPT = 12 # An interrupt occurred during execution of function
    AMDSMI_STATUS_UNEXPECTED_SIZE = 13 # An unexpected amount of data was read
    AMDSMI_STATUS_NO_DATA = 14 # No data was found for a given input
    AMDSMI_STATUS_UNEXPECTED_DATA = 15 # The data read or provided to function is not what was expected
    AMDSMI_STATUS_BUSY = 16   # Device busy
    AMDSMI_STATUS_REFCOUNT_OVERFLOW = 17 # An internal reference counter exceeded INT32_MAX
    AMDSMI_LIB_START = 1000
    AMDSMI_STATUS_FAIL_LOAD_MODULE = AMDSMI_LIB_START  # Fail to load lib
    AMDSMI_STATUS_FAIL_LOAD_SYMBOL = 1001
    AMDSMI_STATUS_DRM_ERROR = 1002   # Error when call libdrm
    AMDSMI_STATUS_IO = 1003  # Error
    AMDSMI_STATUS_FAULT = 1004  # Bad address
    AMDSMI_STATUS_API_FAILED = 1005 # API call failed
    AMDSMI_STATUS_TIMEOUT = 1006  # Timeout in API call
    AMDSMI_STATUS_NO_SLOT = 1007 # No more free slot
    AMDSMI_STATUS_RETRY = 1008 # Retry operation
    AMDSMI_STATUS_NOT_INIT = 1009 # Device not initialized
    AMDSMI_STATUS_UNKNOWN_ERROR = 0xFFFFFFFF  # An unknown error occurred

amdsmi_status_t = amdsmi_status
#Clock types
class amdsmi_clk_type (c_int):
    CLK_TYPE_SYS = 0x0,   # System clock
    CLK_TYPE_FIRST = CLK_TYPE_SYS
    CLK_TYPE_GFX = CLK_TYPE_SYS
    CLK_TYPE_DF = 0x1  # Data Fabric clock (for ASICs
                       # running on a separate clock)
    CLK_TYPE_DCEF = 0x2   # Display Controller Engine clock
    CLK_TYPE_SOC = 0x3
    CLK_TYPE_MEM = 0x4
    CLK_TYPE_PCIE = 0x5
    CLK_TYPE_VCLK0 = 0x6
    CLK_TYPE_VCLK1 = 0x7
    CLK_TYPE_DCLK0 = 0x8
    CLK_TYPE_DCLK1 = 0x9
    CLK_TYPE__MAX = CLK_TYPE_DCLK1

amdsmi_clk_type_t = amdsmi_clk_type
#This enumeration is used to indicate from which part of the device a
# temperature reading should be obtained
class amdsmi_temperature_type (c_int):
    TEMPERATURE_TYPE_EDGE = 0
    TEMPERATURE_TYPE_FIRST = TEMPERATURE_TYPE_EDGE
    TEMPERATURE_TYPE_JUNCTION = 1
    TEMPERATURE_TYPE_VRAM = 2
    TEMPERATURE_TYPE_HBM_0 = 3
    TEMPERATURE_TYPE_HBM_1 = 4
    TEMPERATURE_TYPE_HBM_2 = 5
    TEMPERATURE_TYPE_HBM_3 = 6
    TEMPERATURE_TYPE_PLX = 7
    TEMPERATURE_TYPE__MAX = TEMPERATURE_TYPE_PLX

#The values of this enum are used to identify the various firmware
#blocks.
class amdsmi_fw_block_t (c_int):
    FW_ID_SMU = 1
    FW_ID_FIRST = FW_ID_SMU
    FW_ID_CP_CE = 2
    FW_ID_CP_PFP = 3
    FW_ID_CP_ME = 4
    FW_ID_CP_MEC_JT1 = 5
    FW_ID_CP_MEC_JT2 = 6
    FW_ID_CP_MEC1 = 7
    FW_ID_CP_MEC2 = 8
    FW_ID_RLC = 9
    FW_ID_SDMA0 = 10
    FW_ID_SDMA1 = 11
    FW_ID_SDMA2 = 12
    FW_ID_SDMA3 = 13
    FW_ID_SDMA4 = 14
    FW_ID_SDMA5 = 15
    FW_ID_SDMA6 = 16
    FW_ID_SDMA7 = 17
    FW_ID_VCN = 18
    FW_ID_UVD = 19
    FW_ID_VCE = 20
    FW_ID_ISP = 21
    FW_ID_DMCU_ERAM = 22  # eRAM
    FW_ID_DMCU_ISR = 23 # ISR
    FW_ID_RLC_RESTORE_LIST_GPM_MEM = 24
    FW_ID_RLC_RESTORE_LIST_SRM_MEM = 25
    FW_ID_RLC_RESTORE_LIST_CNTL = 26
    FW_ID_RLC_V = 27
    FW_ID_MMSCH = 28
    FW_ID_PSP_SYSDRV = 29
    FW_ID_PSP_SOSDRV = 30
    FW_ID_PSP_TOC = 31
    FW_ID_PSP_KEYDB = 32
    FW_ID_DFC = 33
    FW_ID_PSP_SPL = 34
    FW_ID_DRV_CAP = 35
    FW_ID_MC = 36
    FW_ID_PSP_BL = 37
    FW_ID_CP_PM4 = 38
    FW_ID_ASD = 39
    FW_ID_TA_RAS = 40
    FW_ID_XGMI = 41
    FW_ID_RLC_SRLG = 42
    FW_ID_RLC_SRLS = 43
    FW_ID_SMC = 44
    FW_ID_DMCU = 45
    FW_ID__MAX = 46

#This structure represents a range (e.g., frequencies or voltages)

class amdsmi_range_t (Structure):
    _fields_ = [
        ('lower_bound', c_uint64),
        ('upper_bound', c_uint64),
    ]

class amdsmi_xgmi_info_t (Structure):
    _fields_ = [
        ('xgmi_lanes', c_uint8),
        ('xgmi_hive_id', c_uint64),
        ('xgmi_node_id', c_uint64),
        ('index', c_uint32),
    ]

#GPU Capability info

class gfx (Structure):
    _fields_ = [
        ('gfxip_major', c_uint32),
        ('gfxip_minor', c_uint32),
        ('gfxip_cu_count', c_uint16)]

class mm (Structure):
    _fields_ = [
        ('mm_ip_count', c_uint8),
        ('mm_ip_list', c_uint8 * AMDSMI_MAX_MM_IP_COUNT)
    ]
class amdsmi_gpu_caps_t (Structure):
    _fields_ = [
        ('gfx', gfx),
        ('mm', mm),
        ('ras_supported', c_bool),
        ('max_vf_num', c_uint8),
        ('gfx_ip_count', c_uint32),
        ('dma_ip_count', c_uint32)
    ]

class amdsmi_vram_info (Structure):
    _fields_ = [
        ('vram_total', c_uint32),
        ('vram_used', c_uint32),
    ]

class amdsmi_frequency_range_t(Structure):
    _fields_ = [
        ('supported_freq_range', amdsmi_range_t),
        ('current_freq_range', amdsmi_range_t),
     ]

class bdf_submodule (Structure):
    _fields_ = [
        ('function_number', c_uint64, 3),
        ('device_number', c_uint64, 5),
        ('bus_number', c_uint64, 8),
        ('domain_number', c_uint64, 48),
    ]
class amdsmi_bdf_t (Union):
    _fields_ = [
        ('bdf_submodule', bdf_submodule),
        ('as_uint', c_uint64)
    ]

class amdsmi_power_cap_info_t (Structure):
    _fields_ = [
    ('power_cap', c_uint64),
    ('default_power_cap', c_uint64),
    ('dpm_cap', c_uint64),
    ('min_power_cap', c_uint64),
    ('max_power_cap', c_uint64)
    ]

class amdsmi_vbios_info_t (Structure):
    _fields_ =[
    ('name', c_char * AMDSMI_MAX_STRING_LENGTH),
    ('vbios_version', c_uint32),
    ('build_date', c_char * AMDSMI_MAX_DATE_LENGTH),
    ('part_number', c_char * AMDSMI_MAX_STRING_LENGTH),
    ('vbios_version_string', c_char * AMDSMI_NORMAL_STRING_LENGTH)
    ]

class fw_info_list (Structure):
    _fields_ = [
    ('fw_id', amdsmi_fw_block_t),
    ('fw_version', c_uint64)
    ]
class amdsmi_fw_info_t (Structure):
    _fields_ =[
        ('num_fw_info', c_uint8),
        ('fw_info_list', fw_info_list * amdsmi_fw_block_t.FW_ID__MAX)
    ]

class amdsmi_asic_info_t (Structure):
    _fields_ = [
        ('market_name', c_char * AMDSMI_MAX_STRING_LENGTH),
        ('family', c_uint32),
        ('vendor_id', c_uint32),
        ('subvendor_id', c_uint32),
        ('device_id', c_uint64),
        ('rev_id', c_uint32),
        ('asic_serial', c_char * AMDSMI_NORMAL_STRING_LENGTH)
    ]

class amdsmi_board_info (Structure):
    _fields_ = [
        ('serial_number', c_uint64),
        ('is_master', c_bool),
        ('model_number', c_char * AMDSMI_NORMAL_STRING_LENGTH),
        ('product_serial', c_char * AMDSMI_NORMAL_STRING_LENGTH),
        ('fru_id', c_char * AMDSMI_NORMAL_STRING_LENGTH),
        ('product_name', c_char * AMDSMI_PRODUCT_NAME_LENGTH),
        ('manufacturer_name', c_char * AMDSMI_NORMAL_STRING_LENGTH),
    ]

class amdsmi_temperature_t (Structure):
    _fields_ = [
        ('cur_temp', c_uint32)
    ]

class amdsmi_temperature_limit_t (Structure):
    _fields_ = [
        ('limit', c_uint32)
    ]

class amdsmi_power_limit_t (Structure):
    _fields_ = [
        ('limit', c_uint32)
    ]

class amdsmi_power_measure (Structure):
    _fields_ = [
        ('average_socket_power', c_uint32),
        ('energy_accumulator', c_uint64),
        ('voltage_gfx', c_uint32),
        ('voltage_soc', c_uint32),
        ('voltage_mem', c_uint32),
    ]

class amdsmi_clk_measure_t (Structure):
    _fields_ = [
        ('cur_clk', c_uint32),
        ('avg_clk', c_uint32),
        ('min_clk', c_uint32),
        ('max_clk', c_uint32)
    ]

class amdsmi_engine_usage_t (Structure):
    _fields_ = [
        ('gfx_activity', c_uint32),
        ('umc_activity', c_uint32),
        ('mm_activity', c_uint32 * AMDSMI_MAX_MM_IP_COUNT)
    ]

amdsmi_process_handle = c_uint32

class memory_usage (Structure):
    _fields_ = [
        ('gtt_mem', c_uint64),
        ('cpu_mem', c_uint64),
        ('vram_mem', c_uint64)
    ]


class engine_usage (Structure):
    _fields_ = [
        ('gfx', c_uint16 * AMDSMI_MAX_MM_IP_COUNT),
        ('compute', c_uint16 * AMDSMI_MAX_MM_IP_COUNT),
        ('sdma', c_uint16 * AMDSMI_MAX_MM_IP_COUNT),
        ('enc', c_uint16 * AMDSMI_MAX_MM_IP_COUNT),
        ('dec',c_uint16 * AMDSMI_MAX_MM_IP_COUNT)
    ]
class amdsmi_proc_info_t(Structure):
    _fields_ = [
        ('name', c_char * AMDSMI_NORMAL_STRING_LENGTH),
        ('pid', amdsmi_process_handle),
        ('mem', c_uint64),
        ('engine_usage', engine_usage),
        ('memory_usage', memory_usage),
        ('container_name', c_char * AMDSMI_NORMAL_STRING_LENGTH)

    ]
amdsmi_process_info = amdsmi_proc_info_t

# Guaranteed maximum possible number of supported frequencies
AMDSMI_MAX_NUM_FREQUENCIES = 32

# The number of points that make up a voltage-frequency curve definition
AMDSMI_NUM_VOLTAGE_CURVE_POINTS = 3

class amdsmi_dev_perf_level_t (c_int):
    AMDSMI_DEV_PERF_LEVEL_AUTO = 0 # Performance level is "auto"
    AMDSMI_DEV_PERF_LEVEL_FIRST = AMDSMI_DEV_PERF_LEVEL_AUTO
    AMDSMI_DEV_PERF_LEVEL_HIGH = 1 # Keep PowerPlay levels "high", regardless of workload
    AMDSMI_DEV_PERF_LEVEL_MANUAL = 2  # Only use values defined by manually setting the AMDSMI_CLK_TYPE_SYS speed
    AMDSMI_DEV_PERF_LEVEL_STABLE_STD = 3 # Stable power state with profiling clocks
    AMDSMI_DEV_PERF_LEVEL_STABLE_PEAK = 4 # Stable power state with peak clocks
    AMDSMI_DEV_PERF_LEVEL_STABLE_MIN_MCLK = 5 # Stable power state with minimum memory clock
    AMDSMI_DEV_PERF_LEVEL_STABLE_MIN_SCLK = 6 # Stable power state with minimum system clock
    AMDSMI_DEV_PERF_LEVEL_DETERMINISM = 7 # Performance determinism state
    AMDSMI_DEV_PERF_LEVEL_LAST = AMDSMI_DEV_PERF_LEVEL_DETERMINISM
    AMDSMI_DEV_PERF_LEVEL_UNKNOWN = 0x100 # Unknown performance level

amdsmi_dev_perf_level = amdsmi_dev_perf_level_t

class amdsmi_sw_component_t (c_int):
    AMDSMI_SW_COMP_FIRST = 0x0
    AMDSMI_SW_COMP_DRIVER = AMDSMI_SW_COMP_FIRST # Driver
    AMDSMI_SW_COMP_LAST = AMDSMI_SW_COMP_DRIVER

amdsmi_event_handle_t = c_uint64


#Event Groups
# Enum denoting an event group. The value of the enum is the
# base value for all the event enums in the group.
class amdsmi_event_group_t (c_int):
    AMDSMI_EVNT_GRP_XGMI = 0 # Data Fabric(XGMI) related events
    AMDSMI_EVNT_GRP_XGMI_DATA_OUT = 10 # XGMI Outbound data
    AMDSMI_EVNT_GRP_INVALID = 0xFFFFFFFF

# Event types
# Event type enum. Events belonging to a particular event group
# ::amdsmi_event_group_t should begin enumerating at the ::amdsmi_event_group_t
# value for that group.

class amdsmi_event_type_t (c_int):
    AMDSMI_EVNT_FIRST = amdsmi_event_group_t.AMDSMI_EVNT_GRP_XGMI
    AMDSMI_EVNT_XGMI_FIRST = amdsmi_event_group_t.AMDSMI_EVNT_GRP_XGMI
    AMDSMI_EVNT_XGMI_0_NOP_TX = AMDSMI_EVNT_XGMI_FIRST # NOPs sent to neighbor 0
    AMDSMI_EVNT_XGMI_0_REQUEST_TX = 1
    AMDSMI_EVNT_XGMI_0_RESPONSE_TX = 2
    AMDSMI_EVNT_XGMI_0_BEATS_TX = 3
    AMDSMI_EVNT_XGMI_1_NOP_TX = 4
    AMDSMI_EVNT_XGMI_1_REQUEST_TX = 5
    AMDSMI_EVNT_XGMI_1_RESPONSE_TX = 6
    AMDSMI_EVNT_XGMI_1_BEATS_TX = 7
    AMDSMI_EVNT_XGMI_LAST = 7
    AMDSMI_EVNT_XGMI_DATA_OUT_FIRST = 10
    AMDSMI_EVNT_XGMI_DATA_OUT_0 = 10
    AMDSMI_EVNT_XGMI_DATA_OUT_1 = 11
    AMDSMI_EVNT_XGMI_DATA_OUT_2 = 12
    AMDSMI_EVNT_XGMI_DATA_OUT_3 = 13
    AMDSMI_EVNT_XGMI_DATA_OUT_4 = 14
    AMDSMI_EVNT_XGMI_DATA_OUT_5 = 15
    AMDSMI_EVNT_XGMI_DATA_OUT_LAST = AMDSMI_EVNT_XGMI_DATA_OUT_5
    AMDSMI_EVNT_LAST = AMDSMI_EVNT_XGMI_DATA_OUT_LAST

class amdsmi_counter_command_t (c_int):
    AMDSMI_CNTR_CMD_START = 0
    AMDSMI_CNTR_CMD_STOP = 1

class amdsmi_counter_value_t (Structure):
    _fields_ = [
        ('value', c_uint64),
        ('time_enabled', c_uint64),
        ('time_running', c_uint64)
    ]

class amdsmi_evt_notification_type_t (c_int):
    AMDSMI_EVT_NOTIF_VMFAULT = 1 # VM page fault
    AMDSMI_EVT_NOTIF_FIRST = AMDSMI_EVT_NOTIF_VMFAULT,
    AMDSMI_EVT_NOTIF_THERMAL_THROTTLE = 2,
    AMDSMI_EVT_NOTIF_GPU_PRE_RESET = 3,
    AMDSMI_EVT_NOTIF_GPU_POST_RESET = 4,
    AMDSMI_EVT_NOTIF_LAST = AMDSMI_EVT_NOTIF_GPU_POST_RESET

# function to generate event bitmask from event id
def AMDSMI_EVENT_MASK_FROM_INDEX (i):
    return c_ulonglong(1 << (i - 1))

MAX_EVENT_NOTIFICATION_MSG_SIZE = 64

# Event notification data returned from event notification API
class amdsmi_evt_notification_data_t (Structure):
    _fields_ = [
        ('device_handle', c_void_p), # Handler of device that corresponds to the event
        ('event', amdsmi_evt_notification_type_t), # Event type
        ('message', c_char * MAX_EVENT_NOTIFICATION_MSG_SIZE) # Event message
    ]

# Temperature Metrics.  This enum is used to identify various
# temperature metrics. Corresponding values will be in millidegress Celcius.

class amdsmi_temperature_metric_t (c_int):
    AMDSMI_TEMP_CURRENT = 0 # Temperature current value
    AMDSMI_TEMP_FIRST = AMDSMI_TEMP_CURRENT
    AMDSMI_TEMP_MAX = 1 # Temperature max value
    AMDSMI_TEMP_MIN = 2 # Temperature min value
    AMDSMI_TEMP_MAX_HYST = 3 # Temperature hysteresis value for max limit (This is an absolute temperature, not a delta)
    AMDSMI_TEMP_MIN_HYST = 4 # Temperature hysteresis value for min limit (not a delta)
    AMDSMI_TEMP_CRITICAL = 5 # Temperature critical max value, typically greater than corresponding temp_max values.
    AMDSMI_TEMP_CRITICAL_HYST = 6 # Temperature hysteresis value for critical limit. (not a delta)
    AMDSMI_TEMP_EMERGENCY = 7 # Temperature emergency max value, for chips supporting more than two upper temperature
                              # limits. Must be equal or greater than corresponding temp_crit values.
    AMDSMI_TEMP_EMERGENCY_HYST = 8 # Temperature hysteresis value for emergency limit. (not a delta).
    AMDSMI_TEMP_CRIT_MIN = 9 # Temperature critical min value, typically lower than corresponding temperature min values
    AMDSMI_TEMP_CRIT_MIN_HYST = 10 # Temperature hysteresis value for critical minimum limit. (not a delta)
    AMDSMI_TEMP_OFFSET = 11 # Temperature offset which is added to the temperature reading by the chip.
    AMDSMI_TEMP_LOWEST = 12 # Historical minimum temperature.
    AMDSMI_TEMP_HIGHEST = 13 # Historical maximum temperature.
    AMDSMI_TEMP_LAST = AMDSMI_TEMP_HIGHEST

class amdsmi_voltage_metric_t (c_int):
    AMDSMI_VOLT_CURRENT = 0   #  Voltage current value.
    AMDSMI_VOLT_FIRST = AMDSMI_VOLT_CURRENT
    AMDSMI_VOLT_MAX = 1  #  Voltage max value.
    AMDSMI_VOLT_MIN_CRIT = 2 #  Voltage critical min value.
    AMDSMI_VOLT_MIN = 3      #  Voltage min value.
    AMDSMI_VOLT_MAX_CRIT = 4 #  Voltage critical max value.
    AMDSMI_VOLT_AVERAGE = 5  #  Average voltage.
    AMDSMI_VOLT_LOWEST = 6   #  Historical minimum voltage.
    AMDSMI_VOLT_HIGHEST = 7  #  Historical maximum voltage.
    AMDSMI_VOLT_LAST = AMDSMI_VOLT_HIGHEST

# This ennumeration is used to indicate which type of
# voltage reading should be obtained.

class amdsmi_voltage_type_t (c_int):
    AMDSMI_VOLT_TYPE_FIRST = 0
    AMDSMI_VOLT_TYPE_VDDGFX = AMDSMI_VOLT_TYPE_FIRST # Vddgfx GPU voltage
    AMDSMI_VOLT_TYPE_LAST = AMDSMI_VOLT_TYPE_VDDGFX
    AMDSMI_VOLT_TYPE_INVALID = 0xFFFFFFFF # Invalid type

# Pre-set Profile Selections. These bitmasks can be AND'd with the
# ::amdsmi_power_profile_status_t.available_profiles returned from
# ::amdsmi_dev_power_profile_presets_get to determine which power profiles
# are supported by the system.

class amdsmi_power_profile_preset_masks_t (c_int):
    AMDSMI_PWR_PROF_PRST_CUSTOM_MASK = 0x1        # Custom Power Profile
    AMDSMI_PWR_PROF_PRST_VIDEO_MASK = 0x2         # Video Power Profile
    AMDSMI_PWR_PROF_PRST_POWER_SAVING_MASK = 0x4  # Power Saving Profile
    AMDSMI_PWR_PROF_PRST_COMPUTE_MASK = 0x8       # Compute Saving Profile
    AMDSMI_PWR_PROF_PRST_VR_MASK = 0x10           # VR Power Profile

    # 3D Full Screen Power Profile
    AMDSMI_PWR_PROF_PRST_3D_FULL_SCR_MASK = 0x20
    AMDSMI_PWR_PROF_PRST_BOOTUP_DEFAULT = 0x40    # Default Boot Up Profile
    AMDSMI_PWR_PROF_PRST_LAST = AMDSMI_PWR_PROF_PRST_BOOTUP_DEFAULT

    # Invalid power profile
    AMDSMI_PWR_PROF_PRST_INVALID = 0xFFFFFFFFFFFFFFFF

class amdsmi_gpu_block_t (c_int):
    AMDSMI_GPU_BLOCK_INVALID =   0x0000000000000000  # Used to indicate an invalid block
    AMDSMI_GPU_BLOCK_FIRST =     0x0000000000000001

    AMDSMI_GPU_BLOCK_UMC = AMDSMI_GPU_BLOCK_FIRST     # UMC block
    AMDSMI_GPU_BLOCK_SDMA =      0x0000000000000002  # SDMA block
    AMDSMI_GPU_BLOCK_GFX =       0x0000000000000004  # GFX block
    AMDSMI_GPU_BLOCK_MMHUB =     0x0000000000000008  # MMHUB block
    AMDSMI_GPU_BLOCK_ATHUB =     0x0000000000000010  # ATHUB block
    AMDSMI_GPU_BLOCK_PCIE_BIF =  0x0000000000000020  # PCIE_BIF block
    AMDSMI_GPU_BLOCK_HDP =       0x0000000000000040  # HDP block
    AMDSMI_GPU_BLOCK_XGMI_WAFL = 0x0000000000000080  # XGMI block
    AMDSMI_GPU_BLOCK_DF =        0x0000000000000100  # DF block
    AMDSMI_GPU_BLOCK_SMN =       0x0000000000000200  # SMN block
    AMDSMI_GPU_BLOCK_SEM =       0x0000000000000400  # SEM block
    AMDSMI_GPU_BLOCK_MP0 =       0x0000000000000800  # MP0 block
    AMDSMI_GPU_BLOCK_MP1 =       0x0000000000001000  # MP1 block
    AMDSMI_GPU_BLOCK_FUSE =      0x0000000000002000  # Fuse block

    AMDSMI_GPU_BLOCK_LAST = AMDSMI_GPU_BLOCK_FUSE    # The highest bit position for supported blocks
    AMDSMI_GPU_BLOCK_RESERVED =  0x8000000000000000

class amdsmi_ras_err_state_t (c_int):
    AMDSMI_RAS_ERR_STATE_NONE = 0      # No current errors
    AMDSMI_RAS_ERR_STATE_DISABLED = 1  # ECC is disabled
    AMDSMI_RAS_ERR_STATE_PARITY = 2    # ECC errors present, but type unknown
    AMDSMI_RAS_ERR_STATE_SING_C = 3    # Single correctable error
    AMDSMI_RAS_ERR_STATE_MULT_UC = 4   # Multiple uncorrectable errors
    AMDSMI_RAS_ERR_STATE_POISON = 5    # Firmware detected error and isolated page. Treat as uncorrectable.
    AMDSMI_RAS_ERR_STATE_ENABLED = 6   # ECC is enabled

    AMDSMI_RAS_ERR_STATE_LAST = AMDSMI_RAS_ERR_STATE_ENABLED
    AMDSMI_RAS_ERR_STATE_INVALID = 0xFFFFFFFF

class amdsmi_memory_type_t (c_int):
    AMDSMI_MEM_TYPE_FIRST = 0

    AMDSMI_MEM_TYPE_VRAM = AMDSMI_MEM_TYPE_FIRST  # VRAM memory
    AMDSMI_MEM_TYPE_VIS_VRAM  = 1                 # VRAM memory that is visible
    AMDSMI_MEM_TYPE_GTT = 2                       # GTT memory

    AMDSMI_MEM_TYPE_LAST = AMDSMI_MEM_TYPE_GTT

class amdsmi_freq_ind_t (c_int):
    AMDSMI_FREQ_IND_MIN = 0  # Index used for the minimum frequency value
    AMDSMI_FREQ_IND_MAX = 1  # Index used for the maximum frequency value
    AMDSMI_FREQ_IND_INVALID = 0xFFFFFFFF  # An invalid frequency index

class amdsmi_xgmi_status_t (c_int):
    AMDSMI_XGMI_STATUS_NO_ERRORS = 0
    AMDSMI_XGMI_STATUS_ERROR = 1
    AMDSMI_XGMI_STATUS_MULTIPLE_ERRORS = 2

amdsmi_bit_field_t = c_uint64()
amdsmi_bit_field = amdsmi_bit_field_t

# Reserved Memory Page States
class amdsmi_memory_page_status_t (c_int):
    AMDSMI_MEM_PAGE_STATUS_RESERVED = 0  # Reserved. This gpu page is reserved and not available for use
    AMDSMI_MEM_PAGE_STATUS_PENDING = 1   # Pending. This gpu page is marked as bad
                                         # and will be marked reserved at the next window.
    AMDSMI_MEM_PAGE_STATUS_UNRESERVABLE = 2   # Unable to reserve this page

# Types for IO Link
class AMDSMI_IO_LINK_TYPE (c_int):
    AMDSMI_IOLINK_TYPE_UNDEFINED = 0      # unknown type.
    AMDSMI_IOLINK_TYPE_PCIEXPRESS = 1     # PCI Express
    AMDSMI_IOLINK_TYPE_XGMI = 2           # XGMI
    AMDSMI_IOLINK_TYPE_NUMIOLINKTYPES = 3 # Number of IO Link types
    AMDSMI_IOLINK_TYPE_SIZE = 0xFFFFFFFF  # Max of IO Link types

# The utilization counter type
class AMDSMI_UTILIZATION_COUNTER_TYPE (c_int):
    AMDSMI_UTILIZATION_COUNTER_FIRST = 0   # GFX Activity
    AMDSMI_COARSE_GRAIN_GFX_ACTIVITY = AMDSMI_UTILIZATION_COUNTER_FIRST
    AMDSMI_COARSE_GRAIN_MEM_ACTIVITY = 1    # Memory Activity
    AMDSMI_UTILIZATION_COUNTER_LAST = AMDSMI_COARSE_GRAIN_MEM_ACTIVITY

# Reserved Memory Page Record
class amdsmi_utilization_counter_t (Structure):
    _fields_=[
        ('page_address', c_uint64),
        ('page_size', c_uint64),
        ('status', amdsmi_memory_page_status_t),
    ]

# Number of possible power profiles that a system could support
AMDSMI_MAX_NUM_POWER_PROFILES = (sizeof(amdsmi_bit_field_t) * 8)

# This structure contains information about which power profiles are
# supported by the system for a given device, and which power profile is currently active.

class amdsmi_power_profile_status_t (Structure):
    _fields_ = [
        ('available_profiles', c_uint64), # Which profiles are supported by this system
        ('current', amdsmi_power_profile_preset_masks_t), # Which power profile is currently active
        ('num_profiles', c_uint32) # How many power profiles are available
    ]

# This structure holds information about clock frequencies.
class amdsmi_frequencies_t (Structure):
    _fields_ = [
        ('num_supported', c_uint32), # The number of supported frequencies
        ('current', c_uint32),       # The current frequency index
        ('frequency', c_uint64 * AMDSMI_MAX_NUM_FREQUENCIES), # List of frequencies.
                                                              # Only the first num_supported frequencies are valid.
    ]

#This structure holds information about the possible PCIe
#bandwidths. Specifically, the possible transfer rates and their
#associated numbers of lanes are stored here.
class amdsmi_pcie_bandwidth_t (Structure):
    _fields_ = [
        ('transfer_rate', amdsmi_frequencies_t), # Transfer rates (T/s) that are possible
        ('lanes', c_uint32 * AMDSMI_MAX_NUM_FREQUENCIES), # List of lanes for corresponding transfer rate.
                                                          # Only the first num_supported bandwidths are valid.
    ]

# This structure holds version information.

class amdsmi_version_t (Structure):
    _fields_ = [
    ('major', c_uint32), # Major version
    ('minor', c_uint32), # Minor version
    ('patch', c_uint32), # Patch, build  or stepping version
    ('build', c_char_p), # Build string
    ]

# This structure represents a point on the frequency-voltage plane.
class amdsmi_od_vddc_point_t (Structure):
    _fields_ = [
        ('frequency', c_uint64), # Frequency coordinate (in Hz)
        ('voltage', c_uint64),   # Voltage coordinate (in mV)
    ]

# This structure holds 2 ::amdsmi_range_t's, one for frequency and one for
# voltage. These 2 ranges indicate the range of possible values for the
# corresponding ::amdsmi_od_vddc_point_t.

class amdsmi_freq_volt_region_t (Structure):
    _fields_ = [
        ('freq_range', amdsmi_range_t), # The frequency range for this VDDC Curve point
        ('volt_range', amdsmi_range_t), # The voltage range for this VDDC Curve point
    ]

# Array of ::AMDSMI_NUM_VOLTAGE_CURVE_POINTS ::amdsmi_od_vddc_point_t's that
# make up the voltage frequency curve points.

class amdsmi_od_volt_curve_t (Structure):
    _fields_ = [
        # Array of ::AMDSMI_NUM_VOLTAGE_CURVE_POINTS ::amdsmi_od_vddc_point_t's that
        # make up the voltage frequency curve points.
        ('vc_points', amdsmi_od_vddc_point_t * AMDSMI_NUM_VOLTAGE_CURVE_POINTS)
    ]

# This structure holds the frequency-voltage values for a device.
class amdsmi_od_volt_freq_data_t (Structure):
    _fields_ = [
        ('curr_sclk_range', amdsmi_range_t),  # The current SCLK frequency range
        ('curr_mclk_range', amdsmi_range_t),  # The current MCLK frequency range; (upper bound only)
        ('sclk_freq_limits', amdsmi_range_t), # The range possible of SCLK values
        ('mclk_freq_limits', amdsmi_range_t), # The range possible of MCLK values
        ('curve', amdsmi_od_volt_curve_t),    # The current voltage curve
        ('num_regions', c_uint32),            # The number of voltage curve regions
    ]

# The following structures hold the gpu metrics values for a device.
# Size and version information of metrics data

class amd_metrics_table_header_t (Structure):
    _fields_ = [
        ('structure_size', c_uint16),
        ('format_revision', c_ubyte),
        ('content_revision', c_ubyte),
    ]

AMDSMI_GPU_METRICS_API_FORMAT_VER    = 1
AMDSMI_GPU_METRICS_API_CONTENT_VER_1 = 1
AMDSMI_GPU_METRICS_API_CONTENT_VER_2 = 2
AMDSMI_GPU_METRICS_API_CONTENT_VER_3 = 3

AMDSMI_NUM_HBM_INSTANCES = 4 # This should match NUM_HBM_INSTANCES
CENTRIGRADE_TO_MILLI_CENTIGRADE = 1000 # Unit conversion factor for HBM temperatures

class amdsmi_gpu_metrics_t (Structure):
    _fields_ = [
        ('common_header', amd_metrics_table_header_t),
        # Temperature
        ('temperature_edge', c_uint16),
        ('temperature_hotspot', c_uint16),
        ('temperature_mem', c_uint16),
        ('temperature_vrgfx', c_uint16),
        ('temperature_vrsoc', c_uint16),
        ('temperature_vrmem', c_uint16),
        # Utilization
        ('average_gfx_activity', c_uint16),
        ('average_umc_activity', c_uint16),
        ('average_mm_activity', c_uint16),
        # Power/Energy
        ('average_socket_power', c_uint16),
        ('energy_accumulator', c_uint64),
        # Driver attached timestamp (in ns)
        ('system_clock_counter', c_uint64),
        # Average clocks
        ('average_gfxclk_frequency', c_uint16),
        ('average_socclk_frequency', c_uint16),
        ('average_uclk_frequency', c_uint16),
        ('average_vclk0_frequency', c_uint16),
        ('average_dclk0_frequency', c_uint16),
        ('average_vclk1_frequency', c_uint16),
        ('average_dclk1_frequency', c_uint16),
        # Current clocks
        ('current_gfxclk', c_uint16),
        ('current_socclk', c_uint16),
        ('current_uclk', c_uint16),
        ('current_vclk0', c_uint16),
        ('current_dclk0', c_uint16),
        ('current_vclk1', c_uint16),
        ('current_dclk1', c_uint16),
        # Throttle status
        ('throttle_status', c_uint32),
        # Fans
        ('current_fan_speed', c_uint16),
        # Link width/speed
        ('pcie_link_width', c_uint16),  # v1 mod.(8->16)
        ('pcie_link_speed', c_uint16),  # in 0.1 GT/s; v1 mod. (8->16)
        ('padding', c_uint16),          # new in v1
        ('gfx_activity_acc', c_uint32), # new in v1
        ('mem_actvity_acc', c_uint32),  # new in v1
        ('temperature_hbm', c_uint16 * AMDSMI_NUM_HBM_INSTANCES) # new in v1
    ]

# This structure holds error counts.
class amdsmi_error_count_t (Structure):
    _fields_ = [
        ('correctable_count', c_uint64),  # Accumulated correctable errors
        ('uncorrectable_count', c_uint64) # Accumulated uncorrectable errors
    ]

# This structure holds pcie info.
class amdsmi_pcie_info_t (Structure):
    _fields_ = [
        ('pcie_lanes', c_uint16),
        ('pcie_speed', c_uint16),
    ]

class amdsmi_process_info_t (Structure):
    _fields_ = [
        ('process_id', c_uint32),   # Process ID
        ('pasid', c_uint32),        # PASID
        ('vram_usage', c_uint64),   # VRAM usage
        ('sdma_usage', c_uint64),   # SDMA usage in microseconds
        ('cu_occupancy', c_uint32), # Compute Unit usage in percent
    ]

# Opaque handle to function-support object
class amdsmi_func_id_iter_handle(Structure):
    pass
amdsmi_func_id_iter_handle_t = POINTER(amdsmi_func_id_iter_handle)

# Place-holder "variant" for functions that have don't have any variants,
# but do have monitors or sensors.

AMDSMI_DEFAULT_VARIANT = 0xFFFFFFFFFFFFFFFF

class submodule_union(Union):
    _fields_ = [
        ('memory_type', amdsmi_memory_type_t),
        ('temp_metric', amdsmi_temperature_metric_t),
        ('evnt_type', amdsmi_event_type_t),
        ('evnt_group', amdsmi_event_group_t),
        ('clk_type', amdsmi_clk_type_t),
        ('fw_block', amdsmi_fw_block_t),
        ('gpu_block_type', amdsmi_gpu_block_t),
    ]
class amdsmi_func_id_value_t (Union):
    _fields_ = [
        ('id', c_uint64),
        ('name', c_char_p),
        ('submodule', submodule_union)
    ]

amd_id = amdsmi_func_id_value_t
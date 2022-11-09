#
# Copyright (C) 2022 Advanced Micro Devices. All rights reserved.
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

# Library Initialization
from .amdsmi_interface import amdsmi_init
from .amdsmi_interface import amdsmi_shut_down

# Device Descovery
from .amdsmi_interface import amdsmi_get_device_type
from .amdsmi_interface import amdsmi_get_device_handles
from .amdsmi_interface import amdsmi_get_device_bdf
from .amdsmi_interface import amdsmi_get_device_uuid
from .amdsmi_interface import amdsmi_get_device_handle_from_bdf

# # SW Version Information
from .amdsmi_interface import amdsmi_get_driver_version

# # ASIC and Bus Static Information
from .amdsmi_interface import amdsmi_get_asic_info
from .amdsmi_interface import amdsmi_get_power_cap_info
from .amdsmi_interface import amdsmi_get_caps_info

# # Microcode and VBIOS Information
from .amdsmi_interface import amdsmi_get_vbios_info
from .amdsmi_interface import amdsmi_get_fw_info

# # GPU Monitoring
from .amdsmi_interface import amdsmi_get_gpu_activity
from .amdsmi_interface import amdsmi_get_vram_usage
from .amdsmi_interface import amdsmi_get_power_measure
from .amdsmi_interface import amdsmi_get_clock_measure
from .amdsmi_interface import amdsmi_get_temperature_measure

from .amdsmi_interface import amdsmi_get_pcie_link_status
from .amdsmi_interface import amdsmi_get_pcie_link_caps
from .amdsmi_interface import amdsmi_get_power_limit
from .amdsmi_interface import amdsmi_get_temperature_limit
from .amdsmi_interface import amdsmi_get_bad_page_info

# # Power Management
from .amdsmi_interface import amdsmi_get_target_frequency_range

# # Process Information
from .amdsmi_interface import amdsmi_get_process_list
from .amdsmi_interface import amdsmi_get_process_info

# # ECC Error Information
from .amdsmi_interface import amdsmi_get_ecc_error_count

# # Board Information
from .amdsmi_interface import amdsmi_get_board_info

# # Ras Information
from .amdsmi_interface import amdsmi_get_ras_block_features_enabled

# # Supported Function Checks
from .amdsmi_interface import amdsmi_dev_supported_func_iterator_open
from .amdsmi_interface import amdsmi_dev_supported_variant_iterator_open
from .amdsmi_interface import amdsmi_dev_supported_func_iterator_close
from .amdsmi_interface import amdsmi_func_iter_next
from .amdsmi_interface import amdsmi_func_iter_value_get

# # Unsupported Functions In Virtual Environment
from .amdsmi_interface import amdsmi_dev_pci_bandwidth_set
from .amdsmi_interface import amdsmi_dev_power_cap_set
from .amdsmi_interface import amdsmi_dev_power_profile_set
from .amdsmi_interface import amdsmi_dev_clk_range_set
from .amdsmi_interface import amdsmi_dev_od_clk_info_set
from .amdsmi_interface import amdsmi_dev_od_volt_info_set
from .amdsmi_interface import amdsmi_dev_perf_level_set_v1

# # Physical State Queries
from .amdsmi_interface import amdsmi_dev_fan_rpms_get
from .amdsmi_interface import amdsmi_dev_fan_speed_get
from .amdsmi_interface import amdsmi_dev_fan_speed_max_get
from .amdsmi_interface import amdsmi_dev_temp_metric_get
from .amdsmi_interface import amdsmi_dev_volt_metric_get

# # Clock, Power and Performance Query
from .amdsmi_interface import amdsmi_dev_busy_percent_get
from .amdsmi_interface import amdsmi_utilization_count_get
from .amdsmi_interface import amdsmi_dev_perf_level_get
from .amdsmi_interface import amdsmi_perf_determinism_mode_set
from .amdsmi_interface import amdsmi_dev_overdrive_level_get
from .amdsmi_interface import amdsmi_dev_gpu_clk_freq_get
from .amdsmi_interface import amdsmi_dev_od_volt_info_get
from .amdsmi_interface import amdsmi_dev_gpu_metrics_info_get
from .amdsmi_interface import amdsmi_dev_od_volt_curve_regions_get
from .amdsmi_interface import amdsmi_dev_power_profile_presets_get

# # Events
from .amdsmi_interface import AmdSmiEventReader

# # Enums

from .amdsmi_interface import AmdSmiInitFlags
from .amdsmi_interface import AmdSmiContainerTypes
from .amdsmi_interface import AmdSmiDeviceType
from .amdsmi_interface import AmdSmiMmIp
from .amdsmi_interface import AmdSmiFWBlock
from .amdsmi_interface import AmdSmiClockType
from .amdsmi_interface import AmdSmiTemperatureType
from .amdsmi_interface import AmdSmiDevPerfLevel
from .amdsmi_interface import AmdSmiSwComponent
from .amdsmi_interface import AmdSmiEventGroup
from .amdsmi_interface import AmdSmiEventType
from .amdsmi_interface import AmdSmiCounterCommand
from .amdsmi_interface import AmdSmiEvtNotificationType
from .amdsmi_interface import AmdSmiTemperatureMetric
from .amdsmi_interface import AmdSmiVoltageMetric
from .amdsmi_interface import AmdSmiVoltageType
from .amdsmi_interface import AmdSmiPowerProfilePresetMasks
from .amdsmi_interface import AmdSmiGpuBlock
from .amdsmi_interface import AmdSmiRasErrState
from .amdsmi_interface import AmdSmiMemoryType
from .amdsmi_interface import AmdSmiFreqInd
from .amdsmi_interface import AmdSmiXgmiStatus
from .amdsmi_interface import AmdSmiMemoryPageStatus
from .amdsmi_interface import AmdSmiIoLinkType
from .amdsmi_interface import AmdSmiUtilizationCounterType

# Exceptions

from .amdsmi_exception import AmdSmiLibraryException
from .amdsmi_exception import AmdSmiRetryException
from .amdsmi_exception import AmdSmiParameterException
from .amdsmi_exception import AmdSmiKeyException
from .amdsmi_exception import AmdSmiBdfFormatException
from .amdsmi_exception import AmdSmiTimeoutException
from .amdsmi_exception import AmdSmiException
from .amdsmi_exception import AmdSmiRetCode

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

# Library Initialization
from .amdsmi_interface import amdsmi_init
from .amdsmi_interface import amdsmi_shut_down

# Device Descovery
from .amdsmi_interface import amdsmi_get_processor_type
from .amdsmi_interface import amdsmi_get_processor_handles
from .amdsmi_interface import amdsmi_get_socket_handles
from .amdsmi_interface import amdsmi_get_socket_info

from .amdsmi_interface import amdsmi_get_gpu_device_bdf
from .amdsmi_interface import amdsmi_get_gpu_device_uuid
from .amdsmi_interface import amdsmi_get_processor_handle_from_bdf

# # SW Version Information
from .amdsmi_interface import amdsmi_get_gpu_driver_version

# # ASIC and Bus Static Information
from .amdsmi_interface import amdsmi_get_gpu_asic_info
from .amdsmi_interface import amdsmi_get_power_cap_info

# # Microcode and VBIOS Information
from .amdsmi_interface import amdsmi_get_gpu_vbios_info
from .amdsmi_interface import amdsmi_get_fw_info

# # GPU Monitoring
from .amdsmi_interface import amdsmi_get_gpu_activity
from .amdsmi_interface import amdsmi_get_gpu_vram_usage
from .amdsmi_interface import amdsmi_get_power_info
from .amdsmi_interface import amdsmi_get_clock_info

from .amdsmi_interface import amdsmi_get_pcie_link_status
from .amdsmi_interface import amdsmi_get_pcie_link_caps
from .amdsmi_interface import amdsmi_get_gpu_bad_page_info

# # Power Management
from .amdsmi_interface import amdsmi_get_gpu_target_frequency_range

# # Process Information
from .amdsmi_interface import amdsmi_get_gpu_process_list
from .amdsmi_interface import amdsmi_get_gpu_process_info

# # ECC Error Information
from .amdsmi_interface import amdsmi_get_gpu_ecc_error_count

# # Board Information
from .amdsmi_interface import amdsmi_get_gpu_board_info

# # Ras Information
from .amdsmi_interface import amdsmi_get_gpu_ras_block_features_enabled

# # Supported Function Checks
from .amdsmi_interface import amdsmi_open_supported_func_iterator
from .amdsmi_interface import amdsmi_open_supported_variant_iterator
from .amdsmi_interface import amdsmi_close_supported_func_iterator
from .amdsmi_interface import amdsmi_next_func_iter
from .amdsmi_interface import amdsmi_get_func_iter_value

# # Unsupported Functions In Virtual Environment
from .amdsmi_interface import amdsmi_set_gpu_pci_bandwidth
from .amdsmi_interface import amdsmi_set_power_cap
from .amdsmi_interface import amdsmi_set_gpu_power_profile
from .amdsmi_interface import amdsmi_set_gpu_clk_range
from .amdsmi_interface import amdsmi_set_gpu_od_clk_info
from .amdsmi_interface import amdsmi_set_gpu_od_volt_info
from .amdsmi_interface import amdsmi_set_gpu_perf_level_v1
from .amdsmi_interface import amdsmi_set_gpu_perf_level
from .amdsmi_interface import amdsmi_get_gpu_power_profile_presets
from .amdsmi_interface import amdsmi_reset_gpu
from .amdsmi_interface import amdsmi_set_gpu_perf_determinism_mode
from .amdsmi_interface import amdsmi_set_gpu_fan_speed
from .amdsmi_interface import amdsmi_reset_gpu_fan
from .amdsmi_interface import amdsmi_set_clk_freq
from .amdsmi_interface import amdsmi_set_gpu_overdrive_level_v1
from .amdsmi_interface import amdsmi_set_gpu_overdrive_level

# # Physical State Queries
from .amdsmi_interface import amdsmi_get_gpu_fan_rpms
from .amdsmi_interface import amdsmi_get_gpu_fan_speed
from .amdsmi_interface import amdsmi_get_gpu_fan_speed_max
from .amdsmi_interface import amdsmi_get_temp_metric
from .amdsmi_interface import amdsmi_get_gpu_volt_metric

# # Clock, Power and Performance Query
from .amdsmi_interface import amdsmi_get_busy_percent
from .amdsmi_interface import amdsmi_get_utilization_count
from .amdsmi_interface import amdsmi_get_gpu_perf_level
from .amdsmi_interface import amdsmi_set_gpu_perf_determinism_mode
from .amdsmi_interface import amdsmi_get_gpu_overdrive_level
from .amdsmi_interface import amdsmi_get_clk_freq
from .amdsmi_interface import amdsmi_get_gpu_od_volt_info
from .amdsmi_interface import amdsmi_get_gpu_metrics_info
from .amdsmi_interface import amdsmi_get_gpu_od_volt_curve_regions
from .amdsmi_interface import amdsmi_get_gpu_power_profile_presets

# # Performance Counters
from .amdsmi_interface import amdsmi_gpu_counter_group_supported
from .amdsmi_interface import amdsmi_gpu_create_counter
from .amdsmi_interface import amdsmi_gpu_destroy_counter
from .amdsmi_interface import amdsmi_gpu_control_counter
from .amdsmi_interface import amdsmi_gpu_read_counter
from .amdsmi_interface import amdsmi_get_gpu_available_counters

# # Error Query
from .amdsmi_interface import amdsmi_get_gpu_ecc_count
from .amdsmi_interface import amdsmi_get_gpu_ecc_enabled
from .amdsmi_interface import amdsmi_get_gpu_ecc_status
from .amdsmi_interface import amdsmi_status_string

# # System Information Query
from .amdsmi_interface import amdsmi_get_gpu_compute_process_info
from .amdsmi_interface import amdsmi_get_gpu_compute_process_info_by_pid
from .amdsmi_interface import amdsmi_get_gpu_compute_process_gpus
from .amdsmi_interface import amdsmi_gpu_xgmi_error_status
from .amdsmi_interface import amdsmi_reset_gpu_xgmi_error

# # PCIE information
from .amdsmi_interface import amdsmi_get_gpu_pci_id
from .amdsmi_interface import amdsmi_get_gpu_pci_bandwidth
from .amdsmi_interface import amdsmi_get_gpu_pci_throughput
from .amdsmi_interface import amdsmi_get_gpu_pci_replay_counter
from .amdsmi_interface import amdsmi_get_gpu_topo_numa_affinity

# # Power information
from .amdsmi_interface import amdsmi_get_energy_count

# # Memory information
from .amdsmi_interface import amdsmi_get_gpu_memory_total
from .amdsmi_interface import amdsmi_get_gpu_memory_usage
from .amdsmi_interface import amdsmi_get_gpu_memory_busy_percent
from .amdsmi_interface import amdsmi_get_gpu_memory_reserved_pages

# # Events
from .amdsmi_interface import AmdSmiEventReader

# # Device Identification information
from .amdsmi_interface import amdsmi_get_gpu_vendor_name
from .amdsmi_interface import amdsmi_get_gpu_id
from .amdsmi_interface import amdsmi_get_gpu_vram_vendor
from .amdsmi_interface import amdsmi_get_gpu_drm_render_minor
from .amdsmi_interface import amdsmi_get_gpu_subsystem_id
from .amdsmi_interface import amdsmi_get_gpu_subsystem_name

# # Version information
from .amdsmi_interface import amdsmi_get_version
from .amdsmi_interface import amdsmi_get_version_str

# # Hardware topology query
from .amdsmi_interface import amdsmi_topo_get_numa_node_number
from .amdsmi_interface import amdsmi_topo_get_link_weight
from .amdsmi_interface import amdsmi_get_minmax_bandwidth
from .amdsmi_interface import amdsmi_topo_get_link_type
from .amdsmi_interface import amdsmi_is_P2P_accessible
from .amdsmi_interface import amdsmi_get_xgmi_info

# # Enums
from .amdsmi_interface import AmdSmiInitFlags
from .amdsmi_interface import AmdSmiContainerTypes
from .amdsmi_interface import AmdSmiDeviceType
from .amdsmi_interface import AmdSmiMmIp
from .amdsmi_interface import AmdSmiFwBlock
from .amdsmi_interface import AmdSmiClkType
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
from .amdsmi_interface import AmdSmiSwComponent
from .amdsmi_interface import AmdSmiIoLinkType

# Exceptions
from .amdsmi_exception import AmdSmiLibraryException
from .amdsmi_exception import AmdSmiRetryException
from .amdsmi_exception import AmdSmiParameterException
from .amdsmi_exception import AmdSmiKeyException
from .amdsmi_exception import AmdSmiBdfFormatException
from .amdsmi_exception import AmdSmiTimeoutException
from .amdsmi_exception import AmdSmiException
from .amdsmi_exception import AmdSmiRetCode

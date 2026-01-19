// Copyright (C) 2024 Advanced Micro Devices. All rights reserved.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy of
// this software and associated documentation files (the "Software"), to deal in
// the Software without restriction, including without limitation the rights to
// use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
// the Software, and to permit persons to whom the Software is furnished to do so,
// subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
// FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
// COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
// IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
// CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
//

use crate::amdsmi_wrapper::*;
use libloading::Library;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::OnceLock;

/// Platform-specific library name
#[cfg(target_os = "linux")]
const LIB_NAME: &str = "libamd_smi.so";
#[cfg(target_os = "macos")]
const LIB_NAME: &str = "libamd_smi.dylib";
#[cfg(target_os = "windows")]
const LIB_NAME: &str = "amd_smi.dll";

/// Struct containing all dynamically loaded AMDSMI function pointers
pub struct AmdsmiLibrary {
    _lib: Library, // Keep library handle alive

    // All 138 function pointers
    pub amdsmi_init: unsafe extern "C" fn(u64) -> AmdsmiStatusT,
    pub amdsmi_shut_down: unsafe extern "C" fn() -> AmdsmiStatusT,
    pub amdsmi_get_socket_handles: unsafe extern "C" fn(*mut u32, *mut AmdsmiSocketHandle) -> AmdsmiStatusT,
    pub amdsmi_get_socket_info: unsafe extern "C" fn(AmdsmiSocketHandle, usize, *mut ::std::os::raw::c_char) -> AmdsmiStatusT,
    pub amdsmi_get_processor_handles: unsafe extern "C" fn(AmdsmiSocketHandle, *mut u32, *mut AmdsmiProcessorHandle) -> AmdsmiStatusT,
    pub amdsmi_get_processor_type: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut ProcessorTypeT) -> AmdsmiStatusT,
    pub amdsmi_get_processor_handle_from_bdf: unsafe extern "C" fn(AmdsmiBdfT, *mut AmdsmiProcessorHandle) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_device_bdf: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiBdfT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_device_uuid: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut ::std::os::raw::c_uint, *mut ::std::os::raw::c_char) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_enumeration_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiEnumerationInfoT) -> AmdsmiStatusT,
    pub amdsmi_get_cpu_affinity_with_scope: unsafe extern "C" fn(AmdsmiProcessorHandle, u32, *mut u64, AmdsmiAffinityScopeT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_virtualization_mode: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiVirtualizationModeT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_id: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u16) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_revision: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u16) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_vendor_name: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut ::std::os::raw::c_char, usize) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_vram_vendor: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut ::std::os::raw::c_char, u32) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_subsystem_id: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u16) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_subsystem_name: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut ::std::os::raw::c_char, usize) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_pci_bandwidth: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiPcieBandwidthT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_bdf_id: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u64) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_topo_numa_affinity: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut i32) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_pci_throughput: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u64, *mut u64, *mut u64) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_pci_replay_counter: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u64) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_pci_bandwidth: unsafe extern "C" fn(AmdsmiProcessorHandle, u64) -> AmdsmiStatusT,
    pub amdsmi_get_energy_count: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u64, *mut f32, *mut u64) -> AmdsmiStatusT,
    pub amdsmi_set_power_cap: unsafe extern "C" fn(AmdsmiProcessorHandle, u32, u64) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_power_profile: unsafe extern "C" fn(AmdsmiProcessorHandle, u32, AmdsmiPowerProfilePresetMasksT) -> AmdsmiStatusT,
    pub amdsmi_get_cpu_socket_power: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_get_cpu_socket_power_cap: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_get_cpu_socket_power_cap_max: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_get_cpu_pwr_svi_telemetry_all_rails: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_set_cpu_socket_power_cap: unsafe extern "C" fn(AmdsmiProcessorHandle, u32) -> AmdsmiStatusT,
    pub amdsmi_set_cpu_pwr_efficiency_mode: unsafe extern "C" fn(AmdsmiProcessorHandle, u8) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_memory_total: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiMemoryTypeT, *mut u64) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_memory_usage: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiMemoryTypeT, *mut u64) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_bad_page_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32, *mut AmdsmiRetiredPageRecordT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_bad_page_threshold: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_gpu_validate_ras_eeprom: unsafe extern "C" fn(AmdsmiProcessorHandle) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_ras_feature_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiRasFeatureT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_ras_block_features_enabled: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiGpuBlockT, *mut AmdsmiRasErrStateT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_memory_reserved_pages: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32, *mut AmdsmiRetiredPageRecordT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_fan_rpms: unsafe extern "C" fn(AmdsmiProcessorHandle, u32, *mut i64) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_fan_speed: unsafe extern "C" fn(AmdsmiProcessorHandle, u32, *mut i64) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_fan_speed_max: unsafe extern "C" fn(AmdsmiProcessorHandle, u32, *mut u64) -> AmdsmiStatusT,
    pub amdsmi_get_temp_metric: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiTemperatureTypeT, AmdsmiTemperatureMetricT, *mut i64) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_cache_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiGpuCacheInfoT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_volt_metric: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiVoltageTypeT, AmdsmiVoltageMetricT, *mut i64) -> AmdsmiStatusT,
    pub amdsmi_reset_gpu_fan: unsafe extern "C" fn(AmdsmiProcessorHandle, u32) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_fan_speed: unsafe extern "C" fn(AmdsmiProcessorHandle, u32, u64) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_busy_percent: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_get_utilization_count: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiUtilizationCounterT, u32, *mut u64) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_perf_level: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiDevPerfLevelT) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_perf_determinism_mode: unsafe extern "C" fn(AmdsmiProcessorHandle, u64) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_overdrive_level: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_mem_overdrive_level: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_get_clk_freq: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiClkTypeT, *mut AmdsmiFrequenciesT) -> AmdsmiStatusT,
    pub amdsmi_reset_gpu: unsafe extern "C" fn(AmdsmiProcessorHandle) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_od_volt_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiOdVoltFreqDataT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_metrics_header_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdMetricsTableHeaderT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_metrics_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiGpuMetricsT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_pm_metrics_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut *mut AmdsmiNameValueT, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_reg_table_info: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiRegTypeT, *mut *mut AmdsmiNameValueT, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_clk_range: unsafe extern "C" fn(AmdsmiProcessorHandle, u64, u64, AmdsmiClkTypeT) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_clk_limit: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiClkTypeT, AmdsmiClkLimitTypeT, u64) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_od_clk_info: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiFreqIndT, u64, AmdsmiClkTypeT) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_od_volt_info: unsafe extern "C" fn(AmdsmiProcessorHandle, u32, u64, u64) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_od_volt_curve_regions: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32, *mut AmdsmiFreqVoltRegionT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_power_profile_presets: unsafe extern "C" fn(AmdsmiProcessorHandle, u32, *mut AmdsmiPowerProfileStatusT) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_perf_level: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiDevPerfLevelT) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_overdrive_level: unsafe extern "C" fn(AmdsmiProcessorHandle, u32) -> AmdsmiStatusT,
    pub amdsmi_set_clk_freq: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiClkTypeT, u64) -> AmdsmiStatusT,
    pub amdsmi_get_soc_pstate: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiDpmPolicyT) -> AmdsmiStatusT,
    pub amdsmi_set_soc_pstate: unsafe extern "C" fn(AmdsmiProcessorHandle, u32) -> AmdsmiStatusT,
    pub amdsmi_get_xgmi_plpd: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiDpmPolicyT) -> AmdsmiStatusT,
    pub amdsmi_set_xgmi_plpd: unsafe extern "C" fn(AmdsmiProcessorHandle, u32) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_process_isolation: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_process_isolation: unsafe extern "C" fn(AmdsmiProcessorHandle, u32) -> AmdsmiStatusT,
    pub amdsmi_clean_gpu_local_data: unsafe extern "C" fn(AmdsmiProcessorHandle) -> AmdsmiStatusT,
    pub amdsmi_get_lib_version: unsafe extern "C" fn(*mut AmdsmiVersionT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_ecc_count: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiGpuBlockT, *mut AmdsmiErrorCountT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_ecc_enabled: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u64) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_total_ecc_count: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiErrorCountT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_cper_entries: unsafe extern "C" fn(AmdsmiProcessorHandle, u32, *mut ::std::os::raw::c_char, *mut u64, *mut *mut AmdsmiCperHdrT, *mut u64, *mut u64) -> AmdsmiStatusT,
    pub amdsmi_get_afids_from_cper: unsafe extern "C" fn(*mut ::std::os::raw::c_char, u32, *mut u64, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_ecc_status: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiGpuBlockT, *mut AmdsmiRasErrStateT) -> AmdsmiStatusT,
    pub amdsmi_status_code_to_string: unsafe extern "C" fn(AmdsmiStatusT, *mut *const ::std::os::raw::c_char) -> AmdsmiStatusT,
    pub amdsmi_gpu_counter_group_supported: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiEventGroupT) -> AmdsmiStatusT,
    pub amdsmi_gpu_create_counter: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiEventTypeT, *mut AmdsmiEventHandleT) -> AmdsmiStatusT,
    pub amdsmi_gpu_destroy_counter: unsafe extern "C" fn(AmdsmiEventHandleT) -> AmdsmiStatusT,
    pub amdsmi_gpu_control_counter: unsafe extern "C" fn(AmdsmiEventHandleT, AmdsmiCounterCommandT, *mut ::std::os::raw::c_void) -> AmdsmiStatusT,
    pub amdsmi_gpu_read_counter: unsafe extern "C" fn(AmdsmiEventHandleT, *mut AmdsmiCounterValueT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_available_counters: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiEventGroupT, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_compute_process_info: unsafe extern "C" fn(*mut AmdsmiProcessInfoT, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_compute_process_info_by_pid: unsafe extern "C" fn(u32, *mut AmdsmiProcessInfoT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_compute_process_gpus: unsafe extern "C" fn(u32, *mut u32, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_gpu_xgmi_error_status: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiXgmiStatusT) -> AmdsmiStatusT,
    pub amdsmi_reset_gpu_xgmi_error: unsafe extern "C" fn(AmdsmiProcessorHandle) -> AmdsmiStatusT,
    pub amdsmi_get_xgmi_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiXgmiInfoT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_xgmi_link_status: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiXgmiLinkStatusT) -> AmdsmiStatusT,
    pub amdsmi_get_link_metrics: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiLinkMetricsT) -> AmdsmiStatusT,
    pub amdsmi_topo_get_numa_node_number: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_topo_get_link_weight: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiProcessorHandle, *mut u64) -> AmdsmiStatusT,
    pub amdsmi_get_minmax_bandwidth_between_processors: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiProcessorHandle, *mut u64, *mut u64) -> AmdsmiStatusT,
    pub amdsmi_topo_get_link_type: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiProcessorHandle, *mut u64, *mut AmdsmiLinkTypeT) -> AmdsmiStatusT,
    pub amdsmi_get_link_topology_nearest: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiLinkTypeT, *mut AmdsmiTopologyNearestT) -> AmdsmiStatusT,
    pub amdsmi_is_P2P_accessible: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiProcessorHandle, *mut bool) -> AmdsmiStatusT,
    pub amdsmi_topo_get_p2p_status: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiProcessorHandle, *mut AmdsmiLinkTypeT, *mut AmdsmiP2pCapabilityT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_compute_partition: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut ::std::os::raw::c_char, u32) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_compute_partition: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiComputePartitionTypeT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_memory_partition: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut ::std::os::raw::c_char, u32) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_memory_partition: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiMemoryPartitionTypeT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_memory_partition_config: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiMemoryPartitionConfigT) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_memory_partition_mode: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiMemoryPartitionTypeT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_accelerator_partition_profile_config: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiAcceleratorPartitionProfileConfigT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_accelerator_partition_profile: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiAcceleratorPartitionProfileT, *mut u32) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_accelerator_partition_profile: unsafe extern "C" fn(AmdsmiProcessorHandle, u32) -> AmdsmiStatusT,
    pub amdsmi_init_gpu_event_notification: unsafe extern "C" fn(AmdsmiProcessorHandle) -> AmdsmiStatusT,
    pub amdsmi_set_gpu_event_notification_mask: unsafe extern "C" fn(AmdsmiProcessorHandle, u64) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_event_notification: unsafe extern "C" fn(::std::os::raw::c_int, *mut u32, *mut AmdsmiEvtNotificationDataT) -> AmdsmiStatusT,
    pub amdsmi_stop_gpu_event_notification: unsafe extern "C" fn(AmdsmiProcessorHandle) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_driver_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiDriverInfoT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_asic_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiAsicInfoT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_kfd_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiKfdInfoT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_vram_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiVramInfoT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_board_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiBoardInfoT) -> AmdsmiStatusT,
    pub amdsmi_get_power_cap_info: unsafe extern "C" fn(AmdsmiProcessorHandle, u32, *mut AmdsmiPowerCapInfoT) -> AmdsmiStatusT,
    pub amdsmi_get_pcie_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiPcieInfoT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_xcd_counter: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u16) -> AmdsmiStatusT,
    pub amdsmi_get_fw_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiFwInfoT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_vbios_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiVbiosInfoT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_activity: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiEngineUsageT) -> AmdsmiStatusT,
    pub amdsmi_get_power_info: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiPowerInfoT) -> AmdsmiStatusT,
    pub amdsmi_is_gpu_power_management_enabled: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut bool) -> AmdsmiStatusT,
    pub amdsmi_get_clock_info: unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiClkTypeT, *mut AmdsmiClkInfoT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_vram_usage: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiVramUsageT) -> AmdsmiStatusT,
    pub amdsmi_get_violation_status: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiViolationStatusT) -> AmdsmiStatusT,
    pub amdsmi_get_gpu_process_list: unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32, *mut AmdsmiProcInfoT) -> AmdsmiStatusT,
    pub amdsmi_gpu_driver_reload: unsafe extern "C" fn() -> AmdsmiStatusT,
}

/// Static storage for the loaded library (initialized once)
static AMDSMI_LIB: OnceLock<Result<AmdsmiLibrary, String>> = OnceLock::new();

/// Helper macro to load a symbol from the library
macro_rules! load_symbol {
    ($lib:expr, $name:ident, $type:ty) => {{
        let symbol_name = concat!(stringify!($name), "\0");
        unsafe {
            *$lib
                .get::<$type>(symbol_name.as_bytes())
                .map_err(|e| format!("Failed to load symbol '{}': {}", stringify!($name), e))?
        }
    }};
}

/// Find the path to the libamd_smi library
///
/// Search priority:
/// 1. AMDSMI_LIB_DIR environment variable
/// 2. ./lib/libamd_smi.so (current directory)
/// 3. /opt/rocm*/lib/libamd_smi.so (latest ROCm installation)
fn find_library_path() -> Result<PathBuf, String> {
    // Priority 1: AMDSMI_LIB_DIR environment variable
    if let Ok(lib_dir) = env::var("AMDSMI_LIB_DIR") {
        let path = PathBuf::from(&lib_dir).join(LIB_NAME);
        if path.exists() {
            return Ok(path);
        }
    }

    // Priority 2: ./lib/libamd_smi.so (current directory)
    if let Ok(current_dir) = env::current_dir() {
        let path = current_dir.join("lib").join(LIB_NAME);
        if path.exists() {
            return Ok(path);
        }
    }

    // Priority 3: /opt/rocm*/lib/libamd_smi.so (latest ROCm)
    if let Some(rocm_path) = find_latest_rocm_dir() {
        let path = rocm_path.join("lib").join(LIB_NAME);
        if path.exists() {
            return Ok(path);
        }
    }

    Err(format!(
        "Could not find {} in AMDSMI_LIB_DIR, ./lib, or /opt/rocm*/lib. \
         Please install ROCm or set AMDSMI_LIB_DIR environment variable.",
        LIB_NAME
    ))
}

/// Find the latest ROCm installation directory
fn find_latest_rocm_dir() -> Option<PathBuf> {
    let opt_path = Path::new("/opt");
    if !opt_path.exists() {
        return None;
    }

    fs::read_dir(opt_path)
        .ok()?
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| {
            p.is_dir()
                && p.file_name()
                    .and_then(|n| n.to_str())
                    .map(|s| s.starts_with("rocm"))
                    .unwrap_or(false)
        })
        .max() // Lexicographic max gives latest version
}

impl AmdsmiLibrary {
    /// Load the AMDSMI library and all function symbols
    pub fn load() -> Result<Self, String> {
        let lib_path = find_library_path()?;
        let lib = unsafe {
            Library::new(&lib_path)
                .map_err(|e| format!("Failed to load library at {:?}: {}", lib_path, e))?
        };

        // Load all 138 function symbols
        Ok(AmdsmiLibrary {
            amdsmi_init: load_symbol!(lib, amdsmi_init, unsafe extern "C" fn(u64) -> AmdsmiStatusT),
            amdsmi_shut_down: load_symbol!(lib, amdsmi_shut_down, unsafe extern "C" fn() -> AmdsmiStatusT),
            amdsmi_get_socket_handles: load_symbol!(lib, amdsmi_get_socket_handles, unsafe extern "C" fn(*mut u32, *mut AmdsmiSocketHandle) -> AmdsmiStatusT),
            amdsmi_get_socket_info: load_symbol!(lib, amdsmi_get_socket_info, unsafe extern "C" fn(AmdsmiSocketHandle, usize, *mut ::std::os::raw::c_char) -> AmdsmiStatusT),
            amdsmi_get_processor_handles: load_symbol!(lib, amdsmi_get_processor_handles, unsafe extern "C" fn(AmdsmiSocketHandle, *mut u32, *mut AmdsmiProcessorHandle) -> AmdsmiStatusT),
            amdsmi_get_processor_type: load_symbol!(lib, amdsmi_get_processor_type, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut ProcessorTypeT) -> AmdsmiStatusT),
            amdsmi_get_processor_handle_from_bdf: load_symbol!(lib, amdsmi_get_processor_handle_from_bdf, unsafe extern "C" fn(AmdsmiBdfT, *mut AmdsmiProcessorHandle) -> AmdsmiStatusT),
            amdsmi_get_gpu_device_bdf: load_symbol!(lib, amdsmi_get_gpu_device_bdf, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiBdfT) -> AmdsmiStatusT),
            amdsmi_get_gpu_device_uuid: load_symbol!(lib, amdsmi_get_gpu_device_uuid, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut ::std::os::raw::c_uint, *mut ::std::os::raw::c_char) -> AmdsmiStatusT),
            amdsmi_get_gpu_enumeration_info: load_symbol!(lib, amdsmi_get_gpu_enumeration_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiEnumerationInfoT) -> AmdsmiStatusT),
            amdsmi_get_cpu_affinity_with_scope: load_symbol!(lib, amdsmi_get_cpu_affinity_with_scope, unsafe extern "C" fn(AmdsmiProcessorHandle, u32, *mut u64, AmdsmiAffinityScopeT) -> AmdsmiStatusT),
            amdsmi_get_gpu_virtualization_mode: load_symbol!(lib, amdsmi_get_gpu_virtualization_mode, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiVirtualizationModeT) -> AmdsmiStatusT),
            amdsmi_get_gpu_id: load_symbol!(lib, amdsmi_get_gpu_id, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u16) -> AmdsmiStatusT),
            amdsmi_get_gpu_revision: load_symbol!(lib, amdsmi_get_gpu_revision, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u16) -> AmdsmiStatusT),
            amdsmi_get_gpu_vendor_name: load_symbol!(lib, amdsmi_get_gpu_vendor_name, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut ::std::os::raw::c_char, usize) -> AmdsmiStatusT),
            amdsmi_get_gpu_vram_vendor: load_symbol!(lib, amdsmi_get_gpu_vram_vendor, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut ::std::os::raw::c_char, u32) -> AmdsmiStatusT),
            amdsmi_get_gpu_subsystem_id: load_symbol!(lib, amdsmi_get_gpu_subsystem_id, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u16) -> AmdsmiStatusT),
            amdsmi_get_gpu_subsystem_name: load_symbol!(lib, amdsmi_get_gpu_subsystem_name, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut ::std::os::raw::c_char, usize) -> AmdsmiStatusT),
            amdsmi_get_gpu_pci_bandwidth: load_symbol!(lib, amdsmi_get_gpu_pci_bandwidth, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiPcieBandwidthT) -> AmdsmiStatusT),
            amdsmi_get_gpu_bdf_id: load_symbol!(lib, amdsmi_get_gpu_bdf_id, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u64) -> AmdsmiStatusT),
            amdsmi_get_gpu_topo_numa_affinity: load_symbol!(lib, amdsmi_get_gpu_topo_numa_affinity, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut i32) -> AmdsmiStatusT),
            amdsmi_get_gpu_pci_throughput: load_symbol!(lib, amdsmi_get_gpu_pci_throughput, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u64, *mut u64, *mut u64) -> AmdsmiStatusT),
            amdsmi_get_gpu_pci_replay_counter: load_symbol!(lib, amdsmi_get_gpu_pci_replay_counter, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u64) -> AmdsmiStatusT),
            amdsmi_set_gpu_pci_bandwidth: load_symbol!(lib, amdsmi_set_gpu_pci_bandwidth, unsafe extern "C" fn(AmdsmiProcessorHandle, u64) -> AmdsmiStatusT),
            amdsmi_get_energy_count: load_symbol!(lib, amdsmi_get_energy_count, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u64, *mut f32, *mut u64) -> AmdsmiStatusT),
            amdsmi_set_power_cap: load_symbol!(lib, amdsmi_set_power_cap, unsafe extern "C" fn(AmdsmiProcessorHandle, u32, u64) -> AmdsmiStatusT),
            amdsmi_set_gpu_power_profile: load_symbol!(lib, amdsmi_set_gpu_power_profile, unsafe extern "C" fn(AmdsmiProcessorHandle, u32, AmdsmiPowerProfilePresetMasksT) -> AmdsmiStatusT),
            amdsmi_get_cpu_socket_power: load_symbol!(lib, amdsmi_get_cpu_socket_power, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT),
            amdsmi_get_cpu_socket_power_cap: load_symbol!(lib, amdsmi_get_cpu_socket_power_cap, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT),
            amdsmi_get_cpu_socket_power_cap_max: load_symbol!(lib, amdsmi_get_cpu_socket_power_cap_max, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT),
            amdsmi_get_cpu_pwr_svi_telemetry_all_rails: load_symbol!(lib, amdsmi_get_cpu_pwr_svi_telemetry_all_rails, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT),
            amdsmi_set_cpu_socket_power_cap: load_symbol!(lib, amdsmi_set_cpu_socket_power_cap, unsafe extern "C" fn(AmdsmiProcessorHandle, u32) -> AmdsmiStatusT),
            amdsmi_set_cpu_pwr_efficiency_mode: load_symbol!(lib, amdsmi_set_cpu_pwr_efficiency_mode, unsafe extern "C" fn(AmdsmiProcessorHandle, u8) -> AmdsmiStatusT),
            amdsmi_get_gpu_memory_total: load_symbol!(lib, amdsmi_get_gpu_memory_total, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiMemoryTypeT, *mut u64) -> AmdsmiStatusT),
            amdsmi_get_gpu_memory_usage: load_symbol!(lib, amdsmi_get_gpu_memory_usage, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiMemoryTypeT, *mut u64) -> AmdsmiStatusT),
            amdsmi_get_gpu_bad_page_info: load_symbol!(lib, amdsmi_get_gpu_bad_page_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32, *mut AmdsmiRetiredPageRecordT) -> AmdsmiStatusT),
            amdsmi_get_gpu_bad_page_threshold: load_symbol!(lib, amdsmi_get_gpu_bad_page_threshold, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT),
            amdsmi_gpu_validate_ras_eeprom: load_symbol!(lib, amdsmi_gpu_validate_ras_eeprom, unsafe extern "C" fn(AmdsmiProcessorHandle) -> AmdsmiStatusT),
            amdsmi_get_gpu_ras_feature_info: load_symbol!(lib, amdsmi_get_gpu_ras_feature_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiRasFeatureT) -> AmdsmiStatusT),
            amdsmi_get_gpu_ras_block_features_enabled: load_symbol!(lib, amdsmi_get_gpu_ras_block_features_enabled, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiGpuBlockT, *mut AmdsmiRasErrStateT) -> AmdsmiStatusT),
            amdsmi_get_gpu_memory_reserved_pages: load_symbol!(lib, amdsmi_get_gpu_memory_reserved_pages, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32, *mut AmdsmiRetiredPageRecordT) -> AmdsmiStatusT),
            amdsmi_get_gpu_fan_rpms: load_symbol!(lib, amdsmi_get_gpu_fan_rpms, unsafe extern "C" fn(AmdsmiProcessorHandle, u32, *mut i64) -> AmdsmiStatusT),
            amdsmi_get_gpu_fan_speed: load_symbol!(lib, amdsmi_get_gpu_fan_speed, unsafe extern "C" fn(AmdsmiProcessorHandle, u32, *mut i64) -> AmdsmiStatusT),
            amdsmi_get_gpu_fan_speed_max: load_symbol!(lib, amdsmi_get_gpu_fan_speed_max, unsafe extern "C" fn(AmdsmiProcessorHandle, u32, *mut u64) -> AmdsmiStatusT),
            amdsmi_get_temp_metric: load_symbol!(lib, amdsmi_get_temp_metric, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiTemperatureTypeT, AmdsmiTemperatureMetricT, *mut i64) -> AmdsmiStatusT),
            amdsmi_get_gpu_cache_info: load_symbol!(lib, amdsmi_get_gpu_cache_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiGpuCacheInfoT) -> AmdsmiStatusT),
            amdsmi_get_gpu_volt_metric: load_symbol!(lib, amdsmi_get_gpu_volt_metric, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiVoltageTypeT, AmdsmiVoltageMetricT, *mut i64) -> AmdsmiStatusT),
            amdsmi_reset_gpu_fan: load_symbol!(lib, amdsmi_reset_gpu_fan, unsafe extern "C" fn(AmdsmiProcessorHandle, u32) -> AmdsmiStatusT),
            amdsmi_set_gpu_fan_speed: load_symbol!(lib, amdsmi_set_gpu_fan_speed, unsafe extern "C" fn(AmdsmiProcessorHandle, u32, u64) -> AmdsmiStatusT),
            amdsmi_get_gpu_busy_percent: load_symbol!(lib, amdsmi_get_gpu_busy_percent, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT),
            amdsmi_get_utilization_count: load_symbol!(lib, amdsmi_get_utilization_count, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiUtilizationCounterT, u32, *mut u64) -> AmdsmiStatusT),
            amdsmi_get_gpu_perf_level: load_symbol!(lib, amdsmi_get_gpu_perf_level, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiDevPerfLevelT) -> AmdsmiStatusT),
            amdsmi_set_gpu_perf_determinism_mode: load_symbol!(lib, amdsmi_set_gpu_perf_determinism_mode, unsafe extern "C" fn(AmdsmiProcessorHandle, u64) -> AmdsmiStatusT),
            amdsmi_get_gpu_overdrive_level: load_symbol!(lib, amdsmi_get_gpu_overdrive_level, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT),
            amdsmi_get_gpu_mem_overdrive_level: load_symbol!(lib, amdsmi_get_gpu_mem_overdrive_level, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT),
            amdsmi_get_clk_freq: load_symbol!(lib, amdsmi_get_clk_freq, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiClkTypeT, *mut AmdsmiFrequenciesT) -> AmdsmiStatusT),
            amdsmi_reset_gpu: load_symbol!(lib, amdsmi_reset_gpu, unsafe extern "C" fn(AmdsmiProcessorHandle) -> AmdsmiStatusT),
            amdsmi_get_gpu_od_volt_info: load_symbol!(lib, amdsmi_get_gpu_od_volt_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiOdVoltFreqDataT) -> AmdsmiStatusT),
            amdsmi_get_gpu_metrics_header_info: load_symbol!(lib, amdsmi_get_gpu_metrics_header_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdMetricsTableHeaderT) -> AmdsmiStatusT),
            amdsmi_get_gpu_metrics_info: load_symbol!(lib, amdsmi_get_gpu_metrics_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiGpuMetricsT) -> AmdsmiStatusT),
            amdsmi_get_gpu_pm_metrics_info: load_symbol!(lib, amdsmi_get_gpu_pm_metrics_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut *mut AmdsmiNameValueT, *mut u32) -> AmdsmiStatusT),
            amdsmi_get_gpu_reg_table_info: load_symbol!(lib, amdsmi_get_gpu_reg_table_info, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiRegTypeT, *mut *mut AmdsmiNameValueT, *mut u32) -> AmdsmiStatusT),
            amdsmi_set_gpu_clk_range: load_symbol!(lib, amdsmi_set_gpu_clk_range, unsafe extern "C" fn(AmdsmiProcessorHandle, u64, u64, AmdsmiClkTypeT) -> AmdsmiStatusT),
            amdsmi_set_gpu_clk_limit: load_symbol!(lib, amdsmi_set_gpu_clk_limit, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiClkTypeT, AmdsmiClkLimitTypeT, u64) -> AmdsmiStatusT),
            amdsmi_set_gpu_od_clk_info: load_symbol!(lib, amdsmi_set_gpu_od_clk_info, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiFreqIndT, u64, AmdsmiClkTypeT) -> AmdsmiStatusT),
            amdsmi_set_gpu_od_volt_info: load_symbol!(lib, amdsmi_set_gpu_od_volt_info, unsafe extern "C" fn(AmdsmiProcessorHandle, u32, u64, u64) -> AmdsmiStatusT),
            amdsmi_get_gpu_od_volt_curve_regions: load_symbol!(lib, amdsmi_get_gpu_od_volt_curve_regions, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32, *mut AmdsmiFreqVoltRegionT) -> AmdsmiStatusT),
            amdsmi_get_gpu_power_profile_presets: load_symbol!(lib, amdsmi_get_gpu_power_profile_presets, unsafe extern "C" fn(AmdsmiProcessorHandle, u32, *mut AmdsmiPowerProfileStatusT) -> AmdsmiStatusT),
            amdsmi_set_gpu_perf_level: load_symbol!(lib, amdsmi_set_gpu_perf_level, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiDevPerfLevelT) -> AmdsmiStatusT),
            amdsmi_set_gpu_overdrive_level: load_symbol!(lib, amdsmi_set_gpu_overdrive_level, unsafe extern "C" fn(AmdsmiProcessorHandle, u32) -> AmdsmiStatusT),
            amdsmi_set_clk_freq: load_symbol!(lib, amdsmi_set_clk_freq, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiClkTypeT, u64) -> AmdsmiStatusT),
            amdsmi_get_soc_pstate: load_symbol!(lib, amdsmi_get_soc_pstate, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiDpmPolicyT) -> AmdsmiStatusT),
            amdsmi_set_soc_pstate: load_symbol!(lib, amdsmi_set_soc_pstate, unsafe extern "C" fn(AmdsmiProcessorHandle, u32) -> AmdsmiStatusT),
            amdsmi_get_xgmi_plpd: load_symbol!(lib, amdsmi_get_xgmi_plpd, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiDpmPolicyT) -> AmdsmiStatusT),
            amdsmi_set_xgmi_plpd: load_symbol!(lib, amdsmi_set_xgmi_plpd, unsafe extern "C" fn(AmdsmiProcessorHandle, u32) -> AmdsmiStatusT),
            amdsmi_get_gpu_process_isolation: load_symbol!(lib, amdsmi_get_gpu_process_isolation, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT),
            amdsmi_set_gpu_process_isolation: load_symbol!(lib, amdsmi_set_gpu_process_isolation, unsafe extern "C" fn(AmdsmiProcessorHandle, u32) -> AmdsmiStatusT),
            amdsmi_clean_gpu_local_data: load_symbol!(lib, amdsmi_clean_gpu_local_data, unsafe extern "C" fn(AmdsmiProcessorHandle) -> AmdsmiStatusT),
            amdsmi_get_lib_version: load_symbol!(lib, amdsmi_get_lib_version, unsafe extern "C" fn(*mut AmdsmiVersionT) -> AmdsmiStatusT),
            amdsmi_get_gpu_ecc_count: load_symbol!(lib, amdsmi_get_gpu_ecc_count, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiGpuBlockT, *mut AmdsmiErrorCountT) -> AmdsmiStatusT),
            amdsmi_get_gpu_ecc_enabled: load_symbol!(lib, amdsmi_get_gpu_ecc_enabled, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u64) -> AmdsmiStatusT),
            amdsmi_get_gpu_total_ecc_count: load_symbol!(lib, amdsmi_get_gpu_total_ecc_count, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiErrorCountT) -> AmdsmiStatusT),
            amdsmi_get_gpu_cper_entries: load_symbol!(lib, amdsmi_get_gpu_cper_entries, unsafe extern "C" fn(AmdsmiProcessorHandle, u32, *mut ::std::os::raw::c_char, *mut u64, *mut *mut AmdsmiCperHdrT, *mut u64, *mut u64) -> AmdsmiStatusT),
            amdsmi_get_afids_from_cper: load_symbol!(lib, amdsmi_get_afids_from_cper, unsafe extern "C" fn(*mut ::std::os::raw::c_char, u32, *mut u64, *mut u32) -> AmdsmiStatusT),
            amdsmi_get_gpu_ecc_status: load_symbol!(lib, amdsmi_get_gpu_ecc_status, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiGpuBlockT, *mut AmdsmiRasErrStateT) -> AmdsmiStatusT),
            amdsmi_status_code_to_string: load_symbol!(lib, amdsmi_status_code_to_string, unsafe extern "C" fn(AmdsmiStatusT, *mut *const ::std::os::raw::c_char) -> AmdsmiStatusT),
            amdsmi_gpu_counter_group_supported: load_symbol!(lib, amdsmi_gpu_counter_group_supported, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiEventGroupT) -> AmdsmiStatusT),
            amdsmi_gpu_create_counter: load_symbol!(lib, amdsmi_gpu_create_counter, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiEventTypeT, *mut AmdsmiEventHandleT) -> AmdsmiStatusT),
            amdsmi_gpu_destroy_counter: load_symbol!(lib, amdsmi_gpu_destroy_counter, unsafe extern "C" fn(AmdsmiEventHandleT) -> AmdsmiStatusT),
            amdsmi_gpu_control_counter: load_symbol!(lib, amdsmi_gpu_control_counter, unsafe extern "C" fn(AmdsmiEventHandleT, AmdsmiCounterCommandT, *mut ::std::os::raw::c_void) -> AmdsmiStatusT),
            amdsmi_gpu_read_counter: load_symbol!(lib, amdsmi_gpu_read_counter, unsafe extern "C" fn(AmdsmiEventHandleT, *mut AmdsmiCounterValueT) -> AmdsmiStatusT),
            amdsmi_get_gpu_available_counters: load_symbol!(lib, amdsmi_get_gpu_available_counters, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiEventGroupT, *mut u32) -> AmdsmiStatusT),
            amdsmi_get_gpu_compute_process_info: load_symbol!(lib, amdsmi_get_gpu_compute_process_info, unsafe extern "C" fn(*mut AmdsmiProcessInfoT, *mut u32) -> AmdsmiStatusT),
            amdsmi_get_gpu_compute_process_info_by_pid: load_symbol!(lib, amdsmi_get_gpu_compute_process_info_by_pid, unsafe extern "C" fn(u32, *mut AmdsmiProcessInfoT) -> AmdsmiStatusT),
            amdsmi_get_gpu_compute_process_gpus: load_symbol!(lib, amdsmi_get_gpu_compute_process_gpus, unsafe extern "C" fn(u32, *mut u32, *mut u32) -> AmdsmiStatusT),
            amdsmi_gpu_xgmi_error_status: load_symbol!(lib, amdsmi_gpu_xgmi_error_status, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiXgmiStatusT) -> AmdsmiStatusT),
            amdsmi_reset_gpu_xgmi_error: load_symbol!(lib, amdsmi_reset_gpu_xgmi_error, unsafe extern "C" fn(AmdsmiProcessorHandle) -> AmdsmiStatusT),
            amdsmi_get_xgmi_info: load_symbol!(lib, amdsmi_get_xgmi_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiXgmiInfoT) -> AmdsmiStatusT),
            amdsmi_get_gpu_xgmi_link_status: load_symbol!(lib, amdsmi_get_gpu_xgmi_link_status, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiXgmiLinkStatusT) -> AmdsmiStatusT),
            amdsmi_get_link_metrics: load_symbol!(lib, amdsmi_get_link_metrics, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiLinkMetricsT) -> AmdsmiStatusT),
            amdsmi_topo_get_numa_node_number: load_symbol!(lib, amdsmi_topo_get_numa_node_number, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32) -> AmdsmiStatusT),
            amdsmi_topo_get_link_weight: load_symbol!(lib, amdsmi_topo_get_link_weight, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiProcessorHandle, *mut u64) -> AmdsmiStatusT),
            amdsmi_get_minmax_bandwidth_between_processors: load_symbol!(lib, amdsmi_get_minmax_bandwidth_between_processors, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiProcessorHandle, *mut u64, *mut u64) -> AmdsmiStatusT),
            amdsmi_topo_get_link_type: load_symbol!(lib, amdsmi_topo_get_link_type, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiProcessorHandle, *mut u64, *mut AmdsmiLinkTypeT) -> AmdsmiStatusT),
            amdsmi_get_link_topology_nearest: load_symbol!(lib, amdsmi_get_link_topology_nearest, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiLinkTypeT, *mut AmdsmiTopologyNearestT) -> AmdsmiStatusT),
            amdsmi_is_P2P_accessible: load_symbol!(lib, amdsmi_is_P2P_accessible, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiProcessorHandle, *mut bool) -> AmdsmiStatusT),
            amdsmi_topo_get_p2p_status: load_symbol!(lib, amdsmi_topo_get_p2p_status, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiProcessorHandle, *mut AmdsmiLinkTypeT, *mut AmdsmiP2pCapabilityT) -> AmdsmiStatusT),
            amdsmi_get_gpu_compute_partition: load_symbol!(lib, amdsmi_get_gpu_compute_partition, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut ::std::os::raw::c_char, u32) -> AmdsmiStatusT),
            amdsmi_set_gpu_compute_partition: load_symbol!(lib, amdsmi_set_gpu_compute_partition, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiComputePartitionTypeT) -> AmdsmiStatusT),
            amdsmi_get_gpu_memory_partition: load_symbol!(lib, amdsmi_get_gpu_memory_partition, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut ::std::os::raw::c_char, u32) -> AmdsmiStatusT),
            amdsmi_set_gpu_memory_partition: load_symbol!(lib, amdsmi_set_gpu_memory_partition, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiMemoryPartitionTypeT) -> AmdsmiStatusT),
            amdsmi_get_gpu_memory_partition_config: load_symbol!(lib, amdsmi_get_gpu_memory_partition_config, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiMemoryPartitionConfigT) -> AmdsmiStatusT),
            amdsmi_set_gpu_memory_partition_mode: load_symbol!(lib, amdsmi_set_gpu_memory_partition_mode, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiMemoryPartitionTypeT) -> AmdsmiStatusT),
            amdsmi_get_gpu_accelerator_partition_profile_config: load_symbol!(lib, amdsmi_get_gpu_accelerator_partition_profile_config, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiAcceleratorPartitionProfileConfigT) -> AmdsmiStatusT),
            amdsmi_get_gpu_accelerator_partition_profile: load_symbol!(lib, amdsmi_get_gpu_accelerator_partition_profile, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiAcceleratorPartitionProfileT, *mut u32) -> AmdsmiStatusT),
            amdsmi_set_gpu_accelerator_partition_profile: load_symbol!(lib, amdsmi_set_gpu_accelerator_partition_profile, unsafe extern "C" fn(AmdsmiProcessorHandle, u32) -> AmdsmiStatusT),
            amdsmi_init_gpu_event_notification: load_symbol!(lib, amdsmi_init_gpu_event_notification, unsafe extern "C" fn(AmdsmiProcessorHandle) -> AmdsmiStatusT),
            amdsmi_set_gpu_event_notification_mask: load_symbol!(lib, amdsmi_set_gpu_event_notification_mask, unsafe extern "C" fn(AmdsmiProcessorHandle, u64) -> AmdsmiStatusT),
            amdsmi_get_gpu_event_notification: load_symbol!(lib, amdsmi_get_gpu_event_notification, unsafe extern "C" fn(::std::os::raw::c_int, *mut u32, *mut AmdsmiEvtNotificationDataT) -> AmdsmiStatusT),
            amdsmi_stop_gpu_event_notification: load_symbol!(lib, amdsmi_stop_gpu_event_notification, unsafe extern "C" fn(AmdsmiProcessorHandle) -> AmdsmiStatusT),
            amdsmi_get_gpu_driver_info: load_symbol!(lib, amdsmi_get_gpu_driver_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiDriverInfoT) -> AmdsmiStatusT),
            amdsmi_get_gpu_asic_info: load_symbol!(lib, amdsmi_get_gpu_asic_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiAsicInfoT) -> AmdsmiStatusT),
            amdsmi_get_gpu_kfd_info: load_symbol!(lib, amdsmi_get_gpu_kfd_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiKfdInfoT) -> AmdsmiStatusT),
            amdsmi_get_gpu_vram_info: load_symbol!(lib, amdsmi_get_gpu_vram_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiVramInfoT) -> AmdsmiStatusT),
            amdsmi_get_gpu_board_info: load_symbol!(lib, amdsmi_get_gpu_board_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiBoardInfoT) -> AmdsmiStatusT),
            amdsmi_get_power_cap_info: load_symbol!(lib, amdsmi_get_power_cap_info, unsafe extern "C" fn(AmdsmiProcessorHandle, u32, *mut AmdsmiPowerCapInfoT) -> AmdsmiStatusT),
            amdsmi_get_pcie_info: load_symbol!(lib, amdsmi_get_pcie_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiPcieInfoT) -> AmdsmiStatusT),
            amdsmi_get_gpu_xcd_counter: load_symbol!(lib, amdsmi_get_gpu_xcd_counter, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u16) -> AmdsmiStatusT),
            amdsmi_get_fw_info: load_symbol!(lib, amdsmi_get_fw_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiFwInfoT) -> AmdsmiStatusT),
            amdsmi_get_gpu_vbios_info: load_symbol!(lib, amdsmi_get_gpu_vbios_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiVbiosInfoT) -> AmdsmiStatusT),
            amdsmi_get_gpu_activity: load_symbol!(lib, amdsmi_get_gpu_activity, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiEngineUsageT) -> AmdsmiStatusT),
            amdsmi_get_power_info: load_symbol!(lib, amdsmi_get_power_info, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiPowerInfoT) -> AmdsmiStatusT),
            amdsmi_is_gpu_power_management_enabled: load_symbol!(lib, amdsmi_is_gpu_power_management_enabled, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut bool) -> AmdsmiStatusT),
            amdsmi_get_clock_info: load_symbol!(lib, amdsmi_get_clock_info, unsafe extern "C" fn(AmdsmiProcessorHandle, AmdsmiClkTypeT, *mut AmdsmiClkInfoT) -> AmdsmiStatusT),
            amdsmi_get_gpu_vram_usage: load_symbol!(lib, amdsmi_get_gpu_vram_usage, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiVramUsageT) -> AmdsmiStatusT),
            amdsmi_get_violation_status: load_symbol!(lib, amdsmi_get_violation_status, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut AmdsmiViolationStatusT) -> AmdsmiStatusT),
            amdsmi_get_gpu_process_list: load_symbol!(lib, amdsmi_get_gpu_process_list, unsafe extern "C" fn(AmdsmiProcessorHandle, *mut u32, *mut AmdsmiProcInfoT) -> AmdsmiStatusT),
            amdsmi_gpu_driver_reload: load_symbol!(lib, amdsmi_gpu_driver_reload, unsafe extern "C" fn() -> AmdsmiStatusT),
            _lib: lib,
        })
    }
}

/// Get a reference to the loaded AMDSMI library
///
/// This function uses OnceLock to ensure the library is loaded only once.
/// Subsequent calls return a reference to the same library instance.
pub fn get_library() -> Result<&'static AmdsmiLibrary, &'static String> {
    AMDSMI_LIB.get_or_init(|| AmdsmiLibrary::load()).as_ref()
}

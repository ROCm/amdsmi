/*
 * Copyright (c) Advanced Micro Devices, Inc. All rights reserved.
 *
 *  Developed by:
 *            Broadcom Inc
 *
 *            www.broadcom.com
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

 
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <regex>

// Platform-specific includes
#ifdef _WIN32
    #include <io.h>
    #include <windows.h>
    #include <direct.h>
    #define S_ISREG(m) (((m) & S_IFMT) == S_IFREG)
    #define S_ISDIR(m) (((m) & S_IFMT) == S_IFDIR)
#else
    #include <sys/types.h>
    #include <dirent.h>
    #include <fcntl.h>
    #include <unistd.h>
    #include <string.h>
#endif
#include "brcm_smi/impl/brcm_smi_no_drm_switch.h"
#include "brcm_smi/impl/brcm_smi_utils.h"
#include <iostream>
#include "brcm_smi/impl/brcm_smi_lspci_commands.h"

namespace brcm {
namespace smi {

brcmsmi_status_t BrcmSmiNoDrmSwitch::init() {
    // Initialize from discovered switch devices
    // This will be implemented to discover BRCM switch devices
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BrcmSmiNoDrmSwitch::cleanup() {
    device_paths_.clear();
    host_paths_.clear();
    no_drm_bdfs_.clear();
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BrcmSmiNoDrmSwitch::query_switch_link( std::string devicePath,
  brcmsmi_switch_link_metric_t &info) {
 
  std::string current_speed = "current_link_speed";
  std::string max_speed = "max_link_speed";
  std::string current_width = "current_link_width";
  std::string max_width = "max_link_width";

  sprintf(info.current_link_speed, "%s", smi_brcm_get_value_string(devicePath, current_speed).c_str());
  sprintf(info.max_link_speed, "%s", smi_brcm_get_value_string(devicePath, max_speed).c_str());
  sprintf(info.current_link_width, "%s", smi_brcm_get_value_string(devicePath, current_width).c_str());
  sprintf(info.max_link_width, "%s", smi_brcm_get_value_string(devicePath, max_width).c_str());

  return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BrcmSmiNoDrmSwitch::query_switch_uuid(std::string bdfStr, std::string& serial) {

  get_lspci_device_data(bdfStr, "Device Serial Number ", serial);

  return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BrcmSmiNoDrmSwitch::query_switch_numa_affinity(std::string devicePath, int32_t *numa_node) {
  std::string numaFile = "numa_node";
  uint32_t numa = smi_brcm_get_value_u32(devicePath, numaFile);
  *numa_node = numa;
  return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BrcmSmiNoDrmSwitch::query_switch_cpu_affinity(std::string devicePath, std::string &cpu_affinity) {
  std::string cpuAffFile = "cpulistaffinity";
  cpu_affinity = smi_brcm_get_value_string(devicePath, cpuAffFile);
  
  return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BrcmSmiNoDrmSwitch::query_switch_device( std::string devicePath,
  brcmsmi_switch_device_metric_t &info) {
 
  std::string brcm_device_aer_dev_correctable      = "aer_dev_correctable";
  std::string brcm_device_aer_dev_fatal            = "aer_dev_fatal";
  std::string brcm_device_aer_dev_nonfatal         = "aer_dev_nonfatal";
  std::string brcm_device_ari_enabled              = "ari_enabled";
  std::string brcm_device_broken_parity_status     = "broken_parity_status";
  std::string brcm_device_class                    = "class";
  std::string brcm_device_config                   = "config";
  std::string brcm_device_consistent_dma_mask_bits = "consistent_dma_mask_bits";
  std::string brcm_device_current_link_speed       = "current_link_speed";
  std::string brcm_device_current_link_width       = "current_link_width";
  std::string brcm_device_d3cold_allowed           = "d3cold_allowed";
  std::string brcm_device_device                   = "device";
  std::string brcm_device_dma_mask_bits            = "dma_mask_bits";
  std::string brcm_device_driver_override          = "driver_override";
  std::string brcm_device_enable                   = "enable";
  std::string brcm_device_irq                      = "irq";
  std::string brcm_device_local_cpulist            = "local_cpulist";
  std::string brcm_device_local_cpus               = "local_cpus";
  std::string brcm_device_max_link_speed           = "max_link_speed";
  std::string brcm_device_max_link_width           = "max_link_width";
  std::string brcm_device_modalias                 = "modalias";
  std::string brcm_device_msi_bus                  = "msi_bus";
  std::string brcm_device_numa_node                = "numa_node";
  std::string brcm_device_pools                    = "pools";
  std::string brcm_device_power_state              = "power_state";
  std::string brcm_device_remove                   = "remove";
  std::string brcm_device_rescan                   = "rescan";
  std::string brcm_device_reset                    = "reset";
  std::string brcm_device_reset_method             = "reset_method";
  std::string brcm_device_resource                 = "resource";
  std::string brcm_device_resource0                = "resource0";
  std::string brcm_device_resource0_wc             = "resource0_wc";
  std::string brcm_device_revision                 = "revision";
  std::string brcm_device_subsystem_device         = "subsystem_device";
  std::string brcm_device_subsystem_vendor         = "subsystem_vendor";
  std::string brcm_device_uevent                   = "uevent";
  std::string brcm_device_vendor                   = "vendor";
  
  sprintf(info.brcm_device_aer_dev_correctable, "%s", smi_brcm_get_value_string(devicePath, brcm_device_aer_dev_correctable).c_str());
  sprintf(info.brcm_device_aer_dev_fatal, "%s", smi_brcm_get_value_string(devicePath, brcm_device_aer_dev_fatal).c_str());
  sprintf(info.brcm_device_aer_dev_nonfatal, "%s", smi_brcm_get_value_string(devicePath, brcm_device_aer_dev_nonfatal).c_str());
  sprintf(info.brcm_device_ari_enabled, "%s", smi_brcm_get_value_string(devicePath, brcm_device_ari_enabled).c_str());
  sprintf(info.brcm_device_broken_parity_status, "%s", smi_brcm_get_value_string(devicePath, brcm_device_broken_parity_status).c_str());
  sprintf(info.brcm_device_class, "%s", smi_brcm_get_value_string(devicePath, brcm_device_class).c_str());
  sprintf(info.brcm_device_config, "%s", smi_brcm_get_value_string(devicePath, brcm_device_config).c_str());
  sprintf(info.brcm_device_consistent_dma_mask_bits, "%s", smi_brcm_get_value_string(devicePath, brcm_device_consistent_dma_mask_bits).c_str());
  sprintf(info.brcm_device_current_link_speed, "%s", smi_brcm_get_value_string(devicePath, brcm_device_current_link_speed).c_str());
  sprintf(info.brcm_device_current_link_width, "%s", smi_brcm_get_value_string(devicePath, brcm_device_current_link_width).c_str());
  sprintf(info.brcm_device_d3cold_allowed, "%s", smi_brcm_get_value_string(devicePath, brcm_device_d3cold_allowed).c_str());
  sprintf(info.brcm_device_device, "%s", smi_brcm_get_value_string(devicePath, brcm_device_device).c_str());
  sprintf(info.brcm_device_dma_mask_bits, "%s", smi_brcm_get_value_string(devicePath, brcm_device_dma_mask_bits).c_str());
  sprintf(info.brcm_device_driver_override, "%s", smi_brcm_get_value_string(devicePath, brcm_device_driver_override).c_str());
  sprintf(info.brcm_device_enable, "%s", smi_brcm_get_value_string(devicePath, brcm_device_enable).c_str());
  sprintf(info.brcm_device_irq, "%s", smi_brcm_get_value_string(devicePath, brcm_device_irq).c_str());
  sprintf(info.brcm_device_local_cpulist, "%s", smi_brcm_get_value_string(devicePath, brcm_device_local_cpulist).c_str());
  sprintf(info.brcm_device_local_cpus, "%s", smi_brcm_get_value_string(devicePath, brcm_device_local_cpus).c_str());
  sprintf(info.brcm_device_max_link_speed, "%s", smi_brcm_get_value_string(devicePath, brcm_device_max_link_speed).c_str());
  sprintf(info.brcm_device_max_link_width, "%s", smi_brcm_get_value_string(devicePath, brcm_device_max_link_width).c_str());
  sprintf(info.brcm_device_modalias, "%s", smi_brcm_get_value_string(devicePath, brcm_device_modalias).c_str());
  sprintf(info.brcm_device_msi_bus, "%s", smi_brcm_get_value_string(devicePath, brcm_device_msi_bus).c_str());
  sprintf(info.brcm_device_numa_node, "%s", smi_brcm_get_value_string(devicePath, brcm_device_numa_node).c_str());
  sprintf(info.brcm_device_pools, "%s", smi_brcm_get_value_string(devicePath, brcm_device_pools).c_str());
  sprintf(info.brcm_device_power_state, "%s", smi_brcm_get_value_string(devicePath, brcm_device_power_state).c_str());
  sprintf(info.brcm_device_reset_method, "%s", smi_brcm_get_value_string(devicePath, brcm_device_reset_method).c_str());
  sprintf(info.brcm_device_resource, "%s", smi_brcm_get_value_string(devicePath, brcm_device_resource).c_str());
  sprintf(info.brcm_device_revision, "%s", smi_brcm_get_value_string(devicePath, brcm_device_revision).c_str());
  sprintf(info.brcm_device_subsystem_device, "%s", smi_brcm_get_value_string(devicePath, brcm_device_subsystem_device).c_str());
  sprintf(info.brcm_device_subsystem_vendor, "%s", smi_brcm_get_value_string(devicePath, brcm_device_subsystem_vendor).c_str());
  sprintf(info.brcm_device_uevent, "%s", smi_brcm_get_value_string(devicePath, brcm_device_uevent).c_str());
  sprintf(info.brcm_device_vendor, "%s", smi_brcm_get_value_string(devicePath, brcm_device_vendor).c_str());

  brcmsmi_status_t power_ret = query_switch_power(devicePath, info.brcm_device_power);
  if (power_ret != BRCMSMI_STATUS_SUCCESS) {
    // Initialize with unknown values if power query fails
    memset(&info.brcm_device_power, 0, sizeof(info.brcm_device_power));
    strcpy(info.brcm_device_power.brcm_power_async, "Unknown");
    strcpy(info.brcm_device_power.brcm_power_control, "Unknown");
  }
  

  return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BrcmSmiNoDrmSwitch::query_switch_power( std::string devicePath,
  brcmsmi_switch_power_metric_t &info) {
  
  // Initialize the struct to prevent memory corruption
  memset(&info, 0, sizeof(info));
  
  devicePath = devicePath+"/power";
  std::string brcm_power_async                  = "async";
  std::string brcm_power_control                = "control";
  std::string brcm_power_runtime_active_kids    = "runtime_active_kids";
  std::string brcm_power_runtime_active_time    = "runtime_active_time";
  std::string brcm_power_runtime_enabled        = "runtime_enabled";
  std::string brcm_power_runtime_status         = "runtime_status";
  std::string brcm_power_runtime_suspended_time = "runtime_suspended_time";
  std::string brcm_power_runtime_usage          = "runtime_usage";
  std::string brcm_power_wakeup                 = "wakeup";
  std::string brcm_power_wakeup_abort_count     = "wakeup_abort_count";
  std::string brcm_power_wakeup_active          = "wakeup_active";
  std::string brcm_power_wakeup_active_count    = "wakeup_active_count";
  std::string brcm_power_wakeup_count           = "wakeup_count";
  std::string brcm_power_wakeup_expire_count    = "wakeup_expire_count";
  std::string brcm_power_wakeup_last_time_ms    = "wakeup_last_time_ms";
  std::string brcm_power_wakeup_max_time_ms     = "wakeup_max_time_ms";
  std::string brcm_power_wakeup_total_time_ms   = "wakeup_total_time_ms";
  
  // Use safe string copying with bounds checking
  std::string async_val = smi_brcm_get_value_string(devicePath, brcm_power_async);
  std::string control_val = smi_brcm_get_value_string(devicePath, brcm_power_control);
  std::string runtime_active_kids_val = smi_brcm_get_value_string(devicePath, brcm_power_runtime_active_kids);
  std::string runtime_active_time_val = smi_brcm_get_value_string(devicePath, brcm_power_runtime_active_time);
  std::string runtime_enabled_val = smi_brcm_get_value_string(devicePath, brcm_power_runtime_enabled);
  std::string runtime_status_val = smi_brcm_get_value_string(devicePath, brcm_power_runtime_status);
  std::string runtime_suspended_time_val = smi_brcm_get_value_string(devicePath, brcm_power_runtime_suspended_time);
  std::string runtime_usage_val = smi_brcm_get_value_string(devicePath, brcm_power_runtime_usage);
  std::string wakeup_val = smi_brcm_get_value_string(devicePath, brcm_power_wakeup);
  std::string wakeup_abort_count_val = smi_brcm_get_value_string(devicePath, brcm_power_wakeup_abort_count);
  std::string wakeup_active_val = smi_brcm_get_value_string(devicePath, brcm_power_wakeup_active);
  std::string wakeup_active_count_val = smi_brcm_get_value_string(devicePath, brcm_power_wakeup_active_count);
  std::string wakeup_count_val = smi_brcm_get_value_string(devicePath, brcm_power_wakeup_count);
  std::string wakeup_expire_count_val = smi_brcm_get_value_string(devicePath, brcm_power_wakeup_expire_count);
  std::string wakeup_last_time_ms_val = smi_brcm_get_value_string(devicePath, brcm_power_wakeup_last_time_ms);
  std::string wakeup_max_time_ms_val = smi_brcm_get_value_string(devicePath, brcm_power_wakeup_max_time_ms);
  std::string wakeup_total_time_ms_val = smi_brcm_get_value_string(devicePath, brcm_power_wakeup_total_time_ms);
  
  // Copy with bounds checking
  strncpy(info.brcm_power_async, async_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_async[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_control, control_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_control[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_runtime_active_kids, runtime_active_kids_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_runtime_active_kids[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_runtime_active_time, runtime_active_time_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_runtime_active_time[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_runtime_enabled, runtime_enabled_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_runtime_enabled[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_runtime_status, runtime_status_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_runtime_status[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_runtime_suspended_time, runtime_suspended_time_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_runtime_suspended_time[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_runtime_usage, runtime_usage_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_runtime_usage[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_wakeup, wakeup_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_wakeup[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_wakeup_abort_count, wakeup_abort_count_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_wakeup_abort_count[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_wakeup_active, wakeup_active_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_wakeup_active[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_wakeup_active_count, wakeup_active_count_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_wakeup_active_count[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_wakeup_count, wakeup_count_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_wakeup_count[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_wakeup_expire_count, wakeup_expire_count_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_wakeup_expire_count[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_wakeup_last_time_ms, wakeup_last_time_ms_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_wakeup_last_time_ms[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_wakeup_max_time_ms, wakeup_max_time_ms_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_wakeup_max_time_ms[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  strncpy(info.brcm_power_wakeup_total_time_ms, wakeup_total_time_ms_val.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
  info.brcm_power_wakeup_total_time_ms[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
  
  return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BrcmSmiNoDrmSwitch::get_bdf_by_index(uint32_t switch_index, brcmsmi_bdf_t *bdf_info) const {
    if (switch_index + 1 > no_drm_bdfs_.size()) return BRCMSMI_STATUS_NOT_SUPPORTED;
    *bdf_info = no_drm_bdfs_[switch_index];
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BrcmSmiNoDrmSwitch::get_device_path_by_index(uint32_t switch_index, std::string *device_path) const {
    if (switch_index + 1 > device_paths_.size()) return BRCMSMI_STATUS_NOT_SUPPORTED;
    *device_path = device_paths_[switch_index];
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BrcmSmiNoDrmSwitch::get_hwmon_path_by_index(uint32_t switch_index, std::string *hwm_path) const {
    if (switch_index + 1 > host_paths_.size()) return BRCMSMI_STATUS_NOT_SUPPORTED;
    *hwm_path = host_paths_[switch_index];
    return BRCMSMI_STATUS_SUCCESS;
}

std::vector<std::string>& BrcmSmiNoDrmSwitch::get_device_paths() { return device_paths_; }
std::vector<std::string> &BrcmSmiNoDrmSwitch::get_hwmon_paths() { return host_paths_; }
std::vector<brcmsmi_bdf_t>& BrcmSmiNoDrmSwitch::get_bdfs_ref() { return no_drm_bdfs_; }

bool BrcmSmiNoDrmSwitch::check_if_no_drm_is_supported() { return true; }

std::vector<brcmsmi_bdf_t> BrcmSmiNoDrmSwitch::get_bdfs() {
    return no_drm_bdfs_;
}

void BrcmSmiNoDrmSwitch::add_device_data(const std::string& device_path, const std::string& hwmon_path, const brcmsmi_bdf_t& bdf) {
    device_paths_.push_back(device_path);
    host_paths_.push_back(hwmon_path);
    no_drm_bdfs_.push_back(bdf);
}

void BrcmSmiNoDrmSwitch::clear_device_data() {
    device_paths_.clear();
    host_paths_.clear();
    no_drm_bdfs_.clear();
}

uint32_t BrcmSmiNoDrmSwitch::get_vendor_id() {
    // Return Broadcom vendor ID (0x14e4)
    return 0x14e4;
}

}  // namespace smi
}  // namespace brcm

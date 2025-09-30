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


#include <functional>
#include <sstream>
#include "brcm_smi/impl/brcm_smi_nic_device.h"
#include "brcm_smi/impl/brcm_smi_utils.h"

namespace brcm {
namespace smi {

uint32_t BrcmSmiNICDevice::get_nic_id() const {
    return nic_id_;
}

std::string& BrcmSmiNICDevice::get_nic_path() {
    return path_;
}

brcmsmi_bdf_t BrcmSmiNICDevice::get_bdf() {
    return bdf_;
}

brcmsmi_status_t BrcmSmiNICDevice::get_no_drm_data() {
    brcmsmi_status_t ret;
    std::string path;
    brcmsmi_bdf_t bdf;
    ret = nodrm_.get_device_path_by_index(nic_id_, &path);
    if (ret != BRCMSMI_STATUS_SUCCESS) return BRCMSMI_STATUS_NOT_SUPPORTED;
    ret = nodrm_.get_bdf_by_index(nic_id_, &bdf);
    if (ret != BRCMSMI_STATUS_SUCCESS) return BRCMSMI_STATUS_NOT_SUPPORTED;
    path_ = path;

    return BRCMSMI_STATUS_SUCCESS;
}

pthread_mutex_t* BrcmSmiNICDevice::get_mutex() {
    return brcm::smi::GetMutex(nic_id_);
}

brcmsmi_status_t BrcmSmiNICDevice::query_nic_info(brcmsmi_nic_info_t& info) const {

    return nodrm_.query_nic_info(nic_id_, info);
}

brcmsmi_status_t BrcmSmiNICDevice::query_nic_temp_info(brcmsmi_nic_temperature_metric_t& info) const {
  brcmsmi_status_t ret;
  std::string hwmonPath;
  ret = nodrm_.get_hwmon_path_by_index(nic_id_, &hwmonPath);
  if (ret != BRCMSMI_STATUS_SUCCESS) return BRCMSMI_STATUS_NOT_SUPPORTED;

  return nodrm_.query_nic_temp(hwmonPath, info);
}

brcmsmi_status_t BrcmSmiNICDevice::query_nic_power_info(brcmsmi_nic_hwmon_power_t& info) const {
    brcmsmi_status_t ret;
    std::string hwmonPath;
    ret = nodrm_.get_hwmon_path_by_index(nic_id_, &hwmonPath);
    if (ret != BRCMSMI_STATUS_SUCCESS) return BRCMSMI_STATUS_NOT_SUPPORTED;
    return nodrm_.query_nic_power(hwmonPath, info);
}

brcmsmi_status_t BrcmSmiNICDevice::query_nic_device_info(brcmsmi_nic_hwmon_device_t& info) const {
    brcmsmi_status_t ret;
    std::string hwmonPath;
    ret = nodrm_.get_hwmon_path_by_index(nic_id_, &hwmonPath);
    if (ret != BRCMSMI_STATUS_SUCCESS) return BRCMSMI_STATUS_NOT_SUPPORTED;
    return nodrm_.query_nic_device(hwmonPath, info);
}

brcmsmi_status_t BrcmSmiNICDevice::query_nic_uuid(std::string& version) const {
  brcmsmi_status_t ret;
  std::string devicePath;
  ret = nodrm_.get_device_path_by_index(nic_id_, &devicePath);
  if (ret != BRCMSMI_STATUS_SUCCESS) return BRCMSMI_STATUS_NOT_SUPPORTED;

  return nodrm_.query_nic_uuid(devicePath, version);
}

brcmsmi_status_t BrcmSmiNICDevice::query_nic_numa_affinity(int32_t *numa_node) const {
  brcmsmi_status_t ret;
  std::string devicePath;
  ret = nodrm_.get_device_path_by_index(nic_id_, &devicePath);
  if (ret != BRCMSMI_STATUS_SUCCESS) return BRCMSMI_STATUS_NOT_SUPPORTED;

  return nodrm_.query_nic_numa_affinity(devicePath, numa_node);
}

brcmsmi_status_t BrcmSmiNICDevice::query_nic_cpu_affinity(std::string& cpu_affinity) const {
  char bdf_str[20];
  sprintf(bdf_str, "%04lx:%02x", bdf_.domain_number, bdf_.bus_number);
  std::stringstream domain_bus_sstream;
  domain_bus_sstream << "/sys/class/pci_bus/" << std::string(bdf_str);

  return nodrm_.query_nic_cpu_affinity(domain_bus_sstream.str(), cpu_affinity);
}

brcmsmi_status_t BrcmSmiNICDevice::query_nic_firmware_info(brcmsmi_nic_firmware_t& info) const {
    brcmsmi_status_t ret;
    std::string devicePath;
    ret = nodrm_.get_device_path_by_index(nic_id_, &devicePath);
    if (ret != BRCMSMI_STATUS_SUCCESS) return BRCMSMI_STATUS_NOT_SUPPORTED;

    return nodrm_.query_nic_fw_info(devicePath, info);
}

brcmsmi_status_t BrcmSmiNICDevice::query_nic_error_info(std::map<std::string, std::map<std::string, uint32_t>>& errors) const {
    // Construct PCI device path from BDF for AER error files
    char pci_path[256];
    snprintf(pci_path, sizeof(pci_path), "/sys/bus/pci/devices/%04lx:%02lx:%02lx.%ld", 
             bdf_.domain_number, bdf_.bus_number, bdf_.device_number, bdf_.function_number);
    std::string pci_device_path(pci_path);

    return nodrm_.query_nic_errors(pci_device_path, errors);
}

}  // namespace smi
}  // namespace brcm


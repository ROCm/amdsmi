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


#ifndef BRCM_SMI_INCLUDE_IMPL_BRCM_SMI_NO_DRM_NIC_H_
#define BRCM_SMI_INCLUDE_IMPL_BRCM_SMI_NO_DRM_NIC_H_

#include <unistd.h>
#include <vector>
#include <memory>
#include <mutex>
#include <map>
#include <string>
#include "brcm_smi/brcmsmi.h"

namespace brcm {
namespace smi {

class BrcmSmiNoDrmNIC {
 public:
    brcmsmi_status_t init();
    brcmsmi_status_t cleanup();
    brcmsmi_status_t get_bdf_by_index(uint32_t nic_index, brcmsmi_bdf_t *bdf_info) const;
    brcmsmi_status_t get_interface_name_by_index(uint32_t nic_index, std::string* interface_name) const;
    brcmsmi_status_t get_device_path_by_index(uint32_t nic_index, std::string* device_path) const;
    brcmsmi_status_t get_hwmon_path_by_index(uint32_t nic_index, std::string* hwm_path) const;
    std::vector<brcmsmi_bdf_t> get_bdfs();
    std::vector<std::string>& get_device_paths();
    std::vector<std::string>& get_hwmon_paths();
    std::vector<std::string>& get_interfaces();
    std::vector<brcmsmi_bdf_t>& get_bdfs_ref();
    bool check_if_no_drm_is_supported();
    
    // Methods to populate device data
    void add_device_data(const std::string& device_path, const std::string& hwmon_path, 
                        const std::string& interface_name, const brcmsmi_bdf_t& bdf);
    void clear_device_data();

    uint32_t get_vendor_id();
    brcmsmi_status_t query_nic_info(uint32_t nic_index, brcmsmi_nic_info_t& info);
    brcmsmi_status_t query_nic_uuid(std::string devicePath, std::string& version);
    brcmsmi_status_t query_nic_temp(std::string hwmonPath, brcmsmi_nic_temperature_metric_t& info);
    brcmsmi_status_t query_nic_device(std::string hwmonPath, brcmsmi_nic_hwmon_device_t& info);
    brcmsmi_status_t query_nic_power(std::string hwmonPath, brcmsmi_nic_hwmon_power_t& info);
    brcmsmi_status_t query_nic_numa_affinity(std::string devicePath, int32_t *numa_node);
    brcmsmi_status_t query_nic_cpu_affinity(std::string devicePath, std::string& cpu_affinity);
    brcmsmi_status_t query_nic_errors(std::string devicePath, std::map<std::string, std::map<std::string, uint32_t>>& errors);

    brcmsmi_status_t query_nic_fw_info(std::string devicePath, brcmsmi_nic_firmware_t& info);
 private:
    // when file is not found, the empty string will be returned
    std::vector<std::string> device_paths_;
    std::vector<std::string> hwmon_paths_;
    std::vector<std::string> interfaces_;
    std::vector<brcmsmi_bdf_t> no_drm_bdfs_;
};


}  // namespace smi
}  // namespace brcm

#endif  // BRCM_SMI_INCLUDE_IMPL_BRCM_SMI_NO_DRM_NIC_H_

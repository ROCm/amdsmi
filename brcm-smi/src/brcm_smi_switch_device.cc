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
#include <cstring>
#include <fstream>
#include <dirent.h>
#include <glob.h>
#include "brcm_smi/impl/brcm_smi_switch_device.h"
#include "brcm_smi/impl/brcm_smi_utils.h"
#include <iostream>

namespace brcm {
namespace smi {

uint32_t BrcmSmiSWITCHDevice::get_switch_id() const {
    return switch_id_;
}

std::string& BrcmSmiSWITCHDevice::get_switch_path() {
    return path_;
}

brcmsmi_bdf_t BrcmSmiSWITCHDevice::get_bdf() {
    return bdf_;
}

brcmsmi_status_t BrcmSmiSWITCHDevice::get_no_drm_data() {
    try {
        brcmsmi_status_t ret;
        std::string path;
        brcmsmi_bdf_t bdf;
        
        ret = nodrm_.get_device_path_by_index(switch_id_, &path);
        if (ret != BRCMSMI_STATUS_SUCCESS) {
            // Set default path if retrieval fails
            path_ = "/sys/bus/pci/devices/unknown";
            return BRCMSMI_STATUS_NOT_SUPPORTED;
        }
        
        ret = nodrm_.get_bdf_by_index(switch_id_, &bdf);
        if (ret != BRCMSMI_STATUS_SUCCESS) {
            // Use provided BDF if retrieval fails
            bdf = bdf_;
        } else {
            // Update BDF with retrieved value
            bdf_ = bdf;
        }
        
        path_ = path;
        return BRCMSMI_STATUS_SUCCESS;
    } catch (...) {
        // Set safe defaults on any exception
        path_ = "/sys/bus/pci/devices/unknown";
        return BRCMSMI_STATUS_NOT_SUPPORTED;
    }
}

pthread_mutex_t* BrcmSmiSWITCHDevice::get_mutex() {
    return brcm::smi::GetMutex(switch_id_);
}

brcmsmi_status_t BrcmSmiSWITCHDevice::query_switch_link_info(brcmsmi_switch_link_metric_t& info) const {
  try {
    brcmsmi_status_t ret;
    std::string devicePath;
    ret = nodrm_.get_device_path_by_index(switch_id_, &devicePath);
    if (ret != BRCMSMI_STATUS_SUCCESS) {
        // Initialize with default values
        memset(&info, 0, sizeof(info));
        strcpy(info.current_link_speed, "Unknown");
        strcpy(info.max_link_speed, "Unknown");
        strcpy(info.current_link_width, "Unknown");
        strcpy(info.max_link_width, "Unknown");
        return BRCMSMI_STATUS_NOT_SUPPORTED;
    }

    return nodrm_.query_switch_link(devicePath, info);
  } catch (...) {
    // Initialize with safe defaults on exception
    memset(&info, 0, sizeof(info));
    strcpy(info.current_link_speed, "Error");
    strcpy(info.max_link_speed, "Error");
    strcpy(info.current_link_width, "Error");
    strcpy(info.max_link_width, "Error");
    return BRCMSMI_STATUS_INTERNAL_EXCEPTION;
  }
}

brcmsmi_status_t BrcmSmiSWITCHDevice::query_switch_power_info(brcmsmi_switch_power_metric_t& info) const {
  try {
    brcmsmi_status_t ret;
    std::string devicePath; //sys/bus/pci/devices/0000:9b:00.0
    ret = nodrm_.get_device_path_by_index(switch_id_, &devicePath);
    if (ret != BRCMSMI_STATUS_SUCCESS) {
        // Initialize with default values
        memset(&info, 0, sizeof(info));
        strcpy(info.brcm_power_control, "Unknown");
        strcpy(info.brcm_power_runtime_status, "Unknown");
        strcpy(info.brcm_power_runtime_enabled, "Unknown");
        return BRCMSMI_STATUS_NOT_SUPPORTED;
    }

    return nodrm_.query_switch_power(devicePath, info);
  } catch (...) {
    // Initialize with safe defaults on exception
    memset(&info, 0, sizeof(info));
    strcpy(info.brcm_power_control, "Error");
    strcpy(info.brcm_power_runtime_status, "Error");
    strcpy(info.brcm_power_runtime_enabled, "Error");
    return BRCMSMI_STATUS_INTERNAL_EXCEPTION;
  }
}

brcmsmi_status_t BrcmSmiSWITCHDevice::query_switch_device_info(brcmsmi_switch_device_metric_t& info) const {
  try {
    brcmsmi_status_t ret;
    std::string devicePath;
    ret = nodrm_.get_device_path_by_index(switch_id_, &devicePath);
    if (ret != BRCMSMI_STATUS_SUCCESS) {
        // Initialize with default values
        memset(&info, 0, sizeof(info));
        strcpy(info.brcm_device_device, "Unknown");
        strcpy(info.brcm_device_vendor, "Unknown");
        strcpy(info.brcm_device_class, "Unknown");
        return BRCMSMI_STATUS_NOT_SUPPORTED;
    }

    return nodrm_.query_switch_device(devicePath, info);
  } catch (...) {
    // Initialize with safe defaults on exception
    memset(&info, 0, sizeof(info));
    strcpy(info.brcm_device_device, "Error");
    strcpy(info.brcm_device_vendor, "Error");
    strcpy(info.brcm_device_class, "Error");
    return BRCMSMI_STATUS_INTERNAL_EXCEPTION;
  }
}

brcmsmi_status_t BrcmSmiSWITCHDevice::query_switch_uuid(std::string& serial) const {
  brcmsmi_status_t ret;
  brcmsmi_bdf_t bdf = {};
  ret = nodrm_.get_bdf_by_index(switch_id_, &bdf);

  if (ret != BRCMSMI_STATUS_SUCCESS) return BRCMSMI_STATUS_NOT_SUPPORTED;

  char bdf_str[20];
  sprintf(bdf_str, "%04lx:%02x:%02x.%d", bdf.domain_number, bdf.bus_number,
          bdf.device_number, bdf.function_number);

  return nodrm_.query_switch_uuid(std::string(bdf_str), serial);
}

brcmsmi_status_t BrcmSmiSWITCHDevice::query_switch_numa_affinity(int32_t *numa_node) const {
  brcmsmi_status_t ret;
  std::string devicePath;
  ret = nodrm_.get_device_path_by_index(switch_id_, &devicePath);
  if (ret != BRCMSMI_STATUS_SUCCESS) return BRCMSMI_STATUS_NOT_SUPPORTED;

  return nodrm_.query_switch_numa_affinity(devicePath, numa_node);
}

brcmsmi_status_t BrcmSmiSWITCHDevice::query_switch_cpu_affinity(std::string& cpu_affinity) const {
  char bdf_str[20];
  sprintf(bdf_str, "%04lx:%02x", bdf_.domain_number, bdf_.bus_number);
  std::stringstream domain_bus_sstream;
  domain_bus_sstream << "/sys/class/pci_bus/" << std::string(bdf_str);
  
  return nodrm_.query_switch_cpu_affinity(domain_bus_sstream.str(), cpu_affinity);
}

brcmsmi_status_t BrcmSmiSWITCHDevice::query_switch_info(brcmsmi_switch_info_t& info) const {
  try {
    // Initialize the structure
    memset(&info, 0, sizeof(info));
    
    // Get device path
    brcmsmi_status_t ret;
    std::string devicePath;
    ret = nodrm_.get_device_path_by_index(switch_id_, &devicePath);
    if (ret != BRCMSMI_STATUS_SUCCESS) {
        // Set default values with sysfs-based device name
        std::string device_name = get_switch_name_from_sysfs();
        strncpy(info.switch_device_name, device_name.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
        info.switch_device_name[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
        strcpy(info.switch_part_number, "Unknown");
        strcpy(info.switch_firmware_version, "Unknown");
        strcpy(info.switch_uuid, "Unknown");
        strcpy(info.switch_vendor_id, "0x14e4");  // Broadcom vendor ID
        strcpy(info.switch_device_id, "Unknown");
        strcpy(info.switch_subsystem_vendor, "Unknown");
        strcpy(info.switch_subsystem_device, "Unknown");
        strcpy(info.switch_class, "Unknown");
        strcpy(info.switch_revision, "Unknown");
        strcpy(info.switch_irq, "Unknown");
        strcpy(info.switch_numa_node, "Unknown");
        strcpy(info.switch_current_link_speed, "Unknown");
        strcpy(info.switch_max_link_speed, "Unknown");
        strcpy(info.switch_current_link_width, "Unknown");
        strcpy(info.switch_max_link_width, "Unknown");
        strcpy(info.switch_power_control, "Unknown");
        strcpy(info.switch_power_runtime_status, "Unknown");
        strcpy(info.switch_power_runtime_enabled, "Unknown");
        info.switch_bdf = bdf_;
        return BRCMSMI_STATUS_NOT_SUPPORTED;
    }
    
    // Get device name from sysfs
    std::string device_name = get_switch_name_from_sysfs();
    strncpy(info.switch_device_name, device_name.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
    info.switch_device_name[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
    
    // Get BDF information
    brcmsmi_bdf_t bdf;
    ret = nodrm_.get_bdf_by_index(switch_id_, &bdf);
    if (ret == BRCMSMI_STATUS_SUCCESS) {
        info.switch_bdf = bdf;
    } else {
        info.switch_bdf = bdf_;
    }
    
    // Get device information
    brcmsmi_switch_device_metric_t device_info = {0};
    ret = nodrm_.query_switch_device(devicePath, device_info);
    if (ret == BRCMSMI_STATUS_SUCCESS) {
        strcpy(info.switch_vendor_id, device_info.brcm_device_vendor);
        strcpy(info.switch_device_id, device_info.brcm_device_device);
        strcpy(info.switch_subsystem_vendor, device_info.brcm_device_subsystem_vendor);
        strcpy(info.switch_subsystem_device, device_info.brcm_device_subsystem_device);
        strcpy(info.switch_class, device_info.brcm_device_class);
        strcpy(info.switch_revision, device_info.brcm_device_revision);
        strcpy(info.switch_irq, device_info.brcm_device_irq);
        strcpy(info.switch_numa_node, device_info.brcm_device_numa_node);
    } else {
        strcpy(info.switch_vendor_id, "0x14e4");  // Broadcom vendor ID
        strcpy(info.switch_device_id, "Unknown");
        strcpy(info.switch_subsystem_vendor, "Unknown");
        strcpy(info.switch_subsystem_device, "Unknown");
        strcpy(info.switch_class, "Unknown");
        strcpy(info.switch_revision, "Unknown");
        strcpy(info.switch_irq, "Unknown");
        strcpy(info.switch_numa_node, "Unknown");
    }
    
    // Get link information
    brcmsmi_switch_link_metric_t link_info = {0};
    ret = nodrm_.query_switch_link(devicePath, link_info);
    if (ret == BRCMSMI_STATUS_SUCCESS) {
        strcpy(info.switch_current_link_speed, link_info.current_link_speed);
        strcpy(info.switch_max_link_speed, link_info.max_link_speed);
        strcpy(info.switch_current_link_width, link_info.current_link_width);
        strcpy(info.switch_max_link_width, link_info.max_link_width);
    } else {
        strcpy(info.switch_current_link_speed, "Unknown");
        strcpy(info.switch_max_link_speed, "Unknown");
        strcpy(info.switch_current_link_width, "Unknown");
        strcpy(info.switch_max_link_width, "Unknown");
    }
    
    // Get power information
    brcmsmi_switch_power_metric_t power_info;
    memset(&power_info, 0, sizeof(power_info));  // Ensure clean initialization
    ret = nodrm_.query_switch_power(devicePath, power_info);
    if (ret == BRCMSMI_STATUS_SUCCESS) {
        strncpy(info.switch_power_control, power_info.brcm_power_control, BRCMSMI_MAX_STRING_LENGTH - 1);
        info.switch_power_control[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
        
        strncpy(info.switch_power_runtime_status, power_info.brcm_power_runtime_status, BRCMSMI_MAX_STRING_LENGTH - 1);
        info.switch_power_runtime_status[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
        
        strncpy(info.switch_power_runtime_enabled, power_info.brcm_power_runtime_enabled, BRCMSMI_MAX_STRING_LENGTH - 1);
        info.switch_power_runtime_enabled[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
        
    } else {
        strcpy(info.switch_power_control, "Unknown");
        strcpy(info.switch_power_runtime_status, "Unknown");
        strcpy(info.switch_power_runtime_enabled, "Unknown");
    }
    
    // Get UUID (serial number)
    std::string uuid;
    ret = query_switch_uuid(uuid);
    if (ret == BRCMSMI_STATUS_SUCCESS && !uuid.empty()) {
        strncpy(info.switch_uuid, uuid.c_str(), BRCMSMI_MAX_STRING_LENGTH - 1);
        info.switch_uuid[BRCMSMI_MAX_STRING_LENGTH - 1] = '\0';
    } else {
        // Generate UUID from BDF
        sprintf(info.switch_uuid, "%04lx:%02lx:%02lx.%ld", 
                info.switch_bdf.domain_number, 
                info.switch_bdf.bus_number,
                info.switch_bdf.device_number, 
                info.switch_bdf.function_number);
    }
    
    // Set part number and firmware version (placeholder for now)
    strcpy(info.switch_part_number, "BRCM-Switch");
    strcpy(info.switch_firmware_version, "Unknown");
    
    return BRCMSMI_STATUS_SUCCESS;
  } catch (...) {
    // Initialize with safe defaults on exception
    memset(&info, 0, sizeof(info));
    sprintf(info.switch_device_name, "Switch_%d", switch_id_);
    strcpy(info.switch_part_number, "Error");
    strcpy(info.switch_firmware_version, "Error");
    strcpy(info.switch_uuid, "Error");
    strcpy(info.switch_vendor_id, "Error");
    info.switch_bdf = bdf_;
    return BRCMSMI_STATUS_INTERNAL_EXCEPTION;
  }
}

std::string BrcmSmiSWITCHDevice::get_switch_name_from_sysfs() const {
    try {
        std::string devicePath;
        brcmsmi_status_t ret = nodrm_.get_device_path_by_index(switch_id_, &devicePath);
        if (ret != BRCMSMI_STATUS_SUCCESS) {
            return "Unknown Switch";
        }
        
        // Method 1: Try to get board_name from scsi_host (most descriptive)
        std::string board_name_pattern = devicePath + "/host*/scsi_host/host*/board_name";
        glob_t glob_result;
        if (glob(board_name_pattern.c_str(), GLOB_TILDE, nullptr, &glob_result) == 0) {
            if (glob_result.gl_pathc > 0) {
                std::ifstream board_file(glob_result.gl_pathv[0]);
                if (board_file.is_open()) {
                    std::string board_name;
                    std::getline(board_file, board_name);
                    board_file.close();
                    globfree(&glob_result);
                    
                    // Clean up the board name (remove quotes and extra spaces)
                    if (!board_name.empty()) {
                        // Remove quotes
                        if (board_name.front() == '"' && board_name.back() == '"') {
                            board_name = board_name.substr(1, board_name.length() - 2);
                        }
                        // Trim leading and trailing spaces
                        size_t start = board_name.find_first_not_of(" \t\r\n");
                        if (start != std::string::npos) {
                            size_t end = board_name.find_last_not_of(" \t\r\n");
                            board_name = board_name.substr(start, end - start + 1);
                        }
                        if (!board_name.empty()) {
                            return board_name;
                        }
                    }
                }
            }
            globfree(&glob_result);
        }
        
        // Method 2: Try to get driver name from uevent
        std::string uevent_path = devicePath + "/uevent";
        std::ifstream uevent_file(uevent_path);
        if (uevent_file.is_open()) {
            std::string line;
            while (std::getline(uevent_file, line)) {
                if (line.find("DRIVER=") == 0) {
                    std::string driver_name = line.substr(7); // Remove "DRIVER="
                    uevent_file.close();
                    if (!driver_name.empty()) {
                        // Convert to more readable format
                        if (driver_name == "mpt3sas") {
                            return "MPT3SAS SCSI Controller";
                        }
                        return driver_name + " Controller";
                    }
                }
            }
            uevent_file.close();
        }
        
        // Method 3: Try to get device and vendor IDs to create a descriptive name
        std::string device_id_path = devicePath + "/device";
        std::string vendor_id_path = devicePath + "/vendor";
        
        std::ifstream device_file(device_id_path);
        std::ifstream vendor_file(vendor_id_path);
        
        std::string device_id, vendor_id;
        if (device_file.is_open()) {
            std::getline(device_file, device_id);
            device_file.close();
        }
        if (vendor_file.is_open()) {
            std::getline(vendor_file, vendor_id);
            vendor_file.close();
        }
        
        // Create descriptive name based on vendor/device IDs
        if (vendor_id == "0x1000" && device_id == "0x00b2") {
            return "Broadcom PCIe Switch";
        } else if (vendor_id == "0x1000") {
            return "Broadcom Device " + device_id;
        } else if (!vendor_id.empty() && !device_id.empty()) {
            return "PCI Device " + vendor_id + ":" + device_id;
        }
        
        // Method 4: Fallback to BDF-based name
        char bdf_str[32];
        sprintf(bdf_str, "Switch %04lx:%02lx:%02lx.%ld", 
                bdf_.domain_number, bdf_.bus_number, 
                bdf_.device_number, bdf_.function_number);
        return std::string(bdf_str);
        
    } catch (...) {
        // Fallback name on any exception
        return "Switch_" + std::to_string(switch_id_);
    }
}

}  // namespace smi
}  // namespace brcm

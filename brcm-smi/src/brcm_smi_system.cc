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


#include "brcm_smi/impl/brcm_smi_system.h"
#include "brcm_smi/impl/brcm_smi_nic_device.h"
#include "brcm_smi/impl/brcm_smi_switch_device.h"
#include "brcm_smi/impl/brcm_smi_no_drm_nic.h"
#include "brcm_smi/impl/brcm_smi_no_drm_switch.h"
#include "brcm_smi/brcm_smi_discovery.h"
#include <algorithm>
#include <iostream>
#include <cstring>
#include <dirent.h>

// Forward declaration of BRCMDeviceInfo from discovery
struct BRCMDeviceInfo {
    std::string device_name;
    std::string path;
    uint64_t bdfid;
    uint32_t card_index;
    bool is_nic;
};

namespace brcm {
namespace smi {

// Helper function to convert bdfid to brcmsmi_bdf_t
brcmsmi_bdf_t convert_bdfid_to_bdf(uint64_t bdfid) {
    brcmsmi_bdf_t bdf = {0};
    // Extract BDF components from bdfid
    // BDFID format: ((<DOMAIN> & 0xffff) << 32) | ((<BUS> & 0xff) << 8) | ((device& 0x1f) <<3 ) | (function & 0x7)
    bdf.domain_number = (bdfid >> 32) & 0xFFFF;
    bdf.bus_number = (bdfid >> 8) & 0xFF;
    bdf.device_number = (bdfid >> 3) & 0x1F;
    bdf.function_number = bdfid & 0x7;
    return bdf;
}

// Helper function to get network interface name from device path
std::string get_network_interface_name(const std::string& device_path) {
    // Try direct path first (for hwmon paths, need to go through device symlink)
    std::string net_path = device_path + "/device/net";
    DIR* net_dir = opendir(net_path.c_str());
    
    // If that doesn't work, try direct net path
    if (net_dir == nullptr) {
        net_path = device_path + "/net";
        net_dir = opendir(net_path.c_str());
    }
    
    if (net_dir == nullptr) {
        return ""; // No network interface found
    }
    
    struct dirent* entry;
    std::string interface_name;
    
    while ((entry = readdir(net_dir)) != nullptr) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }
        // Found a network interface - use the first one
        interface_name = entry->d_name;
        break;
    }
    
    closedir(net_dir);
    return interface_name;
}

// Helper function to populate NIC no-drm data from device vectors
void populate_no_drm_nic_data(BrcmSmiNoDrmNIC& no_drm_nic, const brcmsmi_device_vectors_t& device_vectors) {
    // Clear existing data
    no_drm_nic.clear_device_data();
    
    // Populate from discovered devices
    for (uint32_t i = 0; i < device_vectors.nic_count; i++) {
        if (device_vectors.nic_devices && device_vectors.nic_devices[i]) {
            auto* device_info = static_cast<struct BRCMDeviceInfo*>(device_vectors.nic_devices[i]);
            
            // Create device paths
            std::string device_path = std::string("/sys/class/hwmon/") + device_info->device_name;
            std::string hwmon_path = device_path; // Same as device path for NIC
            
            // Convert bdfid to BDF structure
            brcmsmi_bdf_t bdf = convert_bdfid_to_bdf(device_info->bdfid);
            
            // Get actual network interface name from sysfs
            std::string interface_name = get_network_interface_name(device_path);
            if (interface_name.empty()) {
                // Fallback to generic name if no network interface found
                interface_name = "nic" + std::to_string(i);
            }
            
            // Add device data
            no_drm_nic.add_device_data(device_path, hwmon_path, interface_name, bdf);
        }
    }
}

// Helper function to populate Switch no-drm data from device vectors
void populate_no_drm_switch_data(BrcmSmiNoDrmSwitch& no_drm_switch, const brcmsmi_device_vectors_t& device_vectors) {
    // Clear existing data
    no_drm_switch.clear_device_data();
    
    // Populate from discovered devices
    for (uint32_t i = 0; i < device_vectors.switch_count; i++) {
        if (device_vectors.switch_devices && device_vectors.switch_devices[i]) {
            auto* device_info = static_cast<struct BRCMDeviceInfo*>(device_vectors.switch_devices[i]);
            
            // Create device paths
            std::string device_path = std::string("/sys/bus/pci/devices/") + device_info->device_name;
            std::string hwmon_path = device_path; // Same as device path for Switch
            
            // Convert bdfid to BDF structure
            brcmsmi_bdf_t bdf = convert_bdfid_to_bdf(device_info->bdfid);
            
            // Add device data
            no_drm_switch.add_device_data(device_path, hwmon_path, bdf);
        }
    }
}

BRCMSmiSystem::~BRCMSmiSystem() {
    shutdown();
}

brcmsmi_status_t BRCMSmiSystem::initialize() {
    std::lock_guard<std::mutex> lock(system_mutex_);
    
    if (initialized_) {
        return BRCMSMI_STATUS_SUCCESS;
    }
    
    // Discover BRCM devices using the existing discovery system
    brcmsmi_device_vectors_t device_vectors;
    brcmsmi_status_t status = brcmsmi_get_device_vectors(&device_vectors);
    if (status == BRCMSMI_STATUS_SUCCESS) {
        // Successfully discovered devices - integrate them into the socket system
        BRCMSmiSocket* socket = get_or_create_socket(0);
        
        // Create no-drm instances for device management
        static BrcmSmiNoDrmNIC no_drm_nic;
        static BrcmSmiNoDrmSwitch no_drm_switch;
        
        // Initialize no-drm instances with discovered device data
        populate_no_drm_nic_data(no_drm_nic, device_vectors);
        populate_no_drm_switch_data(no_drm_switch, device_vectors);
        
        // Add discovered NIC processors as proper BrcmSmiNICDevice objects
        std::vector<brcmsmi_bdf_t> nic_bdfs = no_drm_nic.get_bdfs();
        for (uint32_t i = 0; i < device_vectors.nic_count; i++) {
            brcmsmi_bdf_t bdf = (i < nic_bdfs.size()) ? nic_bdfs[i] : brcmsmi_bdf_t{0, 0, 0, 0};
            auto* nic_device = new BrcmSmiNICDevice(i, bdf, no_drm_nic);
            socket->add_processor(nic_device);
        }
        
        // Add discovered Switch processors as proper BrcmSmiSWITCHDevice objects
        std::vector<brcmsmi_bdf_t> switch_bdfs = no_drm_switch.get_bdfs();
        for (uint32_t i = 0; i < device_vectors.switch_count; i++) {
            brcmsmi_bdf_t bdf = (i < switch_bdfs.size()) ? switch_bdfs[i] : brcmsmi_bdf_t{0, 0, 0, 0};
            auto* switch_device = new BrcmSmiSWITCHDevice(i, bdf, no_drm_switch);
            socket->add_processor(switch_device);
        }
    } else {
        // If discovery fails, create a default socket with placeholder devices
        BRCMSmiSocket* socket = get_or_create_socket(0);
        
        // Create placeholder NIC processor
        auto* nic_processor = new BRCMSmiProcessor(BRCMSMI_PROCESSOR_TYPE_NIC, 0);
        socket->add_processor(nic_processor);
        
        // Create placeholder Switch processor
        auto* switch_processor = new BRCMSmiProcessor(BRCMSMI_PROCESSOR_TYPE_SWITCH, 0);
        socket->add_processor(switch_processor);
    }
    
    initialized_ = true;
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BRCMSmiSystem::shutdown() {
    std::lock_guard<std::mutex> lock(system_mutex_);
    
    if (!initialized_) {
        return BRCMSMI_STATUS_SUCCESS;
    }
    
    // Clear all sockets (this will also clean up processors)
    sockets_.clear();
    
    initialized_ = false;
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BRCMSmiSystem::get_socket_count(uint32_t* socket_count) const {
    if (socket_count == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    std::lock_guard<std::mutex> lock(system_mutex_);
    *socket_count = static_cast<uint32_t>(sockets_.size());
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BRCMSmiSystem::get_socket_handles(uint32_t* socket_count, brcmsmi_socket_handle* socket_handles) const {
    if (socket_count == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    std::lock_guard<std::mutex> lock(system_mutex_);
    
    uint32_t available_sockets = static_cast<uint32_t>(sockets_.size());
    
    if (socket_handles == nullptr) {
        // Just return the count
        *socket_count = available_sockets;
        return BRCMSMI_STATUS_SUCCESS;
    }
    
    // Return handles up to the requested count
    uint32_t handles_to_return = std::min(*socket_count, available_sockets);
    for (uint32_t i = 0; i < handles_to_return; i++) {
        socket_handles[i] = reinterpret_cast<brcmsmi_socket_handle>(sockets_[i].get());
    }
    
    *socket_count = handles_to_return;
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BRCMSmiSystem::handle_to_socket(brcmsmi_socket_handle socket_handle, BRCMSmiSocket** socket) const {
    if (socket_handle == nullptr || socket == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    std::lock_guard<std::mutex> lock(system_mutex_);
    
    // Find the socket by handle
    for (const auto& s : sockets_) {
        if (reinterpret_cast<brcmsmi_socket_handle>(s.get()) == socket_handle) {
            *socket = s.get();
            return BRCMSMI_STATUS_SUCCESS;
        }
    }
    
    return BRCMSMI_STATUS_INVALID_ARGS;
}

brcmsmi_status_t BRCMSmiSystem::get_processor_handles(brcmsmi_socket_handle socket_handle,
                                                     brcmsmi_processor_type_t processor_type,
                                                     uint32_t* processor_count,
                                                     brcmsmi_processor_handle* processor_handles) const {
    if (processor_count == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    BRCMSmiSocket* socket = nullptr;
    brcmsmi_status_t status = handle_to_socket(socket_handle, &socket);
    if (status != BRCMSMI_STATUS_SUCCESS) {
        return status;
    }
    
    std::vector<BRCMSmiProcessor*>& processors = socket->get_processors(processor_type);
    uint32_t available_processors = static_cast<uint32_t>(processors.size());
    
    if (processor_handles == nullptr) {
        // Just return the count
        *processor_count = available_processors;
        return BRCMSMI_STATUS_SUCCESS;
    }
    
    // Return handles up to the requested count
    uint32_t handles_to_return = std::min(*processor_count, available_processors);
    for (uint32_t i = 0; i < handles_to_return; i++) {
        processor_handles[i] = reinterpret_cast<brcmsmi_processor_handle>(processors[i]);
    }
    
    *processor_count = handles_to_return;
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BRCMSmiSystem::handle_to_processor(brcmsmi_processor_handle processor_handle, BRCMSmiProcessor** processor) const {
    if (processor_handle == nullptr || processor == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    std::lock_guard<std::mutex> lock(system_mutex_);
    
    // Search all sockets for the processor
    for (const auto& socket : sockets_) {
        auto& all_processors = socket->get_processors();
        for (auto* proc : all_processors) {
            if (reinterpret_cast<brcmsmi_processor_handle>(proc) == processor_handle) {
                *processor = proc;
                return BRCMSMI_STATUS_SUCCESS;
            }
        }
    }
    
    return BRCMSMI_STATUS_INVALID_ARGS;
}

BRCMSmiSocket* BRCMSmiSystem::get_or_create_socket(uint32_t socket_index) {
    // Find existing socket
    for (auto& socket : sockets_) {
        if (socket->get_socket_index() == socket_index) {
            return socket.get();
        }
    }
    
    // Create new socket
    auto new_socket = std::make_unique<BRCMSmiSocket>(socket_index);
    BRCMSmiSocket* socket_ptr = new_socket.get();
    sockets_.push_back(std::move(new_socket));
    
    return socket_ptr;
}

}  // namespace smi
}  // namespace brcm

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
#include <iostream>
#include <sstream>
#include <vector>
#include <memory>
#include <algorithm>

// Platform-specific includes
#ifdef _WIN32
    #include <io.h>
    #include <windows.h>
    #include <direct.h>
    #define S_ISREG(m) (((m) & S_IFMT) == S_IFREG)
    #define S_ISDIR(m) (((m) & S_IFMT) == S_IFDIR)
#else
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <dirent.h>
    #include <fcntl.h>
    #include <unistd.h>
    #include <string.h>
#endif
#include <functional>
#include <fstream>
#include "brcm_smi/brcmsmi.h"
#include "brcm_smi/brcm_smi_device.h"
#include "brcm_smi/brcm_smi_discovery.h"
#include "brcm_smi/brcm_smi_utils.h"
#include "brcm_smi/impl/brcm_smi_utils.h"

namespace brcm {
namespace smi {

// BRCM device discovery paths and prefixes
static const char* kPathNICRoot = "/sys/class/hwmon";
static const char* kPathSwitchRoot = "/sys/bus/pci/devices";
static const char* kNICPrefix = "hwmon";
static const char* kSwitchPrefix = "0000:";

// BRCM device identification constants
static const uint32_t kBRCMnicId = 0x14e4;
static const uint32_t kBRCMswitchId = 0x1000;
static const uint32_t kBRCMswitchDId = 0x00b2;

// BRCM device info structure for compatibility
struct BRCMDeviceInfo {
    std::string device_name;
    std::string path;
    uint64_t bdfid;
    uint32_t card_index;
    bool is_nic;
};

// Global device lists for compatibility
static std::vector<void*> g_nic_devices;
static std::vector<void*> g_switch_devices;

// Global device lists for processed Device objects
static std::vector<std::shared_ptr<brcm::smi::Device>> g_nic_device_objects;
static std::vector<std::shared_ptr<brcm::smi::Device>> g_switch_device_objects;

bool FileExists(const char* filename) {
    struct stat buffer;
    return (stat(filename, &buffer) == 0);
}

// Helper function to check if a device is a BRCM NIC
static bool isBRCMnic(const std::string& dev_path) {
    bool isBRCMnic = false;
    std::string vend_path = dev_path + "/device/vendor";
    if (!FileExists(vend_path.c_str())) {
        return isBRCMnic;
    }

    std::ifstream fs;
    fs.open(vend_path);

    if (!fs.is_open()) {
        return isBRCMnic;
    }

    uint32_t vendor_id;
    fs >> std::hex >> vendor_id;
    fs.close();

    if (vendor_id == kBRCMnicId) {
        isBRCMnic = true;
    }
    return isBRCMnic;
}

// Helper function to check if a device is a BRCM Switch
static bool isBRCMswitch(const std::string& dev_path) {
    bool isBRCMswitch = false;
    std::string vend_path = dev_path + "/vendor";
    std::string ldev_path = dev_path + "/device";

    if (!FileExists(vend_path.c_str()) || !FileExists(ldev_path.c_str())) {
        return isBRCMswitch;
    }

    std::ifstream vfs, dfs;
    vfs.open(vend_path);
    dfs.open(ldev_path);

    if (!vfs.is_open() || !dfs.is_open()) {
        return isBRCMswitch;
    }

    uint32_t vendor_id;
    uint32_t dev_id;

    vfs >> std::hex >> vendor_id;
    dfs >> std::hex >> dev_id;

    vfs.close();
    dfs.close();

    if (vendor_id == kBRCMswitchId && dev_id == kBRCMswitchDId) {
        isBRCMswitch = true;
    }
    return isBRCMswitch;
}

// Helper function to create ROCm SMI compatible device object
static void* CreateBRCMDevice(const std::string& device_name, const std::string& root_path, 
                             uint64_t bdf_id, uint32_t card_index, bool is_nic) {
    // Create a placeholder device object compatible with ROCm SMI Device structure
    // In real implementation, this would create proper BRCM device objects
    // that match the ROCm SMI Device interface
    
    std::string dev_path = root_path + "/" + device_name;
    
    // For now, return a simple pointer that can be cast back to device info
    // In real implementation, this would be a proper Device object
    auto* device_info = new BRCMDeviceInfo{device_name, dev_path, bdf_id, card_index, is_nic};
    return static_cast<void*>(device_info);
}

// Helper function to add NIC device to list
static void AddToNICDeviceList(const std::string& device_name, uint64_t bdf_id, uint32_t index) {
    void* device = CreateBRCMDevice(device_name, kPathNICRoot, bdf_id, index, true);
    g_nic_devices.push_back(device);
}

// Helper function to add Switch device to list  
static void AddToSwitchDeviceList(const std::string& device_name, uint64_t bdf_id, uint32_t index) {
    void* device = CreateBRCMDevice(device_name, kPathSwitchRoot, bdf_id, index, false);
    g_switch_devices.push_back(device);
}

brcmsmi_status_t DiscoverBRCMDevices(brcmsmi_discovery_result_t* result) {
    if (result == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    std::string err_msg;
    uint32_t nic_count = 0;
    uint32_t switch_count = 0;

    // Clear previous findings
    g_nic_devices.clear();
    g_switch_devices.clear();

    // Discover NIC devices
    auto nic_dir = opendir(kPathNICRoot);
    if (nic_dir == nullptr) {
        err_msg = "Failed to open hwmon root directory for NIC discovery: ";
        err_msg += kPathNICRoot;
        err_msg += ". Continuing with switch discovery.";
        perror(err_msg.c_str());
    } else {
        auto dentry = readdir(nic_dir);

        while (dentry != nullptr) {
            if (memcmp(dentry->d_name, kNICPrefix, strlen(kNICPrefix)) == 0) {
                if ((strcmp(dentry->d_name, ".") == 0) || (strcmp(dentry->d_name, "..") == 0)) {
                    dentry = readdir(nic_dir);
                    continue;
                }
                std::string path = kPathNICRoot;
                path += "/" + std::string(dentry->d_name);
                if (isBRCMnic(path)) {
                    AddToNICDeviceList(dentry->d_name, UINT64_MAX, nic_count);
                    nic_count++;
                }
            }
            dentry = readdir(nic_dir);
        }

        if (closedir(nic_dir)) {
            err_msg = "Failed to close hw_mon root directory after NIC discovery: ";
            err_msg += kPathNICRoot;
            perror(err_msg.c_str());
        }
    }

    // Discover Switch devices
    auto pci_devices_dir = opendir(kPathSwitchRoot);
    if (pci_devices_dir == nullptr) {
        err_msg = "Failed to open PCI devices root directory for switch discovery: ";
        err_msg += kPathSwitchRoot;
        perror(err_msg.c_str());
    } else {
        auto dentry = readdir(pci_devices_dir);

        while (dentry != nullptr) {
            if (memcmp(dentry->d_name, kSwitchPrefix, strlen(kSwitchPrefix)) == 0) {
                if ((strcmp(dentry->d_name, ".") == 0) || (strcmp(dentry->d_name, "..") == 0)) {
                    dentry = readdir(pci_devices_dir);
                    continue;
                }
                std::string path = kPathSwitchRoot;
                path += "/" + std::string(dentry->d_name);
                if (isBRCMswitch(path)) {
                    AddToSwitchDeviceList(dentry->d_name, UINT64_MAX, switch_count);
                    switch_count++;
                }
            }
            dentry = readdir(pci_devices_dir);
        }

        if (closedir(pci_devices_dir)) {
            err_msg = "Failed to close PCI devices root directory after switch discovery: ";
            err_msg += kPathSwitchRoot;
            perror(err_msg.c_str());
        }
    }

    // Fill result structure
    result->nic_count = nic_count;
    result->switch_count = switch_count;
    result->total_count = nic_count + switch_count;

    return BRCMSMI_STATUS_SUCCESS;
}

// Complete BRCM device discovery and processing for ROCm SMI integration
brcmsmi_status_t GetBRCMDeviceVectors(brcmsmi_device_vectors_t* device_vectors) {
    if (device_vectors == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    // Clear previous findings
    for (auto* device : g_nic_devices) {
        delete static_cast<struct BRCMDeviceInfo*>(device);
    }
    for (auto* device : g_switch_devices) {
        delete static_cast<struct BRCMDeviceInfo*>(device);
    }
    g_nic_devices.clear();
    g_switch_devices.clear();

    std::string err_msg;
    uint32_t nic_count = 0;
    uint32_t switch_count = 0;

    // Discover NIC devices
    auto nic_dir = opendir(kPathNICRoot);
    if (nic_dir == nullptr) {
        err_msg = "Failed to open hwmon root directory for NIC discovery: ";
        err_msg += kPathNICRoot;
        err_msg += ". Continuing with switch discovery.";
        perror(err_msg.c_str());
    } else {
        auto dentry = readdir(nic_dir);

        while (dentry != nullptr) {
            if (memcmp(dentry->d_name, kNICPrefix, strlen(kNICPrefix)) == 0) {
                if ((strcmp(dentry->d_name, ".") == 0) || (strcmp(dentry->d_name, "..") == 0)) {
                    dentry = readdir(nic_dir);
                    continue;
                }
                std::string path = kPathNICRoot;
                path += "/" + std::string(dentry->d_name);
                if (isBRCMnic(path)) {
                    AddToNICDeviceList(dentry->d_name, UINT64_MAX, nic_count);
                    nic_count++;
                }
            }
            dentry = readdir(nic_dir);
        }

        if (closedir(nic_dir)) {
            err_msg = "Failed to close hw_mon root directory after NIC discovery: ";
            err_msg += kPathNICRoot;
            perror(err_msg.c_str());
        }
    }

    // Discover Switch devices
    auto pci_devices_dir2 = opendir(kPathSwitchRoot);
    if (pci_devices_dir2 == nullptr) {
        err_msg = "Failed to open PCI devices root directory for switch discovery: ";
        err_msg += kPathSwitchRoot;
        perror(err_msg.c_str());
    } else {
        auto dentry = readdir(pci_devices_dir2);

        while (dentry != nullptr) {
            if (memcmp(dentry->d_name, kSwitchPrefix, strlen(kSwitchPrefix)) == 0) {
                if ((strcmp(dentry->d_name, ".") == 0) || (strcmp(dentry->d_name, "..") == 0)) {
                    dentry = readdir(pci_devices_dir2);
                    continue;
                }
                std::string path = kPathSwitchRoot;
                path += "/" + std::string(dentry->d_name);
                if (isBRCMswitch(path)) {
                    AddToSwitchDeviceList(dentry->d_name, UINT64_MAX, switch_count);
                    switch_count++;
                }
            }
            dentry = readdir(pci_devices_dir2);
        }

        if (closedir(pci_devices_dir2)) {
            err_msg = "Failed to close PCI devices root directory after switch discovery: ";
            err_msg += kPathSwitchRoot;
            perror(err_msg.c_str());
        }
    }

    // Process NIC devices - construct BDFIDs and sort by BDF
    for (auto* device_ptr : g_nic_devices) {
        auto* device_info = static_cast<struct BRCMDeviceInfo*>(device_ptr);
        uint64_t bdfid;
        if (ConstructBDFID(device_info->path, &bdfid) == 0) {
            if (device_info->bdfid != UINT64_MAX && device_info->bdfid != bdfid) {
                // handles secondary partitions - keep existing bdfid
                // device_info->bdfid already set
            } else {
                // legacy & pcie card updates
                device_info->bdfid = bdfid;
            }
        }
    }

    // Sort NIC devices by BDF
    std::sort(g_nic_devices.begin(), g_nic_devices.end(), 
        [](const void* a, const void* b) {
            auto* device_a = static_cast<const struct BRCMDeviceInfo*>(a);
            auto* device_b = static_cast<const struct BRCMDeviceInfo*>(b);
            return device_a->bdfid < device_b->bdfid;
        });

    // Process Switch devices - construct BDFIDs and sort by BDF
    for (auto* device_ptr : g_switch_devices) {
        auto* device_info = static_cast<struct BRCMDeviceInfo*>(device_ptr);
        uint64_t bdfid;
        if (ConstructBDFID(device_info->path, &bdfid) == 0) {
            if (device_info->bdfid != UINT64_MAX && device_info->bdfid != bdfid) {
                // handles secondary partitions - keep existing bdfid
                // device_info->bdfid already set
            } else {
                // legacy & pcie card updates
                device_info->bdfid = bdfid;
            }
        }
    }

    // Sort Switch devices by BDF
    std::sort(g_switch_devices.begin(), g_switch_devices.end(),
        [](const void* a, const void* b) {
            auto* device_a = static_cast<const struct BRCMDeviceInfo*>(a);
            auto* device_b = static_cast<const struct BRCMDeviceInfo*>(b);
            return device_a->bdfid < device_b->bdfid;
        });

    // Fill device vectors structure
    device_vectors->nic_devices = g_nic_devices.empty() ? nullptr : g_nic_devices.data();
    device_vectors->switch_devices = g_switch_devices.empty() ? nullptr : g_switch_devices.data();
    device_vectors->nic_count = nic_count;
    device_vectors->switch_count = switch_count;

    return BRCMSMI_STATUS_SUCCESS;
}

// Enhanced device processing with actual Device objects and BDF processing
brcmsmi_status_t GetProcessedBRCMDevices(brcmsmi_device_vectors_t* device_vectors) {
    if (device_vectors == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    // Clear previous Device objects
    g_nic_device_objects.clear();
    g_switch_device_objects.clear();

    // First get the basic device discovery
    brcmsmi_status_t status = GetBRCMDeviceVectors(device_vectors);
    if (status != BRCMSMI_STATUS_SUCCESS) {
        return status;
    }

    // Process NIC devices - create Device objects and process BDFs
    for (uint32_t i = 0; i < device_vectors->nic_count; i++) {
        auto* device_info = static_cast<struct BRCMDeviceInfo*>(device_vectors->nic_devices[i]);
        
        // Create Device object
        std::string dev_path = std::string(kPathNICRoot) + "/" + device_info->device_name;
        auto device = std::make_shared<brcm::smi::Device>(dev_path);
        device->set_card_index(device_info->card_index);
        
        // Process BDF ID
        uint64_t bdfid;
        if (ConstructBDFID(device->path(), &bdfid) != 0) {
            std::cerr << "Failed to construct BDFID for NIC device." << std::endl;
        } else if (device->bdfid() != UINT64_MAX && device->bdfid() != bdfid) {
            // handles secondary partitions - compute partition feature nodes
            std::cout << "NIC device [before] path = " << device->path()
                      << " | bdfid = " << bdfid << " | device->bdfid() = " << device->bdfid()
                      << " | (xgmi node) setting to setting device->set_bdfid(device->bdfid())" << std::endl;
            device->set_bdfid(device->bdfid());
        } else {
            // legacy & pcie card updates
            std::cout << "NIC device [before] path = " << device->path()
                      << " | bdfid = " << bdfid << " | device->bdfid() = " << device->bdfid()
                      << " | (legacy/pcie card) setting device->set_bdfid(bdfid)" << std::endl;
            device->set_bdfid(bdfid);
        }
        std::cout << "NIC device [after] path = " << device->path()
                  << " | bdfid = " << bdfid << " | device->bdfid() = " << device->bdfid()
                  << " | final update: device->bdfid() holds correct device bdf" << std::endl;

        g_nic_device_objects.push_back(device);
    }

    // Sort NIC devices by BDF
    std::vector<std::pair<uint64_t, std::shared_ptr<brcm::smi::Device>>> nic_dv_to_id;
    nic_dv_to_id.reserve(g_nic_device_objects.size());
    for (uint32_t dv_ind = 0; dv_ind < g_nic_device_objects.size(); ++dv_ind) {
        auto dev = g_nic_device_objects[dv_ind];
        uint64_t bdfid = dev->bdfid();
        bdfid = bdfid & 0xFFFFFFFF0FFFFFFF;  // clear out partition id in bdf
        nic_dv_to_id.push_back({bdfid, dev});
    }

    // Stable sort to keep the order if bdf is equal.
    std::stable_sort(nic_dv_to_id.begin(), nic_dv_to_id.end(),
                     [](const std::pair<uint64_t, std::shared_ptr<brcm::smi::Device>>& p1,
                        const std::pair<uint64_t, std::shared_ptr<brcm::smi::Device>>& p2) {
                       return p1.first < p2.first;
                     });
    g_nic_device_objects.clear();
    for (uint32_t dv_ind = 0; dv_ind < nic_dv_to_id.size(); ++dv_ind) {
        g_nic_device_objects.push_back(nic_dv_to_id[dv_ind].second);
    }

    // Process Switch devices - create Device objects and process BDFs
    for (uint32_t i = 0; i < device_vectors->switch_count; i++) {
        auto* device_info = static_cast<struct BRCMDeviceInfo*>(device_vectors->switch_devices[i]);
        
        // Create Device object
        std::string dev_path = std::string(kPathSwitchRoot) + "/" + device_info->device_name;
        auto device = std::make_shared<brcm::smi::Device>(dev_path);
        device->set_card_index(device_info->card_index);
        
        // Process BDF ID
        uint64_t bdfid;
        if (ConstructBDFID(device->path(), &bdfid) != 0) {
            std::cerr << "Failed to construct BDFID for Switch device." << std::endl;
        } else if (device->bdfid() != UINT64_MAX && device->bdfid() != bdfid) {
            // handles secondary partitions - compute partition feature nodes
            std::cout << "Switch device [before] path = " << device->path()
                      << " | bdfid = " << bdfid << " | device->bdfid() = " << device->bdfid()
                      << " | (xgmi node) setting to setting device->set_bdfid(device->bdfid())" << std::endl;
            device->set_bdfid(device->bdfid());
        } else {
            // legacy & pcie card updates
            std::cout << "Switch device [before] path = " << device->path()
                      << " | bdfid = " << bdfid << " | device->bdfid() = " << device->bdfid()
                      << " | (legacy/pcie card) setting device->set_bdfid(bdfid)" << std::endl;
            device->set_bdfid(bdfid);
        }
        std::cout << "Switch device [after] path = " << device->path()
                  << " | bdfid = " << bdfid << " | device->bdfid() = " << device->bdfid()
                  << " | final update: device->bdfid() holds correct device bdf" << std::endl;

        g_switch_device_objects.push_back(device);
    }

    // Sort Switch devices by BDF
    std::vector<std::pair<uint64_t, std::shared_ptr<brcm::smi::Device>>> switch_dv_to_id;
    switch_dv_to_id.reserve(g_switch_device_objects.size());
    for (uint32_t dv_ind = 0; dv_ind < g_switch_device_objects.size(); ++dv_ind) {
        auto dev = g_switch_device_objects[dv_ind];
        uint64_t bdfid = dev->bdfid();
        switch_dv_to_id.push_back({bdfid, dev});
    }

    // Stable sort to keep the order if bdf is equal.
    std::stable_sort(switch_dv_to_id.begin(), switch_dv_to_id.end(),
                      [](const std::pair<uint64_t, std::shared_ptr<brcm::smi::Device>>& p1,
                        const std::pair<uint64_t, std::shared_ptr<brcm::smi::Device>>& p2) {
                        return p1.first < p2.first;
                      });
    g_switch_device_objects.clear();
    for (uint32_t dv_ind = 0; dv_ind < switch_dv_to_id.size(); ++dv_ind) {
        g_switch_device_objects.push_back(switch_dv_to_id[dv_ind].second);
    }

    // Update device vectors to point to Device objects
    device_vectors->nic_devices = g_nic_device_objects.empty() ? nullptr : 
                                  reinterpret_cast<void**>(g_nic_device_objects.data());
    device_vectors->switch_devices = g_switch_device_objects.empty() ? nullptr : 
                                     reinterpret_cast<void**>(g_switch_device_objects.data());

    return BRCMSMI_STATUS_SUCCESS;
}

// New vector management using DeviceManager
brcmsmi_status_t GetManagedDeviceVectors(brcmsmi_device_vectors_t* device_vectors) {
    if (device_vectors == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    // Use DeviceManager to get processed devices
    DeviceManager& manager = DeviceManager::getInstance();
    brcmsmi_status_t status = manager.discover_and_process_devices();
    
    if (status != BRCMSMI_STATUS_SUCCESS) {
        return status;
    }

    // Get device vectors from DeviceManager
    auto& nic_devices = manager.get_nic_devices();
    auto& switch_devices = manager.get_switch_devices();

    // Convert to the expected format
    device_vectors->nic_count = manager.get_nic_device_count();
    device_vectors->switch_count = manager.get_switch_device_count();

    // Allocate and populate device arrays
    if (device_vectors->nic_count > 0) {
        device_vectors->nic_devices = new void*[device_vectors->nic_count];
        for (uint32_t i = 0; i < device_vectors->nic_count; i++) {
            device_vectors->nic_devices[i] = new std::shared_ptr<Device>(nic_devices[i]);
        }
    } else {
        device_vectors->nic_devices = nullptr;
    }

    if (device_vectors->switch_count > 0) {
        device_vectors->switch_devices = new void*[device_vectors->switch_count];
        for (uint32_t i = 0; i < device_vectors->switch_count; i++) {
            device_vectors->switch_devices[i] = new std::shared_ptr<Device>(switch_devices[i]);
        }
    } else {
        device_vectors->switch_devices = nullptr;
    }

    return BRCMSMI_STATUS_SUCCESS;
}

}  // namespace smi
}  // namespace brcm

extern "C" {

brcmsmi_status_t brcmsmi_discover_devices(brcmsmi_discovery_result_t* result) {
    return brcm::smi::DiscoverBRCMDevices(result);
}

brcmsmi_status_t brcmsmi_get_device_vectors(brcmsmi_device_vectors_t* device_vectors) {
    return brcm::smi::GetBRCMDeviceVectors(device_vectors);
}

brcmsmi_status_t brcmsmi_get_processed_device_vectors(brcmsmi_device_vectors_t* device_vectors) {
    return brcm::smi::GetProcessedBRCMDevices(device_vectors);
}

brcmsmi_status_t brcmsmi_get_managed_device_vectors(brcmsmi_device_vectors_t* device_vectors) {
    return brcm::smi::GetManagedDeviceVectors(device_vectors);
}

}  // extern "C"

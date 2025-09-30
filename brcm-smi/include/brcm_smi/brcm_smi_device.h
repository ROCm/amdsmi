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


#ifndef BRCM_SMI_INCLUDE_BRCM_SMI_DEVICE_H_
#define BRCM_SMI_INCLUDE_BRCM_SMI_DEVICE_H_

#include <string>
#include <memory>
#include <vector>
#include <cstdint>
#include "brcmsmi.h"

// Platform-specific threading includes
#ifdef _WIN32
    #include <windows.h>
    #include <mutex>
    #include <thread>
#else
    #include <pthread.h>
#endif

namespace brcm {
namespace smi {

/**
 * @brief BRCM Device class - comprehensive version mirroring amd::smi::Device for BRCM devices
 * 
 * This class represents a BRCM NIC or Switch device and provides comprehensive
 * functionality for device management within the BRCM SMI library. It mirrors
 * the essential functionality of amd::smi::Device while being specialized for
 * BRCM devices.
 */
class Device {
 public:
    /**
     * @brief Construct a new Device object
     * 
     * @param path Device path in sysfs
     * @param env Environment variables (can be nullptr for BRCM-specific usage)
     */
    explicit Device(const std::string& path, void* env = nullptr);
    
    /**
     * @brief Destroy the Device object
     */
    ~Device();

    // Core device information accessors - mirroring amd::smi::Device
    std::string path() const { return path_; }
    uint64_t bdfid() const { return bdfid_; }
    void set_bdfid(uint64_t val) { bdfid_ = val; }
    uint32_t index() const { return card_indx_; }
    void set_card_index(uint32_t index) { card_indx_ = index; }
    uint32_t drm_render_minor() const { return drm_render_minor_; }
    void set_drm_render_minor(uint32_t minor) { drm_render_minor_ = minor; }
    uint64_t kfd_gpu_id() const { return kfd_gpu_id_; }
    void set_kfd_gpu_id(uint64_t id) { kfd_gpu_id_ = id; }

    // Monitor support - mirroring amd::smi::Device
    void set_monitor(std::shared_ptr<void> m) { monitor_ = m; }
    std::shared_ptr<void> monitor() { return monitor_; }
    void set_power_monitor(std::shared_ptr<void> pm) { power_monitor_ = pm; }
    std::shared_ptr<void> power_monitor() { return power_monitor_; }

    // Thread safety - mirroring amd::smi::Device
#ifdef _WIN32
    std::mutex* mutex() { return &mutex_; }
#else
    pthread_mutex_t* mutex() { return &mutex_; }
#endif

    // Device type identification
    enum DeviceType {
        BRCM_NIC,
        BRCM_SWITCH,
        BRCM_UNKNOWN
    };
    
    DeviceType device_type() const { return device_type_; }
    void set_device_type(DeviceType type) { device_type_ = type; }

    // Device information methods - BRCM specific
    int readDevInfo(const std::string& info_type, uint64_t* val);
    int readDevInfo(const std::string& info_type, std::string* val);
    int writeDevInfo(const std::string& info_type, uint64_t val);
    int writeDevInfo(const std::string& info_type, const std::string& val);

    // File path utilities
    std::string get_sys_file_path(const std::string& file_name) const;
    bool file_exists(const std::string& file_path) const;

    // BDF utilities
    std::string bdf_to_string() const;
    static uint64_t bdf_string_to_id(const std::string& bdf_str);

    // Device identification
    bool is_brcm_nic() const { return device_type_ == BRCM_NIC; }
    bool is_brcm_switch() const { return device_type_ == BRCM_SWITCH; }

    // Comparison operators for sorting
    bool operator<(const Device& other) const {
        return bdfid_ < other.bdfid_;
    }
    
    bool operator==(const Device& other) const {
        return path_ == other.path_ && bdfid_ == other.bdfid_;
    }

 private:
    // Core device properties - mirroring amd::smi::Device
    std::string path_;                      // Device path in sysfs
    uint64_t bdfid_;                       // Bus:Device:Function ID
    uint32_t card_indx_;                   // Card index (corresponds to drm index)
    uint32_t drm_render_minor_;            // DRM render minor number
    uint64_t kfd_gpu_id_;                  // KFD GPU ID
    DeviceType device_type_;               // BRCM device type
    
    // Monitor support - mirroring amd::smi::Device
    std::shared_ptr<void> monitor_;        // Monitor pointer (generic)
    std::shared_ptr<void> power_monitor_;  // Power monitor pointer (generic)
    
    // Thread safety
#ifdef _WIN32
    std::mutex mutex_;                     // Device mutex (Windows)
#else
    pthread_mutex_t mutex_;                // Device mutex (Unix/Linux)
#endif
    
    // Environment (can be null for BRCM-specific usage)
    void* env_;                            // Environment variables pointer
    
    // Helper methods
    void initialize_mutex();
    void cleanup_mutex();
    std::string construct_sys_path(const std::string& file_name) const;
};

/**
 * @brief Device vector management class for BRCM SMI
 * 
 * This class manages vectors of BRCM devices and provides functionality
 * similar to what was previously handled in ROCm SMI.
 */
class DeviceManager {
 public:
    static DeviceManager& getInstance();
    
    // Vector management
    std::vector<std::shared_ptr<Device>>& get_nic_devices() { return nic_devices_; }
    std::vector<std::shared_ptr<Device>>& get_switch_devices() { return switch_devices_; }
    
    // Device discovery and processing
    brcmsmi_status_t discover_and_process_devices();
    brcmsmi_status_t add_device(std::shared_ptr<Device> device);
    brcmsmi_status_t clear_devices();
    
    // Device sorting and BDF processing
    brcmsmi_status_t sort_devices_by_bdf();
    brcmsmi_status_t process_device_bdfs();
    
    // Device access
    uint32_t get_nic_device_count() const { return static_cast<uint32_t>(nic_devices_.size()); }
    uint32_t get_switch_device_count() const { return static_cast<uint32_t>(switch_devices_.size()); }
    
    std::shared_ptr<Device> get_nic_device(uint32_t index);
    std::shared_ptr<Device> get_switch_device(uint32_t index);
    
 private:
    DeviceManager() = default;
    ~DeviceManager() = default;
    DeviceManager(const DeviceManager&) = delete;
    DeviceManager& operator=(const DeviceManager&) = delete;
    
    // Device vectors - now managed within BRCM SMI
    std::vector<std::shared_ptr<Device>> nic_devices_;
    std::vector<std::shared_ptr<Device>> switch_devices_;
    
    // Thread safety
#ifdef _WIN32
    std::mutex devices_mutex_;             // Device manager mutex (Windows)
    bool mutex_initialized_ = false;
#else
    pthread_mutex_t devices_mutex_;        // Device manager mutex (Unix/Linux)
    bool mutex_initialized_ = false;
#endif
    
    void initialize_mutex();
    void cleanup_mutex();
};

}  // namespace smi
}  // namespace brcm

#endif  // BRCM_SMI_INCLUDE_BRCM_SMI_DEVICE_H_

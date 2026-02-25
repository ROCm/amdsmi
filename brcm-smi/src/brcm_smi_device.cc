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


#include "brcm_smi/brcm_smi_device.h"
#include "brcm_smi/brcmsmi.h"
#include "brcm_smi/brcm_smi_discovery.h"
#include "brcm_smi/brcm_smi_utils.h"
#include <limits>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <cerrno>
#include <cstring>
#include <iomanip>

// Platform-specific includes
#ifdef _WIN32
    #include <io.h>
    #include <sys/stat.h>
    #include <windows.h>
#else
    #include <sys/stat.h>
    #include <unistd.h>
#endif

namespace brcm {
namespace smi {

// Device class implementation
Device::Device(const std::string& path, void* env) 
    : path_(path), 
      bdfid_(UINT64_MAX), 
      card_indx_(std::numeric_limits<uint32_t>::max()),
      drm_render_minor_(std::numeric_limits<uint32_t>::max()),
      kfd_gpu_id_(0),
      device_type_(BRCM_UNKNOWN),
      monitor_(nullptr),
      power_monitor_(nullptr),
      env_(env) {
    initialize_mutex();
}

Device::~Device() {
    cleanup_mutex();
}

void Device::initialize_mutex() {
#ifdef _WIN32
    // std::mutex is automatically initialized, no explicit setup needed
#else
    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_RECURSIVE);
    pthread_mutex_init(&mutex_, &attr);
    pthread_mutexattr_destroy(&attr);
#endif
}

void Device::cleanup_mutex() {
#ifdef _WIN32
    // std::mutex is automatically destroyed, no explicit cleanup needed
#else
    pthread_mutex_destroy(&mutex_);
#endif
}

std::string Device::construct_sys_path(const std::string& file_name) const {
    if (path_.empty()) {
        return "";
    }
    
    // Handle different path constructions based on device type
    std::string sys_path = path_;
    if (sys_path.back() != '/') {
        sys_path += "/";
    }
    sys_path += file_name;
    
    return sys_path;
}

std::string Device::get_sys_file_path(const std::string& file_name) const {
    return construct_sys_path(file_name);
}

bool Device::file_exists(const std::string& file_path) const {
    struct stat buffer;
    return (stat(file_path.c_str(), &buffer) == 0);
}

int Device::readDevInfo(const std::string& info_type, uint64_t* val) {
    if (val == nullptr) {
        return -1;
    }
    
    std::string file_path = get_sys_file_path(info_type);
    if (!file_exists(file_path)) {
        return -1;
    }
    
    std::ifstream fs(file_path);
    if (!fs.is_open()) {
        return -1;
    }
    
    fs >> *val;
    if (fs.fail()) {
        fs.close();
        return -1;
    }
    
    fs.close();
    return 0;
}

int Device::readDevInfo(const std::string& info_type, std::string* val) {
    if (val == nullptr) {
        return -1;
    }
    
    std::string file_path = get_sys_file_path(info_type);
    if (!file_exists(file_path)) {
        return -1;
    }
    
    std::ifstream fs(file_path);
    if (!fs.is_open()) {
        return -1;
    }
    
    std::getline(fs, *val);
    if (fs.fail()) {
        fs.close();
        return -1;
    }
    
    fs.close();
    return 0;
}

int Device::writeDevInfo(const std::string& info_type, uint64_t val) {
    std::string file_path = get_sys_file_path(info_type);
    
    std::ofstream fs(file_path);
    if (!fs.is_open()) {
        return -1;
    }
    
    fs << val;
    if (fs.fail()) {
        fs.close();
        return -1;
    }
    
    fs.close();
    return 0;
}

int Device::writeDevInfo(const std::string& info_type, const std::string& val) {
    std::string file_path = get_sys_file_path(info_type);
    
    std::ofstream fs(file_path);
    if (!fs.is_open()) {
        return -1;
    }
    
    fs << val;
    if (fs.fail()) {
        fs.close();
        return -1;
    }
    
    fs.close();
    return 0;
}

std::string Device::bdf_to_string() const {
    if (bdfid_ == UINT64_MAX) {
        return "Unknown";
    }
    
    // Extract BDF components from bdfid_
    uint16_t domain = static_cast<uint16_t>((bdfid_ >> 32) & 0xFFFF);
    uint8_t bus = static_cast<uint8_t>((bdfid_ >> 8) & 0xFF);
    uint8_t device = static_cast<uint8_t>((bdfid_ >> 3) & 0x1F);
    uint8_t function = static_cast<uint8_t>(bdfid_ & 0x7);
    
    std::stringstream ss;
    ss << std::hex << std::setw(4) << std::setfill('0') << domain << ":"
       << std::setw(2) << std::setfill('0') << static_cast<uint32_t>(bus) << ":"
       << std::setw(2) << std::setfill('0') << static_cast<uint32_t>(device) << "."
       << static_cast<uint32_t>(function);
    
    return ss.str();
}

uint64_t Device::bdf_string_to_id(const std::string& bdf_str) {
    // Use the utility function from brcm_smi_utils
    uint64_t bdfid;
    if (bdfid_from_path(bdf_str, &bdfid)) {
        return bdfid;
    }
    return UINT64_MAX;
}

// DeviceManager class implementation
DeviceManager& DeviceManager::getInstance() {
    static DeviceManager instance;
    return instance;
}

void DeviceManager::initialize_mutex() {
    if (!mutex_initialized_) {
#ifdef _WIN32
        // std::mutex is automatically initialized, no explicit setup needed
#else
        pthread_mutexattr_t attr;
        pthread_mutexattr_init(&attr);
        pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_RECURSIVE);
        pthread_mutex_init(&devices_mutex_, &attr);
        pthread_mutexattr_destroy(&attr);
#endif
        mutex_initialized_ = true;
    }
}

void DeviceManager::cleanup_mutex() {
    if (mutex_initialized_) {
#ifdef _WIN32
        // std::mutex is automatically destroyed, no explicit cleanup needed
#else
        pthread_mutex_destroy(&devices_mutex_);
#endif
        mutex_initialized_ = false;
    }
}

brcmsmi_status_t DeviceManager::discover_and_process_devices() {
    initialize_mutex();
#ifdef _WIN32
    devices_mutex_.lock();
#else
    pthread_mutex_lock(&devices_mutex_);
#endif
    
    // Clear existing devices
    nic_devices_.clear();
    switch_devices_.clear();
    
    // Use the existing discovery function from brcm_smi_discovery.cc
    brcmsmi_device_vectors_t device_vectors = {0};
    brcmsmi_status_t status = GetProcessedBRCMDevices(&device_vectors);
    
    if (status == BRCMSMI_STATUS_SUCCESS) {
        // Convert the discovered devices to our managed vectors
        for (uint32_t i = 0; i < device_vectors.nic_count; i++) {
            auto brcm_device_ptr = static_cast<std::shared_ptr<Device>*>(device_vectors.nic_devices[i]);
            nic_devices_.push_back(*brcm_device_ptr);
        }
        
        for (uint32_t i = 0; i < device_vectors.switch_count; i++) {
            auto brcm_device_ptr = static_cast<std::shared_ptr<Device>*>(device_vectors.switch_devices[i]);
            switch_devices_.push_back(*brcm_device_ptr);
        }
    }
    
#ifdef _WIN32
    devices_mutex_.unlock();
#else
    pthread_mutex_unlock(&devices_mutex_);
#endif
    return status;
}

brcmsmi_status_t DeviceManager::add_device(std::shared_ptr<Device> device) {
    if (!device) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    initialize_mutex();
#ifdef _WIN32
    devices_mutex_.lock();
#else
    pthread_mutex_lock(&devices_mutex_);
#endif
    
    if (device->is_brcm_nic()) {
        nic_devices_.push_back(device);
    } else if (device->is_brcm_switch()) {
        switch_devices_.push_back(device);
    } else {
    #ifdef _WIN32
    devices_mutex_.unlock();
#else
    pthread_mutex_unlock(&devices_mutex_);
#endif
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
#ifdef _WIN32
    devices_mutex_.unlock();
#else
    pthread_mutex_unlock(&devices_mutex_);
#endif
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t DeviceManager::clear_devices() {
    initialize_mutex();
#ifdef _WIN32
    devices_mutex_.lock();
#else
    pthread_mutex_lock(&devices_mutex_);
#endif
    
    nic_devices_.clear();
    switch_devices_.clear();
    
#ifdef _WIN32
    devices_mutex_.unlock();
#else
    pthread_mutex_unlock(&devices_mutex_);
#endif
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t DeviceManager::sort_devices_by_bdf() {
    initialize_mutex();
#ifdef _WIN32
    devices_mutex_.lock();
#else
    pthread_mutex_lock(&devices_mutex_);
#endif
    
    // Sort NIC devices by BDF
    std::sort(nic_devices_.begin(), nic_devices_.end(),
              [](const std::shared_ptr<Device>& a, const std::shared_ptr<Device>& b) {
                  return a->bdfid() < b->bdfid();
              });
    
    // Sort Switch devices by BDF
    std::sort(switch_devices_.begin(), switch_devices_.end(),
              [](const std::shared_ptr<Device>& a, const std::shared_ptr<Device>& b) {
                  return a->bdfid() < b->bdfid();
              });
    
#ifdef _WIN32
    devices_mutex_.unlock();
#else
    pthread_mutex_unlock(&devices_mutex_);
#endif
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t DeviceManager::process_device_bdfs() {
    initialize_mutex();
#ifdef _WIN32
    devices_mutex_.lock();
#else
    pthread_mutex_lock(&devices_mutex_);
#endif
    
    // Process BDFs for NIC devices
    for (auto& device : nic_devices_) {
        if (device->bdfid() == UINT64_MAX) {
            uint64_t bdfid;
            if (ConstructBDFID(device->path(), &bdfid) == 0) {
                device->set_bdfid(bdfid);
            }
        }
    }
    
    // Process BDFs for Switch devices
    for (auto& device : switch_devices_) {
        if (device->bdfid() == UINT64_MAX) {
            uint64_t bdfid;
            if (ConstructBDFID(device->path(), &bdfid) == 0) {
                device->set_bdfid(bdfid);
            }
        }
    }
    
#ifdef _WIN32
    devices_mutex_.unlock();
#else
    pthread_mutex_unlock(&devices_mutex_);
#endif
    return BRCMSMI_STATUS_SUCCESS;
}

std::shared_ptr<Device> DeviceManager::get_nic_device(uint32_t index) {
    initialize_mutex();
#ifdef _WIN32
    devices_mutex_.lock();
#else
    pthread_mutex_lock(&devices_mutex_);
#endif
    
    if (index >= nic_devices_.size()) {
    #ifdef _WIN32
    devices_mutex_.unlock();
#else
    pthread_mutex_unlock(&devices_mutex_);
#endif
        return nullptr;
    }
    
    auto device = nic_devices_[index];
#ifdef _WIN32
    devices_mutex_.unlock();
#else
    pthread_mutex_unlock(&devices_mutex_);
#endif
    return device;
}

std::shared_ptr<Device> DeviceManager::get_switch_device(uint32_t index) {
    initialize_mutex();
#ifdef _WIN32
    devices_mutex_.lock();
#else
    pthread_mutex_lock(&devices_mutex_);
#endif
    
    if (index >= switch_devices_.size()) {
    #ifdef _WIN32
    devices_mutex_.unlock();
#else
    pthread_mutex_unlock(&devices_mutex_);
#endif
        return nullptr;
    }
    
    auto device = switch_devices_[index];
#ifdef _WIN32
    devices_mutex_.unlock();
#else
    pthread_mutex_unlock(&devices_mutex_);
#endif
    return device;
}

}  // namespace smi
}  // namespace brcm

/*
 * =============================================================================
 * The University of Illinois/NCSA
 * Open Source License (NCSA)
 *
 * Copyright (c) 2022, Advanced Micro Devices, Inc.
 * All rights reserved.
 *
 * Developed by:
 *
 *                 AMD Research and AMD ROC Software Development
 *
 *                 Advanced Micro Devices, Inc.
 *
 *                 www.amd.com
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal with the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 *  - Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimers.
 *  - Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimers in
 *    the documentation and/or other materials provided with the distribution.
 *  - Neither the names of <Name of Development Group, Name of Institution>,
 *    nor the names of its contributors may be used to endorse or promote
 *    products derived from this Software without specific prior written
 *    permission.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
 * OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 * ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS WITH THE SOFTWARE.
 *
 */
#include <sys/types.h>
#include <dirent.h>
#include <fcntl.h>
#include <unistd.h>
#include <xf86drm.h>
#include <string.h>
#include <memory>
#include "amd_smi/impl/amd_smi_drm.h"
#include "amd_smi/impl/amdgpu_drm.h"

namespace amd {
namespace smi {

amdsmi_status_t AMDSmiDrm::init() {
    // A few RAII handler

    using dir_ptr = std::unique_ptr<DIR, decltype(&closedir)>;
    using drm_version_ptr = std::unique_ptr<drmVersion,
            decltype(&drmFreeVersion)>;
    // using drm_device_ptr = std::unique_ptr(drmDevicePtr,
    //         decltype(&drmFreeDevice));

    struct dirent *dir = nullptr;
    int fd = -1;


    amdsmi_status_t status = lib_loader_.load("libdrm.so");
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }

    // load symbol from libdrm
    drm_cmd_write_ = nullptr;
    status = lib_loader_.load_symbol(&drm_cmd_write_, "drmCommandWrite");
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }

    using drmGetVersionType = drmVersionPtr (*)(int);    // drmGetVersion
    using drmFreeVersionType = void (*)(drmVersionPtr);  // drmFreeVersion
    using drmGetDeviceType = int(*)(int, drmDevicePtr*);   // drmGetDevice
    using drmFreeDeviceType = void(*)(drmDevicePtr*);     // drmFreeDevice

    drmGetVersionType drm_get_version = nullptr;
    drmFreeVersionType drm_free_version = nullptr;

    drmGetDeviceType drm_get_device = nullptr;
    drmFreeDeviceType drm_free_device = nullptr;

    status = lib_loader_.load_symbol(&drm_get_version, "drmGetVersion");
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }
    status = lib_loader_.load_symbol(&drm_free_version, "drmFreeVersion");
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }

    status = lib_loader_.load_symbol(&drm_get_device, "drmGetDevice");
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }
    status = lib_loader_.load_symbol(&drm_free_device, "drmFreeDevice");
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }

    auto d = dir_ptr(opendir("/dev/dri/"), &closedir);
    if (d == nullptr) return AMDSMI_STATUS_NOT_INIT;

    drmDevicePtr device;

    while ((dir = readdir(d.get())) != NULL) {
        char* name_cstr = new char[sizeof(dir->d_name) + 10];
        auto name = std::unique_ptr<char[]>(name_cstr);

        snprintf(name.get(), sizeof(dir->d_name) + 10,
                        "/dev/dri/%s", dir->d_name);
        fd = open(name.get(), O_RDWR | O_CLOEXEC);
        if (fd < 0) continue;

        auto version = drm_version_ptr(drm_get_version(fd), drm_free_version);
        if (strcmp("amdgpu", version->name) ||
            strstr(name.get(), "render") == nullptr) {
                close(fd);
                continue;
        }

        if (drm_get_device(fd, &device) != 0) {
            drm_free_device(&device);
            return AMDSMI_STATUS_DRM_ERROR;
        }

        drm_fds_.push_back(fd);
        drm_paths_.push_back(dir->d_name);

        amdsmi_bdf_t bdf;
        bdf.function_number = device->businfo.pci->func;
        bdf.device_number = device->businfo.pci->dev;
        bdf.bus_number = device->businfo.pci->bus;
        bdf.domain_number = device->businfo.pci->domain;

        drm_bdfs_.push_back(bdf);
        drm_free_device(&device);
    }

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t AMDSmiDrm::cleanup() {
    for (unsigned int i=0; i < drm_fds_.size(); i++) {
        close(drm_fds_[i]);
    }

    drm_fds_.clear();
    drm_paths_.clear();
    drm_bdfs_.clear();
    lib_loader_.unload();
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t AMDSmiDrm::amdgpu_query_info(int fd, unsigned info_id,
            unsigned size, void *value) {
    if (drm_cmd_write_ == nullptr) return AMDSMI_STATUS_NOT_SUPPORTED;
    std::lock_guard<std::mutex> guard(drm_mutex_);

    struct drm_amdgpu_info request;
    memset(&request, 0, sizeof(request));
    request.return_pointer = (uintptr_t)value;
    request.return_size = size;
    request.query = info_id;
    int status = drm_cmd_write_(fd, DRM_AMDGPU_INFO,
            &request, sizeof(struct drm_amdgpu_info));
    if (status == 0) return AMDSMI_STATUS_SUCCESS;
    return AMDSMI_STATUS_DRM_ERROR;
}

amdsmi_status_t AMDSmiDrm::amdgpu_query_fw(int fd, unsigned info_id,
        unsigned fw_type, unsigned size, void *value) {
    if (drm_cmd_write_ == nullptr) return AMDSMI_STATUS_NOT_SUPPORTED;

    std::lock_guard<std::mutex> guard(drm_mutex_);

    struct drm_amdgpu_info request;
    memset(&request, 0, sizeof(request));
    request.return_pointer = (uintptr_t)value;
    request.return_size = size;
    request.query = info_id;
    request.query_fw.fw_type = fw_type;
    int status = drm_cmd_write_(fd, DRM_AMDGPU_INFO, &request,
                    sizeof(struct drm_amdgpu_info));
    if (status == 0) return AMDSMI_STATUS_SUCCESS;
    return AMDSMI_STATUS_DRM_ERROR;
}

amdsmi_status_t AMDSmiDrm::amdgpu_query_hw_ip(int fd, unsigned info_id,
        unsigned hw_ip_type, unsigned size, void *value) {
    if (drm_cmd_write_ == nullptr) return AMDSMI_STATUS_NOT_SUPPORTED;

    std::lock_guard<std::mutex> guard(drm_mutex_);

    struct drm_amdgpu_info request;
    memset(&request, 0, sizeof(request));
    request.return_pointer = (uintptr_t)value;
    request.return_size = size;
    request.query = info_id;
    request.query_hw_ip.type = hw_ip_type;
    int status = drm_cmd_write_(fd, DRM_AMDGPU_INFO, &request,
                sizeof(struct drm_amdgpu_info));
    if (status == 0) return AMDSMI_STATUS_SUCCESS;
    return AMDSMI_STATUS_DRM_ERROR;
}

amdsmi_status_t AMDSmiDrm::amdgpu_query_vbios(int fd, void *info) {
    if (drm_cmd_write_ == nullptr) return AMDSMI_STATUS_NOT_SUPPORTED;

    std::lock_guard<std::mutex> guard(drm_mutex_);

    struct drm_amdgpu_info request;
    memset(&request, 0, sizeof request);
    request.return_pointer = (uint64_t) info;
    request.return_size = sizeof(drm_amdgpu_info_vbios);
    request.query = AMDGPU_INFO_VBIOS;
    request.vbios_info.type = AMDGPU_INFO_VBIOS_INFO;
    int status = drm_cmd_write_(fd, DRM_AMDGPU_INFO, &request,
                    sizeof(struct drm_amdgpu_info));
    if (status == 0) return AMDSMI_STATUS_SUCCESS;
    return AMDSMI_STATUS_DRM_ERROR;
}


amdsmi_status_t AMDSmiDrm::get_drm_fd_by_index(uint32_t gpu_index, uint32_t *fd_info) const {
    if (gpu_index + 1 > drm_fds_.size()) return AMDSMI_STATUS_NOT_SUPPORTED;
    *fd_info = drm_fds_[gpu_index];
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t AMDSmiDrm::get_bdf_by_index(uint32_t gpu_index, amdsmi_bdf_t *bdf_info) const {
    if (gpu_index + 1 > drm_bdfs_.size()) return AMDSMI_STATUS_NOT_SUPPORTED;
    *bdf_info = drm_bdfs_[gpu_index];
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t AMDSmiDrm::get_drm_path_by_index(uint32_t gpu_index, std::string *drm_path) const {
    if (gpu_index + 1 > drm_paths_.size()) return AMDSMI_STATUS_NOT_SUPPORTED;
    *drm_path = drm_paths_[gpu_index];
    return AMDSMI_STATUS_SUCCESS;
}

std::vector<std::string>& AMDSmiDrm::get_drm_paths() {
    return drm_paths_;
}

bool AMDSmiDrm::check_if_drm_is_supported() {
    return drm_cmd_write_ != NULL ? true : false;
}

std::vector<amdsmi_bdf_t> AMDSmiDrm::get_bdfs() {
    return drm_bdfs_;
}

}  // namespace smi
}  // namespace amd


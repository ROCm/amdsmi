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
#include <assert.h>
#include <errno.h>
#include <sys/utsname.h>
#include <stdio.h>
#include <string.h>
#include <string>
#include <algorithm>
#include <sstream>
#include <iomanip>
#include <iostream>
#include <vector>
#include <set>
#include <memory>
#include <xf86drm.h>
#include "amd_smi.h"
#include "impl/amd_smi_common.h"
#include "impl/amd_smi_system.h"
#include "impl/amd_smi_socket.h"
#include "impl/amd_smi_gpu_device.h"
#include "rocm_smi/rocm_smi.h"
#include "impl/amdgpu_drm.h"


template <typename F, typename ...Args>
amdsmi_status_t rsmi_wrapper(F && f,
            amdsmi_device_handle device_handle, Args &&... args) {
    if (device_handle == nullptr) return AMDSMI_STATUS_INVAL;

    amd::smi::AMDSmiDevice* device = nullptr;
    amdsmi_status_t r = amd::smi::AMDSmiSystem::getInstance()
                    .handle_to_device(device_handle, &device);
    if (r != AMDSMI_STATUS_SUCCESS) return r;

    if (device->get_device_type() == AMD_GPU) {
         amd::smi::AMDSmiGPUDevice* gpu_device =
                static_cast<amd::smi::AMDSmiGPUDevice*>(device_handle);
         uint32_t gpu_index = gpu_device->get_gpu_id();
        auto r = std::forward<F>(f)(gpu_index,
                    std::forward<Args>(args)...);
        return static_cast<amdsmi_status_t>(r);
    }

    return AMDSMI_STATUS_NOT_SUPPORTED;
}

amdsmi_status_t
amdsmi_init(uint64_t flags) {
    return amd::smi::AMDSmiSystem::getInstance().init(flags);
}

amdsmi_status_t
amdsmi_shut_down() {
    return amd::smi::AMDSmiSystem::getInstance().cleanup();
}

amdsmi_status_t
amdsmi_status_string(amdsmi_status_t status, const char **status_string) {
    if (status <= AMDSMI_LIB_START) {
      return static_cast<amdsmi_status_t>(
        rsmi_status_string(static_cast<rsmi_status_t>(status), status_string));
    }
    switch (status) {
        case AMDSMI_STATUS_FAIL_LOAD_MODULE:
            *status_string = "FAIL_LOAD_MODULE: Fail to load module.";
            break;
        case AMDSMI_STATUS_FAIL_LOAD_SYMBOL:
            *status_string = "FAIL_LOAD_SYMOBL: Fail to load symobl.";
            break;
        case AMDSMI_STATUS_DRM_ERROR:
            *status_string = "DRM_ERROR: Fail to run function in libdrm.";
            break;
        default:
            *status_string = "An unknown error occurred";
            return AMDSMI_STATUS_UNKNOWN_ERROR;
    }
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t amdsmi_get_socket_handles(uint32_t *socket_count,
                amdsmi_socket_handle* socket_handles[]) {
    if (socket_count == nullptr || socket_handles == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    std::vector<amd::smi::AMDSmiSocket*>& sockets
            = amd::smi::AMDSmiSystem::getInstance().get_sockets();
    *socket_count = static_cast<uint32_t>(sockets.size());
    *socket_handles = reinterpret_cast<amdsmi_socket_handle*>(sockets.data());
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t amdsmi_get_socket_info(
                amdsmi_socket_handle socket_handle,
                char *name, size_t len) {
    if (socket_handle == nullptr || name == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }


    amd::smi::AMDSmiSocket* socket = nullptr;
    amdsmi_status_t r = amd::smi::AMDSmiSystem::getInstance()
                    .handle_to_socket(socket_handle, &socket);
    if (r != AMDSMI_STATUS_SUCCESS) return r;

    strncpy(name, socket->get_socket_id().c_str(), len);

    return AMDSMI_STATUS_SUCCESS;
}


amdsmi_status_t amdsmi_get_device_handles(amdsmi_socket_handle socket_handle,
                                    uint32_t *device_count,
                                    amdsmi_device_handle* device_handles[]) {
    if (device_count == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    amd::smi::AMDSmiSocket* socket = nullptr;
    amdsmi_status_t r = amd::smi::AMDSmiSystem::getInstance()
                    .handle_to_socket(socket_handle, &socket);
    if (r != AMDSMI_STATUS_SUCCESS) return r;

    *device_count = static_cast<uint32_t>(socket->get_devices().size());
    *device_handles = reinterpret_cast<amdsmi_device_handle*>(
        socket->get_devices().data());
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t amdsmi_get_device_type(amdsmi_device_handle device_handle ,
              device_type_t* device_type) {
    if (device_type == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }
    amd::smi::AMDSmiDevice* device = nullptr;
    amdsmi_status_t r = amd::smi::AMDSmiSystem::getInstance()
                    .handle_to_device(device_handle, &device);
    if (r != AMDSMI_STATUS_SUCCESS) return r;
    *device_type = device->get_device_type();

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t amdsmi_get_board_info(amdsmi_device_handle device_handle, amdsmi_board_info_t *board_info) {
    if (board_info == NULL) {
        return AMDSMI_STATUS_INVAL;
    }

    return rsmi_wrapper(rsmi_dev_name_get, device_handle, board_info->product_name, AMDSMI_NORMAL_STRING_LENGTH);
}

amdsmi_status_t amdsmi_dev_temp_metric_get(amdsmi_device_handle device_handle,
                    uint32_t sensor_type,
                    amdsmi_temperature_metric_t metric, int64_t *temperature) {
    if (temperature == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    return rsmi_wrapper(rsmi_dev_temp_metric_get, device_handle, sensor_type,
            static_cast<rsmi_temperature_metric_t>(metric), temperature);
}

amdsmi_status_t amdsmi_get_vram_usage(amdsmi_device_handle device_handle, amdsmi_vram_info_t *vram_info) {
    if (vram_info == NULL) {
        return AMDSMI_STATUS_INVAL;
    }

    amd::smi::AMDSmiDevice* device = nullptr;
    amdsmi_status_t r = amd::smi::AMDSmiSystem::getInstance()
                    .handle_to_device(device_handle, &device);
    if (r != AMDSMI_STATUS_SUCCESS) return r;

    if (device->get_device_type() != AMD_GPU) {
        return AMDSMI_STATUS_NOT_SUPPORTED;
    }
    amd::smi::AMDSmiGPUDevice* gpu_device =
                static_cast<amd::smi::AMDSmiGPUDevice*>(device_handle);

    struct drm_amdgpu_info_vram_gtt gtt;
    uint64_t vram_used = 0;

    r = gpu_device->amdgpu_query_info(AMDGPU_INFO_VRAM_GTT,
                sizeof(struct drm_amdgpu_memory_info), &gtt);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;

    vram_info->vram_total = static_cast<uint32_t>(gtt.vram_size / (1024 * 1024));

    r = gpu_device->amdgpu_query_info(AMDGPU_INFO_VRAM_USAGE,
                sizeof(vram_used), &vram_used);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;

    vram_info->vram_used = static_cast<uint32_t>(vram_used / (1024 * 1024));

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t amdsmi_get_caps_info(amdsmi_device_handle device_handle,
      struct amdsmi_gpu_caps *info) {
    if (info == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    amd::smi::AMDSmiDevice* amd_device = nullptr;
    amdsmi_status_t r = amd::smi::AMDSmiSystem::getInstance()
                    .handle_to_device(device_handle, &amd_device);
    if (r != AMDSMI_STATUS_SUCCESS) return r;

    if (amd_device->get_device_type() != AMD_GPU) {
        return AMDSMI_STATUS_NOT_SUPPORTED;
    }
    amd::smi::AMDSmiGPUDevice* gpu_device =
                static_cast<amd::smi::AMDSmiGPUDevice*>(device_handle);

    unsigned uvd, vce, uvd_enc, vcn_enc;
    struct drm_amdgpu_info_hw_ip ip;
    struct drm_amdgpu_info_device device;
    unsigned count, j;

    r = gpu_device->amdgpu_query_info(AMDGPU_INFO_DEV_INFO,
            sizeof(struct drm_amdgpu_info_device), &device);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;

    info->gfx.gfxip_cu_count = device.cu_active_number;

    r = gpu_device->amdgpu_query_hw_ip(AMDGPU_INFO_HW_IP_INFO,
        AMDGPU_HW_IP_GFX, sizeof(ip), &ip);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;

    info->gfx.gfxip_major = ip.hw_ip_version_major;
    info->gfx.gfxip_minor = ip.hw_ip_version_minor;

    r = gpu_device->amdgpu_query_hw_ip(AMDGPU_INFO_HW_IP_COUNT,
            AMDGPU_HW_IP_GFX, sizeof(unsigned), &count);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;
    info->gfx_ip_count = count;

    r = gpu_device->amdgpu_query_hw_ip(AMDGPU_INFO_HW_IP_COUNT,
        AMDGPU_HW_IP_DMA, sizeof(unsigned), &count);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;
    info->dma_ip_count = count;


    count = 0;
    /* Count multimedia engines */
    r = gpu_device->amdgpu_query_hw_ip(AMDGPU_INFO_HW_IP_COUNT,
        AMDGPU_HW_IP_UVD, sizeof(struct drm_amdgpu_info_device), &uvd);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;

    for (j = 0; j < uvd; j++)
        info->mm.mm_ip_list[count++] = MM_UVD;

    r = gpu_device->amdgpu_query_hw_ip(AMDGPU_INFO_HW_IP_COUNT,
        AMDGPU_HW_IP_UVD_ENC, sizeof(struct drm_amdgpu_info_device), &uvd_enc);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;

    for (j = 0; j < uvd_enc; j++)
        info->mm.mm_ip_list[count++] = MM_UVD;

    r = gpu_device->amdgpu_query_hw_ip(AMDGPU_INFO_HW_IP_COUNT,
        AMDGPU_HW_IP_VCE, sizeof(struct drm_amdgpu_info_device), &vce);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;

    for (j = 0; j < vce; j++)
        info->mm.mm_ip_list[count++] = MM_VCE;

    /* VCN is shared DEC/ENC check only ENC */
    r = gpu_device->amdgpu_query_hw_ip(AMDGPU_INFO_HW_IP_COUNT,
            AMDGPU_HW_IP_VCN_ENC, sizeof(struct drm_amdgpu_info_device),
            &vcn_enc);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;

    for (j = 0; j < vcn_enc; j++)
        info->mm.mm_ip_list[count++] = MM_VCN;

    info->mm.mm_ip_count = static_cast<uint8_t>(count);

    info->ras_supported = false;

    return AMDSMI_STATUS_SUCCESS;
}


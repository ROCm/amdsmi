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

// TODO(bliu): One to one map to all status code
static amdsmi_status_t rsmi_to_amdsmi_status(rsmi_status_t status) {
    return static_cast<amdsmi_status_t>(status);
}

static amdsmi_status_t get_gpu_device_from_handle(amdsmi_device_handle device_handle,
            amd::smi::AMDSmiGPUDevice** gpudevice) {
    if (device_handle == nullptr || gpudevice == nullptr)
        return AMDSMI_STATUS_INVAL;

    amd::smi::AMDSmiDevice* device = nullptr;
    amdsmi_status_t r = amd::smi::AMDSmiSystem::getInstance()
                    .handle_to_device(device_handle, &device);
    if (r != AMDSMI_STATUS_SUCCESS) return r;

    if (device->get_device_type() == AMD_GPU) {
        *gpudevice = static_cast<amd::smi::AMDSmiGPUDevice*>(device_handle);
        return AMDSMI_STATUS_SUCCESS;
    }

    return AMDSMI_STATUS_NOT_SUPPORTED;
}

template <typename F, typename ...Args>
amdsmi_status_t rsmi_wrapper(F && f,
            amdsmi_device_handle device_handle, Args &&... args) {
    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(device_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS) return r;


    uint32_t gpu_index = gpu_device->get_gpu_id();
    auto rstatus = std::forward<F>(f)(gpu_index,
                    std::forward<Args>(args)...);
    return rsmi_to_amdsmi_status(rstatus);
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
      return rsmi_to_amdsmi_status(
        rsmi_status_string(static_cast<rsmi_status_t>(status), status_string));
    }
    switch (status) {
        case AMDSMI_STATUS_FAIL_LOAD_MODULE:
            *status_string = "FAIL_LOAD_MODULE: Fail to load module.";
            break;
        case AMDSMI_STATUS_FAIL_LOAD_SYMBOL:
            *status_string = "FAIL_LOAD_SYMOBL: Fail to load symbol.";
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

amdsmi_status_t amdsmi_get_board_info(amdsmi_device_handle device_handle,
            amdsmi_board_info_t *board_info) {
    if (board_info == NULL) {
        return AMDSMI_STATUS_INVAL;
    }

    return rsmi_wrapper(rsmi_dev_name_get, device_handle,
            board_info->product_name, AMDSMI_PRODUCT_NAME_LENGTH);
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

amdsmi_status_t amdsmi_get_vram_usage(amdsmi_device_handle device_handle,
            amdsmi_vram_info_t *vram_info) {
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


amdsmi_status_t amdsmi_dev_fan_rpms_get(amdsmi_device_handle device_handle,
                            uint32_t sensor_ind, int64_t *speed) {
    return rsmi_wrapper(rsmi_dev_fan_rpms_get, device_handle, sensor_ind,
            speed);
}

amdsmi_status_t amdsmi_dev_fan_speed_get(amdsmi_device_handle device_handle,
                                        uint32_t sensor_ind, int64_t *speed) {
    return rsmi_wrapper(rsmi_dev_fan_speed_get, device_handle,
                        sensor_ind, speed);
}

amdsmi_status_t amdsmi_dev_fan_speed_max_get(amdsmi_device_handle device_handle,
                                    uint32_t sensor_ind, uint64_t *max_speed) {
    return rsmi_wrapper(rsmi_dev_fan_speed_max_get, device_handle,
                sensor_ind, max_speed);
}

amdsmi_status_t amdsmi_dev_fan_reset(amdsmi_device_handle device_handle,
                                    uint32_t sensor_ind) {
    return rsmi_wrapper(rsmi_dev_fan_reset, device_handle, sensor_ind);
}

amdsmi_status_t amdsmi_dev_fan_speed_set(amdsmi_device_handle device_handle,
                                uint32_t sensor_ind, uint64_t speed) {
    return rsmi_wrapper(rsmi_dev_fan_speed_set, device_handle,
                            sensor_ind, speed);
}

amdsmi_status_t amdsmi_dev_id_get(amdsmi_device_handle device_handle,
                                uint16_t *id) {
    return rsmi_wrapper(rsmi_dev_id_get, device_handle, id);
}

// TODO(bliu) : add other asic info
amdsmi_status
amdsmi_get_asic_info(amdsmi_device_handle dev, amdsmi_asic_info_t *info) {
    if (info == nullptr)  return AMDSMI_STATUS_INVAL;
    uint16_t vendor_id = 0;
    amdsmi_status status = rsmi_wrapper(rsmi_dev_vendor_id_get, dev,
                            &vendor_id);
    if (status == AMDSMI_STATUS_SUCCESS) info->vendor_id = vendor_id;
    return status;
}


amdsmi_status_t amdsmi_dev_subsystem_id_get(amdsmi_device_handle device_handle,
                                uint16_t *id) {
    return rsmi_wrapper(rsmi_dev_subsystem_id_get, device_handle, id);
}

amdsmi_status_t amdsmi_dev_subsystem_vendor_id_get(
                        amdsmi_device_handle device_handle, uint16_t *id) {
    return rsmi_wrapper(rsmi_dev_subsystem_vendor_id_get, device_handle, id);
}

amdsmi_status_t
amdsmi_event_notification_init(amdsmi_device_handle device_handle) {
    return rsmi_wrapper(rsmi_event_notification_init, device_handle);
}

amdsmi_status_t
amdsmi_event_notification_mask_set(amdsmi_device_handle device_handle,
            uint64_t mask) {
    return rsmi_wrapper(rsmi_event_notification_mask_set, device_handle, mask);
}

amdsmi_status_t
amdsmi_event_notification_get(int timeout_ms,
                     uint32_t *num_elem, amdsmi_evt_notification_data_t *data) {
    if (num_elem == nullptr || data == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    // Get the rsmi data
    std::vector<rsmi_evt_notification_data_t> r_data(*num_elem);
    rsmi_status_t r = rsmi_event_notification_get(
                        timeout_ms, num_elem, &r_data[0]);
    if (r != RSMI_STATUS_SUCCESS) {
        return rsmi_to_amdsmi_status(r);
    }

    // convert output
    for (uint32_t i=0; i < *num_elem; i++) {
        rsmi_evt_notification_data_t rsmi_data = r_data[i];
        data[i].event = static_cast<amdsmi_evt_notification_type_t>(
                rsmi_data.event);
        strncpy(data[i].message, rsmi_data.message,
                MAX_EVENT_NOTIFICATION_MSG_SIZE);
        amdsmi_status_t r = amd::smi::AMDSmiSystem::getInstance()
            .gpu_index_to_handle(rsmi_data.dv_ind, &(data[i].device_handle));
        if (r != AMDSMI_STATUS_SUCCESS) return r;
    }

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t amdsmi_event_notification_stop(
                amdsmi_device_handle device_handle) {
    return rsmi_wrapper(rsmi_event_notification_stop, device_handle);
}

amdsmi_status_t amdsmi_dev_counter_group_supported(
        amdsmi_device_handle device_handle, amdsmi_event_group_t group) {
    return rsmi_wrapper(rsmi_dev_counter_group_supported, device_handle,
                    static_cast<rsmi_event_group_t>(group));
}

amdsmi_status_t amdsmi_dev_counter_create(amdsmi_device_handle device_handle,
        amdsmi_event_type_t type, amdsmi_event_handle_t *evnt_handle) {
    return rsmi_wrapper(rsmi_dev_counter_create, device_handle,
                    static_cast<rsmi_event_type_t>(type),
                    static_cast<rsmi_event_handle_t*>(evnt_handle));
}

amdsmi_status_t amdsmi_dev_counter_destroy(amdsmi_event_handle_t evnt_handle) {
    rsmi_status_t r = rsmi_dev_counter_destroy(
        static_cast<rsmi_event_handle_t>(evnt_handle));
    return rsmi_to_amdsmi_status(r);
}

amdsmi_status_t amdsmi_counter_control(amdsmi_event_handle_t evt_handle,
                                amdsmi_counter_command_t cmd, void *cmd_args) {
    rsmi_status_t r = rsmi_counter_control(
        static_cast<rsmi_event_handle_t>(evt_handle),
        static_cast<rsmi_counter_command_t>(cmd), cmd_args);
    return rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
amdsmi_counter_read(amdsmi_event_handle_t evt_handle,
                            amdsmi_counter_value_t *value) {
    rsmi_status_t r = rsmi_counter_read(
        static_cast<rsmi_event_handle_t>(evt_handle),
        reinterpret_cast<rsmi_counter_value_t*>(value));
    return rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
amdsmi_counter_available_counters_get(amdsmi_device_handle device_handle,
                            amdsmi_event_group_t grp, uint32_t *available) {
    return rsmi_wrapper(rsmi_counter_available_counters_get, device_handle,
                    static_cast<rsmi_event_group_t>(grp),
                    available);
}

amdsmi_status_t
amdsmi_topo_get_numa_node_number(amdsmi_device_handle device_handle, uint32_t *numa_node) {
    return rsmi_wrapper(rsmi_topo_get_numa_node_number, device_handle, numa_node);
}

amdsmi_status_t
amdsmi_topo_get_link_weight(amdsmi_device_handle device_handle_src, amdsmi_device_handle device_handle_dst,
                          uint64_t *weight) {
    amd::smi::AMDSmiGPUDevice* src_device = nullptr;
    amd::smi::AMDSmiGPUDevice* dst_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(device_handle_src, &src_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    r = get_gpu_device_from_handle(device_handle_dst, &dst_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    auto rstatus = rsmi_topo_get_link_weight(src_device->get_gpu_id(), dst_device->get_gpu_id(),
                weight);
    return rsmi_to_amdsmi_status(rstatus);
}

amdsmi_status_t
amdsmi_minmax_bandwidth_get(amdsmi_device_handle device_handle_src, amdsmi_device_handle device_handle_dst,
                          uint64_t *min_bandwidth, uint64_t *max_bandwidth) {
    amd::smi::AMDSmiGPUDevice* src_device = nullptr;
    amd::smi::AMDSmiGPUDevice* dst_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(device_handle_src, &src_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    r = get_gpu_device_from_handle(device_handle_dst, &dst_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    auto rstatus = rsmi_minmax_bandwidth_get(src_device->get_gpu_id(), dst_device->get_gpu_id(),
                min_bandwidth, max_bandwidth);
    return rsmi_to_amdsmi_status(rstatus);
}

amdsmi_status_t
amdsmi_topo_get_link_type(amdsmi_device_handle device_handle_src, amdsmi_device_handle device_handle_dst,
                        uint64_t *hops, AMDSMI_IO_LINK_TYPE *type) {
    amd::smi::AMDSmiGPUDevice* src_device = nullptr;
    amd::smi::AMDSmiGPUDevice* dst_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(device_handle_src, &src_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    r = get_gpu_device_from_handle(device_handle_dst, &dst_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    auto rstatus = rsmi_topo_get_link_type(src_device->get_gpu_id(), dst_device->get_gpu_id(),
                hops, reinterpret_cast<RSMI_IO_LINK_TYPE*>(type));
    return rsmi_to_amdsmi_status(rstatus);
}

amdsmi_status_t
amdsmi_is_P2P_accessible(amdsmi_device_handle device_handle_src, amdsmi_device_handle device_handle_dst,
                       bool *accessible) {
    amd::smi::AMDSmiGPUDevice* src_device = nullptr;
    amd::smi::AMDSmiGPUDevice* dst_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(device_handle_src, &src_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    r = get_gpu_device_from_handle(device_handle_dst, &dst_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    auto rstatus = rsmi_is_P2P_accessible(src_device->get_gpu_id(), dst_device->get_gpu_id(),
                accessible);
    return rsmi_to_amdsmi_status(rstatus);
}

// TODO(bliu) : other xgmi related information
amdsmi_status
amdsmi_get_xgmi_info(amdsmi_device_handle device_handle, amdsmi_xgmi_info_t *info) {
    if (info == nullptr)
        return AMDSMI_STATUS_INVAL;
    return rsmi_wrapper(rsmi_dev_xgmi_hive_id_get, device_handle,
                    &(info->xgmi_hive_id));
}

amdsmi_status_t
amdsmi_dev_xgmi_error_status(amdsmi_device_handle device_handle, amdsmi_xgmi_status_t *status) {
    return rsmi_wrapper(rsmi_dev_xgmi_error_status, device_handle,
                    reinterpret_cast<rsmi_xgmi_status_t*>(status));
}

amdsmi_status_t
amdsmi_dev_xgmi_error_reset(amdsmi_device_handle device_handle) {
    return rsmi_wrapper(rsmi_dev_xgmi_error_reset, device_handle);
}

amdsmi_status_t
amdsmi_dev_supported_func_iterator_open(amdsmi_device_handle device_handle,
                                amdsmi_func_id_iter_handle_t *handle) {
    if (handle == nullptr)
        return AMDSMI_STATUS_INVAL;
    return rsmi_wrapper(rsmi_dev_supported_func_iterator_open, device_handle,
                reinterpret_cast<rsmi_func_id_iter_handle_t*>(handle));
}

amdsmi_status_t
amdsmi_dev_supported_variant_iterator_open(amdsmi_func_id_iter_handle_t obj_h,
                                    amdsmi_func_id_iter_handle_t *var_iter) {
    if (var_iter == nullptr)
        return AMDSMI_STATUS_INVAL;
    auto r = rsmi_dev_supported_variant_iterator_open(
            reinterpret_cast<rsmi_func_id_iter_handle_t>(obj_h),
            reinterpret_cast<rsmi_func_id_iter_handle_t*>(var_iter));
    return rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
amdsmi_func_iter_next(amdsmi_func_id_iter_handle_t handle) {
    auto r = rsmi_func_iter_next(
            reinterpret_cast<rsmi_func_id_iter_handle_t>(handle));
    return rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
amdsmi_dev_supported_func_iterator_close(amdsmi_func_id_iter_handle_t *handle) {
    if (handle == nullptr)
        return AMDSMI_STATUS_INVAL;
    auto r = rsmi_dev_supported_func_iterator_close(
        reinterpret_cast<rsmi_func_id_iter_handle_t*>(handle));
    return rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
amdsmi_func_iter_value_get(amdsmi_func_id_iter_handle_t handle,
                            amdsmi_func_id_value_t *value) {
    if (value == nullptr)
        return AMDSMI_STATUS_INVAL;
    auto r = rsmi_func_iter_value_get(
        reinterpret_cast<rsmi_func_id_iter_handle_t>(handle),
        reinterpret_cast<rsmi_func_id_value_t*>(value));
    return rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
amdsmi_compute_process_info_get(amdsmi_process_info_t *procs, uint32_t *num_items) {
    if (num_items == nullptr)
        return AMDSMI_STATUS_INVAL;
    auto r = rsmi_compute_process_info_get(
        reinterpret_cast<rsmi_process_info_t*>(procs),
        num_items);
    return rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
amdsmi_compute_process_info_by_pid_get(uint32_t pid, amdsmi_process_info_t *proc) {
    if (proc == nullptr)
        return AMDSMI_STATUS_INVAL;
    auto r = rsmi_compute_process_info_by_pid_get(pid,
        reinterpret_cast<rsmi_process_info_t*>(proc));
    return rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
amdsmi_compute_process_gpus_get(uint32_t pid, uint32_t *dv_indices,
                                                       uint32_t *num_devices) {
    if (dv_indices == nullptr || num_devices == nullptr)
        return AMDSMI_STATUS_INVAL;
    auto r = rsmi_compute_process_gpus_get(pid, dv_indices, num_devices);
    return rsmi_to_amdsmi_status(r);
}


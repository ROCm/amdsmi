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
#include <fstream>
#include <vector>
#include <set>
#include <map>
#include <memory>
#include <xf86drm.h>
#include "amd_smi/amdsmi.h"
#include "amd_smi/impl/fdinfo.h"
#include "amd_smi/impl/amd_smi_common.h"
#include "amd_smi/impl/amd_smi_system.h"
#include "amd_smi/impl/amd_smi_socket.h"
#include "amd_smi/impl/amd_smi_gpu_device.h"
#include "amd_smi/impl/amd_smi_uuid.h"
#include "rocm_smi/rocm_smi.h"
#include "rocm_smi/rocm_smi_common.h"
#include "amd_smi/impl/amdgpu_drm.h"
#include "amd_smi/impl/amd_smi_utils.h"

static bool initialized_lib = false;

#define AMDSMI_CHECK_INIT() do { \
	if (!initialized_lib) { \
		return AMDSMI_STATUS_NOT_INIT; \
	} \
} while (0)

static amdsmi_status_t get_gpu_device_from_handle(amdsmi_processor_handle processor_handle,
            amd::smi::AMDSmiGPUDevice** gpudevice) {

    AMDSMI_CHECK_INIT();

    if (processor_handle == nullptr || gpudevice == nullptr)
        return AMDSMI_STATUS_INVAL;

    amd::smi::AMDSmiProcessor* device = nullptr;
    amdsmi_status_t r = amd::smi::AMDSmiSystem::getInstance()
                    .handle_to_processor(processor_handle, &device);
    if (r != AMDSMI_STATUS_SUCCESS) return r;

    if (device->get_processor_type() == AMD_GPU) {
        *gpudevice = static_cast<amd::smi::AMDSmiGPUDevice*>(processor_handle);
        return AMDSMI_STATUS_SUCCESS;
    }

    return AMDSMI_STATUS_NOT_SUPPORTED;
}

template <typename F, typename ...Args>
amdsmi_status_t rsmi_wrapper(F && f,
    amdsmi_processor_handle processor_handle, Args &&... args) {

    AMDSMI_CHECK_INIT();

    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS) return r;


    uint32_t gpu_index = gpu_device->get_gpu_id();
    auto rstatus = std::forward<F>(f)(gpu_index,
                    std::forward<Args>(args)...);
    return amd::smi::rsmi_to_amdsmi_status(rstatus);
}

amdsmi_status_t
amdsmi_init(uint64_t flags) {
    if (initialized_lib)
        return AMDSMI_STATUS_SUCCESS;

    amdsmi_status_t status = amd::smi::AMDSmiSystem::getInstance().init(flags);
    if (status == AMDSMI_STATUS_SUCCESS) {
        initialized_lib = true;
    }
    return status;
}

amdsmi_status_t
amdsmi_shut_down() {
    if (!initialized_lib)
        return AMDSMI_STATUS_SUCCESS;
    amdsmi_status_t status = amd::smi::AMDSmiSystem::getInstance().cleanup();
    if (status == AMDSMI_STATUS_SUCCESS) {
        initialized_lib = false;
    }
    return status;
}

amdsmi_status_t
amdsmi_status_string(amdsmi_status_t status, const char **status_string) {
    switch (status) {
        case AMDSMI_STATUS_FAIL_LOAD_MODULE:
            *status_string = "FAIL_LOAD_MODULE: Fail to load module.";
            break;
        case AMDSMI_STATUS_FAIL_LOAD_SYMBOL:
            *status_string = "FAIL_LOAD_SYMBOL: Fail to load symbol.";
            break;
        case AMDSMI_STATUS_DRM_ERROR:
            *status_string = "DRM_ERROR: Fail to run function in libdrm.";
            break;
        default:
            // The case above didn't have a match, so look up the amdsmi status in the rsmi status map
            // If found, get the rsmi status string.  If not, return unknown error string
            for (auto& iter : amd::smi::rsmi_status_map) {
                if (iter.second == status) {
                    rsmi_status_string(iter.first, status_string);
                    return AMDSMI_STATUS_SUCCESS;
                }
            }
            // Not found
            *status_string = "An unknown error occurred";
            return AMDSMI_STATUS_UNKNOWN_ERROR;
    }
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t amdsmi_get_socket_handles(uint32_t *socket_count,
                amdsmi_socket_handle* socket_handles) {

    AMDSMI_CHECK_INIT();

    if (socket_count == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    std::vector<amd::smi::AMDSmiSocket*>& sockets
            = amd::smi::AMDSmiSystem::getInstance().get_sockets();
    uint32_t socket_size = static_cast<uint32_t>(sockets.size());
    // Get the socket size
    if (socket_handles == nullptr) {
        *socket_count = socket_size;
        return AMDSMI_STATUS_SUCCESS;
    }

    // If the socket_handles can hold all sockets, return all of them.
    *socket_count = *socket_count >= socket_size ? socket_size : *socket_count;

    // Copy the socket handles
    for (uint32_t i = 0; i < *socket_count; i++) {
        socket_handles[i] = reinterpret_cast<amdsmi_socket_handle>(sockets[i]);
    }

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t amdsmi_get_socket_info(
                amdsmi_socket_handle socket_handle,
                char *name, size_t len) {
    AMDSMI_CHECK_INIT();

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

amdsmi_status_t amdsmi_get_processor_handles(amdsmi_socket_handle socket_handle,
                                    uint32_t* processor_count,
                                    amdsmi_processor_handle* processor_handles) {
    AMDSMI_CHECK_INIT();

    if (processor_count == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    // Get the socket object via socket handle.
    amd::smi::AMDSmiSocket* socket = nullptr;
    amdsmi_status_t r = amd::smi::AMDSmiSystem::getInstance()
                    .handle_to_socket(socket_handle, &socket);
    if (r != AMDSMI_STATUS_SUCCESS) return r;


    std::vector<amd::smi::AMDSmiProcessor*>& processors = socket->get_processors();
    uint32_t processor_size = static_cast<uint32_t>(processors.size());
    // Get the processor count only
    if (processor_handles == nullptr) {
        *processor_count = processor_size;
        return AMDSMI_STATUS_SUCCESS;
    }

    // If the processor_handles can hold all processors, return all of them.
    *processor_count = *processor_count >= processor_size ? processor_size : *processor_count;

    // Copy the processor handles
    for (uint32_t i = 0; i < *processor_count; i++) {
        processor_handles[i] = reinterpret_cast<amdsmi_processor_handle>(processors[i]);
    }

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t amdsmi_get_processor_type(amdsmi_processor_handle processor_handle ,
              processor_type_t* processor_type) {

    AMDSMI_CHECK_INIT();

    if (processor_type == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }
    amd::smi::AMDSmiProcessor* processor = nullptr;
    amdsmi_status_t r = amd::smi::AMDSmiSystem::getInstance()
                    .handle_to_processor(processor_handle, &processor);
    if (r != AMDSMI_STATUS_SUCCESS) return r;
    *processor_type = processor->get_processor_type();

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t
amdsmi_get_gpu_device_bdf(amdsmi_processor_handle processor_handle, amdsmi_bdf_t *bdf) {

    AMDSMI_CHECK_INIT();

    if (bdf == NULL) {
        return AMDSMI_STATUS_INVAL;
    }

    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    // get bdf from sysfs file
    *bdf = gpu_device->get_bdf();

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t amdsmi_get_gpu_board_info(amdsmi_processor_handle processor_handle, amdsmi_board_info_t *board_info) {

    AMDSMI_CHECK_INIT();

    if (board_info == NULL) {
        return AMDSMI_STATUS_INVAL;
    }

    amdsmi_status_t status;
    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    if (gpu_device->check_if_drm_is_supported()) {
        // Get from sys file
        status = smi_amdgpu_get_board_info(gpu_device, board_info);
    }
    else {
        // ignore the errors so that it can populate as many fields as possible.
        // call rocm-smi which search multiple places for device name
        status = rsmi_wrapper(rsmi_dev_name_get, processor_handle,
                        board_info->product_name, AMDSMI_PRODUCT_NAME_LENGTH);

        if (board_info->product_serial[0] == '\0') {
            status = rsmi_wrapper(rsmi_dev_serial_number_get, processor_handle,
                        board_info->product_serial, AMDSMI_NORMAL_STRING_LENGTH);
        }
    }

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t  amdsmi_get_temp_metric(amdsmi_processor_handle processor_handle,
                    amdsmi_temperature_type_t sensor_type,
                    amdsmi_temperature_metric_t metric, int64_t *temperature) {

    AMDSMI_CHECK_INIT();

    if (temperature == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    // Get the PLX temperature from the gpu_metrics
    if (sensor_type == TEMPERATURE_TYPE_PLX) {
        amdsmi_gpu_metrics_t metric_info;
        auto r_status =  amdsmi_get_gpu_metrics_info(
                processor_handle, &metric_info);
        if (r_status != AMDSMI_STATUS_SUCCESS)
            return r_status;
        *temperature = metric_info.temperature_vrsoc;
        return r_status;
    }
    amdsmi_status_t amdsmi_status = rsmi_wrapper(rsmi_dev_temp_metric_get, processor_handle,
            static_cast<uint32_t>(sensor_type),
            static_cast<rsmi_temperature_metric_t>(metric), temperature);
    *temperature /= 1000;
    return amdsmi_status;
}

amdsmi_status_t amdsmi_get_gpu_vram_usage(amdsmi_processor_handle processor_handle,
            amdsmi_vram_info_t *vram_info) {

    AMDSMI_CHECK_INIT();

    if (vram_info == NULL) {
        return AMDSMI_STATUS_INVAL;
    }

    amd::smi::AMDSmiProcessor* device = nullptr;
    amdsmi_status_t ret = amd::smi::AMDSmiSystem::getInstance()
                    .handle_to_processor(processor_handle, &device);
    if (ret != AMDSMI_STATUS_SUCCESS) return ret;

    if (device->get_processor_type() != AMD_GPU) {
        return AMDSMI_STATUS_NOT_SUPPORTED;
    }

    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    struct drm_amdgpu_info_vram_gtt gtt;
    uint64_t vram_used = 0;

    r = gpu_device->amdgpu_query_info(AMDGPU_INFO_VRAM_GTT,
                sizeof(struct drm_amdgpu_memory_info), &gtt);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;

    vram_info->vram_total = static_cast<uint32_t>(
        gtt.vram_size / (1024 * 1024));

    r = gpu_device->amdgpu_query_info(AMDGPU_INFO_VRAM_USAGE,
                sizeof(vram_used), &vram_used);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;

    vram_info->vram_used = static_cast<uint32_t>(vram_used / (1024 * 1024));

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t amdsmi_get_caps_info(amdsmi_processor_handle processor_handle,
            amdsmi_gpu_caps_t *info) {

    AMDSMI_CHECK_INIT();

    if (info == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    amd::smi::AMDSmiProcessor* amd_device = nullptr;
    amdsmi_status_t ret = amd::smi::AMDSmiSystem::getInstance()
                    .handle_to_processor(processor_handle, &amd_device);
    if (ret != AMDSMI_STATUS_SUCCESS) return ret;

    if (amd_device->get_processor_type() != AMD_GPU) {
        return AMDSMI_STATUS_NOT_SUPPORTED;
    }
    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    unsigned uvd, vce, uvd_enc, vcn_enc;
    struct drm_amdgpu_info_hw_ip ip;
    struct drm_amdgpu_info_device device;
    unsigned count, j;

    r = gpu_device->amdgpu_query_info(AMDGPU_INFO_DEV_INFO,
            sizeof(struct drm_amdgpu_info_device), &device);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;

    info->gfx.gfxip_cu_count = (uint16_t)device.cu_active_number;

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
        info->mm.mm_ip_list[count++] = AMDSMI_MM_UVD;

    r = gpu_device->amdgpu_query_hw_ip(AMDGPU_INFO_HW_IP_COUNT,
        AMDGPU_HW_IP_UVD_ENC, sizeof(struct drm_amdgpu_info_device), &uvd_enc);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;

    for (j = 0; j < uvd_enc; j++)
        info->mm.mm_ip_list[count++] = AMDSMI_MM_UVD;

    r = gpu_device->amdgpu_query_hw_ip(AMDGPU_INFO_HW_IP_COUNT,
        AMDGPU_HW_IP_VCE, sizeof(struct drm_amdgpu_info_device), &vce);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;

    for (j = 0; j < vce; j++)
        info->mm.mm_ip_list[count++] = AMDSMI_MM_VCE;

    /* VCN is shared DEC/ENC check only ENC */
    r = gpu_device->amdgpu_query_hw_ip(AMDGPU_INFO_HW_IP_COUNT,
            AMDGPU_HW_IP_VCN_ENC, sizeof(struct drm_amdgpu_info_device),
            &vcn_enc);
    if (r != AMDSMI_STATUS_SUCCESS)  return r;

    for (j = 0; j < vcn_enc; j++)
        info->mm.mm_ip_list[count++] = AMDSMI_MM_VCN;

    info->mm.mm_ip_count = static_cast<uint8_t>(count);

    info->ras_supported = false;

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t amdsmi_get_gpu_fan_rpms(amdsmi_processor_handle processor_handle,
                            uint32_t sensor_ind, int64_t *speed) {
    return rsmi_wrapper(rsmi_dev_fan_rpms_get, processor_handle, sensor_ind,
            speed);
}

amdsmi_status_t amdsmi_get_gpu_fan_speed(amdsmi_processor_handle processor_handle,
                                        uint32_t sensor_ind, int64_t *speed) {
    return rsmi_wrapper(rsmi_dev_fan_speed_get, processor_handle,
                        sensor_ind, speed);
}

amdsmi_status_t amdsmi_get_gpu_fan_speed_max(amdsmi_processor_handle processor_handle,
                                    uint32_t sensor_ind, uint64_t *max_speed) {
    return rsmi_wrapper(rsmi_dev_fan_speed_max_get, processor_handle,
                sensor_ind, max_speed);
}

amdsmi_status_t amdsmi_reset_gpu_fan(amdsmi_processor_handle processor_handle,
                                    uint32_t sensor_ind) {
    return rsmi_wrapper(rsmi_dev_fan_reset, processor_handle, sensor_ind);
}

amdsmi_status_t amdsmi_set_gpu_fan_speed(amdsmi_processor_handle processor_handle,
                                uint32_t sensor_ind, uint64_t speed) {
    return rsmi_wrapper(rsmi_dev_fan_speed_set, processor_handle,
                            sensor_ind, speed);
}

amdsmi_status_t amdsmi_get_gpu_id(amdsmi_processor_handle processor_handle,
                                uint16_t *id) {
    return rsmi_wrapper(rsmi_dev_id_get, processor_handle, id);
}

// TODO(bliu) : add fw info from libdrm
amdsmi_status_t amdsmi_get_fw_info(amdsmi_processor_handle processor_handle,
        amdsmi_fw_info_t *info) {
    const std::map<amdsmi_fw_block_t, rsmi_fw_block_t> fw_in_rsmi = {
        { FW_ID_ASD, RSMI_FW_BLOCK_ASD},
        { FW_ID_CP_CE, RSMI_FW_BLOCK_CE},
        { FW_ID_DMCU, RSMI_FW_BLOCK_DMCU},
        { FW_ID_MC, RSMI_FW_BLOCK_MC},
        { FW_ID_CP_ME, RSMI_FW_BLOCK_ME},
        { FW_ID_CP_MEC1, RSMI_FW_BLOCK_MEC},
        { FW_ID_CP_MEC2, RSMI_FW_BLOCK_MEC2},
        { FW_ID_CP_PFP, RSMI_FW_BLOCK_PFP},
        { FW_ID_RLC, RSMI_FW_BLOCK_RLC},
        { FW_ID_RLC_RESTORE_LIST_CNTL, RSMI_FW_BLOCK_RLC_SRLC},
        { FW_ID_RLC_RESTORE_LIST_GPM_MEM, RSMI_FW_BLOCK_RLC_SRLG},
        { FW_ID_RLC_RESTORE_LIST_SRM_MEM, RSMI_FW_BLOCK_RLC_SRLS},
        { FW_ID_SDMA0, RSMI_FW_BLOCK_SDMA},
        { FW_ID_SDMA1, RSMI_FW_BLOCK_SDMA2},
        { FW_ID_SMC, RSMI_FW_BLOCK_SMC},
        { FW_ID_PSP_SOSDRV, RSMI_FW_BLOCK_SOS},
        { FW_ID_TA_RAS, RSMI_FW_BLOCK_TA_RAS},
        { FW_ID_XGMI, RSMI_FW_BLOCK_TA_XGMI},
        { FW_ID_UVD, RSMI_FW_BLOCK_UVD},
        { FW_ID_VCE, RSMI_FW_BLOCK_VCE},
        { FW_ID_VCN, RSMI_FW_BLOCK_VCN}
    };

    AMDSMI_CHECK_INIT();

    if (info == nullptr)
        return AMDSMI_STATUS_INVAL;
    memset(info, 0, sizeof(amdsmi_fw_info_t));

    // collect all rsmi supported fw block
    for (auto ite = fw_in_rsmi.begin(); ite != fw_in_rsmi.end(); ite ++) {
        auto status = rsmi_wrapper(rsmi_dev_firmware_version_get, processor_handle,
                (*ite).second,
                &(info->fw_info_list[info->num_fw_info].fw_version));
        if (status == AMDSMI_STATUS_SUCCESS) {
            info->fw_info_list[info->num_fw_info].fw_id = (*ite).first;
            info->num_fw_info++;
        }
    }
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t
amdsmi_get_gpu_asic_info(amdsmi_processor_handle processor_handle, amdsmi_asic_info_t *info) {

    AMDSMI_CHECK_INIT();

    if (info == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    struct drm_amdgpu_info_device dev_info = {};
    uint16_t vendor_id = 0;
    uint16_t subvendor_id = 0;

    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    amdsmi_status_t status;
    if (gpu_device->check_if_drm_is_supported()){
        status = gpu_device->amdgpu_query_info(AMDGPU_INFO_DEV_INFO, sizeof(struct drm_amdgpu_info_device), &dev_info);
        if (status != AMDSMI_STATUS_SUCCESS) return status;

        SMIGPUDEVICE_MUTEX(gpu_device->get_mutex())

        std::string path = "/sys/class/drm/" + gpu_device->get_gpu_path() + "/device/unique_id";
        FILE *fp = fopen(path.c_str(), "r");
        if (fp) {
            fscanf(fp, "%s", info->asic_serial);
            fclose(fp);
        }

        status = smi_amdgpu_get_market_name_from_dev_id(dev_info.device_id, info->market_name);
        if (status != AMDSMI_STATUS_SUCCESS) {
            rsmi_wrapper(rsmi_dev_brand_get, processor_handle,
                info->market_name, AMDSMI_NORMAL_STRING_LENGTH);
        }

        info->device_id = dev_info.device_id;
        info->family = dev_info.family;
        info->rev_id = dev_info.pci_rev;
        info->vendor_id = gpu_device->get_vendor_id();
    }
    // For other sysfs related information, get from rocm-smi
    else {
        status = rsmi_wrapper(rsmi_dev_serial_number_get, processor_handle,
                info->asic_serial, AMDSMI_NORMAL_STRING_LENGTH);

        status = rsmi_wrapper(rsmi_dev_brand_get, processor_handle,
                info->market_name, AMDSMI_NORMAL_STRING_LENGTH);

        status = rsmi_wrapper(rsmi_dev_vendor_id_get, processor_handle,
                                    &vendor_id);
        if (status == AMDSMI_STATUS_SUCCESS) info->vendor_id = vendor_id;

        status =  rsmi_wrapper(rsmi_dev_subsystem_vendor_id_get, processor_handle,
                    &subvendor_id);
        if (status == AMDSMI_STATUS_SUCCESS) info->subvendor_id = subvendor_id;
    }

    return AMDSMI_STATUS_SUCCESS;
}


amdsmi_status_t amdsmi_get_gpu_subsystem_id(amdsmi_processor_handle processor_handle,
                                uint16_t *id) {
    return rsmi_wrapper(rsmi_dev_subsystem_id_get, processor_handle, id);
}

amdsmi_status_t amdsmi_get_gpu_subsystem_name(
                                amdsmi_processor_handle processor_handle,
                                char *name, size_t len) {
    return rsmi_wrapper(rsmi_dev_subsystem_name_get, processor_handle, name, len);
}

amdsmi_status_t amdsmi_get_gpu_vendor_name(
            amdsmi_processor_handle processor_handle, char *name, size_t len) {
    return rsmi_wrapper(rsmi_dev_vendor_name_get, processor_handle, name, len);
}

amdsmi_status_t amdsmi_get_gpu_vram_vendor(amdsmi_processor_handle processor_handle,
                                     char *brand, uint32_t len) {
    return rsmi_wrapper(rsmi_dev_vram_vendor_get, processor_handle, brand, len);
}

amdsmi_status_t
amdsmi_init_event_notification(amdsmi_processor_handle processor_handle) {
    return rsmi_wrapper(rsmi_event_notification_init, processor_handle);
}

amdsmi_status_t
 amdsmi_set_event_notification_mask(amdsmi_processor_handle processor_handle,
            uint64_t mask) {
    return rsmi_wrapper(rsmi_event_notification_mask_set, processor_handle, mask);
}

amdsmi_status_t
 amdsmi_get_gpu_event_notification(int timeout_ms,
                     uint32_t *num_elem, amdsmi_evt_notification_data_t *data) {
    AMDSMI_CHECK_INIT();

    if (num_elem == nullptr || data == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    // Get the rsmi data
    std::vector<rsmi_evt_notification_data_t> r_data(*num_elem);
    rsmi_status_t r = rsmi_event_notification_get(
                        timeout_ms, num_elem, &r_data[0]);
    if (r != RSMI_STATUS_SUCCESS) {
        return amd::smi::rsmi_to_amdsmi_status(r);
    }
    // convert output
    for (uint32_t i=0; i < *num_elem; i++) {
        rsmi_evt_notification_data_t rsmi_data = r_data[i];
        data[i].event = static_cast<amdsmi_evt_notification_type_t>(
                rsmi_data.event);
        strncpy(data[i].message, rsmi_data.message,
                MAX_EVENT_NOTIFICATION_MSG_SIZE);
        amdsmi_status_t r = amd::smi::AMDSmiSystem::getInstance()
            .gpu_index_to_handle(rsmi_data.dv_ind, &(data[i].processor_handle));
        if (r != AMDSMI_STATUS_SUCCESS) return r;
    }

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t amdsmi_stop_event_notification(
                amdsmi_processor_handle processor_handle) {
    return rsmi_wrapper(rsmi_event_notification_stop, processor_handle);
}

amdsmi_status_t amdsmi_dev_counter_group_supported(
        amdsmi_processor_handle processor_handle, amdsmi_event_group_t group) {
    return rsmi_wrapper(rsmi_dev_counter_group_supported, processor_handle,
                    static_cast<rsmi_event_group_t>(group));
}

amdsmi_status_t amdsmi_dev_create_counter(amdsmi_processor_handle processor_handle,
        amdsmi_event_type_t type, amdsmi_event_handle_t *evnt_handle) {
    return rsmi_wrapper(rsmi_dev_counter_create, processor_handle,
                    static_cast<rsmi_event_type_t>(type),
                    static_cast<rsmi_event_handle_t*>(evnt_handle));
}

amdsmi_status_t amdsmi_dev_destroy_counter(amdsmi_event_handle_t evnt_handle) {
    rsmi_status_t r = rsmi_dev_counter_destroy(
        static_cast<rsmi_event_handle_t>(evnt_handle));
    return amd::smi::rsmi_to_amdsmi_status(r);
}

amdsmi_status_t amdsmi_control_counter(amdsmi_event_handle_t evt_handle,
                                amdsmi_counter_command_t cmd, void *cmd_args) {
    rsmi_status_t r = rsmi_counter_control(
        static_cast<rsmi_event_handle_t>(evt_handle),
        static_cast<rsmi_counter_command_t>(cmd), cmd_args);
    return amd::smi::rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
amdsmi_read_counter(amdsmi_event_handle_t evt_handle,
                            amdsmi_counter_value_t *value) {
    rsmi_status_t r = rsmi_counter_read(
        static_cast<rsmi_event_handle_t>(evt_handle),
        reinterpret_cast<rsmi_counter_value_t*>(value));
    return amd::smi::rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
 amdsmi_counter_get_available_counters(amdsmi_processor_handle processor_handle,
                            amdsmi_event_group_t grp, uint32_t *available) {
    return rsmi_wrapper(rsmi_counter_available_counters_get, processor_handle,
                    static_cast<rsmi_event_group_t>(grp),
                    available);
}

amdsmi_status_t
amdsmi_topo_get_numa_node_number(amdsmi_processor_handle processor_handle, uint32_t *numa_node) {
    return rsmi_wrapper(rsmi_topo_get_numa_node_number, processor_handle, numa_node);
}

amdsmi_status_t
amdsmi_topo_get_link_weight(amdsmi_processor_handle processor_handle_src, amdsmi_processor_handle processor_handle_dst,
                          uint64_t *weight) {
    AMDSMI_CHECK_INIT();

    amd::smi::AMDSmiGPUDevice* src_device = nullptr;
    amd::smi::AMDSmiGPUDevice* dst_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle_src, &src_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    r = get_gpu_device_from_handle(processor_handle_dst, &dst_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    auto rstatus = rsmi_topo_get_link_weight(src_device->get_gpu_id(), dst_device->get_gpu_id(),
                weight);
    return amd::smi::rsmi_to_amdsmi_status(rstatus);
}

amdsmi_status_t
 amdsmi_get_minmax_bandwidth(amdsmi_processor_handle processor_handle_src, amdsmi_processor_handle processor_handle_dst,
                          uint64_t *min_bandwidth, uint64_t *max_bandwidth) {
    AMDSMI_CHECK_INIT();

    amd::smi::AMDSmiGPUDevice* src_device = nullptr;
    amd::smi::AMDSmiGPUDevice* dst_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle_src, &src_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    r = get_gpu_device_from_handle(processor_handle_dst, &dst_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    auto rstatus = rsmi_minmax_bandwidth_get(src_device->get_gpu_id(), dst_device->get_gpu_id(),
                min_bandwidth, max_bandwidth);
    return amd::smi::rsmi_to_amdsmi_status(rstatus);
}

amdsmi_status_t
amdsmi_topo_get_link_type(amdsmi_processor_handle processor_handle_src, amdsmi_processor_handle processor_handle_dst,
                        uint64_t *hops, AMDSMI_IO_LINK_TYPE *type) {
    AMDSMI_CHECK_INIT();

    amd::smi::AMDSmiGPUDevice* src_device = nullptr;
    amd::smi::AMDSmiGPUDevice* dst_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle_src, &src_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    r = get_gpu_device_from_handle(processor_handle_dst, &dst_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    auto rstatus = rsmi_topo_get_link_type(src_device->get_gpu_id(), dst_device->get_gpu_id(),
                hops, reinterpret_cast<RSMI_IO_LINK_TYPE*>(type));
    return amd::smi::rsmi_to_amdsmi_status(rstatus);
}

amdsmi_status_t
amdsmi_is_P2P_accessible(amdsmi_processor_handle processor_handle_src,
                amdsmi_processor_handle processor_handle_dst,
                       bool *accessible) {
    AMDSMI_CHECK_INIT();

    amd::smi::AMDSmiGPUDevice* src_device = nullptr;
    amd::smi::AMDSmiGPUDevice* dst_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle_src, &src_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    r = get_gpu_device_from_handle(processor_handle_dst, &dst_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    auto rstatus = rsmi_is_P2P_accessible(src_device->get_gpu_id(), dst_device->get_gpu_id(),
                accessible);
    return amd::smi::rsmi_to_amdsmi_status(rstatus);
}

// TODO(bliu) : other xgmi related information
amdsmi_status_t
amdsmi_get_xgmi_info(amdsmi_processor_handle processor_handle, amdsmi_xgmi_info_t *info) {
    AMDSMI_CHECK_INIT();

    if (info == nullptr)
        return AMDSMI_STATUS_INVAL;
    return rsmi_wrapper(rsmi_dev_xgmi_hive_id_get, processor_handle,
                    &(info->xgmi_hive_id));
}

amdsmi_status_t
amdsmi_dev_xgmi_error_status(amdsmi_processor_handle processor_handle, amdsmi_xgmi_status_t *status) {
    return rsmi_wrapper(rsmi_dev_xgmi_error_status, processor_handle,
                    reinterpret_cast<rsmi_xgmi_status_t*>(status));
}

amdsmi_status_t
amdsmi_dev_reset_xgmi_error(amdsmi_processor_handle processor_handle) {
    return rsmi_wrapper(rsmi_dev_xgmi_error_reset, processor_handle);
}

amdsmi_status_t
amdsmi_dev_open_supported_func_iterator(amdsmi_processor_handle processor_handle,
                                amdsmi_func_id_iter_handle_t *handle) {
    AMDSMI_CHECK_INIT();

    if (handle == nullptr)
        return AMDSMI_STATUS_INVAL;
    return rsmi_wrapper(rsmi_dev_supported_func_iterator_open, processor_handle,
                reinterpret_cast<rsmi_func_id_iter_handle_t*>(handle));
}

amdsmi_status_t
amdsmi_dev_open_supported_variant_iterator(amdsmi_func_id_iter_handle_t obj_h,
                                    amdsmi_func_id_iter_handle_t *var_iter) {
    AMDSMI_CHECK_INIT();

    if (var_iter == nullptr)
        return AMDSMI_STATUS_INVAL;
    auto r = rsmi_dev_supported_variant_iterator_open(
            reinterpret_cast<rsmi_func_id_iter_handle_t>(obj_h),
            reinterpret_cast<rsmi_func_id_iter_handle_t*>(var_iter));
    return amd::smi::rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
amdsmi_next_func_iter(amdsmi_func_id_iter_handle_t handle) {
    AMDSMI_CHECK_INIT();

    auto r = rsmi_func_iter_next(
            reinterpret_cast<rsmi_func_id_iter_handle_t>(handle));
    return amd::smi::rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
amdsmi_dev_close_supported_func_iterator(amdsmi_func_id_iter_handle_t *handle) {
    AMDSMI_CHECK_INIT();

    if (handle == nullptr)
        return AMDSMI_STATUS_INVAL;
    auto r = rsmi_dev_supported_func_iterator_close(
        reinterpret_cast<rsmi_func_id_iter_handle_t*>(handle));
    return amd::smi::rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
amdsmi_get_func_iter_value(amdsmi_func_id_iter_handle_t handle,
                            amdsmi_func_id_value_t *value) {

    AMDSMI_CHECK_INIT();

    if (value == nullptr)
        return AMDSMI_STATUS_INVAL;

    static const std::map<std::string, const char*> rsmi_2_amdsmi = {
        {"rsmi_dev_vram_vendor_get", "amdsmi_get_gpu_vram_vendor"},
        {"rsmi_dev_id_get", "amdsmi_get_gpu_id"},
        {"rsmi_dev_vendor_id_get", "amdsmi_get_gpu_asic_info"},
        {"rsmi_dev_name_get", "amdsmi_get_gpu_board_info"},
        {"rsmi_dev_sku_get", "amdsmi_get_gpu_board_info"},
        {"rsmi_dev_brand_get", "amdsmi_get_gpu_asic_info"},
        {"rsmi_dev_vendor_name_get", "amdsmi_get_gpu_vendor_name"},
        {"rsmi_dev_serial_number_get", "amdsmi_get_gpu_asic_info"},
        {"rsmi_dev_subsystem_id_get", "amdsmi_get_gpu_subsystem_id"},
        {"rsmi_dev_subsystem_name_get", "amdsmi_get_gpu_subsystem_name"},
        {"rsmi_dev_drm_render_minor_get", "amdsmi_get_gpu_drm_render_minor"},
        {"rsmi_dev_subsystem_vendor_id_get", "amdsmi_get_gpu_asic_info"},
        {"rsmi_dev_unique_id_get", "amdsmi_get_gpu_board_info"},
        {"rsmi_dev_pci_bandwidth_get", "amdsmi_get_gpu_pci_bandwidth"},
        {"rsmi_dev_pci_id_get", "amdsmi_get_gpu_pci_id"},
        {"rsmi_dev_pci_throughput_get", "amdsmi_get_gpu_pci_throughput"},
        {"rsmi_dev_pci_replay_counter_get", " amdsmi_get_gpu_pci_replay_counter"},
        {"rsmi_dev_pci_bandwidth_set", " amdsmi_set_gpu_pci_bandwidth"},
        {"rsmi_dev_power_profile_set", " amdsmi_set_gpu_power_profile"},
        {"rsmi_dev_memory_busy_percent_get", "amdsmi_get_gpu_memory_busy_percent"},
        {"rsmi_dev_busy_percent_get", "amdsmi_get_busy_percent"},
        {"rsmi_dev_memory_reserved_pages_get", "amdsmi_get_gpu_memory_reserved_pages"},
        {"rsmi_dev_overdrive_level_get", "amdsmi_dev_get_overdrive_level"},
        {"rsmi_dev_power_profile_presets_get", " amdsmi_get_gpu_power_profile_presets"},
        {"rsmi_dev_perf_level_set", " amdsmi_set_gpu_perf_level"},
        {"rsmi_dev_perf_level_set_v1", " amdsmi_set_gpu_perf_level_v1"},
        {"rsmi_dev_perf_level_get", "amdsmi_get_gpu_perf_level"},
        {"rsmi_perf_determinism_mode_set", "amdsmi_set_gpu_perf_determinism_mode"},
        {"rsmi_dev_overdrive_level_set", " amdsmi_dev_set_overdrive_level"},
        {"rsmi_dev_vbios_version_get", "amdsmi_get_gpu_vbios_info"},
        {"rsmi_dev_od_volt_info_get", " amdsmi_dev_get_od_volt_info"},
        {"rsmi_dev_od_volt_info_set", " amdsmi_dev_set_od_volt_info"},
        {"rsmi_dev_od_volt_curve_regions_get", " amdsmi_dev_get_od_volt_curve_regions"},
        {"rsmi_dev_ecc_enabled_get", " amdsmi_dev_get_gpu_ecc_enabled"},
        {"rsmi_dev_ecc_status_get", " amdsmi_dev_get_gpu_ecc_status"},
        {"rsmi_dev_counter_group_supported", "amdsmi_dev_counter_group_supported"},
        {"rsmi_dev_counter_create", "amdsmi_dev_create_counter"},
        {"rsmi_dev_xgmi_error_status", "amdsmi_dev_xgmi_error_status"},
        {"rsmi_dev_xgmi_error_reset", "amdsmi_dev_reset_xgmi_error"},
        {"rsmi_dev_memory_reserved_pages_get", "amdsmi_get_gpu_memory_reserved_pages"},
        {"rsmi_topo_numa_affinity_get", "amdsmi_get_gpu_topo_numa_affinity"},
        {"rsmi_dev_gpu_metrics_info_get", " amdsmi_get_gpu_metrics_info"},
        {"rsmi_dev_gpu_reset", "amdsmi_reset_gpu"},
        {"rsmi_dev_memory_total_get", "amdsmi_get_gpu_memory_total"},
        {"rsmi_dev_memory_usage_get", "amdsmi_get_gpu_memory_usage"},
        {"rsmi_dev_gpu_clk_freq_get", " amdsmi_get_clk_freq"},
        {"rsmi_dev_gpu_clk_freq_set", " amdsmi_set_clk_freq"},
        {"rsmi_dev_firmware_version_get", "amdsmi_get_fw_info"},
        {"rsmi_dev_ecc_count_get", " amdsmi_dev_get_gpu_ecc_count"},
        {"rsmi_counter_available_counters_get", " amdsmi_counter_get_available_counters"},
        {"rsmi_dev_power_ave_get", "amdsmi_get_power_ave"},
        {"rsmi_dev_power_cap_get", "amdsmi_get_power_cap_info"},
        {"rsmi_dev_power_cap_default_get", "amdsmi_get_power_cap_info"},
        {"rsmi_dev_power_cap_range_get", "amdsmi_get_power_cap_info"},
        {"rsmi_dev_power_cap_set", " amdsmi_set_power_cap"},
        {"rsmi_dev_fan_rpms_get", "amdsmi_get_gpu_fan_rpms"},
        {"rsmi_dev_fan_speed_get", "amdsmi_get_gpu_fan_speed"},
        {"rsmi_dev_fan_speed_max_get", "amdsmi_get_gpu_fan_speed_max"},
        {"rsmi_dev_temp_metric_get", " amdsmi_get_temp_metric"},
        {"rsmi_dev_fan_reset", "amdsmi_reset_gpu_fan"},
        {"rsmi_dev_fan_speed_set", "amdsmi_set_gpu_fan_speed"},
        {"rsmi_dev_volt_metric_get", " amdsmi_get_gpu_volt_metric"}
    };

    auto rocm_func_handle =
        reinterpret_cast<rsmi_func_id_iter_handle_t>(handle);

    auto r = rsmi_func_iter_value_get(
        rocm_func_handle,
        reinterpret_cast<rsmi_func_id_value_t*>(value));

    if ( r != RSMI_STATUS_SUCCESS )
        return amd::smi::rsmi_to_amdsmi_status(r);

    // Only change the function name, FUNC_ITER == 0
    if (rocm_func_handle->id_type != 0)
        return amd::smi::rsmi_to_amdsmi_status(r);

    auto iter = rsmi_2_amdsmi.find(value->name);
    if (iter != rsmi_2_amdsmi.end()) {
        value->name = (*iter).second;
    }

    return amd::smi::rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
amdsmi_get_gpu_compute_process_info(amdsmi_process_info_t *procs, uint32_t *num_items) {
    AMDSMI_CHECK_INIT();

    if (num_items == nullptr)
        return AMDSMI_STATUS_INVAL;
    auto r = rsmi_compute_process_info_get(
        reinterpret_cast<rsmi_process_info_t*>(procs),
        num_items);
    return amd::smi::rsmi_to_amdsmi_status(r);
}

amdsmi_status_t amdsmi_get_gpu_compute_process_info_by_pid(uint32_t pid,
        amdsmi_process_info_t *proc) {
    AMDSMI_CHECK_INIT();

    if (proc == nullptr)
        return AMDSMI_STATUS_INVAL;
    auto r = rsmi_compute_process_info_by_pid_get(pid,
        reinterpret_cast<rsmi_process_info_t*>(proc));
    return amd::smi::rsmi_to_amdsmi_status(r);
}

amdsmi_status_t
amdsmi_get_gpu_compute_process_gpus(uint32_t pid, uint32_t *dv_indices,
                                                       uint32_t *num_devices) {
    AMDSMI_CHECK_INIT();

    if (dv_indices == nullptr || num_devices == nullptr)
        return AMDSMI_STATUS_INVAL;
    auto r = rsmi_compute_process_gpus_get(pid, dv_indices, num_devices);
    return amd::smi::rsmi_to_amdsmi_status(r);
}

amdsmi_status_t  amdsmi_dev_get_gpu_ecc_count(amdsmi_processor_handle processor_handle,
                        amdsmi_gpu_block_t block, amdsmi_error_count_t *ec) {
    AMDSMI_CHECK_INIT();

    if (ec == nullptr)
        return AMDSMI_STATUS_INVAL;
    return rsmi_wrapper(rsmi_dev_ecc_count_get, processor_handle,
                    static_cast<rsmi_gpu_block_t>(block),
                    reinterpret_cast<rsmi_error_count_t*>(ec));
}
amdsmi_status_t  amdsmi_dev_get_gpu_ecc_enabled(amdsmi_processor_handle processor_handle,
                                                    uint64_t *enabled_blocks) {
    AMDSMI_CHECK_INIT();

    if (enabled_blocks == nullptr)
        return AMDSMI_STATUS_INVAL;
    return rsmi_wrapper(rsmi_dev_ecc_enabled_get, processor_handle,
                    enabled_blocks);
}
amdsmi_status_t  amdsmi_dev_get_gpu_ecc_status(amdsmi_processor_handle processor_handle,
                                amdsmi_gpu_block_t block,
                                amdsmi_ras_err_state_t *state) {
    AMDSMI_CHECK_INIT();

    if (state == nullptr)
        return AMDSMI_STATUS_INVAL;
    return rsmi_wrapper(rsmi_dev_ecc_status_get, processor_handle,
                    static_cast<rsmi_gpu_block_t>(block),
                    reinterpret_cast<rsmi_ras_err_state_t*>(state));
}

amdsmi_status_t
amdsmi_get_busy_percent(amdsmi_processor_handle processor_handle,
                            uint32_t *busy_percent) {
    AMDSMI_CHECK_INIT();

    if (busy_percent == nullptr)
        return AMDSMI_STATUS_INVAL;
    return rsmi_wrapper(rsmi_dev_busy_percent_get, processor_handle,
                    busy_percent);
}
amdsmi_status_t  amdsmi_get_gpu_metrics_info(
        amdsmi_processor_handle processor_handle,
        amdsmi_gpu_metrics_t *pgpu_metrics) {
    AMDSMI_CHECK_INIT();

    if (pgpu_metrics == nullptr)
        return AMDSMI_STATUS_INVAL;
    return rsmi_wrapper(rsmi_dev_gpu_metrics_info_get, processor_handle,
                    reinterpret_cast<rsmi_gpu_metrics_t*>(pgpu_metrics));
}

amdsmi_status_t
amdsmi_get_power_cap_info(amdsmi_processor_handle processor_handle,
                    uint32_t sensor_ind,
                    amdsmi_power_cap_info_t *info) {
    AMDSMI_CHECK_INIT();

    if (info == nullptr)
        return AMDSMI_STATUS_INVAL;

    bool set_ret_success = false;
    amd::smi::AMDSmiGPUDevice* gpudevice = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpudevice);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    amdsmi_status_t status;

    status = get_gpu_device_from_handle(processor_handle, &gpudevice);
    if (status != AMDSMI_STATUS_SUCCESS)
    {
        return status;
    }
    // Ignore errors to get as much as possible info.
    memset(info, 0, sizeof(amdsmi_power_cap_info_t));

    if (gpudevice->check_if_drm_is_supported()) {
        // Get power_cap and dpm
        int power_cap = 0;
        int dpm = 0;
        status = smi_amdgpu_get_power_cap(gpudevice, &power_cap);
        if ((status == AMDSMI_STATUS_SUCCESS) && !set_ret_success)
            set_ret_success = true;

        info->power_cap = power_cap;
        status = smi_amdgpu_get_ranges(gpudevice, CLK_TYPE_GFX,
                NULL, NULL, &dpm);
        if ((status == AMDSMI_STATUS_SUCCESS) && !set_ret_success)
            set_ret_success = true;
        info->dpm_cap = dpm;
    }
    else {
        status = rsmi_wrapper(rsmi_dev_power_cap_get, processor_handle,
                    sensor_ind, &(info->power_cap));
        if ((status == AMDSMI_STATUS_SUCCESS) && !set_ret_success)
            set_ret_success = true;
    }

    // Get other information from rocm-smi
    status = rsmi_wrapper(rsmi_dev_power_cap_default_get, processor_handle,
                        &(info->default_power_cap));

    if ((status == AMDSMI_STATUS_SUCCESS) && !set_ret_success)
        set_ret_success = true;

    status = rsmi_wrapper(rsmi_dev_power_cap_range_get, processor_handle, sensor_ind,
                        &(info->max_power_cap), &(info->min_power_cap));

    if ((status == AMDSMI_STATUS_SUCCESS) && !set_ret_success)
        set_ret_success = true;

    return set_ret_success ? AMDSMI_STATUS_SUCCESS : AMDSMI_STATUS_NOT_SUPPORTED;
}

amdsmi_status_t
 amdsmi_set_power_cap(amdsmi_processor_handle processor_handle,
            uint32_t sensor_ind, uint64_t cap) {
    return rsmi_wrapper(rsmi_dev_power_cap_set, processor_handle,
            sensor_ind, cap);
}

amdsmi_status_t
amdsmi_get_power_ave(amdsmi_processor_handle processor_handle,
                    uint32_t sensor_ind, uint64_t *power) {
    AMDSMI_CHECK_INIT();

    if (power == nullptr)
        return AMDSMI_STATUS_INVAL;
    return rsmi_wrapper(rsmi_dev_power_ave_get, processor_handle,
            sensor_ind, power);
}
amdsmi_status_t
 amdsmi_get_gpu_power_profile_presets(amdsmi_processor_handle processor_handle,
                        uint32_t sensor_ind,
                        amdsmi_power_profile_status_t *status) {
    AMDSMI_CHECK_INIT();

    if (status == nullptr)
        return AMDSMI_STATUS_INVAL;
    return rsmi_wrapper(rsmi_dev_power_profile_presets_get, processor_handle,
                    sensor_ind,
                    reinterpret_cast<rsmi_power_profile_status_t*>(status));
}

amdsmi_status_t amdsmi_set_gpu_perf_determinism_mode(
            amdsmi_processor_handle processor_handle, uint64_t clkvalue) {
    return rsmi_wrapper(rsmi_perf_determinism_mode_set, processor_handle,
                clkvalue);
}

amdsmi_status_t
 amdsmi_set_gpu_power_profile(amdsmi_processor_handle processor_handle,
        uint32_t reserved, amdsmi_power_profile_preset_masks_t profile) {
    return rsmi_wrapper(rsmi_dev_power_profile_set, processor_handle,
                reserved,
                static_cast<rsmi_power_profile_preset_masks_t>(profile));
}
amdsmi_status_t amdsmi_get_gpu_perf_level(amdsmi_processor_handle processor_handle,
                                        amdsmi_dev_perf_level_t *perf) {
    AMDSMI_CHECK_INIT();

    if (perf == nullptr)
        return AMDSMI_STATUS_INVAL;
    return rsmi_wrapper(rsmi_dev_perf_level_get, processor_handle,
                    reinterpret_cast<rsmi_dev_perf_level_t*>(perf));
}
amdsmi_status_t
 amdsmi_set_gpu_perf_level(amdsmi_processor_handle processor_handle,
                amdsmi_dev_perf_level_t perf_lvl) {
    return rsmi_wrapper(rsmi_dev_perf_level_set, processor_handle,
                    static_cast<rsmi_dev_perf_level_t>(perf_lvl));
}

amdsmi_status_t
 amdsmi_set_gpu_perf_level_v1(amdsmi_processor_handle processor_handle,
                amdsmi_dev_perf_level_t perf_lvl) {
    return rsmi_wrapper(rsmi_dev_perf_level_set_v1, processor_handle,
                    static_cast<rsmi_dev_perf_level_t>(perf_lvl));
}

amdsmi_status_t  amdsmi_set_gpu_pci_bandwidth(amdsmi_processor_handle processor_handle,
                uint64_t bw_bitmask) {
    return rsmi_wrapper(rsmi_dev_pci_bandwidth_set, processor_handle,
                    bw_bitmask);
}

amdsmi_status_t amdsmi_get_gpu_pci_bandwidth(amdsmi_processor_handle processor_handle,
            amdsmi_pcie_bandwidth_t *bandwidth) {
    return rsmi_wrapper(rsmi_dev_pci_bandwidth_get, processor_handle,
                    reinterpret_cast<rsmi_pcie_bandwidth_t*>(bandwidth));
}

// TODO(bliu): other frequencies in amdsmi_clk_type_t
amdsmi_status_t  amdsmi_get_clk_freq(amdsmi_processor_handle processor_handle,
                        amdsmi_clk_type_t clk_type, amdsmi_frequencies_t *f) {
    AMDSMI_CHECK_INIT();

    if (f == nullptr)
        return AMDSMI_STATUS_INVAL;

    // Get from gpu_metrics
    if (clk_type == CLK_TYPE_VCLK0 ||
        clk_type == CLK_TYPE_VCLK1 ||
        clk_type == CLK_TYPE_DCLK0 ||
        clk_type == CLK_TYPE_DCLK1 ) {
        amdsmi_gpu_metrics_t metric_info;
        auto r_status =  amdsmi_get_gpu_metrics_info(
                processor_handle, &metric_info);
        if (r_status != AMDSMI_STATUS_SUCCESS)
            return r_status;

        f->num_supported = 1;
        if (clk_type == CLK_TYPE_VCLK0) {
            f->current = metric_info.current_vclk0;
            f->frequency[0] = metric_info.average_vclk0_frequency;
        }
        if (clk_type == CLK_TYPE_VCLK1) {
            f->current = metric_info.current_vclk1;
            f->frequency[0] = metric_info.average_vclk1_frequency;
        }
        if (clk_type == CLK_TYPE_DCLK0) {
            f->current = metric_info.current_dclk0;
            f->frequency[0] = metric_info.average_dclk0_frequency;
        }
        if (clk_type == CLK_TYPE_DCLK1) {
            f->current = metric_info.current_dclk1;
            f->frequency[0] = metric_info.average_dclk1_frequency;
        }

        return r_status;
    }

    return rsmi_wrapper(rsmi_dev_gpu_clk_freq_get, processor_handle,
                    static_cast<rsmi_clk_type_t>(clk_type),
                    reinterpret_cast<rsmi_frequencies_t*>(f));
}

amdsmi_status_t  amdsmi_set_clk_freq(amdsmi_processor_handle processor_handle,
                         amdsmi_clk_type_t clk_type, uint64_t freq_bitmask) {
    AMDSMI_CHECK_INIT();

    // Not support the clock type read from gpu_metrics
    if (clk_type == CLK_TYPE_VCLK0 ||
        clk_type == CLK_TYPE_VCLK1 ||
        clk_type == CLK_TYPE_DCLK0 ||
        clk_type == CLK_TYPE_DCLK1 ) {
            return AMDSMI_STATUS_NOT_SUPPORTED;
    }

    return rsmi_wrapper(rsmi_dev_gpu_clk_freq_set, processor_handle,
                    static_cast<rsmi_clk_type_t>(clk_type), freq_bitmask);
}
amdsmi_status_t
amdsmi_get_gpu_memory_reserved_pages(amdsmi_processor_handle processor_handle,
                                    uint32_t *num_pages,
                                    amdsmi_retired_page_record_t *records) {
    return rsmi_wrapper(rsmi_dev_memory_reserved_pages_get, processor_handle,
                    num_pages,
                    reinterpret_cast<rsmi_retired_page_record_t*>(records));
}
amdsmi_status_t amdsmi_get_gpu_memory_total(amdsmi_processor_handle processor_handle,
                amdsmi_memory_type_t mem_type, uint64_t *total) {
    return rsmi_wrapper(rsmi_dev_memory_total_get, processor_handle,
                    static_cast<rsmi_memory_type_t>(mem_type), total);
}
amdsmi_status_t amdsmi_get_gpu_memory_usage(amdsmi_processor_handle processor_handle,
            amdsmi_memory_type_t mem_type, uint64_t *used) {
    return rsmi_wrapper(rsmi_dev_memory_usage_get, processor_handle,
                    static_cast<rsmi_memory_type_t>(mem_type), used);
}

amdsmi_status_t amdsmi_dev_get_overdrive_level(
            amdsmi_processor_handle processor_handle,
            uint32_t *od) {
    return rsmi_wrapper(rsmi_dev_overdrive_level_get, processor_handle, od);
}

amdsmi_status_t  amdsmi_dev_set_overdrive_level(
            amdsmi_processor_handle processor_handle, uint32_t od) {
    return rsmi_wrapper(rsmi_dev_overdrive_level_set, processor_handle, od);
}
amdsmi_status_t  amdsmi_get_gpu_pci_replay_counter(
            amdsmi_processor_handle processor_handle, uint64_t *counter) {
    return rsmi_wrapper(rsmi_dev_pci_replay_counter_get,
                processor_handle, counter);
}
amdsmi_status_t amdsmi_get_gpu_pci_throughput(
        amdsmi_processor_handle processor_handle,
        uint64_t *sent, uint64_t *received, uint64_t *max_pkt_sz) {
    return rsmi_wrapper(rsmi_dev_pci_throughput_get, processor_handle,
            sent, received, max_pkt_sz);
}

amdsmi_status_t  amdsmi_dev_get_od_volt_info(amdsmi_processor_handle processor_handle,
                                            amdsmi_od_volt_freq_data_t *odv) {
    return rsmi_wrapper(rsmi_dev_od_volt_info_get, processor_handle,
                    reinterpret_cast<rsmi_od_volt_freq_data_t*>(odv));
}

amdsmi_status_t  amdsmi_dev_get_od_volt_curve_regions(
                    amdsmi_processor_handle processor_handle,
                    uint32_t *num_regions, amdsmi_freq_volt_region_t *buffer) {
    return rsmi_wrapper(rsmi_dev_od_volt_curve_regions_get, processor_handle,
        num_regions, reinterpret_cast<rsmi_freq_volt_region_t* >(buffer));
}

amdsmi_status_t  amdsmi_get_gpu_volt_metric(amdsmi_processor_handle processor_handle,
                            amdsmi_voltage_type_t sensor_type,
                            amdsmi_voltage_metric_t metric, int64_t *voltage) {
    return rsmi_wrapper(rsmi_dev_volt_metric_get, processor_handle,
                static_cast<rsmi_voltage_type_t>(sensor_type),
                static_cast<rsmi_voltage_metric_t>(metric), voltage);
}

amdsmi_status_t  amdsmi_dev_set_od_clk_info(amdsmi_processor_handle processor_handle,
                                        amdsmi_freq_ind_t level,
                                       uint64_t clkvalue,
                                       amdsmi_clk_type_t clkType) {
    return rsmi_wrapper(rsmi_dev_od_clk_info_set, processor_handle,
                static_cast<rsmi_freq_ind_t>(level), clkvalue,
                static_cast<rsmi_clk_type_t>(clkType));
}

amdsmi_status_t  amdsmi_dev_set_od_volt_info(amdsmi_processor_handle processor_handle,
                    uint32_t vpoint, uint64_t clkvalue, uint64_t voltvalue) {
    return rsmi_wrapper(rsmi_dev_od_volt_info_set, processor_handle,
                vpoint, clkvalue, voltvalue);
}

amdsmi_status_t amdsmi_set_gpu_clk_range(amdsmi_processor_handle processor_handle,
                                    uint64_t minclkvalue,
                                    uint64_t maxclkvalue,
                                    amdsmi_clk_type_t clkType) {
    return rsmi_wrapper(rsmi_dev_clk_range_set, processor_handle,
                minclkvalue, maxclkvalue,
                static_cast<rsmi_clk_type_t>(clkType));
}

amdsmi_status_t  amdsmi_dev_set_overdrive_level_v1(
                    amdsmi_processor_handle processor_handle,
                    uint32_t od) {
    return rsmi_wrapper(rsmi_dev_overdrive_level_set_v1, processor_handle,
                od);
}

amdsmi_status_t amdsmi_reset_gpu(amdsmi_processor_handle processor_handle) {
    return rsmi_wrapper(rsmi_dev_gpu_reset, processor_handle);
}

amdsmi_status_t amdsmi_get_utilization_count(amdsmi_processor_handle processor_handle,
                amdsmi_utilization_counter_t utilization_counters[],
                uint32_t count,
                uint64_t *timestamp) {
    return rsmi_wrapper(rsmi_utilization_count_get, processor_handle,
            reinterpret_cast<rsmi_utilization_counter_t*>(utilization_counters),
            count, timestamp);
}
amdsmi_status_t amdsmi_get_gpu_memory_busy_percent(
            amdsmi_processor_handle processor_handle,
            uint32_t *busy_percent) {
    return rsmi_wrapper(rsmi_dev_memory_busy_percent_get, processor_handle,
            busy_percent);
}

amdsmi_status_t amdsmi_get_energy_count(amdsmi_processor_handle processor_handle,
            uint64_t *power, float *counter_resolution, uint64_t *timestamp) {
    return rsmi_wrapper(rsmi_dev_energy_count_get, processor_handle,
            power, counter_resolution, timestamp);
}

amdsmi_status_t amdsmi_get_gpu_drm_render_minor(
        amdsmi_processor_handle processor_handle, uint32_t *minor) {
    return rsmi_wrapper(rsmi_dev_drm_render_minor_get, processor_handle,
            minor);
}

amdsmi_status_t amdsmi_get_gpu_pci_id(
        amdsmi_processor_handle processor_handle, uint64_t *bdfid) {
    return rsmi_wrapper(rsmi_dev_pci_id_get, processor_handle,
            bdfid);
}

amdsmi_status_t amdsmi_get_gpu_topo_numa_affinity(
    amdsmi_processor_handle processor_handle, uint32_t *numa_node) {
    return rsmi_wrapper(rsmi_topo_numa_affinity_get, processor_handle,
            numa_node);
}

amdsmi_status_t amdsmi_get_version(amdsmi_version_t *version) {
    AMDSMI_CHECK_INIT();

    if (version == nullptr)
        return AMDSMI_STATUS_INVAL;

    auto rstatus = rsmi_version_get(
        reinterpret_cast<rsmi_version_t*>(version));
    return amd::smi::rsmi_to_amdsmi_status(rstatus);
}

amdsmi_status_t amdsmi_get_version_str(amdsmi_sw_component_t component,
                    char *ver_str,
                    uint32_t len) {
    AMDSMI_CHECK_INIT();

    if (ver_str == nullptr)
        return AMDSMI_STATUS_INVAL;

    auto status = rsmi_version_str_get(
        static_cast<rsmi_sw_component_t>(component), ver_str, len);
    return amd::smi::rsmi_to_amdsmi_status(status);
}

amdsmi_status_t
amdsmi_get_gpu_vbios_info(amdsmi_processor_handle processor_handle, amdsmi_vbios_info_t *info) {
    AMDSMI_CHECK_INIT();

    if (info == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    struct drm_amdgpu_info_vbios vbios = {};
    amdsmi_status_t status;

    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;


    if (gpu_device->check_if_drm_is_supported()) {
        status = gpu_device->amdgpu_query_vbios(&vbios);
        if (status != AMDSMI_STATUS_SUCCESS) {
            return status;
        }
        strncpy(info->name, (char *) vbios.name, AMDSMI_MAX_STRING_LENGTH);
        strncpy(info->build_date, (char *) vbios.date, AMDSMI_MAX_DATE_LENGTH);
        strncpy(info->part_number, (char *) vbios.vbios_pn, AMDSMI_MAX_STRING_LENGTH);
        strncpy(info->vbios_version_string, (char *) vbios.vbios_ver_str, AMDSMI_NORMAL_STRING_LENGTH);
        info->vbios_version = vbios.version;
    }
    else {
        // get vbios version string from rocm_smi
        char vbios_version[AMDSMI_NORMAL_STRING_LENGTH];
        status = rsmi_wrapper(rsmi_dev_vbios_version_get, processor_handle,
                vbios_version,
                AMDSMI_NORMAL_STRING_LENGTH);

        // ignore the errors so that it can populate as many fields as possible.
        if (status == AMDSMI_STATUS_SUCCESS) {
            strncpy(info->vbios_version_string,
                vbios_version, AMDSMI_NORMAL_STRING_LENGTH);
        }
    }

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t
amdsmi_get_gpu_activity(amdsmi_processor_handle processor_handle, amdsmi_engine_usage_t *info) {
    AMDSMI_CHECK_INIT();

    if (info == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    amdsmi_gpu_metrics_t metrics = {};
    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    amdsmi_status_t status;
    status =  amdsmi_get_gpu_metrics_info(processor_handle, &metrics);
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }
    info->gfx_activity = metrics.average_gfx_activity;
    info->mm_activity[0] = metrics.average_mm_activity;
    info->umc_activity = metrics.average_umc_activity;

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t
amdsmi_get_clock_measure(amdsmi_processor_handle processor_handle, amdsmi_clk_type_t clk_type, amdsmi_clk_measure_t *info) {
    AMDSMI_CHECK_INIT();

    if (info == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    if (clk_type > CLK_TYPE__MAX) {
        return AMDSMI_STATUS_INVAL;
    }

    amdsmi_gpu_metrics_t metrics = {};
    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;
    amdsmi_status_t status;

    status =  amdsmi_get_gpu_metrics_info(processor_handle, &metrics);
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }
    int max_freq;
    status = smi_amdgpu_get_ranges(gpu_device, clk_type,
        &max_freq, NULL, NULL);
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }
    info->max_clk = max_freq;

    switch (clk_type) {
    case CLK_TYPE_GFX:
        info->avg_clk = metrics.average_gfxclk_frequency;
        info->cur_clk = metrics.current_gfxclk;
        break;
    case CLK_TYPE_MEM:
        info->avg_clk = metrics.average_uclk_frequency;
        info->cur_clk = metrics.current_uclk;
        break;
    case CLK_TYPE_VCLK0:
        info->avg_clk = metrics.average_vclk0_frequency;
        info->cur_clk = metrics.current_vclk0;
        break;
    case CLK_TYPE_VCLK1:
        info->avg_clk = metrics.average_vclk1_frequency;
        info->cur_clk = metrics.current_vclk1;
        break;
    default:
        return AMDSMI_STATUS_INVAL;
    }

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t
amdsmi_get_gpu_ras_block_features_enabled(amdsmi_processor_handle processor_handle, amdsmi_gpu_block_t block, amdsmi_ras_err_state_t *state) {
    AMDSMI_CHECK_INIT();

    if (state == nullptr || block > AMDSMI_GPU_BLOCK_LAST) {
        return AMDSMI_STATUS_INVAL;
    }

    uint64_t features_mask = 0;
    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    amdsmi_status_t status;
    status = smi_amdgpu_get_enabled_blocks(gpu_device, &features_mask);
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }
    *state = (features_mask & block) ? AMDSMI_RAS_ERR_STATE_ENABLED : AMDSMI_RAS_ERR_STATE_DISABLED;

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t
amdsmi_get_gpu_bad_page_info(amdsmi_processor_handle processor_handle, uint32_t *num_pages, amdsmi_retired_page_record_t *info) {
    AMDSMI_CHECK_INIT();

    if (num_pages == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    amdsmi_status_t status;
    if (gpu_device->check_if_drm_is_supported()){
        status = smi_amdgpu_get_bad_page_info(gpu_device, num_pages, info);
        if (status != AMDSMI_STATUS_SUCCESS) {
            return status;
        }
    }
    else {
        // rocm
    }

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t
amdsmi_get_gpu_ecc_error_count(amdsmi_processor_handle processor_handle, amdsmi_error_count_t *ec) {
    AMDSMI_CHECK_INIT();

    if (ec == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    amdsmi_status_t status;
    if (gpu_device->check_if_drm_is_supported()){
        status = smi_amdgpu_get_ecc_error_count(gpu_device, ec);
        if (status != AMDSMI_STATUS_SUCCESS) {
            return status;
        }
    }
    else {
        // rocm
    }

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t
amdsmi_get_gpu_process_list(amdsmi_processor_handle processor_handle, amdsmi_process_handle *list, uint32_t *max_processes) {
    AMDSMI_CHECK_INIT();

    if (max_processes == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    std::vector<long int> pids;
    uint32_t i = 0;
    uint64_t size = 0;
    amdsmi_status_t status;
    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    if (gpu_device->check_if_drm_is_supported()){
        amdsmi_bdf_t bdf = gpu_device->get_bdf();
        status = gpuvsmi_get_pids(bdf, pids, &size);
        if (status != AMDSMI_STATUS_SUCCESS) {
            return status;
        }
        if (*max_processes == 0 || (pids.size() == 0)) {
            *max_processes = (uint32_t)pids.size();
            return AMDSMI_STATUS_SUCCESS;
        }
        if (!list) {
            return AMDSMI_STATUS_INVAL;
        }
        if (*max_processes < pids.size()) {
            return AMDSMI_STATUS_OUT_OF_RESOURCES;
        }
        for (auto &pid : pids) {
            if (i >= *max_processes) {
                break;
            }
            list[i++] = (uint32_t)pid;
        }
        *max_processes = (uint32_t)pids.size();
    }
    else {
        // rocm
    }

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t
amdsmi_get_gpu_process_info(amdsmi_processor_handle processor_handle, amdsmi_process_handle process, amdsmi_proc_info_t *info) {
    AMDSMI_CHECK_INIT();

    if (info == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    amdsmi_status_t status;
    if (gpu_device->check_if_drm_is_supported()) {
        status = gpuvsmi_get_pid_info(gpu_device->get_bdf(), process, *info);
        if (status != AMDSMI_STATUS_SUCCESS) return status;
    }
    else {
        // rocm
    }

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t
amdsmi_get_power_measure(amdsmi_processor_handle processor_handle, amdsmi_power_measure_t *info) {
    AMDSMI_CHECK_INIT();

    if (info == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    amdsmi_gpu_metrics_t metrics = {};
    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    amdsmi_status_t status;

    status =  amdsmi_get_gpu_metrics_info(processor_handle, &metrics);
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }

    int64_t voltage_read = 0;

    status =  amdsmi_get_gpu_volt_metric(processor_handle, AMDSMI_VOLT_TYPE_VDDGFX, AMDSMI_VOLT_CURRENT, &voltage_read);
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }

    int power_limit = 0;
    status = smi_amdgpu_get_power_cap(gpu_device, &power_limit);
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }
    info->power_limit = power_limit;

    info->voltage_gfx = voltage_read;

    info->average_socket_power = metrics.average_socket_power;
    info->energy_accumulator = metrics.energy_accumulator;

    return status;
}

amdsmi_status_t
amdsmi_get_gpu_target_frequency_range(amdsmi_processor_handle processor_handle, amdsmi_clk_type_t clk_type, amdsmi_frequency_range_t *range) {
    AMDSMI_CHECK_INIT();

    if (range == nullptr || clk_type > CLK_TYPE__MAX) {
        return AMDSMI_STATUS_INVAL;
    }

    amdsmi_gpu_metrics_t metrics = {};
    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    amdsmi_status_t status;

    int min = 0, max = 0;
    status =  amdsmi_get_gpu_metrics_info(processor_handle, &metrics);
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }
    status = smi_amdgpu_get_ranges(gpu_device, clk_type, &max, &min, nullptr);
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }

    range->supported_freq_range.lower_bound = (long)min;
    range->current_freq_range.lower_bound = (long)min;
    range->supported_freq_range.upper_bound = (long)max;
    max = 0;
    switch (clk_type) {
    case CLK_TYPE_GFX:
        max = metrics.current_gfxclk;
        break;
    case CLK_TYPE_MEM:
        max = metrics.current_uclk;
        break;
    case CLK_TYPE_VCLK0:
        max = metrics.current_vclk0;
        break;
    case CLK_TYPE_VCLK1:
        max = metrics.current_vclk1;
        break;
    default:
        return AMDSMI_STATUS_INVAL;
    }
    range->current_freq_range.upper_bound = (long)max;

    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t
amdsmi_get_gpu_driver_version(amdsmi_processor_handle processor_handle, int *length, char *version) {
    AMDSMI_CHECK_INIT();

    if (length == nullptr || version == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }
    amdsmi_status_t status = AMDSMI_STATUS_SUCCESS;
    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    status = smi_amdgpu_get_driver_version(gpu_device, length, version);

    return status;
}

amdsmi_status_t
amdsmi_get_gpu_device_uuid(amdsmi_processor_handle processor_handle, unsigned int *uuid_length, char *uuid) {
    AMDSMI_CHECK_INIT();

    if (uuid_length == nullptr || uuid == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    amdsmi_status_t status = AMDSMI_STATUS_SUCCESS;
    SMIGPUDEVICE_MUTEX(gpu_device->get_mutex())

    FILE *fp;
    size_t len = AMDSMI_GPU_UUID_SIZE;
    ssize_t nread;
    amdsmi_asic_info_t asic_info = {};
    const uint8_t fcn = 0xff;

    std::string path = "/sys/class/drm/" + gpu_device->get_gpu_path() + "/device/uuid_info";
    status = amdsmi_get_gpu_asic_info(processor_handle, &asic_info);
    if (status != AMDSMI_STATUS_SUCCESS) {
        printf("Getting asic info failed. Return code: %d", status);
        return status;
    }

    fp = fopen(path.c_str(), "rb");
    if (!fp) {
        /* generate random UUID */
        status = amdsmi_uuid_gen(uuid, strtoul(asic_info.asic_serial, nullptr, AMDSMI_NORMAL_STRING_LENGTH), (uint16_t)asic_info.device_id, fcn);
        return status;
    }

    nread = getline(&uuid, &len, fp);
    if (nread <= 0) {
        /* generate random UUID */
        status = amdsmi_uuid_gen(uuid, strtoul(asic_info.asic_serial, nullptr, AMDSMI_NORMAL_STRING_LENGTH), (uint16_t)asic_info.device_id, fcn);
        fclose(fp);
        return status;
    }

    fclose(fp);
    return status;
}

amdsmi_status_t
amdsmi_get_pcie_link_status(amdsmi_processor_handle processor_handle, amdsmi_pcie_info_t *info){
    AMDSMI_CHECK_INIT();

    if (info == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }
    amdsmi_status_t status = AMDSMI_STATUS_SUCCESS;
    amdsmi_gpu_metrics_t metric_info = {};
    status =  amdsmi_get_gpu_metrics_info(
            processor_handle, &metric_info);
    if (status != AMDSMI_STATUS_SUCCESS)
        return status;

    info->pcie_lanes = metric_info.pcie_link_width;
    status = smi_amdgpu_get_pcie_speed_from_pcie_type(metric_info.pcie_link_speed, &info->pcie_speed); // mapping to MT/s

    return status;
}

amdsmi_status_t amdsmi_get_pcie_link_caps(amdsmi_processor_handle processor_handle, amdsmi_pcie_info_t *info) {
    AMDSMI_CHECK_INIT();

    if (info == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    amdsmi_status_t status = AMDSMI_STATUS_SUCCESS;
    amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
    amdsmi_status_t r = get_gpu_device_from_handle(processor_handle, &gpu_device);
    if (r != AMDSMI_STATUS_SUCCESS)
        return r;

    SMIGPUDEVICE_MUTEX(gpu_device->get_mutex())

    char buff[AMDSMI_NORMAL_STRING_LENGTH];
    FILE* fp;
    double pcie_speed = 0;
    unsigned pcie_width = 0;
    amdsmi_asic_info_t asic_info = {};

    memset((void *)info, 0, sizeof(*info));

    std::string path_max_link_width = "/sys/class/drm/" +
        gpu_device->get_gpu_path() + "/device/max_link_width";
    fp = fopen(path_max_link_width.c_str(), "r");
    if (fp) {
        fscanf(fp, "%d", &pcie_width);
        fclose(fp);
    } else {
        printf("Failed to open file: %s \n", path_max_link_width.c_str());
        return AMDSMI_STATUS_API_FAILED;
    }
    info->pcie_lanes = (uint16_t)pcie_width;

    std::string path_max_link_speed = "/sys/class/drm/" +
        gpu_device->get_gpu_path() + "/device/max_link_speed";
    fp = fopen(path_max_link_speed.c_str(), "r");
    if (fp) {
        fscanf(fp, "%lf %s", &pcie_speed, buff);
        fclose(fp);
    } else {
        printf("Failed to open file: %s \n", path_max_link_speed.c_str());
        return AMDSMI_STATUS_API_FAILED;
    }

    status = amdsmi_get_gpu_asic_info(processor_handle, &asic_info);
    if (status != AMDSMI_STATUS_SUCCESS)
        return status;

    if (pcie_speed == 0 && asic_info.device_id == 29538)
        pcie_speed = 16;

    info->pcie_speed = pcie_speed * 1000;

    return status;
}

amdsmi_status_t amdsmi_get_processor_handle_from_bdf(amdsmi_bdf_t bdf,
                amdsmi_processor_handle* processor_handle)
{
    amdsmi_status_t status;
    uint32_t socket_count = 0;

    uint32_t device_count = AMDSMI_MAX_DEVICES;
    amdsmi_processor_handle devs[AMDSMI_MAX_DEVICES];

   AMDSMI_CHECK_INIT();

    if (processor_handle == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }

    status = amdsmi_get_socket_handles(&socket_count, nullptr);
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }

    amdsmi_socket_handle sockets[socket_count];

    status = amdsmi_get_socket_handles(&socket_count, &sockets[0]);
    if (status != AMDSMI_STATUS_SUCCESS) {
        return status;
    }

    for (unsigned int i = 0; i < socket_count; i++) {
        status = amdsmi_get_processor_handles(sockets[i], &device_count, devs);
        if (status != AMDSMI_STATUS_SUCCESS) {
            return status;
        }

        for (uint32_t idx = 0; idx < device_count; idx++) {
            amd::smi::AMDSmiGPUDevice* gpu_device = nullptr;
            status = get_gpu_device_from_handle(devs[idx], &gpu_device);
            if (status != AMDSMI_STATUS_SUCCESS) {
                return status;
            }
            amdsmi_bdf_t found_bdf = gpu_device->get_bdf();
            if (bdf.bus_number == found_bdf.bus_number &&
                bdf.device_number == found_bdf.device_number &&
                bdf.domain_number == found_bdf.domain_number &&
                bdf.function_number == found_bdf.function_number) {
                    *processor_handle = devs[idx];
                    return AMDSMI_STATUS_SUCCESS;
                }
        }
    }

    return AMDSMI_STATUS_API_FAILED;
}

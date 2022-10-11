/* * Copyright (C) 2022 Advanced Micro Devices. All rights reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 * the Software, and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

#ifndef AMD_SMI_INCLUDE_AMD_SMI_UTILS_H_
#define AMD_SMI_INCLUDE_AMD_SMI_UTILS_H_

#include "amd_smi/amd_smi.h"
#include "amd_smi/impl/amd_smi_gpu_device.h"
#include "rocm_smi/rocm_smi_utils.h"


#define SMIGPUDEVICE_MUTEX(MUTEX) \
    amd::smi::pthread_wrap _pw(*(MUTEX)); \
    amd::smi::ScopedPthread _lock(_pw, true); \
    if (_lock.mutex_not_acquired()) { \
      return AMDSMI_STATUS_BUSY; \
    }

amdsmi_status_t smi_amdgpu_find_hwmon_dir(amd::smi::AMDSmiGPUDevice* device, std::string* full_path);
amdsmi_status_t smi_amdgpu_get_board_info(amd::smi::AMDSmiGPUDevice* device, amdsmi_board_info_t *info);
amdsmi_status_t smi_amdgpu_get_power_cap(amd::smi::AMDSmiGPUDevice* device, int *cap);
amdsmi_status_t smi_amdgpu_get_ranges(amd::smi::AMDSmiGPUDevice* device, amdsmi_clk_type_t domain, int *max_freq, int *min_freq, int *num_dpm);
amdsmi_status_t smi_amdgpu_get_enabled_blocks(amd::smi::AMDSmiGPUDevice* device, uint64_t *enabled_blocks);
amdsmi_status_t smi_amdgpu_get_bad_page_info(amd::smi::AMDSmiGPUDevice* device, uint32_t *num_pages, amdsmi_retired_page_record_t *info);
amdsmi_status_t smi_amdgpu_get_ecc_error_count(amd::smi::AMDSmiGPUDevice* device, amdsmi_error_count_t *err_cnt);
amdsmi_status_t smi_amdgpu_get_driver_version(amd::smi::AMDSmiGPUDevice* device, int *length, char *version);

#endif //

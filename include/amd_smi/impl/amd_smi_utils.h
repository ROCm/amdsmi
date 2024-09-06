/* 
 * Copyright (C) 2023 Advanced Micro Devices. All rights reserved.
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

#include <limits>
#include <type_traits>

#include "amd_smi/amdsmi.h"
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
amdsmi_status_t smi_amdgpu_get_ranges(amd::smi::AMDSmiGPUDevice* device, amdsmi_clk_type_t domain, int *max_freq, int *min_freq, int *num_dpm, int *sleep_state_freq);
amdsmi_status_t smi_amdgpu_get_enabled_blocks(amd::smi::AMDSmiGPUDevice* device, uint64_t *enabled_blocks);
amdsmi_status_t smi_amdgpu_get_bad_page_info(amd::smi::AMDSmiGPUDevice* device, uint32_t *num_pages, amdsmi_retired_page_record_t *info);
amdsmi_status_t smi_amdgpu_get_ecc_error_count(amd::smi::AMDSmiGPUDevice* device, amdsmi_error_count_t *err_cnt);
amdsmi_status_t smi_amdgpu_get_driver_version(amd::smi::AMDSmiGPUDevice* device, int *length, char *version);
amdsmi_status_t smi_amdgpu_get_pcie_speed_from_pcie_type(uint16_t pcie_type, uint32_t *pcie_speed);
amdsmi_status_t smi_amdgpu_get_market_name_from_dev_id(uint32_t device_id, char *market_name);
amdsmi_status_t smi_amdgpu_is_gpu_power_management_enabled(amd::smi::AMDSmiGPUDevice* device, bool *enabled);


template<typename>
constexpr bool is_dependent_false_v = false;

template<typename T>
inline constexpr bool is_supported_type_v = (
    std::is_same_v<std::remove_cv_t<std::remove_reference_t<T>>, std::uint8_t>  ||
    std::is_same_v<std::remove_cv_t<std::remove_reference_t<T>>, std::uint16_t> ||
    std::is_same_v<std::remove_cv_t<std::remove_reference_t<T>>, std::uint32_t> ||
    std::is_same_v<std::remove_cv_t<std::remove_reference_t<T>>, std::uint64_t>
);

template<typename T>
constexpr T get_std_num_limit()
{
    if constexpr (is_supported_type_v<T>) {
        return std::numeric_limits<T>::max();
    }
    else {
        return std::numeric_limits<T>::min();
        static_assert(is_dependent_false_v<T>, "Error: Type not supported...");
    }
}

template<typename T>
constexpr bool is_std_num_limit(T value)
{
    return (value == get_std_num_limit<T>());
}

template<typename T, typename U,  typename V = T>
constexpr T translate_umax_or_assign_value(U source_value, V target_value)
{
    T result{};
    if constexpr (is_supported_type_v<T> && is_supported_type_v<U>) {
        // If the source value is uint<U>::max(), then return is uint<T>::max()
        if (is_std_num_limit(source_value)) {
            result = get_std_num_limit<T>();
        } else {
            result = static_cast<T>(target_value);
        }

        return result;
    }
    else {
        static_assert(is_dependent_false_v<T>, "Error: Type not supported...");
    }

    return result;
}

#endif //

/*
 * =============================================================================
 * The University of Illinois/NCSA
 * Open Source License (NCSA)
 *
 * Copyright (c) 2024, Advanced Micro Devices, Inc.
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

#ifndef AMD_SMI_INCLUDE_IMPL_AMD_SMI_GPU_DEVICE_H_
#define AMD_SMI_INCLUDE_IMPL_AMD_SMI_GPU_DEVICE_H_

#include "amd_smi/amdsmi.h"
#include "amd_smi/impl/amd_smi_processor.h"
#include "amd_smi/impl/amd_smi_drm.h"
#include "shared_mutex.h"  // NOLINT
#include "rocm_smi/rocm_smi_logger.h"

namespace amd {
namespace smi {


// PID, amdsmi_proc_info_t
using GPUComputeProcessList_t = std::map<amdsmi_process_handle_t, amdsmi_proc_info_t>;
using ComputeProcessListClassType_t = uint16_t;

enum class ComputeProcessListType_t : ComputeProcessListClassType_t
{
    kAllProcesses,
    kAllProcessesOnDevice,
};


class AMDSmiGPUDevice: public AMDSmiProcessor {

 public:
    AMDSmiGPUDevice(uint32_t gpu_id, uint32_t fd, std::string path, amdsmi_bdf_t bdf, AMDSmiDrm& drm):
            AMDSmiProcessor(AMDSMI_PROCESSOR_TYPE_AMD_GPU), gpu_id_(gpu_id), fd_(fd), path_(path), bdf_(bdf), drm_(drm) {}

    AMDSmiGPUDevice(uint32_t gpu_id, AMDSmiDrm& drm):
            AMDSmiProcessor(AMDSMI_PROCESSOR_TYPE_AMD_GPU), gpu_id_(gpu_id), drm_(drm) {
                if (check_if_drm_is_supported()) this->get_drm_data();
            }
    ~AMDSmiGPUDevice() {
    }

    amdsmi_status_t get_drm_data();
    pthread_mutex_t* get_mutex();
    uint32_t get_gpu_id() const;
    uint32_t get_gpu_fd() const;
    std::string& get_gpu_path();
    amdsmi_bdf_t  get_bdf();
    bool check_if_drm_is_supported() { return drm_.check_if_drm_is_supported(); }
    uint32_t get_vendor_id();
    const GPUComputeProcessList_t& amdgpu_get_compute_process_list(ComputeProcessListType_t list_type = ComputeProcessListType_t::kAllProcessesOnDevice);
    const GPUComputeProcessList_t& amdgpu_get_all_compute_process_list() {
        return amdgpu_get_compute_process_list(ComputeProcessListType_t::kAllProcesses);
    }

    amdsmi_status_t amdgpu_query_info(unsigned info_id,
                    unsigned size, void *value) const;
    amdsmi_status_t amdgpu_query_hw_ip(unsigned info_id, unsigned hw_ip_type,
            unsigned size, void *value) const;
    amdsmi_status_t amdgpu_query_fw(unsigned info_id, unsigned fw_type,
            unsigned size, void *value) const;
    amdsmi_status_t amdgpu_query_vbios(void *info) const;
    amdsmi_status_t amdgpu_query_driver_name(std::string& name) const;
    amdsmi_status_t amdgpu_query_driver_date(std::string& date) const;

 private:
    uint32_t gpu_id_;
    uint32_t fd_;
    std::string path_;
    amdsmi_bdf_t bdf_;
    uint32_t vendor_id_;
    AMDSmiDrm& drm_;
    GPUComputeProcessList_t compute_process_list_;
    int32_t get_compute_process_list_impl(GPUComputeProcessList_t& compute_process_list,
                                          ComputeProcessListType_t list_type);

};


}  // namespace smi
}  // namespace amd

#endif  // AMD_SMI_INCLUDE_IMPL_AMD_SMI_GPU_DEVICE_H_

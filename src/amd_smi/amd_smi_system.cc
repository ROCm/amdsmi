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
#include <sstream>
#include <iomanip>
#include "amd_smi/impl/amd_smi_system.h"
#include "amd_smi/impl/amd_smi_gpu_device.h"
#include "rocm_smi/rocm_smi.h"
#include "rocm_smi/rocm_smi_main.h"


namespace amd {
namespace smi {

#define  AMD_SMI_INIT_FLAG_RESRV_TEST1 0x800000000000000  //!< Reserved for test

amdsmi_status_t AMDSmiSystem::init(uint64_t flags) {
    init_flag_ = flags;
    amdsmi_status_t amd_smi_status;
    // populate sockets and devices
    if (flags & AMDSMI_INIT_AMD_GPUS) {
        amd_smi_status = drm_.init();
        // init rsmi
        rsmi_status_t ret = rsmi_init(flags);
        if (ret != RSMI_STATUS_SUCCESS) {
            return static_cast<amdsmi_status_t>(ret);
        }

        // libdrm is supported
        if (amd_smi_status == AMDSMI_STATUS_SUCCESS) {
            amd::smi::RocmSMI::getInstance().DiscoverAmdgpuDevices();
            uint32_t device_count = amd::smi::RocmSMI::getInstance().devices().size();
            for (uint32_t i=0; i < device_count; i++) {
                std::stringstream ss;
                //values for socked id are harcoded
                ss << std::setfill('0') << std::uppercase << std::hex
                    << std::setw(4) << drm_.get_bdfs()[i].domain_number << ":"
                    << std::setw(2) << drm_.get_bdfs()[i].bus_number << ":"
                    << std::setw(2) << drm_.get_bdfs()[i].device_number << "."
                    << std::setw(2) << drm_.get_bdfs()[i].function_number;

                // Multiple devices may share the same socket
                auto socket_id = ss.str();
                AMDSmiSocket* socket = nullptr;
                for (unsigned int j=0; j < sockets_.size(); j++) {
                    if (sockets_[j]->get_socket_id() == socket_id) {
                        socket = sockets_[j];
                        break;
                    }
                }
                if (socket == nullptr) {
                    socket = new AMDSmiSocket(ss.str());
                    sockets_.push_back(socket);
                }

                AMDSmiDevice* device = new AMDSmiGPUDevice(i, drm_);
                socket->add_device(device);
                devices_.insert(device);
            }

        }
        else {
            uint32_t device_count = 0;
            ret = rsmi_num_monitor_devices(&device_count);
            if (ret != RSMI_STATUS_SUCCESS) {
                return static_cast<amdsmi_status_t>(ret);
            }

            for (uint32_t i=0; i < device_count; i++) {
                uint64_t bdfid = 0;
                ret = rsmi_dev_pci_id_get(i, &bdfid);
                if (ret != RSMI_STATUS_SUCCESS) {
                    return static_cast<amdsmi_status_t>(ret);
                }

                uint64_t domain = (bdfid >> 32) & 0xffffffff;
                uint64_t bus = (bdfid >> 8) & 0xff;
                uint64_t device_id = (bdfid >> 3) & 0x1f;
                uint64_t function = bdfid & 0x7;

                std::stringstream ss;
                ss << std::setfill('0') << std::uppercase << std::hex
                    << std::setw(4) << domain << ":" << std::setw(2) << bus << ":"
                    << std::setw(2) << device_id << "." << std::setw(2) << function;

                // Multiple devices may share the same socket
                auto socket_id = ss.str();
                AMDSmiSocket* socket = nullptr;
                for (unsigned int j=0; j < sockets_.size(); j++) {
                    if (sockets_[j]->get_socket_id() == socket_id) {
                        socket = sockets_[j];
                        break;
                    }
                }
                if (socket == nullptr) {
                    socket = new AMDSmiSocket(ss.str());
                    sockets_.push_back(socket);
                }

                AMDSmiDevice* device = new AMDSmiGPUDevice(i, drm_);
                socket->add_device(device);
                devices_.insert(device);
            }
        }
    } else {
        return AMDSMI_STATUS_NOT_SUPPORTED;
    }
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t AMDSmiSystem::cleanup() {
    for (uint32_t i = 0; i < sockets_.size(); i++) {
        delete sockets_[i];
    }
    devices_.clear();
    sockets_.clear();
    init_flag_ = AMDSMI_INIT_ALL_DEVICES;
    rsmi_status_t ret = rsmi_shut_down();
    if (ret != RSMI_STATUS_SUCCESS) {
        return static_cast<amdsmi_status_t>(ret);
    }

    drm_.cleanup();
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t AMDSmiSystem::handle_to_socket(
            amdsmi_socket_handle socket_handle,
            AMDSmiSocket** socket) {
    if (socket_handle == nullptr || socket == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }
    *socket = static_cast<AMDSmiSocket*>(socket_handle);

    // double check handlers is here
    if (std::find(sockets_.begin(), sockets_.end(), *socket)
                != sockets_.end()) {
        return AMDSMI_STATUS_SUCCESS;
    }
    return AMDSMI_STATUS_INVAL;
    }

amdsmi_status_t AMDSmiSystem::handle_to_device(
            amdsmi_device_handle device_handle,
            AMDSmiDevice** device) {
    if (device_handle == nullptr || device == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }
    *device = static_cast<AMDSmiDevice*>(device_handle);

    // double check handlers is here
    if (std::find(devices_.begin(), devices_.end(), *device)
            != devices_.end()) {
        return AMDSMI_STATUS_SUCCESS;
    }
    return AMDSMI_STATUS_INVAL;
}

amdsmi_status_t AMDSmiSystem::gpu_index_to_handle(uint32_t gpu_index,
                    amdsmi_device_handle* device_handle) {
    if (device_handle == nullptr)
        return AMDSMI_STATUS_INVAL;

    auto iter = devices_.begin();
    for (; iter != devices_.end(); iter++) {
        auto cur_device = (*iter);
        if (cur_device->get_device_type() != AMD_GPU)
            continue;
        amd::smi::AMDSmiGPUDevice* gpu_device =
                static_cast<amd::smi::AMDSmiGPUDevice*>(cur_device);
        uint32_t cur_gpu_index = gpu_device->get_gpu_id();
        if (gpu_index == cur_gpu_index) {
            *device_handle = cur_device;
            return AMDSMI_STATUS_SUCCESS;
        }
    }
    return AMDSMI_STATUS_INVAL;
}


}  // namespace smi
}  // namespace amd


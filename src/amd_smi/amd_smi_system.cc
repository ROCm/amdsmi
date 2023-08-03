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
#include "amd_smi/impl/amd_smi_common.h"
#include "rocm_smi/rocm_smi.h"
#include "rocm_smi/rocm_smi_main.h"
#include <fstream>


namespace amd {
namespace smi {

#ifdef ENABLE_ESMI_LIB
uint32_t AMDSmiSystem::sockets = 0;
uint32_t AMDSmiSystem::cpus = 0;
uint32_t AMDSmiSystem::threads = 0;
uint32_t AMDSmiSystem::family = 0;
uint32_t AMDSmiSystem::model = 0;
#endif

#define  AMD_SMI_INIT_FLAG_RESRV_TEST1 0x800000000000000  //!< Reserved for test

amdsmi_status_t AMDSmiSystem::init(uint64_t flags) {
    init_flag_ = flags;
    amdsmi_status_t amd_smi_status;
    // populate sockets and processors
    if (flags & AMDSMI_INIT_AMD_GPUS) {
        amd_smi_status = populate_amd_gpu_devices();
        if (amd_smi_status != AMDSMI_STATUS_SUCCESS)
            return amd_smi_status;
#ifdef ENABLE_ESMI_LIB
    }
    else if(flags & AMDSMI_INIT_AMD_CPUS) {
        amd_smi_status = populate_amd_cpus();
        if (amd_smi_status != AMDSMI_STATUS_SUCCESS)
            return amd_smi_status;
#endif
    } else {
        return AMDSMI_STATUS_NOT_SUPPORTED;
    }
    return AMDSMI_STATUS_SUCCESS;
}

#ifdef ENABLE_ESMI_LIB
amdsmi_status_t AMDSmiSystem::populate_amd_cpus() {
    amdsmi_status_t amd_smi_status;
    amd::smi::AMDSmiCpuSocket *cpu_instance = nullptr;

    /* detect if its an AMD cpu */
    amd_smi_status = cpu_instance->get_cpu_vendor();
    /* esmi is for AMD cpus, if its not AMD CPU, we are not going to initialise esmi */
    if (!amd_smi_status) {
        amd_smi_status = static_cast<amdsmi_status_t>(esmi_init());
        if (amd_smi_status != AMDSMI_STATUS_SUCCESS){
            std::cout<<"\tESMI Not initialized, drivers not found " << std::endl;
            return amd_smi_status;
        }
    }

    amd_smi_status = get_cpu_sockets(sockets);
    amd_smi_status = get_cpu_cores(cpus);
    amd_smi_status = get_threads_per_core(threads);
    amd_smi_status = get_cpu_family(family);
    amd_smi_status = get_cpu_model(model);
    std::cout << "\n***********************EPYC METRICS***********************" << std::endl;
    std::cout <<"| NR_SOCKETS            | "<<sockets<<"\t\t|" << std::endl;
    std::cout <<"| NR_CPUS               | "<<cpus<<"\t\t|" << std::endl;

    if (threads > 1) {
            std::cout <<"| THREADS PER CORE      | "<<threads<<" (SMT ON)\t|" << std::endl;
    } else {
            std::cout <<"| THREADS PER CORE      | "<<threads<<" (SMT OFF)\t|" << std::endl;
    }
    std::cout <<"| CPU Family            | 0x"<<std::hex<<family<<"("<<std::dec<<family<<")\t|" << std::endl;
    std::cout <<"| CPU Model             | 0x"<<std::hex<<model<<"("<<std::dec<<model<<")\t|" << std::endl;
    std::cout << std::endl;

    for(uint32_t i = 0; i < sockets; i++) {
        uint32_t cpu_socket_id = i;

        // Multiple cores may share the same socket
        AMDSmiCpuSocket* socket = nullptr;
        for (uint32_t j = 0; j < cpu_sockets_.size(); j++) {
            if (cpu_sockets_[j]->get_socket_id() == cpu_socket_id) {
                socket = cpu_sockets_[j];
                break;
            }
        }
        if (socket == nullptr) {
            socket = new AMDSmiCpuSocket(cpu_socket_id);
            cpu_sockets_.push_back(socket);
        }

       for (uint32_t k = 0; k < cpus/threads; k++) {
            AMDSmiCpuCore* core = new AMDSmiCpuCore(k);
            socket->add_processor(core);
            processors_.insert(core);
       }
    }

    std::cout << std::endl;
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t AMDSmiSystem::get_cpu_sockets(uint32_t num_socks) {
    amdsmi_status_t ret;
    ret = static_cast<amdsmi_status_t>(esmi_number_of_sockets_get(&num_socks));
    sockets = num_socks;

    if (ret != AMDSMI_STATUS_SUCCESS) {
	    std::cout << "Failed to get number of sockets, Err["<<ret<<"]" << std::endl;
        return ret;
    }
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t AMDSmiSystem::get_cpu_cores(uint32_t num_cpus) {
    amdsmi_status_t ret;
    ret = static_cast<amdsmi_status_t>(esmi_number_of_cpus_get(&num_cpus));
    cpus = num_cpus;

    if (ret != AMDSMI_STATUS_SUCCESS) {
	    std::cout << "Failed to get number of cpus, Err["<<ret<<"]" << std::endl;
        return ret;
    }
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t AMDSmiSystem::get_threads_per_core(uint32_t threads_per_core) {
    amdsmi_status_t ret;
    ret = static_cast<amdsmi_status_t>(esmi_threads_per_core_get(&threads_per_core));
    threads = threads_per_core;

    if (ret != AMDSMI_STATUS_SUCCESS) {
	    std::cout << "Failed to get threads per core, Err["<<ret<<"]" << std::endl;
        return ret;
    }
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t AMDSmiSystem::get_cpu_family(uint32_t cpu_family) {
    amdsmi_status_t ret;
    ret = static_cast<amdsmi_status_t>(esmi_cpu_family_get(&cpu_family));
    family = cpu_family;

    if (ret != AMDSMI_STATUS_SUCCESS) {
	    std::cout << "Failed to get cpu family, Err["<<ret<<"]" << std::endl;
        return ret;
    }
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t AMDSmiSystem::get_cpu_model(uint32_t cpu_model) {
    amdsmi_status_t ret;
    ret = static_cast<amdsmi_status_t>(esmi_cpu_model_get(&cpu_model));
    model = cpu_model;

    if (ret != AMDSMI_STATUS_SUCCESS) {
	    std::cout << "Failed to get cpu model, Err["<<ret<<"]" << std::endl;
        return ret;
    }
    return AMDSMI_STATUS_SUCCESS;
}
#endif

amdsmi_status_t AMDSmiSystem::populate_amd_gpu_devices() {
    // init rsmi
    rsmi_status_t ret = rsmi_init(0);
    if (ret != RSMI_STATUS_SUCCESS) {
        return amd::smi::rsmi_to_amdsmi_status(ret);
    }

    // The init of libdrm depends on rsmi_init
    // libdrm is optional, ignore the error even if init fail.
    amdsmi_status_t amd_smi_status = drm_.init();

    uint32_t device_count = 0;
    ret = rsmi_num_monitor_devices(&device_count);
    if (ret != RSMI_STATUS_SUCCESS) {
        return amd::smi::rsmi_to_amdsmi_status(ret);
    }

    for (uint32_t i=0; i < device_count; i++) {
        // GPU device uses the bdf as the socket id
        std::string socket_id;
        amd_smi_status = get_gpu_bdf_by_index(i, socket_id);
        if (amd_smi_status != AMDSMI_STATUS_SUCCESS) {
            return amd_smi_status;
        }

        // Multiple devices may share the same socket
        AMDSmiSocket* socket = nullptr;
        for (unsigned int j=0; j < sockets_.size(); j++) {
            if (sockets_[j]->get_socket_id() == socket_id) {
                socket = sockets_[j];
                break;
            }
        }
        if (socket == nullptr) {
            socket = new AMDSmiSocket(socket_id);
            sockets_.push_back(socket);
        }

        AMDSmiProcessor* device = new AMDSmiGPUDevice(i, drm_);
        socket->add_processor(device);
        processors_.insert(device);
    }
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t AMDSmiSystem::get_gpu_bdf_by_index(uint32_t index,
            std::string& bdf) {
    uint64_t bdfid = 0;
    rsmi_status_t ret = rsmi_dev_pci_id_get(index, &bdfid);
    if (ret != RSMI_STATUS_SUCCESS) {
        return amd::smi::rsmi_to_amdsmi_status(ret);
    }

    uint64_t domain = (bdfid >> 32) & 0xffffffff;
    uint64_t bus = (bdfid >> 8) & 0xff;
    uint64_t device_id = (bdfid >> 3) & 0x1f;
    uint64_t function = bdfid & 0x7;

    std::stringstream ss;
    ss << std::setfill('0') << std::uppercase << std::hex
        << std::setw(4) << domain << ":" << std::setw(2) << bus << ":"
        << std::setw(2) << device_id << "." << std::setw(2) << function;
    bdf = ss.str();
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t AMDSmiSystem::cleanup() {
#ifdef ENABLE_ESMI_LIB
    if(init_flag_ == AMDSMI_INIT_AMD_CPUS){
        for (uint32_t i = 0; i < cpu_sockets_.size(); i++) {
            delete cpu_sockets_[i];
        }
        cpu_sockets_.clear();
        processors_.clear();
        esmi_exit();
        init_flag_ = AMDSMI_INIT_ALL_PROCESSORS;
        return AMDSMI_STATUS_SUCCESS;
    }
#endif
    for (uint32_t i = 0; i < sockets_.size(); i++) {
        delete sockets_[i];
    }
    processors_.clear();
    sockets_.clear();
    init_flag_ = AMDSMI_INIT_ALL_PROCESSORS;
    rsmi_status_t ret = rsmi_shut_down();
    if (ret != RSMI_STATUS_SUCCESS) {
        return amd::smi::rsmi_to_amdsmi_status(ret);
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

#ifdef ENABLE_ESMI_LIB
amdsmi_status_t AMDSmiSystem::handle_to_cpusocket(
            amdsmi_cpusocket_handle socket_handle,
            AMDSmiCpuSocket** socket) {
    if (socket_handle == nullptr || socket == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }
    *socket = static_cast<AMDSmiCpuSocket*>(socket_handle);

    // double check handlers is here
    if (std::find(cpu_sockets_.begin(), cpu_sockets_.end(), *socket)
                != cpu_sockets_.end()) {
        return AMDSMI_STATUS_SUCCESS;
    }
    return AMDSMI_STATUS_INVAL;
    }
#endif

amdsmi_status_t AMDSmiSystem::handle_to_processor(
            amdsmi_processor_handle processor_handle,
            AMDSmiProcessor** processor) {
    if (processor_handle == nullptr || processor == nullptr) {
        return AMDSMI_STATUS_INVAL;
    }
    *processor = static_cast<AMDSmiProcessor*>(processor_handle);

    // double check handlers is here
    if (std::find(processors_.begin(), processors_.end(), *processor)
            != processors_.end()) {
        return AMDSMI_STATUS_SUCCESS;
    }
    return AMDSMI_STATUS_NOT_FOUND;
}

amdsmi_status_t AMDSmiSystem::gpu_index_to_handle(uint32_t gpu_index,
                    amdsmi_processor_handle* processor_handle) {
    if (processor_handle == nullptr)
        return AMDSMI_STATUS_INVAL;

    auto iter = processors_.begin();
    for (; iter != processors_.end(); iter++) {
        auto cur_device = (*iter);
        if (cur_device->get_processor_type() != AMD_GPU)
            continue;
        amd::smi::AMDSmiGPUDevice* gpu_device =
                static_cast<amd::smi::AMDSmiGPUDevice*>(cur_device);
        uint32_t cur_gpu_index = gpu_device->get_gpu_id();
        if (gpu_index == cur_gpu_index) {
            *processor_handle = cur_device;
            return AMDSMI_STATUS_SUCCESS;
        }
    }
    return AMDSMI_STATUS_INVAL;
}

#ifdef ENABLE_ESMI_LIB
amdsmi_status_t AMDSmiSystem::cpu_index_to_handle(uint32_t cpu_index,
                    amdsmi_cpusocket_handle* cpu_handle) {
    if (cpu_handle == nullptr)
        return AMDSMI_STATUS_INVAL;

    auto iter = cpu_sockets_.begin();
    for (; iter != cpu_sockets_.end(); iter++) {
        auto cur_socket = (*iter);
        if (cur_socket->get_processor_type() != AMD_CPU)
            continue;
        amd::smi::AMDSmiCpuSocket* cpu_socket =
                static_cast<amd::smi::AMDSmiCpuSocket*>(cur_socket);
        uint32_t cur_cpu_index = cpu_socket->get_cpu_id();
        if (cpu_index == cur_cpu_index) {
            *cpu_handle = cur_socket;
            return AMDSMI_STATUS_SUCCESS;
        }
    }
    return AMDSMI_STATUS_INVAL;
}
#endif

}  // namespace smi
}  // namespace amd

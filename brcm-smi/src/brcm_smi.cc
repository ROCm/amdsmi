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


#include "brcm_smi/brcmsmi.h"
#include <iostream>
#include "brcm_smi/impl/brcm_smi_nic_device.h"
#include "brcm_smi/impl/brcm_smi_system.h"
#include "brcm_smi/impl/brcm_smi_switch_device.h"
#include "brcm_smi/impl/brcm_smi_lspci_commands.h"
#include <vector>
#include <memory>
#include <string>
#include <cstring>
#include <stdexcept>
#include <iostream>

namespace brcm {
namespace smi {

// Global state for the library
bool g_initialized = false;
static std::vector<std::unique_ptr<BrcmSmiNICDevice>> g_nic_devices;
static std::vector<std::unique_ptr<BrcmSmiSWITCHDevice>> g_switch_devices;

}  // namespace smi
}  // namespace brcm

extern "C" {

brcmsmi_status_t brcmsmi_init(uint64_t init_flags) {
    if (brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_ALREADY_INITIALIZED;
    }
    
    // Initialize the BRCM SMI system
    brcmsmi_status_t status = brcm::smi::BRCMSmiSystem::getInstance().initialize();
    if (status != BRCMSMI_STATUS_SUCCESS) {
        return status;
    }
    
    brcm::smi::g_initialized = true;
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t brcmsmi_shutdown() {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_SUCCESS;
    }
    
    // Shutdown the BRCM SMI system
    brcm::smi::BRCMSmiSystem::getInstance().shutdown();
    
    // Clear device collections
    brcm::smi::g_nic_devices.clear();
    brcm::smi::g_switch_devices.clear();
    
    brcm::smi::g_initialized = false;
    
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t brcmsmi_get_nic_processor_handles(brcmsmi_socket_handle socket_handle,
                                                   uint32_t *processor_count,
                                                   brcmsmi_processor_handle **processor_handles) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }
    
    if (processor_count == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    // Get the socket object via socket handle.
    brcm::smi::BRCMSmiSocket* socket = nullptr;
    brcmsmi_status_t r = brcm::smi::BRCMSmiSystem::getInstance()
                    .handle_to_socket(socket_handle, &socket);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;
    std::vector<brcm::smi::BRCMSmiProcessor*>& processors = socket->get_processors(BRCMSMI_PROCESSOR_TYPE_NIC);
    uint32_t processor_size = static_cast<uint32_t>(processors.size());
    
    // Always set the processor count
    *processor_count = processor_size;
    
    // If processor_handles is nullptr, caller only wants the count
    if (processor_handles == nullptr) {
        return BRCMSMI_STATUS_SUCCESS;
    }
    
    // If no processors found, return success with nullptr
    if (processor_size == 0) {
        *processor_handles = nullptr;
        return BRCMSMI_STATUS_SUCCESS;
    }

    // Allocate memory for processor handles
    *processor_handles = new brcmsmi_processor_handle[processor_size];
    
    // Copy the processor handles
    for (uint32_t i = 0; i < processor_size; i++) {
        (*processor_handles)[i] = reinterpret_cast<brcmsmi_processor_handle>(processors[i]);
    }

    return BRCMSMI_STATUS_SUCCESS;

}

brcmsmi_status_t brcmsmi_get_switch_processor_handles(brcmsmi_socket_handle socket_handle,
                                                      uint32_t *processor_count,
                                                      brcmsmi_processor_handle **processor_handles) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }
    
    if (processor_count == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    // Get the socket object via socket handle.
    brcm::smi::BRCMSmiSocket* socket = nullptr;
    brcmsmi_status_t r = brcm::smi::BRCMSmiSystem::getInstance()
                    .handle_to_socket(socket_handle, &socket);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;
    
    std::vector<brcm::smi::BRCMSmiProcessor*>& processors = socket->get_processors(BRCMSMI_PROCESSOR_TYPE_SWITCH);
    uint32_t processor_size = static_cast<uint32_t>(processors.size());
    
    // Always set the processor count
    *processor_count = processor_size;
    
    // If processor_handles is nullptr, caller only wants the count
    if (processor_handles == nullptr) {
        return BRCMSMI_STATUS_SUCCESS;
    }
    
    // If no processors found, return success with nullptr
    if (processor_size == 0) {
        *processor_handles = nullptr;
        return BRCMSMI_STATUS_SUCCESS;
    }

    // Allocate memory for processor handles
    *processor_handles = new brcmsmi_processor_handle[processor_size];
    
    // Copy the processor handles
    for (uint32_t i = 0; i < processor_size; i++) {
        (*processor_handles)[i] = reinterpret_cast<brcmsmi_processor_handle>(processors[i]);
    }
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t brcmsmi_get_processor_type(brcmsmi_processor_handle processor_handle ,
    brcmsmi_processor_type_t* processor_type) {

    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (processor_type == nullptr) {
    return BRCMSMI_STATUS_INVALID_ARGS;
    }
    brcm::smi::BRCMSmiProcessor* processor = nullptr;
    brcmsmi_status_t r = brcm::smi::BRCMSmiSystem::getInstance()
            .handle_to_processor(processor_handle, &processor);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;
    *processor_type = processor->get_processor_type();

    return BRCMSMI_STATUS_SUCCESS;
}

static brcmsmi_status_t brcmsmi_get_nic_device_from_handle(brcmsmi_processor_handle processor_handle,
    brcm::smi::BrcmSmiNICDevice **nicdevice) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (processor_handle == nullptr || nicdevice == nullptr) return BRCMSMI_STATUS_INVALID_ARGS;

    brcm::smi::BRCMSmiProcessor *device = nullptr;
    brcmsmi_status_t r =
    brcm::smi::BRCMSmiSystem::getInstance().handle_to_processor(processor_handle, &device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;

    if (device->get_processor_type() == BRCMSMI_PROCESSOR_TYPE_NIC) {
    *nicdevice = static_cast<brcm::smi::BrcmSmiNICDevice *>(device);
    return BRCMSMI_STATUS_SUCCESS;
    }

    return BRCMSMI_STATUS_NOT_SUPPORTED;
}

static brcmsmi_status_t brcmsmi_get_switch_device_from_handle(brcmsmi_processor_handle processor_handle,
    brcm::smi::BrcmSmiSWITCHDevice **switchdevice) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (processor_handle == nullptr || switchdevice == nullptr) return BRCMSMI_STATUS_INVALID_ARGS;

    brcm::smi::BRCMSmiProcessor *device = nullptr;
    brcmsmi_status_t r =
    brcm::smi::BRCMSmiSystem::getInstance().handle_to_processor(processor_handle, &device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;

    if (device->get_processor_type() == BRCMSMI_PROCESSOR_TYPE_SWITCH) {
    *switchdevice = static_cast<brcm::smi::BrcmSmiSWITCHDevice *>(device);
    return BRCMSMI_STATUS_SUCCESS;
    }

    return BRCMSMI_STATUS_NOT_SUPPORTED;
}

brcmsmi_status_t brcmsmi_get_socket_handles(uint32_t *socket_count,
    brcmsmi_socket_handle* socket_handles) {

    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (socket_count == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    std::vector<std::unique_ptr<brcm::smi::BRCMSmiSocket>>& sockets
    = brcm::smi::BRCMSmiSystem::getInstance().get_sockets();
    uint32_t socket_size = static_cast<uint32_t>(sockets.size());
    // Get the socket size
    if (socket_handles == nullptr) {
        *socket_count = socket_size;
        return BRCMSMI_STATUS_SUCCESS;
    }

    // If the socket_handles can hold all sockets, return all of them.
    *socket_count = *socket_count >= socket_size ? socket_size : *socket_count;

    // Copy the socket handles
    for (uint32_t i = 0; i < *socket_count; i++) {
        socket_handles[i] = reinterpret_cast<brcmsmi_socket_handle>(sockets[i].get());
    }

    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t brcmsmi_get_socket_info(
    brcmsmi_socket_handle socket_handle,
    size_t len, char *name) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (socket_handle == nullptr || name == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    brcm::smi::BRCMSmiSocket* socket = nullptr;
    brcmsmi_status_t r = brcm::smi::BRCMSmiSystem::getInstance()
            .handle_to_socket(socket_handle, &socket);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;

    strncpy(name, socket->get_socket_id().c_str(), len);

    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t brcmsmi_get_nic_device_bdf(brcmsmi_processor_handle processor_handle,
    brcmsmi_bdf_t *bdf) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (bdf == NULL) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    brcm::smi::BrcmSmiNICDevice *nic_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_nic_device_from_handle(processor_handle, &nic_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;

    // get bdf from sysfs file
    *bdf = nic_device->get_bdf();

    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t brcmsmi_get_switch_device_bdf(brcmsmi_processor_handle processor_handle,
    brcmsmi_bdf_t* bdf) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (bdf == NULL) {
    return BRCMSMI_STATUS_INVALID_ARGS;
    }

    brcm::smi::BrcmSmiSWITCHDevice* switch_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_switch_device_from_handle(processor_handle, &switch_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;

    // get bdf from sysfs file
    *bdf = switch_device->get_bdf();

    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t brcmsmi_get_switch_link_info(brcmsmi_processor_handle processor_handle,
    brcmsmi_switch_link_metric_t *info) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (info == NULL) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    brcm::smi::BrcmSmiSWITCHDevice *switch_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_switch_device_from_handle(processor_handle, &switch_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;

    switch_device->query_switch_link_info(*info);

    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t brcmsmi_get_switch_power_info(brcmsmi_processor_handle processor_handle,
    brcmsmi_switch_power_metric_t *info) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (info == NULL) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    brcm::smi::BrcmSmiSWITCHDevice *switch_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_switch_device_from_handle(processor_handle, &switch_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;

    switch_device->query_switch_power_info(*info);

    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t brcmsmi_get_switch_info(brcmsmi_processor_handle processor_handle, brcmsmi_switch_info_t *info) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (info == NULL) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    brcm::smi::BrcmSmiSWITCHDevice *switch_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_switch_device_from_handle(processor_handle, &switch_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;

    return switch_device->query_switch_info(*info);
}

brcmsmi_status_t brcmsmi_get_switch_device_info(brcmsmi_processor_handle processor_handle,
    brcmsmi_switch_device_metric_t *info) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (info == NULL) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    brcmsmi_status_t ret;
    ret = brcmsmi_get_switch_power_info(processor_handle, &(info->brcm_device_power));
    if (ret != BRCMSMI_STATUS_SUCCESS) {
        throw std::runtime_error("brcmsmi_get_switch_device_info - Failed to fetch power metrics.\n");
        return ret;
    }

    brcm::smi::BrcmSmiSWITCHDevice *switch_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_switch_device_from_handle(processor_handle, &switch_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;

    switch_device->query_switch_device_info(*info);

    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t brcmsmi_get_switch_metrics_info(brcmsmi_processor_handle processor_handle, brcmsmi_switch_device_metric_t *info){
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (info == NULL) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    brcmsmi_status_t ret;
    ret = brcmsmi_get_switch_power_info(processor_handle, &(info->brcm_device_power));
    if (ret != BRCMSMI_STATUS_SUCCESS) {
        throw std::runtime_error("brcmsmi_get_switch_metrics_info - Failed to fetch power metrics.\n");
        return ret;
    }

    // Fetch the full device struct
    brcmsmi_switch_device_metric_t full_device;
    ret = brcmsmi_get_switch_device_info(processor_handle, &full_device);
    if (ret != BRCMSMI_STATUS_SUCCESS) {
        throw std::runtime_error("brcmsmi_get_switch_metrics_info - Failed to fetch switch device.\n");
        return ret;
    }

    // Copy only the 3 required fields into metrics
    strncpy(info->brcm_device_aer_dev_correctable, full_device.brcm_device_aer_dev_correctable, BRCMSMI_MAX_STRING_LENGTH);
    strncpy(info->brcm_device_aer_dev_fatal, full_device.brcm_device_aer_dev_fatal, BRCMSMI_MAX_STRING_LENGTH);
    strncpy(info->brcm_device_aer_dev_nonfatal, full_device.brcm_device_aer_dev_nonfatal, BRCMSMI_MAX_STRING_LENGTH);

    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t brcmsmi_get_root_switch(brcmsmi_bdf_t deviceBdf, brcmsmi_bdf_t *switchBdf) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }
    brcmsmi_status_t status = brcm::smi::get_lspci_root_switch(deviceBdf, switchBdf);
    return status;
}

brcmsmi_status_t brcmsmi_get_nic_topo_numa_affinity(
    brcmsmi_processor_handle processor_handle, int32_t *numa_node) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    brcm::smi::BrcmSmiNICDevice *nic_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_nic_device_from_handle(processor_handle, &nic_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;
    
    return nic_device->query_nic_numa_affinity(numa_node);
}

brcmsmi_status_t brcmsmi_get_nic_topo_cpu_affinity(brcmsmi_processor_handle processor_handle,
                                           unsigned int *cpu_aff_length, char *cpu_aff_data) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }
    if (cpu_aff_length == nullptr || cpu_aff_data == nullptr ||
        *cpu_aff_length < BRCMSMI_MAX_STRING_LENGTH) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    brcm::smi::BrcmSmiNICDevice *nic_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_nic_device_from_handle(processor_handle, &nic_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;

    brcmsmi_status_t status = BRCMSMI_STATUS_SUCCESS;
    std::string cpu_affinity;
    status = nic_device->query_nic_cpu_affinity(cpu_affinity);
    if (status != BRCMSMI_STATUS_SUCCESS) {
        printf("Getting cpu_affinity info failed. Return code: %d", status);
        return status;
    }
    // Use safe string copy with bounds checking
    if (cpu_affinity.length() >= *cpu_aff_length) {
        return BRCMSMI_STATUS_INSUFFICIENT_SIZE;
    }
    strncpy(cpu_aff_data, cpu_affinity.c_str(), *cpu_aff_length - 1);
    cpu_aff_data[*cpu_aff_length - 1] = '\0';
    *cpu_aff_length = static_cast<unsigned int>(cpu_affinity.length());
    return status;
}

brcmsmi_status_t brcmsmi_get_switch_topo_numa_affinity(
    brcmsmi_processor_handle processor_handle, int32_t *numa_node) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    brcm::smi::BrcmSmiSWITCHDevice *switch_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_switch_device_from_handle(processor_handle, &switch_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;
    
    return switch_device->query_switch_numa_affinity(numa_node);
}

brcmsmi_status_t brcmsmi_get_switch_topo_cpu_affinity(brcmsmi_processor_handle processor_handle,
                                           unsigned int *cpu_aff_length, char *cpu_aff_data) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }
    if (cpu_aff_length == nullptr || cpu_aff_data == nullptr ||
        *cpu_aff_length < BRCMSMI_MAX_STRING_LENGTH) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    brcm::smi::BrcmSmiSWITCHDevice *switch_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_switch_device_from_handle(processor_handle, &switch_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;

    brcmsmi_status_t status = BRCMSMI_STATUS_SUCCESS;
    std::string cpu_affinity;
    status = switch_device->query_switch_cpu_affinity(cpu_affinity);
    if (status != BRCMSMI_STATUS_SUCCESS) {
        printf("Getting cpu_affinity info failed. Return code: %d", status);
        return status;
    }
    // Use safe string copy with bounds checking
    if (cpu_affinity.length() >= *cpu_aff_length) {
        return BRCMSMI_STATUS_INSUFFICIENT_SIZE;
    }
    strncpy(cpu_aff_data, cpu_affinity.c_str(), *cpu_aff_length - 1);
    cpu_aff_data[*cpu_aff_length - 1] = '\0';
    *cpu_aff_length = static_cast<unsigned int>(cpu_affinity.length());
    return status;
}

brcmsmi_status_t brcmsmi_get_nic_gpu_topo_info(brcmsmi_processor_handle nic_processor_handle, 
    brcmsmi_processor_handle gpu_processor_handle, unsigned int *topo_info_length, char *topo_info) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }
    /*if (topo_info_length == nullptr || topo_info == nullptr ||
    *topo_info_length < BRCMSMI_MAX_STRING_LENGTH) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    brcmsmi_status_t status = BRCMSMI_STATUS_SUCCESS;
    brcm::smi::BrcmSmiNICDevice *nic_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_nic_device_from_handle(nic_processor_handle, &nic_device);
    if (status != BRCMSMI_STATUS_SUCCESS) {
        printf("Received invalid NIC handler. Return code: %d", status);
        return status;
    }
    brcm::smi::BRCMSmiGPUDevice* gpu_device = nullptr;
    status = get_gpu_device_from_handle(gpu_processor_handle, &gpu_device);
    if (status != BRCMSMI_STATUS_SUCCESS) {
        printf("Received invalid GPU handler. Return code: %d", status);
        return status;
    }
    brcmsmi_bdf_t nic_switchBdf = {};
    status = brcmsmi_get_root_switch(nic_device->get_bdf(), &nic_switchBdf);
    if (status != BRCMSMI_STATUS_SUCCESS) {
        printf("Not able to get nic's switch bdf. Return code: %d", status);
        return status;
    }
    brcmsmi_bdf_t gpu_switchBdf = {};
    status = brcmsmi_get_root_switch(gpu_device->get_bdf(), &gpu_switchBdf);
    if (status != BRCMSMI_STATUS_SUCCESS) {
        printf("Not able to get nic's switch bdf. Return code: %d", status);
        return status;
    }
    int32_t gpu_numa_node;
    status = brcmsmi_get_gpu_topo_numa_affinity(gpu_processor_handle, &gpu_numa_node);
    if (status != BRCMSMI_STATUS_SUCCESS) {
        printf("Not able to get gpu's NUMA. Return code: %d", status);
        return status;
    }
    int32_t nic_numa_node;
    status = nic_device->query_nic_numa_affinity(&nic_numa_node);
    if (nic_numa_node == 65535) {
        printf("Not able to get nic's NUMA. Return code: %d", status);
        return status;
    }
    if(gpu_numa_node != nic_numa_node) {
        const char* topo_str = "X-NUMA";
        if (strlen(topo_str) >= *topo_info_length) {
            return BRCMSMI_STATUS_INSUFFICIENT_SIZE;
        }
        strncpy(topo_info, topo_str, *topo_info_length - 1);
        topo_info[*topo_info_length - 1] = '\0';
        *topo_info_length = static_cast<unsigned int>(strlen(topo_str));
        return BRCMSMI_STATUS_SUCCESS;
    }
    if(gpu_numa_node == nic_numa_node) {
        const char* topo_str = "NUMA";
        if (strlen(topo_str) >= *topo_info_length) {
            return BRCMSMI_STATUS_INSUFFICIENT_SIZE;
        }
        strncpy(topo_info, topo_str, *topo_info_length - 1);
        topo_info[*topo_info_length - 1] = '\0';
        *topo_info_length = static_cast<unsigned int>(strlen(topo_str));
        if ((gpu_switchBdf.bus_number == nic_switchBdf.bus_number) &&
        (gpu_switchBdf.device_number == nic_switchBdf.device_number) &&
        (gpu_switchBdf.domain_number == nic_switchBdf.domain_number) &&
        (gpu_switchBdf.function_number == nic_switchBdf.function_number)) { 
            const char* topo_str_pcie = "PCIe";
            if (strlen(topo_str_pcie) >= *topo_info_length) {
                return BRCMSMI_STATUS_INSUFFICIENT_SIZE;
            }
            strncpy(topo_info, topo_str_pcie, *topo_info_length - 1);
            topo_info[*topo_info_length - 1] = '\0';
            *topo_info_length = static_cast<unsigned int>(strlen(topo_str_pcie));
        }
    }*/
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t brcmsmi_get_nic_metrics_info(brcmsmi_processor_handle processor_handle,
    brcmsmi_nic_hwmon_metrics_t *metrics) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (metrics == NULL) {
      return BRCMSMI_STATUS_INVALID_ARGS;
    }

    brcmsmi_status_t ret;

    brcm::smi::BrcmSmiNICDevice *nic_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_nic_device_from_handle(processor_handle, &nic_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;

    // Fetch power metrics
    ret = nic_device->query_nic_power_info(metrics->nic_power);
    if (ret != BRCMSMI_STATUS_SUCCESS) {
        printf("Failed to fetch NIC power metrics.\n");
        return ret;
    }

    // Fetch temperature metrics
    ret = nic_device->query_nic_temp_info(metrics->nic_temperature);
    if (ret != BRCMSMI_STATUS_SUCCESS) {
        printf("Failed to fetch NIC temperature metrics.\n");
        return ret;
    }

    // Fetch the full device struct
    brcmsmi_nic_hwmon_device_t full_device;
    ret = nic_device->query_nic_device_info(full_device);
    if (ret != BRCMSMI_STATUS_SUCCESS) {
        printf("Failed to fetch NIC device metrics.\n");
        return ret;
    }

    // Copy only the 3 required fields into metrics
    strncpy(metrics->nic_device_aer_dev_correctable, full_device.nic_device_aer_dev_correctable, BRCMSMI_MAX_STRING_LENGTH);
    strncpy(metrics->nic_device_aer_dev_fatal, full_device.nic_device_aer_dev_fatal, BRCMSMI_MAX_STRING_LENGTH);
    strncpy(metrics->nic_device_aer_dev_nonfatal, full_device.nic_device_aer_dev_nonfatal, BRCMSMI_MAX_STRING_LENGTH);

    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t brcmsmi_get_nic_device_uuid(brcmsmi_processor_handle processor_handle,
    unsigned int *uuid_length, char *uuid) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (uuid_length == nullptr || uuid == nullptr ||
        *uuid_length < BRCMSMI_MAX_STRING_LENGTH) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    brcm::smi::BrcmSmiNICDevice *nic_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_nic_device_from_handle(processor_handle, &nic_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;

    brcmsmi_status_t status = BRCMSMI_STATUS_SUCCESS;
    std::string uuidStr;
    status = nic_device->query_nic_uuid(uuidStr);
    if (status != BRCMSMI_STATUS_SUCCESS) {
        printf("Getting asic info failed. Return code: %d", status);
        return status;
    }
    // Use safe string copy with bounds checking
    if (uuidStr.length() >= *uuid_length) {
        return BRCMSMI_STATUS_INSUFFICIENT_SIZE;
    }
    strncpy(uuid, uuidStr.c_str(), *uuid_length - 1);
    uuid[*uuid_length - 1] = '\0';
    *uuid_length = static_cast<unsigned int>(uuidStr.length());
    return status;
}

brcmsmi_status_t brcmsmi_get_switch_device_uuid(brcmsmi_processor_handle processor_handle,
    unsigned int *uuid_length, char *uuid) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }

    if (uuid_length == nullptr || uuid == nullptr ||
        *uuid_length < BRCMSMI_MAX_STRING_LENGTH) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    brcm::smi::BrcmSmiSWITCHDevice *switch_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_switch_device_from_handle(processor_handle, &switch_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;

    brcmsmi_status_t status = BRCMSMI_STATUS_SUCCESS;
    std::string uuidStr;
    status = switch_device->query_switch_uuid(uuidStr);
    if (status != BRCMSMI_STATUS_SUCCESS) {
        printf("Getting asic info failed. Return code: %d", status);
        return status;
    }
    // Use safe string copy with bounds checking
    if (uuidStr.length() >= *uuid_length) {
        return BRCMSMI_STATUS_INSUFFICIENT_SIZE;
    }
    strncpy(uuid, uuidStr.c_str(), *uuid_length - 1);
    uuid[*uuid_length - 1] = '\0';
    *uuid_length = static_cast<unsigned int>(uuidStr.length());
    return status;
}


//==============================================================================
// AMD SMI Compatibility Functions
//==============================================================================

// AMD SMI compatible init/shutdown functions removed - use brcmsmi_init/brcmsmi_shutdown directly



/**
 * @brief Get BRCM processor handles for AMD SMI compatibility
 */
brcmsmi_status_t brcmsmi_get_brcm_processor_handles(uint32_t socket_index,
                                                    brcmsmi_processor_type_t device_type,
                                                    uint32_t *processor_count,
                                                    brcmsmi_processor_handle *processor_handles) {
    if (processor_count == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    // Get socket handles first
    uint32_t socket_count = 0;
    brcmsmi_socket_handle *socket_handles = nullptr;
    brcmsmi_status_t status = brcmsmi_get_socket_handles(&socket_count, socket_handles);
    
    if (status != BRCMSMI_STATUS_SUCCESS || socket_index >= socket_count) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    // Get appropriate processor handles based on device type
    if (device_type == BRCMSMI_PROCESSOR_TYPE_NIC) {
        return brcmsmi_get_nic_processor_handles(socket_handles[socket_index], 
                                                processor_count, 
                                                (brcmsmi_processor_handle**)&processor_handles);
    } else if (device_type == BRCMSMI_PROCESSOR_TYPE_SWITCH) {
        return brcmsmi_get_switch_processor_handles(socket_handles[socket_index], 
                                                   processor_count, 
                                                   (brcmsmi_processor_handle**)&processor_handles);
    }
    
    return BRCMSMI_STATUS_NOT_SUPPORTED;
}

brcmsmi_status_t brcmsmi_get_brcm_processor_handles_by_type(brcmsmi_socket_handle socket_handle,
                                                         brcmsmi_processor_type_t device_type,
                                                         uint32_t *processor_count,
                                                         brcmsmi_processor_handle *processor_handles) {
    if (socket_handle == nullptr || processor_count == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }

    // Use the BRCM SMI system to get processor handles
    return brcm::smi::BRCMSmiSystem::getInstance().get_processor_handles(
        socket_handle, device_type, processor_count, processor_handles);
}

brcmsmi_status_t brcmsmi_get_brcm_processor_handles_by_bdf(brcmsmi_socket_handle socket_handle,
                                                        brcmsmi_bdf_t bdf,
                                                        uint32_t *processor_count,
                                                        brcmsmi_processor_handle *processor_handles) {
    if (socket_handle == nullptr || processor_count == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    // TODO: Implement BDF-based processor lookup
    return BRCMSMI_STATUS_NOT_SUPPORTED;
}

// Implementation of missing NIC API functions
brcmsmi_status_t brcmsmi_get_nic_info(brcmsmi_processor_handle processor_handle, brcmsmi_nic_info_t *info) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }
    
    if (info == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    brcm::smi::BrcmSmiNICDevice *nic_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_nic_device_from_handle(processor_handle, &nic_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;
    
    return nic_device->query_nic_info(*info);
}

brcmsmi_status_t brcmsmi_get_nic_temp_info(brcmsmi_processor_handle processor_handle,
                                           brcmsmi_nic_temperature_metric_t *info) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }
    
    if (info == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    brcm::smi::BrcmSmiNICDevice *nic_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_nic_device_from_handle(processor_handle, &nic_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;
    
    return nic_device->query_nic_temp_info(*info);
}

brcmsmi_status_t brcmsmi_get_nic_power_info(brcmsmi_processor_handle processor_handle,
                                            brcmsmi_nic_hwmon_power_t *info) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }
    
    if (info == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    brcm::smi::BrcmSmiNICDevice *nic_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_nic_device_from_handle(processor_handle, &nic_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;
    
    return nic_device->query_nic_power_info(*info);
}

brcmsmi_status_t brcmsmi_get_nic_device_info(brcmsmi_processor_handle processor_handle,
                                             brcmsmi_nic_hwmon_device_t *info) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }
    
    if (info == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    brcm::smi::BrcmSmiNICDevice *nic_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_nic_device_from_handle(processor_handle, &nic_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;
    
    return nic_device->query_nic_device_info(*info);
}

brcmsmi_status_t brcmsmi_get_nic_fw_info(brcmsmi_processor_handle processor_handle,
                                         brcmsmi_nic_firmware_t *info) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }
    
    if (info == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    brcm::smi::BrcmSmiNICDevice *nic_device = nullptr;
    brcmsmi_status_t r = brcmsmi_get_nic_device_from_handle(processor_handle, &nic_device);
    if (r != BRCMSMI_STATUS_SUCCESS) return r;
    
    return nic_device->query_nic_firmware_info(*info);
}

// Generic getString method implementation
brcmsmi_status_t brcmsmi_getString(brcmsmi_processor_handle processor_handle,
                                   const char* method_name,
                                   size_t value_length,
                                   char* value) {
    if (!brcm::smi::g_initialized) {
        return BRCMSMI_STATUS_INIT_ERROR;
    }
    
    if (processor_handle == nullptr || method_name == nullptr || value == nullptr || value_length == 0) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    // Clear the output buffer
    memset(value, 0, value_length);
    
    try {
        std::string method(method_name);
        std::string result;
        
        // Determine processor type from handle
        brcm::smi::BrcmSmiNICDevice *nic_device = nullptr;
        brcm::smi::BrcmSmiSWITCHDevice *switch_device = nullptr;
        
        brcmsmi_status_t nic_result = brcmsmi_get_nic_device_from_handle(processor_handle, &nic_device);
        brcmsmi_status_t switch_result = brcmsmi_get_switch_device_from_handle(processor_handle, &switch_device);
        
        bool is_nic = (nic_result == BRCMSMI_STATUS_SUCCESS);
        bool is_switch = (switch_result == BRCMSMI_STATUS_SUCCESS);
        
        if (!is_nic && !is_switch) {
            // If both failed with something other than NOT_SUPPORTED, it's likely an invalid handle
            if (nic_result != BRCMSMI_STATUS_NOT_SUPPORTED && switch_result != BRCMSMI_STATUS_NOT_SUPPORTED) {
                return BRCMSMI_STATUS_INVALID_ARGS;
            }
            // If one failed with NOT_SUPPORTED but the other failed differently, return the error
            if (nic_result != BRCMSMI_STATUS_NOT_SUPPORTED) {
                return nic_result;
            }
            if (switch_result != BRCMSMI_STATUS_NOT_SUPPORTED) {
                return switch_result;
            }
            // Both failed with NOT_SUPPORTED, which means the handle is valid but neither type matches
            return BRCMSMI_STATUS_NOT_SUPPORTED;
        }
        
        // Handle NIC methods
        if (is_nic && nic_device != nullptr) {
            if (method == "get_nic_info") {
                brcmsmi_nic_info_t info;
                brcmsmi_status_t status = nic_device->query_nic_info(info);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = "{"
                        "\"nic_device_name\":\"" + std::string(info.nic_device_name) + "\","
                        "\"nic_part_number\":\"" + std::string(info.nic_part_number) + "\","
                        "\"nic_firmware_version\":\"" + std::string(info.nic_firmware_version) + "\","
                        "\"nic_uuid\":\"" + std::string(info.nic_uuid) + "\""
                        "}";
                } else {
                    return status;
                }
            } else if (method == "get_nic_device_uuid") {
                std::string uuid_str;
                brcmsmi_status_t status = nic_device->query_nic_uuid(uuid_str);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = uuid_str;
                } else {
                    return status;
                }
            } else if (method == "get_nic_metrics") {
                // Get NIC device metrics
                brcmsmi_nic_hwmon_device_t device_info;
                brcmsmi_status_t status = nic_device->query_nic_device_info(device_info);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = "{"
                        "\"nic_device_class\":\"" + std::string(device_info.nic_device_class) + "\","
                        "\"nic_device_vendor\":\"" + std::string(device_info.nic_device_vendor) + "\","
                        "\"nic_device_device\":\"" + std::string(device_info.nic_device_device) + "\","
                        "\"nic_device_numa_node\":\"" + std::to_string(device_info.nic_device_numa_node) + "\","
                        "\"nic_device_enable\":\"" + std::to_string(device_info.nic_device_enable) + "\""
                        "}";
                } else {
                    result = "{\"status\":\"device_metrics_not_available\"}";
                }
            } else if (method == "get_nic_numa_affinity") {
                int32_t numa_node;
                brcmsmi_status_t status = nic_device->query_nic_numa_affinity(&numa_node);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = std::to_string(numa_node);
                } else {
                    result = "-1";  // Invalid NUMA node
                }
            } else if (method == "get_nic_power_info") {
                brcmsmi_nic_hwmon_power_t power_info;
                brcmsmi_status_t status = nic_device->query_nic_power_info(power_info);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = "{"
                        "\"nic_power_async\":\"" + std::string(power_info.nic_power_async) + "\","
                        "\"nic_power_control\":\"" + std::string(power_info.nic_power_control) + "\","
                        "\"nic_power_runtime_active_time\":\"" + std::to_string(power_info.nic_power_runtime_active_time) + "\","
                        "\"nic_power_runtime_status\":\"" + std::string(power_info.nic_power_runtime_status) + "\","
                        "\"nic_power_runtime_usage\":\"" + std::to_string(power_info.nic_power_runtime_usage) + "\","
                        "\"nic_power_runtime_active_kids\":\"" + std::to_string(power_info.nic_power_runtime_active_kids) + "\""
                        "}";
                } else {
                    return status;
                }
            } else if (method == "get_nic_temperature") {
                brcmsmi_nic_temperature_metric_t temp_info;
                brcmsmi_status_t status = nic_device->query_nic_temp_info(temp_info);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = "{"
                        "\"nic_temp_input\":\"" + std::to_string(temp_info.nic_temp_input) + "\","
                        "\"nic_temp_max\":\"" + std::to_string(temp_info.nic_temp_max) + "\","
                        "\"nic_temp_crit\":\"" + std::to_string(temp_info.nic_temp_crit) + "\","
                        "\"nic_temp_emergency\":\"" + std::to_string(temp_info.nic_temp_emergency) + "\","
                        "\"nic_temp_shutdown\":\"" + std::to_string(temp_info.nic_temp_shutdown) + "\","
                        // Add alarm values read directly from hardware
                        "\"nic_temp_crit_alarm\":\"" + std::to_string(temp_info.nic_temp_crit_alarm) + "\","
                        "\"nic_temp_emergency_alarm\":\"" + std::to_string(temp_info.nic_temp_emergency_alarm) + "\","
                        "\"nic_temp_shutdown_alarm\":\"" + std::to_string(temp_info.nic_temp_shutdown_alarm) + "\","
                        "\"nic_temp_max_alarm\":\"" + std::to_string(temp_info.nic_temp_max_alarm) + "\""
                        "}";
                } else {
                    return status;
                }
            } else if (method == "get_nic_firmware_info") {
                brcmsmi_nic_firmware_t fw_info;
                brcmsmi_status_t status = nic_device->query_nic_firmware_info(fw_info);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = "{"
                        "\"nic_fw_version\":\"" + std::string(fw_info.nic_fw_version) + "\","
                        "\"nic_fw_pkg_version\":\"" + std::string(fw_info.nic_fw_pkg_version) + "\","
                        "\"nic_fw_efi_version\":\"" + std::string(fw_info.nic_fw_efi_version) + "\","
                        "\"nic_fw_ncsi_version\":\"" + std::string(fw_info.nic_fw_ncsi_version) + "\","
                        "\"nic_fw_roce_version\":\"" + std::string(fw_info.nic_fw_roce_version) + "\""
                        "}";
                } else {
                    return status;
                }
            } else if (method == "get_nic_topology") {
                // Get NIC topology information using NUMA and device info
                int32_t numa_node;
                brcmsmi_status_t numa_status = nic_device->query_nic_numa_affinity(&numa_node);
                brcmsmi_nic_hwmon_device_t device_info;
                brcmsmi_status_t device_status = nic_device->query_nic_device_info(device_info);
                
                if (numa_status == BRCMSMI_STATUS_SUCCESS || device_status == BRCMSMI_STATUS_SUCCESS) {
                    result = "{"
                        "\"numa_node\":\"" + (numa_status == BRCMSMI_STATUS_SUCCESS ? std::to_string(numa_node) : "unknown") + "\","
                        "\"device_class\":\"" + (device_status == BRCMSMI_STATUS_SUCCESS ? std::string(device_info.nic_device_class) : "unknown") + "\","
                        "\"vendor\":\"" + (device_status == BRCMSMI_STATUS_SUCCESS ? std::string(device_info.nic_device_vendor) : "unknown") + "\","
                        "\"device_id\":\"" + (device_status == BRCMSMI_STATUS_SUCCESS ? std::string(device_info.nic_device_device) : "unknown") + "\""
                        "}";
                } else {
                    result = "{\"status\":\"topology_not_available\"}";
                }
            } else if (method == "get_nic_cpu_affinity") {
                std::string cpu_affinity;
                brcmsmi_status_t status = nic_device->query_nic_cpu_affinity(cpu_affinity);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = cpu_affinity;
                } else {
                    result = "0";  // Default CPU affinity
                }
            } else if (method == "get_nic_errors") {
                // Get NIC error metrics from sysfs AER files
                std::map<std::string, std::map<std::string, uint32_t>> errors;
                brcmsmi_status_t status = nic_device->query_nic_error_info(errors);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    // Build JSON response from the error data
                    result = "{";
                    bool first_category = true;
                    for (const auto& category : errors) {
                        if (!first_category) result += ",";
                        result += "\"" + category.first + "\":{";
                        
                        bool first_error = true;
                        for (const auto& error : category.second) {
                            if (!first_error) result += ",";
                            result += "\"" + error.first + "\":" + std::to_string(error.second);
                            first_error = false;
                        }
                        result += "}";
                        first_category = false;
                    }
                    result += "}";
                } else {
                    // Fallback to basic structure if error reading fails
                    result = "{"
                        "\"nic_dev_correctable\":{\"rxerr\":0},"
                        "\"nic_dev_fatal\":{\"undefined\":0},"
                        "\"nic_dev_nonfatal\":{\"undefined\":0}"
                        "}";
                }
            } else if (method == "get_nic_power") {
                // Alias for get_nic_power_info for backward compatibility
                brcmsmi_nic_hwmon_power_t power_info;
                brcmsmi_status_t status = nic_device->query_nic_power_info(power_info);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = "{"
                        "\"nic_power_async\":\"" + std::string(power_info.nic_power_async) + "\","
                        "\"nic_power_control\":\"" + std::string(power_info.nic_power_control) + "\","
                        "\"nic_power_runtime_active_time\":" + std::to_string(power_info.nic_power_runtime_active_time) + ","
                        "\"nic_power_runtime_status\":\"" + std::string(power_info.nic_power_runtime_status) + "\","
                        "\"nic_power_runtime_usage\":" + std::to_string(power_info.nic_power_runtime_usage) + ","
                        "\"nic_power_runtime_active_kids\":" + std::to_string(power_info.nic_power_runtime_active_kids) + ","
                        "\"nic_power_runtime_enabled\":\"" + std::string(power_info.nic_power_runtime_enabled) + "\","
                        "\"nic_power_runtime_suspended_time\":" + std::to_string(power_info.nic_power_runtime_suspended_time) + ""
                        "}";
                } else {
                    return status;
                }
            } else {
                return BRCMSMI_STATUS_NOT_SUPPORTED;
            }
        }
        // Handle Switch methods  
        else if (is_switch && switch_device != nullptr) {
            if (method == "get_switch_info") {
                brcmsmi_switch_info_t info;
                brcmsmi_status_t status = switch_device->query_switch_info(info);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = "{"
                        "\"switch_device_name\":\"" + std::string(info.switch_device_name) + "\","
                        "\"switch_part_number\":\"" + std::string(info.switch_part_number) + "\","
                        "\"switch_firmware_version\":\"" + std::string(info.switch_firmware_version) + "\","
                        "\"switch_uuid\":\"" + std::string(info.switch_uuid) + "\","
                        "\"switch_vendor_id\":\"" + std::string(info.switch_vendor_id) + "\","
                        "\"switch_device_id\":\"" + std::string(info.switch_device_id) + "\""
                        "}";
                } else {
                    return status;
                }
            } else if (method == "get_switch_device_uuid") {
                std::string uuid_str;
                brcmsmi_status_t status = switch_device->query_switch_uuid(uuid_str);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = uuid_str;
                } else {
                    return status;
                }
            } else if (method == "get_switch_metrics") {
                // Get comprehensive switch metrics using switch_device_info
                brcmsmi_switch_device_metric_t device_metrics;
                memset(&device_metrics, 0, sizeof(device_metrics));  // Initialize to prevent garbage
                brcmsmi_status_t status = switch_device->query_switch_device_info(device_metrics);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    // Helper lambda to safely convert potentially binary strings to UTF-8 safe JSON values
                    auto safe_string = [](const char* input) -> std::string {
                        if (input == nullptr) return "";
                        
                        std::string result;
                        const char* ptr = input;
                        while (*ptr != '\0') {
                            unsigned char c = static_cast<unsigned char>(*ptr);
                            // Only include printable ASCII characters
                            if (c >= 32 && c <= 126) {
                                // Escape JSON special characters
                                if (c == '"') {
                                    result += "\\\"";
                                } else if (c == '\\') {
                                    result += "\\\\";
                                } else if (c == '/') {
                                    result += "\\/";
                                } else {
                                    result += static_cast<char>(c);
                                }
                            } else if (c == '\n') {
                                result += "\\n";
                            } else if (c == '\r') {
                                result += "\\r";
                            } else if (c == '\t') {
                                result += "\\t";
                            } else if (c == '\b') {
                                result += "\\b";
                            } else if (c == '\f') {
                                result += "\\f";
                            } else {
                                // Convert non-printable characters to Unicode escape sequence
                                char unicode[7];
                                snprintf(unicode, sizeof(unicode), "\\u%04x", c);
                                result += unicode;
                            }
                            ptr++;
                        }
                        return result;
                    };

                    // Return comprehensive switch device metrics with safe string conversion
                    result = "{"
                        "\"brcm_device_aer_dev_correctable\":\"" + safe_string(device_metrics.brcm_device_aer_dev_correctable) + "\","
                        "\"brcm_device_aer_dev_fatal\":\"" + safe_string(device_metrics.brcm_device_aer_dev_fatal) + "\","
                        "\"brcm_device_aer_dev_nonfatal\":\"" + safe_string(device_metrics.brcm_device_aer_dev_nonfatal) + "\","
                        "\"brcm_device_ari_enabled\":\"" + safe_string(device_metrics.brcm_device_ari_enabled) + "\","
                        "\"brcm_device_broken_parity_status\":\"" + safe_string(device_metrics.brcm_device_broken_parity_status) + "\","
                        "\"brcm_device_class\":\"" + safe_string(device_metrics.brcm_device_class) + "\","
                        "\"brcm_device_config\":\"" + safe_string(device_metrics.brcm_device_config) + "\","
                        "\"brcm_device_consistent_dma_mask_bits\":\"" + safe_string(device_metrics.brcm_device_consistent_dma_mask_bits) + "\","
                        "\"brcm_device_current_link_speed\":\"" + safe_string(device_metrics.brcm_device_current_link_speed) + "\","
                        "\"brcm_device_current_link_width\":\"" + safe_string(device_metrics.brcm_device_current_link_width) + "\","
                        "\"brcm_device_d3cold_allowed\":\"" + safe_string(device_metrics.brcm_device_d3cold_allowed) + "\","
                        "\"brcm_device_device\":\"" + safe_string(device_metrics.brcm_device_device) + "\","
                        "\"brcm_device_dma_mask_bits\":\"" + safe_string(device_metrics.brcm_device_dma_mask_bits) + "\","
                        "\"brcm_device_driver_override\":\"" + safe_string(device_metrics.brcm_device_driver_override) + "\","
                        "\"brcm_device_enable\":\"" + safe_string(device_metrics.brcm_device_enable) + "\","
                        "\"brcm_device_irq\":\"" + safe_string(device_metrics.brcm_device_irq) + "\","
                        "\"brcm_device_local_cpulist\":\"" + safe_string(device_metrics.brcm_device_local_cpulist) + "\","
                        "\"brcm_device_local_cpus\":\"" + safe_string(device_metrics.brcm_device_local_cpus) + "\","
                        "\"brcm_device_max_link_speed\":\"" + safe_string(device_metrics.brcm_device_max_link_speed) + "\","
                        "\"brcm_device_max_link_width\":\"" + safe_string(device_metrics.brcm_device_max_link_width) + "\","
                        "\"brcm_device_modalias\":\"" + safe_string(device_metrics.brcm_device_modalias) + "\","
                        "\"brcm_device_msi_bus\":\"" + safe_string(device_metrics.brcm_device_msi_bus) + "\","
                        "\"brcm_device_numa_node\":\"" + safe_string(device_metrics.brcm_device_numa_node) + "\","
                        "\"brcm_device_pools\":\"" + safe_string(device_metrics.brcm_device_pools) + "\","
                        "\"brcm_device_power_state\":\"" + safe_string(device_metrics.brcm_device_power_state) + "\","
                        "\"brcm_device_reset_method\":\"" + safe_string(device_metrics.brcm_device_reset_method) + "\","
                        "\"brcm_device_resource\":\"" + safe_string(device_metrics.brcm_device_resource) + "\","
                        "\"brcm_device_revision\":\"" + safe_string(device_metrics.brcm_device_revision) + "\","
                        "\"brcm_device_subsystem_device\":\"" + safe_string(device_metrics.brcm_device_subsystem_device) + "\","
                        "\"brcm_device_subsystem_vendor\":\"" + safe_string(device_metrics.brcm_device_subsystem_vendor) + "\","
                        "\"brcm_device_uevent\":\"" + safe_string(device_metrics.brcm_device_uevent) + "\","
                        "\"brcm_device_vendor\":\"" + safe_string(device_metrics.brcm_device_vendor) + "\","
                        // Power metrics from embedded power structure
                        "\"brcm_power_async\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_async) + "\","
                        "\"brcm_power_control\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_control) + "\","
                        "\"brcm_power_runtime_active_kids\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_runtime_active_kids) + "\","
                        "\"brcm_power_runtime_active_time\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_runtime_active_time) + "\","
                        "\"brcm_power_runtime_enabled\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_runtime_enabled) + "\","
                        "\"brcm_power_runtime_status\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_runtime_status) + "\","
                        "\"brcm_power_runtime_suspended_time\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_runtime_suspended_time) + "\","
                        "\"brcm_power_runtime_usage\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_runtime_usage) + "\","
                        "\"brcm_power_wakeup\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_wakeup) + "\","
                        "\"brcm_power_wakeup_abort_count\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_wakeup_abort_count) + "\","
                        "\"brcm_power_wakeup_active\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_wakeup_active) + "\","
                        "\"brcm_power_wakeup_active_count\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_wakeup_active_count) + "\","
                        "\"brcm_power_wakeup_count\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_wakeup_count) + "\","
                        "\"brcm_power_wakeup_expire_count\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_wakeup_expire_count) + "\","
                        "\"brcm_power_wakeup_last_time_ms\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_wakeup_last_time_ms) + "\","
                        "\"brcm_power_wakeup_max_time_ms\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_wakeup_max_time_ms) + "\","
                        "\"brcm_power_wakeup_total_time_ms\":\"" + safe_string(device_metrics.brcm_device_power.brcm_power_wakeup_total_time_ms) + "\""
                        "}";
                } else {
                    result = "{\"status\":\"device_metrics_not_available\"}";
                }
            } else if (method == "get_switch_link_info") {
                brcmsmi_switch_link_metric_t link_info;
                brcmsmi_status_t status = switch_device->query_switch_link_info(link_info);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = "{"
                        "\"current_link_speed\":\"" + std::string(link_info.current_link_speed) + "\","
                        "\"max_link_speed\":\"" + std::string(link_info.max_link_speed) + "\","
                        "\"current_link_width\":\"" + std::string(link_info.current_link_width) + "\","
                        "\"max_link_width\":\"" + std::string(link_info.max_link_width) + "\""
                        "}";
                } else {
                    result = "{\"status\":\"link_info_not_available\"}";
                }
            } else if (method == "get_switch_numa_affinity") {
                int32_t numa_node;
                brcmsmi_status_t status = switch_device->query_switch_numa_affinity(&numa_node);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = std::to_string(numa_node);
                } else {
                    result = "-1";  // Invalid NUMA node
                }
            } else if (method == "get_switch_power_info") {
                brcmsmi_switch_power_metric_t power_info;
                brcmsmi_status_t status = switch_device->query_switch_power_info(power_info);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = "{"
                        "\"brcm_power_control\":\"" + std::string(power_info.brcm_power_control) + "\","
                        "\"brcm_power_runtime_active_kids\":\"" + std::string(power_info.brcm_power_runtime_active_kids) + "\","
                        "\"brcm_power_runtime_active_time\":\"" + std::string(power_info.brcm_power_runtime_active_time) + "\","
                        "\"brcm_power_runtime_enabled\":\"" + std::string(power_info.brcm_power_runtime_enabled) + "\","
                        "\"brcm_power_runtime_status\":\"" + std::string(power_info.brcm_power_runtime_status) + "\""
                        "}";
                } else {
                    return status;
                }
            } else if (method == "get_switch_topology") {
                // Get switch topology using link info and device metrics
                brcmsmi_switch_link_metric_t link_info;
                brcmsmi_status_t link_status = switch_device->query_switch_link_info(link_info);
                int32_t numa_node;
                brcmsmi_status_t numa_status = switch_device->query_switch_numa_affinity(&numa_node);
                
                if (link_status == BRCMSMI_STATUS_SUCCESS || numa_status == BRCMSMI_STATUS_SUCCESS) {
                    result = "{"
                        "\"numa_node\":\"" + (numa_status == BRCMSMI_STATUS_SUCCESS ? std::to_string(numa_node) : "unknown") + "\","
                        "\"link_speed\":\"" + (link_status == BRCMSMI_STATUS_SUCCESS ? std::string(link_info.current_link_speed) : "unknown") + "\","
                        "\"link_width\":\"" + (link_status == BRCMSMI_STATUS_SUCCESS ? std::string(link_info.current_link_width) : "unknown") + "\""
                        "}";
                } else {
                    result = "{\"status\":\"topology_not_available\"}";
                }
            } else if (method == "get_switch_cpu_affinity") {
                std::string cpu_affinity;
                brcmsmi_status_t status = switch_device->query_switch_cpu_affinity(cpu_affinity);
                if (status == BRCMSMI_STATUS_SUCCESS) {
                    result = cpu_affinity;
                } else {
                    result = "0";  // Default CPU affinity
                }
            } else if (method == "get_root_switch") {
                // Placeholder for root switch info
                result = "{\"status\":\"root_switch_not_implemented\"}";
            } else {
                return BRCMSMI_STATUS_NOT_SUPPORTED;
            }
        } else {
            return BRCMSMI_STATUS_INVALID_ARGS;
        }
        
        // Copy result to output buffer
        if (result.length() >= value_length) {
            return BRCMSMI_STATUS_INSUFFICIENT_SIZE;
        }
        
        strncpy(value, result.c_str(), value_length - 1);
        value[value_length - 1] = '\0';
        
        return BRCMSMI_STATUS_SUCCESS;
        
    } catch (const std::exception& e) {
        return BRCMSMI_STATUS_UNKNOWN_ERROR;
    }
}

}  // extern "C"

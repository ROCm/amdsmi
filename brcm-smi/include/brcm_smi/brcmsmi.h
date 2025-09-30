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


#ifndef BRCM_SMI_INCLUDE_BRCMSMI_H_
#define BRCM_SMI_INCLUDE_BRCMSMI_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>

/** \file brcmsmi.h
 *  Main header file for the Broadcom System Management Interface library.
 *
 *  All required function, structure, enum, etc. definitions should be defined
 *  in this file.
 *
 */

/**
 * @brief Maximum string length for BRCM SMI
 */
#define BRCMSMI_MAX_STRING_LENGTH 256

/**
 * @brief Return values for BRCM SMI functions
 */
typedef enum {
    BRCMSMI_STATUS_SUCCESS = 0,
    BRCMSMI_STATUS_INVALID_ARGS,
    BRCMSMI_STATUS_NOT_SUPPORTED,
    BRCMSMI_STATUS_FILE_ERROR,
    BRCMSMI_STATUS_PERMISSION,
    BRCMSMI_STATUS_OUT_OF_RESOURCES,
    BRCMSMI_STATUS_INTERNAL_EXCEPTION,
    BRCMSMI_STATUS_INPUT_OUT_OF_BOUNDS,
    BRCMSMI_STATUS_INIT_ERROR,
    BRCMSMI_STATUS_NOT_YET_IMPLEMENTED,
    BRCMSMI_STATUS_NOT_FOUND,
    BRCMSMI_STATUS_INSUFFICIENT_SIZE,
    BRCMSMI_STATUS_INTERRUPTED,
    BRCMSMI_STATUS_UNEXPECTED_SIZE,
    BRCMSMI_STATUS_NO_DATA,
    BRCMSMI_STATUS_UNEXPECTED_DATA,
    BRCMSMI_STATUS_BUSY,
    BRCMSMI_STATUS_REFCOUNT_OVERFLOW,
    BRCMSMI_STATUS_NOT_INITIALIZED,
    BRCMSMI_STATUS_ALREADY_INITIALIZED,
    BRCMSMI_STATUS_UNKNOWN_ERROR = 0xFFFFFFFF
} brcmsmi_status_t;

/**
 * @brief Processor types supported by BRCM SMI
 */
typedef enum {
    BRCMSMI_PROCESSOR_TYPE_UNKNOWN = 0,
    BRCMSMI_PROCESSOR_TYPE_NIC,
    BRCMSMI_PROCESSOR_TYPE_SWITCH,
    BRCMSMI_PROCESSOR_TYPE_ALL
} brcmsmi_processor_type_t;

/**
 * @brief BDF (Bus:Device:Function) information
 */
typedef struct {
    uint64_t domain_number;
    uint64_t bus_number;
    uint64_t device_number;
    uint64_t function_number;
} brcmsmi_bdf_t;

/**
 * @brief BRCM NIC Information
 */
typedef struct {
    char nic_device_name[BRCMSMI_MAX_STRING_LENGTH];
    char nic_part_number[BRCMSMI_MAX_STRING_LENGTH];
    char nic_firmware_version[BRCMSMI_MAX_STRING_LENGTH];
    char nic_uuid[BRCMSMI_MAX_STRING_LENGTH];
    brcmsmi_bdf_t nic_bdf;
} brcmsmi_nic_info_t;

/**
 * @brief BRCM Switch Information
 */
typedef struct {
    char switch_device_name[BRCMSMI_MAX_STRING_LENGTH];
    char switch_part_number[BRCMSMI_MAX_STRING_LENGTH];
    char switch_firmware_version[BRCMSMI_MAX_STRING_LENGTH];
    char switch_uuid[BRCMSMI_MAX_STRING_LENGTH];
    brcmsmi_bdf_t switch_bdf;
    char switch_vendor_id[BRCMSMI_MAX_STRING_LENGTH];
    char switch_device_id[BRCMSMI_MAX_STRING_LENGTH];
    char switch_subsystem_vendor[BRCMSMI_MAX_STRING_LENGTH];
    char switch_subsystem_device[BRCMSMI_MAX_STRING_LENGTH];
    char switch_class[BRCMSMI_MAX_STRING_LENGTH];
    char switch_revision[BRCMSMI_MAX_STRING_LENGTH];
    char switch_irq[BRCMSMI_MAX_STRING_LENGTH];
    char switch_numa_node[BRCMSMI_MAX_STRING_LENGTH];
    char switch_current_link_speed[BRCMSMI_MAX_STRING_LENGTH];
    char switch_max_link_speed[BRCMSMI_MAX_STRING_LENGTH];
    char switch_current_link_width[BRCMSMI_MAX_STRING_LENGTH];
    char switch_max_link_width[BRCMSMI_MAX_STRING_LENGTH];
    char switch_power_control[BRCMSMI_MAX_STRING_LENGTH];
    char switch_power_runtime_status[BRCMSMI_MAX_STRING_LENGTH];
    char switch_power_runtime_enabled[BRCMSMI_MAX_STRING_LENGTH];
} brcmsmi_switch_info_t;

/**
 * @brief BRCM NIC Temperature Information
 */
typedef struct {
    uint32_t nic_temp_crit_alarm;
    uint32_t nic_temp_emergency_alarm;
    uint32_t nic_temp_shutdown_alarm;
    uint32_t nic_temp_max_alarm;
    uint32_t nic_temp_crit;
    uint32_t nic_temp_emergency;
    uint32_t nic_temp_input;
    uint32_t nic_temp_max;
    uint32_t nic_temp_shutdown;
} brcmsmi_nic_temperature_metric_t;

/**
 * @brief BRCM NIC Firmware Information
 */
typedef struct {
    char nic_fw_pkg_version[BRCMSMI_MAX_STRING_LENGTH];
    char nic_fw_efi_version[BRCMSMI_MAX_STRING_LENGTH];
    char nic_fw_version[BRCMSMI_MAX_STRING_LENGTH];
    char nic_fw_ncsi_version[BRCMSMI_MAX_STRING_LENGTH];
    char nic_fw_roce_version[BRCMSMI_MAX_STRING_LENGTH];
} brcmsmi_nic_firmware_t;

/**
 * @brief BRCM NIC HWMON Power Information
 */
typedef struct {
    char nic_power_async[BRCMSMI_MAX_STRING_LENGTH];
    char nic_power_control[BRCMSMI_MAX_STRING_LENGTH];
    uint32_t nic_power_runtime_active_time;
    char nic_power_runtime_status[BRCMSMI_MAX_STRING_LENGTH];
    uint32_t nic_power_runtime_usage;
    uint32_t nic_power_runtime_active_kids;
    char nic_power_runtime_enabled[BRCMSMI_MAX_STRING_LENGTH];
    uint32_t nic_power_runtime_suspended_time;
} brcmsmi_nic_hwmon_power_t;

/**
 * @brief BRCM NIC HWMON Device Information
 */
typedef struct {
    char nic_device_aer_dev_correctable[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_aer_dev_fatal[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_aer_dev_nonfatal[BRCMSMI_MAX_STRING_LENGTH];
    uint32_t nic_device_ari_enabled;
    uint32_t nic_device_broken_parity_status;
    char nic_device_class[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_config[BRCMSMI_MAX_STRING_LENGTH];
    uint32_t nic_device_consistent_dma_mask_bits;
    char nic_device_current_link_speed[BRCMSMI_MAX_STRING_LENGTH];
    uint32_t nic_device_current_link_width;
    uint32_t nic_device_d3cold_allowed;
    char nic_device_device[BRCMSMI_MAX_STRING_LENGTH];
    uint32_t nic_device_dma_mask_bits;
    char nic_device_driver_override[BRCMSMI_MAX_STRING_LENGTH];
    uint32_t nic_device_enable;
    uint32_t nic_device_irq;
    char nic_device_local_cpulist[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_local_cpus[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_max_link_speed[BRCMSMI_MAX_STRING_LENGTH];
    uint32_t nic_device_max_link_width;
    char nic_device_modalias[BRCMSMI_MAX_STRING_LENGTH];
    uint32_t nic_device_msi_bus;
    uint32_t nic_device_numa_node;
    char nic_device_pools[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_power_state[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_reset_method[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_resource[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_revision[BRCMSMI_MAX_STRING_LENGTH];
    uint32_t nic_device_sriov_drivers_autoprobe;
    uint32_t nic_device_sriov_numvfs;
    uint32_t nic_device_sriov_offset;
    uint32_t nic_device_sriov_stride;
    uint32_t nic_device_sriov_totalvfs;
    uint32_t nic_device_sriov_vf_device;
    uint32_t nic_device_sriov_vf_total_msix;
    char nic_device_subsystem_device[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_subsystem_vendor[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_uevent[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_vendor[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_vpd[BRCMSMI_MAX_STRING_LENGTH];
} brcmsmi_nic_hwmon_device_t;

/**
 * @brief BRCM Switch Link Information
 */
typedef struct {
    char current_link_speed[BRCMSMI_MAX_STRING_LENGTH];
    char max_link_speed[BRCMSMI_MAX_STRING_LENGTH];
    char current_link_width[BRCMSMI_MAX_STRING_LENGTH];
    char max_link_width[BRCMSMI_MAX_STRING_LENGTH];
} brcmsmi_switch_link_metric_t;

/**
 * @brief BRCM Switch Power Information
 */
typedef struct {
    char brcm_power_async[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_control[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_runtime_active_kids[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_runtime_active_time[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_runtime_enabled[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_runtime_status[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_runtime_suspended_time[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_runtime_usage[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_wakeup[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_wakeup_abort_count[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_wakeup_active[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_wakeup_active_count[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_wakeup_count[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_wakeup_expire_count[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_wakeup_last_time_ms[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_wakeup_max_time_ms[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_power_wakeup_total_time_ms[BRCMSMI_MAX_STRING_LENGTH];
} brcmsmi_switch_power_metric_t;

/**
 * @brief BRCM Switch Device Information
 */
typedef struct {
    char brcm_device_aer_dev_correctable[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_aer_dev_fatal[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_aer_dev_nonfatal[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_ari_enabled[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_broken_parity_status[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_class[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_config[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_consistent_dma_mask_bits[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_current_link_speed[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_current_link_width[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_d3cold_allowed[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_device[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_dma_mask_bits[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_driver_override[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_enable[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_irq[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_local_cpulist[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_local_cpus[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_max_link_speed[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_max_link_width[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_modalias[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_msi_bus[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_numa_node[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_pools[BRCMSMI_MAX_STRING_LENGTH];
    brcmsmi_switch_power_metric_t brcm_device_power;
    char brcm_device_power_state[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_reset_method[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_resource[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_revision[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_subsystem_device[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_subsystem_vendor[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_uevent[BRCMSMI_MAX_STRING_LENGTH];
    char brcm_device_vendor[BRCMSMI_MAX_STRING_LENGTH];
} brcmsmi_switch_device_metric_t;

/**
 * @brief BRCM NIC METRIC Info
 *
 * @cond @tag{gpu_bm_linux} @tag{host} @endcond
 */
typedef struct{
    brcmsmi_nic_hwmon_power_t nic_power;
    brcmsmi_nic_temperature_metric_t nic_temperature;

    char nic_device_aer_dev_correctable[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_aer_dev_fatal[BRCMSMI_MAX_STRING_LENGTH];
    char nic_device_aer_dev_nonfatal[BRCMSMI_MAX_STRING_LENGTH];
}brcmsmi_nic_hwmon_metrics_t;

typedef struct {
    char  brcm_device_aer_dev_correctable[BRCMSMI_MAX_STRING_LENGTH];
    char  brcm_device_aer_dev_fatal[BRCMSMI_MAX_STRING_LENGTH];
    char  brcm_device_aer_dev_nonfatal[BRCMSMI_MAX_STRING_LENGTH];
    brcmsmi_switch_power_metric_t brcm_power;
} brcmsmi_switch_metric_t;

/**
 * @brief Opaque handle for BRCM processor
 */
typedef void* brcmsmi_processor_handle;

/**
 * @brief Opaque handle for BRCM socket
 */
typedef void* brcmsmi_socket_handle;



/**
 * @brief Initialize BRCM SMI library
 *
 * @param[in] init_flags Initialization flags
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_init(uint64_t init_flags);

/**
 * @brief Shutdown BRCM SMI library
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_shutdown();

/**
 * @brief Get number of sockets
 *
 * @param[out] socket_count Number of sockets
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_socket_handles(uint32_t *socket_count, brcmsmi_socket_handle *socket_handles);

/**
 * @brief Get NIC processor handles
 *
 * @param[in] socket_handle Socket handle
 * @param[out] processor_count Number of processors
 * @param[out] processor_handles Array of processor handles
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_nic_processor_handles(brcmsmi_socket_handle socket_handle,
                                                   uint32_t *processor_count,
                                                   brcmsmi_processor_handle **processor_handles);

/**
 * @brief Get switch processor handles
 *
 * @param[in] socket_handle Socket handle
 * @param[out] processor_count Number of processors
 * @param[out] processor_handles Array of processor handles
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_switch_processor_handles(brcmsmi_socket_handle socket_handle,
                                                      uint32_t *processor_count,
                                                      brcmsmi_processor_handle **processor_handles);

/**
 * @brief Get NIC information
 *
 * @param[in] processor_handle Processor handle
 * @param[out] info NIC information
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_nic_info(brcmsmi_processor_handle processor_handle, brcmsmi_nic_info_t *info);

/**
 * @brief Get NIC temperature information
 *
 * @param[in] processor_handle Processor handle
 * @param[out] info Temperature information
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_nic_temp_info(brcmsmi_processor_handle processor_handle,
                                           brcmsmi_nic_temperature_metric_t *info);

/**
 * @brief Get NIC power information
 *
 * @param[in] processor_handle Processor handle
 * @param[out] info Power information
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_nic_power_info(brcmsmi_processor_handle processor_handle,
                                            brcmsmi_nic_hwmon_power_t *info);

/**
 * @brief Get NIC device information
 *
 * @param[in] processor_handle Processor handle
 * @param[out] info Device information
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_nic_device_info(brcmsmi_processor_handle processor_handle,
                                             brcmsmi_nic_hwmon_device_t *info);

/**
 * @brief Get NIC firmware information
 *
 * @param[in] processor_handle Processor handle
 * @param[out] info Firmware information
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_nic_fw_info(brcmsmi_processor_handle processor_handle,
                                         brcmsmi_nic_firmware_t *info);

/**
 * @brief Get switch link information
 *
 * @param[in] processor_handle Processor handle
 * @param[out] info Link information
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_switch_link_info(brcmsmi_processor_handle processor_handle,
                                              brcmsmi_switch_link_metric_t *info);

/**
 * @brief Get switch device information
 *
 * @param[in] processor_handle Processor handle
 * @param[out] info Device information
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_switch_device_info(brcmsmi_processor_handle processor_handle,
                                                brcmsmi_switch_device_metric_t *info);

/**
 * @brief Get switch power information
 *
 * @param[in] processor_handle Processor handle
 * @param[out] info Power information
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_switch_power_info(brcmsmi_processor_handle processor_handle,
                                               brcmsmi_switch_power_metric_t *info);

/**
 * @brief Get comprehensive switch information
 *
 * @param[in] processor_handle Processor handle
 * @param[out] info Comprehensive switch information
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_switch_info(brcmsmi_processor_handle processor_handle, brcmsmi_switch_info_t *info);

/**
 * @brief Device discovery result structure
 */
typedef struct {
    uint32_t nic_count;
    uint32_t switch_count;
    uint32_t total_count;
} brcmsmi_discovery_result_t;

/**
 * @brief Device vectors structure for ROCm SMI integration
 */
typedef struct {
    void** nic_devices;        // Array of NIC device pointers
    void** switch_devices;     // Array of Switch device pointers
    uint32_t nic_count;
    uint32_t switch_count;
} brcmsmi_device_vectors_t;

/**
 * @brief Discover all BRCM devices (NICs and Switches)
 *
 * This function discovers all BRCM devices in the system and populates
 * the internal device lists. It should be called during initialization.
 *
 * @param[out] result Discovery results with device counts
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 * @retval ::BRCMSMI_STATUS_INVALID_ARGS if result parameter is invalid
 * @retval ::BRCMSMI_STATUS_FILE_ERROR if device discovery fails
 */
brcmsmi_status_t brcmsmi_discover_devices(brcmsmi_discovery_result_t* result);

/**
 * @brief Get BRCM device vectors for ROCm SMI integration
 *
 * This function performs complete BRCM device discovery and returns
 * device vectors that can be used directly by ROCm SMI. This replaces
 * the need for ROCm SMI to have its own DiscoverBRCMDevices function.
 *
 * @param[out] device_vectors Structure containing device vectors and counts
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 * @retval ::BRCMSMI_STATUS_INVALID_ARGS if device_vectors parameter is invalid
 * @retval ::BRCMSMI_STATUS_FILE_ERROR if device discovery fails
 */
brcmsmi_status_t brcmsmi_get_device_vectors(brcmsmi_device_vectors_t* device_vectors);

/**
 * @brief Get processed BRCM device vectors with BDF processing and sorting
 *
 * This function discovers BRCM devices, creates Device objects, processes BDF IDs,
 * and sorts devices by BDF. This includes all the device processing logic that
 * was previously handled in ROCm SMI.
 *
 * @param[out] device_vectors Pointer to device vectors structure to be populated
 *                           with processed Device objects
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 * @retval ::BRCMSMI_STATUS_INVALID_ARGS if device_vectors is null
 * @retval ::BRCMSMI_STATUS_INIT_ERROR if BRCM SMI is not initialized
 */
brcmsmi_status_t brcmsmi_get_processed_device_vectors(brcmsmi_device_vectors_t* device_vectors);

/**
 * @brief Get managed BRCM device vectors using DeviceManager
 *
 * This function uses the BRCM SMI DeviceManager to discover, process, and manage
 * BRCM devices. All device vectors are managed internally by the BRCM SMI library,
 * providing complete separation from ROCm SMI.
 *
 * @param[out] device_vectors Pointer to device vectors structure to be populated
 *                           with managed Device objects
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 * @retval ::BRCMSMI_STATUS_INVALID_ARGS if device_vectors is null
 * @retval ::BRCMSMI_STATUS_INIT_ERROR if BRCM SMI is not initialized
 */
brcmsmi_status_t brcmsmi_get_managed_device_vectors(brcmsmi_device_vectors_t* device_vectors);


//==============================================================================
// BRCM SMI Compatibility Functions
//==============================================================================


/**
 * @brief Get BRCM processor handles for BRCM SMI compatibility
 *
 * @param[in] socket_index Socket index
 * @param[in] device_type Device type (NIC or Switch)
 * @param[out] processor_count Number of processors found
 * @param[out] processor_handles Array of processor handles
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_brcm_processor_handles(uint32_t socket_index,
                                                   brcmsmi_processor_type_t device_type,
                                                   uint32_t *processor_count,
                                                   brcmsmi_processor_handle *processor_handles);

// BRCM SMI compatible init/shutdown functions removed - use brcmsmi_init/brcmsmi_shutdown directly

/**
 * @brief Get BRCM processor handles by device type
 *
 * @param[in] socket_handle Socket handle
 * @param[in] device_type Device type (NIC, Switch, or All)
 * @param[in,out] processor_count Input: max handles to return, Output: actual count
 * @param[out] processor_handles Array of processor handles
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_brcm_processor_handles_by_type(brcmsmi_socket_handle socket_handle,
                                                           brcmsmi_processor_type_t device_type,
                                                           uint32_t *processor_count,
                                                           brcmsmi_processor_handle *processor_handles);

/**
 * @brief Get BRCM processor handles by BDF (Bus:Device:Function)
 *
 * @param[in] socket_handle Socket handle
 * @param[in] bdf BDF structure
 * @param[in,out] processor_count Input: max handles to return, Output: actual count
 * @param[out] processor_handles Array of processor handles
 *
 * @retval ::BRCMSMI_STATUS_SUCCESS is returned upon successful call
 */
brcmsmi_status_t brcmsmi_get_brcm_processor_handles_by_bdf(brcmsmi_socket_handle socket_handle,
                                                          brcmsmi_bdf_t bdf,
                                                          uint32_t *processor_count,
                                                          brcmsmi_processor_handle *processor_handles);

/**
 * @brief Generic string retrieval method for BRCM devices
 * 
 * This is a unified interface for retrieving string-based information from BRCM devices.
 * It supports various methods for both NIC and Switch devices.
 * 
 * Supported method names:
 * 
 * NIC Methods:
 * - "get_nic_info": Get NIC basic information (JSON format)
 * - "get_nic_device_uuid": Get NIC device UUID
 * - "get_nic_metrics": Get NIC device metrics (JSON format)
 * - "get_nic_numa_affinity": Get NIC NUMA affinity (node number)
 * - "get_nic_power_info": Get NIC power information (JSON format)
 * - "get_nic_temperature": Get NIC temperature information (JSON format)
 * - "get_nic_firmware_info": Get NIC firmware information (JSON format)
 * - "get_nic_topology": Get NIC topology information (JSON format)
 * - "get_nic_cpu_affinity": Get NIC CPU affinity information
 * 
 * Switch Methods:
 * - "get_switch_info": Get Switch basic information (JSON format)
 * - "get_switch_device_uuid": Get Switch device UUID
 * - "get_switch_metrics": Get Switch device metrics (JSON format)
 * - "get_switch_link_info": Get Switch link information (JSON format)
 * - "get_switch_numa_affinity": Get Switch NUMA affinity (node number)
 * - "get_switch_power_info": Get Switch power information (JSON format)
 * - "get_switch_topology": Get Switch topology information (JSON format)
 * - "get_switch_cpu_affinity": Get Switch CPU affinity information
 * - "get_root_switch": Get root switch information (JSON format)
 * 
 * @param[in] processor_handle Handle to the processor (NIC or Switch)
 * @param[in] method_name Name of the method to call
 * @param[in] value_length Maximum length of the output buffer
 * @param[out] value Output buffer to store the retrieved string
 * @retval ::BRCMSMI_STATUS_SUCCESS on success
 * @retval ::BRCMSMI_STATUS_INVALID_ARGS if parameters are invalid
 * @retval ::BRCMSMI_STATUS_NOT_SUPPORTED if method is not supported
 * @retval ::BRCMSMI_STATUS_NOT_INITIALIZED if not initialized
 * @retval ::BRCMSMI_STATUS_INSUFFICIENT_SIZE if output buffer is too small
 */
brcmsmi_status_t brcmsmi_getString(brcmsmi_processor_handle processor_handle,
                                   const char* method_name,
                                   size_t value_length,
                                   char* value);

#ifdef __cplusplus
}
#endif

#endif  // BRCM_SMI_INCLUDE_BRCMSMI_H_

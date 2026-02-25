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


#ifndef BRCM_SMI_INCLUDE_BRCM_SMI_DISCOVERY_H_
#define BRCM_SMI_INCLUDE_BRCM_SMI_DISCOVERY_H_

#include "brcmsmi.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Check if a file exists
 * @param filename Path to the file to check
 * @return true if file exists, false otherwise
 */
bool FileExists(const char* filename);

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
namespace brcm {
namespace smi {

/**
 * @brief Discover BRCM devices and populate discovery result
 * @param result Pointer to discovery result structure to populate
 * @return brcmsmi_status_t Status of the operation
 */
brcmsmi_status_t DiscoverBRCMDevices(brcmsmi_discovery_result_t* result);

/**
 * @brief Get BRCM device vectors with basic device information
 * @param device_vectors Pointer to device vectors structure to populate
 * @return brcmsmi_status_t Status of the operation
 */
brcmsmi_status_t GetBRCMDeviceVectors(brcmsmi_device_vectors_t* device_vectors);

/**
 * @brief Get processed BRCM devices with enhanced Device objects and BDF processing
 * @param device_vectors Pointer to device vectors structure to populate
 * @return brcmsmi_status_t Status of the operation
 */
brcmsmi_status_t GetProcessedBRCMDevices(brcmsmi_device_vectors_t* device_vectors);

/**
 * @brief Get managed device vectors using DeviceManager
 * @param device_vectors Pointer to device vectors structure to populate
 * @return brcmsmi_status_t Status of the operation
 */
brcmsmi_status_t GetManagedDeviceVectors(brcmsmi_device_vectors_t* device_vectors);

}  // namespace smi
}  // namespace brcm
#endif

#endif  // BRCM_SMI_INCLUDE_BRCM_SMI_DISCOVERY_H_

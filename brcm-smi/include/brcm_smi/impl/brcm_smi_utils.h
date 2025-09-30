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


#ifndef BRCM_SMI_INCLUDE_IMPL_BRCM_SMI_UTILS_H_
#define BRCM_SMI_INCLUDE_IMPL_BRCM_SMI_UTILS_H_

#include <string>
#include <pthread.h>
#include "brcm_smi/brcmsmi.h"

namespace brcm {
namespace smi {

/**
 * @brief Get mutex for thread safety
 */
pthread_mutex_t* GetMutex(uint32_t device_id);

/**
 * @brief Get string value from sysfs file
 */
std::string smi_brcm_get_value_string(std::string filePath, std::string fileName);

/**
 * @brief Get uint32 value from sysfs file
 */
uint32_t smi_brcm_get_value_u32(std::string filePath, std::string fileName);

/**
 * @brief Execute command and get output data
 */
brcmsmi_status_t smi_brcm_execute_cmd_get_data(std::string command, std::string *data);

}  // namespace smi
}  // namespace brcm

#endif  // BRCM_SMI_INCLUDE_IMPL_BRCM_SMI_UTILS_H_

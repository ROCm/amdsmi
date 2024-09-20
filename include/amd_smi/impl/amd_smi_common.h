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

#ifndef AMD_SMI_INCLUDE_AMD_SMI_COMMON_H_
#define AMD_SMI_INCLUDE_AMD_SMI_COMMON_H_

#include <map>
#include "rocm_smi/rocm_smi.h"
#include "amd_smi/amdsmi.h"

namespace amd {
namespace smi {

// Define a map of rsmi status codes to amdsmi status codes
const std::map<rsmi_status_t, amdsmi_status_t> rsmi_status_map = {
    {RSMI_STATUS_SUCCESS, AMDSMI_STATUS_SUCCESS},
    {RSMI_STATUS_INVALID_ARGS, AMDSMI_STATUS_INVAL},
    {RSMI_STATUS_NOT_SUPPORTED, AMDSMI_STATUS_NOT_SUPPORTED},
    {RSMI_STATUS_FILE_ERROR, AMDSMI_STATUS_FILE_ERROR},
    {RSMI_STATUS_PERMISSION, AMDSMI_STATUS_NO_PERM},
    {RSMI_STATUS_OUT_OF_RESOURCES, AMDSMI_STATUS_OUT_OF_RESOURCES},
    {RSMI_STATUS_INTERNAL_EXCEPTION, AMDSMI_STATUS_INTERNAL_EXCEPTION},
    {RSMI_STATUS_INPUT_OUT_OF_BOUNDS, AMDSMI_STATUS_INPUT_OUT_OF_BOUNDS},
    {RSMI_STATUS_INIT_ERROR, AMDSMI_STATUS_NOT_INIT},
    {RSMI_INITIALIZATION_ERROR, AMDSMI_STATUS_NOT_INIT},
    {RSMI_STATUS_NOT_YET_IMPLEMENTED, AMDSMI_STATUS_NOT_YET_IMPLEMENTED},
    {RSMI_STATUS_NOT_FOUND, AMDSMI_STATUS_NOT_FOUND},
    {RSMI_STATUS_INSUFFICIENT_SIZE, AMDSMI_STATUS_INSUFFICIENT_SIZE},
    {RSMI_STATUS_INTERRUPT, AMDSMI_STATUS_INTERRUPT},
    {RSMI_STATUS_UNEXPECTED_SIZE, AMDSMI_STATUS_UNEXPECTED_SIZE},
    {RSMI_STATUS_NO_DATA, AMDSMI_STATUS_NO_DATA},
    {RSMI_STATUS_UNEXPECTED_DATA, AMDSMI_STATUS_UNEXPECTED_DATA},
    {RSMI_STATUS_BUSY, AMDSMI_STATUS_BUSY},
    {RSMI_STATUS_REFCOUNT_OVERFLOW, AMDSMI_STATUS_REFCOUNT_OVERFLOW},
    {RSMI_STATUS_SETTING_UNAVAILABLE, AMDSMI_STATUS_SETTING_UNAVAILABLE},
    {RSMI_STATUS_AMDGPU_RESTART_ERR, AMDSMI_STATUS_AMDGPU_RESTART_ERR},
    {RSMI_STATUS_UNKNOWN_ERROR, AMDSMI_STATUS_UNKNOWN_ERROR},
};

const std::map<unsigned, amdsmi_vram_type_t> vram_type_map = {
    {0, AMDSMI_VRAM_TYPE_UNKNOWN},
    {1, AMDSMI_VRAM_TYPE_GDDR1},
    {2, AMDSMI_VRAM_TYPE_DDR2},
    {3, AMDSMI_VRAM_TYPE_GDDR3},
    {4, AMDSMI_VRAM_TYPE_GDDR4},
    {5, AMDSMI_VRAM_TYPE_GDDR5},
    {6, AMDSMI_VRAM_TYPE_HBM},
    {7, AMDSMI_VRAM_TYPE_DDR3},
    {8, AMDSMI_VRAM_TYPE_DDR4},
    {9, AMDSMI_VRAM_TYPE_GDDR6},
};

amdsmi_status_t rsmi_to_amdsmi_status(rsmi_status_t status);

amdsmi_vram_type_t vram_type_value(unsigned type);

#ifdef ENABLE_ESMI_LIB
// Define a map of esmi status codes to amdsmi status codes
const std::map<esmi_status_t, amdsmi_status_t> esmi_status_map = {
    {ESMI_SUCCESS, AMDSMI_STATUS_SUCCESS},
    {ESMI_INITIALIZED, AMDSMI_STATUS_SUCCESS},
    {ESMI_INVALID_INPUT, AMDSMI_STATUS_INVAL},
    {ESMI_NOT_SUPPORTED, AMDSMI_STATUS_NOT_SUPPORTED},
    {ESMI_PERMISSION, AMDSMI_STATUS_NO_PERM},
    {ESMI_INTERRUPTED, AMDSMI_STATUS_INTERRUPT},
    {ESMI_IO_ERROR, AMDSMI_STATUS_IO},
    {ESMI_FILE_ERROR, AMDSMI_STATUS_FILE_ERROR},
    {ESMI_NO_MEMORY, AMDSMI_STATUS_OUT_OF_RESOURCES},
    {ESMI_DEV_BUSY, AMDSMI_STATUS_BUSY},
    {ESMI_NOT_INITIALIZED, AMDSMI_STATUS_NOT_INIT},
    {ESMI_UNEXPECTED_SIZE, AMDSMI_STATUS_UNEXPECTED_SIZE},
    {ESMI_UNKNOWN_ERROR, AMDSMI_STATUS_UNKNOWN_ERROR},
    {ESMI_NO_ENERGY_DRV, AMDSMI_STATUS_NO_ENERGY_DRV},
    {ESMI_NO_MSR_DRV, AMDSMI_STATUS_NO_MSR_DRV},
    {ESMI_NO_HSMP_DRV, AMDSMI_STATUS_NO_HSMP_DRV},
    {ESMI_NO_HSMP_SUP, AMDSMI_STATUS_NO_HSMP_SUP},
    {ESMI_NO_DRV, AMDSMI_STATUS_NO_DRV},
    {ESMI_FILE_NOT_FOUND, AMDSMI_STATUS_FILE_NOT_FOUND},
    {ESMI_ARG_PTR_NULL, AMDSMI_STATUS_ARG_PTR_NULL},
    {ESMI_HSMP_TIMEOUT, AMDSMI_STATUS_HSMP_TIMEOUT},
    {ESMI_NO_HSMP_MSG_SUP, AMDSMI_STATUS_NO_HSMP_MSG_SUP},
};

amdsmi_status_t esmi_to_amdsmi_status(esmi_status_t status);
#endif
}  // namespace smi
}  // namespace amd

#endif  // AMD_SMI_INCLUDE_AMD_SMI_COMMON_H_

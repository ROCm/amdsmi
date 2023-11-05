/*
 * =============================================================================
 * The University of Illinois/NCSA
 * Open Source License (NCSA)
 *
 * Copyright (c) 2023, Advanced Micro Devices, Inc.
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

#include <functional>
#include "amd_smi/impl/amd_smi_cpu_socket.h"
#include <cpuid.h>

namespace amd {
namespace smi {

AMDSmiCpuSocket::~AMDSmiCpuSocket() {}

amdsmi_status_t AMDSmiCpuSocket::set_socket_id(uint32_t idx, uint32_t socket_id) {
    socket_id = idx;
    return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t AMDSmiCpuSocket::get_cpu_vendor() {
    uint32_t eax, ebx, ecx, edx;

    if (!__get_cpuid(0, &eax, &ebx, &ecx, &edx))
        return AMDSMI_STATUS_IO;

    /* check if the value in ebx, ecx, edx matches "AuthenticAMD" string */
    if (ebx != 0x68747541 || ecx != 0x444d4163 || edx != 0x69746e65)
        return AMDSMI_STATUS_NON_AMD_CPU;

    return AMDSMI_STATUS_SUCCESS;
}

}  // namespace smi
}  // namespace amd

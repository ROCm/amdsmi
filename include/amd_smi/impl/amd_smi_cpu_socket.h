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

#ifndef AMD_SMI_INCLUDE_AMD_SMI_CPU_SOCKET_H_
#define AMD_SMI_INCLUDE_AMD_SMI_CPU_SOCKET_H_

#include <string>
#include <algorithm>
#include <vector>
#include "amd_smi/amdsmi.h"
#include "amd_smi/impl/amd_smi_processor.h"
#include "amd_smi/impl/amd_smi_cpu_core.h"

namespace amd {
namespace smi {

/*Subclass CPU Socket*/
class AMDSmiCpuSocket : public AMDSmiProcessor {
 public:
    explicit AMDSmiCpuSocket(const uint32_t& id):AMDSmiProcessor(AMD_CPU),socket_identifier_(id) {}

    virtual ~AMDSmiCpuSocket() {}

    amdsmi_status_t get_cpu_vendor() { return AMDSMI_STATUS_SUCCESS; }
    uint32_t get_cpu_id() const { return cpu_id_; }
    const uint32_t& get_socket_id() const { return socket_identifier_; }

    void add_processor(AMDSmiProcessor* processor) { processors_.push_back(processor); }
    std::vector<AMDSmiProcessor*>& get_processors() { return processors_;}
    amdsmi_status_t get_processor_count(uint32_t* processor_count) const;

 private:
    uint32_t cpu_id_;
    uint32_t socket_identifier_;
    std::vector<AMDSmiProcessor*> processors_;
};

}  // namespace smi
}  // namespace amd

#endif  // AMD_SMI_INCLUDE_AMD_SMI_CPU_SOCKET_H_

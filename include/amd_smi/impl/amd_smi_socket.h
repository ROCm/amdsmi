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

#ifndef AMD_SMI_INCLUDE_AMD_SMI_SOCKET_H_
#define AMD_SMI_INCLUDE_AMD_SMI_SOCKET_H_

#include <string>
#include <algorithm>
#include <vector>
#include "amd_smi/amdsmi.h"
#include "amd_smi/impl/amd_smi_processor.h"

namespace amd {
namespace smi {

class AMDSmiSocket {
 public:
    explicit AMDSmiSocket(const std::string& id) : socket_identifier_(id) {}
    explicit AMDSmiSocket(uint32_t index) : sindex_(index) {}
    ~AMDSmiSocket();
    const std::string& get_socket_id() const { return socket_identifier_;}
    uint32_t get_socket_index() { return sindex_;}
    void add_processor(AMDSmiProcessor* processor) {
        switch (processor->get_processor_type()) {
        case AMDSMI_PROCESSOR_TYPE_AMD_GPU:
            processors_.push_back(processor);
            break;
        case AMDSMI_PROCESSOR_TYPE_AMD_CPU:
            cpu_processors_.push_back(processor);
            break;
        case AMDSMI_PROCESSOR_TYPE_AMD_CPU_CORE:
            cpu_core_processors_.push_back(processor);
            break;
        default:
            break;
        }
    }
    std::vector<AMDSmiProcessor*>& get_processors() { return processors_;}
    std::vector<AMDSmiProcessor*>& get_processors(processor_type_t type) {
      switch (type) {
      case AMDSMI_PROCESSOR_TYPE_AMD_GPU:
          return processors_;
      case AMDSMI_PROCESSOR_TYPE_AMD_CPU:
          return cpu_processors_;
      case AMDSMI_PROCESSOR_TYPE_AMD_CPU_CORE:
          return cpu_core_processors_;
      default:
          return processors_;
      }
    }
    amdsmi_status_t get_processor_count(uint32_t* processor_count) const;
    amdsmi_status_t get_processor_count(processor_type_t type, uint32_t* processor_count) const;
 private:
    uint32_t sindex_;
    std::string socket_identifier_;
    std::vector<AMDSmiProcessor*> processors_;
    std::vector<AMDSmiProcessor*> cpu_processors_;
    std::vector<AMDSmiProcessor*> cpu_core_processors_;
};

}  // namespace smi
}  // namespace amd

#endif  // AMD_SMI_INCLUDE_AMD_SMI_SOCKET_H_

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

#ifndef AMD_SMI_INCLUDE_AMD_SMI_SOCKET_H_
#define AMD_SMI_INCLUDE_AMD_SMI_SOCKET_H_

#include <string>
#include <algorithm>
#include <vector>
#include "amd_smi/amd_smi.h"
#include "amd_smi/impl/amd_smi_device.h"

namespace amd {
namespace smi {

class AMDSmiSocket {
 public:
    explicit AMDSmiSocket(const std::string& id) : socket_identifier_(id) {}
    ~AMDSmiSocket();
    const std::string& get_socket_id() const { return socket_identifier_;}
    void add_device(AMDSmiDevice* device) { devices_.push_back(device); }
    std::vector<AMDSmiDevice*>& get_devices() { return devices_;}
    amdsmi_status_t get_device_count(uint32_t* device_count) const;
 private:
    std::string socket_identifier_;
    std::vector<AMDSmiDevice*> devices_;
};

}  // namespace smi
}  // namespace amd

#endif  // AMD_SMI_INCLUDE_AMD_SMI_SOCKET_H_

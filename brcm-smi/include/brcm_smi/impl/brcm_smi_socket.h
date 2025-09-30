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


#ifndef BRCM_SMI_INCLUDE_BRCM_SMI_SOCKET_H_
#define BRCM_SMI_INCLUDE_BRCM_SMI_SOCKET_H_

#include <string>
#include <algorithm>
#include <vector>
#include "brcm_smi/brcmsmi.h"
#include "brcm_smi/impl/brcm_smi_processor.h"

namespace brcm {
namespace smi {

class BRCMSmiSocket {
 public:
    explicit BRCMSmiSocket(const std::string& id) : socket_identifier_(id) {}
    explicit BRCMSmiSocket(uint32_t index) : sindex_(index) {}
    ~BRCMSmiSocket();
    const std::string& get_socket_id() const { return socket_identifier_;}
    uint32_t get_socket_index() { return sindex_;}
    void add_processor(BRCMSmiProcessor* processor) {
        switch (processor->get_processor_type()) {
        case BRCMSMI_PROCESSOR_TYPE_NIC:
            nic_processors_.push_back(processor);
            break;
        case BRCMSMI_PROCESSOR_TYPE_SWITCH:
            switch_processors_.push_back(processor);
            break;
        case BRCMSMI_PROCESSOR_TYPE_ALL:
            // Add to all relevant vectors
            nic_processors_.push_back(processor);
            switch_processors_.push_back(processor);
            break;
        default:
            break;
        }
    }
    std::vector<BRCMSmiProcessor*>& get_processors() { 
        // Return all processors (combined NIC and Switch)
        all_processors_.clear();
        all_processors_.insert(all_processors_.end(), nic_processors_.begin(), nic_processors_.end());
        all_processors_.insert(all_processors_.end(), switch_processors_.begin(), switch_processors_.end());
        return all_processors_;
    }
    std::vector<BRCMSmiProcessor*>& get_processors(brcmsmi_processor_type_t type) {
      switch (type) {
      case BRCMSMI_PROCESSOR_TYPE_NIC:
          return nic_processors_;
      case BRCMSMI_PROCESSOR_TYPE_SWITCH:
          return switch_processors_;
      case BRCMSMI_PROCESSOR_TYPE_ALL:
          return get_processors(); // Return combined list
      default:
          return nic_processors_; // Default to NIC
      }
    }
    brcmsmi_status_t get_processor_count(uint32_t* processor_count) const;
    brcmsmi_status_t get_processor_count(brcmsmi_processor_type_t type, uint32_t* processor_count) const;
 private:
    uint32_t sindex_;
    std::string socket_identifier_;
    std::vector<BRCMSmiProcessor*> nic_processors_;
    std::vector<BRCMSmiProcessor*> switch_processors_;
    std::vector<BRCMSmiProcessor*> all_processors_; // Combined list for get_processors()
};

}  // namespace smi
}  // namespace brcm

#endif  // BRCM_SMI_INCLUDE_BRCM_SMI_SOCKET_H_

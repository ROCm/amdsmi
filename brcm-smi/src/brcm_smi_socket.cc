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


#include <functional>
#include "brcm_smi/impl/brcm_smi_socket.h"

namespace brcm {
namespace smi {

BRCMSmiSocket::~BRCMSmiSocket() {
    for (uint32_t i = 0; i < nic_processors_.size(); i++) {
        delete nic_processors_[i];
    }
    nic_processors_.clear();

    for (uint32_t i = 0; i < switch_processors_.size(); i++) {
        delete switch_processors_[i];
    }
    switch_processors_.clear();
    
    all_processors_.clear();
}

brcmsmi_status_t BRCMSmiSocket::get_processor_count(uint32_t* processor_count) const {
    *processor_count = static_cast<uint32_t>(nic_processors_.size() + switch_processors_.size());
    return BRCMSMI_STATUS_SUCCESS;
}

brcmsmi_status_t BRCMSmiSocket::get_processor_count(brcmsmi_processor_type_t type, uint32_t* processor_count) const {
    brcmsmi_status_t ret = BRCMSMI_STATUS_SUCCESS;
    switch (type) {
    case BRCMSMI_PROCESSOR_TYPE_NIC:
        *processor_count = static_cast<uint32_t>(nic_processors_.size());
        break;
    case BRCMSMI_PROCESSOR_TYPE_SWITCH:
        *processor_count = static_cast<uint32_t>(switch_processors_.size());
        break;
    case BRCMSMI_PROCESSOR_TYPE_ALL:
        *processor_count = static_cast<uint32_t>(nic_processors_.size() + switch_processors_.size());
        break;
    default:
        *processor_count = 0;
        ret = BRCMSMI_STATUS_INVALID_ARGS;
        break;
    }
    return ret;
}

}  // namespace smi
}  // namespace brcm

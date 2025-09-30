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


#ifndef BRCM_SMI_INCLUDE_BRCM_SMI_PROCESSOR_H_
#define BRCM_SMI_INCLUDE_BRCM_SMI_PROCESSOR_H_

#include <string>
#include "brcm_smi/brcmsmi.h"

namespace brcm {
namespace smi {

class BRCMSmiProcessor {
 public:
    explicit BRCMSmiProcessor(brcmsmi_processor_type_t type) : processor_type_(type) {}
    explicit BRCMSmiProcessor(brcmsmi_processor_type_t type, uint32_t index) : processor_type_(type), pindex_(index) {}
    explicit BRCMSmiProcessor(const std::string& id) : processor_identifier_(id) {}
    virtual ~BRCMSmiProcessor() {}
    brcmsmi_processor_type_t get_processor_type() const { return processor_type_;}
    const std::string& get_processor_id() const { return processor_identifier_;}
    uint32_t get_processor_index() const { return pindex_;}

 private:
    brcmsmi_processor_type_t processor_type_;
    uint32_t pindex_;
    std::string processor_identifier_;
};

}  // namespace smi
}  // namespace brcm

#endif  // BRCM_SMI_INCLUDE_BRCM_SMI_PROCESSOR_H_
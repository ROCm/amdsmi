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


#ifndef BRCM_SMI_INCLUDE_BRCM_SMI_SYSTEM_H_
#define BRCM_SMI_INCLUDE_BRCM_SMI_SYSTEM_H_

#include <vector>
#include <memory>
#include <mutex>
#include "brcm_smi/brcmsmi.h"
#include "brcm_smi/impl/brcm_smi_socket.h"
#include "brcm_smi/impl/brcm_smi_processor.h"

namespace brcm {
namespace smi {

class BRCMSmiSystem {
 public:
    static BRCMSmiSystem& getInstance() {
        static BRCMSmiSystem instance;
        return instance;
    }

    // Initialize the system
    brcmsmi_status_t initialize();
    
    // Shutdown the system
    brcmsmi_status_t shutdown();
    std::vector<std::unique_ptr<BRCMSmiSocket>>& get_sockets() {return sockets_;}
    // Socket management
    brcmsmi_status_t get_socket_count(uint32_t* socket_count) const;
    brcmsmi_status_t get_socket_handles(uint32_t* socket_count, brcmsmi_socket_handle* socket_handles) const;
    brcmsmi_status_t handle_to_socket(brcmsmi_socket_handle socket_handle, BRCMSmiSocket** socket) const;
    
    // Processor management
    brcmsmi_status_t get_processor_handles(brcmsmi_socket_handle socket_handle, 
                                          brcmsmi_processor_type_t processor_type,
                                          uint32_t* processor_count, 
                                          brcmsmi_processor_handle* processor_handles) const;
    brcmsmi_status_t handle_to_processor(brcmsmi_processor_handle processor_handle, BRCMSmiProcessor** processor) const;
    
    // Discovery methods
    brcmsmi_status_t discover_devices();
    
    bool is_initialized() const { return initialized_; }
    
 private:
    BRCMSmiSystem() : initialized_(false) {}
    ~BRCMSmiSystem();
    
    // Prevent copying
    BRCMSmiSystem(const BRCMSmiSystem&) = delete;
    BRCMSmiSystem& operator=(const BRCMSmiSystem&) = delete;
    
    // Internal methods
    BRCMSmiSocket* get_or_create_socket(uint32_t socket_index);
    
    bool initialized_;
    std::vector<std::unique_ptr<BRCMSmiSocket>> sockets_;
    mutable std::mutex system_mutex_;
};

}  // namespace smi
}  // namespace brcm

#endif  // BRCM_SMI_INCLUDE_BRCM_SMI_SYSTEM_H_

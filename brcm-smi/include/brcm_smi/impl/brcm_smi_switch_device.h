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


#ifndef BRCM_SMI_INCLUDE_IMPL_BRCM_SMI_SWITCH_DEVICE_H_
#define BRCM_SMI_INCLUDE_IMPL_BRCM_SMI_SWITCH_DEVICE_H_

#include "brcm_smi/brcmsmi.h"
#include "brcm_smi/impl/brcm_smi_processor.h"
#include "brcm_smi/impl/brcm_smi_no_drm_switch.h"
#include <pthread.h>

namespace brcm {
namespace smi {

class BrcmSmiSWITCHDevice: public BRCMSmiProcessor {
 public:

    BrcmSmiSWITCHDevice(uint32_t switch_id, brcmsmi_bdf_t bdf, BrcmSmiNoDrmSwitch& no_drm_switch)
                : BRCMSmiProcessor(BRCMSMI_PROCESSOR_TYPE_SWITCH), switch_id_(switch_id), bdf_(bdf), nodrm_(no_drm_switch) {
              try {
                  if (check_if_no_drm_is_supported()) {
                      this->get_no_drm_data();
                  }
              } catch (...) {
                  // Ignore initialization errors to prevent segfaults
              }
            }

    ~BrcmSmiSWITCHDevice() {
    }

    brcmsmi_status_t get_no_drm_data();
    pthread_mutex_t* get_mutex();
    uint32_t get_switch_id() const;
    std::string& get_switch_path();
    brcmsmi_bdf_t get_bdf();
    bool check_if_no_drm_is_supported() { return nodrm_.check_if_no_drm_is_supported(); }

    brcmsmi_status_t query_switch_link_info(brcmsmi_switch_link_metric_t& info) const;
    brcmsmi_status_t query_switch_uuid(std::string& serial) const;
    brcmsmi_status_t query_switch_numa_affinity(int32_t *numa_node) const;
    brcmsmi_status_t query_switch_cpu_affinity(std::string& cpu_affinity) const;
    brcmsmi_status_t query_switch_device_info(brcmsmi_switch_device_metric_t& info) const;
    brcmsmi_status_t query_switch_power_info(brcmsmi_switch_power_metric_t& info) const;
    brcmsmi_status_t query_switch_info(brcmsmi_switch_info_t& info) const;
    std::string get_switch_name_from_sysfs() const;

 private:
    uint32_t switch_id_;
    std::string path_;
    brcmsmi_bdf_t bdf_;
    BrcmSmiNoDrmSwitch& nodrm_;
};


}  // namespace smi
}  // namespace brcm

#endif  // BRCM_SMI_INCLUDE_IMPL_BRCM_SMI_SWITCH_DEVICE_H_

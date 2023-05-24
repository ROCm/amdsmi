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

#include <stdint.h>
#include <stddef.h>

#include <iostream>
#include <string>

#include <gtest/gtest.h>
#include "amd_smi/amdsmi.h"
#include "id_info_read.h"
#include "../test_common.h"

TestIdInfoRead::TestIdInfoRead() : TestBase() {
  set_title("AMDSMI ID Info Read Test");
  set_description("This test verifies that ID information such as the "
             "device, subsystem and vendor IDs can be read properly.");
}

TestIdInfoRead::~TestIdInfoRead(void) {
}

void TestIdInfoRead::SetUp(void) {
  TestBase::SetUp();

  return;
}

void TestIdInfoRead::DisplayTestInfo(void) {
  TestBase::DisplayTestInfo();
}

void TestIdInfoRead::DisplayResults(void) const {
  TestBase::DisplayResults();
  return;
}

void TestIdInfoRead::Close() {
  // This will close handles opened within rsmitst utility calls and call
  // amdsmi_shut_down(), so it should be done after other hsa cleanup
  TestBase::Close();
}

static const uint32_t kBufferLen = 80;

void TestIdInfoRead::Run(void) {
  amdsmi_status_t err;
  uint16_t id;
  uint64_t val_ui64;
  uint32_t drm_render_minor;

  char buffer[kBufferLen];

  TestBase::Run();
  if (setup_failed_) {
    std::cout << "** SetUp Failed for this test. Skipping.**" << std::endl;
    return;
  }

  for (uint32_t i = 0; i < num_monitor_devs(); ++i) {
    IF_VERB(STANDARD) {
      std::cout << "\t*************************" << std::endl;
      std::cout << "\t**Device index: " << i << std::endl;
    }

    // Get the device ID, name, vendor ID and vendor name for the device
    err = amdsmi_get_gpu_id(processor_handles_[i], &id);
    if (err == AMDSMI_STATUS_NOT_SUPPORTED) {
      amdsmi_status_t ret;
      // Verify api support checking functionality is working
      ret = amdsmi_get_gpu_id(processor_handles_[i], nullptr);
      ASSERT_EQ(ret, AMDSMI_STATUS_NOT_SUPPORTED);
    } else {
      CHK_ERR_ASRT(err)

      IF_VERB(STANDARD) {
        std::cout << "\t**Device ID: 0x" << std::hex << id << std::endl;
      }
      // Verify api support checking functionality is working
      err = amdsmi_get_gpu_id(processor_handles_[i], nullptr);
      ASSERT_EQ(err, AMDSMI_STATUS_INVAL);
    }

       // vendor_id, unique_id
    amdsmi_asic_info_t asci_info;
    err = amdsmi_get_gpu_asic_info(processor_handles_[0], &asci_info);
    CHK_ERR_ASRT(err)

    // device name, brand, serial_number
    amdsmi_board_info_t board_info;
    err = amdsmi_get_gpu_board_info(processor_handles_[0], &board_info);
    CHK_ERR_ASRT(err)

    err = amdsmi_get_gpu_vram_vendor(processor_handles_[i], buffer, kBufferLen);
    if (err == AMDSMI_STATUS_NOT_SUPPORTED) {
      std::cout <<
        "\t**Vram Vendor string not supported on this system." << std::endl;
      err = amdsmi_get_gpu_vram_vendor(processor_handles_[i], nullptr, kBufferLen);
      ASSERT_EQ(err, AMDSMI_STATUS_NOT_SUPPORTED);
    } else {
      CHK_ERR_ASRT(err)
      IF_VERB(STANDARD) {
        std::cout << "\t**Device Vram Vendor name: " << buffer << std::endl;
      }
    }

    err = amdsmi_get_gpu_drm_render_minor(processor_handles_[i], &drm_render_minor);
    if (err == AMDSMI_STATUS_NOT_SUPPORTED) {
      // Verify api support checking functionality is working
      err = amdsmi_get_gpu_drm_render_minor(processor_handles_[i], nullptr);
      ASSERT_EQ(err, AMDSMI_STATUS_NOT_SUPPORTED);
    } else {
      CHK_ERR_ASRT(err)
      IF_VERB(STANDARD) {
        std::cout << "\t**DRM Render Minor: " << drm_render_minor << std::endl;
      }
      // Verify api support checking functionality is working
      err = amdsmi_get_gpu_drm_render_minor(processor_handles_[i], nullptr);
      ASSERT_EQ(err, AMDSMI_STATUS_INVAL);
    }
    err = amdsmi_get_gpu_vendor_name(processor_handles_[i], buffer, kBufferLen);
    if (err == AMDSMI_STATUS_NOT_SUPPORTED) {
      std::cout << "\t**Device Vendor name string not found on this system." <<
                                                                     std::endl;
      // Verify api support checking functionality is working
      err = amdsmi_get_gpu_vendor_name(processor_handles_[i], nullptr, kBufferLen);
      ASSERT_EQ(err, AMDSMI_STATUS_NOT_SUPPORTED);
    } else {
      CHK_ERR_ASRT(err)
      IF_VERB(STANDARD) {
        std::cout << "\t**Device Vendor name: " << buffer << std::endl;
      }
      // Verify api support checking functionality is working
      err = amdsmi_get_gpu_vendor_name(processor_handles_[i], nullptr, kBufferLen);
      ASSERT_EQ(err, AMDSMI_STATUS_INVAL);
    }

    // Get the device ID, name, vendor ID and vendor name for the sub-device
    err = amdsmi_get_gpu_subsystem_id(processor_handles_[i], &id);
    if (err == AMDSMI_STATUS_NOT_SUPPORTED) {
      // Verify api support checking functionality is working
      err = amdsmi_get_gpu_subsystem_id(processor_handles_[i], nullptr);
      ASSERT_EQ(err, AMDSMI_STATUS_NOT_SUPPORTED);
    } else {
      CHK_ERR_ASRT(err)
      IF_VERB(STANDARD) {
        std::cout << "\t**Subsystem ID: 0x" << std::hex << id << std::endl;
      }
      // Verify api support checking functionality is working
      err = amdsmi_get_gpu_subsystem_id(processor_handles_[i], nullptr);
      ASSERT_EQ(err, AMDSMI_STATUS_INVAL);
    }
    err = amdsmi_get_gpu_subsystem_name(processor_handles_[i], buffer, kBufferLen);
    if (err == AMDSMI_STATUS_NOT_SUPPORTED) {
      std::cout << "\t**Subsystem name string not found on this system." <<
                                                                    std::endl;
      // Verify api support checking functionality is working
      err = amdsmi_get_gpu_subsystem_name(processor_handles_[i], nullptr, kBufferLen);
      ASSERT_EQ(err, AMDSMI_STATUS_NOT_SUPPORTED);
    } else {
      CHK_ERR_ASRT(err)
      IF_VERB(STANDARD) {
        std::cout << "\t**Subsystem name: " << buffer << std::endl;
      }
      // Verify api support checking functionality is working
      err = amdsmi_get_gpu_subsystem_name(processor_handles_[i], nullptr, kBufferLen);
      ASSERT_EQ(err, AMDSMI_STATUS_INVAL);
    }

    IF_VERB(STANDARD) {
        std::cout << "\t**Sub-system Vendor ID: 0x" << std::hex <<
                                            asci_info.subvendor_id << std::endl;
    }

    err = amdsmi_get_gpu_vendor_name(processor_handles_[i], buffer, kBufferLen);
    if (err == AMDSMI_STATUS_NOT_SUPPORTED) {
      std::cout <<
           "\t**Subsystem Vendor name string not found on this system." <<
                                                                    std::endl;
     // Verify api support checking functionality is working
     err = amdsmi_get_gpu_vendor_name(processor_handles_[i], nullptr, kBufferLen);
     ASSERT_EQ(err, AMDSMI_STATUS_NOT_SUPPORTED);
    } else {
      CHK_ERR_ASRT(err)
      IF_VERB(STANDARD) {
        std::cout << "\t**Subsystem Vendor name: " << buffer << std::endl;
      }
      // Verify api support checking functionality is working
      err = amdsmi_get_gpu_vendor_name(processor_handles_[i], nullptr, kBufferLen);
      ASSERT_EQ(err, AMDSMI_STATUS_INVAL);
    }

    err = amdsmi_get_gpu_pci_id(processor_handles_[i], &val_ui64);
    // Don't check for AMDSMI_STATUS_NOT_SUPPORTED since this should always be
    // supported. It is not based on a sysfs file.
    CHK_ERR_ASRT(err)
    IF_VERB(STANDARD) {
      std::cout << "\t**PCI ID (BDFID): 0x" << std::hex << val_ui64;
      std::cout << " (" << std::dec << val_ui64 << ")" << std::endl;
    }
    // Verify api support checking functionality is working
    err = amdsmi_get_gpu_pci_id(processor_handles_[i], nullptr);
    ASSERT_EQ(err, AMDSMI_STATUS_INVAL);
  }
}

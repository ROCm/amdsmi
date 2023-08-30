/*
 * =============================================================================
 *   ROC Runtime Conformance Release License
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
#include "sys_info_read.h"
#include "../test_common.h"
#include "../test_utils.h"

TestSysInfoRead::TestSysInfoRead() : TestBase() {
  set_title("AMDSMI System Info Read Test");
  set_description("This test verifies that system information such as the "
             "BDFID, AMDSMI version, VBIOS version, etc. can be read properly.");
}

TestSysInfoRead::~TestSysInfoRead(void) {
}

void TestSysInfoRead::SetUp(void) {
  TestBase::SetUp();

  return;
}

void TestSysInfoRead::DisplayTestInfo(void) {
  TestBase::DisplayTestInfo();
}

void TestSysInfoRead::DisplayResults(void) const {
  TestBase::DisplayResults();
  return;
}

void TestSysInfoRead::Close() {
  // This will close handles opened within rsmitst utility calls and call
  // amdsmi_shut_down(), so it should be done after other hsa cleanup
  TestBase::Close();
}


void TestSysInfoRead::Run(void) {
  amdsmi_status_t err;
  uint64_t val_ui64;
  uint32_t val_ui32;
  int32_t val_i32;
  char buffer[80];
  amdsmi_version_t ver = {0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, nullptr};

  TestBase::Run();
  if (setup_failed_) {
    std::cout << "** SetUp Failed for this test. Skipping.**" << std::endl;
    return;
  }

  for (uint32_t i = 0; i < num_monitor_devs(); ++i) {
    PrintDeviceHeader(processor_handles_[i]);

    amdsmi_vbios_info_t info;
    err = amdsmi_get_gpu_vbios_info(processor_handles_[i], &info);

    if (err != AMDSMI_STATUS_SUCCESS) {
      if ((err == AMDSMI_STATUS_FILE_ERROR) || (err == AMDSMI_STATUS_NOT_SUPPORTED)) {
        IF_VERB(STANDARD) {
          std::cout << "\t**VBIOS read: Not supported on this machine"
                                                                << std::endl;
        }
        // Verify api support checking functionality is working
        err = amdsmi_get_gpu_vbios_info(processor_handles_[i], nullptr);
        ASSERT_EQ(err, AMDSMI_STATUS_NOT_SUPPORTED);
      } else {
        // Verify api support checking functionality is working
        err = amdsmi_get_gpu_vbios_info(processor_handles_[i], nullptr);
        ASSERT_EQ(err, AMDSMI_STATUS_INVAL);

        CHK_ERR_ASRT(err)
      }
    } else {
      IF_VERB(STANDARD) {
        std::cout << "\t**VBIOS Version: "
                << info.version << std::endl;
      }
    }

    err = amdsmi_get_gpu_bdf_id(processor_handles_[i], &val_ui64);
    CHK_ERR_ASRT(err)
    IF_VERB(STANDARD) {
      std::cout << "\t**PCI ID (BDFID): 0x" << std::hex << val_ui64;
      std::cout << " (" << std::dec << val_ui64 << ")" << std::endl;
    }
    // Verify api support checking functionality is working
    err = amdsmi_get_gpu_bdf_id(processor_handles_[i], nullptr);
    ASSERT_EQ(err, AMDSMI_STATUS_INVAL);

    err = amdsmi_get_gpu_topo_numa_affinity(processor_handles_[i], &val_i32);
    CHK_ERR_ASRT(err)
    IF_VERB(STANDARD) {
      std::cout << "\t**NUMA NODE: 0x" << std::hex << val_i32;
      std::cout << " (" << std::dec << val_i32 << ")" << std::endl;
    }
    // Verify api support checking functionality is working
    err = amdsmi_get_gpu_topo_numa_affinity(processor_handles_[i], nullptr);
    ASSERT_EQ(err, AMDSMI_STATUS_INVAL);


       // vendor_id, unique_id
    amdsmi_asic_info_t asci_info;
    err = amdsmi_get_gpu_asic_info(processor_handles_[0], &asci_info);
    if (err == AMDSMI_STATUS_NOT_SUPPORTED) {
        std::cout <<
            "\t**amdsmi_dev_unique_id() is not supported"
            " on this machine" << std::endl;
        // Verify api support checking functionality is working
        err = amdsmi_get_gpu_asic_info(processor_handles_[i], nullptr);
        ASSERT_EQ(err, AMDSMI_STATUS_NOT_SUPPORTED);
    } else {
        if (err == AMDSMI_STATUS_SUCCESS) {
            IF_VERB(STANDARD) {
              // TODO(bliu): read unique_id
              /*
                std::cout << "\t**GPU Unique ID : " << std::hex << asci_info.unique_id <<
                std::endl;
                */
            }
            // Verify api support checking functionality is working
            err = amdsmi_get_gpu_asic_info(processor_handles_[i], nullptr);
            ASSERT_EQ(err, AMDSMI_STATUS_INVAL);
        } else {
            std::cout << "amdsmi_dev_unique_id_get() failed with error " <<
                                                               err << std::endl;
        }
    }

  err = amdsmi_get_lib_version(&ver);
  CHK_ERR_ASRT(err)

  ASSERT_TRUE(ver.year != 0xFFFFFFFF && ver.major != 0xFFFFFFFF &&
              ver.minor != 0xFFFFFFFF && ver.release != 0xFFFFFFFF &&
              ver.build != nullptr);
  IF_VERB(STANDARD) {
    std::cout << "\t**AMD SMI Library version: " << ver.year << "." <<
       ver.major << "." << ver.minor << "." << ver.release <<
       " (" << ver.build << ")" << std::endl;
  }

    std::cout << std::setbase(10);

    amdsmi_fw_info_t fw_info;
    err = amdsmi_get_fw_info(processor_handles_[i], &fw_info);
    if (err == AMDSMI_STATUS_NOT_SUPPORTED) {
        std::cout << "\t**No FW  " <<
                    " available on this system" << std::endl;
        err = amdsmi_get_fw_info(processor_handles_[i], nullptr);
        ASSERT_EQ(err, AMDSMI_STATUS_NOT_SUPPORTED);
    } else {
        CHK_ERR_ASRT(err)
    }
  }
}

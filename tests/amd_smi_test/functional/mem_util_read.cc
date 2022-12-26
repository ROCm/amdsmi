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
#include <map>

#include <gtest/gtest.h>
#include "amd_smi/amdsmi.h"
#include "mem_util_read.h"
#include "../test_common.h"

TestMemUtilRead::TestMemUtilRead() : TestBase() {
  set_title("Memory Utilization Read Test");
  set_description("The Memory Utilization Read tests verifies that "
           "memory busy percent, size and amount used can be read properly.");
}

TestMemUtilRead::~TestMemUtilRead(void) {
}

void TestMemUtilRead::SetUp(void) {
  TestBase::SetUp();

  return;
}

void TestMemUtilRead::DisplayTestInfo(void) {
  TestBase::DisplayTestInfo();
}

void TestMemUtilRead::DisplayResults(void) const {
  TestBase::DisplayResults();
  return;
}

void TestMemUtilRead::Close() {
  // This will close handles opened within rsmitst utility calls and call
  // amdsmi_shut_down(), so it should be done after other hsa cleanup
  TestBase::Close();
}

static const std::map<amdsmi_memory_type_t, const char *>
   kDevMemoryTypeNameMap = {
    {AMDSMI_MEM_TYPE_VRAM, "VRAM memory"},
    {AMDSMI_MEM_TYPE_VIS_VRAM, "Visible VRAM memory"},
    {AMDSMI_MEM_TYPE_GTT, "GTT memory"},
};

void TestMemUtilRead::Run(void) {
  amdsmi_status_t err;
  uint64_t total;
  uint64_t usage;

  TestBase::Run();
  if (setup_failed_) {
    std::cout << "** SetUp Failed for this test. Skipping.**" << std::endl;
    return;
  }

  auto err_chk = [&](const char *str) {
    if (err != AMDSMI_STATUS_SUCCESS) {
      if (err == AMDSMI_STATUS_FILE_ERROR) {
        IF_VERB(STANDARD) {
          std::cout << "\t** " << str << ": Not supported on this machine"
                                                                << std::endl;
        }
      } else {
        CHK_ERR_ASRT(err)
      }
    }
  };

  for (uint32_t x = 0; x < num_iterations(); ++x) {
    for (uint32_t i = 0; i < num_monitor_devs(); ++i) {
      PrintDeviceHeader(device_handles_[i]);

#if 0
      err = amdsmi_dev_get_memory_busy_percent(i, &mem_busy_percent);
      err_chk("amdsmi_dev_get_memory_busy_percent()");
      if (err != AMDSMI_STATUS_SUCCESS) {
        return;
      }
      IF_VERB(STANDARD) {
        std::cout << "\t**" << "GPU Memory Busy %: " << mem_busy_percent <<
                                                                      std::endl;
      }
#endif
      for (uint32_t mem_type = AMDSMI_MEM_TYPE_FIRST;
                                   mem_type <= AMDSMI_MEM_TYPE_LAST; ++mem_type) {
        err = amdsmi_dev_get_memory_total(device_handles_[i],
                             static_cast<amdsmi_memory_type_t>(mem_type), &total);
        err_chk("amdsmi_dev_get_memory_total()");
        if (err != AMDSMI_STATUS_SUCCESS) {
          return;
        }

        err = amdsmi_dev_get_memory_usage(device_handles_[i],
                             static_cast<amdsmi_memory_type_t>(mem_type), &usage);
        err_chk("amdsmi_dev_get_memory_usage()");
        if (err != AMDSMI_STATUS_SUCCESS) {
          return;
        }

        IF_VERB(STANDARD) {
          std::cout << "\t**" <<
           kDevMemoryTypeNameMap.at(static_cast<amdsmi_memory_type_t>(mem_type))
            << " Calculated Utilization: " <<
              (static_cast<float>(usage)*100)/total << "% ("<< usage <<
                                              "/" << total << ")" << std::endl;
        }
      }
    }
  }
}

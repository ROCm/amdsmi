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
#include "frequencies_read.h"
#include "../test_common.h"

TestFrequenciesRead::TestFrequenciesRead() : TestBase() {
  set_title("AMDSMI Frequencies Read Test");
  set_description("The Frequency Read tests verifies that the "
              "available and current frequency levels can be read properly.");
}

TestFrequenciesRead::~TestFrequenciesRead(void) {
}

void TestFrequenciesRead::SetUp(void) {
  TestBase::SetUp();

  return;
}

void TestFrequenciesRead::DisplayTestInfo(void) {
  TestBase::DisplayTestInfo();
}

void TestFrequenciesRead::DisplayResults(void) const {
  TestBase::DisplayResults();
  return;
}

void TestFrequenciesRead::Close() {
  // This will close handles opened within rsmitst utility calls and call
  // amdsmi_shut_down(), so it should be done after other hsa cleanup
  TestBase::Close();
}


static void print_frequencies(amdsmi_frequencies_t *f, uint32_t *l = nullptr) {
  assert(f != nullptr);
  for (uint32_t j = 0; j < f->num_supported; ++j) {
    std::cout << "\t**  " << j << ": " << f->frequency[j];
    if (l != nullptr) {
      std::cout << "T/s; x" << l[j];
    } else {
      std::cout << "Hz";
    }

    if (j == f->current) {
      std::cout << " *";
    }
    std::cout << std::endl;
  }
}

void TestFrequenciesRead::Run(void) {
  amdsmi_status_t err;
  amdsmi_frequencies_t f;
  amdsmi_pcie_bandwidth_t b;

  TestBase::Run();
  if (setup_failed_) {
    std::cout << "** SetUp Failed for this test. Skipping.**" << std::endl;
    return;
  }

  for (uint32_t x = 0; x < num_iterations(); ++x) {
    for (uint32_t i = 0; i < num_monitor_devs(); ++i) {
      auto freq_output = [&](amdsmi_clk_type_t t, const char *name) {
        err =  amdsmi_get_clk_freq(processor_handles_[i], t, &f);
        if (err == AMDSMI_STATUS_NOT_SUPPORTED) {
          std::cout << "\t**Get " << name <<
                               ": Not supported on this machine" << std::endl;
          // Verify api support checking functionality is working
          err =  amdsmi_get_clk_freq(processor_handles_[i], t, nullptr);
          ASSERT_EQ(err, AMDSMI_STATUS_INVAL);
        } else if (err == AMDSMI_STATUS_NOT_YET_IMPLEMENTED) {
          std::cout << "\t**Get " << name <<
                               ": Not implemented on this machine" << std::endl;
        // special driver issue, shouldn't normally occur
        } else if (err == AMDSMI_STATUS_UNEXPECTED_DATA) {
          std::cerr << "WARN: Clock file [" << FreqEnumToStr(t) << "] exists on device [" << i << "] but empty!" << std::endl;
          std::cerr << "      Likely a driver issue!" << std::endl;
        } else {
          CHK_ERR_ASRT(err)
          IF_VERB(STANDARD) {
            std::cout << "\t**Supported " << name << " clock frequencies: ";
            std::cout << f.num_supported << std::endl;
            print_frequencies(&f);
            // Verify api support checking functionality is working
            err =  amdsmi_get_clk_freq(processor_handles_[i], t, nullptr);
            ASSERT_EQ(err, AMDSMI_STATUS_INVAL);
          }
        }
      };

      PrintDeviceHeader(processor_handles_[i]);

      freq_output(CLK_TYPE_MEM, "Supported GPU Memory");
      freq_output(CLK_TYPE_SYS, "Supported GPU");
      freq_output(CLK_TYPE_DF, "Data Fabric Clock");
      freq_output(CLK_TYPE_DCEF, "Display Controller Engine Clock");
      freq_output(CLK_TYPE_SOC, "SOC Clock");

      err = amdsmi_get_gpu_pci_bandwidth(processor_handles_[i], &b);
      if (err == AMDSMI_STATUS_NOT_SUPPORTED) {
        std::cout << "\t**Get PCIE Bandwidth: Not supported on this machine"
                                                              << std::endl;
        // Verify api support checking functionality is working
        err = amdsmi_get_gpu_pci_bandwidth(processor_handles_[i], nullptr);
        ASSERT_EQ(err, AMDSMI_STATUS_NOT_SUPPORTED);
      } else if (err == AMDSMI_STATUS_NOT_YET_IMPLEMENTED) {
          std::cout << "\t**Get PCIE Bandwidth "
                    << ": Not implemented on this machine" << std::endl;
      } else {
          CHK_ERR_ASRT(err)
          IF_VERB(STANDARD) {
            std::cout << "\t**Supported PCIe bandwidths: ";
            std::cout << b.transfer_rate.num_supported << std::endl;
            print_frequencies(&b.transfer_rate, b.lanes);
            // Verify api support checking functionality is working
            err = amdsmi_get_gpu_pci_bandwidth(processor_handles_[i], nullptr);
            ASSERT_EQ(err, AMDSMI_STATUS_INVAL);
          }
      }
    }
  }
}

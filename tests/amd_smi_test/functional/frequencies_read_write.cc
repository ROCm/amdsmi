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
#include <map>
#include <bitset>
#include <string>
#include <algorithm>

#include <gtest/gtest.h>
#include "amd_smi/amdsmi.h"
#include "frequencies_read_write.h"
#include "../test_common.h"


TestFrequenciesReadWrite::TestFrequenciesReadWrite() : TestBase() {
  set_title("AMDSMI Frequencies Read/Write Test");
  set_description("The Frequencies tests verify that the frequency "
                       "settings can be read and controlled properly.");
}

TestFrequenciesReadWrite::~TestFrequenciesReadWrite(void) {
}

void TestFrequenciesReadWrite::SetUp(void) {
  TestBase::SetUp();

  return;
}

void TestFrequenciesReadWrite::DisplayTestInfo(void) {
  TestBase::DisplayTestInfo();
}

void TestFrequenciesReadWrite::DisplayResults(void) const {
  TestBase::DisplayResults();
  return;
}

void TestFrequenciesReadWrite::Close() {
  // This will close handles opened within rsmitst utility calls and call
  // amdsmi_shut_down(), so it should be done after other hsa cleanup
  TestBase::Close();
}


void TestFrequenciesReadWrite::Run(void) {
  amdsmi_status_t ret;
  amdsmi_frequencies_t f;
  uint32_t freq_bitmask;
  amdsmi_clk_type_t amdsmi_clk;

  TestBase::Run();
  if (setup_failed_) {
    std::cout << "** SetUp Failed for this test. Skipping.**" << std::endl;
    return;
  }

  for (uint32_t dv_ind = 0; dv_ind < num_monitor_devs(); ++dv_ind) {
    PrintDeviceHeader(device_handles_[dv_ind]);

    for (uint32_t clk = (uint32_t)CLK_TYPE_FIRST;
                                           clk <= CLK_TYPE__MAX; ++clk) {
      amdsmi_clk = (amdsmi_clk_type_t)clk;

      auto freq_read = [&]() -> bool {
        // Skip CLK_TYPE_PCIE, which does not supported in rocm-smi.
        std::cout << amdsmi_clk << std::endl;
        if (amdsmi_clk == CLK_TYPE_PCIE)
          return false;
        ret =  amdsmi_dev_get_gpu_clk_freq(device_handles_[dv_ind], amdsmi_clk, &f);
        std::cout << ret << std::endl;

        if (ret == AMDSMI_STATUS_NOT_SUPPORTED ||
            ret == AMDSMI_STATUS_NOT_YET_IMPLEMENTED) {
          std::cout << "\t**Set " << FreqEnumToStr(amdsmi_clk) <<
                               ": Not supported on this machine" << std::endl;
          return false;
        } else {
         //   CHK_ERR_ASRT(ret)
          IF_VERB(STANDARD) {
            std::cout << "Initial frequency for clock " <<
                FreqEnumToStr(amdsmi_clk) << " is " << f.current << std::endl;
          }
          return true;
        }
      };

      auto freq_write = [&]() {
        // Set clocks to something other than the usual default of the lowest
        // frequency.
        // Skip CLK_TYPE_PCIE, which does not supported in rocm-smi.
        if (amdsmi_clk == CLK_TYPE_PCIE)
          return;

        freq_bitmask = 0b01100;  // Try the 3rd and 4th clocks

        std::string freq_bm_str =
              std::bitset<AMDSMI_MAX_NUM_FREQUENCIES>(freq_bitmask).to_string();

        freq_bm_str.erase(0, std::min(freq_bm_str.find_first_not_of('0'),
                                                       freq_bm_str.size()-1));

        IF_VERB(STANDARD) {
        std::cout << "Setting frequency mask for " <<
            FreqEnumToStr(amdsmi_clk) << " to 0b" << freq_bm_str << " ..." <<
                                                                    std::endl;
        }
        ret =  amdsmi_dev_set_clk_freq(device_handles_[dv_ind], amdsmi_clk, freq_bitmask);
        //Certain ASICs does not allow to set particular clocks. If set function for a clock returns
        //permission error despite root access, manually set ret value to success and return
        if (ret == AMDSMI_STATUS_NO_PERM && geteuid() == 0) {
          std::cout << "\t**Set " << FreqEnumToStr(amdsmi_clk) <<
                              ": Not supported on this machine. Skipping..." << std::endl;
          ret = AMDSMI_STATUS_SUCCESS;
          return;
        } else if (ret == AMDSMI_STATUS_NOT_SUPPORTED) {
          std::cout << "\t**Set " << FreqEnumToStr(amdsmi_clk) <<
                              ": Not supported on this machine. Skipping..." << std::endl;
          ret = AMDSMI_STATUS_SUCCESS;
          return;
        }
        CHK_ERR_ASRT(ret)
        ret =  amdsmi_dev_get_gpu_clk_freq(device_handles_[dv_ind], amdsmi_clk, &f);
        if (ret != AMDSMI_STATUS_SUCCESS) {
          return;
        }

        IF_VERB(STANDARD) {
          std::cout << "Frequency is now index " << f.current << std::endl;
          std::cout << "Resetting mask to all frequencies." << std::endl;
        }
        ret =  amdsmi_dev_set_clk_freq(device_handles_[dv_ind], amdsmi_clk, 0xFFFFFFFF);
        if (ret != AMDSMI_STATUS_SUCCESS) {
          return;
        }

        ret =  amdsmi_dev_set_perf_level(device_handles_[dv_ind], AMDSMI_DEV_PERF_LEVEL_AUTO);
        if (ret != AMDSMI_STATUS_SUCCESS) {
          return;
        }
      };

      if (freq_read()) {
        CHK_ERR_ASRT(ret)
      } else {
        continue;
      }
      freq_write();
      CHK_ERR_ASRT(ret)
#if 0
      ret =  amdsmi_dev_get_gpu_clk_freq(dv_ind, amdsmi_clk, &f);
      CHK_ERR_ASRT(ret)

      IF_VERB(STANDARD) {
        std::cout << "Initial frequency for clock " << amdsmi_clk << " is " <<
                                                        f.current << std::endl;
      }
      // Set clocks to something other than the usual default of the lowest
      // frequency.
      freq_bitmask = 0b01100;  // Try the 3rd and 4th clocks

      std::string freq_bm_str =
              std::bitset<AMDSMI_MAX_NUM_FREQUENCIES>(freq_bitmask).to_string();

      freq_bm_str.erase(0, std::min(freq_bm_str.find_first_not_of('0'),
                                                       freq_bm_str.size()-1));

      IF_VERB(STANDARD) {
      std::cout << "Setting frequency mask for clock " << amdsmi_clk <<
          " to 0b" << freq_bm_str << " ..." << std::endl;
      }
      ret =  amdsmi_dev_set_clk_freq(dv_ind, amdsmi_clk, freq_bitmask);
      CHK_ERR_ASRT(ret)

      ret =  amdsmi_dev_get_gpu_clk_freq(dv_ind, amdsmi_clk, &f);
      CHK_ERR_ASRT(ret)

      IF_VERB(STANDARD) {
        std::cout << "Frequency is now index " << f.current << std::endl;
        std::cout << "Resetting mask to all frequencies." << std::endl;
      }
      ret =  amdsmi_dev_set_clk_freq(dv_ind, amdsmi_clk, 0xFFFFFFFF);
      CHK_ERR_ASRT(ret)

      ret =  amdsmi_dev_set_perf_level(dv_ind, AMDSMI_DEV_PERF_LEVEL_AUTO);
      CHK_ERR_ASRT(ret)
#endif
    }
  }
}

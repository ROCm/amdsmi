/*
 * =============================================================================
 *   ROC Runtime Conformance Release License
 * =============================================================================
 * The University of Illinois/NCSA
 * Open Source License (NCSA)
 *
 * Copyright (c) 2023, Advanced Micro Devices, Inc.
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

#include <string>
#include <vector>
#include <memory>
#include <iostream>

#include "amd_smi/amdsmi.h"
#include <gtest/gtest.h>
#include "test_common.h"
#include "test_base.h"

#include "functional/fan_read.h"
#include "functional/fan_read_write.h"
#include "functional/evt_notif_read_write.h"
#include "functional/perf_cntr_read_write.h"
#include "functional/hw_topology_read.h"
#include "functional/xgmi_read_write.h"
#include "functional/api_support_read.h"
#include "functional/process_info_read.h"
#include "functional/gpu_busy_read.h"
#include "functional/gpu_metrics_read.h"
#include "functional/err_cnt_read.h"
#include "functional/power_read.h"
#include "functional/power_read_write.h"
#include "functional/power_cap_read_write.h"
#include "functional/mem_util_read.h"
#include "functional/mem_page_info_read.h"
#include "functional/frequencies_read.h"
#include "functional/frequencies_read_write.h"
#include "functional/overdrive_read.h"
#include "functional/overdrive_read_write.h"
#include "functional/temp_read.h"
#include "functional/volt_read.h"
#include "functional/volt_freq_curv_read.h"
#include "functional/perf_level_read.h"
#include "functional/perf_level_read_write.h"
#include "functional/pci_read_write.h"
#include "functional/perf_determinism.h"
#include "functional/sys_info_read.h"
#include "functional/id_info_read.h"
#include "functional/metrics_counter_read.h"
#include "functional/version_read.h"
#include "functional/mutual_exclusion.h"
#include "functional/init_shutdown_refcount.h"

static AMDSMITstGlobals *sRSMIGlvalues = nullptr;

static void SetFlags(TestBase *test) {
  assert(sRSMIGlvalues != nullptr);

  test->set_verbosity(sRSMIGlvalues->verbosity);
  test->set_dont_fail(sRSMIGlvalues->dont_fail);
  test->set_init_options(sRSMIGlvalues->init_options);
  test->set_num_iterations(sRSMIGlvalues->num_iterations);
}

static void RunCustomTestProlog(TestBase *test) {
  SetFlags(test);

  if (sRSMIGlvalues->verbosity >= TestBase::VERBOSE_STANDARD) {
    test->DisplayTestInfo();
  }
  test->SetUp();
  test->Run();
}
static void RunCustomTestEpilog(TestBase *tst) {
  if (sRSMIGlvalues->verbosity >= TestBase::VERBOSE_STANDARD) {
    tst->DisplayResults();
  }
  tst->Close();
}

// If the test case one big test, you should use RunGenericTest()
// to run the test case. OTOH, if the test case consists of multiple
// functions to be run as separate tests, follow this pattern:
//   * RunCustomTestProlog(test)  // Run() should contain minimal code
//   * <insert call to actual test function within test case>
//   * RunCustomTestEpilog(test)
static void RunGenericTest(TestBase *test) {
  RunCustomTestProlog(test);
  RunCustomTestEpilog(test);
}


// TEST ENTRY TEMPLATE:
// TEST(rocrtst, Perf_<test name>) {
//  <Test Implementation class> <test_obj>;
//
//  // Copy and modify implementation of RunGenericTest() if you need to deviate
//  // from the standard pattern implemented there.
//  RunGenericTest(&<test_obj>);
// }
TEST(amdsmitstReadOnly, TestVersionRead) {
  TestVersionRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, FanRead) {
  TestFanRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadWrite, FanReadWrite) {
  TestFanReadWrite tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TempRead) {
  TestTempRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, VoltRead) {
  TestVoltRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestVoltCurvRead) {
  TestVoltCurvRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestPerfLevelRead) {
  TestPerfLevelRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadWrite, TestPerfLevelReadWrite) {
  TestPerfLevelReadWrite tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestOverdriveRead) {
  TestOverdriveRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadWrite, TestOverdriveReadWrite) {
  TestOverdriveReadWrite tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestFrequenciesRead) {
  TestFrequenciesRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadWrite, TestFrequenciesReadWrite) {
  TestFrequenciesReadWrite tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadWrite, TestPciReadWrite) {
  TestPciReadWrite tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestSysInfoRead) {
  TestSysInfoRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestGPUBusyRead) {
  TestGPUBusyRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestPowerRead) {
  TestPowerRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadWrite, TestPowerReadWrite) {
  TestPowerReadWrite tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadWrite, TestPowerCapReadWrite) {
  TestPowerCapReadWrite tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestErrCntRead) {
  TestErrCntRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestMemUtilRead) {
  TestMemUtilRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestIdInfoRead) {
  TestIdInfoRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadWrite, TestPerfCntrReadWrite) {
  TestPerfCntrReadWrite tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestProcInfoRead) {
  TestProcInfoRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestHWTopologyRead) {
  TestHWTopologyRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestGpuMetricsRead) {
  TestGpuMetricsRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestMetricsCounterRead) {
  TestMetricsCounterRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadWrite, TestPerfDeterminism) {
  TestPerfDeterminism tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadWrite, TestXGMIReadWrite) {
  TestXGMIReadWrite tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestMemPageInfoRead) {
  TestMemPageInfoRead tst;
  RunGenericTest(&tst);
}
TEST(amdsmitstReadOnly, TestAPISupportRead) {
  TestAPISupportRead tst;
  RunGenericTest(&tst);
}
/*
TEST(amdsmitstReadOnly, TestMutualExclusion) {
  TestMutualExclusion tst;
  SetFlags(&tst);
  tst.DisplayTestInfo();
  tst.SetUp();
  tst.Run();
  RunCustomTestEpilog(&tst);
}
*/
// TODO: add TestComputePartitionReadWrite
// TODO: add TestMemoryPartitionReadWrite
TEST(amdsmitstReadWrite, TestEvtNotifReadWrite) {
  TestEvtNotifReadWrite tst;
  RunGenericTest(&tst);
}
/*
TEST(amdsmitstReadOnly, TestConcurrentInit) {
  TestConcurrentInit tst;
  SetFlags(&tst);
  tst.DisplayTestInfo();
  //  tst.SetUp();   // Avoid extra amdsmi_init
  tst.Run();
  // RunCustomTestEpilog(&tst);  // Avoid extra amdsmi_shut_down
  tst.DisplayResults();
}
*/

int main(int argc, char** argv) {
  ::testing::InitGoogleTest(&argc, argv);

  AMDSMITstGlobals settings;

  // Set some default values
  settings.verbosity = 1;
  settings.monitor_verbosity = 1;
  settings.num_iterations = 1;
  settings.dont_fail = false;
  settings.init_options = 0;

  if (ProcessCmdline(&settings, argc, argv)) {
    return 1;
  }

  sRSMIGlvalues = &settings;
  return RUN_ALL_TESTS();
}

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
#include <map>

#include "gtest/gtest.h"
#include "amd_smi.h"
#include "amd_smi_test/functional/mutual_exclusion.h"
#include "amd_smi_test/test_common.h"

#define  AMD_SMI_INIT_FLAG_RESRV_TEST1 0x800000000000000  //!< Reserved for test

TestMutualExclusion::TestMutualExclusion() : TestBase() {
  set_title("Mutual Exclusion Test");
  set_description("Verify that AMDSMI only allows 1 process at a time"
    " to access AMDSMI resources (primarily sysfs files). This test has one "
    "process that obtains the mutex that ensures only 1 process accesses a "
      "device's sysfs files at a time, and another process that attempts "
      "to access the device's sysfs files. The second process should fail "
      "in these attempts.");
}

TestMutualExclusion::~TestMutualExclusion(void) {
}

extern amdsmi_status_t rsmi_test_sleep(uint32_t dv_ind, uint32_t seconds);

void TestMutualExclusion::SetUp(void) {
  std::string label;
  amdsmi_status_t ret;

  //   TestBase::SetUp(AMD_SMI_INIT_FLAG_RESRV_TEST1);
  IF_VERB(STANDARD) {
    MakeHeaderStr(kSetupLabel, &label);
    printf("\n\t%s\n", label.c_str());
  }

  sleeper_process_ = false;
  child_ = 0;
  child_ = fork();

  if (child_ != 0) {
    sleeper_process_ = true;  // sleeper_process is parent

    // AMD_SMI_INIT_FLAG_RESRV_TEST1 tells rsmi to fail immediately
    // if it can't get the mutex instead of waiting.
    ret = amdsmi_init(AMD_SMI_INIT_FLAG_RESRV_TEST1);
    if (ret != AMDSMI_STATUS_SUCCESS) {
      setup_failed_ = true;
    }
    ASSERT_EQ(ret, AMDSMI_STATUS_SUCCESS);

    sleep(2);  // Let both processes get through amdsmi_init
  } else {
    sleep(1);  // Let the sleeper process get through amdsmi_init() before
              // this one goes, so it doesn't fail.
    ret = amdsmi_init(AMD_SMI_INIT_FLAG_RESRV_TEST1);
    if (ret != AMDSMI_STATUS_SUCCESS) {
      setup_failed_ = true;
    }
    ASSERT_EQ(ret, AMDSMI_STATUS_SUCCESS);

    sleep(2);  // Let both processes get through amdsmi_init;
  }

  num_monitor_devs_ = num_monitor_devs();

  if (num_monitor_devs_ == 0) {
    std::cout << "No monitor devices found on this machine." << std::endl;
    std::cout << "No ROCm SMI tests can be run." << std::endl;
    setup_failed_ = true;
  }

  return;
}

void TestMutualExclusion::DisplayTestInfo(void) {
  IF_VERB(STANDARD) {
    TestBase::DisplayTestInfo();
  }
}

void TestMutualExclusion::DisplayResults(void) const {
  IF_VERB(STANDARD) {
    TestBase::DisplayResults();
  }
  return;
}

void TestMutualExclusion::Close() {
  // This will close handles opened within rsmitst utility calls and call
  // amdsmi_shut_down(), so it should be done after other hsa cleanup
  TestBase::Close();
}

extern amdsmi_status_t
rsmi_test_sleep(uint32_t dv_ind, uint32_t seconds);

void TestMutualExclusion::Run(void) {
  amdsmi_status_t ret;

  if (setup_failed_) {
    std::cout << "** SetUp Failed for this test. Skipping.**" << std::endl;
    return;
  }

  if (sleeper_process_) {
    IF_VERB(STANDARD) {
      std::cout << "MUTEX_HOLDER process: started sleeping for 10 seconds..." <<
                                                                     std::endl;
    }
    ret = rsmi_test_sleep(0, 10);
    ASSERT_EQ(ret, AMDSMI_STATUS_SUCCESS);
    IF_VERB(STANDARD) {
      std::cout << "MUTEX_HOLDER process: Sleep process woke up." << std::endl;
    }
    pid_t cpid = wait(nullptr);
    ASSERT_EQ(cpid, child_);
  } else {
    // Both processes should have completed amdsmi_init().
    // let the other process get started on rsmi_test_sleep().
    sleep(2);
    TestBase::Run();
    IF_VERB(STANDARD) {
      std::cout << "TESTER process: verifing that all amdsmi_dev_* functions "
                    "return AMDSMI_STATUS_BUSY because MUTEX_HOLDER process "
                                               "holds the mutex" << std::endl;
    }
    // Try all the device related rsmi calls. They should all fail with
    // AMDSMI_STATUS_BUSY
    // Set dummy values should to working, deterministic values.
    uint16_t dmy_ui16 = 0;
    uint32_t dmy_ui32 = 1;
    uint32_t dmy_i32 = 0;
    uint64_t dmy_ui64 = 0;
    int64_t dmy_i64 = 0;
    char dmy_str[10];
    amdsmi_dev_perf_level_t dmy_perf_lvl;
    amdsmi_frequencies_t dmy_freqs;
    amdsmi_od_volt_freq_data_t dmy_od_volt;
    amdsmi_freq_volt_region_t dmy_vlt_reg;
    amdsmi_error_count_t dmy_err_cnt;
    amdsmi_ras_err_state_t dmy_ras_err_st;

    // This can be replaced with ASSERT_EQ() once env. stabilizes
#define CHECK_RET(A, B) { \
  if ((A) != (B)) { \
    std::cout << "Expected return value of " << B << \
                               " but got " << A << std::endl; \
    std::cout << "at " << __FILE__ << ":" << __LINE__ << std::endl; \
  } \
}
    ret = amdsmi_dev_id_get(device_handles_[0], &dmy_ui16);

    // vendor_id, unique_id
    amdsmi_asic_info_t asci_info;
    ret = amdsmi_get_asic_info(device_handles_[0], &asci_info);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);

    // device name, brand, serial_number
    amdsmi_board_info_t board_info;
    ret = amdsmi_get_board_info(device_handles_[0], &board_info);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);

    ret = amdsmi_dev_vendor_name_get(device_handles_[0], dmy_str, 10);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_vram_vendor_get(device_handles_[0], dmy_str, 10);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_subsystem_id_get(device_handles_[0], &dmy_ui16);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_pci_id_get(device_handles_[0], &dmy_ui64);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_pci_throughput_get(device_handles_[0], &dmy_ui64, &dmy_ui64, &dmy_ui64);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_pci_replay_counter_get(device_handles_[0], &dmy_ui64);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_pci_bandwidth_set(device_handles_[0], 0);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_fan_rpms_get(device_handles_[0], dmy_ui32, &dmy_i64);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_fan_speed_get(device_handles_[0], 0, &dmy_i64);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_fan_speed_max_get(device_handles_[0], 0, &dmy_ui64);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_temp_metric_get(device_handles_[0], dmy_ui32, AMDSMI_TEMP_CURRENT, &dmy_i64);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_fan_reset(device_handles_[0], 0);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_fan_speed_set(device_handles_[0], dmy_ui32, 0);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_perf_level_get(device_handles_[0], &dmy_perf_lvl);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_overdrive_level_get(device_handles_[0], &dmy_ui32);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_gpu_clk_freq_get(device_handles_[0], CLOCK_TYPE_SYS, &dmy_freqs);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_od_volt_info_get(device_handles_[0], &dmy_od_volt);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_od_volt_curve_regions_get(device_handles_[0], &dmy_ui32, &dmy_vlt_reg);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_overdrive_level_set_v1(device_handles_[0], dmy_i32);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_gpu_clk_freq_set(device_handles_[0], CLOCK_TYPE_SYS, 0);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_ecc_count_get(device_handles_[0], AMDSMI_GPU_BLOCK_UMC, &dmy_err_cnt);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_ecc_enabled_get(device_handles_[0], &dmy_ui64);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);
    ret = amdsmi_dev_ecc_status_get(device_handles_[0], AMDSMI_GPU_BLOCK_UMC, &dmy_ras_err_st);
    CHECK_RET(ret, AMDSMI_STATUS_BUSY);

    /* Other functions holding device mutexes. Listed for reference.
    amdsmi_dev_sku_get
    amdsmi_dev_perf_level_set_v1
    amdsmi_dev_od_clk_info_set
    amdsmi_dev_od_volt_info_set
    amdsmi_dev_firmware_version_get
    amdsmi_dev_firmware_version_get
    amdsmi_dev_name_get
    amdsmi_dev_brand_get
    amdsmi_dev_vram_vendor_get
    amdsmi_dev_subsystem_name_get
    amdsmi_dev_drm_render_minor_get
    amdsmi_dev_vendor_name_get
    amdsmi_dev_pci_bandwidth_get
    amdsmi_dev_pci_bandwidth_set
    amdsmi_dev_pci_throughput_get
    amdsmi_dev_temp_metric_get
    amdsmi_dev_volt_metric_get
    amdsmi_dev_fan_speed_get
    amdsmi_dev_fan_rpms_get
    amdsmi_dev_fan_reset
    amdsmi_dev_fan_speed_set
    amdsmi_dev_fan_speed_max_get
    amdsmi_dev_od_volt_info_get
    amdsmi_dev_gpu_metrics_info_get
    amdsmi_dev_od_volt_curve_regions_get
    amdsmi_dev_power_max_get
    amdsmi_dev_power_ave_get
    amdsmi_dev_power_cap_get
    amdsmi_dev_power_cap_range_get
    amdsmi_dev_power_cap_set
    amdsmi_dev_power_profile_presets_get
    amdsmi_dev_power_profile_set
    amdsmi_dev_memory_total_get
    amdsmi_dev_memory_usage_get
    amdsmi_dev_memory_busy_percent_get
    amdsmi_dev_busy_percent_get
    amdsmi_dev_vbios_version_get
    amdsmi_dev_serial_number_get
    amdsmi_dev_pci_replay_counter_get
    amdsmi_dev_unique_id_get
    amdsmi_dev_counter_create
    amdsmi_counter_available_counters_get
    amdsmi_dev_counter_group_supported
    amdsmi_dev_memory_reserved_pages_get
    amdsmi_dev_xgmi_error_status
    amdsmi_dev_xgmi_error_reset
    amdsmi_dev_xgmi_hive_id_get
    amdsmi_topo_get_link_weight
    amdsmi_event_notification_mask_set
    amdsmi_event_notification_init
    amdsmi_event_notification_stop
    */

    IF_VERB(STANDARD) {
      std::cout << "TESTER process: Finished verifying that all "
                "amdsmi_dev_* functions returned AMDSMI_STATUS_BUSY" << std::endl;
    }
    exit(0);
  }
}

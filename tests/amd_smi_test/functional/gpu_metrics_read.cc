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

#include <stdint.h>
#include <stddef.h>

#include <iostream>
#include <string>
#include <map>

#include <gtest/gtest.h>
#include "amd_smi/amdsmi.h"
#include "gpu_metrics_read.h"
#include "../test_common.h"


TestGpuMetricsRead::TestGpuMetricsRead() : TestBase() {
  set_title("AMDSMI GPU Metrics Read Test");
  set_description("The GPU Metrics tests verifies that "
                  "the gpu metrics info can be read properly.");
}

TestGpuMetricsRead::~TestGpuMetricsRead(void) {
}

void TestGpuMetricsRead::SetUp(void) {
  TestBase::SetUp();

  return;
}

void TestGpuMetricsRead::DisplayTestInfo(void) {
  TestBase::DisplayTestInfo();
}

void TestGpuMetricsRead::DisplayResults(void) const {
  TestBase::DisplayResults();
  return;
}

void TestGpuMetricsRead::Close() {
  // This will close handles opened within amdsmitst utility calls and call
  // amdsmi_shut_down(), so it should be done after other hsa cleanup
  TestBase::Close();
}


void TestGpuMetricsRead::Run(void) {
  amdsmi_status_t err;

  TestBase::Run();
  if (setup_failed_) {
    std::cout << "** SetUp Failed for this test. Skipping.**" << std::endl;
    return;
  }

  for (uint32_t i = 0; i < num_monitor_devs(); ++i) {
    PrintDeviceHeader(processor_handles_[i]);
    std::cout << "Device #" << std::to_string(i) << "\n";

    IF_VERB(STANDARD) {
        std::cout << "\t**GPU METRICS: Using static struct (Backwards Compatibility):\n";
    }
    amdsmi_gpu_metrics_t smu;
    err =  amdsmi_get_gpu_metrics_info(processor_handles_[i], &smu);
    const char *status_string;
    amdsmi_status_code_to_string(err, &status_string);
    std::cout << "\t\t** amdsmi_get_gpu_metrics_info(): " << status_string
    << "\n";
    if (err != AMDSMI_STATUS_SUCCESS) {
      if (err == AMDSMI_STATUS_NOT_SUPPORTED) {
        IF_VERB(STANDARD) {
          std::cout << "\t**" <<
          "Not supported on this machine" << std::endl;
          return;
        }
      }
    } else {
      CHK_ERR_ASRT(err);
      IF_VERB(STANDARD) {
          std::cout << "METRIC TABLE HEADER:\n";
          std::cout << "structure_size=" << std::dec
          << static_cast<int>(smu.common_header.structure_size) << '\n';
          std::cout << "format_revision=" << std::dec
          << static_cast<int>(smu.common_header.format_revision) << '\n';
          std::cout << "content_revision=" << std::dec
          << static_cast<int>(smu.common_header.content_revision) << '\n';
          std::cout << "\n";
          std::cout << "TIME STAMPS (ns):\n";
          std::cout << std::dec << "system_clock_counter="
          << smu.system_clock_counter << '\n';
          std::cout << "firmware_timestamp (10ns resolution)=" << std::dec
          << smu.firmware_timestamp << '\n';
          std::cout << "\n";
          std::cout << "TEMPERATURES (C):\n";
          std::cout << std::dec << "temperature_edge= "
          << static_cast<uint16_t>(smu.temperature_edge) << '\n';
          std::cout << std::dec << "temperature_hotspot= "
          << static_cast<uint16_t>(smu.temperature_hotspot) << '\n';
          std::cout << std::dec << "temperature_mem= "
          << static_cast<uint16_t>(smu.temperature_mem) << '\n';
          std::cout << std::dec << "temperature_vrgfx= "
          << static_cast<uint16_t>(smu.temperature_vrgfx) << '\n';
          std::cout << std::dec << "temperature_vrsoc= "
          << static_cast<uint16_t>(smu.temperature_vrsoc) << '\n';
          std::cout << std::dec << "temperature_vrmem= "
          << static_cast<uint16_t>(smu.temperature_vrmem) << '\n';
          for (int i = 0; i < AMDSMI_NUM_HBM_INSTANCES; ++i) {
            std::cout << "temperature_hbm[" << i << "]= " << std::dec
            << static_cast<uint16_t>(smu.temperature_hbm[i]) << '\n';
          }
          std::cout << "\n";
          std::cout << "UTILIZATION (%):\n";
          std::cout << std::dec << "average_gfx_activity="
          << static_cast<uint16_t>(smu.average_gfx_activity) << '\n';
          std::cout << std::dec << "average_umc_activity="
          << static_cast<uint16_t>(smu.average_umc_activity) << '\n';
          std::cout << std::dec << "average_mm_activity="
          << static_cast<uint16_t>(smu.average_mm_activity) << '\n';
          std::cout << std::dec << "vcn_activity= [";
          uint16_t size = static_cast<uint16_t>(
            sizeof(smu.vcn_activity)/sizeof(smu.vcn_activity[0]));
          for (uint16_t i= 0; i < size; i++) {
            if (i+1 < size) {
              std::cout << std::dec << static_cast<uint16_t>(smu.vcn_activity[i]) << ", ";
            } else {
              std::cout << std::dec << static_cast<uint16_t>(smu.vcn_activity[i]);
            }
          }
          std::cout << std::dec << "]\n";
          std::cout << "\n";
          std::cout << std::dec << "jpeg_activity= [";
          size = static_cast<uint16_t>(
            sizeof(smu.jpeg_activity)/sizeof(smu.jpeg_activity[0]));
          for (uint16_t i= 0; i < size; i++) {
            if (i+1 < size) {
              std::cout << std::dec << static_cast<uint16_t>(smu.jpeg_activity[i]) << ", ";
            } else {
              std::cout << std::dec << static_cast<uint16_t>(smu.jpeg_activity[i]);
            }
          }
          std::cout << std::dec << "]\n";
          std::cout << "\n";
          std::cout << "POWER (W)/ENERGY (15.259uJ per 1ns):\n";
          std::cout << std::dec << "average_socket_power="
          << static_cast<uint16_t>(smu.average_socket_power) << '\n';
          std::cout << std::dec << "current_socket_power="
          << static_cast<uint16_t>(smu.current_socket_power) << '\n';
          std::cout << std::dec << "energy_accumulator="
          << static_cast<uint16_t>(smu.energy_accumulator) << '\n';
          std::cout << "\n";
          std::cout << "AVG CLOCKS (MHz):\n";
          std::cout << std::dec << "average_gfxclk_frequency="
          << static_cast<uint16_t>(smu.average_gfxclk_frequency) << '\n';
          std::cout << std::dec << "average_gfxclk_frequency="
          << static_cast<uint16_t>(smu.average_gfxclk_frequency) << '\n';
          std::cout << std::dec << "average_uclk_frequency="
          << static_cast<uint16_t>(smu.average_uclk_frequency) << '\n';
          std::cout << std::dec << "average_vclk0_frequency="
          << static_cast<uint16_t>(smu.average_vclk0_frequency) << '\n';
          std::cout << std::dec << "average_dclk0_frequency="
          << static_cast<uint16_t>(smu.average_dclk0_frequency) << '\n';
          std::cout << std::dec << "average_vclk1_frequency="
          << static_cast<uint16_t>(smu.average_vclk1_frequency) << '\n';
          std::cout << std::dec << "average_dclk1_frequency="
          << static_cast<uint16_t>(smu.average_dclk1_frequency) << '\n';
          std::cout << "\n";
          std::cout << "CURRENT CLOCKS (MHz):\n";
          std::cout << std::dec << "current_gfxclk="
          << smu.current_gfxclk << '\n';
          std::cout << std::dec << "current_gfxclks= [";
          size = static_cast<uint16_t>(
            sizeof(smu.current_gfxclks)/sizeof(smu.current_gfxclks[0]));
          for (uint16_t i= 0; i < size; i++) {
            if (i+1 < size) {
              std::cout << std::dec << static_cast<uint16_t>(smu.current_gfxclks[i]) << ", ";
            } else {
              std::cout << std::dec << static_cast<uint16_t>(smu.current_gfxclks[i]);
            }
          }
          std::cout << std::dec << "]\n";
          std::cout << std::dec << "current_socclk="
          << smu.current_socclk << '\n';
          std::cout << std::dec << "current_socclks= [";
          size = static_cast<uint16_t>(
            sizeof(smu.current_socclks)/sizeof(smu.current_socclks[0]));
          for (uint16_t i= 0; i < size; i++) {
            if (i+1 < size) {
              std::cout << std::dec << static_cast<uint16_t>(smu.current_socclks[i]) << ", ";
            } else {
              std::cout << std::dec << static_cast<uint16_t>(smu.current_socclks[i]);
            }
          }
          std::cout << std::dec << "]\n";
          std::cout << std::dec << "current_uclk="
          << static_cast<uint16_t>(smu.current_uclk) << '\n';
          std::cout << std::dec << "current_vclk0="
          << static_cast<uint16_t>(smu.current_vclk0) << '\n';
          std::cout << std::dec << "current_vclk0s= [";
          size = static_cast<uint16_t>(
            sizeof(smu.current_vclk0s)/sizeof(smu.current_vclk0s[0]));
          for (uint16_t i= 0; i < size; i++) {
            if (i+1 < size) {
              std::cout << std::dec << static_cast<uint16_t>(smu.current_vclk0s[i]) << ", ";
            } else {
              std::cout << std::dec << static_cast<uint16_t>(smu.current_vclk0s[i]);
            }
          }
          std::cout << std::dec << "]\n";
          std::cout << std::dec << "current_dclk0="
          << smu.current_dclk0 << '\n';
          std::cout << std::dec << "current_dclk0s= [";
          size = static_cast<uint16_t>(
            sizeof(smu.current_dclk0s)/sizeof(smu.current_dclk0s[0]));
          for (uint16_t i= 0; i < size; i++) {
            if (i+1 < size) {
              std::cout << std::dec << static_cast<uint16_t>(smu.current_dclk0s[i]) << ", ";
            } else {
              std::cout << std::dec << static_cast<uint16_t>(smu.current_dclk0s[i]);
            }
          }
          std::cout << std::dec << "]\n";
          std::cout << std::dec << "current_vclk1="
          << static_cast<uint16_t>(smu.current_vclk1) << '\n';
          std::cout << std::dec << "current_dclk1="
          << static_cast<uint16_t>(smu.current_dclk1) << '\n';
          std::cout << "\n";
          std::cout << "TROTTLE STATUS:\n";
          std::cout << std::dec << "throttle_status="
          << static_cast<uint32_t>(smu.throttle_status) << '\n';
          std::cout << "\n";
          std::cout << "FAN SPEED:\n";
          std::cout << std::dec << "current_fan_speed="
          << static_cast<uint16_t>(smu.current_fan_speed) << '\n';
          std::cout << "\n";
          std::cout << "LINK WIDTH (number of lanes) /SPEED (0.1 GT/s):\n";
          std::cout << "pcie_link_width="
          << std::to_string(smu.pcie_link_width) << '\n';
          std::cout << "pcie_link_speed="
          << std::to_string(smu.pcie_link_speed) << '\n';
          std::cout << "xgmi_link_width="
          << std::to_string(smu.xgmi_link_width) << '\n';
          std::cout << "xgmi_link_speed="
          << std::to_string(smu.xgmi_link_speed) << '\n';

          std::cout << "\n";
          std::cout << "Utilization Accumulated(%):\n";
          std::cout << "gfx_activity_acc="
          << std::dec << static_cast<uint32_t>(smu.gfx_activity_acc) << '\n';
          std::cout << "mem_activity_acc="
          << std::dec << static_cast<uint32_t>(smu.mem_activity_acc)  << '\n';

          std::cout << "\n";
          std::cout << "XGMI ACCUMULATED DATA TRANSFER SIZE (KB):\n";
          std::cout << std::dec << "xgmi_read_data_acc= [";
          size = static_cast<uint16_t>(
            sizeof(smu.xgmi_read_data_acc)/sizeof(smu.xgmi_read_data_acc[0]));
          for (uint16_t i= 0; i < size; i++) {
            if (i+1 < size) {
              std::cout << std::dec << static_cast<uint64_t>(smu.xgmi_read_data_acc[i]) << ", ";
            } else {
              std::cout << std::dec << static_cast<uint64_t>(smu.xgmi_read_data_acc[i]);
            }
          }
          std::cout << std::dec << "]\n";
          std::cout << std::dec << "xgmi_write_data_acc= [";
          size = static_cast<uint16_t>(
            sizeof(smu.xgmi_write_data_acc)/sizeof(smu.xgmi_write_data_acc[0]));
          for (uint16_t i= 0; i < size; i++) {
            if (i+1 < size) {
              std::cout << std::dec << static_cast<uint64_t>(smu.xgmi_write_data_acc[i]) << ", ";
            } else {
              std::cout << std::dec << static_cast<uint64_t>(smu.xgmi_write_data_acc[i]);
            }
          }
          std::cout << std::dec << "]\n";

          // Voltage (mV)
          std::cout << "voltage_soc = "
          << std::dec << static_cast<uint16_t>(smu.voltage_soc) << "\n";
          std::cout << "voltage_soc = "
          << std::dec << static_cast<uint16_t>(smu.voltage_gfx) << "\n";
          std::cout << "voltage_mem = "
          << std::dec << static_cast<uint16_t>(smu.voltage_mem) << "\n";

          std::cout << "indep_throttle_status = "
          << std::dec << static_cast<uint64_t>(smu.indep_throttle_status) << "\n";

          // Clock Lock Status. Each bit corresponds to clock instance
          std::cout << "gfxclk_lock_status (in hex) = "
          << std::hex << static_cast<uint32_t>(smu.gfxclk_lock_status) << std::dec <<"\n";

          // Bandwidth (GB/sec)
          std::cout << "pcie_bandwidth_acc=" << std::dec
          << static_cast<uint64_t>(smu.pcie_bandwidth_acc) << "\n";
          std::cout << "pcie_bandwidth_inst=" << std::dec
          << static_cast<uint64_t>(smu.pcie_bandwidth_inst) << "\n";

          // Counts
          std::cout << "pcie_l0_to_recov_count_acc= " << std::dec
          << static_cast<uint64_t>(smu.pcie_l0_to_recov_count_acc) << "\n";
          std::cout << "pcie_replay_count_acc= " << std::dec
          << static_cast<uint64_t>(smu.pcie_replay_count_acc) << "\n";
          std::cout << "pcie_replay_rover_count_acc= " << std::dec
          << static_cast<uint64_t>(smu.pcie_replay_rover_count_acc) << "\n";
          std::cout << "pcie_nak_rcvd_count_acc= " << std::dec
          << static_cast<uint32_t>(smu.pcie_nak_rcvd_count_acc) << "\n";
          std::cout << "pcie_replay_rover_count_acc= " << std::dec
          << static_cast<uint64_t>(smu.pcie_replay_rover_count_acc) << "\n";
      }
    }

    // Verify api support checking functionality is working
    err =  amdsmi_get_gpu_metrics_info(processor_handles_[i], nullptr);
    if (err !=AMDSMI_STATUS_INVAL) {
      DISPLAY_AMDSMI_ERR(err);
    }
    amdsmi_status_code_to_string(err, &status_string);
    std::cout << "\t\t** amdsmi_get_gpu_metrics_info(nullptr check): " << status_string << "\n";
    ASSERT_EQ(err, AMDSMI_STATUS_INVAL);
  }

/**
 * START OF INDIVIDUAL METRIC CALLS
 */

  auto val_ui16 = uint16_t(0);
  auto val_ui32 = uint32_t(0);
  auto val_ui64 = uint64_t(0);
  auto status_code(amdsmi_status_t::AMDSMI_STATUS_SUCCESS);
  for (uint32_t i = 0; i < num_monitor_devs(); ++i) {
    PrintDeviceHeader(processor_handles_[i]);
    std::cout << "Device #" << std::to_string(i) << "\n";

    auto temp_edge_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_temp_edge(processor_handles_[i], &temp_edge_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_temp_edge(): " << status_string << "\n";
    }

    auto temp_hotspot_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_temp_hotspot(processor_handles_[i], &temp_hotspot_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_temp_hotspot(): " << status_string << "\n";
    }

    auto temp_mem_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_temp_mem(processor_handles_[i], &temp_mem_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_temp_mem(): " << status_string << "\n";
    }

    auto temp_vrgfx_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_temp_vrgfx(processor_handles_[i], &temp_vrgfx_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_temp_vrgfx(): " << status_string << "\n";
    }

    auto temp_vrsoc_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_temp_vrsoc(processor_handles_[i], &temp_vrsoc_value);
   if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_temp_vrsoc(): " << status_string << "\n";
    }

    auto temp_vrmem_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_temp_vrmem(processor_handles_[i], &temp_vrmem_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_temp_vrmem(): " << status_string << "\n";
    }

    gpu_metric_temp_hbm_t temp_hbm_values;
    status_code = amdsmi_get_gpu_metrics_temp_hbm(processor_handles_[i], &temp_hbm_values);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_temp_hbm(): " << status_string << "\n";
    }

    auto temp_curr_socket_power_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_curr_socket_power(processor_handles_[i], &temp_curr_socket_power_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
   } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_curr_socket_power(): " << status_string << "\n";
    }

    auto temp_energy_accum_value = val_ui64;
    status_code = amdsmi_get_gpu_metrics_energy_acc(processor_handles_[i], &temp_energy_accum_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_energy_acc(): " << status_string << "\n";
    }

    auto temp_avg_socket_power_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_avg_socket_power(processor_handles_[i], &temp_avg_socket_power_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_temp_edge(): " << status_string << "\n";
    }

    auto temp_avg_gfx_activity_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_avg_gfx_activity(processor_handles_[i], &temp_avg_gfx_activity_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_avg_gfx_activity(): " << status_string << "\n";
    }

    auto temp_avg_umc_activity_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_avg_umc_activity(processor_handles_[i], &temp_avg_umc_activity_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_avg_umc_activity(): " << status_string << "\n";
    }

    auto temp_avg_mm_activity_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_avg_mm_activity(processor_handles_[i], &temp_avg_mm_activity_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_avg_mm_activity(): " << status_string << "\n";
    }

    gpu_metric_vcn_activity_t temp_vcn_values;
    status_code = amdsmi_get_gpu_metrics_vcn_activity(processor_handles_[i], &temp_vcn_values);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_vcn_activity(): " << status_string << "\n";
    }

    auto temp_mem_activity_accum_value = val_ui32;
    status_code = amdsmi_get_gpu_metrics_mem_activity_acc(processor_handles_[i], &temp_mem_activity_accum_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_mem_activity_acc(): " << status_string << "\n";
    }

    auto temp_gfx_activity_accum_value = val_ui32;
    status_code = amdsmi_get_gpu_metrics_gfx_activity_acc(processor_handles_[i], &temp_gfx_activity_accum_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_gfx_activity_acc(): " << status_string << "\n";
    }

    auto temp_avg_gfx_clock_freq_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_avg_gfx_clock_frequency(processor_handles_[i], &temp_avg_gfx_clock_freq_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_avg_gfx_clock_frequency(): " << status_string << "\n";
    }

    auto temp_avg_soc_clock_freq_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_avg_soc_clock_frequency(processor_handles_[i], &temp_avg_soc_clock_freq_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_avg_soc_clock_frequency(): " << status_string << "\n";
    }

    auto temp_avg_uclock_freq_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_avg_uclock_frequency(processor_handles_[i], &temp_avg_uclock_freq_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_avg_uclock_frequency(): " << status_string << "\n";
    }

    auto temp_avg_vclock0_freq_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_avg_vclock0_frequency(processor_handles_[i], &temp_avg_vclock0_freq_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_avg_vclock0_frequency(): " << status_string << "\n";
    }

    auto temp_avg_dclock0_freq_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_avg_dclock0_frequency(processor_handles_[i], &temp_avg_dclock0_freq_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_avg_dclock0_frequency(): " << status_string << "\n";
    }

    auto temp_avg_vclock1_freq_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_avg_vclock1_frequency(processor_handles_[i], &temp_avg_vclock1_freq_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_avg_vclock1_frequency(): " << status_string << "\n";
    }

    auto temp_avg_dclock1_freq_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_avg_dclock1_frequency(processor_handles_[i], &temp_avg_dclock1_freq_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_avg_dclock1_frequency(): " << status_string << "\n";
    }

    auto temp_curr_vclk1_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_curr_vclk1(processor_handles_[i], &temp_curr_vclk1_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_curr_vclk1(): " << status_string << "\n";
    }

    auto temp_curr_dclk1_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_curr_dclk1(processor_handles_[i], &temp_curr_dclk1_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_curr_dclk1(): " << status_string << "\n";
    }

    auto temp_curr_uclk_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_curr_uclk(processor_handles_[i], &temp_curr_uclk_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_curr_uclk(): " << status_string << "\n";
    }

    gpu_metric_curr_dclk0_t temp_curr_dclk0_values;
    status_code = amdsmi_get_gpu_metrics_curr_dclk0(processor_handles_[i], &temp_curr_dclk0_values);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_curr_dclk0(): " << status_string << "\n";
    }

    gpu_metric_curr_gfxclk_t temp_curr_gfxclk_values;
    status_code = amdsmi_get_gpu_metrics_curr_gfxclk(processor_handles_[i], &temp_curr_gfxclk_values);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_curr_gfxclk(): " << status_string << "\n";
    }

    gpu_metric_curr_socclk_t temp_curr_socclk_values;
    status_code = amdsmi_get_gpu_metrics_curr_socclk(processor_handles_[i], &temp_curr_socclk_values);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_curr_socclk(): " << status_string << "\n";
    }

    gpu_metric_curr_vclk0_t temp_curr_vclk0_values;
    status_code = amdsmi_get_gpu_metrics_curr_vclk0(processor_handles_[i], &temp_curr_vclk0_values);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_curr_vclk0(): " << status_string << "\n";
    }

    auto temp_indep_throttle_status_value = val_ui64;
    status_code = amdsmi_get_gpu_metrics_indep_throttle_status(processor_handles_[i], &temp_indep_throttle_status_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_indep_throttle_status(): " << status_string << "\n";
    }

    auto temp_throttle_status_value = val_ui32;
    status_code = amdsmi_get_gpu_metrics_throttle_status(processor_handles_[i], &temp_throttle_status_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_throttle_status(): " << status_string << "\n";
    }

    auto temp_gfxclk_lock_status_value = val_ui32;
    status_code = amdsmi_get_gpu_metrics_gfxclk_lock_status(processor_handles_[i], &temp_gfxclk_lock_status_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_gfxclk_lock_status(): " << status_string << "\n";
    }

    auto temp_curr_fan_speed_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_curr_fan_speed(processor_handles_[i], &temp_curr_fan_speed_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_curr_fan_speed(): " << status_string << "\n";
    }

    auto temp_pcie_link_width_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_pcie_link_width(processor_handles_[i], &temp_pcie_link_width_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_pcie_link_width(): " << status_string << "\n";
    }

    auto temp_pcie_link_speed_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_pcie_link_speed(processor_handles_[i], &temp_pcie_link_speed_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_pcie_link_speed(): " << status_string << "\n";
    }

    auto temp_pcie_bandwidth_accum_value = val_ui64;
    status_code = amdsmi_get_gpu_metrics_pcie_bandwidth_acc(processor_handles_[i], &temp_pcie_bandwidth_accum_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_pcie_bandwidth_acc(): " << status_string << "\n";
    }

    auto temp_pcie_bandwidth_inst_value = val_ui64;
    status_code = amdsmi_get_gpu_metrics_pcie_bandwidth_inst(processor_handles_[i], &temp_pcie_bandwidth_inst_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_pcie_bandwidth_inst(): " << status_string << "\n";
    }

    auto temp_pcie_l0_recov_count_accum_value = val_ui64;
    status_code = amdsmi_get_gpu_metrics_pcie_l0_recov_count_acc(processor_handles_[i], &temp_pcie_l0_recov_count_accum_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_pcie_l0_recov_count_acc(): " << status_string << "\n";
    }

    auto temp_pcie_replay_count_accum_value = val_ui64;
    status_code = amdsmi_get_gpu_metrics_pcie_replay_count_acc(processor_handles_[i], &temp_pcie_replay_count_accum_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_pcie_replay_count_acc(): " << status_string << "\n";
    }

    auto temp_pcie_replay_rover_count_accum_value = val_ui64;
    status_code = amdsmi_get_gpu_metrics_pcie_replay_rover_count_acc(processor_handles_[i], &temp_pcie_replay_rover_count_accum_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_pcie_replay_rover_count_acc(): " << status_string << "\n";
    }

    auto temp_xgmi_link_width_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_xgmi_link_width(processor_handles_[i], &temp_xgmi_link_width_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_xgmi_link_width(): " << status_string << "\n";
    }

    auto temp_xgmi_link_speed_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_xgmi_link_speed(processor_handles_[i], &temp_xgmi_link_speed_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_xgmi_link_speed(): " << status_string << "\n";
    }

    gpu_metric_xgmi_read_data_acc_t temp_xgmi_read_values;
    status_code = amdsmi_get_gpu_metrics_xgmi_read_data(processor_handles_[i], &temp_xgmi_read_values);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_xgmi_read_data(): " << status_string << "\n";
    }

    gpu_metric_xgmi_write_data_acc_t temp_xgmi_write_values;
    status_code = amdsmi_get_gpu_metrics_xgmi_write_data(processor_handles_[i], &temp_xgmi_write_values);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_xgmi_write_data(): " << status_string << "\n";
    }

    auto temp_voltage_soc_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_volt_soc(processor_handles_[i], &temp_voltage_soc_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_volt_soc(): " << status_string << "\n";
    }

    auto temp_voltage_gfx_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_volt_gfx(processor_handles_[i], &temp_voltage_gfx_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_volt_gfx(): " << status_string << "\n";
    }

    auto temp_voltage_mem_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_volt_mem(processor_handles_[i], &temp_voltage_mem_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_volt_mem(): " << status_string << "\n";
    }

    auto temp_system_clock_counter_value = val_ui64;
    status_code = amdsmi_get_gpu_metrics_system_clock_counter(processor_handles_[i], &temp_system_clock_counter_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_system_clock_counter(): " << status_string << "\n";
    }

    auto temp_firmware_timestamp_value = val_ui64;
    status_code = amdsmi_get_gpu_metrics_firmware_timestamp(processor_handles_[i], &temp_firmware_timestamp_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_firmware_timestamp(): " << status_string << "\n";
    }

    auto temp_xcd_counter_value = val_ui16;
    status_code = amdsmi_get_gpu_metrics_xcd_counter(processor_handles_[i], &temp_xcd_counter_value);
    if (status_code != AMDSMI_STATUS_NOT_SUPPORTED) {
      CHK_ERR_ASRT(status_code);
    } else {
      const char *status_string;
      amdsmi_status_code_to_string(status_code, &status_string);
      std::cout << "\t\t** amdsmi_get_gpu_metrics_xcd_counter(): " << status_string << "\n";
    }

    IF_VERB(STANDARD) {
      std::cout << "\n";
      std::cout << "\t[Temperature]" << "\n";
      std::cout << "\t  -> temp_edge(): " << std::dec << temp_edge_value << "\n";
      std::cout << "\t  -> temp_hotspot(): " << std::dec << temp_hotspot_value << "\n";
      std::cout << "\t  -> temp_mem(): " << std::dec << temp_mem_value << "\n";
      std::cout << "\t  -> temp_vrgfx(): " << std::dec << temp_vrgfx_value << "\n";
      std::cout << "\t  -> temp_vrsoc(): " << std::dec << temp_vrsoc_value << "\n";
      std::cout << "\t  -> temp_vrmem(): " << std::dec << temp_vrmem_value << "\n";
      std::cout << "\t  -> temp_hbm(temp_hbm_values): [";
      uint16_t size = static_cast<uint16_t>(
          sizeof(temp_hbm_values) / sizeof(temp_hbm_values[0]));
      for (uint16_t i = 0; i < size; i++) {
        if (i + 1 < size) {
          std::cout << std::dec << temp_hbm_values[i] << ", ";
        } else {
          std::cout << std::dec << temp_hbm_values[i];
        }
      }
      std::cout << std::dec << "]\n";

      std::cout << "\n";
      std::cout << "\t[Power/Energy]" << "\n";
      std::cout << "\t  -> current_socket_power(): " << std::dec << temp_curr_socket_power_value << "\n";
      std::cout << "\t  -> energy_accum(): " << std::dec << temp_energy_accum_value << "\n";
      std::cout << "\t  -> average_socket_power(): " << std::dec << temp_avg_socket_power_value << "\n";

      std::cout << "\n";
      std::cout << "\t[Utilization]" << "\n";
      std::cout << "\t  -> average_gfx_activity(): " << std::dec << temp_avg_gfx_activity_value << "\n";
      std::cout << "\t  -> average_umc_activity(): " << std::dec << temp_avg_umc_activity_value << "\n";
      std::cout << "\t  -> average_mm_activity(): " << std::dec << temp_avg_mm_activity_value << "\n";
      std::cout << "\t  -> vcn_activity(temp_vcn_values): [";
      size = static_cast<uint16_t>(
          sizeof(temp_vcn_values) / sizeof(temp_vcn_values[0]));
      for (uint16_t i = 0; i < size; i++) {
        if (i + 1 < size) {
          std::cout << std::dec << temp_vcn_values[i] << ", ";
        } else {
          std::cout << std::dec << temp_vcn_values[i];
        }
      }
      std::cout << std::dec << "]\n";
      std::cout << "\t  -> mem_activity_accum(): " << std::dec << temp_mem_activity_accum_value << "\n";
      std::cout << "\t  -> gfx_activity_accum(): " << std::dec << temp_gfx_activity_accum_value << "\n";

      std::cout << "\n";
      std::cout << "\t[Average Clock]" << "\n";
      std::cout << "\t  -> average_gfx_clock_frequency(): " << std::dec << temp_avg_gfx_clock_freq_value << "\n";
      std::cout << "\t  -> average_soc_clock_frequency(): " << std::dec << temp_avg_soc_clock_freq_value << "\n";
      std::cout << "\t  -> average_uclock_frequency(): " << std::dec << temp_avg_uclock_freq_value << "\n";
      std::cout << "\t  -> average_vclock0_frequency(): " << std::dec << std::dec << temp_avg_vclock0_freq_value << "\n";
      std::cout << "\t  -> average_dclock0_frequency(): " << std::dec << temp_avg_dclock0_freq_value << "\n";
      std::cout << "\t  -> average_vclock1_frequency(): " << std::dec << temp_avg_vclock1_freq_value << "\n";
      std::cout << "\t  -> average_dclock1_frequency(): " << std::dec << temp_avg_dclock1_freq_value << "\n";

      std::cout << "\n";
      std::cout << "\t[Current Clock]" << "\n";
      std::cout << "\t  -> current_vclock1(): " << std::dec << temp_curr_vclk1_value << "\n";
      std::cout << "\t  -> current_dclock1(): " << std::dec << temp_curr_dclk1_value << "\n";
      std::cout << "\t  -> current_uclock(): " << std::dec << temp_curr_uclk_value << "\n";
      std::cout << "\t  -> current_dclk0(temp_curr_dclk0_values): [";
      size = static_cast<uint16_t>(
          sizeof(temp_curr_dclk0_values) / sizeof(temp_curr_dclk0_values[0]));
      for (uint16_t i = 0; i < size; i++) {
        if (i + 1 < size) {
          std::cout << std::dec << temp_curr_dclk0_values[i] << ", ";
        } else {
          std::cout << std::dec << temp_curr_dclk0_values[i];
        }
      }
      std::cout << std::dec << "]\n";
      std::cout << "\t  -> current_gfxclk(temp_curr_gfxclk_values): [";
      size = static_cast<uint16_t>(
          sizeof(temp_curr_gfxclk_values) / sizeof(temp_curr_gfxclk_values[0]));
      for (uint16_t i = 0; i < size; i++) {
        if (i + 1 < size) {
          std::cout << std::dec << temp_curr_gfxclk_values[i] << ", ";
        } else {
          std::cout << std::dec << temp_curr_gfxclk_values[i];
        }
      }
      std::cout << std::dec << "]\n";
      std::cout << "\t  -> current_soc_clock(temp_curr_socclk_values): [";
      size = static_cast<uint16_t>(
          sizeof(temp_curr_socclk_values) / sizeof(temp_curr_socclk_values[0]));
      for (uint16_t i = 0; i < size; i++) {
        if (i + 1 < size) {
          std::cout << std::dec << temp_curr_socclk_values[i] << ", ";
        } else {
          std::cout << std::dec << temp_curr_socclk_values[i];
        }
      }
      std::cout << std::dec << "]\n";
      std::cout << "\t  -> current_vclk0(temp_curr_vclk0_values): [";
      size = static_cast<uint16_t>(
          sizeof(temp_curr_vclk0_values) / sizeof(temp_curr_vclk0_values[0]));
      for (uint16_t i = 0; i < size; i++) {
        if (i + 1 < size) {
          std::cout << std::dec << temp_curr_vclk0_values[i] << ", ";
        } else {
          std::cout << std::dec << temp_curr_vclk0_values[i];
        }
      }
      std::cout << std::dec << "]\n";

      std::cout << "\n";
      std::cout << "\t[Throttle]" << "\n";
      std::cout << "\t  -> indep_throttle_status(): " << std::dec << temp_indep_throttle_status_value << "\n";
      std::cout << "\t  -> throttle_status(): " << std::dec << temp_throttle_status_value << "\n";

      std::cout << "\n";
      std::cout << "\t[Gfx Clock Lock]" << "\n";
      std::cout << "\t  -> gfxclk_lock_status(): " << std::dec << temp_gfxclk_lock_status_value << "\n";

      std::cout << "\n";
      std::cout << "\t[Current Fan Speed]" << "\n";
      std::cout << "\t  -> current_fan_speed(): " << std::dec << temp_curr_fan_speed_value << "\n";

      std::cout << "\n";
      std::cout << "\t[Link/Bandwidth/Speed]" << "\n";
      std::cout << "\t  -> pcie_link_width(): " << std::dec << temp_pcie_link_width_value << "\n";
      std::cout << "\t  -> pcie_link_speed(): " << std::dec << temp_pcie_link_speed_value << "\n";
      std::cout << "\t  -> pcie_bandwidth_accum(): " << std::dec << std::dec << temp_pcie_bandwidth_accum_value << "\n";
      std::cout << "\t  -> pcie_bandwidth_inst(): " << std::dec << temp_pcie_bandwidth_inst_value << "\n";
      std::cout << "\t  -> pcie_l0_recov_count_accum(): " << std::dec << std::dec << temp_pcie_l0_recov_count_accum_value << "\n";
      std::cout << "\t  -> pcie_replay_count_accum(): " << std::dec << temp_pcie_replay_count_accum_value << "\n";
      std::cout << "\t  -> pcie_replay_rollover_count_accum(): " << std::dec << temp_pcie_replay_rover_count_accum_value << "\n";
      std::cout << "\t  -> xgmi_link_width(): " << std::dec << temp_xgmi_link_width_value << "\n";
      std::cout << "\t  -> xgmi_link_speed(): " << std::dec << std::dec << temp_xgmi_link_speed_value << "\n";
      std::cout << "\t  -> xgmi_read_data(temp_xgmi_read_values): ";
      size = static_cast<uint16_t>(
          sizeof(temp_xgmi_read_values) / sizeof(temp_xgmi_read_values[0]));
      for (uint16_t i = 0; i < size; i++) {
        if (i + 1 < size) {
          std::cout << std::dec << temp_xgmi_read_values[i] << ", ";
        } else {
          std::cout << std::dec << temp_xgmi_read_values[i];
        }
      }
      std::cout << std::dec << "]\n";
      std::cout << "\t  -> xgmi_write_data(temp_xgmi_write_values): [";
      size = static_cast<uint16_t>(
          sizeof(temp_xgmi_write_values) / sizeof(temp_xgmi_write_values[0]));
      for (uint16_t i = 0; i < size; i++) {
        if (i + 1 < size) {
          std::cout << std::dec << temp_xgmi_write_values[i] << ", ";
        } else {
          std::cout << std::dec << temp_xgmi_write_values[i];
        }
      }
      std::cout << std::dec << "]\n";

      std::cout << "\n";
      std::cout << "\t[Voltage]" << "\n";
      std::cout << "\t  -> voltage_soc(): " << std::dec << temp_voltage_soc_value << "\n";
      std::cout << "\t  -> voltage_gfx(): " << std::dec << temp_voltage_gfx_value << "\n";
      std::cout << "\t  -> voltage_mem(): " << std::dec << temp_voltage_mem_value << "\n";

      std::cout << "\n";
      std::cout << "\t[Timestamp]" << "\n";
      std::cout << "\t  -> system_clock_counter(): " << std::dec << temp_system_clock_counter_value << "\n";
      std::cout << "\t  -> firmware_timestamp(): " << std::dec << temp_firmware_timestamp_value << "\n";

      std::cout << "\n";
      std::cout << "\t[XCD Counter]" << "\n";
      std::cout << "\t  -> xcd_counter(): " << std::dec << temp_xcd_counter_value << "\n";
      std::cout << "\n\n";
    }
  }

}

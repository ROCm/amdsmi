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
#include <assert.h>
#include <stdint.h>
#include <unistd.h>

#include <vector>
#include <iostream>
#include <bitset>
#include "amd_smi.h"

#define CHK_AMDSMI_RET(RET) { \
  if (RET != AMDSMI_STATUS_SUCCESS) { \
    const char *err_str; \
    std::cout << "AMDSMI call returned " << RET \
      << " at line " << __LINE__ << std::endl; \
      amdsmi_status_string(RET, &err_str); \
      std::cout << err_str << std::endl; \
    return RET; \
  } \
}

int main() {
  amdsmi_status_t ret;

  // Init amdsmi for sockets and devices.
  // Here we are only interested in AMD_GPUS.
  ret = amdsmi_init(AMD_SMI_INIT_AMD_GPUS);
  CHK_AMDSMI_RET(ret)

  // Get all sockets
  uint32_t socket_count = 0;
  amdsmi_socket_handle* sockets = nullptr;
  ret = amdsmi_get_socket_handles(&socket_count, &sockets);
  CHK_AMDSMI_RET(ret)
  std::cout << "Total Socket: " << socket_count << std::endl;

  // For each socket, get identifier and devices
  for (uint32_t i=0; i < socket_count; i++) {
    // Get Socket info
    char socket_name[128];
    ret = amdsmi_get_socket_info(sockets[i], socket_name, 128);
    CHK_AMDSMI_RET(ret)
    std::cout << "Socket " << socket_name << std::endl;

    // Get all devices of the socket
    uint32_t device_count = 0;
    amdsmi_device_handle* device_handles = nullptr;
    ret = amdsmi_get_device_handles(sockets[i],
            &device_count, &device_handles);
    CHK_AMDSMI_RET(ret)

    // For each device of the socket, get name and temperature.
    for (uint32_t j=0; j < device_count; j++) {
      // Get device type. Since the amdsmi is initialized with
      // AMD_SMI_INIT_AMD_GPUS, the device_type must be AMD_GPU.
      device_type_t device_type;
      ret = amdsmi_get_device_type(device_handles[j], &device_type);
      CHK_AMDSMI_RET(ret)
      if (device_type != AMD_GPU) {
        std::cout << "Expect AMD_GPU device type!\n";
        return 1;
      }

      // Get device name
      amdsmi_board_info board_info;
      ret = amdsmi_get_board_info(device_handles[j], &board_info);
      CHK_AMDSMI_RET(ret)
      std::cout << "\tdevice "
                  << j <<"\n\t\tName:" << board_info.product_name << std::endl;

      // Get temperature
      int64_t val_i64 = 0;
      ret = amdsmi_dev_temp_metric_get(device_handles[j], 0,
              AMDSMI_TEMP_CURRENT, &val_i64);
      CHK_AMDSMI_RET(ret)
      std::cout << "\t\tTemperature: " << val_i64/1000 << "C" << std::endl;

      // Get frame buffer
      amdsmi_vram_info_t vram_usage;
      ret = amdsmi_get_vram_usage(device_handles[j], &vram_usage);
      CHK_AMDSMI_RET(ret)
      std::cout << "\t\tFrame buffer usage (MB): " << vram_usage.vram_used << "/"
              << vram_usage.vram_total << std::endl;

      // Get Cap info
      amdsmi_gpu_caps_t caps_info = {};
      ret = amdsmi_get_caps_info(device_handles[j], &caps_info);
      CHK_AMDSMI_RET(ret)
      std::cout << "\t\tGFX IP Major: " << caps_info.gfx.gfxip_major << "\n";
      std::cout << "\t\tGFX IP Minor: " << caps_info.gfx.gfxip_minor << "\n";
      std::cout << "\t\tCU IP Count: " << caps_info.gfx.gfxip_cu_count << "\n";
      std::cout << "\t\tDMA IP Count: " << caps_info.dma_ip_count << "\n";
      std::cout << "\t\tGFX IP Count: " << caps_info.gfx_ip_count << "\n";
      std::cout << "\t\tMM IP Count: " << int(caps_info.mm.mm_ip_count) << "\n";
    }
  }

  // Clean up resources allocated at amdsmi_init. It will invalidate sockets
  // and devices pointers
  ret = amdsmi_shut_down();
  CHK_AMDSMI_RET(ret)

  return 0;
}


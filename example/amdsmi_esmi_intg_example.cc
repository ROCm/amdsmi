/*
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
#include <assert.h>
#include <stdint.h>
#include <unistd.h>
#include <vector>
#include <iostream>
#include <bitset>
#include <iomanip>
#include "amd_smi/amdsmi.h"
#include "asm/amd_hsmp.h"
#include <cstring>
#include <cmath>

#define SHOWLINESZ 256

#define CHK_AMDSMI_RET(RET)                                                    \
    {                                                                          \
        if (RET != AMDSMI_STATUS_SUCCESS) {                                    \
            const char *err_str;                                               \
            const char **status_str;                                           \
            cout << "AMDSMI call returned " << RET << " at line "              \
                      << __LINE__ << endl;                                     \
            status_str = amdsmi_get_esmi_err_msg(RET, &err_str);               \
            cout << *status_str << endl;                                       \
            return RET;                                                        \
        }                                                                      \
    }

using std::cin;
using std::cout;
using std::endl;
using std::fixed;
using std::setprecision;
using std::vector;

int main(int argc, char **argv) {
  amdsmi_status_t ret;
  uint32_t proto_ver;
  amdsmi_smu_fw_version_t smu_fw = {};

  // Initialize esmi for AMD CPUs
  ret = amdsmi_init(AMDSMI_INIT_AMD_CPUS);
  CHK_AMDSMI_RET(ret)

  // Get all sockets
  uint32_t socket_count = 0;

  /*ret = amdsmi_get_cpusocket_handles(&socket_count, nullptr);
  CHK_AMDSMI_RET(ret)

  // Allocate the memory for the sockets
  vector<amdsmi_cpusocket_handle> sockets(socket_count);

  // Get the sockets of the system
  ret = amdsmi_get_cpusocket_handles(&socket_count, &sockets[0]);
  CHK_AMDSMI_RET(ret)*/
  ret = amdsmi_get_socket_handles(&socket_count, nullptr);
  CHK_AMDSMI_RET(ret)
  // Allocate the memory for the sockets
  vector<amdsmi_socket_handle> sockets(socket_count);
  // Get the sockets of the system
  ret = amdsmi_get_socket_handles(&socket_count, &sockets[0]);
  CHK_AMDSMI_RET(ret)
  cout << "Total Socket: " << socket_count << endl;
  // For each socket, get identifier and cores
  for (uint8_t i = 0; i < socket_count; i++) {
    uint32_t cpu_count = 0;
    uint32_t core_count = 0;
    processor_type_t processor_type = AMD_CPU;
    ret = amdsmi_get_processor_handles_by_type(sockets[i], processor_type, nullptr, &cpu_count);
    CHK_AMDSMI_RET(ret)
    vector<amdsmi_processor_handle> plist(cpu_count);
    ret = amdsmi_get_processor_handles_by_type(sockets[i], processor_type, &plist[0], &cpu_count);
    CHK_AMDSMI_RET(ret)
    cout << endl;
    // Read core count for each sockets
    processor_type = AMD_CPU_CORE;
    ret = amdsmi_get_processor_handles_by_type(sockets[i], processor_type, nullptr, &core_count);
    CHK_AMDSMI_RET(ret)
    vector<amdsmi_processor_handle> core_list(core_count);
    ret = amdsmi_get_processor_handles_by_type(sockets[i], processor_type, &core_list[0], &core_count);
    CHK_AMDSMI_RET(ret)
    for (int index = 0; index < plist.size(); index++) {
      socket_count = plist.size();
      ret = amdsmi_get_cpu_hsmp_proto_ver(plist[i], &proto_ver);
      CHK_AMDSMI_RET(ret)

      cout<<"\n------------------------------------------";
      cout<<"\n| HSMP Proto Version  |  "<< proto_ver <<"\t\t |"<< endl;
      cout<<"------------------------------------------\n";

      ret = amdsmi_get_cpu_smu_fw_version(plist[i], &smu_fw);
      CHK_AMDSMI_RET(ret)

      cout<<"\n------------------------------------------";
      cout<<"\n| SMU FW Version  |  "
              <<(unsigned)smu_fw.major<<"."
              <<(unsigned)smu_fw.minor<<"."
              <<(unsigned)smu_fw.debug
              <<"\t\t |"<<endl;
      cout<<"------------------------------------------\n";

      uint32_t err_bits = 0;

      uint32_t prochot;
      cout<<"\n-------------------------------------------------";
      cout<<"\n| Sensor Name\t\t\t |";
      for (uint32_t i = 0; i < socket_count; i++) {
          cout<<setprecision(3)<<" Socket "<<i<<"\t|";
      }
      cout<<"\n-------------------------------------------------";
      cout<<"\n| ProchotStatus:\t\t |";
      ret = amdsmi_get_cpu_prochot_status(plist[i], &prochot);
      CHK_AMDSMI_RET(ret)
      if (!ret) {
          cout<<setprecision(7)<< (prochot ? "active" : "inactive")<<"\t|";
      } else {
          err_bits |= 1 << ret;
          cout<<" NA (Err:" <<ret<<"     |";
      }
      cout<<"\n-------------------------------------------------\n";

      size_t len;
      char str[SHOWLINESZ] = {};
      int retVal = 0;
      cout<<"\n-------------------------------------------------";
      cout<<"\n| Sensor Name\t\t\t |";
      for (uint32_t i = 0; i < socket_count; i++) {
          cout<<setprecision(3)<<" Socket "<<i<<"\t|";
      }
      cout<<"\n-------------------------------------------------";
      cout<<"\n| fclk (Mhz)\t\t\t |";
      retVal = snprintf(str, SHOWLINESZ, "\n| mclk (Mhz)\t\t\t |");

      len = strlen(str);
      uint32_t fclk, mclk, cclk;
      err_bits = 0;
      ret = amdsmi_get_cpu_fclk_mclk(plist[i], &fclk, &mclk);
      CHK_AMDSMI_RET(ret)
      if (!ret) {
          cout<<setprecision(7)<<" "<<fclk<<"\t\t|";
          retVal = snprintf(str + len, SHOWLINESZ - len, " %d\t\t|", mclk);
      } else {
          err_bits |= 1 << ret;
          cout<<" NA (Err: "<<setprecision(2)<<ret<<"     |";
          retVal = snprintf(str + len, SHOWLINESZ - len, " NA (Err: %-2d)     |", ret);
      }
      if (retVal > 0 && retVal < SHOWLINESZ)
          cout << str;
      else
          cout <<"error writing to buffer" << endl;

      cout<<"\n-------------------------------------------------\n";

      uint32_t socket_power;
      cout<<"\n-------------------------------------------------";
      cout<<"\n| Sensor Name\t\t\t |";
      for (uint32_t i = 0; i < socket_count; i++) {
          cout<<setprecision(3)<<" Socket "<<i<<"\t|";
      }
      cout<<"\n-------------------------------------------------";
      cout<<"\n| Power (Watts)\t\t\t | ";

      ret = amdsmi_get_cpu_socket_power(plist[i], &socket_power);
      CHK_AMDSMI_RET(ret)

      if (!ret) {
          cout<<fixed<<setprecision(3)<<static_cast<double>(socket_power)/1000<<"\t|";
      } else {
          err_bits |= 1 << ret;
          cout<<" NA (Err:" <<ret<<"     |";
      }

      uint32_t power_limit;
      cout<<"\n| PowerLimit (Watts)\t\t | ";

      ret = amdsmi_get_cpu_socket_power_cap(plist[i], &power_limit);
      CHK_AMDSMI_RET(ret)

      if (!ret) {
          cout<<fixed<<setprecision(3)<<static_cast<double>(power_limit)/1000<<"\t|";
      } else {
          err_bits |= 1 << ret;
          cout<<" NA (Err:" <<ret<<"     |";
      }

      uint32_t power_max;
      cout<<"\n| PowerLimitMax (Watts)\t\t | ";

      ret = amdsmi_get_cpu_socket_power_cap_max(plist[i], &power_max);
      CHK_AMDSMI_RET(ret)

      if (!ret) {
          cout<<fixed<<setprecision(3)<<static_cast<double>(power_max)/1000<<"\t|";
      } else {
          err_bits |= 1 << ret;
          cout<<" NA (Err:" <<ret<<"     |";
      }
      cout<<"\n-------------------------------------------------\n";

      uint32_t input_power;
      power_max = 0;
      cout<<"\nEnter the max power to be set:\n";
      cin>>input_power;
      ret = amdsmi_get_cpu_socket_power_cap_max(plist[i], &power_max);
      CHK_AMDSMI_RET(ret)
      if ((ret == AMDSMI_STATUS_SUCCESS) && (input_power > power_max)) {
          cout<<"Input power is more than max power limit,"
              " limiting to "<<static_cast<double>(power_max)/1000<<"Watts\n";
          input_power = power_max;
      }
      ret = amdsmi_set_cpu_socket_power_cap(plist[i], input_power);
      CHK_AMDSMI_RET(ret)
      if (!ret) {
          cout<<"Socket["<<i<<"] power_limit set to "
          <<fixed<<setprecision(3)<<static_cast<double>(input_power)/1000<<" Watts successfully\n";
      }
      cout<<"\n-------------------------------------------------\n";
    }
  }
  // Clean up resources allocated at amdsmi_init
  ret = amdsmi_shut_down();
  CHK_AMDSMI_RET(ret)

  return 0;
}

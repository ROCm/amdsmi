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
#include <iomanip>
#include "amd_smi/amdsmi.h"
#include <cstring>

using namespace std;

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

int main(int argc, char **argv) {
  amdsmi_status_t ret;
  uint32_t proto_ver;
  amdsmi_smu_fw_version_t smu_fw = {};
  amdsmi_cpusocket_handle socket_handle;

  // Initialize esmi for AMD CPUs
  ret = amdsmi_init(AMDSMI_INIT_AMD_CPUS);
  CHK_AMDSMI_RET(ret)

  // Get all sockets
  uint32_t socket_count = 0;

  ret = amdsmi_get_cpusocket_handles(&socket_count, nullptr);
  CHK_AMDSMI_RET(ret)

  // Allocate the memory for the sockets
  vector<amdsmi_cpusocket_handle> sockets(socket_count);

  // Get the sockets of the system
  ret = amdsmi_get_cpusocket_handles(&socket_count, &sockets[0]);
  CHK_AMDSMI_RET(ret)

  cout << "Total Socket: " << socket_count << endl;

  // For each socket, get identifier and cores
  for (uint32_t i = 0; i < socket_count; i++) {
    // Get Socket info
    uint32_t socket_info;
    ret = amdsmi_get_cpusocket_info(sockets[i], socket_info);
    CHK_AMDSMI_RET(ret)
    cout << "Socket " << socket_info << endl;

    // Get the core count available for the socket.
    uint32_t core_count = 0;
    ret = amdsmi_get_cpucore_handles(sockets[i], &core_count, nullptr);
    CHK_AMDSMI_RET(ret)

    // Allocate the memory for the cpu core handles on the socket
    vector<amdsmi_processor_handle> processor_handles(core_count);
    // Get all cores of the socket
    ret = amdsmi_get_cpucore_handles(sockets[i],
                                    &core_count, &processor_handles[0]);
    CHK_AMDSMI_RET(ret)
    cout << "core_count=" << core_count << endl;

    ret = amdsmi_get_cpu_hsmp_proto_ver(sockets[i], &proto_ver);
    CHK_AMDSMI_RET(ret)

    cout<<"\n------------------------------------------";
    cout<<"\n| HSMP Proto Version  |  "<< proto_ver <<"\t\t |"<< endl;
    cout<<"------------------------------------------\n";

    ret = amdsmi_get_cpu_smu_fw_version(sockets[i], &smu_fw);
    CHK_AMDSMI_RET(ret)

    cout<<"\n------------------------------------------";
    cout<<"\n| SMU FW Version  |  "
            <<(unsigned)smu_fw.major<<"."
            <<(unsigned)smu_fw.minor<<"."
            <<(unsigned)smu_fw.debug
            <<"\t\t |"<<endl;
    cout<<"------------------------------------------\n";

    uint32_t err_bits = 0;

    uint64_t pkg_input;
    cout<<"\n-------------------------------------------------";
    cout<<"\n| Sensor Name\t\t\t |";
    for (uint32_t i = 0; i < socket_count; i++) {
        cout<<setprecision(3)<<" Socket "<<i<<"\t|";
    }
    cout<<"\n-------------------------------------------------";
    cout<<"\n| Energy (K Joules)\t\t | ";

    ret = amdsmi_get_cpu_socket_energy(sockets[i], i, &pkg_input);
    CHK_AMDSMI_RET(ret)

    if (!ret) {
        cout<<setprecision(7)<<static_cast<double>(pkg_input)/1000000000<<"\t|";
    } else {
        err_bits |= 1 << ret;
        cout<<" NA (Err:" <<ret<<"     |";
    }
    cout<<"\n-------------------------------------------------\n";

    err_bits = 0;
    uint32_t prochot;
    cout<<"\n-------------------------------------------------";
    cout<<"\n| Sensor Name\t\t\t |";
    for (uint32_t i = 0; i < socket_count; i++) {
        cout<<setprecision(3)<<" Socket "<<i<<"\t|";
    }
    cout<<"\n-------------------------------------------------";
    cout<<"\n| ProchotStatus:\t\t |";
    ret = amdsmi_get_cpu_prochot_status(sockets[i], i, &prochot);
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
    ret = amdsmi_get_cpu_fclk_mclk(sockets[i], i, &fclk, &mclk);
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
    cout<<"-----------------------------------------------------------------";
    ret = amdsmi_get_cpu_cclk_limit(sockets[i], i, &cclk);
    CHK_AMDSMI_RET(ret)
    cout<<"\n| SOCKET["<<i<<"] core clock current frequency limit (MHz) : "<<cclk<<"\t|\n";
    cout<<"-----------------------------------------------------------------\n";

    uint64_t core_input = 0;
    ret = amdsmi_get_cpu_core_energy(processor_handles[i], i, &core_input);
    CHK_AMDSMI_RET(ret)
    cout<<"\n-------------------------------------------------";
    cout<<"\n| core["<<i<<"] energy  | "<<setprecision(7)
        <<static_cast<double>(core_input)/1000000<<" Joules\t\t|\n";
    cout<<"-------------------------------------------------\n";

    core_input = 0;
    cout<<"\n| CPU energies in Joules:\t\t\t\t\t\t\t\t\t|";
    for (uint32_t j = 0; j < core_count; j++) {
        ret = amdsmi_get_cpu_core_energy(processor_handles[j], j, &core_input);
        CHK_AMDSMI_RET(ret)
        if(!(j % 8)) {
            if(j < 10)
                cout<<"\n| cpu [0"<<j<<"] :";
            else
                cout<<"\n| cpu ["<<j<<"] :";
        }
        cout<<setw(8)<<right<<fixed<<setprecision(3)<<static_cast<double>(core_input)/1000000<<"  ";
        if (j % 8 == 7)
            cout<<"\t|";
    }
        cout<<"\n-------------------------------------------------\n";

    uint32_t c_clk = 0;
    ret = amdsmi_get_cpu_core_current_freq_limit(processor_handles[i], i, &c_clk);
    CHK_AMDSMI_RET(ret)

    cout<<"--------------------------------------------------------------";
    cout<<"\n| CPU["<<i<<"] core clock current frequency limit (MHz) : "<<c_clk<<"\t|\n";
    cout<<"--------------------------------------------------------------\n";

    uint32_t power;
    cout<<"\n-------------------------------------------------";
    cout<<"\n| Sensor Name\t\t\t |";
    for (uint32_t i = 0; i < socket_count; i++) {
        cout<<setprecision(3)<<" Socket "<<i<<"\t|";
    }
    cout<<"\n-------------------------------------------------";
    cout<<"\n| Power (Watts)\t\t\t | ";

    ret = amdsmi_get_cpu_socket_power(sockets[i], i, &power);
    CHK_AMDSMI_RET(ret)

    if (!ret) {
        cout<<fixed<<setprecision(3)<<static_cast<double>(power)/1000<<"\t|";
    } else {
        err_bits |= 1 << ret;
        cout<<" NA (Err:" <<ret<<"     |";
    }

    uint32_t powerlimit;
    cout<<"\n| PowerLimit (Watts)\t\t | ";

    ret = amdsmi_get_cpu_socket_power_cap(sockets[i], i, &powerlimit);
    CHK_AMDSMI_RET(ret)

    if (!ret) {
        cout<<fixed<<setprecision(3)<<static_cast<double>(powerlimit)/1000<<"\t|";
    } else {
        err_bits |= 1 << ret;
        cout<<" NA (Err:" <<ret<<"     |";
    }

    uint32_t powermax;
    cout<<"\n| PowerLimitMax (Watts)\t\t | ";

    ret = amdsmi_get_cpu_socket_power_cap_max(sockets[i], i, &powermax);
    CHK_AMDSMI_RET(ret)

    if (!ret) {
        cout<<fixed<<setprecision(3)<<static_cast<double>(powermax)/1000<<"\t|";
    } else {
        err_bits |= 1 << ret;
        cout<<" NA (Err:" <<ret<<"     |";
    }
    cout<<"\n-------------------------------------------------\n";

    uint32_t input_power;
    powermax = 0;
    cout<<"\nEnter the max power to be set:\n";
    cin>>input_power;
    ret = amdsmi_get_cpu_socket_power_cap_max(sockets[i], i, &powermax);
    CHK_AMDSMI_RET(ret)
    if ((ret == AMDSMI_STATUS_SUCCESS) && (input_power > powermax)) {
        cout<<"Input power is more than max power limit,"
            " limiting to "<<static_cast<double>(powermax)/1000<<"Watts\n";
        input_power = powermax;
    }
    ret = amdsmi_set_cpu_socket_power_cap(sockets[i], i, input_power);
    CHK_AMDSMI_RET(ret)
    if (!ret) {
        cout<<"Socket["<<i<<"] power_limit set to "
        <<fixed<<setprecision(3)<<static_cast<double>(input_power)/1000<<" Watts successfully\n";
    }
    cout<<"\n-------------------------------------------------\n";

    uint8_t mode;
    const char *err_str;
    cout <<"Enter the power efficiency mode to be set[0, 1 or 2]:\n";
    cin>>mode;
    ret = amdsmi_set_cpu_pwr_efficiency_mode(sockets[i], i, mode);
    CHK_AMDSMI_RET(ret)

    if (ret != AMDSMI_STATUS_SUCCESS) {
        cout<<"Failed to set power efficiency mode for socket["<<i<<"], Err["
            <<ret<<"]: "<<amdsmi_get_esmi_err_msg(ret, &err_str)<<"\n";
        return ret;
    }

    if (!ret)
        cout<<"Power efficiency profile policy is set to "<<mode<<"successfully\n";

    cout<<"\n-------------------------------------------------\n";

    uint32_t svi_power;
    cout<<"\n| SVI Power Telemetry (mWatts) \t |";

    ret = amdsmi_get_cpu_pwr_svi_telemetry_all_rails(sockets[i], i, &svi_power);
    CHK_AMDSMI_RET(ret)

    if (!ret) {
        cout<<fixed<<setprecision(3)<<static_cast<double>(svi_power)/1000<<"\t|";
    } else {
        err_bits |= 1 << ret;
        cout<<" NA (Err:" <<ret<<"     |";
    }
    cout<<"\n-------------------------------------------------\n";
  }
  // Clean up resources allocated at amdsmi_init
  ret = amdsmi_shut_down();
  CHK_AMDSMI_RET(ret)

  return 0;
}

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

  ret = amdsmi_get_cpusocket_handles(&socket_count, nullptr);
  CHK_AMDSMI_RET(ret)

  // Allocate the memory for the sockets
  vector<amdsmi_cpusocket_handle> sockets(socket_count);

  // Get the sockets of the system
  ret = amdsmi_get_cpusocket_handles(&socket_count, &sockets[0]);
  CHK_AMDSMI_RET(ret)

  cout << "Total Socket: " << socket_count << endl;

  // For each socket, get identifier and cores
  for (uint8_t i = 0; i < socket_count; i++) {
    // Get Socket info
    uint32_t socket_info = 0;
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

    uint32_t c_clk = 0;
    ret = amdsmi_get_cpu_core_current_freq_limit(processor_handles[i], i, &c_clk);
    CHK_AMDSMI_RET(ret)

    cout<<"--------------------------------------------------------------";
    cout<<"\n| CPU["<<i<<"] core clock current frequency limit (MHz) : "<<c_clk<<"\t|\n";
    cout<<"--------------------------------------------------------------\n";

    uint32_t socket_power;
    cout<<"\n-------------------------------------------------";
    cout<<"\n| Sensor Name\t\t\t |";
    for (uint32_t i = 0; i < socket_count; i++) {
        cout<<setprecision(3)<<" Socket "<<i<<"\t|";
    }
    cout<<"\n-------------------------------------------------";
    cout<<"\n| Power (Watts)\t\t\t | ";

    ret = amdsmi_get_cpu_socket_power(sockets[i], i, &socket_power);
    CHK_AMDSMI_RET(ret)

    if (!ret) {
        cout<<fixed<<setprecision(3)<<static_cast<double>(socket_power)/1000<<"\t|";
    } else {
        err_bits |= 1 << ret;
        cout<<" NA (Err:" <<ret<<"     |";
    }

    uint32_t power_limit;
    cout<<"\n| PowerLimit (Watts)\t\t | ";

    ret = amdsmi_get_cpu_socket_power_cap(sockets[i], i, &power_limit);
    CHK_AMDSMI_RET(ret)

    if (!ret) {
        cout<<fixed<<setprecision(3)<<static_cast<double>(power_limit)/1000<<"\t|";
    } else {
        err_bits |= 1 << ret;
        cout<<" NA (Err:" <<ret<<"     |";
    }

    uint32_t power_max;
    cout<<"\n| PowerLimitMax (Watts)\t\t | ";

    ret = amdsmi_get_cpu_socket_power_cap_max(sockets[i], i, &power_max);
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
    ret = amdsmi_get_cpu_socket_power_cap_max(sockets[i], i, &power_max);
    CHK_AMDSMI_RET(ret)
    if ((ret == AMDSMI_STATUS_SUCCESS) && (input_power > power_max)) {
        cout<<"Input power is more than max power limit,"
            " limiting to "<<static_cast<double>(power_max)/1000<<"Watts\n";
        input_power = power_max;
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
            <<ret<<"]: "<<*amdsmi_get_esmi_err_msg(ret, &err_str)<<"\n";
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

    uint32_t boost_limit = 0;
    const char *err_str1;
    ret = amdsmi_get_cpu_core_boostlimit(processor_handles[i], i, &boost_limit);
    CHK_AMDSMI_RET(ret)

    if(ret)
        cout<<"Failed: to get core"<<"["<<i<<"] boostlimit, Err["<<ret<<"]: "
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
    else
        cout<<"| core["<<i<<"] boostlimit (MHz)\t | "<<boost_limit<<" \t |\n";

    cout<<"\n-------------------------------------------------\n";

    boost_limit = 0;
    cout<<"\nEnter the boost limit to be set:\n";
    cin>>boost_limit;
    ret = amdsmi_set_cpu_core_boostlimit(processor_handles[i], i, boost_limit);
    CHK_AMDSMI_RET(ret)

    if(ret != AMDSMI_STATUS_SUCCESS)
        cout<<"Failed: to set core"<<"["<<i<<"] boostlimit, Err["<<ret<<"]: "
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;

    ret = amdsmi_get_cpu_core_boostlimit(processor_handles[i], i, &boost_limit);
    CHK_AMDSMI_RET(ret)

    if(ret)
        cout<<"Failed: to get core"<<"["<<i<<"] boostlimit, Err["<<ret<<"]: "
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
    else
        cout<<"| core["<<i<<"] boostlimit (MHz)\t | "<<boost_limit<<" \t |\n";
    cout<<"\n-------------------------------------------------\n";

    ret = amdsmi_set_cpu_socket_boostlimit(sockets[i], i, boost_limit);
    CHK_AMDSMI_RET(ret)

    if(ret)
        cout<<"Failed: to set socket"<<"["<<i<<"] boostlimit, Err["<<ret<<"]: "
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;

    cout<<"\n-------------------------------------------------\n";

    uint32_t residency = 0;
    ret = amdsmi_get_cpu_socket_c0_residency(sockets[i], i, &residency);
    CHK_AMDSMI_RET(ret)

    if(ret != AMDSMI_STATUS_SUCCESS)
        cout<<"Failed: to get socket"<<"["<<i<<"] c0_residency, Err["<<ret<<"]: "
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
    else
        cout<<"| socket["<<i<<"] c0_residency(%)   | "<<residency<<"   |\n";

    cout<<"\n-------------------------------------------------\n";

    cout<<"\n| DDR Bandwidth\t\t\t\t |\n";
    amdsmi_ddr_bw_metrics_t ddr;
    ret = amdsmi_get_cpu_ddr_bw(sockets[i], &ddr);
    CHK_AMDSMI_RET(ret)

    if(!ret) {
        cout<<"\n| \tDDR Max BW (GB/s)\t |"<<ddr.max_bw<<"\t|"<<endl;
        cout<<"\n| \tDDR Utilized BW (GB/s)\t |"<<ddr.utilized_bw<<"\t|"<<endl;
        cout<<"\n| \tDDR Utilized Percent(%)\t |"<<ddr.utilized_pct<<"\t|"<<endl;
      }

    cout<<"\n-------------------------------------------------\n";

    uint32_t tmon;
    cout<<"\n| Socket temperature (°C)\t\t |";
    ret = amdsmi_get_cpu_socket_temperature(sockets[i], i, &tmon);
    CHK_AMDSMI_RET(ret)

    if (!ret) {
            cout<<fixed<<setprecision(3)<<""<<(double)tmon/1000<<"|";
     } else {
            err_bits |= 1 << ret;
            cout<<" NA (Err: "<<ret<<")     |";
     }

    cout<<"\n-------------------------------------------------\n";

    amdsmi_temp_range_refresh_rate_t rate;
    uint8_t dimm_addr = 0x80;
    cout<<"\n| Socket DIMM temp range and refresh rate\t\t |\n";
    ret = amdsmi_get_cpu_dimm_temp_range_and_refresh_rate(sockets[i], i, dimm_addr, &rate);
    CHK_AMDSMI_RET(ret)

    if(ret) {
        cout<<"\n| \tDIMM temp range\t |"<<rate.range<<"\t|"<<endl;
        cout<<"\n| \tRefresh rate\t |"<<rate.ref_rate<<"\t|"<<endl;
    } else
        cout<<"Failed: to get socket"<<"["<<i<<"] DIMM temperature range and refresh rate, Err["<<ret<<"]: "
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;

    cout<<"\n-------------------------------------------------\n";

    amdsmi_dimm_power_t dimm_power;
    cout<<"\n| Socket DIMM power consumption\t\t |\n";
    ret = amdsmi_get_cpu_dimm_power_consumption(sockets[i], i, dimm_addr, &dimm_power);
    CHK_AMDSMI_RET(ret)

    if(ret) {
        cout<<"\n| Power(mWatts)\t\t |"<<dimm_power.power<<"\t|"<<endl;
        cout<<"\n| Power update rate(ms)\t |"<<dimm_power.update_rate<<"\t|"<<endl;
        cout<<"\n| Dimm address \t\t |"<<dimm_power.dimm_addr<<"\t|"<<endl;
    } else
        cout<<"Failed: to get socket"<<"["<<i<<"] DIMM power and update rate, Err["<<ret<<"]: "
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;

    cout<<"\n-------------------------------------------------\n";

    amdsmi_dimm_thermal_t d_sensor;
    cout<<"\n| Socket DIMM thermal sensor\t\t |\n";
    ret = amdsmi_get_cpu_dimm_thermal_sensor(sockets[i], i, dimm_addr, &d_sensor);
    CHK_AMDSMI_RET(ret)

    if(ret) {
        cout<<"\n| Temperature(°C)\t |"<<d_sensor.temp<<"\t|"<<endl;
        cout<<"\n| Update rate(ms)\t |"<<d_sensor.update_rate<<"\t|"<<endl;
        cout<<"\n| Dimm address returned\t |"<<d_sensor.dimm_addr<<"\t|"<<endl;
    } else
        cout<<"Failed: to get socket"<<"["<<i<<"] DIMM temperature and update rate, Err["<<ret<<"]: "
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;

    cout<<"\n-------------------------------------------------\n";

    uint8_t min, max;
    cout<<"\nEnter the XGMI min value to be set:\n";
    cin>>min;
    cout<<"\nEnter the XGMI max value to be set:\n";
    cin>>max;

    ret = amdsmi_set_cpu_xgmi_width(sockets[i], min, max);
    CHK_AMDSMI_RET(ret)

    if(ret)
        cout<<"Failed: to set xGMI link width, Err["<<ret<<"]: "
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
     else
        cout<<"xGMI link width (min:"<<min<< "max:"<<max<<") is set successfully\n";

    cout<<"\n-------------------------------------------------\n";

    uint8_t min_link_width, max_link_width;
    cout<<"\nEnter the GMI3 link width min value to be set:\n";
    cin>>min_link_width;
    cout<<"\nEnter the GMI3 link width max value to be set:\n";
    cin>>max_link_width;

    ret = amdsmi_set_cpu_gmi3_link_width_range(sockets[i], i, min_link_width, max_link_width);
    CHK_AMDSMI_RET(ret)

    if(ret)
        cout<<"Failed to set gmi3 link width for socket["<<i<<"] Err["<<ret<<"]:"
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
     else
        cout<<"Gmi3 link width range is set successfully\n";

    cout<<"\n-------------------------------------------------\n";

    ret = amdsmi_cpu_apb_enable(sockets[i], i);
    CHK_AMDSMI_RET(ret)

    if(ret)
        cout<<"Failed: to enable DF performance boost algo on socket["<<i<<"] Err["<<ret<<"]:"
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
     else
        cout<<"APB is enabled successfully on socket["<<i<<"]\n";

    cout<<"\n-------------------------------------------------\n";

    int8_t pstate;
    cout<<"\nEnter the pstate to be set:\n";
    cin>>pstate;
    ret = amdsmi_cpu_apb_disable(sockets[i], i, pstate);
    CHK_AMDSMI_RET(ret)

    if(ret)
        cout<<"Failed: to set socket["<<i<<"] DF pstate, Err["<<ret<<"]:"
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
     else
        cout<<"APB is disabled, P-state is set to ["<<pstate<<"] on socket["<<i<<"] successfully\n";

    cout<<"\n-------------------------------------------------\n";

    uint8_t min_val=0, max_val=2;
    uint8_t nbio_id=1;

    ret = amdsmi_set_cpu_socket_lclk_dpm_level(sockets[i], i, nbio_id, min_val, max_val);
    CHK_AMDSMI_RET(ret)

    if(ret != AMDSMI_STATUS_SUCCESS)
        cout<<"Failed: to set lclk dpm level for socket["<<i<<"], nbioid["<<unsigned(nbio_id)<<"], Err["<<ret<<"]:"
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
     else
        cout<<"Socket["<<i<<"] nbio["<<unsigned(nbio_id)<<"] LCLK frequency set successfully\n";

    cout<<"\n-------------------------------------------------\n";

    amdsmi_dpm_level_t nbio;
    ret = amdsmi_get_cpu_socket_lclk_dpm_level(sockets[i], i, nbio_id, &nbio);
    CHK_AMDSMI_RET(ret)

    if(ret != AMDSMI_STATUS_SUCCESS)
        cout<<"Failed: to get lclk dpm level for socket["<<i<<"], nbioid["<<unsigned(nbio_id)<<"], Err["<<ret<<"]:"
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
     else {
        cout<<"| \tMIN\t | "<<unsigned(nbio.min_dpm_level)<<"\t   |\n";
        cout<<"| \tMAX\t | "<<unsigned(nbio.max_dpm_level)<<"\t   |\n";
     }

     cout<<"\n-------------------------------------------------\n";

    uint8_t rate_ctrl;
    uint8_t prev_mode;
    std::string pcie_strings[] = {
           "automatically detect based on bandwidth utilisation",
           "limited to Gen4 rate",
           "limited to Gen5 rate"
           };
    cout<<"\nEnter the rate ctrl to be set:\n";
    cin>>rate_ctrl;

    ret = amdsmi_set_cpu_pcie_link_rate(sockets[i], i, rate_ctrl, &prev_mode);
    CHK_AMDSMI_RET(ret)

    if(ret != AMDSMI_STATUS_SUCCESS)
        cout<<"Failed to set pcie link rate control for socket["<<i<<"], Err["<<ret<<"]:"
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
     else {
        cout<<"Pcie link rate is set to "<<rate_ctrl<<" (i.e. "<<pcie_strings[rate_ctrl]<<") successfully.\n";
        cout<<"\nPrevious pcie link rate control was : "<<prev_mode<<"\n";
     }

    cout<<"\n-------------------------------------------------\n";
    uint8_t max_pstate, min_pstate;
    cout<<"\nEnter the max_pstate to be set:\n";
    cin>>max_pstate;
    cout<<"\nEnter the min_pstate to be set:\n";
    cin>>min_pstate;

    ret = amdsmi_set_cpu_df_pstate_range(sockets[i], i, max_pstate, min_pstate);
    CHK_AMDSMI_RET(ret)

    if(ret != AMDSMI_STATUS_SUCCESS)
        cout<<"Failed to set df pstate range, Err["<<ret<<"]:"
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
     else
        cout<<"Data Fabric PState range(max:"<<unsigned(max_pstate)
            <<" min:"<<unsigned(min_pstate)<<") set successfully\n";

    cout<<"\n-------------------------------------------------\n";

    amdsmi_link_id_bw_type_t io_link;
    uint32_t bw;
    char* link = "P0";
    io_link.link_name = link;
    io_link.bw_type = static_cast<amdsmi_io_bw_encoding_t>(1) ;
    ret = amdsmi_get_cpu_current_io_bandwidth(sockets[i], i, io_link, &bw);
    CHK_AMDSMI_RET(ret)

    if(ret != AMDSMI_STATUS_SUCCESS)
        cout<<"Failed to get io bandwidth width for socket ["<<i<<"], Err["<<ret<<"]:"
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
     else
        cout<<"| Current IO Aggregate bandwidth of link"<<io_link.link_name<<" | "<<bw<<" Mbps |\n";

    cout<<"\n-------------------------------------------------\n";

    amdsmi_link_id_bw_type_t xgmi_link;
    uint32_t bw1;
    int bw_ind = 1;
    char* link1 = "P1";
    xgmi_link.link_name = link1;
    xgmi_link.bw_type = static_cast<amdsmi_io_bw_encoding_t>(1<<bw_ind) ;
    ret = amdsmi_get_cpu_current_xgmi_bw(sockets[i], xgmi_link, &bw1);
    CHK_AMDSMI_RET(ret)

    if(ret != AMDSMI_STATUS_SUCCESS)
        cout<<"Failed to get xgmi bandwidth width, Err["<<ret<<"]:"
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
     else
        cout<<"| Current "<<bw_string[bw_ind]<<"bandwidth of xGMI link "<<xgmi_link.link_name<<" | "<<bw<<" Mbps |\n";

     cout<<"\n-------------------------------------------------\n";

    uint32_t met_ver;
    ret = amdsmi_get_metrics_table_version(sockets[i], &met_ver);
    CHK_AMDSMI_RET(ret)

    if (ret != AMDSMI_STATUS_SUCCESS) {
        cout<<"Failed to get Metrics Table Version, Err["<<ret<<"]:"
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
     } else
        cout<<"\n| METRICS TABLE Version   |  "<<met_ver<<" \t\t |\n";

    cout<<"\n-------------------------------------------------\n";

    double fraction_q10 = 1/pow(2,10);
    double fraction_uq10 = fraction_q10;

    struct hsmp_metric_table mtbl;
    ret = amdsmi_get_metrics_table(sockets[i], i, &mtbl);
    CHK_AMDSMI_RET(ret)

    if (ret != AMDSMI_STATUS_SUCCESS) {
        cout<<"Failed to get Metrics Table for socket["<<i<<"], Err["<<ret<<"]:"
            <<*amdsmi_get_esmi_err_msg(ret, &err_str1)<<endl;
     } else {
        cout<<"\n| METRICS TABLE  \t\t |\n";
        cout<<"\n| ACCUMULATOR COUNTER                   |  "<<mtbl.accumulation_counter<<"\t\t|\n";
        cout<<"\n| SOCKET POWER LIMIT                    |  "<<(mtbl.socket_power_limit * fraction_uq10)<<" W\t\t|\n";
        cout<<"\n| MAX SOCKET POWER LIMIT                    |  "<<(mtbl.max_socket_power_limit * fraction_uq10)<<" W\t\t|\n";
        cout<<"\n| SOCKET POWER                     |  "<<(mtbl.socket_power * fraction_uq10)<<" W\t\t|\n";
    }
    cout<<"\n-------------------------------------------------\n";

  }
  // Clean up resources allocated at amdsmi_init
  ret = amdsmi_shut_down();
  CHK_AMDSMI_RET(ret)

  return 0;
}

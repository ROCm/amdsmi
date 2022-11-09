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

#include "amd_smi/amd_smi.h"
#include <bitset>
#include <iostream>
#include <pwd.h>
#include <sys/stat.h>
#include <vector>

#define CHK_AMDSMI_RET(RET)                                                    \
    {                                                                          \
        if (RET != AMDSMI_STATUS_SUCCESS) {                                    \
            const char *err_str;                                               \
            std::cout << "AMDSMI call returned " << RET << " at line "         \
                      << __LINE__ << std::endl;                                \
            amdsmi_status_string(RET, &err_str);                               \
            std::cout << err_str << std::endl;                                 \
            return RET;                                                        \
        }                                                                      \
    }

int main() {
    amdsmi_status_t ret;

    // Init amdsmi for sockets and devices.
    // Here we are only interested in AMD_GPUS.
    ret = amdsmi_init(AMDSMI_INIT_AMD_GPUS);
    CHK_AMDSMI_RET(ret)

    // Get all sockets
    uint32_t socket_count = 0;

    // Get the socket count available for the system.
    ret = amdsmi_get_socket_handles(&socket_count, nullptr);
    CHK_AMDSMI_RET(ret)

    // Allocate the memory for the sockets
    std::vector<amdsmi_socket_handle> sockets(socket_count);
    // Get the sockets of the system
    ret = amdsmi_get_socket_handles(&socket_count, &sockets[0]);
    CHK_AMDSMI_RET(ret)

    std::cout << "Total Socket: " << socket_count << std::endl;

    // For each socket, get identifier and devices
    for (uint32_t i = 0; i < socket_count; i++) {
        // Get Socket info
        char socket_info[128];
        ret = amdsmi_get_socket_info(sockets[i], socket_info, 128);
        CHK_AMDSMI_RET(ret)
        std::cout << "Socket " << socket_info << std::endl;

        // Get the device count available for the socket.
        uint32_t device_count = 0;
        ret = amdsmi_get_device_handles(sockets[i], &device_count, nullptr);
        CHK_AMDSMI_RET(ret)

        // Allocate the memory for the device handlers on the socket
        std::vector<amdsmi_device_handle> device_handles(device_count);
        // Get all devices of the socket
        ret = amdsmi_get_device_handles(sockets[i],
                                        &device_count, &device_handles[0]);
        CHK_AMDSMI_RET(ret)

        // For each device of the socket, get name and temperature.
        for (uint32_t j = 0; j < device_count; j++) {
            // Get device type. Since the amdsmi is initialized with
            // AMD_SMI_INIT_AMD_GPUS, the device_type must be AMD_GPU.
            device_type_t device_type = {};
            ret = amdsmi_get_device_type(device_handles[j], &device_type);
            CHK_AMDSMI_RET(ret)
            if (device_type != AMD_GPU) {
                std::cout << "Expect AMD_GPU device type!\n";
                return AMDSMI_STATUS_NOT_SUPPORTED;
            }

            // Get BDF info
            amdsmi_bdf_t bdf = {};
            ret = amdsmi_get_device_bdf(device_handles[j], &bdf);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_device_bdf:\n");
            printf("\tDevice[%d] BDF %04x:%02x:%02x.%d\n\n", i,
                   bdf.domain_number, bdf.bus_number, bdf.device_number,
                   bdf.function_number);

            // Get handle from BDF
            amdsmi_device_handle dev_handle;
            ret = amdsmi_get_device_handle_from_bdf(bdf, &device_handles[0], device_count, &dev_handle);
            CHK_AMDSMI_RET(ret)

            // Get ASIC info
            amdsmi_asic_info_t asic_info = {};
            ret = amdsmi_get_asic_info(device_handles[j], &asic_info);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_asic_info:\n");
            printf("\tMarket Name: %s\n", asic_info.market_name);
            printf("\tFamilyID: 0x%x\n", asic_info.family);
            printf("\tDeviceID: 0x%lx\n", asic_info.device_id);
            printf("\tVendorID: 0x%x\n", asic_info.vendor_id);
            printf("\tRevisionID: 0x%x\n", asic_info.rev_id);
            printf("\tAsic serial: 0x%s\n\n", asic_info.asic_serial);

            // Get VBIOS info
            amdsmi_vbios_info_t vbios_info = {};
            ret = amdsmi_get_vbios_info(device_handles[j], &vbios_info);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_vbios_info:\n");
            printf("\tVBios Name: %s\n", vbios_info.name);
            printf("\tBuild Date: %s\n", vbios_info.build_date);
            printf("\tPart Number: %s\n", vbios_info.part_number);
            printf("\tVBios Version: %d\n", vbios_info.vbios_version);
            printf("\tVBios Version String: %s\n\n",
                   vbios_info.vbios_version_string);

            // Get power measure
            amdsmi_power_measure_t power_measure = {};
            ret = amdsmi_get_power_measure(device_handles[j], &power_measure);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_power_measure:\n");
            printf("\tCurrent GFX Voltage: %d\n",
                   power_measure.voltage_gfx);
            printf("\tAverage socket power: %d\n",
                   power_measure.average_socket_power);
            printf("\tEnergy accumulator: %d\n\n",
                   power_measure.energy_accumulator);

            // Get driver version
            char version[AMDSMI_MAX_DRIVER_VERSION_LENGTH];
            int version_length = AMDSMI_MAX_DRIVER_VERSION_LENGTH;
            ret = amdsmi_get_driver_version(device_handles[j], &version_length, version);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_driver_version:\n");
            printf("\tDriver version: %s\n\n", version);

            // Get device uuid
            unsigned int uuid_length = AMDSMI_GPU_UUID_SIZE;
	        char uuid[AMDSMI_GPU_UUID_SIZE];
            ret = amdsmi_get_device_uuid(device_handles[j], &uuid_length, uuid);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_device_uuid:\n");
            printf("\tDevice uuid: %s\n\n", uuid);

            // Get engine usage info
            amdsmi_engine_usage_t engine_usage = {};
            ret = amdsmi_get_gpu_activity(device_handles[j], &engine_usage);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_gpu_activity:\n");
            printf("\tAverage GFX Activity: %d\n",
                   engine_usage.gfx_activity);
            printf("\tAverage MM Activity: %d\n",
                   engine_usage.mm_activity[0]);
            printf("\tAverage UMC Activity: %d\n\n",
                   engine_usage.umc_activity);

            // Get firmware info
            amdsmi_fw_info_t fw_information = {};
            ret = amdsmi_get_fw_info(device_handles[j], &fw_information);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_fw_info:\n");
            printf("\tFirmware version: %d\n", fw_information.num_fw_info);
            printf("\tSMU: %ld\n",
                   fw_information.fw_info_list[amdsmi_fw_block_t::FW_ID_SMU]
                       .fw_version);
            printf("\tSMC: %ld\n",
                   fw_information.fw_info_list[amdsmi_fw_block_t::FW_ID_SMC]
                       .fw_version);
            printf("\tVCN: %ld\n",
                   fw_information.fw_info_list[amdsmi_fw_block_t::FW_ID_VCN]
                       .fw_version);
            printf("\tCP_ME: %ld\n",
                   fw_information.fw_info_list[amdsmi_fw_block_t::FW_ID_CP_ME]
                       .fw_version);
            printf("\tCP_PFP: %ld\n",
                   fw_information.fw_info_list[amdsmi_fw_block_t::FW_ID_CP_PFP]
                       .fw_version);
            printf("\tCP_CE: %ld\n",
                   fw_information.fw_info_list[amdsmi_fw_block_t::FW_ID_CP_CE]
                       .fw_version);
            printf("\tRLC: %ld\n",
                   fw_information.fw_info_list[amdsmi_fw_block_t::FW_ID_RLC]
                       .fw_version);
            printf("\tCP_MEC1: %ld\n",
                   fw_information.fw_info_list[amdsmi_fw_block_t::FW_ID_CP_MEC1]
                       .fw_version);
            printf("\tCP_MEC2: %ld\n",
                   fw_information.fw_info_list[amdsmi_fw_block_t::FW_ID_CP_MEC2]
                       .fw_version);
            printf("\tSDMA0: %ld\n",
                   fw_information.fw_info_list[amdsmi_fw_block_t::FW_ID_SDMA0]
                       .fw_version);
            printf("\tMC: %ld\n",
                   fw_information.fw_info_list[amdsmi_fw_block_t::FW_ID_MC]
                       .fw_version);
            printf("\tRLC RESTORE LIST CNTL: %ld\n",
                   fw_information
                       .fw_info_list
                           [amdsmi_fw_block_t::FW_ID_RLC_RESTORE_LIST_CNTL]
                       .fw_version);
            printf("\tRLC RESTORE LIST GPM MEM: %ld\n",
                   fw_information
                       .fw_info_list
                           [amdsmi_fw_block_t::FW_ID_RLC_RESTORE_LIST_GPM_MEM]
                       .fw_version);
            printf("\tRLC RESTORE LIST SRM MEM: %ld\n",
                   fw_information
                       .fw_info_list
                           [amdsmi_fw_block_t::FW_ID_RLC_RESTORE_LIST_SRM_MEM]
                       .fw_version);
            printf(
                "\tPSP SOSDRV: %ld\n\n",
                fw_information.fw_info_list[amdsmi_fw_block_t::FW_ID_PSP_SOSDRV]
                    .fw_version);

            // Get GPU power limit info
            amdsmi_power_limit_t power_limit = {};
            ret = amdsmi_get_power_limit(device_handles[j], &power_limit);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_power_limit:\n");
            printf("\tGPU Power limit: %d\n\n", power_limit.limit);

            // Get GFX clock measurements
            amdsmi_clk_measure_t gfx_clk_values = {};
            ret = amdsmi_get_clock_measure(device_handles[j], CLK_TYPE_GFX,
                                           &gfx_clk_values);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_clock_measure:\n");
            printf("\tGPU GFX Max Clock: %d\n", gfx_clk_values.max_clk);
            printf("\tGPU GFX Average Clock: %d\n", gfx_clk_values.avg_clk);
            printf("\tGPU GFX Current Clock: %d\n", gfx_clk_values.cur_clk);

            // Get MEM clock measurements
            amdsmi_clk_measure_t mem_clk_values = {};
            ret = amdsmi_get_clock_measure(device_handles[j], CLK_TYPE_MEM,
                                           &mem_clk_values);
            CHK_AMDSMI_RET(ret)
            printf("\tGPU MEM Max Clock: %d\n", mem_clk_values.max_clk);
            printf("\tGPU MEM Average Clock: %d\n", mem_clk_values.avg_clk);
            printf("\tGPU MEM Current Clock: %d\n\n", mem_clk_values.cur_clk);

            // Get PCIe status
            amdsmi_pcie_info_t pcie_info = {};
            ret = amdsmi_get_pcie_link_status(device_handles[j], &pcie_info);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_pcie_link_status:\n");
            printf("\tPCIe lanes: %d\n", pcie_info.pcie_lanes);
            printf("\tPCIe speed: %d\n\n", pcie_info.pcie_speed);

            // Get PCIe caps
            amdsmi_pcie_info_t pcie_caps_info = {};
            ret = amdsmi_get_pcie_link_caps(device_handles[j], &pcie_caps_info);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_pcie_link_caps:\n");
            printf("\tPCIe max lanes: %d\n", pcie_caps_info.pcie_lanes);
            printf("\tPCIe max speed: %d\n\n", pcie_caps_info.pcie_speed);

            // Get VRAM temperature limit
            amdsmi_temperature_limit_t mem_temp_limit = {};
            ret = amdsmi_get_temperature_limit(
                device_handles[j], TEMPERATURE_TYPE_VRAM, &mem_temp_limit);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_temperature_limit:\n");
            printf("\tGPU VRAM temp limit: %d\n", mem_temp_limit.limit);

            // Get GFX temperature limit
            amdsmi_temperature_limit_t gfx_temp_limit = {};
            ret = amdsmi_get_temperature_limit(
                device_handles[j], TEMPERATURE_TYPE_EDGE, &gfx_temp_limit);
            CHK_AMDSMI_RET(ret)
            printf("\tGPU GFX temp limit: %d\n\n", gfx_temp_limit.limit);

            // Get temperature measurements
            // amdsmi_temperature_t edge_temp, junction_temp, vram_temp,
            // plx_temp;
            amdsmi_temperature_t temp_measurements[4];
            amdsmi_temperature_type_t temp_types[4] = {
                TEMPERATURE_TYPE_EDGE, TEMPERATURE_TYPE_JUNCTION,
                TEMPERATURE_TYPE_VRAM, TEMPERATURE_TYPE_PLX};
            for (const auto &temp_type : temp_types) {
                ret = amdsmi_get_temperature_measure(
                    device_handles[j], temp_type,
                    &temp_measurements[(int)(temp_type)]);
                CHK_AMDSMI_RET(ret)
            }
            printf("    Output of amdsmi_get_temperature_measure:\n");
            printf("\tGPU Edge temp measurement: %d\n",
                   temp_measurements[TEMPERATURE_TYPE_EDGE].cur_temp);
            printf("\tGPU Junction temp measurement: %d\n",
                   temp_measurements[TEMPERATURE_TYPE_JUNCTION].cur_temp);
            printf("\tGPU VRAM temp measurement: %d\n",
                   temp_measurements[TEMPERATURE_TYPE_VRAM].cur_temp);
            printf("\tGPU PLX temp measurement: %d\n\n",
                   temp_measurements[TEMPERATURE_TYPE_PLX].cur_temp);

            // Get RAS features enabled
            char block_names[14][10] = {"UMC",   "SDMA",     "GFX", "MMHUB",
                                        "ATHUB", "PCIE_BIF", "HDP", "XGMI_WAFL",
                                        "DF",    "SMN",      "SEM", "MP0",
                                        "MP1",   "FUSE"};
            char status_names[7][10] = {"NONE",   "DISABLED", "PARITY",
                                        "SING_C", "MULT_UC",  "POISON",
                                        "ENABLED"};
            amdsmi_ras_err_state_t state = {};
            int index = 0;
            printf("    Output of amdsmi_get_ras_block_features_enabled:\n");
            for (auto block = AMDSMI_GPU_BLOCK_FIRST;
                 block <= AMDSMI_GPU_BLOCK_LAST;
                 block = (amdsmi_gpu_block_t)(block * 2)) {
                ret = amdsmi_get_ras_block_features_enabled(device_handles[j], block,
                                                      &state);
                CHK_AMDSMI_RET(ret)
                printf("\tBlock: %s\n", block_names[index]);
                printf("\tStatus: %s\n", status_names[state]);
                index++;
            }
            printf("\n");

            // Get bad pages
            char bad_page_status_names[3][15] = {"RESERVED", "PENDING",
                                                 "UNRESERVABLE"};
            uint32_t num_pages = 0;
            ret = amdsmi_get_bad_page_info(device_handles[j], &num_pages,
                                           nullptr);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_bad_page_info:\n");
            if (!num_pages) {
                printf("\tNo bad pages found.\n");
            } else {
                amdsmi_retired_page_record_t bad_page_info[num_pages] = {};
                ret = amdsmi_get_bad_page_info(device_handles[j], &num_pages,
                                               bad_page_info);
                CHK_AMDSMI_RET(ret)
                for (uint32_t page_it = 0; page_it < num_pages; page_it += 1) {
                    printf("      Page[%d]\n", page_it);
                    printf("\tAddress: %lu\n",
                           bad_page_info[page_it].page_address);
                    printf("\tSize: %lu\n", bad_page_info[page_it].page_size);
                    printf(
                        "\tStatus: %s\n",
                        bad_page_status_names[bad_page_info[page_it].status]);
                }
            }
            printf("\n");

            // Get ECC error counts
            amdsmi_error_count_t err_cnt_info = {};
            ret = amdsmi_get_ecc_error_count(device_handles[j], &err_cnt_info);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_ecc_error_count:\n");
            printf("\tCorrectable errors: %lu\n", err_cnt_info.correctable_count);
            printf("\tUncorrectable errors: %lu\n\n",
                   err_cnt_info.uncorrectable_count);
            // Get process list
            auto compare = [](const void *a, const void *b) -> int {
                return (*(amdsmi_proc_info_t *)a).pid >
                               (*(amdsmi_proc_info_t *)b).pid
                           ? 1
                           : -1;
            };

            auto sum_item = [](uint16_t *a) -> float {
                float b = 0;
                for (int iterator = 0; iterator < AMDSMI_MAX_MM_IP_COUNT;
                     iterator += 1) {
                    b += (float)a[iterator] / 100.0;
                }
                return b;
            };

            // Get frequency ranges
            amdsmi_frequency_range_t freq_ranges = {};
            ret = amdsmi_get_target_frequency_range(
                device_handles[j], CLK_TYPE_GFX, &freq_ranges);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_target_frequency_range:\n");
            printf("\tSupported min freq: %lu\n",
                   freq_ranges.supported_freq_range.lower_bound);
            printf("\tSupported max freq: %lu\n",
                   freq_ranges.supported_freq_range.upper_bound);
            printf("\tCurrent min freq: %lu\n",
                   freq_ranges.current_freq_range.lower_bound);
            printf("\tCurrent max freq: %lu\n\n",
                   freq_ranges.current_freq_range.upper_bound);

            uint32_t num_process = 0;
            ret = amdsmi_get_process_list(device_handles[j], nullptr,
                                          &num_process);
            CHK_AMDSMI_RET(ret)
            if (!num_process) {
                printf("No processes found.\n");
            } else {
                amdsmi_process_handle process_list[num_process];
                amdsmi_proc_info_t info_list[num_process];
                amdsmi_proc_info_t process = {};
                uint64_t mem = 0, gtt_mem = 0, cpu_mem = 0, vram_mem = 0;
                float gfx = 0, comp = 0, dma = 0, enc = 0, dec = 0;
                char bdf_str[20];
                sprintf(bdf_str, "%04x:%02x:%02x.%d", bdf.domain_number,
                        bdf.bus_number, bdf.device_number, bdf.function_number);
                int num = 0;
                ret = amdsmi_get_process_list(device_handles[j], process_list,
                                              &num_process);
                CHK_AMDSMI_RET(ret)
                for (uint32_t it = 0; it < num_process; it += 1) {
                    if (getpid() == process_list[it]) {
                        continue;
                    }
                    ret = amdsmi_get_process_info(device_handles[j],
                                                  process_list[it], &process);
                    if (ret != AMDSMI_STATUS_SUCCESS) {
                        printf("amdsmi_get_process_info() failed for "
                               "process_list[%d], returned %d\n",
                               it, ret);
                        continue;
                    }
                    info_list[num++] = process;
                }
                qsort(info_list, num, sizeof(info_list[0]), compare);
                printf("+=======+==================+============+=============="
                       "+=============+=============+=============+============"
                       "==+=========================================+\n");
                printf(
                    "| pid   | name             | user       | gpu bdf      | "
                    "fb usage    | gtt memory  | cpu memory  | vram memory  | "
                    "ring usage (%%)                          |\n");
                printf("|       |                  |            |              "
                       "|             |             |             |            "
                       "  | gfx     comp    dma     enc     dec     |\n");
                printf("+=======+==================+============+=============="
                       "+=============+=============+=============+============"
                       "==+=========================================+\n");
                for (int it = 0; it < num; it++) {
                    char command[30];
                    struct passwd *pwd = NULL;
                    struct stat st;

                    sprintf(command, "/proc/%d", info_list[it].pid);
                    if (stat(command, &st))
                        continue;
                    pwd = getpwuid(st.st_uid);
                    if (!pwd)
                        printf("| %5d | %16s | %10d | %s | %7ld KiB | %7ld KiB "
                               "| %7ld KiB | %7ld KiB  | %6.2f  %6.2f  %6.2f  "
                               "%6.2f  %6.2f  |\n",
                               info_list[it].pid, info_list[it].name, st.st_uid,
                               bdf_str, info_list[it].mem / 1024,
                               info_list[it].memory_usage.gtt_mem / 1024,
                               info_list[it].memory_usage.cpu_mem / 1024,
                               info_list[it].memory_usage.vram_mem / 1024,
                               sum_item(info_list[it].engine_usage.gfx),
                               sum_item(info_list[it].engine_usage.compute),
                               sum_item(info_list[it].engine_usage.sdma),
                               sum_item(info_list[it].engine_usage.enc),
                               sum_item(info_list[it].engine_usage.dec));
                    else
                        printf("| %5d | %16s | %10s | %s | %7ld KiB | %7ld KiB "
                               "| %7ld KiB | %7ld KiB  | %6.2f  %6.2f  %6.2f  "
                               "%6.2f  %6.2f  |\n",
                               info_list[it].pid, info_list[it].name,
                               pwd->pw_name, bdf_str, info_list[it].mem / 1024,
                               info_list[it].memory_usage.gtt_mem / 1024,
                               info_list[it].memory_usage.cpu_mem / 1024,
                               info_list[it].memory_usage.vram_mem / 1024,
                               sum_item(info_list[it].engine_usage.gfx),
                               sum_item(info_list[it].engine_usage.compute),
                               sum_item(info_list[it].engine_usage.sdma),
                               sum_item(info_list[it].engine_usage.enc),
                               sum_item(info_list[it].engine_usage.dec));
                    mem += info_list[it].mem / 1024;
                    gtt_mem += info_list[it].memory_usage.gtt_mem / 1024;
                    cpu_mem += info_list[it].memory_usage.cpu_mem / 1024;
                    vram_mem += info_list[it].memory_usage.vram_mem / 1024;
                    gfx += sum_item(info_list[it].engine_usage.gfx);
                    comp += sum_item(info_list[it].engine_usage.compute);
                    dma += sum_item(info_list[it].engine_usage.sdma);
                    enc += sum_item(info_list[it].engine_usage.enc);
                    dec += sum_item(info_list[it].engine_usage.dec);
                    printf(
                        "+-------+------------------+------------+-------------"
                        "-+-------------+-------------+-------------+----------"
                        "----+-----------------------------------------+\n");
                }
                printf("|                                 TOTAL:| %s | %7ld "
                       "KiB | %7ld KiB | %7ld KiB | %7ld KiB | %6.2f  %6.2f  "
                       "%6.2f  %6.2f  %6.2f   |\n",
                       bdf_str, mem, gtt_mem, cpu_mem, vram_mem, gfx, comp, dma,
                       enc, dec);
                printf("+=======+==================+============+=============="
                       "+=============+=============+=============+============"
                       "=+==========================================+\n");
            }

            // Get device name
            amdsmi_board_info board_info = {};
            ret = amdsmi_get_board_info(device_handles[j], &board_info);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_board_info:\n");
            std::cout << "\tdevice [" << j
                      << "]\n\t\tProduct name: " << board_info.product_name
                      << "\n"
                      << "\t\tProduct number: " << board_info.product_serial
                      << "\n"
                      << "\t\tSerial number: " << board_info.serial_number
                      << "\n\n";

            // Get temperature
            int64_t val_i64 = 0;
            ret = amdsmi_dev_temp_metric_get(device_handles[j], 0,
                                             AMDSMI_TEMP_CURRENT, &val_i64);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_dev_temp_metric_get:\n");
            std::cout << "\t\tTemperature: " << val_i64 / 1000 << "C"
                      << "\n\n";

            // Get frame buffer
            amdsmi_vram_info_t vram_usage = {};
            ret = amdsmi_get_vram_usage(device_handles[j], &vram_usage);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_vram_usage:\n");
            std::cout << "\t\tFrame buffer usage (MB): " << vram_usage.vram_used
                      << "/" << vram_usage.vram_total << "\n\n";

            // Get Cap info
            amdsmi_gpu_caps_t caps_info = {};
            ret = amdsmi_get_caps_info(device_handles[j], &caps_info);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_caps_info:\n");
            std::cout << "\t\tGFX IP Major: " << caps_info.gfx.gfxip_major
                      << "\n"
                      << "\t\tGFX IP Minor: " << caps_info.gfx.gfxip_minor
                      << "\n"
                      << "\t\tCU IP Count: " << caps_info.gfx.gfxip_cu_count
                      << "\n"
                      << "\t\tDMA IP Count: " << caps_info.dma_ip_count << "\n"
                      << "\t\tGFX IP Count: " << caps_info.gfx_ip_count << "\n"
                      << "\t\tMM IP Count: " << int(caps_info.mm.mm_ip_count)
                      << "\n\n";

            amdsmi_power_cap_info cap_info = {};
            ret = amdsmi_get_power_cap_info(device_handles[j], 0, &cap_info);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_power_cap_info:\n");
            std::cout << "\t\t Power Cap: " << cap_info.power_cap
                      << "W\n";
            std::cout << "\t\t Dpm Cap: " << cap_info.dpm_cap
                      << "\n\n";
        }
    }

    // Clean up resources allocated at amdsmi_init. It will invalidate sockets
    // and devices pointers
    ret = amdsmi_shut_down();
    CHK_AMDSMI_RET(ret)

    return 0;
}

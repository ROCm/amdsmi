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

#include "amd_smi/amdsmi.h"
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
        ret = amdsmi_get_processor_handles(sockets[i], &device_count, nullptr);
        CHK_AMDSMI_RET(ret)

        // Allocate the memory for the device handlers on the socket
        std::vector<amdsmi_processor_handle> processor_handles(device_count);
        // Get all devices of the socket
        ret = amdsmi_get_processor_handles(sockets[i],
                                        &device_count, &processor_handles[0]);
        CHK_AMDSMI_RET(ret)

        // For each device of the socket, get name and temperature.
        for (uint32_t j = 0; j < device_count; j++) {
            // Get device type. Since the amdsmi is initialized with
            // AMD_SMI_INIT_AMD_GPUS, the processor_type must be AMD_GPU.
            processor_type_t processor_type = {};
            ret = amdsmi_get_processor_type(processor_handles[j], &processor_type);
            CHK_AMDSMI_RET(ret)
            if (processor_type != AMD_GPU) {
                std::cout << "Expect AMD_GPU device type!\n";
                return AMDSMI_STATUS_NOT_SUPPORTED;
            }

            amdsmi_bdf_t bdf = {};
            ret = amdsmi_get_gpu_device_bdf(processor_handles[j], &bdf);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_gpu_device_bdf:\n");
            printf("\tDevice[%d] BDF %04lx:%02x:%02x.%d\n\n", i,
                   bdf.domain_number, bdf.bus_number, bdf.device_number,
                   bdf.function_number);

            amdsmi_asic_info_t asic_info = {};
            ret = amdsmi_get_gpu_asic_info(processor_handles[j], &asic_info);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_gpu_asic_info:\n");
            printf("\tMarket Name: %s\n", asic_info.market_name);
            printf("\tFamilyID: 0x%x\n", asic_info.family);
            printf("\tDeviceID: 0x%lx\n", asic_info.device_id);
            printf("\tVendorID: 0x%x\n", asic_info.vendor_id);
            printf("\tRevisionID: 0x%x\n", asic_info.rev_id);
            printf("\tAsic serial: 0x%s\n\n", asic_info.asic_serial);

            // Get VBIOS info
            amdsmi_vbios_info_t vbios_info = {};
            ret = amdsmi_get_vbios_info(processor_handles[j], &vbios_info);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_vbios_info:\n");
            printf("\tVBios Name: %s\n", vbios_info.name);
            printf("\tBuild Date: %s\n", vbios_info.build_date);
            printf("\tPart Number: %s\n", vbios_info.part_number);
            printf("\tVBios Version: %d\n", vbios_info.vbios_version);
            printf("\tVBios Version String: %s\n\n",
                   vbios_info.vbios_version_string);

            // Get engine usage info
            amdsmi_engine_usage_t engine_usage = {};
            ret = amdsmi_get_gpu_activity(processor_handles[j], &engine_usage);
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
            ret = amdsmi_get_fw_info(processor_handles[j], &fw_information);
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

            // Get temperature measurements
            int64_t temp_measurements[4];
            amdsmi_temperature_type_t temp_types[4] = {
                TEMPERATURE_TYPE_EDGE, TEMPERATURE_TYPE_JUNCTION,
                TEMPERATURE_TYPE_VRAM, TEMPERATURE_TYPE_PLX};
            for (const auto &temp_type : temp_types) {
                ret = amdsmi_dev_get_temp_metric(
                    processor_handles[j], temp_type,
                    AMDSMI_TEMP_CURRENT,
                    &temp_measurements[(int)(temp_type)]);
                CHK_AMDSMI_RET(ret)
            }
            printf("    Output of amdsmi_dev_get_temp_metric:\n");
            printf("\tGPU Edge temp measurement: %ld\n",
                   temp_measurements[TEMPERATURE_TYPE_EDGE]);
            printf("\tGPU Junction temp measurement: %ld\n",
                   temp_measurements[TEMPERATURE_TYPE_JUNCTION]);
            printf("\tGPU VRAM temp measurement: %ld\n",
                   temp_measurements[TEMPERATURE_TYPE_VRAM]);
            printf("\tGPU PLX temp measurement: %ld\n\n",
                   temp_measurements[TEMPERATURE_TYPE_PLX]);

            // Get bad pages
            char bad_page_status_names[3][15] = {"RESERVED", "PENDING",
                                                 "UNRESERVABLE"};
            uint32_t num_pages = 0;
            ret = amdsmi_get_bad_page_info(processor_handles[j], &num_pages,
                                           nullptr);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_bad_page_info:\n");
            if (!num_pages) {
                printf("\tNo bad pages found.\n");
            } else {
                std::vector<amdsmi_retired_page_record_t> bad_page_info(num_pages);
                ret = amdsmi_get_bad_page_info(processor_handles[j], &num_pages,
                                               bad_page_info.data());
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
            ret = amdsmi_get_ecc_error_count(processor_handles[j], &err_cnt_info);
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

            // Get device name
            amdsmi_board_info_t board_info = {};
            ret = amdsmi_get_board_info(processor_handles[j], &board_info);
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
            ret =  amdsmi_dev_get_temp_metric(processor_handles[j], TEMPERATURE_TYPE_EDGE,
                                             AMDSMI_TEMP_CURRENT, &val_i64);
            CHK_AMDSMI_RET(ret)
            printf("    Output of  amdsmi_dev_get_temp_metric:\n");
            std::cout << "\t\tTemperature: " << val_i64 << "C"
                      << "\n\n";

            // Get frame buffer
            amdsmi_vram_info_t vram_usage = {};
            ret = amdsmi_get_vram_usage(processor_handles[j], &vram_usage);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_vram_usage:\n");
            std::cout << "\t\tFrame buffer usage (MB): " << vram_usage.vram_used
                      << "/" << vram_usage.vram_total << "\n\n";

            // Get Cap info
            amdsmi_gpu_caps_t caps_info = {};
            ret = amdsmi_get_caps_info(processor_handles[j], &caps_info);
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

            amdsmi_power_cap_info_t cap_info = {};
            ret = amdsmi_get_power_cap_info(processor_handles[j], 0, &cap_info);
            CHK_AMDSMI_RET(ret)
            printf("    Output of amdsmi_get_power_cap_info:\n");
            std::cout << "\t\t Power Cap: " << cap_info.power_cap / 1000000
                      << "W\n\n";
        }
    }

    // Clean up resources allocated at amdsmi_init. It will invalidate sockets
    // and devices pointers
    ret = amdsmi_shut_down();
    CHK_AMDSMI_RET(ret)

    return 0;
}

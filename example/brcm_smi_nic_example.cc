/*
 * BRCM SMI NIC Device Monitoring Example
 * 
 * This example demonstrates comprehensive NIC device monitoring including
 * device information, temperature monitoring, power metrics, and firmware details.
 */

#include <brcm_smi/brcmsmi.h>
#include <stdio.h>
#include <stdlib.h>

void monitor_nic_devices() {
    printf("BRCM SMI NIC Device Monitoring\n");
    printf("==============================\n\n");

    // Initialize
    if (brcmsmi_init(0) != BRCMSMI_STATUS_SUCCESS) {
        printf("Failed to initialize BRCM SMI\n");
        return;
    }

    // Get socket handles
    uint32_t socket_count = 0;
    brcmsmi_get_socket_handles(&socket_count, NULL);
    
    if (socket_count == 0) {
        printf("No sockets found\n");
        brcmsmi_shutdown();
        return;
    }

    brcmsmi_socket_handle *socket_handles = (brcmsmi_socket_handle*)malloc(sizeof(brcmsmi_socket_handle) * socket_count);
    if (!socket_handles) {
        printf("Memory allocation failed\n");
        brcmsmi_shutdown();
        return;
    }
    
    brcmsmi_get_socket_handles(&socket_count, socket_handles);
    printf("Found %u sockets\n\n", socket_count);

    // Iterate through sockets
    for (uint32_t i = 0; i < socket_count; i++) {
        uint32_t nic_count = 0;
        brcmsmi_processor_handle *nic_handles = NULL;
        
        // Get NIC processor handles
        brcmsmi_status_t status = brcmsmi_get_nic_processor_handles(socket_handles[i], 
                                                                   &nic_count, 
                                                                   &nic_handles);
        
        if (status == BRCMSMI_STATUS_SUCCESS && nic_count > 0) {
            printf("Socket %u has %u NIC devices:\n", i, nic_count);
            
            // Monitor each NIC
            for (uint32_t j = 0; j < nic_count; j++) {
                printf("\n--- NIC Device %u ---\n", j);
                
                // Get NIC information
                brcmsmi_nic_info_t nic_info;
                if (brcmsmi_get_nic_info(nic_handles[j], &nic_info) == BRCMSMI_STATUS_SUCCESS) {
                    printf("Device Name: %s\n", nic_info.nic_device_name);
                    printf("Part Number: %s\n", nic_info.nic_part_number);
                    printf("Firmware Version: %s\n", nic_info.nic_firmware_version);
                    printf("UUID: %s\n", nic_info.nic_uuid);
                    printf("BDF: %04lx:%02lx:%02lx.%lx\n", 
                           nic_info.nic_bdf.domain_number,
                           nic_info.nic_bdf.bus_number,
                           nic_info.nic_bdf.device_number,
                           nic_info.nic_bdf.function_number);
                } else {
                    printf("Failed to get NIC information\n");
                }

                // Get temperature information
                brcmsmi_nic_temperature_metric_t temp_info;
                if (brcmsmi_get_nic_temp_info(nic_handles[j], &temp_info) == BRCMSMI_STATUS_SUCCESS) {
                    printf("\nTemperature Metrics:\n");
                    printf("  Current: %u°C\n", temp_info.nic_temp_input);
                    printf("  Maximum: %u°C\n", temp_info.nic_temp_max);
                    printf("  Critical: %u°C\n", temp_info.nic_temp_crit);
                    printf("  Emergency: %u°C\n", temp_info.nic_temp_emergency);
                    printf("  Shutdown: %u°C\n", temp_info.nic_temp_shutdown);
                    
                    // Check alarm conditions
                    if (temp_info.nic_temp_crit_alarm) {
                        printf("  WARNING: Critical temperature alarm!\n");
                    }
                    if (temp_info.nic_temp_emergency_alarm) {
                        printf("  CRITICAL: Emergency temperature alarm!\n");
                    }
                } else {
                    printf("Temperature information not available\n");
                }

                // Get power information
                brcmsmi_nic_hwmon_power_t power_info;
                if (brcmsmi_get_nic_power_info(nic_handles[j], &power_info) == BRCMSMI_STATUS_SUCCESS) {
                    printf("\nPower Management:\n");
                    printf("  Runtime Status: %s\n", power_info.nic_power_runtime_status);
                    printf("  Runtime Usage: %u\n", power_info.nic_power_runtime_usage);
                    printf("  Runtime Active Time: %u ms\n", power_info.nic_power_runtime_active_time);
                    printf("  Runtime Suspended Time: %u ms\n", power_info.nic_power_runtime_suspended_time);
                    printf("  Runtime Active Kids: %u\n", power_info.nic_power_runtime_active_kids);
                    printf("  Runtime Enabled: %s\n", power_info.nic_power_runtime_enabled);
                    printf("  Power Control: %s\n", power_info.nic_power_control);
                } else {
                    printf("Power information not available\n");
                }

                // Get firmware information
                brcmsmi_nic_firmware_t fw_info;
                if (brcmsmi_get_nic_fw_info(nic_handles[j], &fw_info) == BRCMSMI_STATUS_SUCCESS) {
                    printf("\nFirmware Information:\n");
                    printf("  Package Version: %s\n", fw_info.nic_fw_pkg_version);
                    printf("  EFI Version: %s\n", fw_info.nic_fw_efi_version);
                    printf("  Firmware Version: %s\n", fw_info.nic_fw_version);
                    printf("  NCSI Version: %s\n", fw_info.nic_fw_ncsi_version);
                    printf("  RoCE Version: %s\n", fw_info.nic_fw_roce_version);
                } else {
                    printf("Firmware information not available\n");
                }

                // Get device hardware information
                brcmsmi_nic_hwmon_device_t device_info;
                if (brcmsmi_get_nic_device_info(nic_handles[j], &device_info) == BRCMSMI_STATUS_SUCCESS) {
                    printf("\nHardware Information:\n");
                    printf("  Device Class: %s\n", device_info.nic_device_class);
                    printf("  Vendor: %s\n", device_info.nic_device_vendor);
                    printf("  IRQ: %u\n", device_info.nic_device_irq);
                    printf("  NUMA Node: %u\n", device_info.nic_device_numa_node);
                    printf("  Current Link Speed: %s\n", device_info.nic_device_current_link_speed);
                    printf("  Max Link Speed: %s\n", device_info.nic_device_max_link_speed);
                    printf("  Current Link Width: %u\n", device_info.nic_device_current_link_width);
                    printf("  Max Link Width: %u\n", device_info.nic_device_max_link_width);
                    printf("  SR-IOV Total VFs: %u\n", device_info.nic_device_sriov_totalvfs);
                    printf("  SR-IOV Num VFs: %u\n", device_info.nic_device_sriov_numvfs);
                } else {
                    printf("Hardware information not available\n");
                }
            }
        } else {
            printf("Socket %u: No NIC devices found\n", i);
        }
    }

    free(socket_handles);
    brcmsmi_shutdown();
    printf("\nNIC monitoring completed\n");
}

int main() {
    monitor_nic_devices();
    return 0;
}

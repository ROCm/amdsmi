/*
 * BRCM SMI Switch Device Management Example
 * 
 * This example demonstrates comprehensive switch device management including
 * device information, link metrics, power management, and device metrics.
 */

#include <brcm_smi/brcmsmi.h>
#include <stdio.h>
#include <stdlib.h>

void manage_switch_devices() {
    printf("BRCM SMI Switch Device Management\n");
    printf("=================================\n\n");

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
        uint32_t switch_count = 0;
        brcmsmi_processor_handle *switch_handles = NULL;
        
        // Get switch processor handles
        brcmsmi_status_t status = brcmsmi_get_switch_processor_handles(socket_handles[i], 
                                                                      &switch_count, 
                                                                      &switch_handles);
        
        if (status == BRCMSMI_STATUS_SUCCESS && switch_count > 0) {
            printf("Socket %u has %u Switch devices:\n", i, switch_count);
            
            // Monitor each switch
            for (uint32_t j = 0; j < switch_count; j++) {
                printf("\n--- Switch Device %u ---\n", j);
                
                // Get switch information
                brcmsmi_switch_info_t switch_info;
                if (brcmsmi_get_switch_info(switch_handles[j], &switch_info) == BRCMSMI_STATUS_SUCCESS) {
                    printf("Device Information:\n");
                    printf("  Device Name: %s\n", switch_info.switch_device_name);
                    printf("  Part Number: %s\n", switch_info.switch_part_number);
                    printf("  Firmware Version: %s\n", switch_info.switch_firmware_version);
                    printf("  UUID: %s\n", switch_info.switch_uuid);
                    printf("  Vendor ID: %s\n", switch_info.switch_vendor_id);
                    printf("  Device ID: %s\n", switch_info.switch_device_id);
                    printf("  Subsystem Vendor: %s\n", switch_info.switch_subsystem_vendor);
                    printf("  Subsystem Device: %s\n", switch_info.switch_subsystem_device);
                    printf("  Device Class: %s\n", switch_info.switch_class);
                    printf("  Revision: %s\n", switch_info.switch_revision);
                    printf("  IRQ: %s\n", switch_info.switch_irq);
                    printf("  NUMA Node: %s\n", switch_info.switch_numa_node);
                    
                    printf("\nBDF Information:\n");
                    printf("  BDF: %04lx:%02lx:%02lx.%lx\n", 
                           switch_info.switch_bdf.domain_number,
                           switch_info.switch_bdf.bus_number,
                           switch_info.switch_bdf.device_number,
                           switch_info.switch_bdf.function_number);
                } else {
                    printf("Failed to get switch information\n");
                }

                // Get link information
                brcmsmi_switch_link_metric_t link_info;
                if (brcmsmi_get_switch_link_info(switch_handles[j], &link_info) == BRCMSMI_STATUS_SUCCESS) {
                    printf("\nLink Metrics:\n");
                    printf("  Current Link Speed: %s\n", link_info.current_link_speed);
                    printf("  Max Link Speed: %s\n", link_info.max_link_speed);
                    printf("  Current Link Width: %s\n", link_info.current_link_width);
                    printf("  Max Link Width: %s\n", link_info.max_link_width);
                } else {
                    printf("Link information not available\n");
                }

                // Get power information
                brcmsmi_switch_power_metric_t power_info;
                if (brcmsmi_get_switch_power_info(switch_handles[j], &power_info) == BRCMSMI_STATUS_SUCCESS) {
                    printf("\nPower Management:\n");
                    printf("  Power Control: %s\n", power_info.brcm_power_control);
                    printf("  Runtime Status: %s\n", power_info.brcm_power_runtime_status);
                    printf("  Runtime Enabled: %s\n", power_info.brcm_power_runtime_enabled);
                    printf("  Runtime Active Time: %s ms\n", power_info.brcm_power_runtime_active_time);
                    printf("  Runtime Suspended Time: %s ms\n", power_info.brcm_power_runtime_suspended_time);
                    printf("  Runtime Usage: %s\n", power_info.brcm_power_runtime_usage);
                    printf("  Runtime Active Kids: %s\n", power_info.brcm_power_runtime_active_kids);
                    printf("  Power Async: %s\n", power_info.brcm_power_async);
                    
                    printf("\nWakeup Information:\n");
                    printf("  Wakeup: %s\n", power_info.brcm_power_wakeup);
                    printf("  Wakeup Active: %s\n", power_info.brcm_power_wakeup_active);
                    printf("  Wakeup Count: %s\n", power_info.brcm_power_wakeup_count);
                    printf("  Wakeup Active Count: %s\n", power_info.brcm_power_wakeup_active_count);
                    printf("  Wakeup Abort Count: %s\n", power_info.brcm_power_wakeup_abort_count);
                    printf("  Wakeup Expire Count: %s\n", power_info.brcm_power_wakeup_expire_count);
                    printf("  Wakeup Last Time: %s ms\n", power_info.brcm_power_wakeup_last_time_ms);
                    printf("  Wakeup Max Time: %s ms\n", power_info.brcm_power_wakeup_max_time_ms);
                    printf("  Wakeup Total Time: %s ms\n", power_info.brcm_power_wakeup_total_time_ms);
                } else {
                    printf("Power information not available\n");
                }

                // Get device metrics
                brcmsmi_switch_device_metric_t device_info;
                if (brcmsmi_get_switch_device_info(switch_handles[j], &device_info) == BRCMSMI_STATUS_SUCCESS) {
                    printf("\nDevice Metrics:\n");
                    printf("  Device Class: %s\n", device_info.brcm_device_class);
                    printf("  Vendor: %s\n", device_info.brcm_device_vendor);
                    printf("  IRQ: %s\n", device_info.brcm_device_irq);
                    printf("  NUMA Node: %s\n", device_info.brcm_device_numa_node);
                    printf("  Current Link Speed: %s\n", device_info.brcm_device_current_link_speed);
                    printf("  Max Link Speed: %s\n", device_info.brcm_device_max_link_speed);
                    printf("  Current Link Width: %s\n", device_info.brcm_device_current_link_width);
                    printf("  Max Link Width: %s\n", device_info.brcm_device_max_link_width);
                    printf("  Power State: %s\n", device_info.brcm_device_power_state);
                    printf("  Reset Method: %s\n", device_info.brcm_device_reset_method);
                    printf("  Revision: %s\n", device_info.brcm_device_revision);
                    printf("  Subsystem Device: %s\n", device_info.brcm_device_subsystem_device);
                    printf("  Subsystem Vendor: %s\n", device_info.brcm_device_subsystem_vendor);
                    
                    printf("\nAdvanced Device Information:\n");
                    printf("  AER Correctable: %s\n", device_info.brcm_device_aer_dev_correctable);
                    printf("  AER Fatal: %s\n", device_info.brcm_device_aer_dev_fatal);
                    printf("  AER Non-Fatal: %s\n", device_info.brcm_device_aer_dev_nonfatal);
                    printf("  ARI Enabled: %s\n", device_info.brcm_device_ari_enabled);
                    printf("  Broken Parity Status: %s\n", device_info.brcm_device_broken_parity_status);
                    printf("  DMA Mask Bits: %s\n", device_info.brcm_device_dma_mask_bits);
                    printf("  Consistent DMA Mask Bits: %s\n", device_info.brcm_device_consistent_dma_mask_bits);
                    printf("  D3Cold Allowed: %s\n", device_info.brcm_device_d3cold_allowed);
                    printf("  Enable: %s\n", device_info.brcm_device_enable);
                    printf("  MSI Bus: %s\n", device_info.brcm_device_msi_bus);
                    printf("  Modalias: %s\n", device_info.brcm_device_modalias);
                } else {
                    printf("Device metrics not available\n");
                }
            }
        } else {
            printf("Socket %u: No Switch devices found\n", i);
        }
    }

    free(socket_handles);
    brcmsmi_shutdown();
    printf("\nSwitch management completed\n");
}

int main() {
    manage_switch_devices();
    return 0;
}

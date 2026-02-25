/*
 * BRCM SMI Basic Device Discovery Example
 * 
 * This example demonstrates basic BRCM SMI initialization, device discovery,
 * and socket enumeration.
 */

#include <brcm_smi/brcmsmi.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
    printf("BRCM SMI Basic Device Discovery Example\n");
    printf("======================================\n\n");

    // Initialize BRCM SMI
    brcmsmi_status_t status = brcmsmi_init(0);
    if (status != BRCMSMI_STATUS_SUCCESS) {
        printf("Failed to initialize BRCM SMI: %d\n", status);
        return -1;
    }
    printf("BRCM SMI initialized successfully\n");

    // Discover devices
    brcmsmi_discovery_result_t discovery_result;
    status = brcmsmi_discover_devices(&discovery_result);
    if (status == BRCMSMI_STATUS_SUCCESS) {
        printf("Device Discovery Results:\n");
        printf("  NIC devices found: %u\n", discovery_result.nic_count);
        printf("  Switch devices found: %u\n", discovery_result.switch_count);
        printf("  Total devices: %u\n", discovery_result.total_count);
    } else {
        printf("Device discovery failed: %d\n", status);
    }

    // Get socket handles
    uint32_t socket_count = 0;
    brcmsmi_get_socket_handles(&socket_count, NULL);
    
    if (socket_count > 0) {
        printf("\nSocket Information:\n");
        brcmsmi_socket_handle *socket_handles = (brcmsmi_socket_handle*)malloc(sizeof(brcmsmi_socket_handle) * socket_count);
        if (socket_handles) {
            brcmsmi_get_socket_handles(&socket_count, socket_handles);
            printf("  Found %u sockets\n", socket_count);
            
            // Display socket information
            for (uint32_t i = 0; i < socket_count; i++) {
                printf("  Socket %u: Handle = %p\n", i, socket_handles[i]);
            }
            
            free(socket_handles);
        }
    } else {
        printf("\nNo sockets found in the system\n");
    }

    // Cleanup
    brcmsmi_shutdown();
    printf("\nBRCM SMI shutdown completed\n");
    return 0;
}

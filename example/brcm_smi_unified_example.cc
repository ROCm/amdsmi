/*
 * BRCM SMI Unified AMD SMI Integration Example
 * 
 * This example demonstrates how to use BRCM SMI functionality through
 * the AMD SMI interface when ENABLE_BRCM_SMI is enabled.
 */

#include <amd_smi/amdsmi.h>
#include <stdio.h>
#include <stdlib.h>

int main() {
    printf("BRCM SMI Unified AMD SMI Integration Example\n");
    printf("============================================\n\n");

    // Initialize AMD SMI
    amdsmi_status_t status = amdsmi_init();
    if (status != AMDSMI_STATUS_SUCCESS) {
        printf("Failed to initialize AMD SMI: %d\n", status);
        return -1;
    }
    printf("AMD SMI initialized successfully\n");

#ifdef ENABLE_BRCM_SMI
    printf("BRCM SMI support is enabled\n");
    
    // Initialize BRCM SMI through AMD SMI
    status = amdsmi_brcm_init(0);
    if (status == AMDSMI_STATUS_SUCCESS) {
        printf("BRCM SMI initialized through AMD SMI interface\n");
        
        // Use BRCM SMI functionality through AMD SMI interface
        amdsmi_brcm_discovery_result_t brcm_result;
        status = amdsmi_brcm_discover_devices(&brcm_result);
        
        if (status == AMDSMI_STATUS_SUCCESS) {
            printf("\nBRCM Device Discovery Results:\n");
            printf("  NIC devices found: %u\n", brcm_result.nic_count);
            printf("  Switch devices found: %u\n", brcm_result.switch_count);
            printf("  Total BRCM devices: %u\n", brcm_result.total_count);
        } else {
            printf("BRCM device discovery failed: %d\n", status);
        }
        
        // Get BRCM socket handles through AMD SMI
        uint32_t brcm_socket_count = 0;
        status = amdsmi_get_brcm_socket_handles(&brcm_socket_count, NULL);
        
        if (status == AMDSMI_STATUS_SUCCESS && brcm_socket_count > 0) {
            printf("\nBRCM Socket Information:\n");
            printf("  Found %u BRCM sockets\n", brcm_socket_count);
            
            amdsmi_brcm_socket_handle *brcm_socket_handles = 
                (amdsmi_brcm_socket_handle*)malloc(sizeof(amdsmi_brcm_socket_handle) * brcm_socket_count);
            
            if (brcm_socket_handles) {
                status = amdsmi_get_brcm_socket_handles(&brcm_socket_count, brcm_socket_handles);
                
                if (status == AMDSMI_STATUS_SUCCESS) {
                    for (uint32_t i = 0; i < brcm_socket_count; i++) {
                        printf("  BRCM Socket %u: Handle = %p\n", i, brcm_socket_handles[i]);
                        
                        // Get processor handles for this socket
                        uint32_t nic_processor_count = 0;
                        uint32_t switch_processor_count = 0;
                        
                        // Get NIC processor count
                        amdsmi_brcm_processor_handle *nic_processors = NULL;
                        status = amdsmi_get_brcm_processor_handles(brcm_socket_handles[i], 
                                                                  AMDSMI_BRCM_PROCESSOR_TYPE_NIC,
                                                                  &nic_processor_count, 
                                                                  nic_processors);
                        
                        if (status == AMDSMI_STATUS_SUCCESS) {
                            printf("    NIC processors: %u\n", nic_processor_count);
                        }
                        
                        // Get Switch processor count
                        amdsmi_brcm_processor_handle *switch_processors = NULL;
                        status = amdsmi_get_brcm_processor_handles(brcm_socket_handles[i], 
                                                                  AMDSMI_BRCM_PROCESSOR_TYPE_SWITCH,
                                                                  &switch_processor_count, 
                                                                  switch_processors);
                        
                        if (status == AMDSMI_STATUS_SUCCESS) {
                            printf("    Switch processors: %u\n", switch_processor_count);
                        }
                    }
                }
                
                free(brcm_socket_handles);
            }
        } else {
            printf("No BRCM sockets found or failed to get socket handles\n");
        }
        
    } else {
        printf("Failed to initialize BRCM SMI through AMD SMI: %d\n", status);
        printf("This may be normal if no BRCM devices are present\n");
    }
#else
    printf("BRCM SMI support is not enabled in this build\n");
    printf("To enable BRCM SMI support, build with -DENABLE_BRCM_SMI=ON\n");
#endif

    // Use regular AMD SMI functions for AMD hardware
    printf("\nAMD SMI Device Information:\n");
    
    // Get AMD GPU device count
    uint32_t num_devices = 0;
    status = amdsmi_get_device_count(&num_devices);
    if (status == AMDSMI_STATUS_SUCCESS) {
        printf("  AMD GPU devices found: %u\n", num_devices);
        
        if (num_devices > 0) {
            // Get device handles
            amdsmi_device_handle *device_handles = 
                (amdsmi_device_handle*)malloc(sizeof(amdsmi_device_handle) * num_devices);
            
            if (device_handles) {
                status = amdsmi_get_device_list(device_handles, &num_devices);
                
                if (status == AMDSMI_STATUS_SUCCESS) {
                    for (uint32_t i = 0; i < num_devices; i++) {
                        printf("  AMD GPU Device %u: Handle = %p\n", i, device_handles[i]);
                        
                        // Get device name
                        char device_name[256];
                        status = amdsmi_get_gpu_device_name(device_handles[i], device_name, sizeof(device_name));
                        if (status == AMDSMI_STATUS_SUCCESS) {
                            printf("    Device Name: %s\n", device_name);
                        }
                        
                        // Get device UUID
                        char device_uuid[256];
                        status = amdsmi_get_gpu_device_uuid(device_handles[i], device_uuid, sizeof(device_uuid));
                        if (status == AMDSMI_STATUS_SUCCESS) {
                            printf("    Device UUID: %s\n", device_uuid);
                        }
                    }
                }
                
                free(device_handles);
            }
        }
    } else {
        printf("  Failed to get AMD GPU device count: %d\n", status);
    }

    // Get CPU device count
    uint32_t num_cpus = 0;
    status = amdsmi_get_cpusocket_handles(&num_cpus, NULL);
    if (status == AMDSMI_STATUS_SUCCESS) {
        printf("  AMD CPU sockets found: %u\n", num_cpus);
    }

    printf("\nSystem Summary:\n");
#ifdef ENABLE_BRCM_SMI
    printf("  - BRCM SMI integration: Enabled\n");
    printf("  - BRCM devices: Available through AMD SMI interface\n");
#else
    printf("  - BRCM SMI integration: Disabled\n");
#endif
    printf("  - AMD GPU devices: Available through AMD SMI interface\n");
    printf("  - AMD CPU devices: Available through AMD SMI interface\n");

    // Cleanup
    amdsmi_shut_down();
    printf("\nUnified system monitoring completed\n");
    return 0;
}

/*
 * Copyright (c) Advanced Micro Devices, Inc. All rights reserved.
 *
 *  Developed by:
 *            Broadcom Inc
 *
 *            www.broadcom.com
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <stdint.h>
#include <stddef.h>
#include <gtest/gtest.h>

#include <iostream>
#include <string>
#include <limits>

#include "amd_smi/amdsmi.h"
#include "brcm_smi_read.h"

#ifdef ENABLE_BRCM_SMI

TestBrcmSmiRead::TestBrcmSmiRead() : TestBase() {
  set_title("AMDSMI BRCM SMI Read Test");
  set_description("This test verifies that BRCM SMI functionality including "
             "device discovery, NIC and Switch information retrieval, "
             "metrics collection, and error handling work properly.");
}

TestBrcmSmiRead::~TestBrcmSmiRead(void) {
}

void TestBrcmSmiRead::SetUp(void) {
  TestBase::SetUp();
  return;
}

void TestBrcmSmiRead::DisplayTestInfo(void) {
  TestBase::DisplayTestInfo();
}

void TestBrcmSmiRead::DisplayResults(void) const {
  TestBase::DisplayResults();
  return;
}

void TestBrcmSmiRead::Close() {
  // This will close handles opened within amdsmi utility calls and call
  // amdsmi_shut_down(), so it should be done after other cleanup
  TestBase::Close();
}

void TestBrcmSmiRead::Run(void) {
  TestBase::Run();
  if (setup_failed_) {
    std::cout << "** SetUp Failed for this test. Skipping.**" << std::endl;
    return;
  }

  std::cout << "\t**BRCM SMI Read Test**" << std::endl;
  
  // Test BRCM SMI initialization and shutdown
  TestBrcmSmiInit();
  
  // Test BRCM SMI device discovery
  TestBrcmSmiDiscovery();
  
  // Test NIC device information
  TestNicDeviceInfo();
  
  // Test Switch device information
  TestSwitchDeviceInfo();
  
  // Test NIC metrics
  TestNicMetrics();
  
  // Test Switch metrics
  TestSwitchMetrics();
  
  // Test error handling
  TestErrorHandling();
}

void TestBrcmSmiRead::TestBrcmSmiInit() {
  amdsmi_status_t ret;
  
  std::cout << "\t**Testing BRCM SMI Initialization**" << std::endl;
  
  // Test BRCM SMI initialization
  ret = amdsmi_brcm_init(0);
  if (ret == AMDSMI_STATUS_SUCCESS) {
    std::cout << "\t\tBRCM SMI initialization: PASSED" << std::endl;
    
    // Test BRCM SMI shutdown
    ret = amdsmi_brcm_shutdown();
    if (ret == AMDSMI_STATUS_SUCCESS) {
      std::cout << "\t\tBRCM SMI shutdown: PASSED" << std::endl;
    } else {
      std::cout << "\t\tBRCM SMI shutdown: FAILED (Status: " << ret << ")" << std::endl;
    }
  } else if (ret == AMDSMI_STATUS_NOT_SUPPORTED) {
    std::cout << "\t\tBRCM SMI initialization: NOT SUPPORTED (Expected on systems without BRCM hardware)" << std::endl;
  } else {
    std::cout << "\t\tBRCM SMI initialization: FAILED (Status: " << ret << ")" << std::endl;
  }
}

void TestBrcmSmiRead::TestBrcmSmiDiscovery() {
  amdsmi_status_t ret;
  amdsmi_brcm_discovery_result_t discovery_result;
  
  std::cout << "\t**Testing BRCM SMI Device Discovery**" << std::endl;
  
  // Initialize BRCM SMI first
  ret = amdsmi_brcm_init(0);
  if (ret != AMDSMI_STATUS_SUCCESS) {
    std::cout << "\t\tSkipping discovery test - BRCM SMI init failed" << std::endl;
    return;
  }
  
  // Test device discovery
  ret = amdsmi_brcm_discover_devices(&discovery_result);
  if (ret == AMDSMI_STATUS_SUCCESS) {
    std::cout << "\t\tDevice discovery: PASSED" << std::endl;
    std::cout << "\t\t\tNIC devices found: " << discovery_result.nic_count << std::endl;
    std::cout << "\t\t\tSwitch devices found: " << discovery_result.switch_count << std::endl;
  } else if (ret == AMDSMI_STATUS_NOT_FOUND) {
    std::cout << "\t\tDevice discovery: NO DEVICES FOUND (Expected on systems without BRCM hardware)" << std::endl;
  } else {
    std::cout << "\t\tDevice discovery: FAILED (Status: " << ret << ")" << std::endl;
  }
  
  amdsmi_brcm_shutdown();
}

void TestBrcmSmiRead::TestNicDeviceInfo() {
  amdsmi_status_t ret;
  uint32_t socket_count = 0;
  amdsmi_brcm_socket_handle* socket_handles = nullptr;
  
  std::cout << "\t**Testing NIC Device Information**" << std::endl;
  
  // Initialize BRCM SMI
  ret = amdsmi_brcm_init(0);
  if (ret != AMDSMI_STATUS_SUCCESS) {
    std::cout << "\t\tSkipping NIC test - BRCM SMI init failed" << std::endl;
    return;
  }
  
  // Get socket handles first
  ret = amdsmi_get_brcm_socket_handles(&socket_count, nullptr);
  if (ret == AMDSMI_STATUS_SUCCESS && socket_count > 0) {
    socket_handles = new amdsmi_brcm_socket_handle[socket_count];
    ret = amdsmi_get_brcm_socket_handles(&socket_count, socket_handles);
    
    if (ret == AMDSMI_STATUS_SUCCESS) {
      std::cout << "\t\tSocket handles retrieved: " << socket_count << " sockets" << std::endl;
      
      // Test getting NIC processors for each socket
      for (uint32_t i = 0; i < socket_count; ++i) {
        uint32_t nic_count = 0;
        amdsmi_brcm_processor_handle* nic_handles = nullptr;
        
        ret = amdsmi_get_brcm_nic_processor_handles(socket_handles[i], &nic_count, nullptr);
        if (ret == AMDSMI_STATUS_SUCCESS && nic_count > 0) {
          nic_handles = new amdsmi_brcm_processor_handle[nic_count];
          ret = amdsmi_get_brcm_nic_processor_handles(socket_handles[i], &nic_count, &nic_handles);
          
          if (ret == AMDSMI_STATUS_SUCCESS) {
            std::cout << "\t\t\tSocket " << i << " NIC processors: " << nic_count << " devices" << std::endl;
            
            // Test getting NIC info for each device
            for (uint32_t j = 0; j < nic_count; ++j) {
              char info_buffer[1024];
              ret = amdsmi_brcm_getString(nic_handles[j], "get_nic_info", sizeof(info_buffer), info_buffer);
              if (ret == AMDSMI_STATUS_SUCCESS) {
                std::cout << "\t\t\t\tNIC " << j << " info: PASSED" << std::endl;
              } else {
                std::cout << "\t\t\t\tNIC " << j << " info: FAILED (Status: " << ret << ")" << std::endl;
              }
            }
          }
          delete[] nic_handles;
        } else {
          std::cout << "\t\t\tSocket " << i << " NICs: NOT FOUND" << std::endl;
        }
      }
    }
    delete[] socket_handles;
  } else if (ret == AMDSMI_STATUS_NOT_FOUND || socket_count == 0) {
    std::cout << "\t\tBRCM sockets: NOT FOUND (Expected on systems without BRCM hardware)" << std::endl;
  } else {
    std::cout << "\t\tSocket handles: FAILED (Status: " << ret << ")" << std::endl;
  }
  
  amdsmi_brcm_shutdown();
}

void TestBrcmSmiRead::TestSwitchDeviceInfo() {
  amdsmi_status_t ret;
  uint32_t socket_count = 0;
  amdsmi_brcm_socket_handle* socket_handles = nullptr;
  
  std::cout << "\t**Testing Switch Device Information**" << std::endl;
  
  // Initialize BRCM SMI
  ret = amdsmi_brcm_init(0);
  if (ret != AMDSMI_STATUS_SUCCESS) {
    std::cout << "\t\tSkipping Switch test - BRCM SMI init failed" << std::endl;
    return;
  }
  
  // Get socket handles first
  ret = amdsmi_get_brcm_socket_handles(&socket_count, nullptr);
  if (ret == AMDSMI_STATUS_SUCCESS && socket_count > 0) {
    socket_handles = new amdsmi_brcm_socket_handle[socket_count];
    ret = amdsmi_get_brcm_socket_handles(&socket_count, socket_handles);
    
    if (ret == AMDSMI_STATUS_SUCCESS) {
      std::cout << "\t\tSocket handles retrieved: " << socket_count << " sockets" << std::endl;
      
      // Test getting Switch processors for each socket
      for (uint32_t i = 0; i < socket_count; ++i) {
        uint32_t switch_count = 0;
        amdsmi_brcm_processor_handle* switch_handles = nullptr;
        
        ret = amdsmi_get_brcm_switch_processor_handles(socket_handles[i], &switch_count, nullptr);
        if (ret == AMDSMI_STATUS_SUCCESS && switch_count > 0) {
          switch_handles = new amdsmi_brcm_processor_handle[switch_count];
          ret = amdsmi_get_brcm_switch_processor_handles(socket_handles[i], &switch_count, &switch_handles);
          
          if (ret == AMDSMI_STATUS_SUCCESS) {
            std::cout << "\t\t\tSocket " << i << " Switch processors: " << switch_count << " devices" << std::endl;
            
            // Test getting Switch info for each device
            for (uint32_t j = 0; j < switch_count; ++j) {
              char info_buffer[1024];
              ret = amdsmi_brcm_getString(switch_handles[j], "get_switch_info", sizeof(info_buffer), info_buffer);
              if (ret == AMDSMI_STATUS_SUCCESS) {
                std::cout << "\t\t\t\tSwitch " << j << " info: PASSED" << std::endl;
              } else {
                std::cout << "\t\t\t\tSwitch " << j << " info: FAILED (Status: " << ret << ")" << std::endl;
              }
            }
          }
          delete[] switch_handles;
        } else {
          std::cout << "\t\t\tSocket " << i << " Switches: NOT FOUND" << std::endl;
        }
      }
    }
    delete[] socket_handles;
  } else if (ret == AMDSMI_STATUS_NOT_FOUND || socket_count == 0) {
    std::cout << "\t\tBRCM sockets: NOT FOUND (Expected on systems without BRCM hardware)" << std::endl;
  } else {
    std::cout << "\t\tSocket handles: FAILED (Status: " << ret << ")" << std::endl;
  }
  
  amdsmi_brcm_shutdown();
}

void TestBrcmSmiRead::TestNicMetrics() {
  amdsmi_status_t ret;
  uint32_t socket_count = 0;
  amdsmi_brcm_socket_handle* socket_handles = nullptr;
  
  std::cout << "\t**Testing NIC Metrics**" << std::endl;
  
  // Initialize BRCM SMI
  ret = amdsmi_brcm_init(0);
  if (ret != AMDSMI_STATUS_SUCCESS) {
    std::cout << "\t\tSkipping NIC metrics test - BRCM SMI init failed" << std::endl;
    return;
  }
  
  // Get socket handles first
  ret = amdsmi_get_brcm_socket_handles(&socket_count, nullptr);
  if (ret == AMDSMI_STATUS_SUCCESS && socket_count > 0) {
    socket_handles = new amdsmi_brcm_socket_handle[socket_count];
    ret = amdsmi_get_brcm_socket_handles(&socket_count, socket_handles);
    
    if (ret == AMDSMI_STATUS_SUCCESS) {
      // Test getting NIC metrics for each socket
      for (uint32_t i = 0; i < socket_count; ++i) {
        uint32_t nic_count = 0;
        amdsmi_brcm_processor_handle* nic_handles = nullptr;
        
        ret = amdsmi_get_brcm_nic_processor_handles(socket_handles[i], &nic_count, nullptr);
        if (ret == AMDSMI_STATUS_SUCCESS && nic_count > 0) {
          nic_handles = new amdsmi_brcm_processor_handle[nic_count];
          ret = amdsmi_get_brcm_nic_processor_handles(socket_handles[i], &nic_count, &nic_handles);
          
          if (ret == AMDSMI_STATUS_SUCCESS) {
            // Test getting NIC metrics for each device
            for (uint32_t j = 0; j < nic_count; ++j) {
              char metrics_buffer[1024];
              ret = amdsmi_brcm_getString(nic_handles[j], "get_nic_metrics", sizeof(metrics_buffer), metrics_buffer);
              if (ret == AMDSMI_STATUS_SUCCESS) {
                std::cout << "\t\t\tSocket " << i << " NIC " << j << " metrics: PASSED" << std::endl;
              } else if (ret == AMDSMI_STATUS_NOT_SUPPORTED) {
                std::cout << "\t\t\tSocket " << i << " NIC " << j << " metrics: NOT SUPPORTED" << std::endl;
              } else {
                std::cout << "\t\t\tSocket " << i << " NIC " << j << " metrics: FAILED (Status: " << ret << ")" << std::endl;
              }
            }
          }
          delete[] nic_handles;
        }
      }
    }
    delete[] socket_handles;
  } else {
    std::cout << "\t\tNIC metrics: SKIPPED (No BRCM sockets available)" << std::endl;
  }
  
  amdsmi_brcm_shutdown();
}

void TestBrcmSmiRead::TestSwitchMetrics() {
  amdsmi_status_t ret;
  uint32_t socket_count = 0;
  amdsmi_brcm_socket_handle* socket_handles = nullptr;
  
  std::cout << "\t**Testing Switch Metrics**" << std::endl;
  
  // Initialize BRCM SMI
  ret = amdsmi_brcm_init(0);
  if (ret != AMDSMI_STATUS_SUCCESS) {
    std::cout << "\t\tSkipping Switch metrics test - BRCM SMI init failed" << std::endl;
    return;
  }
  
  // Get socket handles first
  ret = amdsmi_get_brcm_socket_handles(&socket_count, nullptr);
  if (ret == AMDSMI_STATUS_SUCCESS && socket_count > 0) {
    socket_handles = new amdsmi_brcm_socket_handle[socket_count];
    ret = amdsmi_get_brcm_socket_handles(&socket_count, socket_handles);
    
    if (ret == AMDSMI_STATUS_SUCCESS) {
      // Test getting Switch metrics for each socket
      for (uint32_t i = 0; i < socket_count; ++i) {
        uint32_t switch_count = 0;
        amdsmi_brcm_processor_handle* switch_handles = nullptr;
        
        ret = amdsmi_get_brcm_switch_processor_handles(socket_handles[i], &switch_count, nullptr);
        if (ret == AMDSMI_STATUS_SUCCESS && switch_count > 0) {
          switch_handles = new amdsmi_brcm_processor_handle[switch_count];
          ret = amdsmi_get_brcm_switch_processor_handles(socket_handles[i], &switch_count, &switch_handles);
          
          if (ret == AMDSMI_STATUS_SUCCESS) {
            // Test getting Switch metrics for each device
            for (uint32_t j = 0; j < switch_count; ++j) {
              char metrics_buffer[1024];
              ret = amdsmi_brcm_getString(switch_handles[j], "get_switch_metrics", sizeof(metrics_buffer), metrics_buffer);
              if (ret == AMDSMI_STATUS_SUCCESS) {
                std::cout << "\t\t\tSocket " << i << " Switch " << j << " metrics: PASSED" << std::endl;
              } else if (ret == AMDSMI_STATUS_NOT_SUPPORTED) {
                std::cout << "\t\t\tSocket " << i << " Switch " << j << " metrics: NOT SUPPORTED" << std::endl;
              } else {
                std::cout << "\t\t\tSocket " << i << " Switch " << j << " metrics: FAILED (Status: " << ret << ")" << std::endl;
              }
            }
          }
          delete[] switch_handles;
        }
      }
    }
    delete[] socket_handles;
  } else {
    std::cout << "\t\tSwitch metrics: SKIPPED (No BRCM sockets available)" << std::endl;
  }
  
  amdsmi_brcm_shutdown();
}

void TestBrcmSmiRead::TestErrorHandling() {
  amdsmi_status_t ret;
  
  std::cout << "\t**Testing Error Handling**" << std::endl;
  
  // Test calling functions without initialization
  uint32_t count = 0;
  ret = amdsmi_get_brcm_socket_handles(&count, nullptr);
  if (ret != AMDSMI_STATUS_SUCCESS) {
    std::cout << "\t\tError handling (uninitialized): PASSED (Status: " << ret << ")" << std::endl;
  } else {
    std::cout << "\t\tError handling (uninitialized): UNEXPECTED SUCCESS" << std::endl;
  }
  
  // Initialize for further tests
  ret = amdsmi_brcm_init(0);
  if (ret == AMDSMI_STATUS_SUCCESS) {
    // Test with null pointers
    ret = amdsmi_get_brcm_socket_handles(nullptr, nullptr);
    if (ret == AMDSMI_STATUS_INVAL) {
      std::cout << "\t\tError handling (null pointer): PASSED" << std::endl;
    } else {
      std::cout << "\t\tError handling (null pointer): FAILED (Status: " << ret << ")" << std::endl;
    }
    
    // Test with invalid processor handle
    char buffer[100];
    ret = amdsmi_brcm_getString(nullptr, "test_method", sizeof(buffer), buffer);
    if (ret == AMDSMI_STATUS_INVAL) {
      std::cout << "\t\tError handling (invalid handle): PASSED" << std::endl;
    } else {
      std::cout << "\t\tError handling (invalid handle): FAILED (Status: " << ret << ")" << std::endl;
    }
    
    amdsmi_brcm_shutdown();
  }
}

#endif // ENABLE_BRCM_SMI

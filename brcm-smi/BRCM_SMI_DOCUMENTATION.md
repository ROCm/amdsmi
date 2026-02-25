# BRCM SMI (Broadcom System Management Interface) Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation and Building](#installation-and-building)
4. [API Reference](#api-reference)
5. [Integration with AMD SMI](#integration-with-amd-smi)
6. [Device Management](#device-management)
7. [Troubleshooting](#troubleshooting)
8. [Python Interface](#python-interface)
9. [Best Practices](#best-practices)
10. [Conclusion](#conclusion)

## Overview

BRCM SMI (Broadcom System Management Interface) is a C library that provides system management capabilities for Broadcom network interface cards (NICs) and switches. It offers comprehensive device discovery, monitoring, and management functionality for Broadcom hardware components.

### Key Features

- **Device Discovery**: Automatic detection of Broadcom NICs and switches
- **Hardware Monitoring**: Temperature, power, and performance metrics
- **Device Information**: Firmware versions, device specifications, and topology
- **System Integration**: Socket and processor handle management
- **AMD SMI Integration**: Seamless integration with AMD SMI library
- **Multi-language Support**: C API with Python bindings

### Supported Hardware

- Broadcom Network Interface Cards (NICs)
- Broadcom Network Switches
- PCIe-based Broadcom devices

## Architecture

### BRCM SMI Block Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           BRCM SMI Architecture                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                              Application Layer                               │
├─────────────────────┬─────────────────────┬──────────────────────────────────┤
│   C Applications    │ Python Applications │      AMD SMI Integration         │
│                     │                     │                                  │
│  ┌───────────────┐  │ ┌───────────────┐   │  ┌─────────────────────────────┐ │
│  │ Custom Apps   │  │ │ Python Scripts│   │  │    Unified Management       │ │
│  │ Monitoring    │  │ │ CLI Tools     │   │  │    AMD + BRCM Devices       │ │
│  │ System Mgmt   │  │ │ Automation    │   │  │                             │ │
│  └───────────────┘  │ └───────────────┘   │  └─────────────────────────────┘ │
└─────────────────────┴─────────────────────┴──────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              API Layer                                       │
├─────────────────────┬─────────────────────┬──────────────────────────────────┤
│     C API           │   Python Bindings   │      AMD SMI Interface           │
│  (brcmsmi.h)        │ (brcmsmi_interface)  │   (amdsmi_brcm_* functions)     │
│                     │                     │                                  │
│ • brcmsmi_init()    │ • BrcmSmiInterface  │ • amdsmi_brcm_init()             │
│ • Device Discovery  │ • Device Methods    │ • amdsmi_brcm_discover()         │
│ • NIC Functions     │ • Error Handling    │ • Handle Management              │
│ • Switch Functions  │ • Type Conversion   │                                  │
│ • Generic Interface │                     │                                  │
└─────────────────────┴─────────────────────┴──────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            Core Library                                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                          BRCM SMI Core (brcm_smi.cc)                         │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐   │
│  │ Initialization  │  │ Device Discovery│  │    Handle Management        │   │
│  │                 │  │                 │  │                             │   │
│  │ • Library Init  │  │ • PCIe Scanning │  │ • Socket Handles            │   │
│  │ • Resource Mgmt │  │ • Device Enum   │  │ • Processor Handles         │   │
│  │ • Error Handling│  │ • Type Detection│  │ • Handle Validation         │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         Device Management Layer                              │
├─────────────────────────────┬────────────────────────────────────────────────┤
│        NIC Devices          │              Switch Devices                    │
│   (brcm_smi_nic_device)     │         (brcm_smi_switch_device)               │
│                             │                                                │
│ ┌─────────────────────────┐ │ ┌────────────────────────────────────────────┐ │
│ │   Device Information    │ │ │         Device Information                 │ │
│ │ • Name, Part Number     │ │ │ • Name, Part Number, Vendor ID             │ │
│ │ • Firmware Version      │ │ │ • Firmware Version, Device ID              │ │
│ │ • UUID, BDF Info        │ │ │ • UUID, BDF Info, Class                    │ │
│ └─────────────────────────┘ │ └────────────────────────────────────────────┘ │
│                             │                                                │
│ ┌─────────────────────────┐ │ ┌────────────────────────────────────────────┐ │
│ │    Monitoring           │ │ │           Link Management                  │ │
│ │ • Temperature Metrics   │ │ │ • Current/Max Link Speed                   │ │
│ │ • Power Management      │ │ │ • Current/Max Link Width                   │ │
│ │ • Hardware Info         │ │ │ • Link Status                              │ │
│ │ • Firmware Details      │ │ │                                            │ │
│ └─────────────────────────┘ │ └────────────────────────────────────────────┘ │
│                             │                                                │
│                             │ ┌────────────────────────────────────────────┐ │
│                             │ │        Power Management                    │ │
│                             │ │ • Runtime Status/Control                   │ │
│                             │ │ • Wakeup Management                        │ │
│                             │ │ • Power Metrics                            │ │
│                             │ └────────────────────────────────────────────┘ │
└─────────────────────────────┴────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                          System Interface Layer                              │
├──────────────────────────────────────────────────────────────────────────────┤
│                        Hardware Abstraction                                  │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐   │
│  │   PCIe Access   │  │  System Utils   │  │      LSPCI Commands         │   │
│  │                 │  │                 │  │                             │   │
│  │ • Device Enum   │  │ • NUMA Topology │  │ • Hardware Detection        │   │
│  │ • BDF Parsing   │  │ • CPU Affinity  │  │ • Device Properties         │   │
│  │ • Config Space  │  │ • Socket Mgmt   │  │ • Vendor Information        │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            Hardware Layer                                    │
├─────────────────────────────┬────────────────────────────────────────────────┤
│     Broadcom NICs           │            Broadcom Switches                   │
│                             │                                                │
│ ┌─────────────────────────┐ │ ┌────────────────────────────────────────────┐ │
│ │                         │ │ │         Switch Hardware                    │ │
│ │                         │ │ │ • Network Switches                         │ │
│ │   NetXtreme Cards       │ │ │ • PCIe-based Switches                      │ │
│ │                         │ │ │ • Fabric Switches                          │ │
│ └─────────────────────────┘ │ └────────────────────────────────────────────┘ │
│                             │                                                │
│        PCIe Interface       │              PCIe Interface                    │
│     Temperature Sensors     │           Link Status Monitoring               │
│      Power Management       │            Power Management                    │
│      Firmware Interface     │             Control Interface                  │
└─────────────────────────────┴────────────────────────────────────────────────┘

Data Flow:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Application │─── │  API Layer  │─── │ Core Library│─── │  Hardware   │
│   Request   │    │             │    │             │    │   Access    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                  │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│ Application │─── │  API Layer  │─── │ Core Library│ ◀──────────┘
│  Response   │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Core Components

```
BRCM SMI Library
├── Core System (brcm_smi.cc)
│   ├── Initialization/Shutdown
│   ├── Device Discovery
│   └── Handle Management
├── Device Management
│   ├── NIC Devices (brcm_smi_nic_device.h/cc)
│   ├── Switch Devices (brcm_smi_switch_device.h/cc)
│   └── Device Base Classes
├── System Integration
│   ├── Socket Management (brcm_smi_socket.h/cc)
│   ├── Processor Handles (brcm_smi_processor.h/cc)
│   └── System Utilities (brcm_smi_system.h/cc)
└── Hardware Interface
    ├── PCIe Discovery (brcm_smi_discovery.cc)
    ├── LSPCI Commands (brcm_smi_lspci_commands.h/cc)
    └── Hardware Monitoring
```

### Data Structures

#### Device Types
- **NIC Devices**: Network interface cards with monitoring capabilities
- **Switch Devices**: Network switches with link and power management
- **Socket Handles**: System-level device grouping
- **Processor Handles**: Individual device access points

## Installation and Building

### Prerequisites

- CMake 3.15 or higher
- C++17 compatible compiler
- Linux operating system
- PCIe access permissions

### Building with AMD SMI Integration

To build AMD SMI with BRCM SMI support:

```bash
# Clone the repository
git clone <amd-smi-repo>
cd amd-smi

# Create build directory
mkdir build && cd build

# Configure with BRCM SMI enabled
cmake .. -DENABLE_BRCM_SMI=ON

# Build the library
make -j$(nproc)

# Install (optional)
sudo make install
```

### Building BRCM SMI Standalone

```bash
# Navigate to BRCM SMI directory
cd brcm-smi

# Create build directory
mkdir build && cd build

# Configure and build
cmake ..
make -j$(nproc)
```

### Build Options

- `ENABLE_BRCM_SMI=ON/OFF`: Enable/disable BRCM SMI integration
- `BUILD_SHARED_LIBS=ON/OFF`: Build shared or static libraries
- `CMAKE_BUILD_TYPE=Debug/Release`: Set build type

## API Reference

### Core Functions

#### Initialization and Cleanup

```c
/**
 * @brief Initialize BRCM SMI library
 * @param init_flags Initialization flags (reserved, use 0)
 * @return BRCMSMI_STATUS_SUCCESS on success
 */
brcmsmi_status_t brcmsmi_init(uint64_t init_flags);

/**
 * @brief Shutdown BRCM SMI library
 * @return BRCMSMI_STATUS_SUCCESS on success
 */
brcmsmi_status_t brcmsmi_shutdown();
```

#### Device Discovery

```c
/**
 * @brief Discover all BRCM devices in the system
 * @param result Discovery results with device counts
 * @return BRCMSMI_STATUS_SUCCESS on success
 */
brcmsmi_status_t brcmsmi_discover_devices(brcmsmi_discovery_result_t* result);

/**
 * @brief Get socket handles for device access
 * @param socket_count Number of sockets found
 * @param socket_handles Array of socket handles
 * @return BRCMSMI_STATUS_SUCCESS on success
 */
brcmsmi_status_t brcmsmi_get_socket_handles(uint32_t *socket_count, 
                                           brcmsmi_socket_handle *socket_handles);
```

### NIC Device Functions

#### Device Information

```c
/**
 * @brief Get NIC processor handles
 * @param socket_handle Socket handle
 * @param processor_count Number of processors found
 * @param processor_handles Array of processor handles
 * @return BRCMSMI_STATUS_SUCCESS on success
 */
brcmsmi_status_t brcmsmi_get_nic_processor_handles(brcmsmi_socket_handle socket_handle,
                                                   uint32_t *processor_count,
                                                   brcmsmi_processor_handle **processor_handles);

/**
 * @brief Get NIC device information
 * @param processor_handle Processor handle
 * @param info NIC information structure
 * @return BRCMSMI_STATUS_SUCCESS on success
 */
brcmsmi_status_t brcmsmi_get_nic_info(brcmsmi_processor_handle processor_handle, 
                                      brcmsmi_nic_info_t *info);
```

#### Monitoring Functions

```c
/**
 * @brief Get NIC temperature information
 * @param processor_handle Processor handle
 * @param info Temperature metrics
 * @return BRCMSMI_STATUS_SUCCESS on success
 */
brcmsmi_status_t brcmsmi_get_nic_temp_info(brcmsmi_processor_handle processor_handle,
                                           brcmsmi_nic_temperature_metric_t *info);

/**
 * @brief Get NIC power information
 * @param processor_handle Processor handle
 * @param info Power metrics
 * @return BRCMSMI_STATUS_SUCCESS on success
 */
brcmsmi_status_t brcmsmi_get_nic_power_info(brcmsmi_processor_handle processor_handle,
                                            brcmsmi_nic_hwmon_power_t *info);

/**
 * @brief Get NIC firmware information
 * @param processor_handle Processor handle
 * @param info Firmware information
 * @return BRCMSMI_STATUS_SUCCESS on success
 */
brcmsmi_status_t brcmsmi_get_nic_fw_info(brcmsmi_processor_handle processor_handle,
                                         brcmsmi_nic_firmware_t *info);
```

### Switch Device Functions

```c
/**
 * @brief Get switch processor handles
 * @param socket_handle Socket handle
 * @param processor_count Number of processors found
 * @param processor_handles Array of processor handles
 * @return BRCMSMI_STATUS_SUCCESS on success
 */
brcmsmi_status_t brcmsmi_get_switch_processor_handles(brcmsmi_socket_handle socket_handle,
                                                      uint32_t *processor_count,
                                                      brcmsmi_processor_handle **processor_handles);

/**
 * @brief Get switch device information
 * @param processor_handle Processor handle
 * @param info Switch information
 * @return BRCMSMI_STATUS_SUCCESS on success
 */
brcmsmi_status_t brcmsmi_get_switch_info(brcmsmi_processor_handle processor_handle, 
                                         brcmsmi_switch_info_t *info);

/**
 * @brief Get switch link information
 * @param processor_handle Processor handle
 * @param info Link metrics
 * @return BRCMSMI_STATUS_SUCCESS on success
 */
brcmsmi_status_t brcmsmi_get_switch_link_info(brcmsmi_processor_handle processor_handle,
                                              brcmsmi_switch_link_metric_t *info);

/**
 * @brief Get switch power information
 * @param processor_handle Processor handle
 * @param info Power metrics
 * @return BRCMSMI_STATUS_SUCCESS on success
 */
brcmsmi_status_t brcmsmi_get_switch_power_info(brcmsmi_processor_handle processor_handle,
                                               brcmsmi_switch_power_metric_t *info);
```

### Generic Interface

```c
/**
 * @brief Generic string retrieval method for BRCM devices
 * @param processor_handle Handle to the processor (NIC or Switch)
 * @param method_name Name of the method to call
 * @param value_length Maximum length of the output buffer
 * @param value Output buffer to store the retrieved string
 * @return BRCMSMI_STATUS_SUCCESS on success
 */
brcmsmi_status_t brcmsmi_getString(brcmsmi_processor_handle processor_handle,
                                   const char* method_name,
                                   size_t value_length,
                                   char* value);
```

### Status Codes

```c
typedef enum {
    BRCMSMI_STATUS_SUCCESS = 0,
    BRCMSMI_STATUS_INVALID_ARGS,
    BRCMSMI_STATUS_NOT_SUPPORTED,
    BRCMSMI_STATUS_FILE_ERROR,
    BRCMSMI_STATUS_PERMISSION,
    BRCMSMI_STATUS_OUT_OF_RESOURCES,
    BRCMSMI_STATUS_INTERNAL_EXCEPTION,
    BRCMSMI_STATUS_INPUT_OUT_OF_BOUNDS,
    BRCMSMI_STATUS_INIT_ERROR,
    BRCMSMI_STATUS_NOT_YET_IMPLEMENTED,
    BRCMSMI_STATUS_NOT_FOUND,
    BRCMSMI_STATUS_INSUFFICIENT_SIZE,
    BRCMSMI_STATUS_INTERRUPTED,
    BRCMSMI_STATUS_UNEXPECTED_SIZE,
    BRCMSMI_STATUS_NO_DATA,
    BRCMSMI_STATUS_UNEXPECTED_DATA,
    BRCMSMI_STATUS_BUSY,
    BRCMSMI_STATUS_REFCOUNT_OVERFLOW,
    BRCMSMI_STATUS_NOT_INITIALIZED,
    BRCMSMI_STATUS_ALREADY_INITIALIZED,
    BRCMSMI_STATUS_UNKNOWN_ERROR = 0xFFFFFFFF
} brcmsmi_status_t;
```


## Integration with AMD SMI

BRCM SMI is designed to integrate seamlessly with AMD SMI, providing a unified interface for managing both AMD and Broadcom hardware.

### AMD SMI Integration Functions

When BRCM SMI is built with AMD SMI integration (`ENABLE_BRCM_SMI=ON`), additional functions are available:

```c
// AMD SMI compatible initialization
amdsmi_status_t amdsmi_brcm_init(uint64_t init_flags);
amdsmi_status_t amdsmi_brcm_shutdown();

// Device discovery
amdsmi_status_t amdsmi_brcm_discover_devices(amdsmi_brcm_discovery_result_t* result);

// Handle management
amdsmi_status_t amdsmi_get_brcm_socket_handles(uint32_t* socket_count, 
                                              amdsmi_brcm_socket_handle* socket_handles);
```


## Device Management

### Device Discovery Process

1. **Initialization**: Call `brcmsmi_init()` to initialize the library
2. **Discovery**: Call `brcmsmi_discover_devices()` to scan for devices
3. **Socket Enumeration**: Get socket handles using `brcmsmi_get_socket_handles()`
4. **Device Enumeration**: Get processor handles for NICs and switches
5. **Device Access**: Use processor handles to access device information

### Device Hierarchy

```
System
├── Socket 0
│   ├── NIC Processors
│   │   ├── NIC Device 0
│   │   └── NIC Device 1
│   └── Switch Processors
│       ├── Switch Device 0
│       └── Switch Device 1

```

### Handle Management

- **Socket Handles**: Represent physical sockets or NUMA nodes
- **Processor Handles**: Represent individual devices (NICs or switches)
- **Handle Lifetime**: Valid until `brcmsmi_shutdown()` is called
- **Thread Safety**: Handles are thread-safe for read operations

## Troubleshooting

### Common Issues

#### 1. Initialization Failures

**Problem**: `brcmsmi_init()` returns `BRCMSMI_STATUS_INIT_ERROR`

**Solutions**:
- Ensure you have proper permissions to access PCIe devices
- Check if Broadcom devices are present in the system
- Verify that the library was built correctly

```bash
# Check for Broadcom devices
lspci | grep -i broadcom

# Check permissions
ls -la /sys/bus/pci/devices/
```

#### 2. No Devices Found

**Problem**: `brcmsmi_discover_devices()` returns zero devices

**Solutions**:
- Verify Broadcom hardware is installed and recognized
- Check device drivers are loaded
- Ensure devices are not in use by other applications

```bash
# Check loaded modules
lsmod | grep -i broadcom

# Check device status
dmesg | grep -i broadcom
```

#### 3. Permission Errors

**Problem**: `BRCMSMI_STATUS_PERMISSION` errors

**Solutions**:
- Run as root or with appropriate permissions
- Add user to appropriate groups
- Check SELinux/AppArmor policies

```bash
# Add user to groups
sudo usermod -a -G render,video $USER

# Check current permissions
groups $USER
```

#### 4. Library Loading Issues

**Problem**: Library fails to load or link

**Solutions**:
- Check library path configuration
- Verify all dependencies are installed
- Update library cache

```bash
# Update library cache
sudo ldconfig

# Check library dependencies
ldd /usr/lib/libamd_smi.so

# Check library path
echo $LD_LIBRARY_PATH
```

### Debug Information

Enable debug output by setting environment variables:

```bash
export BRCMSMI_DEBUG=1
export BRCMSMI_LOG_LEVEL=DEBUG
```

### Error Code Reference

| Error Code | Description | Common Causes |
|------------|-------------|---------------|
| `BRCMSMI_STATUS_SUCCESS` | Operation successful | - |
| `BRCMSMI_STATUS_INVALID_ARGS` | Invalid arguments | NULL pointers, invalid handles |
| `BRCMSMI_STATUS_NOT_SUPPORTED` | Operation not supported | Unsupported hardware/feature |
| `BRCMSMI_STATUS_FILE_ERROR` | File system error | Permission issues, missing files |
| `BRCMSMI_STATUS_PERMISSION` | Permission denied | Insufficient privileges |
| `BRCMSMI_STATUS_INIT_ERROR` | Initialization failed | Hardware not found, driver issues |
| `BRCMSMI_STATUS_NOT_INITIALIZED` | Library not initialized | Call `brcmsmi_init()` first |

## Python Interface

BRCM SMI provides Python bindings through the `brcmsmi_interface` module.

### Installation

The Python interface is automatically built when BRCM SMI is enabled:

```bash
# Install Python package
cd build/py-interface/python_package
pip install .
```


### Python API Methods

```python
class BrcmSmiInterface:
    def init(self, flags: int) -> int
    def shutdown(self) -> int
    def discover_devices(self) -> BrcmsmiBdf
    def get_socket_handles(self) -> List[int]
    def get_nic_processor_handles(self, socket_handle: int) -> List[int]
    def get_switch_processor_handles(self, socket_handle: int) -> List[int]
    def get_nic_info(self, processor_handle: int) -> dict
    def get_switch_info(self, processor_handle: int) -> dict
    # ... additional methods
```


## Best Practices

### 1. Resource Management

- Always call `brcmsmi_shutdown()` before program exit
- Check return values for all API calls
- Handle errors gracefully

### 2. Performance Considerations

- Cache device handles when possible
- Avoid frequent device discovery calls
- Use batch operations when available

### 3. Error Handling

```c
brcmsmi_status_t status = brcmsmi_init(0);
switch (status) {
    case BRCMSMI_STATUS_SUCCESS:
        // Continue with operations
        break;
    case BRCMSMI_STATUS_ALREADY_INITIALIZED:
        // Library already initialized, continue
        break;
    case BRCMSMI_STATUS_INIT_ERROR:
        // Handle initialization failure
        fprintf(stderr, "Failed to initialize BRCM SMI\n");
        return -1;
    default:
        // Handle other errors
        fprintf(stderr, "Unexpected error: %d\n", status);
        return -1;
}
```

### 4. Thread Safety

- BRCM SMI is thread-safe for read operations
- Serialize initialization and shutdown calls


## Conclusion

BRCM SMI provides a comprehensive interface for managing Broadcom network hardware. Its integration with AMD SMI creates a unified platform for heterogeneous system management. The library's modular design, extensive API, and multi-language support make it suitable for a wide range of applications, from simple monitoring scripts to complex system management platforms.

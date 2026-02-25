# BRCM SMI Examples

This directory contains example programs demonstrating how to use the BRCM SMI (Broadcom System Management Interface) library for managing Broadcom network interface cards (NICs) and switches.

## Available Examples

### 1. Basic Device Discovery (`brcm_smi_discovery_example.cc`)
- **Executable**: `brcm_smi_discovery_ex`
- **Purpose**: Demonstrates basic BRCM SMI initialization, device discovery, and socket enumeration
- **Features**:
  - Library initialization and cleanup
  - Device discovery (NICs and switches)
  - Socket handle enumeration
  - Basic error handling

### 2. NIC Device Monitoring (`brcm_smi_nic_example.cc`)
- **Executable**: `brcm_smi_nic_ex`
- **Purpose**: Comprehensive NIC device monitoring and information retrieval
- **Features**:
  - NIC device information (name, part number, firmware, UUID, BDF)
  - Temperature monitoring (current, max, critical, emergency thresholds)
  - Power management metrics (runtime status, usage, active time)
  - Firmware information (package, EFI, NCSI, RoCE versions)
  - Hardware information (class, vendor, IRQ, NUMA, link speed/width, SR-IOV)

### 3. Switch Device Management (`brcm_smi_switch_example.cc`)
- **Executable**: `brcm_smi_switch_ex`
- **Purpose**: Comprehensive switch device management and monitoring
- **Features**:
  - Switch device information (name, part number, firmware, vendor/device IDs)
  - Link metrics (current/max speed and width)
  - Power management (control, runtime status, wakeup information)
  - Device metrics (class, vendor, IRQ, NUMA, AER information)
  - Advanced hardware information (DMA, MSI, SR-IOV, etc.)

### 4. Unified AMD SMI Integration (`brcm_smi_unified_example.cc`)
- **Executable**: `brcm_smi_unified_ex`
- **Purpose**: Demonstrates BRCM SMI integration with AMD SMI for unified system management
- **Features**:
  - AMD SMI initialization with BRCM SMI support
  - BRCM device discovery through AMD SMI interface
  - BRCM socket and processor handle management
  - AMD GPU and CPU device enumeration
  - Unified system monitoring approach

## Building the Examples

### Prerequisites

1. **BRCM SMI Support**: Examples require BRCM SMI to be enabled during build
2. **CMake**: Version 3.20 or higher
3. **C++ Compiler**: C++17 compatible compiler
4. **AMD SMI Library**: Built with BRCM SMI integration

### Build Instructions

1. **Configure with BRCM SMI enabled**:
   ```bash
   cd amd-smi
   mkdir build && cd build
   cmake .. -DENABLE_BRCM_SMI=ON
   ```

2. **Build the examples**:
   ```bash
   make -j$(nproc)
   ```

3. **Navigate to examples**:
   ```bash
   cd example
   ```

### Build Output

When `ENABLE_BRCM_SMI=ON` is specified, the following executables will be built:

- `brcm_smi_discovery_ex` - Basic device discovery
- `brcm_smi_nic_ex` - NIC monitoring
- `brcm_smi_switch_ex` - Switch management  
- `brcm_smi_unified_ex` - Unified AMD SMI integration

If `ENABLE_BRCM_SMI=OFF` (default), the BRCM SMI examples will be skipped with an informational message.

## Running the Examples

### Basic Usage

```bash
# Run basic device discovery
./brcm_smi_discovery_ex

# Run NIC monitoring
./brcm_smi_nic_ex

# Run switch management
./brcm_smi_switch_ex

# Run unified integration example
./brcm_smi_unified_ex
```

### Expected Output

#### With BRCM Hardware Present

```
BRCM SMI Basic Device Discovery Example
======================================

BRCM SMI initialized successfully
Device Discovery Results:
  NIC devices found: 2
  Switch devices found: 1
  Total devices: 3

Socket Information:
  Found 1 sockets
  Socket 0: Handle = 0x...

BRCM SMI shutdown completed
```

#### Without BRCM Hardware

```
BRCM SMI Basic Device Discovery Example
======================================

BRCM SMI initialized successfully
Device Discovery Results:
  NIC devices found: 0
  Switch devices found: 0
  Total devices: 0

No sockets found in the system

BRCM SMI shutdown completed
```

### Permissions

Some examples may require elevated permissions to access hardware information:

```bash
# Run with sudo if needed
sudo ./brcm_smi_nic_ex
```

## Example Code Structure

### Common Pattern

All examples follow a similar structure:

1. **Initialization**: Call `brcmsmi_init(0)` to initialize the library
2. **Discovery**: Use `brcmsmi_discover_devices()` to find hardware
3. **Enumeration**: Get socket handles with `brcmsmi_get_socket_handles()`
4. **Device Access**: Get processor handles for specific device types
5. **Information Retrieval**: Use device-specific functions to get metrics
6. **Cleanup**: Call `brcmsmi_shutdown()` before exit

### Error Handling

Examples demonstrate proper error handling:

```c
brcmsmi_status_t status = brcmsmi_init(0);
if (status != BRCMSMI_STATUS_SUCCESS) {
    printf("Failed to initialize BRCM SMI: %d\n", status);
    return -1;
}
```

### Memory Management

Examples show proper memory management:

```c
brcmsmi_socket_handle *socket_handles = malloc(sizeof(brcmsmi_socket_handle) * socket_count);
if (socket_handles) {
    // Use handles
    free(socket_handles);
}
```

## Troubleshooting

### Build Issues

1. **BRCM SMI examples not building**:
   - Ensure `-DENABLE_BRCM_SMI=ON` is specified during cmake configuration
   - Check that BRCM SMI source files are present in `brcm-smi/` directory

2. **Compilation errors**:
   - Verify C++17 compiler support
   - Check that all required headers are installed

### Runtime Issues

1. **"Failed to initialize BRCM SMI"**:
   - Check if Broadcom hardware is present: `lspci | grep -i broadcom`
   - Verify permissions to access PCIe devices
   - Ensure proper device drivers are loaded

2. **"No devices found"**:
   - Normal if no Broadcom hardware is installed
   - Check device recognition: `dmesg | grep -i broadcom`

3. **Permission errors**:
   - Run with elevated privileges: `sudo ./example`
   - Check user group memberships

## Integration with Your Code

### Basic Integration

```c
#include <brcm_smi/brcmsmi.h>

int main() {
    // Initialize
    if (brcmsmi_init(0) != BRCMSMI_STATUS_SUCCESS) {
        return -1;
    }
    
    // Your code here
    
    // Cleanup
    brcmsmi_shutdown();
    return 0;
}
```

### AMD SMI Integration

```c
#include <amd_smi/amdsmi.h>

int main() {
    // Initialize AMD SMI
    amdsmi_init();
    
#ifdef ENABLE_BRCM_SMI
    // Initialize BRCM SMI through AMD SMI
    amdsmi_brcm_init(0);
    
    // Use BRCM functionality
#endif
    
    // Cleanup
    amdsmi_shut_down();
    return 0;
}
```

## Additional Resources

- **BRCM SMI Documentation**: `brcm-smi/BRCM_SMI_DOCUMENTATION.md`
- **AMD SMI Integration Guide**: `BUILD_WITH_BRCM_SMI.md`
- **API Reference**: See header files in `brcm-smi/include/brcm_smi/`
- **Python Interface**: `py-interface/brcmsmi_interface.py`

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the comprehensive documentation
3. Examine the example source code for implementation details
4. Verify hardware compatibility and driver status

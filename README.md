# AMD System Management Interface (AMD SMI) Library

The AMD System Management Interface Library, or AMD SMI library, is a C library for Linux that provides a user space interface for applications to monitor and control AMD devices.

## Supported platforms

At initial release, the AMD SMI library will support Linux bare metal and Linux virtual machine guest for AMD GPUs. In the future release, the library will be extended to support AMD EPYC™ CPUs.

AMD SMI library can run on AMD ROCm supported platforms, please refer to [List of Supported Operating Systems and GPUs](https://docs.amd.com/bundle/ROCm-Getting-Started-Guide-v5.3/page/Introduction_to_ROCm_Getting_Started_Guide_for_Linux.html)

To run the AMD SMI library, the amdgpu driver needs to be installed. Optionally, the libdrm can be
installed to query firmware information and hardware IPs.

## Building AMD SMI

### Additional Required software for building

In order to build the AMD SMI library, the following components are required. Note that the software versions listed are what was used in development. Earlier versions are not guaranteed to work:
* CMake (v3.11.0) - `pip3 install cmake`
* g++ (5.4.0)

In order to build the AMD SMI python package, the following components are required:
* clang (14.0 or above)
* python (3.6 or above)
* virtualenv - `pip3 install virtualenv`

In order to build the latest documentation, the following are required:

* DOxygen (1.8.11)
* latex (pdfTeX 3.14159265-2.6-1.40.16)

The source code for AMD SMI is available on Github.

After the AMD SMI library git repository has been cloned to a local Linux machine, the Default location for the library and headers is /opt/rocm. Building the library is achieved by following the typical CMake build sequence, specifically:

```bash
mkdir -p build
cd build
cmake ..
make -j $(nproc)
make install
```

The built library will appear in the `build` folder.

To build the rpm and deb packages follow the above steps with:

```bash
make package
```

### Documentation

The reference manual, `refman.pdf` will be in the `latex` directory upon a successful build.

### Building the Tests

In order to verify the build and capability of AMD SMI on your system and to see an example of how AMD SMI can be used, you may build and run the tests that are available in the repo. To build the tests, follow these steps:

```bash
mkdir -p build
cd build
cmake -DBUILD_TESTS=ON <location of root of AMD SMI library CMakeLists.txt>
make -j $(nproc)
```

### Run the Tests

To run the test, execute the program `amdsmitst` that is built from the steps above.

## Usage Basics

### Device/Socket handles

Many of the functions in the library take a "socket handle" or "device handle". The socket is an abstraction of hardware physical socket. This will enable amd-smi to provide a better representation of the hardware to user. Although there is always one distinct GPU for a socket, the APU may have both
GPU device and CPU device on the same socket. Moreover, for MI200, it may have multiple GCDs.

To discover the sockets in the system, `amdsmi_get_socket_handles()` is called to get list of sockets
handles, which in turn can be used to query the devices in that socket using `amdsmi_get_device_handles()`. The device handler is used to distinguish the detected devices from one another. It is important to note that a device may end up with a different device handles after restart application, so a device handle should not be relied upon to be constant over process.

## Hello AMD SMI

The only required AMD-SMI call for any program that wants to use AMD-SMI is the `amdsmi_init()` call. This call initializes some internal data structures that will be used by subsequent AMD-SMI calls. In the call, a flag can be passed if the application is only interested in a specific device type.

When AMD-SMI is no longer being used, `amdsmi_shut_down()` should be called. This provides a way to do any releasing of resources that AMD-SMI may have held.

A simple "Hello World" type program that displays the temperature of detected devices would look like this:

```c++
#include <iostream>
#include <vector>
#include "amd_smi/amdsmi.h"

int main() {
  amdsmi_status_t ret;
 
  // Init amdsmi for sockets and devices. Here we are only interested in AMD_GPUS.
  ret = amdsmi_init(AMD_SMI_INIT_AMD_GPUS);
 
  // Get the socket count available in the system.
  ret = amdsmi_get_socket_handles(&socket_count, nullptr);
 
  // Allocate the memory for the sockets
  std::vector<amdsmi_socket_handle> sockets(socket_count);
  // Get the socket handles in the system
  ret = amdsmi_get_socket_handles(&socket_count, &sockets[0]);
     
  std::cout << "Total Socket: " << socket_count << std::endl;
 
  // For each socket, get identifier and devices
  for (uint32_t i=0; i < socket_count; i++) {
    // Get Socket info
    char socket_info[128];
    ret = amdsmi_get_socket_info(sockets[i], socket_info, 128);
    std::cout << "Socket " << socket_info<< std::endl;
 
    // Get the device count for the socket.
    uint32_t device_count = 0;
    ret = amdsmi_get_device_handles(sockets[i], &device_count, nullptr);
 
    // Allocate the memory for the device handlers on the socket
    std::vector<amdsmi_device_handle> device_handles(device_count);
    // Get all devices of the socket
    ret = amdsmi_get_device_handles(sockets[i],
              &device_count, &device_handles[0]);
      
    // For each device of the socket, get name and temperature.
    for (uint32_t j=0; j < device_count; j++) {
      // Get device type. Since the amdsmi is initialized with
      // AMD_SMI_INIT_AMD_GPUS, the device_type must be AMD_GPU.
      device_type_t device_type;
      ret = amdsmi_get_device_type(device_handles[j], &device_type);
      if (device_type != AMD_GPU) {
        std::cout << "Expect AMD_GPU device type!\n";
        return 1;
      }
 
      // Get device name
      amdsmi_board_info_t board_info;
      ret = amdsmi_get_board_info(device_handles[j], &board_info);
      std::cout << "\tdevice "
                  << j <<"\n\t\tName:" << board_info.product_name << std::endl;
 
      // Get temperature
      int64_t val_i64 = 0;
      ret =  amdsmi_dev_get_temp_metric(device_handles[j], TEMPERATURE_TYPE_EDGE,
              AMDSMI_TEMP_CURRENT, &val_i64);
      std::cout << "\t\tTemperature: " << val_i64 << "C" << std::endl;
    }
  }
 
  // Clean up resources allocated at amdsmi_init. It will invalidate sockets
  // and devices pointers
  ret = amdsmi_shut_down();
 
  return 0;
}
```

# Python wrapper
The python wrapper (binding) is an auto-generated file `py-interface/amdsmi_wrapper.py`

Wrapper should be re-generated on each C++ API change, by doing:

```bash
cmake .. -DBUILD_WRAPPER=on
make python_wrapper # or simply 'make'
```

After this command, the file in `py-interface/amdsmi_wrapper.py` will be automatically updated on each compile.

Note: To be able to re-generate python wrapper you need several tools installed on your system: clang-14, clang-format, libclang-dev, and ***python3.7 or newer***.

Note: python_wrapper is NOT automatically re-generated. You must run `cmake` with `-DBUILD_WRAPPER=on` argument.

## DISCLAIMER

The information contained herein is for informational purposes only, and is subject to change without notice. In addition, any stated support is planned and is also subject to change. While every precaution has been taken in the preparation of this document, it may contain technical inaccuracies, omissions and typographical errors, and AMD is under no obligation to update or otherwise correct this information. Advanced Micro Devices, Inc. makes no representations or warranties with respect to the accuracy or completeness of the contents of this document, and assumes no liability of any kind, including the implied warranties of noninfringement, merchantability or fitness for particular purposes, with respect to the operation or use of AMD hardware, software or other products described herein.

© 2022 Advanced Micro Devices, Inc. All Rights Reserved.

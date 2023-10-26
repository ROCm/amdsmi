# AMD System Management Interface (AMD SMI) Library

The AMD System Management Interface Library, or AMD SMI library, is a C library for Linux that provides a user space interface for applications to monitor and control AMD devices.

For additional information refer to [ROCm Documentation](https://rocm.docs.amd.com/projects/amdsmi/en/latest/)

Note: This project is a successor to [rocm_smi_lib](https://github.com/RadeonOpenCompute/rocm_smi_lib)

## Supported platforms

At initial release, the AMD SMI library will support Linux bare metal and Linux virtual machine guest for AMD GPUs. In the future release, the library will be extended to support AMD EPYC™ CPUs.

AMD SMI library can run on AMD ROCm supported platforms, please refer to [List of Supported Operating Systems and GPUs](https://rocm.docs.amd.com/en/latest/release/gpu_os_support.html)

To run the AMD SMI library, the amdgpu driver needs to be installed. Optionally, the libdrm can be
installed to query firmware information and hardware IPs.

## Usage Basics

### Device/Socket handles

Many of the functions in the library take a "socket handle" or "device handle". The socket is an abstraction of hardware physical socket. This will enable amd-smi to provide a better representation of the hardware to user. Although there is always one distinct GPU for a socket, the APU may have both
GPU device and CPU device on the same socket. Moreover, for MI200, it may have multiple GCDs.

To discover the sockets in the system, `amdsmi_get_socket_handles()` is called to get list of sockets
handles, which in turn can be used to query the devices in that socket using `amdsmi_get_processor_handles()`. The device handler is used to distinguish the detected devices from one another. It is important to note that a device may end up with a different device handles after restart application, so a device handle should not be relied upon to be constant over process.

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
  ret = amdsmi_init(AMDSMI_INIT_AMD_GPUS);

  // Get all sockets
  uint32_t socket_count = 0;

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
    ret = amdsmi_get_socket_info(sockets[i], 128, socket_info);
    std::cout << "Socket " << socket_info<< std::endl;

    // Get the device count for the socket.
    uint32_t device_count = 0;
    ret = amdsmi_get_processor_handles(sockets[i], &device_count, nullptr);

    // Allocate the memory for the device handlers on the socket
    std::vector<amdsmi_processor_handle> processor_handles(device_count);
    // Get all devices of the socket
    ret = amdsmi_get_processor_handles(sockets[i],
              &device_count, &processor_handles[0]);

    // For each device of the socket, get name and temperature.
    for (uint32_t j=0; j < device_count; j++) {
      // Get device type. Since the amdsmi is initialized with
      // AMD_SMI_INIT_AMD_GPUS, the processor_type must be AMD_GPU.
      processor_type_t processor_type;
      ret = amdsmi_get_processor_type(processor_handles[j], &processor_type);
      if (processor_type != AMD_GPU) {
        std::cout << "Expect AMD_GPU device type!\n";
        return 1;
      }

      // Get device name
      amdsmi_board_info_t board_info;
      ret = amdsmi_get_gpu_board_info(processor_handles[j], &board_info);
      std::cout << "\tdevice "
                  << j <<"\n\t\tName:" << board_info.product_name << std::endl;

      // Get temperature
      int64_t val_i64 = 0;
      ret =  amdsmi_get_temp_metric(processor_handles[j], TEMPERATURE_TYPE_EDGE,
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

### Documentation

The reference manual, `AMD_SMI_Manual.pdf` will be in the /opt/rocm/share/doc/amd_smi directory upon a successful build.

### Sphinx Documentation

To build the documentation locally, run the commands below:

``` bash
cd docs

python3 -m pip install -r sphinx/requirements.txt

python3 -m sphinx -T -E -b html -d _build/doctrees -D language=en . _build/html
```

The output will be in `docs/_build/html`.

For additional details, see the [ROCm Contributing Guide](https://rocm.docs.amd.com/en/latest/contributing.html#building-documentation)

## Install CLI Tool and Python Library

### Requirements

* python 3.7+ 64-bit
* amdgpu driver must be loaded for amdsmi_init() to pass

### Optional autocompletion

`amd-smi` cli application supports autocompletion. It is enabled by using the
following commands:

```bash
python3 -m pip install argcomplete
activate-global-python-argcomplete
# restart shell to enable
```

### CLI Installation

Before amd-smi install, ensure previous versions of amdsmi library are uninstalled using pip:

```bash
python3 -m pip list | grep amd
python3 -m pip uninstall amdsmi
```

* Install amdgpu driver
* Install amd-smi-lib package through package manager
* amd-smi --help

### Install Example for Ubuntu 22.04

``` bash
python3 -m pip list | grep amd
python3 -m pip uninstall amdsmi
apt install amd-smi-lib
amd-smi --help
```

### Python Development Library Installation

This option is for users who want to develop their own scripts using amd-smi's python library

Verify that your python version is 3.7+ to install the python library

* Install amdgpu driver
* Install amd-smi-lib package through package manager
* cd /opt/rocm/share/amd_smi
* python3 -m pip install --upgrade pip
* python3 -m pip install --user .
* import amdsmi in python to start development

Warning: this will take precedence over the cli tool's library install, to avoid issues run these steps after every amd-smi-lib update.

#### Older RPM Packaged OS's

The default python versions in older RPM based OS's are not gauranteed to have the minium version.

For example RHEL 8 and SLES 15 are 3.6.8 and 3.6.15 . You will need to ensure the latest yaml package is installed ( pyyaml >= 5.1) pyyaml is installed to your pip instance:

``` bash
python3 -m pip install pyyaml
amd-smi list
```

While the CLI will work with these older python versions, to install the python development library you need to upgrade to python 3.7+

#### Python Library Install Example for Ubuntu 22.04

``` bash
apt install amd-smi-lib
amd-smi --help
cd /opt/rocm/share/amd_smi
python3 -m pip install --upgrade pip
python3 -m pip install --user .
```

``` bash
python3
Python 3.8.10 (default, May 26 2023, 14:05:08)
[GCC 9.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import amdsmi
>>>
```

### Rebuilding Python wrapper

The python wrapper (binding) is an auto-generated file `py-interface/amdsmi_wrapper.py`

Wrapper should be re-generated on each C++ API change, by doing:

```bash
./update_wrapper.sh
```

After this command, the file in `py-interface/amdsmi_wrapper.py` will be automatically updated on each compile.

Note: To be able to re-generate python wrapper you need **docker** installed.

Note: python_wrapper is NOT automatically re-generated. You must run `./update_wrapper.sh`.

## Building AMD SMI

### Additional Required software for building

In order to build the AMD SMI library, the following components are required. Note that the software versions listed are what was used in development. Earlier versions are not guaranteed to work:

* CMake (v3.14.0) - `python3 -m pip install cmake`
* g++ (5.4.0)

In order to build the AMD SMI python package, the following components are required:

* clang (14.0 or above)
* python (3.7 or above)
* virtualenv - `python3 -m pip install virtualenv`

In order to build the latest documentation, the following are required:

* DOxygen (1.8.11)
* latex (pdfTeX 3.14159265-2.6-1.40.16)

The source code for AMD SMI is available on Github.

After the AMD SMI library git repository has been cloned to a local Linux machine, the Default location for the library and headers is /opt/rocm. Before installation, the old rocm directories should be deleted:
/opt/rocm
/opt/rocm-{number}

Building the library is achieved by following the typical CMake build sequence (run as root user or use 'sudo' before 'make install' command), specifically:

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

### Building the Tests

In order to verify the build and capability of AMD SMI on your system and to see an example of how AMD SMI can be used, you may build and run the tests that are available in the repo. To build the tests, follow these steps:

```bash
mkdir -p build
cd build
cmake -DBUILD_TESTS=ON ..
make -j $(nproc)
```

### Run the Tests

To run the test, execute the program `amdsmitst` that is built from the steps above.
Path to the program `amdsmitst`: build/tests/amd_smi_test/

## DISCLAIMER

The information contained herein is for informational purposes only, and is subject to change without notice. In addition, any stated support is planned and is also subject to change. While every precaution has been taken in the preparation of this document, it may contain technical inaccuracies, omissions and typographical errors, and AMD is under no obligation to update or otherwise correct this information. Advanced Micro Devices, Inc. makes no representations or warranties with respect to the accuracy or completeness of the contents of this document, and assumes no liability of any kind, including the implied warranties of noninfringement, merchantability or fitness for particular purposes, with respect to the operation or use of AMD hardware, software or other products described herein.

© 2023 Advanced Micro Devices, Inc. All Rights Reserved.

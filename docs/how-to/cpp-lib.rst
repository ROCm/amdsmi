.. meta::
  :description: Learn about the AMD SMI C++ library's basic usage.
  :keywords: AMD, SMI, system, management, interface, how to, examples

********************************
C++ library basic usage
********************************

Usage Basics for the C Library
------------------------------

Device/Socket handles
~~~~~~~~~~~~~~~~~~~~~

Many of the functions in the library take a “socket handle” or “device
handle”. The socket is an abstraction of hardware physical socket. This
will enable amd-smi to provide a better representation of the hardware
to user. Although there is always one distinct GPU for a socket, the APU
may have both GPU device and CPU device on the same socket. Moreover,
for MI200, it may have multiple GCDs.

To discover the sockets in the system, ``amdsmi_get_socket_handles()``
is called to get list of sockets handles, which in turn can be used to
query the devices in that socket using
``amdsmi_get_processor_handles()``. The device handler is used to
distinguish the detected devices from one another. It is important to
note that a device may end up with a different device handles after
restart application, so a device handle should not be relied upon to be
constant over process.

The list of socket handles discovered using
``amdsmi_get_socket_handles()``,can also be used to query the cpus in
that socket using ``amdsmi_get_processor_handles_by_type()``, which in
turn can then be used to query the cores in that cpu using
``amdsmi_get_processor_handles_by_type()`` again.

Hello AMD SMI
-------------

The only required AMD-SMI call for any program that wants to use AMD-SMI
is the ``amdsmi_init()`` call. This call initializes some internal data
structures that will be used by subsequent AMD-SMI calls. In the call, a
flag can be passed if the application is only interested in a specific
device type.

When AMD-SMI is no longer being used, ``amdsmi_shut_down()`` should be
called. This provides a way to do any releasing of resources that
AMD-SMI may have held.

1) A simple “Hello World” type program that displays the temperature of
   detected devices would look like this:

.. code:: cpp

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
         // AMD_SMI_INIT_AMD_GPUS, the processor_type must be AMDSMI_PROCESSOR_TYPE_AMD_GPU.
         processor_type_t processor_type;
         ret = amdsmi_get_processor_type(processor_handles[j], &processor_type);
         if (processor_type != AMDSMI_PROCESSOR_TYPE_AMD_GPU) {
           std::cout << "Expect AMDSMI_PROCESSOR_TYPE_AMD_GPU device type!\n";
           return 1;
         }

         // Get device name
         amdsmi_board_info_t board_info;
         ret = amdsmi_get_gpu_board_info(processor_handles[j], &board_info);
         std::cout << "\tdevice "
                     << j <<"\n\t\tName:" << board_info.product_name << std::endl;

         // Get temperature
         int64_t val_i64 = 0;
         ret =  amdsmi_get_temp_metric(processor_handles[j], AMDSMI_TEMPERATURE_TYPE_EDGE,
                 AMDSMI_TEMP_CURRENT, &val_i64);
         std::cout << "\t\tTemperature: " << val_i64 << "C" << std::endl;
       }
     }

     // Clean up resources allocated at amdsmi_init. It will invalidate sockets
     // and devices pointers
     ret = amdsmi_shut_down();

     return 0;
   }

2) A sample program that displays the power of detected cpus would look
   like this:

.. code:: cpp

   #include <iostream>
   #include <vector>
   #include "amd_smi/amdsmi.h"

   int main(int argc, char **argv) {
       amdsmi_status_t ret;
       uint32_t socket_count = 0;

       // Initialize amdsmi for AMD CPUs
       ret = amdsmi_init(AMDSMI_INIT_AMD_CPUS);

       ret = amdsmi_get_socket_handles(&socket_count, nullptr);

       // Allocate the memory for the sockets
       std::vector<amdsmi_socket_handle> sockets(socket_count);

       // Get the sockets of the system
       ret = amdsmi_get_socket_handles(&socket_count, &sockets[0]);

       std::cout << "Total Socket: " << socket_count << std::endl;

       // For each socket, get cpus
       for (uint32_t i = 0; i < socket_count; i++) {
           uint32_t cpu_count = 0;

           // Set processor type as AMDSMI_PROCESSOR_TYPE_AMD_CPU
           processor_type_t processor_type = AMDSMI_PROCESSOR_TYPE_AMD_CPU;
           ret = amdsmi_get_processor_handles_by_type(sockets[i], processor_type, nullptr, &cpu_count);

           // Allocate the memory for the cpus
           std::vector<amdsmi_processor_handle> plist(cpu_count);

            // Get the cpus for each socket
           ret = amdsmi_get_processor_handles_by_type(sockets[i], processor_type, &plist[0], &cpu_count);

           for (uint32_t index = 0; index < plist.size(); index++) {
               uint32_t socket_power;
               std::cout<<"CPU "<<index<<"\t"<< std::endl;
               std::cout<<"Power (Watts): ";

               ret = amdsmi_get_cpu_socket_power(plist[index], &socket_power);
               if(ret != AMDSMI_STATUS_SUCCESS)
                   std::cout<<"Failed to get cpu socket power"<<"["<<index<<"] , Err["<<ret<<"] "<< std::endl;

               if (!ret) {
                   std::cout<<static_cast<double>(socket_power)/1000<<std::endl;
               }
               std::cout<<std::endl;
           }
       }

       // Clean up resources allocated at amdsmi_init
       ret = amdsmi_shut_down();

       return 0;
   }

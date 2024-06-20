# AMD SMI Python Library

## Requirements

* python 3.6+ 64-bit
* driver must be loaded for amdsmi_init() to pass

## Overview

## Folder structure

File Name | Note
---|---
`__init__.py` | Python package initialization file
`amdsmi_interface.py` | Amdsmi library python interface
`amdsmi_wrapper.py` | Python wrapper around amdsmi binary
`amdsmi_exception.py` | Amdsmi exceptions python file
`README.md` | Documentation

## Usage

`amdsmi` folder should be copied and placed next to importing script. It should be imported as:

```python
from amdsmi import *

try:
    amdsmi_init()

    # amdsmi calls ...

except AmdSmiException as e:
    print(e)
finally:
    try:
        amdsmi_shut_down()
    except AmdSmiException as e:
        print(e)
```

To initialize amdsmi lib, amdsmi_init() must be called before all other calls to amdsmi lib.

To close connection to driver, amdsmi_shut_down() must be the last call.

## Exceptions

All exceptions are in `amdsmi_exception.py` file.
Exceptions that can be thrown are:

* `AmdSmiException`: base amdsmi exception class
* `AmdSmiLibraryException`: derives base `AmdSmiException` class and represents errors that can occur in amdsmi-lib.
When this exception is thrown, `err_code` and `err_info` are set. `err_code` is an integer that corresponds to errors that can occur
in amdsmi-lib and `err_info` is a string that explains the error that occurred.
Example:

```python
try:
    num_of_GPUs = len(amdsmi_get_processor_handles())
    if num_of_GPUs == 0:
        print("No GPUs on machine")
except AmdSmiException as e:
    print("Error code: {}".format(e.err_code))
    if e.err_code == amdsmi_wrapper.AMDSMI_STATUS_RETRY:
        print("Error info: {}".format(e.err_info))
```

* `AmdSmiRetryException` : Derives `AmdSmiLibraryException` class and signals device is busy and call should be retried.
* `AmdSmiTimeoutException` : Derives `AmdSmiLibraryException` class and represents that call had timed out.
* `AmdSmiParameterException`: Derives base `AmdSmiException` class and represents errors related to invaild parameters passed to functions. When this exception is thrown, err_msg is set and it explains what is the actual and expected type of the parameters.
* `AmdSmiBdfFormatException`: Derives base `AmdSmiException` class and represents invalid bdf format.

## API

### amdsmi_init

Description: Initialize amdsmi with AmdSmiInitFlags

Input parameters: AmdSmiInitFlags

Output: `None`

Exceptions that can be thrown by `amdsmi_init` function:

* `AmdSmiLibraryException`

Initialize GPUs only example:

```python
try:
    # by default we initalize with AmdSmiInitFlags.INIT_AMD_GPUS
    ret = amdsmi_init()
    # continue with amdsmi
except AmdSmiException as e:
    print("Init GPUs failed")
    print(e)
```

Initialize CPUs only example:

```python
try:
    ret = amdsmi_init(AmdSmiInitFlags.INIT_AMD_CPUS)
    # continue with amdsmi
except AmdSmiException as e:
    print("Init CPUs failed")
    print(e)
```

Initialize both GPUs and CPUs example:

```python
try:
    ret = amdsmi_init(AmdSmiInitFlags.INIT_AMD_APUS)
    # continue with amdsmi
except AmdSmiException as e:
    print("Init both GPUs & CPUs failed")
    print(e)
```

### amdsmi_shut_down

Description: Finalize and close connection to driver

Input parameters: `None`

Output: `None`

Exceptions that can be thrown by `amdsmi_shut_down` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    amdsmi_init()
    amdsmi_shut_down()
except AmdSmiException as e:
    print("Shut down failed")
    print(e)
```

### amdsmi_get_processor_type

Description: Checks the type of device with provided handle.

Input parameters: device handle as an instance of `amdsmi_processor_handle`

Output: Integer, type of gpu

Exceptions that can be thrown by `amdsmi_get_processor_type` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    type_of_GPU = amdsmi_get_processor_type(processor_handle)
    if type_of_GPU == 1:
        print("This is an AMD GPU")
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_processor_handles

Description: Returns list of GPU device handle objects on current machine

Input parameters: `None`

Output: List of GPU device handle objects

Exceptions that can be thrown by `amdsmi_get_processor_handles` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            print(amdsmi_get_gpu_device_uuid(device))
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_socket_handles

**Note: CURRENTLY HARDCODED TO RETURN DUMMY DATA**
Description: Returns list of socket device handle objects on current machine

Input parameters: `None`

Output: List of socket device handle objects

Exceptions that can be thrown by `amdsmi_get_socket_handles` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    sockets = amdsmi_get_socket_handles()
    print('Socket numbers: {}'.format(len(sockets)))
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_socket_info

**Note: CURRENTLY HARDCODED TO RETURN EMPTY VALUES**
Description: Return socket name

Input parameters:
`socket_handle` socket handle

Output: Socket name

Exceptions that can be thrown by `amdsmi_get_socket_info` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    socket_handles = amdsmi_get_socket_handles()
    if len(socket_handles) == 0:
        print("No sockets on machine")
    else:
        for socket in socket_handles:
            print(amdsmi_get_socket_info(socket))
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_processor_handle_from_bdf

Description: Returns device handle from the given BDF

Input parameters: bdf string in form of either `<domain>:<bus>:<device>.<function>` or `<bus>:<device>.<function>` in hexcode format.
Where:

* `<domain>` is 4 hex digits long from 0000-FFFF interval
* `<bus>` is 2 hex digits long from 00-FF interval
* `<device>` is 2 hex digits long from 00-1F interval
* `<function>` is 1 hex digit long from 0-7 interval

Output: device handle object

Exceptions that can be thrown by `amdsmi_get_processor_handle_from_bdf` function:

* `AmdSmiLibraryException`
* `AmdSmiBdfFormatException`

Example:

```python
try:
    device = amdsmi_get_processor_handle_from_bdf("0000:23:00.0")
    print(amdsmi_get_gpu_device_uuid(device))
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_device_bdf

Description: Returns BDF of the given device

Input parameters:

* `processor_handle` dev for which to query

Output: BDF string in form of `<domain>:<bus>:<device>.<function>` in hexcode format.
Where:

* `<domain>` is 4 hex digits long from 0000-FFFF interval
* `<bus>` is 2 hex digits long from 00-FF interval
* `<device>` is 2 hex digits long from 00-1F interval
* `<function>` is 1 hex digit long from 0-7 interval

Exceptions that can be thrown by `amdsmi_get_gpu_device_bdf` function:

* `AmdSmiParameterException`
* `AmdSmiLibraryException`

Example:

```python
try:
    device = amdsmi_get_processor_handles()[0]
    print("Device's bdf:", amdsmi_get_gpu_device_bdf(device))
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_device_uuid

Description: Returns the UUID of the device

Input parameters:

* `processor_handle` dev for which to query

Output: UUID string unique to the device

Exceptions that can be thrown by `amdsmi_get_gpu_device_uuid` function:

* `AmdSmiParameterException`
* `AmdSmiLibraryException`

Example:

```python
try:
    device = amdsmi_get_processor_handles()[0]
    print("Device UUID: ", amdsmi_get_gpu_device_uuid(device))
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_driver_info

Description: Returns the info of the driver

Input parameters:

* `processor_handle` dev for which to query

Output: Dictionary with fields

Field | Content
---|---
`driver_name` |  driver name
`driver_version` |  driver_version
`driver_date` |  driver_date

Exceptions that can be thrown by `amdsmi_get_gpu_driver_info` function:

* `AmdSmiParameterException`
* `AmdSmiLibraryException`

Example:

```python
try:
    device = amdsmi_get_processor_handles()[0]
    print("Driver info: ", amdsmi_get_gpu_driver_info(device))
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_asic_info

Description: Returns asic information for the given GPU

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with fields

Field | Content
---|---
`market_name` |  market name
`vendor_id` |  vendor id
`vendor_name` |  vendor name
`device_id` |  device id
`rev_id` |  revision id
`asic_serial` | asic serial
`oam_id` | oam id

Exceptions that can be thrown by `amdsmi_get_gpu_asic_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            asic_info = amdsmi_get_gpu_asic_info(device)
            print(asic_info['market_name'])
            print(hex(asic_info['vendor_id']))
            print(asic_info['vendor_name'])
            print(hex(asic_info['device_id']))
            print(hex(asic_info['rev_id']))
            print(asic_info['asic_serial'])
            print(asic_info['oam_id'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_power_cap_info

Description: Returns dictionary of power capabilities as currently configured
on the given GPU. It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description | Units
---|---|---
`power_cap` |  power capability | uW
`dpm_cap` |  dynamic power management capability | MHz
`default_power_cap` |  default power capability | uW
`min_power_cap` | min power capability | uW
`max_power_cap` | max power capability | uW

Exceptions that can be thrown by `amdsmi_get_power_cap_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            power_info = amdsmi_get_power_cap_info(device)
            print(power_info['power_cap'])
            print(power_info['dpm_cap'])
            print(power_info['default_power_cap'])
            print(power_info['min_power_cap'])
            print(power_info['max_power_cap'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_vram_info

Description: Returns dictionary of vram information for the given GPU.

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`vram_type` |  vram type
`vram_vendor` |  vram vendor
`vram_size` |  vram size in mb

Exceptions that can be thrown by `amdsmi_get_gpu_vram_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            vram_info = amdsmi_get_gpu_vram_info(device)
            print(vram_info['vram_type'])
            print(vram_info['vram_vendor'])
            print(vram_info['vram_size'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_cache_info

Description: Returns a list of dictionaries containing cache information for the given GPU.

Input parameters:

* `processor_handle` device which to query

Output: List of Dictionaries containing cache information following the schema below:
Schema:

```JSON
{
    cache_properties:
        {
            "type" : "array",
            "items" : {"type" : "string"}
        },
    cache_size: {"type" : "number"},
    cache_level: {"type" : "number"},
    max_num_cu_shared: {"type" : "number"},
    num_cache_instance: {"type" : "number"}
}
```

Field | Description
---|---
`cache_properties` | list of up to 4 cache property type strings. Ex. data ("DATA_CACHE"), instruction ("INST_CACHE"), CPU ("CPU_CACHE"), or SIMD ("SIMD_CACHE").
`cache_size` | size of cache in KB
`cache_level` | level of cache
`max_num_cu_shared` |  max number of compute units shared
`num_cache_instance` | number of cache instances

Exceptions that can be thrown by `amdsmi_get_gpu_cache_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            cache_info = amdsmi_get_gpu_cache_info(device)
            for cache_index, cache_values in cache_info.items():
                print(cache_values['cache_properties'])
                print(cache_values['cache_size'])
                print(cache_values['cache_level'])
                print(cache_values['max_num_cu_shared'])
                print(cache_values['num_cache_instance'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_vbios_info

Description:  Returns the static information for the VBIOS on the device.

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`name` | vbios name
`build_date` | vbios build date
`part_number` | vbios part number
`version` | vbios version string

Exceptions that can be thrown by `amdsmi_get_gpu_vbios_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            vbios_info = amdsmi_get_gpu_vbios_info(device)
            print(vbios_info['name'])
            print(vbios_info['build_date'])
            print(vbios_info['part_number'])
            print(vbios_info['version'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_fw_info

Description:  Returns GPU firmware related information.

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`fw_list` | List of dictionaries that contain information about a certain firmware block

Exceptions that can be thrown by `amdsmi_get_fw_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            firmware_list = amdsmi_get_fw_info(device)['fw_list']
            for firmware_block in firmware_list:
                print(firmware_block['fw_name'])
                # String formated hex or decimal value ie: 21.00.00.AC or 130
                print(firmware_block['fw_version'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_activity

Description: Returns the engine usage for the given GPU.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query

Output: Dictionary of activites to their respective usage percentage or 'N/A' if not supported

Field | Description
---|---
`gfx_activity` | graphics engine usage percentage (0 - 100)
`umc_activity` | memory engine usage percentage (0 - 100)
`mm_activity` | average multimedia engine usages in percentage (0 - 100)

Exceptions that can be thrown by `amdsmi_get_gpu_activity` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            engine_usage = amdsmi_get_gpu_activity(device)
            print(engine_usage['gfx_activity'])
            print(engine_usage['umc_activity'])
            print(engine_usage['mm_activity'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_power_info

Description: Returns the current power and voltage for the given GPU.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`current_socket_power` | current socket power
`average_socket_power` | average socket power
`gfx_voltage` | voltage gfx
`soc_voltage` | voltage soc
`mem_voltage` | voltage mem
`power_limit` | power limit

Exceptions that can be thrown by `amdsmi_get_power_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            power_measure = amdsmi_get_power_info(device)
            print(power_measure['current_socket_power'])
            print(power_measure['average_socket_power'])
            print(power_measure['gfx_voltage'])
            print(power_measure['soc_voltage'])
            print(power_measure['mem_voltage'])
            print(power_measure['power_limit'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_vram_usage

Description: Returns total VRAM and VRAM in use

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`vram_total` | VRAM total
`vram_used` | VRAM currently in use

Exceptions that can be thrown by `amdsmi_get_gpu_vram_usage` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            vram_usage = amdsmi_get_gpu_vram_usage(device)
            print(vram_usage['vram_used'])
            print(vram_usage['vram_total'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_clock_info

Description: Returns the clock measure for the given GPU.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query
* `clock_type` one of `AmdSmiClkType` enum values:

Field | Description
---|---
`SYS` | SYS clock type
`GFX` | GFX clock type
`DF` | DF clock type
`DCEF` | DCEF clock type
`SOC` | SOC clock type
`MEM` | MEM clock type
`PCIE` | PCIE clock type
`VCLK0` | VCLK0 clock type
`VCLK1` | VCLK1 clock type
`DCLK0` | DCLK0 clock type
`DCLK1` | DCLK1 clock type

Output: Dictionary with fields

Field | Description
---|---
`clk` | Current clock for given clock type
`min_clk` | Minimum clock for given clock type
`max_clk` | Maximum clock for given clock type
`clk_locked` | flag only supported on GFX clock domain
`clk_deep_sleep` | clock deep sleep mode flag

Exceptions that can be thrown by `amdsmi_get_clock_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            clock_measure = amdsmi_get_clock_info(device, AmdSmiClkType.GFX)
            print(clock_measure['clk'])
            print(clock_measure['min_clk'])
            print(clock_measure['max_clk'])
            print(clock_measure['clk_locked'])
            print(clock_measure['clk_deep_sleep'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_pcie_info

Description: Returns the pcie metric and static information for the given GPU.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with 2 fields `pcie_static` and `pcie_metric`

Fields | Description
---|---
`pcie_static` | <table><thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`max_pcie_width`</td><td>Maximum number of pcie lanes available</td></tr><tr><td>`max_pcie_speed`</td><td>Maximum capable pcie speed in GT/s</td></tr><tr><td>`pcie_interface_version`</td><td>PCIe generation ie. 3,4,5...</td></tr><tr><td>`slot_type`</td><td>The type of form factor of the slot: OAM, PCIE, CEM, or Unknown</td></tr></tbody></table>
`pcie_metric` | <table><thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`pcie_width`</td><td>Current number of pcie lanes available</td></tr><tr><td>`pcie_speed`</td><td>Current pcie speed capable in GT/s</td></tr><tr><td>`pcie_bandwidth`</td><td>Current instantaneous bandwidth usage in Mb/s</td></tr><tr><td>`pcie_replay_count`</td><td>Total number of PCIe replays (NAKs)</td></tr><tr><td>`pcie_l0_to_recovery_count`</td><td>PCIE L0 to recovery state transition accumulated count</td></tr><tr><td>`pcie_replay_roll_over_count`</td><td>PCIe Replay accumulated count</td></tr><tr><td>`pcie_nak_sent_count`</td><td>PCIe NAK sent accumulated count</td></tr><tr><td>`pcie_nak_received_count`</td><td>PCIe NAK received accumulated count</td></tr></tbody></table>

Exceptions that can be thrown by `amdsmi_get_pcie_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            pcie_info = amdsmi_get_pcie_info(device)
            print(pcie_info["pcie_static"])
            print(pcie_info["pcie_metric"])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_bad_page_info

Description:  Returns bad page info for the given GPU.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query

Output: List consisting of dictionaries with fields for each bad page found; can be an empty list

Field | Description
---|---
`value` | Value of page
`page_address` | Address of bad page
`page_size` | Size of bad page
`status` | Status of bad page

Exceptions that can be thrown by `amdsmi_get_gpu_bad_page_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            bad_page_info = amdsmi_get_gpu_bad_page_info(device)
            if not bad_page_info: # Can be empty list
                print("No bad pages found")
                continue
            for bad_page in bad_page_info:
                print(bad_page["value"])
                print(bad_page["page_address"])
                print(bad_page["page_size"])
                print(bad_page["status"])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_memory_reserved_pages

Description: Returns reserved memory page info for the given GPU.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query

Output: List consisting of dictionaries with fields for each reserved memory page found; can be an empty list

Field | Description
---|---
`value` | Value of memory reserved page
`page_address` | Address of memory reserved page
`page_size` | Size of memory reserved page
`status` | Status of memory reserved page

Exceptions that can be thrown by `amdsmi_get_gpu_memory_reserved_pages` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            reserved_memory_page_info = amdsmi_get_gpu_memory_reserved_pages(device)
            if not reserved_memory_page_info: # Can be empty list
                print("No memory reserved pages found")
                continue
            for reserved_memory_page in reserved_memory_page_info:
                print(reserved_memory_page["value"])
                print(reserved_memory_page["page_address"])
                print(reserved_memory_page["page_size"])
                print(reserved_memory_page["status"])
except AmdSmiException as e:
    print(e)
```


### amdsmi_get_gpu_process_list

Description: Returns the list of processes running on the target GPU; May require root level access

Input parameters:

* `processor_handle` device which to query

Output: List of Dictionaries with the corresponding fields; empty list if no running process are detected

Field | Description
---|---
`name` | Name of process
`pid` | Process ID
`mem` | Process memory usage
`engine_usage` | <table><thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`gfx`</td><td>GFX engine usage in ns</td></tr><tr><td>`enc`</td><td>Encode engine usage in ns</td></tr></tbody></table>
`memory_usage` | <table><thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`gtt_mem`</td><td>GTT memory usage</td></tr><tr><td>`cpu_mem`</td><td>CPU memory usage</td></tr><tr><td>`vram_mem`</td><td>VRAM memory usage</td></tr> </tbody></table>

Exceptions that can be thrown by `amdsmi_get_gpu_process_list` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            processes = amdsmi_get_gpu_process_list(device)
            if len(processes) == 0:
                print("No processes running on this GPU")
            else:
                for process in processes:
                    print(process)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_total_ecc_count

Description: Returns the ECC error count for the given GPU.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`correctable_count` | Correctable ECC error count
`uncorrectable_count` | Uncorrectable ECC error count
`deferred_count` | Deferred ECC error count

Exceptions that can be thrown by `amdsmi_get_gpu_total_ecc_count` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            ecc_error_count = amdsmi_get_gpu_total_ecc_count(device)
            print(ecc_error_count["correctable_count"])
            print(ecc_error_count["uncorrectable_count"])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_board_info

Description: Returns board info for the given GPU

Input parameters:

* `processor_handle` device which to query

Output:  Dictionary with fields correctable and uncorrectable

Field | Description
---|---
`model_number` | Board serial number
`product_serial` | Product serial
`fru_id` | FRU ID
`product_name` | Product name
`manufacturer_name` | Manufacturer name

Exceptions that can be thrown by `amdsmi_get_gpu_board_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    device = amdsmi_get_processor_handle_from_bdf("0000:23.00.0")
    board_info = amdsmi_get_gpu_board_info(device)
    print(board_info["model_number"])
    print(board_info["product_serial"])
    print(board_info["fru_id"])
    print(board_info["product_name"])
    print(board_info["manufacturer_name"])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_ras_feature_info

Description: Returns RAS version and schema information
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query

Output: List containing dictionaries with fields

Field | Description
---|---
`eeprom_version` | eeprom version
`parity_schema` | parity schema
`single_bit_schema` | single bit schema
`double_bit_schema` | double bit schema
`poison_schema` | poison schema

Exceptions that can be thrown by `amdsmi_get_gpu_ras_feature_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            ras_info = amdsmi_get_gpu_ras_feature_info(device)
            print(ras_info)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_ras_block_features_enabled

Description: Returns status of each RAS block for the given GPU.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query

Output: List containing dictionaries with fields for each RAS block

Field | Description
---|---
`block` | RAS block
`status` | RAS block status

Exceptions that can be thrown by `amdsmi_get_gpu_ras_block_features_enabled` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            ras_block_features = amdsmi_get_gpu_ras_block_features_enabled(device)
            print(ras_block_features)
except AmdSmiException as e:
    print(e)
```

### AmdSmiEventReader class

Description: Providing methods for event monitoring. This is context manager class.
Can be used with `with` statement for automatic cleanup.

Methods:

#### Constructor

Description: Allocates a new event reader notifier to monitor different types of events for the given GPU

Input parameters:

* `processor_handle` device handle corresponding to the device on which to listen for events
* `event_types` list of event types from AmdSmiEvtNotificationType enum. Specifying which events to collect for the given device.

Event Type | Description
---|------
`VMFAULT` | VM page fault
`THERMAL_THROTTLE` | thermal throttle
`GPU_PRE_RESET` | gpu pre reset
`GPU_POST_RESET` | gpu post reset
`RING_HANG` | ring hang event

#### read

Description: Reads events on the given device. When event is caught, device handle, message and event type are returned. Reading events stops when timestamp passes without event reading.

Input parameters:

* `timestamp` number of milliseconds to wait for an event to occur. If event does not happen monitoring is finished
* `num_elem` number of events. This is optional parameter. Default value is 10.

#### stop

Description: Any resources used by event notification for the the given device will be freed with this function. This can be used explicitly or
automatically using `with` statement, like in the examples below. This should be called either manually or automatically for every created AmdSmiEventReader object.

Input parameters: `None`

Example with manual cleanup of AmdSmiEventReader:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        event = AmdSmiEventReader(device[0], AmdSmiEvtNotificationType.GPU_PRE_RESET, AmdSmiEvtNotificationType.GPU_POST_RESET)
        event.read(10000)
except AmdSmiException as e:
    print(e)
finally:
    event.stop()
```

Example with automatic cleanup using `with` statement:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        with AmdSmiEventReader(device[0], AmdSmiEvtNotificationType.GPU_PRE_RESET, AmdSmiEvtNotificationType.GPU_POST_RESET) as event:
            event.read(10000)
except AmdSmiException as e:
    print(e)

```

### amdsmi_set_gpu_pci_bandwidth

Description: Control the set of allowed PCIe bandwidths that can be used
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `bw_bitmask` A bitmask indicating the indices of the bandwidths that are
to be enabled (1) and disabled (0)

Output: None

Exceptions that can be thrown by `amdsmi_set_gpu_pci_bandwidth` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_set_gpu_pci_bandwidth(device, 0)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_power_cap

Description: Set the power cap value. It is not supported on virtual machine
guest

Input parameters:

* `processor_handle` handle for the given device
* `sensor_ind` a 0-based sensor index. Normally, this will be 0. If a
device has more than one sensor, it could be greater than 0
* `cap` int that indicates the desired power cap, in microwatts

Output: None

Exceptions that can be thrown by `amdsmi_set_power_cap` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            power_cap = 250 * 1000000
             amdsmi_set_power_cap(device, 0, power_cap)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_gpu_power_profile

Description: Set the power profile. It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `reserved` Not currently used, set to 0
* `profile` a amdsmi_power_profile_preset_masks_t that hold the mask of
the desired new power profile

Output: None

Exceptions that can be thrown by `amdsmi_set_gpu_power_profile` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            profile = ...
             amdsmi_set_gpu_power_profile(device, 0, profile)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_gpu_clk_range

Description: This function sets the clock range information.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `min_clk_value` minimum clock value for desired clock range
* `max_clk_value` maximum clock value for desired clock range
* `clk_type`AMDSMI_CLK_TYPE_SYS | AMDSMI_CLK_TYPE_MEM range type

Output: None

Exceptions that can be thrown by `amdsmi_set_gpu_clk_range` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_set_gpu_clk_range(device, 0, 1000, AmdSmiClkType.AMDSMI_CLK_TYPE_SYS)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_bdf_id

Description: Get the unique PCI device identifier associated for a device

Input parameters:

* `processor_handle` device which to query

Output: device bdf
The format of bdfid will be as follows:

BDFID = ((DOMAIN & 0xffffffff) << 32) | ((BUS & 0xff) << 8) |
                       ((DEVICE & 0x1f) <<3 ) | (FUNCTION & 0x7)

| Name     | Field   |
---------- | ------- |
| Domain   | [64:32] |
| Reserved | [31:16] |
| Bus      | [15: 8] |
| Device   | [ 7: 3] |
| Function | [ 2: 0] |

Exceptions that can be thrown by `amdsmi_get_gpu_bdf_id` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            bdfid = amdsmi_get_gpu_bdf_id(device)
            print(bdfid)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_pci_bandwidth

Description: Get the list of possible PCIe bandwidths that are available.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with the possible T/s values and associated number of lanes

Field | Content
---|---
`transfer_rate` |  transfer_rate dictionary
`lanes` | lanes

transfer_rate dictionary

Field | Content
---|---
`num_supported` |  num_supported
`current` | current
`frequency` | list of frequency

Exceptions that can be thrown by `amdsmi_get_gpu_pci_bandwidth` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            bandwidth = amdsmi_get_gpu_pci_bandwidth(device)
            print(bandwidth)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_pci_throughput

Description: Get PCIe traffic information. It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with the fields

Field | Content
---|---
`sent` | number of bytes sent in 1 second
`received` | the number of bytes received
`max_pkt_sz` | maximum packet size

Exceptions that can be thrown by `amdsmi_get_gpu_pci_throughput` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            pci = amdsmi_get_gpu_pci_throughput(device)
            print(pci)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_pci_replay_counter

Description: Get PCIe replay counter

Input parameters:

* `processor_handle` device which to query

Output: counter value
The sum of the NAK's received and generated by the GPU

Exceptions that can be thrown by `amdsmi_get_gpu_pci_replay_counter` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            counter =  amdsmi_get_gpu_pci_replay_counter(device)
            print(counter)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_topo_numa_affinity

Description: Get the NUMA node associated with a device

Input parameters:

* `processor_handle` device which to query

Output: NUMA node value

Exceptions that can be thrown by `amdsmi_get_gpu_topo_numa_affinity` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            numa_node = amdsmi_get_gpu_topo_numa_affinity(device)
            print(numa_node)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_energy_count

Description: Get the energy accumulator counter of the device.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with fields

Field | Content
---|---
`power` |  power
`counter_resolution` |  counter resolution
`timestamp` |  timestamp

Exceptions that can be thrown by `amdsmi_get_energy_count` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            power = amdsmi_get_energy_count(device)
            print(power)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_memory_total

Description: Get the total amount of memory that exists

Input parameters:

* `processor_handle` device which to query
* `mem_type` enum AmdSmiMemoryType

Output: total amount of memory

Exceptions that can be thrown by `amdsmi_get_gpu_memory_total` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            vram_memory_total = amdsmi_get_gpu_memory_total(device, amdsmi_interface.AmdSmiMemoryType.VRAM)
            print(vram_memory_total)
            vis_vram_memory_total = amdsmi_get_gpu_memory_total(device, amdsmi_interface.AmdSmiMemoryType.VIS_VRAM)
            print(vis_vram_memory_total)
            gtt_memory_total = amdsmi_get_gpu_memory_total(device, amdsmi_interface.AmdSmiMemoryType.GTT)
            print(gtt_memory_total)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_gpu_od_clk_info

Description: This function sets the clock frequency information
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `level` AMDSMI_FREQ_IND_MIN|AMDSMI_FREQ_IND_MAX to set the minimum (0)
or maximum (1) speed
* `clk_value` value to apply to the clock range
* `clk_type` AMDSMI_CLK_TYPE_SYS | AMDSMI_CLK_TYPE_MEM range type

Output: None

Exceptions that can be thrown by `amdsmi_set_gpu_od_clk_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_set_gpu_od_clk_info(
                device,
                AmdSmiFreqInd.AMDSMI_FREQ_IND_MAX,
                1000,
                AmdSmiClkType.AMDSMI_CLK_TYPE_SYS
            )
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_memory_usage

Description: Get the current memory usage

Input parameters:

* `processor_handle` device which to query
* `mem_type` enum AmdSmiMemoryType

Output: the amount of memory currently being used

Exceptions that can be thrown by `amdsmi_get_gpu_memory_usage` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            vram_memory_usage = amdsmi_get_gpu_memory_usage(device, amdsmi_interface.AmdSmiMemoryType.VRAM)
            print(vram_memory_usage)
            vis_vram_memory_usage = amdsmi_get_gpu_memory_usage(device, amdsmi_interface.AmdSmiMemoryType.VIS_VRAM)
            print(vis_vram_memory_usage)
            gtt_memory_usage = amdsmi_get_gpu_memory_usage(device, amdsmi_interface.AmdSmiMemoryType.GTT)
            print(gtt_memory_usage)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_gpu_od_volt_info

Description: This function sets  1 of the 3 voltage curve points.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `vpoint` voltage point [0|1|2] on the voltage curve
* `clk_value` clock value component of voltage curve point
* `volt_value` voltage value component of voltage curve point

Output: None

Exceptions that can be thrown by `amdsmi_set_gpu_od_volt_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_set_gpu_od_volt_info(device, 1, 1000, 980)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_fan_rpms

Description: Get the fan speed in RPMs of the device with the specified device
handle and 0-based sensor index. It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `sensor_idx` a 0-based sensor index. Normally, this will be 0. If a device has
more than one sensor, it could be greater than 0.

Output: Fan speed in rpms as integer

Exceptions that can be thrown by `amdsmi_get_gpu_fan_rpms` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            fan_rpm = amdsmi_get_gpu_fan_rpms(device, 0)
            print(fan_rpm)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_fan_speed

Description: Get the fan speed for the specified device as a value relative to
AMDSMI_MAX_FAN_SPEED. It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `sensor_idx` a 0-based sensor index. Normally, this will be 0. If a device has
more than one sensor, it could be greater than 0.

Output: Fan speed in relative to MAX

Exceptions that can be thrown by `amdsmi_get_gpu_fan_speed` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            fan_speed = amdsmi_get_gpu_fan_speed(device, 0)
            print(fan_speed)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_fan_speed_max

Description: Get the max fan speed of the device with provided device handle.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `sensor_idx` a 0-based sensor index. Normally, this will be 0. If a device has
more than one sensor, it could be greater than 0.

Output: Max fan speed as integer

Exceptions that can be thrown by `amdsmi_get_gpu_fan_speed_max` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            max_fan_speed = amdsmi_get_gpu_fan_speed_max(device, 0)
            print(max_fan_speed)
except AmdSmiException as e:
    print(e)
```

### amdsmi_is_gpu_power_management_enabled

Description: Returns is power management enabled

Input parameters:

* `processor_handle` GPU device which to query

Output: Bool true if power management enabled else false

Exceptions that can be thrown by `amdsmi_is_gpu_power_management_enabled` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for processor in devices:
            is_power_management_enabled = amdsmi_is_gpu_power_management_enabled(processor)
            print(is_power_management_enabled)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_temp_metric

Description: Get the temperature metric value for the specified metric, from the
specified temperature sensor on the specified device. It is not supported on virtual
machine guest

Input parameters:

* `processor_handle` handle for the given device
* `sensor_type` part of device from which temperature should be obtained
* `metric` enum indicated which temperature value should be retrieved

Output: Temperature as integer in millidegrees Celcius

Exceptions that can be thrown by `amdsmi_get_temp_metric` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            temp_metric =  amdsmi_get_temp_metric(device, AmdSmiTemperatureType.EDGE,
                            AmdSmiTemperatureMetric.CURRENT)
            print(temp_metric)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_volt_metric

Description: Get the voltage metric value for the specified metric, from the
specified voltage sensor on the specified device. It is not supported on virtual
machine guest

Input parameters:

* `processor_handle` handle for the given device
* `sensor_type` part of device from which voltage should be obtained
* `metric` enum indicated which voltage value should be retrieved

Output: Voltage as integer in millivolts

Exceptions that can be thrown by `amdsmi_get_gpu_volt_metric` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            voltage =  amdsmi_get_gpu_volt_metric(device, AmdSmiVoltageType.VDDGFX,
                        AmdSmiVoltageMetric.AVERAGE)
            print(voltage)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_utilization_count

Description: Get coarse grain utilization counter of the specified device

Input parameters:

* `processor_handle` handle for the given device
* `counter_types` variable number of counter types desired

Output: List containing dictionaries with fields

Field | Description
---|---
`timestamp` | The timestamp when the counter is retreived - Resolution: 1 ns
`Dictionary for each counter` | <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`type`</td><td>Type of utilization counter</td></tr><tr><td>`value`</td><td>Value gotten for utilization counter</td></tr></tbody></table>

Exceptions that can be thrown by `amdsmi_get_utilization_count` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            utilization = amdsmi_get_utilization_count(
                            device,
                            AmdSmiUtilizationCounterType.COARSE_GRAIN_GFX_ACTIVITY
                            )
            print(utilization)
            utilization = amdsmi_get_utilization_count(
                            device,
                            AmdSmiUtilizationCounterType.COARSE_GRAIN_GFX_ACTIVITY,
                            AmdSmiUtilizationCounterType.COARSE_GRAIN_MEM_ACTIVITY
                            )
            print(utilization)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_perf_level

Description: Get the performance level of the device with provided device handle.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device

Output: Performance level as enum value of dev_perf_level_t

Exceptions that can be thrown by `amdsmi_get_gpu_perf_level` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            perf_level = amdsmi_get_gpu_perf_level(dev)
            print(perf_level)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_gpu_perf_determinism_mode

Description: Enter performance determinism mode with provided device handle.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `clkvalue` softmax value for GFXCLK in MHz

Output: None

Exceptions that can be thrown by `amdsmi_set_gpu_perf_determinism_mode` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_set_gpu_perf_determinism_mode(device, 1333)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_process_isolation

Description: Get the status of the Process Isolation

Input parameters:

* `processor_handle` handle for the given device

Output: integer corresponding to isolation_status; 0 - disabled, 1 - enabled

Exceptions that can be thrown by `amdsmi_get_gpu_process_isolation` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            isolate = amdsmi_get_gpu_process_isolation(device)
            print("Process Isolation Status: ", isolate)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_gpu_process_isolation
Description: Enable/disable the system Process Isolation for the given device handle.

Input parameters:

* `processor_handle` handle for the given device
* `pisolate` the process isolation status to set. 0 is the process isolation disabled, and 1 is the process isolation enabled.

Output: None

Exceptions that can be thrown by `amdsmi_set_gpu_process_isolation` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_set_gpu_process_isolation(device, 1)
except AmdSmiException as e:
    print(e)
```

### amdsmi_clean_gpu_local_data
Description: Clear the SRAM data of the given device. This can be called between user logins to prevent information leak.

Input parameters:

* `processor_handle` handle for the given device

Output: None

Exceptions that can be thrown by `amdsmi_clean_gpu_local_data` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_clean_gpu_local_data(device)
except AmdSmiException as e:
    print(e)
```


### amdsmi_get_gpu_overdrive_level

Description: Get the overdrive percent associated with the device with provided
device handle. It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device

Output: Overdrive percentage as integer

Exceptions that can be thrown by `amdsmi_get_gpu_overdrive_level` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            od_level = amdsmi_get_gpu_overdrive_level(dev)
            print(od_level)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_clk_freq

Description: Get the list of possible system clock speeds of device for a
specified clock type. It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `clk_type` the type of clock for which the frequency is desired

Output: Dictionary with fields

Field | Description
---|---
`num_supported` | The number of supported frequencies
`current` | The current frequency index
`frequency` | List of frequencies, only the first num_supported frequencies are valid

Exceptions that can be thrown by `amdsmi_get_clk_freq` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_get_clk_freq(device, AmdSmiClkType.SYS)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_od_volt_info

Description: This function retrieves the voltage/frequency curve information.
If the num_regions is 0 then the voltage curve is not supported.
It is not supported on virtual machine guest.

Input parameters:

* `processor_handle` handle for the given device

Output: Dictionary with fields

Field | Description
---|---
`curr_sclk_range` | <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound sclk range</td></tr><tr><td>`upper_bound`</td><td>upper bound sclk range</td></tr></tbody></table>
`curr_mclk_range` |  <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound mclk range</td></tr><tr><td>`upper_bound`</td><td>upper bound mclk range</td></tr></tbody></table>
`sclk_freq_limits` |  <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound sclk range limt</td></tr><tr><td>`upper_bound`</td><td>upper bound sclk range limit</td></tr></tbody></table>
`mclk_freq_limits` |  <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound mclk range limit</td></tr><tr><td>`upper_bound`</td><td>upper bound mclk range limit</td></tr></tbody></table>
`curve.vc_points` | List of voltage curve points
`num_regions` | The number of voltage curve regions

Exceptions that can be thrown by `amdsmi_get_gpu_od_volt_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_get_gpu_od_volt_info(dev)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_info

Description: This function retrieves the gpu metrics information. It is not
supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device

Output: Dictionary with fields

| Field | Description |Unit|
|-------|-------------|----|
`temperature_edge` | Edge temperature value | Celsius (C)
`temperature_hotspot` | Hotspot (aka junction) temperature value | Celsius (C)
`temperature_mem` | Memory temperature value | Celsius (C)
`temperature_vrgfx` | vrgfx temperature value | Celsius (C)
`temperature_vrsoc` | vrsoc temperature value | Celsius (C)
`temperature_vrmem` | vrmem temperature value | Celsius (C)
`average_gfx_activity` | Average gfx activity | %
`average_umc_activity` | Average umc (Universal Memory Controller) activity | %
`average_mm_activity` | Average mm (multimedia) engine activity | %
`average_socket_power` | Average socket power | W
`energy_accumulator` | Energy accumulated with a 15.3 uJ resolution over 1ns | uJ
`system_clock_counter` | System clock counter | ns
`average_gfxclk_frequency` | Average gfx clock frequency | MHz
`average_socclk_frequency` | Average soc clock frequency | MHz
`average_uclk_frequency` | Average uclk frequency | MHz
`average_vclk0_frequency` | Average vclk0 frequency | MHz
`average_dclk0_frequency` | Average dclk0 frequency | MHz
`average_vclk1_frequency` | Average vclk1 frequency | MHz
`average_dclk1_frequency` | Average dclk1 frequency | MHz
`current_gfxclk` | Current gfx clock | MHz
`current_socclk` | Current soc clock | MHz
`current_uclk` | Current uclk | MHz
`current_vclk0` | Current vclk0 | MHz
`current_dclk0` | Current dclk0 | MHz
`current_vclk1` | Current vclk1 | MHz
`current_dclk1` | Current dclk1 | MHz
`throttle_status` | Current throttle status | bool
`current_fan_speed` | Current fan speed | RPM
`pcie_link_width` | PCIe link width (number of lanes) | lanes
`pcie_link_speed` | PCIe link speed in 0.1 GT/s (Giga Transfers per second) | GT/s
`padding` | padding
`gfx_activity_acc` | gfx activity accumulated | %
`mem_activity_acc` | Memory activity accumulated | %
`temperature_hbm` | list of hbm temperatures | Celsius (C)
`firmware_timestamp` | timestamp from PMFW (10ns resolution) | ns
`voltage_soc` | soc voltage | mV
`voltage_gfx` | gfx voltage | mV
`voltage_mem` | mem voltage | mV
`indep_throttle_status` | ASIC independent throttle status (see drivers/gpu/drm/amd/pm/swsmu/inc/amdgpu_smu.h for bit flags) |
`current_socket_power` | Current socket power (also known as instant socket power) | W
`vcn_activity` | List of VCN encode/decode engine utilization per AID | %
`gfxclk_lock_status` | Clock lock status. Bits 0:7 correspond to each gfx clock engine instance. Bits 0:5 for APU/AID devices |
`xgmi_link_width` | XGMI bus width | lanes
`xgmi_link_speed` | XGMI bitrate | GB/s
`pcie_bandwidth_acc` | PCIe accumulated bandwidth | GB/s
`pcie_bandwidth_inst` | PCIe instantaneous bandwidth | GB/s
`pcie_l0_to_recov_count_acc` | PCIe L0 to recovery state transition accumulated count |
`pcie_replay_count_acc` | PCIe replay accumulated count |
`pcie_replay_rover_count_acc` | PCIe replay rollover accumulated count |
`xgmi_read_data_acc` | XGMI accumulated read data transfer size (KiloBytes) | KB
`xgmi_write_data_acc` | XGMI accumulated write data transfer size (KiloBytes) | KB
`current_gfxclks` | List of current gfx clock frequencies | MHz
`current_socclks` | List of current soc clock frequencies | MHz
`current_vclk0s` | List of current v0 clock frequencies | MHz
`current_dclk0s` | List of current d0 clock frequencies | MHz
`pcie_nak_sent_count_acc` | PCIe NAC sent count accumulated |
`pcie_nak_rcvd_count_acc` | PCIe NAC received count accumulated |
`jpeg_activity` | List of JPEG engine activity | %

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_get_gpu_metrics_info(dev)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_od_volt_curve_regions

Description: This function will retrieve the current valid regions in the
frequency/voltage space. It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `num_regions` number of freq volt regions

Output: List containing a dictionary with fields for each freq volt region

Field | Description
---|---
`freq_range` | <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound freq range</td></tr><tr><td>`upper_bound`</td><td>upper bound freq range</td></tr></tbody></table>
`volt_range` |  <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound volt range</td></tr><tr><td>`upper_bound`</td><td>upper bound volt range</td></tr></tbody></table>

Exceptions that can be thrown by `amdsmi_get_gpu_od_volt_curve_regions` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_get_gpu_od_volt_curve_regions(device, 3)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_power_profile_presets

Description:  Get the list of available preset power profiles and an indication of
which profile is currently active. It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `sensor_idx` number of freq volt regions

Output: Dictionary with fields

Field | Description
---|---
`available_profiles` | Which profiles are supported by this system
`current` | Which power profile is currently active
`num_profiles` | How many power profiles are available

Exceptions that can be thrown by `amdsmi_get_gpu_power_profile_presets` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_get_gpu_power_profile_presets(device, 0)
except AmdSmiException as e:
    print(e)
```

### amdsmi_gpu_counter_group_supported

Description: Tell if an event group is supported by a given device.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query
* `event_group` event group being checked for support

Output: None

Exceptions that can be thrown by `amdsmi_gpu_counter_group_supported` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_gpu_counter_group_supported(device, AmdSmiEventGroup.XGMI)
except AmdSmiException as e:
    print(e)
```

### amdsmi_gpu_create_counter

Description: Creates a performance counter object

Input parameters:

* `processor_handle` device which to query
* `event_type` event group being checked for support

Output: An event handle of the newly created performance counter object

Exceptions that can be thrown by `amdsmi_gpu_create_counter` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            event_handle = amdsmi_gpu_create_counter(device, AmdSmiEventGroup.XGMI)
except AmdSmiException as e:
    print(e)
```

### amdsmi_gpu_destroy_counter

Description: Destroys a performance counter object

Input parameters:

* `event_handle` event handle of the performance counter object

Output: None

Exceptions that can be thrown by `amdsmi_gpu_destroy_counter` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            event_handle = amdsmi_gpu_create_counter(device, AmdSmiEventGroup.XGMI)
            amdsmi_gpu_destroy_counter(event_handle)
except AmdSmiException as e:
    print(e)
```

### amdsmi_gpu_control_counter

Description: Issue performance counter control commands. It is not supported
on virtual machine guest

Input parameters:

* `event_handle` event handle of the performance counter object
* `counter_command` command being passed to counter as AmdSmiCounterCommand

Output: None

Exceptions that can be thrown by `amdsmi_gpu_control_counter` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            event_handle = amdsmi_gpu_create_counter(device, AmdSmiEventType.XGMI_1_REQUEST_TX)
            amdsmi_gpu_control_counter(event_handle, AmdSmiCounterCommand.CMD_START)
except AmdSmiException as e:
    print(e)
```

### amdsmi_gpu_read_counter

Description: Read the current value of a performance counter

Input parameters:

* `event_handle` event handle of the performance counter object

Output: Dictionary with fields

Field | Description
---|---
`value` | Counter value
`time_enabled` | Time that the counter was enabled in nanoseconds
`time_running` | Time that the counter was running in nanoseconds

Exceptions that can be thrown by `amdsmi_gpu_read_counter` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            event_handle = amdsmi_gpu_create_counter(device, AmdSmiEventType.XGMI_1_REQUEST_TX)
            amdsmi_gpu_read_counter(event_handle)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_available_counters

Description: Get the number of currently available counters. It is not supported
on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `event_group` event group being checked as AmdSmiEventGroup

Output: Number of available counters for the given device of the inputted event group

Exceptions that can be thrown by `amdsmi_get_gpu_available_counters` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            available_counters =  amdsmi_get_gpu_available_counters(device, AmdSmiEventGroup.XGMI)
            print(available_counters)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_gpu_perf_level

Description: Set a desired performance level for given device. It is not
supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `perf_level` performance level being set as AmdSmiDevPerfLevel

Output: None

Exceptions that can be thrown by `amdsmi_set_gpu_perf_level` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_set_gpu_perf_level(device, AmdSmiDevPerfLevel.STABLE_PEAK)
except AmdSmiException as e:
    print(e)
```

### amdsmi_reset_gpu

Description: Reset the gpu associated with the device with provided device handle
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device

Output: None

Exceptions that can be thrown by `amdsmi_reset_gpu` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_reset_gpu(device)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_gpu_fan_speed

Description: Set the fan speed for the specified device with the provided speed,
in RPMs. It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `sensor_idx` sensor index as integer
* `fan_speed` the speed to which the function will attempt to set the fan

Output: None

Exceptions that can be thrown by `amdsmi_set_gpu_fan_speed` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_set_gpu_fan_speed(device, 0, 1333)
except AmdSmiException as e:
    print(e)
```

### amdsmi_reset_gpu_fan

Description: Reset the fan to automatic driver control. It is not
supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `sensor_idx` sensor index as integer

Output: None

Exceptions that can be thrown by `amdsmi_reset_gpu_fan` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_reset_gpu_fan(device, 0)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_clk_freq

Description: Control the set of allowed frequencies that can be used for the
specified clock. It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `clk_type` the type of clock for which the set of frequencies will be modified
as AmdSmiClkType
* `freq_bitmask`  bitmask indicating the indices of the frequencies that are to
be enabled (1) and disabled (0). Only the lowest ::amdsmi_frequencies_t.num_supported
bits of this mask are relevant.

Output: None

Exceptions that can be thrown by `amdsmi_set_clk_freq` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            freq_bitmask = 0
             amdsmi_set_clk_freq(device, AmdSmiClkType.GFX, freq_bitmask)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_soc_pstate

Description: Get dpm policy information.

Input parameters:

* `processor_handle` handle for the given device
* `policy_id` the policy id to set.

Output: Dictionary with fields

Field | Description
---|---
`num_supported` | total number of supported policies
`current_id` | current policy id
`policies` | list of dictionaries containing possible policies

Exceptions that can be thrown by `amdsmi_get_soc_pstate` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            dpm_policies = amdsmi_get_soc_pstate(device)
            print(dpm_policies)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_soc_pstate

Description: Set the dpm policy to corresponding policy_id. Typically following: 0(default),1,2,3

Input parameters:

* `processor_handle` handle for the given device
* `policy_id` the policy id to set.

Output: None

Exceptions that can be thrown by `amdsmi_set_soc_pstate` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_set_soc_pstate(device, 0)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_xgmi_plpd

Description: Set the xgmi per-link power down policy parameter for the processor

Input parameters:

* `processor_handle` handle for the given device
* `policy_id` the xgmi plpd id to set.

Output: None

Exceptions that can be thrown by `amdsmi_set_xgmi_plpd` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_set_xgmi_plpd(device, 0)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_xgmi_plpd

Description: Get the xgmi per-link power down policy parameter for the processor

Input parameters:

* `processor_handle` handle for the given device

Output: Dict containing information about xgmi per-link power down policy

Field | Description
---|---
`num_supported` | The number of supported policies
`current_id` | The current policy index
`plpds` | List of policies.

Exceptions that can be thrown by `amdsmi_get_xgmi_plpd` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            xgmi_plpd =  amdsmi_get_xgmi_plpd(device)
            print(xgmi_plpd)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_gpu_overdrive_level

Description: **deprecated** Set the overdrive percent associated with the
device with provided device handle with the provided value. It is not
supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `overdrive_value` value to which the overdrive level should be set

Output: None

Exceptions that can be thrown by `amdsmi_set_gpu_overdrive_level` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_set_gpu_overdrive_level(device, 0)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_ecc_count

Description: Retrieve the error counts for a GPU block. It is not supported
on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `block` The block for which error counts should be retrieved

Output: Dict containing information about error counts

Field | Description
---|---
`correctable_count` | Count of correctable errors
`uncorrectable_count` | Count of uncorrectable errors
`deferred_count` | Count of deferred errors

Exceptions that can be thrown by `amdsmi_get_gpu_ecc_count` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            ecc_count =  amdsmi_get_gpu_ecc_count(device, AmdSmiGpuBlock.UMC)
            print(ecc_count)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_ecc_enabled

Description: Retrieve the enabled ECC bit-mask. It is not supported on virtual
machine guest

Input parameters:

* `processor_handle` handle for the given device

Output: Enabled ECC bit-mask

Exceptions that can be thrown by `amdsmi_get_gpu_ecc_enabled` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            enabled =  amdsmi_get_gpu_ecc_enabled(device)
            print(enabled)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_ecc_status

Description: Retrieve the ECC status for a GPU block. It is not supported
on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device
* `block` The block for which ECC status should be retrieved

Output: ECC status for a requested GPU block

Exceptions that can be thrown by `amdsmi_get_gpu_ecc_status` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            status =  amdsmi_get_gpu_ecc_status(device, AmdSmiGpuBlock.UMC)
            print(status)
except AmdSmiException as e:
    print(e)
```

### amdsmi_status_code_to_string

Description: Get a description of a provided AMDSMI error status

Input parameters:

* `status` The error status for which a description is desired

Output: String description of the provided error code

Exceptions that can be thrown by `amdsmi_status_code_to_string` function:

* `AmdSmiParameterException`

Example:

```python
try:
    status_str = amdsmi_status_code_to_string(ctypes.c_uint32(0))
    print(status_str)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_compute_process_info

Description: Get process information about processes currently using GPU

Input parameters: None

Output: List of python dicts each containing a process information

Field | Description
---|---
`process_id` | Process ID
`pasid` | PASID
`vram_usage` | VRAM usage
`sdma_usage` | SDMA usage in microseconds
`cu_occupancy` | Compute Unit usage in percents

Exceptions that can be thrown by `amdsmi_get_gpu_compute_process_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`

Example:

```python
try:
    procs = amdsmi_get_gpu_compute_process_info()
    for proc in procs:
        print(proc)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_compute_process_info_by_pid

Description: Get process information about processes currently using GPU

Input parameters:

* `pid` The process ID for which process information is being requested

Output: Dict containing a process information

Field | Description
---|---
`process_id` | Process ID
`pasid` | PASID
`vram_usage` | VRAM usage
`sdma_usage` | SDMA usage in microseconds
`cu_occupancy` | Compute Unit usage in percents

Exceptions that can be thrown by `amdsmi_get_gpu_compute_process_info_by_pid` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    pid = 0 # << valid pid here
    proc = amdsmi_get_gpu_compute_process_info_by_pid(pid)
    print(proc)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_compute_process_gpus

Description: Get the device indices currently being used by a process

Input parameters:

* `pid` The process id of the process for which the number of gpus currently being used is requested

Output: List of indices of devices currently being used by the process

Exceptions that can be thrown by `amdsmi_get_gpu_compute_process_gpus` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    pid = 0 # << valid pid here
    indices = amdsmi_get_gpu_compute_process_gpus(pid)
    print(indices)
except AmdSmiException as e:
    print(e)
```

### amdsmi_gpu_xgmi_error_status

Description: Retrieve the XGMI error status for a device. It is not supported on
virtual machine guest

Input parameters:

* `processor_handle` handle for the given device

Output: XGMI error status for a requested device

Exceptions that can be thrown by `amdsmi_gpu_xgmi_error_status` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            status = amdsmi_gpu_xgmi_error_status(device)
            print(status)
except AmdSmiException as e:
    print(e)
```

### amdsmi_reset_gpu_xgmi_error

Description: Reset the XGMI error status for a device. It is not supported
on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device

Output: None

Exceptions that can be thrown by `amdsmi_reset_gpu_xgmi_error` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_reset_gpu_xgmi_error(device)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_vendor_name

Description: Returns the device vendor name

Input parameters:

* `processor_handle` device which to query

Output: device vendor name

Exceptions that can be thrown by `amdsmi_get_gpu_vendor_name` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            vendor_name = amdsmi_get_gpu_vendor_name(device)
            print(vendor_name)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_id

Description: Get the device id associated with the device with provided device handler

Input parameters:

* `processor_handle` device which to query

Output: device id

Exceptions that can be thrown by `amdsmi_get_gpu_id` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            dev_id = amdsmi_get_gpu_id(device)
            print(dev_id)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_vram_vendor

Description: Get the vram vendor string of a gpu device.

Input parameters:

* `processor_handle` device which to query

Output: vram vendor

Exceptions that can be thrown by `amdsmi_get_gpu_vram_vendor` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            vram_vendor = amdsmi_get_gpu_vram_vendor(device)
            print(vram_vendor)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_subsystem_id

Description: Get the subsystem device id associated with the device with provided device handle.

Input parameters:

* `processor_handle` device which to query

Output: subsystem device id

Exceptions that can be thrown by `amdsmi_get_gpu_subsystem_id` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            id = amdsmi_get_gpu_subsystem_id(device)
            print(id)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_subsystem_name

Description: Get the name string for the device subsytem

Input parameters:

* `processor_handle` device which to query

Output: device subsytem

Exceptions that can be thrown by `amdsmi_get_gpu_subsystem_name` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            subsystem_nam = amdsmi_get_gpu_subsystem_name(device)
            print(subsystem_nam)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_lib_version

Description: Get the build version information for the currently running build of AMDSMI.

Output: amdsmi build version

Exceptions that can be thrown by `amdsmi_get_lib_version` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    version = amdsmi_get_lib_version()
    print(version)
except AmdSmiException as e:
    print(e)
```

### amdsmi_topo_get_numa_node_number

Description: Retrieve the NUMA CPU node number for a device

Input parameters:

* `processor_handle` device which to query

Output: node number of NUMA CPU for the device

Exceptions that can be thrown by `amdsmi_topo_get_numa_node_number` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            node_number = amdsmi_topo_get_numa_node_number()
            print(node_number)
except AmdSmiException as e:
    print(e)
```

### amdsmi_topo_get_link_weight

Description: Retrieve the weight for a connection between 2 GPUs.

Input parameters:

* `processor_handle_src` the source device handle
* `processor_handle_dest` the destination device handle

Output: the weight for a connection between 2 GPUs

Exceptions that can be thrown by `amdsmi_topo_get_link_weight` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        processor_handle_src = devices[0]
        processor_handle_dest = devices[1]
        weight = amdsmi_topo_get_link_weight(processor_handle_src, processor_handle_dest)
        print(weight)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_minmax_bandwidth_between_processors

Description: Retreive minimal and maximal io link bandwidth between 2 GPUs.

Input parameters:

* `processor_handle_src` the source device handle
* `processor_handle_dest` the destination device handle

Output:  Dictionary with fields:

Field | Description
---|---
`min_bandwidth` | minimal bandwidth for the connection
`max_bandwidth` | maximal bandwidth for the connection

Exceptions that can be thrown by `amdsmi_get_minmax_bandwidth_between_processors` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        processor_handle_src = devices[0]
        processor_handle_dest = devices[1]
        bandwidth =  amdsmi_get_minmax_bandwidth_between_processors(processor_handle_src, processor_handle_dest)
        print(bandwidth['min_bandwidth'])
        print(bandwidth['max_bandwidth'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_topo_get_link_type

Description: Retrieve the hops and the connection type between 2 GPUs

Input parameters:

* `processor_handle_src` the source device handle
* `processor_handle_dest` the destination device handle

Output:  Dictionary with fields:

Field | Description
---|---
`hops` | number of hops
`type` | the connection type

Exceptions that can be thrown by `amdsmi_topo_get_link_type` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        processor_handle_src = devices[0]
        processor_handle_dest = devices[1]
        link_type = amdsmi_topo_get_link_type(processor_handle_src, processor_handle_dest)
        print(link_type['hops'])
        print(link_type['type'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_is_P2P_accessible

Description: Return P2P availability status between 2 GPUs

Input parameters:

* `processor_handle_src` the source device handle
* `processor_handle_dest` the destination device handle

Output: P2P availability status between 2 GPUs

Exceptions that can be thrown by `amdsmi_is_P2P_accessible` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        processor_handle_src = devices[0]
        processor_handle_dest = devices[1]
        accessible = amdsmi_is_P2P_accessible(processor_handle_src, processor_handle_dest)
        print(accessible)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_compute_partition

Description: Get the compute partition from the given GPU

Input parameters:

* `processor_handle` the device handle

Output: String of the partition type

Exceptions that can be thrown by `amdsmi_get_gpu_compute_partition` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            compute_partition_type = amdsmi_get_gpu_compute_partition(device)
            print(compute_partition_type)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_gpu_compute_partition

Description: Set the compute partition to the given GPU

Input parameters:

* `processor_handle` the device handle
* `compute_partition` the type of compute_partition to set

Output: String of the partition type

Exceptions that can be thrown by `amdsmi_set_gpu_compute_partition` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    compute_partition = AmdSmiComputePartitionType.SPX
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_set_gpu_compute_partition(device, compute_partition)
except AmdSmiException as e:
    print(e)
```

### amdsmi_reset_gpu_compute_partition

Description: Reset the compute partitioning on the given GPU

Input parameters:

* `processor_handle` the device handle

Output: String of the partition type

Exceptions that can be thrown by `amdsmi_reset_gpu_compute_partition` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_reset_gpu_compute_partition(device)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_memory_partition

Description: Get the memory partition from the given GPU

Input parameters:

* `processor_handle` the device handle

Output: String of the partition type

Exceptions that can be thrown by `amdsmi_get_gpu_memory_partition` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            memory_partition_type = amdsmi_get_gpu_memory_partition(device)
            print(memory_partition_type)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_gpu_memory_partition

Description: Set the memory partition to the given GPU

Input parameters:

* `processor_handle` the device handle
* `memory_partition` the type of memory_partition to set

Output: String of the partition type

Exceptions that can be thrown by `amdsmi_set_gpu_memory_partition` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    memory_partition = AmdSmiMemoryPartitionType.NPS1
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_set_gpu_memory_partition(device, memory_partition)
except AmdSmiException as e:
    print(e)
```

### amdsmi_reset_gpu_memory_partition

Description: Reset the memory partitioning on the given GPU

Input parameters:

* `processor_handle` the device handle

Output: String of the partition type

Exceptions that can be thrown by `amdsmi_reset_gpu_memory_partition` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_reset_gpu_memory_partition(device)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_xgmi_info

Description: Returns XGMI information for the GPU.

Input parameters:

* `processor_handle`  device handle

Output:  Dictionary with fields:

Field | Description
---|---
`xgmi_lanes` |  xgmi lanes
`xgmi_hive_id` | xgmi hive id
`xgmi_node_id` | xgmi node id
`index` | index

Exceptions that can be thrown by `amdsmi_get_xgmi_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            xgmi_info = amdsmi_get_xgmi_info(device)
            print(xgmi_info['xgmi_lanes'])
            print(xgmi_info['xgmi_hive_id'])
            print(xgmi_info['xgmi_node_id'])
            print(xgmi_info['index'])
except AmdSmiException as e:
    print(e)
```

## CPU APIs

### amdsmi_get_processor_info

**Note: CURRENTLY HARDCODED TO RETURN EMPTY VALUES**
Description: Return processor name

Input parameters:
`processor_handle` processor handle

Output: Processor name

Exceptions that can be thrown by `amdsmi_get_processor_info` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_processor_handles()
    if len(processor_handles) == 0:
        print("No processors on machine")
    else:
        for processor in processor_handles:
            print(amdsmi_get_processor_info(processor))
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_hsmp_proto_ver

Description: Get the hsmp protocol version.

Output: amdsmi hsmp protocol version

Exceptions that can be thrown by `amdsmi_get_cpu_hsmp_proto_ver` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            version = amdsmi_get_cpu_hsmp_proto_ver(processor)
            print(version)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_smu_fw_version

Description: Get the SMU Firmware version.

Output: amdsmi SMU Firmware version

Exceptions that can be thrown by `amdsmi_get_cpu_smu_fw_version` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            version = amdsmi_get_cpu_smu_fw_version(processor)
            print(version['debug'])
            print(version['minor'])
            print(version['major'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_prochot_status

Description: Get the CPU's prochot status.

Output: amdsmi cpu prochot status

Exceptions that can be thrown by `amdsmi_get_cpu_prochot_status` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            prochot = amdsmi_get_cpu_prochot_status(processor)
            print(prochot)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_fclk_mclk

Description: Get the Data fabric clock and Memory clock in MHz.

Output: amdsmi data fabric clock and memory clock

Exceptions that can be thrown by `amdsmi_get_cpu_fclk_mclk` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            clk = amdsmi_get_cpu_fclk_mclk(processor)
            for fclk, mclk in clk.items():
                print(fclk)
                print(mclk)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_cclk_limit

Description: Get the core clock in MHz.

Output: amdsmi core clock

Exceptions that can be thrown by `amdsmi_get_cpu_cclk_limit` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            cclk_limit = amdsmi_get_cpu_cclk_limit(processor)
            print(cclk_limit)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_socket_current_active_freq_limit

Description: Get current active frequency limit of the socket.

Output: amdsmi frequency value in MHz and frequency source name

Exceptions that can be thrown by `amdsmi_get_cpu_socket_current_active_freq_limit` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            freq_limit = amdsmi_get_cpu_socket_current_active_freq_limit(processor)
            for freq, src in freq_limit.items():
                print(freq)
                print(src)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_socket_freq_range

Description: Get socket frequency range

Output: amdsmi maximum frequency and minimum frequency

Exceptions that can be thrown by `amdsmi_get_cpu_socket_freq_range` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            freq_range = amdsmi_get_cpu_socket_freq_range(processor)
            for fmax, fmin in freq_range.items():
                print(fmax)
                print(fmin)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_core_current_freq_limit

Description: Get socket frequency limit of the core

Output: amdsmi frequency

Exceptions that can be thrown by `amdsmi_get_cpu_core_current_freq_limit` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpucore_handles()
    if len(processor_handles) == 0:
        print("No CPU cores on machine")
    else:
        for processor in processor_handles:
            freq_limit = amdsmi_get_cpu_core_current_freq_limit(processor)
            print(freq_limit)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_socket_power

Description: Get the socket power.

Output: amdsmi socket power

Exceptions that can be thrown by `amdsmi_get_cpu_socket_power` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            sock_power = amdsmi_get_cpu_socket_power(processor)
            print(sock_power)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_socket_power_cap

Description: Get the socket power cap.

Output: amdsmi socket power cap

Exceptions that can be thrown by `amdsmi_get_cpu_socket_power_cap` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            sock_power = amdsmi_get_cpu_socket_power_cap(processor)
            print(sock_power)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_socket_power_cap_max

Description: Get the socket power cap max.

Output: amdsmi socket power cap max

Exceptions that can be thrown by `amdsmi_get_cpu_socket_power_cap_max` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            sock_power = amdsmi_get_cpu_socket_power_cap_max(processor)
            print(sock_power)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_pwr_svi_telemetry_all_rails

Description: Get the SVI based power telemetry for all rails.

Output: amdsmi svi based power value

Exceptions that can be thrown by `amdsmi_get_cpu_pwr_svi_telemetry_all_rails` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            power = amdsmi_get_cpu_pwr_svi_telemetry_all_rails(processor)
            print(power)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_cpu_socket_power_cap

Description: Set the power cap value for a given socket.

Input: amdsmi socket power cap value

Exceptions that can be thrown by `amdsmi_set_cpu_socket_power_cap` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            power = amdsmi_set_cpu_socket_power_cap(processor, 1000)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_cpu_pwr_efficiency_mode

Description: Set the power efficiency profile policy.

Input: mode(0, 1, or 2)

Exceptions that can be thrown by `amdsmi_set_cpu_pwr_efficiency_mode` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            policy = amdsmi_set_cpu_pwr_efficiency_mode(processor, 0)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_core_boostlimit

Description: Get boost limit of the cpu core

Output: amdsmi frequency

Exceptions that can be thrown by `amdsmi_get_cpu_core_boostlimit` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpucore_handles()
    if len(processor_handles) == 0:
        print("No CPU cores on machine")
    else:
        for processor in processor_handles:
            boost_limit = amdsmi_get_cpu_core_boostlimit(processor)
            print(boost_limit)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_socket_c0_residency

Description: Get the cpu socket C0 residency.

Output: amdsmi C0 residency value

Exceptions that can be thrown by `amdsmi_get_cpu_socket_c0_residency` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            c0_residency = amdsmi_get_cpu_socket_c0_residency(processor)
            print(c0_residency)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_cpu_core_boostlimit

Description: Set the cpu core boost limit.

Output: amdsmi boostlimit value

Exceptions that can be thrown by `amdsmi_set_cpu_core_boostlimit` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpucore_handles()
    if len(processor_handles) == 0:
        print("No CPU cores on machine")
    else:
        for processor in processor_handles:
            boost_limit = amdsmi_set_cpu_core_boostlimit(processor, 1000)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_cpu_socket_boostlimit

Description: Set the cpu socket boost limit.

Input: amdsmi boostlimit value

Exceptions that can be thrown by `amdsmi_set_cpu_socket_boostlimit` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            boost_limit = amdsmi_set_cpu_socket_boostlimit(processor, 1000)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_ddr_bw

Description: Get the CPU DDR Bandwidth.

Output: amdsmi ddr bandwidth data

Exceptions that can be thrown by `amdsmi_get_cpu_ddr_bw` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            ddr_bw = amdsmi_get_cpu_ddr_bw(processor)
            print(ddr_bw['max_bw'])
            print(ddr_bw['utilized_bw'])
            print(ddr_bw['utilized_pct'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_socket_temperature

Description: Get the socket temperature.

Output: amdsmi temperature value

Exceptions that can be thrown by `amdsmi_get_cpu_socket_temperature` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            ptmon = amdsmi_get_cpu_socket_temperature(processor)
            print(ptmon)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_dimm_temp_range_and_refresh_rate

Description: Get DIMM temperature range and refresh rate.

Output: amdsmi dimm metric data

Exceptions that can be thrown by `amdsmi_get_cpu_dimm_temp_range_and_refresh_rate` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            dimm = amdsmi_get_cpu_dimm_temp_range_and_refresh_rate(processor)
            print(dimm['range'])
            print(dimm['ref_rate'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_dimm_power_consumption

Description: amdsmi_get_cpu_dimm_power_consumption.

Output: amdsmi dimm power consumption value

Exceptions that can be thrown by `amdsmi_get_cpu_dimm_power_consumption` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            dimm = amdsmi_get_cpu_dimm_power_consumption(processor)
            print(dimm['power'])
            print(dimm['update_rate'])
            print(dimm['dimm_addr'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_dimm_thermal_sensor

Description: Get DIMM thermal sensor value.

Output: amdsmi dimm temperature data

Exceptions that can be thrown by `amdsmi_get_cpu_dimm_thermal_sensor` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            dimm = amdsmi_get_cpu_dimm_thermal_sensor(processor)
            print(dimm['sensor'])
            print(dimm['update_rate'])
            print(dimm['dimm_addr'])
            print(dimm['temp'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_cpu_xgmi_width

Description:  Set xgmi width.

Input: amdsmi xgmi width

Exceptions that can be thrown by `amdsmi_set_cpu_xgmi_width` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            xgmi_width = amdsmi_set_cpu_xgmi_width(processor, 0, 100)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_cpu_gmi3_link_width_range

Description:  Set gmi3 link width range.

Input: minimum & maximum link width to be set.

Exceptions that can be thrown by `amdsmi_set_cpu_gmi3_link_width_range` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            gmi_link_width = amdsmi_set_cpu_gmi3_link_width_range(processor, 0, 100)
except AmdSmiException as e:
    print(e)
```

### amdsmi_cpu_apb_enable

Description:  Enable APB.

Input: amdsmi processor handle

Exceptions that can be thrown by `amdsmi_cpu_apb_enable` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            apb_enable = amdsmi_cpu_apb_enable(processor)
except AmdSmiException as e:
    print(e)
```

### amdsmi_cpu_apb_disable

Description:  Disable APB.

Input: pstate value

Exceptions that can be thrown by `amdsmi_cpu_apb_disable` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            apb_disable = amdsmi_cpu_apb_disable(processor, 0)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_cpu_socket_lclk_dpm_level

Description:  Set NBIO lclk dpm level value.

Input: nbio id, min value, max value

Exceptions that can be thrown by `amdsmi_set_cpu_socket_lclk_dpm_level` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            nbio = amdsmi_set_cpu_socket_lclk_dpm_level(socket, 0, 0, 2)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_socket_lclk_dpm_level

Description: Get NBIO LCLK dpm level.

Output: nbio id

Exceptions that can be thrown by `amdsmi_get_cpu_socket_lclk_dpm_level` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            nbio = amdsmi_get_cpu_socket_lclk_dpm_level(processor)
            print(nbio['max_dpm_level'])
            print(nbio['max_dpm_level'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_cpu_pcie_link_rate

Description:  Set pcie link rate.

Input: rate control value

Exceptions that can be thrown by `amdsmi_set_cpu_pcie_link_rate` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            link_rate = amdsmi_set_cpu_pcie_link_rate(processor, 0, 0)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_cpu_df_pstate_range

Description:  Set df pstate range.

Input: max pstate, min pstate

Exceptions that can be thrown by `amdsmi_set_cpu_df_pstate_range` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            pstate_range = amdsmi_set_cpu_df_pstate_range(processor, 0, 2)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_current_io_bandwidth

Description: Get current input output bandwidth.

Output: link id and bw type to which io bandwidth to be obtained

Exceptions that can be thrown by `amdsmi_get_cpu_current_io_bandwidth` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            io_bw = amdsmi_get_cpu_current_io_bandwidth(processor)
            print(io_bw)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_current_xgmi_bw

Description: Get current xgmi bandwidth.

Output: amdsmi link id and bw type to which xgmi bandwidth to be obtained

Exceptions that can be thrown by `amdsmi_get_cpu_current_xgmi_bw` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            xgmi_bw = amdsmi_get_cpu_current_xgmi_bw(processor)
            print(xgmi_bw)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_hsmp_metrics_table_version

Description: Get HSMP metrics table version.

Output: amdsmi HSMP metrics table version

Exceptions that can be thrown by `amdsmi_get_hsmp_metrics_table_version` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            met_ver = amdsmi_get_hsmp_metrics_table_version(processor)
            print(met_ver)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_hsmp_metrics_table

Description: Get HSMP metrics table

Output: HSMP metric table data

Exceptions that can be thrown by `amdsmi_get_hsmp_metrics_table` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            mtbl = amdsmi_get_hsmp_metrics_table(processor)
            print(mtbl['accumulation_counter'])
            print(mtbl['max_socket_temperature'])
            print(mtbl['max_vr_temperature'])
            print(mtbl['max_hbm_temperature'])
            print(mtbl['socket_power_limit'])
            print(mtbl['max_socket_power_limit'])
            print(mtbl['socket_power'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_first_online_core_on_cpu_socket

Description: Get first online core on cpu socket.

Output: first online core on cpu socket

Exceptions that can be thrown by `amdsmi_first_online_core_on_cpu_socket` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    processor_handles = amdsmi_get_cpusocket_handles()
    if len(processor_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for processor in processor_handles:
            pcore_ind = amdsmi_first_online_core_on_cpu_socket(processor)
            print(pcore_ind)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_family

Description: Get cpu family.

Output: cpu family

Exceptions that can be thrown by `amdsmi_get_cpu_family` function:

* `AmdSmiLibraryException`

Example:

```python
try:
     cpu_family = amdsmi_get_cpu_family()
     print(cpu_family)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpu_model

Description: Get cpu model.

Output: cpu model

Exceptions that can be thrown by `amdsmi_get_cpu_model` function:

* `AmdSmiLibraryException`

Example:

```python
try:
     cpu_model = amdsmi_get_cpu_model()
     print(cpu_model)
except AmdSmiException as e:
    print(e)
```

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

Description: Initialize amdsmi lib and connect to driver

Input parameters: `None`

Output: `None`

Exceptions that can be thrown by `amdsmi_init` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    amdsmi_init()
    # continue with amdsmi
except AmdSmiException as e:
    print("Init failed")
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

Field | Description
---|---
`power_cap` |  power capability
`dpm_cap` |  dynamic power management capability
`default_power_cap` |  default power capability
`min_power_cap` | min power capability
`max_power_cap` | max power capability

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
`vram_size_mb` |  vram size in mb

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
            print(vram_info['vram_size_mb'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_cache_info

Description: Returns dictionary of cache information for the given GPU.

Input parameters:

* `processor_handle` device which to query

Output: Dictionary of Dictionaries containing cache information

Field | Description
---|---
`cache #` |  upt 10 caches will be available
`cache_size` | size of cache in KB
`cache_level` | level of cache
`data_cache` | True if data cache is enabled, false otherwise
`instruction_cache` | True if instruction cache is enabled, false otherwise
`cpu_cache` | True if cpu cache is enabled, false otherwise
`simd_cache` | True if simd cache is enabled, false otherwise

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
                print(cache_index)
                print(cache_values['cache_size'])
                print(cache_values['cache_level'])
                print(cache_values['data_cache'])
                print(cache_values['instruction_cache'])
                print(cache_values['cpu_cache'])
                print(cache_values['simd_cache'])
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
`fw_list`| List of dictionaries that contain information about a certain firmware block

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

Output: Dictionary with fields

Field | Description
---|---
`gfx_activity`| graphics engine usage percentage (0 - 100)
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
`average_socket_power`| average socket power
`gfx_voltage` | voltage gfx
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
            print(power_measure['average_socket_power'])
            print(power_measure['gfx_voltage'])
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
`vram_used`| VRAM currently in use

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
`cur_clk`| Current clock for given clock type
`max_clk` | Maximum clock for given clock type
`min_clk` | Minimum clock for given clock type

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
            print(clock_measure['cur_clk'])
            print(clock_measure['min_clk'])
            print(clock_measure['max_clk'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_pcie_link_status

Description: Returns the pcie link status for the given GPU.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`pcie_lanes`| pcie lanes in use
`pcie_speed`| current pcie speed
`pcie_interface_version`| current pcie generation

Exceptions that can be thrown by `amdsmi_get_pcie_link_status` function:

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
            pcie_link_status = amdsmi_get_pcie_link_status(device)
            print(pcie_link_status["pcie_lanes"])
            print(pcie_link_status["pcie_speed"])
            print(pcie_link_status["pcie_interface_version"])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_pcie_link_caps

Description:  Returns the max pcie link capabilities for the given GPU

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`pcie_lanes` | Number of PCIe lanes
`pcie_speed` | PCIe speed in MT/s

Exceptions that can be thrown by `amdsmi_get_pcie_link_caps` function:

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
            pcie_caps = amdsmi_get_pcie_link_caps(device)
            print(pcie_caps['pcie_lanes'])
            print(pcie_caps['pcie_speed'])
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_bad_page_info

Description:  Returns bad page info for the given GPU.
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` device which to query

Output: List consisting of dictionaries with fields for each bad page found

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
            if not len(bad_page_info):
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

### amdsmi_get_gpu_process_list

Description: Returns the list of processes for the given GPU

Input parameters:

* `processor_handle` device which to query

Output: List of process handles found

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
            print(processes)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_process_info

Description: Returns the info for the given process

Input parameters:

* `processor_handle` device which to query
* `process_handle` process which to query

Output: Dictionary with fields

Field | Description
---|---
`name` | Name of process
`pid` | Process ID
`mem` | Process memory usage
`engine_usage`| <table><thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`gfx`</td><td>GFX engine usage in ns</td></tr><tr><td>`enc`</td><td>Encode engine usage in ns</td></tr></tbody></table>
`memory_usage`| <table><thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`gtt_mem`</td><td>GTT memory usage</td></tr><tr><td>`cpu_mem`</td><td>CPU memory usage</td></tr><tr><td>`vram_mem`</td><td>VRAM memory usage</td></tr> </tbody></table>

Exceptions that can be thrown by `amdsmi_get_gpu_process_info` function:

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
            for process in processes:
                print(amdsmi_get_gpu_process_info(device, process))
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
`correctable_count`| Correctable ECC error count
`uncorrectable_count`| Uncorrectable ECC error count

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
`manufacturer_name` | Manufacturer name
`product_name` | Product name

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
    print(board_info["manufacturer_name"])
    print(board_info["product_name"])
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

### Constructor

Description: Allocates a new event reader notifier to monitor different types of events for the given GPU

Input parameters:

* `processor_handle` device handle corresponding to the device on which to listen for events
* `event_types` list of event types from AmdSmiEvtNotificationType enum. Specifying which events to collect for the given device.

Event Type | Description
---|------
`VMFAULT` | VM page fault
`THERMAL_THROTTLE` | thermal throttle
`GPU_PRE_RESET`   | gpu pre reset
`GPU_POST_RESET` | gpu post reset

### read

Description: Reads events on the given device. When event is caught, device handle, message and event type are returned. Reading events stops when timestamp passes without event reading.

Input parameters:

* `timestamp` number of milliseconds to wait for an event to occur. If event does not happen monitoring is finished
* `num_elem` number of events. This is optional parameter. Default value is 10.

### stop

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
            memory = amdsmi_get_gpu_memory_total(device)
            print(memory)
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
            memory = amdsmi_get_gpu_memory_usage(device)
            print(memory)
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
`num_supported`| The number of supported frequencies
`current`| The current frequency index
`frequency`| List of frequencies, only the first num_supported frequencies are valid

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

Description: This function retrieves the voltage/frequency curve information
It is not supported on virtual machine guest

Input parameters:

* `processor_handle` handle for the given device

Output: Dictionary with fields

Field | Description
---|---
`curr_sclk_range` | <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound sclk range</td></tr><tr><td>`upper_bound`</td><td>upper bound sclk range</td></tr></tbody></table>
`curr_mclk_range` |  <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound mclk range</td></tr><tr><td>`upper_bound`</td><td>upper bound mclk range</td></tr></tbody></table>
`sclk_freq_limits` |  <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound sclk range limt</td></tr><tr><td>`upper_bound`</td><td>upper bound sclk range limit</td></tr></tbody></table>
`mclk_freq_limits` |  <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound mclk range limit</td></tr><tr><td>`upper_bound`</td><td>upper bound mclk range limit</td></tr></tbody></table>
`curve.vc_points`| The number of supported frequencies
`num_regions`| The current frequency index

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

Field | Description
`---|---
`temperature_edge` | edge temperature value
`temperature_hotspot` | hotspot temperature value
`temperature_mem` | memory temperature value
`temperature_vrgfx` | vrgfx temperature value
`temperature_vrsoc` | vrsoc temperature value
`temperature_vrmem` | vrmem temperature value
`average_gfx_activity` | average gfx activity
`average_umc_activity` | average umc activity
`average_mm_activity` | average mm activity
`average_socket_power` | average socket power
`energy_accumulator` | energy accumulator value
`system_clock_counter` | system clock counter
`average_gfxclk_frequency` | average gfx clock frequency
`average_socclk_frequency` | average soc clock frequency
`average_uclk_frequency` | average uclk frequency
`average_vclk0_frequency` | average vclk0 frequency
`average_dclk0_frequency` | average dclk0 frequency
`average_vclk1_frequency` | average vclk1 frequency
`average_dclk1_frequency` | average dclk1 frequency
`current_gfxclk` | current gfx clock
`current_socclk` | current soc clock
`current_uclk` | current uclk
`current_vclk0` | current vclk0
`current_dclk0` | current dclk0
`current_vclk1` | current vclk1
`current_dclk1` | current dclk1
`throttle_status` | current throttle status
`current_fan_speed` | current fan speed
`pcie_link_width` | pcie link width
`pcie_link_speed` | pcie link speed
`padding` | padding
`gfx_activity_acc` | gfx activity acc
`mem_activity_acc` | mem activity acc
`temperature_hbm` | list of hbm temperatures
`firmware_timestamp` | timestamp from PMFW
`voltage_soc` | soc voltage
`voltage_gfx` | gfx voltage
`voltage_mem` | mem voltage
`indep_throttle_status` | asic independent throttle status
`current_socket_power` | current socket power
`vcn_activity` | list of encoding and decoding engine utilizations
`gfxclk_lock_status` | gfx clock lock status
`xgmi_link_width` | XGMI bus width
`xgmi_link_speed` | XGMI bitrate (in Gbps)
`pcie_bandwidth_acc` | PCIE accumulated bandwidth (GB/sec)
`pcie_bandwidth_inst` | PCIE instantaneous bandwidth (GB/sec)
`pcie_l0_to_recov_count_acc` | PCIE L0 to recovery state transition accumulated count
`pcie_replay_count_acc` | PCIE replay accumulated count
`pcie_replay_rover_count_acc` | PCIE replay rollover accumulated count
`xgmi_read_data_acc` | XGMI accumulated read data transfer size(KiloBytes)
`xgmi_write_data_acc` | XGMI accumulated write data transfer size(KiloBytes)
`current_gfxclks` | list of current gfx clock frequencies
`current_socclks` | list of current soc clock frequencies
`current_vclk0s` | list of current v0 clock frequencies
`current_dclk0s` | list of current d0 clock frequencies

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
`available_profiles`| Which profiles are supported by this system
`current`| Which power profile is currently active
`num_profiles`| How many power profiles are available

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
`value`| Counter value
`time_enabled`| Time that the counter was enabled in nanoseconds
`time_running`| Time that the counter was running in nanoseconds

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
`correctable_count`| Count of correctable errors
`uncorrectable_count`| Count of uncorrectable errors

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
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
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

## GPU Metrics APIs

### amdsmi_get_gpu_metrics_temp_hotspot

Description: Get the hotspot temperature in degrees Celsius

Input parameters:

* `processor_handle` device which to query

Output: hotspot temperature in degrees Celsius

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_temp_hotspot` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            hotspot_temp = amdsmi_get_gpu_metrics_temp_hotspot(device)
            print(hotspot_temp)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_temp_mem

Description: Get the memory temperature in degrees Celsius

Input parameters:

* `processor_handle` device which to query

Output: memory temperature in degrees Celsius

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_temp_mem` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            mem_temp = amdsmi_get_gpu_metrics_temp_mem(device)
            print(mem_temp)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_temp_vrsoc

Description: Get the VRSOC temperature in degrees Celsius

Input parameters:

* `processor_handle` device which to query

Output: VRSOC temperature in degrees Celsius

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_temp_vrsoc` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            vrsoc_temp = amdsmi_get_gpu_metrics_temp_vrsoc(device)
            print(vrsoc_temp)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_curr_socket_power

Description: Get the current socket power in Watts

Input parameters:

* `processor_handle` device which to query

Output: current socket power in Watts

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_curr_socket_power` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            curr_socket_power = amdsmi_get_gpu_metrics_curr_socket_power(device)
            print(curr_socket_power)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_avg_gfx_activity

Description: Get the average GFX activity in percent

Input parameters:

* `processor_handle` device which to query

Output: average GFX activity in percent

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_avg_gfx_activity` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            avg_gfx_activity = amdsmi_get_gpu_metrics_avg_gfx_activity(device)
            print(avg_gfx_activity)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_avg_umc_activity

Description: Get the average UMC activity in percent

Input parameters:

* `processor_handle` device which to query

Output: average UMC activity in percent

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_avg_umc_activity` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            avg_umc_activity = amdsmi_get_gpu_metrics_avg_umc_activity(device)
            print(avg_umc_activity)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_avg_energy_acc

Description: Get the average energy accumulator in millijoules (check unit)

Input parameters:

* `processor_handle` device which to query

Output: average energy accumulator in millijoules (check unit)

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_avg_energy_acc` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            avg_energy_acc = amdsmi_get_gpu_metrics_avg_energy_acc(device)
            print(avg_energy_acc)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_system_clock_counter

Description: Get the system clock counter

Input parameters:

* `processor_handle` device which to query

Output: system clock counter

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_system_clock_counter` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
             system_clock_counter = amdsmi_get_gpu_metrics_system_clock_counter(device)
             print(system_clock_counter)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_firmware_timestamp

Description: Get the firmware timestamp

Input parameters:

* `processor_handle` device which to query

Output: firmware timestamp

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_firmware_timestamp` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:

            firmware_timestamp = amdsmi_get_gpu_metrics_firmware_timestamp(device)
            print(firmware_timestamp)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_throttle_status

Description: Get the throttle status

Input parameters:

* `processor_handle` device which to query

Output: True if throttled, False if it's not throttled

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_throttle_status` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            throttle_status = amdsmi_get_gpu_metrics_throttle_status(device)
            print(throttle_status)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_pcie_link_width

Description: Get the pcie link width

Input parameters:

* `processor_handle` device which to query

Output: pcie link width

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_pcie_link_width` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            pcie_link_width = amdsmi_get_gpu_metrics_pcie_link_width(device)
            print(pcie_link_width)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_pcie_link_speed

Description: Get the pcie link speed

Input parameters:

* `processor_handle` device which to query

Output: pcie link speed

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_pcie_link_speed` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            pcie_link_speed = amdsmi_get_gpu_metrics_pcie_link_speed(device)
            print(pcie_link_speed)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_xgmi_link_width

Description: Get the xgmi link width

Input parameters:

* `processor_handle` device which to query

Output: xgmi link width

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_xgmi_link_width` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            xgmi_link_width = amdsmi_get_gpu_metrics_xgmi_link_width(device)
            print(xgmi_link_width)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_xgmi_link_speed

Description: Get the xgmi link speed

Input parameters:

* `processor_handle` device which to query

Output: xgmi link speed

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_xgmi_link_speed` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            xgmi_link_speed = amdsmi_get_gpu_metrics_xgmi_link_speed(device)
            print(xgmi_link_speed)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_gfxclk_lock_status

Description: Get the lock status of the gfx clock

Input parameters:

* `processor_handle` device which to query

Output: True if gfx clock is locked, False if it's not locked, raise if not supported

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_gfxclk_lock_status` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            lock_status = amdsmi_get_gpu_metrics_gfxclk_lock_status(device)
            print(lock_status)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_gfx_activity_acc

Description: Get accumulated gfx activity

Input parameters:

* `processor_handle` device which to query

Output: accumulated gfx activity

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_gfx_activity_acc` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            gfx_activity_acc = amdsmi_get_gpu_metrics_gfx_activity_acc(device)
            print(gfx_activity_acc)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_mem_activity_acc

Description: Get accumulated memory activity

Input parameters:

* `processor_handle` device which to query

Output: accumulated mem activity

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_mem_activity_acc` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            mem_activity_acc = amdsmi_get_gpu_metrics_mem_activity_acc(device)
            print(mem_activity_acc)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_pcie_bandwidth_acc

Description: Get accumulated pcie bandwidth activity

Input parameters:

* `processor_handle` device which to query

Output: accumulated pcie bandwidth activity

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_pcie_bandwidth_acc` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            pcie_bandwidth_acc = amdsmi_get_gpu_metrics_pcie_bandwidth_acc(device)
            print(pcie_bandwidth_acc)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_pcie_bandwidth_inst

Description: Get instantaneous pcie bandwidth activity

Input parameters:

* `processor_handle` device which to query

Output: instantaneous pcie bandwidth activity

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_pcie_bandwidth_inst` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            pcie_bandwidth_inst = amdsmi_get_gpu_metrics_pcie_bandwidth_inst(device)
            print(pcie_bandwidth_inst)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_pcie_l0_recov_count

Description: Get count of pcie l0 recovery count errors

Input parameters:

* `processor_handle` device which to query

Output: number of l0 recovery count errors

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_pcie_l0_recov_count` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            pcie_l0_recov_count = amdsmi_get_gpu_metrics_pcie_l0_recov_count(device)
            print(pcie_l0_recov_count)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_pcie_replay_count_acc

Description: Get accumulated pcie replay counts

Input parameters:

* `processor_handle` device which to query

Output: accumulated pcie replay counts

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_pcie_replay_count_acc` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            pcie_replay_count_acc = amdsmi_get_gpu_metrics_pcie_replay_count_acc(device)
            print(pcie_replay_count_acc)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_pcie_replay_rover_count_acc

Description: Get accumulated pcie replay rollover counts

Input parameters:

* `processor_handle` device which to query

Output: accumulated pcie replay rollover counts

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_pcie_replay_rover_count_acc` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            pcie_replay_rover_count_acc = amdsmi_get_gpu_metrics_pcie_replay_rover_count_acc(device)
            print(pcie_replay_rover_count_acc)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_curr_uclk

Description: Get the current u clock frequency

Input parameters:

* `processor_handle` device which to query

Output: Current u clock frequency

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_curr_uclk` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            curr_uclk = amdsmi_get_gpu_metrics_curr_uclk(device)
            print(curr_uclk)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_temp_hbm

Description: Get the HBM temperatures in degrees Celsius

Input parameters:

* `processor_handle` device which to query

Output: list of HBM temperatures in degrees Celsius

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_temp_hbm` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            hbm_temp = amdsmi_get_gpu_metrics_temp_hbm(device)
            print(hbm_temp)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_vcn_activity

Description: Get the activity for each vcn encoding engine

Input parameters:

* `processor_handle` device which to query

Output: list of vcn activities

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_vcn_activity` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            vcn_activity = amdsmi_get_gpu_metrics_vcn_activity(device)
            print(vcn_activity)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_xgmi_read_data

Description: Get the accumulated read xgmi data for each xgmi link

Input parameters:

* `processor_handle` device which to query

Output: list of accumulated read xgmi data

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_xgmi_read_data` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            xgmi_read_data = amdsmi_get_gpu_metrics_xgmi_read_data(device)
            print(xgmi_read_data)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_xgmi_write_data

Description: Get the accumulated written xgmi data for each xgmi link

Input parameters:

* `processor_handle` device which to query

Output: list of accumulated written xgmi data

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_xgmi_write_data` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            xgmi_write_data = amdsmi_get_gpu_metrics_xgmi_write_data(device)
            print(xgmi_write_data)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_curr_gfxclk

Description: Get the current gfx clock frequency

Input parameters:

* `processor_handle` device which to query

Output: Current gfx clock frequency

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_curr_gfxclk` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            curr_gfxclk = amdsmi_get_gpu_metrics_curr_gfxclk(device)
            print(curr_gfxclk)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_curr_socclk

Description: Get the current soc clock frequency

Input parameters:

* `processor_handle` device which to query

Output: Current soc clock frequency

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_curr_socclk` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            curr_socclk = amdsmi_get_gpu_metrics_curr_socclk(device)
            print(curr_socclk)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_curr_vclk0

Description: Get the current v0 clock frequency

Input parameters:

* `processor_handle` device which to query

Output: Current v0 clock frequency

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_curr_vclk0` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            curr_vclk0 = amdsmi_get_gpu_metrics_curr_vclk0(device)
            print(curr_vclk0)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_curr_dclk0

Description: Get the current d0 clock frequency

Input parameters:

* `processor_handle` device which to query

Output: Current d0 clock frequency

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_curr_dclk0` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            curr_dclk0 = amdsmi_get_gpu_metrics_curr_dclk0(device)
            print(curr_dclk0)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_temp_edge

Description: Get the edge temperature in degrees Celsius

Input parameters:

* `processor_handle` device which to query

Output: edge temperature in degrees Celsius

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_temp_edge` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            edge_temp = amdsmi_get_gpu_metrics_temp_edge(device)
            print(edge_temp)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_temp_vr_gfx

Description: Get the VR GFX temperature in degrees Celsius

Input parameters:

* `processor_handle` device which to query

Output: VR GFX temperature in degrees Celsius

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_temp_vr_gfx` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            vr_gfx_temp = amdsmi_get_gpu_metrics_temp_vr_gfx(device)
            print(vr_gfx_temp)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_temp_vr_mem

Description: Get the VR MEM temperature in degrees Celsius

Input parameters:

* `processor_handle` device which to query

Output: VR MEM temperature in degrees Celsius

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_temp_vr_mem` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            vr_mem_temp = amdsmi_get_gpu_metrics_temp_vr_mem(device)
            print(vr_mem_temp)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_avg_mm_activity

Description: Get the average MM activity in percent

Input parameters:

* `processor_handle` device which to query

Output: average MM activity in percent

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_avg_mm_activity` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            avg_mm_activity = amdsmi_get_gpu_metrics_avg_mm_activity(device)
            print(avg_mm_activity)
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_gpu_metrics_curr_vclk1

Description: Get the current v1 clock frequency

Input parameters:

* `processor_handle` device which to query

Output: Current v1 clock frequency

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_curr_vclk1` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            curr_vclk1 = amdsmi_get_gpu_metrics_curr_vclk1(device)
            print(curr_vclk1)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_curr_dclk1

Description: Get the current d1 clock frequency

Input parameters:

* `processor_handle` device which to query

Output: Current d1 clock frequency

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_curr_dclk1` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            curr_dclk1 = amdsmi_get_gpu_metrics_curr_dclk1(device)
            print(curr_dclk1)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_indep_throttle_status

Description: Get the independent throttle status

Input parameters:

* `processor_handle` device which to query

Output: True if throttled, False if it's not throttled

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_indep_throttle_status` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            throttle_status = amdsmi_get_gpu_metrics_indep_throttle_status(device)
            print(throttle_status)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_avg_socket_power

Description: Get the average socket power in Watts

Input parameters:

* `processor_handle` device which to query

Output: average socket power in Watts

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_avg_socket_power` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            avg_socket_power = amdsmi_get_gpu_metrics_avg_socket_power(device)
            print(avg_socket_power)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_curr_fan_speed

Description: Get the current fan speed in percent

Input parameters:

* `processor_handle` device which to query

Output: current fan speed in percent

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_curr_fan_speed` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            curr_fan_speed = amdsmi_get_gpu_metrics_curr_fan_speed(device)
            print(curr_fan_speed)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_avg_gfx_clock_frequency

Description: Get the average gfx clock frequency in MHz

Input parameters:

* `processor_handle` device which to query

Output: average gfx clock frequency in MHz

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_avg_gfx_clock_frequency` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            avg_gfx_clock_frequency = amdsmi_get_gpu_metrics_avg_gfx_clock_frequency(device)
            print(avg_gfx_clock_frequency)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_avg_soc_clock_frequency

Description: Get the average soc clock frequency in MHz

Input parameters:

* `processor_handle` device which to query

Output: average soc clock frequency in MHz

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_avg_soc_clock_frequency` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            avg_soc_clock_frequency = amdsmi_get_gpu_metrics_avg_soc_clock_frequency(device)
            print(avg_soc_clock_frequency)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_avg_uclock_frequency

Description: Get the average u clock frequency in MHz

Input parameters:

* `processor_handle` device which to query

Output: average u clock frequency in MHz

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_avg_uclock_frequency` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            avg_uclock_frequency = amdsmi_get_gpu_metrics_avg_uclock_frequency(device)
            print(avg_uclock_frequency)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_avg_vclock0_frequency

Description: Get the average v0 clock frequency in MHz

Input parameters:

* `processor_handle` device which to query

Output: average v0 clock frequency in MHz

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_avg_vclock0_frequency` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            avg_vclock0_frequency = amdsmi_get_gpu_metrics_avg_vclock0_frequency(device)
            print(avg_vclock0_frequency)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_avg_dclock0_frequency

Description: Get the average d0 clock frequency in MHz

Input parameters:

* `processor_handle` device which to query

Output: average d0 clock frequency in MHz

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_avg_dclock0_frequency` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            avg_dclock0_frequency = amdsmi_get_gpu_metrics_avg_dclock0_frequency(device)
            print(avg_dclock0_frequency)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_avg_vclock1_frequency

Description: Get the average v1 clock frequency in MHz

Input parameters:

* `processor_handle` device which to query

Output: average v1 clock frequency in MHz

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_avg_vclock1_frequency` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            avg_vclock1_frequency = amdsmi_get_gpu_metrics_avg_vclock1_frequency(device)
            print(avg_vclock1_frequency)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_avg_dclock1_frequency

Description: Get the average d1 clock frequency in MHz

Input parameters:

* `processor_handle` device which to query

Output: average d1 clock frequency in MHz

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_avg_dclock1_frequency` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            avg_dclock1_frequency = amdsmi_get_gpu_metrics_avg_dclock1_frequency(device)
            print(avg_dclock1_frequency)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_volt_soc

Description: Get the soc voltage in millivolts

Input parameters:

* `processor_handle` device which to query

Output: soc voltage in millivolts

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_volt_soc` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            volt_soc = amdsmi_get_gpu_metrics_volt_soc(device)
            print(volt_soc)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_volt_gfx

Description: Get the gfx voltage in millivolts

Input parameters:

* `processor_handle` device which to query

Output: gfx voltage in millivolts

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_volt_gfx` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            volt_gfx = amdsmi_get_gpu_metrics_volt_gfx(device)
            print(volt_gfx)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_volt_mem

Description: Get the mem voltage in millivolts

Input parameters:

* `processor_handle` device which to query

Output: mem voltage in millivolts

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_volt_mem` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            volt_mem = amdsmi_get_gpu_metrics_volt_mem(device)
            print(volt_mem)
except AmdSmiException as e:
     print(e)
```

### amdsmi_get_gpu_metrics_header_info

Description: Get the gpu metrics structure header info

Input parameters:

* `processor_handle` device which to query

Output: dictionary of gpu metrics header information

Exceptions that can be thrown by `amdsmi_get_gpu_metrics_header_info` function:

* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:

```python
try:
    devices = amdsmi_get_processor_handles()
    if len(devices) == 0:
        print("No GPUs on the machine")
    else:
        for device in devices:
            header_info = amdsmi_get_gpu_metrics_header_info(device)
            print(header_info)
except AmdSmiException as e:
     print(e)
```

## CPU APIs

### amdsmi_get_cpusocket_handles

**Note: CURRENTLY HARDCODED TO RETURN DUMMY DATA**
Description: Returns list of cpusocket handle objects on current machine

Input parameters: `None`

Output: List of cpusocket handle objects

Exceptions that can be thrown by `amdsmi_get_cpusocket_handles` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    sockets = amdsmi_get_cpusocket_handles()
    print('Socket numbers: {}'.format(len(sockets)))
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpusocket_info

**Note: CURRENTLY HARDCODED TO RETURN EMPTY VALUES**
Description: Return cpu socket index

Input parameters:
`socket_handle` cpu socket handle

Output: Socket index

Exceptions that can be thrown by `amdsmi_get_cpusocket_info` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            print(amdsmi_get_cpusocket_info(socket))
except AmdSmiException as e:
    print(e)
```

### amdsmi_get_cpucore_handles

Description: Returns list of CPU core handle objects on current machine

Input parameters: `None`

Output: List of CPU core handle objects

Exceptions that can be thrown by `amdsmi_get_cpucore_handles` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    core_handles = amdsmi_get_cpucore_handles()
    if len(core_handles) == 0:
        print("No CPU cores on machine")
    else:
        for core in core_handles:
            print(amdsmi_get_cpucore_info(core))
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            version = amdsmi_get_cpu_hsmp_proto_ver(socket)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            version = amdsmi_get_cpu_smu_fw_version(socket)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            prochot = amdsmi_get_cpu_prochot_status(socket)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            clk = amdsmi_get_cpu_fclk_mclk(socket)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            cclk_limit = amdsmi_get_cpu_cclk_limit(socket)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            freq_limit = amdsmi_get_cpu_socket_current_active_freq_limit(socket)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            freq_range = amdsmi_get_cpu_socket_freq_range(socket)
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
    core_handles = amdsmi_get_cpucore_handles()
    if len(core_handles) == 0:
        print("No CPU cores on machine")
    else:
        for core in core_handles:
            freq_limit = amdsmi_get_cpu_core_current_freq_limit(core)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            sock_power = amdsmi_get_cpu_socket_power(socket)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            sock_power = amdsmi_get_cpu_socket_power_cap(socket)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            sock_power = amdsmi_get_cpu_socket_power_cap_max(socket)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            power = amdsmi_get_cpu_pwr_svi_telemetry_all_rails(socket)
            print(power)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_cpu_socket_power_cap

Description: Set the power cap value for a given socket.

Input: socket index, amdsmi socket power cap value

Exceptions that can be thrown by `amdsmi_set_cpu_socket_power_cap` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            power = amdsmi_set_cpu_socket_power_cap(socket, 0, 1000)
except AmdSmiException as e:
    print(e)
```

### amdsmi_set_cpu_pwr_efficiency_mode

Description: Set the power efficiency profile policy.

Input: socket index, mode(0, 1, or 2)

Exceptions that can be thrown by `amdsmi_set_cpu_pwr_efficiency_mode` function:

* `AmdSmiLibraryException`

Example:

```python
try:
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            policy = amdsmi_set_cpu_pwr_efficiency_mode(socket, 0, 0)
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
    core_handles = amdsmi_get_cpucore_handles()
    if len(core_handles) == 0:
        print("No CPU cores on machine")
    else:
        for core in core_handles:
            boost_limit = amdsmi_get_cpu_core_boostlimit(core)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            c0_residency = amdsmi_get_cpu_socket_c0_residency(socket)
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
    core_handles = amdsmi_get_cpucore_handles()
    if len(core_handles) == 0:
        print("No CPU cores on machine")
    else:
        for core in core_handles:
            boost_limit = amdsmi_set_cpu_core_boostlimit(core, 1000)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            boost_limit = amdsmi_set_cpu_socket_boostlimit(socket, 1000)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            ddr_bw = amdsmi_get_cpu_ddr_bw(socket)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            ptmon = amdsmi_get_cpu_socket_temperature(socket)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            dimm = amdsmi_get_cpu_dimm_temp_range_and_refresh_rate(socket)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            dimm = amdsmi_get_cpu_dimm_power_consumption(socket)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            dimm = amdsmi_get_cpu_dimm_thermal_sensor(socket)
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
    socket_handles = amdsmi_get_cpusocket_handles()
    if len(socket_handles) == 0:
        print("No CPU sockets on machine")
    else:
        for socket in socket_handles:
            xgmi_width = amdsmi_set_cpu_xgmi_width(socket, 0, 100)
except AmdSmiException as e:
    print(e)
```

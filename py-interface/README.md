# Requirements
* python 3.6 64-bit
* driver must be loaded for amdsmi_init() to pass

# Overview
## Folder structure:
File Name | Note
---|---
`__init__.py` | Python package initialization file
`amdsmi_interface.py` | Amdsmi library python interface
`amdsmi_wrapper.py` | Python wrapper around amdsmi binary
`amdsmi_exception.py` | Amdsmi exceptions python file
`README.md` | Documentation

## Usage:

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

# Exceptions

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
    if e.err_code == AmdSmiRetCode.ERR_RETRY:
        print("Error info: {}".format(e.err_info))
```
* `AmdSmiRetryException` : Derives `AmdSmiLibraryException` class and signals device is busy and call should be retried.
* `AmdSmiTimeoutException` : Derives `AmdSmiLibraryException` class and represents that call had timed out.
* `AmdSmiParameterException`: Derives base `AmdSmiException` class and represents errors related to invaild parameters passed to functions. When this exception is thrown, err_msg is set and it explains what is the actual and expected type of the parameters.
* `AmdSmiBdfFormatException`: Derives base `AmdSmiException` class and represents invalid bdf format.

# API

## amdsmi_init
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

## amdsmi_shut_down
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

## amdsmi_get_processor_type
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

## amdsmi_get_processor_handles
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

## amdsmi_get_socket_handles
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

## amdsmi_get_socket_info
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


## amdsmi_get_processor_handle_from_bdf
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

## amdsmi_get_gpu_device_bdf
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

## amdsmi_get_gpu_device_uuid
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

## amdsmi_get_driver_version
Description: Returns the version string of the driver

Input parameters:
* `processor_handle` dev for which to query

Output: Driver version string that is handling the device

Exceptions that can be thrown by `amdsmi_get_driver_version` function:
* `AmdSmiParameterException`
* `AmdSmiLibraryException`

Example:
```python
try:
    device = amdsmi_get_processor_handles()[0]
    print("Driver version: ", amdsmi_get_driver_version(device))
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_asic_info
Description: Returns asic information for the given GPU

Input parameters:
* `processor_handle` device which to query

Output: Dictionary with fields

Field | Content
---|---
`market_name` |  market name
`family` |  family
`vendor_id` |  vendor id
`device_id` |  device id
`rev_id` |  revision id
`asic_serial` | asic serial

Exceptions that can be thrown by `amdsmi_get_asic_info` function:
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
            asic_info = amdsmi_get_asic_info(device)
            print(asic_info['market_name'])
            print(hex(asic_info['family']))
            print(hex(asic_info['vendor_id']))
            print(hex(asic_info['device_id']))
            print(hex(asic_info['rev_id']))
            print(asic_info['asic_serial'])
except AmdSmiException as e:
    print(e)
```
## amdsmi_get_power_cap_info
Description: Returns dictionary of power capabilities as currently configured
on the given GPU

Input parameters:
* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`power_cap` |  power capability
`dpm_cap` |  dynamic power management capability
`power_cap_default` |  default power capability
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
            print(power_info['power_cap_default'])
            print(power_info['min_power_cap'])
            print(power_info['max_power_cap'])
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_caps_info
Description: Returns capabilities as currently configured for the given GPU

Input parameters:
* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
 `gfx` | <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`gfxip_major`</td><td> major revision of GFX IP</td></tr><tr><td>`gfxip_minor`</td><td>minor revision of GFX IP</td></tr><tr><td>`gfxip_cu_count`</td><td>number of GFX compute units</td></tr></tbody></table>
 `mm_ip_list` |  List of MM engines on the device, of AmdSmiMmIp type
 `ras_supported` |  `True` if ecc is supported, `False` if not
 `gfx_ip_count` |  Number of GFX engines on the device
 `dma_ip_count` | Number of DMA engines on the device

Exceptions that can be thrown by `amdsmi_get_caps_info` function:
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
            caps_info =  amdsmi_get_caps_info(device)
            print(caps_info['ras_supported'])
            print(caps_info['gfx']['gfxip_major'])
            print(caps_info['gfx']['gfxip_minor'])
            print(caps_info['gfx']['gfxip_cu_count'])
            print(caps_info['mm_ip_list'])
            print(caps_info['gfx_ip_count'])
            print(caps_info['dma_ip_count'])
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_vbios_info
Description:  Returns the static information for the VBIOS on the device.

Input parameters:
* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`name` | vbios name
`vbios_version` | vbios current version
`build_date` | vbios build date
`part_number` | vbios part number
`vbios_version_string` | vbios version string

Exceptions that can be thrown by `amdsmi_get_vbios_info` function:
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
            vbios_info = amdsmi_get_vbios_info(device)
            print(vbios_info['name'])
            print(vbios_info['vbios_version'])
            print(vbios_info['build_date'])
            print(vbios_info['part_number'])
            print(vbios_info['vbios_version_string'])
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_fw_info
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
                print(firmware_block['fw_version'])
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_gpu_activity
Description: Returns the engine usage for the given GPU

Input parameters:
* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`gfx_activity`| graphics engine usage percentage (0 - 100)
`umc_activity` | memory engine usage percentage (0 - 100)
`mm_activity` | list of multimedia engine usages in percentage (0 - 100)

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
## amdsmi_get_power_measure
Description: Returns the current power and voltage for the given GPU

Input parameters:
* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`average_socket_power`| average socket power
`voltage_gfx` | voltage gfx
`energy_accumulator` | energy accumulator
`power_limit` | power limit

Exceptions that can be thrown by `amdsmi_get_power_measure` function:
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
            power_measure = amdsmi_get_power_measure(device)
            print(power_measure['average_socket_power'])
            print(power_measure['voltage_gfx'])
            print(power_measure['energy_accumulator'])
            print(power_measure['power_limit'])
except AmdSmiException as e:
    print(e)
```
## amdsmi_get_vram_usage
Description: Returns total VRAM and VRAM in use

Input parameters:
* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`vram_total` | VRAM total
`vram_used`| VRAM currently in use

Exceptions that can be thrown by `amdsmi_get_vram_usage` function:
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
            vram_usage = amdsmi_get_vram_usage(device)
            print(vram_usage['vram_used'])
            print(vram_usage['vram_total'])
except AmdSmiException as e:
    print(e)
```
## amdsmi_get_clock_measure
Description: Returns the clock measure for the given GPU

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
`avg_clk` | Average clock for given clock type
`min_clk` | Minimum clock for given clock type
`max_clk` | Maximum clock for given clock type

Exceptions that can be thrown by `amdsmi_get_clock_measure` function:
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
            clock_measure = amdsmi_get_clock_measure(device, AmdSmiClkType.GFX)
            print(clock_measure['cur_clk'])
            print(clock_measure['avg_clk'])
            print(clock_measure['min_clk'])
            print(clock_measure['max_clk'])
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_pcie_link_status
Description: Returns the pcie link status for the given GPU

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`pcie_lanes`| pcie lanes in use
`pcie_speed`| current pcie speed

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
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_pcie_link_caps
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

## amdsmi_get_bad_page_info
Description:  Returns bad page info for the given GPU

Input parameters:
* `processor_handle` device which to query

Output: List consisting of dictionaries with fields for each bad page found

Field | Description
---|---
`value` | Value of page
`page_address` | Address of bad page
`page_size` | Size of bad page
`status` | Status of bad page

Exceptions that can be thrown by `amdsmi_get_bad_page_info` function:
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
            bad_page_info = amdsmi_get_bad_page_info(device)
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

## amdsmi_get_target_frequency_range
Description: Returns the supported frequency target range for the given GPU

`Note: Not Supported`

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
`supported_upper_bound` | Maximal value of target supported frequency in MHz
`supported_lower_bound` | Minimal value of target supported frequency in MHz
`current_upper_bound` | Maximal value of target current frequency in MHz
`current_lower_bound` | Minimal value of target current frequency in MHz

Exceptions that can be thrown by `amdsmi_get_target_frequency_range` function:
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
            print("=============== GFX DOMAIN ================")
            freq_range = amdsmi_get_target_frequency_range(device,
                AmdSmiClkType.GFX)
            print(freq_range['supported_upper_bound'])
            print(freq_range['supported_lower_bound'])
            print(freq_range['current_upper_bound'])
            print(freq_range['current_lower_bound'])
            print("=============== MEM DOMAIN ================")
            freq_range = amdsmi_get_target_frequency_range(device,
                AmdSmiClkType.MEM)
            print(freq_range['supported_upper_bound'])
            print(freq_range['supported_lower_bound'])
            print(freq_range['current_upper_bound'])
            print(freq_range['current_lower_bound'])
            print("=============== VCLK0 DOMAIN ================")
            freq_range = amdsmi_get_target_frequency_range(device,
                AmdSmiClkType.VCLK0)
            print(freq_range['supported_upper_bound'])
            print(freq_range['supported_lower_bound'])
            print(freq_range['current_upper_bound'])
            print(freq_range['current_lower_bound'])
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_process_list
Description: Returns the list of processes for the given GPU

Input parameters:

* `processor_handle` device which to query

Output: List of process handles found

Exceptions that can be thrown by `amdsmi_get_process_list` function:
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
            processes = amdsmi_get_process_list(device)
            print(processes)
except AmdSmiException as e:
    print(e)
```
## amdsmi_get_process_info
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
`engine_usage`| <table><thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`gfx`</td><td>GFX engine usage in ns</td></tr><tr><td>`compute`</td><td>Compute engine usage in ns</td></tr><tr><td>`dma`</td><td>DMA engine usage in ns </td></tr><tr><td>`enc`</td><td>Encode engine usage in ns</td></tr><tr><td>`dec`</td><td>Decode engine usage in ns</td></tr></tbody></table>
`memory_usage`| <table><thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`gtt_mem`</td><td>GTT memory usage</td></tr><tr><td>`cpu_mem`</td><td>CPU memory usage</td></tr><tr><td>`vram_mem`</td><td>VRAM memory usage</td></tr> </tbody></table>

Exceptions that can be thrown by `amdsmi_get_process_info` function:
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
            processes = amdsmi_get_process_list(device)
            for process in processes:
                print(amdsmi_get_process_info(device, process))
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_ecc_error_count
Description: Returns the ECC error count for the given GPU

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`correctable_count`| Correctable ECC error count
`uncorrectable_count`| Uncorrectable ECC error count

Exceptions that can be thrown by `amdsmi_get_ecc_error_count` function:
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
            ecc_error_count = amdsmi_get_ecc_error_count(device)
            print(ecc_error_count["correctable_count"])
            print(ecc_error_count["uncorrectable_count"])
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_board_info
Description: Returns board info for the given GPU

Input parameters:

* `processor_handle` device which to query

Output:  Dictionary with fields correctable and uncorrectable

Field | Description
---|---
`serial_number` | Board serial number
`product_serial` | Product serial
`product_name` | Product name

Exceptions that can be thrown by `amdsmi_get_board_info` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    device = amdsmi_get_processor_handle_from_bdf("0000:23.00.0")
    board_info = amdsmi_get_board_info(device)
    print(board_info["serial_number"])
    print(board_info["product_serial"])
    print(board_info["product_name"])
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_ras_block_features_enabled
Description: Returns status of each RAS block for the given GPU

Input parameters:

* `processor_handle` device which to query

Output: List containing dictionaries with fields for each RAS block

Field | Description
---|---
`block` | RAS block
`status` | RAS block status

Exceptions that can be thrown by `amdsmi_get_ras_block_features_enabled` function:
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
            ras_block_features = amdsmi_get_ras_block_features_enabled(device)
            print(ras_block_features)
except AmdSmiException as e:
    print(e)
```
## AmdSmiEventReader class

Description: Providing methods for event monitoring. This is context manager class.
Can be used with `with` statement for automatic cleanup.

Methods:

## Constructor

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

## read

Description: Reads events on the given device. When event is caught, device handle, message and event type are returned. Reading events stops when timestamp passes without event reading.

Input parameters:

* `timestamp` number of milliseconds to wait for an event to occur. If event does not happen monitoring is finished
* `num_elem` number of events. This is optional parameter. Default value is 10.

## stop

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

## amdsmi_dev_open_supported_func_iterator
Description: Get a function name iterator of supported AMDSMI functions for a device

Input parameters:

* `processor_handle` device which to query

Output: Handle for a function iterator

Exceptions that can be thrown by `amdsmi_dev_open_supported_func_iterator` function:
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
            obj_handle = amdsmi_dev_open_supported_func_iterator(device)
            print(obj_handle)
            amdsmi_dev_close_supported_func_iterator(obj_handle)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_open_supported_variant_iterator
Description: Get a variant iterator for a given handle

Input parameters:

* `obj_handle` Object handle for witch to return a variant handle

Output: Variant iterator handle

Exceptions that can be thrown by `amdsmi_dev_open_supported_variant_iterator` function:
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
            obj_handle = amdsmi_dev_open_supported_func_iterator(device)
            var_iter = amdsmi_dev_open_supported_variant_iterator(obj_handle)
            print(var_iter)
            amdsmi_dev_close_supported_func_iterator(obj_handle)
            amdsmi_dev_close_supported_func_iterator(var_iter)
except AmdSmiException as e:
    print(e)
```

## amdsmi_next_func_iter
Description: Advance an object identifier iterator

Input parameters:

* `obj_handle` Object handle to advance

Output: Next iterator handle

Exceptions that can be thrown by `amdsmi_next_func_iter` function:
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
            obj_handle = amdsmi_dev_open_supported_func_iterator(device)
            print(obj_handle)
            obj_handle = amdsmi_next_func_iter(obj_handle)
            print(obj_handle)
            amdsmi_dev_close_supported_func_iterator(obj_handle)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_close_supported_func_iterator
Description: Close a variant iterator handle

Input parameters:

* `obj_handle` Object handle to be closed

Output: None

Exceptions that can be thrown by `amdsmi_dev_close_supported_func_iterator` function:
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
            obj_handle = amdsmi_dev_open_supported_func_iterator(device)
            amdsmi_dev_close_supported_func_iterator(obj_handle)
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_func_iter_value
Description: Get the value associated with a function/variant iterator

Input parameters:

* `obj_handle` Object handle to query

Output: Data associated with a function/variant iterator

Field | Description
---|---
`id`| Internal ID of the function/variant
`name`| Descriptive name of the function/variant
`amd_id_0` | <table>  <thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`memory_type`</td><td>Memory type</td></tr><tr><td>`temp_metric`</td><td>Temperature metric</td></tr><tr><td>`evnt_type`</td><td>Event type</td></tr><tr><td>`evnt_group`</td><td>Event group</td></tr><tr><td>`clk_type`</td><td>Clock type</td></tr></tr><tr><td>`fw_block`</td><td>Firmware block</td></tr><tr><td>`gpu_block_type`</td><td>GPU block type</td></tr></tbody></table>

Exceptions that can be thrown by `amdsmi_get_func_iter_value` function:
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
            obj_handle = amdsmi_dev_open_supported_func_iterator(device)
            value = amdsmi_get_func_iter_value(obj_handle)
            print(value)
            amdsmi_dev_close_supported_func_iterator(obj_handle)
except AmdSmiException as e:
    print(e)
```

##  amdsmi_dev_set_pci_bandwidth
Description: Control the set of allowed PCIe bandwidths that can be used

Input parameters:
* `processor_handle` handle for the given device
* `bw_bitmask` A bitmask indicating the indices of the bandwidths that are
to be enabled (1) and disabled (0)

Output: None

Exceptions that can be thrown by ` amdsmi_dev_set_pci_bandwidth` function:
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
             amdsmi_dev_set_pci_bandwidth(device, 0)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_dev_set_power_cap
Description: Set the power cap value

Input parameters:
* `processor_handle` handle for the given device
* `sensor_ind` a 0-based sensor index. Normally, this will be 0. If a
device has more than one sensor, it could be greater than 0
* `cap` int that indicates the desired power cap, in microwatts

Output: None

Exceptions that can be thrown by ` amdsmi_dev_set_power_cap` function:
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
             amdsmi_dev_set_power_cap(device, 0, power_cap)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_dev_set_power_profile
Description: Set the power profile

Input parameters:
* `processor_handle` handle for the given device
* `reserved` Not currently used, set to 0
* `profile` a amdsmi_power_profile_preset_masks_t that hold the mask of
the desired new power profile

Output: None

Exceptions that can be thrown by ` amdsmi_dev_set_power_profile` function:
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
             amdsmi_dev_set_power_profile(device, 0, profile)
except AmdSmiException as e:
    print(e)
```


## amdsmi_dev_set_clk_range
Description: This function sets the clock range information

Input parameters:
* `processor_handle` handle for the given device
* `min_clk_value` minimum clock value for desired clock range
* `max_clk_value` maximum clock value for desired clock range
* `clk_type`AMDSMI_CLK_TYPE_SYS | AMDSMI_CLK_TYPE_MEM range type

Output: None

Exceptions that can be thrown by `amdsmi_dev_set_clk_range` function:
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
            amdsmi_dev_set_clk_range(device, 0, 1000, AmdSmiClkType.AMDSMI_CLK_TYPE_SYS)
except AmdSmiException as e:
    print(e)
```


## amdsmi_dev_get_pci_id
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


Exceptions that can be thrown by `amdsmi_dev_get_pci_id` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            bdfid = amdsmi_dev_get_pci_id(device)
            print(bdfid)
except AmdSmiException as e:
    print(e)
```


## amdsmi_dev_get_pci_bandwidth
Description: Get the list of possible PCIe bandwidths that are available.

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

Exceptions that can be thrown by `amdsmi_dev_get_pci_bandwidth` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            bandwidth = amdsmi_dev_get_pci_bandwidth(device)
            print(bandwidth)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_get_pci_throughput
Description: Get PCIe traffic information

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with the fields

Field | Content
---|---
`sent` | number of bytes sent in 1 second
`received` | the number of bytes received
`max_pkt_sz` | maximum packet size

Exceptions that can be thrown by `amdsmi_dev_get_pci_throughput` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            pci = amdsmi_dev_get_pci_throughput(device)
            print(pci)
except AmdSmiException as e:
    print(e)
```

##  amdsmi_dev_get_pci_replay_counter

Description: Get PCIe replay counter

Input parameters:

* `processor_handle` device which to query

Output: counter value
The sum of the NAK's received and generated by the GPU

Exceptions that can be thrown by ` amdsmi_dev_get_pci_replay_counter` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            counter =  amdsmi_dev_get_pci_replay_counter(device)
            print(counter)
except AmdSmiException as e:
    print(e)
```

## amdsmi_topo_get_numa_affinity

Description: Get the NUMA node associated with a device

Input parameters:

* `processor_handle` device which to query

Output: NUMA node value

Exceptions that can be thrown by `amdsmi_topo_get_numa_affinity` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            numa_node = amdsmi_topo_get_numa_affinity(device)
            print(numa_node)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_get_power_ave

Description: Get the average power consumption of the device

Input parameters:

* `processor_handle` device which to query
* `sensor_id` a 0-based sensor index. Normally, this will be 0.
If a device has more than one sensor, it could be greater than 0.

Output: the average power consumption

Exceptions that can be thrown by `amdsmi_dev_get_power_ave` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            power = amdsmi_dev_get_power_ave(device)
            print(power)
except AmdSmiException as e:
    print(e)
```


## amdsmi_dev_get_energy_count

Description: Get the energy accumulator counter of the device.

Input parameters:

* `processor_handle` device which to query

Output: Dictionary with fields

Field | Content
---|---
`power` |  power
`counter_resolution` |  counter resolution
`timestamp` |  timestamp

Exceptions that can be thrown by `amdsmi_dev_get_energy_count` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            power = amdsmi_dev_get_energy_count(device)
            print(power)
except AmdSmiException as e:
    print(e)
```


## amdsmi_dev_get_memory_total

Description: Get the total amount of memory that exists

Input parameters:

* `processor_handle` device which to query
* `mem_type` enum AmdSmiMemoryType

Output: total amount of memory

Exceptions that can be thrown by `amdsmi_dev_get_memory_total` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            memory = amdsmi_dev_get_memory_total(device)
            print(memory)
except AmdSmiException as e:
    print(e)
```




##  amdsmi_dev_set_od_clk_info
Description: This function sets the clock frequency information

Input parameters:
* `processor_handle` handle for the given device
* `level` AMDSMI_FREQ_IND_MIN|AMDSMI_FREQ_IND_MAX to set the minimum (0)
or maximum (1) speed
* `clk_value` value to apply to the clock range
* `clk_type` AMDSMI_CLK_TYPE_SYS | AMDSMI_CLK_TYPE_MEM range type

Output: None

Exceptions that can be thrown by ` amdsmi_dev_set_od_clk_info` function:
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
             amdsmi_dev_set_od_clk_info(
                device,
                AmdSmiFreqInd.AMDSMI_FREQ_IND_MAX,
                1000,
                AmdSmiClkType.AMDSMI_CLK_TYPE_SYS
            )
except AmdSmiException as e:
    print(e)
```


## amdsmi_dev_get_memory_usage

Description: Get the current memory usage

Input parameters:

* `processor_handle` device which to query
* `mem_type` enum AmdSmiMemoryType

Output: the amount of memory currently being used

Exceptions that can be thrown by `amdsmi_dev_get_memory_usage` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            memory = amdsmi_dev_get_memory_usage(device)
            print(memory)
except AmdSmiException as e:
    print(e)
```


##  amdsmi_dev_set_od_volt_info
Description: This function sets  1 of the 3 voltage curve points

Input parameters:
* `processor_handle` handle for the given device
* `vpoint` voltage point [0|1|2] on the voltage curve
* `clk_value` clock value component of voltage curve point
* `volt_value` voltage value component of voltage curve point

Output: None

Exceptions that can be thrown by ` amdsmi_dev_set_od_volt_info` function:
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
             amdsmi_dev_set_od_volt_info(device, 1, 1000, 980)
except AmdSmiException as e:
    print(e)
```


## amdsmi_dev_get_memory_busy_percent

Description: Get percentage of time any device memory is being used

Input parameters:

* `processor_handle` device which to query

Output: percentage of time that any device memory is being used for the specified device.

Exceptions that can be thrown by `amdsmi_dev_get_memory_busy_percent` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            busy_percent = amdsmi_dev_get_memory_busy_percent(device)
            print(busy_percent)
except AmdSmiException as e:
    print(e)
```



##  amdsmi_dev_set_perf_level_v1
Description: Set the PowerPlay performance level associated with the device
with provided device handle with the provided value

Input parameters:
* `processor_handle` handle for the given device
* `perf_lvl` the value to which the performance level should be set

Output: None

Exceptions that can be thrown by ` amdsmi_dev_set_perf_level_v1` function:
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
             amdsmi_dev_set_perf_level_v1(device, AmdSmiDevPerfLevel.AMDSMI_DEV_PERF_LEVEL_HIGH)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_get_fan_rpms
Description: Get the fan speed in RPMs of the device with the specified device
handle and 0-based sensor index.

Input parameters:
* `processor_handle` handle for the given device
* `sensor_idx` a 0-based sensor index. Normally, this will be 0. If a device has
more than one sensor, it could be greater than 0.

Output: Fan speed in rpms as integer

Exceptions that can be thrown by `amdsmi_dev_get_fan_rpms` function:
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
            fan_rpm = amdsmi_dev_get_fan_rpms(device, 0)
            print(fan_rpm)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_get_fan_speed
Description: Get the fan speed for the specified device as a value relative to
AMDSMI_MAX_FAN_SPEED

Input parameters:
* `processor_handle` handle for the given device
* `sensor_idx` a 0-based sensor index. Normally, this will be 0. If a device has
more than one sensor, it could be greater than 0.

Output: Fan speed in relative to MAX

Exceptions that can be thrown by `amdsmi_dev_get_fan_speed` function:
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
            fan_speed = amdsmi_dev_get_fan_speed(device, 0)
            print(fan_speed)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_get_fan_speed_max
Description: Get the max fan speed of the device with provided device handle

Input parameters:
* `processor_handle` handle for the given device
* `sensor_idx` a 0-based sensor index. Normally, this will be 0. If a device has
more than one sensor, it could be greater than 0.

Output: Max fan speed as integer

Exceptions that can be thrown by `amdsmi_dev_get_fan_speed_max` function:
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
            max_fan_speed = amdsmi_dev_get_fan_speed_max(device, 0)
            print(max_fan_speed)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_dev_get_temp_metric
Description: Get the temperature metric value for the specified metric, from the
specified temperature sensor on the specified device

Input parameters:
* `processor_handle` handle for the given device
* `sensor_type` part of device from which temperature should be obtained
* `metric` enum indicated which temperature value should be retrieved

Output: Temperature as integer in millidegrees Celcius

Exceptions that can be thrown by ` amdsmi_dev_get_temp_metric` function:
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
            temp_metric =  amdsmi_dev_get_temp_metric(device, AmdSmiTemperatureType.EDGE,
                            AmdSmiTemperatureMetric.CURRENT)
            print(temp_metric)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_dev_get_volt_metric
Description: Get the voltage metric value for the specified metric, from the
specified voltage sensor on the specified device

Input parameters:
* `processor_handle` handle for the given device
* `sensor_type` part of device from which voltage should be obtained
* `metric` enum indicated which voltage value should be retrieved

Output: Voltage as integer in millivolts

Exceptions that can be thrown by ` amdsmi_dev_get_volt_metric` function:
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
            voltage =  amdsmi_dev_get_volt_metric(device, AmdSmiVoltageType.VDDGFX,
                        AmdSmiVoltageMetric.AVERAGE)
            print(voltage)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_get_busy_percent
Description: Get percentage of time device is busy doing any processing

Input parameters:
* `processor_handle` handle for the given device

Output: How busy the device is (as percentage of time)

Exceptions that can be thrown by `amdsmi_dev_get_busy_percent` function:
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
            busy = amdsmi_dev_get_busy_percent(dev)
            print(busy)
except AmdSmiException as e:
    print(e)
```
## amdsmi_get_utilization_count
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
## amdsmi_dev_get_perf_level
Description: Get the performance level of the device with provided device handle

Input parameters:
* `processor_handle` handle for the given device

Output: Performance level as enum value of dev_perf_level_t

Exceptions that can be thrown by `amdsmi_dev_get_perf_level` function:
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
            perf_level = amdsmi_dev_get_perf_level(dev)
            print(perf_level)
except AmdSmiException as e:
    print(e)
```
## amdsmi_set_perf_determinism_mode
Description: Enter performance determinism mode with provided device handle

Input parameters:
* `processor_handle` handle for the given device
* `clkvalue` softmax value for GFXCLK in MHz

Output: None

Exceptions that can be thrown by `amdsmi_set_perf_determinism_mode` function:
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
            amdsmi_set_perf_determinism_mode(device, 1333)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_get_overdrive_level
Description: Get the overdrive percent associated with the device with provided
device handle

Input parameters:
* `processor_handle` handle for the given device

Output: Overdrive percentage as integer

Exceptions that can be thrown by `amdsmi_dev_get_overdrive_level` function:
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
            od_level = amdsmi_dev_get_overdrive_level(dev)
            print(od_level)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_dev_get_gpu_clk_freq
Description: Get the list of possible system clock speeds of device for a
specified clock type

Input parameters:
* `processor_handle` handle for the given device
* `clk_type` the type of clock for which the frequency is desired

Output: Dictionary with fields

Field | Description
---|---
`num_supported`| The number of supported frequencies
`current`| The current frequency index
`frequency`| List of frequencies, only the first num_supported frequencies are valid

Exceptions that can be thrown by ` amdsmi_dev_get_gpu_clk_freq` function:
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
             amdsmi_dev_get_gpu_clk_freq(device, AmdSmiClkType.SYS)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_dev_get_od_volt_info
Description: This function retrieves the voltage/frequency curve information

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


Exceptions that can be thrown by ` amdsmi_dev_get_od_volt_info` function:
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
             amdsmi_dev_get_od_volt_info(dev)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_dev_get_gpu_metrics_info
Description: This function retrieves the gpu metrics information

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
`mem_actvity_acc` | mem activity acc
`temperature_hbm` | hbm temperature

Exceptions that can be thrown by ` amdsmi_dev_get_gpu_metrics_info` function:
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
             amdsmi_dev_get_gpu_metrics_info(dev)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_dev_get_od_volt_curve_regions
Description: This function will retrieve the current valid regions in the
frequency/voltage space

Input parameters:
* `processor_handle` handle for the given device
* `num_regions` number of freq volt regions

Output: List containing a dictionary with fields for each freq volt region

Field | Description
---|---
`freq_range` | <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound freq range</td></tr><tr><td>`upper_bound`</td><td>upper bound freq range</td></tr></tbody></table>
`volt_range` |  <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound volt range</td></tr><tr><td>`upper_bound`</td><td>upper bound volt range</td></tr></tbody></table>

Exceptions that can be thrown by ` amdsmi_dev_get_od_volt_curve_regions` function:
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
             amdsmi_dev_get_od_volt_curve_regions(device, 3)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_dev_get_power_profile_presets
Description:  Get the list of available preset power profiles and an indication of
which profile is currently active

Input parameters:
* `processor_handle` handle for the given device
* `sensor_idx` number of freq volt regions

Output: Dictionary with fields

Field | Description
---|---
`available_profiles`| Which profiles are supported by this system
`current`| Which power profile is currently active
`num_profiles`| How many power profiles are available

Exceptions that can be thrown by ` amdsmi_dev_get_power_profile_presets` function:
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
             amdsmi_dev_get_power_profile_presets(device, 0)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_counter_group_supported
Description: Tell if an event group is supported by a given device

Input parameters:

* `processor_handle` device which to query
* `event_group` event group being checked for support

Output: None

Exceptions that can be thrown by `amdsmi_dev_counter_group_supported` function:
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
            amdsmi_dev_counter_group_supported(device, AmdSmiEventGroup.XGMI)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_create_counter
Description: Creates a performance counter object

Input parameters:

* `processor_handle` device which to query
* `event_type` event group being checked for support

Output: An event handle of the newly created performance counter object

Exceptions that can be thrown by `amdsmi_dev_create_counter` function:
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
            event_handle = amdsmi_dev_create_counter(device, AmdSmiEventGroup.XGMI)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_destroy_counter
Description: Destroys a performance counter object

Input parameters:

* `event_handle` event handle of the performance counter object

Output: None

Exceptions that can be thrown by `amdsmi_dev_destroy_counter` function:
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
            event_handle = amdsmi_dev_create_counter(device, AmdSmiEventGroup.XGMI)
            amdsmi_dev_destroy_counter(event_handle)
except AmdSmiException as e:
    print(e)
```
## amdsmi_control_counter
Description: Issue performance counter control commands

Input parameters:

* `event_handle` event handle of the performance counter object
* `counter_command` command being passed to counter as AmdSmiCounterCommand

Output: None

Exceptions that can be thrown by `amdsmi_control_counter` function:
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
            event_handle = amdsmi_dev_create_counter(device, AmdSmiEventType.XGMI_1_REQUEST_TX)
            amdsmi_control_counter(event_handle, AmdSmiCounterCommand.CMD_START)
except AmdSmiException as e:
    print(e)
```
## amdsmi_read_counter
Description: Read the current value of a performance counter

Input parameters:

* `event_handle` event handle of the performance counter object

Output: Dictionary with fields

Field | Description
---|---
`value`| Counter value
`time_enabled`| Time that the counter was enabled in nanoseconds
`time_running`| Time that the counter was running in nanoseconds

Exceptions that can be thrown by `amdsmi_read_counter` function:
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
            event_handle = amdsmi_dev_create_counter(device, AmdSmiEventType.XGMI_1_REQUEST_TX)
            amdsmi_read_counter(event_handle)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_counter_get_available_counters
Description: Get the number of currently available counters

Input parameters:

* `processor_handle` handle for the given device
* `event_group` event group being checked as AmdSmiEventGroup

Output: Number of available counters for the given device of the inputted event group

Exceptions that can be thrown by ` amdsmi_counter_get_available_counters` function:
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
            available_counters =  amdsmi_counter_get_available_counters(device, AmdSmiEventGroup.XGMI)
            print(available_counters)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_dev_set_perf_level
Description: Set a desired performance level for given device

Input parameters:
* `processor_handle` handle for the given device
* `perf_level` performance level being set as AmdSmiDevPerfLevel

Output: None

Exceptions that can be thrown by ` amdsmi_dev_set_perf_level` function:
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
             amdsmi_dev_set_perf_level(device, AmdSmiDevPerfLevel.STABLE_PEAK)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_dev_get_power_profile_presets
Description: Get the list of available preset power profiles and an indication of
which profile is currently active.

Input parameters:
* `processor_handle` handle for the given device
* `sensor_idx` sensor index as integer

Output: Dictionary with fields

Field | Description
---|---
`available_profiles`| Which profiles are supported by this system
`current`| Which power profile is currently active
`num_profiles`| How many power profiles are available

Exceptions that can be thrown by ` amdsmi_dev_get_power_profile_presets` function:
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
            status =  amdsmi_dev_get_power_profile_presets(device, 0)
            print(status)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_reset_gpu
Description: Reset the gpu associated with the device with provided device handle

Input parameters:
* `processor_handle` handle for the given device

Output: None

Exceptions that can be thrown by `amdsmi_dev_reset_gpu` function:
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
            amdsmi_dev_reset_gpu(device)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_set_fan_speed
Description: Set the fan speed for the specified device with the provided speed,
in RPMs

Input parameters:
* `processor_handle` handle for the given device
* `sensor_idx` sensor index as integer
* `fan_speed` the speed to which the function will attempt to set the fan

Output: None

Exceptions that can be thrown by `amdsmi_dev_set_fan_speed` function:
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
            amdsmi_dev_set_fan_speed(device, 0, 1333)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_reset_fan
Description: Reset the fan to automatic driver control

Input parameters:
* `processor_handle` handle for the given device
* `sensor_idx` sensor index as integer

Output: None

Exceptions that can be thrown by `amdsmi_dev_reset_fan` function:
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
            amdsmi_dev_reset_fan(device, 0)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_dev_set_clk_freq
Description: Control the set of allowed frequencies that can be used for the
specified clock

Input parameters:
* `processor_handle` handle for the given device
* `clk_type` the type of clock for which the set of frequencies will be modified
as AmdSmiClkType
* `freq_bitmask`  bitmask indicating the indices of the frequencies that are to
be enabled (1) and disabled (0). Only the lowest ::amdsmi_frequencies_t.num_supported
bits of this mask are relevant.

Output: None

Exceptions that can be thrown by ` amdsmi_dev_set_clk_freq` function:
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
             amdsmi_dev_set_clk_freq(device, AmdSmiClkType.GFX, freq_bitmask)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_dev_set_overdrive_level_v1
Description: Set the overdrive percent associated with the device with provided
device handle with the provided value

Input parameters:
* `processor_handle` handle for the given device
* `overdrive_value` value to which the overdrive level should be set

Output: None

Exceptions that can be thrown by ` amdsmi_dev_set_overdrive_level_v1` function:
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
             amdsmi_dev_set_overdrive_level_v1(device, 0)
except AmdSmiException as e:
    print(e)
```
##  amdsmi_dev_set_overdrive_level
Description: **deprecated** Set the overdrive percent associated with the
device with provided device handle with the provided value

Input parameters:
* `processor_handle` handle for the given device
* `overdrive_value` value to which the overdrive level should be set

Output: None

Exceptions that can be thrown by ` amdsmi_dev_set_overdrive_level` function:
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
             amdsmi_dev_set_overdrive_level(device, 0)
except AmdSmiException as e:
    print(e)
```

##  amdsmi_dev_get_ecc_count
Description: Retrieve the error counts for a GPU block

Input parameters:
* `processor_handle` handle for the given device
* `block` The block for which error counts should be retrieved

Output: Dict containing information about error counts

Field | Description
---|---
`correctable_count`| Count of correctable errors
`uncorrectable_count`| Count of uncorrectable errors

Exceptions that can be thrown by ` amdsmi_dev_get_ecc_count` function:
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
            ecc_count =  amdsmi_dev_get_ecc_count(device, AmdSmiGpuBlock.UMC)
            print(ecc_count)
except AmdSmiException as e:
    print(e)
```

##  amdsmi_dev_get_ecc_enabled
Description: Retrieve the enabled ECC bit-mask

Input parameters:
* `processor_handle` handle for the given device

Output: Enabled ECC bit-mask

Exceptions that can be thrown by ` amdsmi_dev_get_ecc_enabled` function:
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
            enabled =  amdsmi_dev_get_ecc_enabled(device)
            print(enabled)
except AmdSmiException as e:
    print(e)
```

##  amdsmi_dev_get_ecc_status
Description: Retrieve the ECC status for a GPU block

Input parameters:
* `processor_handle` handle for the given device
* `block` The block for which ECC status should be retrieved

Output: ECC status for a requested GPU block

Exceptions that can be thrown by ` amdsmi_dev_get_ecc_status` function:
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
            status =  amdsmi_dev_get_ecc_status(device, AmdSmiGpuBlock.UMC)
            print(status)
except AmdSmiException as e:
    print(e)
```

## amdsmi_status_string
Description: Get a description of a provided AMDSMI error status

Input parameters:
* `status` The error status for which a description is desired

Output: String description of the provided error code

Exceptions that can be thrown by `amdsmi_status_string` function:
* `AmdSmiParameterException`

Example:
```python
try:
    status_str = amdsmi_status_string(ctypes.c_uint32(0))
    print(status_str)
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_compute_process_info
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

Exceptions that can be thrown by `amdsmi_get_compute_process_info` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`

Example:
```python
try:
    procs = amdsmi_get_compute_process_info()
    for proc in procs:
        print(proc)
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_compute_process_info_by_pid
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

Exceptions that can be thrown by `amdsmi_get_compute_process_info_by_pid` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    pid = 0 # << valid pid here
    proc = amdsmi_get_compute_process_info_by_pid(pid)
    print(proc)
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_compute_process_gpus
Description: Get the device indices currently being used by a process

Input parameters:
* `pid` The process id of the process for which the number of gpus currently being used is requested

Output: List of indices of devices currently being used by the process

Exceptions that can be thrown by `amdsmi_get_compute_process_gpus` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    pid = 0 # << valid pid here
    indices = amdsmi_get_compute_process_gpus(pid)
    print(indices)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_xgmi_error_status
Description: Retrieve the XGMI error status for a device

Input parameters:
* `processor_handle` handle for the given device

Output: XGMI error status for a requested device

Exceptions that can be thrown by `amdsmi_dev_xgmi_error_status` function:
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
            status = amdsmi_dev_xgmi_error_status(device)
            print(status)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_reset_xgmi_error
Description: Reset the XGMI error status for a device

Input parameters:
* `processor_handle` handle for the given device

Output: None

Exceptions that can be thrown by `amdsmi_dev_reset_xgmi_error` function:
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
            amdsmi_dev_reset_xgmi_error(device)
except AmdSmiException as e:
    print(e)
```
## amdsmi_get_gpu_vendor_name
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

## amdsmi_get_gpu_id
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

## amdsmi_get_gpu_vram_vendor
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

## amdsmi_dev_get_drm_render_minor
Description: Get the drm minor number associated with this device.

Input parameters:

* `processor_handle` device which to query

Output: drm minor number

Exceptions that can be thrown by `amdsmi_dev_get_drm_render_minor` function:
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
            render_minor = amdsmi_dev_get_drm_render_minor(device)
            print(render_minor)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_get_subsystem_id
Description: Get the subsystem device id associated with the device with provided device handle.

Input parameters:

* `processor_handle` device which to query

Output: subsystem device id

Exceptions that can be thrown by `amdsmi_dev_get_subsystem_id` function:
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
            id = amdsmi_dev_get_subsystem_id(device)
            print(id)
except AmdSmiException as e:
    print(e)
```


## amdsmi_dev_get_subsystem_name
Description: Get the name string for the device subsytem

Input parameters:

* `processor_handle` device which to query

Output: device subsytem

Exceptions that can be thrown by `amdsmi_dev_get_subsystem_name` function:
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
            subsystem_nam = amdsmi_dev_get_subsystem_name(device)
            print(subsystem_nam)
except AmdSmiException as e:
    print(e)
```


## amdsmi_get_version
Description: Get the build version information for the currently running build of AMDSMI.

Output: amdsmi build version

Exceptions that can be thrown by `amdsmi_get_version` function:
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
            version = amdsmi_get_version()
            print(version)
except AmdSmiException as e:
    print(e)
```


## amdsmi_get_version_str
Description: Get the driver version string for the current system.

Input parameters:

* `sw_component` software component which to query

Output: driver version string

Exceptions that can be thrown by `amdsmi_get_version_str` function:
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
            version = amdsmi_get_version_str(AmdSmiSwComponent.DRIVER)
            print(version)
except AmdSmiException as e:
    print(e)
```


## amdsmi_topo_get_numa_node_number
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

## amdsmi_topo_get_link_weight
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


##  amdsmi_get_minmax_bandwidth
Description: Retreive minimal and maximal io link bandwidth between 2 GPUs.

Input parameters:

* `processor_handle_src` the source device handle
* `processor_handle_dest` the destination device handle

Output:  Dictionary with fields:

Field | Description
---|---
`min_bandwidth` | minimal bandwidth for the connection
`max_bandwidth` | maximal bandwidth for the connection

Exceptions that can be thrown by ` amdsmi_get_minmax_bandwidth` function:
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
        bandwith =  amdsmi_get_minmax_bandwidth(processor_handle_src, processor_handle_dest)
        print(bandwith['min_bandwidth'])
        print(bandwith['max_bandwidth'])
except AmdSmiException as e:
    print(e)
```


## amdsmi_topo_get_link_type
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


## amdsmi_is_P2P_accessible
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


## amdsmi_get_xgmi_info
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

# Requirements
* python 3.6 64-bit
* driver must be loaded for gpuvsmi_init() to pass

# Overview
## Folder structure:
File Name | Note
---|---
`__init__.py` | Python package initialization file
`smi_interface.py` | Smi library python interface
`smi_wrapper.py` | Python wrapper around smi binary
`smi_exception.py` | Smi exceptions python file
`README.md` | Documentation

## Usage:

`amdsmi` folder should be copied and placed next to importing script. It should be imported as:
```python
from amdsmi import *

try:
    gpuvsmi_init()

    # amdsmi calls ...

except SmiException as e:
    print(e)
finally:
    try:
        gpuvsmi_fini()
    except SmiException as e:
        print(e)
```

To initialize smi lib, gpuvsmi_init() must be called before all other calls to smi lib.

To close connection to driver, gpuvsmi_fini() must be the last call.

# Exceptions

All exceptions are in `smi_exception.py` file.
Exceptions that can be thrown are:
* `SmiException`: base smi exception class
* `SmiLibraryException`: derives base `SmiException` class and represents errors that can occur in smi-lib.
When this exception is thrown, `err_code` and `err_info` are set. `err_code` is an integer that corresponds to errors that can occur
in smi-lib and `err_info` is a string that explains the error that occurred.
Example:
```python
try:
    num_of_GPUs = gpuvsmi_get_device_count()
    if num_of_GPUs == 0:
        print("No GPUs on machine")
except SmiException as e:
    print("Error code: {}".format(e.err_code))
    if e.err_code == SmiRetCode.ERR_RETRY:
        print("Error info: {}".format(e.err_info))
```
* `SmiRetryException` : Derives `SmiLibraryException` class and signals device is busy and call should be retried.
* `SmiTimeoutException` : Derives `SmiLibraryException` class and represents that call had timed out.
* `SmiParameterException`: Derives base `SmiException` class and represents errors related to invaild parameters passed to functions. When this exception is thrown, err_msg is set and it explains what is the actual and expected type of the parameters.
* `SmiBdfFormatException`: Derives base `SmiException` class and represents invalid bdf format.

# API

## gpuvsmi_init
Description: Initialize smi lib and connect to driver

Input parameters: `None`

Output: `None`

Exceptions that can be thrown by `gpuvsmi_init` function:
* `SmiLibraryException`

Example:
```python
try:
    gpuvsmi_init()
    # continue with amdsmi
except SmiException as e:
    print("Init failed")
    print(e)
```

## gpuvsmi_fini
Description: Finalize and close connection to driver

Input parameters: `None`

Output: `None`

Exceptions that can be thrown by `gpuvsmi_fini` function:
* `SmiLibraryException`

Example:
```python
try:
    gpuvsmi_fini()
except SmiException as e:
    print("Fini failed")
    print(e)
```

## gpuvsmi_get_device_count
Description: Returns number of GPUs on current machine

Input parameters: `None`

Output: Integer, number of GPUs

Exceptions that can be thrown by `gpuvsmi_get_device_count` function:
* `SmiLibraryException`

Example:
```python
try:
    num_of_GPUs = gpuvsmi_get_device_count()
    if num_of_GPUs == 0:
        print("No GPUs on machine")
except SmiException as e:
    print(e)
```

## gpuvsmi_get_devices
Description: Returns list of GPU device handle objects on current machine

Input parameters: `None`

Output: List of GPU device handle objects

Exceptions that can be thrown by `gpuvsmi_get_devices` function:
* `SmiLibraryException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            print(gpuvsmi_get_device_uuid(device))
except SmiException as e:
    print(e)
```

## gpuvsmi_get_device_handle
Description: Returns device handle from the given BDF

Input parameters: bdf string in form of either `<domain>:<bus>:<device>.<function>` or `<bus>:<device>.<function>` in hexcode format.
Where:
* `<domain>` is 4 hex digits long from 0000-FFFF interval
* `<bus>` is 2 hex digits long from 00-FF interval
* `<device>` is 2 hex digits long from 00-1F interval
* `<function>` is 1 hex digit long from 0-7 interval

Output: device handle object

Exceptions that can be thrown by `gpuvsmi_get_device_handle` function:
* `SmiLibraryException`
* `SmiBdfFormatException`

Example:
```python
try:
    device = gpuvsmi_get_device_handle("0000:23:00.0")
    print(gpuvsmi_get_device_uuid(device))
except SmiException as e:
    print(e)
```

## gpuvsmi_get_device_bdf
Description: Returns BDF of the given device

Input parameters:
* `device_handle` dev for which to query

Output: BDF string in form of `<domain>:<bus>:<device>.<function>` in hexcode format.
Where:
* `<domain>` is 4 hex digits long from 0000-FFFF interval
* `<bus>` is 2 hex digits long from 00-FF interval
* `<device>` is 2 hex digits long from 00-1F interval
* `<function>` is 1 hex digit long from 0-7 interval

Exceptions that can be thrown by `gpuvsmi_get_device_bdf` function:
* `SmiParameterException`
* `SmiLibraryException`

Example:
```python
try:
    device = gpuvsmi_get_device_handle("0000:23:00.0")
    print("Device's bdf:", gpuvsmi_get_device_bdf(device))
except SmiException as e:
    print(e)
```

## gpuvsmi_get_device_uuid
Description: Returns the UUID of the device

Input parameters:
* `device_handle` dev for which to query

Output: UUID string unique to the device

Exceptions that can be thrown by `gpuvsmi_get_device_uuid` function:
* `SmiParameterException`
* `SmiLibraryException`

Example:
```python
try:
    device = gpuvsmi_get_device_handle("0000:23:00.0")
    print("Device UUID: ", gpuvsmi_get_device_uuid(device))
except SmiException as e:
    print(e)
```

## gpuvsmi_get_driver_version
Description: Returns the version string of the driver

Input parameters:
* `device_handle` dev for which to query

Output: Driver version string that is handling the device

Exceptions that can be thrown by `gpuvsmi_get_driver_version` function:
* `SmiParameterException`
* `SmiLibraryException`

Example:
```python
try:
    device = gpuvsmi_get_device_handle("0000:23:00.0")
    print("Driver version: ", gpuvsmi_get_driver_version(device))
except SmiException as e:
    print(e)
```

## gpuvsmi_get_asic_info
Description: Returns asic information for the given GPU

Input parameters:
* `device_handle` device which to query

Output: Dictionary with fields

Field | Content
---|---
`market_name` |  market name
`family` |  family
`vendor_id` |  vendor id
`device_id` |  device id
`rev_id` |  revision id

Exceptions that can be thrown by `gpuvsmi_get_asic_info` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            asic_info = gpuvsmi_get_asic_info(device)
            print(asic_info['market_name'])
            print(hex(asic_info['family']))
            print(hex(asic_info['vendor_id']))
            print(hex(asic_info['device_id']))
            print(hex(asic_info['rev_id']))
except SmiException as e:
    print(e)
```

## gpuvsmi_get_bus_info
Description: Returns bus information for the given GPU

Input parameters:
* `device_handle` device which to query

Output: Dictionary with `pcie` and `xgmi` fields and its subfields

Field | Content
---|---
`pcie` | <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`bdf`</td><td>bdf string</td></tr><tr><td>`pcie_link_speed`</td><td>pcie speed in MT/s</td></tr><tr><td>`pcie_link_width`</td><td>pcie_lanes</td></tr></tbody></table>
`xgmi` |  <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`xgmi_lanes`</td><td>xgmi lanes</td></tr> <tr><td>`xgmi_hive_id`</td><td>xgmi hive id</td></tr><tr><td>`xgmi_node_id`</td><td>xgmi node id</td></tr><tr><td>`index`</td><td>xgmi index</td></tr></tbody></table>

Exceptions that can be thrown by `gpuvsmi_get_bus_info` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            bus_info = gpuvsmi_get_bus_info(device)
            print(bus_info['pcie']['bdf'])
            print(bus_info['pcie']['pcie_link_speed'])
            print(bus_info['pcie']['pcie_link_width'])
            print(bus_info['xgmi']['xgmi_lanes'])
            print(bus_info['xgmi']['xgmi_hive_id'])
            print(bus_info['xgmi']['xgmi_node_id'])
            print(bus_info['xgmi']['index'])
except SmiException as e:
    print(e)
```

## gpuvsmi_get_power_info
Description: Returns dictionary of power capabilities as currently configured
on the given GPU

Input parameters:
* `device_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`dpm_cap` |  dynamic power management capability
`power_cap` |  power capability

Exceptions that can be thrown by `gpuvsmi_get_power_info` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            power_info = gpuvsmi_get_power_info(device)
            print(power_info['dpm_cap'])
            print(power_info['power_cap'])
except SmiException as e:
    print(e)
```

## gpuvsmi_get_caps_info
Description: Returns capabilities as currently configured for the given GPU

Input parameters:
* `device_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
 `ras_supported` |  `True` if ecc is supported, `False` if not
 `mm_list` |  List of MM engines on the device, of SmiMmIp type
 `gfx_ip_count` |  Number of GFX engines on the device
 `dma_ip_count` | Number of DMA engines on the device
 `gfx` | <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`gfxip_major`</td><td> major revision of GFX IP</td></tr><tr><td>`gfxip_minor`</td><td>minor revision of GFX IP</td></tr><tr><td>`gfxip_cu_count`</td><td>number of GFX compute units</td></tr></tbody></table>
`supported_flags` | <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td> `xgmi` </td><td> `True` if xgmi is supported, `False` if not</td></tr><tr><td>`mm_metrics`</td><td>`True` if mm metrics is supported, `False` if not</td></tr><tr><td>`power_gfx_voltage`</td><td>`True` if gfx voltage is supported, `False` if not</td></tr><tr><td>`power_dpm`</td><td>`True` if dpm is supported, `False` if not</td></tr><tr><td>`mem_usage`</td><td>`True` if mem usage is supported, `False` if not</td></tr><tr><td>`max_freq_target_range`</td><td>`True` if target frequency setting is supported, `False` if not</td></tr></tbody></table>

Exceptions that can be thrown by `gpuvsmi_get_caps_info` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            caps_info =  gpuvsmi_get_caps_info(device)
            print(caps_info['ras_supported'])
            print(caps_info['gfx']['gfxip_major'])
            print(caps_info['gfx']['gfxip_minor'])
            print(caps_info['gfx']['gfxip_cu_count'])
            print(caps_info['mm_list'])
            print(caps_info['gfx_ip_count'])
            print(caps_info['dma_ip_count'])
            print(caps_info['supported_flags']['xgmi'])
            print(caps_info['supported_flags']['mm_metrics'])
            print(caps_info['supported_flags']['power_gfx_voltage'])
            print(caps_info['supported_flags']['power_dpm'])
            print(caps_info['supported_flags']['mem_usage'])
            print(caps_info['supported_flags']['max_freq_target_range'])
except SmiException as e:
    print(e)
```

## gpuvsmi_get_vbios_info
Description:  Returns the static information for the VBIOS on the device.

Input parameters:
* `device_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`vbios_part_number` | vbios part number
`vbios_build_date` | vbios build date
`vbios_version` | vbios current version
`vbios_name` | vbios name
`vbios_version_string` | vbios version string

Exceptions that can be thrown by `gpuvsmi_get_vbios_info` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            vbios_info = gpuvsmi_get_vbios_info(device)
            print(vbios_info['vbios_part_number'])
            print(vbios_info['vbios_build_date'])
            print(vbios_info['vbios_version'])
            print(vbios_info['vbios_name'])
            print(vbios_info['vbios_version_string'])
except SmiException as e:
    print(e)
```

## gpuvsmi_get_ucode_info
Description:  Returns GPU microcode related information.

Input parameters:
* `device_handle` device which to query

Output: Dictionary with field `ucode_list`, which is a list of dictionary elements:

Field | Description
---|---
`ucode_list` | <table>  <thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`ucode_name`</td><td>`SmiUcodeName` enum</td></tr><tr><td>`ucode_version_integer`</td><td>ucode version which is integer</td></tr></tbody></table>

If microcode of certain type is not loaded, version will be 0.

Exceptions that can be thrown by `gpuvsmi_get_ucode_info` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            ucode_info = gpuvsmi_get_ucode_info(device)
            ucode_num = len(ucode_info['ucode_list'])
            for j in range(0, ucode_num):
                ucode = ucode_info['ucode_list'][j]
                print(ucode['ucode_name'].name)
                print(ucode['ucode_version_integer'])
except SmiException as e:
    print(e)
```

## gpuvsmi_get_gpu_activity
Description: Returns the engine usage for the given GPU

Input parameters:
* `device_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`gfx_usage`| graphics engine usage percentage (0 - 100)
`mem_usage` | memory engine usage percentage (0 - 100)
`mm_usage_list` | list of multimedia engine usages in percentage (0 - 100)

Exceptions that can be thrown by `gpuvsmi_get_gpu_activity` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            engine_usage = gpuvsmi_get_gpu_activity(device)
            print(engine_usage['gfx_usage'])
            print(engine_usage['mem_usage'])
            print(engine_usage['mm_usage_list'])
except SmiException as e:
    print(e)
```
## gpuvsmi_get_power_measure
Description: Returns the current power and voltage for the given GPU

Input parameters:
* `device_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`current_power_usage`| current power
`current_voltage` | current voltage gfx
`current_voltage_soc` | current voltage soc
`current_voltage_mem` | current voltage mem
`current_fan_rpm` | current fan speed

Exceptions that can be thrown by `gpuvsmi_get_power_measure` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            power_measure = gpuvsmi_get_power_measure(device)
            print(power_measure['current_power_usage'])
            print(power_measure['current_voltage'])
            print(power_measure['current_voltage_soc'])
            print(power_measure['current_voltage_mem'])
            print(power_measure['current_fan_rpm'])
except SmiException as e:
    print(e)
```
## gpuvsmi_get_thermal_measure
Description: Returns the measurements of thermals for the given GPU

Input parameters:

* `device_handle` device which to query
* `thermal_domain` one of `SmiThermalDomain` enum values:

Field | Description
---|---
`EDGE` | edge thermal domain
`HOTSPOT` | hotspot thermal domain
`MEM` | memory thermal domain
`PLX` | plx thermal domain

Output: Dictionary with fields

Field | Description
---|---
`temperature`| temperature value for the given thermal domain

Exceptions that can be thrown by `gpuvsmi_get_thermal_measure` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            thermal_measure = gpuvsmi_get_thermal_measure(device, SmiThermalDomain.EDGE)
            print(thermal_measure['temperature'])
except SmiException as e:
    print(e)
```

## gpuvsmi_get_power_limit
Description: Returns the power limit for the given GPU

Input parameters:
* `device handle object` PF or child VF of a device for which to query

Output: Dictionary with fields

Field | Description
---|---
`power_limit`| power limit

Exceptions that can be thrown by `gpuvsmi_get_power_limit` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            power_limit = gpuvsmi_get_power_limit(device)
            print(power_limit['power_limit'])

except SmiException as e:
    print(e)
```

## gpuvsmi_get_thermal_limit
Description: Returns the temperature limits of thermals for the given GPU

Input parameters:

* `device handle object` PF or child VF of a device for which to query
* `SmiThermalDomain enum object with values`

Field | Description
---|---
`EDGE` | edge thermal domain
`HOTSPOT` | hotspot thermal domain
`MEM` | memory thermal domain

Output: Dictionary with fields

Field | Description
---|---
`temperature`| temperature limit for the given thermal domain

Exceptions that can be thrown by `gpuvsmi_get_thermal_limit` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            thermal_limit = gpuvsmi_get_thermal_limit(device, SmiThermalDomain.EDGE)
            print(thermal_limit['temperature'])
except SmiException as e:
    print(e)
```

## gpuvsmi_get_clock_measure
Description: Returns the clock measurements for the given GPU

Input parameters:

* `device_handle` device which to query
* `clock_domain` one of `SmiClockDomain` enum values:

Field | Description
---|---
`GFX` | gfx clock domain
`MEM` | memory clock domain
`MM1` | first multimedia engine clock domain
`MM2` | second multimedia engine clock domain

Output: Dictionary with fields

Field | Description
---|---
`cur_clk`| current clock value for the given domain

Exceptions that can be thrown by `gpuvsmi_get_clock_measure` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            print("=============== GFX DOMAIN ================")
            clock_measure = gpuvsmi_get_clock_measure(device, SmiClockDomain.GFX)
            print(clock_measure['cur_clk'])
            print("=============== MEM DOMAIN ================")
            clock_measure = gpuvsmi_get_clock_measure(device, SmiClockDomain.MEM)
            print(clock_measure['cur_clk'])
            print("=============== MM1 engine DOMAIN ================")
            clock_measure = gpuvsmi_get_clock_measure(device, SmiClockDomain.MM1)
            print(clock_measure['cur_clk'])
except SmiException as e:
    print(e)
```

## gpuvsmi_get_pcie_link_status
Description:  Returns current PCIe configuration

Input parameters:
* `device_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`lanes` | Number of PCIe lanes
`speed` | PCIe speed in MT/s

Exceptions that can be thrown by `gpuvsmi_get_pcie_link_status` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            pcie_status = gpuvsmi_get_pcie_link_status(device)
            print(pcie_status['lanes'])
            print(pcie_status['speed'])
except SmiException as e:
    print(e)
```

## gpuvsmi_get_fb_usage
Description:  Returns current framebuffer usage

Input parameters:
* `device_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`total` | Total FB size in MBs
`used` | Used FB size in MBs

Exceptions that can be thrown by `gpuvsmi_get_fb_usage` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            fb_usage = gpuvsmi_get_fb_usage(device)
            print(fb_usage['total'])
            print(fb_usage['used'])
except SmiException as e:
    print(e)
```

## gpuvsmi_get_target_frequency_supported_range
Description: Returns the supported frequency target range

`Note: Not Supported`

Input parameters:

* `device_handle` device which to query
* `clock_domain` one of `SmiClockDomain` enum values:

Field | Description
---|---
`GFX` | gfx clock domain
`MEM` | memory clock domain
`MM1` | first multimedia engine clock domain
`MM2` | second multimedia engine clock domain

Output: Dictionary with fields

Field | Description
---|---
`soft_min`| Minimal value of target frequency in MHz
`soft_max`| Maximal value of target frequency in MHz

Exceptions that can be thrown by `gpuvsmi_get_target_frequency_supported_range` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            print("=============== GFX DOMAIN ================")
            freq_range = gpuvsmi_get_target_frequency_supported_range(device,
                SmiClockDomain.GFX)
            print(freq_range['soft_min'])
            print(freq_range['soft_max'])
            print("=============== MEM DOMAIN ================")
            freq_range = gpuvsmi_get_target_frequency_supported_range(device,
                SmiClockDomain.MEM)
            print(freq_range['soft_min'])
            print(freq_range['soft_max'])
            print("=============== MM1 engine DOMAIN ================")
            freq_range = gpuvsmi_get_target_frequency_supported_range(device,
                SmiClockDomain.MM1)
            print(freq_range['soft_min'])
            print(freq_range['soft_max'])
except SmiException as e:
    print(e)
```

## gpuvsmi_get_target_frequency_current_range
Description: Returns the current frequency target range

`Note: Not Supported`

Input parameters:

* `device_handle` device which to query
* `clock_domain` one of `SmiClockDomain` enum values:

Field | Description
---|---
`GFX` | gfx clock domain
`MEM` | memory clock domain
`MM1` | first multimedia engine clock domain
`MM2` | second multimedia engine clock domain

Output: Dictionary with fields

Field | Description
---|---
`soft_min`| Minimal value of target frequency in MHz
`soft_max`| Maximal value of target frequency in MHz

Exceptions that can be thrown by `gpuvsmi_get_target_frequency_current_range` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            print("=============== GFX DOMAIN ================")
            freq_range = gpuvsmi_get_target_frequency_current_range(device,
                SmiClockDomain.GFX)
            print(freq_range['soft_min'])
            print(freq_range['soft_max'])
            print("=============== MEM DOMAIN ================")
            freq_range = gpuvsmi_get_target_frequency_current_range(device,
                SmiClockDomain.MEM)
            print(freq_range['soft_min'])
            print(freq_range['soft_max'])
            print("=============== MM1 engine DOMAIN ================")
            freq_range = gpuvsmi_get_target_frequency_current_range(device,
                SmiClockDomain.MM1)
            print(freq_range['soft_min'])
            print(freq_range['soft_max'])
except SmiException as e:
    print(e)
```


## gpuvsmi_get_process_list
Description: Returns the list of processes running on a device

Input parameters:

* `device_handle` device which to query

Output: List of process handles

Exceptions that can be thrown by `gpuvsmi_get_process_list` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            proc_list = gpuvsmi_get_process_list(device)
            print(proc_list)
except SmiException as e:
    print(e)
```

## gpuvsmi_get_process_info
Description: Returns the process information of a given process

Input parameters:

* `device_handle` device which to query
* `procces_handle` handle of process to query

Output: Dictionary with fields

Field | Description
---|---
`name`| Process name
`pid`| Process ID
`mem`| Process memory usage
`flags`| <table><thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`has_usage_metrics`</td><td>True if engine usage metrics are available</td></tr><tr><td>`has_compute_metrics`</td><td>True if compute metrics are available</td></tr></tbody></table>
`usage`| <table><thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`gfx`</td><td>GFX engine usage</td></tr><tr><td>`compute`</td><td>Compute engine usage</td></tr><tr><td>`sdma`</td><td>DMA engine usage</td></tr><tr><td>`enc`</td><td>Encode engine usage</td></tr><tr><td>`dec`</td><td>Decode engine usage</td></tr></tbody></table>
`memory_usage`| <table><thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`gtt_mem`</td><td>GTT memory usage</td></tr><tr><td>`cpu_mem`</td><td>CPU memory usage</td></tr><tr><td>`vram_mem`</td><td>VRAM memory usage</td></tr> </tbody></table>


Exceptions that can be thrown by `gpuvsmi_get_process_info` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            proc_list = gpuvsmi_get_process_list(device)
            for proc in proc_list:
                proc_info = gpuvsmi_get_process_info(device, proc)
                print(proc_info['name'])
                print(proc_info['pid'])
                print(proc_info['mem'])
                print(proc_info['flags']['has_usage_metrics'])
                print(proc_info['flags']['has_compute_metrics'])
                print(proc_info['usage']['gfx'])
                print(proc_info['usage']['compute'])
                print(proc_info['usage']['sdma'])
                print(proc_info['usage']['enc'])
                print(proc_info['usage']['dec'])
                print(proc_info['memory_usage']['gtt_mem'])
                print(proc_info['memory_usage']['cpu_mem'])
                print(proc_info['memory_usage']['vram_mem'])
except SmiException as e:
    print(e)
```

## gpuvsmi_get_ecc_error_count
Description: Returns dictionary of ecc error counts

Input parameters:

* `device_handle` device which to query

Output:  Dictionary with fields correctable and uncorrectable

Field | Description
---|---
`correctable`| Count of ecc correctable errors since last time driver was loaded
`uncorrectable`| Count of ecc uncorrectable errors since last time driver was loaded

Exceptions that can be thrown by `gpuvsmi_get_ecc_error_count` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    device = gpuvsmi_get_device_handle("0000:23.00.0")
    ecc_count_dict = gpuvsmi_get_ecc_error_count(device)
    if ecc_count_dict["correctable"] == 0 and ecc_count_dict["uncorrectable"] == 0:
        print("no errors")
except SmiException as e:
    print(e)
```

## gpuvsmi_get_ras_features_enabled
Description: Returns status of each block

Input parameters:

* `device_handle` device which to query
* `block` block which to query

Output: Status of block

Exceptions that can be thrown by `gpuvsmi_get_ras_features_enabled` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            block = SmiGpuBlocks.DF
            status = gpuvsmi_get_ras_features_enabled(device, block)
            print(status)
except SmiException as e:
    print(e)
```

## gpuvsmi_get_bad_page_info
Description: Returns the bad page information

Input parameters:

* `device_handle` device which to query

Output: Number of pages and list of bad page records

Field | Description
---|---
`count` | number of pages
`table_records` | <table>  <thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`page_address`</td><td>Address of page</td></tr><tr><td>`page_size`</td><td>Size of page</td></tr><tr><td>`status`</td><td>Status</td></tr></tbody></table>

Exceptions that can be thrown by `gpuvsmi_get_bad_page_info` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            bad_page = gpuvsmi_get_bad_page_info(device)
            print(bad_page)
except SmiException as e:
    print(e)
```

## gpuvsmi_get_board_info
Description: Returns board related information for the given GPU

Input parameters:

* `device_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`serial_number`| board serial number
`product_number`| board product serial number
`product_name`| board product name

Exceptions that can be thrown by `gpuvsmi_get_board_info` function:
* `SmiLibraryException`
* `SmiRetryException`
* `SmiParameterException`

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            board_info = gpuvsmi_get_board_info(device)
            print(board_info)
except SmiException as e:
    print(e)
```

## EventListen class

Description: Providing methods for event monitoring

Methods:

## Constructor

Description: Allocates a new event reader notifier to monitor different types of events with the multiple GPUs

Input parameters:

* `event_types` types of events to monitor and react on

## read

Description: Reads events on GPUs. When event is caught, device handle, event id, message, event type and
             time are returned. Reading events stops when timestamp passes without event reading.

Input parameters:

* `timestamp` Amount of miliseconds to wait for event. If event does not happen monitoring is finished
* `i` GPU index to which we need to listen to events. For example 0,1,2...

Example:
```python
try:
    devices = gpuvsmi_get_devices()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        device = devices[0]
        listener = EventListen(SmiEventType.GPU_PRE_RESET)
        listener.read(10000)
except SmiException as e:
    print(e)
```

## Destructor

Description: Detroys event listener object, closes all open files and directories

Input parameters: `None`


## amdsmi_dev_supported_func_iterator_open
Description: Get a function name iterator of supported AMDSMI functions for a device

Input parameters:

* `device_handle` device which to query

Output: Handle for a function iterator

Exceptions that can be thrown by `amdsmi_dev_supported_func_iterator_open` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            obj_handle = amdsmi_dev_supported_func_iterator_open(device)
            print(obj_handle)
            amdsmi_dev_supported_func_iterator_close(obj_handle)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_supported_variant_iterator_open
Description: Get a variant iterator for a given handle

Input parameters:

* `obj_handle` Object handle for witch to return a variant handle

Output: Variant iterator handle

Exceptions that can be thrown by `amdsmi_dev_supported_variant_iterator_open` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            obj_handle = amdsmi_dev_supported_func_iterator_open(device)
            var_iter = amdsmi_dev_supported_variant_iterator_open(obj_handle)
            print(var_iter)
            amdsmi_dev_supported_func_iterator_close(obj_handle)
            amdsmi_dev_supported_func_iterator_close(var_iter)
except AmdSmiException as e:
    print(e)
```

## amdsmi_func_iter_next
Description: Advance an object identifier iterator

Input parameters:

* `obj_handle` Object handle to advance

Output: Next iterator handle

Exceptions that can be thrown by `amdsmi_func_iter_next` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            obj_handle = amdsmi_dev_supported_func_iterator_open(device)
            print(obj_handle)
            obj_handle = amdsmi_func_iter_next(obj_handle)
            print(obj_handle)
            amdsmi_dev_supported_func_iterator_close(obj_handle)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_supported_func_iterator_close
Description: Close a variant iterator handle

Input parameters:

* `obj_handle` Object handle to be closed

Output: None

Exceptions that can be thrown by `amdsmi_dev_supported_func_iterator_close` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            obj_handle = amdsmi_dev_supported_func_iterator_open(device)
            amdsmi_dev_supported_func_iterator_close(obj_handle)
except AmdSmiException as e:
    print(e)
```

## amdsmi_func_iter_value_get
Description: Get the value associated with a function/variant iterator

Input parameters:

* `obj_handle` Object handle to query

Output: Data associated with a function/variant iterator

Field | Description
---|---
`id`| Internal ID of the function/variant
`name`| Descriptive name of the function/variant
`amd_id_0` | <table>  <thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`memory_type`</td><td>Memory type</td></tr><tr><td>`temp_metric`</td><td>Temperature metric</td></tr><tr><td>`evnt_type`</td><td>Event type</td></tr><tr><td>`evnt_group`</td><td>Event group</td></tr><tr><td>`clk_type`</td><td>Clock type</td></tr></tr><tr><td>`fw_block`</td><td>Firmware block</td></tr><tr><td>`gpu_block_type`</td><td>GPU block type</td></tr></tbody></table>

Exceptions that can be thrown by `amdsmi_func_iter_value_get` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            obj_handle = amdsmi_dev_supported_func_iterator_open(device)
            value = amdsmi_func_iter_value_get(obj_handle)
            print(value)
            amdsmi_dev_supported_func_iterator_close(obj_handle)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_pci_bandwidth_set
Description: Control the set of allowed PCIe bandwidths that can be used

Input parameters:
* `device_handle` handle for the given device
* `bw_bitmask` A bitmask indicating the indices of the bandwidths that are
to be enabled (1) and disabled (0)

Output: None

Exceptions that can be thrown by `amdsmi_dev_pci_bandwidth_set` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_dev_pci_bandwidth_set(device, 0)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_power_cap_set
Description: Set the power cap value

Input parameters:
* `device_handle` handle for the given device
* `sensor_ind` a 0-based sensor index. Normally, this will be 0. If a
device has more than one sensor, it could be greater than 0
* `cap` int that indicates the desired power cap, in microwatts

Output: None

Exceptions that can be thrown by `amdsmi_dev_power_cap_set` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            power_cap = 250 * 1000000
            amdsmi_dev_power_cap_set(device, 0, power_cap)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_power_profile_set
Description: Set the power profile

Input parameters:
* `device_handle` handle for the given device
* `reserved` Not currently used, set to 0
* `profile` a amdsmi_power_profile_preset_masks_t that hold the mask of
the desired new power profile

Output: None

Exceptions that can be thrown by `amdsmi_dev_power_profile_set` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            profile = ...
            amdsmi_dev_power_profile_set(device, 0, profile)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_clk_range_set
Description: This function sets the clock range information

Input parameters:
* `device_handle` handle for the given device
* `min_clk_value` minimum clock value for desired clock range
* `max_clk_value` maximum clock value for desired clock range
* `clk_type`AMDSMI_CLK_TYPE_SYS | AMDSMI_CLK_TYPE_MEM range type

Output: None

Exceptions that can be thrown by `amdsmi_dev_clk_range_set` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_dev_clk_range_set(device, 0, 1000, AmdSmiClockType.AMDSMI_CLK_TYPE_SYS)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_od_clk_info_set
Description: This function sets the clock frequency information

Input parameters:
* `device_handle` handle for the given device
* `level` AMDSMI_FREQ_IND_MIN|AMDSMI_FREQ_IND_MAX to set the minimum (0)
or maximum (1) speed
* `clk_value` value to apply to the clock range
* `clk_type` AMDSMI_CLK_TYPE_SYS | AMDSMI_CLK_TYPE_MEM range type

Output: None

Exceptions that can be thrown by `amdsmi_dev_od_clk_info_set` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_dev_od_clk_info_set(
                device,
                AmdSmiFreqInd.AMDSMI_FREQ_IND_MAX,
                1000,
                AmdSmiClockType.AMDSMI_CLK_TYPE_SYS
            )
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_od_volt_info_set
Description: This function sets  1 of the 3 voltage curve points

Input parameters:
* `device_handle` handle for the given device
* `vpoint` voltage point [0|1|2] on the voltage curve
* `clk_value` clock value component of voltage curve point
* `volt_value` voltage value component of voltage curve point

Output: None

Exceptions that can be thrown by `amdsmi_dev_od_volt_info_set` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_dev_od_volt_info_set(device, 1, 1000, 980)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_perf_level_set_v1
Description: Set the PowerPlay performance level associated with the device
with provided device handle with the provided value

Input parameters:
* `device_handle` handle for the given device
* `perf_lvl` the value to which the performance level should be set

Output: None

Exceptions that can be thrown by `amdsmi_dev_perf_level_set_v1` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            amdsmi_dev_perf_level_set_v1(device, AmdSmiDevPerfLevel.AMDSMI_DEV_PERF_LEVEL_HIGH)
except AmdSmiException as e:
    print(e)
```
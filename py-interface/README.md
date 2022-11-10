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
    num_of_GPUs = len(amdsmi_get_device_handles())
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

## amdsmi_get_device_type
Description: Checks the type of device with provided handle.

Input parameters: device handle as an instance of `amdsmi_device_handle`

Output: Integer, type of gpu

Exceptions that can be thrown by `amdsmi_get_device_type` function:
* `AmdSmiLibraryException`

Example:
```python
try:
    type_of_GPU = amdsmi_get_device_type(device_handle)
    if type_of_GPU == 1:
        print("This is an AMD GPU")
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_device_handles
Description: Returns list of GPU device handle objects on current machine

Input parameters: `None`

Output: List of GPU device handle objects

Exceptions that can be thrown by `amdsmi_get_device_handles` function:
* `AmdSmiLibraryException`

Example:
```python
try:
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            print(amdsmi_get_device_uuid(device))
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_device_handle_from_bdf
Description: Returns device handle from the given BDF

Input parameters: bdf string in form of either `<domain>:<bus>:<device>.<function>` or `<bus>:<device>.<function>` in hexcode format.
Where:
* `<domain>` is 4 hex digits long from 0000-FFFF interval
* `<bus>` is 2 hex digits long from 00-FF interval
* `<device>` is 2 hex digits long from 00-1F interval
* `<function>` is 1 hex digit long from 0-7 interval

Output: device handle object

Exceptions that can be thrown by `amdsmi_get_device_handle_from_bdf` function:
* `AmdSmiLibraryException`
* `AmdSmiBdfFormatException`

Example:
```python
try:
    device = amdsmi_get_device_handle_from_bdf("0000:23:00.0")
    print(amdsmi_get_device_uuid(device))
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_device_bdf
Description: Returns BDF of the given device

Input parameters:
* `device_handle` dev for which to query

Output: BDF string in form of `<domain>:<bus>:<device>.<function>` in hexcode format.
Where:
* `<domain>` is 4 hex digits long from 0000-FFFF interval
* `<bus>` is 2 hex digits long from 00-FF interval
* `<device>` is 2 hex digits long from 00-1F interval
* `<function>` is 1 hex digit long from 0-7 interval

Exceptions that can be thrown by `amdsmi_get_device_bdf` function:
* `AmdSmiParameterException`
* `AmdSmiLibraryException`

Example:
```python
try:
    device = amdsmi_get_device_handles()[0]
    print("Device's bdf:", amdsmi_get_device_bdf(device))
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_device_uuid
Description: Returns the UUID of the device

Input parameters:
* `device_handle` dev for which to query

Output: UUID string unique to the device

Exceptions that can be thrown by `amdsmi_get_device_uuid` function:
* `AmdSmiParameterException`
* `AmdSmiLibraryException`

Example:
```python
try:
    device = amdsmi_get_device_handles()[0]
    print("Device UUID: ", amdsmi_get_device_uuid(device))
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_driver_version
Description: Returns the version string of the driver

Input parameters:
* `device_handle` dev for which to query

Output: Driver version string that is handling the device

Exceptions that can be thrown by `amdsmi_get_driver_version` function:
* `AmdSmiParameterException`
* `AmdSmiLibraryException`

Example:
```python
try:
    device = amdsmi_get_device_handles()[0]
    print("Driver version: ", amdsmi_get_driver_version(device))
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_asic_info
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
`asic_serial` | asic serial

Exceptions that can be thrown by `amdsmi_get_asic_info` function:
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
* `device_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`dpm_cap` |  dynamic power management capability
`power_cap` |  power capability

Exceptions that can be thrown by `amdsmi_get_power_cap_info` function:
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
            power_info = amdsmi_get_power_cap_info(device)
            print(power_info['dpm_cap'])
            print(power_info['power_cap'])
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_caps_info
Description: Returns capabilities as currently configured for the given GPU

Input parameters:
* `device_handle` device which to query

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
    devices = amdsmi_get_device_handles()
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
* `device_handle` device which to query

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
    devices = amdsmi_get_device_handles()
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
* `device_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`FW_ID_SMU` | SMU info
`FW_ID_CP_CE` | CP_CE info
`FW_ID_CP_PFP` | CP_PFP info
`FW_ID_CP_ME` | CP_ME info
`FW_ID_CP_MEC_JT1` | CP_MEC_JT1 info
`FW_ID_CP_MEC_JT2` | CP_MEC_JT2 info
`FW_ID_CP_MEC1` | CP_MEC1 info
`FW_ID_CP_MEC2` | CP_MEC2 info
`FW_ID_RLC` | RLC info
`FW_ID_SDMA0` | SDMA0 info
`FW_ID_SDMA1` | SDMA1 info
`FW_ID_SDMA2` | SDMA2 info
`FW_ID_SDMA3` | SDMA3 info
`FW_ID_SDMA4` | SDMA4 info
`FW_ID_SDMA5` | SDMA5 info
`FW_ID_SDMA6` | SDMA6 info
`FW_ID_SDMA7` | SDMA7 info
`FW_ID_VCN` | VCN info
`FW_ID_UVD` | UVD info
`FW_ID_VCE` | VCE info
`FW_ID_ISP` | ISP info
`FW_ID_DMCU_ERAM` | DMCU_ERAM info
`FW_ID_DMCU_ISR` | DMCU_ISR info
`FW_ID_RLC_RESTORE_LIST_GPM_MEM` | RLC_RESTORE_LIST_GPM_MEM info
`FW_ID_RLC_RESTORE_LIST_SRM_MEM` | RLC_RESTORE_LIST_SRM_MEM info
`FW_ID_RLC_RESTORE_LIST_CNTL` | RLC_RESTORE_LIST_CNTL info
`FW_ID_RLC_V` | RLC_V info
`FW_ID_MMSCH` | MMSCH info
`FW_ID_PSP_SYSDRV` | PSP_SYSDRV info
`FW_ID_PSP_SOSDRV` | PSP_SOSDRV info
`FW_ID_PSP_TOC` | PSP_TOC info
`FW_ID_PSP_KEYDB` | PSP_KEYDB info
`FW_ID_DFC` | DFC info
`FW_ID_PSP_SPL` | PSP_SPL info
`FW_ID_DRV_CAP` | DRV_CAP info
`FW_ID_MC` | MC info
`FW_ID_PSP_BL` | PSP_BL info
`FW_ID_CP_PM4` | CP_PM4 info
`FW_ID_ASD` | ASD info
`FW_ID_TA_RAS` | TA_RAS info
`FW_ID_XGMI` | XGMI info
`FW_ID_RLC_SRLG` | RLC_SRLG info
`FW_ID_RLC_SRLS` | RLC_SRLS info
`FW_ID_SMC` | SMC info
`FW_ID_DMCU` | DMCU info

Exceptions that can be thrown by `amdsmi_get_fw_info` function:
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
            fw_info = amdsmi_get_fw_info(device)
            for block_name, block_value in fw_info.items():
                print(block_name, str(block_value))

except AmdSmiException as e:
    print(e)
```

## amdsmi_get_gpu_activity
Description: Returns the engine usage for the given GPU

Input parameters:
* `device_handle` device which to query

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
    devices = amdsmi_get_device_handles()
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
* `device_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`average_socket_power`| average socket power
`voltage_gfx` | voltage gfx
`energy_accumulator` | energy accumulator

Exceptions that can be thrown by `amdsmi_get_power_measure` function:
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
            power_measure = amdsmi_get_power_measure(device)
            print(power_measure['average_socket_power'])
            print(power_measure['voltage_gfx'])
            print(power_measure['energy_accumulator'])
except AmdSmiException as e:
    print(e)
```
## amdsmi_get_vram_usage
Description: Returns total VRAM and VRAM in use

Input parameters:
* `device_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`vram_used`| VRAM currently in use
`vram_total` | VRAM total

Exceptions that can be thrown by `amdsmi_get_vram_usage` function:
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
            vram_usage = amdsmi_get_vram_usage(device)
            print(vram_usage['vram_used'])
            print(vram_usage['vram_total'])
except AmdSmiException as e:
    print(e)
```
## amdsmi_get_temperature_measure
Description: Returns the measurements of temperatures for the given GPU

Input parameters:

* `device_handle` device which to query
* `temperature_type` one of `AmdSmiTemperatureType` enum values:

Field | Description
---|---
`EDGE` | edge temperature type
`JUNCTION` | junction temperature type
`VRAM` | vram temperature type
`HBM_0` | HBM_0 temperature type
`HBM_1` | HBM_1 temperature type
`HBM_2` | HBM_2 temperature type
`HBM_3` | HBM_3 temperature type
`PLX` | PLX temperature type

Output: Dictionary with fields

Field | Description
---|---
`cur_temp`| temperature value for the given temperature type

Exceptions that can be thrown by `amdsmi_get_temperature_measure` function:
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
            temperature_measure = amdsmi_get_temperature_measure(device, AmdSmiTemperatureType.EDGE)
            print(temperature_measure['cur_temp'])
except AmdSmiException as e:
    print(e)
```
## amdsmi_get_clock_measure
Description: Returns the clock measure for the given GPU

Input parameters:
* `device_handle` device which to query
* `clock_type` one of `AmdSmiClockType` enum values:

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
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            clock_measure = amdsmi_get_clock_measure(device, AmdSmiClockType.GFX)
            print(clock_measure['cur_clk'])
            print(clock_measure['avg_clk'])
            print(clock_measure['min_clk'])
            print(clock_measure['max_clk'])
except AmdSmiException as e:
    print(e)
```
## amdsmi_get_power_limit
Description: Returns the power limit for the given GPU

Input parameters:
* `device_handle` device which to query

Output: Dictionary with fields

Field | Description
---|---
`limit`| power limit

Exceptions that can be thrown by `amdsmi_get_power_limit` function:
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
            power_limit = amdsmi_get_power_limit(device)
            print(power_limit['limit'])

except AmdSmiException as e:
    print(e)
```

## amdsmi_get_temperature_limit
Description: Returns the temperature limits for the given GPU

Input parameters:

* `device_handle` device which to query
* `temperature_type` one of `AmdSmiTemperatureType` enum values:

Field | Description
---|---
`EDGE` | edge temperature type
`JUNCTION` | junction temperature type
`VRAM` | vram temperature type
`HBM_0` | HBM_0 temperature type
`HBM_1` | HBM_1 temperature type
`HBM_2` | HBM_2 temperature type
`HBM_3` | HBM_3 temperature type
`PLX` | PLX temperature type

Output: Dictionary with fields

Field | Description
---|---
`limit`| temperature limit for the given thermal domain

Exceptions that can be thrown by `amdsmi_get_temperature_limit` function:
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
            temperature_limit = amdsmi_get_temperature_limit(device, AmdSmiTemperatureType.EDGE)
            print(temperature_limit['limit'])
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_pcie_link_status
Description: Returns the pcie link status for the given GPU

Input parameters:

* `device_handle` device which to query

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
    devices = amdsmi_get_device_handles()
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
* `device_handle` device which to query

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
    devices = amdsmi_get_device_handles()
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
* `device_handle` device which to query

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
    devices = amdsmi_get_device_handles()
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

* `device_handle` device which to query
* `clock_type` one of `AmdSmiClockType` enum values:

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
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        for device in devices:
            print("=============== GFX DOMAIN ================")
            freq_range = amdsmi_get_target_frequency_range(device,
                AmdSmiClockType.GFX)
            print(freq_range['supported_upper_bound'])
            print(freq_range['supported_lower_bound'])
            print(freq_range['current_upper_bound'])
            print(freq_range['current_lower_bound'])
            print("=============== MEM DOMAIN ================")
            freq_range = amdsmi_get_target_frequency_range(device,
                AmdSmiClockType.MEM)
            print(freq_range['supported_upper_bound'])
            print(freq_range['supported_lower_bound'])
            print(freq_range['current_upper_bound'])
            print(freq_range['current_lower_bound'])
            print("=============== VCLK0 DOMAIN ================")
            freq_range = amdsmi_get_target_frequency_range(device,
                AmdSmiClockType.VCLK0)
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

* `device_handle` device which to query

Output: List of process handles found

Exceptions that can be thrown by `amdsmi_get_process_list` function:
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
            processes = amdsmi_get_process_list(device)
            print(processes)
except AmdSmiException as e:
    print(e)
```
## amdsmi_get_process_info
Description: Returns the info for the given process

Input parameters:

* `device_handle` device which to query
* `process_handle` process which to query

Output: Dictionary with fields

Field | Description
---|---
`name` | Name of process
`pid` | Process ID
`mem` | Process memory usage
`usage`| <table><thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`gfx`</td><td>GFX engine usage</td></tr><tr><td>`compute`</td><td>Compute engine usage</td></tr><tr><td>`sdma`</td><td>DMA engine usage</td></tr><tr><td>`enc`</td><td>Encode engine usage</td></tr><tr><td>`dec`</td><td>Decode engine usage</td></tr></tbody></table>
`memory_usage`| <table><thead><tr> <th> Subfield </th> <th> Description</th> </tr></thead><tbody><tr><td>`gtt_mem`</td><td>GTT memory usage</td></tr><tr><td>`cpu_mem`</td><td>CPU memory usage</td></tr><tr><td>`vram_mem`</td><td>VRAM memory usage</td></tr> </tbody></table>

Exceptions that can be thrown by `amdsmi_get_process_info` function:
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
            processes = amdsmi_get_process_list(device)
            for process in processes:
                print(amdsmi_get_process_info(device, process))
except AmdSmiException as e:
    print(e)
```

## amdsmi_get_ecc_error_count
Description: Returns the ECC error count for the given GPU

Input parameters:

* `device_handle` device which to query

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
    devices = amdsmi_get_device_handles()
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

* `device_handle` device which to query

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
    device = amdsmi_get_device_handle_from_bdf("0000:23.00.0")
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

* `device_handle` device which to query

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
    devices = amdsmi_get_device_handles()
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

* `device_handle` device handle corresponding to the device on which to listen for events
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
    devices = amdsmi_get_device_handles()
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
    devices = amdsmi_get_device_handles()
    if len(devices) == 0:
        print("No GPUs on machine")
    else:
        with AmdSmiEventReader(device[0], AmdSmiEvtNotificationType.GPU_PRE_RESET, AmdSmiEvtNotificationType.GPU_POST_RESET) as event:
            event.read(10000)
except AmdSmiException as e:
    print(e)

```

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
## amdsmi_dev_fan_rpms_get
Description: Get the fan speed in RPMs of the device with the specified device
handle and 0-based sensor index.

Input parameters:
* `device_handle` handle for the given device
* `sensor_idx` a 0-based sensor index. Normally, this will be 0. If a device has
more than one sensor, it could be greater than 0.

Output: Fan speed in rpms as integer

Exceptions that can be thrown by `amdsmi_dev_fan_rpms_get` function:
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
            fan_rpm = amdsmi_dev_fan_rpms_get(device, 0)
            print(fan_rpm)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_fan_speed_get
Description: Get the fan speed for the specified device as a value relative to
AMDSMI_MAX_FAN_SPEED

Input parameters:
* `device_handle` handle for the given device
* `sensor_idx` a 0-based sensor index. Normally, this will be 0. If a device has
more than one sensor, it could be greater than 0.

Output: Fan speed in relative to MAX

Exceptions that can be thrown by `amdsmi_dev_fan_speed_get` function:
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
            fan_speed = amdsmi_dev_fan_speed_get(device, 0)
            print(fan_speed)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_fan_speed_max_get
Description: Get the max fan speed of the device with provided device handle

Input parameters:
* `device_handle` handle for the given device
* `sensor_idx` a 0-based sensor index. Normally, this will be 0. If a device has
more than one sensor, it could be greater than 0.

Output: Max fan speed as integer

Exceptions that can be thrown by `amdsmi_dev_fan_speed_max_get` function:
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
            max_fan_speed = amdsmi_dev_fan_speed_max_get(device, 0)
            print(max_fan_speed)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_temp_metric_get
Description: Get the temperature metric value for the specified metric, from the
specified temperature sensor on the specified device

Input parameters:
* `device_handle` handle for the given device
* `sensor_type` part of device from which temperature should be obtained
* `metric` enum indicated which temperature value should be retrieved

Output: Temperature as integer in millidegrees Celcius

Exceptions that can be thrown by `amdsmi_dev_temp_metric_get` function:
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
            temp_metric = amdsmi_dev_temp_metric_get(device, AmdSmiTemperatureType.EDGE,
                            AmdSmiTemperatureMetric.CURRENT)
            print(temp_metric)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_volt_metric_get
Description: Get the voltage metric value for the specified metric, from the
specified voltage sensor on the specified device

Input parameters:
* `device_handle` handle for the given device
* `sensor_type` part of device from which voltage should be obtained
* `metric` enum indicated which voltage value should be retrieved

Output: Voltage as integer in millivolts

Exceptions that can be thrown by `amdsmi_dev_volt_metric_get` function:
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
            voltage = amdsmi_dev_volt_metric_get(device, AmdSmiVoltageType.VDDGFX,
                        AmdSmiVoltageMetric.AVERAGE)
            print(voltage)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_busy_percent_get
Description: Get percentage of time device is busy doing any processing

Input parameters:
* `device_handle` handle for the given device

Output: How busy the device is (as percentage of time)

Exceptions that can be thrown by `amdsmi_dev_busy_percent_get` function:
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
            busy = amdsmi_dev_busy_percent_get(dev)
            print(busy)
except AmdSmiException as e:
    print(e)
```
## amdsmi_utilization_count_get
Description: Get coarse grain utilization counter of the specified device

Input parameters:
* `device_handle` handle for the given device
* `counter_types` variable number of counter types desired

Output: List containing dictionaries with fields

Field | Description
---|---
`timestamp` | The timestamp when the counter is retreived - Resolution: 1 ns
`Dictionary for each counter` | <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`type`</td><td>Type of utilization counter</td></tr><tr><td>`value`</td><td>Value gotten for utilization counter</td></tr></tbody></table>

Exceptions that can be thrown by `amdsmi_utilization_count_get` function:
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
            utilization = amdsmi_utilization_count_get(
                            device,
                            AmdSmiUtilizationCounterType.COARSE_GRAIN_GFX_ACTIVITY
                            )
            print(utilization)
            utilization = amdsmi_utilization_count_get(
                            device,
                            AmdSmiUtilizationCounterType.COARSE_GRAIN_GFX_ACTIVITY,
                            AmdSmiUtilizationCounterType.COARSE_GRAIN_MEM_ACTIVITY
                            )
            print(utilization)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_perf_level_get
Description: Get the performance level of the device with provided device handle

Input parameters:
* `device_handle` handle for the given device

Output: Performance level as enum value of dev_perf_level_t

Exceptions that can be thrown by `amdsmi_dev_perf_level_get` function:
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
            perf_level = amdsmi_dev_perf_level_get(dev)
            print(perf_level)
except AmdSmiException as e:
    print(e)
```
## amdsmi_perf_determinism_mode_set
Description: Enter performance determinism mode with provided device handle

Input parameters:
* `device_handle` handle for the given device
* `clkvalue` softmax value for GFXCLK in MHz

Output: None

Exceptions that can be thrown by `amdsmi_perf_determinism_mode_set` function:
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
            amdsmi_perf_determinism_mode_set(device, 1333)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_overdrive_level_get
Description: Get the overdrive percent associated with the device with provided
device handle

Input parameters:
* `device_handle` handle for the given device

Output: Overdrive percentage as integer

Exceptions that can be thrown by `amdsmi_dev_overdrive_level_get` function:
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
            od_level = amdsmi_dev_overdrive_level_get(dev)
            print(od_level)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_gpu_clk_freq_get
Description: Get the list of possible system clock speeds of device for a
specified clock type

Input parameters:
* `device_handle` handle for the given device
* `clk_type` the type of clock for which the frequency is desired

Output: Dictionary with fields

Field | Description
---|---
`num_supported`| The number of supported frequencies
`current`| The current frequency index
`frequency`| List of frequencies, only the first num_supported frequencies are valid

Exceptions that can be thrown by `amdsmi_dev_gpu_clk_freq_get` function:
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
            amdsmi_dev_gpu_clk_freq_get(device, AmdSmiClockType.SYS)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_od_volt_info_get
Description: This function retrieves the voltage/frequency curve information

Input parameters:
* `device_handle` handle for the given device

Output: Dictionary with fields

Field | Description
---|---
`curr_sclk_range` | <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound sclk range</td></tr><tr><td>`upper_bound`</td><td>upper bound sclk range</td></tr></tbody></table>
`curr_mclk_range` |  <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound mclk range</td></tr><tr><td>`upper_bound`</td><td>upper bound mclk range</td></tr></tbody></table>
`sclk_freq_limits` |  <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound sclk range limt</td></tr><tr><td>`upper_bound`</td><td>upper bound sclk range limit</td></tr></tbody></table>
`mclk_freq_limits` |  <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound mclk range limit</td></tr><tr><td>`upper_bound`</td><td>upper bound mclk range limit</td></tr></tbody></table>
`curve.vc_points`| The number of supported frequencies
`num_regions`| The current frequency index


Exceptions that can be thrown by `amdsmi_dev_od_volt_info_get` function:
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
            amdsmi_dev_od_volt_info_get(dev)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_gpu_metrics_info_get
Description: This function retrieves the gpu metrics information

Input parameters:
* `device_handle` handle for the given device

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

Exceptions that can be thrown by `amdsmi_dev_gpu_metrics_info_get` function:
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
            amdsmi_dev_gpu_metrics_info_get(dev)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_od_volt_curve_regions_get
Description: This function will retrieve the current valid regions in the
frequency/voltage space

Input parameters:
* `device_handle` handle for the given device
* `num_regions` number of freq volt regions

Output: List containing a dictionary with fields for each freq volt region

Field | Description
---|---
`freq_range` | <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound freq range</td></tr><tr><td>`upper_bound`</td><td>upper bound freq range</td></tr></tbody></table>
`volt_range` |  <table> <thead><tr><th> Subfield </th><th>Description</th></tr></thead><tbody><tr><td>`lower_bound`</td><td>lower bound volt range</td></tr><tr><td>`upper_bound`</td><td>upper bound volt range</td></tr></tbody></table>

Exceptions that can be thrown by `amdsmi_dev_od_volt_curve_regions_get` function:
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
            amdsmi_dev_od_volt_curve_regions_get(device, 3)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_power_profile_presets_get
Description:  Get the list of available preset power profiles and an indication of
which profile is currently active

Input parameters:
* `device_handle` handle for the given device
* `sensor_idx` number of freq volt regions

Output: Dictionary with fields

Field | Description
---|---
`available_profiles`| Which profiles are supported by this system
`current`| Which power profile is currently active
`num_profiles`| How many power profiles are available

Exceptions that can be thrown by `amdsmi_dev_power_profile_presets_get` function:
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
            amdsmi_dev_power_profile_presets_get(device, 0)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_counter_group_supported
Description: Tell if an event group is supported by a given device

Input parameters:

* `device_handle` device which to query
* `event_group` event group being checked for support

Output: None

Exceptions that can be thrown by `amdsmi_dev_counter_group_supported` function:
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
            amdsmi_dev_counter_group_supported(device, AmdSmiEventGroup.XGMI)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_counter_create
Description: Creates a performance counter object

Input parameters:

* `device_handle` device which to query
* `event_type` event group being checked for support

Output: An event handle of the newly created performance counter object

Exceptions that can be thrown by `amdsmi_dev_counter_create` function:
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
            event_handle = amdsmi_dev_counter_create(device, AmdSmiEventGroup.XGMI)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_counter_destroy
Description: Destroys a performance counter object

Input parameters:

* `event_handle` event handle of the performance counter object

Output: None

Exceptions that can be thrown by `amdsmi_dev_counter_destroy` function:
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
            event_handle = amdsmi_dev_counter_create(device, AmdSmiEventGroup.XGMI)
            amdsmi_dev_counter_destroy(event_handle)
except AmdSmiException as e:
    print(e)
```
## amdsmi_counter_control
Description: Issue performance counter control commands

Input parameters:

* `event_handle` event handle of the performance counter object
* `counter_command` command being passed to counter as AmdSmiCounterCommand

Output: None

Exceptions that can be thrown by `amdsmi_counter_control` function:
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
            event_handle = amdsmi_dev_counter_create(device, AmdSmiEventType.XGMI_1_REQUEST_TX)
            amdsmi_counter_control(event_handle, AmdSmiCounterCommand.CMD_START)
except AmdSmiException as e:
    print(e)
```
## amdsmi_counter_read
Description: Read the current value of a performance counter

Input parameters:

* `event_handle` event handle of the performance counter object

Output: Dictionary with fields

Field | Description
---|---
`value`| Counter value
`time_enabled`| Time that the counter was enabled in nanoseconds
`time_running`| Time that the counter was running in nanoseconds

Exceptions that can be thrown by `amdsmi_counter_read` function:
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
            event_handle = amdsmi_dev_counter_create(device, AmdSmiEventType.XGMI_1_REQUEST_TX)
            amdsmi_counter_read(event_handle)
except AmdSmiException as e:
    print(e)
```
## amdsmi_counter_available_counters_get
Description: Get the number of currently available counters

Input parameters:

* `device_handle` handle for the given device
* `event_group` event group being checked as AmdSmiEventGroup

Output: Number of available counters for the given device of the inputted event group

Exceptions that can be thrown by `amdsmi_counter_available_counters_get` function:
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
            available_counters = amdsmi_counter_available_counters_get(device, AmdSmiEventGroup.XGMI)
            print(available_counters)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_perf_level_set
Description: Set a desired performance level for given device

Input parameters:
* `device_handle` handle for the given device
* `perf_level` performance level being set as AmdSmiDevPerfLevel

Output: None

Exceptions that can be thrown by `amdsmi_dev_perf_level_set` function:
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
            amdsmi_dev_perf_level_set(device, AmdSmiDevPerfLevel.STABLE_PEAK)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_power_profile_presets_get
Description: Get the list of available preset power profiles and an indication of
which profile is currently active.

Input parameters:
* `device_handle` handle for the given device
* `sensor_idx` sensor index as integer

Output: Dictionary with fields

Field | Description
---|---
`available_profiles`| Which profiles are supported by this system
`current`| Which power profile is currently active
`num_profiles`| How many power profiles are available

Exceptions that can be thrown by `amdsmi_dev_power_profile_presets_get` function:
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
            status = amdsmi_dev_power_profile_presets_get(device, 0)
            print(status)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_gpu_reset
Description: Reset the gpu associated with the device with provided device handle

Input parameters:
* `device_handle` handle for the given device

Output: None

Exceptions that can be thrown by `amdsmi_dev_gpu_reset` function:
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
            amdsmi_dev_gpu_reset(device)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_fan_speed_set
Description: Set the fan speed for the specified device with the provided speed,
in RPMs

Input parameters:
* `device_handle` handle for the given device
* `sensor_idx` sensor index as integer
* `fan_speed` the speed to which the function will attempt to set the fan

Output: None

Exceptions that can be thrown by `amdsmi_dev_fan_speed_set` function:
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
            amdsmi_dev_fan_speed_set(device, 0, 1333)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_fan_reset
Description: Reset the fan to automatic driver control

Input parameters:
* `device_handle` handle for the given device
* `sensor_idx` sensor index as integer

Output: None

Exceptions that can be thrown by `amdsmi_dev_fan_reset` function:
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
            amdsmi_dev_fan_reset(device, 0)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_gpu_clk_freq_set
Description: Control the set of allowed frequencies that can be used for the
specified clock

Input parameters:
* `device_handle` handle for the given device
* `clk_type` the type of clock for which the set of frequencies will be modified
as AmdSmiClockType
* `freq_bitmask`  bitmask indicating the indices of the frequencies that are to
be enabled (1) and disabled (0). Only the lowest ::amdsmi_frequencies_t.num_supported
bits of this mask are relevant.

Output: None

Exceptions that can be thrown by `amdsmi_dev_gpu_clk_freq_set` function:
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
            freq_bitmask = 0
            amdsmi_dev_gpu_clk_freq_set(device, AmdSmiClockType.GFX, freq_bitmask)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_overdrive_level_set_v1
Description: Set the overdrive percent associated with the device with provided
device handle with the provided value

Input parameters:
* `device_handle` handle for the given device
* `overdrive_value` value to which the overdrive level should be set

Output: None

Exceptions that can be thrown by `amdsmi_dev_overdrive_level_set_v1` function:
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
            amdsmi_dev_overdrive_level_set_v1(device, 0)
except AmdSmiException as e:
    print(e)
```
## amdsmi_dev_overdrive_level_set
Description: **deprecated** Set the overdrive percent associated with the
device with provided device handle with the provided value

Input parameters:
* `device_handle` handle for the given device
* `overdrive_value` value to which the overdrive level should be set

Output: None

Exceptions that can be thrown by `amdsmi_dev_overdrive_level_set` function:
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
            amdsmi_dev_overdrive_level_set(device, 0)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_ecc_count_get
Description: Retrieve the error counts for a GPU block

Input parameters:
* `device_handle` handle for the given device
* `block` The block for which error counts should be retrieved

Output: Dict containing information about error counts

Field | Description
---|---
`correctable_count`| Count of correctable errors
`uncorrectable_count`| Count of uncorrectable errors

Exceptions that can be thrown by `amdsmi_dev_ecc_count_get` function:
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
            ecc_count = amdsmi_dev_ecc_count_get(device, AmdSmiGpuBlock.UMC)
            print(ecc_count)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_ecc_enabled_get
Description: Retrieve the enabled ECC bit-mask

Input parameters:
* `device_handle` handle for the given device

Output: Enabled ECC bit-mask

Exceptions that can be thrown by `amdsmi_dev_ecc_enabled_get` function:
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
            enabled = amdsmi_dev_ecc_enabled_get(device)
            print(enabled)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_ecc_status_get
Description: Retrieve the ECC status for a GPU block

Input parameters:
* `device_handle` handle for the given device
* `block` The block for which ECC status should be retrieved

Output: ECC status for a requested GPU block

Exceptions that can be thrown by `amdsmi_dev_ecc_status_get` function:
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
            status = amdsmi_dev_ecc_status_get(device, AmdSmiGpuBlock.UMC)
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

## amdsmi_compute_process_info_get
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

Exceptions that can be thrown by `amdsmi_compute_process_info_get` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`

Example:
```python
try:
    procs = amdsmi_compute_process_info_get()
    for proc in procs:
        print(proc)
except AmdSmiException as e:
    print(e)
```

## amdsmi_compute_process_info_by_pid_get
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

Exceptions that can be thrown by `amdsmi_compute_process_info_by_pid_get` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    pid = 0 # << valid pid here
    proc = amdsmi_compute_process_info_by_pid_get(pid)
    print(proc)
except AmdSmiException as e:
    print(e)
```

## amdsmi_compute_process_gpus_get
Description: Get the device indices currently being used by a process

Input parameters:
* `pid` The process id of the process for which the number of gpus currently being used is requested

Output: List of indices of devices currently being used by the process

Exceptions that can be thrown by `amdsmi_compute_process_gpus_get` function:
* `AmdSmiLibraryException`
* `AmdSmiRetryException`
* `AmdSmiParameterException`

Example:
```python
try:
    pid = 0 # << valid pid here
    indices = amdsmi_compute_process_gpus_get(pid)
    print(indices)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_xgmi_error_status
Description: Retrieve the XGMI error status for a device

Input parameters:
* `device_handle` handle for the given device

Output: XGMI error status for a requested device

Exceptions that can be thrown by `amdsmi_dev_xgmi_error_status` function:
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
            status = amdsmi_dev_xgmi_error_status(device)
            print(status)
except AmdSmiException as e:
    print(e)
```

## amdsmi_dev_xgmi_error_reset
Description: Reset the XGMI error status for a device

Input parameters:
* `device_handle` handle for the given device

Output: None

Exceptions that can be thrown by `amdsmi_dev_xgmi_error_reset` function:
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
            amdsmi_dev_xgmi_error_reset(device)
except AmdSmiException as e:
    print(e)
```

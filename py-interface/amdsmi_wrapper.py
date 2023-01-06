
#
# Copyright (C) 2022 Advanced Micro Devices. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import os
# -*- coding: utf-8 -*-
#
# TARGET arch is: ['-I/usr/lib/llvm-6.0/lib/clang/6.0.0/include']
# WORD_SIZE is: 8
# POINTER_SIZE is: 8
# LONGDOUBLE_SIZE is: 16
#
import ctypes


c_int128 = ctypes.c_ubyte*16
c_uint128 = c_int128
void = None
if ctypes.sizeof(ctypes.c_longdouble) == 16:
    c_long_double_t = ctypes.c_longdouble
else:
    c_long_double_t = ctypes.c_ubyte*16

class AsDictMixin:
    @classmethod
    def as_dict(cls, self):
        result = {}
        if not isinstance(self, AsDictMixin):
            # not a structure, assume it's already a python object
            return self
        if not hasattr(cls, "_fields_"):
            return result
        # sys.version_info >= (3, 5)
        # for (field, *_) in cls._fields_:  # noqa
        for field_tuple in cls._fields_:  # noqa
            field = field_tuple[0]
            if field.startswith('PADDING_'):
                continue
            value = getattr(self, field)
            type_ = type(value)
            if hasattr(value, "_length_") and hasattr(value, "_type_"):
                # array
                if not hasattr(type_, "as_dict"):
                    value = [v for v in value]
                else:
                    type_ = type_._type_
                    value = [type_.as_dict(v) for v in value]
            elif hasattr(value, "contents") and hasattr(value, "_type_"):
                # pointer
                try:
                    if not hasattr(type_, "as_dict"):
                        value = value.contents
                    else:
                        type_ = type_._type_
                        value = type_.as_dict(value.contents)
                except ValueError:
                    # nullptr
                    value = None
            elif isinstance(value, AsDictMixin):
                # other structure
                value = type_.as_dict(value)
            result[field] = value
        return result


class Structure(ctypes.Structure, AsDictMixin):

    def __init__(self, *args, **kwds):
        # We don't want to use positional arguments fill PADDING_* fields

        args = dict(zip(self.__class__._field_names_(), args))
        args.update(kwds)
        super(Structure, self).__init__(**args)

    @classmethod
    def _field_names_(cls):
        if hasattr(cls, '_fields_'):
            return (f[0] for f in cls._fields_ if not f[0].startswith('PADDING'))
        else:
            return ()

    @classmethod
    def get_type(cls, field):
        for f in cls._fields_:
            if f[0] == field:
                return f[1]
        return None

    @classmethod
    def bind(cls, bound_fields):
        fields = {}
        for name, type_ in cls._fields_:
            if hasattr(type_, "restype"):
                if name in bound_fields:
                    if bound_fields[name] is None:
                        fields[name] = type_()
                    else:
                        # use a closure to capture the callback from the loop scope
                        fields[name] = (
                            type_((lambda callback: lambda *args: callback(*args))(
                                bound_fields[name]))
                        )
                    del bound_fields[name]
                else:
                    # default callback implementation (does nothing)
                    try:
                        default_ = type_(0).restype().value
                    except TypeError:
                        default_ = None
                    fields[name] = type_((
                        lambda default_: lambda *args: default_)(default_))
            else:
                # not a callback function, use default initialization
                if name in bound_fields:
                    fields[name] = bound_fields[name]
                    del bound_fields[name]
                else:
                    fields[name] = type_()
        if len(bound_fields) != 0:
            raise ValueError(
                "Cannot bind the following unknown callback(s) {}.{}".format(
                    cls.__name__, bound_fields.keys()
            ))
        return cls(**fields)


class Union(ctypes.Union, AsDictMixin):
    pass



def string_cast(char_pointer, encoding='utf-8', errors='strict'):
    value = ctypes.cast(char_pointer, ctypes.c_char_p).value
    if value is not None and encoding is not None:
        value = value.decode(encoding, errors=errors)
    return value


def char_pointer_cast(string, encoding='utf-8'):
    if encoding is not None:
        try:
            string = string.encode(encoding)
        except AttributeError:
            # In Python3, bytes has no encode attribute
            pass
    string = ctypes.c_char_p(string)
    return ctypes.cast(string, ctypes.POINTER(ctypes.c_char))



_libraries = {}
_libraries['libamd_smi.so'] = ctypes.CDLL(os.path.join(os.path.dirname(__file__), 'libamd_smi.so'))



# values for enumeration 'amdsmi_init_flags'
amdsmi_init_flags__enumvalues = {
    0: 'AMDSMI_INIT_ALL_DEVICES',
    1: 'AMDSMI_INIT_AMD_CPUS',
    2: 'AMDSMI_INIT_AMD_GPUS',
    4: 'AMDSMI_INIT_NON_AMD_CPUS',
    8: 'AMDSMI_INIT_NON_AMD_GPUS',
}
AMDSMI_INIT_ALL_DEVICES = 0
AMDSMI_INIT_AMD_CPUS = 1
AMDSMI_INIT_AMD_GPUS = 2
AMDSMI_INIT_NON_AMD_CPUS = 4
AMDSMI_INIT_NON_AMD_GPUS = 8
amdsmi_init_flags = ctypes.c_uint32 # enum
amdsmi_init_flags_t = amdsmi_init_flags
amdsmi_init_flags_t__enumvalues = amdsmi_init_flags__enumvalues

# values for enumeration 'amdsmi_mm_ip'
amdsmi_mm_ip__enumvalues = {
    0: 'AMDSMI_MM_UVD',
    1: 'AMDSMI_MM_VCE',
    2: 'AMDSMI_MM_VCN',
    3: 'AMDSMI_MM__MAX',
}
AMDSMI_MM_UVD = 0
AMDSMI_MM_VCE = 1
AMDSMI_MM_VCN = 2
AMDSMI_MM__MAX = 3
amdsmi_mm_ip = ctypes.c_uint32 # enum
amdsmi_mm_ip_t = amdsmi_mm_ip
amdsmi_mm_ip_t__enumvalues = amdsmi_mm_ip__enumvalues

# values for enumeration 'amdsmi_container_types'
amdsmi_container_types__enumvalues = {
    0: 'CONTAINER_LXC',
    1: 'CONTAINER_DOCKER',
}
CONTAINER_LXC = 0
CONTAINER_DOCKER = 1
amdsmi_container_types = ctypes.c_uint32 # enum
amdsmi_container_types_t = amdsmi_container_types
amdsmi_container_types_t__enumvalues = amdsmi_container_types__enumvalues
amdsmi_device_handle = ctypes.POINTER(None)
amdsmi_socket_handle = ctypes.POINTER(None)

# values for enumeration 'device_type'
device_type__enumvalues = {
    0: 'UNKNOWN',
    1: 'AMD_GPU',
    2: 'AMD_CPU',
    3: 'NON_AMD_GPU',
    4: 'NON_AMD_CPU',
}
UNKNOWN = 0
AMD_GPU = 1
AMD_CPU = 2
NON_AMD_GPU = 3
NON_AMD_CPU = 4
device_type = ctypes.c_uint32 # enum
device_type_t = device_type
device_type_t__enumvalues = device_type__enumvalues

# values for enumeration 'amdsmi_status_t'
amdsmi_status_t__enumvalues = {
    0: 'AMDSMI_STATUS_SUCCESS',
    1: 'AMDSMI_STATUS_INVAL',
    2: 'AMDSMI_STATUS_NOT_SUPPORTED',
    3: 'AMDSMI_STATUS_NOT_YET_IMPLEMENTED',
    4: 'AMDSMI_STATUS_FAIL_LOAD_MODULE',
    5: 'AMDSMI_STATUS_FAIL_LOAD_SYMBOL',
    6: 'AMDSMI_STATUS_DRM_ERROR',
    7: 'AMDSMI_STATUS_API_FAILED',
    8: 'AMDSMI_STATUS_TIMEOUT',
    9: 'AMDSMI_STATUS_RETRY',
    10: 'AMDSMI_STATUS_NO_PERM',
    11: 'AMDSMI_STATUS_INTERRUPT',
    12: 'AMDSMI_STATUS_IO',
    13: 'AMDSMI_STATUS_ADDRESS_FAULT',
    14: 'AMDSMI_STATUS_FILE_ERROR',
    15: 'AMDSMI_STATUS_OUT_OF_RESOURCES',
    16: 'AMDSMI_STATUS_INTERNAL_EXCEPTION',
    17: 'AMDSMI_STATUS_INPUT_OUT_OF_BOUNDS',
    18: 'AMDSMI_STATUS_INIT_ERROR',
    19: 'AMDSMI_STATUS_REFCOUNT_OVERFLOW',
    30: 'AMDSMI_STATUS_BUSY',
    31: 'AMDSMI_STATUS_NOT_FOUND',
    32: 'AMDSMI_STATUS_NOT_INIT',
    33: 'AMDSMI_STATUS_NO_SLOT',
    40: 'AMDSMI_STATUS_NO_DATA',
    41: 'AMDSMI_STATUS_INSUFFICIENT_SIZE',
    42: 'AMDSMI_STATUS_UNEXPECTED_SIZE',
    43: 'AMDSMI_STATUS_UNEXPECTED_DATA',
    4294967294: 'AMDSMI_STATUS_MAP_ERROR',
    4294967295: 'AMDSMI_STATUS_UNKNOWN_ERROR',
}
AMDSMI_STATUS_SUCCESS = 0
AMDSMI_STATUS_INVAL = 1
AMDSMI_STATUS_NOT_SUPPORTED = 2
AMDSMI_STATUS_NOT_YET_IMPLEMENTED = 3
AMDSMI_STATUS_FAIL_LOAD_MODULE = 4
AMDSMI_STATUS_FAIL_LOAD_SYMBOL = 5
AMDSMI_STATUS_DRM_ERROR = 6
AMDSMI_STATUS_API_FAILED = 7
AMDSMI_STATUS_TIMEOUT = 8
AMDSMI_STATUS_RETRY = 9
AMDSMI_STATUS_NO_PERM = 10
AMDSMI_STATUS_INTERRUPT = 11
AMDSMI_STATUS_IO = 12
AMDSMI_STATUS_ADDRESS_FAULT = 13
AMDSMI_STATUS_FILE_ERROR = 14
AMDSMI_STATUS_OUT_OF_RESOURCES = 15
AMDSMI_STATUS_INTERNAL_EXCEPTION = 16
AMDSMI_STATUS_INPUT_OUT_OF_BOUNDS = 17
AMDSMI_STATUS_INIT_ERROR = 18
AMDSMI_STATUS_REFCOUNT_OVERFLOW = 19
AMDSMI_STATUS_BUSY = 30
AMDSMI_STATUS_NOT_FOUND = 31
AMDSMI_STATUS_NOT_INIT = 32
AMDSMI_STATUS_NO_SLOT = 33
AMDSMI_STATUS_NO_DATA = 40
AMDSMI_STATUS_INSUFFICIENT_SIZE = 41
AMDSMI_STATUS_UNEXPECTED_SIZE = 42
AMDSMI_STATUS_UNEXPECTED_DATA = 43
AMDSMI_STATUS_MAP_ERROR = 4294967294
AMDSMI_STATUS_UNKNOWN_ERROR = 4294967295
amdsmi_status_t = ctypes.c_uint32 # enum

# values for enumeration 'amdsmi_clk_type'
amdsmi_clk_type__enumvalues = {
    0: 'CLK_TYPE_SYS',
    0: 'CLK_TYPE_FIRST',
    0: 'CLK_TYPE_GFX',
    1: 'CLK_TYPE_DF',
    2: 'CLK_TYPE_DCEF',
    3: 'CLK_TYPE_SOC',
    4: 'CLK_TYPE_MEM',
    5: 'CLK_TYPE_PCIE',
    6: 'CLK_TYPE_VCLK0',
    7: 'CLK_TYPE_VCLK1',
    8: 'CLK_TYPE_DCLK0',
    9: 'CLK_TYPE_DCLK1',
    9: 'CLK_TYPE__MAX',
}
CLK_TYPE_SYS = 0
CLK_TYPE_FIRST = 0
CLK_TYPE_GFX = 0
CLK_TYPE_DF = 1
CLK_TYPE_DCEF = 2
CLK_TYPE_SOC = 3
CLK_TYPE_MEM = 4
CLK_TYPE_PCIE = 5
CLK_TYPE_VCLK0 = 6
CLK_TYPE_VCLK1 = 7
CLK_TYPE_DCLK0 = 8
CLK_TYPE_DCLK1 = 9
CLK_TYPE__MAX = 9
amdsmi_clk_type = ctypes.c_uint32 # enum
amdsmi_clk_type_t = amdsmi_clk_type
amdsmi_clk_type_t__enumvalues = amdsmi_clk_type__enumvalues

# values for enumeration 'amdsmi_temperature_type'
amdsmi_temperature_type__enumvalues = {
    0: 'TEMPERATURE_TYPE_EDGE',
    0: 'TEMPERATURE_TYPE_FIRST',
    1: 'TEMPERATURE_TYPE_JUNCTION',
    2: 'TEMPERATURE_TYPE_VRAM',
    3: 'TEMPERATURE_TYPE_HBM_0',
    4: 'TEMPERATURE_TYPE_HBM_1',
    5: 'TEMPERATURE_TYPE_HBM_2',
    6: 'TEMPERATURE_TYPE_HBM_3',
    7: 'TEMPERATURE_TYPE_PLX',
    7: 'TEMPERATURE_TYPE__MAX',
}
TEMPERATURE_TYPE_EDGE = 0
TEMPERATURE_TYPE_FIRST = 0
TEMPERATURE_TYPE_JUNCTION = 1
TEMPERATURE_TYPE_VRAM = 2
TEMPERATURE_TYPE_HBM_0 = 3
TEMPERATURE_TYPE_HBM_1 = 4
TEMPERATURE_TYPE_HBM_2 = 5
TEMPERATURE_TYPE_HBM_3 = 6
TEMPERATURE_TYPE_PLX = 7
TEMPERATURE_TYPE__MAX = 7
amdsmi_temperature_type = ctypes.c_uint32 # enum
amdsmi_temperature_type_t = amdsmi_temperature_type
amdsmi_temperature_type_t__enumvalues = amdsmi_temperature_type__enumvalues

# values for enumeration 'amdsmi_fw_block'
amdsmi_fw_block__enumvalues = {
    1: 'FW_ID_SMU',
    1: 'FW_ID_FIRST',
    2: 'FW_ID_CP_CE',
    3: 'FW_ID_CP_PFP',
    4: 'FW_ID_CP_ME',
    5: 'FW_ID_CP_MEC_JT1',
    6: 'FW_ID_CP_MEC_JT2',
    7: 'FW_ID_CP_MEC1',
    8: 'FW_ID_CP_MEC2',
    9: 'FW_ID_RLC',
    10: 'FW_ID_SDMA0',
    11: 'FW_ID_SDMA1',
    12: 'FW_ID_SDMA2',
    13: 'FW_ID_SDMA3',
    14: 'FW_ID_SDMA4',
    15: 'FW_ID_SDMA5',
    16: 'FW_ID_SDMA6',
    17: 'FW_ID_SDMA7',
    18: 'FW_ID_VCN',
    19: 'FW_ID_UVD',
    20: 'FW_ID_VCE',
    21: 'FW_ID_ISP',
    22: 'FW_ID_DMCU_ERAM',
    23: 'FW_ID_DMCU_ISR',
    24: 'FW_ID_RLC_RESTORE_LIST_GPM_MEM',
    25: 'FW_ID_RLC_RESTORE_LIST_SRM_MEM',
    26: 'FW_ID_RLC_RESTORE_LIST_CNTL',
    27: 'FW_ID_RLC_V',
    28: 'FW_ID_MMSCH',
    29: 'FW_ID_PSP_SYSDRV',
    30: 'FW_ID_PSP_SOSDRV',
    31: 'FW_ID_PSP_TOC',
    32: 'FW_ID_PSP_KEYDB',
    33: 'FW_ID_DFC',
    34: 'FW_ID_PSP_SPL',
    35: 'FW_ID_DRV_CAP',
    36: 'FW_ID_MC',
    37: 'FW_ID_PSP_BL',
    38: 'FW_ID_CP_PM4',
    39: 'FW_ID_ASD',
    40: 'FW_ID_TA_RAS',
    41: 'FW_ID_XGMI',
    42: 'FW_ID_RLC_SRLG',
    43: 'FW_ID_RLC_SRLS',
    44: 'FW_ID_SMC',
    45: 'FW_ID_DMCU',
    46: 'FW_ID__MAX',
}
FW_ID_SMU = 1
FW_ID_FIRST = 1
FW_ID_CP_CE = 2
FW_ID_CP_PFP = 3
FW_ID_CP_ME = 4
FW_ID_CP_MEC_JT1 = 5
FW_ID_CP_MEC_JT2 = 6
FW_ID_CP_MEC1 = 7
FW_ID_CP_MEC2 = 8
FW_ID_RLC = 9
FW_ID_SDMA0 = 10
FW_ID_SDMA1 = 11
FW_ID_SDMA2 = 12
FW_ID_SDMA3 = 13
FW_ID_SDMA4 = 14
FW_ID_SDMA5 = 15
FW_ID_SDMA6 = 16
FW_ID_SDMA7 = 17
FW_ID_VCN = 18
FW_ID_UVD = 19
FW_ID_VCE = 20
FW_ID_ISP = 21
FW_ID_DMCU_ERAM = 22
FW_ID_DMCU_ISR = 23
FW_ID_RLC_RESTORE_LIST_GPM_MEM = 24
FW_ID_RLC_RESTORE_LIST_SRM_MEM = 25
FW_ID_RLC_RESTORE_LIST_CNTL = 26
FW_ID_RLC_V = 27
FW_ID_MMSCH = 28
FW_ID_PSP_SYSDRV = 29
FW_ID_PSP_SOSDRV = 30
FW_ID_PSP_TOC = 31
FW_ID_PSP_KEYDB = 32
FW_ID_DFC = 33
FW_ID_PSP_SPL = 34
FW_ID_DRV_CAP = 35
FW_ID_MC = 36
FW_ID_PSP_BL = 37
FW_ID_CP_PM4 = 38
FW_ID_ASD = 39
FW_ID_TA_RAS = 40
FW_ID_XGMI = 41
FW_ID_RLC_SRLG = 42
FW_ID_RLC_SRLS = 43
FW_ID_SMC = 44
FW_ID_DMCU = 45
FW_ID__MAX = 46
amdsmi_fw_block = ctypes.c_uint32 # enum
amdsmi_fw_block_t = amdsmi_fw_block
amdsmi_fw_block_t__enumvalues = amdsmi_fw_block__enumvalues
class struct_c__SA_amdsmi_range_t(Structure):
    pass

struct_c__SA_amdsmi_range_t._pack_ = 1 # source:False
struct_c__SA_amdsmi_range_t._fields_ = [
    ('lower_bound', ctypes.c_uint64),
    ('upper_bound', ctypes.c_uint64),
    ('reserved', ctypes.c_uint64 * 2),
]

amdsmi_range_t = struct_c__SA_amdsmi_range_t
amdsmi_range = struct_c__SA_amdsmi_range_t
class struct_amdsmi_xgmi_info(Structure):
    pass

struct_amdsmi_xgmi_info._pack_ = 1 # source:False
struct_amdsmi_xgmi_info._fields_ = [
    ('xgmi_lanes', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 7),
    ('xgmi_hive_id', ctypes.c_uint64),
    ('xgmi_node_id', ctypes.c_uint64),
    ('index', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32 * 9),
]

amdsmi_xgmi_info_t = struct_amdsmi_xgmi_info
class struct_amdsmi_gpu_caps(Structure):
    pass

class struct_amdsmi_gpu_caps_0(Structure):
    pass

struct_amdsmi_gpu_caps_0._pack_ = 1 # source:False
struct_amdsmi_gpu_caps_0._fields_ = [
    ('gfxip_major', ctypes.c_uint32),
    ('gfxip_minor', ctypes.c_uint32),
    ('gfxip_cu_count', ctypes.c_uint16),
    ('PADDING_0', ctypes.c_ubyte * 2),
    ('reserved', ctypes.c_uint32 * 5),
]

class struct_amdsmi_gpu_caps_1(Structure):
    pass

struct_amdsmi_gpu_caps_1._pack_ = 1 # source:False
struct_amdsmi_gpu_caps_1._fields_ = [
    ('mm_ip_count', ctypes.c_ubyte),
    ('mm_ip_list', ctypes.c_ubyte * 8),
    ('PADDING_0', ctypes.c_ubyte * 3),
    ('reserved', ctypes.c_uint32 * 5),
]

struct_amdsmi_gpu_caps._pack_ = 1 # source:False
struct_amdsmi_gpu_caps._fields_ = [
    ('gfx', struct_amdsmi_gpu_caps_0),
    ('mm', struct_amdsmi_gpu_caps_1),
    ('ras_supported', ctypes.c_bool),
    ('max_vf_num', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 2),
    ('gfx_ip_count', ctypes.c_uint32),
    ('dma_ip_count', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32 * 5),
]

amdsmi_gpu_caps_t = struct_amdsmi_gpu_caps
class struct_amdsmi_vram_info(Structure):
    pass

struct_amdsmi_vram_info._pack_ = 1 # source:False
struct_amdsmi_vram_info._fields_ = [
    ('vram_total', ctypes.c_uint32),
    ('vram_used', ctypes.c_uint32),
]

amdsmi_vram_info_t = struct_amdsmi_vram_info
class struct_amdsmi_frequency_range(Structure):
    pass

struct_amdsmi_frequency_range._pack_ = 1 # source:False
struct_amdsmi_frequency_range._fields_ = [
    ('supported_freq_range', amdsmi_range_t),
    ('current_freq_range', amdsmi_range_t),
    ('reserved', ctypes.c_uint32 * 8),
]

amdsmi_frequency_range_t = struct_amdsmi_frequency_range
class union_amdsmi_bdf(Union):
    pass

class struct_amdsmi_bdf_0(Structure):
    pass

struct_amdsmi_bdf_0._pack_ = 1 # source:False
struct_amdsmi_bdf_0._fields_ = [
    ('function_number', ctypes.c_uint64, 3),
    ('device_number', ctypes.c_uint64, 5),
    ('bus_number', ctypes.c_uint64, 8),
    ('domain_number', ctypes.c_uint64, 48),
]

union_amdsmi_bdf._pack_ = 1 # source:False
union_amdsmi_bdf._fields_ = [
    ('amdsmi_bdf_0', struct_amdsmi_bdf_0),
    ('as_uint', ctypes.c_uint64),
]

amdsmi_bdf_t = union_amdsmi_bdf
class struct_amdsmi_power_cap_info(Structure):
    pass

struct_amdsmi_power_cap_info._pack_ = 1 # source:False
struct_amdsmi_power_cap_info._fields_ = [
    ('power_cap', ctypes.c_uint64),
    ('default_power_cap', ctypes.c_uint64),
    ('dpm_cap', ctypes.c_uint64),
    ('min_power_cap', ctypes.c_uint64),
    ('max_power_cap', ctypes.c_uint64),
    ('reserved', ctypes.c_uint64 * 3),
]

amdsmi_power_cap_info_t = struct_amdsmi_power_cap_info
class struct_amdsmi_vbios_info(Structure):
    pass

struct_amdsmi_vbios_info._pack_ = 1 # source:False
struct_amdsmi_vbios_info._fields_ = [
    ('name', ctypes.c_char * 64),
    ('vbios_version', ctypes.c_uint32),
    ('build_date', ctypes.c_char * 32),
    ('part_number', ctypes.c_char * 64),
    ('vbios_version_string', ctypes.c_char * 32),
    ('reserved', ctypes.c_uint32 * 15),
]

amdsmi_vbios_info_t = struct_amdsmi_vbios_info
class struct_amdsmi_fw_info(Structure):
    pass

class struct_amdsmi_fw_info_0(Structure):
    pass

struct_amdsmi_fw_info_0._pack_ = 1 # source:False
struct_amdsmi_fw_info_0._fields_ = [
    ('fw_id', amdsmi_fw_block_t),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('fw_version', ctypes.c_uint64),
    ('reserved', ctypes.c_uint64 * 2),
]

struct_amdsmi_fw_info._pack_ = 1 # source:False
struct_amdsmi_fw_info._fields_ = [
    ('num_fw_info', ctypes.c_ubyte),
    ('PADDING_0', ctypes.c_ubyte * 7),
    ('fw_info_list', struct_amdsmi_fw_info_0 * 46),
    ('reserved', ctypes.c_uint32 * 7),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

amdsmi_fw_info_t = struct_amdsmi_fw_info
class struct_amdsmi_asic_info(Structure):
    pass

struct_amdsmi_asic_info._pack_ = 1 # source:False
struct_amdsmi_asic_info._fields_ = [
    ('market_name', ctypes.c_char * 64),
    ('family', ctypes.c_uint32),
    ('vendor_id', ctypes.c_uint32),
    ('subvendor_id', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('device_id', ctypes.c_uint64),
    ('rev_id', ctypes.c_uint32),
    ('asic_serial', ctypes.c_char * 32),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

amdsmi_asic_info_t = struct_amdsmi_asic_info
class struct_amdsmi_board_info(Structure):
    pass

struct_amdsmi_board_info._pack_ = 1 # source:False
struct_amdsmi_board_info._fields_ = [
    ('serial_number', ctypes.c_uint64),
    ('is_master', ctypes.c_bool),
    ('model_number', ctypes.c_char * 32),
    ('product_serial', ctypes.c_char * 32),
    ('fru_id', ctypes.c_char * 32),
    ('product_name', ctypes.c_char * 128),
    ('manufacturer_name', ctypes.c_char * 32),
    ('PADDING_0', ctypes.c_ubyte * 7),
]

amdsmi_board_info_t = struct_amdsmi_board_info
class struct_amdsmi_temperature(Structure):
    pass

struct_amdsmi_temperature._pack_ = 1 # source:False
struct_amdsmi_temperature._fields_ = [
    ('cur_temp', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32 * 7),
]

amdsmi_temperature_t = struct_amdsmi_temperature
class struct_amdsmi_temperature_limit(Structure):
    pass

struct_amdsmi_temperature_limit._pack_ = 1 # source:False
struct_amdsmi_temperature_limit._fields_ = [
    ('limit', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32 * 7),
]

amdsmi_temperature_limit_t = struct_amdsmi_temperature_limit
class struct_amdsmi_power_limit(Structure):
    pass

struct_amdsmi_power_limit._pack_ = 1 # source:False
struct_amdsmi_power_limit._fields_ = [
    ('limit', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32 * 7),
]

amdsmi_power_limit_t = struct_amdsmi_power_limit
class struct_amdsmi_power_measure(Structure):
    pass

struct_amdsmi_power_measure._pack_ = 1 # source:False
struct_amdsmi_power_measure._fields_ = [
    ('average_socket_power', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('energy_accumulator', ctypes.c_uint64),
    ('voltage_gfx', ctypes.c_uint32),
    ('voltage_soc', ctypes.c_uint32),
    ('voltage_mem', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32 * 10),
    ('PADDING_1', ctypes.c_ubyte * 4),
]

amdsmi_power_measure_t = struct_amdsmi_power_measure
class struct_amdsmi_clk_measure(Structure):
    pass

struct_amdsmi_clk_measure._pack_ = 1 # source:False
struct_amdsmi_clk_measure._fields_ = [
    ('cur_clk', ctypes.c_uint32),
    ('avg_clk', ctypes.c_uint32),
    ('min_clk', ctypes.c_uint32),
    ('max_clk', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32 * 4),
]

amdsmi_clk_measure_t = struct_amdsmi_clk_measure
class struct_amdsmi_engine_usage(Structure):
    pass

struct_amdsmi_engine_usage._pack_ = 1 # source:False
struct_amdsmi_engine_usage._fields_ = [
    ('gfx_activity', ctypes.c_uint32),
    ('umc_activity', ctypes.c_uint32),
    ('mm_activity', ctypes.c_uint32 * 8),
    ('reserved', ctypes.c_uint32 * 6),
]

amdsmi_engine_usage_t = struct_amdsmi_engine_usage
amdsmi_process_handle = ctypes.c_uint32
class struct_amdsmi_process_info(Structure):
    pass

class struct_amdsmi_process_info_1(Structure):
    pass

struct_amdsmi_process_info_1._pack_ = 1 # source:False
struct_amdsmi_process_info_1._fields_ = [
    ('gtt_mem', ctypes.c_uint64),
    ('cpu_mem', ctypes.c_uint64),
    ('vram_mem', ctypes.c_uint64),
]

class struct_amdsmi_process_info_0(Structure):
    pass

struct_amdsmi_process_info_0._pack_ = 1 # source:False
struct_amdsmi_process_info_0._fields_ = [
    ('gfx', ctypes.c_uint16 * 8),
    ('compute', ctypes.c_uint16 * 8),
    ('sdma', ctypes.c_uint16 * 8),
    ('enc', ctypes.c_uint16 * 8),
    ('dec', ctypes.c_uint16 * 8),
]

struct_amdsmi_process_info._pack_ = 1 # source:False
struct_amdsmi_process_info._fields_ = [
    ('name', ctypes.c_char * 32),
    ('pid', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('mem', ctypes.c_uint64),
    ('engine_usage', struct_amdsmi_process_info_0),
    ('memory_usage', struct_amdsmi_process_info_1),
    ('container_name', ctypes.c_char * 32),
    ('reserved', ctypes.c_uint32 * 10),
]

amdsmi_proc_info_t = struct_amdsmi_process_info

# values for enumeration 'c__EA_amdsmi_dev_perf_level_t'
c__EA_amdsmi_dev_perf_level_t__enumvalues = {
    0: 'AMDSMI_DEV_PERF_LEVEL_AUTO',
    0: 'AMDSMI_DEV_PERF_LEVEL_FIRST',
    1: 'AMDSMI_DEV_PERF_LEVEL_LOW',
    2: 'AMDSMI_DEV_PERF_LEVEL_HIGH',
    3: 'AMDSMI_DEV_PERF_LEVEL_MANUAL',
    4: 'AMDSMI_DEV_PERF_LEVEL_STABLE_STD',
    5: 'AMDSMI_DEV_PERF_LEVEL_STABLE_PEAK',
    6: 'AMDSMI_DEV_PERF_LEVEL_STABLE_MIN_MCLK',
    7: 'AMDSMI_DEV_PERF_LEVEL_STABLE_MIN_SCLK',
    8: 'AMDSMI_DEV_PERF_LEVEL_DETERMINISM',
    8: 'AMDSMI_DEV_PERF_LEVEL_LAST',
    256: 'AMDSMI_DEV_PERF_LEVEL_UNKNOWN',
}
AMDSMI_DEV_PERF_LEVEL_AUTO = 0
AMDSMI_DEV_PERF_LEVEL_FIRST = 0
AMDSMI_DEV_PERF_LEVEL_LOW = 1
AMDSMI_DEV_PERF_LEVEL_HIGH = 2
AMDSMI_DEV_PERF_LEVEL_MANUAL = 3
AMDSMI_DEV_PERF_LEVEL_STABLE_STD = 4
AMDSMI_DEV_PERF_LEVEL_STABLE_PEAK = 5
AMDSMI_DEV_PERF_LEVEL_STABLE_MIN_MCLK = 6
AMDSMI_DEV_PERF_LEVEL_STABLE_MIN_SCLK = 7
AMDSMI_DEV_PERF_LEVEL_DETERMINISM = 8
AMDSMI_DEV_PERF_LEVEL_LAST = 8
AMDSMI_DEV_PERF_LEVEL_UNKNOWN = 256
c__EA_amdsmi_dev_perf_level_t = ctypes.c_uint32 # enum
amdsmi_dev_perf_level_t = c__EA_amdsmi_dev_perf_level_t
amdsmi_dev_perf_level_t__enumvalues = c__EA_amdsmi_dev_perf_level_t__enumvalues
amdsmi_dev_perf_level = c__EA_amdsmi_dev_perf_level_t
amdsmi_dev_perf_level__enumvalues = c__EA_amdsmi_dev_perf_level_t__enumvalues

# values for enumeration 'c__EA_amdsmi_sw_component_t'
c__EA_amdsmi_sw_component_t__enumvalues = {
    0: 'AMDSMI_SW_COMP_FIRST',
    0: 'AMDSMI_SW_COMP_DRIVER',
    0: 'AMDSMI_SW_COMP_LAST',
}
AMDSMI_SW_COMP_FIRST = 0
AMDSMI_SW_COMP_DRIVER = 0
AMDSMI_SW_COMP_LAST = 0
c__EA_amdsmi_sw_component_t = ctypes.c_uint32 # enum
amdsmi_sw_component_t = c__EA_amdsmi_sw_component_t
amdsmi_sw_component_t__enumvalues = c__EA_amdsmi_sw_component_t__enumvalues
amdsmi_event_handle_t = ctypes.c_uint64

# values for enumeration 'c__EA_amdsmi_event_group_t'
c__EA_amdsmi_event_group_t__enumvalues = {
    0: 'AMDSMI_EVNT_GRP_XGMI',
    10: 'AMDSMI_EVNT_GRP_XGMI_DATA_OUT',
    4294967295: 'AMDSMI_EVNT_GRP_INVALID',
}
AMDSMI_EVNT_GRP_XGMI = 0
AMDSMI_EVNT_GRP_XGMI_DATA_OUT = 10
AMDSMI_EVNT_GRP_INVALID = 4294967295
c__EA_amdsmi_event_group_t = ctypes.c_uint32 # enum
amdsmi_event_group_t = c__EA_amdsmi_event_group_t
amdsmi_event_group_t__enumvalues = c__EA_amdsmi_event_group_t__enumvalues

# values for enumeration 'c__EA_amdsmi_event_type_t'
c__EA_amdsmi_event_type_t__enumvalues = {
    0: 'AMDSMI_EVNT_FIRST',
    0: 'AMDSMI_EVNT_XGMI_FIRST',
    0: 'AMDSMI_EVNT_XGMI_0_NOP_TX',
    1: 'AMDSMI_EVNT_XGMI_0_REQUEST_TX',
    2: 'AMDSMI_EVNT_XGMI_0_RESPONSE_TX',
    3: 'AMDSMI_EVNT_XGMI_0_BEATS_TX',
    4: 'AMDSMI_EVNT_XGMI_1_NOP_TX',
    5: 'AMDSMI_EVNT_XGMI_1_REQUEST_TX',
    6: 'AMDSMI_EVNT_XGMI_1_RESPONSE_TX',
    7: 'AMDSMI_EVNT_XGMI_1_BEATS_TX',
    7: 'AMDSMI_EVNT_XGMI_LAST',
    10: 'AMDSMI_EVNT_XGMI_DATA_OUT_FIRST',
    10: 'AMDSMI_EVNT_XGMI_DATA_OUT_0',
    11: 'AMDSMI_EVNT_XGMI_DATA_OUT_1',
    12: 'AMDSMI_EVNT_XGMI_DATA_OUT_2',
    13: 'AMDSMI_EVNT_XGMI_DATA_OUT_3',
    14: 'AMDSMI_EVNT_XGMI_DATA_OUT_4',
    15: 'AMDSMI_EVNT_XGMI_DATA_OUT_5',
    15: 'AMDSMI_EVNT_XGMI_DATA_OUT_LAST',
    15: 'AMDSMI_EVNT_LAST',
}
AMDSMI_EVNT_FIRST = 0
AMDSMI_EVNT_XGMI_FIRST = 0
AMDSMI_EVNT_XGMI_0_NOP_TX = 0
AMDSMI_EVNT_XGMI_0_REQUEST_TX = 1
AMDSMI_EVNT_XGMI_0_RESPONSE_TX = 2
AMDSMI_EVNT_XGMI_0_BEATS_TX = 3
AMDSMI_EVNT_XGMI_1_NOP_TX = 4
AMDSMI_EVNT_XGMI_1_REQUEST_TX = 5
AMDSMI_EVNT_XGMI_1_RESPONSE_TX = 6
AMDSMI_EVNT_XGMI_1_BEATS_TX = 7
AMDSMI_EVNT_XGMI_LAST = 7
AMDSMI_EVNT_XGMI_DATA_OUT_FIRST = 10
AMDSMI_EVNT_XGMI_DATA_OUT_0 = 10
AMDSMI_EVNT_XGMI_DATA_OUT_1 = 11
AMDSMI_EVNT_XGMI_DATA_OUT_2 = 12
AMDSMI_EVNT_XGMI_DATA_OUT_3 = 13
AMDSMI_EVNT_XGMI_DATA_OUT_4 = 14
AMDSMI_EVNT_XGMI_DATA_OUT_5 = 15
AMDSMI_EVNT_XGMI_DATA_OUT_LAST = 15
AMDSMI_EVNT_LAST = 15
c__EA_amdsmi_event_type_t = ctypes.c_uint32 # enum
amdsmi_event_type_t = c__EA_amdsmi_event_type_t
amdsmi_event_type_t__enumvalues = c__EA_amdsmi_event_type_t__enumvalues

# values for enumeration 'c__EA_amdsmi_counter_command_t'
c__EA_amdsmi_counter_command_t__enumvalues = {
    0: 'AMDSMI_CNTR_CMD_START',
    1: 'AMDSMI_CNTR_CMD_STOP',
}
AMDSMI_CNTR_CMD_START = 0
AMDSMI_CNTR_CMD_STOP = 1
c__EA_amdsmi_counter_command_t = ctypes.c_uint32 # enum
amdsmi_counter_command_t = c__EA_amdsmi_counter_command_t
amdsmi_counter_command_t__enumvalues = c__EA_amdsmi_counter_command_t__enumvalues
class struct_c__SA_amdsmi_counter_value_t(Structure):
    pass

struct_c__SA_amdsmi_counter_value_t._pack_ = 1 # source:False
struct_c__SA_amdsmi_counter_value_t._fields_ = [
    ('value', ctypes.c_uint64),
    ('time_enabled', ctypes.c_uint64),
    ('time_running', ctypes.c_uint64),
]

amdsmi_counter_value_t = struct_c__SA_amdsmi_counter_value_t

# values for enumeration 'c__EA_amdsmi_evt_notification_type_t'
c__EA_amdsmi_evt_notification_type_t__enumvalues = {
    1: 'AMDSMI_EVT_NOTIF_VMFAULT',
    1: 'AMDSMI_EVT_NOTIF_FIRST',
    2: 'AMDSMI_EVT_NOTIF_THERMAL_THROTTLE',
    3: 'AMDSMI_EVT_NOTIF_GPU_PRE_RESET',
    4: 'AMDSMI_EVT_NOTIF_GPU_POST_RESET',
    4: 'AMDSMI_EVT_NOTIF_LAST',
}
AMDSMI_EVT_NOTIF_VMFAULT = 1
AMDSMI_EVT_NOTIF_FIRST = 1
AMDSMI_EVT_NOTIF_THERMAL_THROTTLE = 2
AMDSMI_EVT_NOTIF_GPU_PRE_RESET = 3
AMDSMI_EVT_NOTIF_GPU_POST_RESET = 4
AMDSMI_EVT_NOTIF_LAST = 4
c__EA_amdsmi_evt_notification_type_t = ctypes.c_uint32 # enum
amdsmi_evt_notification_type_t = c__EA_amdsmi_evt_notification_type_t
amdsmi_evt_notification_type_t__enumvalues = c__EA_amdsmi_evt_notification_type_t__enumvalues
class struct_c__SA_amdsmi_evt_notification_data_t(Structure):
    pass

struct_c__SA_amdsmi_evt_notification_data_t._pack_ = 1 # source:False
struct_c__SA_amdsmi_evt_notification_data_t._fields_ = [
    ('device_handle', ctypes.POINTER(None)),
    ('event', amdsmi_evt_notification_type_t),
    ('message', ctypes.c_char * 64),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

amdsmi_evt_notification_data_t = struct_c__SA_amdsmi_evt_notification_data_t

# values for enumeration 'c__EA_amdsmi_temperature_metric_t'
c__EA_amdsmi_temperature_metric_t__enumvalues = {
    0: 'AMDSMI_TEMP_CURRENT',
    0: 'AMDSMI_TEMP_FIRST',
    1: 'AMDSMI_TEMP_MAX',
    2: 'AMDSMI_TEMP_MIN',
    3: 'AMDSMI_TEMP_MAX_HYST',
    4: 'AMDSMI_TEMP_MIN_HYST',
    5: 'AMDSMI_TEMP_CRITICAL',
    6: 'AMDSMI_TEMP_CRITICAL_HYST',
    7: 'AMDSMI_TEMP_EMERGENCY',
    8: 'AMDSMI_TEMP_EMERGENCY_HYST',
    9: 'AMDSMI_TEMP_CRIT_MIN',
    10: 'AMDSMI_TEMP_CRIT_MIN_HYST',
    11: 'AMDSMI_TEMP_OFFSET',
    12: 'AMDSMI_TEMP_LOWEST',
    13: 'AMDSMI_TEMP_HIGHEST',
    13: 'AMDSMI_TEMP_LAST',
}
AMDSMI_TEMP_CURRENT = 0
AMDSMI_TEMP_FIRST = 0
AMDSMI_TEMP_MAX = 1
AMDSMI_TEMP_MIN = 2
AMDSMI_TEMP_MAX_HYST = 3
AMDSMI_TEMP_MIN_HYST = 4
AMDSMI_TEMP_CRITICAL = 5
AMDSMI_TEMP_CRITICAL_HYST = 6
AMDSMI_TEMP_EMERGENCY = 7
AMDSMI_TEMP_EMERGENCY_HYST = 8
AMDSMI_TEMP_CRIT_MIN = 9
AMDSMI_TEMP_CRIT_MIN_HYST = 10
AMDSMI_TEMP_OFFSET = 11
AMDSMI_TEMP_LOWEST = 12
AMDSMI_TEMP_HIGHEST = 13
AMDSMI_TEMP_LAST = 13
c__EA_amdsmi_temperature_metric_t = ctypes.c_uint32 # enum
amdsmi_temperature_metric_t = c__EA_amdsmi_temperature_metric_t
amdsmi_temperature_metric_t__enumvalues = c__EA_amdsmi_temperature_metric_t__enumvalues
amdsmi_temperature_metric = c__EA_amdsmi_temperature_metric_t
amdsmi_temperature_metric__enumvalues = c__EA_amdsmi_temperature_metric_t__enumvalues

# values for enumeration 'c__EA_amdsmi_voltage_metric_t'
c__EA_amdsmi_voltage_metric_t__enumvalues = {
    0: 'AMDSMI_VOLT_CURRENT',
    0: 'AMDSMI_VOLT_FIRST',
    1: 'AMDSMI_VOLT_MAX',
    2: 'AMDSMI_VOLT_MIN_CRIT',
    3: 'AMDSMI_VOLT_MIN',
    4: 'AMDSMI_VOLT_MAX_CRIT',
    5: 'AMDSMI_VOLT_AVERAGE',
    6: 'AMDSMI_VOLT_LOWEST',
    7: 'AMDSMI_VOLT_HIGHEST',
    7: 'AMDSMI_VOLT_LAST',
}
AMDSMI_VOLT_CURRENT = 0
AMDSMI_VOLT_FIRST = 0
AMDSMI_VOLT_MAX = 1
AMDSMI_VOLT_MIN_CRIT = 2
AMDSMI_VOLT_MIN = 3
AMDSMI_VOLT_MAX_CRIT = 4
AMDSMI_VOLT_AVERAGE = 5
AMDSMI_VOLT_LOWEST = 6
AMDSMI_VOLT_HIGHEST = 7
AMDSMI_VOLT_LAST = 7
c__EA_amdsmi_voltage_metric_t = ctypes.c_uint32 # enum
amdsmi_voltage_metric_t = c__EA_amdsmi_voltage_metric_t
amdsmi_voltage_metric_t__enumvalues = c__EA_amdsmi_voltage_metric_t__enumvalues

# values for enumeration 'c__EA_amdsmi_voltage_type_t'
c__EA_amdsmi_voltage_type_t__enumvalues = {
    0: 'AMDSMI_VOLT_TYPE_FIRST',
    0: 'AMDSMI_VOLT_TYPE_VDDGFX',
    0: 'AMDSMI_VOLT_TYPE_LAST',
    4294967295: 'AMDSMI_VOLT_TYPE_INVALID',
}
AMDSMI_VOLT_TYPE_FIRST = 0
AMDSMI_VOLT_TYPE_VDDGFX = 0
AMDSMI_VOLT_TYPE_LAST = 0
AMDSMI_VOLT_TYPE_INVALID = 4294967295
c__EA_amdsmi_voltage_type_t = ctypes.c_uint32 # enum
amdsmi_voltage_type_t = c__EA_amdsmi_voltage_type_t
amdsmi_voltage_type_t__enumvalues = c__EA_amdsmi_voltage_type_t__enumvalues

# values for enumeration 'c__EA_amdsmi_power_profile_preset_masks_t'
c__EA_amdsmi_power_profile_preset_masks_t__enumvalues = {
    1: 'AMDSMI_PWR_PROF_PRST_CUSTOM_MASK',
    2: 'AMDSMI_PWR_PROF_PRST_VIDEO_MASK',
    4: 'AMDSMI_PWR_PROF_PRST_POWER_SAVING_MASK',
    8: 'AMDSMI_PWR_PROF_PRST_COMPUTE_MASK',
    16: 'AMDSMI_PWR_PROF_PRST_VR_MASK',
    32: 'AMDSMI_PWR_PROF_PRST_3D_FULL_SCR_MASK',
    64: 'AMDSMI_PWR_PROF_PRST_BOOTUP_DEFAULT',
    64: 'AMDSMI_PWR_PROF_PRST_LAST',
    18446744073709551615: 'AMDSMI_PWR_PROF_PRST_INVALID',
}
AMDSMI_PWR_PROF_PRST_CUSTOM_MASK = 1
AMDSMI_PWR_PROF_PRST_VIDEO_MASK = 2
AMDSMI_PWR_PROF_PRST_POWER_SAVING_MASK = 4
AMDSMI_PWR_PROF_PRST_COMPUTE_MASK = 8
AMDSMI_PWR_PROF_PRST_VR_MASK = 16
AMDSMI_PWR_PROF_PRST_3D_FULL_SCR_MASK = 32
AMDSMI_PWR_PROF_PRST_BOOTUP_DEFAULT = 64
AMDSMI_PWR_PROF_PRST_LAST = 64
AMDSMI_PWR_PROF_PRST_INVALID = 18446744073709551615
c__EA_amdsmi_power_profile_preset_masks_t = ctypes.c_uint64 # enum
amdsmi_power_profile_preset_masks_t = c__EA_amdsmi_power_profile_preset_masks_t
amdsmi_power_profile_preset_masks_t__enumvalues = c__EA_amdsmi_power_profile_preset_masks_t__enumvalues
amdsmi_power_profile_preset_masks = c__EA_amdsmi_power_profile_preset_masks_t
amdsmi_power_profile_preset_masks__enumvalues = c__EA_amdsmi_power_profile_preset_masks_t__enumvalues

# values for enumeration 'c__EA_amdsmi_gpu_block_t'
c__EA_amdsmi_gpu_block_t__enumvalues = {
    0: 'AMDSMI_GPU_BLOCK_INVALID',
    1: 'AMDSMI_GPU_BLOCK_FIRST',
    1: 'AMDSMI_GPU_BLOCK_UMC',
    2: 'AMDSMI_GPU_BLOCK_SDMA',
    4: 'AMDSMI_GPU_BLOCK_GFX',
    8: 'AMDSMI_GPU_BLOCK_MMHUB',
    16: 'AMDSMI_GPU_BLOCK_ATHUB',
    32: 'AMDSMI_GPU_BLOCK_PCIE_BIF',
    64: 'AMDSMI_GPU_BLOCK_HDP',
    128: 'AMDSMI_GPU_BLOCK_XGMI_WAFL',
    256: 'AMDSMI_GPU_BLOCK_DF',
    512: 'AMDSMI_GPU_BLOCK_SMN',
    1024: 'AMDSMI_GPU_BLOCK_SEM',
    2048: 'AMDSMI_GPU_BLOCK_MP0',
    4096: 'AMDSMI_GPU_BLOCK_MP1',
    8192: 'AMDSMI_GPU_BLOCK_FUSE',
    8192: 'AMDSMI_GPU_BLOCK_LAST',
    9223372036854775808: 'AMDSMI_GPU_BLOCK_RESERVED',
}
AMDSMI_GPU_BLOCK_INVALID = 0
AMDSMI_GPU_BLOCK_FIRST = 1
AMDSMI_GPU_BLOCK_UMC = 1
AMDSMI_GPU_BLOCK_SDMA = 2
AMDSMI_GPU_BLOCK_GFX = 4
AMDSMI_GPU_BLOCK_MMHUB = 8
AMDSMI_GPU_BLOCK_ATHUB = 16
AMDSMI_GPU_BLOCK_PCIE_BIF = 32
AMDSMI_GPU_BLOCK_HDP = 64
AMDSMI_GPU_BLOCK_XGMI_WAFL = 128
AMDSMI_GPU_BLOCK_DF = 256
AMDSMI_GPU_BLOCK_SMN = 512
AMDSMI_GPU_BLOCK_SEM = 1024
AMDSMI_GPU_BLOCK_MP0 = 2048
AMDSMI_GPU_BLOCK_MP1 = 4096
AMDSMI_GPU_BLOCK_FUSE = 8192
AMDSMI_GPU_BLOCK_LAST = 8192
AMDSMI_GPU_BLOCK_RESERVED = 9223372036854775808
c__EA_amdsmi_gpu_block_t = ctypes.c_uint64 # enum
amdsmi_gpu_block_t = c__EA_amdsmi_gpu_block_t
amdsmi_gpu_block_t__enumvalues = c__EA_amdsmi_gpu_block_t__enumvalues
amdsmi_gpu_block = c__EA_amdsmi_gpu_block_t
amdsmi_gpu_block__enumvalues = c__EA_amdsmi_gpu_block_t__enumvalues

# values for enumeration 'c__EA_amdsmi_ras_err_state_t'
c__EA_amdsmi_ras_err_state_t__enumvalues = {
    0: 'AMDSMI_RAS_ERR_STATE_NONE',
    1: 'AMDSMI_RAS_ERR_STATE_DISABLED',
    2: 'AMDSMI_RAS_ERR_STATE_PARITY',
    3: 'AMDSMI_RAS_ERR_STATE_SING_C',
    4: 'AMDSMI_RAS_ERR_STATE_MULT_UC',
    5: 'AMDSMI_RAS_ERR_STATE_POISON',
    6: 'AMDSMI_RAS_ERR_STATE_ENABLED',
    6: 'AMDSMI_RAS_ERR_STATE_LAST',
    4294967295: 'AMDSMI_RAS_ERR_STATE_INVALID',
}
AMDSMI_RAS_ERR_STATE_NONE = 0
AMDSMI_RAS_ERR_STATE_DISABLED = 1
AMDSMI_RAS_ERR_STATE_PARITY = 2
AMDSMI_RAS_ERR_STATE_SING_C = 3
AMDSMI_RAS_ERR_STATE_MULT_UC = 4
AMDSMI_RAS_ERR_STATE_POISON = 5
AMDSMI_RAS_ERR_STATE_ENABLED = 6
AMDSMI_RAS_ERR_STATE_LAST = 6
AMDSMI_RAS_ERR_STATE_INVALID = 4294967295
c__EA_amdsmi_ras_err_state_t = ctypes.c_uint32 # enum
amdsmi_ras_err_state_t = c__EA_amdsmi_ras_err_state_t
amdsmi_ras_err_state_t__enumvalues = c__EA_amdsmi_ras_err_state_t__enumvalues

# values for enumeration 'c__EA_amdsmi_memory_type_t'
c__EA_amdsmi_memory_type_t__enumvalues = {
    0: 'AMDSMI_MEM_TYPE_FIRST',
    0: 'AMDSMI_MEM_TYPE_VRAM',
    1: 'AMDSMI_MEM_TYPE_VIS_VRAM',
    2: 'AMDSMI_MEM_TYPE_GTT',
    2: 'AMDSMI_MEM_TYPE_LAST',
}
AMDSMI_MEM_TYPE_FIRST = 0
AMDSMI_MEM_TYPE_VRAM = 0
AMDSMI_MEM_TYPE_VIS_VRAM = 1
AMDSMI_MEM_TYPE_GTT = 2
AMDSMI_MEM_TYPE_LAST = 2
c__EA_amdsmi_memory_type_t = ctypes.c_uint32 # enum
amdsmi_memory_type_t = c__EA_amdsmi_memory_type_t
amdsmi_memory_type_t__enumvalues = c__EA_amdsmi_memory_type_t__enumvalues

# values for enumeration 'c__EA_amdsmi_freq_ind_t'
c__EA_amdsmi_freq_ind_t__enumvalues = {
    0: 'AMDSMI_FREQ_IND_MIN',
    1: 'AMDSMI_FREQ_IND_MAX',
    4294967295: 'AMDSMI_FREQ_IND_INVALID',
}
AMDSMI_FREQ_IND_MIN = 0
AMDSMI_FREQ_IND_MAX = 1
AMDSMI_FREQ_IND_INVALID = 4294967295
c__EA_amdsmi_freq_ind_t = ctypes.c_uint32 # enum
amdsmi_freq_ind_t = c__EA_amdsmi_freq_ind_t
amdsmi_freq_ind_t__enumvalues = c__EA_amdsmi_freq_ind_t__enumvalues
amdsmi_freq_ind = c__EA_amdsmi_freq_ind_t
amdsmi_freq_ind__enumvalues = c__EA_amdsmi_freq_ind_t__enumvalues

# values for enumeration 'c__EA_amdsmi_xgmi_status_t'
c__EA_amdsmi_xgmi_status_t__enumvalues = {
    0: 'AMDSMI_XGMI_STATUS_NO_ERRORS',
    1: 'AMDSMI_XGMI_STATUS_ERROR',
    2: 'AMDSMI_XGMI_STATUS_MULTIPLE_ERRORS',
}
AMDSMI_XGMI_STATUS_NO_ERRORS = 0
AMDSMI_XGMI_STATUS_ERROR = 1
AMDSMI_XGMI_STATUS_MULTIPLE_ERRORS = 2
c__EA_amdsmi_xgmi_status_t = ctypes.c_uint32 # enum
amdsmi_xgmi_status_t = c__EA_amdsmi_xgmi_status_t
amdsmi_xgmi_status_t__enumvalues = c__EA_amdsmi_xgmi_status_t__enumvalues
amdsmi_bit_field_t = ctypes.c_uint64
amdsmi_bit_field = ctypes.c_uint64

# values for enumeration 'c__EA_amdsmi_memory_page_status_t'
c__EA_amdsmi_memory_page_status_t__enumvalues = {
    0: 'AMDSMI_MEM_PAGE_STATUS_RESERVED',
    1: 'AMDSMI_MEM_PAGE_STATUS_PENDING',
    2: 'AMDSMI_MEM_PAGE_STATUS_UNRESERVABLE',
}
AMDSMI_MEM_PAGE_STATUS_RESERVED = 0
AMDSMI_MEM_PAGE_STATUS_PENDING = 1
AMDSMI_MEM_PAGE_STATUS_UNRESERVABLE = 2
c__EA_amdsmi_memory_page_status_t = ctypes.c_uint32 # enum
amdsmi_memory_page_status_t = c__EA_amdsmi_memory_page_status_t
amdsmi_memory_page_status_t__enumvalues = c__EA_amdsmi_memory_page_status_t__enumvalues

# values for enumeration '_AMDSMI_IO_LINK_TYPE'
_AMDSMI_IO_LINK_TYPE__enumvalues = {
    0: 'AMDSMI_IOLINK_TYPE_UNDEFINED',
    1: 'AMDSMI_IOLINK_TYPE_PCIEXPRESS',
    2: 'AMDSMI_IOLINK_TYPE_XGMI',
    3: 'AMDSMI_IOLINK_TYPE_NUMIOLINKTYPES',
    4294967295: 'AMDSMI_IOLINK_TYPE_SIZE',
}
AMDSMI_IOLINK_TYPE_UNDEFINED = 0
AMDSMI_IOLINK_TYPE_PCIEXPRESS = 1
AMDSMI_IOLINK_TYPE_XGMI = 2
AMDSMI_IOLINK_TYPE_NUMIOLINKTYPES = 3
AMDSMI_IOLINK_TYPE_SIZE = 4294967295
_AMDSMI_IO_LINK_TYPE = ctypes.c_uint32 # enum
AMDSMI_IO_LINK_TYPE = _AMDSMI_IO_LINK_TYPE
AMDSMI_IO_LINK_TYPE__enumvalues = _AMDSMI_IO_LINK_TYPE__enumvalues

# values for enumeration 'c__EA_AMDSMI_UTILIZATION_COUNTER_TYPE'
c__EA_AMDSMI_UTILIZATION_COUNTER_TYPE__enumvalues = {
    0: 'AMDSMI_UTILIZATION_COUNTER_FIRST',
    0: 'AMDSMI_COARSE_GRAIN_GFX_ACTIVITY',
    1: 'AMDSMI_COARSE_GRAIN_MEM_ACTIVITY',
    1: 'AMDSMI_UTILIZATION_COUNTER_LAST',
}
AMDSMI_UTILIZATION_COUNTER_FIRST = 0
AMDSMI_COARSE_GRAIN_GFX_ACTIVITY = 0
AMDSMI_COARSE_GRAIN_MEM_ACTIVITY = 1
AMDSMI_UTILIZATION_COUNTER_LAST = 1
c__EA_AMDSMI_UTILIZATION_COUNTER_TYPE = ctypes.c_uint32 # enum
AMDSMI_UTILIZATION_COUNTER_TYPE = c__EA_AMDSMI_UTILIZATION_COUNTER_TYPE
AMDSMI_UTILIZATION_COUNTER_TYPE__enumvalues = c__EA_AMDSMI_UTILIZATION_COUNTER_TYPE__enumvalues
class struct_c__SA_amdsmi_utilization_counter_t(Structure):
    pass

struct_c__SA_amdsmi_utilization_counter_t._pack_ = 1 # source:False
struct_c__SA_amdsmi_utilization_counter_t._fields_ = [
    ('type', AMDSMI_UTILIZATION_COUNTER_TYPE),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('value', ctypes.c_uint64),
]

amdsmi_utilization_counter_t = struct_c__SA_amdsmi_utilization_counter_t
class struct_c__SA_amdsmi_retired_page_record_t(Structure):
    pass

struct_c__SA_amdsmi_retired_page_record_t._pack_ = 1 # source:False
struct_c__SA_amdsmi_retired_page_record_t._fields_ = [
    ('page_address', ctypes.c_uint64),
    ('page_size', ctypes.c_uint64),
    ('status', amdsmi_memory_page_status_t),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

amdsmi_retired_page_record_t = struct_c__SA_amdsmi_retired_page_record_t
class struct_c__SA_amdsmi_power_profile_status_t(Structure):
    pass

struct_c__SA_amdsmi_power_profile_status_t._pack_ = 1 # source:False
struct_c__SA_amdsmi_power_profile_status_t._fields_ = [
    ('available_profiles', ctypes.c_uint64),
    ('current', amdsmi_power_profile_preset_masks_t),
    ('num_profiles', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

amdsmi_power_profile_status_t = struct_c__SA_amdsmi_power_profile_status_t
amdsmi_power_profile_status = struct_c__SA_amdsmi_power_profile_status_t
class struct_c__SA_amdsmi_frequencies_t(Structure):
    pass

struct_c__SA_amdsmi_frequencies_t._pack_ = 1 # source:False
struct_c__SA_amdsmi_frequencies_t._fields_ = [
    ('num_supported', ctypes.c_uint32),
    ('current', ctypes.c_uint32),
    ('frequency', ctypes.c_uint64 * 32),
]

amdsmi_frequencies_t = struct_c__SA_amdsmi_frequencies_t
amdsmi_frequencies = struct_c__SA_amdsmi_frequencies_t
class struct_c__SA_amdsmi_pcie_bandwidth_t(Structure):
    pass

struct_c__SA_amdsmi_pcie_bandwidth_t._pack_ = 1 # source:False
struct_c__SA_amdsmi_pcie_bandwidth_t._fields_ = [
    ('transfer_rate', amdsmi_frequencies_t),
    ('lanes', ctypes.c_uint32 * 32),
]

amdsmi_pcie_bandwidth_t = struct_c__SA_amdsmi_pcie_bandwidth_t
amdsmi_pcie_bandwidth = struct_c__SA_amdsmi_pcie_bandwidth_t
class struct_c__SA_amdsmi_version_t(Structure):
    pass

struct_c__SA_amdsmi_version_t._pack_ = 1 # source:False
struct_c__SA_amdsmi_version_t._fields_ = [
    ('major', ctypes.c_uint32),
    ('minor', ctypes.c_uint32),
    ('patch', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
    ('build', ctypes.POINTER(ctypes.c_char)),
    ('reserved', ctypes.c_uint32 * 4),
]

amdsmi_version_t = struct_c__SA_amdsmi_version_t
amdsmi_version = struct_c__SA_amdsmi_version_t
class struct_c__SA_amdsmi_od_vddc_point_t(Structure):
    pass

struct_c__SA_amdsmi_od_vddc_point_t._pack_ = 1 # source:False
struct_c__SA_amdsmi_od_vddc_point_t._fields_ = [
    ('frequency', ctypes.c_uint64),
    ('voltage', ctypes.c_uint64),
]

amdsmi_od_vddc_point_t = struct_c__SA_amdsmi_od_vddc_point_t
amdsmi_od_vddc_point = struct_c__SA_amdsmi_od_vddc_point_t
class struct_c__SA_amdsmi_freq_volt_region_t(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('freq_range', amdsmi_range_t),
    ('volt_range', amdsmi_range_t),
     ]

amdsmi_freq_volt_region_t = struct_c__SA_amdsmi_freq_volt_region_t
amdsmi_freq_volt_region = struct_c__SA_amdsmi_freq_volt_region_t
class struct_c__SA_amdsmi_od_volt_curve_t(Structure):
    _pack_ = 1 # source:False
    _fields_ = [
    ('vc_points', struct_c__SA_amdsmi_od_vddc_point_t * 3),
     ]

amdsmi_od_volt_curve_t = struct_c__SA_amdsmi_od_volt_curve_t
amdsmi_od_volt_curve = struct_c__SA_amdsmi_od_volt_curve_t
class struct_c__SA_amdsmi_od_volt_freq_data_t(Structure):
    pass

struct_c__SA_amdsmi_od_volt_freq_data_t._pack_ = 1 # source:False
struct_c__SA_amdsmi_od_volt_freq_data_t._fields_ = [
    ('curr_sclk_range', amdsmi_range_t),
    ('curr_mclk_range', amdsmi_range_t),
    ('sclk_freq_limits', amdsmi_range_t),
    ('mclk_freq_limits', amdsmi_range_t),
    ('curve', amdsmi_od_volt_curve_t),
    ('num_regions', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

amdsmi_od_volt_freq_data_t = struct_c__SA_amdsmi_od_volt_freq_data_t
amdsmi_od_volt_freq_data = struct_c__SA_amdsmi_od_volt_freq_data_t
class struct_amd_metrics_table_header_t(Structure):
    pass

struct_amd_metrics_table_header_t._pack_ = 1 # source:False
struct_amd_metrics_table_header_t._fields_ = [
    ('structure_size', ctypes.c_uint16),
    ('format_revision', ctypes.c_ubyte),
    ('content_revision', ctypes.c_ubyte),
]

class struct_c__SA_amdsmi_gpu_metrics_t(Structure):
    pass

struct_c__SA_amdsmi_gpu_metrics_t._pack_ = 1 # source:False
struct_c__SA_amdsmi_gpu_metrics_t._fields_ = [
    ('common_header', struct_amd_metrics_table_header_t),
    ('temperature_edge', ctypes.c_uint16),
    ('temperature_hotspot', ctypes.c_uint16),
    ('temperature_mem', ctypes.c_uint16),
    ('temperature_vrgfx', ctypes.c_uint16),
    ('temperature_vrsoc', ctypes.c_uint16),
    ('temperature_vrmem', ctypes.c_uint16),
    ('average_gfx_activity', ctypes.c_uint16),
    ('average_umc_activity', ctypes.c_uint16),
    ('average_mm_activity', ctypes.c_uint16),
    ('average_socket_power', ctypes.c_uint16),
    ('energy_accumulator', ctypes.c_uint64),
    ('system_clock_counter', ctypes.c_uint64),
    ('average_gfxclk_frequency', ctypes.c_uint16),
    ('average_socclk_frequency', ctypes.c_uint16),
    ('average_uclk_frequency', ctypes.c_uint16),
    ('average_vclk0_frequency', ctypes.c_uint16),
    ('average_dclk0_frequency', ctypes.c_uint16),
    ('average_vclk1_frequency', ctypes.c_uint16),
    ('average_dclk1_frequency', ctypes.c_uint16),
    ('current_gfxclk', ctypes.c_uint16),
    ('current_socclk', ctypes.c_uint16),
    ('current_uclk', ctypes.c_uint16),
    ('current_vclk0', ctypes.c_uint16),
    ('current_dclk0', ctypes.c_uint16),
    ('current_vclk1', ctypes.c_uint16),
    ('current_dclk1', ctypes.c_uint16),
    ('throttle_status', ctypes.c_uint32),
    ('current_fan_speed', ctypes.c_uint16),
    ('pcie_link_width', ctypes.c_uint16),
    ('pcie_link_speed', ctypes.c_uint16),
    ('padding', ctypes.c_uint16),
    ('gfx_activity_acc', ctypes.c_uint32),
    ('mem_actvity_acc', ctypes.c_uint32),
    ('temperature_hbm', ctypes.c_uint16 * 4),
]

amdsmi_gpu_metrics_t = struct_c__SA_amdsmi_gpu_metrics_t
class struct_c__SA_amdsmi_error_count_t(Structure):
    pass

struct_c__SA_amdsmi_error_count_t._pack_ = 1 # source:False
struct_c__SA_amdsmi_error_count_t._fields_ = [
    ('correctable_count', ctypes.c_uint64),
    ('uncorrectable_count', ctypes.c_uint64),
    ('reserved', ctypes.c_uint64 * 2),
]

amdsmi_error_count_t = struct_c__SA_amdsmi_error_count_t
class struct_amdsmi_pcie_info(Structure):
    pass

struct_amdsmi_pcie_info._pack_ = 1 # source:False
struct_amdsmi_pcie_info._fields_ = [
    ('pcie_lanes', ctypes.c_uint16),
    ('PADDING_0', ctypes.c_ubyte * 2),
    ('pcie_speed', ctypes.c_uint32),
    ('reserved', ctypes.c_uint32 * 6),
]

amdsmi_pcie_info_t = struct_amdsmi_pcie_info
class struct_c__SA_amdsmi_process_info_t(Structure):
    pass

struct_c__SA_amdsmi_process_info_t._pack_ = 1 # source:False
struct_c__SA_amdsmi_process_info_t._fields_ = [
    ('process_id', ctypes.c_uint32),
    ('pasid', ctypes.c_uint32),
    ('vram_usage', ctypes.c_uint64),
    ('sdma_usage', ctypes.c_uint64),
    ('cu_occupancy', ctypes.c_uint32),
    ('PADDING_0', ctypes.c_ubyte * 4),
]

amdsmi_process_info_t = struct_c__SA_amdsmi_process_info_t
class struct_amdsmi_func_id_iter_handle(Structure):
    pass

amdsmi_func_id_iter_handle_t = ctypes.POINTER(struct_amdsmi_func_id_iter_handle)
class union_amd_id(Union):
    pass

class union_amd_id_0(Union):
    _pack_ = 1 # source:False
    _fields_ = [
    ('memory_type', amdsmi_memory_type_t),
    ('temp_metric', amdsmi_temperature_metric_t),
    ('evnt_type', amdsmi_event_type_t),
    ('evnt_group', amdsmi_event_group_t),
    ('clk_type', amdsmi_clk_type_t),
    ('fw_block', amdsmi_fw_block_t),
    ('gpu_block_type', amdsmi_gpu_block_t),
     ]

union_amd_id._pack_ = 1 # source:False
union_amd_id._fields_ = [
    ('id', ctypes.c_uint64),
    ('name', ctypes.POINTER(ctypes.c_char)),
    ('amd_id_0', union_amd_id_0),
]

amdsmi_func_id_value_t = union_amd_id
uint64_t = ctypes.c_uint64
amdsmi_init = _libraries['libamd_smi.so'].amdsmi_init
amdsmi_init.restype = amdsmi_status_t
amdsmi_init.argtypes = [uint64_t]
amdsmi_shut_down = _libraries['libamd_smi.so'].amdsmi_shut_down
amdsmi_shut_down.restype = amdsmi_status_t
amdsmi_shut_down.argtypes = []
amdsmi_get_socket_handles = _libraries['libamd_smi.so'].amdsmi_get_socket_handles
amdsmi_get_socket_handles.restype = amdsmi_status_t
amdsmi_get_socket_handles.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.POINTER(None))]
size_t = ctypes.c_uint64
amdsmi_get_socket_info = _libraries['libamd_smi.so'].amdsmi_get_socket_info
amdsmi_get_socket_info.restype = amdsmi_status_t
amdsmi_get_socket_info.argtypes = [amdsmi_socket_handle, ctypes.POINTER(ctypes.c_char), size_t]
amdsmi_get_device_handles = _libraries['libamd_smi.so'].amdsmi_get_device_handles
amdsmi_get_device_handles.restype = amdsmi_status_t
amdsmi_get_device_handles.argtypes = [amdsmi_socket_handle, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.POINTER(None))]
amdsmi_get_device_type = _libraries['libamd_smi.so'].amdsmi_get_device_type
amdsmi_get_device_type.restype = amdsmi_status_t
amdsmi_get_device_type.argtypes = [amdsmi_device_handle, ctypes.POINTER(device_type)]
amdsmi_get_device_handle_from_bdf = _libraries['libamd_smi.so'].amdsmi_get_device_handle_from_bdf
amdsmi_get_device_handle_from_bdf.restype = amdsmi_status_t
amdsmi_get_device_handle_from_bdf.argtypes = [amdsmi_bdf_t, ctypes.POINTER(ctypes.POINTER(None))]
amdsmi_dev_get_id = _libraries['libamd_smi.so'].amdsmi_dev_get_id
amdsmi_dev_get_id.restype = amdsmi_status_t
amdsmi_dev_get_id.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint16)]
amdsmi_dev_get_vendor_name = _libraries['libamd_smi.so'].amdsmi_dev_get_vendor_name
amdsmi_dev_get_vendor_name.restype = amdsmi_status_t
amdsmi_dev_get_vendor_name.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_char), size_t]
uint32_t = ctypes.c_uint32
amdsmi_dev_get_vram_vendor = _libraries['libamd_smi.so'].amdsmi_dev_get_vram_vendor
amdsmi_dev_get_vram_vendor.restype = amdsmi_status_t
amdsmi_dev_get_vram_vendor.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_char), uint32_t]
amdsmi_dev_get_subsystem_id = _libraries['libamd_smi.so'].amdsmi_dev_get_subsystem_id
amdsmi_dev_get_subsystem_id.restype = amdsmi_status_t
amdsmi_dev_get_subsystem_id.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint16)]
amdsmi_dev_get_subsystem_name = _libraries['libamd_smi.so'].amdsmi_dev_get_subsystem_name
amdsmi_dev_get_subsystem_name.restype = amdsmi_status_t
amdsmi_dev_get_subsystem_name.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_char), size_t]
amdsmi_dev_get_drm_render_minor = _libraries['libamd_smi.so'].amdsmi_dev_get_drm_render_minor
amdsmi_dev_get_drm_render_minor.restype = amdsmi_status_t
amdsmi_dev_get_drm_render_minor.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint32)]
amdsmi_dev_get_pci_bandwidth = _libraries['libamd_smi.so'].amdsmi_dev_get_pci_bandwidth
amdsmi_dev_get_pci_bandwidth.restype = amdsmi_status_t
amdsmi_dev_get_pci_bandwidth.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_c__SA_amdsmi_pcie_bandwidth_t)]
amdsmi_dev_get_pci_id = _libraries['libamd_smi.so'].amdsmi_dev_get_pci_id
amdsmi_dev_get_pci_id.restype = amdsmi_status_t
amdsmi_dev_get_pci_id.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint64)]
amdsmi_topo_get_numa_affinity = _libraries['libamd_smi.so'].amdsmi_topo_get_numa_affinity
amdsmi_topo_get_numa_affinity.restype = amdsmi_status_t
amdsmi_topo_get_numa_affinity.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint32)]
amdsmi_dev_get_pci_throughput = _libraries['libamd_smi.so'].amdsmi_dev_get_pci_throughput
amdsmi_dev_get_pci_throughput.restype = amdsmi_status_t
amdsmi_dev_get_pci_throughput.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
amdsmi_dev_get_pci_replay_counter = _libraries['libamd_smi.so'].amdsmi_dev_get_pci_replay_counter
amdsmi_dev_get_pci_replay_counter.restype = amdsmi_status_t
amdsmi_dev_get_pci_replay_counter.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint64)]
amdsmi_dev_set_pci_bandwidth = _libraries['libamd_smi.so'].amdsmi_dev_set_pci_bandwidth
amdsmi_dev_set_pci_bandwidth.restype = amdsmi_status_t
amdsmi_dev_set_pci_bandwidth.argtypes = [amdsmi_device_handle, uint64_t]
amdsmi_dev_get_power_ave = _libraries['libamd_smi.so'].amdsmi_dev_get_power_ave
amdsmi_dev_get_power_ave.restype = amdsmi_status_t
amdsmi_dev_get_power_ave.argtypes = [amdsmi_device_handle, uint32_t, ctypes.POINTER(ctypes.c_uint64)]
amdsmi_dev_get_energy_count = _libraries['libamd_smi.so'].amdsmi_dev_get_energy_count
amdsmi_dev_get_energy_count.restype = amdsmi_status_t
amdsmi_dev_get_energy_count.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_uint64)]
amdsmi_dev_set_power_cap = _libraries['libamd_smi.so'].amdsmi_dev_set_power_cap
amdsmi_dev_set_power_cap.restype = amdsmi_status_t
amdsmi_dev_set_power_cap.argtypes = [amdsmi_device_handle, uint32_t, uint64_t]
amdsmi_dev_set_power_profile = _libraries['libamd_smi.so'].amdsmi_dev_set_power_profile
amdsmi_dev_set_power_profile.restype = amdsmi_status_t
amdsmi_dev_set_power_profile.argtypes = [amdsmi_device_handle, uint32_t, amdsmi_power_profile_preset_masks_t]
amdsmi_dev_get_memory_total = _libraries['libamd_smi.so'].amdsmi_dev_get_memory_total
amdsmi_dev_get_memory_total.restype = amdsmi_status_t
amdsmi_dev_get_memory_total.argtypes = [amdsmi_device_handle, amdsmi_memory_type_t, ctypes.POINTER(ctypes.c_uint64)]
amdsmi_dev_get_memory_usage = _libraries['libamd_smi.so'].amdsmi_dev_get_memory_usage
amdsmi_dev_get_memory_usage.restype = amdsmi_status_t
amdsmi_dev_get_memory_usage.argtypes = [amdsmi_device_handle, amdsmi_memory_type_t, ctypes.POINTER(ctypes.c_uint64)]
amdsmi_get_bad_page_info = _libraries['libamd_smi.so'].amdsmi_get_bad_page_info
amdsmi_get_bad_page_info.restype = amdsmi_status_t
amdsmi_get_bad_page_info.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(struct_c__SA_amdsmi_retired_page_record_t)]
amdsmi_get_ras_block_features_enabled = _libraries['libamd_smi.so'].amdsmi_get_ras_block_features_enabled
amdsmi_get_ras_block_features_enabled.restype = amdsmi_status_t
amdsmi_get_ras_block_features_enabled.argtypes = [amdsmi_device_handle, amdsmi_gpu_block, ctypes.POINTER(c__EA_amdsmi_ras_err_state_t)]
amdsmi_dev_get_memory_busy_percent = _libraries['libamd_smi.so'].amdsmi_dev_get_memory_busy_percent
amdsmi_dev_get_memory_busy_percent.restype = amdsmi_status_t
amdsmi_dev_get_memory_busy_percent.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint32)]
amdsmi_dev_get_memory_reserved_pages = _libraries['libamd_smi.so'].amdsmi_dev_get_memory_reserved_pages
amdsmi_dev_get_memory_reserved_pages.restype = amdsmi_status_t
amdsmi_dev_get_memory_reserved_pages.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(struct_c__SA_amdsmi_retired_page_record_t)]
amdsmi_dev_get_fan_rpms = _libraries['libamd_smi.so'].amdsmi_dev_get_fan_rpms
amdsmi_dev_get_fan_rpms.restype = amdsmi_status_t
amdsmi_dev_get_fan_rpms.argtypes = [amdsmi_device_handle, uint32_t, ctypes.POINTER(ctypes.c_int64)]
amdsmi_dev_get_fan_speed = _libraries['libamd_smi.so'].amdsmi_dev_get_fan_speed
amdsmi_dev_get_fan_speed.restype = amdsmi_status_t
amdsmi_dev_get_fan_speed.argtypes = [amdsmi_device_handle, uint32_t, ctypes.POINTER(ctypes.c_int64)]
amdsmi_dev_get_fan_speed_max = _libraries['libamd_smi.so'].amdsmi_dev_get_fan_speed_max
amdsmi_dev_get_fan_speed_max.restype = amdsmi_status_t
amdsmi_dev_get_fan_speed_max.argtypes = [amdsmi_device_handle, uint32_t, ctypes.POINTER(ctypes.c_uint64)]
amdsmi_dev_get_temp_metric = _libraries['libamd_smi.so'].amdsmi_dev_get_temp_metric
amdsmi_dev_get_temp_metric.restype = amdsmi_status_t
amdsmi_dev_get_temp_metric.argtypes = [amdsmi_device_handle, amdsmi_temperature_type_t, amdsmi_temperature_metric_t, ctypes.POINTER(ctypes.c_int64)]
amdsmi_dev_get_volt_metric = _libraries['libamd_smi.so'].amdsmi_dev_get_volt_metric
amdsmi_dev_get_volt_metric.restype = amdsmi_status_t
amdsmi_dev_get_volt_metric.argtypes = [amdsmi_device_handle, amdsmi_voltage_type_t, amdsmi_voltage_metric_t, ctypes.POINTER(ctypes.c_int64)]
amdsmi_dev_reset_fan = _libraries['libamd_smi.so'].amdsmi_dev_reset_fan
amdsmi_dev_reset_fan.restype = amdsmi_status_t
amdsmi_dev_reset_fan.argtypes = [amdsmi_device_handle, uint32_t]
amdsmi_dev_set_fan_speed = _libraries['libamd_smi.so'].amdsmi_dev_set_fan_speed
amdsmi_dev_set_fan_speed.restype = amdsmi_status_t
amdsmi_dev_set_fan_speed.argtypes = [amdsmi_device_handle, uint32_t, uint64_t]
amdsmi_dev_get_busy_percent = _libraries['libamd_smi.so'].amdsmi_dev_get_busy_percent
amdsmi_dev_get_busy_percent.restype = amdsmi_status_t
amdsmi_dev_get_busy_percent.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint32)]
amdsmi_get_utilization_count = _libraries['libamd_smi.so'].amdsmi_get_utilization_count
amdsmi_get_utilization_count.restype = amdsmi_status_t
amdsmi_get_utilization_count.argtypes = [amdsmi_device_handle, struct_c__SA_amdsmi_utilization_counter_t * 0, uint32_t, ctypes.POINTER(ctypes.c_uint64)]
amdsmi_get_pcie_link_status = _libraries['libamd_smi.so'].amdsmi_get_pcie_link_status
amdsmi_get_pcie_link_status.restype = amdsmi_status_t
amdsmi_get_pcie_link_status.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_amdsmi_pcie_info)]
amdsmi_get_pcie_link_caps = _libraries['libamd_smi.so'].amdsmi_get_pcie_link_caps
amdsmi_get_pcie_link_caps.restype = amdsmi_status_t
amdsmi_get_pcie_link_caps.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_amdsmi_pcie_info)]
amdsmi_dev_get_perf_level = _libraries['libamd_smi.so'].amdsmi_dev_get_perf_level
amdsmi_dev_get_perf_level.restype = amdsmi_status_t
amdsmi_dev_get_perf_level.argtypes = [amdsmi_device_handle, ctypes.POINTER(c__EA_amdsmi_dev_perf_level_t)]
amdsmi_set_perf_determinism_mode = _libraries['libamd_smi.so'].amdsmi_set_perf_determinism_mode
amdsmi_set_perf_determinism_mode.restype = amdsmi_status_t
amdsmi_set_perf_determinism_mode.argtypes = [amdsmi_device_handle, uint64_t]
amdsmi_dev_get_overdrive_level = _libraries['libamd_smi.so'].amdsmi_dev_get_overdrive_level
amdsmi_dev_get_overdrive_level.restype = amdsmi_status_t
amdsmi_dev_get_overdrive_level.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint32)]
amdsmi_dev_get_gpu_clk_freq = _libraries['libamd_smi.so'].amdsmi_dev_get_gpu_clk_freq
amdsmi_dev_get_gpu_clk_freq.restype = amdsmi_status_t
amdsmi_dev_get_gpu_clk_freq.argtypes = [amdsmi_device_handle, amdsmi_clk_type_t, ctypes.POINTER(struct_c__SA_amdsmi_frequencies_t)]
amdsmi_dev_reset_gpu = _libraries['libamd_smi.so'].amdsmi_dev_reset_gpu
amdsmi_dev_reset_gpu.restype = amdsmi_status_t
amdsmi_dev_reset_gpu.argtypes = [amdsmi_device_handle]
amdsmi_dev_get_od_volt_info = _libraries['libamd_smi.so'].amdsmi_dev_get_od_volt_info
amdsmi_dev_get_od_volt_info.restype = amdsmi_status_t
amdsmi_dev_get_od_volt_info.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_c__SA_amdsmi_od_volt_freq_data_t)]
amdsmi_dev_get_gpu_metrics_info = _libraries['libamd_smi.so'].amdsmi_dev_get_gpu_metrics_info
amdsmi_dev_get_gpu_metrics_info.restype = amdsmi_status_t
amdsmi_dev_get_gpu_metrics_info.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_c__SA_amdsmi_gpu_metrics_t)]
amdsmi_dev_set_clk_range = _libraries['libamd_smi.so'].amdsmi_dev_set_clk_range
amdsmi_dev_set_clk_range.restype = amdsmi_status_t
amdsmi_dev_set_clk_range.argtypes = [amdsmi_device_handle, uint64_t, uint64_t, amdsmi_clk_type_t]
amdsmi_dev_set_od_clk_info = _libraries['libamd_smi.so'].amdsmi_dev_set_od_clk_info
amdsmi_dev_set_od_clk_info.restype = amdsmi_status_t
amdsmi_dev_set_od_clk_info.argtypes = [amdsmi_device_handle, amdsmi_freq_ind_t, uint64_t, amdsmi_clk_type_t]
amdsmi_dev_set_od_volt_info = _libraries['libamd_smi.so'].amdsmi_dev_set_od_volt_info
amdsmi_dev_set_od_volt_info.restype = amdsmi_status_t
amdsmi_dev_set_od_volt_info.argtypes = [amdsmi_device_handle, uint32_t, uint64_t, uint64_t]
amdsmi_dev_get_od_volt_curve_regions = _libraries['libamd_smi.so'].amdsmi_dev_get_od_volt_curve_regions
amdsmi_dev_get_od_volt_curve_regions.restype = amdsmi_status_t
amdsmi_dev_get_od_volt_curve_regions.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(struct_c__SA_amdsmi_freq_volt_region_t)]
amdsmi_dev_get_power_profile_presets = _libraries['libamd_smi.so'].amdsmi_dev_get_power_profile_presets
amdsmi_dev_get_power_profile_presets.restype = amdsmi_status_t
amdsmi_dev_get_power_profile_presets.argtypes = [amdsmi_device_handle, uint32_t, ctypes.POINTER(struct_c__SA_amdsmi_power_profile_status_t)]
amdsmi_dev_set_perf_level = _libraries['libamd_smi.so'].amdsmi_dev_set_perf_level
amdsmi_dev_set_perf_level.restype = amdsmi_status_t
amdsmi_dev_set_perf_level.argtypes = [amdsmi_device_handle, amdsmi_dev_perf_level_t]
amdsmi_dev_set_perf_level_v1 = _libraries['libamd_smi.so'].amdsmi_dev_set_perf_level_v1
amdsmi_dev_set_perf_level_v1.restype = amdsmi_status_t
amdsmi_dev_set_perf_level_v1.argtypes = [amdsmi_device_handle, amdsmi_dev_perf_level_t]
amdsmi_dev_set_overdrive_level = _libraries['libamd_smi.so'].amdsmi_dev_set_overdrive_level
amdsmi_dev_set_overdrive_level.restype = amdsmi_status_t
amdsmi_dev_set_overdrive_level.argtypes = [amdsmi_device_handle, uint32_t]
amdsmi_dev_set_overdrive_level_v1 = _libraries['libamd_smi.so'].amdsmi_dev_set_overdrive_level_v1
amdsmi_dev_set_overdrive_level_v1.restype = amdsmi_status_t
amdsmi_dev_set_overdrive_level_v1.argtypes = [amdsmi_device_handle, uint32_t]
amdsmi_dev_set_clk_freq = _libraries['libamd_smi.so'].amdsmi_dev_set_clk_freq
amdsmi_dev_set_clk_freq.restype = amdsmi_status_t
amdsmi_dev_set_clk_freq.argtypes = [amdsmi_device_handle, amdsmi_clk_type_t, uint64_t]
amdsmi_get_version = _libraries['libamd_smi.so'].amdsmi_get_version
amdsmi_get_version.restype = amdsmi_status_t
amdsmi_get_version.argtypes = [ctypes.POINTER(struct_c__SA_amdsmi_version_t)]
amdsmi_get_version_str = _libraries['libamd_smi.so'].amdsmi_get_version_str
amdsmi_get_version_str.restype = amdsmi_status_t
amdsmi_get_version_str.argtypes = [amdsmi_sw_component_t, ctypes.POINTER(ctypes.c_char), uint32_t]
amdsmi_dev_get_ecc_count = _libraries['libamd_smi.so'].amdsmi_dev_get_ecc_count
amdsmi_dev_get_ecc_count.restype = amdsmi_status_t
amdsmi_dev_get_ecc_count.argtypes = [amdsmi_device_handle, amdsmi_gpu_block_t, ctypes.POINTER(struct_c__SA_amdsmi_error_count_t)]
amdsmi_dev_get_ecc_enabled = _libraries['libamd_smi.so'].amdsmi_dev_get_ecc_enabled
amdsmi_dev_get_ecc_enabled.restype = amdsmi_status_t
amdsmi_dev_get_ecc_enabled.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint64)]
amdsmi_dev_get_ecc_status = _libraries['libamd_smi.so'].amdsmi_dev_get_ecc_status
amdsmi_dev_get_ecc_status.restype = amdsmi_status_t
amdsmi_dev_get_ecc_status.argtypes = [amdsmi_device_handle, amdsmi_gpu_block_t, ctypes.POINTER(c__EA_amdsmi_ras_err_state_t)]
amdsmi_status_string = _libraries['libamd_smi.so'].amdsmi_status_string
amdsmi_status_string.restype = amdsmi_status_t
amdsmi_status_string.argtypes = [amdsmi_status_t, ctypes.POINTER(ctypes.POINTER(ctypes.c_char))]
amdsmi_dev_counter_group_supported = _libraries['libamd_smi.so'].amdsmi_dev_counter_group_supported
amdsmi_dev_counter_group_supported.restype = amdsmi_status_t
amdsmi_dev_counter_group_supported.argtypes = [amdsmi_device_handle, amdsmi_event_group_t]
amdsmi_dev_create_counter = _libraries['libamd_smi.so'].amdsmi_dev_create_counter
amdsmi_dev_create_counter.restype = amdsmi_status_t
amdsmi_dev_create_counter.argtypes = [amdsmi_device_handle, amdsmi_event_type_t, ctypes.POINTER(ctypes.c_uint64)]
amdsmi_dev_destroy_counter = _libraries['libamd_smi.so'].amdsmi_dev_destroy_counter
amdsmi_dev_destroy_counter.restype = amdsmi_status_t
amdsmi_dev_destroy_counter.argtypes = [amdsmi_event_handle_t]
amdsmi_control_counter = _libraries['libamd_smi.so'].amdsmi_control_counter
amdsmi_control_counter.restype = amdsmi_status_t
amdsmi_control_counter.argtypes = [amdsmi_event_handle_t, amdsmi_counter_command_t, ctypes.POINTER(None)]
amdsmi_read_counter = _libraries['libamd_smi.so'].amdsmi_read_counter
amdsmi_read_counter.restype = amdsmi_status_t
amdsmi_read_counter.argtypes = [amdsmi_event_handle_t, ctypes.POINTER(struct_c__SA_amdsmi_counter_value_t)]
amdsmi_counter_get_available_counters = _libraries['libamd_smi.so'].amdsmi_counter_get_available_counters
amdsmi_counter_get_available_counters.restype = amdsmi_status_t
amdsmi_counter_get_available_counters.argtypes = [amdsmi_device_handle, amdsmi_event_group_t, ctypes.POINTER(ctypes.c_uint32)]
amdsmi_get_compute_process_info = _libraries['libamd_smi.so'].amdsmi_get_compute_process_info
amdsmi_get_compute_process_info.restype = amdsmi_status_t
amdsmi_get_compute_process_info.argtypes = [ctypes.POINTER(struct_c__SA_amdsmi_process_info_t), ctypes.POINTER(ctypes.c_uint32)]
amdsmi_get_compute_process_info_by_pid = _libraries['libamd_smi.so'].amdsmi_get_compute_process_info_by_pid
amdsmi_get_compute_process_info_by_pid.restype = amdsmi_status_t
amdsmi_get_compute_process_info_by_pid.argtypes = [uint32_t, ctypes.POINTER(struct_c__SA_amdsmi_process_info_t)]
amdsmi_get_compute_process_gpus = _libraries['libamd_smi.so'].amdsmi_get_compute_process_gpus
amdsmi_get_compute_process_gpus.restype = amdsmi_status_t
amdsmi_get_compute_process_gpus.argtypes = [uint32_t, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
amdsmi_dev_xgmi_error_status = _libraries['libamd_smi.so'].amdsmi_dev_xgmi_error_status
amdsmi_dev_xgmi_error_status.restype = amdsmi_status_t
amdsmi_dev_xgmi_error_status.argtypes = [amdsmi_device_handle, ctypes.POINTER(c__EA_amdsmi_xgmi_status_t)]
amdsmi_dev_reset_xgmi_error = _libraries['libamd_smi.so'].amdsmi_dev_reset_xgmi_error
amdsmi_dev_reset_xgmi_error.restype = amdsmi_status_t
amdsmi_dev_reset_xgmi_error.argtypes = [amdsmi_device_handle]
amdsmi_topo_get_numa_node_number = _libraries['libamd_smi.so'].amdsmi_topo_get_numa_node_number
amdsmi_topo_get_numa_node_number.restype = amdsmi_status_t
amdsmi_topo_get_numa_node_number.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint32)]
amdsmi_topo_get_link_weight = _libraries['libamd_smi.so'].amdsmi_topo_get_link_weight
amdsmi_topo_get_link_weight.restype = amdsmi_status_t
amdsmi_topo_get_link_weight.argtypes = [amdsmi_device_handle, amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint64)]
amdsmi_get_minmax_bandwidth = _libraries['libamd_smi.so'].amdsmi_get_minmax_bandwidth
amdsmi_get_minmax_bandwidth.restype = amdsmi_status_t
amdsmi_get_minmax_bandwidth.argtypes = [amdsmi_device_handle, amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
amdsmi_topo_get_link_type = _libraries['libamd_smi.so'].amdsmi_topo_get_link_type
amdsmi_topo_get_link_type.restype = amdsmi_status_t
amdsmi_topo_get_link_type.argtypes = [amdsmi_device_handle, amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(_AMDSMI_IO_LINK_TYPE)]
amdsmi_is_P2P_accessible = _libraries['libamd_smi.so'].amdsmi_is_P2P_accessible
amdsmi_is_P2P_accessible.restype = amdsmi_status_t
amdsmi_is_P2P_accessible.argtypes = [amdsmi_device_handle, amdsmi_device_handle, ctypes.POINTER(ctypes.c_bool)]
amdsmi_dev_open_supported_func_iterator = _libraries['libamd_smi.so'].amdsmi_dev_open_supported_func_iterator
amdsmi_dev_open_supported_func_iterator.restype = amdsmi_status_t
amdsmi_dev_open_supported_func_iterator.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.POINTER(struct_amdsmi_func_id_iter_handle))]
amdsmi_dev_open_supported_variant_iterator = _libraries['libamd_smi.so'].amdsmi_dev_open_supported_variant_iterator
amdsmi_dev_open_supported_variant_iterator.restype = amdsmi_status_t
amdsmi_dev_open_supported_variant_iterator.argtypes = [amdsmi_func_id_iter_handle_t, ctypes.POINTER(ctypes.POINTER(struct_amdsmi_func_id_iter_handle))]
amdsmi_next_func_iter = _libraries['libamd_smi.so'].amdsmi_next_func_iter
amdsmi_next_func_iter.restype = amdsmi_status_t
amdsmi_next_func_iter.argtypes = [amdsmi_func_id_iter_handle_t]
amdsmi_dev_close_supported_func_iterator = _libraries['libamd_smi.so'].amdsmi_dev_close_supported_func_iterator
amdsmi_dev_close_supported_func_iterator.restype = amdsmi_status_t
amdsmi_dev_close_supported_func_iterator.argtypes = [ctypes.POINTER(ctypes.POINTER(struct_amdsmi_func_id_iter_handle))]
amdsmi_get_func_iter_value = _libraries['libamd_smi.so'].amdsmi_get_func_iter_value
amdsmi_get_func_iter_value.restype = amdsmi_status_t
amdsmi_get_func_iter_value.argtypes = [amdsmi_func_id_iter_handle_t, ctypes.POINTER(union_amd_id)]
amdsmi_init_event_notification = _libraries['libamd_smi.so'].amdsmi_init_event_notification
amdsmi_init_event_notification.restype = amdsmi_status_t
amdsmi_init_event_notification.argtypes = [amdsmi_device_handle]
amdsmi_set_event_notification_mask = _libraries['libamd_smi.so'].amdsmi_set_event_notification_mask
amdsmi_set_event_notification_mask.restype = amdsmi_status_t
amdsmi_set_event_notification_mask.argtypes = [amdsmi_device_handle, uint64_t]
amdsmi_get_event_notification = _libraries['libamd_smi.so'].amdsmi_get_event_notification
amdsmi_get_event_notification.restype = amdsmi_status_t
amdsmi_get_event_notification.argtypes = [ctypes.c_int32, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(struct_c__SA_amdsmi_evt_notification_data_t)]
amdsmi_stop_event_notification = _libraries['libamd_smi.so'].amdsmi_stop_event_notification
amdsmi_stop_event_notification.restype = amdsmi_status_t
amdsmi_stop_event_notification.argtypes = [amdsmi_device_handle]
amdsmi_get_device_bdf = _libraries['libamd_smi.so'].amdsmi_get_device_bdf
amdsmi_get_device_bdf.restype = amdsmi_status_t
amdsmi_get_device_bdf.argtypes = [amdsmi_device_handle, ctypes.POINTER(union_amdsmi_bdf)]
amdsmi_get_device_uuid = _libraries['libamd_smi.so'].amdsmi_get_device_uuid
amdsmi_get_device_uuid.restype = amdsmi_status_t
amdsmi_get_device_uuid.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_char)]
amdsmi_get_driver_version = _libraries['libamd_smi.so'].amdsmi_get_driver_version
amdsmi_get_driver_version.restype = amdsmi_status_t
amdsmi_get_driver_version.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_char)]
amdsmi_get_asic_info = _libraries['libamd_smi.so'].amdsmi_get_asic_info
amdsmi_get_asic_info.restype = amdsmi_status_t
amdsmi_get_asic_info.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_amdsmi_asic_info)]
amdsmi_get_board_info = _libraries['libamd_smi.so'].amdsmi_get_board_info
amdsmi_get_board_info.restype = amdsmi_status_t
amdsmi_get_board_info.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_amdsmi_board_info)]
amdsmi_get_power_cap_info = _libraries['libamd_smi.so'].amdsmi_get_power_cap_info
amdsmi_get_power_cap_info.restype = amdsmi_status_t
amdsmi_get_power_cap_info.argtypes = [amdsmi_device_handle, uint32_t, ctypes.POINTER(struct_amdsmi_power_cap_info)]
amdsmi_get_xgmi_info = _libraries['libamd_smi.so'].amdsmi_get_xgmi_info
amdsmi_get_xgmi_info.restype = amdsmi_status_t
amdsmi_get_xgmi_info.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_amdsmi_xgmi_info)]
amdsmi_get_caps_info = _libraries['libamd_smi.so'].amdsmi_get_caps_info
amdsmi_get_caps_info.restype = amdsmi_status_t
amdsmi_get_caps_info.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_amdsmi_gpu_caps)]
amdsmi_get_fw_info = _libraries['libamd_smi.so'].amdsmi_get_fw_info
amdsmi_get_fw_info.restype = amdsmi_status_t
amdsmi_get_fw_info.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_amdsmi_fw_info)]
amdsmi_get_vbios_info = _libraries['libamd_smi.so'].amdsmi_get_vbios_info
amdsmi_get_vbios_info.restype = amdsmi_status_t
amdsmi_get_vbios_info.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_amdsmi_vbios_info)]
amdsmi_get_gpu_activity = _libraries['libamd_smi.so'].amdsmi_get_gpu_activity
amdsmi_get_gpu_activity.restype = amdsmi_status_t
amdsmi_get_gpu_activity.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_amdsmi_engine_usage)]
amdsmi_get_power_measure = _libraries['libamd_smi.so'].amdsmi_get_power_measure
amdsmi_get_power_measure.restype = amdsmi_status_t
amdsmi_get_power_measure.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_amdsmi_power_measure)]
amdsmi_get_clock_measure = _libraries['libamd_smi.so'].amdsmi_get_clock_measure
amdsmi_get_clock_measure.restype = amdsmi_status_t
amdsmi_get_clock_measure.argtypes = [amdsmi_device_handle, amdsmi_clk_type_t, ctypes.POINTER(struct_amdsmi_clk_measure)]
amdsmi_get_temperature_measure = _libraries['libamd_smi.so'].amdsmi_get_temperature_measure
amdsmi_get_temperature_measure.restype = amdsmi_status_t
amdsmi_get_temperature_measure.argtypes = [amdsmi_device_handle, amdsmi_temperature_type_t, ctypes.POINTER(struct_amdsmi_temperature)]
amdsmi_get_temperature_limit = _libraries['libamd_smi.so'].amdsmi_get_temperature_limit
amdsmi_get_temperature_limit.restype = amdsmi_status_t
amdsmi_get_temperature_limit.argtypes = [amdsmi_device_handle, amdsmi_temperature_type_t, ctypes.POINTER(struct_amdsmi_temperature_limit)]
amdsmi_get_power_limit = _libraries['libamd_smi.so'].amdsmi_get_power_limit
amdsmi_get_power_limit.restype = amdsmi_status_t
amdsmi_get_power_limit.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_amdsmi_power_limit)]
amdsmi_get_vram_usage = _libraries['libamd_smi.so'].amdsmi_get_vram_usage
amdsmi_get_vram_usage.restype = amdsmi_status_t
amdsmi_get_vram_usage.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_amdsmi_vram_info)]
amdsmi_get_target_frequency_range = _libraries['libamd_smi.so'].amdsmi_get_target_frequency_range
amdsmi_get_target_frequency_range.restype = amdsmi_status_t
amdsmi_get_target_frequency_range.argtypes = [amdsmi_device_handle, amdsmi_clk_type_t, ctypes.POINTER(struct_amdsmi_frequency_range)]
amdsmi_get_process_list = _libraries['libamd_smi.so'].amdsmi_get_process_list
amdsmi_get_process_list.restype = amdsmi_status_t
amdsmi_get_process_list.argtypes = [amdsmi_device_handle, ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32)]
amdsmi_get_process_info = _libraries['libamd_smi.so'].amdsmi_get_process_info
amdsmi_get_process_info.restype = amdsmi_status_t
amdsmi_get_process_info.argtypes = [amdsmi_device_handle, amdsmi_process_handle, ctypes.POINTER(struct_amdsmi_process_info)]
amdsmi_get_ecc_error_count = _libraries['libamd_smi.so'].amdsmi_get_ecc_error_count
amdsmi_get_ecc_error_count.restype = amdsmi_status_t
amdsmi_get_ecc_error_count.argtypes = [amdsmi_device_handle, ctypes.POINTER(struct_c__SA_amdsmi_error_count_t)]
__all__ = \
    ['AMDSMI_CNTR_CMD_START', 'AMDSMI_CNTR_CMD_STOP',
    'AMDSMI_COARSE_GRAIN_GFX_ACTIVITY',
    'AMDSMI_COARSE_GRAIN_MEM_ACTIVITY', 'AMDSMI_DEV_PERF_LEVEL_AUTO',
    'AMDSMI_DEV_PERF_LEVEL_DETERMINISM',
    'AMDSMI_DEV_PERF_LEVEL_FIRST', 'AMDSMI_DEV_PERF_LEVEL_HIGH',
    'AMDSMI_DEV_PERF_LEVEL_LAST', 'AMDSMI_DEV_PERF_LEVEL_LOW',
    'AMDSMI_DEV_PERF_LEVEL_MANUAL',
    'AMDSMI_DEV_PERF_LEVEL_STABLE_MIN_MCLK',
    'AMDSMI_DEV_PERF_LEVEL_STABLE_MIN_SCLK',
    'AMDSMI_DEV_PERF_LEVEL_STABLE_PEAK',
    'AMDSMI_DEV_PERF_LEVEL_STABLE_STD',
    'AMDSMI_DEV_PERF_LEVEL_UNKNOWN', 'AMDSMI_EVNT_FIRST',
    'AMDSMI_EVNT_GRP_INVALID', 'AMDSMI_EVNT_GRP_XGMI',
    'AMDSMI_EVNT_GRP_XGMI_DATA_OUT', 'AMDSMI_EVNT_LAST',
    'AMDSMI_EVNT_XGMI_0_BEATS_TX', 'AMDSMI_EVNT_XGMI_0_NOP_TX',
    'AMDSMI_EVNT_XGMI_0_REQUEST_TX', 'AMDSMI_EVNT_XGMI_0_RESPONSE_TX',
    'AMDSMI_EVNT_XGMI_1_BEATS_TX', 'AMDSMI_EVNT_XGMI_1_NOP_TX',
    'AMDSMI_EVNT_XGMI_1_REQUEST_TX', 'AMDSMI_EVNT_XGMI_1_RESPONSE_TX',
    'AMDSMI_EVNT_XGMI_DATA_OUT_0', 'AMDSMI_EVNT_XGMI_DATA_OUT_1',
    'AMDSMI_EVNT_XGMI_DATA_OUT_2', 'AMDSMI_EVNT_XGMI_DATA_OUT_3',
    'AMDSMI_EVNT_XGMI_DATA_OUT_4', 'AMDSMI_EVNT_XGMI_DATA_OUT_5',
    'AMDSMI_EVNT_XGMI_DATA_OUT_FIRST',
    'AMDSMI_EVNT_XGMI_DATA_OUT_LAST', 'AMDSMI_EVNT_XGMI_FIRST',
    'AMDSMI_EVNT_XGMI_LAST', 'AMDSMI_EVT_NOTIF_FIRST',
    'AMDSMI_EVT_NOTIF_GPU_POST_RESET',
    'AMDSMI_EVT_NOTIF_GPU_PRE_RESET', 'AMDSMI_EVT_NOTIF_LAST',
    'AMDSMI_EVT_NOTIF_THERMAL_THROTTLE', 'AMDSMI_EVT_NOTIF_VMFAULT',
    'AMDSMI_FREQ_IND_INVALID', 'AMDSMI_FREQ_IND_MAX',
    'AMDSMI_FREQ_IND_MIN', 'AMDSMI_GPU_BLOCK_ATHUB',
    'AMDSMI_GPU_BLOCK_DF', 'AMDSMI_GPU_BLOCK_FIRST',
    'AMDSMI_GPU_BLOCK_FUSE', 'AMDSMI_GPU_BLOCK_GFX',
    'AMDSMI_GPU_BLOCK_HDP', 'AMDSMI_GPU_BLOCK_INVALID',
    'AMDSMI_GPU_BLOCK_LAST', 'AMDSMI_GPU_BLOCK_MMHUB',
    'AMDSMI_GPU_BLOCK_MP0', 'AMDSMI_GPU_BLOCK_MP1',
    'AMDSMI_GPU_BLOCK_PCIE_BIF', 'AMDSMI_GPU_BLOCK_RESERVED',
    'AMDSMI_GPU_BLOCK_SDMA', 'AMDSMI_GPU_BLOCK_SEM',
    'AMDSMI_GPU_BLOCK_SMN', 'AMDSMI_GPU_BLOCK_UMC',
    'AMDSMI_GPU_BLOCK_XGMI_WAFL', 'AMDSMI_INIT_ALL_DEVICES',
    'AMDSMI_INIT_AMD_CPUS', 'AMDSMI_INIT_AMD_GPUS',
    'AMDSMI_INIT_NON_AMD_CPUS', 'AMDSMI_INIT_NON_AMD_GPUS',
    'AMDSMI_IOLINK_TYPE_NUMIOLINKTYPES',
    'AMDSMI_IOLINK_TYPE_PCIEXPRESS', 'AMDSMI_IOLINK_TYPE_SIZE',
    'AMDSMI_IOLINK_TYPE_UNDEFINED', 'AMDSMI_IOLINK_TYPE_XGMI',
    'AMDSMI_IO_LINK_TYPE', 'AMDSMI_IO_LINK_TYPE__enumvalues',
    'AMDSMI_MEM_PAGE_STATUS_PENDING',
    'AMDSMI_MEM_PAGE_STATUS_RESERVED',
    'AMDSMI_MEM_PAGE_STATUS_UNRESERVABLE', 'AMDSMI_MEM_TYPE_FIRST',
    'AMDSMI_MEM_TYPE_GTT', 'AMDSMI_MEM_TYPE_LAST',
    'AMDSMI_MEM_TYPE_VIS_VRAM', 'AMDSMI_MEM_TYPE_VRAM',
    'AMDSMI_MM_UVD', 'AMDSMI_MM_VCE', 'AMDSMI_MM_VCN',
    'AMDSMI_MM__MAX', 'AMDSMI_PWR_PROF_PRST_3D_FULL_SCR_MASK',
    'AMDSMI_PWR_PROF_PRST_BOOTUP_DEFAULT',
    'AMDSMI_PWR_PROF_PRST_COMPUTE_MASK',
    'AMDSMI_PWR_PROF_PRST_CUSTOM_MASK',
    'AMDSMI_PWR_PROF_PRST_INVALID', 'AMDSMI_PWR_PROF_PRST_LAST',
    'AMDSMI_PWR_PROF_PRST_POWER_SAVING_MASK',
    'AMDSMI_PWR_PROF_PRST_VIDEO_MASK', 'AMDSMI_PWR_PROF_PRST_VR_MASK',
    'AMDSMI_RAS_ERR_STATE_DISABLED', 'AMDSMI_RAS_ERR_STATE_ENABLED',
    'AMDSMI_RAS_ERR_STATE_INVALID', 'AMDSMI_RAS_ERR_STATE_LAST',
    'AMDSMI_RAS_ERR_STATE_MULT_UC', 'AMDSMI_RAS_ERR_STATE_NONE',
    'AMDSMI_RAS_ERR_STATE_PARITY', 'AMDSMI_RAS_ERR_STATE_POISON',
    'AMDSMI_RAS_ERR_STATE_SING_C', 'AMDSMI_STATUS_ADDRESS_FAULT',
    'AMDSMI_STATUS_API_FAILED', 'AMDSMI_STATUS_BUSY',
    'AMDSMI_STATUS_DRM_ERROR', 'AMDSMI_STATUS_FAIL_LOAD_MODULE',
    'AMDSMI_STATUS_FAIL_LOAD_SYMBOL', 'AMDSMI_STATUS_FILE_ERROR',
    'AMDSMI_STATUS_INIT_ERROR', 'AMDSMI_STATUS_INPUT_OUT_OF_BOUNDS',
    'AMDSMI_STATUS_INSUFFICIENT_SIZE',
    'AMDSMI_STATUS_INTERNAL_EXCEPTION', 'AMDSMI_STATUS_INTERRUPT',
    'AMDSMI_STATUS_INVAL', 'AMDSMI_STATUS_IO',
    'AMDSMI_STATUS_MAP_ERROR', 'AMDSMI_STATUS_NOT_FOUND',
    'AMDSMI_STATUS_NOT_INIT', 'AMDSMI_STATUS_NOT_SUPPORTED',
    'AMDSMI_STATUS_NOT_YET_IMPLEMENTED', 'AMDSMI_STATUS_NO_DATA',
    'AMDSMI_STATUS_NO_PERM', 'AMDSMI_STATUS_NO_SLOT',
    'AMDSMI_STATUS_OUT_OF_RESOURCES',
    'AMDSMI_STATUS_REFCOUNT_OVERFLOW', 'AMDSMI_STATUS_RETRY',
    'AMDSMI_STATUS_SUCCESS', 'AMDSMI_STATUS_TIMEOUT',
    'AMDSMI_STATUS_UNEXPECTED_DATA', 'AMDSMI_STATUS_UNEXPECTED_SIZE',
    'AMDSMI_STATUS_UNKNOWN_ERROR', 'AMDSMI_SW_COMP_DRIVER',
    'AMDSMI_SW_COMP_FIRST', 'AMDSMI_SW_COMP_LAST',
    'AMDSMI_TEMP_CRITICAL', 'AMDSMI_TEMP_CRITICAL_HYST',
    'AMDSMI_TEMP_CRIT_MIN', 'AMDSMI_TEMP_CRIT_MIN_HYST',
    'AMDSMI_TEMP_CURRENT', 'AMDSMI_TEMP_EMERGENCY',
    'AMDSMI_TEMP_EMERGENCY_HYST', 'AMDSMI_TEMP_FIRST',
    'AMDSMI_TEMP_HIGHEST', 'AMDSMI_TEMP_LAST', 'AMDSMI_TEMP_LOWEST',
    'AMDSMI_TEMP_MAX', 'AMDSMI_TEMP_MAX_HYST', 'AMDSMI_TEMP_MIN',
    'AMDSMI_TEMP_MIN_HYST', 'AMDSMI_TEMP_OFFSET',
    'AMDSMI_UTILIZATION_COUNTER_FIRST',
    'AMDSMI_UTILIZATION_COUNTER_LAST',
    'AMDSMI_UTILIZATION_COUNTER_TYPE',
    'AMDSMI_UTILIZATION_COUNTER_TYPE__enumvalues',
    'AMDSMI_VOLT_AVERAGE', 'AMDSMI_VOLT_CURRENT', 'AMDSMI_VOLT_FIRST',
    'AMDSMI_VOLT_HIGHEST', 'AMDSMI_VOLT_LAST', 'AMDSMI_VOLT_LOWEST',
    'AMDSMI_VOLT_MAX', 'AMDSMI_VOLT_MAX_CRIT', 'AMDSMI_VOLT_MIN',
    'AMDSMI_VOLT_MIN_CRIT', 'AMDSMI_VOLT_TYPE_FIRST',
    'AMDSMI_VOLT_TYPE_INVALID', 'AMDSMI_VOLT_TYPE_LAST',
    'AMDSMI_VOLT_TYPE_VDDGFX', 'AMDSMI_XGMI_STATUS_ERROR',
    'AMDSMI_XGMI_STATUS_MULTIPLE_ERRORS',
    'AMDSMI_XGMI_STATUS_NO_ERRORS', 'AMD_CPU', 'AMD_GPU',
    'CLK_TYPE_DCEF', 'CLK_TYPE_DCLK0', 'CLK_TYPE_DCLK1',
    'CLK_TYPE_DF', 'CLK_TYPE_FIRST', 'CLK_TYPE_GFX', 'CLK_TYPE_MEM',
    'CLK_TYPE_PCIE', 'CLK_TYPE_SOC', 'CLK_TYPE_SYS', 'CLK_TYPE_VCLK0',
    'CLK_TYPE_VCLK1', 'CLK_TYPE__MAX', 'CONTAINER_DOCKER',
    'CONTAINER_LXC', 'FW_ID_ASD', 'FW_ID_CP_CE', 'FW_ID_CP_ME',
    'FW_ID_CP_MEC1', 'FW_ID_CP_MEC2', 'FW_ID_CP_MEC_JT1',
    'FW_ID_CP_MEC_JT2', 'FW_ID_CP_PFP', 'FW_ID_CP_PM4', 'FW_ID_DFC',
    'FW_ID_DMCU', 'FW_ID_DMCU_ERAM', 'FW_ID_DMCU_ISR',
    'FW_ID_DRV_CAP', 'FW_ID_FIRST', 'FW_ID_ISP', 'FW_ID_MC',
    'FW_ID_MMSCH', 'FW_ID_PSP_BL', 'FW_ID_PSP_KEYDB',
    'FW_ID_PSP_SOSDRV', 'FW_ID_PSP_SPL', 'FW_ID_PSP_SYSDRV',
    'FW_ID_PSP_TOC', 'FW_ID_RLC', 'FW_ID_RLC_RESTORE_LIST_CNTL',
    'FW_ID_RLC_RESTORE_LIST_GPM_MEM',
    'FW_ID_RLC_RESTORE_LIST_SRM_MEM', 'FW_ID_RLC_SRLG',
    'FW_ID_RLC_SRLS', 'FW_ID_RLC_V', 'FW_ID_SDMA0', 'FW_ID_SDMA1',
    'FW_ID_SDMA2', 'FW_ID_SDMA3', 'FW_ID_SDMA4', 'FW_ID_SDMA5',
    'FW_ID_SDMA6', 'FW_ID_SDMA7', 'FW_ID_SMC', 'FW_ID_SMU',
    'FW_ID_TA_RAS', 'FW_ID_UVD', 'FW_ID_VCE', 'FW_ID_VCN',
    'FW_ID_XGMI', 'FW_ID__MAX', 'NON_AMD_CPU', 'NON_AMD_GPU',
    'TEMPERATURE_TYPE_EDGE', 'TEMPERATURE_TYPE_FIRST',
    'TEMPERATURE_TYPE_HBM_0', 'TEMPERATURE_TYPE_HBM_1',
    'TEMPERATURE_TYPE_HBM_2', 'TEMPERATURE_TYPE_HBM_3',
    'TEMPERATURE_TYPE_JUNCTION', 'TEMPERATURE_TYPE_PLX',
    'TEMPERATURE_TYPE_VRAM', 'TEMPERATURE_TYPE__MAX', 'UNKNOWN',
    '_AMDSMI_IO_LINK_TYPE', 'amdsmi_asic_info_t', 'amdsmi_bdf_t',
    'amdsmi_bit_field', 'amdsmi_bit_field_t', 'amdsmi_board_info_t',
    'amdsmi_clk_measure_t', 'amdsmi_clk_type', 'amdsmi_clk_type_t',
    'amdsmi_clk_type_t__enumvalues', 'amdsmi_container_types',
    'amdsmi_container_types_t',
    'amdsmi_container_types_t__enumvalues', 'amdsmi_control_counter',
    'amdsmi_counter_command_t',
    'amdsmi_counter_command_t__enumvalues',
    'amdsmi_counter_get_available_counters', 'amdsmi_counter_value_t',
    'amdsmi_dev_close_supported_func_iterator',
    'amdsmi_dev_counter_group_supported', 'amdsmi_dev_create_counter',
    'amdsmi_dev_destroy_counter', 'amdsmi_dev_get_busy_percent',
    'amdsmi_dev_get_drm_render_minor', 'amdsmi_dev_get_ecc_count',
    'amdsmi_dev_get_ecc_enabled', 'amdsmi_dev_get_ecc_status',
    'amdsmi_dev_get_energy_count', 'amdsmi_dev_get_fan_rpms',
    'amdsmi_dev_get_fan_speed', 'amdsmi_dev_get_fan_speed_max',
    'amdsmi_dev_get_gpu_clk_freq', 'amdsmi_dev_get_gpu_metrics_info',
    'amdsmi_dev_get_id', 'amdsmi_dev_get_memory_busy_percent',
    'amdsmi_dev_get_memory_reserved_pages',
    'amdsmi_dev_get_memory_total', 'amdsmi_dev_get_memory_usage',
    'amdsmi_dev_get_od_volt_curve_regions',
    'amdsmi_dev_get_od_volt_info', 'amdsmi_dev_get_overdrive_level',
    'amdsmi_dev_get_pci_bandwidth', 'amdsmi_dev_get_pci_id',
    'amdsmi_dev_get_pci_replay_counter',
    'amdsmi_dev_get_pci_throughput', 'amdsmi_dev_get_perf_level',
    'amdsmi_dev_get_power_ave',
    'amdsmi_dev_get_power_profile_presets',
    'amdsmi_dev_get_subsystem_id', 'amdsmi_dev_get_subsystem_name',
    'amdsmi_dev_get_temp_metric', 'amdsmi_dev_get_vendor_name',
    'amdsmi_dev_get_volt_metric', 'amdsmi_dev_get_vram_vendor',
    'amdsmi_dev_open_supported_func_iterator',
    'amdsmi_dev_open_supported_variant_iterator',
    'amdsmi_dev_perf_level', 'amdsmi_dev_perf_level__enumvalues',
    'amdsmi_dev_perf_level_t', 'amdsmi_dev_perf_level_t__enumvalues',
    'amdsmi_dev_reset_fan', 'amdsmi_dev_reset_gpu',
    'amdsmi_dev_reset_xgmi_error', 'amdsmi_dev_set_clk_freq',
    'amdsmi_dev_set_clk_range', 'amdsmi_dev_set_fan_speed',
    'amdsmi_dev_set_od_clk_info', 'amdsmi_dev_set_od_volt_info',
    'amdsmi_dev_set_overdrive_level',
    'amdsmi_dev_set_overdrive_level_v1',
    'amdsmi_dev_set_pci_bandwidth', 'amdsmi_dev_set_perf_level',
    'amdsmi_dev_set_perf_level_v1', 'amdsmi_dev_set_power_cap',
    'amdsmi_dev_set_power_profile', 'amdsmi_dev_xgmi_error_status',
    'amdsmi_device_handle', 'amdsmi_engine_usage_t',
    'amdsmi_error_count_t', 'amdsmi_event_group_t',
    'amdsmi_event_group_t__enumvalues', 'amdsmi_event_handle_t',
    'amdsmi_event_type_t', 'amdsmi_event_type_t__enumvalues',
    'amdsmi_evt_notification_data_t',
    'amdsmi_evt_notification_type_t',
    'amdsmi_evt_notification_type_t__enumvalues', 'amdsmi_freq_ind',
    'amdsmi_freq_ind__enumvalues', 'amdsmi_freq_ind_t',
    'amdsmi_freq_ind_t__enumvalues', 'amdsmi_freq_volt_region',
    'amdsmi_freq_volt_region_t', 'amdsmi_frequencies',
    'amdsmi_frequencies_t', 'amdsmi_frequency_range_t',
    'amdsmi_func_id_iter_handle_t', 'amdsmi_func_id_value_t',
    'amdsmi_fw_block', 'amdsmi_fw_block_t',
    'amdsmi_fw_block_t__enumvalues', 'amdsmi_fw_info_t',
    'amdsmi_get_asic_info', 'amdsmi_get_bad_page_info',
    'amdsmi_get_board_info', 'amdsmi_get_caps_info',
    'amdsmi_get_clock_measure', 'amdsmi_get_compute_process_gpus',
    'amdsmi_get_compute_process_info',
    'amdsmi_get_compute_process_info_by_pid', 'amdsmi_get_device_bdf',
    'amdsmi_get_device_handle_from_bdf', 'amdsmi_get_device_handles',
    'amdsmi_get_device_type', 'amdsmi_get_device_uuid',
    'amdsmi_get_driver_version', 'amdsmi_get_ecc_error_count',
    'amdsmi_get_event_notification', 'amdsmi_get_func_iter_value',
    'amdsmi_get_fw_info', 'amdsmi_get_gpu_activity',
    'amdsmi_get_minmax_bandwidth', 'amdsmi_get_pcie_link_caps',
    'amdsmi_get_pcie_link_status', 'amdsmi_get_power_cap_info',
    'amdsmi_get_power_limit', 'amdsmi_get_power_measure',
    'amdsmi_get_process_info', 'amdsmi_get_process_list',
    'amdsmi_get_ras_block_features_enabled',
    'amdsmi_get_socket_handles', 'amdsmi_get_socket_info',
    'amdsmi_get_target_frequency_range',
    'amdsmi_get_temperature_limit', 'amdsmi_get_temperature_measure',
    'amdsmi_get_utilization_count', 'amdsmi_get_vbios_info',
    'amdsmi_get_version', 'amdsmi_get_version_str',
    'amdsmi_get_vram_usage', 'amdsmi_get_xgmi_info',
    'amdsmi_gpu_block', 'amdsmi_gpu_block__enumvalues',
    'amdsmi_gpu_block_t', 'amdsmi_gpu_block_t__enumvalues',
    'amdsmi_gpu_caps_t', 'amdsmi_gpu_metrics_t', 'amdsmi_init',
    'amdsmi_init_event_notification', 'amdsmi_init_flags',
    'amdsmi_init_flags_t', 'amdsmi_init_flags_t__enumvalues',
    'amdsmi_is_P2P_accessible', 'amdsmi_memory_page_status_t',
    'amdsmi_memory_page_status_t__enumvalues', 'amdsmi_memory_type_t',
    'amdsmi_memory_type_t__enumvalues', 'amdsmi_mm_ip',
    'amdsmi_mm_ip_t', 'amdsmi_mm_ip_t__enumvalues',
    'amdsmi_next_func_iter', 'amdsmi_od_vddc_point',
    'amdsmi_od_vddc_point_t', 'amdsmi_od_volt_curve',
    'amdsmi_od_volt_curve_t', 'amdsmi_od_volt_freq_data',
    'amdsmi_od_volt_freq_data_t', 'amdsmi_pcie_bandwidth',
    'amdsmi_pcie_bandwidth_t', 'amdsmi_pcie_info_t',
    'amdsmi_power_cap_info_t', 'amdsmi_power_limit_t',
    'amdsmi_power_measure_t', 'amdsmi_power_profile_preset_masks',
    'amdsmi_power_profile_preset_masks__enumvalues',
    'amdsmi_power_profile_preset_masks_t',
    'amdsmi_power_profile_preset_masks_t__enumvalues',
    'amdsmi_power_profile_status', 'amdsmi_power_profile_status_t',
    'amdsmi_proc_info_t', 'amdsmi_process_handle',
    'amdsmi_process_info_t', 'amdsmi_range', 'amdsmi_range_t',
    'amdsmi_ras_err_state_t', 'amdsmi_ras_err_state_t__enumvalues',
    'amdsmi_read_counter', 'amdsmi_retired_page_record_t',
    'amdsmi_set_event_notification_mask',
    'amdsmi_set_perf_determinism_mode', 'amdsmi_shut_down',
    'amdsmi_socket_handle', 'amdsmi_status_string', 'amdsmi_status_t',
    'amdsmi_stop_event_notification', 'amdsmi_sw_component_t',
    'amdsmi_sw_component_t__enumvalues', 'amdsmi_temperature_limit_t',
    'amdsmi_temperature_metric',
    'amdsmi_temperature_metric__enumvalues',
    'amdsmi_temperature_metric_t',
    'amdsmi_temperature_metric_t__enumvalues', 'amdsmi_temperature_t',
    'amdsmi_temperature_type', 'amdsmi_temperature_type_t',
    'amdsmi_temperature_type_t__enumvalues',
    'amdsmi_topo_get_link_type', 'amdsmi_topo_get_link_weight',
    'amdsmi_topo_get_numa_affinity',
    'amdsmi_topo_get_numa_node_number',
    'amdsmi_utilization_counter_t', 'amdsmi_vbios_info_t',
    'amdsmi_version', 'amdsmi_version_t', 'amdsmi_voltage_metric_t',
    'amdsmi_voltage_metric_t__enumvalues', 'amdsmi_voltage_type_t',
    'amdsmi_voltage_type_t__enumvalues', 'amdsmi_vram_info_t',
    'amdsmi_xgmi_info_t', 'amdsmi_xgmi_status_t',
    'amdsmi_xgmi_status_t__enumvalues',
    'c__EA_AMDSMI_UTILIZATION_COUNTER_TYPE',
    'c__EA_amdsmi_counter_command_t', 'c__EA_amdsmi_dev_perf_level_t',
    'c__EA_amdsmi_event_group_t', 'c__EA_amdsmi_event_type_t',
    'c__EA_amdsmi_evt_notification_type_t', 'c__EA_amdsmi_freq_ind_t',
    'c__EA_amdsmi_gpu_block_t', 'c__EA_amdsmi_memory_page_status_t',
    'c__EA_amdsmi_memory_type_t',
    'c__EA_amdsmi_power_profile_preset_masks_t',
    'c__EA_amdsmi_ras_err_state_t', 'c__EA_amdsmi_sw_component_t',
    'c__EA_amdsmi_temperature_metric_t',
    'c__EA_amdsmi_voltage_metric_t', 'c__EA_amdsmi_voltage_type_t',
    'c__EA_amdsmi_xgmi_status_t', 'device_type', 'device_type_t',
    'device_type_t__enumvalues', 'size_t',
    'struct_amd_metrics_table_header_t', 'struct_amdsmi_asic_info',
    'struct_amdsmi_bdf_0', 'struct_amdsmi_board_info',
    'struct_amdsmi_clk_measure', 'struct_amdsmi_engine_usage',
    'struct_amdsmi_frequency_range',
    'struct_amdsmi_func_id_iter_handle', 'struct_amdsmi_fw_info',
    'struct_amdsmi_fw_info_0', 'struct_amdsmi_gpu_caps',
    'struct_amdsmi_gpu_caps_0', 'struct_amdsmi_gpu_caps_1',
    'struct_amdsmi_pcie_info', 'struct_amdsmi_power_cap_info',
    'struct_amdsmi_power_limit', 'struct_amdsmi_power_measure',
    'struct_amdsmi_process_info', 'struct_amdsmi_process_info_0',
    'struct_amdsmi_process_info_1', 'struct_amdsmi_temperature',
    'struct_amdsmi_temperature_limit', 'struct_amdsmi_vbios_info',
    'struct_amdsmi_vram_info', 'struct_amdsmi_xgmi_info',
    'struct_c__SA_amdsmi_counter_value_t',
    'struct_c__SA_amdsmi_error_count_t',
    'struct_c__SA_amdsmi_evt_notification_data_t',
    'struct_c__SA_amdsmi_freq_volt_region_t',
    'struct_c__SA_amdsmi_frequencies_t',
    'struct_c__SA_amdsmi_gpu_metrics_t',
    'struct_c__SA_amdsmi_od_vddc_point_t',
    'struct_c__SA_amdsmi_od_volt_curve_t',
    'struct_c__SA_amdsmi_od_volt_freq_data_t',
    'struct_c__SA_amdsmi_pcie_bandwidth_t',
    'struct_c__SA_amdsmi_power_profile_status_t',
    'struct_c__SA_amdsmi_process_info_t',
    'struct_c__SA_amdsmi_range_t',
    'struct_c__SA_amdsmi_retired_page_record_t',
    'struct_c__SA_amdsmi_utilization_counter_t',
    'struct_c__SA_amdsmi_version_t', 'uint32_t', 'uint64_t',
    'union_amd_id', 'union_amd_id_0', 'union_amdsmi_bdf']

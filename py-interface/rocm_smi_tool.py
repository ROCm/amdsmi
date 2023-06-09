#!/usr/bin/env python3

#
# Copyright (C) 2020 Advanced Micro Devices. All rights reserved.
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

import sys
import importlib
import re
import ctypes

smi_api = importlib.import_module('amdsmi')

##############################################
# utils
##############################################


class Color:
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    WHITE = '\033[0m'
    END = '\033[0m'


class Style:
    def __init__(self, background=Color.YELLOW, text=Color.WHITE, header=Color.BOLD):
        self.background_style = background
        self.text_style = text
        self.header_style = header

    def background(self, text):
        return Color.END + self.background_style + text + Color.END

    def text(self, text):
        return Color.END + self.text_style + text + Color.END + self.background_style

    def header(self, text):
        return self.text_style + self.header_style + text + Color.END + self.background_style


class CmdLineParser:
    def __init__(self, cmd_args, formatter):
        self.formatter = formatter
        if len(cmd_args) == 1 or (len(cmd_args) == 2 and (cmd_args[1] == "-h" or cmd_args[1] == "--help")):
            self.formatter.print_usage()
            sys.exit()
        elif len(cmd_args) == 2 and (cmd_args[1] == "-i" or cmd_args[1] == "--info"):
            self.formatter.print_info()
            sys.exit()
        else:
            self.cmd_args = cmd_args
            self.command_entry = None
            self.extra_args = 0

    def _check_bdf(self, bdf):
        if bdf is None:
            raise smi_api.AmdSmiBdfFormatException(bdf)
        extended_regex = re.compile(r'^([0-9a-fA-F]{4}):([0-9a-fA-F]{2}):([0-1][0-9a-fA-F])\.([0-7])$')
        if extended_regex.match(bdf) is None:
            simple_regex = re.compile(r'^([0-9a-fA-F]{2}):([0-1][0-9a-fA-F])\.([0-7])$')
            if simple_regex.match(bdf) is None:
                raise smi_api.AmdSmiBdfFormatException(bdf)

    def _check_type(self, arg_name, arg_type, arg_value):
        if not ((arg_type == int and arg_value.isdigit()) or (arg_type == str and not arg_value.isdigit())):
            raise smi_api.AmdSmiParameterException(arg_value, arg_type, self.formatter.style.background("Invalid value for {}:\n\nExpected {} got {} of type {}.".format(arg_name, arg_type, arg_value, type(arg_value))))

    def _check_range(self, arg_name, arg_value, min_val, max_val):
        if arg_value < min_val or arg_value > max_val:
            raise smi_api.AmdSmiParameterException(arg_value, int, self.formatter.style.background("Invalid value for {}:\n\nExpected integer in range [{}, {}] got {}.".format(arg_name, min, max, arg_value)))

    def _check_if_arg_exists(self, arg_name, arg_type, arg_position):
        if len(self.cmd_args) <= arg_position:
            raise smi_api.AmdSmiParameterException(None, arg_type, self.formatter.style.background("{} is missing at position {}:\n\nExpected {} got nothing.".format(arg_name, arg_position, arg_type)))

    def _should_skip_arg(self, arg_name, arg_type, arg_value, is_arg_obligatory):
        # If 'S' is passed instead of a value, argument should have default value
        if arg_value == 'S':
            if is_arg_obligatory:
                raise smi_api.AmdSmiParameterException(arg_value, arg_type, self.formatter.style.background("Invalid value for {}:\n\n'S' can be used only for args that are optional.".format(arg_name)))
            return True
        return False

    def _get_processor_handle_from_id(self, gpu_id, vf_id=None):
        devices = smi_api.amdsmi_get_processor_handles()
        self._check_range("gpu id", gpu_id, 0, len(devices) - 1)
        processor_handle = devices[gpu_id]

        if vf_id is not None:
            partitions = smi_api.amdsmi_get_vf_partition_info(processor_handle)
            self._check_range("vf id", vf_id, 0, len(partitions) - 1)
            processor_handle = smi_api.amdsmi_get_vf_handle_from_vf_index(processor_handle, vf_id)
        return processor_handle

    def _parse_vf_id_if_exists(self):
        gpu_id = None
        vf_id = None
        # parse gpu_id,vf_id and gpu_id, vf_id
        if ',' in self.cmd_args[2]:
            ids = self.cmd_args[2].split(',')
            gpu_id = ids[0]
            if ids[1]:
                vf_id = ids[1]
            else:
                self._check_if_arg_exists("vf_id", int, 3)
                vf_id = self.cmd_args[3]
                self.extra_args += 1
        # parse gpu_id , vf_id
        elif len(self.cmd_args) > 3 and self.cmd_args[3] == ',':
            gpu_id = self.cmd_args[2]
            self._check_if_arg_exists("vf_id", int, 4)
            vf_id = self.cmd_args[4]
            self.extra_args += 2
        # parse gpu_id ,vf_id
        elif len(self.cmd_args) > 3 and ',' in self.cmd_args[3]:
            gpu_id = self.cmd_args[2]
            ids = self.cmd_args[3].split(',')
            vf_id = ids[1]
            self.extra_args += 1
        if gpu_id and vf_id:
            self._check_type("gpu id", int, gpu_id)
            self._check_type("vf id", int, vf_id)

            gpu_id = int(gpu_id)
            vf_id = int(vf_id)

        return dict(gpu_id=gpu_id, vf_id=vf_id)

    def get_command_handle(self):
        command_id = self.cmd_args[1]
        self._check_type("command id", int, command_id)

        command_id = int(command_id)
        self._check_range("command id", command_id, list(commands)[0], list(commands)[-1])

        self.command_entry = commands[command_id]

        return self.command_entry[0]

    def get_processor_handle(self):
        processor_handles = []

        def parse_processor_handle(possition):
            self._check_if_arg_exists("Device identifier", "device bdf or device id", possition)

            ids = self._parse_vf_id_if_exists()
            if ids["gpu_id"] is not None and ids["vf_id"] is not None:
                processor_handle = self._get_processor_handle_from_id(ids["gpu_id"], ids["vf_id"])
            else:
                gpu_arg = self.cmd_args[position]
                if gpu_arg.isdigit():
                    processor_handle = self._get_processor_handle_from_id(int(gpu_arg))
                else:
                    self._check_bdf(gpu_arg)
                    processor_handle = smi_api.amdsmi_get_processor_handle_from_bdf(gpu_arg)
            processor_handles.append(processor_handle)

        for i in range(len(self.command_entry)):
            if f"device_identifier{i + 1}" in self.command_entry[1]:
                parse_processor_handle(i + 2)

        if len(processor_handles) == 0:
            return None

        return processor_handles

    def get_command_args(self):
        offset = 2 + self.extra_args
        arg_copy = self.command_entry[1]
        if "device_identifier1" in arg_copy:
            offset += 1
            del arg_copy["device_identifier1"]

        if "device_identifier2" in arg_copy:
            offset += 1
            del arg_copy["device_identifier2"]

        arg_names = list(arg_copy.keys())
        if len(arg_copy) > 0:
            command_args = {}
            for i in range(0, len(arg_copy)):
                arg_name = arg_names[i]
                arg_type = arg_copy.get(arg_name)[0]
                is_arg_obligatory = arg_copy.get(arg_name)[1]

                self._check_if_arg_exists(arg_name, arg_type, i + offset)
                arg_value = self.cmd_args[i + offset]
                if self._should_skip_arg(arg_name, arg_type, arg_value, is_arg_obligatory):
                    continue
                self._check_type(arg_name, arg_type, arg_value)
                dictionary = command_args
                keys = arg_name.split(".")
                for j in range(len(keys) - 1):
                    nested_dict = {}
                    if keys[j] not in dictionary:
                        dictionary.update({keys[j]: nested_dict})
                        dictionary = nested_dict
                    else:
                        dictionary = dictionary[keys[j]]

                dictionary.update({keys[-1]: arg_type(arg_value)})
            return command_args

        return None


class Formatter:
    def __init__(self, style):
        self.style = style

    def print_output(self, result):
        print()
        if result or result == 0:
            if isinstance(result, dict):
                self.print_dict(result)
            elif isinstance(result, list):
                self.print_list(result)
            elif isinstance(result, smi_api.amdsmi_wrapper.amdsmi_processor_handle):
                self.print_handle("\n" + result)
            else:
                print(result)
        print()
    def print_list(self, lst, indent=0):
        space = " " * (indent * 4)
        for item in lst:
            if isinstance(item, dict):
                self.print_dict(item, indent=indent)
                print('\n')
            elif isinstance(item, list):
                self.print_list(item, indent=indent + 1)
            else:
                print("{}{}:".format(space, self.style.background(str(item))))

    def print_dict(self, dictionary, indent=0):
        space = " " * (indent * 4)
        for key, value in dictionary.items():
            if isinstance(value, dict):
                print("{}{}:".format(space, self.style.background(key)))
                self.print_dict(value, indent=indent + 1)
            elif isinstance(value, list):
                print("{}{}:".format(space, self.style.background(key)))
                self.print_list(value, indent=indent + 1)
            else:
                print("{}{:25} :{}".format(space, self.style.background(key), str(value)))

    def print_handle(self, handle):
        bdf = smi_api.amdsmi_get_gpu_device_bdf(handle)
        print("{:25} :{}".format(self.style.background("BDF"), str(bdf)))

    def print_usage(self):
        text_usage = """
    +=========================================================================================================================+
    |                                         """ + self.style.header("ROCM SMI TOOL") + """                                                                   |
    +=========================================================================================================================+
    |                                                                                                                         |
    |  """ + self.style.header("DESCRIPTION:") + """                                                                                                           |
    |    """ + self.style.text("This command line tool provides quick access to querying") + """                                                             |
    |    """ + self.style.text("and modifying information in libgv through smi-lib") + """                                                                   |
    |                                                                                                                         |
    |  """ + self.style.header("OPTIONS:") + """                                                                                                               |
    |    -h, --help  """ + self.style.text("Show this help information") + """                                                                               |
    |                                                                                                                         |
    |  """ + self.style.header("USAGE:") + """                                                                                                                 |
    |    """ + self.style.text("$ sudo python3 rocm_smi_tool.py [command_id] [command_args ...]") + """                                                      |
    |                                                                                                                         |
    |  """ + self.style.header("EXAMPLE:") + """                                                                                                               |
    |    """ + self.style.text("$ sudo python3 rocm_smi_tool.py 62") + """                                                                                   |
    |                                                                                                                         |
    |  """ + self.style.header("COMMANDS:") + """                                                                                                              |
    |                                                                                                                         |
    |     """ + self.style.text(" 1   Get device vendor name.               Api: amdsmi_get_gpu_vendor_name             <bdf>") + """                        |
    |     """ + self.style.text(" 2   Get device id.                        Api: amdsmi_get_gpu_id                      <bdf>") + """                        |
    |     """ + self.style.text(" 3   Get device vram vendor.               Api: amdsmi_get_gpu_vram_vendor             <bdf>") + """                        |
    |     """ + self.style.text(" 4   Get device drm render minor.          Api: amdsmi_get_gpu_drm_render_minor        <bdf>") + """                        |
    |     """ + self.style.text(" 5   Get device subsystem id.              Api: amdsmi_get_gpu_subsystem_id            <bdf>") + """                        |
    |     """ + self.style.text(" 6   Get device subsystem name.            Api: amdsmi_get_gpu_subsystem_name          <bdf>") + """                        |
    |     """ + self.style.text(" 7   Get device pci id.                    Api: amdsmi_get_gpu_pci_id                  <bdf>") + """                        |
    |     """ + self.style.text(" 8   Get device pci bandwidth.             Api: amdsmi_get_gpu_pci_bandwidth           <bdf>") + """                        |
    |     """ + self.style.text(" 9   Get device pci throughput.            Api: amdsmi_get_gpu_pci_throughput          <bdf>") + """                        |
    |     """ + self.style.text("10   Get device pci replay counter.        Api:  amdsmi_get_gpu_pci_replay_counter      <bdf>") + """                        |
    |     """ + self.style.text("11   Get topo numa affinity.               Api: amdsmi_get_gpu_topo_numa_affinity          <bdf>") + """                        |
    |     """ + self.style.text("13   Get device energy count.              Api: amdsmi_get_energy_count            <bdf>") + """                        |
    |     """ + self.style.text("14   Get device memory total.              Api: amdsmi_get_gpu_memory_total            <bdf>") + """                        |
    |     """ + self.style.text("15   Get device memory usage.              Api: amdsmi_get_gpu_memory_usage            <bdf>") + """                        |
    |     """ + self.style.text("16   Get device memory busy percent.       Api: amdsmi_get_gpu_memory_busy_percent     <bdf>") + """                        |
    |     """ + self.style.text("17   Get device memory reserved pages.     Api: amdsmi_get_gpu_memory_reserved_pages   <bdf>") + """                        |
    |     """ + self.style.text("18   Get device fan rpms.                  Api: amdsmi_get_gpu_fan_rpms                <bdf><sensor_idx>") + """            |
    |     """ + self.style.text("19   Get device fan speed.                 Api: amdsmi_get_gpu_fan_speed               <bdf><sensor_idx>") + """            |
    |     """ + self.style.text("20   Get device fan speed max.             Api: amdsmi_get_gpu_fan_speed_max           <bdf><sensor_idx>") + """            |
    |     """ + self.style.text("21   Get device temp metric.               Api:  amdsmi_get_temp_metric             <bdf>") + """                        |
    |     """ + self.style.text("22   Get device volt metric.               Api:  amdsmi_get_gpu_volt_metric             <bdf>") + """                        |
    |     """ + self.style.text("23   Get device busy percent.              Api: amdsmi_get_busy_percent            <bdf>") + """                        |
    |     """ + self.style.text("24   Get utilization count.                Api: amdsmi_get_utilization_count           <bdf>") + """                        |
    |     """ + self.style.text("25   Get device perf level.                Api: amdsmi_get_gpu_perf_level              <bdf>") + """                        |
    |     """ + self.style.text("26   Set perf determinism mode.            Api: amdsmi_set_gpu_perf_determinism_mode       <bdf><clock_value>") + """           |
    |     """ + self.style.text("27   Get device overdrive level.           Api: amdsmi_get_gpu_overdrive_level         <bdf>") + """                        |
    |     """ + self.style.text("28   Get device gpu clk freq.              Api:  amdsmi_get_clk_freq            <bdf>") + """                        |
    |     """ + self.style.text("29   Get device od volt.                   Api:  amdsmi_get_gpu_od_volt_info            <bdf>") + """                        |
    |     """ + self.style.text("30   Get device gpu metrics.               Api:  amdsmi_get_gpu_metrics_info        <bdf>") + """                        |
    |     """ + self.style.text("31   Get device od volt curve regions.     Api:  amdsmi_get_gpu_od_volt_curve_regions   <bdf><num_regions>") + """           |
    |     """ + self.style.text("32   Get device power profile presets.     Api:  amdsmi_get_gpu_power_profile_presets   <bdf><sensor_idx>") + """            |
    |     """ + self.style.text("33   Get the build version.                Api: amdsmi_get_version                     <None>") + """                       |
    |     """ + self.style.text("34   Get version string.                   Api: amdsmi_get_version_str                 <None>") + """                       |
    |     """ + self.style.text("35   Get device ecc counter.               Api:  amdsmi_get_gpu_ecc_count               <bdf>") + """                        |
    |     """ + self.style.text("36   Get device ecc enable.                Api:  amdsmi_get_gpu_ecc_enabled             <bdf>") + """                        |
    |     """ + self.style.text("37   Get device ecc status.                Api:  amdsmi_get_gpu_ecc_status              <bdf>") + """                        |
    |     """ + self.style.text("38   Get status string.                    Api: amdsmi_status_string                   <status>") + """                     |
    |     """ + self.style.text("39   Get compute process info.             Api: amdsmi_get_gpu_compute_process_info        <None>") + """                       |
    |     """ + self.style.text("40   Get compute process info by pid.      Api: amdsmi_get_gpu_compute_process_info_by_pid <pid>") + """                        |
    |     """ + self.style.text("41   Get compute process gpus.             Api: amdsmi_get_gpu_compute_process_gpus        <pid>") + """                        |
    |     """ + self.style.text("42   Get device xgmi_error_status.         Api: amdsmi_gpu_xgmi_error_status           <bdf>") + """                        |
    |     """ + self.style.text("43   Get device xgmi error reset.          Api: amdsmi_reset_gpu_xgmi_error            <bdf>") + """                        |
    |     """ + self.style.text("44   Get topo get numa node number.        Api: amdsmi_topo_get_numa_node_number       <bdf>") + """                        |
    |     """ + self.style.text("45   Get topo get link weight.             Api: amdsmi_topo_get_link_weight            <bdf><bdf>") + """                   |
    |     """ + self.style.text("46   Get minmax_bandwidth_get.             Api:  amdsmi_get_minmax_bandwidth            <bdf><bdf>") + """                   |
    |     """ + self.style.text("47   Get topo get link type.               Api: amdsmi_topo_get_link_type              <bdf><bdf>") + """                   |
    |     """ + self.style.text("48   Get is P2P accessible.                Api: amdsmi_is_P2P_accessible               <bdf><bdf>") + """                   |
    |     """ + self.style.text("49   Get asic info.                        Api: amdsmi_get_gpu_asic_info                   <bdf>") + """                        |
    |     """ + self.style.text("50   Get processor_handles.                   Api: amdsmi_get_processor_handles              <None>") + """                       |
    |     """ + self.style.text("51   Get event notification.               Api:  amdsmi_get_gpu_event_notification          <bdf>") + """                        |
    |     """ + self.style.text("52   Init event notification.              Api: amdsmi_init_gpu_event_notification         <bdf>") + """                        |
    |     """ + self.style.text("53   Set event notification mask.          Api:  amdsmi_set_gpu_event_notification_mask     <bdf><mask>") + """                  |
    |     """ + self.style.text("54   Get event notification.               Api: amdsmi_stop_gpu_event_notification         <bdf>") + """                        |
    |     """ + self.style.text("55   Init.                                 Api: amdsmi_init                            <None>") + """                       |
    |     """ + self.style.text("56   Shut down.                            Api: amdsmi_shut_down                       <None>") + """                       |
    |     """ + self.style.text("57   Get fw info.                          Api: amdsmi_get_fw_info                     <bdf>") + """                        |
    |     """ + self.style.text("58   Get vbios info.                       Api: amdsmi_get_gpu_vbios_info                  <bdf>") + """                        |
    |     """ + self.style.text("59   Get counter available counters.       Api:  amdsmi_get_gpu_available_counters  <bdf>") + """                        |
    |     """ + self.style.text("60   Get counter control.                  Api: amdsmi_gpu_control_counter                 <bdf>") + """                        |
    |     """ + self.style.text("61   Get counter read.                     Api: amdsmi_gpu_read_counter                    <bdf>") + """                        |
    |     """ + self.style.text("62   Set dev clk range.                    Api: amdsmi_set_gpu_clk_range               <bdf><min_clk><max_clk>") + """      |
    |     """ + self.style.text("63   Get dev counter group supported.      Api: amdsmi_gpu_counter_group_supported     <bdf>") + """                        |
    |     """ + self.style.text("64   Reset dev fan.                        Api: amdsmi_reset_gpu_fan                   <bdf><sensor_idx>") + """            |
    |     """ + self.style.text("65   Set dev fan speed.                    Api: amdsmi_set_gpu_fan_speed               <bdf><sensor_idx><fan_speed>") + """ |
    |     """ + self.style.text("66   Set dev gpu clk freq.                 Api:  amdsmi_set_clk_freq            <bdf><freq_bitmask>") + """          |
    |     """ + self.style.text("67   Reset dev gpu.                        Api: amdsmi_reset_gpu                   <bdf>") + """                        |
    |     """ + self.style.text("68   Set dev od clk info.                  Api:  amdsmi_set_gpu_od_clk_info             <bdf><value>") + """                 |
    |     """ + self.style.text("69   Set dev od volt info.                 Api:  amdsmi_set_gpu_od_volt_info     <bdf><vpoint><clk_value><volt_value>") + """|
    |     """ + self.style.text("70   Set dev overdrive level.              Api:  amdsmi_set_gpu_overdrive_level         <bdf><overdrive_value>") + """       |
    |     """ + self.style.text("71   Set v1 dev overdrive level.           Api:  amdsmi_set_gpu_overdrive_level_v1      <bdf><overdrive_value>") + """       |
    |     """ + self.style.text("72   Set dev pci bandwidth.                Api:  amdsmi_set_gpu_pci_bandwidth           <bdf><bitmask>") + """               |
    |     """ + self.style.text("73   Set dev perf level.                   Api:  amdsmi_set_gpu_perf_level              <bdf>") + """                        |
    |     """ + self.style.text("74   Set dev perf level v1.                Api:  amdsmi_set_gpu_perf_level_v1           <bdf>") + """                        |
    |     """ + self.style.text("75   Set dev power cap.                    Api:  amdsmi_set_power_cap               <bdf><sensor_ind><cap>") + """       |
    |     """ + self.style.text("76   Set dev power profile.                Api:  amdsmi_set_gpu_power_profile           <bdf><reserved>") + """              |
    |     """ + self.style.text("77   Close dev supported func iterator.    Api: amdsmi_close_supported_func_iterator    <bdf>") + """                   |
    |     """ + self.style.text("78   Pen dev supported func iterator.      Api: amdsmi_open_supported_func_iterator     <bdf>") + """                   |
    |     """ + self.style.text("79   Get func iter next.                   Api: amdsmi_next_func_iter                  <bdf>") + """                        |
    |     """ + self.style.text("80   Get power cap info.                   Api: amdsmi_get_power_cap_info              <bdf>") + """                        |
    |     """ + self.style.text("81   Get xgmi info.                        Api: amdsmi_get_xgmi_info                   <bdf>") + """                        |
    +=========================================================================================================================+"""
        print(self.style.background(text_usage))


##############################################
# SMI tool wrapper
##############################################
def amdsmi_tool_dev_memory_total_get(dev):
    result = {}
    for memory_type in smi_api.AmdSmiMemoryType:
        try:
            value = smi_api.amdsmi_get_gpu_memory_total(dev, memory_type)
            result.update({memory_type.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(memory_type.name, e))

    return result

def amdsmi_tool_dev_memory_usage_get(dev):
    result = {}
    for memory_type in smi_api.AmdSmiMemoryType:
        try:
            value = smi_api.amdsmi_get_gpu_memory_usage(dev, memory_type)
            result.update({memory_type.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(memory_type.name, e))

    return result

def amdsmi_tool_dev_fan_rpms_get(dev, dic):
    sensor_idx = dic["sensor_idx"]
    return smi_api.amdsmi_get_gpu_fan_rpms(dev, sensor_idx)

def amdsmi_tool_dev_fan_speed_get(dev, dic):
    sensor_idx = dic["sensor_idx"]
    return smi_api.amdsmi_get_gpu_fan_speed(dev, sensor_idx)

def amdsmi_tool_dev_fan_speed_max_get(dev, dic):
    sensor_idx = dic["sensor_idx"]
    return smi_api.amdsmi_get_gpu_fan_speed_max(dev, sensor_idx)

def amdsmi_tool_dev_temp_metric_get(dev):
    result = {}
    for temperature_type in smi_api.AmdSmiTemperatureType:
        for temperature_metric in smi_api.AmdSmiTemperatureMetric:
            try:
                value = smi_api. amdsmi_get_temp_metric(dev, temperature_type, temperature_metric)
                result.update({"AmdSmiTemperatureType: " + temperature_type.name + ", AmdSmiTemperatureMetric: " + temperature_metric.name: value})
            except smi_api.AmdSmiException as e:
                print("{},{}:\t{}".format(temperature_type.name,  temperature_metric.name, e))

    return result

def amdsmi_tool_dev_volt_metric_get(dev):
    result = {}
    for voltage_type in smi_api.AmdSmiVoltageType:
        for voltage_metric in smi_api.AmdSmiVoltageMetric:
            try:
                value = smi_api. amdsmi_get_gpu_volt_metric(dev, voltage_type, voltage_metric)
                result.update({"AmdSmiVoltageType: " + voltage_type.name + ", AmdSmiVoltageMetric: " + voltage_metric.name: value})
            except smi_api.AmdSmiException as e:
                print("{},{}:\t{}".format(voltage_type.name,  voltage_metric.name, e))

    return result

def amdsmi_tool_utilization_count_get(dev):
    result = {}
    for counter_type in smi_api.AmdSmiUtilizationCounterType:
        try:
            value = smi_api.amdsmi_get_utilization_count(dev, counter_type)
            result.update({counter_type.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(counter_type.name, e))

    return result

def amdsmi_tool_perf_determinism_mode_set(dev, dic):
    clock_value = dic["clock_value"]
    return smi_api.amdsmi_set_gpu_perf_determinism_mode(dev, clock_value)

def amdsmi_tool_dev_power_profile_presets_get(dev, dic):
    sensor_idx = dic["sensor_idx"]
    return smi_api. amdsmi_get_gpu_power_profile_presets(dev, sensor_idx)

def amdsmi_tool_version_str_get():
    result = {}
    for sw_component in smi_api.AmdSmiSwComponent:
        try:
            value = smi_api.amdsmi_get_version_str(sw_component)
            result.update({sw_component.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(sw_component.name, e))

    return result

def amdsmi_tool_dev_fan_reset(dev, dic):
    sensor_idx = dic["sensor_idx"]
    return smi_api.amdsmi_reset_gpu_fan(dev, sensor_idx)

def amdsmi_tool_dev_fan_speed_set(dev, dic):
    sensor_idx = dic["sensor_idx"]
    fan_speed = dic["fan_speed"]
    return smi_api.amdsmi_set_gpu_fan_speed(dev, sensor_idx, fan_speed)

def amdsmi_tool_dev_overdrive_level_set(dev, dic):
    overdrive_value = dic["overdrive_value"]
    return smi_api. amdsmi_set_gpu_overdrive_level(dev, overdrive_value)

def amdsmi_tool_dev_overdrive_level_set_v1(dev, dic):
    overdrive_value = dic["overdrive_value"]
    return smi_api. amdsmi_set_gpu_overdrive_level(dev, overdrive_value)

def amdsmi_tool_dev_pci_bandwidth_set(dev, dic):
    bitmask = dic["bitmask"]
    return smi_api. amdsmi_set_gpu_pci_bandwidth(dev, bitmask)


def amdsmi_tool_dev_gpu_clk_freq_get(dev):
    result = {}
    for clock_type in smi_api.AmdSmiClkType:
        try:
            value = smi_api. amdsmi_get_clk_freq(dev, clock_type)
            result.update({clock_type.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(clock_type.name, e))

    return result

def amdsmi_tool_dev_od_volt_curve_regions_get(dev, dic):
    num_regions = dic["num_regions"]
    return smi_api. amdsmi_get_gpu_od_volt_curve_regions(dev, num_regions)


def amdsmi_tool_dev_ecc_count_get(dev):
    result = {}
    for gpu_block in smi_api.AmdSmiGpuBlock:
        try:
            value = smi_api. amdsmi_get_gpu_ecc_count(dev, gpu_block)
            result.update({gpu_block.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(gpu_block.name, e))

    return result

def amdsmi_tool_dev_ecc_status_get(dev):
    result = {}
    for gpu_block in smi_api.AmdSmiGpuBlock:
        try:
            value = smi_api. amdsmi_get_gpu_ecc_status(dev, gpu_block)
            result.update({gpu_block.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(gpu_block.name, e))

    return result

def amdsmi_tool_status_string(dic):
    status = dic["status"]
    return smi_api.amdsmi_status_string(ctypes.c_uint32(status))

def amdsmi_tool_compute_process_gpus_get(dic):
    pid = dic["pid"]
    return smi_api.amdsmi_get_gpu_compute_process_gpus(pid)

def amdsmi_tool_compute_process_info_by_pid_get(dic):
    pid = dic["pid"]
    return smi_api.amdsmi_get_gpu_compute_process_info_by_pid(pid)

def amdsmi_tool_topo_get_link_weight(dev):
    return smi_api.amdsmi_topo_get_link_weight(dev[0], dev[1])

def amdsmi_tool_minmax_bandwidth_get(dev):
    return smi_api. amdsmi_get_minmax_bandwidth(dev[0], dev[1])

def amdsmi_tool_topo_get_link_type(dev):
    return smi_api.amdsmi_topo_get_link_type(dev[0], dev[1])

def amdsmi_tool_is_P2P_accessible(dev):
    return smi_api.amdsmi_is_P2P_accessible(dev[0], dev[1])

def amdsmi_tool_event_notification_get(dev):
    result = {}
    for evt_notification_type in smi_api.AmdSmiEvtNotificationType:
        try:
            event = smi_api.AmdSmiEventReader(dev, evt_notification_type)
            value = event.read(500)
            result.update({evt_notification_type.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(evt_notification_type.name, e))

    return result

def amdsmi_tool_event_notification_init(dev):
    return smi_api.amdsmi_wrapper.amdsmi_init_gpu_event_notification(dev)

def amdsmi_tool_event_notification_mask_set(dev, dic):
    mask = dic["mask"]
    return smi_api.amdsmi_wrapper.amdsmi_set_gpu_event_notification_mask(dev, ctypes.c_uint64(mask))

def amdsmi_tool_event_notification_stop(dev):
    return smi_api.amdsmi_wrapper.amdsmi_stop_gpu_event_notification(dev)

def amdsmi_tool_shut_down():
    smi_api.amdsmi_init()
    smi_api.amdsmi_shut_down()
    smi_api.amdsmi_init()

def amdsmi_tool_counter_available_counters_get(dev):
    result = {}
    for event_group in smi_api.AmdSmiEventGroup:
        try:
            value = smi_api. amdsmi_get_gpu_available_counters(dev, event_group)
            result.update({event_group.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(event_group.name, e))

    return result

def amdsmi_tool_counter_control(dev):
    result = {}
    for event_type in smi_api.AmdSmiEventType:
        for counter_command in smi_api.AmdSmiCounterCommand:
            try:
                event_handle = smi_api.amdsmi_gpu_create_counter(dev, event_type)
                value = smi_api.amdsmi_gpu_control_counter(event_handle, counter_command)
                result.update({event_type.name: value})
            except smi_api.AmdSmiException as e:
                print("{}:\t{}".format(event_type.name, e))

    return result

def amdsmi_tool_counter_read(dev):
    result = {}
    for event_type in smi_api.AmdSmiEventType:
        try:
            event_handle = smi_api.amdsmi_gpu_create_counter(dev, event_type)
            value = smi_api.amdsmi_gpu_read_counter(event_handle)
            result.update({event_type.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(event_type.name, e))

    return result

def amdsmi_tool_dev_clk_range_set(dev, dic):
    result = {}
    min_clk = dic["min_clk"]
    max_clk = dic["max_clk"]
    for clock_type in smi_api.AmdSmiClkType:
        try:
            value = smi_api.amdsmi_set_gpu_clk_range(dev, min_clk, max_clk, clock_type)
            result.update({clock_type.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(clock_type.name, e))

    return result

def amdsmi_tool_dev_counter_group_supported(dev):
    result = {}
    for event_group in smi_api.AmdSmiEventGroup:
        try:
            value = smi_api.amdsmi_gpu_counter_group_supported(dev, event_group)
            result.update({event_group.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(event_group.name, e))

    return result

def amdsmi_tool_dev_gpu_clk_freq_set(dev, dic):
    result = {}
    freq_bitmask = dic["freq_bitmask"]
    for clock_type in smi_api.AmdSmiClkType:
        try:
            value = smi_api. amdsmi_set_clk_freq(dev, clock_type, freq_bitmask)
            result.update({clock_type.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(clock_type.name, e))

    return result

def amdsmi_tool_dev_od_clk_info_set(dev, dic):
    result = {}
    value = dic["value"]
    for freq_ind in smi_api.AmdSmiFreqInd:
        for clock_type in smi_api.AmdSmiClkType:
            try:
                value = smi_api. amdsmi_set_gpu_od_clk_info(dev, freq_ind, value, clock_type)
                result.update({"AmdSmiFreqInd: " + freq_ind.name + ", AmdSmiClkType: " + clock_type.name: value})
            except smi_api.AmdSmiException as e:
                print("{},{}:\t{}".format(freq_ind.name,  clock_type.name, e))

    return result

def amdsmi_tool_dev_od_volt_info_set(dev, dic):
    vpoint = dic["vpoint"]
    clk_value = dic["clk_value"]
    volt_value = dic["volt_value"]
    return smi_api. amdsmi_set_gpu_od_volt_info(dev, vpoint, clk_value, volt_value)

def amdsmi_tool_dev_perf_level_set(dev):
    result = {}
    for dev_perf_level in smi_api.AmdSmiDevPerfLevel:
        try:
            value = smi_api. amdsmi_set_gpu_perf_level(dev, dev_perf_level)
            result.update({dev_perf_level.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(dev_perf_level.name, e))

    return result

def amdsmi_tool_dev_perf_level_set_v1(dev):
    result = {}
    for dev_perf_level in smi_api.AmdSmiDevPerfLevel:
        try:
            value = smi_api. amdsmi_set_gpu_perf_level_v1(dev, dev_perf_level)
            result.update({dev_perf_level.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(dev_perf_level.name, e))

    return result

def amdsmi_tool_dev_power_cap_set(dev, dic):
    sensor_ind = dic["sensor_ind"]
    cap = dic["cap"]
    return smi_api. amdsmi_set_power_cap(dev, sensor_ind, cap)

def amdsmi_tool_dev_power_profile_set(dev, dic):
    result = {}
    reserved = dic["reserved"]
    for power_profile_preset_maks in smi_api.AmdSmiPowerProfilePresetMasks:
        try:
            value = smi_api. amdsmi_set_gpu_power_profile(dev, reserved, power_profile_preset_maks)
            result.update({power_profile_preset_maks.name: value})
        except smi_api.AmdSmiException as e:
            print("{}:\t{}".format(power_profile_preset_maks.name, e))

    return result

def amdsmi_tool_dev_supported_func_iterator_close(dev):
    obj_handle = smi_api.amdsmi_open_supported_func_iterator(dev)
    return smi_api.amdsmi_close_supported_func_iterator(obj_handle)

def amdsmi_tool_func_iter_next(dev):
    obj_handle = smi_api.amdsmi_open_supported_func_iterator(dev)
    return smi_api.amdsmi_next_func_iter(obj_handle)

##############################################
# command table
##############################################

commands = {
    # idx: [func, {arg_name : [arg_type, is_arg_obligatory]}]
    1: [smi_api.amdsmi_get_gpu_vendor_name, {
        "device_identifier1": [None, True]
    }],
    2: [smi_api.amdsmi_get_gpu_id, {
        "device_identifier1": [None, True]
    }],
    3: [smi_api.amdsmi_get_gpu_vram_vendor, {
        "device_identifier1": [None, True]
    }],
    4: [smi_api.amdsmi_get_gpu_drm_render_minor, {
        "device_identifier1": [None, True]
    }],
    5: [smi_api.amdsmi_get_gpu_subsystem_id, {
        "device_identifier1": [None, True]
    }],
    6: [smi_api.amdsmi_get_gpu_subsystem_name, {
        "device_identifier1": [None, True]
    }],
    7: [smi_api.amdsmi_get_gpu_pci_id, {
        "device_identifier1": [None, True]
    }],
    8: [smi_api.amdsmi_get_gpu_pci_bandwidth, {
        "device_identifier1": [None, True]
    }],
    9: [smi_api.amdsmi_get_gpu_pci_throughput, {
        "device_identifier1": [None, True]
    }],
    10: [smi_api. amdsmi_get_gpu_pci_replay_counter, {
        "device_identifier1": [None, True]
    }],
    11: [smi_api.amdsmi_get_gpu_topo_numa_affinity, {
        "device_identifier1": [None, True]
    }],
    12: [amdsmi_tool_dev_power_ave_get, {
        "device_identifier1": [None, True],
        "sensor_id": [int, True]
    }],
    13: [smi_api.amdsmi_get_energy_count, {
        "device_identifier1": [None, True]
    }],
    14: [amdsmi_tool_dev_memory_total_get, {
        "device_identifier1": [None, True],
    }],
    15: [amdsmi_tool_dev_memory_usage_get, {
        "device_identifier1": [None, True]
    }],
    16: [smi_api.amdsmi_get_gpu_memory_busy_percent, {
        "device_identifier1": [None, True]
    }],
    17: [smi_api.amdsmi_get_gpu_memory_reserved_pages, {
        "device_identifier1": [None, True]
    }],
    18: [amdsmi_tool_dev_fan_rpms_get, {
        "device_identifier1": [None, True],
        "sensor_idx": [int, True]
    }],
    19: [amdsmi_tool_dev_fan_speed_get, {
        "device_identifier1": [None, True],
        "sensor_idx": [int, True]
    }],
    20: [amdsmi_tool_dev_fan_speed_max_get, {
        "device_identifier1": [None, True],
        "sensor_idx": [int, True]
    }],
    21: [amdsmi_tool_dev_temp_metric_get, {
        "device_identifier1": [None, True]
    }],
    22: [amdsmi_tool_dev_volt_metric_get, {
        "device_identifier1": [None, True],
    }],
    23: [smi_api.amdsmi_get_busy_percent, {
        "device_identifier1": [None, True]
    }],
    24: [amdsmi_tool_utilization_count_get, {
        "device_identifier1": [None, True],
    }],
    25: [smi_api.amdsmi_get_gpu_perf_level, {
        "device_identifier1": [None, True]
    }],
    26: [amdsmi_tool_perf_determinism_mode_set, {
        "device_identifier1": [None, True],
        "clock_value": [int, True]
    }],
    27: [smi_api.amdsmi_get_gpu_overdrive_level, {
        "device_identifier1": [None, True]
    }],
    28: [amdsmi_tool_dev_gpu_clk_freq_get, {
        "device_identifier1": [None, True]
    }],
    29: [smi_api. amdsmi_get_gpu_od_volt_info, {
        "device_identifier1": [None, True]
    }],
    30: [smi_api. amdsmi_get_gpu_metrics_info, {
        "device_identifier1": [None, True]
    }],
    31: [amdsmi_tool_dev_od_volt_curve_regions_get, {
        "device_identifier1": [None, True],
        "num_regions": [int, True]
    }],
    32: [amdsmi_tool_dev_power_profile_presets_get, {
        "device_identifier1": [None, True],
        "sensor_idx": [int, True]
    }],
    33: [smi_api.amdsmi_get_version, {}],
    34: [amdsmi_tool_version_str_get, {}],
    35: [amdsmi_tool_dev_ecc_count_get, {
        "device_identifier1": [None, True]
    }],
    36: [smi_api. amdsmi_get_gpu_ecc_enabled, {
        "device_identifier1": [None, True]
    }],
    37: [amdsmi_tool_dev_ecc_status_get, {
        "device_identifier1": [None, True]
    }],
    38: [amdsmi_tool_status_string, {
        "status": [int, True]
    }],
    39: [smi_api.amdsmi_get_gpu_compute_process_info, {}],
    40: [amdsmi_tool_compute_process_info_by_pid_get, {
        "pid": [int, True]
    }],
    41: [amdsmi_tool_compute_process_gpus_get, {
        "pid": [int, True]
    }],
    42: [smi_api.amdsmi_gpu_xgmi_error_status, {
        "device_identifier1": [None, True]
    }],
    43: [smi_api.amdsmi_reset_gpu_xgmi_error, {
        "device_identifier1": [None, True]
    }],
    44: [smi_api.amdsmi_topo_get_numa_node_number, {
        "device_identifier1": [None, True]
    }],
    45: [amdsmi_tool_topo_get_link_weight, {
        "device_identifier1": [None, True],
        "device_identifier2": [None, True]
    }],
    46: [amdsmi_tool_minmax_bandwidth_get, {
        "device_identifier1": [None, True],
        "device_identifier2": [None, True]
    }],
    47: [amdsmi_tool_topo_get_link_type, {
        "device_identifier1": [None, True],
        "device_identifier2": [None, True]
    }],
    48: [amdsmi_tool_is_P2P_accessible, {
        "device_identifier1": [None, True],
        "device_identifier2": [None, True]
    }],
    49: [smi_api.amdsmi_get_gpu_asic_info, {
        "device_identifier1": [None, True]
    }],
    50: [smi_api.amdsmi_get_processor_handles, {}],
    51: [amdsmi_tool_event_notification_get, {
        "device_identifier1": [None, True]
    }],
    52: [amdsmi_tool_event_notification_init, {
        "device_identifier1": [None, True]
    }],
    53: [amdsmi_tool_event_notification_mask_set, {
        "device_identifier1": [None, True],
        "mask": [int, True]
    }],
    54: [amdsmi_tool_event_notification_stop, {
        "device_identifier1": [None, True]
    }],
    55: [smi_api.amdsmi_init, {}],
    56: [amdsmi_tool_shut_down, {}],
    57: [smi_api.amdsmi_get_fw_info, {
        "device_identifier1": [None, True]
    }],
    58: [smi_api.amdsmi_get_gpu_vbios_info, {
        "device_identifier1": [None, True]
    }],
    59: [amdsmi_tool_counter_available_counters_get, {
        "device_identifier1": [None, True]
    }],
    60: [amdsmi_tool_counter_control, {
        "device_identifier1": [None, True]
    }],
    61: [amdsmi_tool_counter_read, {
        "device_identifier1": [None, True]
    }],
    62: [amdsmi_tool_dev_clk_range_set, {
        "device_identifier1": [None, True],
        "min_clk": [int, True],
        "max_clk": [int, True]
    }],
    63: [amdsmi_tool_dev_counter_group_supported, {
        "device_identifier1": [None, True]
    }],
    64: [amdsmi_tool_dev_fan_reset, {
        "device_identifier1": [None, True],
        "sensor_idx": [int, True]
    }],
    65: [amdsmi_tool_dev_fan_speed_set, {
        "device_identifier1": [None, True],
        "sensor_idx": [int, True],
        "fan_speed": [int, True]
    }],
    66: [amdsmi_tool_dev_gpu_clk_freq_set, {
        "device_identifier1": [None, True],
        "freq_bitmask": [int, True]
    }],
    67: [smi_api.amdsmi_reset_gpu, {
        "device_identifier1": [None, True]
    }],
    68: [amdsmi_tool_dev_od_clk_info_set, {
        "device_identifier1": [None, True],
        "value": [int, True]
    }],
    69: [amdsmi_tool_dev_od_volt_info_set, {
        "device_identifier1": [None, True],
        "vpoint": [int, True],
        "clk_value": [int, True],
        "volt_value": [int, True]
    }],
    70: [amdsmi_tool_dev_overdrive_level_set, {
        "device_identifier1": [None, True],
        "overdrive_value": [int, True]
    }],
    71: [amdsmi_tool_dev_overdrive_level_set_v1, {
        "device_identifier1": [None, True],
        "overdrive_value": [int, True]
    }],
    72: [amdsmi_tool_dev_pci_bandwidth_set, {
        "device_identifier1": [None, True],
        "bitmask": [int, True]
    }],
    73: [amdsmi_tool_dev_perf_level_set, {
        "device_identifier1": [None, True]
    }],
    74: [amdsmi_tool_dev_perf_level_set_v1, {
        "device_identifier1": [None, True]
    }],
    75: [amdsmi_tool_dev_power_cap_set, {
        "device_identifier1": [None, True],
        "sensor_ind": [int, True],
        "cap": [int, True]
    }],
    76: [amdsmi_tool_dev_power_profile_set, {
        "device_identifier1": [None, True],
        "reserved": [int, True]
    }],
    77: [amdsmi_tool_dev_supported_func_iterator_close, {
        "device_identifier1": [None, True]
    }],
    78: [smi_api.amdsmi_open_supported_func_iterator, {
        "device_identifier1": [None, True]
    }],
    79: [amdsmi_tool_func_iter_next, {
        "device_identifier1": [None, True]
    }],
    80: [smi_api.amdsmi_get_power_cap_info, {
        "device_identifier1": [None, True]
    }],
    81: [smi_api.amdsmi_get_xgmi_info, {
        "device_identifier1": [None, True]
    }]
}

BACKGROUND_COLOR = Color.CYAN

if __name__ == "__main__":

    formatter = Formatter(Style(BACKGROUND_COLOR))
    parser = CmdLineParser(sys.argv, formatter)

    try:
        smi_api.amdsmi_init()

        command = parser.get_command_handle()
        processor_handles = parser.get_processor_handle()
        command_args = parser.get_command_args()
        result = None

        if not processor_handles and not command_args:
            result = command()
        elif not processor_handles and command_args:
            result = command(command_args)
        elif len(processor_handles) == 1 and not command_args:
            result = command(processor_handles[0])
        elif len(processor_handles) > 1 and not command_args:
            result = command(processor_handles)
        elif len(processor_handles) == 1 and command_args:
            result = command(processor_handles[0], command_args)
        else:
            result = command(processor_handles, command_args)

        formatter.print_output(result)

        print("operation successfully completed")

    except smi_api.AmdSmiException as e:
        print(e)

    smi_api.amdsmi_shut_down()

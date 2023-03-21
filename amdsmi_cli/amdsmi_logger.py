#!/usr/bin/env python3
#
# Copyright (C) 2023 Advanced Micro Devices. All rights reserved.
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

import json
import time
import yaml
import re
from enum import Enum

from amdsmi_helpers import AMDSMIHelpers

class AMDSMILogger():
    def __init__(self, compatibility='amdsmi', format='human_readable',
                    destination='stdout') -> None:
        self.output = {}
        self.multiple_device_output = []
        self.watch_output = []
        self.compatibility = compatibility # amd-smi, gpuv-smi, or rocm-smi
        self.format = format # csv, json, or human_readable
        self.destination = destination # stdout, path to a file (append)
        self.amd_smi_helpers = AMDSMIHelpers()


    class LoggerFormat(Enum):
        """Enum for logger formats"""
        json = 'json'
        csv = 'csv'
        human_readable = 'human_readable'

    class LoggerCompatibility(Enum):
        """Enum for logger compatibility"""
        amdsmi = 'amdsmi'
        rocmsmi = 'rocmsmi'
        gpuvsmi = 'gpuvsmi'


    def is_json_format(self):
        return self.format == self.LoggerFormat.json.value


    def is_csv_format(self):
        return self.format == self.LoggerFormat.csv.value


    def is_human_readable_format(self):
        return self.format == self.LoggerFormat.human_readable.value


    def is_amdsmi_compatibility(self):
        return self.compatibility == self.LoggerCompatibility.amdsmi.value


    def is_rocmsmi_compatibility(self):
        return self.compatibility == self.LoggerCompatibility.rocmsmi.value


    def is_gpuvsmi_compatibility(self):
        return self.compatibility == self.LoggerCompatibility.gpuvsmi.value


    def store_output(self, device_handle, argument, data):
        """ Store the argument and device handle according to the compatibility.
                Each compatibility function will handle the output format and
                populate the output
            params:
                device_handle - device handle object to the target device output
                argument (str) - key to store data
                data (dict | list) - Data store against argument
            return:
                Nothing
        """
        gpu_id = self.amd_smi_helpers.get_gpu_id_from_device_handle(device_handle)
        if self.is_amdsmi_compatibility():
            self._store_output_amdsmi(gpu_id=gpu_id, argument=argument, data=data)
        elif self.is_rocmsmi_compatibility():
            self._store_output_rocmsmi(gpu_id=gpu_id, argument=argument, data=data)
        elif self.is_gpuvsmi_compatibility():
            self._store_output_gpuvsmi(gpu_id=gpu_id, argument=argument, data=data)


    def _store_output_amdsmi(self, gpu_id, argument, data):
        if self.is_json_format() or self.is_human_readable_format():
            self.output['gpu'] = int(gpu_id)
            if argument == 'values' and isinstance(data, dict):
                self.output.update(data)
            else:
                self.output[argument] = data

        elif self.is_csv_format():
            # put output into self.csv_output
            pass
        else:
            raise "err"


    def _store_output_rocmsmi(self, gpu_id, argument, data):
        if self.is_json_format():
            # put output into self.json_output
            pass
        elif self.is_csv_format():
            # put output into self.csv_output
            pass
        elif self.is_human_readable_format():
            # put output into self.human_readable_output
            pass
        else:
            raise "err"


    def _store_output_gpuvsmi(self, gpu_id, argument, data):
        if self.is_json_format() or self.is_human_readable_format():
            self.output['gpu'] = int(gpu_id)
            self.output[argument] = data
        elif self.is_csv_format():
            # put output into self.csv_output
            pass
        else:
            raise "err"


    def store_multiple_device_output(self):
        """ Store the current output into the multiple_device_output
                then clear the current output
            params:
                None
            return:
                Nothing
        """
        if self.is_amdsmi_compatibility():
            self._store_multiple_device_output_amdsmi()
        elif self.is_rocmsmi_compatibility():
            self._store_multiple_device_output_rocmsmi()
        elif self.is_gpuvsmi_compatibility():
            self._store_multiple_device_output_gpuvsmi()


    def _store_multiple_device_output_amdsmi(self):
        if self.is_json_format() or self.is_human_readable_format():
            self.multiple_device_output.append(self.output)
            self.output = {}
        elif self.is_csv_format():
            # put output into self.csv_output
            pass
        else:
            raise "err"


    def _store_multiple_device_output_rocmsmi(self):
        if self.is_json_format():
            # put output into self.json_output
            pass
        elif self.is_csv_format():
            # put output into self.csv_output
            pass
        elif self.is_human_readable_format():
            # put output into self.human_readable_output
            pass
        else:
            raise "err"


    def _store_multiple_device_output_gpuvsmi(self):
        if self.is_json_format() or self.is_human_readable_format():
            self.multiple_device_output.append(self.output)
            self.output = {}
        elif self.is_csv_format():
            # put output into self.csv_output
            pass
        else:
            raise "err"


    def store_watch_output(self, multiple_devices=False):
        """ Add the current output or multiple_devices_output
            params:
                multiple_devices (bool) - True if watching multiple devices
            return:
                Nothing
        """
        if self.is_amdsmi_compatibility():
            self._store_watch_output_amdsmi(multiple_devices=multiple_devices)
        elif self.is_rocmsmi_compatibility():
            self._store_watch_output_rocmsmi(multiple_devices=multiple_devices)
        elif self.is_gpuvsmi_compatibility():
            self._store_watch_output_gpuvsmi(multiple_devices=multiple_devices)


    def _store_watch_output_amdsmi(self, multiple_devices):
        if self.is_json_format() or self.is_human_readable_format():
            values = self.output
            if multiple_devices:
                values = self.multiple_device_output

            self.watch_output.append({'timestamp': int(time.time()),
                                        'values': values})
        elif self.is_csv_format():
            # put output into self.csv_output
            pass
        else:
            raise "err"


    def _store_watch_output_rocmsmi(self, multiple_devices):
        if self.is_json_format():
            # put output into self.json_output
            pass
        elif self.is_csv_format():
            # put output into self.csv_output
            pass
        elif self.is_human_readable_format():
            # put output into self.human_readable_output
            pass
        else:
            raise "err"


    def _store_watch_output_gpuvsmi(self, multiple_devices):
        if self.is_json_format() or self.is_human_readable_format():
            values = self.output
            if multiple_devices:
                values = self.multiple_device_output

            self.watch_output.append({'timestamp': int(time.time()),
                                        'values': values})
        elif self.is_csv_format():
            # put output into self.csv_output
            pass
        else:
            raise "err"


    def capitalize_keys(self, input_dict):
        output_dict = {}
        for key in input_dict.keys():
            # Capitalize key if it is a string
            if isinstance(key, str):
                cap_key = key.upper()
            else:
                cap_key = key

            if isinstance(input_dict[key], dict):
                output_dict[cap_key] = self.capitalize_keys(input_dict[key])
            elif isinstance(input_dict[key], list):
                cap_key_list = []
                for data in input_dict[key]:
                    if isinstance(data, dict):
                        cap_key_list.append(self.capitalize_keys(data))
                    else:
                        cap_key_list.append(data)
                output_dict[cap_key] = cap_key_list
            else:
                output_dict[cap_key] = input_dict[key]

        return output_dict


    def convert_json_to_human_readable(self, json_object):
        # First Capitalize all keys in the json object
        capitalized_json = self.capitalize_keys(json_object)
        json_string = json.dumps(capitalized_json, indent=4)
        yaml_data = yaml.safe_load(json_string)
        yaml_output = yaml.dump(yaml_data, sort_keys=False, allow_unicode=True)

        if self.is_gpuvsmi_compatibility():
            # Convert from GPU: 0 to GPU 0:
            yaml_output = re.sub('GPU: ([0-9]+)', 'GPU \\1:', yaml_output)

        # Remove a key line if it is a spacer
        yaml_output = yaml_output.replace("AMDSMI_SPACING_REMOVAL:\n", "")
        yaml_output = yaml_output.replace("'", "") # Remove ''

        clean_yaml_output = ''
        for line in yaml_output.splitlines():
            line = line.split(':')

            # Remove dashes and increase tabbing split key
            line[0] = line[0].replace("-", " ", 1)
            line[0] = line[0].replace("  ", "    ")

            # Join cleaned output
            line = ':'.join(line) + '\n'
            clean_yaml_output += line

        return clean_yaml_output


    def print_output(self, multiple_device_output=False, watch_output=False):
        """ Print current output acording to format and then destination
            params:
                multiple_device_output (bool) - True if printing output from
                    multiple devices
                watch_output (bool) - True if printing watch output
            return:
                Nothing
        """
        if self.is_json_format():
            self._print_json_output(multiple_device_output=multiple_device_output,
                                    watch_output=watch_output)
        elif self.is_csv_format():
            self._print_csv_output(multiple_device_output=multiple_device_output,
                                    watch_output=watch_output)
        elif self.is_human_readable_format():
            self._print_human_readable_output(multiple_device_output=multiple_device_output,
                                                watch_output=watch_output)


    def _print_json_output(self, multiple_device_output=False, watch_output=False):
        json_output = json.dumps(self.output, indent = 4)
        json_multiple_device_output = json.dumps(self.multiple_device_output, indent = 4)
        if self.destination == 'stdout':
            if watch_output:
                return # We don't need to print to stdout at the end of watch
            elif multiple_device_output:
                print(json_multiple_device_output)
            else:
                print(json_output)
        else: # Write output to file
            if watch_output:
                with self.destination.open('w') as output_file:
                    json.dump(self.watch_output, output_file, indent=4)
            elif multiple_device_output:
                with self.destination.open('a') as output_file:
                    json.dump(self.multiple_device_output, output_file, indent=4)
            else:
                with self.destination.open('a') as output_file:
                    json.dump(self.output, output_file, indent=4)


    def _print_csv_output(self, multiple_device_output=False, watch_output=False):
        if self.destination == 'stdout':
            if watch_output:
                return # We don't need to print to stdout at the end of watch
            elif multiple_device_output:
                pass
            else:
                pass
        else: # Write output to file
            if watch_output:
                pass
            elif multiple_device_output:
                pass
            else:
                pass


    def _print_human_readable_output(self, multiple_device_output=False, watch_output=False):
        if multiple_device_output:
            human_readable = ''
            for output in self.multiple_device_output:
                human_readable += (self.convert_json_to_human_readable(output))
        else:
            human_readable = self.convert_json_to_human_readable(self.output)

        if self.destination == 'stdout':
            if watch_output:
                return
                # print_output may need another value: flush_output vs watch_output
            print(human_readable)
        else:
            if watch_output:
                return
            with self.destination.open('a') as output_file:
                output_file.write(human_readable)

        return

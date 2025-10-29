#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
#
# Copyright (C) Advanced Micro Devices. All rights reserved.
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

# This script is used to quickly debug and check amdsmi Python APIs.
# This is not meant to serve best practices for development.
# Run this post install with python3 -i quick_start.py

import argparse
import datetime
import os
import sys
import pathlib
import textwrap

version_number = '1.0.0'
build_date = f'{datetime.datetime.now():%b %d %Y}'
verbose_choices = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'ALWAYS']


def Check_For_Files(amdsmi, file_names):
    header_found = True
    if not os.path.exists(amdsmi):
        header_found = False

    log_files = []
    log_files_missing = []
    for key, file_path in file_names.items():
        if file_path != None:
            if os.path.exists(file_path):
                log_files.append(file_path)
            else:
                log_files_missing.append(file_path)
                continue
    return (header_found, log_files, log_files_missing)

def Find_Root_Dir(root_dir):
    sys_root_path = pathlib.Path('/')
    root = pathlib.Path(root_dir)
    while (True):
        if False: # jcnii
            print(f'root={root}')
            print(f'\tcwd={root.cwd()}')
            print(f'\tname={root.name}')
            print(f'\tstem={root.stem}')
            print(f'\tsuffix={root.suffix}')
            print(f'\tanchor={root.anchor}')
            print(f'\tparent={root.parent}')
        git_dir = pathlib.Path(root / '.git')
        if git_dir.exists():
            root_dir = root
            break
        root = pathlib.Path(root.parent)
        if root.parent == sys_root_path:
            print(f'Could not find root dir in path {root_dir}')
            root_dir = None
            break
    return root_dir

def Main():
#{
    return 0
#}


def Parse_Command_Line(cmds=None):
#{
    msg_description = 'Create API coverage report for unit_test.py and integration_test.py tests'
    msg_epilog = 'Example:\n\t%(prog)s --c_unit_test <c_unit_test.log> --py_integration_test <py_integration_test.log>'
    parser = argparse.ArgumentParser(description=msg_description, formatter_class=argparse.RawTextHelpFormatter, epilog=textwrap.dedent(msg_epilog))

    parser_header = parser.add_argument_group('Information')
    parser.add_argument('--version', action='version', version=version_number, help='Show version and exit')
    parser.add_argument('--build', action='version', version=build_date, help='Show build and exit')
    parser.add_argument('--verbose', choices=verbose_choices , type=str, default='WARNING', help='Level of information to output, default=%(default)s')

    parser_header = parser.add_argument_group('Header File')
    parser_header.add_argument('--amdsmi', default='include/amd_smi/amdsmi.h', help='Path to header file amdsmi.h, default=%(default)s')
    parser_logs = parser.add_argument_group('Log Files')
    parser_logs.add_argument('--c_unit_test', default='build/_c_unit_test.log', help='Path to C unit_test output')
    parser_logs.add_argument('--c_integration', default='build/_c_integration_test.log', help='Path to C integration_test output')
    parser_logs.add_argument('--py_unit_test', default='build/_unit_test.log', help='Path to python unit_test output')
    parser_logs.add_argument('--py_integration', default='build/_integration_test.log', help='Path to python integration_test output')
    parser_output = parser.add_argument_group('Output File')
    parser_output.add_argument('--output', default='./api_summary.csv', help='Path to output file')

    if cmds:
        args = parser.parse_args(cmds.split())
    else:
        args = parser.parse_args()

    args.file_names = {}
    args.file_names['c_unit_test'] = args.c_unit_test
    args.file_names['c_integration'] = args.c_integration
    args.file_names['py_unit_test'] = args.py_unit_test
    args.file_names['py_integration'] = args.py_integration

    header_found, log_files, log_files_missing = Check_For_Files(args.amdsmi, args.file_names)
            
    if not header_found or not len(log_files):
        cwd = pathlib.Path.cwd()
        root_dir = Find_Root_Dir(cwd)
        if root_dir:
            args.amdsmi = root_dir / pathlib.Path(args.amdsmi)
            if False: #jcnii
                print(f'root_dir={root_dir}')
                print(f'\tamdsmi={args.amdsmi}')
            for file_name in args.file_names:
                args.file_names[file_name] = root_dir / pathlib.Path(args.file_names[file_name])
                if False: #jcnii
                    print(f'\tfile_name={args.file_names[file_name]}')
            header_found, log_files, log_files_missing = Check_For_Files(args.amdsmi, args.file_names)

    if not header_found or not len(log_files):
        if not header_found:
            print(f'Header path does not exist: {args.amdsmi}')
        if not len(log_files):
            for log_file in log_files_missing:
                print(f'Log file path does not exist: {log_file}')
        #parser.print_help()
        sys.exit(1)

    print(f'Using Header: {args.amdsmi}')
    for log_file in log_files:
        print(f'Using Log file: {log_file}')

    return args
#}


if __name__ == '__main__':
#{
    args = Parse_Command_Line()
    rc = Main()
    sys.exit(rc)
#}


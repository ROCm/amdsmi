import argparse
import datetime
import os
import sys
import textwrap

version_number = '1.0.0'
build_date = f'{datetime.datetime.now():%b %d %Y}'
verbose_choices = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'ALWAYS']

open_parenthesis = '('
close_parenthesis = ')'

header = 'any C(any, func, unit) py(any, func, unit)'


def ReadAmdsmiHeader(file_content):
#{
    api_map = {}
    end_block_pos = 0
    while (True):
    #{
        start_block_pos = file_content.find('@ingroup', end_block_pos)
        if start_block_pos == -1:
            break

        end_block_pos = file_content.find(f'{close_parenthesis};', start_block_pos)
        if end_block_pos == -1:
            print(f'Could not find func definition end, {start_block_pos}')
            break

        end_pos = file_content.rfind(open_parenthesis, start_block_pos, end_block_pos)
        start_pos = file_content.rfind('amdsmi_', start_block_pos, end_pos)
        #print(f'start_block_pos={start_block_pos}  start_pos={start_pos} end_pos={end_pos}  end_block_pos={end_block_pos}')
        func_name = file_content[start_pos:end_pos].strip()
        api_map[func_name] = 0
    #}

    return api_map
#}

def ReadTestingInput(file_contents):
#{
    # api_map[file_name][func_name] = number_times_called
    api_map = {}
    for file_name in file_contents:
    #{
        api_map[file_name] = {}
        for line in file_contents[file_name]:
        #{
            #for line in file_content:
            if '###' in line:
            #{
                pos_start = line.find('amdsmi_')
                if pos_start == -1:
                #{
                    print(f'start: Bad ### definition, {line}')
                    continue
                #}
                pos_end = line.find(open_parenthesis)
                if pos_end == -1:
                #{
                    print(f'end: Bad ### definition, {line}')
                    continue
                #}

                func_name = line[pos_start:pos_end].strip()
                if func_name in api_map[file_name]:
                    api_map[file_name][func_name] += 1
                else:
                    api_map[file_name][func_name] = 1
            #}
        #}
    #}

    return api_map
#}


def Main(amdsmi_content, file_contents):
#{
    # Read in header input
    amdsmi_map = {}
    if amdsmi_content:
        amdsmi_map = ReadAmdsmiHeader(amdsmi_content)
    num_api = len(amdsmi_map)
    if not num_api:
    #{
        num_api = 1  # set so code does not divide by zero
        print('No header APIs found')
    #}
    if False:
    #{
        print(f'amdsmi APIs = {num_api}')
        for func_name in amdsmi_map:
            print(f'\tfunc: {func_name}')
    #}

    # Read in testing inputs
    api_map = ReadTestingInput(file_contents)
    found = False
    for file_name in api_map:
    #{
        if len(api_map[file_name]):
            found = True
    #}
    if not found:
    #{
        print('No testing APIs found')
        return 1
    #}
    if True:
    #{
        for file_name in api_map:
        #{
            print(f'Tested {file_name} funcs = {len(api_map[file_name])}')
            for func_name in api_map[file_name]:
                print(f'\tfunc: {func_name}')
        #}
    #}

    if False:
        #{
        # Find missing APIs
        #     api == 0 -> Missing
        #     api == 1 -> Tested
        for func_name in amdsmi_map:
        #{
            amdsmi_map[func_name] = [0, []]
            # Mark function as either 0 or 1
            for file_name in api_map:
            #{
                if func_name in api_map[file_name]:
                    amdsmi_map[func_name][0] = 1
                    amdsmi_map[func_name][1].append(file_name)
            #}
        #}

        for func_name, values in amdsmi_map.items():
            has_been_tested = values[0]
            file_names = values[1]
            if has_been_tested == 0:
                print(f'Missing:', end='')
            else:
                print(f'  Found:', end='')
            print(f' {func_name}: {file_names}')
    #}

    if False:
        for func_name in amdsmi_map:
        #{
            amdsmi_map[func_name] = {'tested':0, 'c_unit_test':0, 'c_integration':0, 'py_unit_test':0, 'py_integration':0}
            for file_name in api_map:
            #{
                if func_name in api_map[file_name]:
                    amdsmi_map[func_name]['tested'] = 1
                    amdsmi_map[func_name][file_name] = 1
            #}
        #}
    else: # better way
        # Initialize
        for func_name in amdsmi_map:
            amdsmi_map[func_name] = {'tested':0, 'c_unit_test':0, 'c_integration':0, 'py_unit_test':0, 'py_integration':0}
# api_map[file_name][func_name] = number_times_called
        for file_name in api_map:
        #{
            for func_name in api_map[file_name]:
            #{
                amdsmi_map[func_name]['tested'] += 1
                amdsmi_map[func_name][file_name] = 1
            #}
        #}

    print(f'API, Tested, c_unit_test, c_integration, py_unit_test, py_integration')
    for func_name, tests_map in amdsmi_map.items():
        print(f'{func_name}, {tests_map["tested"]}, {tests_map["c_unit_test"]}, {tests_map["c_integration"]}, {tests_map["py_unit_test"]}, {tests_map["py_integration"]}')
    
    if True:
    #{
        c_unit_test_total = 0
        c_integration_total = 0
        c_any_total = 0
        py_unit_test_total = 0
        py_integration_total = 0
        py_any_total = 0
        any_total = 0
        integration_total = 0
        unit_test_total = 0
        for func_name, values in amdsmi_map.items():
        #{
            tested = values['tested']
            if tested:
            #{
                c_unit_test = values['c_unit_test']
                c_integration = values['c_integration']
                c_any = 0
                if c_unit_test or c_integration:
                #{
                    c_any = 1
                    c_any_total += 1
                    if c_unit_test:
                        c_unit_test_total += 1
                    if c_integration:
                        c_integration_total += 1
                #}

                py_unit_test = values['py_unit_test']
                py_integration = values['py_integration']
                py_any = 0
                if py_unit_test or py_integration:
                #{
                    py_any = 1
                    py_any_total += 1
                    if py_unit_test:
                        py_unit_test_total += 1
                    if py_integration:
                        py_integration_total += 1
                #}

                if c_integration or py_integration:
                    integration_total += 1

                if c_unit_test or py_unit_test:
                    unit_test_total += 1

                if c_unit_test or c_integration or py_unit_test or py_integration:
                    any_total += 1

                if tested == 0:
                    print(f'Missing:', end='')
                else:
                    print(f'  Found:', end='')
                print(f' {func_name}: C(any={c_any} unit={c_unit_test} int={c_integration}) py(any={py_any} unit={py_unit_test} int={py_integration})')
            #}
        #}

        print(f'Totals: c(any={c_any_total}, unit={c_unit_test_total}, int={c_integration_total})')
        print(f'Totals: py(any={py_any_total}, unit={py_unit_test_total}, int={py_integration_total})')
    #}

    if False: # for testing
        c_unit_test_total = 100
        c_integration_total = 100
        c_any_total = 100
        py_unit_test_total = 100
        py_integration_total = 100
        py_any_total = 100
        any_total = 100
        integration_total = 100
        unit_test_total = 100

    c_any_total_percent = (c_any_total / num_api) * 100
    c_unit_test_total_percent = (c_unit_test_total / num_api) * 100
    c_integration_total_percent = (c_integration_total / num_api) * 100

    py_any_total_percent = (py_any_total / num_api) * 100
    py_unit_test_total_percent = (py_unit_test_total / num_api) * 100
    py_integration_total_percent = (py_integration_total / num_api) * 100

    any_total_percent = (any_total / num_api) * 100
    unit_test_total_percent = (unit_test_total / num_api) * 100
    integration_total_percent = (integration_total / num_api) * 100

    #API          Test(%)                    Func(%)                  Unit(%)
    #C      c_any_total(XX.X)  c_integration_total(XX.X)  c_unit_test_total(XX.X)
    #Py    py_any_total(XX.X) py_integration_total(XX.X) py_unit_test_total(XX.X)
    #Total    any_total(XX.X)    integration_total(XX.X)    unit_test_total(XX.X)
    #
    #Total API's: <Num>

    def PrintLine(val1, num1, val2, num2, val3, num3, val4, num4):
    #{
        print(f'{val1:^{num1}s} {val2:^{num2}s} {val3:^{num3}s} {val4:^{num4}s}')
    #}
    def PrintLine2(val, num, val1a, num1a, val1b, num1b, val1c, num1c, val2a, num2a, val2b, num2b, val2c, num2c, val3a, num3a, val3b, num3b, val3c, num3c):
    #{
        print(f'{val:^{num}} {val1a:{num1a}s}{val1b:{num1b}d}({val1c:{num1c}f}) {val2a:{num2a}s}{val2b:{num2b}d}({val2c:{num2c}f}) {val3a:{num3a}s}{val3b:{num3b}d}({val3c:{num3c}f})')
    #}

    size_d = 3
    size_f = 4.1
    space1 = 5
    space2 = 1
    space3 = 11
    PrintLine('API', space1, 'Test(%)', space3, 'Unit(%)', space3, 'Func(%)', space3)
    PrintLine2('C', space1,
        ' ', space2, c_any_total,         size_d, c_any_total_percent,         size_f,
        ' ', space2, c_unit_test_total,   size_d, c_unit_test_total_percent,   size_f,
        ' ', space2, c_integration_total, size_d, c_integration_total_percent, size_f)
    PrintLine2('Py', space1, ' ', space2, py_any_total, size_d, py_any_total_percent, size_f, ' ', space2, py_unit_test_total, size_d, py_unit_test_total_percent, size_f, ' ', space2, py_integration_total, size_d, py_integration_total_percent, size_f)
    PrintLine2('Total', space1, ' ', space2, any_total, size_d, any_total_percent, size_f, ' ', space2, unit_test_total, size_d, unit_test_total_percent, size_f, ' ', space2, integration_total, size_d, integration_total_percent, size_f)

    print(f'Num APIs: {num_api}')

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
    parser_logs.add_argument('--c_unit_test', default='./build/_c_unit_test.log', help='Path to C unit_test output')
    parser_logs.add_argument('--c_integration', default='./build/_c_integration_test.log', help='Path to C integration_test output')
    parser_logs.add_argument('--py_unit_test', default='./build/_unit_test.log', help='Path to python unit_test output')
    parser_logs.add_argument('--py_integration', default='./build/_integration_test.log', help='Path to python integration_test output')
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

    header_found = True
    if not os.path.exists(args.amdsmi):
        print(f'Header path does not exist: {args.amdsmi}')
        header_found = False

    num_log_files = 0
    for key, file_path in args.file_names.items():
        if file_path != None:
            if os.path.exists(file_path):
                num_log_files += 1
                continue
            args.file_names[key] = None
            
    if not header_found or not num_log_files:
        parser.print_help()
        sys.exit(1)

    return args
#}


if __name__ == '__main__':
#{
    rc = 1
    args = Parse_Command_Line()

    # Check that all testing files exist
    all_files_exist = True
    for key in args.file_names:
    #{
        file_name = args.file_names[key]
        if file_name and not os.path.exists(file_name):
            all_files_exist = False
            print(f'Specified file does not exist, {file_name}, for {key}')
    #}
    if not all_files_exist:
        sys.exit(0)

    # Each file is stored as a [string]
    file_contents = {}
    for key in args.file_names:
    #{
        file_contents[key] = []

        file_name = args.file_names[key]
        if not file_name:
            continue

        with open(file_name, 'r') as fin:
            content = fin.read()
            file_contents[key] = content.split('\n')
        print(f'file_contents[{key}] = {len(file_contents[key])}')
    #}

    # Header file is stored as a string
    amdsmi_content = ''
    if os.path.exists(args.amdsmi):
        with open(args.amdsmi, 'r') as fin:
            content = fin.read()
            amdsmi_content = content

    rc = Main(amdsmi_content, file_contents)

    sys.exit(rc)
#}


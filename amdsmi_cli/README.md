# AMD SMI CLI Tool

This tool acts as a command line interface for manipulating
and monitoring the amdgpu kernel, and is intended to replace
and deprecate the existing rocm_smi CLI tool & gpuv-smi tool.
It uses Ctypes to call the amd_smi_lib API.
Recommended: At least one AMD GPU with AMD driver installed

## Requirements

* python 3.7+ 64-bit
* driver must be loaded for amdsmi_init() to pass

## Installation

* Install amdgpu driver
* Install amd-smi-lib package through package manager
* cd /opt/rocm/share/amd_smi
* python3 -m pip install --upgrade pip
* python3 -m pip install --user .
* /opt/rocm/bin/amd-smi --help

Add /opt/rocm/bin to your shell's path to access amd-smi via the cmdline

### RHEL 8 & SLES 15

The default python versions in RHEL 8 and SLES 15 are 3.6.8 and 3.6.15

While the CLI may work with these python versions, to install the python library you need to upgrade to python 3.7+

Verify that your python version is 3.7+ to install the python library

### Install Example for Ubuntu 22.04

``` bash
apt install amd-smi-lib
cd /opt/rocm/share/amd_smi
python3 -m pip install --upgrade pip
python3 -m pip install --user .
/opt/rocm/bin/amd-smi
```

Add /opt/rocm/bin to your shell's path to access amd-smi via the cmdline

``` bash
export PATH=$PATH:/opt/rocm/bin
```

## Usage

amd-smi will report the version and current platform detected when running the command without arguments:

``` bash
amd-smi
usage: amd-smi [-h]  ...

AMD System Management Interface | Version: 23.2.0.1 | Platform: Linux Baremetal

optional arguments:
  -h, --help        show this help message and exit

AMD-SMI Commands:
                    Descriptions:
    version         Display version information
    discovery (list)
                    Display discovery information
    static          Gets static information about the specified GPU
    firmware (ucode)
                    Gets firmware information about the specified GPU
    bad-pages       Gets bad page information about the specified GPU
    metric          Gets metric/performance information about the specified GPU
    process         Lists general process information running on the specified GPU
    topology        Displays topology information of the devices.
    set             Set options for devices.
    reset           Reset options for devices.
```

More detailed verison information can be give when running `amd-smi version`

Each command will have detailed information via `amd-smi [command] --help`

## Commands

For convenience, here is the help output for each command

``` bash
amd-smi discovery --help
usage: amd-smi discovery [-h] [--json | --csv] [--file FILE]
                         [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                         [-g GPU [GPU ...]]

Lists all the devices on the system and the links between devices.
Lists all the sockets and for each socket, GPUs and/or CPUs associated to
that socket alongside some basic information for each device.
In virtualization environments, it can also list VFs associated to each
GPU with some basic information for each VF.

optional arguments:
  -h, --help                                      show this help message and exit
  -g GPU [GPU ...], --gpu GPU [GPU ...]           Select a GPU ID, BDF, or UUID from the possible choices:
                                                  ID:0  | BDF:0000:23:00.0 | UUID:ffffffff-ffff-ffff-ffff-ffffffffffff

Command Modifiers:
  --json                                          Displays output in JSON format (human readable by default).
  --csv                                           Displays output in CSV format (human readable by default).
  --file FILE                                     Saves output into a file on the provided path (stdout by default).
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}  Set the logging level for the parser commands
```

``` bash
amd-smi firmware --help
usage: amd-smi firmware [-h] [--json | --csv] [--file FILE]
                        [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        [-g GPU [GPU ...]] [-f]

If no GPU is specified, return firmware information for all GPUs on the system.

Firmware Arguments:
  -h, --help                                      show this help message and exit
  -g GPU [GPU ...], --gpu GPU [GPU ...]           Select a GPU ID, BDF, or UUID from the possible choices:
                                                  ID:0  | BDF:0000:23:00.0 | UUID:ffffffff-ffff-ffff-ffff-ffffffffffff
  -f, --ucode-list, --fw-list                     All FW list information

Command Modifiers:
  --json                                          Displays output in JSON format (human readable by default).
  --csv                                           Displays output in CSV format (human readable by default).
  --file FILE                                     Saves output into a file on the provided path (stdout by default).
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}  Set the logging level for the parser commands
```

```bash
amd-smi static --help
usage: amd-smi static [-h] [--json | --csv] [--file FILE]
                      [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-g GPU [GPU ...]]
                      [-a] [-b] [-V] [-l] [-d] [-c] [-r] [-B] [-u]

If no GPU is specified, returns static information for all GPUs on the system.
If no static argument is provided, all static information will be displayed.

Static Arguments:
  -h, --help                                      show this help message and exit
  -g GPU [GPU ...], --gpu GPU [GPU ...]           Select a GPU ID, BDF, or UUID from the possible choices:
                                                  ID:0  | BDF:0000:23:00.0 | UUID:ffffffff-ffff-ffff-ffff-ffffffffffff
  -a, --asic                                      All asic information
  -b, --bus                                       All bus information
  -V, --vbios                                     All video bios information (if available)
  -l, --limit                                     All limit metric values (i.e. power and thermal limits)
  -d, --driver                                    Displays driver version
  -r, --ras                                       Displays RAS features information
  -B, --board                                     All board information
  -u, --numa                                      All numa node information

Command Modifiers:
  --json                                          Displays output in JSON format (human readable by default).
  --csv                                           Displays output in CSV format (human readable by default).
  --file FILE                                     Saves output into a file on the provided path (stdout by default).
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}  Set the logging level for the parser commands
```

```bash
amd-smi bad-pages --help
usage: amd-smi bad-pages [-h] [--json | --csv] [--file FILE]
                         [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                         [-g GPU [GPU ...]] [-p] [-r] [-u]

If no GPU is specified, return bad page information for all GPUs on the system.

Bad Pages Arguments:
  -h, --help                                      show this help message and exit
  -g GPU [GPU ...], --gpu GPU [GPU ...]           Select a GPU ID, BDF, or UUID from the possible choices:
                                                  ID:0  | BDF:0000:23:00.0 | UUID:ffffffff-ffff-ffff-ffff-ffffffffffff
  -p, --pending                                   Displays all pending retired pages
  -r, --retired                                   Displays retired pages
  -u, --un-res                                    Displays unreservable pages

Command Modifiers:
  --json                                          Displays output in JSON format (human readable by default).
  --csv                                           Displays output in CSV format (human readable by default).
  --file FILE                                     Saves output into a file on the provided path (stdout by default).
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}  Set the logging level for the parser commands
```

```bash
amd-smi metric --help
usage: amd-smi metric [-h] [--json | --csv] [--file FILE]
                      [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-g GPU [GPU ...]]
                      [-w loop_time] [-W total_loop_time] [-i number_of_iterations] [-u]
                      [-b] [-p] [-c] [-t] [-e] [-P] [-V] [-f] [-C] [-o] [-M] [-l] [-r]
                      [-x] [-E] [-m]

If no GPU is specified, returns metric information for all GPUs on the system.
If no metric argument is provided all metric information will be displayed.

Metric arguments:
  -h, --help                                                  show this help message and exit
  -g GPU [GPU ...], --gpu GPU [GPU ...]                       Select a GPU ID, BDF, or UUID from the possible choices:
                                                              ID:0  | BDF:0000:23:00.0 | UUID:ffffffff-ffff-ffff-ffff-ffffffffffff
  -w loop_time, --watch loop_time                             Reprint the command in a loop of Interval seconds
  -W total_loop_time, --watch_time total_loop_time            The total time to watch the given command
  -i number_of_iterations, --iterations number_of_iterations  Total number of iterations to loop on the given command
  -u, --usage                                                 Displays engine usage information
  -b, --fb-usage                                              Total and used framebuffer
  -p, --power                                                 Current power usage
  -c, --clock                                                 Average, max, and current clock frequencies
  -t, --temperature                                           Current temperatures
  -e, --ecc                                                   Number of ECC errors
  -P, --pcie                                                  Current PCIe speed and width
  -V, --voltage                                               Current GPU voltages
  -f, --fan                                                   Current fan speed
  -C, --voltage-curve                                         Display voltage curve
  -o, --overdrive                                             Current GPU clock overdrive level
  -M, --mem-overdrive                                         Current memory clock overdrive level
  -l, --perf-level                                            Current DPM performance level
  -r, --replay-count                                          PCIe replay count
  -x, --xgmi-err                                              XGMI error information since last read
  -E, --energy                                                Amount of energy consumed
  -m, --mem-usage                                             Memory usage per block

Command Modifiers:
  --json                                                      Displays output in JSON format (human readable by default).
  --csv                                                       Displays output in CSV format (human readable by default).
  --file FILE                                                 Saves output into a file on the provided path (stdout by default).
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}              Set the logging level for the parser commands
```

```bash
amd-smi process --help
usage: amd-smi process [-h] [--json | --csv] [--file FILE]
                       [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-g GPU [GPU ...]]
                       [-w loop_time] [-W total_loop_time] [-i number_of_iterations] [-G]
                       [-e] [-p PID] [-n NAME]

If no GPU is specified, returns information for all GPUs on the system.
If no process argument is provided all process information will be displayed.

Process arguments:
  -h, --help                                                  show this help message and exit
  -g GPU [GPU ...], --gpu GPU [GPU ...]                       Select a GPU ID, BDF, or UUID from the possible choices:
                                                              ID:0  | BDF:0000:23:00.0 | UUID:ffffffff-ffff-ffff-ffff-ffffffffffff
  -w loop_time, --watch loop_time                             Reprint the command in a loop of Interval seconds
  -W total_loop_time, --watch_time total_loop_time            The total time to watch the given command
  -i number_of_iterations, --iterations number_of_iterations  Total number of iterations to loop on the given command
  -G, --general                                               pid, process name, memory usage
  -e, --engine                                                All engine usages
  -p PID, --pid PID                                           Gets all process information about the specified process based on Process ID
  -n NAME, --name NAME                                        Gets all process information about the specified process based on Process Name.
                                                              If multiple processes have the same name information is returned for all of them.

Command Modifiers:
  --json                                                      Displays output in JSON format (human readable by default).
  --csv                                                       Displays output in CSV format (human readable by default).
  --file FILE                                                 Saves output into a file on the provided path (stdout by default).
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}              Set the logging level for the parser commands
```

```bash
amd-smi topology --help
usage: amd-smi topology [-h] [--json | --csv] [--file FILE]
                        [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        [-g GPU [GPU ...]] [-a] [-w] [-o] [-t] [-b]

If no GPU is specified, returns information for all GPUs on the system.
If no topology argument is provided all topology information will be displayed.

Topology arguments:
  -h, --help                                      show this help message and exit
  -g GPU [GPU ...], --gpu GPU [GPU ...]           Select a GPU ID, BDF, or UUID from the possible choices:
                                                  ID:0  | BDF:0000:23:00.0 | UUID:ffffffff-ffff-ffff-ffff-ffffffffffff
  -a, --access                                    Displays link accessibility between GPUs
  -w, --weight                                    Displays relative weight between GPUs
  -o, --hops                                      Displays the number of hops between GPUs
  -t, --link-type                                 Displays the link type between GPUs
  -b, --numa-bw                                   Display max and min bandwidth between nodes

Command Modifiers:
  --json                                          Displays output in JSON format (human readable by default).
  --csv                                           Displays output in CSV format (human readable by default).
  --file FILE                                     Saves output into a file on the provided path (stdout by default).
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}  Set the logging level for the parser commands
```

```bash
amd-smi set --help
usage: amd-smi set [-h] [--json | --csv] [--file FILE]
                   [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}] -g GPU [GPU ...]
                   [-c CLK_TYPE [CLK_LEVELS ...]] [-s CLK_LEVELS [CLK_LEVELS ...]]
                   [-m CLK_LEVELS [CLK_LEVELS ...]] [-p CLK_LEVELS [CLK_LEVELS ...]]
                   [-S SCLKLEVEL SCLK] [-M MCLKLEVEL MCLK] [-V POINT SCLK SVOLT]
                   [-r SCLKMIN SCLKMAX] [-R MCLKMIN MCLKMAX] [-f %] [-l LEVEL] [-o %]
                   [-O %] [-w WATTS] [-P SETPROFILE] [-d SCLKMAX]

A GPU must be specified to set a configuration.
A set argument must be provided; Multiple set arguments are accepted

Set Arguments:
  -h, --help                                                          show this help message and exit
  -g GPU [GPU ...], --gpu GPU [GPU ...]                               Select a GPU ID, BDF, or UUID from the possible choices:
                                                                      ID:0  | BDF:0000:23:00.0 | UUID:ffffffff-ffff-ffff-ffff-ffffffffffff
  -c CLK_TYPE [CLK_LEVELS ...], --clock CLK_TYPE [CLK_LEVELS ...]     Sets clock frequency levels for specified clocks
  -s CLK_LEVELS [CLK_LEVELS ...], --sclk CLK_LEVELS [CLK_LEVELS ...]  Sets GPU clock frequency levels
  -m CLK_LEVELS [CLK_LEVELS ...], --mclk CLK_LEVELS [CLK_LEVELS ...]  Sets memory clock frequency levels
  -p CLK_LEVELS [CLK_LEVELS ...], --pcie CLK_LEVELS [CLK_LEVELS ...]  Sets PCIe Bandwith
  -S SCLKLEVEL SCLK, --slevel SCLKLEVEL SCLK                          Change GPU clock frequency and voltage for a specific level
  -M MCLKLEVEL MCLK, --mlevel MCLKLEVEL MCLK                          Change GPU memory frequency and voltage for a specific level
  -V POINT SCLK SVOLT, --vc POINT SCLK SVOLT                          Change SCLK voltage curve for a specified point
  -r SCLKMIN SCLKMAX, --srange SCLKMIN SCLKMAX                        Sets min and max SCLK speed
  -R MCLKMIN MCLKMAX, --mrange MCLKMIN MCLKMAX                        Sets min and max MCLK speed
  -f %, --fan %                                                       Sets GPU fan speed (0-255 or 0-100%)
  -l LEVEL, --perflevel LEVEL                                         Sets performance level
  -o %, --overdrive %                                                 Set GPU overdrive (0-20%) ***DEPRECATED IN NEWER KERNEL VERSIONS (use --slevel instead)***
  -O %, --memoverdrive %                                              Set memory overclock overdrive level ***DEPRECATED IN NEWER KERNEL VERSIONS (use --mlevel instead)***
  -w WATTS, --poweroverdrive WATTS                                    Set the maximum GPU power using power overdrive in Watts
  -P SETPROFILE, --profile SETPROFILE                                 Set power profile level (#) or a quoted string of custom profile attributes
  -d SCLKMAX, --perfdeterminism SCLKMAX                               Sets GPU clock frequency limit and performance level to determinism to get minimal performance variation

Command Modifiers:
  --json                                                              Displays output in JSON format (human readable by default).
  --csv                                                               Displays output in CSV format (human readable by default).
  --file FILE                                                         Saves output into a file on the provided path (stdout by default).
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}                      Set the logging level for the parser commands
```

```bash
amd-smi reset --help
usage: amd-smi reset [-h] [--json | --csv] [--file FILE]
                     [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}] -g GPU [GPU ...]
                     [-G] [-c] [-f] [-p] [-o] [-x] [-d]

A GPU must be specified to reset a configuration.
A reset argument must be provided; Multiple reset arguments are accepted

Reset Arguments:
  -h, --help                                      show this help message and exit
  -g GPU [GPU ...], --gpu GPU [GPU ...]           Select a GPU ID, BDF, or UUID from the possible choices:
                                                  ID:0  | BDF:0000:23:00.0 | UUID:ffffffff-ffff-ffff-ffff-ffffffffffff
  -G, --gpureset                                  Reset the specified GPU
  -c, --clocks                                    Reset clocks and overdrive to default
  -f, --fans                                      Reset fans to automatic (driver) control
  -p, --profile                                   Reset power profile back to default
  -o, --poweroverdrive                            Set the maximum GPU power back to the device default state
  -x, --xgmierr                                   Reset XGMI error counts
  -d, --perfdeterminism                           Disable performance determinism

Command Modifiers:
  --json                                          Displays output in JSON format (human readable by default).
  --csv                                           Displays output in CSV format (human readable by default).
  --file FILE                                     Saves output into a file on the provided path (stdout by default).
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}  Set the logging level for the parser commands
```

## Disclaimer

The information contained herein is for informational purposes only, and is subject to change without notice. While every precaution has been taken in the preparation of this document, it may contain technical inaccuracies, omissions and typographical errors, and AMD is under no obligation to update or otherwise correct this information. Advanced Micro Devices, Inc. makes no representations or warranties with respect to the accuracy or completeness of the contents of this document, and assumes no liability of any kind, including the implied warranties of noninfringement, merchantability or fitness for particular purposes, with respect to the operation or use of AMD hardware, software or other products described herein.

AMD, the AMD Arrow logo, and combinations thereof are trademarks of Advanced Micro Devices, Inc. Other product names used in this publication are for identification purposes only and may be trademarks of their respective companies.

Copyright (c) 2014-2023 Advanced Micro Devices, Inc. All rights reserved.

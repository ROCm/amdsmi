---
myst:
  html_meta:
    "description lang=en": "Get started with the AMD SMI Python interface."
    "keywords": "api, smi, lib, py, system, management, interface, ROCm"
---

# AMD SMI Python interface overview

The AMD SMI Python interface provides a convenient way to interact with AMD
hardware through a simple and accessible [API](../reference/amdsmi-py-api.md).
Compatible with Python 3.6 and higher, this library requires the AMD driver to
be loaded for initialization -- review the [prerequisites](#install_reqs).

## Get started

To get started, the `amdsmi` folder should be copied and placed next to
the importing script. Import it as follows:

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

(py_lib_fs)=
### Folder structure

File name             | Description
----------------------|-------------------------------------------------
`__init__.py`         | Python package initialization file
`amdsmi_interface.py` | Amdsmi library Python interface
`amdsmi_wrapper.py`   | Python wrapper around amdsmi binary
`amdsmi_exception.py` | Amdsmi [exceptions](#py_exceptions) Python file

(py_usage)=
## Usage

```{note}
``hipcc`` and other compilers will not automatically link in the ``libamd_smi``
dynamic library. To compile code that uses the AMD SMI library API, ensure the
``libamd_smi.so`` can be located by setting the ``LD_LIBRARY_PATH`` environment
variable to the directory containing ``librocm_smi64.so`` (usually
``/opt/rocm/lib``) or by passing the ``-lamd_smi`` flag to the compiler.
```

```{seealso}
Refer to the [Python library API reference](../reference/amdsmi-py-api.md).
```

An application using AMD SMI must call `amdsmi_init()` to initialize the AMI SMI
library before all other calls. This call initializes the internal data
structures required for subsequent AMD SMI operations. In the call, a flag can
be passed to indicate if the application is interested in a specific device
type.

`amdsmi_shut_down()` must be the last call to properly close connection to
driver and make sure that any resources held by AMD SMI are released.

(py_exceptions)=
## Exceptions

All exceptions are in `amdsmi_exception.py` file.

Exceptions that can be thrown by AMD SMI are:

* `AmdSmiException`: base amdsmi exception class
* `AmdSmiLibraryException`: derives base `AmdSmiException` class and represents errors that can occur in amdsmi-lib.
  When this exception is thrown, `err_code` and `err_info` are set. `err_code` is an integer that corresponds to errors that can occur
  in amdsmi-lib and `err_info` is a string that explains the error that occurred.

   For example:

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

* `AmdSmiRetryException` : Derives `AmdSmiLibraryException` class and signals
  device is busy and call should be retried.
* `AmdSmiTimeoutException` : Derives `AmdSmiLibraryException` class and
  represents that call had timed out.
* `AmdSmiParameterException`: Derives base `AmdSmiException` class and
  represents errors related to invaild parameters passed to functions. When this
  exception is thrown, `err_msg` is set and it explains what is the actual and
  expected type of the parameters.
* `AmdSmiBdfFormatException`: Derives base `AmdSmiException` class and
  represents invalid bdf format.

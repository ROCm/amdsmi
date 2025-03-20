---
myst:
  html_meta:
    "description lang=en": "AMD SMI documentation and API reference."
    "keywords": "amdsmi, lib, cli, system, management, interface, amdgpu, admin, sys"
---

# AMD SMI documentation

The AMD System Management Interface (AMD SMI) library offers a unified tool for
managing and monitoring GPUs, particularly in high-performance computing
environments. It provides a user-space interface that allows applications to
control GPU operations, monitor performance, and retrieve information about the
system's drivers and GPUs.

Find the source code at <https://github.com/ROCm/amdsmi>.

```{note}
AMD SMI is the successor to <https://github.com/ROCm/rocm_smi_lib>.
```

::::{grid} 2
:gutter: 3

:::{grid-item-card} Install
* [Library and CLI tool installation](./install/install.md)
* [Build from source](./install/build.md)
:::

:::{grid-item-card} How to
* [C++ library usage](./how-to/amdsmi-cpp-lib.md)
* [Python library usage](./how-to/amdsmi-py-lib.md)
* [Go library usage](./how-to/amdsmi-go-lib.md)
* [CLI tool usage](./how-to/amdsmi-cli-tool.md)
* [Use AMD SMI in a Docker container](./how-to/setup-docker-container.md)
:::

:::{grid-item-card} Reference
* [C++ API](./reference/amdsmi-cpp-api.md)
  * [Modules](../doxygen/docBin/html/modules)
  * [Files](../doxygen/docBin/html/files)
  * [Globals](../doxygen/docBin/html/globals)
  * [Data structures](../doxygen/docBin/html/annotated)
  * [Data fields](../doxygen/docBin/html/functions_data_fields)
* [Python API](./reference/amdsmi-py-api.md)
* [Go API](./reference/amdsmi-go-api.md)
:::

:::{grid-item-card} Tutorials
* [AMD SMI examples (GitHub)](https://github.com/ROCm/amdsmi/tree/amd-staging/example)
* [ROCm SMI examples (GitHub)](https://github.com/ROCm/rocm_smi_lib/tree/amd-staging/example)
:::
::::

To contribute to the documentation, refer to
{doc}`Contributing to ROCm <rocm:contribute/contributing>`.

Find ROCm licensing information on the
{doc}`Licensing <rocm:about/license>` page.

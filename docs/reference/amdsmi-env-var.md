---
myst:
  html_meta:
    "description lang=en": "Explore the AMD SMI environment variable references."
    "keywords": "api, smi, ROCm, environment variables, environment, reference, settings, AMD SMI"
---

# AMD SMI environment variable reference

This section describes the environment variables used to control the behavior of AMD SMI.

```{list-table}
:header-rows: 1
:widths: 70 30

* - **Environment variable**
  - **Value**
* - `AMDSMI_ASIC_INFO_CACHE_MS` \
    Configures the cache duration for ASIC information retrieved by `amdsmi_get_gpu_asic_info` API calls. The cache stores ASIC info for each GPU device to improve performance by avoiding redundant hardware queries.
  - Duration in milliseconds \
    Default: `10000`
* - `AMDSMI_GPU_METRICS_CACHE_MS` \
    Configures the cache duration for GPU metrics retrieved by GPU metrics API calls. The cache stores metrics for each GPU device to improve performance by avoiding redundant hardware queries.
  - Duration in milliseconds \
    Default: `1`
```

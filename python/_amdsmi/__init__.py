# Copyright (c) Advanced Micro Devices, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

"""
Runtime selection module for AMDSMI.

This module provides runtime selection between different variants of the
AMDSMI library (e.g., default vs instrumented builds).
"""

import os
import sys

def _get_runtime_variant():
    """Get the runtime variant to use based on environment variables."""
    variant = os.environ.get("AMDSMI_RUNTIME_VARIANT", "default")
    return variant

def _import_runtime():
    """Import and return the appropriate runtime variant."""
    variant = _get_runtime_variant()

    if variant == "default":
        try:
            from amdsmi import _amdsmi_impl
            return _amdsmi_impl
        except ImportError as e:
            raise ImportError(f"Failed to import default AMDSMI runtime: {e}")
    else:
        raise ValueError(f"Unsupported runtime variant: {variant}")

# Export the runtime
_runtime = _import_runtime()

# Re-export all symbols from the runtime
for name in dir(_runtime):
    if not name.startswith('_'):
        globals()[name] = getattr(_runtime, name)

__version__ = getattr(_runtime, '__version__', 'unknown')
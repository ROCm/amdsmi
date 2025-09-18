# Copyright (c) Advanced Micro Devices, Inc. All rights reserved.
#
# Auto-generated version file from version.json

import json
import os

# Read version from version.json in the root directory
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    version_file = os.path.join(root_dir, "version.json")

    with open(version_file, 'r') as f:
        version_data = json.load(f)
    __version__ = version_data['package-version']
except Exception:
    # Fallback version if file cannot be read
    __version__ = "26.1.0"
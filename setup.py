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

import json
import os
import shutil
import subprocess
import sys
import traceback
from distutils.command.build import build as _build
from distutils.core import setup, Extension
from pathlib import Path
from setuptools import find_namespace_packages
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.build_ext import build_ext as _build_ext


def get_env_boolean(name: str, default_value: bool = False) -> bool:
    svalue = os.getenv(name)
    if svalue is None:
        return default_value
    svalue = svalue.upper()
    if svalue in ["1", "ON", "TRUE"]:
        return True
    elif svalue in ["0", "OFF", "FALSE"]:
        return False
    else:
        print(f"WARNING: {name} env var cannot be interpreted as a boolean value")
        return default_value


def get_env_cmake_option(name: str, default_value: bool = False) -> str:
    svalue = os.getenv(name)
    if not svalue:
        svalue = "ON" if default_value else "OFF"
    return f"-D{name}={svalue}"


def add_env_cmake_setting(
    args, env_name: str, cmake_name=None, default_value=None
) -> str:
    svalue = os.getenv(env_name)
    if svalue is None and default_value is not None:
        svalue = default_value
    if svalue is not None:
        if not cmake_name:
            cmake_name = env_name
        args.append(f"-D{cmake_name}={svalue}")


class CMakeBuildPy(_build_py):
    def run(self):
        self.run_cmake_build()
        super().run()

    def run_cmake_build(self):
        source_dir = Path(__file__).parent.resolve()
        build_temp = Path(self.build_temp).resolve()
        build_temp.mkdir(parents=True, exist_ok=True)

        # Read version from version.json
        version_file = source_dir / "version.json"
        with open(version_file, 'r') as f:
            version_data = json.load(f)
        version_string = version_data['package-version']

        cfg = os.environ.get("AMDSMI_CMAKE_BUILD_TYPE", "Release")
        is_debug = cfg == "Debug"

        cmake_args = [
            f"-DCMAKE_BUILD_TYPE={cfg}",
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={build_temp}",
            f"-DAMDSMI_BUILD_PYTHON_BINDINGS=ON",
            f"-DAMDSMI_BUILD_SHARED_LIBS=ON",
            f"-DAMDSMI_BUILD_TESTS=OFF",
        ]

        # Add environment-controlled settings
        add_env_cmake_setting(cmake_args, "CMAKE_C_COMPILER")
        add_env_cmake_setting(cmake_args, "CMAKE_CXX_COMPILER")
        add_env_cmake_setting(cmake_args, "CMAKE_VERBOSE_MAKEFILE")

        # Development mode settings
        if get_env_boolean("AMDSMI_DEV_MODE"):
            cmake_args.extend([
                "-DCMAKE_C_FLAGS=-O0 -g",
                "-DCMAKE_CXX_FLAGS=-O0 -g",
            ])

        # Use ninja if available
        generator = "Ninja" if shutil.which("ninja") else "Unix Makefiles"
        cmake_args.extend(["-G", generator])

        build_args = []
        if generator == "Unix Makefiles":
            # Use available cores for make
            cpu_count = os.cpu_count() or 1
            build_args.extend(["-j", str(cpu_count)])

        print(f"CMake build temp: {build_temp}")
        print(f"CMake source dir: {source_dir}")
        print(f"CMake args: {cmake_args}")

        # Configure
        subprocess.check_call(
            ["cmake", str(source_dir)] + cmake_args,
            cwd=build_temp
        )

        # Build
        subprocess.check_call(
            ["cmake", "--build", ".", "--config", cfg] + build_args,
            cwd=build_temp
        )

        # Find and copy the built Python package files
        python_build_dir = build_temp / "python"
        if python_build_dir.exists():
            for item in python_build_dir.rglob("*"):
                if item.is_file():
                    # Calculate relative path and copy to build directory
                    rel_path = item.relative_to(python_build_dir)
                    dest_path = Path(self.build_lib) / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_path)


class CMakeBuildExt(_build_ext):
    def run(self):
        # CMake extension building is handled by CMakeBuildPy
        pass


# Read version from version.json
def get_version():
    version_file = Path(__file__).parent / "version.json"
    with open(version_file, 'r') as f:
        version_data = json.load(f)
    return version_data['package-version']


# Setup configuration
setup(
    name="amdsmi",
    version=get_version(),
    author="AMD",
    author_email="amd-smi.support@amd.com",
    description="AMDSMI Python Library - AMD GPU Monitoring Library",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/ROCm/amdsmi",

    packages=find_namespace_packages(where="python"),
    package_dir={"": "python"},

    # Extension modules (will be built by CMake)
    ext_modules=[Extension("amdsmi._amdsmi_impl", [])],

    cmdclass={
        "build_py": CMakeBuildPy,
        "build_ext": CMakeBuildExt,
    },

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C++",
        "Topic :: System :: Hardware",
        "Topic :: System :: Monitoring",
    ],

    python_requires=">=3.8",

    # Runtime dependencies
    install_requires=[
        "nanobind>=2.0.0",
    ],

    # Development dependencies
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
        ],
        "test": [
            "pytest",
            "pytest-cov",
        ],
    },

    zip_safe=False,
    include_package_data=True,
)
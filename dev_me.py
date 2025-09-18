#!/usr/bin/env python3
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
Development script for AMDSMI.

This script provides an opinionated development environment setup for building
and testing AMDSMI. It automates common development tasks and provides
sensible defaults for fast iteration.
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def get_version():
    """Get version from version.json."""
    version_file = Path(__file__).parent / "version.json"
    with open(version_file, 'r') as f:
        version_data = json.load(f)
    return version_data['package-version']


def run_command(cmd, *, cwd=None, env=None, check=True):
    """Run a command with nice error handling."""
    print(f"+ {' '.join(cmd)}")
    if env:
        run_env = os.environ.copy()
        run_env.update(env)
        env = run_env

    try:
        result = subprocess.run(cmd, cwd=cwd, env=env, check=check)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        raise


def find_cmake():
    """Find CMake executable."""
    cmake = shutil.which("cmake")
    if not cmake:
        print("ERROR: cmake not found. Please install CMake 3.29+")
        sys.exit(1)

    # Check version
    try:
        result = subprocess.run([cmake, "--version"], capture_output=True, text=True)
        version_line = result.stdout.split('\n')[0]
        # Extract version number
        import re
        match = re.search(r'cmake version (\d+)\.(\d+)', version_line)
        if match:
            major, minor = int(match.group(1)), int(match.group(2))
            if major < 3 or (major == 3 and minor < 29):
                print(f"WARNING: CMake {major}.{minor} found, but 3.29+ recommended")
    except Exception:
        print("WARNING: Could not check CMake version")

    return cmake


def setup_build_dir(build_dir: Path, source_dir: Path):
    """Setup build directory."""
    if build_dir.exists():
        print(f"Build directory exists: {build_dir}")
    else:
        print(f"Creating build directory: {build_dir}")
        build_dir.mkdir(parents=True)


def detect_compiler():
    """Detect preferred compiler."""
    # Prefer clang/clang++ if available
    if shutil.which("clang") and shutil.which("clang++"):
        return "clang", "clang++"
    elif shutil.which("gcc") and shutil.which("g++"):
        return "gcc", "g++"
    else:
        return None, None


def cmake_configure(source_dir: Path, build_dir: Path, args):
    """Configure CMake build."""
    cmake = find_cmake()

    cmake_args = [
        cmake,
        str(source_dir),
        f"-DCMAKE_BUILD_TYPE={args.build_type}",
        f"-DAMDSMI_BUILD_SHARED_LIBS={'ON' if args.shared else 'OFF'}",
        f"-DAMDSMI_BUILD_STATIC_LIBS={'ON' if args.static else 'OFF'}",
        f"-DAMDSMI_BUILD_PYTHON_BINDINGS={'ON' if args.python else 'OFF'}",
        f"-DAMDSMI_BUILD_TESTS={'ON' if args.tests else 'OFF'}",
    ]

    # Compiler selection
    cc, cxx = detect_compiler()
    if cc and cxx and not args.system_compiler:
        cmake_args.extend([
            f"-DCMAKE_C_COMPILER={cc}",
            f"-DCMAKE_CXX_COMPILER={cxx}",
        ])
        print(f"Using compilers: {cc}, {cxx}")

    # Generator selection
    if args.ninja and shutil.which("ninja"):
        cmake_args.extend(["-G", "Ninja"])
        print("Using Ninja generator")
    elif platform.system() == "Windows":
        cmake_args.extend(["-G", "Visual Studio 17 2022"])
    else:
        cmake_args.extend(["-G", "Unix Makefiles"])

    # Development flags
    if args.dev:
        cmake_args.extend([
            "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
            "-DCMAKE_VERBOSE_MAKEFILE=ON",
        ])
        if args.build_type == "Debug":
            cmake_args.extend([
                "-DCMAKE_C_FLAGS=-O0 -g -fno-omit-frame-pointer",
                "-DCMAKE_CXX_FLAGS=-O0 -g -fno-omit-frame-pointer",
            ])

    # Address sanitizer
    if args.asan:
        cmake_args.extend([
            "-DCMAKE_C_FLAGS=-fsanitize=address -fno-omit-frame-pointer",
            "-DCMAKE_CXX_FLAGS=-fsanitize=address -fno-omit-frame-pointer",
            "-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address",
            "-DCMAKE_SHARED_LINKER_FLAGS=-fsanitize=address",
        ])

    print(f"Configuring with: {' '.join(cmake_args)}")
    run_command(cmake_args, cwd=build_dir)


def cmake_build(build_dir: Path, args):
    """Build with CMake."""
    cmake = find_cmake()

    build_args = [cmake, "--build", ".", "--config", args.build_type]

    # Parallel building
    if args.jobs:
        build_args.extend(["--parallel", str(args.jobs)])
    elif not args.ninja:  # ninja auto-detects
        import multiprocessing
        jobs = multiprocessing.cpu_count()
        build_args.extend(["--parallel", str(jobs)])

    if args.verbose:
        build_args.append("--verbose")

    print(f"Building with: {' '.join(build_args)}")
    run_command(build_args, cwd=build_dir)


def install_python_package(source_dir: Path, args):
    """Install Python package in development mode."""
    if not args.python:
        return

    python = sys.executable
    env = {
        "AMDSMI_CMAKE_BUILD_TYPE": args.build_type,
        "AMDSMI_DEV_MODE": "1" if args.dev else "0",
    }

    if args.editable:
        cmd = [python, "-m", "pip", "install", "-e", "."]
    else:
        cmd = [python, "-m", "pip", "install", "."]

    if args.verbose:
        cmd.append("-v")

    print("Installing Python package...")
    run_command(cmd, cwd=source_dir, env=env)


def run_tests(build_dir: Path, args):
    """Run tests."""
    if not args.tests:
        return

    print("Running C++ tests...")
    ctest_cmd = ["ctest", "--output-on-failure"]
    if args.verbose:
        ctest_cmd.append("--verbose")
    if args.jobs:
        ctest_cmd.extend(["-j", str(args.jobs)])

    try:
        run_command(ctest_cmd, cwd=build_dir)
    except subprocess.CalledProcessError:
        print("Some C++ tests failed")

    # Python tests
    if args.python:
        python = sys.executable
        pytest_cmd = [python, "-m", "pytest", "tests/python/"]
        if args.verbose:
            pytest_cmd.append("-v")

        try:
            run_command(pytest_cmd, cwd=build_dir.parent)
        except subprocess.CalledProcessError:
            print("Some Python tests failed")


def main():
    parser = argparse.ArgumentParser(
        description="AMDSMI development build script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick development build
  ./dev_me.py

  # Debug build with tests
  ./dev_me.py --build-type Debug --tests

  # Release build with Python package
  ./dev_me.py --build-type Release --python --install

  # Clean rebuild
  ./dev_me.py --clean --tests --python
        """
    )

    # Build options
    parser.add_argument("--build-type", choices=["Debug", "Release", "RelWithDebInfo"],
                       default="Debug", help="CMake build type")
    parser.add_argument("--build-dir", type=Path, default="build-dev",
                       help="Build directory")
    parser.add_argument("--clean", action="store_true",
                       help="Clean build directory before building")

    # Component options
    parser.add_argument("--shared", action="store_true", default=True,
                       help="Build shared library")
    parser.add_argument("--static", action="store_true", default=False,
                       help="Build static library")
    parser.add_argument("--python", action="store_true", default=True,
                       help="Build Python bindings")
    parser.add_argument("--tests", action="store_true", default=False,
                       help="Build and run tests")

    # Build tools
    parser.add_argument("--ninja", action="store_true", default=True,
                       help="Use Ninja generator if available")
    parser.add_argument("--system-compiler", action="store_true", default=False,
                       help="Use system default compiler")
    parser.add_argument("--jobs", "-j", type=int,
                       help="Number of parallel build jobs")

    # Development options
    parser.add_argument("--dev", action="store_true", default=True,
                       help="Development mode (export compile commands, etc.)")
    parser.add_argument("--asan", action="store_true", default=False,
                       help="Enable AddressSanitizer")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")

    # Python options
    parser.add_argument("--install", action="store_true", default=False,
                       help="Install Python package")
    parser.add_argument("--editable", "-e", action="store_true", default=True,
                       help="Install Python package in editable mode")

    # Actions
    parser.add_argument("--configure-only", action="store_true",
                       help="Only configure, don't build")
    parser.add_argument("--version", action="version", version=f"AMDSMI {get_version()}")

    args = parser.parse_args()

    source_dir = Path(__file__).parent.resolve()
    build_dir = source_dir / args.build_dir

    print(f"AMDSMI Development Build Script")
    print(f"Source: {source_dir}")
    print(f"Build:  {build_dir}")
    print(f"Type:   {args.build_type}")
    print()

    # Clean if requested
    if args.clean and build_dir.exists():
        print(f"Cleaning build directory: {build_dir}")
        shutil.rmtree(build_dir)

    # Setup and configure
    setup_build_dir(build_dir, source_dir)
    cmake_configure(source_dir, build_dir, args)

    if args.configure_only:
        print("Configuration complete (--configure-only specified)")
        return

    # Build
    cmake_build(build_dir, args)

    # Install Python package
    if args.install:
        install_python_package(source_dir, args)

    # Run tests
    if args.tests:
        run_tests(build_dir, args)

    print("\nBuild complete!")
    print(f"Build artifacts in: {build_dir}")

    if args.python and not args.install:
        print("\nTo install Python package:")
        print(f"  cd {source_dir}")
        print("  pip install -e .")


if __name__ == "__main__":
    main()
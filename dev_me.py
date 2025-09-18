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


class EnvInfo:
    """Environment information and validation like shortfin."""

    def __init__(self, args):
        self.cmake = self.find_cmake_and_validate()
        self.python = self.find_python_and_validate()
        self.compiler = self.find_compiler_and_validate(args)
        self.validate_dependencies()

    def find_cmake_and_validate(self):
        """Find CMake executable and validate version."""
        cmake = shutil.which("cmake")
        if not cmake:
            print("ERROR: cmake not found. Please install CMake 3.25+")
            print("  Ubuntu/Debian: sudo apt-get install cmake")
            print("  RHEL/Fedora: sudo yum install cmake")
            sys.exit(1)

        # Check version
        try:
            result = subprocess.run([cmake, "--version"], capture_output=True, text=True)
            version_line = result.stdout.split('\n')[0]
            # Extract version number
            import re
            match = re.search(r'cmake version (\d+)\.(\d+)\.(\d+)', version_line)
            if match:
                major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
                print(f"✓ Found CMake {major}.{minor}.{patch}")
                if major < 3 or (major == 3 and minor < 25):
                    print(f"ERROR: CMake {major}.{minor}.{patch} is too old. Need 3.25+")
                    sys.exit(1)
                elif major == 3 and minor < 29:
                    print(f"  WARNING: CMake 3.29+ recommended for full feature support")
        except Exception as e:
            print(f"WARNING: Could not check CMake version: {e}")

        return cmake

    def find_python_and_validate(self):
        """Find Python and validate version."""
        python = sys.executable
        version = sys.version_info
        print(f"✓ Found Python {version.major}.{version.minor}.{version.micro}")

        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"ERROR: Python {version.major}.{version.minor} is too old. Need 3.8+")
            sys.exit(1)

        return python

    def find_compiler_and_validate(self, args):
        """Find and validate compiler."""
        if args.system_compiler:
            print("✓ Using system default compiler")
            return None, None

        # Prefer clang/clang++ if available
        cc, cxx = None, None
        if shutil.which("clang") and shutil.which("clang++"):
            cc, cxx = "clang", "clang++"
            # Check clang version
            try:
                result = subprocess.run([cc, "--version"], capture_output=True, text=True)
                version_line = result.stdout.split('\n')[0]
                import re
                match = re.search(r'clang version (\d+)', version_line)
                if match:
                    version = int(match.group(1))
                    print(f"✓ Found Clang {version}")
            except Exception:
                print("✓ Found Clang (version unknown)")
        elif shutil.which("gcc") and shutil.which("g++"):
            cc, cxx = "gcc", "g++"
            # Check gcc version
            try:
                result = subprocess.run([cc, "--version"], capture_output=True, text=True)
                version_line = result.stdout.split('\n')[0]
                import re
                match = re.search(r'gcc.*?(\d+)\.(\d+)', version_line)
                if match:
                    major, minor = int(match.group(1)), int(match.group(2))
                    print(f"✓ Found GCC {major}.{minor}")
            except Exception:
                print("✓ Found GCC (version unknown)")
        else:
            print("WARNING: No C/C++ compiler found (clang or gcc)")
            print("  The build will use CMake's default compiler detection")

        return cc, cxx

    def validate_dependencies(self):
        """Validate required dependencies."""
        print("\nChecking dependencies:")

        # Check for libdrm
        if shutil.which("pkg-config"):
            result = subprocess.run(
                ["pkg-config", "--exists", "libdrm"],
                capture_output=True
            )
            if result.returncode == 0:
                print("✓ Found libdrm")
            else:
                print("WARNING: libdrm not found. GPU functionality may be limited")
                print("  Ubuntu/Debian: sudo apt-get install libdrm-dev")
                print("  RHEL/Fedora: sudo yum install libdrm-devel")

        # Check for pthread
        print("✓ pthread support (standard on Linux)")

        # Check for nanobind
        try:
            import nanobind
            print(f"✓ Found nanobind {nanobind.__version__}")
        except ImportError:
            print("✓ nanobind will be installed during build")

        print()


def find_cmake():
    """Find CMake executable (legacy function for compatibility)."""
    cmake = shutil.which("cmake")
    if not cmake:
        print("ERROR: cmake not found. Please install CMake 3.25+")
        sys.exit(1)
    return cmake


def setup_build_dir(build_dir: Path, source_dir: Path):
    """Setup build directory."""
    if build_dir.exists():
        print(f"Build directory exists: {build_dir}")
    else:
        print(f"Creating build directory: {build_dir}")
        build_dir.mkdir(parents=True)




def cmake_configure(source_dir: Path, build_dir: Path, args, cc=None, cxx=None):
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

    print(f"{'='*60}")
    print(f"AMDSMI Development Build Script v{get_version()}")
    print(f"{'='*60}")
    print(f"Source: {source_dir}")
    print(f"Build:  {build_dir}")
    print(f"Type:   {args.build_type}")
    print(f"{'='*60}\n")

    # Validate environment (shortfin-style)
    env_info = EnvInfo(args)
    cc, cxx = env_info.compiler

    # Clean if requested
    if args.clean and build_dir.exists():
        print(f"Cleaning build directory: {build_dir}")
        shutil.rmtree(build_dir)

    # Setup and configure
    setup_build_dir(build_dir, source_dir)
    cmake_configure(source_dir, build_dir, args, cc, cxx)

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
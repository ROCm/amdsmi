from setuptools import setup, find_packages
from _version import __version__

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='amdsmi',
    version=__version__,
    description="SMI LIB - AMD GPU Monitoring Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(), # can be customized later, but works for now
    package_data={'': ['LICENSE']},
    include_package_data=True,
    python_requires=">=3.6",
)

# To build wheel
# python3 -m pip install -U wheel
# python3 setup.py bdist_wheel
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import subprocess

import urllib
from rocm_docs import ROCmDocs

esmi_readme_link = "https://raw.githubusercontent.com/amd/esmi_ib_library/master/docs/README.md"
try:
    # Try to override esmi_lib_readme_link.md with the github esmi readme contents
    with urllib.request.urlopen(esmi_readme_link) as f:
        esmi_readme = f.read().decode('utf-8')

    with open("./esmi_lib_readme_link.md", "w", encoding='utf-8') as f:
        f.write(esmi_readme)
except urllib.error.URLError:
    # don't care about the error because there is backup link in the file already
    pass

get_version_year = r'sed -n -e "s/^#define\ AMDSMI_LIB_VERSION_YEAR\ //p" ../include/amd_smi/amdsmi.h'
get_version_major = r'sed -n -e "s/^#define\ AMDSMI_LIB_VERSION_MAJOR\ //p" ../include/amd_smi/amdsmi.h'
get_version_minor = r'sed -n -e "s/^#define\ AMDSMI_LIB_VERSION_MINOR\ //p" ../include/amd_smi/amdsmi.h'
get_version_release = r'sed -n -e "s/^#define\ AMDSMI_LIB_VERSION_RELEASE\ //p" ../include/amd_smi/amdsmi.h'
version_year = subprocess.getoutput(get_version_year)
version_major = subprocess.getoutput(get_version_major)
version_minor = subprocess.getoutput(get_version_minor)
version_release = subprocess.getoutput(get_version_release)
name = f"AMD SMI {version_year}.{version_major}.{version_minor}.{version_release}"

external_toc_path = "./sphinx/_toc.yml"

docs_core = ROCmDocs(f"{name} Documentation")
docs_core.run_doxygen(doxygen_root="doxygen", doxygen_path="doxygen/docBin/xml")
docs_core.enable_api_reference()
docs_core.setup()

for sphinx_var in ROCmDocs.SPHINX_VARS:
    globals()[sphinx_var] = getattr(docs_core, sphinx_var)

# CMake script to configure __init__.py.in template at build time
# This script is called from the custom command in CMakeLists.txt

# Set CMake policy to use new evaluation rules
cmake_policy(SET CMP0053 NEW)

# Read the input template file
file(READ ${INPUT_FILE} TEMPLATE_CONTENT)

# Replace the @BRCM_SMI_IMPORT@ placeholder with the actual value
# Remove escaped backslashes from the BRCM_SMI_IMPORT variable
string(REPLACE "\\ " " " CLEAN_BRCM_SMI_IMPORT "${BRCM_SMI_IMPORT}")
string(REPLACE "@BRCM_SMI_IMPORT@" "${CLEAN_BRCM_SMI_IMPORT}" CONFIGURED_CONTENT "${TEMPLATE_CONTENT}")

# Write the configured content to the output file
file(WRITE ${OUTPUT_FILE} "${CONFIGURED_CONTENT}")

message(STATUS "Configured __init__.py with BRCM_SMI_IMPORT: ${BRCM_SMI_IMPORT}")

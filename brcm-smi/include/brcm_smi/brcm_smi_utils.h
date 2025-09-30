/*
 * Copyright (c) Advanced Micro Devices, Inc. All rights reserved.
 *
 *  Developed by:
 *            Broadcom Inc
 *
 *            www.broadcom.com
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */


#ifndef BRCM_SMI_INCLUDE_BRCM_SMI_UTILS_H_
#define BRCM_SMI_INCLUDE_BRCM_SMI_UTILS_H_

#include <string>
#include <cstdint>

namespace brcm {
namespace smi {

/**
 * @brief Construct BDF ID from device path
 * 
 * @param path Device path in sysfs
 * @param bdfid Pointer to store the constructed BDF ID
 * @return uint32_t 0 on success, 1 on failure
 */
uint32_t ConstructBDFID(const std::string& path, uint64_t* bdfid);

/**
 * @brief Extract BDF ID from path string
 * 
 * @param path_str Path string containing BDF information
 * @param bdfid Pointer to store the extracted BDF ID
 * @return bool true if BDF ID was successfully extracted
 */
bool bdfid_from_path(const std::string& path_str, uint64_t* bdfid);

/**
 * @brief Print integer as hexadecimal string
 * 
 * @param val Value to print
 * @param prefix Whether to include "0x" prefix
 * @param width Minimum width of the output
 * @return std::string Hexadecimal representation
 */
std::string print_int_as_hex(uint64_t val, bool prefix = true, int width = 0);

}  // namespace smi
}  // namespace brcm

#endif  // BRCM_SMI_INCLUDE_BRCM_SMI_UTILS_H_

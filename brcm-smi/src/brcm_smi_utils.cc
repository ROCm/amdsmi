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


#include "brcm_smi/brcm_smi_utils.h"
#include "brcm_smi/impl/brcm_smi_utils.h"
#include <cstring>
#include <cerrno>
#include <cassert>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <fstream>
#include <vector>
#include <mutex>
#include <pthread.h>
#include <cstdio>

// Platform-specific includes
#ifdef _WIN32
    #include <io.h>
    #include <windows.h>
#else
    #include <unistd.h>
#endif

namespace brcm {
namespace smi {

bool bdfid_from_path(const std::string& in_name, uint64_t* bdfid) {
    char* p = nullptr;
    char* name_start;
    char name[13] = {'\0'};
    uint64_t tmp;

    assert(bdfid != nullptr);

    if (in_name.size() != 12) {
        return false;
    }

    tmp = in_name.copy(name, 12);
    assert(tmp == 12);

    // BDFID = ((<DOMAIN> & 0xffff) << 32) | ((<BUS> & 0xff) << 8) |
    //                        ((device& 0x1f) <<3 ) | (function & 0x7)
    *bdfid = 0;
    name_start = name;
    p = name_start;

    // Match this: XXXX:xx:xx.x
    tmp = std::strtoul(p, &p, 16);
    if (*p != ':' || p - name_start != 4) {
        return false;
    }
    *bdfid |= tmp << 32;

    // Match this: xxxx:XX:xx.x
    p++;  // Skip past ':'
    tmp = std::strtoul(p, &p, 16);
    if (*p != ':' || p - name_start != 7) {
        return false;
    }
    *bdfid |= tmp << 8;

    // Match this: xxxx:xx:XX.x
    p++;  // Skip past ':'
    tmp = std::strtoul(p, &p, 16);
    if (*p != '.' || p - name_start != 10) {
        return false;
    }
    *bdfid |= tmp << 3;

    // Match this: xxxx:xx:xx.X
    p++;  // Skip past '.'
    tmp = std::strtoul(p, &p, 16);
    if (*p != '\0' || p - name_start != 12) {
        return false;
    }
    *bdfid |= tmp;

    return true;
}

uint32_t ConstructBDFID(const std::string& path, uint64_t* bdfid) {
    assert(bdfid != nullptr);
    const unsigned int MAX_BDF_LENGTH = 512;
    char tpath[MAX_BDF_LENGTH] = {'\0'};
    ssize_t ret;
    memset(tpath, 0, MAX_BDF_LENGTH);

    ret = readlink(path.c_str(), tpath, MAX_BDF_LENGTH);

    if (ret <= 0 || ret >= MAX_BDF_LENGTH) {
        std::cerr << "ConstructBDFID: readlink failed for path = " << path 
                  << " | ret = " << ret << " | errno = " << errno 
                  << " | error = " << strerror(errno) << std::endl;
        return 1;
    }

    // We are looking for the last element in the path that has the form
    //  XXXX:XX:XX.X, where X is a hex integer (lower case is expected)
    std::size_t slash_i;
    std::size_t end_i;
    std::string tmp;

    std::string tpath_str(tpath);

    end_i = tpath_str.size() - 1;
    while (end_i > 0) {
        slash_i = tpath_str.find_last_of('/', end_i);
        tmp = tpath_str.substr(slash_i + 1, end_i - slash_i);

        if (bdfid_from_path(tmp, bdfid)) {
            //std::cout << "ConstructBDFID: Found bdfid = " 
                      //<< print_int_as_hex(*bdfid, true, 8) << " | from path = "
                      //<< path << " | tmp = " << tmp << std::endl;
            return 0;
        }
        end_i = slash_i - 1;
    }
    
    std::cerr << "ConstructBDFID: No valid bdfid found in path = " << path 
              << " | tpath = " << tpath << " | errno = " << errno 
              << " | error = " << strerror(errno) << std::endl;
    return 1;
}

std::string print_int_as_hex(uint64_t val, bool prefix, int width) {
    std::stringstream ss;
    if (prefix) {
        if (width == 0) {
            ss << "0x" << std::hex << std::setw(sizeof(uint64_t) * 2) << std::setfill('0');
        } else {
            // 8 bits per 1 byte
            int byteSize = (width / 8) * 2;
            ss << "0x" << std::hex << std::setw(byteSize) << std::setfill('0');
        }
    } else {
        if (width == 0) {
            ss << std::hex << std::setw(sizeof(uint64_t) * 2) << std::setfill('0');
        } else {
            int byteSize = (width / 8) * 2;
            ss << std::hex << std::setw(byteSize) << std::setfill('0');
        }
    }

    ss << static_cast<unsigned long long int>(val | 0);
    return ss.str();
}

// Global mutex storage for device synchronization
static std::vector<pthread_mutex_t> g_device_mutexes;
static std::mutex g_mutex_map_lock;

pthread_mutex_t* GetMutex(uint32_t device_id) {
    std::lock_guard<std::mutex> lock(g_mutex_map_lock);
    
    // Ensure we have enough mutexes
    while (g_device_mutexes.size() <= device_id) {
        pthread_mutex_t new_mutex;
        pthread_mutexattr_t attr;
        pthread_mutexattr_init(&attr);
        pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_RECURSIVE);
        pthread_mutex_init(&new_mutex, &attr);
        pthread_mutexattr_destroy(&attr);
        g_device_mutexes.push_back(new_mutex);
    }
    
    return &g_device_mutexes[device_id];
}

std::string smi_brcm_get_value_string(std::string filePath, std::string fileName) {
    std::string fullPath = filePath + "/" + fileName;
    std::ifstream file(fullPath);
    
    if (!file.is_open()) {
        if (errno == ENOENT) {
            // File doesn't exist, return empty string
            return "";
        }
        std::cerr << "Error opening file: " << fullPath << " - " << strerror(errno) << std::endl;
        return "";
    }
    
    std::string content;
    std::string line;
    
    // Read the first line and trim whitespace
    if (std::getline(file, line)) {
        // Remove trailing whitespace and newlines
        size_t end = line.find_last_not_of(" \t\r\n");
        if (end != std::string::npos) {
            content = line.substr(0, end + 1);
        } else {
            content = "";
        }
    }
    
    file.close();
    return content;
}

uint32_t smi_brcm_get_value_u32(std::string filePath, std::string fileName) {
    std::string value_str = smi_brcm_get_value_string(filePath, fileName);
    
    if (value_str.empty()) {
        return 0;
    }
    
    try {
        // Handle hexadecimal values
        if (value_str.substr(0, 2) == "0x" || value_str.substr(0, 2) == "0X") {
            return static_cast<uint32_t>(std::stoul(value_str, nullptr, 16));
        } else {
            return static_cast<uint32_t>(std::stoul(value_str, nullptr, 10));
        }
    } catch (const std::exception& e) {
        std::cerr << "Error converting string to uint32_t: " << value_str 
                  << " - " << e.what() << std::endl;
        return 0;
    }
}

brcmsmi_status_t smi_brcm_execute_cmd_get_data(std::string command, std::string *data) {
    if (data == nullptr) {
        return BRCMSMI_STATUS_INVALID_ARGS;
    }
    
    // Execute command and capture output
    FILE* pipe = popen(command.c_str(), "r");
    if (!pipe) {
        std::cerr << "Error executing command: " << command << " - " << strerror(errno) << std::endl;
        return BRCMSMI_STATUS_FILE_ERROR;
    }
    
    char buffer[4096];
    std::string result;
    
    while (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
        result += buffer;
    }
    
    int status = pclose(pipe);
    if (status != 0) {
        // Handle common expected failures gracefully
        int exit_code = WEXITSTATUS(status);
        if (exit_code == 1) {
            // Exit code 1 is common for grep when no matches found - this is expected
            // Return success but with empty result (already handled by caller)
            *data = result;
            return BRCMSMI_STATUS_SUCCESS;
        } else {
            // Actual command execution failures  
            std::cerr << "Command execution failed: " << command 
                      << " | exit code: " << exit_code 
                      << " | status: " << status << std::endl;
            return BRCMSMI_STATUS_FILE_ERROR;
        }
    }
    
    *data = result;
    return BRCMSMI_STATUS_SUCCESS;
}

}  // namespace smi
}  // namespace brcm
/*
 * =============================================================================
 * The University of Illinois/NCSA
 * Open Source License (NCSA)
 *
 * Copyright (c) 2018-2023, Advanced Micro Devices, Inc.
 * All rights reserved.
 *
 * Developed by:
 *
 *                 AMD Research and AMD ROC Software Development
 *
 *                 Advanced Micro Devices, Inc.
 *
 *                 www.amd.com
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal with the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 *  - Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimers.
 *  - Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimers in
 *    the documentation and/or other materials provided with the distribution.
 *  - Neither the names of <Name of Development Group, Name of Institution>,
 *    nor the names of its contributors may be used to endorse or promote
 *    products derived from this Software without specific prior written
 *    permission.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
 * OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 * ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS WITH THE SOFTWARE.
 *
 */
#include <assert.h>
#include <errno.h>
#include <sys/stat.h>
#include <unistd.h>
#include <dirent.h>
#include <glob.h>
#include <sys/utsname.h>

#include <fstream>
#include <string>
#include <cstring>
#include <cstdint>
#include <iostream>
#include <sstream>
#include <algorithm>
#include <vector>
#include <regex>

#include "rocm_smi/rocm_smi.h"
#include "rocm_smi/rocm_smi_utils.h"
#include "rocm_smi/rocm_smi_exception.h"
#include "rocm_smi/rocm_smi_main.h"
#include "rocm_smi/rocm_smi_device.h"
#include "rocm_smi/rocm_smi_logger.h"

using namespace ROCmLogging;

namespace amd {
namespace smi {
const std::string kTmpFilePrefix = "rocmsmi_";

// Return 0 if same file, 1 if not, and -1 for error
int SameFile(const std::string fileA, const std::string fileB) {
  struct stat aStat;
  struct stat bStat;
  int ret;

  ret = stat(fileA.c_str(), &aStat);
  if (ret) {
      return -1;
  }

  ret = stat(fileB.c_str(), &bStat);
  if (ret) {
      return -1;
  }

  if (aStat.st_dev != bStat.st_dev) {
      return 1;
  }

  if (aStat.st_ino != bStat.st_ino) {
      return 1;
  }

  return 0;
}

bool FileExists(char const *filename) {
  struct stat buf;
  return (stat(filename, &buf) == 0);
}

static void debugFilesDiscovered(std::vector<std::string> files) {
  std::ostringstream ss;
  int numberOfFilesFound = static_cast<int>(files.size());
  ss << "fileName.size() = " << numberOfFilesFound
     << "; Files discovered = {";
  if(numberOfFilesFound > 0) {
    for (auto it = begin(files); it != end(files); ++it) {
      auto nextElement = std::next(it);
      if (nextElement != files.end()) {
        ss << *it << ", ";
      } else {
        ss << *it;
      }
    }
  } else {
    ss << "<none>";
  }
  ss << "}";
  LOG_DEBUG(ss);
}

// Input: string filePattern = can put in * file searches (see example)
// example: globFilesExist("/etc/*release")
// Return a vector containing file paths that matched
// You can obtain if files exist by doing globFilesExist(...).size() > 0
std::vector<std::string> globFilesExist(const std::string& filePattern) {
  std::ostringstream ss;
  std::vector<std::string> fileNames;
  glob_t result_glob;
  memset(&result_glob, 0, sizeof(result_glob));

  if (glob(filePattern.c_str(), GLOB_TILDE, NULL, &result_glob) != 0) {
    globfree(&result_glob);
    // Leaving below to help debug issues discovering future glob file searches
    // debugFilesDiscovered(fileNames);
    return fileNames;
  }

  for(size_t i = 0; i < result_glob.gl_pathc; ++i) {
    fileNames.push_back(std::string(result_glob.gl_pathv[i]));
  }
  globfree(&result_glob);

  // Leaving below to help debug issues discovering future glob file searches
  // debugFilesDiscovered(fileNames);
  return fileNames;
}

int isRegularFile(std::string fname, bool *is_reg) {
  struct stat file_stat;
  int ret;

  assert(is_reg != nullptr);

  ret = stat(fname.c_str(), &file_stat);
  if (ret) {
    return errno;
  }
  *is_reg = S_ISREG(file_stat.st_mode);
  return 0;
}

int WriteSysfsStr(std::string path, std::string val) {
  std::ofstream fs;
  int ret = 0;
  std::ostringstream ss;

  fs.open(path);
  if (!fs.is_open()) {
    ret = errno;
    errno = 0;
    ss << "Could not write/open SYSFS file (" << path << ") string = " << val
       << ", returning " << std::to_string(ret) << " ("
       << std::strerror(ret) << ")";
    LOG_ERROR(ss);
    return ret;
  }

  fs << val;
  fs.close();
  if (!fs) {
    return ENOENT;  // Map to NOT_SUPPORT if errors
  }
  ss << "Successfully wrote to SYSFS file (" << path << ") string = " << val;
  LOG_INFO(ss);
  return ret;
}

int ReadSysfsStr(std::string path, std::string *retStr) {
  std::stringstream ss;
  int ret = 0;
  std::ostringstream oss;

  assert(retStr != nullptr);

  std::ifstream fs;
  fs.open(path);

  if (!fs.is_open()) {
    ret = errno;
    errno = 0;
    oss << "Could not read SYSFS file (" << path << ")"
        << ", returning " << std::to_string(ret) << " ("
        << std::strerror(ret) << ")";
    LOG_ERROR(oss);
    return ret;
  }
  ss << fs.rdbuf();
  fs.close();

  *retStr = ss.str();

  retStr->erase(std::remove(retStr->begin(), retStr->end(), '\n'),
                                                               retStr->end());
  oss << "Successfully read SYSFS file (" << path << ")"
      << ", returning str = " << *retStr;
  LOG_INFO(oss);
  return ret;
}

bool IsInteger(const std::string & n_str) {
  if (n_str.empty() || ((!isdigit(n_str[0])) && (n_str[0] != '-')
                                                      && (n_str[0] != '+'))) {
    return false;
  }

  char * tmp;
  strtol(n_str.c_str(), &tmp, 10);

  return (*tmp == 0);
}

rsmi_status_t handleException() {
  try {
    throw;
  } catch (const std::bad_alloc& e) {
    debug_print("RSMI exception: BadAlloc\n");
    return RSMI_STATUS_OUT_OF_RESOURCES;
  } catch (const amd::smi::rsmi_exception& e) {
    debug_print("Exception caught: %s.\n", e.what());
    return e.error_code();
  } catch (const std::exception& e) {
    debug_print("Exception caught: %s\n", e.what());
    return RSMI_STATUS_INTERNAL_EXCEPTION;
  } catch (const std::nested_exception& e) {
    debug_print("Callback threw.\n");
    return RSMI_STATUS_INTERNAL_EXCEPTION;
  } catch (...) {
    debug_print("Unknown exception caught.\n");
    return RSMI_STATUS_INTERNAL_EXCEPTION;
  }
}

pthread_mutex_t *GetMutex(uint32_t dv_ind) {
  amd::smi::RocmSMI& smi = amd::smi::RocmSMI::getInstance();

  if (dv_ind >= smi.devices().size()) {
    return nullptr;
  }
  std::shared_ptr<amd::smi::Device> dev = smi.devices()[dv_ind];
  assert(dev != nullptr);

  return dev->mutex();
}

rsmi_status_t GetDevValueVec(amd::smi::DevInfoTypes type,
                         uint32_t dv_ind, std::vector<std::string> *val_vec) {
  assert(val_vec != nullptr);
  if (val_vec == nullptr) {
    return RSMI_STATUS_INVALID_ARGS;
  }
  GET_DEV_FROM_INDX

  int ret = dev->readDevInfo(type, val_vec);
  return ErrnoToRsmiStatus(ret);
}

rsmi_status_t
GetDevBinaryBlob(amd::smi::DevInfoTypes type,
  uint32_t dv_ind, std::size_t b_size, void* p_binary_data) {
  assert(p_binary_data != nullptr);
  if (p_binary_data == nullptr) {
    return RSMI_STATUS_INVALID_ARGS;
  }
  GET_DEV_FROM_INDX

  int ret = dev->readDevInfo(type, b_size, p_binary_data);
  return ErrnoToRsmiStatus(ret);
}

rsmi_status_t ErrnoToRsmiStatus(int err) {
  switch (err) {
    case 0:      return RSMI_STATUS_SUCCESS;
    case ESRCH:  return RSMI_STATUS_NOT_FOUND;
    case EACCES: return RSMI_STATUS_PERMISSION;
    case EPERM:
    case ENOENT: return RSMI_STATUS_NOT_SUPPORTED;
    case EBADF:
    case EISDIR: return RSMI_STATUS_FILE_ERROR;
    case EINTR:  return RSMI_STATUS_INTERRUPT;
    case EIO:    return RSMI_STATUS_UNEXPECTED_SIZE;
    case ENXIO:  return RSMI_STATUS_UNEXPECTED_DATA;
    case EBUSY:  return RSMI_STATUS_BUSY;
    default:     return RSMI_STATUS_UNKNOWN_ERROR;
  }
}

bool is_vm_guest() {
  // the cpuinfo will set hypervisor flag in VM guest
  const std::string hypervisor = "hypervisor";
  std::string line;

  // default to false if cannot find the file
  std::ifstream infile("/proc/cpuinfo");
  if (infile.fail()) {
    return false;
  }

  while (std::getline(infile, line)) {
    if (line.find(hypervisor) != std::string::npos) {
      return true;
    }
  }
  return false;
}

std::string leftTrim(const std::string &s) {
  if (!s.empty()) {
    return std::regex_replace(s, std::regex("^\\s+"), "");
  }
  return s;
}

std::string rightTrim(const std::string &s) {
  if (!s.empty()) {
    return std::regex_replace(s, std::regex("\\s+$"), "");
  }
  return s;
}

std::string removeNewLines(const std::string &s) {
  if (!s.empty()) {
    return std::regex_replace(s, std::regex("\n+"), "");
  }
  return s;
}

std::string trim(const std::string &s) {
  if (!s.empty()) {
    // remove new lines -> trim white space at ends
    std::string noNewLines = removeNewLines(s);
    return leftTrim(rightTrim(noNewLines));
  }
  return s;
}

// Given original string and string to remove (removeMe)
// Return will provide the resulting modified string with the removed string(s)
std::string removeString(const std::string origStr,
                         const std::string &removeMe) {
  std::string modifiedStr = origStr;
  std::string::size_type l = removeMe.length();
  for (std::string::size_type i = modifiedStr.find(removeMe);
       i != std::string::npos;
       i = modifiedStr.find(removeMe)) {
    modifiedStr.erase(i, l);
  }
  return modifiedStr;
}

// defaults to trim stdOut
std::pair<bool, std::string> executeCommand(std::string command, bool stdOut) {
  char buffer[128];
  std::string stdoutAndErr = "";
  bool successfulRun = true;
  command = "stdbuf -i0 -o0 -e0 " + command; // remove stdOut and err buffering

  FILE *pipe = popen(command.c_str(), "r");
  if (!pipe) {
    stdoutAndErr = "[ERROR] popen failed to call " + command;
    successfulRun = false;
  } else {
    //read until end of process
    while (!feof(pipe)) {
      // use buffer to read and add to stdoutAndErr
      if (fgets(buffer, sizeof(buffer), pipe) != nullptr) {
        stdoutAndErr += buffer;
      }
    }
  }

  // any return code other than 0, is a failed execution
  if (pclose(pipe) != 0) {
    successfulRun = false;
  }

  if (stdOut) {
    // remove leading and trailing spaces of output and new lines
    stdoutAndErr = trim(stdoutAndErr);
  }
  return std::make_pair(successfulRun, stdoutAndErr);
}

// originalstring - string to search for substring
// substring - string looking to find
bool containsString(std::string originalString, std::string substring) {
  if (originalString.find(substring) != std::string::npos) {
    return true;
  } else {
    return false;
  }
}

// Creates and stores supplied data into a temporary file (within /tmp/).
// All temporary files are removed upon reboot.
// Allows all users/groups to read the temporary file.
//
// For more detail, refer to mkstemp manpage:
// https://man7.org/linux/man-pages/man3/mkstemp.3.html
//
// Temporary file name format:
// <app prefix>_<state name>_<paramenter name>_<device id>
// <app prefix> - prefix for our application's identifier (see kTmpFilePrefix)
// <paramenter name> - name of parameter being stored
// <state name> - state at which the stored value captures
// <device index> - device identifier
//
// dv_ind - device index
// parameterName - name of parameter stored
// stateName - state at which the stored value captures
// storageData - string value of data to be stored
rsmi_status_t storeTmpFile(uint32_t dv_ind, std::string parameterName,
                           std::string stateName, std::string storageData) {
  // Required tags needed to store our files
  // Files name format:
  // <app prefix>_<stateName>_<parameterName>_<device id>
  std::string fullFileName = kTmpFilePrefix + stateName + "_" +
                             parameterName + "_" + std::to_string(dv_ind);
  bool doesFileExist;
  std::tie(doesFileExist, std::ignore) =
        readTmpFile(dv_ind, stateName, parameterName);
  if (doesFileExist) {
    // do not store, if file already exists
    return RSMI_STATUS_SUCCESS;
  }
  // template for our file
  std::string fullTempFilePath = "/tmp/" + fullFileName + ".XXXXXX";
  char *fileName = &fullTempFilePath[0];
  int fd = mkstemp(fileName);
  if (fd == -1) {
    return RSMI_STATUS_FILE_ERROR;
  }

  chmod(fileName, S_IRUSR|S_IRGRP|S_IROTH);
  write(fd, storageData.c_str(), storageData.size());
  close(fd);
  return RSMI_STATUS_SUCCESS;
}

std::vector<std::string> getListOfAppTmpFiles() {
  std::string path = "/tmp";
  DIR *dir;
  struct dirent *ent;
  std::vector<std::string> tmpFiles;

  if ((dir = opendir(path.c_str())) != nullptr) {
    // captures all files & directories under specified path
    while ((ent  = readdir(dir)) != nullptr) {
      std::string fileDirName = ent->d_name;
      // we only want our app specific files
      if (containsString(fileDirName, kTmpFilePrefix)) {
        tmpFiles.emplace_back(path + "/" + fileDirName);
      } else {
        continue;
      }
    }
  }
  return tmpFiles;
}

// Reads a file in path provided
// If file does not exist, returns an empty string
// If file exists, returns content (which could be an empty string)
std::string readFile(std::string path) {
  std::string fileContent;
  std::ifstream inFileStream(path);
  if (inFileStream.is_open()) {
    inFileStream >> fileContent;
  }
  return fileContent;
}

// Reads a file in path provided
// If file does not exist, returns an empty vector
// If file exists, returns content (each line put into a vector; which
// could be an empty string)
std::vector<std::string> readEntireFile(std::string path) {
  std::vector<std::string> fileContent;
  std::ifstream inFileStream(path);
  if (inFileStream.is_open()) {
    std::string line;
    while (std::getline(inFileStream, line)) {
      std::istringstream ss(line);
      if(line.size() > 0) {
        fileContent.push_back(line);
      }
    }
  }
  return fileContent;
}

// Used to debug application temporary files (identified by kTmpFilePrefix)
// and their content
void displayAppTmpFilesContent() {
  std::vector<std::string> tmpFiles = getListOfAppTmpFiles();
  if (tmpFiles.empty() == false) {
    for (auto &x: tmpFiles) {
      std::string out = readFile(x);
      std::cout << __PRETTY_FUNCTION__ << " | Temporary file: " << x
                << "; Contained content: " << out << std::endl;
    }
  } else {
    std::cout << __PRETTY_FUNCTION__ << " | No temporary files were found"
              << std::endl;
  }
}

// Used to debug vector string list and their content
void displayVectorContent(std::vector<std::string> v) {
  std::cout << "Vector = {";
  if (v.size() > 0) {
    for (auto it=v.begin(); it < v.end(); it++) {
      std::cout << *it;
      auto temp_it = it;
      if(++temp_it != v.end()) {
        std::cout << ", ";
      }
    }
  } else {
    std::cout << "}" << std::endl;
  }
}

// Attempts to read application specific temporary file
// This method is to be used for reading (or determing if it exists),
// in order to keep file naming scheme consistent.
//
// dv_ind - device index
// parameterName - name of parameter stored
// stateName - state at which the stored value captures
// Returns:
// boolean - if temporary file exists
// string - content of temporary file, if it exists (otherwise, an empty
// string is returned)
std::tuple<bool, std::string> readTmpFile(uint32_t dv_ind,
                                          std::string stateName,
                                          std::string parameterName) {
  bool fileExists = false;
  std::string tmpFileName = kTmpFilePrefix + stateName + "_" +parameterName +
                            "_" + std::to_string(dv_ind);
  std::string fileContent;
  std::vector<std::string> tmpFiles = getListOfAppTmpFiles();
  if (tmpFiles.empty() == false) {
    for (auto &x: tmpFiles) {
      if (containsString(x, tmpFileName)) {
        fileContent = readFile(x);
        fileExists = true;
        break;
      }
    }
  }
  return std::make_tuple(fileExists, fileContent);
}

// wrapper to return string expression of a rsmi_status_t return
std::string getRSMIStatusString(rsmi_status_t ret) {
  const char *err_str;
  rsmi_status_string(ret, &err_str);
  return std::string(err_str);
}

// Returns a tuple:
// boolean errorDetected = returns true, if error found retrieving system
// details
// string sysname = system name (os name)
// string nodename = name of the system's node on the network
// string release = os's release level
// string version = os's version level
// string machine = hardware type system is running on
// string domainName = domain name of the the system's node on the network
// string os_distribution = pretty name of os distribution
// (typically found in /etc/*-release file)
std::tuple<bool, std::string, std::string, std::string, std::string,
           std::string, std::string, std::string> getSystemDetails(void) {
  struct utsname buf;
  bool errorDetected = false;
  std::string temp_data;
  std::string sysname, nodename, release, version, machine;
  std::string domainName = "<undefined>";
  std::string os_distribution = "<undefined>";

  if (uname(&buf) < 0) {
    errorDetected = true;
  } else {
    sysname = buf.sysname;
    nodename = buf.nodename;
    release = buf.release;
    version = buf.version;
    machine = buf.machine;
    #ifdef _GNU_SOURCE
      domainName = buf.domainname;
    #endif
  }

  std::string filePath = "/etc/os-release";
  bool fileExists = FileExists(filePath.c_str());
  if (fileExists == true) {
    std::vector<std::string> fileContent = readEntireFile(filePath);
    for (auto &line: fileContent) {
      if (line.find("PRETTY_NAME=") != std::string::npos) {
        temp_data = removeString(line, "PRETTY_NAME=");
        temp_data = removeString(temp_data, "\"");
        os_distribution = temp_data;
        break;
      }
    }
  }
  return std::make_tuple(errorDetected, sysname, nodename, release,
                         version, machine, domainName, os_distribution);
}

// If logging is enabled through RSMI_LOGGING environment variable.
// We display helpful system metrics for debug purposes.
void logSystemDetails(void) {
  std::ostringstream ss;
  bool errorDetected;
  std::string sysname, node, release, version, machine, domain, distName;
  std::tie(errorDetected, sysname, node, release, version, machine, domain,
           distName) = getSystemDetails();
  if (errorDetected == false) {
    ss << "====== Gathered system details ============\n"
       << "SYSTEM NAME: " << sysname << "\n"
       << "OS DISTRIBUTION: " << distName << "\n"
       << "NODE NAME: " << node << "\n"
       << "RELEASE: " << release << "\n"
       << "VERSION: " << version << "\n"
       << "MACHINE TYPE: " << machine << "\n"
       << "DOMAIN: " << domain << "\n";
    LOG_INFO(ss);
  } else {
    ss << "====== Gathered system details ============\n"
       << "Could not retrieve system details";
    LOG_ERROR(ss);
  }
}

}  // namespace smi
}  // namespace amd

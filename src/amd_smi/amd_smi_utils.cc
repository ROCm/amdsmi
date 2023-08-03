/* * Copyright (C) 2022 Advanced Micro Devices. All rights reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
 * the Software, and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

#include <errno.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <dirent.h>
#include <sys/types.h>
#include <memory>
#include <random>
#include <fstream>
#include <iostream>
#include <sstream>
#include <sys/ioctl.h>
#include <algorithm>
#include <string.h>
#include <limits.h>

#include "amd_smi/impl/amd_smi_utils.h"
#include "shared_mutex.h"  // NOLINT

static const uint32_t kAmdGpuId = 0x1002;

static bool isAMDGPU(std::string dev_path) {
  std::string vend_path = dev_path + "/device/vendor";

  if (!amd::smi::FileExists(vend_path.c_str())) {
	return false;
  }

  std::ifstream fs;
  fs.open(vend_path);

  if (!fs.is_open()) {
	  return false;
  }

  uint32_t vendor_id;

  fs >> std::hex >> vendor_id;

  fs.close();

  if (vendor_id == kAmdGpuId) {
	return true;
  }
  return false;
}

amdsmi_status_t smi_amdgpu_find_hwmon_dir(amd::smi::AMDSmiGPUDevice *device, std::string* full_path)
{
	if (!device->check_if_drm_is_supported()) {
		return AMDSMI_STATUS_NOT_SUPPORTED;
	}
	if (full_path == nullptr) {
		return AMDSMI_STATUS_API_FAILED;
	}
	SMIGPUDEVICE_MUTEX(device->get_mutex())

	DIR *dh;
	struct dirent * contents;
	std::string device_path = "/sys/class/drm/" + device->get_gpu_path();
	std::string directory_path = device_path + "/device/hwmon/";

	if (!isAMDGPU(device_path)) {
		return AMDSMI_STATUS_NOT_SUPPORTED;
	}

	dh = opendir(directory_path.c_str());
	if (!dh) {
		return AMDSMI_STATUS_NOT_SUPPORTED;
	}

	/*
	First directory is '.', second directory is '..' and third directory is
	valid directory for reading sysfs node
	*/
	while ((contents = readdir(dh)) != NULL) {
		std::string name = contents->d_name;
		if (name.find("hwmon", 0) != std::string::npos)
			*full_path = directory_path + name;
	}

	closedir(dh);

	return AMDSMI_STATUS_SUCCESS;
}


amdsmi_status_t smi_amdgpu_get_board_info(amd::smi::AMDSmiGPUDevice* device, amdsmi_board_info_t *info) {
	if (!device->check_if_drm_is_supported()) {
		return AMDSMI_STATUS_NOT_SUPPORTED;
	}
	SMIGPUDEVICE_MUTEX(device->get_mutex())
	std::string product_name_path = "/sys/class/drm/" + device->get_gpu_path() + std::string("/device/product_name");
	std::string product_number_path = "/sys/class/drm/" + device->get_gpu_path() + std::string("/device/product_number");
	std::string serial_number_path = "/sys/class/drm/" + device->get_gpu_path() + std::string("/device/serial_number");

	FILE *fp;

	fp = fopen(product_name_path.c_str(), "rb");
	if (fp) {
		fgets(info->product_name, sizeof(info->product_name), fp);
		fclose(fp);
	}


	fp = fopen(product_number_path.c_str(), "rb");
	if (fp) {
		fgets(info->model_number, sizeof(info->model_number), fp);
		fclose(fp);
	}


	fp = fopen(serial_number_path.c_str(), "rb");
	if (fp) {
		fscanf(fp, "%lx", &info->serial_number);
		fclose(fp);
	}

	return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t smi_amdgpu_get_power_cap(amd::smi::AMDSmiGPUDevice* device, int *cap)
{
	if (!device->check_if_drm_is_supported()) {
		return AMDSMI_STATUS_NOT_SUPPORTED;
	}
	constexpr int DATA_SIZE = 10;
	char val[DATA_SIZE];
	std::string fullpath;
	amdsmi_status_t ret = AMDSMI_STATUS_SUCCESS;

	ret = smi_amdgpu_find_hwmon_dir(device, &fullpath);

	SMIGPUDEVICE_MUTEX(device->get_mutex())

	if (ret)
		return ret;

	fullpath += "/power1_cap_max";
	std::ifstream file(fullpath.c_str(), std::ifstream::in);
	if (!file.is_open()) {
		return AMDSMI_STATUS_API_FAILED;
	}

	file.getline(val, DATA_SIZE);

	if (sscanf(val, "%d", cap) < 0) {
		return AMDSMI_STATUS_API_FAILED;
	}

	// Dividing by 1000000 to get measurement in Watts
	*cap /= 1000000;

	return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t smi_amdgpu_get_ranges(amd::smi::AMDSmiGPUDevice* device, amdsmi_clk_type_t domain,
		int *max_freq, int *min_freq, int *num_dpm)
{
	if (!device->check_if_drm_is_supported()) {
		return AMDSMI_STATUS_NOT_SUPPORTED;
	}
	SMIGPUDEVICE_MUTEX(device->get_mutex())
	std::string fullpath = "/sys/class/drm/" + device->get_gpu_path() + "/device";
	char str[10];
	unsigned int max, min, dpm;

	switch (domain) {
	case CLK_TYPE_GFX:
		fullpath += "/pp_dpm_sclk";
		break;
	case CLK_TYPE_MEM:
		fullpath += "/pp_dpm_mclk";
		break;
	case CLK_TYPE_VCLK0:
		fullpath += "/pp_dpm_vclk";
		break;
	case CLK_TYPE_VCLK1:
		fullpath += "/pp_dpm_vclk1";
		break;
	default:
		return AMDSMI_STATUS_INVAL;
	}

	std::ifstream ranges(fullpath.c_str());

	if (ranges.fail()) {
		return AMDSMI_STATUS_API_FAILED;
	}

	max = 0;
	min = UINT_MAX;
	dpm = 0;
	for (std::string line; getline(ranges, line);) {
		unsigned int d, freq;

		if (sscanf(line.c_str(), "%u: %d%s", &d, &freq, str) <= 2){
			ranges.close();
			return AMDSMI_STATUS_IO;
		}

		max = freq > max ? freq : max;
		min = freq < min ? freq: min;
		dpm = d > dpm ? d : dpm;
	}

	if (num_dpm)
		*num_dpm = dpm;
	if (max_freq)
		*max_freq = max;
	if (min_freq)
		*min_freq = min;

	ranges.close();
	return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t smi_amdgpu_get_enabled_blocks(amd::smi::AMDSmiGPUDevice* device, uint64_t *enabled_blocks) {
	if (!device->check_if_drm_is_supported()) {
		return AMDSMI_STATUS_NOT_SUPPORTED;
	}
	SMIGPUDEVICE_MUTEX(device->get_mutex())
	std::string fullpath = "/sys/class/drm/" + device->get_gpu_path() + "/device/ras/features";
	std::ifstream f(fullpath.c_str());
	std::string tmp_str;

	if (f.fail()) {
		return AMDSMI_STATUS_API_FAILED;
	}

	std::string line;
	getline(f, line);

	std::istringstream f1(line);

	f1 >> tmp_str;  // ignore
	f1 >> tmp_str;  // ignore
	f1 >> tmp_str;

	*enabled_blocks = strtoul(tmp_str.c_str(), nullptr, 16);
	f.close();

	if (*enabled_blocks == 0 || *enabled_blocks == ULONG_MAX) {
		return AMDSMI_STATUS_API_FAILED;
	}

	return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t smi_amdgpu_get_bad_page_info(amd::smi::AMDSmiGPUDevice* device, uint32_t *num_pages, amdsmi_retired_page_record_t *info) {

	if (!device->check_if_drm_is_supported()) {
		return AMDSMI_STATUS_NOT_SUPPORTED;
	}
	SMIGPUDEVICE_MUTEX(device->get_mutex())
	std::string line;
	std::vector<std::string> badPagesVec;

	std::string fullpath = "/sys/class/drm/" + device->get_gpu_path() + std::string("/device/ras/gpu_vram_bad_pages");
	std::ifstream fs(fullpath.c_str());

	if (fs.fail()) {
		return AMDSMI_STATUS_NOT_SUPPORTED;
	}

	while (std::getline(fs, line)) {
		badPagesVec.push_back(line);
	}

	if (badPagesVec.size() == 0) {
		num_pages = 0;
		return AMDSMI_STATUS_SUCCESS;
	}
	// Remove any *trailing* empty (whitespace) lines
	while (badPagesVec.size() != 0 &&
			badPagesVec.back().find_first_not_of(" \t\n\v\f\r") == std::string::npos) {
		badPagesVec.pop_back();
	}

	*num_pages = static_cast<uint32_t>(badPagesVec.size());

	if (info == nullptr) {
		return AMDSMI_STATUS_SUCCESS;
	}

	char status_code;
	amdsmi_memory_page_status_t tmp_stat;
	std::string junk;

	for (uint32_t i = 0; i < *num_pages; ++i) {
		std::istringstream fs1(badPagesVec[i]);

		fs1 >> std::hex >> info[i].page_address;
		fs1 >> junk;
		fs1 >> std::hex >> info[i].page_size;
		fs1 >> junk;
		fs1 >> status_code;

		switch (status_code) {
		case 'P':
			tmp_stat = AMDSMI_MEM_PAGE_STATUS_PENDING;
			break;

		case 'F':
			tmp_stat = AMDSMI_MEM_PAGE_STATUS_UNRESERVABLE;
			break;

		case 'R':
			tmp_stat = AMDSMI_MEM_PAGE_STATUS_RESERVED;
			break;
		default:
			return AMDSMI_STATUS_API_FAILED;
		}
		info[i].status = tmp_stat;
	}

	return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t smi_amdgpu_get_ecc_error_count(amd::smi::AMDSmiGPUDevice* device, amdsmi_error_count_t *err_cnt) {

	if (!device->check_if_drm_is_supported()) {
		return AMDSMI_STATUS_NOT_SUPPORTED;
	}
	SMIGPUDEVICE_MUTEX(device->get_mutex())
	char str[10];

	std::string fullpath = "/sys/class/drm/" + device->get_gpu_path() + std::string("/device/ras/umc_err_count");
	std::ifstream f(fullpath.c_str());

	if (f.fail()) {
		return AMDSMI_STATUS_NOT_SUPPORTED;
	}

	std::string line;
	getline(f, line);
	sscanf(line.c_str(), "%s%ld", str, &(err_cnt->uncorrectable_count));

	getline(f, line);
	sscanf(line.c_str(), "%s%ld", str, &(err_cnt->correctable_count));

	f.close();

	return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t smi_amdgpu_get_driver_version(amd::smi::AMDSmiGPUDevice* device, int *length, char *version) {
	if (!device->check_if_drm_is_supported()) {
		return AMDSMI_STATUS_NOT_SUPPORTED;
	}
	SMIGPUDEVICE_MUTEX(device->get_mutex())
	amdsmi_status_t status = AMDSMI_STATUS_SUCCESS;
	FILE *fp;
	char *tmp, *ptr, *token;
	char *ver = NULL;
	int i = 0;
	size_t len;

	if (length)
		len = *length < AMDSMI_MAX_DRIVER_VERSION_LENGTH ? *length :
		AMDSMI_MAX_DRIVER_VERSION_LENGTH;
	else
		len = AMDSMI_MAX_DRIVER_VERSION_LENGTH;

	std::string path = "/sys/module/amdgpu/version";

	fp = fopen(path.c_str(), "r");
	if (fp == nullptr){
		fp = fopen("/proc/version", "r");
		if (fp == nullptr) {
			status = AMDSMI_STATUS_IO;
			return status;
		}

		len = 0;
		if (getline(&ver, &len, fp) <= 0) {
			status = AMDSMI_STATUS_IO;
			fclose(fp);
			free(ver);
			return status;
		}

		fclose(fp);

		ptr = ver;
		token = strtok_r(ptr, " ", &tmp);

		if (!token) {
			free(ver);
			status = AMDSMI_STATUS_IO;
			return status;
		}
		for (i = 0; i < 2; i++) {
			ptr = strtok_r(NULL, " ", &tmp);
			if (!ptr)
				break;
		}
		if (i != 2 || !ptr) {
			free(ver);
			status = AMDSMI_STATUS_IO;
			return status;
		}
		if (length)
			len = *length < AMDSMI_MAX_DRIVER_VERSION_LENGTH ? *length :
			AMDSMI_MAX_DRIVER_VERSION_LENGTH;
		else
			len = AMDSMI_MAX_DRIVER_VERSION_LENGTH;

		strncpy(version, ptr,  len);
		free(ver);
	} else {
		if ((len = getline(&version, &len, fp)) <= 0)
			status = AMDSMI_STATUS_IO;

		fclose(fp);
		if (length) {
			*length = version[len-1] == '\n' ? len - 1 : len;
		}
		version[len-1] = version[len-1] == '\n' ? '\0' : version[len-1];
	}

	return status;
}

amdsmi_status_t smi_amdgpu_get_pcie_speed_from_pcie_type(uint16_t pcie_type, uint32_t *pcie_speed)
{
	switch (pcie_type) {
	case 1:
		*pcie_speed = 2500;
		break;
	case 2:
		*pcie_speed = 5000;
		break;
	case 3:
		*pcie_speed = 8000;
		break;
	case 4:
		*pcie_speed = 16000;
		break;
	case 5:
		*pcie_speed = 32000;
		break;
	default:
		return AMDSMI_STATUS_API_FAILED;
	}
	return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t smi_amdgpu_get_market_name_from_dev_id(uint32_t device_id, char *market_name)
{
	switch (device_id) {
	case 0x73c8:
	case 0x73c4:
	case 0x73c5:
	case 0x7460:
	case 0x7461:
		strcpy(market_name, "NAVI32");
		break;
	case 0x73a1:
	case 0x73ae:
		strcpy(market_name, "NAVI21");
		break;
	default:
		return AMDSMI_STATUS_API_FAILED;
	}
	return AMDSMI_STATUS_SUCCESS;
}

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

#include <sys/types.h>
#include <dirent.h>
#include <unistd.h>
#include <memory>
#include <vector>
#include <cstdlib>
#include <fstream>
#include <algorithm>
#include <string.h>

#include "amd_smi/amd_smi.h"
#include "amd_smi/impl/amd_smi_utils.h"

extern "C" {

amdsmi_status_t gpuvsmi_pid_is_gpu(const std::string &path, const char *bdf)
{
	DIR *d;
	struct dirent *dir;

	d = opendir(path.c_str());
	if (!d)
		return AMDSMI_STATUS_NO_PERM;

	/* iterate through all the fds, try to find
	* a match for the GPU bdf
	*/
	while ((dir = readdir(d)) != NULL) {
		std::string file = path + dir->d_name;
		std::ifstream fdinfo(file.c_str());
		for (std::string line; std::getline(fdinfo, line);) {
			if (line.find(bdf) != std::string::npos) {
				closedir(d);
				return AMDSMI_STATUS_SUCCESS;
			}
		}
	}

	closedir(d);

	return AMDSMI_STATUS_NOT_FOUND;
}

amdsmi_status_t gpuvsmi_get_pids(const amdsmi_bdf_t &bdf, std::vector<long int> &pids, uint64_t *size)
{
	char bdf_str[13];
	DIR *d;
	struct dirent *dir;

	/* 0000:00:00.0 */
	snprintf(bdf_str, 13, "%04x:%02x:%02x.%d", bdf.domain_number & 0xffff,
			bdf.bus_number & 0xff,
			bdf.device_number & 0x1f,
			bdf.function_number & 0x7);

	d = opendir("/proc");
	if (!d)
		return AMDSMI_STATUS_NO_PERM;

	pids.clear();
	/* Find the pid folders in /proc/ that we have access to */
	while ((dir = readdir(d)) != NULL) {
		if (dir->d_type == DT_DIR) {
			/* Try to cast the name of the folder to a
			* number, if it fails, it is not */
			char *p;
			long int pid;

			pid = strtol(dir->d_name, &p, 10);
			if (*p != 0)
				continue;

			/* Check if fdinfo is accesible */
			std::string path = "/proc/" + std::string(dir->d_name) + "/fdinfo/";

			if (access(path.c_str(), R_OK))
				continue;

			/* check if GPU is present */
			if (gpuvsmi_pid_is_gpu(path, bdf_str))
				continue;
			pids.push_back(pid);
		}
	}
	closedir(d);

	*size = pids.size();
	return AMDSMI_STATUS_SUCCESS;
}

amdsmi_status_t gpuvsmi_get_pid_info(const amdsmi_bdf_t &bdf, long int pid,
		amdsmi_proc_info_t &info)
{
	char bdf_str[13];
	DIR *d;
	struct dirent *dir;

	/* 0000:00:00.0 */
	snprintf(bdf_str, 13, "%04x:%02x:%02x.%d", bdf.domain_number & 0xffff,
			bdf.bus_number & 0xff,
			bdf.device_number & 0x1f,
			bdf.function_number & 0x7);


	std::string path = "/proc/" + std::to_string(pid) + "/fdinfo/";
	std::string name_path = "/proc/" + std::to_string(pid) + "/comm";
	std::string cgroup_path = "/proc/" + std::to_string(pid) + "/cgroup";

	if (gpuvsmi_pid_is_gpu(path.c_str(), bdf_str)) {
		return AMDSMI_STATUS_INVAL;
	}

	d = opendir(path.c_str());
	if (!d)
		return AMDSMI_STATUS_NO_PERM;

	/* Vectors to check if repated fd pasid */
	std::vector<int> pasids;

	memset(&info, 0, sizeof(info));
	/* Iterate through all fdinfos */
	while ((dir = readdir(d)) != NULL) {

		std::string file = path + dir->d_name;
		std::ifstream fdinfo(file.c_str());

		for (std::string line; getline(fdinfo, line);) {
			if (line.find("pasid:") != std::string::npos) {
				int pasid;

				if (sscanf(line.c_str(), "pasid:  %d", &pasid) != 1)
					continue;

				auto it = std::find(pasids.begin(), pasids.end(), pasid);

				if (it == pasids.end())
					pasids.push_back(pasid);
			} else if (line.find("gtt mem:") != std::string::npos) {
				unsigned long mem;

				if (sscanf(line.c_str(), "gtt mem:  %lu", &mem) != 1)
					continue;

				info.mem += mem * 1024;
				info.memory_usage.gtt_mem += mem * 1024;
			} else if (line.find("cpu mem:") != std::string::npos) {
				unsigned long mem;

				if (sscanf(line.c_str(), "cpu mem:  %lu", &mem) != 1)
					continue;

				info.mem += mem * 1024;
				info.memory_usage.cpu_mem += mem * 1024;
			} else if (line.find("vram mem:") != std::string::npos) {
				unsigned long mem;

				if (sscanf(line.c_str(), "vram mem:  %lu", &mem) != 1)
					continue;

				info.mem += mem * 1024;
				info.memory_usage.vram_mem += mem * 1024;
			} else if (line.find("gfx") != std::string::npos) {
				float usage;
				int ring;

				if (sscanf(line.c_str(), "gfx%d:  %f%%", &ring, &usage) != 2)
					continue;

				if (ring >= AMDSMI_MAX_MM_IP_COUNT)
					continue;

				info.engine_usage.gfx[ring] += (uint16_t)(usage * 100);
			} else if (line.find("compute") != std::string::npos) {
				float usage;
				int ring;

				if (sscanf(line.c_str(), "compute%d:  %f%%", &ring, &usage) != 2)
					continue;

				if (ring >= AMDSMI_MAX_MM_IP_COUNT)
					continue;

				info.engine_usage.compute[ring] += (uint16_t)(usage * 100);
			} else if (line.find("dma") != std::string::npos) {
				float usage;
				int ring;

				if (sscanf(line.c_str(), "dma%d:  %f%%", &ring, &usage) != 2)
					continue;

				if (ring >= AMDSMI_MAX_MM_IP_COUNT)
					continue;

				info.engine_usage.sdma[ring] += (uint16_t)(usage * 100);
			} else if (line.find("enc") != std::string::npos) {
				float usage;
				int ring;

				if (sscanf(line.c_str(), "enc%d:  %f%%", &ring, &usage) != 2)
					continue;

				if (ring >= AMDSMI_MAX_MM_IP_COUNT)
					continue;

				info.engine_usage.enc[ring] += (uint16_t)(usage * 100);
			} else if (line.find("dec") != std::string::npos) {
				float usage;
				int ring;

				if (sscanf(line.c_str(), "dec%d:  %f%%", &ring, &usage) != 2)
					continue;

				if (ring >= AMDSMI_MAX_MM_IP_COUNT)
					continue;

				info.engine_usage.dec[ring] += (uint16_t)(usage * 100);
			}
		}
	}


	closedir(d);

	if (!pasids.size())
		return AMDSMI_STATUS_NOT_FOUND;

	std::ifstream filename(name_path.c_str());
	std::string name;

	getline(filename, name);

	if (name.empty())
		return AMDSMI_STATUS_API_FAILED;

	strncpy(info.name, name.c_str(), std::min(
				(unsigned long) AMDSMI_NORMAL_STRING_LENGTH,
				name.length()));

	info.pid = (uint32_t)pid;

	return AMDSMI_STATUS_SUCCESS;
}

} // extern "C"

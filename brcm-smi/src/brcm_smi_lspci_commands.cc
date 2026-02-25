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


#include "brcm_smi/impl/brcm_smi_lspci_commands.h"
#include "brcm_smi/impl/brcm_smi_utils.h"
#include <sstream>
#include <fstream>
#include <memory>
#include <regex>
#include <iomanip>

namespace brcm {
namespace smi {

    brcmsmi_status_t get_lspci_device_data(std::string bdfStr, std::string search_key, std::string& version) {
        std::string lspci_data;
        std::string command = "lspci -s " + bdfStr + " -vv | grep -i '" + search_key + "'";
    
        if (smi_brcm_execute_cmd_get_data(command, &lspci_data) != BRCMSMI_STATUS_SUCCESS)
          return BRCMSMI_STATUS_NOT_SUPPORTED;
    
        int pos = lspci_data.find(search_key);
        if (pos != std::string::npos) {
            version = lspci_data.erase(0, lspci_data.find(search_key) + search_key.length());
            if (!version.empty() && version[version.length() - 1] == '\n') {
                version.erase(version.length() - 1);
            }
        }
        else
            version = "N/A";
    
        return BRCMSMI_STATUS_SUCCESS;
    }
    
    brcmsmi_status_t get_lspci_root_switch(brcmsmi_bdf_t deviceBdf, brcmsmi_bdf_t *switchBdf) {
    
        brcmsmi_status_t status = BRCMSMI_STATUS_SUCCESS;
        std::string lspci_data;
    
        status = smi_brcm_execute_cmd_get_data("lspci -tvv", &lspci_data);
        std::istringstream lines(lspci_data);
    
        std::string line;
        uint64_t bus_pos, dev_pos, fun_pos;
    
        std::vector<brcmsmi_bdf_t> switch_list;
        brcmsmi_bdf_t temp;
    
    
        // Loop through and get the switch list
        while (std::getline(lines, line)) {
    
            if(line.find("LSI PCIe Switch management endpoint") != std::string::npos){
                //get Bus
                bus_pos = line.rfind(']----');
                if (bus_pos == std::string::npos){
                continue;
                }
                
                //Get device
                dev_pos = line.rfind('.');
                if (dev_pos == std::string::npos){
                    continue;
                }
    
                //Get function
                fun_pos = dev_pos + 1;
    
                //std::cout << line.substr(bus_pos - 6, 2) << ":" << line.substr(dev_pos - 2, 2) << ":" << line.substr(fun_pos - 2, 1) << std::endl;
    
                try
                {
                    temp.bus_number =  std::stoi(line.substr(bus_pos - 6, 2), NULL, 16);
                    temp.device_number =  std::stoi(line.substr(dev_pos - 2, 2), NULL, 16);
                    temp.function_number =  std::stoi(line.substr(fun_pos - 2, 1), NULL, 16);
                } 
                catch (const std::invalid_argument& e) {
                    printf("Invalid input: Not a valid hexadecimal string\n");
                }
                catch (const std::out_of_range& e) {
                    printf("Invalid input: Number out of range\n");
                }
                
                switch_list.push_back(temp);
            }
        }
    
        //Reset Stream
        lines.clear();
        lines.seekg(0, std::ios::beg);
    
    
        for (const auto& d : switch_list){
            //std::cout << "BDF" << std::hex << d.bus_number << ":" << d.device_number << ":" << d.function_number << std::endl;
            uint64_t switch_bus_start, switch_bus_end = 0x0 ;
            std::stringstream ss;
            ss << std::hex << std::setw(2) << std::setfill('0') << d.bus_number;
    
            while (std::getline(lines, line)) {
    
                if ((line.rfind('-' + ss.str() + ']') != std::string::npos)) {
                    switch_bus_end = d.bus_number;
                    
                    bus_pos = line.rfind('-' + ss.str() + ']');
                    //std::cout << line.substr(bus_pos - 2, 2) << std::endl;
                    
                    try
                    {
                        switch_bus_start = std::stoi(line.substr(bus_pos - 2, 2), NULL, 16);
                    } 
                    catch (const std::invalid_argument& e) {
                        printf("Invalid input: Not a valid hexadecimal string\n");
                    }
                    catch (const std::out_of_range& e) {
                        printf("Invalid input: Number out of range\n");
                    }
    
                    //std::cout << switch_bus_start << "-" << switch_bus_end << std::endl; 
                    break;
                }
                
            }
    
            if (deviceBdf.bus_number >= switch_bus_start  && deviceBdf.bus_number <= switch_bus_end){
                switchBdf->bus_number = d.bus_number;
                switchBdf->device_number = d.device_number;
                switchBdf->function_number = d.function_number;
                //std::cout << "Switch found" << std::endl;
                break;
            }
        }
    
          return status;
    }

}  // namespace smi
}  // namespace brcm

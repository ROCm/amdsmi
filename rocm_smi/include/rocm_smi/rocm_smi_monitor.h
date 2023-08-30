/*
 * =============================================================================
 *   ROC Runtime Conformance Release License
 * =============================================================================
 * The University of Illinois/NCSA
 * Open Source License (NCSA)
 *
 * Copyright (c) 2017, Advanced Micro Devices, Inc.
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
#ifndef INCLUDE_ROCM_SMI_ROCM_SMI_MONITOR_H_
#define INCLUDE_ROCM_SMI_ROCM_SMI_MONITOR_H_

#include <string>
#include <cstdint>
#include <map>

#include "rocm_smi/rocm_smi_common.h"
#include "rocm_smi/rocm_smi.h"

namespace amd {
namespace smi {

enum MonitorTypes {
  kMonName,
  kMonTemp,     // Temperature in millidegrees
  kMonFanSpeed,
  kMonMaxFanSpeed,
  kMonFanRPMs,
  kMonFanCntrlEnable,
  kMonPowerCap,
  kMonPowerCapDefault,
  kMonPowerCapMax,
  kMonPowerCapMin,
  kMonPowerAve,
  kMonTempMax,
  kMonTempMin,
  kMonTempMaxHyst,
  kMonTempMinHyst,
  kMonTempCritical,
  kMonTempCriticalHyst,
  kMonTempEmergency,
  kMonTempEmergencyHyst,
  kMonTempCritMin,
  kMonTempCritMinHyst,
  kMonTempOffset,
  kMonTempLowest,
  kMonTempHighest,
  kMonTempLabel,
  kMonVolt,
  kMonVoltMax,
  kMonVoltMinCrit,
  kMonVoltMin,
  kMonVoltMaxCrit,
  kMonVoltAverage,
  kMonVoltLowest,
  kMonVoltHighest,
  kMonVoltLabel,

  kMonInvalid = 0xFFFFFFFF,
};

const std::map<MonitorTypes,std::string> monitorTypesToString {
   {MonitorTypes::kMonName, "amd::smi::kMonName"},
   {MonitorTypes::kMonTemp, "amd::smi::kMonName"},
   {MonitorTypes::kMonFanSpeed, "amd::smi::kMonName"},
   {MonitorTypes::kMonMaxFanSpeed, "amd::smi::kMonName"},
   {MonitorTypes::kMonFanRPMs, "amd::smi::kMonName"},
   {MonitorTypes::kMonFanCntrlEnable, "amd::smi::kMonName"},
   {MonitorTypes::kMonPowerCap, "amd::smi::kMonName"},
   {MonitorTypes::kMonPowerCapDefault, "amd::smi::kMonName"},
   {MonitorTypes::kMonPowerCapMax, "amd::smi::kMonName"},
   {MonitorTypes::kMonPowerCapMin, "amd::smi::kMonName"},
   {MonitorTypes::kMonPowerAve, "amd::smi::kMonName"},
   {MonitorTypes::kMonTempMax, "amd::smi::kMonName"},
   {MonitorTypes::kMonTempMin, "amd::smi::kMonName"},
   {MonitorTypes::kMonTempMaxHyst, "amd::smi::kMonName"},
   {MonitorTypes::kMonTempMinHyst, "amd::smi::kMonName"},
   {MonitorTypes::kMonTempCritical, "amd::smi::kMonName"},
   {MonitorTypes::kMonTempCriticalHyst, "amd::smi::kMonName"},
   {MonitorTypes::kMonTempEmergency, "amd::smi::kMonName"},
   {MonitorTypes::kMonTempEmergencyHyst, "amd::smi::kMonName"},
   {MonitorTypes::kMonTempCritMin, "amd::smi::kMonName"},
   {MonitorTypes::kMonTempCritMinHyst, "amd::smi::kMonName"},
   {MonitorTypes::kMonTempOffset, "amd::smi::kMonName"},
   {MonitorTypes::kMonTempLowest, "amd::smi::kMonName"},
   {MonitorTypes::kMonTempHighest, "amd::smi::kMonName"},
   {MonitorTypes::kMonTempLabel, "amd::smi::kMonName"},
   {MonitorTypes::kMonVolt, "amd::smi::kMonName"},
   {MonitorTypes::kMonVoltMax, "amd::smi::kMonName"},
   {MonitorTypes::kMonVoltMinCrit, "amd::smi::kMonName"},
   {MonitorTypes::kMonVoltMin, "amd::smi::kMonName"},
   {MonitorTypes::kMonVoltMaxCrit, "amd::smi::kMonName"},
   {MonitorTypes::kMonVoltAverage, "amd::smi::kMonName"},
   {MonitorTypes::kMonVoltLowest, "amd::smi::kMonName"},
   {MonitorTypes::kMonVoltHighest, "amd::smi::kMonName"},
   {MonitorTypes::kMonVoltLabel, "amd::smi::kMonName"},
   {MonitorTypes::kMonInvalid, "amd::smi::kMonName"},
};


class Monitor {
 public:
    explicit Monitor(std::string path, RocmSMI_env_vars const *e);
    ~Monitor(void);
    const std::string path(void) const {return path_;}
    int readMonitor(MonitorTypes type, uint32_t sensor_ind, std::string *val);
    int writeMonitor(MonitorTypes type, uint32_t sensor_ind, std::string val);
    int32_t setTempSensorLabelMap(void);
    uint32_t getTempSensorIndex(rsmi_temperature_type_t type);
    rsmi_temperature_type_t getTempSensorEnum(uint64_t ind);
    int32_t setVoltSensorLabelMap(void);
    uint32_t getVoltSensorIndex(rsmi_voltage_type_t type);
    rsmi_voltage_type_t getVoltSensorEnum(uint64_t ind);
    void fillSupportedFuncs(SupportedFuncMap *supported_funcs);

 private:
    std::string MakeMonitorPath(MonitorTypes type, uint32_t sensor_id);
    std::string path_;
    const RocmSMI_env_vars *env_;
    std::map<rsmi_temperature_type_t, uint32_t> temp_type_index_map_;
    std::map<rsmi_voltage_type_t, uint32_t> volt_type_index_map_;

    // This map uses a 64b index instead of 32b (unlike temp_type_index_map_)
    // for flexibility and simplicity. Currently, some parts of the
    // implementation store both the RSMI api index and the file index into a
    // single value. 32 bits is enough to store both, but we are using 64
    // bits for simpler integration with existing implementation, which uses
    // a 64b value. Also, if we need to encode anything else, 64b will give
    // us more room to do so, without excessive changes.
    std::map<uint64_t, rsmi_temperature_type_t> index_temp_type_map_;
    std::map<uint64_t, rsmi_voltage_type_t> index_volt_type_map_;
};

}  // namespace smi
}  // namespace amd

#endif  // INCLUDE_ROCM_SMI_ROCM_SMI_MONITOR_H_

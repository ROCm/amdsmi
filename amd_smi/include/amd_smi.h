/*
 * =============================================================================
 * The University of Illinois/NCSA
 * Open Source License (NCSA)
 *
 * Copyright (c) 2022, Advanced Micro Devices, Inc.
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

#ifndef INCLUDE_AMD_SMI_H_
#define INCLUDE_AMD_SMI_H_

#include <stdlib.h>
#ifdef __cplusplus
extern "C" {
#include <cstdint>
#else
#include <stdint.h>
#endif  // __cplusplus
#include "rocm_smi/kfd_ioctl.h"

/**
 * @brief Initialization flags
 *
 * Initialization flags may be OR'd together and passed to ::amdsmi_init().
 */

#define  AMD_SMI_INIT_ALL_DEVICES       0x0             // Default option
#define  AMD_SMI_INIT_AMD_CPUS          (1 << 0)
#define  AMD_SMI_INIT_AMD_GPUS          (1 << 1)
#define  AMD_SMI_INIT_NON_AMD_CPUS      (1 << 2)
#define  AMD_SMI_INIT_NON_AMD_GPUS      (1 << 3)

/* Maximum size definitions GPUVSMI */
#define AMDSMI_MAX_MM_IP_COUNT	      8
#define AMDSMI_MAX_DATE_LENGTH	      32 /**< YYYY-MM-DD:HH:MM:SS.MSC */
#define AMDSMI_MAX_STRING_LENGTH	      64
#define AMDSMI_NORMAL_STRING_LENGTH      32
#define AMDSMI_MAX_DEVICES		      32
#define AMDSMI_MAX_NAME		      32
#define AMDSMI_MAX_DRIVER_VERSION_LENGTH 80
#define AMDSMI_PRODUCT_NAME_LENGTH 128
#define AMDSMI_MAX_CONTAINER_TYPE    2

#define AMDSMI_GPU_UUID_SIZE 38

/* string format */
#define AMDSMI_TIME_FORMAT "%02d:%02d:%02d.%03d"
#define AMDSMI_DATE_FORMAT "%04d-%02d-%02d:%02d:%02d:%02d.%03d"

typedef enum amdsmi_mm_ip { MM_UVD, MM_VCE, MM_VCN, MM__MAX } amdsmi_mm_ip_t;

typedef enum amdsmi_container_types {
	CONTAINER_LXC,
	CONTAINER_DOCKER,
} amdsmi_container_types_t;

//! opaque handler point to underlying implementation
typedef void *amdsmi_device_handle;
typedef void *amdsmi_socket_handle;

typedef enum device_type {
  UNKNOWN = 0,
  AMD_GPU,
  AMD_CPU,
  NON_AMD_GPU,
  NON_AMD_CPU
} device_type_t;

/**
 * @brief Error codes retured by amd_smi_lib functions
 */
typedef enum amdsmi_status {
    AMDSMI_STATUS_SUCCESS = 0,  /**< Call succeeded */
    AMDSMI_STATUS_INVAL,  /**< Invalid parameters */
    AMDSMI_STATUS_NOT_SUPPORTED,  /**< Command not supported */
    AMDSMI_STATUS_FILE_ERROR, /**< Problem accessing a file. */
    AMDSMI_STATUS_NO_PERM,  /**< Permission Denied */
    AMDSMI_STATUS_OUT_OF_RESOURCES,  /**< Not enough memory */
    AMDSMI_STATUS_INTERNAL_EXCEPTION,  /**< An internal exception was caught */
    AMDSMI_STATUS_INPUT_OUT_OF_BOUNDS, /**< The provided input is out of allowable or safe range */
    AMDSMI_STATUS_INIT_ERROR, /**< An error occurred when initializing internal data structures */
    AMDSMI_STATUS_NOT_YET_IMPLEMENTED, /**< Not implemented yet */
    AMDSMI_STATUS_NOT_FOUND,  /**< Device Not found */
    AMDSMI_STATUS_INSUFFICIENT_SIZE, /**< Not enough resources were available for the operation */
    AMDSMI_STATUS_INTERRUPT, /**< An interrupt occurred during execution of function */
    AMDSMI_STATUS_UNEXPECTED_SIZE, /**< An unexpected amount of data was read */
    AMDSMI_STATUS_NO_DATA, /**< No data was found for a given input */
    AMDSMI_STATUS_UNEXPECTED_DATA, /**< The data read or provided to function is not what was expected */
    AMDSMI_STATUS_BUSY,  /**< Device busy */
    AMDSMI_STATUS_REFCOUNT_OVERFLOW, /**< An internal reference counter exceeded INT32_MAX */
    AMDSMI_LIB_START = 1000,
    AMDSMI_STATUS_FAIL_LOAD_MODULE = AMDSMI_LIB_START,  //!< Fail to load lib
    AMDSMI_STATUS_FAIL_LOAD_SYMBOL,
    AMDSMI_STATUS_DRM_ERROR,   //!< Error when call libdrm
    AMDSMI_STATUS_IO,  /**< I/O Error */
    AMDSMI_STATUS_FAULT,  /**< Bad address */
    AMDSMI_STATUS_API_FAILED, /**< API call failed */
    AMDSMI_STATUS_TIMEOUT, /**< Timeout in API call */
    AMDSMI_STATUS_NO_SLOT, /**< No more free slot */
    AMDSMI_STATUS_RETRY, /**< Retry operation */
    AMDSMI_STATUS_NOT_INIT, /**< Device not initialized */
    AMDSMI_STATUS_UNKNOWN_ERROR = 0xFFFFFFFF,  //!< An unknown error occurred
} amdsmi_status_t;

/**
 * Clock types
 */
typedef enum amdsmi_clk_type {
     CLOCK_TYPE_SYS,   //!< System clock
    CLOCK_TYPE_DF,  //!< Data Fabric clock (for ASICs
                    //!< running on a separate clock)
    CLOCK_TYPE_DCEF,   //!< Display Controller Engine clock
    CLOCK_TYPE_SOC,
    CLOCK_TYPE_MEM,
    CLOCK_TYPE_PCIE,
    CLOCK_TYPE_GFX,
    CLOCK_TYPE_VCLK0,
    CLOCK_TYPE_VCLK1,
    CLOCK_TYPE_DCLK0,
    CLOCK_TYPE_DCLK1,
    CLOCK_TYPE__MAX = CLOCK_TYPE_DCLK1
} amdsmi_clk_type_t;
/// \cond Ignore in docs.
typedef amdsmi_clk_type_t amdsmi_clk_type;
/// \endcond

/**
 * @brief This enumeration is used to indicate from which part of the device a
 * temperature reading should be obtained.
 */
typedef enum amdsmi_temperature_type {
    TEMPERATURE_TYPE_EDGE,
    TEMPERATURE_TYPE_JUNCTION,
    TEMPERATURE_TYPE_VRAM,
    TEMPERATURE_TYPE_PLX,
    TEMPERATURE_TYPE_HBM_0,
    TEMPERATURE_TYPE_HBM_1,
    TEMPERATURE_TYPE_HBM_2,
    TEMPERATURE_TYPE_HBM_3,
    TEMPERATURE_TYPE__MAX,
} amdsmi_temperature_type_t;

/**
 * @brief The values of this enum are used to identify the various firmware
 * blocks.
 */
typedef enum amdsmi_fw_block {
    FW_ID_SMU = 1,
    FW_ID_CP_CE,
    FW_ID_CP_PFP,
    FW_ID_CP_ME,
    FW_ID_CP_MEC_JT1,
    FW_ID_CP_MEC_JT2,
    FW_ID_CP_MEC1,
    FW_ID_CP_MEC2,
    FW_ID_RLC,
    FW_ID_SDMA0,
    FW_ID_SDMA1,
    FW_ID_SDMA2,
    FW_ID_SDMA3,
    FW_ID_SDMA4,
    FW_ID_SDMA5,
    FW_ID_SDMA6,
    FW_ID_SDMA7,
    FW_ID_VCN,
    FW_ID_UVD,
    FW_ID_VCE,
    FW_ID_ISP,
    FW_ID_DMCU_ERAM, /*eRAM*/
    FW_ID_DMCU_ISR,  /*ISR*/
    FW_ID_RLC_RESTORE_LIST_GPM_MEM,
    FW_ID_RLC_RESTORE_LIST_SRM_MEM,
    FW_ID_RLC_RESTORE_LIST_CNTL,
    FW_ID_RLC_V,
    FW_ID_MMSCH,
    FW_ID_PSP_SYSDRV,
    FW_ID_PSP_SOSDRV,
    FW_ID_PSP_TOC,
    FW_ID_PSP_KEYDB,
    FW_ID_DFC,
    FW_ID_PSP_SPL,
    FW_ID_DRV_CAP,
    FW_ID_MC,
    FW_ID_PSP_BL,
    FW_ID_CP_PM4,
    FW_ID_ASD,
    FW_ID_TA_RAS,
    FW_ID_XGMI,
    FW_ID_RLC_SRLG,
    FW_ID_RLC_SRLS,
    FW_ID_SMC,
    FW_ID__MAX
} amdsmi_fw_block_t;

/**
 * @brief This structure represents a range (e.g., frequencies or voltages).
 */
typedef struct {
    uint64_t lower_bound;      //!< Lower bound of range
    uint64_t upper_bound;      //!< Upper bound of range
} amdsmi_range_t;
/// \cond Ignore in docs.
typedef amdsmi_range_t amdsmi_range;
/// \endcond

typedef struct amdsmi_xgmi_info {
	uint8_t	 xgmi_lanes;
	uint64_t xgmi_hive_id;
	uint64_t xgmi_node_id;
	uint32_t index;
} amdsmi_xgmi_info_t;

/**
 * GPU Capability info
 */
typedef struct amdsmi_gpu_caps {
	struct {
		uint32_t gfxip_major;
		uint32_t gfxip_minor;
		uint16_t gfxip_cu_count;
	} gfx;
	struct {
		uint8_t mm_ip_count;
		uint8_t mm_ip_list[AMDSMI_MAX_MM_IP_COUNT];
	} mm;

	bool	 ras_supported;
	uint8_t	 max_vf_num;
	uint32_t gfx_ip_count;
	uint32_t dma_ip_count;
} amdsmi_gpu_caps_t;

typedef struct amdsmi_vram_info {
	uint32_t vram_total;
	uint32_t vram_used;
} amdsmi_vram_info_t;

typedef struct amdsmi_frequency_range {
	amdsmi_range_t supported_freq_range;
	amdsmi_range_t current_freq_range;
} amdsmi_frequency_range_t;
typedef union amdsmi_bdf {
	struct {
		uint64_t function_number : 6;
		uint64_t device_number : 10;
		uint64_t bus_number : 16;
		uint64_t domain_number : 32;
	};
	uint64_t as_uint;
} amdsmi_bdf_t;

typedef struct amdsmi_power_cap_info {
	uint32_t power_cap;
	uint32_t default_power_cap;
	uint32_t dpm_cap;
	uint32_t min_power_cap;
	uint32_t max_power_cap;
} amdsmi_power_cap_info_t;

typedef struct amdsmi_vbios_info {
	char	 name[AMDSMI_MAX_STRING_LENGTH];
	uint32_t vbios_version;
	char	 build_date[AMDSMI_MAX_DATE_LENGTH];
	char     part_number[AMDSMI_MAX_STRING_LENGTH];
	char     vbios_version_string[AMDSMI_NORMAL_STRING_LENGTH];
} amdsmi_vbios_info_t;

typedef struct amdsmi_fw_info {
	uint8_t num_fw_info;
	struct {
		amdsmi_fw_block_t fw_id;
		uint32_t fw_version;
	} fw_info_list[FW_ID__MAX];
} amdsmi_fw_info_t;

typedef struct amdsmi_asic_info {
	char	 market_name[AMDSMI_MAX_STRING_LENGTH];
	uint32_t family; /**< Has zero value */
	uint32_t vendor_id;   //< Use 32 bit to be compatible with other platform.
	uint32_t subvendor_id;
	uint32_t device_id;
	uint32_t rev_id;
	uint64_t asic_serial;
} amdsmi_asic_info_t;

typedef struct amdsmi_board_info {
	uint64_t serial_number;
  bool	 is_master;
	char	 model_number[AMDSMI_NORMAL_STRING_LENGTH];
	char	 product_serial[AMDSMI_NORMAL_STRING_LENGTH];
	char	 fru_id[AMDSMI_NORMAL_STRING_LENGTH];
	char	 product_name[AMDSMI_PRODUCT_NAME_LENGTH];
	char	 manufacturer_name[AMDSMI_NORMAL_STRING_LENGTH];
} amdsmi_board_info_t;

typedef struct amdsmi_temperature {
	uint16_t      cur_temp;
} amdsmi_temperature_t;

typedef struct amdsmi_temperature_limit {
	uint16_t      limit;
} amdsmi_temperature_limit_t;

typedef struct amdsmi_power_limit {
	uint16_t      limit;
} amdsmi_power_limit_t;

typedef struct amdsmi_power_measure {
	uint16_t average_socket_power;
 	uint64_t energy_accumulator;      // v1 mod. (32->64)
	uint32_t voltage_gfx;  //GFX voltage measurement in mV
	uint32_t voltage_soc; // SOC voltage measurement in mV
	uint32_t voltage_mem; // MEM voltage measurement in mV
} amdsmi_power_measure_t;

typedef struct amdsmi_clock_measure {
  	uint32_t cur_clk;
	uint32_t avg_clk;
	uint32_t min_clk;
	uint32_t max_clk;
} amdsmi_clock_measure_t;

typedef struct amdsmi_engine_usage {
	uint32_t average_gfx_activity;
	uint32_t average_umc_activity;
	uint32_t average_mm_activity[AMDSMI_MAX_MM_IP_COUNT];
} amdsmi_engine_usage_t;

typedef uint32_t amdsmi_process_handle;

typedef struct amdsmi_process_info {
	char                  name[AMDSMI_NORMAL_STRING_LENGTH];
	amdsmi_process_handle pid;
	uint64_t              mem; /** in bytes */
	struct {
		uint16_t gfx[AMDSMI_MAX_MM_IP_COUNT];
		uint16_t compute[AMDSMI_MAX_MM_IP_COUNT];
		uint16_t sdma[AMDSMI_MAX_MM_IP_COUNT];
		uint16_t enc[AMDSMI_MAX_MM_IP_COUNT];
		uint16_t dec[AMDSMI_MAX_MM_IP_COUNT];
	} usage; /** percentage 0-100% times 100 */
	char container_name[AMDSMI_NORMAL_STRING_LENGTH];
} amdsmi_proc_info_t;

//! Guaranteed maximum possible number of supported frequencies
#define AMDSMI_MAX_NUM_FREQUENCIES 32

//! Maximum possible value for fan speed. Should be used as the denominator
//! when determining fan speed percentage.
#define AMDSMI_MAX_FAN_SPEED 255

//! The number of points that make up a voltage-frequency curve definition
#define AMDSMI_NUM_VOLTAGE_CURVE_POINTS 3
/**
 * @brief PowerPlay performance levels
 */
typedef enum {
  AMDSMI_DEV_PERF_LEVEL_AUTO = 0,       //!< Performance level is "auto"
  AMDSMI_DEV_PERF_LEVEL_FIRST = AMDSMI_DEV_PERF_LEVEL_AUTO,

  AMDSMI_DEV_PERF_LEVEL_LOW,              //!< Keep PowerPlay levels "low",
                                        //!< regardless of workload
  AMDSMI_DEV_PERF_LEVEL_HIGH,             //!< Keep PowerPlay levels "high",
                                        //!< regardless of workload
  AMDSMI_DEV_PERF_LEVEL_MANUAL,           //!< Only use values defined by manually
                                        //!< setting the AMDSMI_CLK_TYPE_SYS speed
  AMDSMI_DEV_PERF_LEVEL_STABLE_STD,       //!< Stable power state with profiling
                                        //!< clocks
  AMDSMI_DEV_PERF_LEVEL_STABLE_PEAK,      //!< Stable power state with peak clocks
  AMDSMI_DEV_PERF_LEVEL_STABLE_MIN_MCLK,  //!< Stable power state with minimum
                                        //!< memory clock
  AMDSMI_DEV_PERF_LEVEL_STABLE_MIN_SCLK,  //!< Stable power state with minimum
                                        //!< system clock
  AMDSMI_DEV_PERF_LEVEL_DETERMINISM,      //!< Performance determinism state

  AMDSMI_DEV_PERF_LEVEL_LAST = AMDSMI_DEV_PERF_LEVEL_DETERMINISM,

  AMDSMI_DEV_PERF_LEVEL_UNKNOWN = 0x100   //!< Unknown performance level
} amdsmi_dev_perf_level_t;
/// \cond Ignore in docs.
typedef amdsmi_dev_perf_level_t amdsmi_dev_perf_level;
/// \endcond
/**
 * @brief Available clock types.
 */

/**
 * @brief Software components
 */
typedef enum {
  AMDSMI_SW_COMP_FIRST = 0x0,

  AMDSMI_SW_COMP_DRIVER = AMDSMI_SW_COMP_FIRST,    //!< Driver

  AMDSMI_SW_COMP_LAST = AMDSMI_SW_COMP_DRIVER
} amdsmi_sw_component_t;

/**
 * Event counter types
 */

/**
 * @brief Handle to performance event counter
 */
typedef uintptr_t amdsmi_event_handle_t;

/**
 * Event Groups
 *
 * @brief Enum denoting an event group. The value of the enum is the
 * base value for all the event enums in the group.
 */
typedef enum {
  AMDSMI_EVNT_GRP_XGMI = 0,         //!< Data Fabric (XGMI) related events
  AMDSMI_EVNT_GRP_XGMI_DATA_OUT = 10,  //!< XGMI Outbound data
  AMDSMI_EVNT_GRP_INVALID = 0xFFFFFFFF
} amdsmi_event_group_t;

/**
 * Event types
 * @brief Event type enum. Events belonging to a particular event group
 * ::amdsmi_event_group_t should begin enumerating at the ::amdsmi_event_group_t
 * value for that group.
 */
typedef enum {
  AMDSMI_EVNT_FIRST = AMDSMI_EVNT_GRP_XGMI,

  AMDSMI_EVNT_XGMI_FIRST = AMDSMI_EVNT_GRP_XGMI,
  AMDSMI_EVNT_XGMI_0_NOP_TX = AMDSMI_EVNT_XGMI_FIRST,  //!< NOPs sent to neighbor 0
  AMDSMI_EVNT_XGMI_0_REQUEST_TX,                    //!< Outgoing requests to
                                                  //!< neighbor 0
  AMDSMI_EVNT_XGMI_0_RESPONSE_TX,                   //!< Outgoing responses to
                                                  //!< neighbor 0
  /**
   * @brief
   *
   * Data beats sent to neighbor 0; Each beat represents 32 bytes.<br><br>
   *
   * XGMI throughput can be calculated by multiplying a BEATs event
   * such as ::AMDSMI_EVNT_XGMI_0_BEATS_TX by 32 and dividing by
   * the time for which event collection occurred,
   * ::amdsmi_counter_value_t.time_running (which is in nanoseconds). To get
   * bytes per second, multiply this value by 10<sup>9</sup>.<br>
   * <br>
   * Throughput = BEATS/time_running * 10<sup>9</sup>  (bytes/second)<br>
   */
  // ie, Throughput = BEATS/time_running 10^9  bytes/sec
  AMDSMI_EVNT_XGMI_0_BEATS_TX,
  AMDSMI_EVNT_XGMI_1_NOP_TX,                        //!< NOPs sent to neighbor 1
  AMDSMI_EVNT_XGMI_1_REQUEST_TX,                        //!< Outgoing requests to
                                                  //!< neighbor 1
  AMDSMI_EVNT_XGMI_1_RESPONSE_TX,                   //!< Outgoing responses to
                                                  //!< neighbor 1
  AMDSMI_EVNT_XGMI_1_BEATS_TX,                      //!< Data beats sent to
                                                  //!< neighbor 1; Each beat
                                                  //!< represents 32 bytes

  AMDSMI_EVNT_XGMI_LAST = AMDSMI_EVNT_XGMI_1_BEATS_TX,   // 5

  AMDSMI_EVNT_XGMI_DATA_OUT_FIRST = AMDSMI_EVNT_GRP_XGMI_DATA_OUT,  // 10

  /*
   * @brief Events in the AMDSMI_EVNT_GRP_XGMI_DATA_OUT group measure
   * the number of beats sent on an XGMI link. Each beat represents
   * 32 bytes. AMDSMI_EVNT_XGMI_DATA_OUT_n represents the number of
   * outbound beats (each representing 32 bytes) on link n.<br><br>
   *
   * XGMI throughput can be calculated by multiplying a event
   * such as ::AMDSMI_EVNT_XGMI_DATA_OUT_n by 32 and dividing by
   * the time for which event collection occurred,
   * ::amdsmi_counter_value_t.time_running (which is in nanoseconds). To get
   * bytes per second, multiply this value by 10<sup>9</sup>.<br>
   * <br>
   * Throughput = BEATS/time_running * 10<sup>9</sup>  (bytes/second)<br>
   */
  // ie, Throughput = BEATS/time_running 10^9  bytes/sec
  AMDSMI_EVNT_XGMI_DATA_OUT_0 = AMDSMI_EVNT_XGMI_DATA_OUT_FIRST,
  AMDSMI_EVNT_XGMI_DATA_OUT_1,   //!< Outbound beats to neighbor 1
  AMDSMI_EVNT_XGMI_DATA_OUT_2,   //!< Outbound beats to neighbor 2
  AMDSMI_EVNT_XGMI_DATA_OUT_3,   //!< Outbound beats to neighbor 3
  AMDSMI_EVNT_XGMI_DATA_OUT_4,   //!< Outbound beats to neighbor 4
  AMDSMI_EVNT_XGMI_DATA_OUT_5,   //!< Outbound beats to neighbor 5
  AMDSMI_EVNT_XGMI_DATA_OUT_LAST = AMDSMI_EVNT_XGMI_DATA_OUT_5,

  AMDSMI_EVNT_LAST = AMDSMI_EVNT_XGMI_DATA_OUT_LAST,
} amdsmi_event_type_t;

/**
 * Event counter commands
 */
typedef enum {
  AMDSMI_CNTR_CMD_START = 0,  //!< Start the counter
  AMDSMI_CNTR_CMD_STOP,       //!< Stop the counter; note that this should not
                            //!< be used before reading.
} amdsmi_counter_command_t;

/**
 * Counter value
 */
typedef struct {
  uint64_t value;            //!< Counter value
  uint64_t time_enabled;     //!< Time that the counter was enabled
                             //!< (in nanoseconds)
  uint64_t time_running;     //!< Time that the counter was running
                             //!< (in nanoseconds)
} amdsmi_counter_value_t;

/**
 * Event notification event types
 */
typedef enum {
  AMDSMI_EVT_NOTIF_VMFAULT = KFD_SMI_EVENT_VMFAULT,  //!< VM page fault
  AMDSMI_EVT_NOTIF_FIRST = AMDSMI_EVT_NOTIF_VMFAULT,
  AMDSMI_EVT_NOTIF_THERMAL_THROTTLE = KFD_SMI_EVENT_THERMAL_THROTTLE,
  AMDSMI_EVT_NOTIF_GPU_PRE_RESET = KFD_SMI_EVENT_GPU_PRE_RESET,
  AMDSMI_EVT_NOTIF_GPU_POST_RESET = KFD_SMI_EVENT_GPU_POST_RESET,

  AMDSMI_EVT_NOTIF_LAST = AMDSMI_EVT_NOTIF_GPU_POST_RESET
} amdsmi_evt_notification_type_t;

/**
 * Macro to generate event bitmask from event id
 */
#define AMDSMI_EVENT_MASK_FROM_INDEX(i) (1ULL << ((i) - 1))

//! Maximum number of characters an event notification message will be
#define MAX_EVENT_NOTIFICATION_MSG_SIZE 64

/**
 * Event notification data returned from event notification API
 */
typedef struct {
    amdsmi_device_handle device_handle;        //!< Handler of device that corresponds to the event
    amdsmi_evt_notification_type_t event;     //!< Event type
    char message[MAX_EVENT_NOTIFICATION_MSG_SIZE];  //!< Event message
} amdsmi_evt_notification_data_t;

/**
 * @brief Temperature Metrics.  This enum is used to identify various
 * temperature metrics. Corresponding values will be in millidegress
 * Celcius.
 */
typedef enum {
  AMDSMI_TEMP_CURRENT = 0x0,   //!< Temperature current value.
  AMDSMI_TEMP_FIRST = AMDSMI_TEMP_CURRENT,

  AMDSMI_TEMP_MAX,             //!< Temperature max value.
  AMDSMI_TEMP_MIN,             //!< Temperature min value.
  AMDSMI_TEMP_MAX_HYST,        //!< Temperature hysteresis value for max limit.
                             //!< (This is an absolute temperature, not a
                             //!< delta).
  AMDSMI_TEMP_MIN_HYST,        //!< Temperature hysteresis value for min limit.
                             //!< (This is an absolute temperature,
                             //!<  not a delta).
  AMDSMI_TEMP_CRITICAL,        //!< Temperature critical max value, typically
                             //!<  greater than corresponding temp_max values.
  AMDSMI_TEMP_CRITICAL_HYST,   //!< Temperature hysteresis value for critical
                             //!<  limit. (This is an absolute temperature,
                             //!<  not a delta).
  AMDSMI_TEMP_EMERGENCY,       //!< Temperature emergency max value, for chips
                             //!<  supporting more than two upper temperature
                             //!<  limits. Must be equal or greater than
                             //!<  corresponding temp_crit values.
  AMDSMI_TEMP_EMERGENCY_HYST,  //!< Temperature hysteresis value for emergency
                             //!<  limit. (This is an absolute temperature,
                             //!<  not a delta).
  AMDSMI_TEMP_CRIT_MIN,        //!< Temperature critical min value, typically
                             //!<  lower than corresponding temperature
                             //!<  minimum values.
  AMDSMI_TEMP_CRIT_MIN_HYST,   //!< Temperature hysteresis value for critical
                             //!< minimum limit. (This is an absolute
                             //!< temperature, not a delta).
  AMDSMI_TEMP_OFFSET,          //!< Temperature offset which is added to the
                             //!  temperature reading by the chip.
  AMDSMI_TEMP_LOWEST,          //!< Historical minimum temperature.
  AMDSMI_TEMP_HIGHEST,         //!< Historical maximum temperature.

  AMDSMI_TEMP_LAST = AMDSMI_TEMP_HIGHEST
} amdsmi_temperature_metric_t;
/// \cond Ignore in docs.
typedef amdsmi_temperature_metric_t amdsmi_temperature_metric;
/// \endcond

/**
 * @brief Voltage Metrics.  This enum is used to identify various
 * Volatge metrics. Corresponding values will be in millivolt.
 *
 */
typedef enum {
  AMDSMI_VOLT_CURRENT = 0x0,               //!< Voltage current value.

  AMDSMI_VOLT_FIRST = AMDSMI_VOLT_CURRENT,
  AMDSMI_VOLT_MAX,                         //!< Voltage max value.
  AMDSMI_VOLT_MIN_CRIT,                    //!< Voltage critical min value.
  AMDSMI_VOLT_MIN,                         //!< Voltage min value.
  AMDSMI_VOLT_MAX_CRIT,                    //!< Voltage critical max value.
  AMDSMI_VOLT_AVERAGE,                     //!< Average voltage.
  AMDSMI_VOLT_LOWEST,                      //!< Historical minimum voltage.
  AMDSMI_VOLT_HIGHEST,                     //!< Historical maximum voltage.

  AMDSMI_VOLT_LAST = AMDSMI_VOLT_HIGHEST
} amdsmi_voltage_metric_t;

/**
 * @brief This ennumeration is used to indicate which type of
 * voltage reading should be obtained.
 */
typedef enum {
  AMDSMI_VOLT_TYPE_FIRST = 0,

  AMDSMI_VOLT_TYPE_VDDGFX = AMDSMI_VOLT_TYPE_FIRST,  //!< Vddgfx GPU
                                                 //!< voltage
  AMDSMI_VOLT_TYPE_LAST = AMDSMI_VOLT_TYPE_VDDGFX,
  AMDSMI_VOLT_TYPE_INVALID = 0xFFFFFFFF            //!< Invalid type
} amdsmi_voltage_type_t;

/**
 * @brief Pre-set Profile Selections. These bitmasks can be AND'd with the
 * ::amdsmi_power_profile_status_t.available_profiles returned from
 * ::amdsmi_dev_power_profile_presets_get to determine which power profiles
 * are supported by the system.
 */
typedef enum {
  AMDSMI_PWR_PROF_PRST_CUSTOM_MASK = 0x1,        //!< Custom Power Profile
  AMDSMI_PWR_PROF_PRST_VIDEO_MASK = 0x2,         //!< Video Power Profile
  AMDSMI_PWR_PROF_PRST_POWER_SAVING_MASK = 0x4,  //!< Power Saving Profile
  AMDSMI_PWR_PROF_PRST_COMPUTE_MASK = 0x8,       //!< Compute Saving Profile
  AMDSMI_PWR_PROF_PRST_VR_MASK = 0x10,           //!< VR Power Profile

  //!< 3D Full Screen Power Profile
  AMDSMI_PWR_PROF_PRST_3D_FULL_SCR_MASK = 0x20,
  AMDSMI_PWR_PROF_PRST_BOOTUP_DEFAULT = 0x40,    //!< Default Boot Up Profile
  AMDSMI_PWR_PROF_PRST_LAST = AMDSMI_PWR_PROF_PRST_BOOTUP_DEFAULT,

  //!< Invalid power profile
  AMDSMI_PWR_PROF_PRST_INVALID = 0xFFFFFFFFFFFFFFFF
} amdsmi_power_profile_preset_masks_t;
/// \cond Ignore in docs.
typedef amdsmi_power_profile_preset_masks_t amdsmi_power_profile_preset_masks;
/// \endcond

/**
 * @brief This enum is used to identify different GPU blocks.
 */
typedef enum {
  AMDSMI_GPU_BLOCK_INVALID =   0x0000000000000000,  //!< Used to indicate an
                                                  //!< invalid block
  AMDSMI_GPU_BLOCK_FIRST =     0x0000000000000001,

  AMDSMI_GPU_BLOCK_UMC = AMDSMI_GPU_BLOCK_FIRST,      //!< UMC block
  AMDSMI_GPU_BLOCK_SDMA =      0x0000000000000002,  //!< SDMA block
  AMDSMI_GPU_BLOCK_GFX =       0x0000000000000004,  //!< GFX block
  AMDSMI_GPU_BLOCK_MMHUB =     0x0000000000000008,  //!< MMHUB block
  AMDSMI_GPU_BLOCK_ATHUB =     0x0000000000000010,  //!< ATHUB block
  AMDSMI_GPU_BLOCK_PCIE_BIF =  0x0000000000000020,  //!< PCIE_BIF block
  AMDSMI_GPU_BLOCK_HDP =       0x0000000000000040,  //!< HDP block
  AMDSMI_GPU_BLOCK_XGMI_WAFL = 0x0000000000000080,  //!< XGMI block
  AMDSMI_GPU_BLOCK_DF =        0x0000000000000100,  //!< DF block
  AMDSMI_GPU_BLOCK_SMN =       0x0000000000000200,  //!< SMN block
  AMDSMI_GPU_BLOCK_SEM =       0x0000000000000400,  //!< SEM block
  AMDSMI_GPU_BLOCK_MP0 =       0x0000000000000800,  //!< MP0 block
  AMDSMI_GPU_BLOCK_MP1 =       0x0000000000001000,  //!< MP1 block
  AMDSMI_GPU_BLOCK_FUSE =      0x0000000000002000,  //!< Fuse block

  AMDSMI_GPU_BLOCK_LAST = AMDSMI_GPU_BLOCK_FUSE,       //!< The highest bit position
                                                  //!< for supported blocks
  AMDSMI_GPU_BLOCK_RESERVED =  0x8000000000000000
} amdsmi_gpu_block_t;
/// \cond Ignore in docs.
typedef amdsmi_gpu_block_t amdsmi_gpu_block;
/// \endcond

/**
 * @brief The current ECC state
 */
typedef enum {
  AMDSMI_RAS_ERR_STATE_NONE = 0,   //!< No current errors
  AMDSMI_RAS_ERR_STATE_DISABLED,   //!< ECC is disabled
  AMDSMI_RAS_ERR_STATE_PARITY,     //!< ECC errors present, but type unknown
  AMDSMI_RAS_ERR_STATE_SING_C,     //!< Single correctable error
  AMDSMI_RAS_ERR_STATE_MULT_UC,    //!< Multiple uncorrectable errors
  AMDSMI_RAS_ERR_STATE_POISON,     //!< Firmware detected error and isolated
                                 //!< page. Treat as uncorrectable.
  AMDSMI_RAS_ERR_STATE_ENABLED,    //!< ECC is enabled

  AMDSMI_RAS_ERR_STATE_LAST = AMDSMI_RAS_ERR_STATE_ENABLED,
  AMDSMI_RAS_ERR_STATE_INVALID = 0xFFFFFFFF
} amdsmi_ras_err_state_t;

/**
 * @brief Types of memory
 */
typedef enum {
  AMDSMI_MEM_TYPE_FIRST = 0,

  AMDSMI_MEM_TYPE_VRAM = AMDSMI_MEM_TYPE_FIRST,  //!< VRAM memory
  AMDSMI_MEM_TYPE_VIS_VRAM,                    //!< VRAM memory that is visible
  AMDSMI_MEM_TYPE_GTT,                         //!< GTT memory

  AMDSMI_MEM_TYPE_LAST = AMDSMI_MEM_TYPE_GTT
} amdsmi_memory_type_t;

/**
 * @brief The values of this enum are used as frequency identifiers.
 */
typedef enum {
  AMDSMI_FREQ_IND_MIN = 0,  //!< Index used for the minimum frequency value
  AMDSMI_FREQ_IND_MAX = 1,  //!< Index used for the maximum frequency value
  AMDSMI_FREQ_IND_INVALID = 0xFFFFFFFF  //!< An invalid frequency index
} amdsmi_freq_ind_t;
/// \cond Ignore in docs.
typedef amdsmi_freq_ind_t amdsmi_freq_ind;
/// \endcond

/**
 * @brief XGMI Status
 */
typedef enum {
  AMDSMI_XGMI_STATUS_NO_ERRORS = 0,
  AMDSMI_XGMI_STATUS_ERROR,
  AMDSMI_XGMI_STATUS_MULTIPLE_ERRORS,
} amdsmi_xgmi_status_t;

/**
 * @brief Bitfield used in various AMDSMI calls
 */
typedef uint64_t amdsmi_bit_field_t;
/// \cond Ignore in docs.
typedef amdsmi_bit_field_t amdsmi_bit_field;
/// \endcond

/**
 * @brief Reserved Memory Page States
 */
typedef enum {
  AMDSMI_MEM_PAGE_STATUS_RESERVED = 0,  //!< Reserved. This gpu page is reserved
                                      //!<  and not available for use
  AMDSMI_MEM_PAGE_STATUS_PENDING,       //!< Pending. This gpu page is marked
                                      //!<  as bad and will be marked reserved
                                      //!<  at the next window.
  AMDSMI_MEM_PAGE_STATUS_UNRESERVABLE   //!< Unable to reserve this page
} amdsmi_memory_page_status_t;

/**
 * @brief Types for IO Link
 */
typedef enum _AMDSMI_IO_LINK_TYPE {
  AMDSMI_IOLINK_TYPE_UNDEFINED      = 0,          //!< unknown type.
  AMDSMI_IOLINK_TYPE_PCIEXPRESS     = 1,          //!< PCI Express
  AMDSMI_IOLINK_TYPE_XGMI           = 2,          //!< XGMI
  AMDSMI_IOLINK_TYPE_NUMIOLINKTYPES,              //!< Number of IO Link types
  AMDSMI_IOLINK_TYPE_SIZE           = 0xFFFFFFFF  //!< Max of IO Link types
} AMDSMI_IO_LINK_TYPE;

/**
 * @brief The utilization counter type
 */
typedef enum {
  AMDSMI_UTILIZATION_COUNTER_FIRST = 0,
  //!< GFX Activity
  AMDSMI_COARSE_GRAIN_GFX_ACTIVITY  = AMDSMI_UTILIZATION_COUNTER_FIRST,
  AMDSMI_COARSE_GRAIN_MEM_ACTIVITY,    //!< Memory Activity
  AMDSMI_UTILIZATION_COUNTER_LAST = AMDSMI_COARSE_GRAIN_MEM_ACTIVITY
} AMDSMI_UTILIZATION_COUNTER_TYPE;

/**
 * @brief The utilization counter data
 */
typedef struct  {
  AMDSMI_UTILIZATION_COUNTER_TYPE type;   //!< Utilization counter type
  uint64_t value;                       //!< Utilization counter value
} amdsmi_utilization_counter_t;

/**
 * @brief Reserved Memory Page Record
 */
typedef struct {
  uint64_t page_address;                  //!< Start address of page
  uint64_t page_size;                     //!< Page size
  amdsmi_memory_page_status_t status;       //!< Page "reserved" status
} amdsmi_retired_page_record_t;

/**
 * @brief Number of possible power profiles that a system could support
 */
#define AMDSMI_MAX_NUM_POWER_PROFILES (sizeof(amdsmi_bit_field_t) * 8)

/**
 * @brief This structure contains information about which power profiles are
 * supported by the system for a given device, and which power profile is
 * currently active.
 */
typedef struct {
    /**
    * Which profiles are supported by this system
    */
    amdsmi_bit_field_t available_profiles;

    /**
    * Which power profile is currently active
    */
    amdsmi_power_profile_preset_masks_t current;

    /**
    * How many power profiles are available
    */
    uint32_t num_profiles;
} amdsmi_power_profile_status_t;
/// \cond Ignore in docs.
typedef amdsmi_power_profile_status_t amdsmi_power_profile_status;
/// \endcond

/**
 * @brief This structure holds information about clock frequencies.
 */
typedef struct {
    /**
     * The number of supported frequencies
     */
    uint32_t num_supported;

    /**
     * The current frequency index
     */
    uint32_t current;

    /**
     * List of frequencies.
     * Only the first num_supported frequencies are valid.
     */
    uint64_t frequency[AMDSMI_MAX_NUM_FREQUENCIES];
} amdsmi_frequencies_t;
/// \cond Ignore in docs.
typedef amdsmi_frequencies_t amdsmi_frequencies;
/// \endcond

/**
 * @brief This structure holds information about the possible PCIe
 * bandwidths. Specifically, the possible transfer rates and their
 * associated numbers of lanes are stored here.
 */
typedef struct {
    /**
     * Transfer rates (T/s) that are possible
     */
    amdsmi_frequencies_t transfer_rate;

    /**
     * List of lanes for corresponding transfer rate.
     * Only the first num_supported bandwidths are valid.
     */
    uint32_t lanes[AMDSMI_MAX_NUM_FREQUENCIES];
} amdsmi_pcie_bandwidth_t;

/// \cond Ignore in docs.
typedef amdsmi_pcie_bandwidth_t amdsmi_pcie_bandwidth;
/// \endcond

/**
 * @brief This structure holds version information.
 */
typedef struct {
    uint32_t major;     //!< Major version
    uint32_t minor;     //!< Minor version
    uint32_t patch;     //!< Patch, build  or stepping version
    const char *build;  //!< Build string
} amdsmi_version_t;
/// \cond Ignore in docs.
typedef amdsmi_version_t amdsmi_version;
/// \endcond

/**
 * @brief This structure represents a point on the frequency-voltage plane.
 */
typedef struct {
    uint64_t frequency;      //!< Frequency coordinate (in Hz)
    uint64_t voltage;        //!< Voltage coordinate (in mV)
} amdsmi_od_vddc_point_t;
/// \cond Ignore in docs.
typedef amdsmi_od_vddc_point_t amdsmi_od_vddc_point;
/// \endcond

/**
 * @brief This structure holds 2 ::amdsmi_range_t's, one for frequency and one for
 * voltage. These 2 ranges indicate the range of possible values for the
 * corresponding ::amdsmi_od_vddc_point_t.
 */
typedef struct {
    amdsmi_range_t freq_range;  //!< The frequency range for this VDDC Curve point
    amdsmi_range_t volt_range;  //!< The voltage range for this VDDC Curve point
} amdsmi_freq_volt_region_t;
/// \cond Ignore in docs.
typedef amdsmi_freq_volt_region_t amdsmi_freq_volt_region;
/// \endcond

/**
 * ::AMDSMI_NUM_VOLTAGE_CURVE_POINTS number of ::amdsmi_od_vddc_point_t's
 */
typedef struct {
    /**
     * Array of ::AMDSMI_NUM_VOLTAGE_CURVE_POINTS ::amdsmi_od_vddc_point_t's that
     * make up the voltage frequency curve points.
     */
    amdsmi_od_vddc_point_t vc_points[AMDSMI_NUM_VOLTAGE_CURVE_POINTS];
} amdsmi_od_volt_curve_t;
/// \cond Ignore in docs.
typedef amdsmi_od_volt_curve_t amdsmi_od_volt_curve;
/// \endcond

/**
 * @brief This structure holds the frequency-voltage values for a device.
 */
typedef struct {
  amdsmi_range_t curr_sclk_range;          //!< The current SCLK frequency range
  amdsmi_range_t curr_mclk_range;          //!< The current MCLK frequency range;
                                         //!< (upper bound only)
  amdsmi_range_t sclk_freq_limits;         //!< The range possible of SCLK values
  amdsmi_range_t mclk_freq_limits;         //!< The range possible of MCLK values

  /**
   * @brief The current voltage curve
   */
  amdsmi_od_volt_curve_t curve;
  uint32_t num_regions;                //!< The number of voltage curve regions
} amdsmi_od_volt_freq_data_t;
/// \cond Ignore in docs.
typedef amdsmi_od_volt_freq_data_t amdsmi_od_volt_freq_data;
/// \endcond


/**
 * @brief The following structures hold the gpu metrics values for a device.
 */

/**
 * @brief Size and version information of metrics data
 */
struct amd_metrics_table_header_t {
  // TODO(amd) Doxygen documents
  /// \cond Ignore in docs.
  uint16_t      structure_size;
  uint8_t       format_revision;
  uint8_t       content_revision;
  /// \endcond
};

/**
 * @brief The following structure holds the gpu metrics values for a device.
 */
// Below is the assumed version of gpu_metric data on the device. If the device
// is using this version, we can read data directly into amdsmi_gpu_metrics_t.
// If the device is using an older format, a conversion of formats will be
// required.
// DGPU targets have a format version of 1. APU targets have a format version of
// 2. Currently, only version 1 (DGPU) gpu_metrics is supported.
#define AMDSMI_GPU_METRICS_API_FORMAT_VER 1
// The content version increments when gpu_metrics is extended with new and/or
// existing field sizes are changed.
#define AMDSMI_GPU_METRICS_API_CONTENT_VER_1 1
#define AMDSMI_GPU_METRICS_API_CONTENT_VER_2 2
#define AMDSMI_GPU_METRICS_API_CONTENT_VER_3 3

// This should match NUM_HBM_INSTANCES
#define AMDSMI_NUM_HBM_INSTANCES 4

// Unit conversion factor for HBM temperatures
#define CENTRIGRADE_TO_MILLI_CENTIGRADE 1000

typedef struct {
// TODO(amd) Doxygen documents
  /// \cond Ignore in docs.
  struct amd_metrics_table_header_t common_header;

/* Temperature */
  uint16_t      temperature_edge;
  uint16_t      temperature_hotspot;
  uint16_t      temperature_mem;
  uint16_t      temperature_vrgfx;
  uint16_t      temperature_vrsoc;
  uint16_t      temperature_vrmem;

/* Utilization */
  uint16_t      average_gfx_activity;
  uint16_t      average_umc_activity;  // memory controller
  uint16_t      average_mm_activity;   // UVD or VCN

/* Power/Energy */
  uint16_t      average_socket_power;
  uint64_t      energy_accumulator;      // v1 mod. (32->64)

/* Driver attached timestamp (in ns) */
  uint64_t      system_clock_counter;   // v1 mod. (moved from top of struct)

/* Average clocks */
  uint16_t      average_gfxclk_frequency;
  uint16_t      average_socclk_frequency;
  uint16_t      average_uclk_frequency;
  uint16_t      average_vclk0_frequency;
  uint16_t      average_dclk0_frequency;
  uint16_t      average_vclk1_frequency;
  uint16_t      average_dclk1_frequency;

/* Current clocks */
  uint16_t      current_gfxclk;
  uint16_t      current_socclk;
  uint16_t      current_uclk;
  uint16_t      current_vclk0;
  uint16_t      current_dclk0;
  uint16_t      current_vclk1;
  uint16_t      current_dclk1;

/* Throttle status */
  uint32_t      throttle_status;

/* Fans */
  uint16_t      current_fan_speed;

/* Link width/speed */
  uint16_t       pcie_link_width;  // v1 mod.(8->16)
  uint16_t       pcie_link_speed;  // in 0.1 GT/s; v1 mod. (8->16)

  uint16_t       padding;          // new in v1

  uint32_t       gfx_activity_acc;   // new in v1
  uint32_t       mem_actvity_acc;     // new in v1
  uint16_t       temperature_hbm[AMDSMI_NUM_HBM_INSTANCES];  // new in v1
  /// \endcond
} amdsmi_gpu_metrics_t;

/**
 * @brief This structure holds error counts.
 */
typedef struct {
    uint64_t correctable_err;            //!< Accumulated correctable errors
    uint64_t uncorrectable_err;          //!< Accumulated uncorrectable errors
} amdsmi_error_count_t;

/**
 * @brief This structure contains information specific to a process.
 */
typedef struct {
    uint32_t process_id;      //!< Process ID
    uint32_t pasid;           //!< PASID
    uint64_t vram_usage;      //!< VRAM usage
    uint64_t sdma_usage;      //!< SDMA usage in microseconds
    uint32_t cu_occupancy;    //!< Compute Unit usage in percent
} amdsmi_process_info_t;

/**
 * @brief Opaque handle to function-support object
 */
typedef struct amdsmi_func_id_iter_handle * amdsmi_func_id_iter_handle_t;

//! Place-holder "variant" for functions that have don't have any variants,
//! but do have monitors or sensors.
#define AMDSMI_DEFAULT_VARIANT 0xFFFFFFFFFFFFFFFF

/**
 * @brief This union holds the value of an ::amdsmi_func_id_iter_handle_t. The
 * value may be a function name, or an ennumerated variant value of types
 * such as ::amdsmi_memory_type_t, ::amdsmi_temperature_metric_t, etc.
 */
typedef union amd_id {
        uint64_t id;           //!< uint64_t representation of value
        const char *name;      //!< name string (applicable to functions only)
        union {
            //!< Used for ::amdsmi_memory_type_t variants
            amdsmi_memory_type_t memory_type;
            //!< Used for ::amdsmi_temperature_metric_t variants
            amdsmi_temperature_metric_t temp_metric;
            //!< Used for ::amdsmi_event_type_t variants
            amdsmi_event_type_t evnt_type;
            //!< Used for ::amdsmi_event_group_t variants
            amdsmi_event_group_t evnt_group;
            //!< Used for ::amdsmi_clk_type_t variants
            amdsmi_clk_type_t clk_type;
            //!< Used for ::amdsmi_fw_block_t variants
            amdsmi_fw_block_t fw_block;
            //!< Used for ::amdsmi_gpu_block_t variants
            amdsmi_gpu_block_t gpu_block_type;
        };
} amdsmi_func_id_value_t;


/*****************************************************************************/
/** @defgroup InitShutAdmin Initialization and Shutdown
 *  These functions are used for initialization of AMD SMI and clean up when
 *  done.
 *  @{
 */
/**
 *  @brief Initialize AMD SMI.
 *
 *  @details When called, this initializes internal data structures,
 *  including those corresponding to sources of information that SMI provides.
 *
 *  @param[in] init_flags Bit flags that tell SMI how to initialze. Values of
 *  ::amdsmi_init_flags_t may be OR'd together and passed through @p init_flags
 *  to modify how AMDSMI initializes.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 */
amdsmi_status_t amdsmi_init(uint64_t init_flags);

/**
 *  @brief Shutdown AMD SMI.
 *
 *  @details Do any necessary clean up.
 */
amdsmi_status_t amdsmi_shut_down(void);

/** @} */  // end of InitShut

/*****************************************************************************/
/** @defgroup Discovery Queries
 *  These functions provide discovery of the sockets.
 *  @{
 */

amdsmi_status_t amdsmi_get_socket_handles(uint32_t *socket_count,
                amdsmi_socket_handle* socket_handles[]);
amdsmi_status_t amdsmi_get_socket_info(
                amdsmi_socket_handle socket_handle,
                char *name, size_t len);

amdsmi_status_t amdsmi_get_device_handles(amdsmi_socket_handle socket_handle,
                                    uint32_t *device_count,
                                    amdsmi_device_handle* device_handles[]);
amdsmi_status_t amdsmi_get_device_type(amdsmi_device_handle device_handle,
              device_type_t* device_type);



/** @} */  // end of Discovery


/*****************************************************************************/
/** @defgroup IDQuer Identifier Queries
 *  These functions provide identification information.
 *  @{
 */


/**
 *  @brief Get the device id associated with the device with provided device
 *  handler.
 *
 *  @details Given a device handle @p device_handle and a pointer to a uint32_t @p id,
 *  this function will write the device id value to the uint64_t pointed to by
 *  @p id. This ID is an identification of the type of device, so calling this
 *  function for different devices will give the same value if they are kind
 *  of device. Consequently, this function should not be used to distinguish
 *  one device from another. amdsmi_dev_pci_id_get() should be used to get a
 *  unique identifier.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] id a pointer to uint64_t to which the device id will be
 *  written
 * If this parameter is nullptr, this function will return
 * ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 * arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 * provided arguments.
 *
 * @retval ::AMDSMI_STATUS_SUCCESS call was successful
 * @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 * support this function with the given arguments
 * @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t amdsmi_dev_id_get(amdsmi_device_handle device_handle, uint16_t *id);

/**
 *  @brief Get the name string for a give vendor ID
 *
 *  @details Given a device handle @p device_handle, a pointer to a caller provided
 *  char buffer @p name, and a length of this buffer @p len, this function will
 *  write the name of the vendor (up to @p len characters) buffer @p name. The
 *  @p id may be a device vendor or subsystem vendor ID.
 *
 *  If the integer ID associated with the vendor is not found in one of the
 *  system files containing device name information (e.g.
 *  /usr/share/misc/pci.ids), then this function will return the hex vendor ID
 *  as a string. Updating the system name files can be accompplished with
 *  "sudo update-pciids".
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] name a pointer to a caller provided char buffer to which the
 *  name will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @param[in] len the length of the caller provided buffer @p name.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *  @retval ::AMDSMI_STATUS_INSUFFICIENT_SIZE is returned if @p len bytes is not
 *  large enough to hold the entire name. In this case, only @p len bytes will
 *  be written.
 *
 */
amdsmi_status_t amdsmi_dev_vendor_name_get(amdsmi_device_handle device_handle, char *name,
                                                                  size_t len);

/**
 *  @brief Get the vram vendor string of a gpu device.
 *
 *  @details Given a device handle @p device_handle, a pointer to a caller provided
 *  char buffer @p brand, and a length of this buffer @p len, this function
 *  will write the vram vendor of the device (up to @p len characters) to the
 *  buffer @p brand.
 *
 *  If the vram vendor for the device is not found as one of the values
 *  contained within amdsmi_dev_vram_vendor_get, then this function will return
 *  the string 'unknown' instead of the vram vendor.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] brand a pointer to a caller provided char buffer to which the
 *  vram vendor will be written
 *
 *  @param[in] len the length of the caller provided buffer @p brand.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *
 */
amdsmi_status_t amdsmi_dev_vram_vendor_get(amdsmi_device_handle device_handle, char *brand,
                                                                uint32_t len);

/**
 *  @brief Get the subsystem device id associated with the device with
 *  provided device handle.
 *
 *  @details Given a device handle @p device_handle and a pointer to a uint32_t @p id,
 *  this function will write the subsystem device id value to the uint64_t
 *  pointed to by @p id.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] id a pointer to uint64_t to which the subsystem device id
 *  will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t amdsmi_dev_subsystem_id_get(amdsmi_device_handle device_handle, uint16_t *id);

/**
 *  @brief Get the name string for the device subsytem
 *
 *  @details Given a device handle @p device_handle, a pointer to a caller provided
 *  char buffer @p name, and a length of this buffer @p len, this function
 *  will write the name of the device subsystem (up to @p len characters)
 *  to the buffer @p name.
 *
 *  If the integer ID associated with the sub-system is not found in one of the
 *  system files containing device name information (e.g.
 *  /usr/share/misc/pci.ids), then this function will return the hex sub-system
 *  ID as a string. Updating the system name files can be accompplished with
 *  "sudo update-pciids".
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] name a pointer to a caller provided char buffer to which the
 *  name will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.

 *  @param[in] len the length of the caller provided buffer @p name.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *  @retval ::AMDSMI_STATUS_INSUFFICIENT_SIZE is returned if @p len bytes is not
 *  large enough to hold the entire name. In this case, only @p len bytes will
 *  be written.
 *
 */
amdsmi_status_t
amdsmi_dev_subsystem_name_get(amdsmi_device_handle device_handle, char *name, size_t len);

/**
 *  @brief Get the drm minor number associated with this device
 *
 *  @details Given a device handle @p device_handle, find its render device file
 *  /dev/dri/renderDN where N corresponds to its minor number.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] minor a pointer to a uint32_t into which minor number will
 *  be copied
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *  @retval ::AMDSMI_STATUS_INIT_ERROR if failed to get minor number during
 *  initialization.
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t
amdsmi_dev_drm_render_minor_get(amdsmi_device_handle device_handle, uint32_t *minor);

/**
 *  @brief Get the device subsystem vendor id associated with the device with
 *  provided device handle.
 *
 *  @details Given a device handle @p device_handle and a pointer to a uint32_t @p id,
 *  this function will write the device subsystem vendor id value to the
 *  uint64_t pointed to by @p id.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] id a pointer to uint64_t to which the device subsystem vendor
 *  id will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 */
amdsmi_status_t amdsmi_dev_subsystem_vendor_id_get(amdsmi_device_handle device_handle, uint16_t *id);

/** @} */  // end of IDQuer

/*****************************************************************************/
/** @defgroup PCIeQuer PCIe Queries
 *  These functions provide information about PCIe.
 *  @{
 */
/**
 *  @brief Get the list of possible PCIe bandwidths that are available.
 *
 *  @details Given a device handle @p device_handle and a pointer to a to an
 *  ::amdsmi_pcie_bandwidth_t structure @p bandwidth, this function will fill in
 *  @p bandwidth with the possible T/s values and associated number of lanes,
 *  and indication of the current selection.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] bandwidth a pointer to a caller provided
 *  ::amdsmi_pcie_bandwidth_t structure to which the frequency information will be
 *  written
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *
 */
amdsmi_status_t
amdsmi_dev_pci_bandwidth_get(amdsmi_device_handle device_handle, amdsmi_pcie_bandwidth_t *bandwidth);

/**
 *  @brief Get the unique PCI device identifier associated for a device
 *
 *  @details Give a device handle @p device_handle and a pointer to a uint64_t @p
 *  bdfid, this function will write the Bus/Device/Function PCI identifier
 *  (BDFID) associated with device @p device_handle to the value pointed to by
 *  @p bdfid.
 *
 *  The format of @p bdfid will be as follows:
 *
 *      BDFID = ((DOMAIN & 0xffffffff) << 32) | ((BUS & 0xff) << 8) |
 *                                   ((DEVICE & 0x1f) <<3 ) | (FUNCTION & 0x7)
 *
 *  | Name     | Field   |
 *  ---------- | ------- |
 *  | Domain   | [64:32] |
 *  | Reserved | [31:16] |
 *  | Bus      | [15: 8] |
 *  | Device   | [ 7: 3] |
 *  | Function | [ 2: 0] |
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] bdfid a pointer to uint64_t to which the device bdfid value
 *  will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 */
amdsmi_status_t amdsmi_dev_pci_id_get(amdsmi_device_handle device_handle, uint64_t *bdfid);

/**
 *  @brief Get the NUMA node associated with a device
 *
 *  @details Given a device handle @p device_handle and a pointer to a uint32_t @p
 *  numa_node, this function will retrieve the NUMA node value associated
 *  with device @p device_handle and store the value at location pointed to by
 *  @p numa_node.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] numa_node pointer to location where NUMA node value will
 *  be written.
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 */
amdsmi_status_t amdsmi_topo_numa_affinity_get(amdsmi_device_handle device_handle, uint32_t *numa_node);

/**
 *  @brief Get PCIe traffic information
 *
 *  @details Give a device handle @p device_handle and pointers to a uint64_t's, @p
 *  sent, @p received and @p max_pkt_sz, this function will write the number
 *  of bytes sent and received in 1 second to @p sent and @p received,
 *  respectively. The maximum possible packet size will be written to
 *  @p max_pkt_sz.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] sent a pointer to uint64_t to which the number of bytes sent
 *  will be written in 1 second. If pointer is NULL, it will be ignored.
 *
 *  @param[inout] received a pointer to uint64_t to which the number of bytes
 *  received will be written. If pointer is NULL, it will be ignored.
 *
 *  @param[inout] max_pkt_sz a pointer to uint64_t to which the maximum packet
 *  size will be written. If pointer is NULL, it will be ignored.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 */
amdsmi_status_t amdsmi_dev_pci_throughput_get(amdsmi_device_handle device_handle, uint64_t *sent,
                                    uint64_t *received, uint64_t *max_pkt_sz);

/**
 *  @brief Get PCIe replay counter
 *
 *  @details Given a device handle @p device_handle and a pointer to a uint64_t @p
 *  counter, this function will write the sum of the number of NAK's received
 *  by the GPU and the NAK's generated by the GPU to memory pointed to by @p
 *  counter.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] counter a pointer to uint64_t to which the sum of the NAK's
 *  received and generated by the GPU is written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 */
amdsmi_status_t amdsmi_dev_pci_replay_counter_get(amdsmi_device_handle device_handle,
                                                           uint64_t *counter);

/** @} */  // end of PCIeQuer
/*****************************************************************************/
/** @defgroup PCIeCont PCIe Control
 *  These functions provide some control over PCIe.
 *  @{
 */

/**
 *  @brief Control the set of allowed PCIe bandwidths that can be used.
 *
 *  @details Given a device handle @p device_handle and a 64 bit bitmask @p bw_bitmask,
 *  this function will limit the set of allowable bandwidths. If a bit in @p
 *  bw_bitmask has a value of 1, then the frequency (as ordered in an
 *  ::amdsmi_frequencies_t returned by ::amdsmi_dev_gpu_clk_freq_get()) corresponding
 *  to that bit index will be allowed.
 *
 *  This function will change the performance level to
 *  ::AMDSMI_DEV_PERF_LEVEL_MANUAL in order to modify the set of allowable
 *  band_widths. Caller will need to set to ::AMDSMI_DEV_PERF_LEVEL_AUTO in order
 *  to get back to default state.
 *
 *  All bits with indices greater than or equal to the value of the
 *  ::amdsmi_frequencies_t::num_supported field of ::amdsmi_pcie_bandwidth_t will be
 *  ignored.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] bw_bitmask A bitmask indicating the indices of the
 *  bandwidths that are to be enabled (1) and disabled (0). Only the lowest
 *  ::amdsmi_frequencies_t::num_supported (of ::amdsmi_pcie_bandwidth_t) bits of
 *  this mask are relevant.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_PERMISSION function requires root access
 *
 */
amdsmi_status_t amdsmi_dev_pci_bandwidth_set(amdsmi_device_handle device_handle, uint64_t bw_bitmask);

/** @} */  // end of PCIeCont

/*****************************************************************************/
/** @defgroup PowerQuer Power Queries
 *  These functions provide information about power usage.
 *  @{
 */
/**
 *  @brief Get the average power consumption of the device with provided
 *  device handle.
 *
 *  @details Given a device handle @p device_handle and a pointer to a uint64_t
 *  @p power, this function will write the current average power consumption
 *  (in microwatts) to the uint64_t pointed to by @p power.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a device has more than one sensor, it could be greater than 0.
 *
 *  @param[inout] power a pointer to uint64_t to which the average power
 *  consumption will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 */
amdsmi_status_t
amdsmi_dev_power_ave_get(amdsmi_device_handle device_handle, uint32_t sensor_ind, uint64_t *power);

/**
 *  @brief Get the energy accumulator counter of the device with provided
 *  device handle.
 *
 *  @details Given a device handle @p device_handle, a pointer to a uint64_t
 *  @p power, and a pointer to a uint64_t @p timestamp, this function will write
 *  amount of energy consumed to the uint64_t pointed to by @p power,
 *  and the timestamp to the uint64_t pointed to by @p timestamp.
 *  The amdsmi_dev_power_ave_get() is an average of a short time. This function
 *  accumulates all energy consumed.
 *
 *  @param[in] device_handle a device handle
 *  @param[inout] counter_resolution resolution of the counter @p power in
 *  micro Joules
 *
 *  @param[inout] power a pointer to uint64_t to which the energy
 *  counter will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @param[inout] timestamp a pointer to uint64_t to which the timestamp
 *  will be written. Resolution: 1 ns.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 */
amdsmi_status_t
amdsmi_dev_energy_count_get(amdsmi_device_handle device_handle, uint64_t *power,
                          float *counter_resolution, uint64_t *timestamp);

/** @} */  // end of PowerQuer

/*****************************************************************************/
/** @defgroup PowerCont Power Control
 *  These functions provide ways to control power usage.
 *  @{
 */
/**
 *  @brief Set the power cap value
 *
 *  @details This function will set the power cap to the provided value @p cap.
 *  @p cap must be between the minimum and maximum power cap values set by the
 *  system, which can be obtained from ::amdsmi_dev_power_cap_range_get.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a device has more than one sensor, it could be greater than 0.
 *
 *  @param[in] cap a uint64_t that indicates the desired power cap, in
 *  microwatts
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *  @retval ::AMDSMI_STATUS_PERMISSION function requires root access
 *
 */
amdsmi_status_t
amdsmi_dev_power_cap_set(amdsmi_device_handle device_handle, uint32_t sensor_ind, uint64_t cap);

/**
 *  @brief Set the power profile
 *
 *  @details Given a device handle @p device_handle and a @p profile, this function will
 *  attempt to set the current profile to the provided profile. The provided
 *  profile must be one of the currently supported profiles, as indicated by a
 *  call to ::amdsmi_dev_power_profile_presets_get()
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] reserved Not currently used. Set to 0.
 *
 *  @param[in] profile a ::amdsmi_power_profile_preset_masks_t that hold the mask
 *  of the desired new power profile
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *  @retval ::AMDSMI_STATUS_PERMISSION function requires root access
 *
 */
amdsmi_status_t
amdsmi_dev_power_profile_set(amdsmi_device_handle device_handle, uint32_t reserved,
                                   amdsmi_power_profile_preset_masks_t profile);
/** @} */  // end of PowerCont
/*****************************************************************************/



/*****************************************************************************/
/** @defgroup MemQuer Memory Queries
 *  These functions provide information about memory systems.
 *  @{
 */

/**
 *  @brief Get the total amount of memory that exists
 *
 *  @details Given a device handle @p device_handle, a type of memory @p mem_type, and
 *  a pointer to a uint64_t @p total, this function will write the total amount
 *  of @p mem_type memory that exists to the location pointed to by @p total.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] mem_type The type of memory for which the total amount will be
 *  found
 *
 *  @param[inout] total a pointer to uint64_t to which the total amount of
 *  memory will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t
amdsmi_dev_memory_total_get(amdsmi_device_handle device_handle, amdsmi_memory_type_t mem_type,
                                                             uint64_t *total);

/**
 *  @brief Get the current memory usage
 *
 *  @details Given a device handle @p device_handle, a type of memory @p mem_type, and
 *  a pointer to a uint64_t @p usage, this function will write the amount of
 *  @p mem_type memory that that is currently being used to the location
 *  pointed to by @p used.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] mem_type The type of memory for which the amount being used will
 *  be found
 *
 *  @param[inout] used a pointer to uint64_t to which the amount of memory
 *  currently being used will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t
amdsmi_dev_memory_usage_get(amdsmi_device_handle device_handle, amdsmi_memory_type_t mem_type,
                                                              uint64_t *used);

/**
 *  @brief Get percentage of time any device memory is being used
 *
 *  @details Given a device handle @p device_handle, this function returns the
 *  percentage of time that any device memory is being used for the specified
 *  device.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] busy_percent a pointer to the uint32_t to which the busy
 *  percent will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t
amdsmi_dev_memory_busy_percent_get(amdsmi_device_handle device_handle, uint32_t *busy_percent);

/**
 *  @brief Get information about reserved ("retired") memory pages
 *
 *  @details Given a device handle @p device_handle, this function returns retired page
 *  information @p records corresponding to the device with the provided device
 *  handle @p device_handle. The number of retired page records is returned through @p
 *  num_pages. @p records may be NULL on input. In this case, the number of
 *  records available for retrieval will be returned through @p num_pages.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] num_pages a pointer to a uint32. As input, the value passed
 *  through this parameter is the number of ::amdsmi_retired_page_record_t's that
 *  may be safely written to the memory pointed to by @p records. This is the
 *  limit on how many records will be written to @p records. On return, @p
 *  num_pages will contain the number of records written to @p records, or the
 *  number of records that could have been written if enough memory had been
 *  provided.
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @param[inout] records A pointer to a block of memory to which the
 *  ::amdsmi_retired_page_record_t values will be written. This value may be NULL.
 *  In this case, this function can be used to query how many records are
 *  available to read.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *  @retval ::AMDSMI_STATUS_INSUFFICIENT_SIZE is returned if more records were available
 *  than allowed by the provided, allocated memory.
 */
amdsmi_status_t
amdsmi_dev_memory_reserved_pages_get(amdsmi_device_handle device_handle, uint32_t *num_pages,
                                         amdsmi_retired_page_record_t *records);
/** @} */  // end of MemQuer

/** @defgroup PhysQuer Physical State Queries
 *  These functions provide information about the physical characteristics of
 *  the device.
 *  @{
 */
/**
 *  @brief Get the fan speed in RPMs of the device with the specified device
 *  handle and 0-based sensor index.
 *
 *  @details Given a device handle @p device_handle and a pointer to a uint32_t
 *  @p speed, this function will write the current fan speed in RPMs to the
 *  uint32_t pointed to by @p speed
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a device has more than one sensor, it could be greater than 0.
 *
 *  @param[inout] speed a pointer to uint32_t to which the speed will be
 *  written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t amdsmi_dev_fan_rpms_get(amdsmi_device_handle device_handle, uint32_t sensor_ind,
                                                              int64_t *speed);

/**
 *  @brief Get the fan speed for the specified device as a value relative to
 *  ::AMDSMI_MAX_FAN_SPEED
 *
 *  @details Given a device handle @p device_handle and a pointer to a uint32_t
 *  @p speed, this function will write the current fan speed (a value
 *  between 0 and the maximum fan speed, ::AMDSMI_MAX_FAN_SPEED) to the uint32_t
 *  pointed to by @p speed
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a device has more than one sensor, it could be greater than 0.
 *
 *  @param[inout] speed a pointer to uint32_t to which the speed will be
 *  written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t amdsmi_dev_fan_speed_get(amdsmi_device_handle device_handle,
                                        uint32_t sensor_ind, int64_t *speed);

/**
 *  @brief Get the max. fan speed of the device with provided device handle.
 *
 *  @details Given a device handle @p device_handle and a pointer to a uint32_t
 *  @p max_speed, this function will write the maximum fan speed possible to
 *  the uint32_t pointed to by @p max_speed
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a device has more than one sensor, it could be greater than 0.
 *
 *  @param[inout] max_speed a pointer to uint32_t to which the maximum speed
 *  will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t amdsmi_dev_fan_speed_max_get(amdsmi_device_handle device_handle,
                                    uint32_t sensor_ind, uint64_t *max_speed);

/**
 *  @brief Get the temperature metric value for the specified metric, from the
 *  specified temperature sensor on the specified device.
 *
 *  @details Given a device handle @p device_handle, a sensor type @p sensor_type, a
 *  ::amdsmi_temperature_metric_t @p metric and a pointer to an int64_t @p
 *  temperature, this function will write the value of the metric indicated by
 *  @p metric and @p sensor_type to the memory location @p temperature.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] sensor_type part of device from which temperature should be
 *  obtained. This should come from the enum ::amdsmi_temperature_type_t
 *
 *  @param[in] metric enum indicated which temperature value should be
 *  retrieved
 *
 *  @param[inout] temperature a pointer to int64_t to which the temperature
 *  will be written, in millidegrees Celcius.
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t amdsmi_dev_temp_metric_get(amdsmi_device_handle device_handle, uint32_t sensor_type,
                      amdsmi_temperature_metric_t metric, int64_t *temperature);

/**
 *  @brief Get the voltage metric value for the specified metric, from the
 *  specified voltage sensor on the specified device.
 *
 *  @details Given a device handle @p device_handle, a sensor type @p sensor_type, a
 *  ::amdsmi_voltage_metric_t @p metric and a pointer to an int64_t @p
 *  voltage, this function will write the value of the metric indicated by
 *  @p metric and @p sensor_type to the memory location @p voltage.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] sensor_type part of device from which voltage should be
 *  obtained. This should come from the enum ::amdsmi_voltage_type_t
 *
 *  @param[in] metric enum indicated which voltage value should be
 *  retrieved
 *
 *  @param[inout] voltage a pointer to int64_t to which the voltage
 *  will be written, in millivolts.
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t amdsmi_dev_volt_metric_get(amdsmi_device_handle device_handle,
                               amdsmi_voltage_type_t sensor_type,
                              amdsmi_voltage_metric_t metric, int64_t *voltage);
/** @} */  // end of PhysQuer

/*****************************************************************************/
/** @defgroup PhysCont Physical State Control
 *  These functions provide control over the physical state of a device.
 *  @{
 */
/**
 *  @brief Reset the fan to automatic driver control
 *
 *  @details This function returns control of the fan to the system
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a device has more than one sensor, it could be greater than 0.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments

 */
amdsmi_status_t amdsmi_dev_fan_reset(amdsmi_device_handle device_handle, uint32_t sensor_ind);

/**
 *  @brief Set the fan speed for the specified device with the provided speed,
 *  in RPMs.
 *
 *  @details Given a device handle @p device_handle and a integer value indicating
 *  speed @p speed, this function will attempt to set the fan speed to @p speed.
 *  An error will be returned if the specified speed is outside the allowable
 *  range for the device. The maximum value is 255 and the minimum is 0.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a device has more than one sensor, it could be greater than 0.
 *
 *  @param[in] speed the speed to which the function will attempt to set the fan
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_PERMISSION function requires root access
 *
 */
amdsmi_status_t amdsmi_dev_fan_speed_set(amdsmi_device_handle device_handle, uint32_t sensor_ind,
                                                              uint64_t speed);

/** @} */  // end of PhysCont
/*****************************************************************************/
/** @defgroup PerfQuer Clock, Power and Performance Queries
 *  These functions provide information about clock frequencies and
 *  performance.
 *  @{
 */

/**
 *  @brief Get percentage of time device is busy doing any processing
 *
 *  @details Given a device handle @p device_handle, this function returns the
 *  percentage of time that the specified device is busy. The device is
 *  considered busy if any one or more of its sub-blocks are working, and idle
 *  if none of the sub-blocks are working.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] busy_percent a pointer to the uint32_t to which the busy
 *  percent will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t
amdsmi_dev_busy_percent_get(amdsmi_device_handle device_handle, uint32_t *busy_percent);

/**
 *  @brief Get coarse grain utilization counter of the specified device
 *
 *  @details Given a device handle @p device_handle, the array of the utilization counters,
 *  the size of the array, this function returns the coarse grain utilization counters
 *  and timestamp.
 *  The counter is the accumulated percentages. Every milliseconds the firmware calculates
 *  % busy count and then accumulates that value in the counter. This provides minimally
 *  invasive coarse grain GPU usage information.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] utilization_counters Multiple utilization counters can be retreived with a single
 *  call. The caller must allocate enough space to the utilization_counters array. The caller also
 *  needs to set valid AMDSMI_UTILIZATION_COUNTER_TYPE type for each element of the array.
 *  ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the provided arguments.
 *
 *  If the function reutrns AMDSMI_STATUS_SUCCESS, the counter will be set in the value field of
 *  the amdsmi_utilization_counter_t.
 *
 *  @param[in] count The size of @utilization_counters array.
 *
 *  @param[inout] timestamp The timestamp when the counter is retreived. Resolution: 1 ns.
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t
amdsmi_utilization_count_get(amdsmi_device_handle device_handle,
                amdsmi_utilization_counter_t utilization_counters[],
                uint32_t count,
                uint64_t *timestamp);

/**
 *  @brief Get the performance level of the device with provided
 *  device handle.
 *
 *  @details Given a device handle @p device_handle and a pointer to a uint32_t @p
 *  perf, this function will write the ::amdsmi_dev_perf_level_t to the uint32_t
 *  pointed to by @p perf
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] perf a pointer to ::amdsmi_dev_perf_level_t to which the
 *  performance level will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t amdsmi_dev_perf_level_get(amdsmi_device_handle device_handle,
                                                 amdsmi_dev_perf_level_t *perf);

/**
 *  @brief Enter performance determinism mode with provided device handle.
 *
 *  @details Given a device handle @p device_handle and @p clkvalue this function
 *  will enable performance determinism mode, which enforces a GFXCLK frequency
 *  SoftMax limit per GPU set by the user. This prevents the GFXCLK PLL from
 *  stretching when running the same workload on different GPUS, making
 *  performance variation minimal. This call will result in the performance
 *  level ::amdsmi_dev_perf_level_t of the device being
 *  ::AMDSMI_DEV_PERF_LEVEL_DETERMINISM.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] clkvalue Softmax value for GFXCLK in MHz.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */

amdsmi_status_t amdsmi_perf_determinism_mode_set(amdsmi_device_handle device_handle, uint64_t clkvalue);
/**
 *  @brief Get the overdrive percent associated with the device with provided
 *  device handle.
 *
 *  @details Given a device handle @p device_handle and a pointer to a uint32_t @p od,
 *  this function will write the overdrive percentage to the uint32_t pointed
 *  to by @p od
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] od a pointer to uint32_t to which the overdrive percentage
 *  will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */

amdsmi_status_t amdsmi_dev_overdrive_level_get(amdsmi_device_handle device_handle, uint32_t *od);

/**
 *  @brief Get the list of possible system clock speeds of device for a
 *  specified clock type.
 *
 *  @details Given a device handle @p device_handle, a clock type @p clk_type, and a
 *  pointer to a to an ::amdsmi_frequencies_t structure @p f, this function will
 *  fill in @p f with the possible clock speeds, and indication of the current
 *  clock speed selection.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] clk_type the type of clock for which the frequency is desired
 *
 *  @param[inout] f a pointer to a caller provided ::amdsmi_frequencies_t structure
 *  to which the frequency information will be written. Frequency values are in
 *  Hz.
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t amdsmi_dev_gpu_clk_freq_get(amdsmi_device_handle device_handle,
                             amdsmi_clk_type_t clk_type, amdsmi_frequencies_t *f);

/**
 *  @brief Reset the gpu associated with the device with provided device handle
 *
 *  @details Given a device handle @p device_handle, this function will reset the GPU
 *
 *  @param[in] device_handle a device handle
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t amdsmi_dev_gpu_reset(int32_t dv_ind);

/**
 *  @brief This function retrieves the voltage/frequency curve information
 *
 *  @details Given a device handle @p device_handle and a pointer to a
 *  ::amdsmi_od_volt_freq_data_t structure @p odv, this function will populate @p
 *  odv. See ::amdsmi_od_volt_freq_data_t for more details.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] odv a pointer to an ::amdsmi_od_volt_freq_data_t structure
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 */
amdsmi_status_t amdsmi_dev_od_volt_info_get(amdsmi_device_handle device_handle,
                                               amdsmi_od_volt_freq_data_t *odv);

/**
 *  @brief This function retrieves the gpu metrics information
 *
 *  @details Given a device handle @p device_handle and a pointer to a
 *  ::amdsmi_gpu_metrics_t structure @p pgpu_metrics, this function will populate
 *  @p pgpu_metrics. See ::amdsmi_gpu_metrics_t for more details.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] pgpu_metrics a pointer to an ::amdsmi_gpu_metrics_t structure
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 */
amdsmi_status_t amdsmi_dev_gpu_metrics_info_get(amdsmi_device_handle device_handle,
                                            amdsmi_gpu_metrics_t *pgpu_metrics);

/**
 *  @brief This function sets the clock range information
 *
 *  @details Given a device handle @p device_handle, a minimum clock value @p minclkvalue,
 *  a maximum clock value @p maxclkvalue and a clock type @p clkType this function
 *  will set the sclk|mclk range
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] minclkvalue value to apply to the clock range. Frequency values
 *  are in MHz.
 *
 *  @param[in] maxclkvalue value to apply to the clock range. Frequency values
 *  are in MHz.
 *
 *  @param[in] clkType AMDSMI_CLK_TYPE_SYS | AMDSMI_CLK_TYPE_MEM range type
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 */
amdsmi_status_t amdsmi_dev_clk_range_set(amdsmi_device_handle device_handle, uint64_t minclkvalue,
                                       uint64_t maxclkvalue,
                                       amdsmi_clk_type_t clkType);

/**
 *  @brief This function sets the clock frequency information
 *
 *  @details Given a device handle @p device_handle, a frequency level @p level,
 *  a clock value @p clkvalue and a clock type @p clkType this function
 *  will set the sclk|mclk range
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] level AMDSMI_FREQ_IND_MIN|AMDSMI_FREQ_IND_MAX to set the
 *  minimum (0) or maximum (1) speed.
 *
 *  @param[in] clkvalue value to apply to the clock range. Frequency values
 *  are in MHz.
 *
 *  @param[in] clkType AMDSMI_CLK_TYPE_SYS | AMDSMI_CLK_TYPE_MEM range type
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 */
amdsmi_status_t amdsmi_dev_od_clk_info_set(amdsmi_device_handle device_handle, amdsmi_freq_ind_t level,
                                       uint64_t clkvalue,
                                       amdsmi_clk_type_t clkType);

/**
 *  @brief This function sets  1 of the 3 voltage curve points.
 *
 *  @details Given a device handle @p device_handle, a voltage point @p vpoint
 *  and a voltage value @p voltvalue this function will set voltage curve point
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] vpoint voltage point [0|1|2] on the voltage curve
 *
 *  @param[in] clkvalue clock value component of voltage curve point.
 *  Frequency values are in MHz.
 *
 *  @param[in] voltvalue voltage value component of voltage curve point.
 *  Voltage is in mV.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 */
amdsmi_status_t amdsmi_dev_od_volt_info_set(amdsmi_device_handle device_handle, uint32_t vpoint,
                                        uint64_t clkvalue, uint64_t voltvalue);

/**
 *  @brief This function will retrieve the current valid regions in the
 *  frequency/voltage space.
 *
 *  @details Given a device handle @p device_handle, a pointer to an unsigned integer
 *  @p num_regions and a buffer of ::amdsmi_freq_volt_region_t structures, @p
 *  buffer, this function will populate @p buffer with the current
 *  frequency-volt space regions. The caller should assign @p buffer to memory
 *  that can be written to by this function. The caller should also
 *  indicate the number of ::amdsmi_freq_volt_region_t structures that can safely
 *  be written to @p buffer in @p num_regions.
 *
 *  The number of regions to expect this function provide (@p num_regions) can
 *  be obtained by calling ::amdsmi_dev_od_volt_info_get().
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] num_regions As input, this is the number of
 *  ::amdsmi_freq_volt_region_t structures that can be written to @p buffer. As
 *  output, this is the number of ::amdsmi_freq_volt_region_t structures that were
 *  actually written.
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @param[inout] buffer a caller provided buffer to which
 *  ::amdsmi_freq_volt_region_t structures will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 */
amdsmi_status_t amdsmi_dev_od_volt_curve_regions_get(amdsmi_device_handle device_handle,
                      uint32_t *num_regions, amdsmi_freq_volt_region_t *buffer);

/**
 *  @brief Get the list of available preset power profiles and an indication of
 *  which profile is currently active.
 *
 *  @details Given a device handle @p device_handle and a pointer to a
 *  ::amdsmi_power_profile_status_t @p status, this function will set the bits of
 *  the ::amdsmi_power_profile_status_t.available_profiles bit field of @p status to
 *  1 if the profile corresponding to the respective
 *  ::amdsmi_power_profile_preset_masks_t profiles are enabled. For example, if both
 *  the VIDEO and VR power profiles are available selections, then
 *  ::AMDSMI_PWR_PROF_PRST_VIDEO_MASK AND'ed with
 *  ::amdsmi_power_profile_status_t.available_profiles will be non-zero as will
 *  ::AMDSMI_PWR_PROF_PRST_VR_MASK AND'ed with
 *  ::amdsmi_power_profile_status_t.available_profiles. Additionally,
 *  ::amdsmi_power_profile_status_t.current will be set to the
 *  ::amdsmi_power_profile_preset_masks_t of the profile that is currently active.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a device has more than one sensor, it could be greater than 0.
 *
 *  @param[inout] status a pointer to ::amdsmi_power_profile_status_t that will be
 *  populated by a call to this function
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t
amdsmi_dev_power_profile_presets_get(amdsmi_device_handle device_handle, uint32_t sensor_ind,
                                         amdsmi_power_profile_status_t *status);

/** @} */  // end of PerfQuer
/*****************************************************************************/

/** @defgroup PerfCont Clock, Power and Performance Control
 *  These functions provide control over clock frequencies, power and
 *  performance.
 *  @{
 */
/**
 *  @brief Set the PowerPlay performance level associated with the device with
 *  provided device handle with the provided value.
 *
 *  @deprecated ::amdsmi_dev_perf_level_set_v1() is preferred, with an
 *  interface that more closely  matches the rest of the amd_smi API.
 *
 *  @details Given a device handle @p device_handle and an ::amdsmi_dev_perf_level_t @p
 *  perf_level, this function will set the PowerPlay performance level for the
 *  device to the value @p perf_lvl.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] perf_lvl the value to which the performance level should be set
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_PERMISSION function requires root access
 *
 */
amdsmi_status_t
amdsmi_dev_perf_level_set(int32_t dv_ind, amdsmi_dev_perf_level_t perf_lvl);

/**
 *  @brief Set the PowerPlay performance level associated with the device with
 *  provided device handle with the provided value.
 *
 *  @details Given a device handle @p device_handle and an ::amdsmi_dev_perf_level_t @p
 *  perf_level, this function will set the PowerPlay performance level for the
 *  device to the value @p perf_lvl.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] perf_lvl the value to which the performance level should be set
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_PERMISSION function requires root access
 *
 */
amdsmi_status_t
amdsmi_dev_perf_level_set_v1(amdsmi_device_handle device_handle, amdsmi_dev_perf_level_t perf_lvl);

/**
 *  @brief Set the overdrive percent associated with the device with provided
 *  device handle with the provided value. See details for WARNING.
 *
 *  @deprecated This function is deprecated. ::amdsmi_dev_overdrive_level_set_v1
 *  has the same functionaltiy, with an interface that more closely
 *  matches the rest of the amd_smi API.
 *
 *  @details Given a device handle @p device_handle and an overdrive level @p od,
 *  this function will set the overdrive level for the device to the value
 *  @p od. The overdrive level is an integer value between 0 and 20, inclusive,
 *  which represents the overdrive percentage; e.g., a value of 5 specifies
 *  an overclocking of 5%.
 *
 *  The overdrive level is specific to the gpu system clock.
 *
 *  The overdrive level is the percentage above the maximum Performance Level
 *  to which overclocking will be limited. The overclocking percentage does
 *  not apply to clock speeds other than the maximum. This percentage is
 *  limited to 20%.
 *
 *   ******WARNING******
 *  Operating your AMD GPU outside of official AMD specifications or outside of
 *  factory settings, including but not limited to the conducting of
 *  overclocking (including use of this overclocking software, even if such
 *  software has been directly or indirectly provided by AMD or otherwise
 *  affiliated in any way with AMD), may cause damage to your AMD GPU, system
 *  components and/or result in system failure, as well as cause other problems.
 *  DAMAGES CAUSED BY USE OF YOUR AMD GPU OUTSIDE OF OFFICIAL AMD SPECIFICATIONS
 *  OR OUTSIDE OF FACTORY SETTINGS ARE NOT COVERED UNDER ANY AMD PRODUCT
 *  WARRANTY AND MAY NOT BE COVERED BY YOUR BOARD OR SYSTEM MANUFACTURER'S
 *  WARRANTY. Please use this utility with caution.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] od the value to which the overdrive level should be set
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_PERMISSION function requires root access
 *
 */
amdsmi_status_t amdsmi_dev_overdrive_level_set(int32_t dv_ind, uint32_t od);

/**
 *  @brief Set the overdrive percent associated with the device with provided
 *  device handle with the provided value. See details for WARNING.
 *
 *  @details Given a device handle @p device_handle and an overdrive level @p od,
 *  this function will set the overdrive level for the device to the value
 *  @p od. The overdrive level is an integer value between 0 and 20, inclusive,
 *  which represents the overdrive percentage; e.g., a value of 5 specifies
 *  an overclocking of 5%.
 *
 *  The overdrive level is specific to the gpu system clock.
 *
 *  The overdrive level is the percentage above the maximum Performance Level
 *  to which overclocking will be limited. The overclocking percentage does
 *  not apply to clock speeds other than the maximum. This percentage is
 *  limited to 20%.
 *
 *   ******WARNING******
 *  Operating your AMD GPU outside of official AMD specifications or outside of
 *  factory settings, including but not limited to the conducting of
 *  overclocking (including use of this overclocking software, even if such
 *  software has been directly or indirectly provided by AMD or otherwise
 *  affiliated in any way with AMD), may cause damage to your AMD GPU, system
 *  components and/or result in system failure, as well as cause other problems.
 *  DAMAGES CAUSED BY USE OF YOUR AMD GPU OUTSIDE OF OFFICIAL AMD SPECIFICATIONS
 *  OR OUTSIDE OF FACTORY SETTINGS ARE NOT COVERED UNDER ANY AMD PRODUCT
 *  WARRANTY AND MAY NOT BE COVERED BY YOUR BOARD OR SYSTEM MANUFACTURER'S
 *  WARRANTY. Please use this utility with caution.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] od the value to which the overdrive level should be set
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_PERMISSION function requires root access
 *
 */
amdsmi_status_t amdsmi_dev_overdrive_level_set_v1(amdsmi_device_handle device_handle, uint32_t od);

/**
 * @brief Control the set of allowed frequencies that can be used for the
 * specified clock.
 *
 * @details Given a device handle @p device_handle, a clock type @p clk_type, and a
 * 64 bit bitmask @p freq_bitmask, this function will limit the set of
 * allowable frequencies. If a bit in @p freq_bitmask has a value of 1, then
 * the frequency (as ordered in an ::amdsmi_frequencies_t returned by
 * amdsmi_dev_gpu_clk_freq_get()) corresponding to that bit index will be
 * allowed.
 *
 * This function will change the performance level to
 * ::AMDSMI_DEV_PERF_LEVEL_MANUAL in order to modify the set of allowable
 * frequencies. Caller will need to set to ::AMDSMI_DEV_PERF_LEVEL_AUTO in order
 * to get back to default state.
 *
 * All bits with indices greater than or equal to
 * ::amdsmi_frequencies_t::num_supported will be ignored.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] clk_type the type of clock for which the set of frequencies
 *  will be modified
 *
 *  @param[in] freq_bitmask A bitmask indicating the indices of the
 *  frequencies that are to be enabled (1) and disabled (0). Only the lowest
 *  ::amdsmi_frequencies_t.num_supported bits of this mask are relevant.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_PERMISSION function requires root access
 *
 */
amdsmi_status_t amdsmi_dev_gpu_clk_freq_set(amdsmi_device_handle device_handle,
                             amdsmi_clk_type_t clk_type, uint64_t freq_bitmask);

/** @} */  // end of PerfCont

/*****************************************************************************/
/** @defgroup VersQuer Version Queries
 *  These functions provide version information about various subsystems.
 *  @{
 */

/**
 * @brief Get the build version information for the currently running build of
 * AMDSMI.
 *
 * @details  Get the major, minor, patch and build string for AMDSMI build
 * currently in use through @p version
 *
 * @param[inout] version A pointer to an ::amdsmi_version_t structure that will
 * be updated with the version information upon return.
 *
 * @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call
 *
 */
amdsmi_status_t
amdsmi_version_get(amdsmi_version_t *version);

/**
 *  @brief Get the driver version string for the current system.
 *
 *  @details Given a software component @p component, a pointer to a char
 *  buffer, @p ver_str, this function will write the driver version string
 *  (up to @p len characters) for the current system to @p ver_str. The caller
 *  must ensure that it is safe to write at least @p len characters to @p
 *  ver_str.
 *
 *  @param[in] component The component for which the version string is being
 *  requested
 *
 *  @param[inout] ver_str A pointer to a buffer of char's to which the version
 *  of @p component will be written
 *
 *  @param[in] len the length of the caller provided buffer @p name.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *  @retval ::AMDSMI_STATUS_INSUFFICIENT_SIZE is returned if @p len bytes is not
 *  large enough to hold the entire name. In this case, only @p len bytes will
 *  be written.
 */
amdsmi_status_t
amdsmi_version_str_get(amdsmi_sw_component_t component, char *ver_str,
                                                                uint32_t len);

/** @} */  // end of VersQuer

/*****************************************************************************/
/** @defgroup ErrQuer Error Queries
 *  These functions provide error information about AMDSMI calls as well as
 *  device errors.
 *  @{
 */

/**
 *  @brief Retrieve the error counts for a GPU block
 *
 *  @details Given a device handle @p device_handle, an ::amdsmi_gpu_block_t @p block and a
 *  pointer to an ::amdsmi_error_count_t @p ec, this function will write the error
 *  count values for the GPU block indicated by @p block to memory pointed to by
 *  @p ec.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] block The block for which error counts should be retrieved
 *
 *  @param[inout] ec A pointer to an ::amdsmi_error_count_t to which the error
 *  counts should be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t amdsmi_dev_ecc_count_get(amdsmi_device_handle device_handle,
                              amdsmi_gpu_block_t block, amdsmi_error_count_t *ec);

/**
 *  @brief Retrieve the enabled ECC bit-mask
 *
 *  @details Given a device handle @p device_handle, and a pointer to a uint64_t @p
 *  enabled_mask, this function will write bits to memory pointed to by
 *  @p enabled_blocks. Upon a successful call, @p enabled_blocks can then be
 *  AND'd with elements of the ::amdsmi_gpu_block_t ennumeration to determine if
 *  the corresponding block has ECC enabled. Note that whether a block has ECC
 *  enabled or not in the device is independent of whether there is kernel
 *  support for error counting for that block. Although a block may be enabled,
 *  but there may not be kernel support for reading error counters for that
 *  block.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] enabled_blocks A pointer to a uint64_t to which the enabled
 *  blocks bits will be written.
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 */
amdsmi_status_t amdsmi_dev_ecc_enabled_get(amdsmi_device_handle device_handle,
                                                    uint64_t *enabled_blocks);

/**
 *  @brief Retrieve the ECC status for a GPU block
 *
 *  @details Given a device handle @p device_handle, an ::amdsmi_gpu_block_t @p block and
 *  a pointer to an ::amdsmi_ras_err_state_t @p state, this function will write
 *  the current state for the GPU block indicated by @p block to memory pointed
 *  to by @p state.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] block The block for which error counts should be retrieved
 *
 *  @param[inout] state A pointer to an ::amdsmi_ras_err_state_t to which the
 *  ECC state should be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t amdsmi_dev_ecc_status_get(amdsmi_device_handle device_handle, amdsmi_gpu_block_t block,
                                                  amdsmi_ras_err_state_t *state);
/**
 *  @brief Get a description of a provided AMDSMI error status
 *
 *  @details Set the provided pointer to a const char *, @p status_string, to
 *  a string containing a description of the provided error code @p status.
 *
 *  @param[in] status The error status for which a description is desired
 *
 *  @param[inout] status_string A pointer to a const char * which will be made
 *  to point to a description of the provided error code
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call
 *
 */
amdsmi_status_t
amdsmi_status_string(amdsmi_status_t status, const char **status_string);

/** @} */  // end of ErrQuer

/*****************************************************************************/
/** @defgroup PerfCntr Performance Counter Functions
 *  These functions are used to configure, query and control performance
 *  counting.
 *
 *  These functions use the same mechanisms as the "perf" command line
 *  utility. They share the same underlying resources and have some similarities
 *  in how they are used. The events supported by this API should have
 *  corresponding perf events that can be seen with "perf stat ...". The events
 *  supported by perf can be seen with "perf list"
 *
 *  The types of events available and the ability to count those
 *  events are dependent on which device is being targeted and if counters are
 *  still available for that device, respectively.
 *  ::amdsmi_dev_counter_group_supported() can be used to see which event types
 *  (::amdsmi_event_group_t) are supported for a given device. Assuming a device
 *  supports a given event type, we can then check to see if there are counters
 *  available to count a specific event with
 *  ::amdsmi_counter_available_counters_get(). Counters may be occupied by other
 *  perf based programs.
 *
 *  Once it is determined that events are supported and counters are available,
 *  an event counter can be created/destroyed and controlled.
 *
 *  ::amdsmi_dev_counter_create() allocates internal data structures that will be
 *  used to used to control the event counter, and return a handle to this data
 *  structure.
 *
 *  Once an event counter handle is obtained, the event counter can be
 *  controlled (i.e., started, stopped,...) with ::amdsmi_counter_control() by
 *  passing ::amdsmi_counter_command_t commands. ::AMDSMI_CNTR_CMD_START starts an
 *  event counter and ::AMDSMI_CNTR_CMD_STOP stops a counter.
 *  ::amdsmi_counter_read() reads an event counter.
 *
 *  Once the counter is no longer needed, the resources it uses should be freed
 *  by calling ::amdsmi_dev_counter_destroy().
 *
 *
 *  Important Notes about Counter Values
 *  ====================================
 *  - A running "absolute" counter is kept internally. For the discussion that
 *  follows, we will call the internal counter value at time \a t \a
 *  val<sub>t</sub>
 *  - Issuing ::AMDSMI_CNTR_CMD_START or calling ::amdsmi_counter_read(), causes
 *  AMDSMI (in kernel) to internally record the current absolute counter value
 *  - ::amdsmi_counter_read() returns the number of events that have occurred
 *  since the previously recorded value (ie, a relative value,
 *  \a val<sub>t</sub> - val<sub>t-1</sub>) from the issuing of
 *  ::AMDSMI_CNTR_CMD_START or calling ::amdsmi_counter_read()
 *
 *  Example of event counting sequence:
 *
 *  \latexonly
 *  \pagebreak
 *  \endlatexonly
 *  \code{.cpp}
 *
 *    amdsmi_counter_value_t value;
 *
 *    // Determine if AMDSMI_EVNT_GRP_XGMI is supported for device dv_ind
 *    ret = amdsmi_dev_counter_group_supported(dv_ind, AMDSMI_EVNT_GRP_XGMI);
 *
 *    // See if there are counters available for device dv_ind for event
 *    // AMDSMI_EVNT_GRP_XGMI
 *
 *    ret = amdsmi_counter_available_counters_get(dv_ind,
 *                                 AMDSMI_EVNT_GRP_XGMI, &counters_available);
 *
 *    // Assuming AMDSMI_EVNT_GRP_XGMI is supported and there is at least 1
 *    // counter available for AMDSMI_EVNT_GRP_XGMI on device dv_ind, create
 *    // an event object for an event of group AMDSMI_EVNT_GRP_XGMI (e.g.,
 *    // AMDSMI_EVNT_XGMI_0_BEATS_TX) and get the handle
 *    // (amdsmi_event_handle_t).
 *
 *    ret = amdsmi_dev_counter_create(dv_ind, AMDSMI_EVNT_XGMI_0_BEATS_TX,
 *                                                          &evnt_handle);
 *
 *    // A program that generates the events of interest can be started
 *    // immediately before or after starting the counters.
 *    // Start counting:
 *    ret = amdsmi_counter_control(evnt_handle, AMDSMI_CNTR_CMD_START, NULL);
 *
 *    // Wait...
 *
 *    // Get the number of events since AMDSMI_CNTR_CMD_START was issued:
 *    ret = amdsmi_counter_read(amdsmi_event_handle_t evt_handle, &value)
 *
 *    // Wait...
 *
 *    // Get the number of events since amdsmi_counter_read() was last called:
 *    ret = amdsmi_counter_read(amdsmi_event_handle_t evt_handle, &value)
 *
 *    // Stop counting.
 *    ret = amdsmi_counter_control(evnt_handle, AMDSMI_CNTR_CMD_STOP, NULL);
 *
 *    // Release all resources (e.g., counter and memory resources) associated
 *    with evnt_handle.
 *    ret = amdsmi_dev_counter_destroy(evnt_handle);
 *  \endcode
 *  @{
 */

/**
 *  @brief Tell if an event group is supported by a given device
 *
 *  @details Given a device handle @p device_handle and an event group specifier @p
 *  group, tell if @p group type events are supported by the device associated
 *  with @p device_handle
 *
 *  @param[in] dv_ind device handle of device being queried
 *
 *  @param[in] group ::amdsmi_event_group_t identifier of group for which support
 *  is being queried
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS if the device associatee with @p device_handle
 *  support counting events of the type indicated by @p group.
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  group
 *
 */
amdsmi_status_t
amdsmi_dev_counter_group_supported(amdsmi_device_handle device_handle, amdsmi_event_group_t group);

/**
 *  @brief Create a performance counter object
 *
 *  @details Create a performance counter object of type @p type for the device
 *  with a device handle of @p device_handle, and write a handle to the object to the
 *  memory location pointed to by @p evnt_handle. @p evnt_handle can be used
 *  with other performance event operations. The handle should be deallocated
 *  with ::amdsmi_dev_counter_destroy() when no longer needed.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] type the ::amdsmi_event_type_t of performance event to create
 *
 *  @param[inout] evnt_handle A pointer to a ::amdsmi_event_handle_t which will be
 *  associated with a newly allocated counter
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *  @retval ::AMDSMI_STATUS_OUT_OF_RESOURCES unable to allocate memory for counter
 *  @retval ::AMDSMI_STATUS_PERMISSION function requires root access
 *
 */
amdsmi_status_t
amdsmi_dev_counter_create(amdsmi_device_handle device_handle, amdsmi_event_type_t type,
                                            amdsmi_event_handle_t *evnt_handle);

/**
 *  @brief Deallocate a performance counter object
 *
 *  @details Deallocate the performance counter object with the provided
 *  ::amdsmi_event_handle_t @p evnt_handle
 *
 *  @param[in] evnt_handle handle to event object to be deallocated
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *  @retval ::AMDSMI_STATUS_PERMISSION function requires root access
 *
 */
amdsmi_status_t
amdsmi_dev_counter_destroy(amdsmi_event_handle_t evnt_handle);

/**
 *  @brief Issue performance counter control commands
 *
 *  @details Issue a command @p cmd on the event counter associated with the
 *  provided handle @p evt_handle.
 *
 *  @param[in] evt_handle an event handle
 *
 *  @param[in] cmd The event counter command to be issued
 *
 *  @param[inout] cmd_args Currently not used. Should be set to NULL.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *  @retval ::AMDSMI_STATUS_PERMISSION function requires root access
 *
 */
amdsmi_status_t
amdsmi_counter_control(amdsmi_event_handle_t evt_handle,
                                  amdsmi_counter_command_t cmd, void *cmd_args);

/**
 *  @brief Read the current value of a performance counter
 *
 *  @details Read the current counter value of the counter associated with the
 *  provided handle @p evt_handle and write the value to the location pointed
 *  to by @p value.
 *
 *  @param[in] evt_handle an event handle
 *
 *  @param[inout] value pointer to memory of size of ::amdsmi_counter_value_t to
 *  which the counter value will be written
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *  @retval ::AMDSMI_STATUS_PERMISSION function requires root access
 *
 */
amdsmi_status_t
amdsmi_counter_read(amdsmi_event_handle_t evt_handle,
                                                 amdsmi_counter_value_t *value);

/**
 *  @brief Get the number of currently available counters
 *
 *  @details Given a device handle @p device_handle, a performance event group @p grp,
 *  and a pointer to a uint32_t @p available, this function will write the
 *  number of @p grp type counters that are available on the device with handle
 *  @p device_handle to the memory that @p available points to.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[in] grp an event device group
 *
 *  @param[inout] available A pointer to a uint32_t to which the number of
 *  available counters will be written
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t
amdsmi_counter_available_counters_get(amdsmi_device_handle device_handle,
                                 amdsmi_event_group_t grp, uint32_t *available);
/** @} */  // end of PerfCntr

/*****************************************************************************/
/** @defgroup SysInfo System Information Functions
 *  These functions are used to configure, query and control performance
 *  counting.
 *  @{
 */

/**
 *  @brief Get process information about processes currently using GPU
 *
 *  @details Given a non-NULL pointer to an array @p procs of
 *  ::amdsmi_process_info_t's, of length *@p num_items, this function will write
 *  up to *@p num_items instances of ::amdsmi_process_info_t to the memory pointed
 *  to by @p procs. These instances contain information about each process
 *  utilizing a GPU. If @p procs is not NULL, @p num_items will be updated with
 *  the number of processes actually written. If @p procs is NULL, @p num_items
 *  will be updated with the number of processes for which there is current
 *  process information. Calling this function with @p procs being NULL is a way
 *  to determine how much memory should be allocated for when @p procs is not
 *  NULL.
 *
 *  @param[inout] procs a pointer to memory provided by the caller to which
 *  process information will be written. This may be NULL in which case only @p
 *  num_items will be updated with the number of processes found.
 *
 *  @param[inout] num_items A pointer to a uint32_t, which on input, should
 *  contain the amount of memory in ::amdsmi_process_info_t's which have been
 *  provided by the @p procs argument. On output, if @p procs is non-NULL, this
 *  will be updated with the number ::amdsmi_process_info_t structs actually
 *  written. If @p procs is NULL, this argument will be updated with the number
 *  processes for which there is information.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *  @retval ::AMDSMI_STATUS_INSUFFICIENT_SIZE is returned if there were more
 *  processes for which information was available, but not enough space was
 *  provided as indicated by @p procs and @p num_items, on input.
 */
amdsmi_status_t
amdsmi_compute_process_info_get(amdsmi_process_info_t *procs, uint32_t *num_items);

/**
 *  @brief Get process information about a specific process
 *
 *  @details Given a pointer to an ::amdsmi_process_info_t @p proc and a process
 *  id
 *  @p pid, this function will write the process information for @p pid, if
 *  available, to the memory pointed to by @p proc.
 *
 *  @param[in] pid The process ID for which process information is being
 *  requested
 *
 *  @param[inout] proc a pointer to a ::amdsmi_process_info_t to which
 *  process information for @p pid will be written if it is found.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *  @retval ::AMDSMI_STATUS_NOT_FOUND is returned if there was no process
 *  information
 *  found for the provided @p pid
 *
 */
amdsmi_status_t
amdsmi_compute_process_info_by_pid_get(uint32_t pid, amdsmi_process_info_t *proc);

/**
 *  @brief Get the device indices currently being used by a process
 *
 *  @details Given a process id @p pid, a non-NULL pointer to an array of
 *  uint32_t's @p device_handleices of length *@p num_devices, this function will
 *  write up to @p num_devices device indices to the memory pointed to by
 *  @p device_handleices. If @p device_handleices is not NULL, @p num_devices will be
 *  updated with the number of gpu's currently being used by process @p pid.
 *  If @p device_handleices is NULL, @p device_handleices will be updated with the number of
 *  gpus currently being used by @p pid. Calling this function with @p
 *  dv_indices being NULL is a way to determine how much memory is required
 *  for when @p device_handleices is not NULL.
 *
 *  @param[in] pid The process id of the process for which the number of gpus
 *  currently being used is requested
 *
 *  @param[inout] dv_indices a pointer to memory provided by the caller to
 *  which indices of devices currently being used by the process will be
 *  written. This may be NULL in which case only @p num_devices will be
 *  updated with the number of devices being used.
 *
 *  @param[inout] num_devices A pointer to a uint32_t, which on input, should
 *  contain the amount of memory in uint32_t's which have been provided by the
 *  @p device_handleices argument. On output, if @p device_handleices is non-NULL, this will
 *  be updated with the number uint32_t's actually written. If @p device_handleices is
 *  NULL, this argument will be updated with the number devices being used.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *  @retval ::AMDSMI_STATUS_INSUFFICIENT_SIZE is returned if there were more
 *  gpu indices that could have been written, but not enough space was
 *  provided as indicated by @p device_handleices and @p num_devices, on input.
 *
 */
amdsmi_status_t
amdsmi_compute_process_gpus_get(uint32_t pid, uint32_t *dv_indices,
                                                       uint32_t *num_devices);

/** @} */  // end of SysInfo

/*****************************************************************************/
/** @defgroup XGMIInfo XGMI Functions
 *  These functions are used to configure, query and control XGMI.
 *  @{
 */

/**
 *  @brief Retrieve the XGMI error status for a device
 *
 *  @details Given a device handle @p device_handle, and a pointer to an
 *  ::amdsmi_xgmi_status_t @p status, this function will write the current XGMI
 *  error state ::amdsmi_xgmi_status_t for the device @p device_handle to the memory
 *  pointed to by @p status.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] status A pointer to an ::amdsmi_xgmi_status_t to which the
 *  XGMI error state should be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVALID_ARGS if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_NOT_SUPPORTED installed software or hardware does not
 *  support this function with the given arguments
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t
amdsmi_dev_xgmi_error_status(amdsmi_device_handle device_handle, amdsmi_xgmi_status_t *status);

/**
 * @brief Reset the XGMI error status for a device
 *
 * @details Given a device handle @p device_handle, this function will reset the
 * current XGMI error state ::amdsmi_xgmi_status_t for the device @p device_handle to
 * amdsmi_xgmi_status_t::AMDSMI_XGMI_STATUS_NO_ERRORS
 *
 * @param[in] device_handle a device handle
 *
 * @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *
 */
amdsmi_status_t
amdsmi_dev_xgmi_error_reset(amdsmi_device_handle device_handle);

/** @} */  // end of SysInfo

/*****************************************************************************/
/** @defgroup HWTopo Hardware Topology Functions
 *  These functions are used to query Hardware topology.
 *  @{
 */

/**
 *  @brief Retrieve the NUMA CPU node number for a device
 *
 *  @details Given a device handle @p device_handle, and a pointer to an
 *  uint32_t @p numa_node, this function will write the
 *  node number of NUMA CPU for the device @p device_handle to the memory
 *  pointed to by @p numa_node.
 *
 *  @param[in] device_handle a device handle
 *
 *  @param[inout] numa_node A pointer to an uint32_t to which the
 *  numa node number should be written.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t
amdsmi_topo_get_numa_node_number(amdsmi_device_handle device_handle, uint32_t *numa_node);

/**
 *  @brief Retrieve the weight for a connection between 2 GPUs
 *
 *  @details Given a source device handle @p device_handle_src and
 *  a destination device handle @p device_handle_dst, and a pointer to an
 *  uint64_t @p weight, this function will write the
 *  weight for the connection between the device @p device_handle_src
 *  and @p device_handle_dst to the memory pointed to by @p weight.
 *
 *  @param[in] dv_ind_src the source device handle
 *
 *  @param[in] dv_ind_dst the destination device handle
 *
 *  @param[inout] weight A pointer to an uint64_t to which the
 *  weight for the connection should be written.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t
amdsmi_topo_get_link_weight(amdsmi_device_handle device_handle_src, amdsmi_device_handle device_handle_dst,
                          uint64_t *weight);

/**
 *  @brief Retreive minimal and maximal io link bandwidth between 2 GPUs
 *
 *  @details Given a source device handle @p device_handle_src and
 *  a destination device handle @p device_handle_dst,  pointer to an
 *  uint64_t @p min_bandwidth, and a pointer to uint64_t @p max_bandiwidth,
 *  this function will write theoretical minimal and maximal bandwidth limits.
 *  API works if src and dst are connected via xgmi and have 1 hop distance.
 *
 *  @param[in] dv_ind_src the source device handle
 *
 *  @param[in] dv_ind_dst the destination device handle
 *
 *  @param[inout] min_bandwidth A pointer to an uint64_t to which the
 *  minimal bandwidth for the connection should be written.
 *
 *  @param[inout] max_bandwidth A pointer to an uint64_t to which the
 *  maximal bandwidth for the connection should be written.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 */
amdsmi_status_t
amdsmi_minmax_bandwidth_get(amdsmi_device_handle device_handle_src, amdsmi_device_handle device_handle_dst,
                          uint64_t *min_bandwidth, uint64_t *max_bandwidth);

/**
 *  @brief Retrieve the hops and the connection type between 2 GPUs
 *
 *  @details Given a source device handle @p device_handle_src and
 *  a destination device handle @p device_handle_dst, and a pointer to an
 *  uint64_t @p hops and a pointer to an AMDSMI_IO_LINK_TYPE @p type,
 *  this function will write the number of hops and the connection type
 *  between the device @p device_handle_src and @p device_handle_dst to the memory
 *  pointed to by @p hops and @p type.
 *
 *  @param[in] dv_ind_src the source device handle
 *
 *  @param[in] dv_ind_dst the destination device handle
 *
 *  @param[inout] hops A pointer to an uint64_t to which the
 *  hops for the connection should be written.
 *
 *  @param[inout] type A pointer to an ::AMDSMI_IO_LINK_TYPE to which the
 *  type for the connection should be written.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t
amdsmi_topo_get_link_type(amdsmi_device_handle device_handle_src, amdsmi_device_handle device_handle_dst,
                        uint64_t *hops, AMDSMI_IO_LINK_TYPE *type);

/**
 *  @brief Return P2P availability status between 2 GPUs
 *
 *  @details Given a source device handle @p device_handle_src and
 *  a destination device handle @p device_handle_dst, and a pointer to a
 *  bool @accessible, this function will write the P2P connection status
 *  between the device @p device_handle_src and @p device_handle_dst to the memory
 *  pointed to by @p accessible.
 *
 *  @param[in] dv_ind_src the source device handle
 *
 *  @param[in] dv_ind_dst the destination device handle
 *
 *  @param[inout] accessible A pointer to a bool to which the status for
 *  the P2P connection availablity should be written.
 *
 *  @retval ::AMDSMI_STATUS_SUCCESS call was successful
 *  @retval ::AMDSMI_STATUS_INVALID_ARGS the provided arguments are not valid
 *
 */
amdsmi_status_t
amdsmi_is_P2P_accessible(amdsmi_device_handle device_handle_src, amdsmi_device_handle device_handle_dst,
                       bool *accessible);

/** @} */  // end of HWTopo

/*****************************************************************************/
/** @defgroup APISupport Supported Functions
 *  API function support varies by both GPU type and the version of the
 *  installed ROCm stack.  The functions described in this section can be used
 *  to determine, up front, which functions are supported for a given device
 *  on a system. If such "up front" knowledge of support for a function is not
 *  needed, alternatively, one can call a device related function and check the
 *  return code.
 *
 *  Some functions have several variations ("variants") where some variants are
 *  supported and others are not. For example, on a given device,
 *  ::amdsmi_dev_temp_metric_get may support some types of temperature metrics
 *  (e.g., ::AMDSMI_TEMP_CRITICAL_HYST), but not others
 *  (e.g., ::AMDSMI_TEMP_EMERGENCY).
 *
 *  In addition to a top level of variant support for a function, a function
 *  may have varying support for monitors/sensors. These are considered
 *  "sub-variants" in functions described in this section. Continuing the
 *  ::amdsmi_dev_temp_metric_get example, if variant
 *  ::AMDSMI_TEMP_CRITICAL_HYST is supported, perhaps
 *  only the sub-variant sensors ::AMDSMI_TEMP_TYPE_EDGE
 *  and ::AMDSMI_TEMP_TYPE_EDGE are supported, but not
 *  ::AMDSMI_TEMP_TYPE_MEMORY.
 *
 *  In cases where a function takes in a sensor id parameter but does not have
 *  any "top level" variants, the functions in this section will indicate a
 *  default "variant", ::AMDSMI_DEFAULT_VARIANT, for the top level variant, and
 *  the various monitor support will be sub-variants of this.
 *
 *  The functions in this section use the "iterator" concept to list which
 *  functions are supported; to list which variants of the supported functions
 *  are supported; and finally which monitors/sensors are supported for a
 *  variant.
 *
 *  Here is example code that prints out all supported functions, their
 *  supported variants and sub-variants. Please see the related descriptions
 *  functions and AMDSMI types.
 *  \latexonly
 *  \pagebreak
 *  \endlatexonly
 *  \code{.cpp}
 *     amdsmi_func_id_iter_handle_t iter_handle, var_iter, sub_var_iter;
 *     amdsmi_func_id_value_t value;
 *     amdsmi_status_t err;
 *
 *     for (uint32_t i = 0; i < <number of devices>; ++i) {
 *      std::cout << "Supported AMDSMI Functions:" << std::endl;
 *      std::cout << "\tVariants (Monitors)" << std::endl;
 *
 *      err = amdsmi_dev_supported_func_iterator_open(i, &iter_handle);
 *
 *      while (1) {
 *        err = amdsmi_func_iter_value_get(iter_handle, &value);
 *        std::cout << "Function Name: " << value.name << std::endl;
 *
 *        err = amdsmi_dev_supported_variant_iterator_open(iter_handle, &var_iter);
 *        if (err != AMDSMI_STATUS_NO_DATA) {
 *          std::cout << "\tVariants/Monitors: ";
 *          while (1) {
 *            err = amdsmi_func_iter_value_get(var_iter, &value);
 *            if (value.id == AMDSMI_DEFAULT_VARIANT) {
 *              std::cout << "Default Variant ";
 *            } else {
 *              std::cout << value.id;
 *            }
 *            std::cout << " (";
 *
 *            err =
 *              amdsmi_dev_supported_variant_iterator_open(var_iter, &sub_var_iter);
 *            if (err != AMDSMI_STATUS_NO_DATA) {
 *
 *              while (1) {
 *                err = amdsmi_func_iter_value_get(sub_var_iter, &value);
 *                std::cout << value.id << ", ";
 *
 *                err = amdsmi_func_iter_next(sub_var_iter);
 *
 *                if (err == AMDSMI_STATUS_NO_DATA) {
 *                  break;
 *                }
 *              }
 *              err = amdsmi_dev_supported_func_iterator_close(&sub_var_iter);
 *            }
 *
 *            std::cout << "), ";
 *
 *            err = amdsmi_func_iter_next(var_iter);
 *
 *            if (err == AMDSMI_STATUS_NO_DATA) {
 *              break;
 *            }
 *          }
 *          std::cout << std::endl;
 *
 *          err = amdsmi_dev_supported_func_iterator_close(&var_iter);
 *        }
 *
 *        err = amdsmi_func_iter_next(iter_handle);
 *
 *        if (err == AMDSMI_STATUS_NO_DATA) {
 *          break;
 *        }
 *      }
 *      err = amdsmi_dev_supported_func_iterator_close(&iter_handle);
 *    }
 * \endcode
 *
 *  @{
 */


/**
 * @brief Get a function name iterator of supported AMDSMI functions for a device
 *
 * @details Given a device handle @p device_handle, this function will write a function
 * iterator handle to the caller-provided memory pointed to by @p handle. This
 * handle can be used to iterate through all the supported functions.
 *
 * Note that although this function takes in @p device_handle as an argument,
 * ::amdsmi_dev_supported_func_iterator_open itself will not be among the
 * functions listed as supported. This is because
 * ::amdsmi_dev_supported_func_iterator_open does not depend on hardware or
 * driver support and should always be supported.
 *
 * @param[in] device_handle a device handle of device for which support information is
 * requested
 *
 * @param[inout] handle A pointer to caller-provided memory to which the
 * function iterator will be written.
 *
 * @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *
 */
amdsmi_status_t
amdsmi_dev_supported_func_iterator_open(amdsmi_device_handle device_handle,
                                          amdsmi_func_id_iter_handle_t *handle);

/**
 * @brief Get a variant iterator for a given handle
 *
 * @details Given a ::amdsmi_func_id_iter_handle_t @p obj_h, this function will
 * write a function iterator handle to the caller-provided memory pointed to
 * by @p var_iter. This handle can be used to iterate through all the supported
 * variants of the provided handle. @p obj_h may be a handle to a function
 * object, as provided by a call to ::amdsmi_dev_supported_func_iterator_open, or
 * it may be a variant itself (from a call to
 * ::amdsmi_dev_supported_variant_iterator_open), it which case @p var_iter will
 * be an iterator of the sub-variants of @p obj_h (e.g., monitors).
 *
 * This call allocates a small amount of memory to @p var_iter. To free this memory
 * ::amdsmi_dev_supported_func_iterator_close should be called on the returned
 * iterator handle @p var_iter when it is no longer needed.
 *
 * @param[in] obj_h an iterator handle for which the variants are being requested
 *
 * @param[inout] var_iter A pointer to caller-provided memory to which the
 * sub-variant iterator will be written.
 *
 * @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *
 */
amdsmi_status_t
amdsmi_dev_supported_variant_iterator_open(amdsmi_func_id_iter_handle_t obj_h,
                                        amdsmi_func_id_iter_handle_t *var_iter);

/**
 * @brief Advance a function identifer iterator
 *
 * @details Given a function id iterator handle (::amdsmi_func_id_iter_handle_t)
 * @p handle, this function will increment the iterator to point to the next
 * identifier. After a successful call to this function, obtaining the value
 * of the iterator @p handle will provide the value of the next item in the
 * list of functions/variants.
 *
 * If there are no more items in the list, ::AMDSMI_STATUS_NO_DATA is returned.
 *
 * @param[in] handle A pointer to an iterator handle to be incremented
 *
 * @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 * @retval ::AMDSMI_STATUS_NO_DATA is returned when list of identifiers has been
 * exhausted
 *
 */
amdsmi_status_t
amdsmi_func_iter_next(amdsmi_func_id_iter_handle_t handle);

/**
 * @brief Close a variant iterator handle
 *
 * @details Given a pointer to an ::amdsmi_func_id_iter_handle_t @p handle, this
 * function will free the resources being used by the handle
 *
 * @param[in] handle A pointer to an iterator handle to be closed
 *
 * @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *
 */
amdsmi_status_t
amdsmi_dev_supported_func_iterator_close(amdsmi_func_id_iter_handle_t *handle);

/**
 * @brief Get the value associated with a function/variant iterator
 *
 * @details Given an ::amdsmi_func_id_iter_handle_t @p handle, this function
 * will write the identifier of the function/variant to the user provided
 * memory pointed to by @p value.
 *
 * @p value may point to a function name, a variant id, or a monitor/sensor
 * index, depending on what kind of iterator @p handle is
 *
 * @param[in] handle An iterator for which the value is being requested
 *
 * @param[inout] value A pointer to an ::amdsmi_func_id_value_t provided by the
 * caller to which this function will write the value assocaited with @p handle
 *
 * @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 *
 */
amdsmi_status_t
amdsmi_func_iter_value_get(amdsmi_func_id_iter_handle_t handle,
                                                 amdsmi_func_id_value_t *value);

/** @} */  // end of APISupport

/*****************************************************************************/
/** @defgroup EvntNotif Event Notification Functions
 *  These functions are used to configure for and get asynchronous event
 *  notifications.
 *  @{
 */

/**
 * @brief Prepare to collect event notifications for a GPU
 *
 * @details This function prepares to collect events for the GPU with device
 * ID @p device_handle, by initializing any required system parameters. This call
 * may open files which will remain open until ::amdsmi_event_notification_stop()
 * is called.
 *
 * @param device_handle a device handle corresponding to the device on which to
 * listen for events
 *
 * @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call.
 */
amdsmi_status_t
amdsmi_event_notification_init(amdsmi_device_handle device_handle);

/**
 * @brief Specify which events to collect for a device
 *
 * @details Given a device handle @p device_handle and a @p mask consisting of
 * elements of ::amdsmi_evt_notification_type_t OR'd together, this function
 * will listen for the events specified in @p mask on the device
 * corresponding to @p device_handle.
 *
 * @param device_handle a device handle corresponding to the device on which to
 * listen for events
 *
 * @param mask Bitmask generated by OR'ing 1 or more elements of
 * ::amdsmi_evt_notification_type_t indicating which event types to listen for,
 * where the amdsmi_evt_notification_type_t value indicates the bit field, with
 * bit position starting from 1.
 * For example, if the mask field is 0x0000000000000003, which means first bit,
 * bit 1 (bit position start from 1) and bit 2 are set, which indicate interest
 * in receiving AMDSMI_EVT_NOTIF_VMFAULT (which has a value of 1) and
 * AMDSMI_EVT_NOTIF_THERMAL_THROTTLE event (which has a value of 2).
 *
 * @retval ::AMDSMI_STATUS_INIT_ERROR is returned if
 * ::amdsmi_event_notification_init() has not been called before a call to this
 * function
 *
 * @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call
 */
amdsmi_status_t
amdsmi_event_notification_mask_set(amdsmi_device_handle device_handle, uint64_t mask);

/**
 * @brief Collect event notifications, waiting a specified amount of time
 *
 * @details Given a time period @p timeout_ms in milliseconds and a caller-
 * provided buffer of ::amdsmi_evt_notification_data_t's @p data with a length
 * (in ::amdsmi_evt_notification_data_t's, also specified by the caller) in the
 * memory location pointed to by @p num_elem, this function will collect
 * ::amdsmi_evt_notification_type_t events for up to @p timeout_ms milliseconds,
 * and write up to *@p num_elem event items to @p data. Upon return @p num_elem
 * is updated with the number of events that were actually written. If events
 * are already present when this function is called, it will write the events
 * to the buffer then poll for new events if there is still caller-provided
 * buffer available to write any new events that would be found.
 *
 * This function requires prior calls to ::amdsmi_event_notification_init() and
 * ::amdsmi_event_notification_mask_set(). This function polls for the
 * occurrance of the events on the respective devices that were previously
 * specified by ::amdsmi_event_notification_mask_set().
 *
 * @param[in] timeout_ms number of milliseconds to wait for an event
 * to occur
 *
 * @param[inout] num_elem pointer to uint32_t, provided by the caller. On
 * input, this value tells how many ::amdsmi_evt_notification_data_t elements
 * are being provided by the caller with @p data. On output, the location
 * pointed to by @p num_elem will contain the number of items written to
 * the provided buffer.
 *
 * @param[out] data pointer to a caller-provided memory buffer of size
 * @p num_elem ::amdsmi_evt_notification_data_t to which this function may safely
 * write. If there are events found, up to @p num_elem event items will be
 * written to @p data.
 *
 * @retval ::AMDSMI_STATUS_SUCCESS The function ran successfully. The events
 * that were found are written to @p data and @p num_elems is updated
 * with the number of elements that were written.
 *
 * @retval ::AMDSMI_STATUS_NO_DATA No events were found to collect.
 *
 */
amdsmi_status_t
amdsmi_event_notification_get(int timeout_ms,
                     uint32_t *num_elem, amdsmi_evt_notification_data_t *data);

/**
 * @brief Close any file handles and free any resources used by event
 * notification for a GPU
 *
 * @details Any resources used by event notification for the GPU with
 * device handle @p device_handle will be free with this
 * function. This includes freeing any memory and closing file handles. This
 * should be called for every call to ::amdsmi_event_notification_init()
 *
 * @param[in] dv_ind The device handle of the GPU for which event
 * notification resources will be free
 *
 * @retval ::AMDSMI_STATUS_INVALID_ARGS resources for the given device have
 * either already been freed, or were never allocated by
 * ::amdsmi_event_notification_init()
 *
 * @retval ::AMDSMI_STATUS_SUCCESS is returned upon successful call
 */
amdsmi_status_t amdsmi_event_notification_stop(amdsmi_device_handle device_handle);

/** @} */  // end of EvntNotif

/**
 *  \brief          Returns BDF of the given device
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [out]    bdf - Reference to BDF. Must be allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_INVAL - Parameters are invalid
 *                  * -::SMI_ERR_NOT_FOUND - Device cannot be found
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status_t
amdsmi_get_device_bdf(amdsmi_device_handle dev, amdsmi_bdf_t *bdf);

/**
 *  \brief          Returns the UUID of the device
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [in,out] uuid_length - Length of the uuid string. As input, must be
 *                  equal or greater than SMI_GPU_UUID_SIZE and be allocated by
 *                  user. As output it is the length of the uuid string.
 *
 *  \param [out]    uuid - Pointer to string to store the UUID. Must be
 *                  allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_INVAL - Parameters are invalid
 *                  * -::SMI_ERR_NOT_FOUND - Device cannot be found
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_device_uuid(amdsmi_device_handle dev, unsigned int *uuid_length, char *uuid);

/** @}  */
/*---------------------------------------------------------------------------*/
/** @defgroup swversion     SW Version Information                           */
/*---------------------------------------------------------------------------*/
/** @{  */

/**
 *  \brief          Returns the driver version information
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [in,out] length - As input parameter length of the user allocated
 *                  string buffer. As output parameter length of the returned
 *                  string buffer.
 *
 *  \param [out]    version - Version information in string format. Must be
 *                  allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NOT_FOUND - Device cannot be found
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_driver_version(amdsmi_device_handle dev, int *length, char *version);

/** @}  */
/*---------------------------------------------------------------------------*/
/** @defgroup asicinfo     ASIC & Board Static Information                   */
/*---------------------------------------------------------------------------*/
/** @{  */

/**
 *  \brief          Returns the ASIC information for the device.
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [out]    info - Reference to static asic information structure.
 *                  Must be allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_asic_info(amdsmi_device_handle dev, amdsmi_asic_info_t *info);

/**
 *  \brief          Returns the board part number and board information for the requested device
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [out]    info - Reference to board info structure.
 *                  Must be allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialize
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_board_info(amdsmi_device_handle dev, amdsmi_board_info_t *info);

/**
 *  \brief          Returns the power caps as currently configured in the
 *                  system.
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [out]    info - Reference to power caps information structure. Must be
 *                  allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_power_cap_info(amdsmi_device_handle dev, amdsmi_power_cap_info_t *info);

/**
 *  \brief          Returns XGMI information for the GPU.
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [out]    info - Reference to xgmi information structure. Must be
 *                  allocated by user.
 *
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_xgmi_info(amdsmi_device_handle dev, amdsmi_xgmi_info_t *info);

/**
 *  \brief          Returns the device capabilities as currently configured in
 *                  the system
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [out]    info - Reference to caps information structure. Must be
 *                  allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_caps_info(amdsmi_device_handle dev, amdsmi_gpu_caps_t *info);

/** @}  */
/*---------------------------------------------------------------------------*/
/** @defgroup firmwareinfo     Firmware & VBIOS queries                        */
/*---------------------------------------------------------------------------*/
/** @{  */

/**
 *  \brief          Returns the firmware versions running on the device.
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [out]    info - Reference to the fw info. Must be allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_fw_info(amdsmi_device_handle dev, amdsmi_fw_info_t *info);

/**
 *  \brief          Returns the static information for the vBIOS on the device.
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [out]    info - Reference to static vBIOS information.
 *                  Must be allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_vbios_info(amdsmi_device_handle dev, amdsmi_vbios_info_t *info);

/** @}  */
/*---------------------------------------------------------------------------*/
/** @defgroup gpumon     GPU Monitoring                                      */
/*---------------------------------------------------------------------------*/
/** @{  */

/**
 *  \brief          Returns the current usage of the GPU engines (GFX, MM and MEM).
 *                  Each usage is reported as a percentage from 0-100%.
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [out]    info - Reference to the gpu engine usage structure. Must be allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_gpu_activity(amdsmi_device_handle dev, amdsmi_engine_usage_t *info);

/**
 *  \brief          Returns the current power and voltage of the GPU.
 *                  The voltage is in units of mV and the power in units of W.
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [out]    info - Reference to the gpu power structure. Must be allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_power_measure(amdsmi_device_handle dev, amdsmi_power_measure_t *info);

/**
 *  \brief          Returns the measurements of the clocks in the GPU
 *                  for the GFX and multimedia engines and Memory. This call
 *                  reports the averages over 1s in MHz.
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [in]     clk_type - Enum representing the clock type to query.
 *
 *  \param [out]    info - Reference to the gpu clock structure.
 *                  Must be allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_clock_measure(amdsmi_device_handle dev, amdsmi_clk_type_t clk_type, amdsmi_clock_measure_t *info);

/**
 *  \brief          Returns temperature measurements of the GPU.
 *                  The results are in °C.
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [in]     temp_type - Enum representing the temperature type to query.
 *
 *  \param [out]    info - Reference to the temperature measured.
 *                  Must be allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_temperature_measure(amdsmi_device_handle dev, amdsmi_temperature_type_t temp_type, amdsmi_temperature_t *info);

/**
 *  \brief          Returns temperature limit of the GPU.
 *                  The results are in °C.
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [in]     temp_type - Enum representing the temperature type to query.
 *
 *  \param [out]    limit - Reference to the temperature limit.
 *                  Must be allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_temperature_limit(amdsmi_device_handle dev, amdsmi_temperature_t temp_type, amdsmi_temperature_limit_t *limit);

/**
 *  \brief          Returns power limit of the GPU.
 *                  The results are in W.
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [out]    limit - Reference to the power limit.
 *                  Must be allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_power_limit(amdsmi_device_handle dev, amdsmi_power_limit_t *limit);

/**
 *  \brief          Returns the VRAM usage (both total and used memory)
 *                  in MegaBytes.
 *
 *  \param [in]     dev - device which to query
 *
 *
 *  \param [out]    info - Reference to vram information.
 *                  Must be allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_vram_usage(amdsmi_device_handle dev, amdsmi_vram_info_t *info);

/** @}  */
/*---------------------------------------------------------------------------*/
/** @defgroup gpumon     Power Management                                    */
/*---------------------------------------------------------------------------*/
/** @{  */

/**
 *  \brief          Returns current and supported frequency range
 *                  for the specified clock type.
 *
 *  \param [in]     dev - device which to query
 *
 *
 *  \param [in]     clk_type - Clock type for which to get current and supported
 *                  frequency range.
 *
 *
 *  \param [out]    range - Reference to frequency range structure.
 *                  Must be allocated by user.
 *
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialize
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_INVAL - Parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_target_frequency_range(amdsmi_device_handle dev, amdsmi_clk_type_t clk_type, amdsmi_frequency_range_t *range);

/** @}  */
/*---------------------------------------------------------------------------*/
/**  @defgroup processinfo     Process information                           */
/*---------------------------------------------------------------------------*/
/** @{  */

/**
 *  \brief          Returns the list of processes running on a given GPU including itself.
 *
 *  \note           The user provides a buffer to store the list and the
 *                  maximum number of processes that can be returned. If the user
 *                  sets max_processes to 0, the total number of processes will be
 *                  returned.
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [out]    list - Reference to a user-provided buffer where the process
 *                  list will be returned. This buffer must contain at least
 *                  max_processes entries of type smi_process_handle. Must be allocated
 *                  by user.
 *
 *  \param [in,out] max_processes - Reference to the size of the list buffer in
 *                  number of elements. Returns the return number of elements
 *                  in list or the number of running processes if equal to 0.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_INVAL - The parameters are not valid or NULL
 *                  * -::SMI_ERR_NOMEM - Provided buffer is not large enough
 *                  * -::SMI_ERR_NOT_SUPPORTED - API not supported
 */
amdsmi_status
amdsmi_get_process_list(amdsmi_device_handle dev, amdsmi_process_handle *list, uint32_t *max_processes);

/**
 *  \brief          Returns the process information of a given process.
 *
 *  \param [in]     dev - device which to query
 *
 *  \param [in]     process - handle of process to query.
 *
 *  \param [out]    info - Reference to a process information structure where to return
 *                  information. Must be allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_INVAL - The parameters are not valid or NULL
 *                  * -::SMI_ERR_NOT_SUPPORTED - API not supported
 */
amdsmi_status
amdsmi_get_process_info(amdsmi_device_handle dev, amdsmi_process_handle process, amdsmi_proc_info_t *info);

/** @}  */
/*---------------------------------------------------------------------------*/
/**  @defgroup eccinfo     ECC information                                   */
/*---------------------------------------------------------------------------*/
/** @{  */

/**
 *  \brief          Returns the number of ECC errors (correctable and
 *                  uncorrectable) in the given GPU.
 *
 *  \param [in]     dev - device which to query
 *
 *
 *  \param [out]    ec - Reference to ecc error count structure.
 *                  Must be allocated by user.
 *
 *  \return
 *                  *  ::SMI_SUCCESS - Successful
 *                  * -::SMI_ERR_RETRY - Device is busy. Please retry
 *                  * -::SMI_ERR_NO_PERM - Library was not initialized
 *                  * -::SMI_ERR_INVAL - The parameters are not valid or NULL
 *                  * -::SMI_ERR_IO - Device is in an unrecoverable state
 *                  * -::SMI_ERR_NOT_INIT - Device is uninitialized
 *                  * -::SMI_ERR_API_FAILED - Other errors
 */
amdsmi_status
amdsmi_get_ecc_error_count(amdsmi_device_handle dev, amdsmi_error_count_t *ec);

#ifdef __cplusplus
}
#endif  // __cplusplus
#endif  // INCLUDE_AMD_SMI_H_

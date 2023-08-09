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
#ifndef INCLUDE_AMDSMI_H_
#define INCLUDE_AMDSMI_H_

/**
 * @file amdsmi.h
 * @brief AMD System Management Interface API
 */

#include <stdlib.h>
#include <stdbool.h>
#ifdef __cplusplus
extern "C" {
#include <cstdint>
#else
#include <stdint.h>
#endif  // __cplusplus

/**
 * @brief Initialization flags
 *
 * Initialization flags may be OR'd together and passed to ::amdsmi_init().
 */
typedef enum {
  AMDSMI_INIT_ALL_PROCESSORS = 0x0,           // Default option
  AMDSMI_INIT_AMD_CPUS = (1 << 0),
  AMDSMI_INIT_AMD_GPUS = (1 << 1),
  AMDSMI_INIT_NON_AMD_CPUS = (1 << 2),
  AMDSMI_INIT_NON_AMD_GPUS = (1 << 3)
} amdsmi_init_flags_t;

/* Maximum size definitions AMDSMI */
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

/**
 * @brief library versioning
 */

//! Year should follow the IP driver package version: 22.40/23.10 and similar
#define AMDSMI_LIB_VERSION_YEAR 23

//! Major version should be changed for every header change (adding/deleting APIs, changing names, fields of structures, etc.)
#define AMDSMI_LIB_VERSION_MAJOR 2

//! Minor version should be updated for each API change, but without changing headers
#define AMDSMI_LIB_VERSION_MINOR 0

//! Release version should be set to 0 as default and can be updated by the PMs for each CSP point release
#define AMDSMI_LIB_VERSION_RELEASE 1

#define AMDSMI_LIB_VERSION_CREATE_STRING(YEAR, MAJOR, MINOR, RELEASE) (#YEAR "." #MAJOR "." #MINOR "." #RELEASE)
#define AMDSMI_LIB_VERSION_EXPAND_PARTS(YEAR_STR, MAJOR_STR, MINOR_STR, RELEASE_STR) AMDSMI_LIB_VERSION_CREATE_STRING(YEAR_STR, MAJOR_STR, MINOR_STR, RELEASE_STR)
#define AMDSMI_LIB_VERSION_STRING AMDSMI_LIB_VERSION_EXPAND_PARTS(AMDSMI_LIB_VERSION_YEAR, AMDSMI_LIB_VERSION_MAJOR, AMDSMI_LIB_VERSION_MINOR, AMDSMI_LIB_VERSION_RELEASE)

typedef enum {
  AMDSMI_MM_UVD,
  AMDSMI_MM_VCE,
  AMDSMI_MM_VCN,
  AMDSMI_MM__MAX
} amdsmi_mm_ip_t;

typedef enum {
	CONTAINER_LXC,
	CONTAINER_DOCKER,
} amdsmi_container_types_t;

//! opaque handler point to underlying implementation
typedef void *amdsmi_processor_handle;
typedef void *amdsmi_socket_handle;

/**
 * @brief Device types detectable by AMD SMI
 */
typedef enum {
  UNKNOWN = 0,
  AMD_GPU,
  AMD_CPU,
  NON_AMD_GPU,
  NON_AMD_CPU
} processor_type_t;

/**
 * @brief Error codes returned by amdsmi functions
 */
// Please avoid status codes that are multiples of 256 (256, 512, etc..)
// Return values in the shell get modulo 256 applied, meaning any multiple of 256 ends up as 0
typedef enum {
    AMDSMI_STATUS_SUCCESS = 0,  //!< Call succeeded
    // Library usage errors
    AMDSMI_STATUS_INVAL = 1,  //!< Invalid parameters
    AMDSMI_STATUS_NOT_SUPPORTED = 2,  //!< Command not supported
    AMDSMI_STATUS_NOT_YET_IMPLEMENTED = 3,  //!< Not implemented yet
    AMDSMI_STATUS_FAIL_LOAD_MODULE = 4,  //!< Fail to load lib
    AMDSMI_STATUS_FAIL_LOAD_SYMBOL = 5,  //!< Fail to load symbol
    AMDSMI_STATUS_DRM_ERROR = 6,  //!< Error when call libdrm
    AMDSMI_STATUS_API_FAILED = 7,  //!< API call failed
    AMDSMI_STATUS_TIMEOUT = 8,  //!< Timeout in API call
    AMDSMI_STATUS_RETRY = 9,  //!< Retry operation
    AMDSMI_STATUS_NO_PERM = 10,  //!< Permission Denied
    AMDSMI_STATUS_INTERRUPT = 11,  //!< An interrupt occurred during execution of function
    AMDSMI_STATUS_IO = 12,  //!< I/O Error
    AMDSMI_STATUS_ADDRESS_FAULT = 13,  //!< Bad address
    AMDSMI_STATUS_FILE_ERROR = 14,  //!< Problem accessing a file
    AMDSMI_STATUS_OUT_OF_RESOURCES = 15,  //!< Not enough memory
    AMDSMI_STATUS_INTERNAL_EXCEPTION = 16,  //!< An internal exception was caught
    AMDSMI_STATUS_INPUT_OUT_OF_BOUNDS = 17,  //!< The provided input is out of allowable or safe range
    AMDSMI_STATUS_INIT_ERROR = 18,  //!< An error occurred when initializing internal data structures
    AMDSMI_STATUS_REFCOUNT_OVERFLOW = 19,  //!< An internal reference counter exceeded INT32_MAX
    // Device related errors
    AMDSMI_STATUS_BUSY = 30,  //!< Device busy
    AMDSMI_STATUS_NOT_FOUND = 31,  //!< Device Not found
    AMDSMI_STATUS_NOT_INIT = 32,  //!< Device not initialized
    AMDSMI_STATUS_NO_SLOT = 33,  //!< No more free slot
    // Data and size errors
    AMDSMI_STATUS_NO_DATA = 40,  //!< No data was found for a given input
    AMDSMI_STATUS_INSUFFICIENT_SIZE = 41,  //!< Not enough resources were available for the operation
    AMDSMI_STATUS_UNEXPECTED_SIZE = 42,  //!< An unexpected amount of data was read
    AMDSMI_STATUS_UNEXPECTED_DATA = 43,  //!< The data read or provided to function is not what was expected
    // General errors
    AMDSMI_STATUS_MAP_ERROR = 0xFFFFFFFE,  //!< The internal library error did not map to a status code
    AMDSMI_STATUS_UNKNOWN_ERROR = 0xFFFFFFFF,  //!< An unknown error occurred
} amdsmi_status_t;

/**
 * Clock types
 */
typedef enum {
    CLK_TYPE_SYS = 0x0,   //!< System clock
    CLK_TYPE_FIRST = CLK_TYPE_SYS,
    CLK_TYPE_GFX = CLK_TYPE_SYS,
    CLK_TYPE_DF,  //!< Data Fabric clock (for ASICs
                    //!< running on a separate clock)
    CLK_TYPE_DCEF,   //!< Display Controller Engine clock
    CLK_TYPE_SOC,
    CLK_TYPE_MEM,
    CLK_TYPE_PCIE,
    CLK_TYPE_VCLK0,
    CLK_TYPE_VCLK1,
    CLK_TYPE_DCLK0,
    CLK_TYPE_DCLK1,
    CLK_TYPE__MAX = CLK_TYPE_DCLK1
} amdsmi_clk_type_t;

/**
 * @brief This enumeration is used to indicate from which part of the device a
 * temperature reading should be obtained.
 */
typedef enum {
    TEMPERATURE_TYPE_EDGE,
    TEMPERATURE_TYPE_FIRST = TEMPERATURE_TYPE_EDGE,
    TEMPERATURE_TYPE_JUNCTION,
    TEMPERATURE_TYPE_VRAM,
    TEMPERATURE_TYPE_HBM_0,
    TEMPERATURE_TYPE_HBM_1,
    TEMPERATURE_TYPE_HBM_2,
    TEMPERATURE_TYPE_HBM_3,
    TEMPERATURE_TYPE_PLX,
    TEMPERATURE_TYPE__MAX = TEMPERATURE_TYPE_PLX
} amdsmi_temperature_type_t;

/**
 * @brief The values of this enum are used to identify the various firmware
 * blocks.
 */
typedef enum {
    FW_ID_SMU = 1,
    FW_ID_FIRST = FW_ID_SMU,
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
    FW_ID_RLC_P,
    FW_ID_SEC_POLICY_STAGE2,
    FW_ID_REG_ACCESS_WHITELIST,
    FW_ID_IMU_DRAM,
    FW_ID_IMU_IRAM,
    FW_ID_SDMA_TH0,
    FW_ID_SDMA_TH1,
    FW_ID_CP_MES,
    FW_ID_MES_STACK,
    FW_ID_MES_THREAD1,
    FW_ID_MES_THREAD1_STACK,
    FW_ID_RLX6,
    FW_ID_RLX6_DRAM_BOOT,
    FW_ID_RS64_ME,
    FW_ID_RS64_ME_P0_DATA,
    FW_ID_RS64_ME_P1_DATA,
    FW_ID_RS64_PFP,
    FW_ID_RS64_PFP_P0_DATA,
    FW_ID_RS64_PFP_P1_DATA,
    FW_ID_RS64_MEC,
    FW_ID_RS64_MEC_P0_DATA,
    FW_ID_RS64_MEC_P1_DATA,
    FW_ID_RS64_MEC_P2_DATA,
    FW_ID_RS64_MEC_P3_DATA,
    FW_ID_PPTABLE,
    FW_ID_PSP_SOC,
    FW_ID_PSP_DBG,
    FW_ID_PSP_INTF,
    FW_ID_RLX6_CORE1,
    FW_ID_RLX6_DRAM_BOOT_CORE1,
    FW_ID_RLCV_LX7,
    FW_ID_RLC_SAVE_RESTORE_LIST,
    FW_ID_ASD,
    FW_ID_TA_RAS,
    FW_ID_XGMI,
    FW_ID_RLC_SRLG,
    FW_ID_RLC_SRLS,
    FW_ID_SMC,
    FW_ID_DMCU,
    FW_ID__MAX
} amdsmi_fw_block_t;

/**
 * @brief This structure represents a range (e.g., frequencies or voltages).
 */
typedef struct {
    uint64_t lower_bound;      //!< Lower bound of range
    uint64_t upper_bound;      //!< Upper bound of range
    uint64_t reserved[2];
} amdsmi_range_t;

typedef struct {
  uint8_t xgmi_lanes;
  uint64_t xgmi_hive_id;
  uint64_t xgmi_node_id;
  uint32_t index;
  uint32_t reserved[9];
} amdsmi_xgmi_info_t;

typedef struct {
  uint32_t vram_total;
  uint32_t vram_used;
  uint32_t reserved[2];
} amdsmi_vram_info_t;

typedef struct {
	amdsmi_range_t supported_freq_range;
	amdsmi_range_t current_freq_range;
	uint32_t reserved[8];
} amdsmi_frequency_range_t;

typedef union {
  struct {
    uint64_t function_number : 3;
    uint64_t device_number : 5;
    uint64_t bus_number : 8;
    uint64_t domain_number : 48;
  };
  uint64_t as_uint;
} amdsmi_bdf_t;

typedef struct {
  uint64_t power_cap;
  uint64_t default_power_cap;
  uint64_t dpm_cap;
  uint64_t min_power_cap;
  uint64_t max_power_cap;
  uint64_t reserved[3];
} amdsmi_power_cap_info_t;

typedef struct {
  char    name[AMDSMI_MAX_STRING_LENGTH];
  char    build_date[AMDSMI_MAX_DATE_LENGTH];
  char    part_number[AMDSMI_MAX_STRING_LENGTH];
  char    version[AMDSMI_NORMAL_STRING_LENGTH];
  uint32_t reserved[16];
} amdsmi_vbios_info_t;

typedef struct {
  uint8_t num_fw_info;
  struct {
    amdsmi_fw_block_t fw_id;
    uint64_t fw_version;
    uint64_t reserved[2];
  } fw_info_list[FW_ID__MAX];
  uint32_t reserved[7];
} amdsmi_fw_info_t;

typedef struct {
  char  market_name[AMDSMI_MAX_STRING_LENGTH];
  uint32_t vendor_id;   //< Use 32 bit to be compatible with other platform.
  uint32_t subvendor_id;   //< The subsystem vendor id
  uint64_t device_id;   //< The unique id of a GPU
  uint32_t rev_id;
  char asic_serial[AMDSMI_NORMAL_STRING_LENGTH];
  uint32_t reserved[3];
} amdsmi_asic_info_t;

typedef struct {
  uint64_t serial_number;
  bool  is_master;
  char  model_number[AMDSMI_NORMAL_STRING_LENGTH];
  char  product_serial[AMDSMI_NORMAL_STRING_LENGTH];
  char  fru_id[AMDSMI_NORMAL_STRING_LENGTH];
  char  product_name[AMDSMI_PRODUCT_NAME_LENGTH];
  char  manufacturer_name[AMDSMI_NORMAL_STRING_LENGTH];
} amdsmi_board_info_t;

typedef struct {
  uint32_t average_socket_power;
  uint32_t gfx_voltage;   // GFX voltage measurement in mV
  uint32_t soc_voltage;  // SOC voltage measurement in mV
  uint32_t mem_voltage;  // MEM voltage measurement in mV
  uint32_t power_limit;  // The power limit;
  uint32_t reserved[11];
} amdsmi_power_info_t;

typedef struct {
  uint32_t cur_clk;
  uint32_t min_clk;
  uint32_t max_clk;
  uint32_t reserved[5];
} amdsmi_clk_info_t;

typedef struct {
  uint32_t gfx_activity;
  uint32_t umc_activity;
  uint32_t mm_activity;
  uint32_t reserved[13];
} amdsmi_engine_usage_t;

typedef uint32_t amdsmi_process_handle_t;

typedef struct {
	char                  name[AMDSMI_NORMAL_STRING_LENGTH];
	amdsmi_process_handle_t pid;
	uint64_t              mem; /** in bytes */
	struct {
		uint64_t gfx;
		uint64_t enc;
    uint32_t reserved[12];
	} engine_usage; /** How much time the process spend using these engines in ns */
  struct {
    uint64_t gtt_mem;
    uint64_t cpu_mem;
    uint64_t vram_mem;
    uint32_t reserved[10];
  } memory_usage; /** in bytes */
  char container_name[AMDSMI_NORMAL_STRING_LENGTH];
  uint32_t reserved[4];
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

/**
 * @brief Available clock types.
 */


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
  AMDSMI_EVT_NOTIF_VMFAULT = 1,  //!< VM page fault
  AMDSMI_EVT_NOTIF_FIRST = AMDSMI_EVT_NOTIF_VMFAULT,
  AMDSMI_EVT_NOTIF_THERMAL_THROTTLE = 2,
  AMDSMI_EVT_NOTIF_GPU_PRE_RESET = 3,
  AMDSMI_EVT_NOTIF_GPU_POST_RESET = 4,

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
    amdsmi_processor_handle processor_handle;        //!< Handler of device that corresponds to the event
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
 * :: amdsmi_get_gpu_power_profile_presets to determine which power profiles
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
typedef enum {
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
typedef struct {
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

/**
 * @brief This structure holds version information.
 */
typedef struct {
    uint32_t year;      //!< Last 2 digits of the Year released
    uint32_t major;     //!< Major version
    uint32_t minor;     //!< Minor version
    uint32_t release;   //!< Patch, build or stepping version
    const char *build;  //!< Full Build version string
} amdsmi_version_t;

/**
 * @brief This structure represents a point on the frequency-voltage plane.
 */
typedef struct {
    uint64_t frequency;      //!< Frequency coordinate (in Hz)
    uint64_t voltage;        //!< Voltage coordinate (in mV)
} amdsmi_od_vddc_point_t;

/**
 * @brief This structure holds 2 ::amdsmi_range_t's, one for frequency and one for
 * voltage. These 2 ranges indicate the range of possible values for the
 * corresponding ::amdsmi_od_vddc_point_t.
 */
typedef struct {
    amdsmi_range_t freq_range;  //!< The frequency range for this VDDC Curve point
    amdsmi_range_t volt_range;  //!< The voltage range for this VDDC Curve point
} amdsmi_freq_volt_region_t;

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

/**
 * @brief The following structures hold the gpu metrics values for a device.
 */

/**
 * @brief Size and version information of metrics data
 */
typedef struct {
  // TODO(amd) Doxygen documents
  /// @cond Ignore in docs.
  uint16_t      structure_size;
  uint8_t       format_revision;
  uint8_t       content_revision;
  /// @endcond
} amd_metrics_table_header_t;

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
  /// @cond Ignore in docs.
  amd_metrics_table_header_t common_header;

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
  /// @endcond
} amdsmi_gpu_metrics_t;

/**
 * @brief This structure holds error counts.
 */
typedef struct {
    uint64_t correctable_count;            //!< Accumulated correctable errors
    uint64_t uncorrectable_count;          //!< Accumulated uncorrectable errors
    uint64_t reserved[2];
} amdsmi_error_count_t;

/**
 * @brief This structure holds pcie info.
 */
typedef struct {
	uint16_t pcie_lanes;
	uint32_t pcie_speed;
	uint32_t pcie_interface_version;
	uint32_t reserved[5];
} amdsmi_pcie_info_t;
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

//! Place-holder "variant" for functions that have don't have any variants,
//! but do have monitors or sensors.
#define AMDSMI_DEFAULT_VARIANT 0xFFFFFFFFFFFFFFFF

/*****************************************************************************/
/** @defgroup InitShutAdmin Initialization and Shutdown
 *  These functions are used for initialization of AMD SMI and clean up when done.
 *  @{
 */

/**
 *  @brief Initialize the AMD SMI library
 *
 *  @details This function initializes the library and the internal data structures, 
 *  including those corresponding to sources of information that SMI provides.
 *
 *  The @p init_flags decides which type of processor
 *  can be discovered by ::amdsmi_get_socket_handles(). AMDSMI_INIT_AMD_GPUS returns
 *  sockets with AMD GPUS, and AMDSMI_INIT_AMD_GPUS | AMDSMI_INIT_AMD_CPUS returns
 *  sockets with either AMD GPUS or CPUS.
 *  Currently, only AMDSMI_INIT_AMD_GPUS is supported.
 *
 *  @param[in] init_flags Bit flags that tell SMI how to initialze. Values of
 *  ::amdsmi_init_flags_t may be OR'd together and passed through @p init_flags
 *  to modify how AMDSMI initializes.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_init(uint64_t init_flags);

/**
 *  @brief Shutdown the AMD SMI library
 *
 *  @details This function shuts down the library and internal data structures and 
 *  performs any necessary clean ups.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_shut_down(void);

/** @} End InitShutAdmin */

/*****************************************************************************/
/** @defgroup DiscQueries Discovery Queries
 *  These functions provide discovery of the sockets.
 *  @{
 */

/**
 *  @brief Get the list of socket handles in the system.
 *
 *  @details Depends on what flag is passed to ::amdsmi_init.  AMDSMI_INIT_AMD_GPUS
 *  returns sockets with AMD GPUS, and AMDSMI_INIT_AMD_GPUS | AMDSMI_INIT_AMD_CPUS returns
 *  sockets with either AMD GPUS or CPUS.
 *  The socket handles can be used to query the processor handles in that socket, which
 *  will be used in other APIs to get processor detail information or telemtries.
 *
 *  @param[in,out] socket_count As input, the value passed
 *  through this parameter is the number of ::amdsmi_socket_handle that
 *  may be safely written to the memory pointed to by @p socket_handles. This is the
 *  limit on how many socket handles will be written to @p socket_handles. On return, @p
 *  socket_count will contain the number of socket handles written to @p socket_handles,
 *  or the number of socket handles that could have been written if enough memory had been
 *  provided.
 *  If @p socket_handles is NULL, as output, @p socket_count will contain
 *  how many sockets are available to read in the system.
 *
 *  @param[in,out] socket_handles A pointer to a block of memory to which the
 *  ::amdsmi_socket_handle values will be written. This value may be NULL.
 *  In this case, this function can be used to query how many sockets are
 *  available to read in the system.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_socket_handles(uint32_t *socket_count,
                amdsmi_socket_handle* socket_handles);

/**
 *  @brief Get information about the given socket
 *
 *  @details This function retrieves socket information. The @p socket_handle must 
 *  be provided to retrieve the Socket ID.
 *
 *  @param[in] socket_handle a socket handle
 *
 *  @param[out] name The id of the socket.
 *
 *  @param[in] len the length of the caller provided buffer @p name.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_socket_info(
                amdsmi_socket_handle socket_handle,
                size_t len, char *name);

/**
 *  @brief Get the list of the processor handles associated to a socket.
 *
 *  @details This function retrieves the processor handles of a socket. The
 *  @p socket_handle must be provided for the processor. A socket may have mulitple different
 *  type processors: An APU on a socket have both CPUs and GPUs.
 *  Currently, only AMD GPUs are supported.
 *
 *  The number of processor count is returned through @p processor_count
 *  if @p processor_handles is NULL. Then the number of @p processor_count can be pass
 *  as input to retrieval all processors on the socket to @p processor_handles.
 *
 *  @param[in] socket_handle The socket to query
 *
 *  @param[in,out] processor_count As input, the value passed
 *  through this parameter is the number of ::amdsmi_processor_handle's that
 *  may be safely written to the memory pointed to by @p processor_handles. This is the
 *  limit on how many processor handles will be written to @p processor_handles. On return, @p
 *  processor_count will contain the number of processor handles written to @p processor_handles,
 *  or the number of processor handles that could have been written if enough memory had been
 *  provided.
 *  If @p processor_handles is NULL, as output, @p processor_count will contain
 *  how many processors are available to read for the socket.
 *
 *  @param[in,out] processor_handles A pointer to a block of memory to which the
 *  ::amdsmi_processor_handle values will be written. This value may be NULL.
 *  In this case, this function can be used to query how many processors are
 *  available to read.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_processor_handles(amdsmi_socket_handle socket_handle,
                                    uint32_t *processor_count,
                                    amdsmi_processor_handle* processor_handles);

/**
 *  @brief Get the processor type of the processor_handle
 *
 *  @details This function retrieves the processor type. A processor_handle must be provided
 *  for that processor.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[out] processor_type a pointer to processor_type_t to which the processor type
 *  will be written. If this parameter is nullptr, this function will return
 * ::AMDSMI_STATUS_INVAL.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_processor_type(amdsmi_processor_handle processor_handle,
              processor_type_t* processor_type);

/**
 *  @brief Get processor handle with the matching bdf.
 *
 *  @details Given bdf info @p bdf, this function will get
 *  the processor handle with the matching bdf.
 *
 *  @param[in] bdf The bdf to match with corresponding processor handle.
 *
 *  @param[out] processor_handle processor handle with the matching bdf.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_processor_handle_from_bdf(amdsmi_bdf_t bdf, amdsmi_processor_handle* processor_handle);

/** @} End DiscQueries */

/*****************************************************************************/
/** @defgroup IDQuer Identifier Queries
 *  These functions provide identification information.
 *  @{
 */

/**
 *  @brief Get the device id associated with the device with provided device
 *  handler.
 *
 *  @details Given a processor handle @p processor_handle and a pointer to a uint32_t @p id,
 *  this function will write the device id value to the uint64_t pointed to by
 *  @p id. This ID is an identification of the type of device, so calling this
 *  function for different devices will give the same value if they are kind
 *  of device. Consequently, this function should not be used to distinguish
 *  one device from another. amdsmi_get_gpu_bdf_id() should be used to get a
 *  unique identifier.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] id a pointer to uint64_t to which the device id will be
 *  written
 * If this parameter is nullptr, this function will return
 * ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 * arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 * provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_gpu_id(amdsmi_processor_handle processor_handle, uint16_t *id);

/**
 *  @brief Get the name string for a give vendor ID
 *
 *  @details Given a processor handle @p processor_handle, a pointer to a caller provided
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
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] name a pointer to a caller provided char buffer to which the
 *  name will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @param[in] len the length of the caller provided buffer @p name.
 *
 *  @note ::AMDSMI_STATUS_INSUFFICIENT_SIZE is returned if @p len bytes is not
 *  large enough to hold the entire name. In this case, only @p len bytes will
 *  be written.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_gpu_vendor_name(amdsmi_processor_handle processor_handle, char *name,
                                                                  size_t len);

/**
 *  @brief Get the vram vendor string of a device.
 *
 *  @details This function retrieves the vram vendor name given a processor handle
 *  @p processor_handle, a pointer to a caller provided
 *  char buffer @p brand, and a length of this buffer @p len, this function
 *  will write the vram vendor of the device (up to @p len characters) to the
 *  buffer @p brand.
 *
 *  If the vram vendor for the device is not found as one of the values
 *  contained within amdsmi_get_gpu_vram_vendor, then this function will return
 *  the string 'unknown' instead of the vram vendor.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] brand a pointer to a caller provided char buffer to which the
 *  vram vendor will be written
 *
 *  @param[in] len the length of the caller provided buffer @p brand.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_gpu_vram_vendor(amdsmi_processor_handle processor_handle, char *brand,
                                                                uint32_t len);

/**
 *  @brief Get the subsystem device id associated with the device with
 *  provided processor handle.
 *
 *  @details Given a processor handle @p processor_handle and a pointer to a uint32_t @p id,
 *  this function will write the subsystem device id value to the uint64_t
 *  pointed to by @p id.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] id a pointer to uint64_t to which the subsystem device id
 *  will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_gpu_subsystem_id(amdsmi_processor_handle processor_handle, uint16_t *id);

/**
 *  @brief Get the name string for the device subsytem
 *
 *  @details Given a processor handle @p processor_handle, a pointer to a caller provided
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
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] name a pointer to a caller provided char buffer to which the
 *  name will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.

 *  @param[in] len the length of the caller provided buffer @p name.
 *
 *  @note ::AMDSMI_STATUS_INSUFFICIENT_SIZE is returned if @p len bytes is not
 *  large enough to hold the entire name. In this case, only @p len bytes will
 *  be written.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_subsystem_name(amdsmi_processor_handle processor_handle, char *name, size_t len);

/** @} End IDQuer */

/*****************************************************************************/
/** @defgroup PCIeQuer PCIe Queries
 *  These functions provide information about PCIe.
 *  @{
 */

/**
 *  @brief Get the list of possible PCIe bandwidths that are available. It is not
 *  supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle and a pointer to a to an
 *  ::amdsmi_pcie_bandwidth_t structure @p bandwidth, this function will fill in
 *  @p bandwidth with the possible T/s values and associated number of lanes,
 *  and indication of the current selection.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] bandwidth a pointer to a caller provided
 *  ::amdsmi_pcie_bandwidth_t structure to which the frequency information will be
 *  written
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_pci_bandwidth(amdsmi_processor_handle processor_handle, amdsmi_pcie_bandwidth_t *bandwidth);

/**
 *  @brief Get the unique PCI device identifier associated for a device
 *
 *  @details Give a processor handle @p processor_handle and a pointer to a uint64_t @p
 *  bdfid, this function will write the Bus/Device/Function PCI identifier
 *  (BDFID) associated with device @p processor_handle to the value pointed to by
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
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] bdfid a pointer to uint64_t to which the device bdfid value
 *  will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_gpu_bdf_id(amdsmi_processor_handle processor_handle, uint64_t *bdfid);

/**
 *  @brief Get the NUMA node associated with a device
 *
 *  @details Given a processor handle @p processor_handle and a pointer to a uint32_t @p
 *  numa_node, this function will retrieve the NUMA node value associated
 *  with device @p processor_handle and store the value at location pointed to by
 *  @p numa_node.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] numa_node pointer to location where NUMA node value will
 *  be written.
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_gpu_topo_numa_affinity(amdsmi_processor_handle processor_handle, uint32_t *numa_node);

/**
 *  @brief Get PCIe traffic information. It is not supported on virtual machine guest
 *
 *  @details Give a processor handle @p processor_handle and pointers to a uint64_t's, @p
 *  sent, @p received and @p max_pkt_sz, this function will write the number
 *  of bytes sent and received in 1 second to @p sent and @p received,
 *  respectively. The maximum possible packet size will be written to
 *  @p max_pkt_sz.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] sent a pointer to uint64_t to which the number of bytes sent
 *  will be written in 1 second. If pointer is NULL, it will be ignored.
 *
 *  @param[in,out] received a pointer to uint64_t to which the number of bytes
 *  received will be written. If pointer is NULL, it will be ignored.
 *
 *  @param[in,out] max_pkt_sz a pointer to uint64_t to which the maximum packet
 *  size will be written. If pointer is NULL, it will be ignored.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_gpu_pci_throughput(amdsmi_processor_handle processor_handle, uint64_t *sent,
                                    uint64_t *received, uint64_t *max_pkt_sz);

/**
 *  @brief Get PCIe replay counter
 *
 *  @details Given a processor handle @p processor_handle and a pointer to a uint64_t @p
 *  counter, this function will write the sum of the number of NAK's received
 *  by the GPU and the NAK's generated by the GPU to memory pointed to by @p
 *  counter.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] counter a pointer to uint64_t to which the sum of the NAK's
 *  received and generated by the GPU is written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_get_gpu_pci_replay_counter(amdsmi_processor_handle processor_handle,
                                                           uint64_t *counter);

/** @} End PCIeQuer */

/*****************************************************************************/
/** @defgroup PCIeCont PCIe Control
 *  These functions provide some control over PCIe.
 *  @{
 */

/**
 *  @brief Control the set of allowed PCIe bandwidths that can be used. It is not
 *  supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle and a 64 bit bitmask @p bw_bitmask,
 *  this function will limit the set of allowable bandwidths. If a bit in @p
 *  bw_bitmask has a value of 1, then the frequency (as ordered in an
 *  ::amdsmi_frequencies_t returned by :: amdsmi_get_clk_freq()) corresponding
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
 *  @note This function requires root access
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] bw_bitmask A bitmask indicating the indices of the
 *  bandwidths that are to be enabled (1) and disabled (0). Only the lowest
 *  ::amdsmi_frequencies_t::num_supported (of ::amdsmi_pcie_bandwidth_t) bits of
 *  this mask are relevant.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_set_gpu_pci_bandwidth(amdsmi_processor_handle processor_handle, uint64_t bw_bitmask);

/** @} End PCIeCont */

/*****************************************************************************/
/** @defgroup PowerQuer Power Queries
 *  These functions provide information about power usage.
 *  @{
 */

/**
 *  @brief Get the energy accumulator counter of the processor with provided
 *  processor handle. It is not supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle, a pointer to a uint64_t
 *  @p power, and a pointer to a uint64_t @p timestamp, this function will write
 *  amount of energy consumed to the uint64_t pointed to by @p power,
 *  and the timestamp to the uint64_t pointed to by @p timestamp.
 *  The amdsmi_get_power_ave() is an average of a short time. This function
 *  accumulates all energy consumed.
 *
 *  @param[in] processor_handle a processor handle
 *  @param[in,out] counter_resolution resolution of the counter @p power in
 *  micro Joules
 *
 *  @param[in,out] power a pointer to uint64_t to which the energy
 *  counter will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @param[in,out] timestamp a pointer to uint64_t to which the timestamp
 *  will be written. Resolution: 1 ns.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_energy_count(amdsmi_processor_handle processor_handle, uint64_t *power,
                          float *counter_resolution, uint64_t *timestamp);

/** @} End PowerQuer */

/*****************************************************************************/
/** @defgroup PowerCont Power Control
 *  These functions provide ways to control power usage.
 *  @{
 */
/**
 *  @brief Set the maximum gpu power cap value. It is not supported on virtual
 *  machine guest
 *
 *  @details This function will set the power cap to the provided value @p cap.
 *  @p cap must be between the minimum and maximum power cap values set by the
 *  system, which can be obtained from ::amdsmi_dev_power_cap_range_get.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a processor has more than one sensor, it could be greater than 0.
 *
 *  @param[in] cap a uint64_t that indicates the desired power cap, in
 *  microwatts
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
 amdsmi_set_power_cap(amdsmi_processor_handle processor_handle, uint32_t sensor_ind, uint64_t cap);

/**
 *  @brief Set the power performance profile. It is not supported on virtual machine guest
 *
 *  @details This function will attempt to set the current profile to the provided
 *  profile, given a processor handle @p processor_handle and a @p profile. The provided
 *  profile must be one of the currently supported profiles, as indicated by a
 *  call to :: amdsmi_get_gpu_power_profile_presets()
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] reserved Not currently used. Set to 0.
 *
 *  @param[in] profile a ::amdsmi_power_profile_preset_masks_t that hold the mask
 *  of the desired new power profile
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
 amdsmi_set_gpu_power_profile(amdsmi_processor_handle processor_handle, uint32_t reserved,
                                   amdsmi_power_profile_preset_masks_t profile);

/** @} End PowerCont*/

/*****************************************************************************/
/** @defgroup MemQuer Memory Queries
 *  These functions provide information about memory systems.
 *  @{
 */

/**
 *  @brief Get the total amount of memory that exists
 *
 *  @details Given a processor handle @p processor_handle, a type of memory @p mem_type, and
 *  a pointer to a uint64_t @p total, this function will write the total amount
 *  of @p mem_type memory that exists to the location pointed to by @p total.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] mem_type The type of memory for which the total amount will be
 *  found
 *
 *  @param[in,out] total a pointer to uint64_t to which the total amount of
 *  memory will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_memory_total(amdsmi_processor_handle processor_handle, amdsmi_memory_type_t mem_type,
                                                             uint64_t *total);

/**
 *  @brief Get the current memory usage
 *
 *  @details This function will write the amount of @p mem_type memory that
 *  that is currently being used to the location pointed to by @p used.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] mem_type The type of memory for which the amount being used will
 *  be found
 *
 *  @param[in,out] used a pointer to uint64_t to which the amount of memory
 *  currently being used will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_memory_usage(amdsmi_processor_handle processor_handle, amdsmi_memory_type_t mem_type,
                                                              uint64_t *used);

/**
 * @brief Get the bad pages of a processor. It is not supported on virtual
 * machine guest
 * @details This call will query the device @p processor_handle for the
 * number of bad pages (written to @p num_pages address). The results are
 * written to address held by the @p info pointer.
 * The first call to this API returns the number of bad pages which
 * should be used to allocate the buffer that should contain the bad page
 * records.
 * @param[in] processor_handle a processor handle
 * @param[out] num_pages Number of bad page records.
 * @param[out] info The results will be written to the 
 * amdsmi_retired_page_record_t pointer.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_bad_page_info(amdsmi_processor_handle processor_handle, uint32_t *num_pages, amdsmi_retired_page_record_t *info);

/**
 * @brief Returns if RAS features are enabled or disabled for given block. It is not
 * supported on virtual machine guest
 *
 * @details Given a processor handle @p processor_handle, this function queries the
 * state of RAS features for a specific block @p block. Result will be written
 * to address held by pointer @p state.
 *
 * @param[in] processor_handle Device handle which to query
 *
 * @param[in] block Block which to query
 *
 * @param[in,out] state A pointer to amdsmi_ras_err_state_t to which the state
 * of block will be written.
 * If this parameter is nullptr, this function will return
 * ::AMDSMI_STATUS_INVAL if the function is supported with the provided
 * arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 * provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_ras_block_features_enabled(amdsmi_processor_handle processor_handle, amdsmi_gpu_block_t block,
                                                                  amdsmi_ras_err_state_t *state);

/**
 *  @brief Get information about reserved ("retired") memory pages. It is not supported on
 *  virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle, this function returns retired page
 *  information @p records corresponding to the device with the provided processor
 *  handle @p processor_handle. The number of retired page records is returned through @p
 *  num_pages. @p records may be NULL on input. In this case, the number of
 *  records available for retrieval will be returned through @p num_pages.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] num_pages a pointer to a uint32. As input, the value passed
 *  through this parameter is the number of ::amdsmi_retired_page_record_t's that
 *  may be safely written to the memory pointed to by @p records. This is the
 *  limit on how many records will be written to @p records. On return, @p
 *  num_pages will contain the number of records written to @p records, or the
 *  number of records that could have been written if enough memory had been
 *  provided.
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @param[in,out] records A pointer to a block of memory to which the
 *  ::amdsmi_retired_page_record_t values will be written. This value may be NULL.
 *  In this case, this function can be used to query how many records are
 *  available to read.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_memory_reserved_pages(amdsmi_processor_handle processor_handle, uint32_t *num_pages,
                                         amdsmi_retired_page_record_t *records);

/** @} End MemQuer */

/** @defgroup PhysQuer Physical State Queries
 *  These functions provide information about the physical characteristics of
 *  the device.
 *  @{
 */

/**
 *  @brief Get the fan speed in RPMs of the device with the specified processor
 *  handle and 0-based sensor index. It is not supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle and a pointer to a uint32_t
 *  @p speed, this function will write the current fan speed in RPMs to the
 *  uint32_t pointed to by @p speed
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a device has more than one sensor, it could be greater than 0.
 *
 *  @param[in,out] speed a pointer to uint32_t to which the speed will be
 *  written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_gpu_fan_rpms(amdsmi_processor_handle processor_handle, uint32_t sensor_ind,
                                                              int64_t *speed);

/**
 *  @brief Get the fan speed for the specified device as a value relative to
 *  ::AMDSMI_MAX_FAN_SPEED. It is not supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle and a pointer to a uint32_t
 *  @p speed, this function will write the current fan speed (a value
 *  between 0 and the maximum fan speed, ::AMDSMI_MAX_FAN_SPEED) to the uint32_t
 *  pointed to by @p speed
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a device has more than one sensor, it could be greater than 0.
 *
 *  @param[in,out] speed a pointer to uint32_t to which the speed will be
 *  written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_gpu_fan_speed(amdsmi_processor_handle processor_handle,
                                        uint32_t sensor_ind, int64_t *speed);

/**
 *  @brief Get the max. fan speed of the device with provided processor handle. It is
 *  not supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle and a pointer to a uint32_t
 *  @p max_speed, this function will write the maximum fan speed possible to
 *  the uint32_t pointed to by @p max_speed
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a device has more than one sensor, it could be greater than 0.
 *
 *  @param[in,out] max_speed a pointer to uint32_t to which the maximum speed
 *  will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_gpu_fan_speed_max(amdsmi_processor_handle processor_handle,
                                    uint32_t sensor_ind, uint64_t *max_speed);

/**
 *  @brief Get the temperature metric value for the specified metric, from the
 *  specified temperature sensor on the specified device. It is not supported on
 *  virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle, a sensor type @p sensor_type, a
 *  ::amdsmi_temperature_metric_t @p metric and a pointer to an int64_t @p
 *  temperature, this function will write the value of the metric indicated by
 *  @p metric and @p sensor_type to the memory location @p temperature.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] sensor_type part of device from which temperature should be
 *  obtained. This should come from the enum ::amdsmi_temperature_type_t
 *
 *  @param[in] metric enum indicated which temperature value should be
 *  retrieved
 *
 *  @param[in,out] temperature a pointer to int64_t to which the temperature
 *  will be written, in millidegrees Celcius.
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_get_temp_metric(amdsmi_processor_handle processor_handle,
                      amdsmi_temperature_type_t sensor_type,
                      amdsmi_temperature_metric_t metric, int64_t *temperature);

/**
 *  @brief Get the voltage metric value for the specified metric, from the
 *  specified voltage sensor on the specified device. It is not supported on
 *  virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle, a sensor type @p sensor_type, a
 *  ::amdsmi_voltage_metric_t @p metric and a pointer to an int64_t @p
 *  voltage, this function will write the value of the metric indicated by
 *  @p metric and @p sensor_type to the memory location @p voltage.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] sensor_type part of device from which voltage should be
 *  obtained. This should come from the enum ::amdsmi_voltage_type_t
 *
 *  @param[in] metric enum indicated which voltage value should be
 *  retrieved
 *
 *  @param[in,out] voltage a pointer to int64_t to which the voltage
 *  will be written, in millivolts.
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_get_gpu_volt_metric(amdsmi_processor_handle processor_handle,
                               amdsmi_voltage_type_t sensor_type,
                              amdsmi_voltage_metric_t metric, int64_t *voltage);

/** @} End PhysQuer */

/*****************************************************************************/
/** @defgroup PhysCont Physical State Control
 *  These functions provide control over the physical state of a device.
 *  @{
 */

/**
 *  @brief Reset the fan to automatic driver control. It is not supported on virtual
 *  machine guest
 *
 *  @details This function returns control of the fan to the system
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a device has more than one sensor, it could be greater than 0.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_reset_gpu_fan(amdsmi_processor_handle processor_handle, uint32_t sensor_ind);

/**
 *  @brief Set the fan speed for the specified device with the provided speed,
 *  in RPMs. It is not supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle and a integer value indicating
 *  speed @p speed, this function will attempt to set the fan speed to @p speed.
 *  An error will be returned if the specified speed is outside the allowable
 *  range for the device. The maximum value is 255 and the minimum is 0.
 *
 *  @note This function requires root access
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a device has more than one sensor, it could be greater than 0.
 *
 *  @param[in] speed the speed to which the function will attempt to set the fan
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_set_gpu_fan_speed(amdsmi_processor_handle processor_handle,
      uint32_t sensor_ind, uint64_t speed);

/** @} End PhysCont */

/*****************************************************************************/
/** @defgroup PerfQuer Clock, Power and Performance Queries
 *  These functions provide information about clock frequencies and
 *  performance.
 *  @{
 */

/**
 *  @brief Get coarse grain utilization counter of the specified device
 *
 *  @details Given a processor handle @p processor_handle, the array of the utilization counters,
 *  the size of the array, this function returns the coarse grain utilization counters
 *  and timestamp.
 *  The counter is the accumulated percentages. Every milliseconds the firmware calculates
 *  % busy count and then accumulates that value in the counter. This provides minimally
 *  invasive coarse grain GPU usage information.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] utilization_counters Multiple utilization counters can be retreived with a single
 *  call. The caller must allocate enough space to the utilization_counters array. The caller also
 *  needs to set valid AMDSMI_UTILIZATION_COUNTER_TYPE type for each element of the array.
 *  ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the provided arguments.
 *
 *  If the function reutrns AMDSMI_STATUS_SUCCESS, the counter will be set in the value field of
 *  the amdsmi_utilization_counter_t.
 *
 *  @param[in] count The size of @p utilization_counters array.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_utilization_count(amdsmi_processor_handle processor_handle,
                amdsmi_utilization_counter_t utilization_counters[],
                uint32_t count,
                uint64_t *timestamp);

/**
 *  @brief Get current PCIE info of the device with provided processor handle. It is not supported
 *  on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle, this function returns PCIE info of the
 *  given device.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[out] info amdsmi_pcie_info_t struct which will hold all the extracted PCIE info data.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_pcie_link_status(amdsmi_processor_handle processor_handle, amdsmi_pcie_info_t *info);

/**
 *  @brief Get max PCIe capabilities of the device with provided processor handle.
 *
 *  @details Given a processor handle @p processor_handle, this function returns PCIe caps info of the
 *  given device.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[out] info amdsmi_pcie_info_t struct which will hold all the extracted PCIe caps data.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_pcie_link_caps(amdsmi_processor_handle processor_handle, amdsmi_pcie_info_t *info);

/**
 *  @brief Get the performance level of the device. It is not supported on virtual
 *  machine guest
 *
 *  @details This function will write the ::amdsmi_dev_perf_level_t to the uint32_t
 *  pointed to by @p perf, for a given processor handle @p processor_handle and a pointer
 *  to a uint32_t @p perf. 
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] perf a pointer to ::amdsmi_dev_perf_level_t to which the
 *  performance level will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_get_gpu_perf_level(amdsmi_processor_handle processor_handle,
                                                 amdsmi_dev_perf_level_t *perf);

/**
 *  @brief Enter performance determinism mode with provided processor handle. It is
 *  not supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle and @p clkvalue this function
 *  will enable performance determinism mode, which enforces a GFXCLK frequency
 *  SoftMax limit per GPU set by the user. This prevents the GFXCLK PLL from
 *  stretching when running the same workload on different GPUS, making
 *  performance variation minimal. This call will result in the performance
 *  level ::amdsmi_dev_perf_level_t of the device being
 *  ::AMDSMI_DEV_PERF_LEVEL_DETERMINISM.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] clkvalue Softmax value for GFXCLK in MHz.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_set_gpu_perf_determinism_mode(amdsmi_processor_handle processor_handle, uint64_t clkvalue);

/**
 *  @brief Get the overdrive percent associated with the device with provided
 *  processor handle. It is not supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle and a pointer to a uint32_t @p od,
 *  this function will write the overdrive percentage to the uint32_t pointed
 *  to by @p od
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] od a pointer to uint32_t to which the overdrive percentage
 *  will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */

amdsmi_status_t amdsmi_get_gpu_overdrive_level(amdsmi_processor_handle processor_handle, uint32_t *od);

/**
 *  @brief Get the list of possible system clock speeds of device for a
 *  specified clock type. It is not supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle, a clock type @p clk_type, and a
 *  pointer to a to an ::amdsmi_frequencies_t structure @p f, this function will
 *  fill in @p f with the possible clock speeds, and indication of the current
 *  clock speed selection.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] clk_type the type of clock for which the frequency is desired
 *
 *  @param[in,out] f a pointer to a caller provided ::amdsmi_frequencies_t structure
 *  to which the frequency information will be written. Frequency values are in
 *  Hz.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_get_clk_freq(amdsmi_processor_handle processor_handle,
                             amdsmi_clk_type_t clk_type, amdsmi_frequencies_t *f);

/**
 *  @brief Reset the gpu associated with the device with provided processor handle. It is not
 *  supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle, this function will reset the GPU
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_reset_gpu(amdsmi_processor_handle processor_handle);

/**
 *  @brief This function retrieves the voltage/frequency curve information. It is
 *  not supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle and a pointer to a
 *  ::amdsmi_od_volt_freq_data_t structure @p odv, this function will populate @p
 *  odv. See ::amdsmi_od_volt_freq_data_t for more details.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] odv a pointer to an ::amdsmi_od_volt_freq_data_t structure
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_get_gpu_od_volt_info(amdsmi_processor_handle processor_handle,
                                               amdsmi_od_volt_freq_data_t *odv);

/**
 *  @brief This function retrieves the gpu metrics information. It is not supported
 *  on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle and a pointer to a
 *  ::amdsmi_gpu_metrics_t structure @p pgpu_metrics, this function will populate
 *  @p pgpu_metrics. See ::amdsmi_gpu_metrics_t for more details.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] pgpu_metrics a pointer to an ::amdsmi_gpu_metrics_t structure
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_get_gpu_metrics_info(amdsmi_processor_handle processor_handle,
                                            amdsmi_gpu_metrics_t *pgpu_metrics);

/**
 *  @brief This function sets the clock range information. It is not supported on virtual
 *  machine guest
 *
 *  @details Given a processor handle @p processor_handle, a minimum clock value @p minclkvalue,
 *  a maximum clock value @p maxclkvalue and a clock type @p clkType this function
 *  will set the sclk|mclk range
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] minclkvalue value to apply to the clock range. Frequency values
 *  are in MHz.
 *
 *  @param[in] maxclkvalue value to apply to the clock range. Frequency values
 *  are in MHz.
 *
 *  @param[in] clkType AMDSMI_CLK_TYPE_SYS | AMDSMI_CLK_TYPE_MEM range type
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_set_gpu_clk_range(amdsmi_processor_handle processor_handle, uint64_t minclkvalue,
                                       uint64_t maxclkvalue,
                                       amdsmi_clk_type_t clkType);

/**
 *  @brief This function sets the clock frequency information. It is not supported on
 *  virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle, a frequency level @p level,
 *  a clock value @p clkvalue and a clock type @p clkType this function
 *  will set the sclk|mclk range
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] level AMDSMI_FREQ_IND_MIN|AMDSMI_FREQ_IND_MAX to set the
 *  minimum (0) or maximum (1) speed.
 *
 *  @param[in] clkvalue value to apply to the clock range. Frequency values
 *  are in MHz.
 *
 *  @param[in] clkType AMDSMI_CLK_TYPE_SYS | AMDSMI_CLK_TYPE_MEM range type
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_set_gpu_od_clk_info(amdsmi_processor_handle processor_handle, amdsmi_freq_ind_t level,
                                       uint64_t clkvalue,
                                       amdsmi_clk_type_t clkType);

/**
 *  @brief This function sets  1 of the 3 voltage curve points. It is not supported
 *  on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle, a voltage point @p vpoint
 *  and a voltage value @p voltvalue this function will set voltage curve point
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] vpoint voltage point [0|1|2] on the voltage curve
 *
 *  @param[in] clkvalue clock value component of voltage curve point.
 *  Frequency values are in MHz.
 *
 *  @param[in] voltvalue voltage value component of voltage curve point.
 *  Voltage is in mV.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_set_gpu_od_volt_info(amdsmi_processor_handle processor_handle, uint32_t vpoint,
                                        uint64_t clkvalue, uint64_t voltvalue);

/**
 *  @brief This function will retrieve the current valid regions in the
 *  frequency/voltage space. It is not supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle, a pointer to an unsigned integer
 *  @p num_regions and a buffer of ::amdsmi_freq_volt_region_t structures, @p
 *  buffer, this function will populate @p buffer with the current
 *  frequency-volt space regions. The caller should assign @p buffer to memory
 *  that can be written to by this function. The caller should also
 *  indicate the number of ::amdsmi_freq_volt_region_t structures that can safely
 *  be written to @p buffer in @p num_regions.
 *
 *  The number of regions to expect this function provide (@p num_regions) can
 *  be obtained by calling :: amdsmi_get_gpu_od_volt_info().
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] num_regions As input, this is the number of
 *  ::amdsmi_freq_volt_region_t structures that can be written to @p buffer. As
 *  output, this is the number of ::amdsmi_freq_volt_region_t structures that were
 *  actually written.
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @param[in,out] buffer a caller provided buffer to which
 *  ::amdsmi_freq_volt_region_t structures will be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_get_gpu_od_volt_curve_regions(amdsmi_processor_handle processor_handle,
                      uint32_t *num_regions, amdsmi_freq_volt_region_t *buffer);

/**
 *  @brief Get the list of available preset power profiles and an indication of
 *  which profile is currently active. It is not supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle and a pointer to a
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
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] sensor_ind a 0-based sensor index. Normally, this will be 0.
 *  If a device has more than one sensor, it could be greater than 0.
 *
 *  @param[in,out] status a pointer to ::amdsmi_power_profile_status_t that will be
 *  populated by a call to this function
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
 amdsmi_get_gpu_power_profile_presets(amdsmi_processor_handle processor_handle, uint32_t sensor_ind,
                                         amdsmi_power_profile_status_t *status);

/** @} End PerfQuer */

/*****************************************************************************/
/** @defgroup PerfCont Clock, Power and Performance Control
 *  These functions provide control over clock frequencies, power and
 *  performance.
 *  @{
 */

/**
 *  @brief Set the PowerPlay performance level associated with the device with
 *  provided processor handle with the provided value. It is not supported
 *  on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle and an ::amdsmi_dev_perf_level_t @p
 *  perf_level, this function will set the PowerPlay performance level for the
 *  device to the value @p perf_lvl.
 *
 *  @note This function requires root access
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] perf_lvl the value to which the performance level should be set
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
 amdsmi_set_gpu_perf_level(amdsmi_processor_handle processor_handle, amdsmi_dev_perf_level_t perf_lvl);

/**
 *  @brief Set the overdrive percent associated with the device with provided
 *  processor handle with the provided value. See details for WARNING. It is
 *  not supported on virtual machine guest
 *
 *
 *  @details Given a processor handle @p processor_handle and an overdrive level @p od,
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
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] od the value to which the overdrive level should be set
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_set_gpu_overdrive_level(amdsmi_processor_handle processor_handle, uint32_t od);

/**
 * @brief Control the set of allowed frequencies that can be used for the
 * specified clock. It is not supported on virtual machine guest
 *
 * @details Given a processor handle @p processor_handle, a clock type @p clk_type, and a
 * 64 bit bitmask @p freq_bitmask, this function will limit the set of
 * allowable frequencies. If a bit in @p freq_bitmask has a value of 1, then
 * the frequency (as ordered in an ::amdsmi_frequencies_t returned by
 *  amdsmi_get_clk_freq()) corresponding to that bit index will be
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
 *  @note This function requires root access
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] clk_type the type of clock for which the set of frequencies
 *  will be modified
 *
 *  @param[in] freq_bitmask A bitmask indicating the indices of the
 *  frequencies that are to be enabled (1) and disabled (0). Only the lowest
 *  ::amdsmi_frequencies_t.num_supported bits of this mask are relevant.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_set_clk_freq(amdsmi_processor_handle processor_handle,
                             amdsmi_clk_type_t clk_type, uint64_t freq_bitmask);

/** @} End PerfCont */

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
 * @param[in,out] version A pointer to an ::amdsmi_version_t structure that will
 * be updated with the version information upon return.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_lib_version(amdsmi_version_t *version);

/** @} End VersQuer */

/*****************************************************************************/
/** @defgroup ErrQuer Error Queries
 *  These functions provide error information about AMDSMI calls as well as
 *  device errors.
 *  @{
 */

/**
 *  @brief Retrieve the error counts for a GPU block. It is not supported on virtual
 *  machine guest
 *
 *  @details Given a processor handle @p processor_handle, an ::amdsmi_gpu_block_t @p block and a
 *  pointer to an ::amdsmi_error_count_t @p ec, this function will write the error
 *  count values for the GPU block indicated by @p block to memory pointed to by
 *  @p ec.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] block The block for which error counts should be retrieved
 *
 *  @param[in,out] ec A pointer to an ::amdsmi_error_count_t to which the error
 *  counts should be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_get_gpu_ecc_count(amdsmi_processor_handle processor_handle,
                              amdsmi_gpu_block_t block, amdsmi_error_count_t *ec);

/**
 *  @brief Retrieve the enabled ECC bit-mask. It is not supported on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle, and a pointer to a uint64_t @p
 *  enabled_mask, this function will write bits to memory pointed to by
 *  @p enabled_blocks. Upon a successful call, @p enabled_blocks can then be
 *  AND'd with elements of the ::amdsmi_gpu_block_t ennumeration to determine if
 *  the corresponding block has ECC enabled. Note that whether a block has ECC
 *  enabled or not in the device is independent of whether there is kernel
 *  support for error counting for that block. Although a block may be enabled,
 *  but there may not be kernel support for reading error counters for that
 *  block.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] enabled_blocks A pointer to a uint64_t to which the enabled
 *  blocks bits will be written.
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_get_gpu_ecc_enabled(amdsmi_processor_handle processor_handle,
                                                    uint64_t *enabled_blocks);

/**
 *  @brief Retrieve the ECC status for a GPU block. It is not supported on virtual machine
 *  guest
 *
 *  @details Given a processor handle @p processor_handle, an ::amdsmi_gpu_block_t @p block and
 *  a pointer to an ::amdsmi_ras_err_state_t @p state, this function will write
 *  the current state for the GPU block indicated by @p block to memory pointed
 *  to by @p state.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] block The block for which error counts should be retrieved
 *
 *  @param[in,out] state A pointer to an ::amdsmi_ras_err_state_t to which the
 *  ECC state should be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t  amdsmi_get_gpu_ecc_status(amdsmi_processor_handle processor_handle, amdsmi_gpu_block_t block,
                                                  amdsmi_ras_err_state_t *state);

/**
 *  @brief Get a description of a provided AMDSMI error status
 *
 *  @details Set the provided pointer to a const char *, @p status_string, to
 *  a string containing a description of the provided error code @p status.
 *
 *  @param[in] status The error status for which a description is desired
 *
 *  @param[in,out] status_string A pointer to a const char * which will be made
 *  to point to a description of the provided error code
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_status_code_to_string(amdsmi_status_t status, const char **status_string);

/** @} End ErrQuer */

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
 *  ::amdsmi_gpu_counter_group_supported() can be used to see which event types
 *  (::amdsmi_event_group_t) are supported for a given device. Assuming a device
 *  supports a given event type, we can then check to see if there are counters
 *  available to count a specific event with
 *  :: amdsmi_get_gpu_available_counters(). Counters may be occupied by other
 *  perf based programs.
 *
 *  Once it is determined that events are supported and counters are available,
 *  an event counter can be created/destroyed and controlled.
 *
 *  ::amdsmi_gpu_create_counter() allocates internal data structures that will be
 *  used to used to control the event counter, and return a handle to this data
 *  structure.
 *
 *  Once an event counter handle is obtained, the event counter can be
 *  controlled (i.e., started, stopped,...) with ::amdsmi_gpu_control_counter() by
 *  passing ::amdsmi_counter_command_t commands. ::AMDSMI_CNTR_CMD_START starts an
 *  event counter and ::AMDSMI_CNTR_CMD_STOP stops a counter.
 *  ::amdsmi_gpu_read_counter() reads an event counter.
 *
 *  Once the counter is no longer needed, the resources it uses should be freed
 *  by calling ::amdsmi_gpu_destroy_counter().
 *
 *
 *  Important Notes about Counter Values
 *  ====================================
 *  - A running "absolute" counter is kept internally. For the discussion that
 *  follows, we will call the internal counter value at time @a t @a
 *  val<sub>t</sub>
 *  - Issuing ::AMDSMI_CNTR_CMD_START or calling ::amdsmi_gpu_read_counter(), causes
 *  AMDSMI (in kernel) to internally record the current absolute counter value
 *  - ::amdsmi_gpu_read_counter() returns the number of events that have occurred
 *  since the previously recorded value (ie, a relative value,
 *  @a val<sub>t</sub> - val<sub>t-1</sub>) from the issuing of
 *  ::AMDSMI_CNTR_CMD_START or calling ::amdsmi_gpu_read_counter()
 *
 *  Example of event counting sequence:
 *
 *  @latexonly
 *  \pagebreak
 *  @endlatexonly
 *  @code{.cpp}
 *
 *    amdsmi_counter_value_t value;
 *
 *    // Determine if AMDSMI_EVNT_GRP_XGMI is supported for device dv_ind
 *    ret = amdsmi_gpu_counter_group_supported(dv_ind, AMDSMI_EVNT_GRP_XGMI);
 *
 *    // See if there are counters available for device dv_ind for event
 *    // AMDSMI_EVNT_GRP_XGMI
 *
 *    ret =  amdsmi_get_gpu_available_counters(dv_ind,
 *                                 AMDSMI_EVNT_GRP_XGMI, &counters_available);
 *
 *    // Assuming AMDSMI_EVNT_GRP_XGMI is supported and there is at least 1
 *    // counter available for AMDSMI_EVNT_GRP_XGMI on device dv_ind, create
 *    // an event object for an event of group AMDSMI_EVNT_GRP_XGMI (e.g.,
 *    // AMDSMI_EVNT_XGMI_0_BEATS_TX) and get the handle
 *    // (amdsmi_event_handle_t).
 *
 *    ret = amdsmi_gpu_create_counter(dv_ind, AMDSMI_EVNT_XGMI_0_BEATS_TX,
 *                                                          &evnt_handle);
 *
 *    // A program that generates the events of interest can be started
 *    // immediately before or after starting the counters.
 *    // Start counting:
 *    ret = amdsmi_gpu_control_counter(evnt_handle, AMDSMI_CNTR_CMD_START, NULL);
 *
 *    // Wait...
 *
 *    // Get the number of events since AMDSMI_CNTR_CMD_START was issued:
 *    ret = amdsmi_gpu_read_counter(amdsmi_event_handle_t evt_handle, &value)
 *
 *    // Wait...
 *
 *    // Get the number of events since amdsmi_gpu_read_counter() was last called:
 *    ret = amdsmi_gpu_read_counter(amdsmi_event_handle_t evt_handle, &value)
 *
 *    // Stop counting.
 *    ret = amdsmi_gpu_control_counter(evnt_handle, AMDSMI_CNTR_CMD_STOP, NULL);
 *
 *    // Release all resources (e.g., counter and memory resources) associated
 *    with evnt_handle.
 *    ret = amdsmi_gpu_destroy_counter(evnt_handle);
 *  @endcode
 *  @{
 */

/**
 *  @brief Tell if an event group is supported by a given device. It is not supported
 *  on virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle and an event group specifier @p
 *  group, tell if @p group type events are supported by the device associated
 *  with @p processor_handle
 *
 *  @param[in] processor_handle processor handle of device being queried
 *
 *  @param[in] group ::amdsmi_event_group_t identifier of group for which support
 *  is being queried
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_gpu_counter_group_supported(amdsmi_processor_handle processor_handle, amdsmi_event_group_t group);

/**
 *  @brief Create a performance counter object
 *
 *  @details Create a performance counter object of type @p type for the device
 *  with a processor handle of @p processor_handle, and write a handle to the object to the
 *  memory location pointed to by @p evnt_handle. @p evnt_handle can be used
 *  with other performance event operations. The handle should be deallocated
 *  with ::amdsmi_gpu_destroy_counter() when no longer needed.
 *
 *  @note This function requires root access
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] type the ::amdsmi_event_type_t of performance event to create
 *
 *  @param[in,out] evnt_handle A pointer to a ::amdsmi_event_handle_t which will be
 *  associated with a newly allocated counter
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_gpu_create_counter(amdsmi_processor_handle processor_handle, amdsmi_event_type_t type,
                                            amdsmi_event_handle_t *evnt_handle);

/**
 *  @brief Deallocate a performance counter object
 *
 *  @details Deallocate the performance counter object with the provided
 *  ::amdsmi_event_handle_t @p evnt_handle
 *
 *  @note This function requires root access
 *
 *  @param[in] evnt_handle handle to event object to be deallocated
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_gpu_destroy_counter(amdsmi_event_handle_t evnt_handle);

/**
 *  @brief Issue performance counter control commands. It is not supported on
 *  virtual machine guest
 *
 *  @details Issue a command @p cmd on the event counter associated with the
 *  provided handle @p evt_handle.
 *
 *  @note This function requires root access
 *
 *  @param[in] evt_handle an event handle
 *
 *  @param[in] cmd The event counter command to be issued
 *
 *  @param[in,out] cmd_args Currently not used. Should be set to NULL.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_gpu_control_counter(amdsmi_event_handle_t evt_handle,
                                  amdsmi_counter_command_t cmd, void *cmd_args);

/**
 *  @brief Read the current value of a performance counter
 *
 *  @details Read the current counter value of the counter associated with the
 *  provided handle @p evt_handle and write the value to the location pointed
 *  to by @p value.
 *
 *  @note This function requires root access
 *
 *  @param[in] evt_handle an event handle
 *
 *  @param[in,out] value pointer to memory of size of ::amdsmi_counter_value_t to
 *  which the counter value will be written
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_gpu_read_counter(amdsmi_event_handle_t evt_handle,
                    amdsmi_counter_value_t *value);

/**
 *  @brief Get the number of currently available counters. It is not supported on
 *  virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle, a performance event group @p grp,
 *  and a pointer to a uint32_t @p available, this function will write the
 *  number of @p grp type counters that are available on the device with handle
 *  @p processor_handle to the memory that @p available points to.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in] grp an event device group
 *
 *  @param[in,out] available A pointer to a uint32_t to which the number of
 *  available counters will be written
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
 amdsmi_get_gpu_available_counters(amdsmi_processor_handle processor_handle,
                                 amdsmi_event_group_t grp, uint32_t *available);

/** @} End PerfCntr */

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
 *  @param[in,out] procs a pointer to memory provided by the caller to which
 *  process information will be written. This may be NULL in which case only @p
 *  num_items will be updated with the number of processes found.
 *
 *  @param[in,out] num_items A pointer to a uint32_t, which on input, should
 *  contain the amount of memory in ::amdsmi_process_info_t's which have been
 *  provided by the @p procs argument. On output, if @p procs is non-NULL, this
 *  will be updated with the number ::amdsmi_process_info_t structs actually
 *  written. If @p procs is NULL, this argument will be updated with the number
 *  processes for which there is information.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_compute_process_info(amdsmi_process_info_t *procs, uint32_t *num_items);

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
 *  @param[in,out] proc a pointer to a ::amdsmi_process_info_t to which
 *  process information for @p pid will be written if it is found.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_compute_process_info_by_pid(uint32_t pid, amdsmi_process_info_t *proc);

/**
 *  @brief Get the device indices currently being used by a process
 *
 *  @details Given a process id @p pid, a non-NULL pointer to an array of
 *  uint32_t's @p processor_handleices of length *@p num_devices, this function will
 *  write up to @p num_devices device indices to the memory pointed to by
 *  @p processor_handleices. If @p processor_handleices is not NULL, @p num_devices will be
 *  updated with the number of gpu's currently being used by process @p pid.
 *  If @p processor_handleices is NULL, @p processor_handleices will be updated with the number of
 *  gpus currently being used by @p pid. Calling this function with @p
 *  dv_indices being NULL is a way to determine how much memory is required
 *  for when @p processor_handleices is not NULL.
 *
 *  @param[in] pid The process id of the process for which the number of gpus
 *  currently being used is requested
 *
 *  @param[in,out] dv_indices a pointer to memory provided by the caller to
 *  which indices of devices currently being used by the process will be
 *  written. This may be NULL in which case only @p num_devices will be
 *  updated with the number of devices being used.
 *
 *  @param[in,out] num_devices A pointer to a uint32_t, which on input, should
 *  contain the amount of memory in uint32_t's which have been provided by the
 *  @p processor_handleices argument. On output, if @p processor_handleices is non-NULL, this will
 *  be updated with the number uint32_t's actually written. If @p processor_handleices is
 *  NULL, this argument will be updated with the number devices being used.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_compute_process_gpus(uint32_t pid, uint32_t *dv_indices,
                                                       uint32_t *num_devices);

/** @} End SysInfo */

/*****************************************************************************/
/** @defgroup XGMIInfo XGMI Functions
 *  These functions are used to configure, query and control XGMI.
 *  @{
 */

/**
 *  @brief Retrieve the XGMI error status for a device. It is not supported on
 *  virtual machine guest
 *
 *  @details Given a processor handle @p processor_handle, and a pointer to an
 *  ::amdsmi_xgmi_status_t @p status, this function will write the current XGMI
 *  error state ::amdsmi_xgmi_status_t for the device @p processor_handle to the memory
 *  pointed to by @p status.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] status A pointer to an ::amdsmi_xgmi_status_t to which the
 *  XGMI error state should be written
 *  If this parameter is nullptr, this function will return
 *  ::AMDSMI_STATUS_INVAL if the function is supported with the provided,
 *  arguments and ::AMDSMI_STATUS_NOT_SUPPORTED if it is not supported with the
 *  provided arguments.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_gpu_xgmi_error_status(amdsmi_processor_handle processor_handle, amdsmi_xgmi_status_t *status);

/**
 * @brief Reset the XGMI error status for a device. It is not supported on virtual
 * machine guest
 *
 * @details Given a processor handle @p processor_handle, this function will reset the
 * current XGMI error state ::amdsmi_xgmi_status_t for the device @p processor_handle to
 * amdsmi_xgmi_status_t::AMDSMI_XGMI_STATUS_NO_ERRORS
 *
 * @param[in] processor_handle a processor handle
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_reset_gpu_xgmi_error(amdsmi_processor_handle processor_handle);

/** @} End SysInfo */

/*****************************************************************************/
/** @defgroup HWTopo Hardware Topology Functions
 *  These functions are used to query Hardware topology.
 *  @{
 */

/**
 *  @brief Retrieve the NUMA CPU node number for a device
 *
 *  @details Given a processor handle @p processor_handle, and a pointer to an
 *  uint32_t @p numa_node, this function will write the
 *  node number of NUMA CPU for the device @p processor_handle to the memory
 *  pointed to by @p numa_node.
 *
 *  @param[in] processor_handle a processor handle
 *
 *  @param[in,out] numa_node A pointer to an uint32_t to which the
 *  numa node number should be written.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_topo_get_numa_node_number(amdsmi_processor_handle processor_handle, uint32_t *numa_node);

/**
 *  @brief Retrieve the weight for a connection between 2 GPUs
 *
 *  @details Given a source processor handle @p processor_handle_src and
 *  a destination processor handle @p processor_handle_dst, and a pointer to an
 *  uint64_t @p weight, this function will write the
 *  weight for the connection between the device @p processor_handle_src
 *  and @p processor_handle_dst to the memory pointed to by @p weight.
 *
 *  @param[in] processor_handle_src the source processor handle
 *
 *  @param[in] processor_handle_dst the destination processor handle
 *
 *  @param[in,out] weight A pointer to an uint64_t to which the
 *  weight for the connection should be written.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_topo_get_link_weight(amdsmi_processor_handle processor_handle_src, amdsmi_processor_handle processor_handle_dst,
                          uint64_t *weight);

/**
 *  @brief Retreive minimal and maximal io link bandwidth between 2 GPUs
 *
 *  @details Given a source processor handle @p processor_handle_src and
 *  a destination processor handle @p processor_handle_dst,  pointer to an
 *  uint64_t @p min_bandwidth, and a pointer to uint64_t @p max_bandiwidth,
 *  this function will write theoretical minimal and maximal bandwidth limits.
 *  API works if src and dst are connected via xgmi and have 1 hop distance.
 *
 *  @param[in] processor_handle_src the source processor handle
 *
 *  @param[in] processor_handle_dst the destination processor handle
 *
 *  @param[in,out] min_bandwidth A pointer to an uint64_t to which the
 *  minimal bandwidth for the connection should be written.
 *
 *  @param[in,out] max_bandwidth A pointer to an uint64_t to which the
 *  maximal bandwidth for the connection should be written.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
 amdsmi_get_minmax_bandwith_between_processors(amdsmi_processor_handle processor_handle_src, amdsmi_processor_handle processor_handle_dst,
                          uint64_t *min_bandwidth, uint64_t *max_bandwidth);

/**
 *  @brief Retrieve the hops and the connection type between 2 GPUs
 *
 *  @details Given a source processor handle @p processor_handle_src and
 *  a destination processor handle @p processor_handle_dst, and a pointer to an
 *  uint64_t @p hops and a pointer to an AMDSMI_IO_LINK_TYPE @p type,
 *  this function will write the number of hops and the connection type
 *  between the device @p processor_handle_src and @p processor_handle_dst to the memory
 *  pointed to by @p hops and @p type.
 *
 *  @param[in] processor_handle_src the source processor handle
 *
 *  @param[in] processor_handle_dst the destination processor handle
 *
 *  @param[in,out] hops A pointer to an uint64_t to which the
 *  hops for the connection should be written.
 *
 *  @param[in,out] type A pointer to an ::AMDSMI_IO_LINK_TYPE to which the
 *  type for the connection should be written.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_topo_get_link_type(amdsmi_processor_handle processor_handle_src,
                        amdsmi_processor_handle processor_handle_dst,
                        uint64_t *hops, AMDSMI_IO_LINK_TYPE *type);

/**
 *  @brief Return P2P availability status between 2 GPUs
 *
 *  @details Given a source processor handle @p processor_handle_src and
 *  a destination processor handle @p processor_handle_dst, and a pointer to a
 *  bool @p accessible, this function will write the P2P connection status
 *  between the device @p processor_handle_src and @p processor_handle_dst to the memory
 *  pointed to by @p accessible.
 *
 *  @param[in] processor_handle_src the source processor handle
 *
 *  @param[in] processor_handle_dst the destination processor handle
 *
 *  @param[in,out] accessible A pointer to a bool to which the status for
 *  the P2P connection availablity should be written.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_is_P2P_accessible(amdsmi_processor_handle processor_handle_src, amdsmi_processor_handle processor_handle_dst,
                       bool *accessible);

/** @} End HWTopo */

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
 * ID @p processor_handle, by initializing any required system parameters. This call
 * may open files which will remain open until ::amdsmi_stop_gpu_event_notification()
 * is called.
 *
 * @param processor_handle a processor handle corresponding to the device on which to
 * listen for events
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_init_gpu_event_notification(amdsmi_processor_handle processor_handle);

/**
 * @brief Specify which events to collect for a device
 *
 * @details Given a processor handle @p processor_handle and a @p mask consisting of
 * elements of ::amdsmi_evt_notification_type_t OR'd together, this function
 * will listen for the events specified in @p mask on the device
 * corresponding to @p processor_handle.
 *
 * @param processor_handle a processor handle corresponding to the device on which to
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
 * @note ::AMDSMI_STATUS_INIT_ERROR is returned if
 * ::amdsmi_init_gpu_event_notification() has not been called before a call to this
 * function
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
 amdsmi_set_gpu_event_notification_mask(amdsmi_processor_handle processor_handle, uint64_t mask);

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
 * This function requires prior calls to ::amdsmi_init_gpu_event_notification() and
 * :: amdsmi_set_gpu_event_notification_mask(). This function polls for the
 * occurrance of the events on the respective devices that were previously
 * specified by :: amdsmi_set_gpu_event_notification_mask().
 *
 * @param[in] timeout_ms number of milliseconds to wait for an event
 * to occur
 *
 * @param[in,out] num_elem pointer to uint32_t, provided by the caller. On
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
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
 amdsmi_get_gpu_event_notification(int timeout_ms,
                     uint32_t *num_elem, amdsmi_evt_notification_data_t *data);

/**
 * @brief Close any file handles and free any resources used by event
 * notification for a GPU
 *
 * @details Any resources used by event notification for the GPU with
 * processor handle @p processor_handle will be free with this
 * function. This includes freeing any memory and closing file handles. This
 * should be called for every call to ::amdsmi_init_gpu_event_notification()
 *
 * @param[in] processor_handle The processor handle of the GPU for which event
 * notification resources will be free
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t amdsmi_stop_gpu_event_notification(amdsmi_processor_handle processor_handle);

/** @} End EvntNotif */

/**
 *  @brief          Returns BDF of the given device
 *
 *  @param[in]      processor_handle Device which to query
 *
 *  @param[out]     bdf Reference to BDF. Must be allocated by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_device_bdf(amdsmi_processor_handle processor_handle, amdsmi_bdf_t *bdf);

/**
 *  @brief          Returns the UUID of the device
 *
 *  @param[in]      processor_handle Device which to query
 *
 *  @param[in,out]  uuid_length Length of the uuid string. As input, must be
 *                  equal or greater than SMI_GPU_UUID_SIZE and be allocated by
 *                  user. As output it is the length of the uuid string.
 *
 *  @param[out]     uuid Pointer to string to store the UUID. Must be
 *                  allocated by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_device_uuid(amdsmi_processor_handle processor_handle, unsigned int *uuid_length, char *uuid);

/*****************************************************************************/
/** @defgroup swversion     SW Version Information
 *  @{
 */

/**
 *  @brief          Returns the driver version information
 *
 *  @param[in]      processor_handle Device which to query
 *
 *  @param[in,out]  length As input parameter length of the user allocated
 *                  string buffer. As output parameter length of the returned
 *                  string buffer.
 *
 *  @param[out]     version Version information in string format. Must be
 *                  allocated by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_driver_version(amdsmi_processor_handle processor_handle, int *length, char *version);

/** @} End swversion */

/*****************************************************************************/
/** @defgroup asicinfo     ASIC & Board Static Information
 *  @{
 */

/**
 *  @brief          Returns the ASIC information for the device
 * 
 *  @details        This function returns ASIC information such as the product name,
 *                  the vendor ID, the subvendor ID, the device ID,
 *                  the revision ID and the serial number.
 *
 *  @param[in]      processor_handle Device which to query
 *
 *  @param[out]     info Reference to static asic information structure.
 *                  Must be allocated by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_asic_info(amdsmi_processor_handle processor_handle, amdsmi_asic_info_t *info);

/**
 *  @brief          Returns the board part number and board information for the requested device
 *
 *  @param[in]      processor_handle Device which to query
 *
 *  @param[out]     info Reference to board info structure.
 *                  Must be allocated by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_board_info(amdsmi_processor_handle processor_handle, amdsmi_board_info_t *info);

/**
 *  @brief          Returns the power caps as currently configured in the
 *                  system. It is not supported on virtual machine guest
 *
 *  @param[in]      processor_handle Device which to query
 *  @param[in]      sensor_ind A 0-based sensor index. Normally, this will be 0.
 *                  If a device has more than one sensor, it could be greater than 0.
 *  @param[out]     info Reference to power caps information structure. Must be
 *                  allocated by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_power_cap_info(amdsmi_processor_handle processor_handle, uint32_t sensor_ind,
          amdsmi_power_cap_info_t *info);

/**
 *  @brief          Returns XGMI information for the GPU.
 *
 *  @param[in]      processor_handle Device which to query
 *
 *  @param[out]     info Reference to xgmi information structure. Must be
 *                  allocated by user.
 *
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_xgmi_info(amdsmi_processor_handle processor_handle, amdsmi_xgmi_info_t *info);

/** @} End asicinfo */

/*****************************************************************************/
/** @defgroup firmwareinfo     Firmware & VBIOS queries
 *  @{
 */

/**
 *  @brief          Returns the firmware versions running on the device.
 *
 *  @param[in]      processor_handle Device which to query
 *
 *  @param[out]     info Reference to the fw info. Must be allocated by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_fw_info(amdsmi_processor_handle processor_handle, amdsmi_fw_info_t *info);

/**
 *  @brief          Returns the static information for the vBIOS on the device.
 *
 *  @param[in]      processor_handle Device which to query
 *
 *  @param[out]     info Reference to static vBIOS information.
 *                  Must be allocated by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_vbios_info(amdsmi_processor_handle processor_handle, amdsmi_vbios_info_t *info);

/** @} End fwinfo */

/*****************************************************************************/
/** @defgroup gpumon     GPU Monitoring
 *  @{
 */

/**
 *  @brief          Returns the current usage of the GPU engines (GFX, MM and MEM).
 *                  Each usage is reported as a percentage from 0-100%. It is not
 *                  supported on virtual machine guest
 *
 *  @param[in]      processor_handle Device which to query
 *
 *  @param[out]     info Reference to the gpu engine usage structure. Must be allocated by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_activity(amdsmi_processor_handle processor_handle, amdsmi_engine_usage_t *info);

/**
 *  @brief          Returns the current power and voltage of the GPU.
 *                  The voltage is in units of mV and the power in units of W.
 *                  It is not supported on virtual machine guest
 *
 *  @param[in]      processor_handle Device which to query
 *
 *  @param[out]     info Reference to the gpu power structure. Must be allocated by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_power_info(amdsmi_processor_handle processor_handle, amdsmi_power_info_t *info);

/**
 *  @brief          Returns the measurements of the clocks in the GPU
 *                  for the GFX and multimedia engines and Memory. This call
 *                  reports the averages over 1s in MHz. It is not supported
 *                  on virtual machine guest
 *
 *  @param[in]      processor_handle Device which to query
 *
 *  @param[in]      clk_type Enum representing the clock type to query.
 *
 *  @param[out]     info Reference to the gpu clock structure.
 *                  Must be allocated by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_clock_info(amdsmi_processor_handle processor_handle, amdsmi_clk_type_t clk_type, amdsmi_clk_info_t *info);

/**
 *  @brief          Returns the VRAM usage (both total and used memory)
 *                  in MegaBytes.
 *
 *  @param[in]      processor_handle Device which to query
 *
 *
 *  @param[out]     info Reference to vram information.
 *                  Must be allocated by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_vram_usage(amdsmi_processor_handle processor_handle, amdsmi_vram_info_t *info);

/** @} End gpumon */

/*****************************************************************************/
/**  @defgroup processinfo     Process information
 *  @{
 */

/**
 *  @brief          Returns the list of processes running on a given GPU including itself.
 *
 *  @note           The user provides a buffer to store the list and the maximum
 *                  number of processes that can be returned. If the user sets
 *                  max_processes to 0, the current total number of processes will
 *                  replace max_processes param. After that, the function needs to be
 *                  called again, with updated max_processes, to successfully fill the
 *                  process list, which was previously allocated with max_processes
 *
 *  @param[in]      processor_handle Device which to query
 *
 *  @param[in,out]  max_processes Reference to the size of the list buffer in
 *                  number of elements. Returns the return number of elements
 *                  in list or the number of running processes if equal to 0,
 *                  and if given value in param max_processes is less than
 *                  number of processes currently running,
 *                  AMDSMI_STATUS_OUT_OF_RESOURCES will be returned.
 *
 *  @param[out]     list Reference to a user-provided buffer where the process
 *                  list will be returned. This buffer must contain at least
 *                  max_processes entries of type smi_process_handle. Must be allocated
 *                  by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_process_list(amdsmi_processor_handle processor_handle, uint32_t *max_processes, amdsmi_process_handle_t *list);

/**
 *  @brief          Returns the process information of a given process.
 *                  Engine usage show how much time the process spend using these engines in ns.
 *
 *  @param[in]      processor_handle Device which to query
 *
 *  @param[in]      process Handle of process to query.
 *
 *  @param[out]     info Reference to a process information structure where to return
 *                  information. Must be allocated by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_process_info(amdsmi_processor_handle processor_handle, amdsmi_process_handle_t process, amdsmi_proc_info_t *info);

/** @} End processinfo */

/*****************************************************************************/
/** @defgroup eccinfo     ECC information
 *  @{
 */

/**
 *  @brief          Returns the total number of ECC errors (correctable and
 *                  uncorrectable) in the given GPU. It is not supported on
 *                  virtual machine guest
 *
 *  @param[in]      processor_handle Device which to query
 *
 *  @param[out]     ec Reference to ecc error count structure.
 *                  Must be allocated by user.
 *
 *  @return ::amdsmi_status_t | ::AMDSMI_STATUS_SUCCESS on success, non-zero on fail
 */
amdsmi_status_t
amdsmi_get_gpu_total_ecc_count(amdsmi_processor_handle processor_handle, amdsmi_error_count_t *ec);

/** @} End eccinfo */

#ifdef __cplusplus
}
#endif  // __cplusplus
#endif  // INCLUDE_AMDSMI_H_

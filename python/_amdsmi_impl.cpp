// Copyright (c) Advanced Micro Devices, Inc. All rights reserved.

#include <nanobind/nanobind.h>
#include <amd_smi/amdsmi.h>
#include <stdexcept>
#include <string>
#include <vector>

namespace nb = nanobind;
using namespace nb::literals;

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)

NB_MODULE(_amdsmi_impl, m) {
    m.doc() = "AMDSMI Python bindings";

    // Version info
    m.attr("__version__") = TOSTRING(VERSION_INFO);

    // Define custom exception
    auto amdsmi_exception = nb::exception<std::runtime_error>(m, "AmdSmiException");

    // Initialization flags enum
    nb::enum_<amdsmi_init_flags_t>(m, "InitFlags")
        .value("INIT_ALL_PROCESSORS", AMDSMI_INIT_ALL_PROCESSORS)
        .value("INIT_AMD_CPUS", AMDSMI_INIT_AMD_CPUS)
        .value("INIT_AMD_GPUS", AMDSMI_INIT_AMD_GPUS)
        .value("INIT_NON_AMD_CPUS", AMDSMI_INIT_NON_AMD_CPUS)
        .value("INIT_NON_AMD_GPUS", AMDSMI_INIT_NON_AMD_GPUS)
        .value("INIT_AMD_APUS", AMDSMI_INIT_AMD_APUS);

    // Status codes enum
    nb::enum_<amdsmi_status_t>(m, "Status")
        .value("SUCCESS", AMDSMI_STATUS_SUCCESS)
        .value("INVAL", AMDSMI_STATUS_INVAL)
        .value("NOT_SUPPORTED", AMDSMI_STATUS_NOT_SUPPORTED)
        .value("NOT_YET_IMPLEMENTED", AMDSMI_STATUS_NOT_YET_IMPLEMENTED);

    // Helper function to check status and throw exception
    auto check_status = [](amdsmi_status_t status) {
        if (status != AMDSMI_STATUS_SUCCESS) {
            throw std::runtime_error("AMDSMI error: " + std::to_string(static_cast<int>(status)));
        }
    };

    // Core library functions
    m.def("init", [check_status](amdsmi_init_flags_t flags = AMDSMI_INIT_AMD_GPUS) {
        check_status(amdsmi_init(flags));
    }, "flags"_a = AMDSMI_INIT_AMD_GPUS, "Initialize AMDSMI library");

    m.def("shut_down", [check_status]() {
        check_status(amdsmi_shut_down());
    }, "Shutdown AMDSMI library");

    // Processor count function
    m.def("get_processor_count", [check_status]() -> uint32_t {
        uint32_t socket_count = 0;
        check_status(amdsmi_get_socket_handles(&socket_count, nullptr));

        if (socket_count == 0) {
            return 0;
        }

        std::vector<amdsmi_socket_handle> sockets(socket_count);
        check_status(amdsmi_get_socket_handles(&socket_count, sockets.data()));

        uint32_t total_processor_count = 0;
        for (uint32_t i = 0; i < socket_count; i++) {
            uint32_t processor_count = 0;
            // Get processor count for this socket
            check_status(amdsmi_get_processor_handles(sockets[i], &processor_count, nullptr));
            total_processor_count += processor_count;
        }

        return total_processor_count;
    }, "Get total processor count");

    // Simple test function - just return a constant
    m.def("get_socket_count", []() -> uint32_t {
        return 42; // Dummy implementation for testing
    }, "Get CPU socket count");

    // Version functions
    m.def("get_lib_version", [check_status]() {
        amdsmi_version_t version;
        check_status(amdsmi_get_lib_version(&version));
        return nb::make_tuple(version.major, version.minor, version.release);
    }, "Get library version (major, minor, release)");

    // Constants
    m.attr("MAX_STRING_LENGTH") = AMDSMI_MAX_STRING_LENGTH;
    m.attr("MAX_DEVICES") = AMDSMI_MAX_DEVICES;
}
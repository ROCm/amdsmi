/*
 * Copyright (c) Advanced Micro Devices, Inc. All rights reserved.
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

#ifndef AMDSMI_EXPORT_H
#define AMDSMI_EXPORT_H

#ifdef AMDSMI_STATIC_DEFINE
#  define AMDSMI_EXPORT
#  define AMDSMI_NO_EXPORT
#  define AMDSMI_API
#else
#  ifndef AMDSMI_EXPORT
#    ifdef _AMDSMI_BUILDING_DYLIB
       /* We are building this library */
#      define AMDSMI_EXPORT __attribute__((visibility("default")))
#    else
       /* We are using this library */
#      define AMDSMI_EXPORT __attribute__((visibility("default")))
#    endif
#  endif

#  ifndef AMDSMI_NO_EXPORT
#    define AMDSMI_NO_EXPORT __attribute__((visibility("hidden")))
#  endif

#  ifndef AMDSMI_API
#    define AMDSMI_API AMDSMI_EXPORT
#  endif
#endif

#ifndef AMDSMI_DEPRECATED
#  define AMDSMI_DEPRECATED __attribute__ ((__deprecated__))
#endif

#ifndef AMDSMI_DEPRECATED_EXPORT
#  define AMDSMI_DEPRECATED_EXPORT AMDSMI_EXPORT AMDSMI_DEPRECATED
#endif

#ifndef AMDSMI_DEPRECATED_NO_EXPORT
#  define AMDSMI_DEPRECATED_NO_EXPORT AMDSMI_NO_EXPORT AMDSMI_DEPRECATED
#endif

#if 0 /* DEFINE_NO_DEPRECATED */
#  ifndef AMDSMI_NO_DEPRECATED
#    define AMDSMI_NO_DEPRECATED
#  endif
#endif

#endif /* AMDSMI_EXPORT_H */
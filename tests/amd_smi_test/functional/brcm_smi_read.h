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

#ifndef TESTS_AMD_SMI_TEST_FUNCTIONAL_BRCM_SMI_READ_H_
#define TESTS_AMD_SMI_TEST_FUNCTIONAL_BRCM_SMI_READ_H_

#include "../test_base.h"

#ifdef ENABLE_BRCM_SMI

class TestBrcmSmiRead : public TestBase {
 public:
    TestBrcmSmiRead();

  // @Brief: Destructor for test case of TestBrcmSmiRead
  virtual ~TestBrcmSmiRead();

  // @Brief: Setup the environment for measurement
  virtual void SetUp();

  // @Brief: Core measurement execution
  virtual void Run();

  // @Brief: Clean up and retrieve the resource
  virtual void Close();

  // @Brief: Display results
  virtual void DisplayResults() const;

  // @Brief: Display information about what this test does
  virtual void DisplayTestInfo(void);

 private:
  // @Brief: Test BRCM SMI initialization and shutdown
  void TestBrcmSmiInit();
  
  // @Brief: Test BRCM SMI device discovery
  void TestBrcmSmiDiscovery();
  
  // @Brief: Test NIC device information retrieval
  void TestNicDeviceInfo();
  
  // @Brief: Test Switch device information retrieval
  void TestSwitchDeviceInfo();
  
  // @Brief: Test NIC metrics retrieval
  void TestNicMetrics();
  
  // @Brief: Test Switch metrics retrieval
  void TestSwitchMetrics();
  
  // @Brief: Test error handling for invalid parameters
  void TestErrorHandling();
};

#endif // ENABLE_BRCM_SMI

#endif  // TESTS_AMD_SMI_TEST_FUNCTIONAL_BRCM_SMI_READ_H_

#!/usr/bin/python
# vi: ts=4 expandtab syntax=python
##############################################################################
# Copyright (c) 2008 IBM Corporation
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
# Marcos Cintron (IBM) - initial implementation
##############################################################################
import unittest

import OvfTestCase
import OvfSetTestCase
import OvfFileTestCase
import OvfReferencedFileTestCase
import OvfManifestTestCase
import OvfCertificateTestCase
import OvfEnvironmentTestCase
import OvfPropertyTestCase
import OvfPlatformTestCase
import OvfTransportTestCase
import OvfLibvirtTestCase

if __name__ == "__main__":
    test = []
    test.append(unittest.TestLoader().loadTestsFromModule(OvfTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfSetTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfFileTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfReferencedFileTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfManifestTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfCertificateTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfEnvironmentTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfPropertyTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfPlatformTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfTransportTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfLibvirtTestCase))
    runner = unittest.TextTestRunner(verbosity=2)

    testSuite = unittest.TestSuite()
    for each in test:
        testSuite.addTest(each)
    runner.run(testSuite)


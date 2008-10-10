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

if __name__ == "__main__":
    test = []
    test.append(unittest.TestLoader().loadTestsFromModule(OvfTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfSetTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfFileTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfReferencedFileTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfManifestTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfCertificateTestCase))
    test.append(unittest.TestLoader().loadTestsFromModule(OvfEnvironmentTestCase))
    runner = unittest.TextTestRunner(verbosity=2)

    testSuite = unittest.TestSuite()
    for each in test:
        testSuite.addTest(each)
    runner.run(testSuite)


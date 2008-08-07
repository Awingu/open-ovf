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
# Eric Casler (IBM) - initial implementation
##############################################################################
import unittest, os

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files/")

class OvfCertificateTestCase(unittest.TestCase):
    pass

if __name__ == "__main__":
    test = unittest.TestLoader().loadTestsFromTestCase(OvfCertificateTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(unittest.TestSuite(test))

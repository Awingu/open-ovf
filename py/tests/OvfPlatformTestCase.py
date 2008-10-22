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
# Dave Leskovec (IBM) - initial implementation
##############################################################################
"""
Test case for functions in OvfPlatform.py
"""

import unittest, os
from locale import getlocale, getdefaultlocale
from time import timezone

from ovf import Ovf
from ovf.OvfFile import OvfFile
from ovf import OvfPlatform

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files/")

class OvfPropertyTestCase(unittest.TestCase):
    """
    Test OvfProperty functions
    """

    path = TEST_FILES_DIR

    ovf = 'someOVF.ovf'


    def test_getPlatformDict(self):
        """
        Test OvfPlatform.getPlatformDict
        """
        ovfFileName = self.path+"/"+self.ovf
        ovfFile = OvfFile(ovfFileName)
        # Get the virtual system node in the ovf
        vsNode = Ovf.getContentEntities(ovfFile.envelope, None,
                                        True, False)[0]

        # gather some values to compare
        (langCode, encoding) = getlocale()
        if langCode == None:
            (langCode, encoding) = getdefaultlocale()

        # Case with no platform type
        platformDict = OvfPlatform.getPlatformDict(vsNode)
        assert platformDict['Kind'] == 'vmx-4', "failed type test"
        assert platformDict['Locale'] == langCode, "failed locale test"
        assert platformDict['TimeZone'] == timezone, "failed timezone test"


        # Case with platform type
        platformDict = OvfPlatform.getPlatformDict(vsNode, "qemu")
        assert platformDict['Kind'] == 'qemu', "with type: failed type test"
        assert platformDict['Locale'] == langCode, \
                                         "with type: failed locale test"
        assert platformDict['TimeZone'] == timezone, \
                                           "with type: failed timezone test"



if __name__ == "__main__":
    TEST = unittest.TestLoader().loadTestsFromTestCase(OvfPropertyTestCase)
    RUNNER = unittest.TextTestRunner(verbosity=2)
    RUNNER.run(unittest.TestSuite(TEST))

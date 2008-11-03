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
Test case for functions in OvfTransport.py
"""

import unittest, os
import hashlib
from subprocess import call
from subprocess import Popen
from subprocess import PIPE
from subprocess import STDOUT

from ovf import OvfTransport

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files/")

def compareFileMD5s(isoFileName, sourceFile, isoEnvFile=None):
    """
    Dump isoEnvFile on isoFileName.  Compare it's md5 sum to the sum
    for sourceFile.
    """
    isoinfoCmd = ["isoinfo", "-JR", "-i", isoFileName, "-x", ""]

    # the way this is done assumes a reasonable sized env file.  if
    # the size of these files get bigger, this algorithm would need
    # to be changed
    sourcemd5 = hashlib.md5()
    sfd = open(sourceFile)
    fileContents = sfd.read()
    sourcemd5.update(fileContents)
    sfd.close()

    # run command to dump file out of iso
    if not isoEnvFile:
        isoEnvFile = os.path.basename(sourceFile)
    isoinfoCmd[5] = '/' + isoEnvFile
    pcmd = Popen(isoinfoCmd, stdout=PIPE, stderr=STDOUT)
    isodump = pcmd.communicate()[0]
    targetmd5 = hashlib.md5()
    targetmd5.update(isodump)

    return sourcemd5.digest() == targetmd5.digest()

class OvfTransportTestCase(unittest.TestCase):
    """
    Test OvfTransport functions
    """

    path = TEST_FILES_DIR
    outIsoFile = path + 'ourOVF.iso'
    inEnvFile = path + 'test-environment.xml'


    def test_selectISOProgram(self):
        """
        Test OvfTransport.selectISOProgram
        """
        isoProgs = ['genisoimage', 'mkisofs']

        # inspect the system to see what's installed and where
        for prog in isoProgs:
            retcode = call(["which", prog], stdout=PIPE, stderr=STDOUT)
            if not retcode:
                isoProg = OvfTransport.selectISOProgram()
                assert isoProg == prog, "failed test for: " + prog
                return

        self.fail("no ISO format programs available on system")



    def test_makeISOTransport(self):
        """
        Test OvfTransport.makeISOTransport
        """
        makeFileList = [(self.outIsoFile, [self.inEnvFile])]
        OvfTransport.makeISOTransport(makeFileList)

        # validate the generated image
        self.assertTrue(os.path.exists(self.outIsoFile),
                        'ISO file was not created')

        retcode = call(["which", "isoinfo"], stdout=PIPE, stderr=STDOUT)
        if not retcode:
            # for each file, dump the file and calc the md5 sum.  compare
            # that to the one for the original file.
            # the way this is done assumes a reasonable sized env file.  if
            # the size of these files get bigger, this algorithm would need
            # to be changed

            # check the env file first
            for (outfilename, infilelist) in makeFileList:
                self.assertTrue(compareFileMD5s(outfilename, infilelist[0],
                                                'ovf-env.xml'),
                                'MD5 miscompare')

                restOfFiles = infilelist[1:]
                for curFile in restOfFiles:
                    # assert the two are equal
                    self.assertTrue(compareFileMD5s(outfilename, curFile),
                                    'MD5 mismatch')


if __name__ == "__main__":
    TEST = unittest.TestLoader().loadTestsFromTestCase(OvfTransportTestCase)
    RUNNER = unittest.TextTestRunner(verbosity=2)
    RUNNER.run(unittest.TestSuite(TEST))

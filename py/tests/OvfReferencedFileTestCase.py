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
import unittest, os, time
from stat import *
from xml.dom.minidom import parse

from ovf import OvfReferencedFile

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files/")

def isSamePath(a,b):
    return ( os.path.abspath(a) == os.path.abspath(b) )

class OvfReferencedFileTestCase(unittest.TestCase):
    """

    """

    ovfRef = None
    ovfRef2 = None
    "OvfReferencedFile variables"
    href = "ourOVF.ovf"
    path = TEST_FILES_DIR

    checksum = "5b47e3fe7e6d727c274de9d926b085467c9d8856"

    checksumStamp = None

    size = 7549
    chunksize = 0
    compression = "gzip"
    file_id = "file1"

    def setUp(self):
        self.ovfRef = OvfReferencedFile.OvfReferencedFile(self.path + self.href,self.href)
        self.ovfRef2 = OvfReferencedFile.OvfReferencedFile(self.path + self.href,self.href,self.checksum,self.checksumStamp,self.size,self.compression,self.file_id,self.chunksize)
    def tearDown(self):
        self.ovfRef = None

    def test_NewObj(self):
        #"Test 1: Create object with only a path and an href and access them"
        #check to see that the object is created
        assert isSamePath(self.ovfRef.path,self.path + self.href),"Test1: path do not match"
        assert self.ovfRef.href == self.href, "Test1: href do not match"

        #"Test 1.1: Create object with all fields and access them"
        assert isSamePath(self.ovfRef2.path, self.path + self.href),"Test1.1: path do not match"
        assert self.ovfRef2.href == self.href, "Test1.1: href do not match"
        assert self.ovfRef2.checksum == self.checksum, "Test1.1: checksum do not match"
        assert self.ovfRef2.checksumStamp == self.checksumStamp, "Test1.1: checksumStamp do not match"
        assert self.ovfRef2.size == self.size, "Test1.1: size do not match"
        assert self.ovfRef2.compression == self.compression, "Test1.1: compression do not match"
        assert self.ovfRef2.file_id == self.file_id, "Test1.1: file_id does not match"

    def test_getFileObject(self):

        fd = open(self.path + self.href,"rb")
        fd2 = self.ovfRef2.getFileObject()

        assert fd2.readline()== fd.readline(),"compare files failed"

       # assert cmp(fd,fd2) == 1 , "files are not equal using cmp(fd,fd2)"

        fd.close()
        fd2.close()

    def test_doChecksum(self):

        assert self.ovfRef.checksumStamp == None, "The time stamp was set. Not expecting to already be set."
        file=self.ovfRef.getFileObject()

        self.ovfRef.doChecksum()


        self.checksumStamp=time.gmtime(os.fstat(file.fileno())[ST_MTIME])

        assert self.checksumStamp == self.ovfRef.checksumStamp,"checksum timestamp does not match"
        assert self.ovfRef.checksum == self.checksum , "checksum does not match"

        #print time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())

    def test_setChecksum(self):

        self.ovfRef.setChecksum(self.checksum,self.checksumStamp)

        assert self.ovfRef.checksum == self.checksum, "checksum does not match"
        assert self.ovfRef.checksumStamp == self.checksumStamp, "checksumstamp does not match"

    def test_getChecksum(self):

        assert self.ovfRef.checksum == None, "checksum incorrect"

        self.ovfRef.setChecksum(self.checksum)
        assert self.ovfRef.checksum == self.checksum, "checksum does not match"

    def test_setChecksumStamp(self):

        assert self.ovfRef.checksumStamp == None, "checksumStamp incorrect"

        self.ovfRef.setChecksumStamp(self.checksumStamp)

        assert self.ovfRef.checksumStamp == self.checksumStamp, "checksumStamp incorrect"

    def test_setCompression(self):

        assert self.ovfRef.compression == None, "incorrect compression"

        self.ovfRef.setCompression(self.compression)
        assert self.ovfRef.compression == self.compression, "incorrect compression"

    def test_getCompression(self):

        assert self.ovfRef2.getCompression() == self.compression, "incorrect compression"


if __name__ == "__main__":
    test = unittest.TestLoader().loadTestsFromTestCase(OvfReferencedFileTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(unittest.TestSuite(test))

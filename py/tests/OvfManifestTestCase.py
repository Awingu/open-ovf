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

from ovf import OvfReferencedFile
from ovf.OvfManifest import *

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files/")

def isSamePath(a,b):
    return ( os.path.abspath(a) == os.path.abspath(b) )

class OvfManifestTestCase(unittest.TestCase):

    path = TEST_FILES_DIR

    ovf = 'ourOVF.ovf'
    mf = 'ourOVF.mf'
    cert = 'ourOVF.cert'
    img1 = 'Ubuntu1.vmdk'
    img2 = 'Ubuntu-0.vmdk'

    ovfSum = '5b47e3fe7e6d727c274de9d926b085467c9d8856'
   # mfSum = '78554e6c131f57a1b2e1fe860a29b7cbf6af859c'
    certSum = 'bf1ae2642e7dacac1a8fa0d1759925b836693dc5'
    img1Sum = 'fb86e12e912c3a002daf0d8b8bf579e69578c14b'
    img2Sum = 'fdb10384ba4362317ac4048e858707be936a274f'



    def test_getReferencedFilesFromManifest(self):
        files = []

        name = self.path+"/"+self.ovf
        files.append(OvfReferencedFile.OvfReferencedFile(name,self.ovf,self.ovfSum))
        name = self.path+"/"+self.img1
        files.append(OvfReferencedFile.OvfReferencedFile(name,self.img1,self.img1Sum))
        name = self.path+"/"+self.img2
        files.append(OvfReferencedFile.OvfReferencedFile(name,self.img2,self.img2Sum))

        list = getReferencedFilesFromManifest(self.path + self.mf)

        i = 0
        for curr in list:
            assert curr.href == files[i].href, "href do not match"
            assert isSamePath(curr.path, files[i].path), "path do not match"
            assert curr.checksum.strip() == files[i].checksum, "checksum do not match"
            i+=1
        self.assertRaises(Exception,getReferencedFilesFromManifest,name)

    def test_writeManifestFromReferencedFilesList(self):
        files = []
        name = self.path+"/"+self.ovf

        files.append(OvfReferencedFile.OvfReferencedFile(name,self.ovf,self.ovfSum))
        mfname = self.path+"/"+'tmp'+self.mf
        #files.append(OvfReferencedFile.OvfReferencedFile(mfname,self.mf,self.mfSum))
        name = self.path+"/"+self.cert
        files.append(OvfReferencedFile.OvfReferencedFile(name,self.cert,self.certSum))
        name = self.path+"/"+self.img1
        files.append(OvfReferencedFile.OvfReferencedFile(name,self.img1,self.img1Sum))
        name = self.path+"/"+self.img2
        files.append(OvfReferencedFile.OvfReferencedFile(name,self.img2,self.img2Sum))

        writeManifestFromReferencedFilesList(mfname,files)

        assert os.path.isfile(mfname) == True , "File not created: " + mfname
        os.remove(mfname)

if __name__ == "__main__":
    test = unittest.TestLoader().loadTestsFromTestCase(OvfManifestTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(unittest.TestSuite(test))

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

from ovf import OvfFile
from ovf import OvfSet
from ovf import OvfReferencedFile
from xml.dom.minidom import parse
import tempfile, os, shutil, unittest, tarfile, sys
import testUtils

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files/")

class SimpleTestCase(unittest.TestCase):
    def setUp(self):
        # Create OvfSet Object
        self.path = TEST_FILES_DIR
        self.ovfSetObject = OvfSet.OvfSet(self.path + 'ourOVF.ovf','r')
        
    def tearDown(self):
        # Dispose of OvfSet instance
        self.ovfSetObject.__del__()
        self.ovfSetObject = None
        
    def test_getName(self):
        """Testing OvfSet.getName"""
        self.ovfSetObject.name = 'ourOVF'
        self.assertEqual(self.ovfSetObject.getName(), 'ourOVF')

    def test_setName(self):
        """Testing OvfSet.setName"""
        self.ovfSetObject.name = 'ourOVF'
        self.ovfSetObject.setName('testOvf')
        self.assertEqual(self.ovfSetObject.name, 'testOvf')
        self.assertRaises(TypeError, self.ovfSetObject.setName, None)

    def test_toString(self):
        """Testing OvfSet.toString"""
        self.ovfSetObject.name = 'ourOVF'
        self.ovfSetObject.mode = "r"
        self.ovfSetObject.archiveFormat = "Dir"
        self.ovfSetObject.archivePath = "tests/"
        self.ovfSetObject.archiveSavePath = "tests/archive/"
        
        string = "name=ourOVF mode=r archiveFormat=Dir archivePath=tests/" \
            + " archiveSavePath=tests/archive/"
        if self.ovfSetObject.__tmpdir__ != None:
            string = string + " tmpdir=" + self.ovfSetObject.__tmpdir__
        self.assertEqual(self.ovfSetObject.toString(), string)
        
    def test_getOvfFile(self):
        """Testing OvfSet.getOvfFile"""
        self.assertEqual(self.ovfSetObject.getOvfFile().path, self.path + 'ourOVF.ovf')
        self.assertEqual(self.ovfSetObject.getOvfFile().document.toxml(), \
                         parse(self.path + 'ourOVF.ovf').toxml())
        refList = self.ovfSetObject.getOvfFile().files
        testList = ["Ubuntu1.vmdk","Ubuntu-0.vmdk","ourOVF.mf","ourOVF.cert"]
        for each in refList:
            testList.remove(each.href)
        self.assertEqual(testList,[])

    def test_verifyManifest(self):
        """Testing OvfSet.verifyManifest"""
        self.assertTrue(self.ovfSetObject.verifyManifest(self.path + 'ourOVF.mf'))
        for each in self.ovfSetObject.ovfFile.files:
            if each.href == 'Ubuntu1.vmdk':
                each.checksum = "wrongChecksum!!!"
            else:
                self.ovfSetObject.ovfFile.files.pop(0)
        self.assertFalse(self.ovfSetObject.verifyManifest(self.path + 'ourOVF.mf'))
        self.assertRaises(IOError, self.ovfSetObject.verifyManifest, '!')

class WriteTestCase(unittest.TestCase):
    def setUp(self):
        # Create OvfSet Object
        self.path = TEST_FILES_DIR
        self.ovfSetObject = OvfSet.OvfSet(self.path + 'ourOVF.ovf','r')
        
        # Create temporary directory to store test files
        self.tmpDir = tempfile.mkdtemp() + '/'
        self.assertTrue(os.path.isdir(self.tmpDir), 'Temp directory failed to be created')
        
    def tearDown(self):
        # Dispose of OvfSet instance
        self.ovfSetObject.__del__()
        self.ovfSetObject = None
        
        # Remove temporary files
        shutil.rmtree(self.tmpDir)
        self.assertFalse(os.path.isdir(self.tmpDir), 'Temporary files were not successfully removed')
        
    def test_write(self):
        """Testing OvfSet.write"""
        self.ovfSetObject.archiveFormat = None
        self.assertRaises(ValueError,self.ovfSetObject.write, self.tmpDir, None)
        
        self.assertRaises(ValueError,self.ovfSetObject.write, self.tmpDir, "File")
        
#        self.ovfSetObject.archiveSavePath = None
#        self.assertRaises(ValueError,self.ovfSetObject.write, None, "Tar")

    def test_writeAsTar(self):
        """Testing OvfSet.writeAsTar"""
        name = self.ovfSetObject.name
        output=self.tmpDir + name + ".ova"
        self.ovfSetObject.writeAsTar(output)
        self.assertTrue((tarfile.is_tarfile(output)),
            "according to tarfile.is_tarfile, writeAsTar output is not tar")
        tar = tarfile.open(output,"r")
        tarmembers = []
        for tarinfo in tar:
            self.assertFalse((tarinfo.name in tarmembers),
                             "name " + tarinfo.name + " occurs twice in tarfile")
            tarmembers.append(tarinfo.name)
        tar.close()

        self.assertEqual(tarmembers[0], name + ".ovf",
            "first entry in tar must be <name>.ovf")

        objmembers = [ tarmembers[0] ]
        for ref in self.ovfSetObject.getOvfFile().getReferencedFiles():
            objmembers.append(ref.href)

        # if a .mf is present it must be second file
        self.assertTrue((name + ".mf" not in objmembers or 
                         tarmembers[1] == name + ".mf"),
                        "file named <name>.mf present but not second file")

        # if a .cert is present it must be third
        self.assertTrue((name + ".cert" not in objmembers or 
                         tarmembers[2] == name + ".cert"),
                        "file named <name>.mf present but not second file")

        # other entries in the tar might not be in order of getReferencedFiles
        # but the list should contain the same items (without extras)
        # a reason for that would be if 2 references had same href (with 
        # different file_ids) the tar should only contain one copy

        objuniq = []
        for x in objmembers:
            if x not in objuniq: objuniq.append(x)

        tarmembers.sort()
        objuniq.sort()
        self.assertTrue(tarmembers.sort() == objuniq.sort(),
                        "files in tar (" + str(tarmembers) +
                        ") != files referenced (" + str(objuniq) + ")")
        
    def test_writeAsDir(self):
        """Testing OvfSet.writeAsDir"""
        # Write the modified OvfSet to disk as a dir
        self.ovfSetObject.writeAsDir(self.tmpDir)
        file = open(self.tmpDir + self.ovfSetObject.name + ".ovf","r")
        doc = parse(file)
        doc.normalize()
        file.close()
        self.assertTrue(testUtils.compare_dom(self.ovfSetObject.ovfFile.document,doc,True),
            'Written Ovf DOM does not match the DOM in memory')
        for each in self.ovfSetObject.ovfFile.files:
            self.assertTrue(os.path.isfile(self.tmpDir + each.href), \
                'Files referenced in the Ovf were not found in write path')
    
        # Test if IOError raised when no save path was provided
        self.ovfSetObject.ovfFile.path = ''
        self.assertRaises(IOError, self.ovfSetObject.writeAsDir, None)
        
    #TODO: Unfinished
    def test_initializeFromPath(self):
        """Testing OvfSet.initializeFromPath"""
        self.assertTrue

#    def testDel(self):
#        """Testing OvfSet.__del__"""
#        tempPath = self.ovfSetObject.archivePath + '/tmp/'
#        self.ovfSetObject.__tmpdir__ = tempPath
#        os.mkdir(tempPath)
#        #self.ovfSetObject.__del__()
#        self.assertEqual(os.path.isdir(tempPath), True)
#        os.rmdir(tempPath)

if __name__ == "__main__":
    simple = unittest.TestLoader().loadTestsFromTestCase(SimpleTestCase)
    write = unittest.TestLoader().loadTestsFromTestCase(WriteTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(unittest.TestSuite((simple, write)))

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
import os, unittest
from xml.dom.minidom import parse

from ovf import OvfFile
from ovf import OvfReferencedFile
import testUtils

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files/")

def isSamePath(a,b):
    return ( os.path.abspath(a) == os.path.abspath(b) )

class OvfFileTestCase(unittest.TestCase):

    path = TEST_FILES_DIR
    fileName = path + 'ourOVF.ovf'
    ovfSum = '3e391a32e58f1ebf9990858b87f34af3e01c40b8'

    document = parse(fileName)

    ovfFile = None
    ovfFile2 = None
    ovfFile3 = None

    def setUp(self):
        self.ovfFile = OvfFile.OvfFile(self.fileName)
        self.ovfFile2 = OvfFile.OvfFile()
        self.ovfFile3 = OvfFile.OvfFile()

    def test_NewObj(self):
        assert isSamePath(self.ovfFile.path,self.fileName),"object not created"
        assert self.ovfFile.files != [] , "file list not created"
        #do we really want to parse the whole ovf when we create this object???

    def test_addReferencedFile(self):

        assert self.ovfFile2.files == [] , "files list not empty"
        name = self.path+'/'+self.fileName
        newFile = OvfReferencedFile.OvfReferencedFile(name,self.fileName,self.ovfSum)
        self.ovfFile2.addReferencedFile(newFile)
        assert self.ovfFile2.files != [], "files list not created"

    def test_getReferencedFiles(self):

         files = self.ovfFile.getReferencedFiles()
         assert files != [], "files not created"
         assert self.ovfFile.files != [], "files are empty"

         files2 = self.ovfFile2.getReferencedFiles()
         #it should only contain 1 OvfRef.. file in that list and that is the .ovf file
         #print files2[0].href
         assert len(files2) <= 1, "files were created, they were not suppsed to be created"
         assert len(self.ovfFile2.files) <= 1, "files are not empty, they should be empty"

    def test_setFilesFromOvfFileReferences(self):
        self.ovfFile.setFilesFromOvfFileReferences()
        assert len(self.ovfFile.files) >= 1, "The files list was not created"

        #if no ovf is passed in when the object was created and you try to sel the list throw an exception
        self.assertRaises(Exception,self.ovfFile2.setFilesFromOvfFileReferences)
    def test_writeFile(self):
        self.assertRaises(AttributeError,self.ovfFile2.writeFile,'our.fda')#not a valid xml
        self.assertRaises(TypeError,self.ovfFile2.writeFile)#no filename initialized

        fullname = self.path+"/"+"tester.ovf"
        fileObj = open(fullname, "w")
        self.ovfFile.writeFile(fileObj)
        fileObj.close()
        myDoc = parse(fullname)

        self.assertTrue(testUtils.compare_dom(myDoc,self.ovfFile.document,True),
            "Documents are not the same")

        os.remove(fullname)

    def test_syncReferencedFilesToDom(self):
        fileID = []
        fileHref = []

        name = "testHref.cert"
        newFile = OvfReferencedFile.OvfReferencedFile(name,name,None,None,None,
                                                      None,'TEST',None)
        self.ovfFile.addReferencedFile(newFile)

        self.ovfFile.syncReferencedFilesToDom()

        for node in self.ovfFile.document.getElementsByTagName('File'):#this will get the element with the tag: File
            fileID.append(node.attributes["ovf:id"].value)
            fileHref.append(node.attributes["ovf:href"].value)

        assert name in fileHref, "File not added to the ovf"
        assert 'TEST' in fileID, "FileId not added to the ovf"

    def test_createEnevelope(self):
        """test_createEnevelope: Testing OvfFile.createEnvelope: """
        version = "1.0.0b"
        lang = "en-us"
        self.assertEquals(self.ovfFile2.envelope,None)
        self.ovfFile2.createEnvelope(version,lang)
        self.assertNotEqual(self.ovfFile2.envelope, None)

        self.assertEqual(self.ovfFile2.envelope.attributes['ovf:version'].value,version)
        self.assertEqual(self.ovfFile2.envelope.attributes['xml:lang'].value,lang)

    def test_createRefSection(self):
        """test_createRefSection: Testing OvfFile.createRefSection:"""
        self.assertRaises(NotImplementedError,self.ovfFile3.createRefSection)#document is not created

        self.ovfFile3.files = None #for some reasson when ovfFile3 is created an obejct is added to ovfFile3.files
        self.assertRaises(NotImplementedError,self.ovfFile3.createRefSection)
        self.ovfFile3.createEnvelope()
        self.ovfFile3.files = self.ovfFile2.files
        self.ovfFile3.createRefSection()
        self.assertNotEquals(self.ovfFile3.document.getElementsByTagName('References'),None)
        #all the createRefSection does is what is tested. The actual adding of the files is done in syncReferencedFilesToDom
        #that function is tested above.

    def test_createDiskSection(self):
        """test_createDiskSection: Testing OvfFile.createDiskSection() this will create a disk section in the ovf:"""
        #******Disk Section data****************
        diskDictList = []
        dict ={}
        dict['diskId'] = 'disk1'
        dict['fileRef'] = 'file1'
        dict['capacity'] = '12884901888'
        dict['populatedSize'] = '11884901880'
        dict['format'] = 'http://www.vmware.com/specifications/vmdk.html#sparse'
        dict['capacityAllocUnits'] = "GigaBytes"
        dict['parentRef'] = None
        diskDictList.append(dict)


        #******************************************
        self.ovfFile3.createEnvelope()
        self.ovfFile3.createDiskSection(diskDictList, "Some Comment", '1', '1', False)
        self.assertNotEquals(self.ovfFile3.document.getElementsByTagName('DiskSection'),None)
        for node in self.ovfFile3.document.getElementsByTagName('DiskSection'):
            self.assertTrue(node.nodeName == "DiskSection")
            self.assertTrue(node.getAttribute("ovf:id") == "1")
            self.assertTrue(node.getAttribute("ovf:id") == "1")
            self.assertTrue(node.getAttribute("ovf:required") == "false")

        for node in self.ovfFile3.document.getElementsByTagName('Disk'):
            self.assertTrue(node.getAttribute("ovf:diskId") == 'disk1')
            self.assertTrue(node.getAttribute("ovf:fileRef") == 'file1')
            self.assertTrue(node.getAttribute("ovf:capacity") == '12884901888')
            self.assertTrue(node.getAttribute("ovf:populatedSize") == '11884901880')
            self.assertTrue(node.getAttribute("ovf:format") == 'http://www.vmware.com/specifications/vmdk.html#sparse')
            self.assertTrue(node.getAttribute("ovf:capacityAllocationUnits") == "GigaBytes")
            self.assertTrue(node.getAttribute("ovf:parentRef") =='')

    def test_createNetworkSection(self):
        """Testing OvfFile.createNetworkSection:"""

        networkList = []
        dict ={}
        dict['networkID'] = "Red"
        dict['networkName'] = 'red Network'
        dict['description'] = "Here is where the RED network would be described in detail"
        networkList.append(dict)

        self.ovfFile3.createEnvelope()
        self.ovfFile3.createNetworkSection(networkList, "Some network comment", "2")
        net = self.ovfFile3.document.getElementsByTagName('NetworkSection')
        self.assertTrue(net[0].nodeName == "NetworkSection")
        self.assertTrue(net[0].getElementsByTagName('Network')[0].getAttribute('ovf:id') == "Red")
        self.assertTrue(net[0].getElementsByTagName('Network')[0].getAttribute("ovf:name") == 'red Network')

    def test_createDeploymentOptions(self):
        """createDeploymentOptions: Testing createDeploymentOptions:"""
        self.ovfFile3.createEnvelope()
        dpl = self.ovfFile3.createDeploymentOptions("some comments")

        self.assertTrue(dpl.nodeName == "DeploymentOptionSection")

        self.assertRaises(TypeError,self.ovfFile3.createDeploymentOptions,"comment")
        self.assertEquals(dpl.nodeName, "DeploymentOptionSection")

    def test_defineDeploymentOptions(self):
        self.ovfFile3.createEnvelope()
        dpl = self.ovfFile3.createDeploymentOptions("some comments")
        self.assertRaises(TypeError, self.ovfFile3.defineDeploymentOptions,self.ovfFile3.envelope, "1", "some", "description")
        self.ovfFile3.defineDeploymentOptions(dpl, "1", "some", "description","3","4",True)

        for node in self.ovfFile3.document.getElementsByTagName('Configuration'):
            self.assertTrue(node.getAttribute("ovf:id") == '1')

        self.assertRaises(NameError, self.ovfFile3.defineDeploymentOptions,dpl, "1", "some", "description","3","4",'True')

    def test_createVirtualSystemCollection(self):

        self.ovfFile3.createEnvelope()
        self.ovfFile3.createVirtualSystemCollection("1", "No Info", "3")


        for node in self.ovfFile3.document.getElementsByTagName('VirtualSystemCollection'):
            self.assertTrue(node.nodeName == "VirtualSystemCollection")
            self.assertTrue(node.getAttribute("ovf:id") == '1')

    def test_createResourceAllocation(self):
        self.ovfFile3.createEnvelope()
        vsc = self.ovfFile3.createVirtualSystemCollection("1", "No Info", "3")
        self.assertRaises(TypeError, self.ovfFile3.createResourceAllocation,self.ovfFile3.envelope, "some", "1", "adv,dac", "min")
        rsc = self.ovfFile3.createResourceAllocation(vsc, "some", "1", "adv,dac", "min")

        for node in self.ovfFile3.document.getElementsByTagName('ResourceAllocationSection'):
            self.assertTrue(node.nodeName == "ResourceAllocationSection")
            self.assertTrue(node.getAttribute("ovf:configuration") == "adv,dac")
            self.assertTrue(node.getAttribute("ovf:bound") == "min")
            self.assertRaises(TypeError,self.ovfFile3.createResourceAllocation,vsc, "some", "1", "adv,dac", "sa")


        self.assertEquals(rsc.nodeName, "ResourceAllocationSection")

    def test_defineResourceAllocation(self):
        self.ovfFile3.createEnvelope()
        vsc = self.ovfFile3.createVirtualSystemCollection("1", "No Info", "3")
        rsc = self.ovfFile3.createResourceAllocation(vsc, "some", "1", "adv,dac", "min")

        address = "EF1453"
        addressOnParent = "somwhere"
        allocUnits = "MegaBytes"
        automaticAllocation = "true"
        autoDealloc = "false"
        caption = "some caption"
        connection = "Red"
        consVis = "consvis"
        description = "description"
        elementName = 'elementName'
        hostResource = "true"
        instanceId = "14"
        limit = "3"
        mapBehavior= "map beha"
        otherResourceType = "machine"
        parent = "15"
        poolID = "37"
        reservation = "1"
        resourceSubtype = "virtual sys"
        resourceType = "true"
        virtualQuantity = "8"
        weight = "37"

        refDefDict = {
             "Address": address,"AddressOnParent":addressOnParent,
             "AllocationUnits":allocUnits,
             "AutomaticAllocation":automaticAllocation ,
             "AutomaticDeallocation":autoDealloc,"Caption":caption,
             "Connection": connection,"ConsumerVisibility":consVis,
             "Description" : description,"ElementName":elementName,
             "HostResource":hostResource ,
             "InstanceID": instanceId ,   "Limit":limit ,
             "MappingBehavior":mapBehavior, "OtherResourceType":otherResourceType,
             "Parent":parent ,
              "PoolID":poolID, "Reservation":reservation,"ResourceSubType":resourceSubtype,
             "ResourceType":resourceType,"VirtualQuantity":virtualQuantity,"Weight":weight
         }

        vs = self.ovfFile3.createVirtualSystemSection("VS1", "some info", self.ovfFile3.envelope, "id3")
        vhwNode = self.ovfFile3.createVirtualHardwareSection(vs, 'info', 'infoID', 'transport')
        self.ovfFile3.defineResourceAllocation(vhwNode,refDefDict)
#                                     options.config, options.bound,
#                                     options.required)

        list = [
             ("Address", address),("AddressOnParent", addressOnParent),
             ("AllocationUnits",allocUnits),("AutomaticAllocation",automaticAllocation) ,
             ("AutomaticDeallocation",autoDealloc),("Caption",caption),
             ("Connection", connection),("ConsumerVisibility",consVis),
             ("Description" , description),("HostResource",hostResource) ,
             ("InstanceId", instanceId ),  ( "Limit",limit) ,
             ("MappingBehavior",mapBehavior),  ( "OtherResourceType",otherResourceType),
             ("Parent",parent) ,
             ( "PoolID",poolID), ("Reservation",reservation),("ResourceSubType",resourceSubtype),
             ("ResourceType",resourceType),("VirtualQuantity",virtualQuantity),("Weight",weight)
         ]
        for node in self.ovfFile3.document.getElementsByTagName('Item'):
            self.assertEquals(node.nodeName,'Item')

        for ent in list:
            if ent[0] != None:
                 if ent[1] != None:
                     nodes = self.ovfFile3.document.getElementsByTagName("rasd:" + ent[0])
                     for node in nodes:
                         self.assertEquals(node.tagName, "rasd:" + ent[0])


    def test_createProductSection(self):
        self.ovfFile3.createEnvelope()
        info = 'info'
        product = 'product'
        version = 'version'
        infoID = '1'
        classDesc = 'classDesc'
        instance = '3'
        vendor = 'vendor'
        fullVersion = 'fullVersion'
        prodURL = 'prodURL'
        vendorURL = 'vendorURL'
        appURL = 'appURL'
        vsc = self.ovfFile3.createVirtualSystemCollection("1", "No Info", "3")
        prodList = [("Product", product),
                ("Vendor",vendor),
                ("Version", version),
                ("FullVersion", fullVersion),
                ("ProductUrl", prodURL),
                ("VendorUrl", vendorURL),
                ("AppUrl", appURL)]
        prod = self.ovfFile3.createProductSection(vsc,"This is the first product of the VM",
                                                 prodList,"com.xen.tools", '1')

        prodLlist = [("Product",product),("Vendor",vendor),("Version",version),
                ("FullVersion",fullVersion),("ProductUrl",prodURL),
                ("VendorUrl",vendorURL),("AppUrl",appURL),
                ]
        for node in self.ovfFile3.document.getElementsByTagName('ProductSection'):
            self.assertTrue(node.nodeName == "ProductSection")

        for ent in prodList:
            if ent[0] != None:
                 if ent[1] != None:
                     nodes = self.ovfFile3.document.getElementsByTagName(ent[0])
                     for node in nodes:
                         self.assertEquals(node.tagName, ent[0])


    def test_createIconType(self):
        self.ovfFile3.createEnvelope()
        vsc = self.ovfFile3.createVirtualSystemCollection("1", "No Info", "3")
        prodDict = [("Product", "Red Hat Linux"),
                ("Vendor","RedHat"),
                ("Version", "2.2.5"),
                ("FullVersion", "2.2.5-alpah2"),
                ("ProductUrl", "http://2.2.5-alpah2.redhat.com"),
                ("VendorUrl", "http://redhat.com"),
                ("AppUrl", "http://someApp.com")]
        prod = self.ovfFile3.createProductSection(vsc,"This is the first product of the VM",
                                                 prodDict,"com.xen.tools", '1')

        self.assertRaises(TypeError,self.ovfFile3.createIconType,self.ovfFile3.envelope, 'fileRef', '4', '3', 'mimeType')

        self.ovfFile3.createIconType(prod, 'fileRef', 'height', 'width', 'mimeType')

        for node in self.ovfFile3.document.getElementsByTagName('Icon'):
            self.assertEquals(node.nodeName,'Icon')
            self.assertTrue(node.hasAttribute("ovf:height"))
            self.assertTrue(node.hasAttribute("ovf:width"))
            self.assertTrue(node.hasAttribute("ovf:mimeType"))
            self.assertTrue(node.hasAttribute("ovf:fileRef"))

            self.assertEquals(node.getAttribute("ovf:height"), 'height')
            self.assertEquals(node.getAttribute("ovf:width"), 'width')
            self.assertEquals(node.getAttribute("ovf:mimeType"), 'mimeType')
            self.assertEquals(node.getAttribute("ovf:fileRef"), 'fileRef')

    def test_createCategory(self):
        self.ovfFile3.createEnvelope()
        self.ovfFile3.createCategory(self.ovfFile3.envelope, "category")

        nodes = self.ovfFile3.document.getElementsByTagName('Category')
        for node in nodes:
            self.assertEquals(node.tagName, 'Category')

    def test_createPropertyProductSection(self):
        self.ovfFile3.createEnvelope()
        self.assertRaises(TypeError,self.ovfFile3.createPropertyProductSection,self.ovfFile3.envelope, 'key')
        vsc = self.ovfFile3.createVirtualSystemCollection("1", "No Info", "3")
        prodDict = [("Product", "Red Hat Linux"),
                ("Vendor","RedHat"),
                ("Version", "2.2.5"),
                ("FullVersion", "2.2.5-alpah2"),
                ("ProductUrl", "http://2.2.5-alpah2.redhat.com"),
                ("VendorUrl", "http://redhat.com"),
                ("AppUrl", "http://someApp.com")]
        prod = self.ovfFile3.createProductSection(vsc,"This is the first product of the VM",
                                                 prodDict,"com.xen.tools", '1')
        self.assertRaises(TypeError, self.ovfFile3.createPropertyProductSection,prod, "key", 'type', 'value', 'usrConfig', 'required')
        self.assertRaises(TypeError, self.ovfFile3.createPropertyProductSection,prod, "key", 'type', 'value', False, 'required')

        prop = self.ovfFile3.createPropertyProductSection(prod, 'key', 'type', 'value', True, False)
        nodes = self.ovfFile3.document.getElementsByTagName('Property')
        for node in nodes:
            self.assertEquals(node.tagName, 'Property')
            self.assertTrue(node.hasAttribute("ovf:key"))
            self.assertTrue(node.hasAttribute("ovf:type"))
            self.assertTrue(node.hasAttribute("ovf:value"))
            self.assertTrue(node.hasAttribute("ovf:userConfigurable"))
            self.assertTrue(node.hasAttribute("ovf:required"))

            self.assertEquals(node.getAttribute("ovf:key"), 'key')
            self.assertEquals(node.getAttribute("ovf:type"), 'type')
            self.assertEquals(node.getAttribute("ovf:value"), 'value')
            self.assertEquals(node.getAttribute("ovf:userConfigurable"), 'true')
            self.assertEquals(node.getAttribute("ovf:required"), 'false')

        self.assertEquals(prop.nodeName, "Property")

    def test_createEULASection(self):
        self.ovfFile3.createEnvelope()
        vsc= self.ovfFile3.createVirtualSystemCollection("1", "No Info", "3")
        eula = self.ovfFile3.createEULASection("some info",vsc,"3")

        for node in self.ovfFile3.document.getElementsByTagName('EulaSection'):
            self.assertEquals(node.nodeName,"EulaSection")

        self.assertEquals(eula.nodeName, "EulaSection")

    def test_defineLicenseSection(self):
        self.ovfFile3.createEnvelope()

        self.assertRaises(TypeError,self.ovfFile3.defineLicenseSection,self.ovfFile3.envelope, "license", 'msgID')
        vsc = self.ovfFile3.createVirtualSystemCollection("1", "No Info", "3")
        eula = self.ovfFile3.createEULASection("some info",vsc, "3")
        self.ovfFile3.defineLicenseSection(eula, "some", "2")

        nodes = self.ovfFile3.document.getElementsByTagName('License')
        for node in nodes:
            self.assertEquals(node.tagName, 'License')
            self.assertEquals(node.getAttribute("ovf:msgid"),'2')

    def test_createStartupSection(self):
        self.ovfFile3.createEnvelope()
        self.assertRaises(TypeError,self.ovfFile3.createStartupSection,self.ovfFile3.envelope, "0", "3")

        vsc = self.ovfFile3.createVirtualSystemCollection("1", "No Info", "3")
        start= self.ovfFile3.createStartupSection(vsc, "some info", "1")

        for node in self.ovfFile3.document.getElementsByTagName('StartupSection'):
            self.assertEquals(node.nodeName,"StartupSection")

        self.assertEquals(start.nodeName, "StartupSection")

    def test_defineStartUpSection(self):
        self.ovfFile3.createEnvelope()
        self.assertRaises(TypeError,self.ovfFile3.defineStartUpSection,self.ovfFile3.envelope, '2', 'order')

        vsc = self.ovfFile3.createVirtualSystemCollection("1", "No Info", "3")

        start= self.ovfFile3.createStartupSection(vsc, "some info", "1")

        self.assertRaises(TypeError,self.ovfFile3.defineStartUpSection,start, 'id', 'order', 'startDelay', 'False')
        self.assertRaises(TypeError,self.ovfFile3.defineStartUpSection,start, 'id', 'order', 'startDelay', False, 'power')
        self.assertRaises(TypeError,self.ovfFile3.defineStartUpSection,start,'id', 'order', 'startDelay', False, 'poweOn', 'stopDelay', 'on')


        self.ovfFile3.defineStartUpSection(start, 'id', 'order', 'startDelay', False, 'powerOn', 'stopDelay', 'powerOff')

        nodes = self.ovfFile3.document.getElementsByTagName('Item')
        for node in nodes:
            self.assertEquals(node.tagName, 'Item')
            self.assertTrue(node.hasAttribute("ovf:id"))
            self.assertTrue(node.hasAttribute("ovf:order"))
            self.assertTrue(node.hasAttribute("ovf:startDelay"))
            self.assertTrue(node.hasAttribute("ovf:waitingForGuest"))
            self.assertTrue(node.hasAttribute("ovf:startAction"))
            self.assertTrue(node.hasAttribute("ovf:stopDelay"))
            self.assertTrue(node.hasAttribute("ovf:stopAction"))

            self.assertEquals(node.getAttribute("ovf:id"), 'id')
            self.assertEquals(node.getAttribute("ovf:order"), 'order')
            self.assertEquals(node.getAttribute("ovf:startDelay"), 'startDelay')
            self.assertEquals(node.getAttribute("ovf:waitingForGuest"), 'false')
            self.assertEquals(node.getAttribute("ovf:startAction"), 'powerOn')
            self.assertEquals(node.getAttribute("ovf:stopDelay"), 'stopDelay')
            self.assertEquals(node.getAttribute("ovf:stopAction"), 'powerOff')

    def test_createVirtualSystemSection(self):
        self.ovfFile3.createEnvelope()
        vsc = self.ovfFile3.createVirtualSystemCollection("2", "No Info", "4")
        eula = self.ovfFile3.createEULASection("some info", vsc,"3")
        self.assertRaises(TypeError, self.ovfFile3.createVirtualSystemSection,'id', 'info', eula, 'infoID')
        #Make the actual section using ovfFile3
        vs = self.ovfFile3.createVirtualSystemSection("VS1", "some info", self.ovfFile3.envelope, "id3")

        for node in self.ovfFile3.document.getElementsByTagName('VirtualSystem'):
            self.assertTrue(node.nodeName == "VirtualSystem")
            self.assertTrue(node.getAttribute("ovf:id") == 'VS1')

        self.assertTrue(vs.nodeName == "VirtualSystem")

    def test_createOSsection(self):
        self.ovfFile3.createEnvelope()

        self.assertRaises(TypeError,self.ovfFile3.createOSsection,self.ovfFile3.envelope, 'id', 'info', 'infoID')

        vs = self.ovfFile3.createVirtualSystemSection("VS1", "some info", self.ovfFile3.envelope, "id3")
        os = self.ovfFile3.createOSsection(vs, 'id', 'info', 'infoID','description','descID')
        childPresent = False
        for node in self.ovfFile3.document.getElementsByTagName('OperatingSystemSection'):
            self.assertTrue(node.nodeName) == "OperatingSystemSection"
            self.assertTrue(node.getAttribute("ovf:id") == "id")
            for child in node.childNodes:
                if child.nodeName == "Description":
                    childPresent = True
            self.assertTrue(childPresent)

        self.assertTrue(os.nodeName == "OperatingSystemSection")



    def test_createInstallSection(self):
        self.ovfFile3.createEnvelope()
        self.assertRaises(TypeError,self.ovfFile3.createInstallSection,self.ovfFile3.envelope, "info", "infoID")
        vs = self.ovfFile3.createVirtualSystemSection("VS1", "some info", self.ovfFile3.envelope, "id3")
        self.assertRaises(TypeError,self.ovfFile3.createInstallSection,vs, 'info', 'infoID', 'initBoot', 'bootStopdelay')
        install = self.ovfFile3.createInstallSection(vs, "some info", "3", True, 'bootStopdelay')

        for node in self.ovfFile3.document.getElementsByTagName('InstallSection'):
            self.assertTrue(node.nodeName == "InstallSection")
            self.assertTrue(node.getAttribute("ovf:initialBoot") == "true")
            self.assertTrue(node.getAttribute("ovf:initialBootStopDelay") == "bootStopdelay")

        self.assertTrue(install.nodeName == "InstallSection")

    def test_createVirtualHardwareSection(self):
        self.ovfFile3.createEnvelope()
        self.assertRaises(TypeError, self.ovfFile3.createVirtualHardwareSection,self.ovfFile3.envelope, 'info', 'infoID', 'transport')

        vs = self.ovfFile3.createVirtualSystemSection("VS1", "some info", self.ovfFile3.envelope, "id3")
        hw = self.ovfFile3.createVirtualHardwareSection(vs,'someID', 'info', 'infoID', 'transport')

        node = self.ovfFile3.document.getElementsByTagName('VirtualHardwareSection')

        self.assertTrue(hw.getAttribute("ovf:transport") == "transport")

        self.assertTrue(hw.nodeName == "VirtualHardwareSection")

    def test_createSystem(self):
        self.ovfFile3.createEnvelope()

        self.assertRaises(TypeError, self.ovfFile3.createSystem, self.ovfFile3.envelope)
        vs = self.ovfFile3.createVirtualSystemSection("VS1", "some info", self.ovfFile3.envelope, "id3")
        hw = self.ovfFile3.createVirtualHardwareSection(vs, 'info', 'infoID', 'transport')
        sys = self.ovfFile3.createSystem(hw)

        self.assertTrue(sys.nodeName == "System")

    def test_defineSystem(self):
        self.ovfFile3.createEnvelope()

        name = 'elementName'
        instanceId = 'instanceId'

        systemDict = dict(Caption="test",
                          Description="test protocol",
                          VirtualSystemIdentifier="test id",
                          VirtualSystemType="test type")

        self.assertRaises(TypeError, self.ovfFile3.defineSystem,
                          self.ovfFile3.envelope, name, instanceId)

        vs = self.ovfFile3.createVirtualSystemSection("VS1", "some info", self.ovfFile3.envelope, "id3")
        hw = self.ovfFile3.createVirtualHardwareSection(vs, 'info', 'infoID', 'transport')
        sys = self.ovfFile3.createSystem(hw)

        self.ovfFile3.defineSystem(sys, name, instanceId, systemDict)

        for node in self.ovfFile3.document.getElementsByTagName('System'):
            for child in node.childNodes:
                if child.nodeType == 1: # Check if ELEMENT_NODE
                    childName = child.nodeName.rsplit(':', 1).pop() # strip 'vssd:'
                    if child.firstChild.data == systemDict[childName]:
                        self.assertTrue(True)
                    else:
                        self.assertTrue(False)

    def test_createDescriptionChild(self):
        self.ovfFile3.createEnvelope()
        self.ovfFile3.createDescriptionChild(self.ovfFile3.envelope, 'description', 'msgID')

        for node in self.ovfFile3.document.getElementsByTagName('Description'):
            self.assertTrue(node.getAttribute("ovf:msgid") == "msgID")
            self.assertEquals(node.firstChild.data, 'description')

    def test_createLabelChild(self):
        self.ovfFile3.createEnvelope()
        self.ovfFile3.createLabelChild(self.ovfFile3.envelope, 'label', 'msgID')

        for node in self.ovfFile3.document.getElementsByTagName('Label'):
            self.assertTrue(node.getAttribute("ovf:msgid") == "msgID")
            self.assertEquals(node.firstChild.data, 'label')

    def test_createInfoChild(self):
        self.ovfFile3.createEnvelope()
        self.ovfFile3.createInfoChild(self.ovfFile3.envelope, 'infoComments', 'msgID')

        for node in self.ovfFile3.document.getElementsByTagName('Info'):
            self.assertTrue(node.getAttribute("ovf:msgid") == "msgID")
            self.assertEquals(node.firstChild.data, 'infoComments')

    def test_createComment(self):
        self.ovfFile3.createEnvelope()
        self.ovfFile3.createComment('comment')
        self.assertEquals(self.ovfFile3.envelope.firstChild.data, 'comment')

    def test_createAnnotationSection(self):
        self.ovfFile3.createEnvelope()
        vsc = self.ovfFile3.createVirtualSystemCollection("id", "info", "infoID", self.ovfFile3.envelope)
        self.ovfFile3.createAnnotationSection('annotation', 'info', self.ovfFile3.envelope, 'msgID')

        for node in self.ovfFile3.document.getElementsByTagName('AnnotationSection'):
            self.assertTrue(node.nodeName == "AnnotationSection")
            self.assertEquals(node.firstChild.nodeName, "Info")

        for node in self.ovfFile3.document.getElementsByTagName('Annotation'):
            self.assertTrue(node.getAttribute("ovf:msgid") == "msgID")

        eula = self.ovfFile3.createEULASection("some info", vsc,"3" )
        self.assertRaises(TypeError,self.ovfFile3.createAnnotationSection,'annotation', 'info', eula, 'msgID')

    def test_createCaptionChild(self):
        self.ovfFile3.createEnvelope()
        self.ovfFile3.createCaptionChild(self.ovfFile3.envelope, 'caption')

        for node in self.ovfFile3.document.getElementsByTagName('Caption'):
            self.assertEquals(node.firstChild.data, 'caption')

    def test_getReferencedFilesFromOvf(self):
        files2 = []
        files = OvfFile.getReferencedFilesFromOvf(self.fileName)

        #file1 "Ubuntu1.vmdk"
        filePath = self.path+"/"+"Ubuntu1.vmdk"
        fileHref = "Ubuntu1.vmdk"
        checksum = None
        checksumStamp = None
        fileSize = "4882023564"
        fileCompression =None
        fileID = "file1"
        fileChunkSize = "2147483648"
        files2.append(OvfReferencedFile.OvfReferencedFile(filePath,fileHref,checksum,checksumStamp,fileSize,fileCompression, fileID,fileChunkSize))

        #file2 Ubuntu-0.vmdk
        filePath = self.path+"/"+"Ubuntu-0.vmdk"
        fileHref = "Ubuntu-0.vmdk"
        checksum = None
        checksumStamp = None
        fileSize = "280114671"
        fileCompression ="gzip"
        fileID = "file2"
        fileChunkSize = None
        files2.append(OvfReferencedFile.OvfReferencedFile(filePath,fileHref,checksum,checksumStamp,fileSize,fileCompression, fileID,fileChunkSize))

        #file3 ourOVF.mf
        filePath = self.path+"/"+"ourOVF.mf"
        fileHref = "ourOVF.mf"
        checksum = None
        checksumStamp = None
        fileSize = "1"
        fileCompression =None
        fileID = "file3"
        fileChunkSize = None
        files2.append(OvfReferencedFile.OvfReferencedFile(filePath,fileHref,checksum,checksumStamp,fileSize,fileCompression, fileID,fileChunkSize))

        #file4 ourOVF.cert
        filePath = self.path+"/"+"ourOVF.cert"
        fileHref = "ourOVF.cert"
        checksum = None
        checksumStamp = None
        fileSize = "1"
        fileCompression =None
        fileID = "file4"
        fileChunkSize = None
        files2.append(OvfReferencedFile.OvfReferencedFile(filePath,fileHref,checksum,checksumStamp,fileSize,fileCompression, fileID,fileChunkSize))


        for curr in files:
            for innerCurr in files2:
                if curr.href == innerCurr.href:
                    assert isSamePath(curr.path,innerCurr.path), "Path does not match reference"
                    assert curr.checksum == innerCurr.checksum, "Checksum does not match reference"
                    assert curr.checksumStamp == innerCurr.checksumStamp, "Checksum time stamp does not match reference"
                    assert curr.size == innerCurr.size, "Size does not match reference"
                    assert curr.compression == innerCurr.compression, "Compression type does not match reference"
                    assert curr.file_id == innerCurr.file_id, "File ID does not match reference"
                    assert curr.chunksize == innerCurr.chunksize, "File chunk size does not match reference"


if __name__ == "__main__":
    test = unittest.TestLoader().loadTestsFromTestCase(OvfFileTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(unittest.TestSuite(test))

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
# Sharad Mishra (IBM) - initial implementation
##############################################################################
"""
pyUnit tests
"""

import os, unittest
from xml.dom.minidom import parse

from ovf.env import EnvironmentSection
from ovf.env import PlatformSection

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files/")
SCHEMA_FILES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..")
OVF_ENV_XSD = os.path.join(os.path.dirname(__file__), "..", "..",
                                           "schemas", "ovf-environment.xsd")

def isSamePath(a, b):
    """ test if two paths are same. """
    return ( os.path.abspath(a) == os.path.abspath(b) )

class OvfEnvironmentTestCase (unittest.TestCase):
    """ Test EnvironmentSection """

    path = TEST_FILES_DIR
    fileName = path + 'test-environment.xml'

    document = parse(fileName)
    ovfEnv = None
    ovfEnv2 = None
    envID = "22"
    newID = "1234"
    entID = "2"
    propdata = {'fillerkey':'fillervalue', 'propkey':'propvalue' }
    platdata = PlatformSection.PlatformSection({'Kind': "ESX Server",
                    'Vendor': "VMware, Inc.",
                    'Version': "3.0.1",
                    'Locale': "en_US"})

    def setUp(self):
        """ Setup the test."""
        self.ovfEnv = EnvironmentSection.EnvironmentSection(self.fileName)
        self.ovfEnv2 = EnvironmentSection.EnvironmentSection()

    def test_NewObj(self):
        """ Verify that a new EnvironmentSection object is created."""
        assert isSamePath(self.ovfEnv.path, self.fileName),"object not created"

    def testInitNoInputFile(self):
        """ Tests EnvironmentSection's __init__ method."""
        assert self.ovfEnv2.id == None, "object id should be None."
        assert self.ovfEnv2.document == None, "document should be None."
        assert self.ovfEnv2.environment == None, \
        "environment element should be None."
        assert self.ovfEnv2.oldChild == None, "oldChild should be None."
        assert self.ovfEnv2.path == None, "path should be None."

    def testCreateHeaderNew(self):
        """ Tests the createHeader method. No file is parsed."""
        self.assertEquals(self.ovfEnv2.environment, None)
        self.ovfEnv2.createHeader(None)
        self.assertNotEqual(self.ovfEnv2.environment, None)
        self.ovfEnv2.generateXML("out.xml")
        rc = EnvironmentSection.validateXML("out.xml", OVF_ENV_XSD)
        self.assertEquals(rc, 0)

    def testCreateHeaderExisting(self):
        """ Test createHeader when an existing xml file is passed as input."""
        self.ovfEnv.createHeader(self.envID)
        self.assertNotEqual(self.ovfEnv.environment, None)
        self.assertEqual\
        (self.ovfEnv.environment.attributes['ovfenv:id'].value, self.envID)
        self.ovfEnv.generateXML("out.xml")
        rc = EnvironmentSection.validateXML("out.xml", OVF_ENV_XSD)
        self.assertEquals(rc, 0)

    def testCreateSection(self):
        """ Test createSection with no existing ovf-env.xml file."""
        self.ovfEnv2.createHeader()
        # Verify that VauleError is raised when creating section without
        # an ID and SectionName.
        self.assertRaises(ValueError, self.ovfEnv2.createSection, None, None)
        # Verify that Entity is not created when no ID is given.
        self.assertRaises\
        (ValueError, self.ovfEnv2.createSection, None, "Entity")
        # Verify that a new Entity is created.
        self.ovfEnv2.createSection (self.envID, "Entity")
        self.assertNotEquals\
        (self.ovfEnv2.document.getElementsByTagName('Entity'), [])
        self.assertEquals\
        (self.ovfEnv2.document.getElementsByTagName('PropertySection'), [])
        # Verify that a Platform section is created.
        self.ovfEnv2.createSection(self.envID, "PlatformSection", self.platdata)
        element = self.ovfEnv2.document.getElementsByTagName("Version")
        self.assertEquals(element[0].firstChild.data, "3.0.1")
        self.ovfEnv2.generateXML("out.xml")
        rc = EnvironmentSection.validateXML("out.xml", OVF_ENV_XSD)
        self.assertEquals(rc, 0)

    def testCreateSectionWithID(self):
        """ Test createSection with an existing ovf-env.xml file. """
        # Verify that ValueError is raised when new Platform or Property
        # section is created without Entity.
        self.assertRaises\
        (ValueError, self.ovfEnv.createSection, self.newID, "PlatformSection")
        self.assertRaises\
        (ValueError, self.ovfEnv.createSection, self.newID, "PropertySection")
        # Verify that envID is updated for the header section.
        self.ovfEnv.createHeader(self.envID)
        self.assertEqual\
        (self.ovfEnv.environment.attributes['ovfenv:id'].value, self.envID)
        # Verify that a second PlatformSection is added to header.
        self.ovfEnv.createSection(self.envID, "PlatformSection", self.platdata)
        element = self.ovfEnv.document.getElementsByTagName("PlatformSection")
        self.assertEquals(element.length, 3)
        # Verify that another PropertySection is added to the xml.
        self.ovfEnv.createSection(self.envID, "PropertySection", self.propdata)
        element = self.ovfEnv.findElementById(self.envID)
        section = element.getElementsByTagName("PropertySection")
        self.assertEquals(section.length, 3)
        # Verify that a new PlatformSection is added to an
        # existing Entity.
        self.ovfEnv.createSection(self.entID, "PlatformSection", self.platdata)
        section = self.ovfEnv.findElementById(self.entID)
        element = section.getElementsByTagName("Version")
        self.assertEquals(element.length, 1)
        # Verify that a new PropertySection is added to an
        # existing Entity.
        self.ovfEnv.createSection(self.entID, "PropertySection", self.propdata)
        element = self.ovfEnv.findElementById(self.entID)
        section = element.getElementsByTagName("PropertySection")
        self.assertEquals(section.length, 2)
        # Verify that a new Platform/Property section cannot be
        # created with a new ID. An Entity by that ID should exist.
        self.assertRaises(ValueError, self.ovfEnv.createSection, self.newID,
                          "PlatformSection", self.platdata)
        self.assertRaises(ValueError, self.ovfEnv.createSection, self.newID,
                          "PropertySection", self.propdata)
        # Verify that a new platform section is created with given data.
        self.ovfEnv.createSection(self.newID, "Entity")
        self.ovfEnv.createSection(self.newID, "PlatformSection",
                                  PlatformSection.PlatformSection(
                                                   {'Kind': "ESX Server",
                                                   'Version': "3.0.1",
                                                   'Vendor': "VMware, Inc.",
                                                   'Locale': "en_US"}))
        section = self.ovfEnv.findElementById(self.newID)
        element = section.getElementsByTagName("Version")
        self.assertEquals(element[0].firstChild.data, "3.0.1")
        # Verify that a new property section is created with given data.
        self.ovfEnv.createSection(self.newID, "PropertySection", self.propdata)
        element = self.ovfEnv.findElementById(self.newID)
        section = element.getElementsByTagName("PropertySection")
        props = section[0].getElementsByTagName("Property")
        for i in range(0, props.length):
            if props[i].getAttribute('ovfenv:key') == "propkey":
                self.assertEquals(props[i].getAttribute('ovfenv:value'),
                                  "propvalue")
#        print self.ovfEnv.document.toprettyxml()
        self.ovfEnv.generateXML("out.xml")
        rc = EnvironmentSection.validateXML("out.xml", OVF_ENV_XSD)
        self.assertEquals(rc, 0)

    def testCreateNewSection(self):
        """ Test createNewSection when no id is passed to method. """
        self.ovfEnv2.createHeader()
        self.assertRaises(ValueError, self.ovfEnv2.createNewSection,
                          None, None)
        self.assertRaises(ValueError, self.ovfEnv2.createNewSection,
                          None, "Entity")
        self.ovfEnv2.createNewSection(None, "PropertySection")
        self.ovfEnv2.createNewSection(None, "PlatformSection")
        self.assertNotEquals \
        (self.ovfEnv2.document.getElementsByTagName('Environment'), [])
        self.assertNotEquals \
        (self.ovfEnv2.document.getElementsByTagName('PropertySection'), [])
        self.assertNotEquals \
        (self.ovfEnv2.document.getElementsByTagName('PlatformSection'), [])
        self.assertEquals \
        (self.ovfEnv2.document.getElementsByTagName('Entity'), [])
        self.ovfEnv2.generateXML("out.xml")
        rc = EnvironmentSection.validateXML("out.xml", OVF_ENV_XSD)
        self.assertEquals(rc, 0)

    def testCreateNewSectionWithID(self):
        """ Test createNewSection when an id is passed to method. """
        self.assertRaises(ValueError, self.ovfEnv.createNewSection,
                          self.newID, "PlatformSection")
        self.assertRaises(ValueError, self.ovfEnv.createNewSection,
                          self.newID, "PropertySection")

    def testInvalidSectionName(self):
        """ Test if invalid section name passed to createSection."""
        self.assertRaises(ValueError, self.ovfEnv.createSection, self.entID,
                          "sectionName", None)

    def testRemoveSection(self):
        """ Verify the functionality of removeSection. """
        self.ovfEnv.removeSection(self.entID, "PlatformSection")
        self.assertRaises(NameError, self.ovfEnv.removeSection, self.entID,
                          "PlatformSection")
        # Verify that a section from document header can be removed.
        self.ovfEnv.removeSection("12", "PlatformSection")
        self.assertRaises(NameError, self.ovfEnv.removeSection,
                          "12", "PlatformSection")
        self.ovfEnv.removeSection("12", "PropertySection")
        self.assertRaises(ValueError, self.ovfEnv.removeSection,
                          "12", "PropertySection")
        # Verify that Property section can be removed.
        self.ovfEnv = EnvironmentSection.EnvironmentSection(self.fileName)
        self.ovfEnv.removeSection(self.entID, "PropertySection")
        self.assertRaises(NameError, self.ovfEnv.removeSection, self.entID,
                          "PropertySection")
        # Verify that ValueError is raise when id does not exist.
        self.assertRaises(ValueError, self.ovfEnv.removeSection, self.newID,
                          "PropertySection")
        # Verify that all PropertySections are removed.
        self.ovfEnv = EnvironmentSection.EnvironmentSection(self.fileName)
        self.ovfEnv.createSection(self.entID, "PropertySection", self.propdata)
        self.ovfEnv.removeSection(self.entID, "PropertySection")
        self.assertRaises(NameError, self.ovfEnv.removeSection, self.entID,
                          "PropertySection")

        # Verify that all PlatformSections are removed.
        self.ovfEnv = EnvironmentSection.EnvironmentSection(self.fileName)
        self.ovfEnv.createSection(self.entID, "PlatformSection", self.propdata)
        self.ovfEnv.removeSection(self.entID, "PlatformSection")
        self.assertRaises(NameError, self.ovfEnv.removeSection, self.entID,
                          "PlatformSection")

        self.ovfEnv.generateXML("out.xml")
        rc = EnvironmentSection.validateXML("out.xml", OVF_ENV_XSD)
        self.assertEquals(rc, 0)

    def testRemoveProperties(self):
        """ Verify the functionality of removeProperties. """

        properties = {'UserName':'fillervalue',
                      'IP':'propvalue', 'Passord':'my+pass' }
        props = ["UserName"]
        props2 = ["UserName", "IP"]
        propsAll = ["UserName", "IP", "Passord"]
        vProps = ["UserName"]
        vProps2 = ["UserName", "IP"]
        vPropsAll = ["UserName", "IP", "Passord"]

        #: Verify that a ValueError is raised when removing non-existent prop.
        self.ovfEnv.createSection("12", "PropertySection", properties)
        self.assertRaises(ValueError, self.ovfEnv.removeProperties,
                          "12", "noentry")

        #: Verify that a property can be removed from root.
        self.ovfEnv.removeProperties("12", props2)
        self.assertRaises(ValueError, self.ovfEnv.removeProperties,
                          "12", vProps2)

        #: Verify that multiple Properties can be removed from root.
        self.ovfEnv.removeProperties("12", propsAll)
        self.assertRaises(ValueError, self.ovfEnv.removeProperties,
                          "12", vPropsAll)

        #: Verify that a Property can be successfully removed.
        self.ovfEnv.removeProperties(self.entID, props)
        self.assertRaises(ValueError, self.ovfEnv.removeProperties,
                          self.entID, vProps)

        #: Verify that multiple Properties can be successfully removed.
        self.ovfEnv.removeProperties(self.entID, ["UserName", "IP"])
        self.assertRaises(ValueError, self.ovfEnv.removeProperties,
                          self.entID, ["UserName", "IP"])

        #: Verify that all Properties can be successfully removed.
        self.ovfEnv.removeProperties(self.entID, ["UserName", "IP", "Passord"])
        self.assertRaises(ValueError, self.ovfEnv.removeProperties,
                          self.entID, ["UserName", "IP", "Passord"])

        self.ovfEnv.generateXML("out.xml")
        rc = EnvironmentSection.validateXML("out.xml", OVF_ENV_XSD)
        self.assertEquals(rc, 0)

    def testRemovePropertiesMultiSection(self):
        """ Verify removeProperties when multiple sections in Entity. """
        props = ["Version"]
        props2 = ["Kind", "Version"]
        propsAll = ["fillerkey", "propkey", "Passord"]
        vProps = ["Version"]
        vProps2 = ["Kind", "Version"]
        vPropsAll = ["fillerkey", "propkey", "Passord"]

        self.ovfEnv2.createHeader(self.envID)
        self.ovfEnv2.createSection(self.entID, "Entity")
        self.ovfEnv2.createSection(self.entID, "PropertySection",
                                   self.propdata)
        self.ovfEnv2.createSection(self.entID, "PropertySection",
                                   self.platdata)
        self.ovfEnv2.createSection(None, "PropertySection", self.propdata)

        #: Verify that ValueError is raised when unable to remove any property
        self.assertRaises(ValueError, self.ovfEnv2.removeProperties,
                          self.entID, "errir")
        #: Verify that a Property can be successfully removed.
        self.ovfEnv2.removeProperties(self.entID, props)
        self.assertRaises(ValueError, self.ovfEnv2.removeProperties,
                          self.entID, vProps)

        #: Verify that multiple Properties can be successfully removed.
        self.ovfEnv2.removeProperties(self.entID, props2)
        self.assertRaises(ValueError, self.ovfEnv2.removeProperties,
                          self.entID, vProps2)

        #: Verify that all Properties can be successfully removed.
        self.ovfEnv2.removeProperties(self.entID, propsAll)
        self.assertRaises(ValueError, self.ovfEnv2.removeProperties,
                          self.entID, vPropsAll)

        self.ovfEnv2.generateXML("out.xml")
        rc = EnvironmentSection.validateXML("out.xml", OVF_ENV_XSD)
        self.assertEquals(rc, 0)

    def testRemovePlatformProperties(self):
        """ Verify the functionality of removePlatformProperties. """

        props = ["Version"]
        props2 = ["Kind", "Version"]
        propsAll = ["Kind", "Vendor", "Locale"]
        vProps2 = ["Kind", "Version"]
        vpropsAll = ["Kind", "Vendor", "Locale"]

        #: Verify that ValueError is thrown when removing a
        #: non-existent property.
        self.assertRaises(ValueError, self.ovfEnv.removePlatformProperties,
                          self.entID, props)

        #: Verify that multiple Properties can be successfully removed.
        self.setUp()
        self.ovfEnv.removePlatformProperties(self.entID, props2)
        self.assertRaises(ValueError, self.ovfEnv.removePlatformProperties,
                          self.entID, vProps2)

        #: Verify that all Properties can be successfully removed.
        self.setUp()
        self.ovfEnv.removePlatformProperties(self.entID, propsAll)
        self.assertRaises(ValueError, self.ovfEnv.removePlatformProperties,
                          self.entID, vpropsAll)

        self.ovfEnv.generateXML("out.xml")
        rc = EnvironmentSection.validateXML("out.xml", OVF_ENV_XSD)
        self.assertEquals(rc, 0)

    def testRemovePlatformPropertiesMultiSection(self):
        """ Verify removePlatformProperties w/ multiple sections in Entity."""

        props = ["Version"]
        props2 = ["Kind", "Version"]
        propsAll = ["Kind", "Vendor", "Locale"]
        vProps = ["Version"]
        vProps2 = ["Kind", "Version"]
        vpropsAll = ["Kind", "Vendor", "Locale"]

        self.ovfEnv2.createHeader(self.envID)
        self.ovfEnv2.createSection(self.entID, "Entity")
        self.ovfEnv2.createSection(self.entID, "PlatformSection",
                                   self.platdata)
        self.ovfEnv2.createSection(self.entID, "PlatformSection",
                                   self.platdata)
        self.ovfEnv2.createSection(None, "PlatformSection", self.platdata)

        #: Verify that ValueError is raised when unable to remove any property
        self.assertRaises(ValueError, self.ovfEnv2.removePlatformProperties,
                          self.entID, "errir")

        #: Verify that a Property can be successfully removed from root.
        self.ovfEnv2.removePlatformProperties(self.envID, props)
        self.assertRaises(ValueError, self.ovfEnv2.removePlatformProperties,
                          self.envID, vProps)

        #: Verify that multiple Properties can be removed from root.
        self.ovfEnv2.createSection(None, "PlatformSection", self.platdata)
        self.ovfEnv2.removePlatformProperties(self.envID, props2)
        self.assertRaises(ValueError, self.ovfEnv2.removePlatformProperties,
                          self.envID, vProps2)

        #: Verify that a Property can be successfully removed.
        self.ovfEnv2.removePlatformProperties(self.entID, props)
        self.assertRaises(ValueError, self.ovfEnv2.removePlatformProperties,
                          self.entID, vProps)

        #: Verify that multiple Properties can be successfully removed.
        self.ovfEnv2.removePlatformProperties(self.entID, props2)
        self.assertRaises(ValueError, self.ovfEnv2.removePlatformProperties,
                          self.entID, vProps2)

        #: Verify that all Properties can be successfully removed.
        self.ovfEnv2.removePlatformProperties(self.entID, propsAll)
        self.assertRaises(ValueError, self.ovfEnv2.removePlatformProperties,
                          self.entID, vpropsAll)

        self.ovfEnv2.generateXML("out.xml")
        rc = EnvironmentSection.validateXML("out.xml", OVF_ENV_XSD)
        self.assertEquals(rc, 0)

    def testChangeID(self):
        """ Verify the functionality of changeID. """

        #: Verify that root Id can be changed.
        self.ovfEnv.changeID("12", self.envID)
        self.assertEqual\
        (self.ovfEnv.environment.attributes['ovfenv:id'].value, self.envID)
        #: Verify that Entity ID can be changed.
        self.ovfEnv.changeID(self.entID, self.newID)
        element = self.ovfEnv.findElementById(self.newID)
        self.assertEqual\
        (element.attributes['ovfenv:id'].value, self.newID)
        #: Verity that ValueError is raised when Id is not found.
        self.assertRaises(ValueError, self.ovfEnv.changeID, self.entID, "6")
        #: Verify that ValueError is raised if newID already exists.
        self.assertRaises(ValueError, self.ovfEnv.changeID, self.envID,
                          self.newID)
        #: Verify that valueError is raised when None is passed as
        #: oldId or newId.
        self.assertRaises(ValueError, self.ovfEnv.changeID, None, self.newID)
        self.assertRaises(ValueError, self.ovfEnv.changeID, self.newID, None)
        #: Validate the xml.
        self.ovfEnv.generateXML("out.xml")
        rc = EnvironmentSection.validateXML("out.xml", OVF_ENV_XSD)
        self.assertEquals(rc, 0)

    def testValidateXML(self):
        """ test ValidateXML function. """
        rc = EnvironmentSection.validateXML("test.xml", OVF_ENV_XSD)
        self.assertEquals(rc, 0)

        self.assertRaises(ValueError,
                          EnvironmentSection.validateXML,"test.xml", None)
        self.assertRaises(ValueError,
                          EnvironmentSection.validateXML, "None", "test.xml")
        self.assertRaises(ValueError,
                           EnvironmentSection.validateXML,"tes.xml",
                                                          OVF_ENV_XSD)
        self.ovfEnv.createSection("12", "PlatformSection", self.propdata)
        self.ovfEnv.generateXML("out.xml")
        self.assertRaises(ValueError, EnvironmentSection.validateXML,
                          "out.xml", OVF_ENV_XSD)

if __name__ == "__main__":
    __runTest__ = unittest.TestLoader().loadTestsFromTestCase\
    (OvfEnvironmentTestCase)
    __runner__ = unittest.TextTestRunner(verbosity=2)
    __runner__.run(unittest.TestSuite(__runTest__))

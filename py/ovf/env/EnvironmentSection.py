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
Object representing an ovf-env file (XML).
Contains methods to generate/manipulate environment xml file.
"""

#from xml.dom.ext import PrettyPrint
import os
import sys
from xml.dom.minidom import parse, Document
from xml.dom.minidom import NodeList
import Constants
from ovf import validation

class EnvironmentSection:
    """
    Object representing an ovf-env file (XML).
    Contains methods to generate/manipulate environment xml file.
    """

    def __init__(self, path=None):
        """
        Initialize the member variables. Parse the xml file if its provided.

        @param path: path to ovf-env.xml file
        @type  path: string
        """

        self.id = None #: will store optional EnvironmentType id
        self.document = None #: Document object.
        self.environment = None #: Environment object.
        self.oldChild = None #: used for merging nodes.
        self.path = None

        if path != None:
            self.path = path
            try:
                self.document = parse(self.path)
            except IOError, (errno, strerror):
                raise IOError("I/O error(%s): %s" % (errno, strerror))
            self.document.normalize()
            self.environment = self.document.documentElement


    def createHeader(self, envid=None):
        """
        Create root element of the ovf-env file.

        @param envid: Environment id to be used for the header.
        @type envid: String
        """

        if self.document == None:
            self.document = Document()
            self.environment = self.document.createElement(Constants.ENV_SEC)
            self.environment.setAttribute(Constants.XSI_KEY, Constants.XSI_VAL)
            self.environment.setAttribute(Constants.ENV_KEY, Constants.ENV_VAL)
            self.environment.setAttribute(Constants.STR_KEY, Constants.STR_VAL)
            self.environment.setAttribute(Constants.NS_KEY, Constants.NS_VAL)

            if envid != None:
                self.environment.setAttribute("ovfenv:id", envid)

            self.document.appendChild(self.environment)

        else:
            if envid != None:
                modifyAttribute(self.environment, "ovfenv:id", envid)


    def createSection(self, envId, sectionName, data=None):
        """
        Create section in ovf-env xml file.

        'sectionName' contains the name of the section that will be created.
        It could be a 'PlatformSection' or 'PropertySection' or "Entity".
        A new section will be created if one with given id does
        not already exist. All Entity elements have an id, so given id must match the
        appropriate Entity id to be created in that Entity. A section which is the child
        of the root element may not have any id.

        @param envId: Unique id of the Entity or Element containing the section.
        @type envId: String

        @param sectionName: Could be "PlatformSection"/"PropertySection"/"Entity".
        @type sectionName: String

        @param data: Information about the deployment  platform or its properties.
        @type data: dict.

        @raise ValueError: The possible cases are as follow
            - I{B{Case 1:}} The document has not been initialized.
            - I{B{Case 2:}} No section name provided.
            - I{B{Case 3:}} ID is required while creating an Entity Section.
        """

        if self.environment == None:
            raise ValueError (Constants.MISSING_ENV)

        if sectionName == None or (sectionName != Constants.PLAT_SEC and \
                                   sectionName != Constants.ENT_SEC and \
                                   sectionName != Constants.PROP_SEC):
            raise ValueError(Constants.MISSING_ELEMENT)

        if sectionName == Constants.ENT_SEC and envId == None:
            raise ValueError(Constants.ID_REQUIRED)

        self.createNewSection(envId, sectionName, data)



    def createNewSection(self, envId, sectionName, data=None):
        """
        Create a new section in ovf-env file.

        If the id is none or matches that of the root element, then
        a new section will be created in the root. Else, the document
        will be searched for matching id and a new section added to
        that id. If a match is not found then throw exception.

        @param envId: Unique id of the Entity or Element containing the section.
        @type envId: String

        @param sectionName: Could be "PlatformSection" or "PropertySection".
        @type sectionName: String

        @param data: Information about the deployment  platform or its properties.
        @type data: dict.

        @raise ValueError: The possible cases are as follow
            - I{B{Case 1:}} No section name provided.
            - I{B{Case 2:}} Given id was not found in the document.
        """

        if sectionName == None:
            raise ValueError(Constants.MISSING_ELEMENT)

        if envId == None: #: If no id, then add a child to the root element.
            if sectionName == Constants.ENT_SEC:
                raise ValueError(Constants.ID_REQUIRED)
            element = self.environment
        else:
            element = self.findElementById(envId)

        if element == None:
            if sectionName == Constants.ENT_SEC:
                self.createEntity(envId)
            else:
                raise ValueError (Constants.MISSING_ID)
        else:
            if sectionName == Constants.ENT_SEC:
                raise ValueError (Constants.ENT_EXISTS)
            else:
                self.addSection(element, sectionName, data)



    def createEntity(self, envId):
        """
        Method to create Entity section in the document.

        Adds 'envId' as the attribute of the Entity Section.

        @param envId: Unique ID of the Entity Section.
        @type envId: String.

        @raise ValueError: The possible cases are as follow
            - I{B{Case 1:}} No id provided.
        """

        if envId == None:
            raise ValueError(Constants.NO_ENVID)

        element = self.document.createElement(Constants.ENT_SEC)
        element.setAttribute("ovfenv:id", envId)
        self.environment.appendChild(element)


    def addSection(self, section, secType, data):
        """
        This method will append or replace a section.

        It appends to given 'section' if there isn't a section of
        given 'secType' with the same entity id. It replaces the
        section if a section already exists.

        @param section: Node which will be replaced or appended with the given data.
        @type section: Node

        @param secType: Could be "PlatformSection" or "PropertySection".
        @type secType: String

        @param data: Information about the deployment  platform or its properties.
        @type data: dict.

        @raise ValueError: The possible cases are as follow
            - I{B{Case 1:}} No 'Node' provided as input.
            - I{B{Case 2:}} No 'Type' provided as input.
            - I{B{Case 3:}} No 'Data' provided as input.
            - I{B{Case 4:}} Failed to create a new element/node.
        """

        if section == None:
            raise ValueError (Constants.MISSING_SECTION)

        if secType == None:
            raise ValueError (Constants.MISSING_ELEMENT)

        platform = self.document.createElement(secType)
        if platform == None:
            raise ValueError (Constants.CREATE_FAILED)

        if secType == Constants.PLAT_SEC:
            self.addElementsFromDict(platform, data)
        else:
            self.addAttributesFromDict(Constants.PROPERTY, \
                                       Constants.PREFIX, platform, data)
        if section == self.environment:
            elements = section.getElementsByTagName(Constants.ENT_SEC)
            if elements != []:
                section.insertBefore(platform, elements[0])
                return
        section.appendChild(platform)


    def addElementsFromDict (self, node, platformDict, attachBeforeNode=None):
        """
        Add key + value pairs from the given dictionary as Elements.

        @param node:section that will be updated.
        @type node: Node

        @param platformDict: Dictionary with key/values to be added.
        @type platformDict: dict


        @raise ValueError: The possible cases are as follow
            - I{B{Case 1:}} No 'Node' provided as input.
            - I{B{Case 2:}} dictionary object provided as input is None.
        """

        if node == None:
            raise ValueError (Constants.MISSING_SECTION)

        if platformDict != None:
            for key, val in platformDict.iteritems():
                element = self.document.createElement(key)
                text = self.document.createTextNode(str(val))
                element.appendChild(text)
                if attachBeforeNode != None:
                    node.insertBefore(element, attachBeforeNode)
                else:
                    node.appendChild(element)



    def addAttributesFromDict(self, elementName, \
                              prefix, node, attrDict):
        """
        Add key/values from given dictionary as Attributes.

        @param elementName: Name of the element that will be created.
        @type elementName: String

        @param prefix: prefix for the attribute keys.
        @type prefix: String

        @param node:section that will be updated.
        @type node: Node

        @param attrDict: Dictionary with key/values to be added.
        @type attrDict: dict


        @raise ValueError: The possible cases are as follow
            - I{B{Case 1:}} There is no name provided for the element that will be created.
            - I{B{Case 2:}} No 'Node' provided as input.
            - I{B{Case 3:}} dictionary object provided as input is None.
        """

        if elementName == None:
            raise ValueError (Constants.MISSING_NAME)

        if node == None:
            raise ValueError (Constants.MISSING_SECTION)

        if attrDict != None:
            for key, val in attrDict.iteritems():
                element = self.document.createElement(elementName)
                element.setAttribute(prefix+"key", key)
                element.setAttribute(prefix+"value", val)
                node.appendChild(element)


    def findElementById(self, envID):
        """
        Find node with given ID.

        This method searches the tree for given envID. And returns it
        back to the caller. Returns 'None' on failure.

        @param envID: ID to be searched.
        @type envID: String

        @return: Node that matches the envID.
        @type : Node.

        @raise ValueError: The possible cases are as follow
            - I{B{Case 1:}} No 'envID' provided as input.
            - I{B{Case 2:}} Environment Section not defined.
        """

        if envID == None:
            raise ValueError (Constants.NO_ENVID)

        rootElement = self.document.getElementsByTagName(Constants.ENV_SEC)
        if rootElement == []:
            raise ValueError (Constants.MISSING_ENV)

        attr = rootElement[0].attributes
        if attr != None:
            for i in range (0, attr.length):
                if (attr.item(i).name == Constants.ID) \
                & (attr.item(i).nodeValue == envID):
                    return rootElement[0]

        entityElement = self.document.getElementsByTagName(Constants.ENT_SEC)
        if entityElement != []:
            lenth = len(entityElement)
            for i in range (0, lenth):
                nam = entityElement[i]
                if (nam.hasAttribute(Constants.ID)) \
                & (nam.getAttribute(Constants.ID) == envID):
                    return nam

        return None


    def removeSection(self, secID, sectionName):
        """
        Remove a given section from environment xml.
        """
        if secID == None:
            raise ValueError(Constants.MISSING_ID)
        #: Find the given ID in the xml
        element = self.findElementById(secID)
        if element == None:
            raise ValueError(Constants.MISSING_ID)
        #: Find Element child with given sectionName.
        section = self.findNodeBySectionName(element, sectionName)
        if section == []:
            raise ValueError(Constants.MISSING_SECTION)
        for i in range(0, section.length):
            element.removeChild(section[i])

    def removeProperties (self, secID, keys):
        """
        Remove properties from PropertySection.

        This method removes properties whose keys were passed
        as input. It looks for the propertySection with given
        secID.

        @param secID: The ID of the section whose properties need removed.
        @type secID: String
        @param keys: Property keys that need removed.
        @type keys: list
        """
        if secID == None:
            raise ValueError(Constants.MISSING_ID)
        done = 0
        #: Find the given ID in the xml
        element = self.findElementById(secID)
        if element == None:
            raise ValueError(Constants.MISSING_ID)
        #: Find Element child with given sectionName.
        section = self.findNodeBySectionName(element, Constants.PROP_SEC)
        if section == []:
            raise ValueError(Constants.MISSING_SECTION)
        #: Remove properties with given keys.
        for x in range(0, section.length):
            props = section[x].getElementsByTagName("Property")
            for i in range(0, props.length):
                attrs = props[i].attributes
                attrList = attrs.items()
                if attrList == []:
                    raise ValueError(Constants.MISSING_PROPERTY)
                else:
                    for l in range(0, len(keys)):
                        if keys[l] == attrList[0][1]:
                            section[x].removeChild(props[i])
                            keys.remove(keys[l])
                            done = 1
                            break
        if done == 0:
            raise  ValueError(Constants.MISSING_PROPERTY)

    def removePlatformProperties (self, secID, keys):
        """
        Remove properties from PlatformSection.

        This method removes properties whose keys were passed
        as input. It looks for the PlatformSection with given
        secID.

        @param secID: The ID of the section whose properties need removed.
        @type secID: String
        @param keys: Property keys that need removed.
        @type keys: list
        """

        if secID == None:
            raise ValueError(Constants.MISSING_ID)
        done = 0
        #: Find the given ID in the xml
        element = self.findElementById(secID)
        if element == None:
            raise ValueError(Constants.MISSING_ID)
        #: Find Element child with given sectionName.
        section = self.findNodeBySectionName(element, Constants.PLAT_SEC)
        if section == []:
            raise ValueError(Constants.MISSING_SECTION)
        #: Remove properties with given keys.
        for x in range(0, section.length):
            for y in range(0, len(keys)):
                props = section[x].getElementsByTagName(keys[y])
                for z in range(0, props.length):
                    section[x].removeChild(props[z])
                    done = 1
        if done == 0:
            raise  ValueError(Constants.MISSING_PROPERTY)

    def generateXML(self, fileName):
        """ Write the xml to a file. """

        fileHandle = open ( fileName, 'w' )
        fileHandle.write (self.document.toprettyxml() )
        fileHandle.close()


    def changeID(self, oldId, newId):
        """ Will change ID of a section from oldId to newId.

        Search for oldId in the xml and change it to newId.
        Throw exception if xml does not have oldID.

        @param oldId: ID that will change
        @type oldId: String
        @param newId: new ID that will replace the oldId.
        @type newId: String
        """

        if oldId == None or newId == None:
            raise ValueError(Constants.MISSING_ID)
        #: Verify that newId does not exist.
        element = self.findElementById(newId)
        if element != None:
            raise ValueError(Constants.ENT_EXISTS)
        #: Search for oldId
        element = self.findElementById(oldId)
        if element == None:
            raise ValueError(Constants.MISSING_ID)
        #: Replace oldId with newId
        modifyAttribute(element, Constants.ID, newId)


    def findNodeBySectionName(self, element, sectionName):
        """
        Find node with given ID and SectionName.

        This method looks for a node that has the given sectionName
        in the Element.

        @param element: Element which will be searched.
        @type secID: Element
        @param sectionName: section name to be searched.
        @type sectionName: String

        @return: nodeList
        """

        if element == None:
            raise ValueError (Constants.MISSING_ID)
        # Find the section in given entity.
        section = element.getElementsByTagName(sectionName)
        if section.length == 0:
            raise NameError (Constants.MISSING_ELEMENT)
        if element == self.environment:
            # Weed out the Entity sections
            section = NodeList()
            nodes = element.childNodes
            for i in range(0, nodes.length):
                if nodes[i].localName == Constants.ENT_SEC:
                    break
                elif nodes[i].localName == sectionName:
                    section.append(nodes[i])
        return section


def modifyAttribute(section, key, value):
    """
    Looks for given 'key' in the 'section' and changes it with the provided 'value'.

    @param section: Section to be searched.
    @type section: Element

    @param key: Look for this key in the section.
    @type key: String

    @param value: Replace the value of the key with this value.
    @type value: String
    """

    attrib = section.getAttribute(key)
    if len(attrib) > 0:
        section.removeAttribute(key)
    section.setAttribute(key, value)



def validateXML(xmlFile, schemaFile):
    """
    This method validates the XML against the schema.

    @param xmlFile: Path to xml file that needs to be validated.
    @type xmlFile: String

    @param schemaFile: Path to schema file used for validation.
    @type schemaFile: String
    """

    if not schemaFile:
        schemaFile = Constants.ENV_SCHEMA

    if not os.path.exists(schemaFile):
        print >> sys.stderr, "ERROR: Schema file not found"
        return 1

    if not os.path.exists(xmlFile):
        print >> sys.stderr, "ERROR: XML file not found"
        return 1

    msgHandler = validation.ErrorHandler()
    ret = validation.validateOVF(schemaFile, xmlFile, msgHandler)

    for each in msgHandler.error_list:
        print "E: %s" % each

    for each in msgHandler.warning_list:
        print "W: %s" % each

    if ret == 0:
        print xmlFile + " validates"
    return ret
#    cmdStr = "xmllint --schema " + schemaFile + " " + fileName +" >/dev/null"

#    return os.system(cmdStr)

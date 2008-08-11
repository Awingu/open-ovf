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
from xml.dom.minidom import parse, Document
import os

import OvfReferencedFile
import Ovf

OVF_VERSION = "1.0.0b"

class OvfFile:
    """
    Object representing a .ovf file (XML)
    """

    files = []     #: list of OvfReferencedFile objects
    document = None
    path = None
    envelope = None
    version = None

    def __init__(self, path=None):
        """
        Initializes the class variables.

        @param path: a filename to read
        @type  path: string

        @return: an OvfSet object for the file in name
        @rtype: OvfSet
        """
        if path != None:
            self.path = path
            self.setFilesFromOvfFileReferences()
            self.document = parse(self.path)
            self.document.normalize()
            self.envelope = self.document.documentElement
            self.version = OVF_VERSION

    def addReferencedFile(self, refFileObj):
        """
        This method will add a OvfReferencedFile
        to the file list.

        Note::
            If a file with a certain href is present and another file with the
            same href is added to the files list, the information for that file
            will be updated and two files with duplicate href's will not be
            created.

        @param refFileObj: OvfReferencedFile
        @type refFileObj: OvfReferencedFile object

        """
        allowAppend = True
        for refFile in self.files:
            if unicode(str(refFile.href)) == unicode(refFileObj.href):
                refFile.href = refFileObj.href
                refFile.path = refFileObj.path
                refFile.checksum = refFileObj.checksum
                refFile.checksumStamp = refFileObj.checksumStamp
                refFile.size = refFileObj.size
                refFile.compression = refFileObj.compression
                refFile.file_id = refFileObj.file_id
                refFile.chunksize  = refFileObj.chunksize
                allowAppend = False
                break

        if allowAppend:
            self.files.append(refFileObj)

    def getReferencedFiles(self):
        """
        Return a list of OvfReferencedFiles for this object

        @return: a list of files referenced in this OvfFile
        @rtype: List of OvfReferencedFile

        """
        return(self.files)

    def setFilesFromOvfFileReferences(self):
        """
        Set 'files' list based on contents of the ovfFile. The method gets the
        files in the Reference section in the OVF and sets them to the files
        list.
        """
        self.files = getReferencedFilesFromOvf(self.path)

    def writeFile(self, fileObj=None, pretty=True, encoding=None):
        """
        Write out the file to fileobject.

        @param fileObj: a file handle to write to
        @type  fileObj: file handle

        @param pretty: if True format/indent (writexml) False = toxml()
        @type  pretty: Boolean

        @param encoding: The encoding used for the XML.
        @type encoding: String

        """
        needClose = False
        if fileObj == None:
            fileObj = open(self.path, "w")
            needClose = True

        if pretty:
            Ovf.remove_whitespace_nodes(self.document)
            Ovf.xwritexml(self.document, fileObj, '', '\t', '\n', encoding)
        else:
            fileObj.write(self.document.toxml())

        if needClose:
            fileObj.close()


    def syncReferencedFilesToDom(self):
        """
        This function will modify the document record for the OVF file
        in the OvfFile object by adding files from its reference list.
        Use writeFile to save changes to disk.

        """
        ref = None
        for child in self.document.getElementsByTagName('References'):
            ref = child
            break

        while ref.firstChild != None:
           ref.removeChild(ref.firstChild).unlink()
        for currFile in  self.files:
            ref.appendChild(currFile.toElement())

    def createEnvelope(self, version=None, lang=None):
        """
        This method will create the envelope for the OVF. This is the root
        element for the .ovf file.

        @param version: The version of the OVF spec being used. Default is
        1.0.0b
        @type version: String

        @param lang: The language being used in the OVF. Default is en-US.
        @type lang: String
        """
        if self.document == None:
            self.document = Document()
            if version == None:
                version = OVF_VERSION
            if lang == None:
                lang = "en-US"

            self.envelope = self.document.createElement('Envelope')
            self.envelope.setAttribute("xmlns:xsi",
                                       "http://www.w3.org/2001/XMLSchema-instance")
            self.envelope.setAttribute("xmlns:ovf",
                                       "http://schemas.dmtf.org/ovf/envelope/1" )
            self.envelope.setAttribute("xmlns:ovfstr",
                                       "http://schema.dmtf.org/ovf/strings/1")
            self.envelope.setAttribute("xmlns:vssd",
                                       "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_VirtualSystemSettingData")
            self.envelope.setAttribute("xmlns:rasd",
                                       "http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData")
            self.envelope.setAttribute("ovf:version", version)
            self.envelope.setAttribute("xml:lang", lang)
            self.envelope.setAttribute('xsi:schemaLocation',
                                       "http://schemas.dmtf.org/ovf/envelope/1 ../ovf-envelope.xsd")
            self.envelope.setAttribute("xmlns",
                                       "http://schemas.dmtf.org/ovf/envelope/1")

            self.document.appendChild(self.envelope)
        else:
            self.envelope = self.document.DOCUMENT_NODE

    def createRefSection(self):
        """
        This will create the referenced files section. If the section already
        exists it will append new files to the already existing section.
        NOTE::
            The files list MUST contain files to be added. Otherwise raises
            NotImplementedError.

        @raise NotImplementedError: The possible cases are as follow
                - I{B{Case 1:}} The document has not been
                initialized.
                - I{B{Case 2:}} The list that contains the files within the
                class has not been initialized.
        """
        if self.document == None:
            raise NotImplementedError, "The document has not been initialized.\
             Please create a document. Create envelope."

        if self.files == None:
            raise NotImplementedError, "The files list must contain at least\
             one reference."
        if self.envelope.getElementsByTagName('References') == []:
            comment = self.document.createComment("Reference of all external\
             files")
            self.envelope.appendChild(comment)

            refsChild = self.document.createElement("References")
            self.envelope.appendChild(refsChild)
        self.syncReferencedFilesToDom()

    def createDiskSection(self, diskDictList, infoComments, infoID=None,
                          sectionID=None, sectionReq=None):
        """
        This method will create the disk section of the OVF. This section of
        the OVF describes meta-information about all virtual disks in the
        package.

        NOTE::
            If a section is missing enter None. Parent disk elements must
            occur before child Disk elements that refer them. parentRef must be
            present for a child disk.

        @raise TypeError: The function raises this error if sectionReq is not
                            a boolean.

        @raise AttributeError: The possible cases are as follow
                - I{B{Case 1:}} The diskId is not passed in as part of
                the diskDictList.
                - I{B{Case 2:}} The capacity is not passed in as part
                of the diskDictList.
                - I{B{Case 3:}} The format is not passed in as part
                of the diskDictList.

        @raise ValueError: If a disk with a parentRef is added but the parent
                            disk with the given id does not exist.

        @param diskDictList: Is a list of dictionaries that contains the
                            information of the individual disks.

        @type diskDictList: List of dictionaries of disks.
            - The dictionaries MUST contain:
                - dict['diskId']
                - dict['fileRef']
                - dict['capacity']
                - dict['populatedSize']
                - dict['format']
                - dict['capacityAllocUnits']
                - dict['parentRef']

        @param infoComments: These are the comments that describe all the disks
        @type infoComments: String

        @param sectionID: The id for the section inside the ovf.
        @type sectionID: String

        @param sectionReq: If this section is required enter 'true' or 'false'
        @type sectionReq: String
        ""        """
        if self.envelope.getElementsByTagName('DiskSection') != []:
            self.addNewDisk(diskDictList)

        #if there is only a new disk to be added don't allow to create another
        # disk section
        else:
            ovfid = "ovf:id"
            ovfRequired = "ovf:required"
            ovfCapacity = "ovf:capacity"
            ovfDiskId = "ovf:diskId"
            ovfPopulated = "ovf:populatedSize"
            ovfFormat = "ovf:format"
            ovfFileRef = "ovf:fileRef"
            ovfCapacityAllocUnits = "ovf:capacityAllocationUnits"
            ovfParentRef = "ovf:parentRef"

            comment = self.document.createComment("Meta Data description")
            self.envelope.appendChild(comment)

            comment = self.document.createComment("Disk Section")
            self.envelope.appendChild(comment)


            diskSectionChild = self.document.createElement("DiskSection")

            if sectionID != None: #if the param is None don't add the attribute
                diskSectionChild.setAttribute(ovfid, sectionID)
            if sectionReq != None:
                if sectionReq == False:
                    diskSectionChild.setAttribute(ovfRequired, 'false')
                elif sectionReq == True:
                    diskSectionChild.setAttribute(ovfRequired, 'true')
                else:
                    raise TypeError, "The param 'sectionReq' must be a\
                     boolean."

            #info for comments
            self.createInfoChild(diskSectionChild, infoComments, infoID)

            #this list is to keep track of which files have already been added
            #it is a constraint that if a child file is to be added a parent
            # must have already being added into the disk section
            fileAdded = []

            for child in self.document.getElementsByTagName('Disk'):
                if child.hasAttribute(ovfDiskId):
                    fileAdded.append(child.getAttribute(ovfDiskId))

            for disk in diskDictList:
                diskChild = self.document.createElement("Disk")
                if disk['diskId'] != None:
                    diskChild.setAttribute(ovfDiskId, disk['diskId'])
                else:
                    raise AttributeError,"Disk ID required."

                if disk['fileRef'] != None:
                    diskChild.setAttribute(ovfFileRef, disk['fileRef'])

                if disk['capacity'] != None:
                    diskChild.setAttribute(ovfCapacity, disk['capacity'])
                else:
                    raise AttributeError,"Disk capacity required."

                if disk['populatedSize'] != None:
                    diskChild.setAttribute(ovfPopulated, disk['populatedSize'])

                if disk['format'] != None:
                    diskChild.setAttribute(ovfFormat, disk['format'])
                else:
                    raise AttributeError, "Format required."

                if disk['capacityAllocUnits'] != None:
                    diskChild.setAttribute(ovfCapacityAllocUnits,
                                           disk['capacityAllocUnits'])
                if disk['parentRef'] != None:
                    if disk['parentRef'] in fileAdded:
                        diskChild.setAttribute(ovfParentRef, disk['parentRef'])
                    else:
                        raise ValueError,"In order to add a child disk the\
                         parent must be defined first. Also verify that\
                          parentRef matches parent's fileId."

                fileAdded.append(disk['diskId'])

                diskSectionChild.appendChild(diskChild)

            self.envelope.appendChild(diskSectionChild)

    def addNewDisk(self, diskDictList):
        """
        This section will add a new disc to an already existing Disk section.
        If there isn't a disk section present a NotImplementedError will be
        raised. Also if a diskID is already specified it will update the values
        of that specific disk.

        @raise TypeError: The function raises this error if sectionReq is not
                            a boolean.

        @raise AttributeError: The possible cases are as follow
                - I{B{Case 1:}} The diskId is not passed in as part of
                the diskDictList.
                - I{B{Case 2:}} The capacity is not passed in as part
                of the diskDictList.
                - I{B{Case 3:}} The format is not passed in as part
                of the diskDictList.

        @raise ValueError: If a disk with a parentRef is added but the parent
                            disk with the given id does not exist.

        @type diskDictList: List of dictionaries of disks.
            - The dictionaries MUST contain:
                - dict['diskId']
                - dict['fileRef']
                - dict['capacity']
                - dict['populatedSize']
                - dict['format']
                - dict['capacityAllocUnits']
                - dict['parentRef']


        @param diskDictList: A list of dictionaries that contains the information of the
                            individual disks.
        """
        diskNode = None
        sectionPresent = False
        ovfCapacity = "ovf:capacity"
        ovfDiskId = "ovf:diskId"
        ovfPopulated = "ovf:populatedSize"
        ovfFormat = "ovf:format"
        ovfFileRef = "ovf:fileRef"
        ovfCapacityAllocUnits = "ovf:capacityAllocationUnits"
        ovfParentRef = "ovf:parentRef"
        newDisk = True #to see if we are simply updating the info for a given
        # disk.
        diskToModify = None

        diskNode = self.envelope.getElementsByTagName("DiskSection")[0]
        if diskNode != None:
            sectionPresent = True
        #this list is to keep track of which files have already been added
        #it is a constraint that if a child file is to be added a parent must
        # have already being added into the disk section
        fileAdded = []
        #the way the loop works below is you will first look in the list of\
        # dictionaries  (diskDictList) the next for loop will get the childs\
        # in the Disk section, then if you find a disk with the same id as one\
        # of the disks in the list passed in you will set it up to 'update'\
        # that specific disk rather than create a new one.
        for child in self.document.getElementsByTagName('Disk'):
            if child.hasAttribute(ovfDiskId):
                fileAdded.append(child.getAttribute(ovfDiskId))

        for disk in diskDictList:
            for child in diskNode.childNodes:
                if child.nodeName == 'Disk':
                    if child.getAttribute(ovfDiskId) == disk['diskId']:
                        newDisk = False
                        diskToModify = child
                        fileAdded.append(disk['diskId'])

            if newDisk:
                diskChild = self.document.createElement("Disk")
            if disk['diskId'] != None:
                if not newDisk:
                    diskToModify.removeAttribute(ovfDiskId)
                    diskToModify.setAttribute(ovfDiskId, disk['diskId'])
                else:
                    diskChild.setAttribute(ovfDiskId, disk['diskId'])
            else:
                raise AttributeError,"Disk ID required."

            if disk['fileRef'] != None:
                if not newDisk:
                    diskToModify.removeAttribute(ovfFileRef)
                    diskToModify.setAttribute(ovfFileRef, disk['fileRef'])
                else:
                    diskChild.setAttribute(ovfFileRef, disk['fileRef'])

            if disk['capacity'] != None:
                if not newDisk:
                    diskToModify.removeAttribute(ovfCapacity)
                    diskToModify.setAttribute(ovfCapacity, disk['capacity'])
                else:
                    diskChild.setAttribute(ovfCapacity, disk['capacity'])
            else:
                raise AttributeError,"Disk capacity required."

            if disk['populatedSize'] != None:
                if not newDisk:
                    diskToModify.removeAttribute(ovfPopulated)
                    diskToModify.setAttribute(ovfPopulated,
                                              disk['populatedSize'])
                else:
                    diskChild.setAttribute(ovfPopulated, disk['populatedSize'])

            if disk['format'] != None:
                if not newDisk:
                    diskToModify.removeAttribute(ovfFormat)
                    diskToModify.setAttribute(ovfFormat, disk['format'])
                else:
                    diskChild.setAttribute(ovfFormat, disk['format'])
            else:
                raise AttributeError, "Format required."

            if disk['capacityAllocUnits'] != None:
                if not newDisk:
                    diskToModify.removeAttribute(ovfCapacityAllocUnits)
                    diskToModify.setAttribute(ovfCapacityAllocUnits,
                                              disk['capacityAllocUnits'])
                else:
                    diskChild.setAttribute(ovfCapacityAllocUnits,
                                           disk['capacityAllocUnits'])

            if disk['parentRef'] != None:
                if disk['parentRef'] in fileAdded:
                    if not newDisk:#is is already in there then just modify it
                        diskToModify.removeAttribute(ovfParentRef)
                        diskToModify.setAttribute(ovfParentRef,
                                                  disk['parentRef'])
                    else:
                        diskChild.setAttribute(ovfParentRef,
                                               disk['parentRef'])
                else:
                    raise ValueError,"In order to add a child disk the parent\
                     must be defined first. Also verify that parentRef matches\
                      parent's fileId."

            fileAdded.append(disk['diskId'])


            if not sectionPresent:
                raise NotImplementedError, "A Disk section must be present to\
                 add a new disk. No disk section found."
            else:
                if newDisk:
                    diskNode.appendChild(diskChild)

    def createNetworkSection(self, networkList, infoComments, infoID=None):
        """
        This method will create the network section in the ovf. The network section lists all
        logical networks used in the OVF package.

        @param networkList: A list of networks.
        @type networkList: List of dictionaries of networks.
            - The dictionaries MUST contain:
                - dict['networkID']
                - dict['networkName']
                - dict['description']

        @param infoComments: These are the comments that describe all the networks.
        @type infoComments: String

        @param infoID: The id for the information comment
        @type infoID: String
        """
        #TODO: node not used, for-loop code seems confusing.
        createNet = True
        for node in self.document.getElementsByTagName('NetworkSection'):
            self.addNetwork(networkList)
            createNet = False
        if createNet:
            ovfName = "ovf:name"
            ovfId = "ovf:id"

            comment = self.document.createComment("Network Section")
            self.envelope.appendChild(comment)

            networkSectionChild = self.document.createElement("NetworkSection")

            #info for comments
            self.createInfoChild(networkSectionChild, infoComments, infoID)

            for net in networkList:
                networkChild = self.document.createElement("Network")
                if net['networkName'] != None:
                    networkChild.setAttribute(ovfName, net['networkName'])

                if net['networkID'] != None:
                    networkChild.setAttribute(ovfId, net['networkID'])

                networkDescriptionChild = (self.document.
                                           createElement("Description"))
                descriptionChild = (self.document.
                                    createTextNode(net['description']))
                networkDescriptionChild.appendChild(descriptionChild)

                networkChild.appendChild(networkDescriptionChild)
                networkSectionChild.appendChild(networkChild)


            self.envelope.appendChild(networkSectionChild)
    def addNetwork(self, networkList):
        """
        This function will create and add a network to an already existing Network Section.

        @raise NotImplementedError: This is raised if a NetworkSection is not
        present.

        @param networkList: A list of networks.
        @type networkList: List of dictionaries of networks.
            - The dictionaries MUST contain:
                - dict['networkID']
                - dict['networkName']
                - dict['description']
        """
        ovfName = "ovf:name"
        ovfId = "ovf:id"
        netNode = None

        netNode = self.document.getElementsByTagName("NetworkSection")[0]
        for net in networkList:
            networkChild = self.document.createElement("Network")
            if net['networkName'] != None:
                networkChild.setAttribute(ovfName, net['networkName'])

            if net['networkID'] != None:
                networkChild.setAttribute(ovfId, net['networkID'])

            networkDescriptionChild = (self.document.
                                       createElement("Description"))
            descriptionChild = self.document.createTextNode(net['description'])
            networkDescriptionChild.appendChild(descriptionChild)

            networkChild.appendChild(networkDescriptionChild)
            if netNode != None:
                netNode.appendChild(networkChild)
            else:
                raise NotImplementedError, "A Network Section was not found.\
                 To add a Network the Network section must be present."

    def createDeploymentOptions(self, infoComments, infoID=None, id=None):
        """
        This method creates a deployment options section. The section specifies
        a discrete set of intended resource configurations.

        Note::
            This section can only be created at the Envelope level. Only one
            section can be specified in an OVF descriptor.

        @raise TypeError: It is thrown if a DeploymentOptionsSection has
        already been defined.

        @param infoComments: The information ,<Info>,comments for the section.
        @type infoComments: String

        @param infoID: The id for the information comment
        @type infoID: String

        @return: DOM node of the deployment options section
        """

         #if deployment options have already been spcified then it will throw
        deployOptElement = (self.envelope.
                            getElementsByTagName("DeploymentOptionSection"))

        if len(deployOptElement) == 0:
            deployOptElement = (self.document.
                                createElement("DeploymentOptionSection"))
        else:
            raise TypeError, "The deployment section is already described."
        if id != None:
            deployOptElement.setAttribute("ovf:id", id)
        #create info child
        node = deployOptElement
        self.createInfoChild(node, infoComments, infoID)

        self.envelope.appendChild(deployOptElement)

        return deployOptElement

    def defineDeploymentOptions(self, node, id, label, description, labID=None,
                                desID=None, default=None):
        """
        This method will help describe the deployment options.

        @raise TypeError: The possible cases are as follow
                - I{B{Case 1:}}Is thrown if the node passed in does not have a
                name of DeploymentOptionSection.

                - I{B{Case 2:}}The value passed in for default is not boolean.

        @raise NameError: Is thrown if the id passed in has already been
        specified by another configuration.

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param id: The id for the given configuration.
        @type id: String

        @param label: The label to describe the configuration
        @type label: String

        @param description: The description to describe the configuration
        @type description: String

        @param labID: The id for the label, if any.
        @type labID: String

        @param desID: The id for the description, if any.
        @type desID: String

        @param default: If it is a default configuration.
        @type default: Boolean

        @return: DOM node of the configuration element
        """

        if 'DeploymentOptionSection' != node.nodeName:
            raise TypeError, "The node can only be appended to a\
             DeploymentOptionSection. The given node is not a\
              DeploymentOptionSection."
        for child in node.childNodes:
            if child.nodeName == "Configuration":
                if id == child.getAttribute("ovf:id"):
                    raise NameError, "The id "+id+" for the configuration has\
                     already been implemented. The id for each configuration\
                      has to be unique."

        configElement = self.document.createElement("Configuration")
        configElement.setAttribute("ovf:id", id)

        if default != None:
            if default == True:
                configElement.setAttribute("ovf:default","true")
            elif default == False:
                configElement.setAttribute("ovf:default", "false")
            else:
                raise TypeError, "The input for default is incorrect. It needs\
                 a boolean."
        #since a document can contain multiple labels, it is neccesary to have\
        # an id to distinguish them
        if labID != None:
            self.createLabelChild(configElement, label, labID)
        else:
            self.createLabelChild(configElement, label)

        # just like the label id, the description id is used to distinguish\
        # descriptions
        if desID != None:
            self.createDescriptionChild(configElement, description, desID)
        else:
            self.createDescriptionChild(configElement, description)

        node.appendChild(configElement)

    def createVirtualSystemCollection(self, id, info, infoID=None, node=None):
        """
        This method creates a Virtual System Collection. A Virtual System Collection
        is a container of multiple content elements, which themselves might be Virtual
        System Collections content types. Thus, arbitrary complex configurations  can
        be described.

        @raise NameError: It is raised if the id passed in has already been
        used in another VirtualSystemCollection.

        @raise TypeError: It is thrown if the node passed in does not have
        the node name of VirtualSystemCollection or Envelope.

        @param id: The id for that Virtual System Collection
        @type id: String

        @param info: The information that will be attached to the Virtual System Collection
        @type info: String

        @param infoID: The id for the information comment
        @type infoID: String

        @param node: The VirtualSystemCollection node to append to.
        @type node: DOM Element

        @return: DOM node of the virtual system
        """

        ovfid = "ovf:id"

        if node == None:
            vscNode = self.envelope
        else:
            vscNode = node
        for child in vscNode.childNodes:
            if child.nodeName == "VirtualSystemCollection":
                if id == child.getAttribute(ovfid):
                    raise NameError, "The id "+id+" for the Virtual System\
                     Collection has already been implemented. The id for each\
                      Virtual System Collection has to be unique."

        contentElement = self.document.createElement("VirtualSystemCollection")
        contentElement.setAttribute(ovfid, id)


        self.createInfoChild(contentElement, info, infoID)
        if node != None:

            if (node.nodeName == 'VirtualSystemCollection' or
                node.nodeName == 'Envelope'):
                node.appendChild(contentElement)
            else:
                raise TypeError, "A Virtual System Collection can only be\
                 appended to another Virtual System Collection or the\
                  Envelope."
        else:
            self.envelope.appendChild(contentElement)

        return contentElement

    def createResourceAllocation(self, node, info, infoID=None, config=None,
                                 bound=None, id=None):
        """
        This method will create a resource allocation section.

        @raise TypeError: The possible cases are as follow
                - I{B{Case 1:}} The node passed in does not have a node name of
                VirtualSystemCollection nor VirtualSystem.

                - I{B{Case 2:}}The parameter bound does not have one of the
                 followings as a value:
                     - I{min}
                     - I{max}
                     - I{normal}

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param config: A comma-separated list of configuration names.
        @type config: String.

        @param bound: Specify ranges of the Item element.
                - The ONLY valid values are:
                    - I{min}
                    - I{max}
                    - I{normal}
        @type bound: String.

        @param info: The information ,<Info>,comments for the section.
        @type info: String

        @param infoID: The id for the information comment
        @type infoID: String

        @return: DOM node of the virtual system
        """

        ovfConfig = "ovf:configuration"
        ovfBound = "ovf:bound"

        if "VirtualSystemCollection" != node.nodeName:
            if "VirtualSystem" != node.nodeName:
                raise TypeError, "The node can only be appended to a Virtual\
                     System Collection Section or Virtual System."

        ovfResAlloc = "ResourceAllocationSection"
        resAllocNode = self.document.createElement(ovfResAlloc)

        if id != None:
            resAllocNode.setAttribute("ovf:id", id)
        if config != None:
            resAllocNode.setAttribute(ovfConfig, config)
        if bound != None:
            if bound != 'min' and bound != 'max' and bound != 'normal':
                raise TypeError, "The bound input for a Resource allocation\
                 can ONLY be 'min' OR 'max' OR 'normal'"
            else:
                resAllocNode.setAttribute(ovfBound, bound)

        self.createInfoChild(resAllocNode, info, infoID)
        node.appendChild(resAllocNode)
        return resAllocNode

    def defineResourceAllocation(self, node, refsDefDict, config=None,
                                 bound=None, required=None):
        """
        This method will create a DOM element that can be used to describe virtual
        devices and controllers in the virtual hardware section.

        NOTE::
         Enter None if a field is not to be filled.
        Fields refsDefDict is expecting are
            - refsDefDict['Address']
            - refsDefDict['AddressOnParent']
            - refsDefDict['AllocationUnits']
            - refsDefDict['AutomaticAllocation']
            - refsDefDict['AutomaticDeallocation']
            - refsDefDict['Caption']
            - refsDefDict['Connection']
            - refsDefDict['ConsumerVisibility']
            - refsDefDict['Description']
            - refsDefDict['ElementName']
            - refsDefDict['HostResource']
            - refsDefDict['InstanceID']
            - refsDefDict['Limit']
            - refsDefDict['MappingBehavior']
            - refsDefDict['OtherResourceType']
            - refsDefDict['Parent']
            - refsDefDict['PoolID']
            - refsDefDict['Reservation']
            - refsDefDict['ResourceSubType']
            - refsDefDict['ResourceType']
            - refsDefDict['VirtualQuantity']
            - refsDefDict['Weight']

        @raise TypeError: The cases are as follow
                - I{B{Case 1:}}The value of the parameter required is not a
                boolean.
                - I{B{Case 2:}}The parameter bound does not have one of the
                 followings as a value:
                     - I{min}
                     - I{max}
                     - I{normal}

        @param node: DOM node where the Item element will be attached.
        @type node: DOM node object.

        @param refsDefDict: Dictionary containing information about resources.
        @type refsDefDict: Dictionary

        @param config: A comma-separated list of configuration names.
        @type config: String.

        @param bound: Specify ranges of the Item element. The ONLY valid values are
                      'min','max','normal'.
        @type bound: String.

        @param required: Specifies if the section is required or not.
        @type required:  Boolean

        """

        itemChild = self.document.createElement('Item')#create the element <Item>

        ovfConfig = "ovf:configuration"
        ovfBound = "ovf:bound"
        ovfRequired = "ovf:required"
        if config != None:
            itemChild.setAttribute(ovfConfig, config)
        if bound != None:
            if bound != 'min' and bound != 'max' and bound != 'normal':
                raise TypeError, "The bound input for a Resource allocation can ONLY be 'min' OR 'max' OR 'normal'"
            else:
                itemChild.setAttribute(ovfBound, bound)
        if required != None:
            if required == True:
                itemChild.setAttribute(ovfRequired, "true")
            elif required == False:
                itemChild.setAttribute(ovfRequired, "false")
            elif required != True or required != False:
                raise TypeError, "The value 'required' must be; True | False."
        keys = refsDefDict.keys()
        keys.sort()
        for ent in keys:
            if refsDefDict[ent] != None:

                child = self.document.createElement("rasd:" + ent)
                child.appendChild(self.document.createTextNode(refsDefDict[ent]))
                itemChild.appendChild(child)
        node.appendChild(itemChild)

    def createProductSection(self, node, info, prodList,classDesc, instance,id=None,infoID=None):
        """
        This method will create the product section.

        Note::
          If more than one product section is present then classDesc and
          instance must be defined. Otherwise it is empty. The combination of
          these attributes is used to uniquely identify a virtual sysem's
          product section from a number of product sections.

          prodList fields:
            prodList = [("Product", product),
                ("Vendor", vendor),
                ("Version", productVersion),
                ("FullVersion", fullVersion),
                ("ProductUrl", prodURL),
                ("VendorUrl", vendorURL),
                ("AppUrl", appURL)]

        @raise TypeError: The error is thrown if the node passed in does not
        have a node name of VirtualSystemCollection nor VirtualSystem.

        @param node: Place where the child will  be inserted.
        @type  node: DOM node object

        @param info: The information ,<Info>,comments for the section.
        @type  info: String

        @param prodList: A list containing all the elements for the
                            product section.
        @type  prodList: List

        @param classDesc: class used to define the product section.
        @type classDesc: String

        @param instance: The instance of this product section
        @type instance: String

        @param id: The id for the section.
        @type id: String

        @param infoID: The id for the information of the section.
        @type infoID: String

        @return: DOM node of the Product Section
        """
        if ("VirtualSystemCollection" != node.nodeName):
            if "VirtualSystem" != node.nodeName:
                raise TypeError, "The node can only be appended to a Virtual\
                 System Collection Section or Virtual System."
        ovfClass = "ovf:class"
        prodInstance = "ovf:instance"
        productSect = "ProductSection"
        #this will create the section for the product
        #<Section xsi:type="ovf:ProductSection_Type">
        sectionElement = self.document.createElement(productSect)

        if classDesc != None:
            sectionElement.setAttribute(ovfClass, classDesc)
        if instance != None:
            sectionElement.setAttribute(prodInstance, instance)
        if id != None:
            sectionElement.setAttribute("ovf:id", id)
        self.createInfoChild(sectionElement, info, infoID)

        for curr in prodList:
            if curr[1] != None:
                elem = self.document.createElement(curr[0])
                text = self.document.createTextNode(curr[1])
                elem.appendChild(text)
                sectionElement.appendChild(elem)

        node.appendChild(sectionElement)
        return sectionElement

    def createIconType(self, node, fileRef, height=None, width=None,
                       mimeType=None):
        """
        This method will add an icon section to the product section.

        @raise TypeError: The error is thrown if the node passed in does not
        have a name of ProductSection.

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param fileRef: The name of the file of the Icon.
        @type fileRef: String

        @param height: The height of the icon.
        @type height: String

        @param width: The width of the icon.
        @type width: String

        @param mimeType: Type of icon ("image/png")
        @type mimeType: String
        """

        if "ProductSection" != node.nodeName:
            raise TypeError, "The node param must be of type Product Section."
        ovfHeight = "ovf:height"
        ovfWidth = "ovf:width"
        ovfMimeType = "ovf:mimeType"
        ovfFileRef = "ovf:fileRef"
        iconSect = self.document.createElement("Icon")
        iconSect.setAttribute(ovfFileRef, fileRef)

        if height != None:
            iconSect.setAttribute(ovfHeight, height)
        if width != None:
            iconSect.setAttribute(ovfWidth, width)
        if mimeType != None:
            iconSect.setAttribute(ovfMimeType, mimeType)
        node.appendChild(iconSect)

    def createCategory(self, node, category):
        """
        This method will create an element <Category> that can be added to any node.
        @param node: The node to attach the newly created category to
        @type  node: Node

        @param category: The category to be entered
        @type category: String
        """
        categoryNode = self.document.createElement("Category")
        categoryTextNode = self.document.createTextNode(category)
        categoryNode.appendChild(categoryTextNode)
        node.appendChild(categoryNode)

    def createPropertyProductSection(self, node, key, type=None, value=None,
                                     usrConfig=None, required=None, id=None):
        """
        This method will create the property section of a product description.

        Note: If the node passed in is not a Product Section a TypeError is raised.

        @raise TypeError: The possible cases are as follow
                - I{B{Case 1:}}The node passed in does not have a name of
                ProductSection.
                - I{B{Case 2:}}The usrConfig parameter value is not a Boolean.
                - I{B{Case 3:}}The required parameter value is not a Boolean.

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param key: Unique identifier
        @type key: String

        @param type: Type of the product
        @type type: String

        @param value: Used to provide default values to the property
        @type value: String

        @param usrConfig: Determines whether the property value is configurable during
                          the installation.
        @type usrConfig: Boolean.

        @param required: If the field is required then True
        @type required: Boolean

        @return: DOM node of the Product Section
        """

        if "ProductSection" != node.nodeName:
            raise TypeError, "The node can only be appended to a Product\
             Section. The given node is not a Product Section"

        propertyElement = self.document.createElement("Property")
        ovfKey = "ovf:key"
        ovfType = "ovf:type"
        ovfValue = "ovf:value"
        ovfUserConfig = "ovf:userConfigurable"
        ovfRequired = "ovf:required"

        propertyElement.setAttribute(ovfKey, key)
        if id != None:
            propertyElement.setAttribute("ovf:id", id)
        if type != None:
            propertyElement.setAttribute(ovfType, type)
        if value != None:
            propertyElement.setAttribute(ovfValue, value)
        if usrConfig != None:
            if usrConfig == True:
                propertyElement.setAttribute(ovfUserConfig, "true")
            elif usrConfig == False:
                propertyElement.setAttribute(ovfUserConfig, "false")
            else:
                raise TypeError, "usrConfig must be of type Boolean."

        if required != None:
            if required == True:
                propertyElement.setAttribute(ovfRequired, "true")
            elif required == False:
                propertyElement.setAttribute(ovfRequired, "false")
            else:
                raise TypeError, "The input 'required' must be of type\
                 Boolean."

        node.appendChild(propertyElement)

        return propertyElement

    def createEULASection(self, info, node, infoID=None, id=None):
        """
        This method will create the EULA section of the ovf. If a node
        is not specified the EULA section created will be appended to the
        envelope (root element).

        @raise TypeError: The error is thrown if the node passed in does not
        have a node name of VirtualSystemCollection nor VirtualSystem.

        @param info: The information ,<Info>,comments for the section.
        @type info: String

        @param infoID: The id for the information comment
        @type infoID: String

        @param node: The node to which the section will be attached to.
        @type node: DOM Element

        @param id: The id for the seciton.
        @type id: String

        @return: DOM node of the EULA section
        """

        if "VirtualSystemCollection" != node.nodeName:
            if "VirtualSystem" != node.nodeName:
                raise TypeError, "The node can only be appended to a Virtual\
                     System Collection Section."

        ovfEula = "EulaSection"

        eulaSec = self.document.createElement(ovfEula)
        self.createInfoChild(eulaSec, info, infoID)

        if id != None:
            eulaSec.setAttribute("ovf:id", id)

        node.appendChild(eulaSec)

        return eulaSec

    def defineLicenseSection(self, node, license, msgID=None):
        """
        This method is to create the license in the
        EULA section.

        @raise TypeError: The error is thrown if the node passed in does not
        have a node name of EulaSection.

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param license: The legal terms for using a particular entity.
        @type license: String

        @param msgID: The id of the given message.
        @type msgID: String
        """

        #the license element can only be created as sub-child of the EULA
        # section
        if "EulaSection" != node.nodeName:
            raise TypeError, "The node can only be appended to a EULA Section.\
             The given node is not a EULA Section."
        licNode = self.document.createElement("License")

        #putting the license content in this fashion <License>some license
        # agreement</License>
        licTextNode = self.document.createTextNode(license)
        licNode.appendChild(licTextNode)
        #since there can be multiple license the way to distinguish them is
        # by the id
        if msgID != None:
            licNode.setAttribute("ovf:msgid", msgID)
        node.appendChild(licNode)

    def createStartupSection(self, node, info, infoID=None, id=None):
        """
        This method will create the startup section for either a Virtual System or a
        Virtual System Collection.

        @raise TypeError: The error is thrown if the node passed in does not
        have a node name of VirtualSystemCollection.

        @param node: Place where the child will  be inserted.
        @type node: DOM node object
        @param info: The information ,<Info>,comments for the section.
        @type info: String
        @param infoID: The id for the information comment
        @type infoID: String

        @return: DOM node of the system section
        """

        ovfstartUp = "StartupSection"
        if "VirtualSystemCollection" != node.nodeName:
            raise TypeError, "The node can only be appended to a Virtual\
             System Collection Section."
        startupNode = self.document.createElement(ovfstartUp)
        self.createInfoChild(startupNode, info, infoID)

        if id != None:
            startupNode.setAttribute("ovf:id", id)
        node.appendChild(startupNode)
        return startupNode

    def defineStartUpSection(self, node, id, order, startDelay=None,
                             waitForGuest=None, startAction=None,
                             stopDelay=None, stopAction=None):
        """
        This method is a helper to the createStartupSection. It is used to further define
        the start up section.

        NOTE::
            startDelay,waitForGuest,startAction,stopDelay and stopAction are only optional only
            for a Virtual System but are not used to describe a Virtual System Collection.

        @raise TypeError: The cases are as follow
                - I{B{Case 1:}}The node passed in does not have a node name of
                StartupSection.
                - I{B{Case 2:}}The parameter waitForGuest does not have a value
                of type Boolean.
                - I{B{Case 3:}}The parameter startAction does not have a value
                of one of the following
                    - I{powerOn}
                    - I{none}
                - I{B{Case 4:}}The parameter stopAction does not have a value
                of one of the following
                    - I{powerOff}
                    - I{guestShutdown}
                    - I{none}

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param id: The entity name within a collection
        @type id: String

        @param order: Specifies the startup order, starting from 0. Items with same
                      order identifier may be started up concurrently. The order is reversed
                      for shutdown. Default order is 0.
        @type order: String

        ONLY SUPPORTED FOR A  Virtual System:
        @param startDelay: Specifies a delay in seconds to wait until proceeding to
                           the next order in the start sequence. Default is 0.
        @type startDelay: String

        @param waitForGuest: Allows the platform to resume the startup sequence after
                            after the guest has reported is ready. Default is False.
        @type waitForGuest: Boolean

        @param startAction: Specifies the the start action to use. Valid values are
                            "powerOn" and none.The default value is "powerOn"
        @type startAction: String

        @param stopDelay: Specifies a delay in seconds to wait until proceeding to the
                          previous order in the sequence. The default is 0.
        @type stopDelay: String

        @param stopAction: Specifies the stop action to use. Valid values are "powerOff",
                           "guestShutdown", and "none". The default is "powerOff"
        @type stopAction: String
        """

        ovfId = "ovf:id"
        ovfOrder = "ovf:order"

        if "StartupSection" != node.nodeName:
            raise TypeError("The node can only be appended to a StartupSection")

        itemNode = self.document.createElement("Item")
        itemNode.setAttribute(ovfId, id)
        itemNode.setAttribute(ovfOrder, order)

        if (startDelay != None or waitForGuest != None or startAction != None
             or stopDelay != None or stopAction != None):
            #don't want to allocate if not needed...
            ovfStartDelay = "ovf:startDelay"
            ovfWaitforGuest = "ovf:waitingForGuest"
            ovfStartAction = "ovf:startAction"
            ovfStopDelay = "ovf:stopDelay"
            ovfStopAction = "ovf:stopAction"

            if startDelay != None:
                itemNode.setAttribute(ovfStartDelay, startDelay)
            else:
                itemNode.setAttribute(ovfStartDelay, "0")

            if waitForGuest != None:
                if waitForGuest == True:
                    itemNode.setAttribute(ovfWaitforGuest, "true")
                elif waitForGuest == False:
                    itemNode.setAttribute(ovfWaitforGuest, "false")
                else:
                    raise TypeError,"Input waitForGuest must be boolean."
            else:
                itemNode.setAttribute(ovfWaitforGuest, "false")

            if startAction != None:
                if startAction == "powerOn" or startAction == "none":
                    itemNode.setAttribute(ovfStartAction, startAction)
                else:
                    raise TypeError, "The startAction input must be either\
                     'powerOn' or 'none' "
            else:
                itemNode.setAttribute(ovfStartAction, "powerOn")

            if stopDelay != None:
                itemNode.setAttribute(ovfStopDelay, stopDelay)
            else:
                itemNode.setAttribute(ovfStopDelay,"0")

            if stopAction != None:
                if (stopAction == "powerOff" or
                    stopAction == "guestShutdown" or
                    stopAction == "none"):
                    itemNode.setAttribute(ovfStopAction, stopAction)
                else:
                    raise TypeError("The ONLY valid input values are 'powerOff', 'guestShutdown' or 'none'. None of those values where present.")
            else:
                itemNode.setAttribute(ovfStopAction, "powerOff")

        node.appendChild(itemNode)

    def createVirtualSystemSection(self, id, info, node=None, infoID=None):
        """
        This method will create a VirtualSystem.

        @raise NameError: It is raised if the id passed in has already been
        used in another VirtualSystem.

        @raise TypeError: It is thrown if the node passed in does not have
        the node name of VirtualSystemCollection or Envelope.

        @param id: The id for that virtual system
        @type id: String

        @param node: Place where the Virtual System child will be inserted.
        @type node: DOM node object

        @param info: The information ,<Info>,comments for the section.
        @type info: String

        @param infoID: The id for the information comment
        @type infoID: String

        @return: DOM node of the virtual system
        """

        ovfid = "ovf:id"
        virtualSys = "VirtualSystem"

        if node == None:
            vscNode = self.envelope
        else:
            vscNode = node

        for child in self.document.getElementsByTagName(virtualSys):
            if id == child.getAttribute(ovfid):
                raise NameError, "The id "+id+" for the Virtual System has\
                 already been implemented. The id for each Virtual System has\
                  to be unique."
        if node != None:
            if "VirtualSystemCollection" != node.nodeName:
                if node.nodeName != "Envelope":
                    raise TypeError, "The node can only be appended to a\
                     Virtual System Collection Section. The given node is not\
                      a Virtual System Collection Section"
        contentElement = self.document.createElement(virtualSys)
        contentElement.setAttribute(ovfid, id)
        self.createInfoChild(contentElement, info, infoID)
        if node == None:
            self.envelope.appendChild(contentElement)
        else:
            vscNode.appendChild(contentElement)

        return contentElement

    def createOSsection(self, node, id, info, infoID=None, description=None,
                        descriptionID=None):
        """
        This method creates the operating systems section for a Virtual System.

        @raise TypeError: This error is thrown if the node passed in does not
        have a node name of VirtualSystem.

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param id: The valid values are defined by the CIM_OperatingSystem.OsType
        @type id: String

        @param info: The information ,<Info>,comments for the section.
        @type info: String

        @param infoID: The id for the information comment
        @type infoID: String

        @param description: The description of the operating system.
        @type description: String

        @param descriptionID: The id for the description
        @type descriptionID: String

        @return: DOM node of the Operating system section
        """

        osType = "OperatingSystemSection"
        ovfID = "ovf:id"

        if "VirtualSystem" != node.nodeName:
            raise TypeError, "The node can only be appended to a Virtual\
             System Section. The given node is not a Virtual System Section."
        osNode = self.document.createElement(osType)
        self.createInfoChild(osNode, info, infoID)

        if id != None:
            osNode.setAttribute(ovfID, id)

        if description != None:
            self.createDescriptionChild(osNode, description, descriptionID)

        node.appendChild(osNode)
        return osNode

    def createInstallSection(self, node, info, infoID=None, initBoot=None,
                             bootStopDelay=None, id=None):
        """
        This method creates the install section used to describe a virtual system collection.

        @raise TypeError: The cases are as follow
                - I{B{Case 1:}}The node passed in does not have a node name
                of VirtualSystem.
                - I{B{Case 2:}}The parameter initboot does not have a value
                that is of type Boolean.

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param initBoot: Specifies if the virtual machine needs to be initially booted to install
                         and configure software.
        @type initBoot: Boolean

        @param bootStopDelay: Specifies a delay in seconds to wait for the virtual machine to power off.
        @param bootStopDelay: Int

        @param info: The information ,<Info>,comments for the section.
        @type info: String

        @param infoID: The id for the information comment
        @type infoID: String

        @return: DOM node of the install section
        """

        ovfInitBoot = "ovf:initialBoot"
        stopDelay = "ovf:initialBootStopDelay"
        installType = "InstallSection"

        if "VirtualSystem" != node.nodeName:
            raise TypeError, "The node can only be appended to a Virtual\
             System Section. The given node is not a Virtual System Section"

        installNode = self.document.createElement(installType)
        self.createInfoChild(installNode, info, infoID)

        if id != None:
            installNode.setAttribute("ovf:id", id)
        if initBoot != None:
            if initBoot == True:
                installNode.setAttribute(ovfInitBoot,"true")
            elif initBoot == False:
                installNode.setAttribute(ovfInitBoot,"false")
            else:
                raise TypeError, "The parameter for the initboot in the\
                 install section needs to be a Boolean."

        if bootStopDelay != None:
            installNode.setAttribute(stopDelay, bootStopDelay)
        node.appendChild(installNode)
        return installNode

    def createVirtualHardwareSection(self, node, id, info, infoID=None,
                                     transport=None):
        """
        This method creates the VirtualHardwareSection which is required to be present
        for any VirtualSystem. However this section is disallowed in a VirtualSystemCollection.
        Multiple occurrences of this section is allowed.

        @raise TypeError: The error is thrown if the node passed in does not
        have a node name of VirtualSystem.

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param id: Unique identifier within the OVF.
        @type id: String

        @param transport: It specifies how properties are passed to the virtual machine.
        @type transport: String

        @param info: The information ,<Info>,comments for the section.
        @type info: String

        @param infoID: The id for the information comment
        @type infoID: String

        @return: DOM node of the virtual hardware section
        """

        ovfTransport = "ovf:transport"
        ovfHardwareSec = "VirtualHardwareSection"
        ovfID = "ovf:id"

        if "VirtualSystem" != node.nodeName:
            raise TypeError, "The node can only be appended to a Virtual\
             System Section. The given node is not a Virtual System Section."

        hardwareSection = self.document.createElement(ovfHardwareSec)
        self.createInfoChild(hardwareSection, info, infoID)

        if id != None:
            hardwareSection.setAttribute(ovfID, id)

        if transport != None:
            hardwareSection.setAttribute(ovfTransport, transport)

        node.appendChild(hardwareSection)
        return hardwareSection

    def createSystemType(self, node):
        """
        This method will create a System child for the Virtual Hardware Section.

        NOTE::
         This method can throw a TypeError if the node passed in is not of type VirtualHardwareSection.

        @raise TypeError: The error is thrown if the node passed in does not
        have a node name of VirtualHardwareSection.

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @return: DOM node of the system section
        """

        if "VirtualHardwareSection" != node.nodeName:
            raise TypeError, "The node can only be appended to a Virtual\
             Hardware Section. The given node is not a Virtual Hardware\
              Section."
        systemNode = self.document.createElement("System")
        node.appendChild(systemNode)
        return systemNode

    def defineSystemType(self, node, caption, description=None,
                         instanceId=None, virtualSysIdent=None,
                         virtualSysType=None):
        """
        This method is used to create a virtual system type. This is used to uniquely
        identify the family of virtual hardware that is required.

        NOTE::
            This method throws an error if the node passed in is not of type System.

        @raise TypeError: The error is thrown if the node passed in does not
        have a node name of System.

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param virtualSysIdent: Unique identifier for the family of virtual hardware that is required.
        @type virtualSysIdent: String
        """

        if "System" != node.nodeName:
            raise TypeError, "The node can only be appended to a System in a\
             Virtual Hardware Section. The given node is not a System in a\
              Virtual Hardware Section."

        sysList = [("Caption", caption),
                   ("Description", description),
                   ("InstanceId", instanceId),
                   ("VirtualSystemIdentifier", virtualSysIdent),
                   ("VirtualSystemType",virtualSysType)]

        for ent in sysList:
            if ent[0] != None:
                if ent[1] != None:
                    child = self.document.createElement("vssd:" + ent[0])
                    child.appendChild(self.document.createTextNode(ent[1]))
                    node.appendChild(child)

    def createValue(self, node, value, configuration):
        """
        This function will create a value child element for the Property Product Section.
        Note: This element can only be appended to a Property node.

        @raise TypeError: The error is thrown if the node passed in does not
        have a node name of Property.

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param value: Used to provide default values to the property
        @type value: String

        @param configuration: A comma-separated list of configuration names.
        @type  configuration: String.

        """
        if "Property" != node.nodeName:
            raise TypeError, "The node can only be appended to a Property\
             Element. The given node is not a Property Element."

        ovfValue = "ovf:value"
        ovfConfig = "ovf:configuration"
        valNode = self.document.createElement("Value")
        valNode.setAttribute(ovfValue, value)
        valNode.setAttribute(ovfConfig, configuration)

        node.appendChild(valNode)

    def createDescriptionChild(self, node, description, msgID=None):
        """
        This method will create a description that can be appended to any node.

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param description: The description to be entered
        @type description: String

        @param msgID: The id of the given message.
        @type msgID: String
        """
        descriptionElement = self.document.createElement("Description")
        descTextNode = self.document.createTextNode(description)
        descriptionElement.appendChild(descTextNode)
        if msgID != None:
            descriptionElement.setAttribute("ovf:msgid", msgID)

        node.appendChild(descriptionElement)

    def createLabelChild(self, node, label, msgID=None):
        """
        This method will create a label that can be appended to a node.

        @param node: Place where the label child will be inserted.
        @type node: DOM node object

        @param label: The text for the label
        @type label: String

        @param msgID: The id of the given message.
        @type msgID: String
        """
        labelElement = self.document.createElement("Label")
        labelTextNode = self.document.createTextNode(label)
        labelElement.appendChild(labelTextNode)
        if msgID != None:
            labelElement.setAttribute("ovf:msgid", msgID)

        node.appendChild(labelElement)
    def createInfoChild(self, node, infoComments, msgID=None):
        """
        This method will insert an info into a node. This is a helper function.

        NOTE: The document in the class cannot be None.

        @param infoComments: Message that will be contained in the info.
        @type infoComments: String

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param msgID: The id of the given message.
        @type msgID: String
        """
         #info for comments
        infoNode = self.document.createElement("Info")
        if msgID != None:
            infoNode.setAttribute("ovf:msgid", msgID)

        if infoComments == None:
            infoText = "Information not available."
        else:
            infoText = infoComments
        infoTextNode = self.document.createTextNode(infoText)
        infoNode.appendChild(infoTextNode)
        node.appendChild(infoNode)

    def createComment(self, comment, node=None):
        """
        This method is used to create a comment. If the
        node is not passed in as a parametere the comment
        is then added to the envelope (after the last child added).

        Note: The envelope, root node, must have been created.

        @param comment: The text for the comment to be created.
        @type comment: Strings

        @param node: Place where the child will  be inserted.
        @type node: DOM node object


        """
        commentNode = self.document.createComment(comment)
        if node == None:
            self.envelope.appendChild(commentNode)
        else:
            node.appendChild(commentNode)

    def createAnnotationSection(self, annotation, info=None, node=None,
                                msgID=None):
        """
        This method will create an annotation section. By default it will
        append it do the last child of the root element if node is not
        specified.

        Note: The annotation section is a user-defined on an entity

        @raise TypeError: The error is thrown if the node passed in does not
        have a node name of VirtualSystem nor VirtualSystemCollection.

        @param annotation: Actual annotation
        @type annotation: String

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param info: Any notes to describe the annotation
        @type info: String

        @param msgID: The id of the given message.
        @type msgID: String
        """
        if node != None:
            if node != self.envelope:
                if "VirtualSystem" != node.nodeName:
                    if "VirtualSystemCollection" != node.nodeName:
                        raise TypeError, "The node can only be appended to a\
                         Virtual System Section or Virtual System Collection\
                          Section."

        annotationSect = "AnnotationSection"

        if node == None:
            node = self.envelope
        sectionElement = self.document.createElement(annotationSect)

        if info != None:
            #create info
            self.createInfoChild(sectionElement, info)

        annotationElement = self.document.createElement("Annotation")
        annotationTextChild = self.document.createTextNode(annotation)
        annotationElement.appendChild(annotationTextChild)
        sectionElement.appendChild(annotationElement)

        if msgID != None:
            annotationElement.setAttribute("ovf:msgid", msgID)
        node.appendChild(sectionElement)

    def createCaptionChild(self, node, caption):
        """
        This method will create a caption element that can be appended as a child of a
        given node.

        NOTE: Page 23 line 789 the Caption can be inside the Network section but the schemas do not support it.

        @param node: Place where the child will  be inserted.
        @type node: DOM node object

        @param caption: A human readable description
        @type caption: String
        """
        captionElement = self.document.createElement("Caption")
        captionTextNode = self.document.createTextNode(caption)
        captionElement.appendChild(captionTextNode)

        node.appendChild(captionElement)

def getReferencedFilesFromOvf(fileName, path=None):
    """
    Return a list of OvfReferencedFile objects that are referenced
    in the References section of an Ovf file

    @type  fileName: string
    @param fileName: basename.ovf
    @type  path:     string
    @param path:     file path to use as base for path element of objects defaults to
    dirname(fileName)
    @rtype :  list of OvfReferencedFile
    @return: an OvfReferencedFile list object
    """

    if os.path.isfile(fileName):
        document = parse(fileName)#parse the file
        document.normalize()

        if path == None:
            path = fileName

        checksum = None
        checksumStamp = None
        files = []
        mfObj = None
        certObj = None
        temp = []

        for node in document.getElementsByTagName('File'):#this will get the element with the tag: File

            fileID = node.attributes["ovf:id"].value
            fileHref = node.attributes["ovf:href"].value

            filePath = Ovf.href2abspath(fileHref, path)

            #since some of the values are not required we must check that they are present
            if "ovf:size" in node.attributes.keys():
                fileSize = node.attributes["ovf:size"].value
            else:
                fileSize = None

            if "ovf:chunkSize" in node.attributes.keys():
                fileChunkSize = node.attributes["ovf:chunkSize"].value
            else:
                fileChunkSize = None

            if "ovf:compression" in node.attributes.keys():
                fileCompression = node.attributes["ovf:compression"].value
            else:
                fileCompression = None


            if fileHref.endswith(".mf"):
                mfObj = OvfReferencedFile.OvfReferencedFile(filePath,
                                                            fileHref,
                                                            checksum,
                                                            checksumStamp,
                                                            fileSize,
                                                            fileCompression,
                                                            fileID,fileChunkSize)
            elif fileHref.endswith(".cert"):
                certObj = OvfReferencedFile.OvfReferencedFile(filePath,
                                                            fileHref,
                                                            checksum,
                                                            checksumStamp,
                                                            fileSize,
                                                            fileCompression,
                                                            fileID,fileChunkSize)
            else:
                refObj = OvfReferencedFile.OvfReferencedFile(filePath,
                                                            fileHref,
                                                            checksum,
                                                            checksumStamp,
                                                            fileSize,
                                                            fileCompression,
                                                            fileID,fileChunkSize)
                temp.append(refObj)

        if mfObj != None:
            files.append(mfObj)
        if certObj != None:
            files.append(certObj)

        for i in temp:
            files.append(i)
            #if os.path.isfile(fileHref):#check that the files listed in the xml are actually there

        return files

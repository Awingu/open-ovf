# vi: ts=4 expandtab syntax=python
##############################################################################
# Copyright (c) 2008 IBM Corporation
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
# Scott Moser (IBM) - initial implementation
##############################################################################

"""
Module for interfacing to an OVF and XML
"""

import os
import sha
from xml.dom import Node

def rmNode(node):
    """
    This function will remove a node and all of its children.

    NOTE::
        If parentNode is None then it will use self.envelope.

    @param node: The DOM node of the section to be deleted
    @type node: DOM node
    """
    while node.firstChild != None:
        node.removeChild(node.firstChild)

    node.parentNode.removeChild(node)

def rmNodeAttributes(node,attributeList=[],strict=False):
    """
    This function will remove the attributes for a given section.
    Passing False to strict will mean that no errors will be thrown
    if an attribute for the given node is not found.

    @param node: The DOM node of the attribute to be deleted
    @type node: DOM node

    @param strict: This will allow an error to be thrown if an attribute is not
                    present. Default is False, no errors thrown.
    @type strict: Boolean

    @param attributeList: A list of attributes to be deleted.
    @type attributeList: List in the following form:
            attList =['ovf:size','ovf:href']
    """
    section = node

    if section == None:
        raise ValueError, 'Node must be present.'

    if attributeList != []:
        for attribute in attributeList:
            if section.hasAttribute(attribute):
                section.removeAttribute(attribute)
            elif strict:
                raise ValueError, ("The attribute, "+attribute
                                   +", does not exist.")

def getDefaultConfiguration(ovfDoc):
    """
    Returns identifier for the default configuration
    """
    deploySection = getNodes(ovfDoc, 'DeploymentOptions')
    if deploySection != []:
        deployDict = getDict(deploySection[0])
        if deployDict['children'] != []:
            return deployDict['children'][0]['ovf:id']

    return None

def getNodes(ovfNode, tagName, attrList = { }):
    """
    Returns a list of nodes from an OVF whose tagname is tagName 
    and that have attributes matching attrList.

    @param ovfNode: document or element to search
    @type ovfNode: DOM Node

    @param tagName: tag name of a node
    @type tagName: String

    @param attrList: dictionary of attributes that returned list must contain
    @type  attrList: dictionary

    @return: list of nodes
    @rtype: list of DOM nodes
    """
    matches = [ ]
    for element in ovfNode.getElementsByTagName(tagName):
        matches.append(element)
        for key, val in attrList.items():
            if element.getAttribute(key) != val:
                matches.pop()
                break
    return(matches)

def getNodesWithId(ovfNode, tagName, id = None):
    """
    return a list of nodes that have attribute 
        ( ovf:id | ovf:msgid | ovf:diskId ) == id
    if id is 'None', all nodes matching tagName will be returned

    @param ovfNode: document or element to search
    @type ovfNode: DOM Node

    @param tagName: tag name of a node
    @type  tagName: String

    @param id: id
    @type  id: String

    @return: list of nodes
    @rtype: list of DOM nodes
    """
    if(id == None):
        return(getNodes(ovfNode, tagName))
    else:
        t = getNodes(ovfNode,tagName)
        return([ x for x in getNodes(ovfNode,tagName)
                   if x.getAttribute('ovf:id') == id or
                      x.getAttribute('ovf:msgid') == id or
                      x.getAttribute('ovf:diskId') == id
               ])

def getContentEntities(ovfNode, ovfId=None):
    """
    Returns a list of OVF Entities, optionally restricted by id.

    @param ovfNode: OVF document or element
    @type ovfNode: DOM Node

    @param ovfId: VirtualSystem or VirtualSystemCollection id
    @type ovfId: String

    @return: list of entities
    @rtype: list of DOM nodes
    """
    entities = ovfNode.getElementsByTagName('VirtualSystem')
    entities.extend(ovfNode.getElementsByTagName('VirtualSystemCollection'))

    if ovfId == None:
        return entities
    else:
        return [entity for entity in entities
                if entity.getAttribute('ovf:id') == ovfId]

def getDict(ovfSection, configId=None):
    """
    Returns a dictionary, with keys representing the attributes and the
    children, for an ovf section. Optionally, limits to given configuration.
    L{getNodes} can be used to get a list of sections, each of which
    could be passed in for the argument ovfSectionNode.

    @param ovfSection: OVF section
    @type ovfSection: DOM Node

    @param configId: configuration identifier
    @type configId: String

    @return: attributes and data from section
    @rtype: dictionary

    @note: Returned dict keys,
        - name: OVF section tag name
        - node: section DOM Node
        - attr(optional): attributes of section, only valid for some sections
        - children: list of dictionaries for children, contain same basic
                    structure, as they have name, node, and optional attr
                    keys. They may also have a text key for enclosed data
                    and additional keys for their children.

    @todo: modify to handle and OVF DOM Node
    """
    # Setup dictionary for ovf section
    sectDict = dict(node=ovfSection,
                    name=ovfSection.tagName)

    attributes = getOvfAttributes(ovfSection)
    if attributes != None:
        sectDict['attr'] = attributes

    # Fill in dictionary with information from node's children
    if sectDict['node'].hasChildNodes():
        sectDict['children'] = []
        for child in sectDict['node'].childNodes:
            if(child.nodeType == Node.ELEMENT_NODE and
               child.nodeName != 'Info'):

                # Restrict by given configuration
                if(configId == None or
                   isConfiguration(configId)):

                    childDict = dict(node=child,
                                     name=child.tagName)
                    getOvfAttributes(child, childDict)
                    sectDict['children'].append(childDict)

                    # Get info from grandchildren, either text, or
                    # data from offspring.
                    if child.hasChildNodes():
                        data = False
                        for grandchild in child.childNodes:
                            if grandchild.nodeType == Node.ELEMENT_NODE:
                                childDict[grandchild.tagName] = \
                                    grandchild.firstChild.data
                                data = True

                        if not data:
                            # Child has data i.e. AnnotationSection
                            if not childDict.has_key('text'):
                                childDict['text'] = ''
                            childDict['text'] = (childDict['text'] +
                                                 child.firstChild.data)

    return sectDict

def getOvfAttributes(xmlNode, attributes=None):
    """
    Returns a dictionary of the attributes for a DOM node.

    @param xmlNode: ovf element
    @type xmlNode: DOM Node

    @param attributes: attributes dictionary
    @type attributes: dictionary

    @return: new or modified (passed in) attributes dictionary
    @rtype: dictionary
    """
    if xmlNode.hasAttributes():
        if attributes == None:
            attributes = dict()
        for index in range(xmlNode.attributes.length):
            attrName = xmlNode.attributes.item(index).name
            attrValue = xmlNode.attributes.item(index).value
            attributes[attrName] = attrValue

    return attributes

def ovfString(sectDict):
    """
    Return a dictionary returned from L{getDict} as a string.

    @param sectDict: ovf section dictionary, L{getDict}
    @type sectDict: dictionary

    @return: section dictionary as string
    @rtype: String

    @todo: not machine-readable, e.g. escaped quotes
    """
    # list keys to print
    ret = ''
    printList = sectDict.keys()
    printList.remove('node')

    ret += sectDict['name'] + "\n"
    printList.remove('name')

    if sectDict.has_key('attr'):
        for key in sectDict['attr'].keys():
            ret += key + ":= `" + sectDict['attr'][key] + "`\n"

        printList.remove('attr')

    if sectDict.has_key('children'):
        printList.remove('children')
        for child in sectDict['children']:
            ret += ovfString(child) + "\n"

    for key in printList:
        if type(sectDict[key]) == type(dict()):
            ret += ovfString(sectDict[key]) + "\n"
        else:
            ret += key + ":= `" + sectDict[key] + "`\n"

    return ret

def isVirtualSystem(ovfDoc, ovfId):
    """
    Determines if an id corresponds to an Entity node of
    VirtualSystem_Type in an ovf.

    @param ovfDoc: OVF Document
    @type ovfDoc: DOM Document

    @param ovfId: Entity identifier
    @type ovfId: String

    @return: True or False
    @rtype: boolean
    """
    return(getNodes(ovfDoc,'VirtualSystem', { 'ovf:id':ovfId }) != [])

def isVirtualSystemCollection(ovfDoc, ovfId):
    """
    Determines if an id corresponds to an Entity node of
    VirtualSystemCollection_Type in an ovf.

    @param ovfDoc: OVF Document
    @type ovfDoc: DOM Document

    @param ovfId: Entity identifier
    @type ovfId: String

    @return: True or False
    @rtype: boolean
    """
    return(getNodes(ovfDoc,'VirtualSystemCollection',
                    { 'ovf:id':ovfId }) != [])

def isConfiguration(ovfDoc, configId):
    """
    Verifies whether a configuration is defined in the ovf.

    @param ovfDoc: OVF Document
    @type ovfDoc: DOM Document

    @param configId: configuration name
    @type configId: String

    @return: tests if configuration exists
    @rtype: boolean

    @raise ValueError: ConfigId doesn't match any in DeploymentOptions
    @raise NotImplementedError: DeploymentOptions not defined
    """
    deploy = getNodes(ovfDoc, 'DeploymentOptions')
    if deploy != []:
        configList = getDict(deploy[0])['children']
        while configList != []:
            config = configList.pop(0)
            if config['ovf:id'] == configId:
                return True

        return False
    else:
        # may want to throw different error if doesn't exist
        raise NotImplementedError("Ovf.isConfiguration: No configurations found.")

def sha1sumFile(path):
    """
    This will give the sha1sum of a given file in hex.

    if file object is given, it is expected to be at the start of the file
    (no rewind/seek(0) will be performed)

    @param path: path to file or file object
    @type path: String

    @return: sha1sum of filename in hex
    @rtype: String
    """
    if  path.__class__.__name__ != "file":
        fd = open(path, "rb")
    else:
        fd = path

    digested = sha.new()
    while 1:
        buf = fd.read(4096)
        if buf == "":
            break
        digested.update(buf)
    res =  digested.hexdigest()
    if  path.__class__.__name__ != "file":
        fd.close()
    return res

def href2abspath(href, base=None):
    """
    Returns the absolute path when passed an href.

    @param href: an "href" from a .ovf file or elsewhere
    @type href: String

    @param base: search in base directory for file if not absolute path href,
                 if base is a file, will search from dirname(base)
    @type base: String

    @return: absolute path to file (or the href if remote)
    @rtype: String
    """

    cwd = os.getcwd()
    if base == None:
        path = cwd
    else:
        if(os.path.isfile(base)):
            path = os.path.dirname(base)
        else:
            path = base

        # dirname returns "" rather than "." for "filename"
        if path == "":
            path = "."

    if href.startswith("/"):
        filePath = href
    elif os.path.isfile(path + "/" + href):
        filePath = os.path.abspath(path + "/" + href)
    elif os.path.isfile(cwd + "/" + href):
        filePath = os.path.abspath(cwd + "/" + href)
    elif href.find("://") != -1:
        filePath = href
    else: # file doesn't exist as far as we can see
        filePath = None
    return(filePath)

def xmlString(obj, indent="", newline="", encoding='UTF-8'):
    """
    Wrapper function: Returns a String representing the
    DOM object that was passed.

    @param obj: any DOM Node
    @type obj: DOM Object

    @param indent: indentation character
    @type indent: String

    @param newline: newline character
    @type newline: String

    @param encoding: character encoding
    @type encoding: String

    @return: XML document
    @rtype: String
    """
    from StringIO import StringIO

    buf = StringIO()
    xwritexml(obj, buf, indent, indent, newline, encoding)
    return buf.getvalue()

def xwritexml(obj, writer, indent="", addindent="", newl="", encoding=None):
    func = None
    if   obj.nodeType == Node.DOCUMENT_NODE:
        func = document_writexml
    elif obj.nodeType == Node.ELEMENT_NODE :
        func = element_writexml
    elif obj.nodeType == Node.TEXT_NODE    :
        func = text_writexml

    if func != None:
        func(obj, writer, indent, addindent, newl, encoding)
    else:
        obj.writexml(writer, indent, addindent, newl)

def remove_whitespace_nodes(node):
    """
    Removes all whitespace in DOM node.
    http://safari.oreilly.com/0596007973/pythoncook2-CHP-12-SECT-6
    """
    # prepare the list of text nodes to remove (and recurse when needed)
    remove_list = [  ]
    for child in node.childNodes:
        if child.nodeType == Node.TEXT_NODE and not child.data.strip( ):
            # add this text node to the to-be-removed list
            remove_list.append(child)
        elif child.hasChildNodes( ):
            # recurse, it's the simplest way to deal with the subtree
            remove_whitespace_nodes(child)
    # perform the removals
    for node in remove_list:
        node.parentNode.removeChild(node)
        node.unlink( )


## the following is taken and modified /usr/lib/python2.5/xml/dom/minidom.py
## the xwritexml is just a copied writexml function that calls
## the versions copied 'writexml' functions here rather than the
## ones provided by the library.  For nodes other than those needed
## it will call the functions provided by the library
##
## BEGIN COPY / MODIFY from /usr/lib/python2.5/xml/dom/minidom.py

## def _write_data
def _xwrite_data(writer, data):
    "Writes datachars to writer."
    data = data.replace("&", "&amp;").replace("<", "&lt;")
    data = data.replace("\"", "&quot;").replace(">", "&gt;")
    writer.write(data)

## class Element(Node):
## def writexml(self, writer, indent="", addindent="", newl=""):
def element_writexml(self, writer, indent="", addindent="", newl="",
                     encoding=None):
    # indent = current indentation
    # addindent = indentation to add to higher levels
    # newl = newline string
    writer.write(indent + "<" + self.tagName)

    attrs = self._get_attributes()
    a_names = attrs.keys()
    a_names.sort()

    for a_name in a_names:
        writer.write(" %s=\"" % a_name)
        _xwrite_data(writer, attrs[a_name].value)
        writer.write("\"")
    if self.childNodes:
        if(self.childNodes[0].nodeType == Node.TEXT_NODE):
            writer.write(">")
        else:
            writer.write(">%s"%(newl))
        for node in self.childNodes:
            xwritexml(node, writer, indent + addindent, addindent, newl, encoding)
        if(self.childNodes[0].nodeType == Node.TEXT_NODE):
            writer.write("</%s>%s" %(self.tagName, newl))
        else:
            writer.write("%s</%s>%s" % (indent, self.tagName, newl))
    else:
        writer.write("/>%s"%(newl))

## class Document(Node, DocumentLS):
## def writexml(self, writer, indent="", addindent="", newl="",
def document_writexml(self, writer, indent="", addindent="", newl="",
                      encoding=None):
    if encoding is None:
        writer.write('<?xml version="1.0" ?>'+newl)
    else:
        writer.write('<?xml version="1.0" encoding="%s"?>%s' % (encoding, newl))
    for node in self.childNodes:
        xwritexml(node, writer, indent, addindent, newl)


## class Text(CharacterData):
## def writexml(self, writer, indent="", addindent="", newl=""):
def text_writexml(self, writer, indent="", addindent="", newl="", encoding=None):
    _xwrite_data(writer, self.data)

## END COPY / MODIFY from /usr/lib/python2.5/xml/dom/minidom.py

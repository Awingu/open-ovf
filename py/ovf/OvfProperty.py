# vi: ts=4 expandtab syntax=python
##############################################################################
# Copyright (c) 2008 IBM Corporation
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
# Dave Leskovec (IBM) - Initial implementation
##############################################################################
"""
This file defines some functions to handle property information from
product sections in an ovf file.
"""

from xml.dom import Node
import Ovf

def getPropertyDefaultValue(propertyNode, configuration):
    """
    Get the default value for a given Property node.  The value returned is
    based on this priority:
    1) value node for given configuration
    2) ovf:value attribute
    3) first Value node
    @type propertyNode: DOM node
    @param propertyNode: Property node
    @type configuration: String
    @param configuration: Configuration used to select the default value

    @rtype: String
    @return: Default value for node.  May be empty string.  None if no default
             was specified
    """
    if not configuration:
        docNode = propertyNode.parentNode
        while docNode.nodeType != Node.DOCUMENT_NODE:
            docNode = docNode.parentNode
            if not docNode:
                raise RuntimeError, "Unable to find document node"

        configuration = Ovf.getDefaultConfiguration(docNode)

    if configuration:
        valueNodes = Ovf.getChildNodes(propertyNode,
                                       (Ovf.hasTagName, 'Value'),
                                       (Ovf.hasAttribute, 'ovf:configuration',
                                        configuration))
        if valueNodes:
            attributes = Ovf.getAttributes(valueNodes[0])
            if attributes.has_key('ovf:value'):
                return attributes['ovf:value']

    attributes = Ovf.getAttributes(propertyNode)
    if attributes.has_key('ovf:value'):
        return attributes['ovf:value']

    valueNodes = Ovf.getChildNodes(propertyNode, (Ovf.hasTagName, 'Value'))
    if valueNodes:
        attributes = Ovf.getAttributes(valueNodes[0])
        if attributes.has_key('ovf:value'):
            return attributes['ovf:value']

    return None

def getPropertiesForNode(node, configuration):
    """
    Generate an array of tuples containing the environment information
    for a single node (vs or vsc)
    @type node: DOM node
    @param node: virtual system or collection DOM node
    @type configuration: String
    @param configuration: Configuration being used.  Can be None

    @rtype: array
    @return: array of [(key, property node, value)]
    """
    # Start by getting all product sections for this node
    productSections = Ovf.getChildNodes(node, (Ovf.hasTagName,
                                               'ProductSection'))
    retArray = []

    # it's valid for there to be 0 product sections
    if productSections != []:
        for prodNode in productSections:
            prodClass = prodNode.getAttribute('ovf:class')
            if prodClass != '':
                prodClass += '.'
            prodInstance = prodNode.getAttribute('ovf:instance')
            if prodInstance != '':
                prodInstance = '.' + prodInstance

            properties = Ovf.getChildNodes(prodNode,
                                           (Ovf.hasTagName, 'Property'))

            if properties == []:
                continue

            for propertyNode in properties:
                attributes = Ovf.getAttributes(propertyNode)
                if not attributes.has_key('ovf:key'):
                    raise RuntimeError, 'Node missing required attribute ' +\
                                        'ovf:key'

                propKey = prodClass + attributes['ovf:key'] + prodInstance
                retArray.append((propKey, propertyNode,
                                getPropertyDefaultValue(propertyNode,\
                                                        configuration)))

    return retArray


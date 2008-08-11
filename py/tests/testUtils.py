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

import xml.dom.minidom
from copy import deepcopy

def remove_whitespace_nodes(node,stripTextContent=False):
    """
    Removes all whitespace in DOM node.
    http://safari.oreilly.com/0596007973/pythoncook2-CHP-12-SECT-6
    """
    # prepare the list of text nodes to remove (and recurse when needed)
    remove_list = [  ]
    for child in node.childNodes:
        if child.nodeType == xml.dom.Node.TEXT_NODE:
            child.data=child.data.strip()
        if child.nodeType == xml.dom.Node.TEXT_NODE and not child.data.strip( ):
            # add this text node to the to-be-removed list
            remove_list.append(child)
        elif child.hasChildNodes( ):
            # recurse, it's the simplest way to deal with the subtree
            remove_whitespace_nodes(child)
    # perform the removals
    for node in remove_list:
        node.parentNode.removeChild(node)
        node.unlink( )

def compare_dom(dom1,dom2,stripTextContent=False):
    x=deepcopy(dom1)
    y=deepcopy(dom2)
    remove_whitespace_nodes(x,stripTextContent)
    remove_whitespace_nodes(y,stripTextContent)
    if(x.toxml()==y.toxml()):
        return(True)
    return(False)

# vi: ts=4 expandtab syntax=python
##############################################################################
# Copyright (c) 2008 IBM Corporation
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
# Dave Leskovec (IBM) - initial implementation
##############################################################################
"""
This module contains functions dealing with platform information.
"""

import OvfLibvirt
from locale import getlocale, getdefaultlocale
from time import timezone

def virtTypeIsAvailable(virtType):
    """
    Check if the given virt type is available on this system
    @type node: String
    @param node: Platform type to check

    @rtype: Boolean
    @return: Indication if type is available or not
    """
    if virtType:
        return True

    return False

def getVsSystemType(vs):
    """
    This function gets the list of system types for the virtual system and
    selects one based on the libvirt capabilities.  It will select the
    first type in the list that is present on the system.
    @type node: DOM node
    @param node: Virtual System node

    @rtype: String
    @return: Platform type for Virtual System
    """
    virtTypes = OvfLibvirt.getOvfSystemType(vs)

    for virtType in virtTypes:
        # check if this virtType is available
        if virtTypeIsAvailable(virtType):
            return virtType

    return None

def getPlatformDict(vs, virtPlatform=None):
    """
    Get the platform information
    @type node: DOM node
    @param node: Virtual System node
    @type virtPlatform: String
    @param node: Virtual Platform type.  If None, will be taken from vs

    @rtype: String
    @return: Dictionary containing platform information for the virtual
             system the contents are defined by the ovf specification for
             the environment.
    """
    retDict = {}

    if not virtPlatform:
        virtPlatform = getVsSystemType(vs)

    retDict['Kind'] = virtPlatform
    # We could possibly look up the version and vendor here

    # gather the details of the platform
    (langCode, encoding) = getlocale()
    if langCode == None:
        (langCode, encoding) = getdefaultlocale()
    retDict['Locale'] = langCode

    retDict['Timezone'] = timezone

    return retDict

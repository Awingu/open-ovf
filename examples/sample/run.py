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

import sys

import libvirt

from ovf import OvfLibvirtDomain
from ovf import Ovf

"""
OvfLibvirtDomain

@todo: needs to be updated to demonstrate new code
"""

def buildLibvirtXML(ovfFilePath):
    """Sample build of libvirt XML DOM using OvfLibvirtDomain.py"""

    #metadata
    nameSection = OvfLibvirtDomain.nameElement(ovfFilePath)
    
    #resources
    memorySection = OvfLibvirtDomain.memoryElement(ovfFilePath)
    vcpuSection = OvfLibvirtDomain.vcpuElement(ovfFilePath)
    
    #boot
    bootSection = OvfLibvirtDomain.bootElement('hvm', 'i686', 'pc', 
                                               None, 'hd', 'cdrom')
    
    #time
    timeSection = OvfLibvirtDomain.clockElement('utc')
    
    #features
    featureSection = OvfLibvirtDomain.featuresElement(acpi=True)
    
    #life cycle
    onPowerOffSection = OvfLibvirtDomain.onPowerOffElement('destroy')
    onRebootSection = OvfLibvirtDomain.onRebootElement('restart')
    onCrashSection = OvfLibvirtDomain.onCrashElement('destroy')
    
    #devices
    deviceSection = OvfLibvirtDomain.devicesElement(ovfFilePath)
    
    #network
    networkSection = OvfLibvirtDomain.networkElement('bridge', 'br1')
    deviceSection = OvfLibvirtDomain.addDevice(deviceSection, 
                                               networkSection)
    
    #devices - graphics
    graphicsSection = OvfLibvirtDomain.graphicsElement('vnc', 
                                                       '127.0.0.1', 
                                                       '5911')
    
    deviceSection = OvfLibvirtDomain.addDevice(deviceSection, 
                                               graphicsSection)
    
    #domain
    domainSection = OvfLibvirtDomain.domainElement('xen')
    
    #document
    document = OvfLibvirtDomain.libvirtDocument(domainSection, 
                                                nameSection, 
                                                memorySection, 
                                                vcpuSection,
                                                timeSection,
                                                featureSection, 
                                                onPowerOffSection,
                                                onRebootSection, 
                                                onCrashSection,
                                                deviceSection)

    return document


def getConnect():
    """open a libvirt connection"""
    return libvirt.open('qemu:///system')
    
def getDom(connect, xmlDesc):    
    """Define a libvirt domain based on xml description"""
    return connect.createLinux(xmlDesc, 0)


if __name__ == "__main__":
    #create domain xml
    if(len(sys.argv) == 2):
        #sys.argv[1]: works with py/tests/test_files/ourOVF.ovf
        domainDom = buildLibvirtXML(sys.argv[1])

        domainStr = Ovf.xmlString(domainDom)
        
        conn = getConnect()
        dom0 = getDom(conn, domainStr)
        
    else:
        print "Usage: " + sys.argv[0] + \
              " <ovf source path> <boot device source path>"
        print "  example: " + sys.argv[0] + \
              " /path/to/file.ovf /path/to/file.iso "
        sys.exit(2)

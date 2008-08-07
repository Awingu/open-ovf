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

import libvirt

from ovf import OvfSet

if __name__ == "__main__":
    # Open libvirt connection
    conn = libvirt.open('qemu:///system')
    
    # Instantiate OvfSet instance for httpd.ovf
    ovf = OvfSet.OvfSet('httpd.ovf')
    
    # Boot Virtual Machines
    ovf.boot(conn)

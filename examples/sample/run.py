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

from optparse import OptionParser

import libvirt

from ovf import OvfSet

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                  help="path to OVF file", metavar="FILE PATH")
    parser.add_option("-c", "--connect", dest="connect",
                  help="libvirt connection URI", metavar="URI")

    (options, args) = parser.parse_args()

    if options.connect != None:
        # Open libvirt connection
        conn = libvirt.open(options.connect)

        if options.filename != None:
            # Instantiate OvfSet instance for httpd.ovf
            ovf = OvfSet.OvfSet(options.filename)

            # Boot Virtual Machines
            ovf.boot(conn)


    # Otherwise, just print help/usage message
    
        else:
            parser.print_help()
    else:
        parser.print_help()

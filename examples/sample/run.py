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
import commands
import os

OVA = "../../py/scripts/ova"
OVF = "auxiliary/ubuntu-hardy/httpd.ovf"

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-c", "--connect", dest="connect",
                  help="libvirt connection URI", metavar="URI")

    (options, args) = parser.parse_args()

    OVA_PATH = os.path.join(os.path.dirname(__file__) + "/" + OVA)
    OVF_PATH = os.path.join(os.path.dirname(__file__) + "/" + OVF)

    if options.connect != None:
        CMD = (OVA_PATH + " --runtime" +
               " -f " + OVF_PATH +
               " -c " + str(options.connect))
        print CMD
        ret = commands.getstatusoutput(CMD)
        if ret[0] != 0:
            print ret[1]
    else:
        parser.print_help()

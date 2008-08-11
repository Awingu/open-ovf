# vi: ts=4 expandtab syntax=python
##############################################################################
# Copyright (c) 2008 IBM Corporation
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
# Murillo Fernandes Bernardes (IBM) - initial implementation
##############################################################################
"""Common commands constants"""

from ovf.OvfFile import OVF_VERSION

VERSION = '0.1'

#
VERSION_STR = """%(prog)s (Open-OVF) %(version)s
OVF version: %(ovf_version)s
""" % {
        'prog': '%prog',
        'version': VERSION,
        'ovf_version': OVF_VERSION
      }

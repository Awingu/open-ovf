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
# Dave Leskovec (IBM) - initial implementation
##############################################################################
"""
Test case for functions in OvfProperty.py
"""

import unittest, os

from ovf import Ovf
from ovf.OvfFile import OvfFile
from ovf import OvfProperty

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files/")

class OvfPropertyTestCase(unittest.TestCase):
    """
    Test OvfProperty functions
    """

    path = TEST_FILES_DIR

    ovf = 'someOVF.ovf'


    def test_getPropertyDefaultValue(self):
        """
        Test OvfProperty.getPropertyDefaultValue
        """
        ovfFileName = self.path+"/"+self.ovf
        ovfFile = OvfFile(ovfFileName)
        # Get all property nodes in the ovf
        propertyNodes = Ovf.getNodes(ovfFile.envelope,
                                     (Ovf.hasTagName, 'Property'))

        # The first (hostname) property is the one we want to test with
        testNode = propertyNodes[0]
        # Test no default specified
        value = OvfProperty.getPropertyDefaultValue(testNode, None)
        assert value == None, "failed no default test"

        # The seventh (httpPort) property is the one we want to test with
        testNode = propertyNodes[6]
        # Test default specified as attribute
        value = OvfProperty.getPropertyDefaultValue(testNode, None)
        assert value == '80', "failed attribute test"

        # The ninth (startThreads) property is the one we want to test with
        testNode = propertyNodes[8]
        # Test default specified as default configuration
        value = OvfProperty.getPropertyDefaultValue(testNode, None)
        assert value == '50', "failed attribute test"

        # Using the same property node
        # Test default specified for given configuration
        value = OvfProperty.getPropertyDefaultValue(testNode, 'Minimal')
        assert value == '10', "failed config test"


    def test_getPropertiesForNode(self):
        """
        Test OvfProperty.getPropertiesForNode
        """

        propertiesNoConfig = [('org.linuxdistx.hostname', None),
                             ('org.linuxdistx.ip', None),
                             ('org.linuxdistx.subnet', None),
                             ('org.linuxdistx.gateway', None),
                             ('org.linuxdistx.dns', None),
                             ('org.linuxdistx.netCoreRmemMaxMB', None),
                             ('org.apache.httpd.httpPort', '80'),
                             ('org.apache.httpd.httpsPort', '443'),
                             ('org.apache.httpd.startThreads', '50'),
                             ('org.apache.httpd.minSpareThreads', '15'),
                             ('org.apache.httpd.maxSpareThreads', '30'),
                             ('org.apache.httpd.maxClients', '256'),
                             ('org.mysql.db.queryCacheSizeMB', '32'),
                             ('org.mysql.db.maxConnections', '500'),
                             ('org.mysql.db.waitTimeout', '100'),
                             ('org.mysql.db.waitTimeout', '100'),
                             ('net.php.sessionTimeout', '5'),
                             ('net.php.concurrentSessions', '500'),
                             ('net.php.memoryLimit', '32')]
        propertiesMinConfig = [('org.linuxdistx.hostname', None),
                               ('org.linuxdistx.ip', None),
                               ('org.linuxdistx.subnet', None),
                               ('org.linuxdistx.gateway', None),
                               ('org.linuxdistx.dns', None),
                               ('org.linuxdistx.netCoreRmemMaxMB', None),
                               ('org.apache.httpd.httpPort', '80'),
                               ('org.apache.httpd.httpsPort', '443'),
                               ('org.apache.httpd.startThreads', '10'),
                               ('org.apache.httpd.minSpareThreads', '5'),
                               ('org.apache.httpd.maxSpareThreads', '15'),
                               ('org.apache.httpd.maxClients', '128'),
                               ('org.mysql.db.queryCacheSizeMB', '32'),
                               ('org.mysql.db.maxConnections', '500'),
                               ('org.mysql.db.waitTimeout', '100'),
                               ('org.mysql.db.waitTimeout', '100'),
                               ('net.php.sessionTimeout', '5'),
                               ('net.php.concurrentSessions', '500'),
                               ('net.php.memoryLimit', '32')]
        propertiesMaxConfig = [('org.linuxdistx.hostname', None),
                               ('org.linuxdistx.ip', None),
                               ('org.linuxdistx.subnet', None),
                               ('org.linuxdistx.gateway', None),
                               ('org.linuxdistx.dns', None),
                               ('org.linuxdistx.netCoreRmemMaxMB', None),
                               ('org.apache.httpd.httpPort', '80'),
                               ('org.apache.httpd.httpsPort', '443'),
                               ('org.apache.httpd.startThreads', '100'),
                               ('org.apache.httpd.minSpareThreads', '25'),
                               ('org.apache.httpd.maxSpareThreads', '45'),
                               ('org.apache.httpd.maxClients', '512'),
                               ('org.mysql.db.queryCacheSizeMB', '32'),
                               ('org.mysql.db.maxConnections', '500'),
                               ('org.mysql.db.waitTimeout', '100'),
                               ('org.mysql.db.waitTimeout', '100'),
                               ('net.php.sessionTimeout', '5'),
                               ('net.php.concurrentSessions', '500'),
                               ('net.php.memoryLimit', '32')]

        ovfFileName = self.path + "/" + self.ovf
        ovfFile = OvfFile(ovfFileName)

        # Get the virtual system from the ovf
        vsNodes = Ovf.getNodes(ovfFile.envelope,
                               (Ovf.hasTagName, 'VirtualSystem'),
                               (Ovf.hasAttribute, 'ovf:id', 'MyLampService'))
        vsNode = vsNodes[0]

        # Get the environment for the node
        properties = OvfProperty.getPropertiesForNode(vsNode, None)
        # validate the returned data
        propOffset = 0
        for (key, node, value) in properties:
            assert key == propertiesNoConfig[propOffset][0], "key mismatch"
            assert node != None, "failed with invalid property node"
            assert value == propertiesNoConfig[propOffset][1], "value mismatch"
            propOffset = propOffset + 1

        # Get the environment for the node with configuration
        properties = OvfProperty.getPropertiesForNode(vsNode, 'Minimal')
        # validate the returned data
        propOffset = 0
        for (key, node, value) in properties:
            assert key == propertiesMinConfig[propOffset][0], "key mismatch"
            assert value == propertiesMinConfig[propOffset][1], "value mismatch"
            propOffset = propOffset + 1

        # Get the environment for the node with configuration
        properties = OvfProperty.getPropertiesForNode(vsNode, 'Maximum')
        # validate the returned data
        propOffset = 0
        for (key, node, value) in properties:
            assert key == propertiesMaxConfig[propOffset][0], "key mismatch"
            assert value == propertiesMaxConfig[propOffset][1], "value mismatch"
            propOffset = propOffset + 1

if __name__ == "__main__":
    TEST = unittest.TestLoader().loadTestsFromTestCase(OvfPropertyTestCase)
    RUNNER = unittest.TextTestRunner(verbosity=2)
    RUNNER.run(unittest.TestSuite(TEST))

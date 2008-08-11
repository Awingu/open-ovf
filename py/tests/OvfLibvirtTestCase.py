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
import os
import unittest
from xml.dom.minidom import Document

from ovf import OvfLibvirt
from ovf import Ovf

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files/")

class OvfLibvirtTestCase(unittest.TestCase):
    def setUp(self):
        """Setup"""
        self.docTag = '<?xml version="1.0" encoding="UTF-8"?>'
        self.testDocument = Document()

    def tearDown(self):
        """tearDown"""
        self.testDocument = None

    def test_libvirtDocument(self):
        """Testing OvfLibvirt.libvirtDocument"""
        domain = self.testDocument.createElement('domain')
        domain.setAttribute('type', 'xen')

        elem = self.testDocument.createElement('name')
        elem.appendChild(self.testDocument.createTextNode('test'))
        domain.appendChild(elem)

        # no sections
        testDoc = OvfLibvirt.libvirtDocument(domain)
        testStr = self.docTag + '<domain type="xen"><name>test</name></domain>'
        self.assertEqual(Ovf.xmlString(testDoc), testStr)

        # new section
        clockSection = self.testDocument.createElement('clock')
        clockSection.setAttribute('sync','utc')

        testDoc = OvfLibvirt.libvirtDocument(domain, clockSection)
        testStr = self.docTag + '<domain type="xen"><name>test</name>' + \
                  '<clock sync="utc"/></domain>'
        self.assertEqual(Ovf.xmlString(testDoc), testStr)

        # replace section
        domain.appendChild(clockSection)
        newClockSection = self.testDocument.createElement('clock')
        newClockSection.setAttribute('sync','localtime')

        testDoc = OvfLibvirt.libvirtDocument(domain, newClockSection)
        testStr = self.docTag + '<domain type="xen"><name>test</name>' + \
                  '<clock sync="localtime"/></domain>'
        self.assertEqual(Ovf.xmlString(testDoc), testStr)

        # multiple sections (new and old)
        newNameSection = self.testDocument.createElement('name')
        nameNode = self.testDocument.createTextNode('test_completed')
        newNameSection.appendChild(nameNode)

        testDoc = OvfLibvirt.libvirtDocument(domain, newNameSection,
                                                   newClockSection)
        testStr = self.docTag + '<domain type="xen">' + \
                  '<name>test_completed</name>' + \
                  '<clock sync="localtime"/></domain>'
        self.assertEqual(Ovf.xmlString(testDoc), testStr)

    def test_domainElement(self):
        """Testing OvfLibvirt.domainElement"""
        testElem = OvfLibvirt.domainElement('kqemu')
        self.assertEqual(Ovf.xmlString(testElem),
                         '<domain type="kqemu"/>')

    def test_nameElement(self):
        """Testing OvfLibvirt.nameElement"""
        self.assertEqual(Ovf.xmlString(OvfLibvirt.nameElement('test')),
                         '<name>test</name>')

    def test_uuidElement(self):
        """Testing OvfLibvirt.uuidElement"""
        testStr = '4dea22b31d52d8f32516782e98ab3fa0'
        self.assertEqual(Ovf.xmlString(OvfLibvirt.uuidElement(testStr)),
                         '<uuid>' + testStr + '</uuid>')

    def test_bootElement(self):
        """Testing OvfLibvirt.bootElement

        @todo: add more test cases for code coverage
        """
        # Test TypeError
        testErrorList = [dict(),
                         dict(bootloader='/usr/bin/pygrub',
                              devices=['cdrom']),
                         dict(bootloader='/usr/bin/pygrub',
                              kernel='/root/f8-i386-vmlinuz'),
                         dict(devices=['cdrom'],
                              kernel='/root/f8-i386-vmlinuz'),
                         dict(bootloader='/usr/bin/pygrub',
                              kernel='/root/f8-i386-vmlinuz',
                              devices=['cdrom'])
                         ]
        for test in testErrorList:
            self.assertRaises(TypeError, OvfLibvirt.bootElement, test)

        # bootloader

        # bios

        # kernel

#        boot.setAttribute('dev','cdrom')
#        self.assertEqual(Ovf.xmlString(createBIOSBootElem('hvm', 'i686', 'pc', '/usr/lib/xen/boot/hvmloader', boot)),
#                         '<os><type arch=\"i686\" machine=\"pc\">hvm</type><loader>/usr/lib/xen/boot/hvmloader</loader><boot dev=\"cdrom\"/></os>')
#
#        self.assertEqual(Ovf.xmlString(createBootloaderBootElem('/path/to/bootloader')),
#                         '<bootloader>/path/to/bootloader</bootloader>')
#        self.assertEqual(Ovf.xmlString(createBootloaderArgsBootElem('--append single')),
#                         '<bootloader_args>--append single</bootloader_args>')

    def test_memoryElement(self):
        """Testing OvfLibvirt.memoryElement"""
        self.assertEqual(Ovf.xmlString(OvfLibvirt.memoryElement('262144')),
                         '<memory>262144</memory>')

    def test_currentMemoryElement(self):
        """Testing OvfLibvirt.currentMemoryElement"""
        self.assertEqual(Ovf.xmlString(OvfLibvirt.currentMemoryElement('262144')),
                         '<currentMemory>262144</currentMemory>')

    def test_vcpuElement(self):
        """Testing OvfLibvirt.vcpuElement"""
        self.assertEqual(Ovf.xmlString(OvfLibvirt.vcpuElement('1')),
                         '<vcpu>1</vcpu>')

    def test_onPowerOffElement(self):
        """Testing OvfLibvirt.onPowerOffElement"""
        self.assertEqual(Ovf.xmlString(OvfLibvirt.onPowerOffElement('destroy')),
                         '<on_poweroff>destroy</on_poweroff>')

    def test_onRebootElement(self):
        """Testing OvfLibvirt.onRebootElement"""
        self.assertEqual(Ovf.xmlString(OvfLibvirt.onRebootElement('restart')),
                         '<on_reboot>restart</on_reboot>')

    def test_onCrashElement(self):
        """Testing OvfLibvirt.onCrashElement"""
        self.assertEqual(Ovf.xmlString(OvfLibvirt.onCrashElement('restart')),
                         '<on_crash>restart</on_crash>')

    def test_featuresElement(self):
        """Testing OvfLibvirt.featuresElement"""
        self.assertEqual(Ovf.xmlString(OvfLibvirt.featuresElement(True, True, True, True)),
                         '<features><pae/><nonpae/><acpi/><apic/></features>')
        self.assertEqual(Ovf.xmlString(OvfLibvirt.featuresElement(pae=True)),
                         '<features><pae/></features>')
        self.assertEqual(Ovf.xmlString(OvfLibvirt.featuresElement(nonpae=True)),
                         '<features><nonpae/></features>')
        self.assertEqual(Ovf.xmlString(OvfLibvirt.featuresElement(acpi=True)),
                         '<features><acpi/></features>')
        self.assertEqual(Ovf.xmlString(OvfLibvirt.featuresElement(apic=True)),
                         '<features><apic/></features>')

    def test_clockElement(self):
        """Testing OvfLibvirt.clockElement"""
        self.assertEqual(Ovf.xmlString(OvfLibvirt.clockElement('localtime')),
                         '<clock sync="localtime"/>')

    def test_devicesElement(self):
        """Testing OvfLibvirt.devicesElement"""
        #self.assertEqual(Ovf.xmlString(OvfLibvirt.devicesElement()),
        #                 '<devices/>')
        elem1 = self.testDocument.createElement('emulator')
        node1 = self.testDocument.createTextNode('/usr/bin/qemu')
        elem1.appendChild(node1)

        elem2 = self.testDocument.createElement('graphics')
        elem2.setAttribute('type','sdl')
        #self.assertEqual(Ovf.xmlString(OvfLibvirt.devicesElement(elem1,elem2)),
        #                 '<devices><emulator>/usr/bin/qemu</emulator><graphics type="sdl"/></devices>')

    def test_emulatorElement(self):
        """Testing OvfLibvirt.emulatorElement"""
        testElem = OvfLibvirt.emulatorElement('/usr/bin/qemu')
        self.assertEqual(Ovf.xmlString(testElem),
                         '<emulator>/usr/bin/qemu</emulator>')

    def test_diskElement(self):
        """Testing OvfLibvirt.diskElement"""
        #TODO: test method with None values
        #self.assertEqual(Ovf.xmlString(OvfLibvirt.diskElement('file', 'disk', '/path/to/disk.img', 'ide', 'hda', True, 'tap', 'aio')),
        #                 '<disk device="disk" type="file"><source file="/path/to/disk.img"/>' +
        #                 '<target bus="ide" dev="hda"/><driver name="tap" type="aio"/><readonly/></disk>')

    def test_networkElement(self):
        """Testing OvfLibvirt.networkElement"""
        #TODO: Define tests
        self.assertTrue

    def test_inputElement(self):
        """Testing OvfLibvirt.inputElement"""
        self.assertEqual(Ovf.xmlString(OvfLibvirt.inputElement('mouse', 'usb')),
                         '<input bus="usb" type="mouse"/>')
        self.assertEqual(Ovf.xmlString(OvfLibvirt.inputElement('tablet')),
                         '<input type="tablet"/>')

    def test_graphicsElement(self):
        """Testing OvfLibvirt.graphicsElement"""
        self.assertEqual(Ovf.xmlString(OvfLibvirt.graphicsElement('vnc', '192.168.1.1', '6522')),
                         '<graphics listen="192.168.1.1" port="6522" type="vnc"/>')
        self.assertEqual(Ovf.xmlString(OvfLibvirt.graphicsElement('sdl')),
                         '<graphics type="sdl"/>')

    def test_addDevice(self):
        """Testing OvfLibvirt.addDevice"""


if __name__ == "__main__":
    libvirtSuite = unittest.TestLoader().loadTestsFromTestCase(OvfLibvirtTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(unittest.TestSuite(libvirtSuite))

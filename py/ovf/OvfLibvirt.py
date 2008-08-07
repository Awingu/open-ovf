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
"""OvfLibvirt"""

from xml.dom.minidom import Document
import sched
import time

import Ovf

def libvirtDocument(domain, *sections):
    """
    Creates a libvirt XML Document when passed the L{domain element
    <domainElement>}. Additional section arguments modify the L{domain element
    <domainElement>} to include children. The XML DOM can be used to add them 
    manually.
    
    L{Domain<domainElement>}:
    =======

    Sections:
        - L{Name<nameElement>}
        - L{uuid<uuidElement>}

        - L{<Memory<memoryElement>}
        - L{Current Memory<currentMemoryElement>}
        - L{Vcpu<vcpuElement>}

        - L{"Boot"<bootElement>}
        
        - L{On Poweroff<onPowerOffElement>}
        - L{On Reboot<onRebootElement>}
        - L{On Crash<onCrashElement>}
        
        - L{Features<featuresElement>}
        
        - L{Clock<clockElement>}
        
        - L{Devices<devicesElement>}
    
    @param domain: L{Domain Element<domainElement>}
    @type domain: DOM Element
    
    @param sections: sequence of Libvirt sections
    @type sections: variable length DOM Element tuple
        
    @return: XML DOM Document
    @rtype: DOM Document
    """
    document = Document()
    for section in sections:
        old = domain.getElementsByTagName(section.tagName)
        if old == []:
            domain.appendChild(section)
        else:
            domain.replaceChild(section, old[0])
    document.appendChild(domain)
    return document

def domainElement(domainType):
    """
    Creates a <domain> element in a L{libvirt document<libvirtDocument>}
    when passed the hypervisor type.

    @param domainType: hypervisor type
    @type domainType: String

    @return: <domain> Element 
    @rtype: DOM Element
    """
    domain = Document().createElement('domain')
    domain.setAttribute('type', domainType)
    return domain

def nameElement(name):
    """
    Creates a libvirt <name> element, a child of L{domain element
    <domainElement>}, representing the name of the Virtual Machine.

    @param name: a short (alphanumeric) name for the virtual machine    
    @type name: String

    @return: <name> Element
    @rtype: DOM Element
    """
    document = Document()
    elem = document.createElement('name')
    elem.appendChild(document.createTextNode(name))
    return elem
    
def uuidElement(uuid):
    """
    Creates a libvirt <uuid> element, a child of L{domain element
    <domainElement>}, representing a unique global identifier for the 
    virtual machine. The format must be RFC 4122 compliant.
    
    e.g. 3e3fce45-4f53-4fa7-bb32-11f34168b82b

    @param uuid: a globally unique identifier, RFC 4122 compliant
    @type uuid: String

    @return: <uuid> element
    @rtype: DOM Element
    """
    document = Document()
    elem = document.createElement('uuid')
    elem.appendChild(document.createTextNode(uuid))
    return elem

def memoryElement(quantity):
    """
    Creates a <memory> element, a child of L{domain element<domainElement>}, 
    that specifies the maximum allocation of memory at boot time. 

    @param quantity: maximum allocation of memory at boot time
    @type quantity: String

    @return: <memory> element
    @rtype: DOM Element
    """
    document = Document()
    elem = document.createElement('memory')
    elem.appendChild(document.createTextNode(quantity))
    return elem
    
def currentMemoryElement(quantity):
    """
    Creates a <currentMemory> element, a child of L{domain element
    <domainElement>}, that specifies the current allocation of memory. 

    @param quantity: current allocation of memory for guest
    @type quantity: String

    @return: <currentMemory> element
    @rtype: DOM Element
    """
    document = Document()
    elem = document.createElement('currentMemory')
    elem.appendChild(document.createTextNode(quantity))
    return elem
    
def vcpuElement(quantity):
    """
    Creates a <vcpu> element, a child of L{domain element<domainElement>}, 
    that specifies the number of CPUs allocated. 

    @param quantity: number of virtual CPUs allocated
    @type quantity: String

    @return: <vcpu> element
    @rtype: DOM Element
    """
    document = Document()
    elem = document.createElement('vcpu')
    elem.appendChild(document.createTextNode(quantity))
    return elem

def bootElement(bootDict):
    """
    Creates a libvirt <os> element, a child of L{domain element
    <domainElement>}, that describes the operating system boot protocol for 
    the Virtual Machine, specifically values to enable booting from the BIOS.
    
    @param bootDict: dictionary of boot arguments
    @type bootDict: dictionary
    
    @note: bootDict has specific key values for boot type:
    
    bootloader:
        - bootloader: path to bootloader
        - bootloader_args(optional): arguments to bootloader
    
    bios:
        - arch(optional): VM CPU architecture, e.g. i686
        - devices: ordered boot device list: cdrom, hd, fd, or network
        - loader(optional): path to Xen loader
        - machine(optional): VM type, e.g. pc
        - type: hvm or linux
    
    kernel:
        - arch(optional): VM CPU architecture, e.g. i686
        - cmdline(optional): arguments to kernel
        - initrd(optional): path to optional ramdisk image
        - kernel: path to kernel image
        - loader(optional): path to Xen loader
        - machine(optional): VM type, e.g. pc
        - type: hvm or linux
    
    @return: DOM element list
    @rtype: list
    """
    document = Document()
    bootList = []
    
    # Bootloader
    if bootDict.has_key('bootloader'):
        if(bootDict.has_key('devices') | bootDict.has_key('kernel')):
            raise TypeError
        else:
            bootloader = document.createElement('bootloader')
            bootloaderText = document.createTextNode(bootDict['bootloader'])
            bootloader.appendChild(bootloaderText)
            bootList.append(bootloader)
            
            if bootDict.has_key('arguments'):
                arguments = document.createElement('bootloader_args')
                argumentsText = \
                    document.createTextNode(bootDict['bootloader_args'])
                arguments.appendChild(argumentsText)
                bootList.append(arguments)
    elif(bootDict.has_key('devices') ^
         bootDict.has_key('kernel')):
        os = document.createElement('os')
            
        bootType = document.createElement('type')
        if bootDict.has_key('arch'):
            bootType.setAttribute('arch', bootDict['arch'])
        if bootDict.has_key('machine'):
            bootType.setAttribute('machine', bootDict['machine'])
        bootType.appendChild(document.createTextNode(bootDict['type']))
        os.appendChild(bootType)
            
        if bootDict.has_key('loader'):
            loader = document.createElement('loader')
            loader.appendChild(document.createTextNode(bootDict['loader']))
            os.appendChild(loader)
        
    # BIOS
        if bootDict.has_key('devices'):
            for device in bootDict['devices']:
                boot = document.createElement('boot')
                boot.setAttribute('dev', device)
                os.appendChild(boot)
            
    # Kernel
        else:
            kernel = document.createElement('kernel')
            kernel.appendChild(document.createTextNode(bootDict['kernel']))
            os.appendChild(kernel)
            
            if bootDict.has_key('initrd'):
                initrd = document.createElement('initrd')
                initrdText = document.createTextNode(bootDict['initrd'])
                initrd.appendChild(initrdText)
                os.appendChild(initrd)
            
            if bootDict.has_key('cmdline'): 
                cmdline = document.createElement('cmdline')
                cmdlineText = document.createTextNode(bootDict['cmdline'])
                cmdline.appendChild(cmdlineText)
                os.appendChild(cmdline)
        bootList.append(os)
    else:
        raise TypeError
    
    return bootList

def onPowerOffElement(action):
    """
    Creates a <on_poweroff> element, a child of L{domain element
    <domainElement>}, that specifies the action to take when powered off. 

    @param action: action to take on power off
    @type action: String

    @return: <on_poweroff> element
    @rtype: DOM Element
    """
    document = Document()
    elem = document.createElement('on_poweroff')
    elem.appendChild(document.createTextNode(action))
    return elem

def onRebootElement(action):
    """
    Creates a <on_reboot> element, a child of L{domain element
    <domainElement>}, that specifies the action to take when rebooted.

    @param action: action to take on reboot
    @type action: String

    @return: <on_reboot> element
    @rtype: DOM Element
    """
    document = Document()
    elem = document.createElement('on_reboot')
    elem.appendChild(document.createTextNode(action))
    return elem

def onCrashElement(action):
    """
    Creates a <on_crash> element, a child of L{domain element
    <domainElement>}, that specifies the action to take upon a crash.

    @param action: action to take on crash
    @type action: String

    @return: <on_crash> element
    @rtype: DOM Element
    """
    document = Document()
    elem = document.createElement('on_crash')
    elem.appendChild(document.createTextNode(action))
    return elem

def featuresElement(pae=False, nonpae=False, acpi=False, apic=False):
    """
    Creates a <features> element, a child of L{domain element
    <domainElement>}, that specifies mutually exclusive hypervisor features.

    @param pae: physical address extension mode
    @type pae: boolean

    @param nonpae: physical address extension mode
    @type nonpae: boolean

    @param acpi: acpi support
    @type acpi: boolean

    @param apic: apic support
    @type apic: boolean

    @return: <features> element
    @rtype: DOM Element
    """
    document = Document()
    features = document.createElement('features')
    if pae:
        features.appendChild(document.createElement('pae'))
    if nonpae:
        features.appendChild(document.createElement('nonpae'))
    if acpi:
        features.appendChild(document.createElement('acpi'))
    if apic:
        features.appendChild(document.createElement('apic'))
    return features

def clockElement(sync):
    """
    Creates a <clock> element, a child of L{domain element<domainElement>}, 
    that specifies how the clock is set.

    @param sync: initialization method for host, 'localtime' or 'utc'
    @type sync: String

    @return: <clock> element
    @rtype: DOM Element
    """
    document = Document()
    elem = document.createElement('clock')
    elem.setAttribute('sync', sync)
    return elem

def devicesElement(*devices):
    """
    Creates a <devices> element, a child of L{domain element
    <domainElement>}, is the parent element for all devices.
    
    Devices:
    ========
    
    -L{<Emulator<emulatorElement>}
    -L{<Disk<diskElement>}
    -L{<Network<networkElement>}
    -L{<Input<inputElement>}
    -L{<Graphics<graphicsElement>}

    @param devices: sequence of device elements
    @type devices: variable length DOM Element tuple

    @return: <devices> element
    @rtype: DOM Element
    """
    document = Document()
    elem = document.createElement('devices')
    addDevice(elem, devices)
    return elem

def addDevice(deviceElem, *devices):
    """
    Adds to a <devices> element, a child of L{domain element<domainElement>}, 
    the devices specified as elements in the devices argument.

    @param deviceElem: <devices> element
    @type deviceElem: DOM Element

    @param devices: sequence of device elements
    @type devices: DOM Element tuple

    @return: <devices> element
    @rtype: DOM Element
    """
    for each in devices:
        deviceElem.appendChild(each)
    return deviceElem

def emulatorElement(path):
    """
    Creates a <emulator> element, a child of L{device element
    <devicesElement>}, that specifies the path to the emulator binary.

    @param path: path to emulator binary
    @type path: String

    @return: <emulator> element
    @rtype: DOM Element
    """
    document = Document()
    elem = document.createElement('emulator')
    elem.appendChild(document.createTextNode(path))
    return elem

def diskElement(diskDict):
    """
    Creates a <disk> element, a child of L{device element<devicesElement>}, 
    that specifies the devices to be mounted.

    diskType, diskDevice, sourceFile, targetBus=None,
    targetDev=None, readonly=False, driverName=None, driverType=None
    
    @param diskDict: dictionary of disk arguments
    @type diskDict: dictionary
    
    @note: diskDict has specific key values:
        - diskDevice(optional): floppy, disk, or cdrom
        - driverName(optional): primary hypervisor backend name
        - driverType(optional): primary hypervisor backend sub-type
        - readonly(optional): specifies if device is read-only
        - sourceFile: source path
        - targetDev: logical device name
        - targetBus(optional): ide, scsi, virtio, or xen
        - diskType: file or block

    @return: <disk> element
    @rtype: DOM Element
    """
    document = Document()
    diskElem = document.createElement('disk')
    diskElem.setAttribute('type', diskDict['diskType'])
    diskElem.setAttribute('device', diskDict['diskDevice'])
    
    sourceElem = document.createElement('source')
    sourceElem.setAttribute('file', diskDict['sourceFile'])
    diskElem.appendChild(sourceElem)
    
    if(diskDict.has_key('targetDev') or diskDict.has_key('targetBus')):
        targetElem = document.createElement('target')
        if diskDict.has_key('targetDev'):
            targetElem.setAttribute('dev', diskDict['targetDev'])
        if diskDict.has_key('targetBus'):
            targetElem.setAttribute('bus', diskDict['targetBus'])
        diskElem.appendChild(targetElem)
    
    if(diskDict.has_key('driverName') or diskDict.has_key('driverType')):
        driverElem = document.createElement('driver')
        if diskDict.has_key('driverName'):
            driverElem.setAttribute('name', diskDict['driverName'])
        if diskDict.has_key('driverType'):
            driverElem.setAttribute('type', diskDict['driverType'])
        diskElem.appendChild(driverElem)
    
    if diskDict.has_key('readonly'):
        if diskDict['readonly']:
            readonlyElem = document.createElement('readonly')
            diskElem.appendChild(readonlyElem)
        
    return diskElem

def networkElement(netDict):
    """
    Creates a <interface> element, a child of L{device element
    <devicesElement>}, that specifies network interfaces. 
    
    @param netDict: dictionary of network interfaces
    @type netDict: dictionary
    
    @note: netDict has specific key values:
    
    bridge:
        - interfaceType: bridge
        - macAddress: MAC address
        - sourceName: bridge name
        - targetDev: tun device name
    
    client:
        - interfaceType: client
        - sourceAddress: ip address
        - sourcePort: port
    
    ethernet:
        - interfaceType: ethernet
        - script: host setup shell script
        - targetDev: tun device name
    
    mcast:
        - interfaceType: mcast
        - sourceAddress: ip address
        - sourcePort: port
    
    network:
        - interfaceType: network
        - macAddress: MAC address
        - sourceName: network name
        - targetDev: tun device name
    
    server:
        - interfaceType: server
        - sourceAddress: ip address
        - sourcePort: port
    
    user:
        - interfaceType: user
        - macAddress: MAC address

    @return: <interface> element
    @rtype: DOM Element
    """
    document = Document()

    interface = document.createElement('interface')
    interface.setAttribute('type', netDict['interfaceType'])
    
    if netDict['interfaceType'] == 'user':
        if netDict.has_key('macAddress'):
            mac = document.createElement('mac')
            mac.setAttribute('address', netDict['macAddress'])
            interface.appendChild(mac)
    elif netDict['interfaceType'] == 'ethernet':
        if netDict.has_key('target'):
            target = document.createElement('target')
            target.setAttribute('dev', netDict['target'])
            interface.appendChild(target)
        if netDict.has_key('script'):
            script = document.createElement('script')
            script.setAttribute('path', netDict['script'])
            interface.appendChild(script)
    else:
        source = document.createElement('source')
        if(netDict['interfaceType'] == 'network' or
           netDict['interfaceType'] == 'bridge'):
            source.setAttribute(netDict['interfaceType'], 
                                netDict['sourceName'])
            interface.appendChild(source)
            if netDict.has_key('target'):
                target = document.createElement('target')
                target.setAttribute('dev', netDict['target'])
                interface.appendChild(target)
            if netDict.has_key('macAddress'):
                mac = document.createElement('mac')
                mac.setAttribute('address', netDict['macAddress'])
                interface.appendChild(mac)
        elif(netDict['interfaceType'] == 'server' or 
             netDict['interfaceType'] == 'client' or
             netDict['interfaceType'] == 'mcast'):
            source.setAttribute('address', netDict['sourceAddress'])
            source.setAttribute('port', netDict['sourcePort'])
            interface.appendChild(source)
        else:
            raise ValueError
    
    return interface

def inputElement(inputType, bus=None):
    """
    Creates a <input> element, a child of L{device element<devicesElement>}, 
    that specifies input devices. Input device automatically provided, use to 
    add additional input devices, such as a tablet input device for absolute 
    cursor movement. 

    @param inputType: input type: mouse or tablet
    @type inputType: String

    @param bus: refines device type: xen, ps2, or usb
    @type bus: String

    @return: <input> element
    @rtype: DOM Element
    """
    document = Document()
    elem = document.createElement('input')
    elem.setAttribute('type', inputType)
    if(bus != None):
        elem.setAttribute('bus', bus)
    return elem

def graphicsElement(graphicsType, listen=None, port=None):
    """
    Creates a <graphics> element, a child of L{device element<devicesElement>}, 
    that specifies the graphics framebuffer device, either on the host or 
    through a VNC server.

    @param graphicsType: frame buffer type: sdl or vnc    
    @type graphicsType: String

    @param listen: IP address for VNC server    
    @type listen: String

    @param port: port for VNC server    
    @type port: String

    @return: <graphics> element    
    @rtype: DOM Element
    """
    document = Document()
    elem = document.createElement('graphics')
    elem.setAttribute('type', graphicsType)
    if(listen != None):
        elem.setAttribute('listen', listen)
    if(port != None):
        elem.setAttribute('port', port)
    return elem

def serialElement(deviceDict):
    """
    Creates a character device element, a <serial> element, as a child 
    of L{device element<devicesElement>}, that specifies the serial character 
    device to be used. Examples from libvirt.org:
        
    Device Logfile: A file is opened and all data sent to the character 
    device is written to the file.
        - type: file
        - path: /var/log/vm/vm-serial.log
        - port: 1
        
    Virtual Console: Connects the character device to the graphical 
    framebuffer in a virtual console. This is typically accessed via a 
    special hotkey sequence such as "ctrl+alt+3".
        - type: vc
        - port: 1
        
    Null Device: Connects the character device to the void. No data is 
    ever provided to the input. All data written is discarded.
        - type: null
        - port: 1
        
    TCP Client/Server: The character device acts as a TCP client connecting 
    to a remote server, or as a server waiting for a client connection.
        - type: tcp
        - mode: connect
        - host: 127.0.0.1
        - service: 2445
        - wiremode: telnet
        - port: 1
    
    @param deviceDict: dictionary of character device attributes
    @type deviceDict: dictionary
    
    @note: deviceDict keys:
        - type: pty, stdio, vc, null, dev, tcp, udp, unix, or file
        - port: port number
        - path(optional): source path
        - mode(optional): connect or bind
        - host(optional): ip address
        - service(optional): service port
        - wiremode(optional): telnet
    
    @return: character device Element
    @rtype: DOM Element
    """
    document = Document()
    deviceElem = document.createElement('serial')
    deviceElem.setAttribute('type', deviceDict['type'])
    
    if deviceDict.has_key('path'):
        pathElem = document.createElement('source')
        pathElem.setAttribute('path', deviceDict['path'])
        deviceElem.appendChild(pathElem)
    elif deviceDict.has_key('mode'):
        sourceElem = document.createElement('source')
        sourceElem.setAttribute('mode', deviceDict['mode'])
        sourceElem.setAttribute('host', deviceDict['host'])
        sourceElem.setAttribute('service', deviceDict['service'])
        deviceElem.appendChild(sourceElem)

    if deviceDict.has_key('wiremode'):
        wiremodeElem = document.createElement('wiremode')
        wiremodeElem.setAttribute('type', deviceDict['wiremode'])
        deviceElem.appendChild(wiremodeElem)
    
    portElem = document.createElement('target')
    portElem.setAttribute('port', deviceDict['port'])
    deviceElem.appendChild(portElem)
    return deviceElem

def consoleElement(deviceType, port):
    """
    Creates a character device element, a <console> element, as a child 
    of L{device element<devicesElement>}, that specifies the console character
    device to be used. Examples from libvirt.org:
    
    Domain Logfile: This disables all input on the character device, and 
    sends output into the virtual machine's logfile.
        - type: stdio
        - port: 1
        
    @param deviceType: device type
    @type deviceType: String
    
    @param port: port number
    @type port: String
    
    @return: <console> element
    @rtype: String
    """
    document = Document()
    deviceElem = document.createElement('console')
    deviceElem.setAttribute('type', deviceType)
    portElem = document.createElement('target')
    portElem.setAttribute('port', port)
    deviceElem.appendChild(portElem)
    return deviceElem
    
def parallalElement(deviceType, path, port):
    """
    Creates a character device element, a <parallel> element, as a child 
    of L{device element<devicesElement>}, that specifies the parallel character 
    device to be used.
    
    @param deviceType: device type
    @type deviceType: String
    
    @param path: source path
    @type path: String
    
    @param port: port number
    @type port: String
    
    @return: <parallel> element
    @rtype: DOM Element
    """
    document = Document()
    deviceElem = document.createElement('parallel')
    deviceElem.setAttribute('type', deviceType)
    portElem = document.createElement('source')
    portElem.setAttribute('path', path)
    portElem = document.createElement('target')
    portElem.setAttribute('port', port)
    deviceElem.appendChild(portElem)
    return deviceElem

def getOvfSystemType(ovf, ovfId):
    """
    Retrieves a list of system types for the virtual machine from the 
    Ovf file.

    @param ovf: Ovf file
    @type ovf: DOM Document
    
    @param ovfId: VirtualSystem(Collection) identifier
    @type ovfId: String

    @return: list of OVF system types
    @rtype: list
    """
    systemTypes = []
    vs = Ovf.getSections(ovf, 'VirtualSystem', ovfId)
    if vs != []:
        sys = vs[0].getElementsByTagName('vssd:VirtualSystemType')
        if sys != []:
            for each in sys:
                systemTypes.append(each.firstChild.data)
    
    return systemTypes

def getOvfMemory(ovf, ovfId, configId=None):
    """
    Retrieves the maximum amount of memory (kB) to be allocated for the 
    virtual machine from the Ovf file. 

    @param ovf: Ovf file
    @type ovf: DOM Document
    
    @param ovfId: VirtualSystem(Collection) identifier
    @type ovfId: String
    
    @param configId: configuration name
    @type configId: String

    @return: memory in kB
    @rtype: String
    """
    # TODO: needs to use bound:max, if it exists
    if Ovf.isVirtualSystem(ovf, ovfId):
        ovfSectionName = 'VirtualHardwareSection'
    elif Ovf.isVirtualSystemCollection(ovf, ovfId):
        ovfSectionName = 'ResourceAllocationSection'
    else:
        raise ValueError("No Entities exist in OVF.")    
    
    ovfNode = Ovf.getSections(ovf, ovfSectionName, ovfId)
    if ovfNode != []:
        rasd = Ovf.getDict(ovfNode, ovfId, configId)['children']
        for resource in rasd:
            if resource['ResourceType'] == '4':
                memoryQuantity = resource['VirtualQuantity']
                memoryUnits = resource['AllocationUnits']
    else:
        raise ValueError(ovfSectionName + ": Section not found")
    
    # Calculate PUnit numerical factor
    memoryUnits.replace('^','**')
    
    # Determine PUnit Quantifier DMTF DSP0004, {byte, bit}
    memoryUnits = memoryUnits.split(' ', 1)
    quantifier = memoryUnits[0]
    if quantifier == 'byte':
        memoryUnits[0] = 1
    elif quantifier == 'bit':
        memoryUnits[0] = 0.125
    else:
        raise ValueError("Incompatible PUnit quantifier for memory.")
    
    memoryUnits = ' '.join(memoryUnits)
    memoryFactor = eval(memoryUnits)
    
    memoryValue = str(int(memoryQuantity) * memoryFactor)
    
    return memoryElement(memoryValue)

def getOvfCurrentMemory(ovf, ovfId=None, configId=None):
    """
    Retrieves the amount of memory (kB) to be allocated for the virtual machine 
    from the Ovf file.

    @param ovf: Ovf file
    @type ovf: DOM Document
    
    @param ovfId: VirtualSystem(Collection) identifier
    @type ovfId: String
    
    @param configId: configuration name
    @type configId: String

    @return: memory in kB
    @rtype: String
    """
    # TODO: needs to use bound:normal, if it is present
    if Ovf.isVirtualSystem(ovf, ovfId):
        ovfSectionName = 'VirtualHardwareSection'
    elif Ovf.isVirtualSystemCollection(ovf, ovfId):
        ovfSectionName = 'ResourceAllocationSection'
    else:
        raise ValueError("No Entities exist in OVF.")    
    
    ovfNode = Ovf.getSections(ovf, ovfSectionName, ovfId)
    if ovfNode != []:
        rasd = Ovf.getDict(ovfNode, ovfId, configId)['children']
        for resource in rasd:
            if resource['ResourceType'] == '4':
                memoryQuantity = resource['VirtualQuantity']
                memoryUnits = resource['AllocationUnits']
    else:
        raise ValueError(ovfSectionName + ": Section not found")
    
    # Calculate PUnit numerical factor
    memoryUnits.replace('^','**')
    
    # Determine PUnit Quantifier DMTF DSP0004, {byte, bit}
    memoryUnits = memoryUnits.split(' ', 1)
    quantifier = memoryUnits[0]
    if quantifier == 'byte':
        memoryUnits[0] = 1
    elif quantifier == 'bit':
        memoryUnits[0] = 0.125
    else:
        raise ValueError("Incompatible PUnit quantifier for memory.")
    
    memoryUnits = ' '.join(memoryUnits)
    memoryFactor = eval(memoryUnits)
    
    memoryValue = str(int(memoryQuantity) * memoryFactor)
    
    return currentMemoryElement(memoryValue)
    
def getOvfVcpu(ovf, ovfId=None, configId=None):
    """
    Retrieves the number of virtual CPUs to be allocated for the virtual 
    machine from the Ovf file. 

    @param ovf: Ovf file
    @type ovf: DOM Document
    
    @param ovfId: VirtualSystem(Collection) identifier
    @type ovfId: String
    
    @param configId: configuration name
    @type configId: String

    @return: quantity of virtual cpu's
    @rtype: String
    """
    if Ovf.isVirtualSystem(ovf, ovfId):
        ovfSectionName = 'VirtualHardwareSection'
    elif Ovf.isVirtualSystemCollection(ovf, ovfId):
        ovfSectionName = 'ResourceAllocationSection'
    else:
        raise ValueError("No Entities exist in OVF.") 
    
    ovfNode = Ovf.getSections(ovf, ovfSectionName, ovfId)
    rasd = Ovf.getDict(ovfNode, ovfId, configId)['children']
    for resource in rasd:
        if resource['ResourceType'] == '3':
            vcpu = resource['VirtualQuantity']

    return vcpu

def getOvfDevices(ovf, ovfId=None, configId=None):
    """
    Retrieves device information for the virtual machine from the Ovf file. 

    @param ovf: Ovf file
    @type ovf: DOM Document
    
    @param ovfId: VirtualSystem(Collection) identifier
    @type ovfId: String
    
    @param configId: configuration name
    @type configId: String

    @return: L{Devices Element<devicesElement>}
    @rtype: DOM Element
    """
    devices = []
    
    devices.extend(getOvfDiskList(ovf, ovfId, configId))
    devices.extend(getOvfNetworkList(ovf, ovfId, configId))
    
    return devices

def getOvfDiskList(ovf, ovfId=None, configId=None):
    """
    Retrieves disk device information for the virtual machine from the Ovf file. 

    @param ovf: Ovf file
    @type ovf: DOM Document
    
    @param ovfId: VirtualSystem(Collection) identifier
    @type ovfId: String
    
    @param configId: configuration name
    @type configId: String

    @return: list of dictionaries, see L{Disk Elements<diskElement>}
    @rtype: list
    
    @todo: stubbed function, needs work
    """
    diskList = []
#    logicalNames = ['hda', 'hdb', 'hdd']
#    
#    if Ovf.isVirtualSystem(ovf, ovfId):
#        ovfSectionName = 'VirtualHardwareSection'
#    elif Ovf.isVirtualSystemCollection(ovf, ovfId):
#        ovfSectionName = 'ResourceAllocationSection'
#    else:
#        raise ValueError("No Entities exist in OVF.")
#    
#    ovfNode = Ovf.getSections(ovf, ovfSectionName, ovfId)
#    rasd = Ovf.getDict(ovfNode, ovfId, configId)['children']
#    
#    ovfDisks = []
#    
#    for resource in rasd:
#        if resource['ResourceType'] == '14':
#            ovfDisks.append(('fd', resource))
#        elif resource['ResourceType'] == '15':
#            ovfDisks.append(('cdrom', resource))
#        elif resource['ResourceType'] == '17':
#            ovfDisks.append(('disk', resource))
#    
#    for each in ovfDisks:
#        disk = each[1]
#        
#        #disk device
#        device = each[0]
#
#        #source file
#        hostResource = disk['HostResource']
#        resourceId = hostResource.rsplit('/', 1).pop()
#        if hostResource.startswith('ovf://file/'):
#            refs = Ovf.getDict(Ovf.getSections(ovf, 'References'), 
#                               configId)
#            if refs.has_key(resourceId):
#                sourceFile = refs[resourceId]['href']
#            else:
#                raise ValueError
#
#        elif hostResource.startswith('ovf://disk/'):
#            diskList = Ovf.getDict(Ovf.getSections(ovf, 'References'), 
#                                   configId)
#            if diskList.has_key(resourceId):
#                sourceFile = diskList[resourceId]['fileRef']
#            else:
#                raise ValueError
#        else:
#            raise ValueError(resourceId)
#        
#        #target bus
#        parentType = rasd[disk['Parent']]['ResourceType']
#        if(parentType == '5'):
#            bus = 'ide'
#        elif(parentType == '6'):
#            bus = 'scsi'
#        else:
#            raise ValueError
#        
#        #target device
#        if(device == 'cdrom'):
#            disk = diskElement('file', device, sourceFile, bus, 'hdc', True)
#        else:
#            disk = diskElement('file', device, sourceFile, bus, logicalNames.pop(0))
#        diskElementList.append(disk)
#
    return diskList

def getOvfNetworkList(ovf, ovfId=None, configId=None):
    """
    Retrieves network interface information for the virtual machine from the Ovf file. 

    @param ovf: Ovf file
    @type ovf: DOM Document
    
    @param ovfId: VirtualSystem(Collection) identifier
    @type ovfId: String
    
    @param configId: configuration name
    @type configId: String

    @return: list of dictionaries, seeL{Interface Elements<networkElement>}
    @rtype: list
    
    @todo: stubbed function, needs work
    """
    netList = []
#    return [networkElement('network', 'test')]
    return netList

def getOvfDomain(ovf, ovfId, configId=None):
    """
    Returns a libvirt domain object for a specific virtual system, 
    based on the id and configuration, from the ovf.
    
    
    @param ovfId: VirtualSystem(Collection) identifier
    @type ovfId: String
    
    @param configId: configuration name
    @type configId: String
    
    @todo: needs work, very basic, lots of assumptions
    """
    #metadata
    name = nameElement(ovfId)
    
    #resources
    memory = getOvfMemory(ovf, ovfId, configId)
    vcpu = getOvfVcpu(ovf, ovfId, configId)
    
    #boot
    bootDict = dict(type='hvm',
                loader='/usr/lib/xen/boot/hvmloader',
                devices=['hd'])
    
    boot = bootElement(bootDict)
    
    #time
    clock = clockElement('utc')
    
    #features
    features = featuresElement(acpi=True)
    
    #life cycle
    onPowerOff = onPowerOffElement('destroy')
    onReboot = onRebootElement('restart')
    onCrash = onCrashElement('destroy')
    
    #devices
    devices = getOvfDevices(ovf, ovfId, configId)
    
    #network
    #networkType = 'bridge'
    #networkSource = 'br1'
    #network = networkElement(networkType, networkSource)
    #devices = addDevice(deviceSection, networkSection)
    
    #devices - graphics
    graphics = graphicsElement('vnc', 'localhost', '5911')
    devices = addDevice(devices, graphics)
    
    #domain
    domain = domainElement('xen')
    
    #document
    document = libvirtDocument(domain, name, memory, vcpu, boot, clock, 
                               features, onPowerOff, onReboot, onCrash, devices)

    return Ovf.xmlString(document)

def getOvfLibvirt(ovf, configId=None):
    """
    Returns a dictionary with all of the VirtualSystems in an ovf
    listed as keys with the libvirt domain, for the specified configuration,
    stored as the value.

    @param ovf: Ovf file
    @type ovf: DOM Document
    
    @param configId: configuration name
    @type configId: String
    
    @return: dicitonary of L{Libvirt Domains<getOvfDomain>}
    @rtype: dictionary 
    """
    domains = dict()
    
    if configId == None:
        configId = Ovf.getDefaultConfiguration(ovf)
    
    # For each system, create libvirt domain description
    for ovfId in Ovf.getSections(ovf, 'VirtualSystems'):
        domains[id] = getOvfDomain(ovf, ovfId, configId)
        
    return domains

def getOvfStartup(ovf):
    """
    Returns a schedule representing the startup order for a virtual
    appliance from an ovf.
    
    @param ovf: Ovf file
    @type ovf: DOM Document
    
    @rtype: dictionary
    @return: startup dictionary of domains
    """
    startupDict = dict(boot='',
                       systems=dict())
    
    systems = startupDict['systems']
    
    # Create a list of all startup sections
    startupSections = Ovf.getSections(ovf, 'StartupSection')
    
    # Create an entry in startup dictionary for each entry in Startup sections
    for section in startupSections:
        for item in section.getElementsByTagName('Item'):
            attributes = []
            for i in range(item.attributes.length):
                attr = item.attributes.item(i)
                if attr.name == 'ovf:id':
                    sysId = attr.value
                elif(attr.name == 'ovf:order' or
                   attr.name == 'ovf:startDelay'):
                    attributes.append((attr.name, attr.value))
            
            # Store attribute pairs in dicitonary
            virtualSys = dict(attributes)
            if not virtualSys.has_key('ovf:order'):
                virtualSys['ovf:order'] = '0'
            if not virtualSys.has_key('ovf:startDelay'):
                virtualSys['ovf:startDelay'] = '0'
            
            parentId = section.parentNode.getAttribute('ovf:id')
            systems[parentId] = dict(systems=dict())
            systems[parentId]['systems'][sysId] = virtualSys
                
    # Create a default entry for each system not in a startup section
    for each in Ovf.getSections(ovf, 'VirtualSystem'):
        sysId = each.getAttribute('ovf:id')
        
        # If parentNode is Envelope, set as root system
        # else, trace back and fill in missing parent info
        if each.parentNode.tagName == 'Envelope':
            startupDict['boot'] = sysId
            systems[sysId] = {'ovf:order':'0', 'ovf:startDelay':'0'}
        else:
            parent = each.parentNode
            parentId = parent.getAttribute('ovf:id')
            if systems.has_key(parentId):
                systems[parentId]['systems'][sysId] = {'ovf:order':'0',
                                                       'ovf:startDelay':'0'}
                
            while(not systems.has_key(parentId)):
                systems[parentId] = {'systems':dict(),
                                     'ovf:order':'0', 
                                     'ovf:startDelay':'0'}
                systems[parentId]['systems'][sysId] = {'ovf:order':'0',
                                                       'ovf:startDelay':'0'}
                
                # Increment, if not at root
                if parent.parentNode.tagName == 'Envelope':
                    startupDict['boot'] = parentId
                else:
                    parent = parent.parentNode
                    sysId = parentId
                    parentId = parent.getAttribute('ovf:id')
            
    return startupDict
    
def getSchedule(conn, startup, domains):
    """
    Returns a schedule representing the startup order for a virtual
    appliance and boots the defined domains.
        
    @param conn: libvirt connection instance
    @type conn: libvirt.virConnect
    
    @param startup: L{Startup dictionary<getOvfStartup>}
    @type startup: dictionary
    
    @param domains: L{Domain dictionary<getOvfDomain>}
    @type domains: dictionary
    
    @return: queue of domains and their startup delays
    @rtype: sched.scheduler
    """
    # Initialization
    index = 0
    delay = 0
    queue = [startup['boot']]
    schedule = sched.scheduler(time.time, time.sleep)
    
    # Add actions to scheduler
    while(queue != []):
        sysId = queue.pop(0)
        system = startup['systems'][sysId]
        
        index += int(system['ovf:order'])
        delay += int(system['ovf:startDelay'])
        
        for sys in system['systems'].keys():
            if startup['systems'].has_key(sys):
                queue.append(sys)
            else:
                sysIndex = index + int(system['ovf:order'])
                sysDelay = delay + int(system['ovf:startDelay'])
                schedule.enter(sysDelay, sysIndex,
                               conn.createLinux,(domains[sysId]))
    
    return schedule

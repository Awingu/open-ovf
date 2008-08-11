# vi: ts=4 expandtab syntax=python
##############################################################################
# Copyright (c) 2008 IBM Corporation
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
# Marcos Cintron (IBM) - initial implementation
##############################################################################
import os

import Ovf
import OvfReferencedFile

def getReferencedFilesFromManifest(fileName):
    """
    get a list of OvfReferencedFile objects mentioned in OVF Manifest file
    @type  fileName: string
    @param fileName: path to a file to read Manifest file from
    @rtype : list of OvfReferencedFile objects
    @return: list of OvfReferencedFile objects that appear in manifest
    """
    try:
        files = []
        mfFD = open(fileName,"r")#only need to read the contents

        line = mfFD.readline()

        prefix = "SHA1("

        while line:
            txt = line.strip()
            newLn = txt.split('=')#newLn is what we get from the .mf file
            #when you append newLn it returns as a list so need to add both elements
            partial = newLn[0].split(prefix)#this will return ['', 'ourOVF.ovf)']
            #still need to take out the last )
            name = partial[1].split(')')
            #the above line will return ['Ubuntu-0.vmdk', '']
            href = name[0]#the name will always be stored in name[0]
            sumSection = txt.split('=')
            ans = sumSection[1].strip()
            path = Ovf.href2abspath(href, fileName)
            files.append(OvfReferencedFile.OvfReferencedFile(path, href, ans))
            line = mfFD.readline()#get the next line

        return files

    except Exception, e:
        raise e


def writeManifestFromReferencedFilesList(fileName, refList):
    """
    Write a OVF Manifest file from a list of ReferencedFile objects
    @type  fileName: string
    @param fileName: path to a file to write Manifest file to
    @type  refList    : list of OvfReferencedFile objects
    @param refList    : each of the OvfReferencedFile objects will appear in the manifest
    """

    try:
        mfFile = fileName

        if os.path.isfile(mfFile):
            os.remove(mfFile)

        mfFD = os.open(mfFile, os.O_RDWR | os.O_CREAT)#might want to change how i open it to just create

        prefix = "SHA1("
        suffix = ")= "
        #since list is a OvfReferencedFile list we don't need to create a new object
        sum = refList[0].getChecksum()#this will get the new sum for the ovf file that was passed
        #The line below creates the line in the correct format
        newLine = prefix+fileName+suffix+sum
        os.write(mfFD, newLine)

        for currFile in refList:
            if currFile.checksum == None:#if the file doesn't have a sum then get one
                currFile.doChecksum()

            sum = currFile.checksum
            name = currFile.href
            newLine = "\n" + prefix + name + suffix+sum

            os.write(mfFD, newLine)

        os.close(mfFD)

    except Exception, e:
        print "%swriteManifestFromReferencedFilesList: %s" % ('', e)

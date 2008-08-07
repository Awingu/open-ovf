# vi: ts=4 expandtab syntax=python
##############################################################################
# Copyright (c) 2008 IBM Corporation
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
# Scott Moser (IBM) - initial implementation
##############################################################################
import os
import shutil
import tarfile
import tempfile

import OvfFile
import OvfLibvirt
import OvfReferencedFile
import OvfManifest

class OvfSet:
    """
    This is the base OvfSet class. It represents an OVF Set, either as a tar 
    archive or as a directory layout
    """

    name    = None  #: the package name of this object (the name of .ovf
                    #: without extension)
    mode = "r"      #: read/write mode of object
    certificate = None    #: The OvfCertificate object
    ovfFile = None        #: The OvfFile object
    archiveFormat = "Dir" #: The archive type of this (default save type)
    archivePath = None    #: The write path of the archive
    archiveSavePath = None #: The Save Path for the archive (differs from archivePath for tar)
    __tmpdir__ = None     #: the temporary dir if tar (cleaned up in __del__)

    def __init__(self, path=None, mode="r"):
        """
        initialize object from path in read/write mode

        @type  path: String
        @param path: a path to initialize object from
        @type  mode: String
        @param mode: mode for open, either 'r' or 'w'
        """
        if not ( mode == "r" or mode == "w" ):
            raise TypeError("mode must be r or w")

        self.mode = mode

        if path != None:
            self.initializeFromPath(path, mode)

    def __del__(self):
        """
        Destructor, clean up temp directory if needed
        """
        if self.__tmpdir__ == None:
            return
        shutil.rmtree(self.__tmpdir__)

    def initializeFromPath(self, path, mode="r"):
        """
        initialize object from the file or path given in path
    
        @type  path: String
        @param path: a path to a file to open
        @type  mode: string
        @param mode: mode for open, either 'r' or 'w'
        """

        exists = True
        if os.path.isdir(path):
            self.archiveFormat = "Dir"
        elif os.path.isfile(path):
            if tarfile.is_tarfile(path):
                self.archiveFormat = "Tar"
            else:
                # this file is not a tar file, assume that this is a .ovf
                self.archiveFormat = "Dir"
        elif os.path.exists(path):
            raise IOError("unsupported file type for " + path)
        else:
            exists = False
            if mode == "r":
                raise IOError("cannot open for read " + path)
            if path.endswith("/") or path.endswith("\\"):
                self.archiveFormat = "Dir"
            elif path.endswith(".ovf") or path.endswith(".OVF"):
                self.archiveFormat = "Dir"
            else:
                self.archiveFormat = "Tar"

        if exists == True and self.archiveFormat == "Tar":
            # Here, for now, we make a temporary copy
            tmpd = tempfile.mkdtemp()
            self.__tmpdir__ = tmpd
            tf = tarfile.open(path, "r")
            ti = tf.next()
            while ti is not None:
                #TODO: need to do safe extraction here this
                # on windows need to protect c://
                # also, check that .ovf is first file
                # suggestion[ejcasler]: change ".." to "../"
                # make absolute refs begin with tempdir path
                if ti.name.find("..") != -1 or ti.name.startswith("/"):
                    raise IOError("Unsafe Tar file" + path)
                tf.extract(ti, tmpd)
                ti = tf.next()
            self.archivePath = tmpd
            self.archiveSavePath = path
        elif exists == True and self.archiveFormat == "Dir":
            # for existing, if it is a file path=dirname(path)
            if os.path.isfile(path):
                self.archivePath = os.path.dirname(path)
                # dirname returns "" rather than "." for "filename"
                if self.archivePath == "": 
                    self.archivePath = "."
                self.setName(os.path.basename(path)[0:(len(os.path.basename(path))-4)])
            else:
                self.archivePath = path
            self.archiveSavePath = self.archivePath
        elif exists == False and self.archiveFormat == "Tar":
            # for non-existant file, this is the file (.ova)
            self.archivePath = path
            self.archiveSavePath = self.archivePath
            self.setName(os.path.basename(path)[0:(len(os.path.basename(path))-4)])
        elif exists == False and self.archiveFormat == "Dir":
            # for non-existant dir, this is a dir (not .ovf)
            self.archivePath = path
            self.archiveSavePath = self.archivePath
        else:
            raise IOError("shouldn't be here")

        if ( not os.path.isfile(path) and self.archiveFormat == "Dir" and 
             exists == True ) or self.__tmpdir__ != None:
            name = False
            for curFile in os.listdir(self.archivePath):
                if curFile.endswith(".ovf"):
                    if name != False:
                        return False
                    # set name to filename without .ovf
                    name = curFile[0:(len(curFile)-4)]
            if name == False and mode == "r":
                raise IOError("no ovf file in " + path + "(" + self.archivePath + ")")
            elif name:
                self.setName(name)

        # now self.archivePath, self.archiveSavePath and self.archiveFormat should
        # be set.  self.name should be set if possible.
        # now, self.archivePath/self.name + ".ovf" should have the ovf file
        
        if self.name != None:
            basepath = self.archivePath + "/" + self.name
            self.ovfFile = OvfFile.OvfFile(basepath + ".ovf")
            if os.path.isfile(basepath + ".mf"):
                # we have a manifest
                pass

            if os.path.isfile(basepath + ".cert"):
                # we have a certificate
                pass

    def toString(self):
        """Overrides toString for OvfSet"""
        string = "name=" + str(self.name) + " mode=" + self.mode \
            + " archiveFormat=" + self.archiveFormat \
            + " archivePath=" + self.archivePath \
            + " archiveSavePath="  + self.archiveSavePath
        if self.__tmpdir__ != None:
            string = string + " tmpdir=" + self.__tmpdir__
        return string

    def getName(self):
        """
        get the OvfSet's name (file name of .ovf file without .ovf)
        @rtype: String
        @return: the name
        """
        return(self.name)

    def setName(self, name):
        """
        set the OvfSet's name (file name of .ovf file without .ovf)
        @type  name: String
        @param name: the new name
        @raise TypeError: on non-string input 
        """
        if type(name) == type(''):
            self.name = name
        else:
            raise TypeError("setName[name]: expected value of string type")

    def write(self, path=None, format=None):
        """
        write the object to disk

        @type  path: String
        @param path: path to save the file to.  Default is self.archivePath
        @type  format: String
        @param format: one of "Dir" or "Tar" or None. Default is self.archiveFormat
        @rtype: Boolean
        @return: success or failure of write
        """
        try:
            if format == None:
                format = self.archiveFormat
            if path == None:
                path = self.archiveSavePath
            if format == "Dir":
                return self.writeAsDir(path)
            elif format == "Tar":
                return self.writeAsTar(path)
            else:
                raise ValueError
        except IOError, (errno, strerror):
            raise IOError("I/O error(%s): %s" % (errno, strerror))
        except ValueError, (errno, strerror):
            raise ValueError("Value error(%s): %s" % (errno, strerror))

    def writeAsTar(self, path=None):
        """
        write a tar archive to path given
        @type path: String
        @param path: path to the archive to write to
        """
        if path == None:
            path = self.archivePath
        
        tar = tarfile.open(path,"w")#if any type of compression is needed use "w:<compressoin_used>" 
        
        ovfName = None
        try:
            (fd, ovfName) = tempfile.mkstemp()
            os.close(fd)
            ovftmp = open(ovfName, "w")
            self.ovfFile.writeFile(ovftmp)
            ovftmp.close()
            tar.add(ovftmp.name, (self.name + ".ovf").encode('ascii'))
            os.unlink(ovfName)
            ovfname = None
        except:
            if ovfname != None:
                os.unlink(ovfName)
            raise
        
        files = self.getOvfFile().getReferencedFiles() 
        
        for currFile in files:
            tar.add(currFile.path, currFile.href.encode('ascii'))
                                 
        tar.close()
            
    def writeAsDir(self, path=None):
        """
        write a directory archive to path given
        @type path: String
        @param path: path to the directory to write to
        @raise IOError: file or directory does not exist
        """
        try:
            if path != None:
                ovfPath = path + self.getName() + '.ovf'
            else:
                ovfPath = self.ovfFile.path
                
            #Open the file for writing, write, and close file.
            ovf = open(ovfPath, 'w')
            self.ovfFile.writeFile(ovf)
            ovf.close()

            #Write referenced files to path
            for each in self.ovfFile.getReferencedFiles():
                refFile = path + each.href
                if not os.path.isfile(refFile):
                    dirPath = refFile[:refFile.rfind('/')]
                    if not os.path.isdir(dirPath):
                        os.makedirs(dirPath)
                    shutil.copy(each.path, refFile)
        except IOError, (errno, strerror):
            raise IOError("I/O error(%s): %s" % (errno, strerror))

    def getOvfFile(self):
        """
        This function will return the object instance of the L{OvfFile}
        class that is associated with this L{OvfSet} object. 
        
        @rtype: OvfFile object
        @return: OvfFile object associated with calling OvfSet object
        """
        return self.ovfFile
    
    def verifyManifest(self, path=None):
        """
        This method will get manifest file based on the current object name.
        It will then get all the sums from the manifest file and compare them 
        to the sums in the OvfRefernecedFile list. If the checksum for a 
        specified file does not match then the given OvfRefencedFile will return False.
        
        @type  path: String
        @param path: the file that contains the manifest for the OvfSet (basename.mf)
        
        @rtype: Boolean
        @return: True if all the checksums of the files match
                 False if at least one checksum does not match
                 
        @raise IOError: File does not exist at path 
        """
        try:
            if path == None:
                path = self.archivePath + self.name+".mf"

            expected = { }
            for ref in OvfManifest.getReferencedFilesFromManifest(path):
                expected[ref.href] = ref
                
            found = { }
            for ref in self.ovfFile.files:
                if ref.checksum == None:
                    ref.doChecksum()
                found[ref.href] = ref

            # ovf file doesn't reference itself, so its not in the
            # found list.  add it if it is present in the expected
            if expected[self.name + ".ovf"]: 
                nref = OvfReferencedFile.OvfReferencedFile(
                        self.archivePath + "/" + self.name + ".ovf",
                        self.name + ".ovf")
                nref.doChecksum()
                found[nref.href] = nref

            for href in expected:
                if found[href].checksum != expected[href].checksum:
                    return False

            return True
        except:
            raise 

# Libvirt Interface
    def boot(self, conn, configId=None):
        """
        Boots OvfSet as libvirt domain(s).
        
        @param conn: libvirt connection instance
        @type conn: libvirt.virConnect
        
        @param configId: configuration identifier
        @type configId: String
        """
        ovf = self.ovfFile.document
            
        # TODO: Verify reservations DON'T exceed capabilities     
        
        # Get Startup order
        startup = OvfLibvirt.getOvfStartup(ovf)
        
        # Get Domain definitions
        domains = OvfLibvirt.getOvfLibvirt(ovf, configId)
        
        # queue domains with action: domains[id].create()
        schedule = OvfLibvirt.getSchedule(conn, startup, domains)
        
        schedule.run()
        

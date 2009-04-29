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
# Dave Leskovec (IBM) - minor fixes to writeAsDir
##############################################################################
import os
import shutil
import tarfile
import tempfile

import OvfFile
import OvfLibvirt
import OvfReferencedFile
import OvfManifest

FORMAT_DIR = "Dir"
FORMAT_TAR = "Tar"

class OvfSet(object):
    """
    This is the base OvfSet class. It represents an OVF Set, either as a tar
    archive or as a directory layout
    """

    def __init__(self, path=None, mode="r"):
        """
        Initialize object from path in read/write mode

        Note::
            Default mode is r for read.

        @raise TypeError: The error gets thrown if the prameter mode has a
        value other than I{r} or I{w}.

        @type  path: String
        @param path: a path to initialize object from
        @type  mode: String
        @param mode: mode for open, either 'r' or 'w'
        """

        #: the package name of this object (the name of .ovf without extension)
        self.name = None

        self.ovfFile = None     #: The OvfFile object
        self.archiveFormat = FORMAT_DIR #: The archive type of this (default save type)
        self.archivePath = None     #: The write path of the archive
        self.archiveSavePath = None #: The Save Path for the archive (differs from archivePath for tar)
        self.__tmpdir__ = None      #: the temporary dir if tar (cleaned up in __del__)

        self.mode = mode

        self.manifest = None
        self.certificate = None

        if path != None:
            self.initializeFromPath(path, mode)

    def __del__(self):
        """
        Destructor, clean up temp directory if needed
        """
        if self.__tmpdir__ == None:
            return
        shutil.rmtree(self.__tmpdir__)

    def _getMode(self):
        """read/write mode of object"""
        return self._mode

    def _setMode(self, value):
        """Set mode.
        @param value: must be 'r' or 'w'
        @type value: str

        @raise ValueError: if trying to set to anything
                           diffent then 'r' or 'w'
        """
        if value in ['r', 'w']:
            self._mode = value
        else:
            raise ValueError("mode must be r or w")

    mode = property(_getMode, _setMode)

    def initializeFromPath(self, path, mode="r"):
        """
        initialize object from the file or path given in path

        @raise IOError: The cases are as follow
                - I{B{Case 1:}} The path provided in the parameters is not
                valid.
                - I{B{Case 2:}} The mode parameter has a value of r and the path
                already exist.
                - I{B{Case 3:}} Unsafe Tar file
                - I{B{Case 4:}} The tar file cannot be found.



        @type  path: String
        @param path: a path to a file to open
        @type  mode: string
        @param mode: mode for open, either 'r' or 'w'
        """

        exists = True
        if os.path.isdir(path):
            self.archiveFormat = FORMAT_DIR
        elif os.path.isfile(path):
            if tarfile.is_tarfile(path):
                self.archiveFormat = FORMAT_TAR
            else:
                # this file is not a tar file, assume that this is a .ovf
                self.archiveFormat = FORMAT_DIR
        elif os.path.exists(path):
            raise IOError("unsupported file type for " + path)
        else:
            exists = False
            if mode == "r":
                raise IOError("cannot open for read " + path)
            if path.endswith("/") or path.endswith("\\"):
                self.archiveFormat = FORMAT_DIR
            elif path.endswith(".ovf") or path.endswith(".OVF"):
                self.archiveFormat = FORMAT_DIR
            else:
                self.archiveFormat = FORMAT_TAR

        if exists == True and self.archiveFormat == FORMAT_TAR:
            # Here, for now, we make a temporary copy
            tmpdir = os.path.dirname(os.path.abspath(path))
            if os.environ.has_key("TMPDIR"): tmpdir = None
            tmpd = tempfile.mkdtemp(dir=tmpdir)
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
        elif exists == True and self.archiveFormat == FORMAT_DIR:
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
        elif exists == False and self.archiveFormat == FORMAT_TAR:
            # for non-existant file, this is the file (.ova)
            self.archivePath = path
            self.archiveSavePath = self.archivePath
            self.setName(os.path.basename(path)[0:(len(os.path.basename(path))-4)])
        elif exists == False and self.archiveFormat == FORMAT_DIR:
            # for non-existant dir, this is a dir (not .ovf)
            self.archivePath = path
            self.archiveSavePath = self.archivePath
        else:
            raise IOError("shouldn't be here")

        if ( not os.path.isfile(path) and self.archiveFormat == FORMAT_DIR and
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
            basepath = os.path.join(self.archivePath, self.name)
            self.ovfFile = OvfFile.OvfFile(basepath + ".ovf")
            if os.path.isfile(basepath + ".mf"):
                # we have a manifest
                self.manifest = basepath + ".mf"

            if os.path.isfile(basepath + ".cert"):
                # we have a certificate
                self.certificate = basepath + ".cert"

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
        Get the OvfSet's name (file name of .ovf file without .ovf)
        @rtype: String
        @return: the name
        """
        return(self.name)

    def setName(self, name):
        """
        Set the OvfSet's name (file name of .ovf file without .ovf)
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
        Write the object to disk

        @raise ValueError: The error is thrown if the format parameter is not
        FORMAT_DIR or FORMAT_TAR.

        @type  path: String
        @param path: path to save the file to.  Default is self.archivePath
        @type  format: String
        @param format: one of FORMAT_DIR or FORMAT_TAR or None. Default is self.archiveFormat
        @rtype: Boolean
        @return: success or failure of write
        """
        try:
            if format == None:
                format = self.archiveFormat
            if path == None:
                path = self.archiveSavePath
            if format == FORMAT_DIR:
                return self.writeAsDir(path)
            elif format == FORMAT_TAR:
                return self.writeAsTar(path)
            else:
                raise ValueError
        except IOError, (errno, strerror):
            raise IOError("I/O error(%s): %s" % (errno, strerror))
        except ValueError, (errno, strerror):
            raise ValueError("Value error(%s): %s" % (errno, strerror))

    def writeAsTar(self, path=None):
        """
        Write a tar archive to path given
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

        # add the mf and cert files if we have them
        if self.manifest:
            altManifestFile = os.path.basename(self.manifest)
            tar.add(self.manifest, (altManifestFile).encode('ascii'))
        if self.certificate:
            altCertificateFile = os.path.basename(self.certificate)
            tar.add(self.certificate, (altCertificateFile).encode('ascii'))

        files = self.getOvfFile().files

        for currFile in files:
            tar.add(currFile.path, currFile.href.encode('ascii'))

        tar.close()

    def writeAsDir(self, path=None):
        """
        Write a directory archive to path given.
        @type path: String
        @param path: path to the directory to write to
        @raise IOError: file or directory does not exist
        """
        try:
            if path == None:
                path = self.ovfFile.path

            ovfPath = os.path.join(path, self.getName() + '.ovf')

            #Open the file for writing, write, and close file.
            ovf = open(ovfPath, 'w')
            self.ovfFile.writeFile(ovf)
            ovf.close()

            # Write mf and cert files if we have them
            if self.manifest:
                refFile = os.path.join(path,
                                       os.path.basename(self.manifest))
                shutil.copy(self.manifest, refFile)

            if self.certificate:
                refFile = os.path.join(path,
                                       os.path.basename(self.certificate))
                shutil.copy(self.certificate, refFile)

            #Write referenced files to path
            for each in self.ovfFile.files:
                refFile = os.path.join(path, each.href)
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
                path = os.path.join(self.archivePath, self.name + ".mf")

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
                        os.path.join(self.archivePath, self.name + ".ovf"),
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
    def boot(self, virtPlatform = None, configId=None, installLoc=None, envDirectory=None):
        """
        Boots OvfSet as libvirt domain(s).

        @param configId: configuration identifier
        @type configId: String
        """
        ovf = self.ovfFile.document

        # TODO: Verify reservations DON'T exceed capabilities

        # Get Startup order
        startup = OvfLibvirt.getOvfStartup(ovf)

        if installLoc == None:
            dirpath = os.path.dirname(os.path.abspath(self.ovfFile.path))
        else:
            dirpath = installLoc

        # Get Domain definitions
        domains = OvfLibvirt.getOvfDomains(ovf, dirpath,
                                           virtPlatform, configId,
                                           envDirectory)

        # queue domains with action: domains[id].create()
        schedule = OvfLibvirt.getSchedule(startup, domains)

        schedule.run()


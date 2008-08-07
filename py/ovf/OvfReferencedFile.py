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
from xml.dom.minidom import Document
import os
import time
import stat

import Ovf

class OvfReferencedFile:
    """
    This is class representing a file in a L{OvfSet}
    """

    checksum = None      #: the checksum of the file
    checksumStamp = None #: represents last time this checksum has been verified
    size = None          #: file size
    compression = None   #: compression type of file
    file_id = None       #: file id in the ovf 
    chunksize = None     #: chunksize of the file
    href = None          #: href/filename of the file
    path = None          #: the path to file

    def __init__(self, path, href, checksum = None, checksumStamp = None,
                 size = None, compression = None, file_id = None, 
                 chunksize = None):
        """
        Initialize object from filename.  Does not checksum object.
       
        @param path: The path to the referenced file.
        @type path: String
        
        @param href    : a reference to a file
        @type  href    : String
       
        @param checksum: The sha1 check sum for the file.
        @type checksum: String
        
        @param checksumStamp: The time stamp for the checksum.
        @type checksumStamp: String
        
        @param size: The size of the file.
        @type size: String.
        
        @param compression: The compression used for the file. 
        @type compression: String.
        
        @param file_id: The unique id for the given file.
        @type file_id: String
        
        @param chunksize: The size of the file's chunk being specified.
        @type chunksize: String. 
        """
        self.path = path
        self.href = href
        self.file_id = file_id
        self.checksum = checksum
        self.setChecksumStamp(checksumStamp)
        self.chunksize = chunksize
        self.size = size
        self.compression = compression
        
    def getFileObject(self):
        """
        Return a file-like object for this file, supporting 
        read(), readline(), readlines(), seek(), tell().   operations return
        compression free data (ie, if data is compressed it is uncompressed
        before returned) See extractfile at
        U{http://docs.python.org/lib/tarfile-objects.html#l2h-2417}
        
        Note: this method can throw an IO exception if the file cannot be opened
        
        @return: File handle based on self.path
        @rtype: File handle
        """
        return open(self.path,"rb")

    def doChecksum(self, stamp="auto"):
        """
        This method will optionally take a time stamp. If the file is not 
        local it will use time.gmtime() to set the checksumstamp. Otherwise
        it will use the file descriptor to extract that information. The method
        will then perform a SHA1 checksum of the file and store the results in 
        checksum.
        
        @type stamp: time in UTC.
        @param stamp: Time stamp of the file. (Last modify)
        
        """
        refFile = self.getFileObject()
        if stamp != "auto":
            self.setChecksum(stamp)
        else:
            mtime = None
            try:
                mtime = os.fstat(refFile.fileno())[stat.ST_MTIME]
            except:
                # if the fstat failed, call with no args
                self.setChecksumStamp()

            if mtime != None:
                # if fstat succeeded call it with mtime
                self.setChecksumStamp(mtime)
       
        self.checksum = Ovf.sha1sumFile(refFile)

    def setChecksum(self, checksum, stamp=None):
        """
        set the checksum for this object, if stamp is specified, use that
        stamp. Otherwise use the current date.

        @type checksum: String
        @param checksum: the checksum for this object
        @type  stamp: int
        @param stamp: unix timestamp of time checked
        @rtype:  Exception
        @return: pass or fail
        """
        self.checksum = checksum
        self.setChecksumStamp(stamp)
        
    def getChecksum(self):
        """
        This returns the checksum of this object.  If it has not been calculated or
        is known to be invalid, this will be None
        
        @rtype:  string
        @return: sha1sum of fileName in hex
        """    
        return self.checksum

    def setChecksumStamp(self, stamp="now"):
        """
        set the checksum stamp for this object
        @type  stamp: "now", None, int, or time object
        @param stamp: time of last update (time at which this checksum was 
                      known valid).  stamp can be of:
                        - string "now": current time
                        - type None: set to None
                        - type int: a unix timestamp
                        - type struct_time: a time object (assumed to be GMT)
        """
        if stamp == None:
            self.checksumStamp = None
        elif stamp == "now":
            self.checksumStamp = time.gmtime()
        elif stamp.__class__.__name__ == "int":
            self.checksumStamp = time.gmtime(stamp)
        elif stamp.__class__.__name__ == "struct_time":
            self.checksumStamp = stamp
        else:
            raise ValueError("stamp must be \"now\", None, int, or struct_time")
        
    def setCompression(self, compressType=None):
        """
        set the compression type

        @type  compressType: String
        @param compressType: type of compression
        @rtype: Boolean
        @return: pass or fail
        """
        self.compression = compressType

    def getCompression(self):
        """
        get the compression type

        @rtype:  String
        @return: type of compression
       
        """
        return self.compression

    def toElement(self):
        """
        Create and return a DOM element for this object
        
        @return: DOM element based on the infomation stored within the object.
        @rtype: DOM element.
        """
        childF = Document().createElement('File')

        if self.file_id != None:
            childF.setAttribute("ovf:id", self.file_id)
        if self.size != None:
            childF.setAttribute("ovf:size", self.size)
        if self.href != None:
            childF.setAttribute("ovf:href", self.href)
        if self.compression != None:
            childF.setAttribute("ovf:compression", self.compression)
        if self.chunksize != None:
            childF.setAttribute("ovf:chunkSize", self.chunksize)

        return(childF)

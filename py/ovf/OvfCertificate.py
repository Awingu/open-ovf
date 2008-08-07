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

#from OpenSSL import crypto

class OvfCertificate:
    """
    Object representing a OVF Certificate.  This is used for verification of
    manifest and for signing the signature of a manifest

    many functions here map to those of U{pyOpenSSL <http://pyopenssl.sourceforge.net/>}
    """

    privateKey = None #: the pkey object from pyopenssl
    certificate = None #: the X509 object in a .cert file

    def __init__(self, path=None):
        """
        Initialize OvfCertificate Object
        """
        if path != None:
            getCertificateFromFile(path)
            
    def generatePrivateKey(self, bits):
        """
        Generate private key to be used to sign certificate and digest.
        """
        #crypto.PKey().generate_key(crypto.TYPE_RSA, 512)

    def verify(self, signedKey, manifestFile):
        """
        verify the signature of an sha1 digest with the given manifest file
        This takes file-like object.

        @type signedKey    : String
        @param signedKey   : the signature of an sha1 digest
        @type manifestFile : String
        @param manifestFile: path to manifest file
        """
        #TODO:

    def setCertificate(self, inputString):
        """
        Set the certificate. Input can be from a .cert file or a String buffer.

        @type inputString: String
        @param inputString: path to *.cert file, or String buffer containing certificate
        """
        if os.path.isfile(inputString):
            certificateBuffer = open(inputString, "r").read()
        else:
            certificateBuffer = inputString    
        #self.certificate = crypto.load_certificate(crypto.FILETYPE_PEM,certificateBuffer)

    def getCertificate(self):
        """
        Return a String buffer representation of the certificate in the X509 object.
        to a .cert file

        @rtype: String
        @return: certificate
        """
        #return crypto.dump_certificate(crypto.FILETYPE_PEM,self.certificate)
        
    def loadPrivateKey(self, buf, passphrase):
        """
        load a private key, setting the privateKey to be used in signing
        
        @type buf        : String
        @param buf       : a String including the private key
        @type passphrase : String
        @param passphrase: the passphrase to use for private key, or callback

        @rtype:  boolean
        @return: success or failure of private key load
        """
        #self.privateKey = crypto.load_privatekey(crypto.FILETYPE_PEM,buf,passphrase)
        
    def signDigest(self, sha1digest):
        """
        sign the sha1digest given

        @type sha1digest : String
        @param sha1digest: a sha1digest to sign
        @rtype : String
        @return: a signed digest suitable for writing to .cert file
            (SHA1(package.mf)= ...)
        """
        #TODO:
    
    def writeCertificate(self, path=None):
        """
        Write the certificate to a file, named <basename>.cert

        @type path: String
        @param path: Save path for file, including filename
        """
        if not path.endswith('.cert'):
            raise ValueError('Type Error: Invalid type, must be of *.cert filetype')
        else:
            if os.path.isfile(path) or os.path.isdir(path):
                certFile = open(path, "w")
                #certFile.write(crypto.dump_certificate(crypto.FILETYPE_PEM, self.certificate))
                certFile.close()
            else:
                raise IOError('I/O Error: file could not be opened')

def getSignedDigestFromFile(path, passphrase):
    """
    Pull the signed digest out of an OVF .cert file

    @type path: String
    @param path: path to a .cert file
    @rtype: String
    @return: the signed digest from a OVF .cert file
    """
    if os.path.isfile(path):
        if path.endswith('.cert'):
            certFile = open(path, "r")
            buf = certFile.readline()
            while not buf.startswith('SHA1'):
                buf = certFile.readline()
            signedDigest = buf.split("=").pop()
            certFile.close()
            return signedDigest
        else:
            raise TypeError('Type Error: Invalid type, must be of *.cert filetype')
    else:
        raise IOError('I/O Error: file could not be opened')
    
def getCertificateFromFile(path):
    """
    Pull the certificate portion of an OVF .cert file

    @type path : String
    @param path: path to a .cert file or file handle object for reading
    @rtype: String
    @return: the certificate portion of an OVF .cert file
    """
    if os.path.isfile(path):
        if path.endswith('.cert'):
            certFile = open(path, "r")
            buf = certFile.readline()
            while not buf == '-----BEGIN CERTIFICATE-----':
                buf = certFile.readline()
            certificateString = buf.append(certFile.read())
            certFile.close()
            return certificateString
        else:
            raise TypeError('Type Error: Invalid type, must be of *.cert filetype')
    else:
        raise IOError('I/O Error: file could not be opened')
    
def publicKeyFromCertificate(path):
    """
    Given the certificate (as returned by getCertificateFromFile), return the
    public key
    """
    if os.path.isfile(path):
        if path.endswith('.cert'):
            certificateString = getCertificateFromFile(path)
            #TODO: verify that crypto.dump_privatekey works for public key too.
            #crypto.dump_privatekey(crypto.FILETYPE_PEM,certificateString.get_pubkey())
        else:
            raise TypeError('Type Error: Invalid type, must be of *.cert filetype')
    else:
        raise IOError('I/O Error: file could not be opened')

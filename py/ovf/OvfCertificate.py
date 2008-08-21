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
"""OVF Certificate functions.

(This uses openssl directly, not any python bindings to it)

Chek L{sign} and L{verify}.
"""

import os
import subprocess
import binascii
import tempfile
import shutil
import re

BASE_CMD = "openssl dgst -sha1 "

CMD_SIGN = BASE_CMD + "-hex -sign %(privkey)s -out %(outfile)s %(infile)s"
CMD_VERIFY = BASE_CMD + "-verify %(pubkey)s -signature %(sign)s %(infile)s"

CMD_GETPUBKEY = "openssl x509 -inform pem -in %(certificate)s -pubkey -noout"

def _runCommand(cmd):
    """Popen wrapper to simplify the execution of external programs.

    @param cmd: Command line to be executed
    @type cmd: string

    @return: tuple (exit code, stdout, stderr).
    @rtype: tuple
    """

    ssl = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
    status = ssl.wait()
    out, err = ssl.communicate()

    return status, out, err

def _appendX509Cert(destination, x509Cert):
    """Append the X.509 certificate to the destination file.

    @param destination: Filename to append the X.509 certificate to
                        (file should already exist).
    @type destination: string

    @param x509Cert: X.509 certificate filename
    @type x509Cert: string

    @raise IOError: If any of the specified files don't exist or
                    are not readable.
    """

    x509CertFile = file(x509Cert, 'r')
    certFile = file(destination, 'a')

    certFile.write(x509CertFile.read())
    x509CertFile.close()
    certFile.close()

def _extractPubkey(x509Cert, destDir=tempfile.gettempdir()):
    """Extract a public key from a x509 certificate.

    @param x509Cert: X.509 certificate filename
    @type x509Cert: string

    @param destDir: Directory to save the pubkey file to.
    @type destDir: string

    @return: Public key filename
    @rtype: string
    """

    cmd = CMD_GETPUBKEY % {'certificate': x509Cert}
    ret = _runCommand(cmd)
    if ret[0] != 0:
        raise

    pubFd, filename = tempfile.mkstemp(dir=destDir)
    os.write(pubFd, ret[1])
    os.close(pubFd)

    return filename

def _extractSignature(ovfCert, destDir=tempfile.gettempdir()):
    """Extract the manifest signature from an OVF certificate to
    a separate binary file, as needed to verify it with openssl.

    @param ovfCert: OVF certificate file
    @type ovfCert: string

    @param destDir: Directory to save the signature file to.
    @type destDir: string

    @return: (manifest filename, binary signature filename)
    @rtype: tuple
    """

    certFile = file(ovfCert, 'r')
    line = certFile.readline()
    certFile.close()

    try:
        match = re.match('SHA1\((.*)\)= ([A-Za-z0-9]*)', line).groups()
    except AttributeError:
        # first line should be SHA1(manifest)= d07fa7bb8a49c114...
        raise ValueError("ill-formed certificate file.")

    manifest = match[0]
    digest = match[1]

    binaryDigest = binascii.unhexlify(digest)

    digestFd, filename = tempfile.mkstemp(dir=destDir)
    os.write(digestFd, binaryDigest)
    os.close(digestFd)

    return manifest, filename

def sign(manifest, privkey, x509Cert):
    """Sign a manifest file. The certificate file will have the same
    basename as the manifest, but with the extension .cert, instead
    of .mf.

    @param manifest: manifest filename (must end with ".mf").
    @type manifest: string

    @param privkey: Private key filename
    @type privkey: string

    @param x509Cert: X.509 certificate filename
    @type x509Cert: string

    @raise IOError: If any of the specified files don't exist or
                    are not readable. Or also if the certificate file
                    can not be created.
    """

    if not os.path.isfile(manifest):
        raise IOError("Manifest file not found")

    if not os.path.isfile(privkey):
        raise IOError("Private key file not found")

    if not os.path.isfile(x509Cert):
        raise IOError("x509 certificate not found")

    if not manifest.endswith(".mf"):
        raise ValueError("Manifest file must have .mf extension")

    ovfCert = manifest.replace('.mf', '.cert')
    manifestDir = os.path.dirname(manifest) # command will run in this dir

    cmd = CMD_SIGN % { 'privkey': privkey,
                        'outfile': os.path.basename(ovfCert),
                        'infile': os.path.basename(manifest)}

    origDir = os.getcwd()
    os.chdir(manifestDir)

    status = _runCommand(cmd)
    os.chdir(origDir)

    if status[0] != 0:
        raise ValueError("Openssl failed")

    _appendX509Cert(ovfCert, x509Cert)

def verify(ovfCert):
    """Verify an OVF signature.

    @param ovfCert: OVF Certificate filename
    @type ovfCert: string

    @return: True = Valid, False = Not valid
    @rtype: bool

    @raise IOError: If L{ovfCert}, or the referenced manifest
                    file don't exist
    """

    if not os.path.isfile(ovfCert):
        raise IOError("Certificate file not found")

    tmpdir = tempfile.mkdtemp()
    pubkey = _extractPubkey(ovfCert, tmpdir)
    manifest, signature = _extractSignature(ovfCert, tmpdir)

    manifest = os.path.join(os.path.dirname(ovfCert), manifest)

    if not os.path.isfile(manifest):
        raise IOError("Manifest file not found")

    cmd = CMD_VERIFY % {'pubkey': pubkey, 'sign':  signature,
                        'infile': manifest}

    status = _runCommand(cmd)

    shutil.rmtree(tmpdir)

    return not status[0] # make it boolean


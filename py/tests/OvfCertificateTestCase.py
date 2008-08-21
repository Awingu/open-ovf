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
import unittest
import os
import tempfile
import shutil

from ovf import OvfCertificate


CMD_CREATE_CERT = "openssl req -x509 -nodes -days 365 \
 -subj /C=US/ST=Michigan/L=Plymouth/CN=www.scott.mosers.us \
 -newkey rsa:512 -keyout %(privkey)s -out %(certificate)s"

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files/")

class OvfCertificateTestCase(unittest.TestCase):

    def setUp(self):
        self.basepath = tempfile.mkdtemp()

        origManifest = os.path.join(TEST_FILES_DIR, 'ourOVF.mf')
        self.manifest = os.path.join(self.basepath, 'ourOVF.mf')
        shutil.copyfile(origManifest, self.manifest)

        self.privkey = os.path.join(self.basepath, 'private.pem')
        self.x509Cert = os.path.join(self.basepath, 'certificate.pem')

        cmd = CMD_CREATE_CERT % {'privkey': self.privkey,
                                 'certificate': self.x509Cert}
        OvfCertificate._runCommand(cmd)

        if not os.path.isfile(self.privkey) or \
                not os.path.isfile(self.x509Cert):
            raise IOError("Private key or certificate were not created")

    def tearDown(self):
        shutil.rmtree(self.basepath)

    def test_Sign(self):
        OvfCertificate.sign(self.manifest, self.privkey, self.x509Cert)

        ovfCert = self.manifest.replace('.mf', '.cert')
        self.assertTrue(os.path.isfile(ovfCert))

    def test_Verify(self):
        OvfCertificate.sign(self.manifest, self.privkey, self.x509Cert)

        ovfCert = self.manifest.replace('.mf', '.cert')
        self.assertTrue(os.path.isfile(ovfCert))

        valid = OvfCertificate.verify(ovfCert)
        self.assertTrue(valid)


if __name__ == "__main__":
    test = unittest.TestLoader().loadTestsFromTestCase(OvfCertificateTestCase)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(unittest.TestSuite(test))

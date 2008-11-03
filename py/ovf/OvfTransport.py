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
This module contains functions dealing with the environment transport
"""

import os
import shutil
import tempfile
from subprocess import call
from subprocess import Popen
from subprocess import PIPE
from subprocess import STDOUT

def selectISOProgram():
    """
    Identify if genisoimage or mkisofs in installed.  Will check genisoimage
    first and use that if available.  Will return None if neither is
    present.  Both programs support the same set of parms, at least as far
    as our usage is concerned.
    @rtype: String
    @return: iso program.  'genisoimage' or 'mkisofs'
    """
    isoProgs = ["genisoimage", "mkisofs"]
    for prog in isoProgs:
        retcode = call(["which", prog], stdout=PIPE, stderr=STDOUT)
        if not retcode:
            return prog

    return None

def makeISOTransport(fileList):
    """
    Create an iso(s) containing the file(s) passed by the user.
    @type fileList: List
    @param fileList: List in the format [outFileName, [inFileNames]]
                     For each entry in the list, an iso file outFileName will
                     be created containing the files in inFileNames

    @raise RuntimeError: a) No ISO format program
                         b) ISO format program returns an error
    """
    prog = selectISOProgram()
    if not prog:
        raise RuntimeError, "No ISO format program available."

    for (outFile, inFileList) in fileList:
        if not outFile:
            # no outfile name, base it on the first file in inFileList
            outFile = os.path.splitext(inFileList[0])[0] + '.iso'

        localInFileList = inFileList
        envFileBasename = os.path.basename(localInFileList[0])
        if envFileBasename != 'ovf-env.xml':
            tempDir = tempfile.mkdtemp()
            targetFileName = os.path.join(tempDir, 'ovf-env.xml')
            shutil.copyfile(localInFileList[0], targetFileName)
            localInFileList[0] = targetFileName
        callArgs = [prog, "-JR", "-o", outFile]
        callArgs.extend(inFileList)

        pObject = Popen(callArgs, stdout=PIPE, stderr=STDOUT)
        pStdout = pObject.communicate()[0]
        if pObject.returncode:
            raise RuntimeError, pStdout


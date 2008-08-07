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

"""OVF schema validation"""

import libxml2
import sys

class ErrorHandler:
    """Schema validation error/warning messages handler"""

    def __init__(self):
        """Initializes an L{ErrorHandler} object."""

        self.error_list = []
        self.warning_list = []

    def error(self, msg, data=None):
        """Method used to store error messages

        @type msg: string 
        @param msg: Error message to store.
        @type data: None 
        @param data: Ignored parameter.
        """
        self.error_list.append(msg)

    def warning(self, msg, data=None):
        """Method used to store warning messages

        @type msg: string 
        @param msg: Warning message to store.
        @type data: None 
        @param data: Ignored parameter.
        """
        self.warning_list.append(msg)

def validateOVF(schema_file, ovf_file, handler=None):
    """
    OVF schema validation.

    @type   schema_file: string
    @param  schema_file: OVF Schema path.
    @type   ovf_file: string
    @param  ovf_file: OVF file path.
    @type   handler: L{ErrorHandler} 
    @param  handler: object used to return validation 
            error and warning messages.
    @rtype:     int
    @return:    Error Code. 0 (zero) is OK.
    """

    ctxt_parser = libxml2.schemaNewParserCtxt(schema_file)
    ctxt_schema = ctxt_parser.schemaParse()
    del ctxt_parser

    validator  = ctxt_schema.schemaNewValidCtxt()

    if not handler:
        handler = ErrorHandler()

    validator.setValidityErrorHandler(handler.error, handler.warning)
 
    # Test valid document
    ret = validator.schemaValidateFile(ovf_file, 0)

    del ctxt_schema
    del validator 

    return ret

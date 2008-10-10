# vi: ts=4 expandtab syntax=python
##############################################################################
# Copyright (c) 2008 IBM Corporation
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
# Sharad Mishra (IBM) - initial implementation
##############################################################################

"""
Module to hold constants.
"""

XSI_KEY = "xmlns:xsi"
XSI_VAL = "http://www.w3.org/2001/XMLSchema-instance"

ENV_KEY = "xmlns:ovfenv"
ENV_VAL = "http://schemas.dmtf.org/ovf/environment/1"

STR_KEY = "xmlns:ovfstr"
STR_VAL = "http://schema.dmtf.org/ovf/strings/1"

NS_KEY = "xmlns"
NS_VAL = "http://schemas.dmtf.org/ovf/environment/1"

ENV_SEC = "Environment"
ENT_SEC = "Entity"
PLAT_SEC = "PlatformSection"
PROP_SEC = "PropertySection"

PLAT_INFO_ERR = "The platform list must contain at least one property."
PLAT_CREATE_ERR = "Failed to create PlatformSection element."
PLAT_ERROR = "Error creating PlatformSection..."

MISSING_ELEMENT = "Element name was not provided."
MISSING_TAG = "Given tag was not found in the document tree."
MISSING_ID = "Given id was not found in the document tree."

PROPERTY_INFO_ERR = "Missing properties for PropertySection."
PROPERTY_CREATE_ERR = "Failed to create PropertySection element."
PROPERTY_ERROR = "Error creating PropertySection..."

MISSING_ENV = "The environment document has not been initialized."
MISSING_SECTION = "No section node provided."
NO_ENVID = "No id provided as input to the method."
MISSING_DICT = "Dictionary object provided as input is None."
MISSING_DATA = "No data provided."
MISSING_NAME = "No element name provided."
ID_REQUIRED = "Id is required for creating Entity section."

ENT_EXISTS = "Entity with given ID already exists."

PROPERTY = "Property"
PREFIX = "ovfenv:"
CREATE_FAILED = "Failed to create a new element."
MISSING_PROPERTY = "Given property does not exist."
ENV_SCHEMA = "../../schemas/ovf-environment.xsd"
ID = "ovfenv:id"
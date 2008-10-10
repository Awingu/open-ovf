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

"""OVF Environment PlatformSection representation"""

ORDERED_ELEMENTS = ("Kind", "Version", "Vendor", "Locale", "Timezone")
#:List of ordered elements that can be members of Platform Section.

class PlatformSection(object):
    """OVF Environment PlatformSection class"""

    __slots__ = ORDERED_ELEMENTS
    platDict = {} #: Store the elements as dict.

    def __init__(self, data=None):
        """ Initialize the PlatformSection."""
        if data:
            self.update(data)


    def update(self, data):
        """Method to update attributes based in the dictionary
        passed as argument

        @param data: dictionary with new values.
        @type data: dict
        """
        for key, value in data.iteritems():
            setattr(self, key, value)
            self.platDict[key] = value


    def iteritems(self):
        """Make this object iterable, like in a dict.
        The iterator is ordered as required in the schema.

        @return: iterable (key, value) pairs
        """
        ret = []
        for key in self.__slots__:
            try:
                value = getattr(self, key)
                ret.append((key, value))
            except AttributeError:
                continue

        return ret

    def __setattr__(self, name, value):
        """Overrides method in order to ensure Timezone's type
        as required in the OVF spec.
        """

        if name == "Timezone":
            try:
                int(value)
            except ValueError:
                raise ValueError("Timezone must be an integer-like value")

        object.__setattr__(self, name, value)


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
"""Module to handle ovf command line interface"""

import sys
from optparse import OptionParser
from ovf import Ovf

GENERIC_USAGE = "usage: %prog command -f <Ovf file path> [options]"

class CLI:
    """Main class for handling ovf command line interface"""

    def __init__(self, commands, common, usage=None, version=None):
        """


        @param commands: subcommand specification
        @type commands: dict

        @param common: arguments in common to all subcommands
        @type common: tuple of dicts
        """

        self.commands = commands
        self.common = common
        self.usage = usage or GENERIC_USAGE
        self.version = version

    def getAllCmdArgs(self, cmd):
        """Method to return an integrated argument list.

        @param cmd: Command name
        @type cmd: str

        @return: a single list containing both the specific
                 and common arguments for a specified command.
        @rtype: list
        """

        try:
            allArgs = self.commands[cmd]['args'] + self.common
        except KeyError:
            return []

        return allArgs

    def checkRequiredArgs(self, cmd, options):
        """Return a list of missing required arguments for a
        specified command. Returns an empty if all required
        args were set or if there is no required argument.

        @param cmd: Command name
        @type cmd: str

        @param options: object returned by OptionParser.parse_args(),
                        containing the values set by the user.
        @type options: optparse.Values

        @return: list of missing required arguments
        @rtype: list
        """
        ret = []

        for opt in self.getAllCmdArgs(cmd):
            # If not required, there is nothing to check
            if not opt.get('required', False):
                continue

            dest = opt['parms']['dest']
            value = getattr(options, dest)

            # If Required and has some value, we're done
            if value:
                continue

            # otherwise, add to the missing list
            flag = opt['flags'][0]
            ret.append(flag)

        return ret

    def _parseCommand(self, args):
        """Method to parse only the command. If the command
        specified does not exists exit with status 2.

        @param args: Arguments passed
        @type args: list

        @return: Command name
        @rtype: str
        """

        parser = OptionParser(self.usage, version = self.version)
        for opt in self.commands:
            parser.add_option("--" + opt, help = self.commands[opt]['help'],
                 action="store_const", const=opt, dest="cmd")

        try:
            cmdStr = args[0]
        except IndexError:
            parser.print_help()
            sys.exit(2)

        options, args = parser.parse_args([ cmdStr ])

        return options.cmd

    def _parseSubcommand(self, command, args):
        """Method to parse a command specific arguments

        @param command: Command name
        @type command: str

        @param args: Arguments passed
        @type args: list

        @return: Tuple (options, args), as returned by
                 OptionParser.parse_args()
        @rtype: tuple
        """

        parser = OptionParser(self.usage)

        for opt in self.getAllCmdArgs(command):
            parser.add_option(*opt['flags'], **opt['parms'])

        (options, args) = parser.parse_args(args)

        missing = self.checkRequiredArgs(command, options)
        if missing:
            errMsg =  "%s are required" % ", ".join(missing)
            parser.error(errMsg)

        return (options, args)

    def parseArgs(self, args=None):
        """Method to actually parse the arguments.
        In case it finds

        @param args: Arguments (defaults to sys.argv[1:])
        @type args: list

        @return: tuple (command, options, args).
                 command: the command name specified,
                 options: command options, as returned by
                 OptionParser.parse_args().
                 pArgs: a list of positional args, as
                 returned by OptionParser.parse_args().
        @rtype: tuple
        """

        # if args is not specified use sys.argv
        args = args or sys.argv[1:]

        cmd = self._parseCommand(args)
        options, pArgs = self._parseSubcommand(cmd, args[1:])

        return cmd, options, pArgs
class MultipleNodeError(Exception):
    """
    This error class will be used to print information about multiple
    similar nodes being found.
    """
    def __init__(self,nodeList,baseMessage=None):
        """
        Create the objects for the class.
        """
        self.baseMessage = baseMessage
        self.nodeList = nodeList

        if baseMessage == None:
            baseMessage =("More than 1 Node was found please use"+
                      " --node-number flag to specify which node.")
        i = 0
        errMsg = baseMessage
        for node in nodeList:
            info = '\n Node '+str(i)+': '
            try:
                info += Ovf.getNodes(node, 'Info')[0].firstChild.data
            except IndexError:
                try:
                    info += (Ovf.getNodes(node, 'rasd:ElementName')[0].
                             firstChild.data)
                except IndexError:
                    try:
                        info += (Ovf.getNodes(node, 'vssd:ElementName')[0]
                                 .firstChild.data)
                    except IndexError:#we look for attributes to print
                        for key in node.attributes.keys():
                           info += key
                           info += '=' + str(node.attributes[key].value) + ' '
            i += 1
            errMsg += info

        self.message = errMsg

    def __str__(self):
        """
        This function will return the error message.
        """
        return self.message


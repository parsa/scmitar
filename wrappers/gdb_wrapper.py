# -*- coding: utf-8 -*-
#
# Scimitar: Ye Distributed Debugger
# 
# Copyright (c) 2016 Parsa Amini
# Copyright (c) 2016 Hartmut Kaiser
# Copyright (c) 2016 Thomas Heller
#
# Distributed under the Boost Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
import errors

class GDBWrapper(object):

    """Docstring for GDBWrapper. """

    def __init__(self):
        raise errors.CommandImplementationIncompleteError

    def launch_gdb(self, args):
        """Launch GDB.

        :args: arguments that will be use to launch GDB
        :returns: None

        """
        ## Build the command line and launch GDB
        #gdb_cmd += [gdb_config['attach'].format(pid = pid)]
        #cmd = ['ssh', node].extend(gdb_cmd)
        #cmd_str = ' '.join(cmd)

        #self.connection.PROMPT = gdb_config['mi_prompt_pattern']
        #self.connection.sendline(cmd_str)

        #self.remote_terminals.append(self.connection)
        raise errors.CommandImplementationIncompleteError


# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

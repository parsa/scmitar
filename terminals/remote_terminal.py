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
import paramiko
import errors

#ssh -t srvname ' cp ~/.bashrc ~/.scimitar_login &>/dev/null ; echo "LS_COLORS=\"no=00:fi=00:ETC:ETC:ETC\";" >> ~/.scimitar_login ; echo "export LS_COLORS" >> ~/.scimitar_login ; echo "alias ls=\"ls --color=auto\";" >> ~/.scimitar_login ; exec bash --rcfile ~/.scimitar_login'
class RemoteTerminal(object):


    def __init__(self, host):
        # NOTE: We're assuming host configurations are all in utils/config.py.
        # Try to get the configuration
        try:
            self.config = configuration.get_host_config(name)
        except configuration.HostNotConfiguredError:
            raise errors.BadArgsError(
                'remote',
                '{name} not found in "utils/config.py"'.format_map(
                    name = name
                )
            )
        # Establish the SSH connection
        try:
            self.terminal = sp.pxssh(echo = False)
            self.terminal.login(
                self.config.login_node, self.config.user,
                self.config.PS1
            )

            # Build the command line and launch GDB
            gdb_cmd += [gdb_config['attach'].format(pid = pid)]
            cmd = ['ssh', node].extend(gdb_cmd)
            cmd_str = ' '.join(cmd)

            self.terminal.PROMPT = gdb_config['mi_prompt_pattern']
            self.terminal.sendline(cmd_str)

        except sp.ExceptionPxssh as e:
            raise e


    def run(self, cmd):
        try:
            raise errors.CommandImplementationIncompleteError
        except paramiko.SSHException() as e:
            raise e

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

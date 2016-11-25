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
'''
module scimitar.session.offline_session

This module contains code used by the main Scimitar procedure. The code in
this module is executed in offline mode i.e. when Scimitar no debugging
session is active and while being idle.
'''

from . import modes, local_session as _local_s, remote_session as _remote_s
from .exceptions import *
from util import config, print_ahead
import pexpect.pxssh as sp
import pexpect as lp
import pty


class Terminal():
    pass


class LocalTerminal(Terminal):

    def __init__():
        self.connection = pty.spawn('')
        #self.agent = lp.spawn('bash')
        pass

    def execute(self, cmd):
        if '\n' in cmd:
            self.connection.println(
                '__cmd_func__(){\n%s\n' % cmd +
                '}; echo __"cmd_start"__; __cmd_func__; echo __"cmd_end"__; unset -f __cmd_func__'
            )
        else:
            self.connection.println(
                'echo __"cmd_start"__; %s; echo __"cmd_end"__' % cmd
            )

        resp = ''
        while not '__cmd_start__\r\n' in resp:
            resp += self.connection.read()

        resp = resp[resp.find('__cmd_start__\r\n') + 15:
                    ] # 15 == len('__cmd_start__\r\n')

        while not '_cmd_end__' in resp:
            resp += self.connection.read()

        return resp[:resp.find('__cmd_end__')]

    def sendline():
        pass


class RemoteTerminal(Terminal):

    def __init__():
        pass

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

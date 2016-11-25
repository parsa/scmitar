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
from .exceptions import *
from . import modes
from util import configuration, print_ahead
import pexpect as sp


#############################
# mode: local
#############################
def attach(args):
    raise CommandImplementationIncompleteError


def quit(args):
    raise CommandImplementationIncompleteError


commands = {
    'attach': attach,
    'quit': quit,
}


def process(cmd, args):
    raise CommandImplementationIncompleteError
    #return (modes.local, None)


# FIXME: Disabled for now
# MERGE: local_session (8c110db273af4a81bea68ef8686f1beb)
def launch(pids):
    """Not active in this version"""
    global session

    session = LocalSession()
    raise CommandImplementationIncompleteError
    #for pid in pids:
    #    new_session = _local.LocalSession(pid)
    #_sessions.append(new_session)


def quit(args):
    raise CommandImplementationIncompleteError


class LocalSession():

    def __init__(self):
        self.terminals = None
        self.active_terminal = None
        self.connect_one()

    @classmethod
    def attach_to_pids(cls, pids):
        raise CommandImplementationIncompleteError

    def query(self, msg):
        self.active_terminal.sendline(msg)
        self.active_terminal.prompt()
        return self.conn.before

    def connect_one(self):
        try:
            gdb_cmd = configuration.settings['gdb']['cmd']
            cmd_str = ' '.join(gdb_cmd)
            conn = sp.spawn(cmd_str)
            conn.expect('\s{1,2}\(gdb\) \s{1,2}')
            conn.setecho(False)
            if self.terminals:
                self.terminals.append(conn)
            else:
                self.terminals = [conn]
            self.active_terminal = conn
        except Exception as e:
            raise e

    def connect_all(self):
        raise CommandImplementationIncompleteError

    def __enter__(self):
        raise CommandImplementationIncompleteError

    def __exit__(self):
        raise CommandImplementationIncompleteError

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

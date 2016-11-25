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
import modes
import console


def ls(args):
    raise errors.CommandImplementationIncompleteError


def switch(args):
    raise errors.CommandImplementationIncompleteError


def end(args):
    raise errors.CommandImplementationIncompleteError
    #return (modes.offline, None)


def quit(args):
    console.close_all_sessions()

    return (modes.quit, None)


def gdb_exec(cmd):
    cs = console.get_current_session()
    msg = cs.query(' '.join(cmd))
    return modes.debugging, msg


def debug(args):
    import pdb
    pdb.set_trace()
    return modes.quit, None


commands = {
    'ls': ls,
    'switch': switch,
    'debug': debug, # HACK: For debugging only
    'end': end,
    'quit': quit,
}

def process(cmd, args):
    if cmd in commands:
        return commands[cmd](args)
    else:
        return gdb_exec([cmd] + (args or []))
    #raise errors.UnknownCommandError(cmd)
    raise errors.CommandImplementationIncompleteError

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

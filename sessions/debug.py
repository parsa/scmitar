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
import mi_interface


def ls(args):
    raise errors.CommandImplementationIncompleteError


def switch(args):
    # Verify command syntax
    if len(args) != 1:
        raise errors.BadArgsError('switch', 'switch <session_id>')

    try:
        id = int(args[0])
    except ValueError:
        raise errors.BadArgsError('switch', 'switch <session_id>')

    session_list = console.list_sessions()
    if id >= len(session_list):
        raise errors.BadArgsError('switch', 'No such session exists.')

    console.current_session_id = id
    return modes.debugging, 'Switched to session #' + str(id)


def end(args):
    for s in console.list_sessions():
        s.query('-gdb-exit')
    return modes.offline, None


def quit(args):
    for s in console.list_sessions():
        s.query('-gdb-exit')
    console.close_all_sessions()

    return modes.quit, None


def gdb_exec(cmd):
    cs = console.get_current_session()
    gdb_response = cs.query(' '.join(cmd))
    indrec, cout, tout, lout = mi_interface.parse(gdb_response)
    return modes.debugging, cout


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

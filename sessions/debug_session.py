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


session_dict = None
current_session_tag = None


def init_session_dict(current_tag):
    global current_session_tag
    global session_dict

    if not session_dict:
        session_dict = {}
        for s in console.list_sessions():
            session_dict[s.tag] = s

    current_session_tag = current_tag


def ls(args):
    ls_out = []
    for x in session_dict.itervalues():
        ls_out.append('%6s' % ((x.tag if x.tag == current_session_tag else ('(*) ' + x.tag))) + ') ' + x.host + ':' + str(x.meta))
    return modes.debugging, 'Sessions:\n' + '\n'.join(ls_out)


def switch(args):
    # Verify command syntax
    if len(args) != 1:
        raise errors.BadArgsError('switch', 'switch <session_id>')

    id = args[0]

    if not session_dict.has_key(id):
        raise errors.BadArgsError('switch', 'No such session exists.')

    global current_session_tag
    current_session_tag = id
    return modes.debugging, 'Switch to session #' + current_session_tag


def end(args):
    for s in console.list_sessions():
        s.query('-gdb-exit')
    session_dict = None
    return modes.offline, None


def quit(args):
    for s in console.list_sessions():
        s.query('-gdb-exit')
    console.close_all_sessions()
    session_dict = None

    return modes.quit, None


def gdb_exec(cmd):
    if not session_dict.has_key(current_session_tag):
        raise errors.BadArgsError('switch', 'This session is dead.')
        
    cs = session_dict[current_session_tag]
    gdb_response = cs.query(' '.join(cmd))
    if gdb_response in (r'^exit', r'^kill'):
        session_dict.pop(current_session_tag)
        raise errors.CommandFailedError('switch', 'Session died.')
    indrec, cout, tout, lout = mi_interface.parse(gdb_response)

    if indrec[0] == mi_interface.indicator_error:
        raise errors.CommandFailedError(indrec[1])
    elif indrec[0] == mi_interface.indicator_exit:
        session_dict.pop(current_session_tag)
        raise errors.CommandFailedError('switch', 'Session died.')
    return modes.debugging, cout


def debug(args):
    import pdb
    pdb.set_trace()
    return modes.debugging, None


commands = {
    'ls': ls,
    'switch': switch,
    'debug': debug, # HACK: For debugging only
    'end': end,
    'quit': quit,
}

def process(cmd, args):
    if not current_session_tag:
        raise errors.CommandFailedError('Unable to find the current session. Debugger start failed. (Maybe init_session_dict was not called?)')
    if cmd in commands:
        return commands[cmd](args)
    else:
        return gdb_exec([cmd] + (args or []))
    #raise errors.UnknownCommandError(cmd)
    raise errors.CommandImplementationIncompleteError

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

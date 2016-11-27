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

session_manager = None
current_session_tag = None


def init_session_dict(mgr):
    global current_session_tag
    global session_manager

    session_manager = mgr
    current_session_tag = mgr.get_oldest().tag

    return modes.debugging, None


def _ls_out():
    ls_out = []
    for s_i in session_manager.ls_sessions():
        if s_i.tag != current_session_tag:
            ls_head = s_i.tag
        else:
            ls_head = '(*) ' + s_i.tag
        ls_out.append('%6s) %s:%d' % (
            ls_head,
            s_i.hostname,
            s_i.meta,
        ))
    return '\n'.join(ls_out)


def ls(args):
    return modes.debugging, 'Sessions:\n' + _ls_out()


def switch(args):
    # Verify command syntax
    if len(args) != 1:
        raise errors.BadArgsError('switch', 'switch <session_id>')

    id = args[0]

    if not session_manager.exists(id):
        raise errors.BadArgsError('switch', 'No such session exists.')

    global current_session_tag
    current_session_tag = id
    return modes.debugging, 'Switch to session #%s\n%s' % (
        current_session_tag, _ls_out()
    )


def _kill_all():
    for s_i in session_manager.ls_sessions():
        if s_i.is_alive():
            s_i.query('-gdb-exit')
    session_manager.kill_all()

    global session_manager
    session_manager = None


def end(args):
    _kill_all()
    return modes.offline, None


def quit(args):
    _kill_all()
    return modes.quit, None


def gdb_exec(cmd):
    if not session_manager.exists(current_session_tag):
        raise errors.BadArgsError('gdb_exec', 'This session is dead.')

    cs = session_manager.get(current_session_tag)
    gdb_response = cs.query(' '.join(cmd))
    if gdb_response in (r'^exit', r'^kill'):
        session_manager.rm(current_session_tag)
        raise errors.CommandFailedError('gdb_exec', 'Session died.')
    indrec, cout, tout, lout = mi_interface.parse(gdb_response)

    if indrec[0] == mi_interface.indicator_error:
        raise errors.CommandFailedError('gdb_exec', indrec[1])
    elif indrec[0] == mi_interface.indicator_exit:
        session_manager.rm(current_session_tag)
        raise errors.CommandFailedError('gdb_exec', 'Session died.')
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
        raise errors.CommandFailedError(
            'Unable to find the current session. Debugger start failed. (Maybe init_session_dict was not called?)'
        )
    if cmd in commands:
        return commands[cmd](args)
    else:
        return gdb_exec([cmd] + (args or []))
    #raise errors.UnknownCommandError(cmd)
    raise errors.CommandImplementationIncompleteError

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

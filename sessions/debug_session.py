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

from collections import deque
import threading

import errors
import modes
import console
import mi_interface as mi
from config import settings
from command_completer import CommandCompleter
from util import format_error, format_warning, format_info, repr_str_dict

session_manager = None
selected_sessions = None
sessions_history = None

history_length = int(settings['sessions']['history_length'])


def init_debugging_mode(mgr, msgs):
    global selected_sessions
    global session_manager
    global sessions_history

    session_manager = mgr
    sessions_history = {}

    oldest_session = mgr.get_oldest()
    if oldest_session:
        selected_sessions = [oldest_session.tag]

    for tag in session_manager.list_session_tags():
        sessions_history[tag] = deque(maxlen = history_length)
        sessions_history[tag].append(msgs[tag])

    return modes.debugging, None


def _ls_out():
    ls_out = []
    for s_i in session_manager.list_sessions():
        if not s_i.tag in selected_sessions:
            ls_head = s_i.tag
        else:
            ls_head = '(*) {}'.format(s_i.tag)
        ls_out.append('%6s) %s:%d' % (
            ls_head,
            s_i.hostname,
            s_i.meta,
        ))
    return '\n'.join(ls_out)


def list_sessions(args):
    # Verify command syntax
    if len(args) != 0:
        raise errors.BadArgsError(
            'ls', 'This command does not accept arguments'
        )

    pretty_session_list = _ls_out()
    if not pretty_session_list:
        return modes.debugging, 'ls: Empty. No sessions are alive.'
    return modes.debugging, 'Sessions:\n' + pretty_session_list


def select_session_complete(args):
    if not args:
        return ['all', 'none'] + session_manager.list_session_tags()

    # If 'all' then no further arguments are meaningful
    if 'all' in args or 'none' in args:
        return []

    if 'all'.startswith(args[0]):
        return ['all']

    if 'none'.startswith(args[0]):
        return ['none']

    return [
        tag for tag in session_manager.list_session_tags() if not tag in args
    ]


def select_session(args):
    # Verify command syntax
    if not args:
        raise errors.BadArgsError(
            'select', 'select all | none | <session id>[ <session id>[ ...]]'
        )

    if args:
        if args[0] == 'all':
            global selected_sessions
            selected_sessions = sorted(session_manager.list_session_tags())

            return modes.debugging, 'Selected session(s) #{0}\n{1}'.format(
                ', '.join(selected_sessions), _ls_out()
            )
        elif args[0] == 'none':
            global selected_sessions
            selected_sessions = []

            return modes.debugging, 'No sessions selected'.format(
                ', '.join(selected_sessions), _ls_out()
            )

    non_existing_sessions = [
        id for id in args if not session_manager.exists(id)
    ]
    if non_existing_sessions:
        raise errors.BadArgsError(
            'select', 'Session(s) {0} do not exist.'.
            format(', '.join(non_existing_sessions))
        )

    global selected_sessions
    selected_sessions = args
    return modes.debugging, 'Selected session(s) #{0}\n{1}'.format(
        ', '.join(selected_sessions), _ls_out()
    )


def _kill_all():
    for s_i in session_manager.list_sessions():
        if s_i.is_alive():
            s_i.query('-gdb-exit')
    session_manager.kill_all()

    global session_manager
    session_manager = None


def end_sessions(args):
    # Verify command syntax
    if len(args) != 0:
        raise errors.BadArgsError(
            'ls', 'This command does not accept arguments'
        )

    _kill_all()
    return modes.offline, None


def quit(args):
    # Verify command syntax
    if len(args) != 0:
        raise errors.BadArgsError(
            'ls', 'This command does not accept arguments'
        )

    _kill_all()
    return modes.quit, None


def _ensure_sessions_selected(cmd):
    if not selected_sessions:
        raise errors.CommandFailedError(
            cmd,
            'No session(s) selected. Debugging mode failed to start. (Maybe init_debugging_mode() was not called?)'
        )

def _ensure_valid_sessions_selected(cmd):
    non_existing_sessions = [
        id for id in selected_sessions if not session_manager.exists(id)
    ]
    if non_existing_sessions:
        raise errors.BadArgsError(
            cmd, 'Cannot proceed. Dead session(s): {0}.'.
            format(', '.format(non_existing_sessions))
        )

def message_history(args):
    _ensure_sessions_selected('history')

    index = -1
    if len(args) == 1:
        try:
            index = -int(args[0])
        except ValueError:
            raise errors.BadArgsError(
                'history', 'history[ <index>]'
            )

    if index > history_length:
        raise errors.BadArgsError(
            'history', 'Selected record does not exist in the history'
        )

    results = []
    for tag in selected_sessions:
        # Output header
        results.append('~~~ Scimitar - Session: {} ~~~'.format(tag))
        try:
            ind_rec, cout, tout, lout = sessions_history[tag][index]
            if ind_rec:
                # Check the type of indicator
                if ind_rec[0] == mi.indicator_error:
                    results.append(format_error(ind_rec[1]))
                elif ind_rec[0] == mi.indicator_exit:
                    session_manager.remove(tag)
                    results.append(format_error('Session {} died.', tag))
                else:
                    results.append(cout)
            else:
                results.append(''.join([cout, tout, lout]))
        except IndexError:
            results.append(format_error('Scimitar: Record does not exist'))
    return modes.debugging, '\n'.join(results)


def gdb_exec(cmd):

    class RemoteCommandExecutingThread(threading.Thread):
        '''This thread type is responsible for running commands on terminal
        '''

        def __init__(self, term, cmd):
            super(RemoteCommandExecutingThread, self).__init__()
            self.term = term
            self.cmd = cmd
            self.error = None
            self.result = None

        def run(self):
            try:
                self._run()
            except Exception as e:
                self.error = e

        def _run(self):
            # Send the command
            gdb_response = self.term.query(self.cmd)
            # In case GDB dies 
            if gdb_response in (r'^exit', r'^kill'):
                raise console.SessionDiedError
            else:
                self.result = mi.parse(gdb_response)

        def report(self):
            if self.error:
                raise self.error
            return self.result

    def _sanitize_gdb_command(cmd):
        if cmd and not repr_str_dict.has_key(cmd[0]):
            return ['-interpreter-exec', 'console'] + cmd
        return cmd

    def _parallel_exec_async(cmd, tag, target_sessions):
        tasks = {}
        for tag in target_sessions:
            # Get the session
            cs = session_manager.get(tag)
            exctr = RemoteCommandExecutingThread(cs, ' '.join(cmd))
            exctr.start()
            tasks[tag] = exctr
        return tasks

    def _collect_exec_results(tasks):
        # If sessions died during execution collect them
        session_casualties = []
        # Results
        results = []

        # Go through the results
        for tag, task in tasks.iteritems():
            task.join()
            try:
                mi_response = task.report()
                # Add it to message history stash
                sessions_history[tag].append(mi_response)
                # Output header
                results.append('~~~ Scimitar - Session: {} ~~~'.format(tag))
                ind_rec, cout, tout, lout = mi_response
                # Check the type of indicator
                if ind_rec[0] == mi.indicator_error:
                    results.append(format_error(ind_rec[1]))
                elif ind_rec[0] == mi.indicator_exit:
                    session_manager.remove(tag)
                    results.append(format_error('Session {} died.', tag))
                else:
                    results.append(cout)
            except console.SessionDiedError:
                # It is not a session we can work with in future
                session_manager.remove(tag)
                selected_sessions.remove(tag)
                # Add this session to killed sessions
                session_casualties += [tag]
        return results, session_casualties

    #
    # gdb_exec starts here
    #

    # Ensure there are selected sessions
    _ensure_sessions_selected('gdb:cmd(?)')
    # Make sure selected sessions are valid
    _ensure_valid_sessions_selected('gdb:cmd(?)')

    # GDB launch command
    cmd = _sanitize_gdb_command(cmd)

    # Threads that run the command
    tasks = _parallel_exec_async(cmd, tag, selected_sessions)

    # Wait for all commands to finish
    session_casualties, results = _collect_exec_results(tasks)

    # In case we had dead sessions the command has essentially failed.
    if session_casualties:
        results.append(
            format_error(
                'Session(s) {} died.', ', '.join(session_casualties)
            )
        )
    return modes.debugging, '\n'.join(results)


def debug(args):
    import pdb
    pdb.set_trace()
    return modes.debugging, None


commands = {
    'ls': (list_sessions, None),
    'select': (select_session, select_session_complete),
    'debug': (debug, None), # HACK: For debugging only
    'history': (message_history, None),
    'end': (end_sessions, None),
    'quit': (quit, None),
}


def process(cmd, args):
    if cmd in commands:
        return commands[cmd][0](args)
    else:
        return gdb_exec([cmd] + (args or []))
    raise errors.CommandImplementationIncompleteError


class DebugSessionCommandCompleter(CommandCompleter):

    def _complete_command(self):
        return commands.keys()

    def _complete_command_arguments(self, cmd, args):
        if commands.has_key(cmd) and commands[cmd][1]:
            return commands[cmd][1](args)

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

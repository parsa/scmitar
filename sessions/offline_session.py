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
import re
import modes
import errors
import pexpect
import console
import mi_interface
import debug_session
import schedulers.investigator as csssi # chief scimitar scheduler system investigator
from util import print_ahead, print_out, print_info, print_warning
from config import settings
from command_completer import CommandCompleter

gdb_config = settings['gdb']
hops = console.HopManager()
default_terminal = None
default_terminal_scheduler = None


def _establish_default_terminal(reestablish = False):
    global default_terminal
    if not default_terminal:
        default_terminal = console.Terminal(hops.ls())
        default_terminal.connect()
    elif reestablish:
        global default_terminal_scheduler
        default_terminal.close()

        default_terminal_scheduler = None
        default_terminal = None


def _cleanup_default_terminal():
    if default_terminal:
        default_terminal.close()


def _ensure_scheduler_exists(cmd):
    if not default_terminal_scheduler:
        try:
            global default_terminal_scheduler
            default_terminal_scheduler = csssi.detect_scheduler(
                default_terminal
            )
        except csssi.NoSchedulerFoundError:
            if not cmd:
                return False
            raise errors.CommandFailedError(
                cmd,
                'Unable to detect the scheduling system type on this machine.'
            )
    return True


def job_complete(args):
    if len(args) > 1:
        return []
    _establish_default_terminal()
    if not _ensure_scheduler_exists(None):
        return []
    return ['auto'] + csssi.ls_user_jobs(default_terminal)


def job(args):
    # Verify command syntax
    if len(args) > 2:
        raise errors.BadArgsError('job', 'job[ <job_id> | <auto>[ <app>]]')

    pid_dict = None

    _establish_default_terminal()
    _ensure_scheduler_exists('job')
    if len(args) == 0 or args[0] == 'auto':
        try:
            job_id = csssi.detect_active_job(default_terminal)
        except csssi.NoActiveJobError:
            raise errors.CommandFailedError(
                'job', 'No active user jobs found. Cannot proceed.'
            )
        except csssi.MoreThanOneActiveJobError:
            raise errors.CommandFailedError(
                'job', 'Found more than one job. Cannot proceed.'
            )
    else:
        job_id = args[0]
    app = args[1] if len(args) == 2 else None
    try:
        pid_dict = csssi.ls_job_pids(default_terminal, job_id, app)
    except csssi.InvalidJobError:
        raise errors.CommandFailedError(
            'job', '{0} does not seem to be a valid job id'.format(job_id)
        )
    except csssi.NoRunningAppFoundError:
        raise errors.CommandFailedError(
            'job', 'Unable to find an MPI application running in job {0}'.
            format(job_id)
        )

    # Launch GDB and attach to PIDs
    session_manager = _attach_pids(pid_dict)

    # Initialize the debugging session
    return debug_session.init_session_dict(session_manager)


def list_jobs(args):
    # Verify command syntax
    if len(args) > 0:
        raise errors.BadArgsError(
            'jobs', 'This command does not accept arguments.'
        )

    _establish_default_terminal()
    _ensure_scheduler_exists('jobs')
    items = csssi.ls_user_jobs(default_terminal)
    jobs_str = ('\n    ' + '\n    '.join(items)) if items else '\r\n    None'
    return modes.offline, 'Current jobs:' + jobs_str


def _find_dead_pids_host(host, pids):
    dead_pids = []

    _establish_default_terminal()
    _ensure_scheduler_exists('jobs')
    for pid in pids:
        if not default_terminal.is_pid_alive(pid):
            host_path = '.'.join(hops.ls())
            if host:
                host_path += '.' + host
            dead_pids.append(
                '{host}:{pid}'.format(
                    host = host_path or 'localhost', pid = pid
                )
            )
    return dead_pids


def _find_dead_pids(pid_dict):
    # Check the status of all provided PIDs
    dead_pids = []
    for host, pids in pid_dict.iteriterms():
        # Establish a connection per each process
        dead_pids.extend(_find_dead_pids_host(host, pids))
    return dead_pids


def _attach_pid(host, pid, tag, cmd):
    term = console.Terminal(
        hops.ls(), target_host = host, meta = pid, tag = tag
    )
    term.connect()

    term.exit_re = r'&"quit\n"|\^exit'
    term.prompt_re = r'\(gdb\)\ \r\n'
    gdb_response = term.query(cmd)
    try:
        mi_response = mi_interface.parse(gdb_response)
        return term, mi_response
    except pexpect.ExceptionPexpect as e:
        raise errors.CommandFailedError('attach', 'attach', e)


def _attach_pids(pid_dict):
    mgr = console.SessionManager()

    gdb_cmd = gdb_config['cmd']
    gdb_attach_tmpl = gdb_config['attach']

    tag_counter = 0

    # Start GDB instances
    for host in pid_dict.iterkeys():
        for pid in pid_dict[host]:
            tag_counter += 1

            # Build the command line and launch GDB
            cmd = gdb_cmd + [gdb_attach_tmpl.format(pid = pid)]
            cmd_str = ' '.join(cmd)

            print_info(
                'Host "{host}", Process "{pid}"...',
                host = host or 'localhost',
                pid = pid
            )

            session, mi_response = _attach_pid(
                host, pid, str(tag_counter), cmd_str
            )
            mgr.add(session)
            r, c, t, l = mi_response

            print_out(''.join([c, t, l]))

    print_info('Hosts connected. Debugging session starting...')
    return mgr


def _parse_group_pids(expr):
    pid_dict = {}
    for app_instance in re.finditer('((?:(\w+):)?(\d+))', expr):
        host = app_instance.group(2)
        pid = int(app_instance.group(3))

        if pid_dict.has_key(host):
            pid_dict[host] += [pid]
        else:
            pid_dict[host] = [pid]


def attach(args):
    args_string = ' '.join(args)
    # Verify command syntax
    if len(args) < 1 or not re.match('(?:(?:\w+:)?\d+|\s)+', args_string):
        raise errors.BadArgsError(
            'attach', 'attach [<host>:]<pid>[ [<host>:]<pid> [...]]'
        )

    # Group by host
    pid_dict = _parse_group_pids(args_string)

    # Check the status of all provided PIDs
    dead_pids = _find_dead_pids(pid_dict)

    # Stop if all processes are alive
    if len(dead_pids) != 0:
        raise errors.CommandFailedError(
            'attach',
            'Invalid PIDs provided: {0}'.format(' ,'.join(dead_pids))
        )

    # Launch GDB and attach to PIDs
    session_manager = _attach_pids(pid_dict)

    # Initialize the debugging session
    return debug_session.init_session_dict(session_manager)


def quit(args):
    _cleanup_default_terminal()
    return modes.quit, None


def add_hop(args):
    # Verify command syntax
    if len(args) < 1:
        raise errors.BadArgsError('hop', 'hop <host>[ [<host> [...]]')

    for host in args:
        hops.add(host)

    _establish_default_terminal(reestablish = True)

    return modes.offline, None


def unhop(args):
    # Verify command syntax
    if len(args) > 1:
        raise errors.BadArgsError('unhop', 'unhop[ <number of hops to remove>].')

    n_hops_to_remove = 1
    if len(args) == 1:
        try:
            n_hops_to_remove = int(args[0])
        except ValueError:
            raise errors.BadArgsError(
                'unhop', 'unhop[ <number of hops to remove>].'
            )
    try:
        for _ in range(n_hops_to_remove):
            hops.rm()
    except console.NoHopsError:
        raise errors.CommandFailedError(
            'unhop', 'No more hops currently exist. Nothing can be removed'
        )

    _establish_default_terminal(reestablish = True)

    return modes.offline, None


def list_hops(args):
    # Verify command syntax
    if len(args) > 0:
        raise errors.BadArgsError(
            'unhop', 'This command does not accept arguments.'
        )

    items = hops.ls()
    hops_str = ('\n    ' + '\n    '.join(items)) if items else '\n    None'
    return modes.offline, 'Current hops:' + hops_str


def debug(args):
    import pdb
    pdb.set_trace()

    return modes.offline, None


commands = {
    'hop': (add_hop, None),
    'unhop': (unhop, None),
    'hops': (list_hops, None),
    'job': (job, job_complete),
    'jobs': (list_jobs, None),
    'attach': (attach, None),
    'debug': (debug, None), # HACK: For debugging only
    'quit': (quit, None),
}


def process(cmd, args):
    if cmd in commands:
        return commands[cmd][0](args)
    raise errors.UnknownCommandError(cmd)


class OfflineSessionCommandCompleter(CommandCompleter):

    def _complete_command(self):
        return commands.keys()

    def _complete_command_arguments(self, cmd, args):
        if commands.has_key(cmd) and commands[cmd][1]:
            return commands[cmd][1](args)

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

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
import threading
import pexpect

import modes
import errors
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
        default_terminal = console.Terminal(hops.list_hops())
        default_terminal.connect()
    elif reestablish:
        global default_terminal_scheduler
        default_terminal.close()

        default_terminal_scheduler = None
        default_terminal = None


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

    valid_choices = csssi.ls_user_jobs(default_terminal)
    if not valid_choices:
        return []

    return ['auto'] + valid_choices


def job(args):
    # Verify command syntax
    if len(args) > 2:
        raise errors.BadArgsError('job', 'job[ <job_id> | <auto>[ <app>]]')

    # Basic checks
    _establish_default_terminal()
    _ensure_scheduler_exists('job')

    # If job name is not provided then probably only one job is active
    if len(args) == 0 or args[0] == 'auto':
        try:
            job_id = csssi.detect_active_job(default_terminal)
        # No active jobs
        except csssi.NoActiveJobError:
            raise errors.CommandFailedError(
                'job', 'No active user jobs found. Cannot proceed.'
            )
        # More than one job is active
        except csssi.MoreThanOneActiveJobError:
            raise errors.CommandFailedError(
                'job', 'Found more than one job. Cannot proceed.'
            )
    # Job Id provided
    else:
        job_id = args[0]
    # In case app name is provided
    app = args[1] if len(args) == 2 else None

    # Hosts and PIDs will be stored here
    pid_dict = None

    # List job nodes and processes
    try:
        pid_dict = csssi.ls_job_pids(default_terminal, job_id, app)
    # Job does not exist
    except csssi.InvalidJobError:
        raise errors.CommandFailedError(
            'job', '{0} does not seem to be a valid job id'.format(job_id)
        )
    # Cannot determine app
    except csssi.NoRunningAppFoundError:
        raise errors.CommandFailedError(
            'job',
            'No application name lookup pattern provided and automatic MPI application detection did not succeed. Ensure job {0} is actually running a distributed application and provide the application name'.
            format(job_id)
        )

    # Launch GDB and attach to PIDs
    session_manager, msgs = _attach_pids(pid_dict)

    # Initialize the debugging session
    return debug_session.init_debugging_mode(session_manager, msgs)


def list_jobs(args):
    # Verify command syntax
    if args:
        raise errors.BadArgsError(
            'jobs', 'This command does not accept arguments.'
        )

    _establish_default_terminal()
    _ensure_scheduler_exists('jobs')
    items = csssi.ls_user_jobs(default_terminal)
    jobs_str = '\t'.join(items)
    return modes.offline, jobs_str


class _AttachPidThread(threading.Thread):

    def __init__(self, host, pid, tag, cmd):
        super(_AttachPidThread, self).__init__()
        self.host = host
        self.pid = pid
        self.tag = tag
        self.cmd = cmd
        self.error = None

        self.term = None
        self.mi_response = None

    def run(self):
        try:
            self.term = console.Terminal(
                hops.list_hops(),
                target_host = self.host,
                meta = self.pid,
                tag = self.tag,
                prompt_re = r'\(gdb\)\ \r\n',
                exit_re = r'&"quit\n"|\^exit',
            )
            self.term.connect()

            gdb_response = self.term.query(self.cmd)
            try:
                self.mi_response = mi_interface.parse(gdb_response)
            except pexpect.ExceptionPexpect as e:
                raise errors.CommandFailedError('attach', 'attach', e)
        except Exception as e:
            self.error = e

    def report(self):
        if self.error:
            raise self.error
        return self.term, self.mi_response


def _attach_pids(pid_dict):
    mgr = console.SessionManager()

    gdb_cmd = gdb_config['cmd']
    gdb_attach_tmpl = gdb_config['attach']

    tag_counter = 0

    tasks = {}
    msgs = {}

    # Start GDB instances
    for host in pid_dict.iterkeys():
        for pid in pid_dict[host]:
            tag_counter += 1
            tag = str(tag_counter)

            # Build the command line and launch GDB
            cmd = gdb_cmd + [gdb_attach_tmpl.format(pid = pid)]
            cmd_str = ' '.join(cmd)

            attach_pid_task = _AttachPidThread(host, pid, tag, cmd_str)
            tasks[tag] = attach_pid_task
            attach_pid_task.start()

    for tag, task in tasks.iteritems():
        print_info(
            'Connecting to Process "{pid}" on "{host}"...',
            host = task.host or 'localhost',
            pid = task.pid
        )

        task.join()
        print_info('Connected.')

        session, mi_response = task.report()

        mgr.add(session)
        msgs[tag] = mi_response
        r, c, t, l = mi_response
        print_out(''.join([c, t, l]))

    print_info('Beginning debugging session...')
    return mgr, msgs


def attach(args):

    def _find_dead_pids_host(host, pids):
        dead_pids = []

        _establish_default_terminal()
        _ensure_scheduler_exists('jobs')
        for pid in pids:
            if not default_terminal.is_pid_alive(pid):
                host_path = '.'.join(hops.list_hops())
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

    def _parse_group_pids(expr):
        pid_dict = {}
        for app_instance in re.finditer('((?:(\w+):)?(\d+))', expr):
            host = app_instance.group(2)
            pid = int(app_instance.group(3))

            if pid_dict.has_key(host):
                pid_dict[host] += [pid]
            else:
                pid_dict[host] = [pid]

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
    session_manager, msgs = _attach_pids(pid_dict)

    # Initialize the debugging session
    return debug_session.init_debugging_mode(session_manager, msgs)


def quit(args):

    def _cleanup_default_terminal():
        if default_terminal:
            default_terminal.close()

    _cleanup_default_terminal()
    return modes.quit, None


def hop(args):
    # List hops
    if not args:
        items = hops.list_hops()
        hops_str = '->'.join(items)
        return modes.offline, hops_str

    for host in args:
        hops.add(host)

    _establish_default_terminal(reestablish = True)

    return modes.offline, None


def unhop(args):
    # Verify command syntax
    if len(args) > 1:
        raise errors.BadArgsError(
            'unhop', 'unhop[ <number of hops to remove>].'
        )

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
            hops.remove_last()
    except console.NoHopsError:
        raise errors.CommandFailedError(
            'unhop', 'No more hops currently exist. Nothing can be removed'
        )

    _establish_default_terminal(reestablish = True)

    return modes.offline, None


def debug(args):
    import pdb
    pdb.set_trace()

    return modes.offline, None


commands = {
    'hop': (hop, None),
    'unhop': (unhop, None),
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

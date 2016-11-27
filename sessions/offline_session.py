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

gdb_config = settings['gdb']
base_machine = None


def _ensure_scheduler_exists(cmd, term):
    try:
        csssi.detect_scheduler(term)
    except csssi.NoSchedulerFoundError:
        raise errors.CommandFailedError(
            cmd, 'Unable to detect the scheduling system type on this machine.'
        )


def job(args):
    # Verify command syntax
    if len(args) > 2:
        raise errors.BadArgsError('job', 'job[ <job_id>[ <app>]]')

    pid_dict = None
    with console.Terminal() as term:
        _ensure_scheduler_exists('job', term)
        if len(args) == 0 or args[0] == 'auto':
            try:
                job_id = csssi.detect_active_job(term)
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
            pid_dict = csssi.ls_job_pids(term, job_id, app)
        except csssi.InvalidJobError:
            raise errors.CommandFailedError(
                'job',
                '{0} does not seem to be a valid job id'.format(job_id)
            )
        except csssi.NoRunningAppFoundError:
            raise errors.CommandFailedError(
                'job', 'Unable to find an MPI application running in job {0}'.
                format(job_id)
            )

    # Launch GDB and attach to PIDs
    _attach_pids(pid_dict)

    # Initialize the debugging session
    return debug_session.init_session_dict(console.get_oldest_session().tag)


def list_jobs(args):
    # Verify command syntax
    if len(args) > 0:
        raise errors.BadArgsError(
            'jobs', 'This command does not accept arguments.'
        )

    with console.Terminal() as term:
        _ensure_scheduler_exists('jobs', term)
        items = csssi.ls_user_jobs(term)
        jobs_str = ('\n    ' + '\n    '.join(items)
                    ) if items else '\r\n    None'
        return modes.offline, 'Current jobs:' + jobs_str


def _find_dead_pids_host(host, pids):
    dead_pids = []
    with console.Terminal(host) as term:
        for pid in pids:
            if not term.is_pid_alive(pid):
                host_path = '.'.join(console.list_hops())
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
    term = console.Terminal(target_host = host, meta = pid, tag = tag)
    term.connect()

    term.exit_re = r'&"quit\n"|\^exit'
    term.prompt_re = r'\(gdb\)\ \r\n'
    gdb_response = term.query(cmd)
    try:
        return mi_interface.parse(gdb_response)
    except pexpect.ExceptionPexpect as e:
        raise errors.CommandFailedError('attach', 'attach', e)


def _attach_pids(pid_dict):
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

            r, c, t, l = _attach_pid(host, pid, str(tag_counter), cmd_str)

            print_out(''.join([c, t, l]))

    print_info('Hosts connected. Debugging session starting...')


def attach(args):
    args_string = ' '.join(args)
    # Verify command syntax
    if len(args) < 1 or not re.match('(?:(?:\w+:)?\d+|\s)+', args_string):
        raise errors.BadArgsError(
            'attach', 'attach [<host>:]<pid>[ [<host>:]<pid> [...]]'
        )

    # Group by host
    pid_dict = {}
    for app_instance in re.finditer('((?:(\w+):)?(\d+))', args_string):
        host = app_instance.group(2) # or base_machine
        pid = int(app_instance.group(3))

        if pid_dict.has_key(host):
            pid_dict[host] += [pid]
        else:
            pid_dict[host] = [pid]

    # Check the status of all provided PIDs
    dead_pids = _find_dead_pids(pid_dict)

    # Stop if all processes are alive
    if len(dead_pids) != 0:
        raise errors.CommandFailedError(
            'attach',
            'Invalid PIDs provided: {0}'.format(' ,'.join(dead_pids))
        )

    # Launch GDB and attach to PIDs
    _attach_pids(pid_dict)

    # Initialize the debugging session
    return debug_session.init_session_dict(console.get_oldest_session().tag)


def quit(args):
    return modes.quit, None


def add_hop(args):
    # Verify command syntax
    if len(args) < 1:
        raise errors.BadArgsError('hop', 'hop <host>[ [<host> [...]]')

    for host in args:
        console.add_hop(host)

    return modes.offline, None


def pop_hop(args):
    # Verify command syntax
    if len(args) > 1:
        raise errors.BadArgsError('pop', 'pop[ <number of hops to remove>].')

    n_hops_to_remove = 1
    if len(args) == 1:
        try:
            n_hops_to_remove = int(args[0])
        except ValueError:
            raise errors.BadArgsError(
                'pop', 'pop[ <number of hops to remove>].'
            )

    try:
        for _ in range(n_hops_to_remove):
            console.pop_hop()
    except console.NoHopsError:
        raise errors.CommandFailedError(
            'pop', 'No more hops currently exist. Nothing can be removed'
        )
    except console.SessionsAliveError:
        raise errors.CommandFailedError(
            'pop', 'Cannot add a hop while there are active sessions.'
        )

    return modes.offline, None


def list_hops(args):
    # Verify command syntax
    if len(args) > 0:
        raise errors.BadArgsError(
            'pop', 'This command does not accept arguments.'
        )

    items = console.list_hops()
    hops_str = ('\n    ' + '\n    '.join(items)) if items else '\n    None'
    return modes.offline, 'Current hops:' + hops_str


def debug(args):
    import pdb
    pdb.set_trace()

    return modes.offline, None


commands = {
    'hop': add_hop,
    'pop': pop_hop,
    'hops': list_hops,
    'job': job,
    'jobs': list_jobs,
    'attach': attach,
    'debug': debug, # HACK: For debugging only
    'quit': quit,
}


def process(cmd, args):
    if cmd in commands:
        return commands[cmd](args)
    raise errors.UnknownCommandError(cmd)


def complete(self, text, state):
    response = None
    if state == 0:
        # If first time for this text build a match list.
        if text:
            self.matches = [
                s for s in commands.keys() if s and s.startswith(text)
            ]
        else:
            self.matches = commands.keys()[:]

    try:
        response = self.matches[state]
    except IndexError:
        response = None
    return response

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

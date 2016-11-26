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
from util import config, print_ahead, print_out, configuration
#######################
# mode: offline
#######################

base_machine = None

def job(args):
    # Verify command syntax
    if len(args) > 1:
        raise errors.BadArgsError('job', 'job\nor\njob <job_id>')

    if len(args) == 0:
        pass
    else:
        id = args[0]

    raise errors.CommandImplementationIncompleteError


def _find_dead_pids_host(host, pids):
    dead_pids = []
    with console.Terminal(host) as term:
        for pid in pids:
            if not term.is_pid_alive(pid):
                host_path = '.'.join(console.list_hops())
                if host:
                    host_path += '.' + host
                dead_pids.append('{host}:{pid}'.format(host=host_path or 'localhost', pid=pid))
    return dead_pids


def _find_dead_pids(pid_dict):
    # Check the status of all provided PIDs
    dead_pids = []
    for host, pids in pid_dict.iteriterms():
        # Establish a connection per each process
        dead_pids.extend(_find_dead_pids_host(host, pids))
    return dead_pids


def _attach_pids(pid_dict):
    tag_counter = 0
    for host in pid_dict.iterkeys():
        for pid in pid_dict[host]:

            tag_counter += 1

            # Start all GDB instances
            gdb_config = configuration.get_gdb_config()
            gdb_cmd = gdb_config['cmd']

            # Build the command line and launch GDB
            gdb_cmd += [gdb_config['attach'].format(pid = pid)]
            #cmd = ['ssh', host].extend(gdb_cmd)
            cmd_str = ' '.join(gdb_cmd)

            print_out('Host "{host}", Process "{pid}"...', host=host or 'localhost', pid=pid)

            term = console.Terminal(target_host=host, meta=pid, tag=str(tag_counter))
            term.connect()

            try:
                term.exit_re = r'&"quit\n"|\^exit'
                term.prompt_re = r'\(gdb\)\ \r\n'
                gdb_response = term.query(cmd_str)
                r, c, t, l = mi_interface.parse(gdb_response)
                print_out(''.join([c, t, l]))
            except pexpect.ExceptionPexpect as e:
                raise errors.CommandFailedError('attach', 'attach', e)


def attach(args):
    args_string = ' '.join(args)
    # Verify command syntax
    if len(args) < 1 or not re.match('(?:(?:\w+:)?\d+|\s)+', args_string):
        raise errors.BadArgsError('attach', 'attach [<host>:]<pid>[ [<host>:]<pid> [...]]')

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
            'attach', 'Invalid PIDs provided: {0}'.format(
            ' ,'.join(dead_pids)))

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
    if len(args) > 0:
        raise errors.BadArgsError('pop', 'No arguments.\r\nSyntax:\r\n\tpop')

    try:
        console.pop_hop();
    except errors.CommandFailedError as e:
        raise e

    return modes.offline, None


def list_hops(args):
    items = console.list_hops()
    hops_str = '\r\n    '.join(items) if items else '\r\n    None'
    return modes.offline, 'Current hops:' + hops_str


def debug(args):
    import pdb
    pdb.set_trace()

    return modes.offline, None


commands = {
    'chain': add_hop,
    'pop': pop_hop,
    'hops': list_hops,
    'job': job,
    'attach': attach,
    'debug': debug, # HACK: For debugging only
    'quit': quit,
}


def process(cmd, args):
    if cmd in commands:
        return commands[cmd](args)
    raise errors.UnknownCommandError(cmd)

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

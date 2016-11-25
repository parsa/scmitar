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
from . import modes, local_session as _local_s, remote_session as _remote_s
from .exceptions import *
from util import config, print_ahead
#######################
# mode: offline
#######################
# Valid commands:
## $ local <pid>[ <pid>...]
## $ remote <machine_name>
## $ remote <machine_name> <jobid>
## $ remote <machine_name> attach <node:pid>[ <node:pid>...]
## $ quit

# Are we doing whatever we're doing locally or over SSH
# helps us to choose between pxssh/pexpect
is_this_ssh = False


def connect(args):
    pass


def end(args):
    pass


def raw(args):
    pass


def pin(args):
    pass


def auto(args):
    pass


def job(args):
    pass


init_commands = {
    # Operations:
    # connect <host>
    #     SSHs to remote node
    'connect': connect,
    # disconnect
    #     Disconnects remote connections
    'disconnect': disconnect,
    # pin <node>:<pid> <node>:<pid> <node>:<pid> ....
    #     Attaches to nodes and PIDs provided
    'pin': pin,
    # raw
    #     Starts a local debugging session
    'raw': raw,
    # auto
    #     !!! Assumes the machine it's running on has scheduler commands
    #     !!! Assumes there's only one active job
    #     Tries to find the active job, gather information about the job and
    #     attach to the relevant PIDs on their respective nodes
    'auto': auto,
    # job <jobid>
    #     !!! Assumes the machine it's running on has scheduler commands
    #     !!! Assumes <jobid> is an active job we can query on this machine
    #     Tries to collect information about job <jobid> and attach attach to
    #     the relevant PIDs on their respective nodes
    'job': job,
}
setting_commands = {
    # Settings:
    # blitz - If no relevant active jobs are found return (default)
    'blitz': 'ls',
    # ambush - If relevant jobs are found but are not started, or other
    # criteria is not met yet keep waiting
    'ambush': 'ls',
}


def local(args):
    try:
        pids = []
        for arg in args:
            pids.append(int(arg))
        _local_s.launch(pids)
        return (modes.to_local, None)
    except ValueError:
        raise BadArgsError(
            'local', 'Was expecting PIDs, received non-integer(s): {0}'.
            format(repr(args))
        )
    _local_s.launch(pids)
    raise CommandImplementationIncompleteError
    #return (modes.local, None)


def remote(args):
    if len(args) != 2:
        raise BadArgsError('remote', 'remote <machine_name> <jobid>')
    #print_ahead('Launching remote session')
    _remote_s.launch(name = args[0], jobid = args[1])
    return (modes.remote, None)


def quit(args):
    return (modes.quit, None)


def debug(args):
    import pdb
    pdb.set_trace()
    return (modes.offline, None)


commands = {
    'local': local,
    'remote': remote,
    'quit': quit,
    'debug': debug,
}


def process(cmd, args):
    if cmd in commands:
        return commands[cmd](args)
    raise UnknownCommandError(cmd)

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

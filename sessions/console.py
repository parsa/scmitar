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
import errors
import pexpect

hops = []
all_sessions = []

global current_session_id, newest_session_id
current_session_id, newest_session_id = -1, -1


def list_sessions():
    return all_sessions


def add_hop(host):
    if len(all_sessions) != 0:
        raise errors.CommandFailedError('Cannot add a hop while connections alive.')
    hops.append(host)

def pop_hop():
    if len(all_sessions) != 0:
        raise errors.CommandFailedError('Cannot add a hop while connections alive.')
    if len(hops) == 0:
        raise errors.CommandFailedError('No hops currently exist, nothing can be removed.')
    return hops.pop()


def get_current_session():
    if current_session_id < 0:
        return None
    return all_sessions[current_session_id]


class Terminal(object):
    ps1_export_cmd = r"export PS1='SCIMITAR_PS\n$ '"
    ps1_pattern = 'SCIMITAR_PS\r*\n\$\ '

    def __init__(self, node=None):
        self.node = node
        self.con = None
        self.prompt_pattern = self.ps1_pattern


    def __enter__(self):
        return self.connect()


    def connect(self):
        global newest_session_id

        self.con = pexpect.spawn('/usr/bin/env bash')

        for host in hops:
            self.con.sendline('ssh -tt {host}'.format(host=host))

        if self.node:
            self.con.sendline('ssh -tt {host}'.format(host=self.node))

        self.con.sendline(self.ps1_export_cmd)
        self.con.expect(self.ps1_pattern)

        all_sessions.append(self)
        newest_session_id = len(all_sessions) - 1

        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        if self.con.isalive():
            try:
                self.query('quit')
            finally:
                self.con.close()

        all_sessions.remove(self)


    def set_prompt(self, prompt):
        self.prompt_pattern = prompt


    def query(self, cmd):
        self.con.sendline(cmd)
        self.con.expect(self.prompt_pattern)
        return self.con.before


    def is_pid_alive(self, process_id):
        """Checks if a PID is still valid

        :pid: The Process ID
        :returns: bool

        """
        if re.match('.*aye\r*\n*', self.query('ps -p {pid} >/dev/null 2>&1 && echo aye || echo nay'.format(pid=process_id))):
            return True
        return False
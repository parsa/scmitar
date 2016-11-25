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

newest_session_id = -1


def get_oldest_session():
    if all_sessions:
        return all_sessions[0]
    return None


def get_newest_session():
    if all_sessions and not newest_session_id < 0:
        return all_sessions[newest_session_id]
    return None


def list_hops():
    return hops


def list_sessions():
    return all_sessions


def add_hop(host):
    if len(all_sessions) > 0:
        raise errors.CommandFailedError('Cannot add a hop while connections alive.')
    hops.append(host)


def pop_hop():
    if len(all_sessions) > 0:
        raise errors.CommandFailedError('pop', 'Cannot add a hop while connections alive.')
    if len(hops) == 0:
        raise errors.CommandFailedError('pop', 'No hops currently exist. Nothing can be removed')
    return hops.pop()


def close_all_sessions():
    if len(all_sessions) > 0:
        for s in all_sessions:
            s.close()


class Terminal(object):
    ps1_export_cmd = r"export PS1='SCIMITAR_PS\n$ '"
    ps1_re = r'SCIMITAR_PS\s+\$ '

    def __init__(self, node=None):
        self.node = node
        self.con = None

        self.host = 'localhost'
        self.meta = None
        self.tag = None

        self.exit_re = None
        self.prompt_re = None


    def __enter__(self):
        return self.connect()


    def connect(self):
        global newest_session_id

        self.con = pexpect.spawn('/usr/bin/env bash')

        for host in hops:
            self.con.sendline('ssh -tt {host}'.format(host=host))
            self.host = host

        if self.node:
            self.con.sendline('ssh -tt {host}'.format(host=self.node))
            self.host = self.node

        self.con.sendline(self.ps1_export_cmd)
        self.con.expect(self.ps1_re)

        all_sessions.append(self)
        newest_session_id = len(all_sessions) - 1

        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


    def close(self):
        try:
            cntr = 5
            while self.con.isalive() and cntr > 0:
                self.query('quit')
                cntr -= 1
        finally:
            self.con.close()

        all_sessions.remove(self)


    def query(self, cmd):
        self.con.sendline(cmd)
        try:
            p_re = [ self.ps1_re ]
            if self.exit_re:
                p_re.insert(0, self.exit_re)
            if self.prompt_re:
                p_re.insert(0, self.prompt_re)

            pattern_index = self.con.expect(p_re)
            if pattern_index == 0:
                return self.con.before
            elif pattern_index == 1:
                self.close()
                return '^exit'
            elif pattern_index == 2:
                self.con.close()
                return '^kill'
        except (pexpect.TIMEOUT, pexpect.EOF):
            ## Connection's probably dead, close the socket
            self.close()
            raise errors.ConsoleSessionError
        raise errors.UnexpectedResponseError


    def is_pid_alive(self, process_id):
        """Checks if a PID is still valid

        :pid: The Process ID
        :returns: bool

        """
        if re.match('^.*aye[\r\n]*$', self.query('ps -p {pid} >/dev/null 2>&1 && echo aye || echo nay'.format(pid=process_id)), re.DOTALL):
            return True
        return False

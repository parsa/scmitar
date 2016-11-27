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


class SessionsAliveError(errors.ScimitarError):
    "Raised when attempting to modify hops while there are active sessions."
    pass


class NoHopsError(errors.ScimitarError):
    "Rased when there are no more hops to remove."
    pass


class HopManager(object):

    def __init__(self):
        self._hops = None

    def add(self, hop):
        if not self._hops:
            self._hops = []
        self._hops.append(hop)

    def ls(self):
        return self._hops or []

    def rm(self):
        if not self._hops:
            raise NoHopsError
        return self._hops.pop()

    def is_empty(self):
        return not self._hops


class SessionManager(object):

    def __init__(self):
        self._session_dict = None
        self._order = None

    def add(self, session):
        if not self._session_dict:
            self._session_dict = {}
            self._order = []
        self._order.append(session)
        self._session_dict[session.tag] = session

    def rm(self, session_tag):
        session = self._session_dict.pop(session_tag)
        self._order.remove(session)

    def ls_sessions(self):
        if not self._session_dict:
            return []
        return self._session_dict.values()

    def ls(self):
        if not self._session_dict:
            return []
        return self._session_dict.keys()

    def exists(self, tag):
        if self._session_dict and self._session_dict.has_key(tag):
            return True
        return False

    def get(self, tag):
        return self._session_dict[tag]

    def is_empty(self):
        return not self._session_dict

    def kill_all(self):
        if self._session_dict:
            for s in self._session_dict.itervalues():
                s.close()
        self._session_dict = None
        self._order = None

    def get_oldest(self):
        if not self._order:
            return None
        return self._order[0]

    def get_newest(self):
        if not self._order:
            return None
        return self._order[-1]


class Terminal(object):
    ps1_export_cmd = r"export PS1='SCIMITAR_PS\n$ '"
    ps1_re = r'SCIMITAR_PS\s+\$ '

    def __init__(
        self,
        hops,
        target_host = None,
        meta = None,
        tag = None,
        exit_re = None,
        prompt_re = None,
    ):
        self.con = None
        self.hops = hops

        self.hostname = 'localhost'

        self.target_host = target_host
        self.meta = meta
        self.tag = tag

        self.exit_re = exit_re
        self.prompt_re = prompt_re

    def __enter__(self):
        return self.connect()

    def connect(self):
        self.con = pexpect.spawn('/usr/bin/env bash')

        for hop in self.hops:
            self.con.sendline('ssh -tt {host}'.format(host = hop))
            self.hostname = hop

        if self.target_host:
            self.con.sendline('ssh -tt {host}'.format(host = self.target_host))
            self.hostname = self.target_host

        self.con.sendline(self.ps1_export_cmd)
        self.con.expect(self.ps1_re)

        #all_sessions.append(self)

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

        #all_sessions.remove(self)

    def query(self, cmd):
        if not self.con.isalive():
            raise errors.DeadConsoleError
        self.con.sendline(cmd)
        try:
            p_re = [self.ps1_re]
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

    def test_query(self, cmd):
        if re.match(
            '^.*aye[\r\n]*$',
            self.query(
                '{cmd} >/dev/null 2>&1 && echo aye || echo nay'.
                format(cmd = cmd)
            ),
            re.DOTALL
        ):
            return True
        return False

    def is_pid_alive(self, process_id):
        """Checks if a PID is still valid

        :pid: The Process ID
        :returns: bool

        """
        return self.test_query(
            'ps -p {pid}'.format(pid = process_id), re.DOTALL
        )

    def is_alive(self):
        return self.con.isalive()

    def __repr__(self):
        return '<Terminal {0} @{1}:{2}>'.format(
            self.tag, self.hostname, self.meta
        )

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

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

import os
import errors
import pexpect

class LocalTerminal(object):


    def __init__(self):
        self.terminal = pexpect.spawn('/usr/bin/env bash')


    def run(self, cmd):
        raise errors.CommandImplementationIncompleteError

    # Alternative command: ps -p $PID > /dev/null 2>&1
    def is_pid_alive(self, process_id):
        """Checks if a PID is still valid

        :pid: The Process ID
        :returns: bool

        """
        try:
            os.kill(process_id, 0)
            return True
        except OSError:
            return False

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

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
import console


def ls_user_jobs(term):
    cmd_out = term.query(r'qstat -u $USER')
    return re.findall(r'^\d([^\s]+)', cmd_out)


def ls_job_nodes(term, job_id):
    cmd_out = term.query(r'checkjob {job_id}'.format(job_id = job_id))
    return re.findall(r'\[(\w+):\d+\]', cmd_out)


def which_appname(term, host):
    cmd_out = term.query(
        r'''ssh {host} "ps -o pid:1,cmd:1 -e" | grep -o "MPISPAWN_ARGV_[0-9]='.\+'"'''.
        format(host = host)
    )
    return re.findall(r'MPISPAWN_ARGV_0=([\S]+)', cmd_out
                      )[0].replace(r'"', r'').replace(r"'", r'')


def ls_pids(term, host, appname):
    cmd_out = term.query(
        r'ssh {host} "pgrep {appname}"'.format(
            host = host, appname = appname
        )
    )
    return [int(pid) for pid in cmd_out.split()]

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

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
    term = console.Terminal()
    cmd_out = term.query('squeue -h -A -u $USER')
    return cmd_out.split()


def ls_job_nodes(term, job_id):
    term = console.Terminal()
    cmd_out = term.query('checkjob {jobid}')
    return re.findall('\[(\w+):\d+\]', cmd_out)


def which_appname(term, host):
    term = console.Terminal()
    cmd_out = term.query('''ssh {host} "ps -o pid:1,cmd:1 -e" | grep -o "MPISPAWN_ARGV_[0-9]='.\+'"'''.format(host=host))
    return re.findall('MPISPAWN_ARGV_0=([\S]+)', cmd_out)[0].replace('"','').replace("'",'')


def ls_pids(term, host, appname):
    term = console.Terminal()
    cmd_out = term.query('ssh {host} "pgrep {appname}"'.format(host=host,appname=appname))
    return [int(pid) for pid in cmd_out.split()]


# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

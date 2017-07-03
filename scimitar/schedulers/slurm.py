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

delimited_nodes_re = re.compile(r'\w+(?:\[\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*\])?')
grouped_nodes_re = re.compile(r'([^[]+)\[([^]]+)\]')


def _ungroup_node_names(job_nodes):
    squeue_out = []

    for node_subgroup in delimited_nodes_re.findall(job_nodes):
        grouped_nodes = grouped_nodes_re.match(node_subgroup)
        if grouped_nodes:
            ungrouped_nodes = []
            base_name = grouped_nodes.group(1)
            for id_parts in grouped_nodes.group(2).split(','):
                range_parts = id_parts.split('-')
                if len(range_parts) == 1:
                    ungrouped_nodes.append(base_name + range_parts[0])
                    squeue_out += [base_name + range_parts[0]]
                elif len(range_parts) == 2:
                    naming_length = len(range_parts[0])
                    node_range_low = int(range_parts[0])
                    node_range_up = int(range_parts[1]) + 1
                    for node_number in range(node_range_low, node_range_up):
                        node_name = base_name + str(node_number).rjust(
                            naming_length, '0'
                        )
                        ungrouped_nodes.append(base_name + range_parts[0])
                        squeue_out += [node_name]
        else:
            squeue_out += [node_subgroup]
    return squeue_out


def _sanitize_output(expr):
    if not expr:
        return ''
    expr = expr.replace('\r', '')
    expr = re.sub(r'\n{2,}', '\n', expr)
    expr = re.sub(r'^[^\n]*\n', '', expr)
    return re.sub(r'\n$', '', expr)


def ls_user_jobs(term):
    query_cmd = '''squeue -h -o '%A' -u $USER'''
    cmd_out = term.query(query_cmd)
    cmd_out_san = _sanitize_output(cmd_out)
    jobs = list(filter(None, cmd_out_san.split('\n')))
    return jobs


def ls_job_nodes(term, job_id):
    query_cmd = '''squeue -h -o '%N' -j {job_id}'''.format(job_id = job_id)
    cmd_out = term.query(query_cmd)
    cmd_out_san = _sanitize_output(cmd_out)

    job_nodes = []
    if not 'Invalid' in cmd_out_san:
        job_nodes = _ungroup_node_names(cmd_out_san)
    return job_nodes


def which_appname(term, host):
    query_cmd = '''ssh {host} "ps -o pid:1,cmd:1 -e" | grep -o "MPISPAWN_ARGV_[0-9]='.\+'"'''.format(
        host = host
    )
    cmd_out = term.query(query_cmd)
    re_m = re.search('''MPISPAWN_ARGV_0=([\S]+)''', cmd_out).group(1)
    appname = re_m.replace('"', '').replace("'", '')
    return appname


# This nasty piece of work wasted so much of my time. Be ware:
# 'ssh marvin00 "pgrep mpi_hello_world"\r\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\r\r\n@       WARNING: POSSIBLE DNS SPOOFING DETECTED!          @\r\r\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\r\r\nThe ECDSA host key for marvin00 has changed,\r\r\nand the key for the corresponding IP address 10.3.3.50\r\r\nis unknown. This could either mean that\r\r\nDNS SPOOFING is happening or the IP address for the host\r\r\nand its host key have changed at the same time.\r\r\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\r\r\n@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @\r\r\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\r\r\nIT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!\r\r\nSomeone could be eavesdropping on you right now (man-in-the-middle attack)!\r\r\nIt is also possible that a host key has just been changed.\r\r\nThe fingerprint for the ECDSA key sent by the remote host is\r\na9:18:47:c2:60:96:80:dc:a5:d3:bd:e7:7f:c1:3b:dd.\r\r\nPlease contact your system administrator.\r\r\nAdd correct host key in /home/pamini/.ssh/known_hosts to get rid of this message.\r\r\nOffending ECDSA key in /home/pamini/.ssh/known_hosts:16\r\r\nPassword authentication is disabled to avoid man-in-the-middle attacks.\r\r\nKeyboard-interactive authentication is disabled to avoid man-in-the-middle attacks.\r\r\n29177\r\n'
def ls_pids(term, host, appname):
    cmd_out = term.query(
        '''ssh {host} "pgrep {appname}"'''.format(
            host = host, appname = appname
        )
    )
    pids_m = re.search(r'\s*([\d\s]+)\s*$', cmd_out)
    if not pids_m:
        return []
    raw_pids = pids_m.group(1).split('\n')
    raw_pids = list(filter(None, raw_pids))

    return [int(pid) for pid in raw_pids]

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

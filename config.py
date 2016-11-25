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
import getpass

settings = {
    'ui':
    {
        'prompts':
            [
                '# ',
                '$ ',
            ],
    },
    'signals':
    {
        'sigkill'     : 5,
        'sigkill_last': 1,
        # TODO: See if we need to handle the other signals. These maybe:
        ## EOF
        ## SIGALRM
        ## SIGINT
        ## SIGQUIT
        ## SIGTERM
        ## SIGSTOP
    },
    'gdb':
    {
        # GDB command line
        # Supress banner, interactive mode
        'cmd'   :
            [
                'gdb',
                '-interpreter=mi2', # Use GDB/MI2 interface
                '-quiet',           # Suppress banner
                '--nx',             # Don't load any .gdbinits whatsoever
            ],
        'attach': '--pid={pid}',
        'mi_prompt_pattern': '\[(\]gdb\[)\] \[\r\n\]+',
    },
}

remotes = {
    'smic':
    {
        # MERGE: dotsshconfig (a6206aa120844233b986cb470013cf54)
        #'use_dotsshconfig': True,
        # NOTE: I have smic in my .ssh/config. Won't work elsewhere as is
        'login_node'      : 'smic',
        # FIXME: Find a way usernames can be provided with more ease
        'user'            : getpass.getuser(),
        'PS1'             : '[\$\#] ',
        # Solution 1: Works on the head node only
        ## uniq /var/spool/torque/aux/{jobid}*
        # Solution 2:
        ## $ checkjob {jobid}
        # Sample output:
        ## $ checkjob 164018
        ## job 164018
        ## 
        ## AName: STDIN
        ## State: Running 
        ## Creds:  user:parsa  group:Users  account:hpc_hpx_grav  class:hybrid  qos:userres
        ## WallTime:   00:00:00 of 1:00:00
        ## SubmitTime: Mon Aug 22 21:38:29
        ##   (Time Queued  Total: 00:00:20  Eligible: 00:00:20)
        ## 
        ## StartTime: Mon Aug 22 21:38:49
        ## TemplateSets:  DEFAULT
        ## NodeMatchPolicy: EXACTNODE
        ## Total Requested Tasks: 60
        ## 
        ## Req[0]  TaskCount: 60  Partition: base
        ## 
        ## Allocated Nodes:
        ## [smic361:20][smic362:20][smic363:20]
        ## 
        ## 
        ## SystemID:   sched
        ## SystemJID:  164018
        ## 
        ## IWD:            /home/parsa
        ## StartCount:     1
        ## Partition List: base
        ## Flags:          INTERACTIVE
        ## Attr:           INTERACTIVE,checkpoint
        ## StartPriority:  140075
        ## Reservation '164018' (-00:00:20 -> 00:59:40  Duration: 1:00:00)
        ## 
        #'node_list'     : "checkjob {jobid} | grep -o '\w\+:[0-9]\+\]' | sed 's/:[0-9]*\]//'",
        'node_ls_cmd'     : "checkjob {jobid}",
        'node_ls_fn'      : lambda x: re.findall('\[(\w+):\d+\]', x),
        'app_name_cmd'    : '''ssh {host} "ps -o pid:1,cmd:1 -e" | grep -o "MPISPAWN_ARGV_[0-9]='.\+'"''',
        'app_name_fn'     : lambda x: re.findall('MPISPAWN_ARGV_0=([\S]+)', x)[0].replace('"','').replace("'",''),
        #'pid_ls'          : 'ps -o pid:1,cmd:1 -e | grep {appname}',
        'pid_ls_cmd'      : 'ssh {host} "pgrep {appname}"',
        'pid_ls_fn'       : lambda x: [int(y) for y in x.split()],
    },
    'rostam':
    {
        # MERGE: dotsshconfig (a6206aa120844233b986cb470013cf54)
        #'use_dotsshconfig': True,
        # NOTE: I have rostam in my .ssh/config. Won't work elsewhere as is
        'login_node'      : 'rostam',
        # HACK: I hardcoded my username. Not good
        'user'            : 'pamini',
        'PS1'             : '[\$\#] ',
        # FIXME: add rostam's config once SLURM starts working again
        'node_ls_cmd'     : None,
        'node_ls_fn'      : None,
        'app_name_cmd'    : None,
        'app_name_fn'     : None,
        'pid_ls_cmd'      : None,
        'pid_ls_fn'       : None,
    },
    # MERGE: stampede_config (3c21aec9daba4bc49fd2d0d98ec0e46b)
    # MERGE: edison_config (613a076ab3254014b55f645a7d85e529)
    # MERGE: cori_config (d8459d9a002047239fb21c3c92050980)
    # MERGE: bigdat_config (406ec14fae894e66ad147245ede1abda)
    # MERGE: supermike2_config (08e71a6fd99246c7ad01e996dd79fea2)
}

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

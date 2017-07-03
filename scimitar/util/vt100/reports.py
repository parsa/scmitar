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
from .apply import apply

_report_curser_pos = '\033[6n' # Cursor position report
report_curser_pos = lambda: apply(_report_curser_pos)
#'\033[Pl;PcR'            (response; Pl=line#; Pc=column#)
#
_report_status = '\033[5n' # Status report
report_status = lambda: apply(_report_status)
#'\033[c'                 (response; terminal Ok)
#'\033[0c'                (response; teminal not Ok)
#
_id_terminal = '\033[c' # What are you?
id_terminal = lambda: apply(_id_terminal)
_id_terminal_2 = '\033[0c' # Same
id_terminal_2 = lambda: apply(_id_terminal_2)
#'\033[?1;Psc'            response; where Ps is option present:
#    0    Base VT100, no options
#    1    Preprocessor option (STP)
#    2    Advanced video option (AVO)
#    3    AVO and STP
#    4    Graphics processor option (GO)
#    5    GO and STP
#    6    GO and AVO
#    7    GO, STP, and AVO
#
_powerup_reset_routine = '\033c' # Causes power-up reset routine to be executed
powerup_reset_routine = lambda: apply(_powerup_reset_routine)
#
_fill_screen_with_E = '\033#8' # Fill screen with "E"
fill_screen_with_E = lambda: apply(_fill_screen_with_E)
#
_fill_screen_with_x_test = lambda x: '\033}1{test}'.format(x = x)
fill_screen_with_x_test = lambda x: apply(_fill_screen_with_star_test(x))
#
# Invoke Test(s), where Ps is a decimal computed by adding the numbers of the
# desired tests to be executed:
_invoke_test_ps = lambda Ps: '\033[2;{Ps}y'.format(Ps = Ps)
invoke_test_ps = lambda Ps: apply(_invoke_test_ps(Ps = Ps))
#    1    Power up test
#    2    Data loop back
#    4    EIA modem control signal test
#    8    Repeat test(s) indefinitely

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

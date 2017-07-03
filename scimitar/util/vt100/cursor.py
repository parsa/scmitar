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

_up = lambda count = 1: '\x1b[{COUNT}A'.format(COUNT = count)
up = lambda count = 1: apply(up(count))
#
_down = lambda count = 1: '\033[{COUNT}B'.format(COUNT = count)
down = lambda count = 1: apply(down(count))
#
_forward = lambda count = 1: '\033[{COUNT}C'.format(COUNT = count)
forward = lambda count = 1: apply(forward(count))
#
_backward = lambda count = 1: '\033[{COUNT}D'.format(COUNT = count)
backward = lambda count = 1: apply(backward(count))
#
_column = lambda column_id = 0: '\033[{COL}G'.format(COL = column_id)
column = lambda column_id = 0: apply(column(column_id))
#
_save_cursor = '\033[s'
save_cursor = lambda: apply(_save_cursor)
#
_unsave_cursor = '\033]s'
unsave_cursor = lambda: apply(_unsave_cursor)
#
_save_cursor_attr = '\0337'
save_cursor_attr = lambda: apply(_save_cursor_attr)
#
_restore_cursor_attr = '\0338'
restore_cursor_attr = lambda: apply(_restore_cursor_attr)
#
_cursor_off = '\033[?25l'
cursor_off = lambda: apply(_cursor_off)
#
_cursor_on = '\033[?25h'
cursor_on = lambda: apply(cursor_on)
#
_cursor_off_2 = '\033[?50l'
cursor_off_2 = lambda: apply(_cursor_off_2)
#
_cursor_on_2 = '\033[?50h'
cursor_on_2 = lambda: apply(cursor_on_2)

_index = '\033D' # LF?
rev_index = '\033M' # Inverse LF?

lf = '\033[20h'
inv_lf = '\033I'
cr = '\033[20l'
cr_lf = '\033E'

#
_top_left = '\033[H' # Cursor home
top_left = lambda: apply(_top_left)
#
_move_cursor = lambda row, column: '\033[{ROW};{COLUMN}H'.format(
    ROW = row, COLUMN = column
)
move_cursor = lambda row, column: apply(move_cursor(row, column))
#
_move_cursor_2 = lambda row, column: '\033[{ROW};{COLUMN}f'.format(
    ROW = row, COLUMN = column
)
move_cursor_2 = lambda row, column: apply(move_cursor_2(row, column))
#
_direct_cursor_addr = lambda row, column: '\033Yn{ROW}c{COLUMN}'.format(
    ROW = row, COLUMN = column
) # Direct cursor addressing (line/column number)
direct_cursor_addr = lambda row, column: apply(
    _direct_cursor_addr(row, column)
)
#
_tab_cur_set = '\033H' # Tab set at present cursor position
tab_cur_set = lambda: apply(_tab_cur_set)
#
_clear_cur_tab = '\033[0g' # Clear tab at present cursor position
clear_cur_tab = lambda: apply(_clear_cur_tab)
#
_clear_all_tabs = '\033[3g' # Clear all tabs
clear_all_tabs = lambda: apply(_clear_all_tabs)

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

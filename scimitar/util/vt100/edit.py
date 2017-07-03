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

_insert_mode = '\033[4h'
insert_mode = lambda: apply(_insert_mode)
#
_replace_mode = '\033[4l'
replace_mode = lambda: apply(_replace_mode)
#
_immediate_enter = '\033?14h'
immediate_enter = lambda: apply(_immediate_enter)
#
_deferred_enter = '\033?14l'
deferred_enter = lambda: apply(_deferred_enter)
#
_immediate_edit_selection = '\033?16h'
immediate_edit_selection = lambda: apply(_immediate_edit_selection)
#
_deferred_edit_selection = '\033?16l'
deferred_edit_selection = lambda: apply(_deferred_edit_selection)
#
_del_1_char = '\033[P' # Delete a character from cursor position
del_1_char = lambda: apply(_del_1_char)
#
_delete_n_chars = lambda count = 1: '\033[{COUNT}P'.format(
    COUNT = count
) # Delete n characters from cursor position
delete_n_chars = lambda count = 1: apply(_delete_n_chars(count))
#
_del_1_line = '\033[M' # Delete a line from cursor position down
del_1_line = lambda: apply(_del_1_line)
#
_delete_n_lines = lambda count = 1: '\033[{COUNT}M'.format(
    COUNT = count
) # Delete n lines from cursor position down
delete_n_lines = lambda count = 1: apply(_delete_n_lines(count))
#
_erase_down = '\033[J' # Erase screen from cursor to end
erase_down = lambda: apply(_erase_down)
#
_erase_up = '\033[1J' # Erase beginning of screen to cursor
erase_up = lambda: apply(_erase_up)
#
_clear_screen = '\033[2J' # Erase entire screen but do not move cursor
clear_screen = lambda: apply(_clear_screen)
#
_erase_right = '\033[K'
erase_right = lambda: apply(_erase_right)
#
_erase_left = '\033[1K'
erase_left = lambda: apply(_erase_left)
#
_erase_line = '\033[2K'
erase_line = lambda: apply(_erase_line)
#
_insert_1_line = '\033[L' # Insert a line from cursor position
insert_1_line = lambda: apply(_insert_1_line)
#
insert_n_lines = lambda count = 1: '\033[{COUNT}L'.format(
    COUNT = count
) # Insert n lines from cursor position
_insert_n_lines = lambda count = 1: apply(_insert_n_lines(count))

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

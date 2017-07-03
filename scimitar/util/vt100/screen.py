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

_cursor_key_app = '[?1h' # 132 Characters on
cursor_key_app = lambda: apply(_cursor_key_app)
#
_cursor_key_cursor = '[?1l' # 132 Characters on
cursor_key_cursor = lambda: apply(_cursor_key_app)
#
_col_mode_132 = '[?3h' # 132 Characters on
col_mode_132 = lambda: apply(_col_mode_132)
#
_col_mode_80 = '[?3l' # 80 Characters on
col_mode_80 = lambda: apply(_col_mode_80)
#
_smooth_scroll_on = '[?4h' # Smooth Scroll on
smooth_scroll_on = lambda: apply(_smooth_scroll_on)
#
_jump_scroll_on = '[?4l' # Jump Scroll on
jump_scroll_on = lambda: apply(_jump_scroll_on)
#
_scroll_region_selected = lambda t, b: '[{t};{b}r'.format(
    t = t, b = b
) # Scrolling region selected, line *t to *b
scroll_region_selected = lambda t, b: apply(_scroll_region_selected(t, b))
#
_screen_mode_reverse = '[?5h' # Inverse video on
screen_mode_reverse = lambda: apply(_screen_mode_reverse)
#
_screen_mode_normal = '[?5l' # Normal video off
screen_mode_normal = lambda: apply(_screen_mode_normal)
#
_origin_mode_relative = '[?6l' # Normal video off
origin_mode_relative = lambda: apply(_origin_mode_relative)
#
_origin_mode_absolute = '[?6l' # Normal video off
origin_mode_absolute = lambda: apply(_origin_mode_absolute)
#
_wraparound_on = '[?7h' # Wraparound ON
wraparound_on = lambda: apply(_wraparound_on)
#
_wraparound_off = '[?7l' # Wraparound OFF
wraparound_off = lambda: apply(_wraparound_off)
#
_screen_display_on = '[?75h' # Screen display ON
screen_display_on = lambda: apply(_screen_display_on)
#
_screen_display_off = '[?75l' # Screen display OFF
screen_display_off = lambda: apply(_screen_display_off)

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

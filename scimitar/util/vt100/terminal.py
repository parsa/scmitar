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

_reset = '\033c'
reset = lambda: apply(_reset)
#
_soft_reset = '\033[!p'
soft_reset = lambda: apply(_soft_reset)
#
_video_attr_test_display = '\033}2'
video_attr_test_display = lambda: apply(_video_attr_test_display)
#
_char_set_display_test = '\033}3'
char_set_display_test = lambda: apply(_char_set_display_test)
#
_enable_line_wrap = '\033[7h'
enable_line_wrap = lambda: apply(_enable_line_wrap)
#
_disable_line_wrap = '\033[7l'
disable_line_wrap = lambda: apply(_disable_line_wrap)
#
_enable_interface = '\033[?9h'
enable_interface = lambda: apply(_)
#
_disable_interface = '\033[?9l'
disable_interface = lambda: apply(_)

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

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

_lock_keyboard = '\033[2h'
lock_keyboard = lambda: apply(_lock_keyboard)
#
_unlock_keyboard = '\033[2l'
unlock_keyboard = lambda: apply(_unlock_keyboard)

_auto_repeat_on = '\033[8h'
auto_repeat_on = lambda: apply(_auto_repeat_on)
#
_auto_repeat_off = '\033[8l'
auto_repeat_off = lambda: apply(_auto_repeat_off)

_lights_off_on_keyboard = '\033[0q'
lights_off_on_keyboard = lambda: apply(_lights_off_on_keyboard)

_light_x_on_on_keyboard = lambda x: '\033[{x}q'.format(x = x)
light_x_on_on_keyboard = lambda x: apply(_light_x_on_on_keyboard(x))

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

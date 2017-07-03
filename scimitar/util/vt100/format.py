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

def style(*args):
    return '\033[{0}m'.format(';'.join(args))

__clear_all_chars_attrs = '0'
_clear_all_chars_attrs = style(__clear_all_chars_attrs)
clear_all_chars_attrs = lambda: apply(_clear_all_chars_attrs)
#
__alternate_intesity_on = '1'
_alternate_intesity_on = style(__alternate_intesity_on)
alternate_intesity_on = lambda: apply(_alternate_intesity_on)
#
__alternate_intesity_off = '22'
_alternate_intesity_off = style(__alternate_intesity_off)
alternate_intesity_off = lambda: apply(_alternate_intesity_off)
#
__dim = '2'
_dim = style(__dim)
dim = lambda: apply(_dim)
#
__underline_on = '4'
_underline_on = style(__underline_on)
underline_on = lambda: apply(_underline_on)
#
__underline_off = '24'
_underline_off = style(__underline_off)
underline_off = lambda: apply(_underline_off)
#
__blink_on = '5'
_blink_on = style(__blink_on)
blink_on = lambda: apply(_blink_on)
#
__blink_off = '25'
_blink_off = style(__blink_off)
blink_off = lambda: apply(_blink_off)
#
__inv_video_on = '7'
_inv_video_on = style(__inv_video_on)
inv_video_on = lambda: apply(_inv_video_on)
#
__inv_video_off = '27'
_inv_video_off = style(__inv_video_off)
inv_video_off = lambda: apply(_inv_video_off)
#
_protected_fields_off = '\033[0}'
protected_fields_off = lambda: apply(_protected_fields_off)
#
_protected_alt_intensity = '\033[1}'
protected_alt_intensity = lambda: apply(_protected_alt_intensity)
#
_protected_underline = '\033[4}'
protected_underline = lambda: apply(_protected_underline)
#
_protected_blinking = '\033[5}'
protected_blinking = lambda: apply(_protected_blinking)
#
_protected_inverse = '\033[7}'
protected_inverse = lambda: apply(_protected_inverse)
#
_protected_all_attrs_off = '\033[254}'
protected_all_attrs_off = lambda: apply(_protected_all_attrs_off)
#
__hidden = '8'
_hidden = style(__hidden)
hidden = lambda: apply(_hidden)

__fg_black = '30'
_fg_black = style(__fg_black)
fg_black = lambda: apply(_fg_black)
#
__fg_red = '31'
_fg_red = style(__fg_red)
fg_red = lambda: apply(_fg_red)
#
__fg_green = '32'
_fg_green = style(__fg_green)
fg_green = lambda: apply(_fg_green)
#
__fg_yellow = '33'
_fg_yellow = style(__fg_yellow)
fg_yellow = lambda: apply(_fg_yellow)
#
__fg_blue = '34'
_fg_blue = style(__fg_blue)
fg_blue = lambda: apply(_fg_blue)
#
__fg_magenta = '35'
_fg_magenta = style(__fg_magenta)
fg_magenta = lambda: apply(_fg_magenta)
#
__fg_cyan = '36'
_fg_cyan = style(__fg_cyan)
fg_cyan = lambda: apply(_fg_cyan)
#
__fg_white = '37'
_fg_white = style(__fg_white)
fg_white = lambda: apply(_fg_white)

__bg_black = '40'
_bg_black = style(__bg_black)
bg_black = lambda: apply(_bg_black)
#
__bg_red = '41'
_bg_red = style(__bg_red)
bg_red = lambda: apply(_bg_red)
#
__bg_green = '42'
_bg_green = style(__bg_green)
bg_green = lambda: apply(_bg_green)
#
__bg_yellow = '43'
_bg_yellow = style(__bg_yellow)
bg_yellow = lambda: apply(_bg_yellow)
#
__bg_blue = '44'
_bg_blue = style(__bg_blue)
bg_blue = lambda: apply(_bg_blue)
#
__bg_magenta = '45'
_bg_magenta = style(__bg_magenta)
bg_magenta = lambda: apply(_bg_magenta)
#
__bg_cyan = '46'
_bg_cyan = style(__bg_cyan)
bg_cyan = lambda: apply(_bg_cyan)
#
__bg_white = '47'
_bg_white = style(__bg_white)
bg_white = lambda: apply(_bg_white)

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

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
from sys import stdout
import signal
import readline
from itertools import chain
from . import vt100 as v

FORMAT_CONSTS = {'u1': v.format._underline_on, 'u0': v.format._underline_off}


def merge_dicts(dict_a, dict_b):
    '''Creates a new dictionary including items in both dict_a and dict_b'''
    return dict(chain(dict_a.items(), dict_b.items()))


def print_out(expr, ending = '\n', *args, **kwargs):
    '''Standard print() function in Scimitar'''
    stdout.write(
        expr.format(*args, **merge_dicts(kwargs, FORMAT_CONSTS)) + ending
    )
    stdout.flush()


def print_error(expr, *args, **kwargs):
    '''Standard print() function for errors in Scimitar'''
    print_out(
        '\r' + v.format._clear_all_chars_attrs +
        v.format._alternate_intesity_on + v.format._fg_red + expr +
        v.format._clear_all_chars_attrs, *args, **kwargs
    )


def print_warning(expr, *args, **kwargs):
    '''Standard print() function for warinings in Scimitar'''
    print_out(
        '\r' + v.format._clear_all_chars_attrs +
        v.format._alternate_intesity_on + v.format._fg_yellow + expr +
        v.format._clear_all_chars_attrs, *args, **kwargs
    )


def print_info(expr, *args, **kwargs):
    '''Standard print() function for information messages in Scimitar'''
    print_out(
        '\r' + v.format._clear_all_chars_attrs +
        v.format._alternate_intesity_on + v.format._fg_blue + expr +
        v.format._clear_all_chars_attrs, *args, **kwargs
    )


def print_ahead(expr, prompt = '', *args, **kwargs):
    '''Prints expr above the current line'''
    current_input = readline.get_line_buffer()
    v.erase_line()
    stdout.write('\r')

    print_out(expr, *args, **kwargs)
    print_out(prompt + current_input, ending = '')


repr_str_dict = {
    # ASCII Control Codes
    '\x01': '<C-a>', # SOH (Start of heading)
    '\x02': '<C-b>', # STX (Start of text)
    '\x03': '<C-c>', # ETX (End of text)
    '\x04': '<C-d>', # EOT (End of transmission)
    '\x05': '<C-e>', # ENQ (Enquiry)
    '\x06': '<C-f>', # ACK (Acknowledge)
    '\x07': '<C-g>', # BEL (Bell)
    '\x08': '<C-h>', # BS  (Backspace)
    '\x09': '<C-i>', # HT  (Horizontal tab)
    '\x0a': '<C-j>', # LF  (Line feed)
    '\x0b': '<C-k>', # VT  (Vertical tab)
    '\x0c': '<C-l>', # FF  (Form feed)
    '\x0d': '<C-m>', # CR  (Carriage return)
    '\x0e': '<C-n>', # SO  (Shift out)
    '\x0f': '<C-o>', # SI  (Shift in)
    '\x10': '<C-p>', # DLE (Data line escape)
    '\x11': '<C-q>', # DC1 (Device control 1)
    '\x12': '<C-r>', # DC2 (Device control 2)
    '\x13': '<C-s>', # DC3 (Device control 3)
    '\x14': '<C-t>', # DC4 (Device control 4)
    '\x15': '<C-u>', # NAK (Negative acknowledge)
    '\x16': '<C-v>', # SYN (Synchronous idle)
    '\x17': '<C-w>', # ETB (End transmission block)
    '\x18': '<C-x>', # CAN (Cancel)
    '\x19': '<C-y>', # EM  (End of medium)
    '\x1a': '<C-z>', # SUB (Substitute)
    '\x1b': '<C-[>', # ESC (Escape)
    '\x1c': '<C-\>', # FS  (File separator)
    '\x1d': '<C-]>', # GS  (Group separator)
    '\x1e': '<C-^>', # RS  (Record separator)
    '\x1f': '<C-_>', # US  (Unit separator)
}


def repr_str(string):
    '''Calls repr() except for when string is an ASCII <C-key> char'''
    t = repr_str_dict.get(string)
    if not t:
        return repr(string)
    return t


# NOTE: I don't remember why I wrote this one either
def stream_writeline(msg, stream):
    stream.write(msg)
    stream.flush()

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

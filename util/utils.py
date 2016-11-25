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
import config
from . import signals
from . import vt100 as v
from sys import stdout, exit
from datetime import datetime as time
import signal
import readline
import re
import select
from itertools import chain

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


# NOTE: What did I write this function for?
def stream_readline(stream):
    return stream.readline()


# NOTE: I don't remember why I wrote this one either
def stream_writeline(msg, stream):
    stream.write(msg)
    stream.flush()


def attempt_read(stream, retries = -1, timeout = -1, pattern = None):
    """Tries to read until a condition is met.
    Returns empty if nothing was read."""
    before_read = time.now()

    is_ready = select.poll()
    is_ready.register(stream, select.POLLIN)

    out_text = ''
    q = 0
    while True:
        if timeout > 0 and (time.now() - before_read).seconds >= timeout:
            break

        if not is_ready.poll(0):
            q += 1
            if retries > 0 and q >= retries:
                break
            else:
                continue

        if pattern and re.search(pattern, out_text):
            break

        out_text += stream_readline(stream)
    return out_text


# MERGE: asyncio_processing_loop (939bad3d2718407e8b07176c14839ba0)
def raw_input_async(prompt = '', timeout = 5):
    """This is a blocking user input read function.
    It has to be running inside the main thread because it contains code handling signals.
    Despite what the title suggests this version IS NOT ASYNC.
    ALARM signal is not enabled."""
    #signal.signal(signal.SIGINT, signal_handler) # <C-c>
    signal.signal(signal.SIGTSTP, signals.__stop_handler) # <C-z>
    signal.signal(signal.SIGQUIT, signals.__quit_handler) # <C-\>
    #signal.signal(signal.SIGALRM, signals.__alarm_handler)
    #signal.alarm(timeout)

    try:
        text = raw_input(prompt)
        text_parts = text.split()
        #signal.alarm(0)
        return text_parts, None
    #except signals.AlarmSignal:
    #    return None
    except signals.StopSignal: # <C-z> SUB (Substitute) 0x1a
        return None, '\x1a'
    except signals.QuitSignal: # <C-\> FS (File Separator) 0x1c
        # HACK: For debugging. Disable for release
        import pdb
        pdb.set_trace()
        return None, '\x1c'
    except KeyboardInterrupt: # <C-c> ETX (End of Text) 0x03
        # HACK: Disable for production
        if raw_input_async.last_kill_sig:
            if (time.now() - raw_input_async.last_kill_sig
                ).seconds < config.settings['signals']['sigkill_last']:
                # The user is frantically sending <C-c>s
                if raw_input_async.kill_sigs >= config.settings['signals'][
                    'sigkill'
                ] - 1:
                    print_out(
                        '\rGot too many {u1}<C-c>{u0}s. ABAAAAAAANDON SHIP!'
                        )
                    exit(0)
            else:
                raw_input_async.kill_sigs = 0
        else:
            raw_input_async.kill_sigs = 0
        raw_input_async.kill_sigs += 1
        raw_input_async.last_kill_sig = time.now()
        # HACK: NOTE: Only this line stays
        return None, '\x03'
    except EOFError: # <C-d> EOT (End of Transmission) 0x04
        return None, '\x04'
    finally:
        signal.signal(signal.SIGTSTP, signal.SIG_DFL)
        signal.signal(signal.SIGQUIT, signal.SIG_DFL)
        #signal.signal(signal.SIGALRM, signal.SIG_IGN)
    # We should never reach here
    return None, None

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

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
from sys import exit
from datetime import datetime as time
import signal
import readline
import re
import select
import print_helpers
import history

from . import signals
from . import vt100 as v
from config import settings

signals_config = settings['signals']
FORMAT_CONSTS = {'u1': v.format._underline_on, 'u0': v.format._underline_off}


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
                ).seconds < signals_config['sigkill_last']:
                # The user is frantically sending <C-c>s
                if raw_input_async.kill_sigs >= signals_config['sigkill'] - 1:
                    print_helpers.print_out(
                        '\rGot too many {u1}<C-c>{u0}s. ABAAAAAAANDON SHIP!'
                    )
                    cleanup_terminal()
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


def init_terminal():
    readline.parse_and_bind('tab: complete')


def cleanup_terminal():
    # Clean up the terminal before letting go
    history.save_history()
    v.unlock_keyboard()
    v.format.clear_all_chars_attrs()

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

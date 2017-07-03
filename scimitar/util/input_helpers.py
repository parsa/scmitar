# -*- coding: utf-8 -*-
#
# Scimitar: Ye Distributed Debugger
#
# Copyright (c) 2016-2017 Parsa Amini
# Copyright (c) 2016 Hartmut Kaiser
# Copyright (c) 2016 Thomas Heller
#
# Distributed under the Boost Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
from sys import exit
from datetime import datetime as time
import signal
import re
import select
import print_helpers
import prompt_toolkit as ptk
import os.path

from . import signals
from . import vt100 as v
from config import settings

signals_config = settings['signals']
FORMAT_CONSTS = {'u1': v.format._underline_on, 'u0': v.format._underline_off}
history_file = None
custom_completer_type = None


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
        text = ptk.prompt(prompt, patch_stdout=True, history=history_file, completer=custom_completer_type)
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
    # Possibly raised when history file is not accessible
    #    IOError: [Errno 13] Permission denied: u'<PATH>'
    except IOError as e:
        raise e
    finally:
        signal.signal(signal.SIGTSTP, signal.SIG_DFL)
        signal.signal(signal.SIGQUIT, signal.SIG_DFL)
        #signal.signal(signal.SIGALRM, signal.SIG_IGN)
    # We should never reach here
    return None, None


def init_terminal():
    # Load history
    global history_file
    history_file_path = os.path.join(os.path.expanduser('~'), '.scimitar_history')
    history_file = ptk.history.FileHistory(history_file_path)


def register_completer(cmpl_type):
    global custom_completer_type
    custom_completer_type = cmpl_type


def cleanup_terminal():
    # Clean up the terminal before letting go
    v.unlock_keyboard()
    v.format.clear_all_chars_attrs()

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

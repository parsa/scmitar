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
import readline
import select
import os.path

history_file_path = os.path.join(os.path.expanduser('~'), '.scimitar_history')


def load_history():
    try:
        readline.set_history_length(10000)
        readline.read_history_file(history_file_path)
    except IOError:
        pass


def save_history():
    try:
        open(history_file_path, 'a').close()
        readline.write_history_file(history_file_path)
    except IOError:
        pass


# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

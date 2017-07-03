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
from errors import ScimitarError


class AlarmSignal(ScimitarError):
    pass


def __alarm_handler(signum, frame):
    raise AlarmSignal


class StopSignal(ScimitarError):
    pass


def __stop_handler(signum, frame):
    raise StopSignal


class QuitSignal(ScimitarError):
    pass


def __quit_handler(signum, frame):
    raise QuitSignal

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

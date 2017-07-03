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


class ScimitarError(Exception):
    pass


class UnknownCommandError(ScimitarError):
    '''Raised when the command called does not exist.'''

    def __init__(self, cmd):
        self.message = 'Unknown command entered'
        self.expression = cmd


class BadArgsError(ScimitarError):
    '''Raised when arguments of a command are nonsense.'''

    def __init__(self, cmd, expectation):
        self.message = expectation
        self.expression = cmd


class CommandFailedError(ScimitarError):
    '''Raised when command fails and no clue what's wrong.'''

    def __init__(self, cmd, expectation):
        self.message = expectation
        self.expression = cmd


class BadConfigError(ScimitarError):
    '''Raised when configuration seems to have wrong values.'''

    def __init__(self, cmd, expectation):
        self.message = expectation
        self.expression = cmd


class TimeOutError(ScimitarError):
    '''Can be raised when something times out.'''
    pass


class UnexpectedResponseError(ScimitarError):
    '''Raised when encountering an unexpected response during SSH connections.'''
    pass


class CommandImplementationIncompleteError(ScimitarError):
    '''Raised when a command I had to remove is called.'''
    pass


class DeadConsoleError(ScimitarError):
    '''Raised when encountering an unexpected response during terminal sessions.'''
    pass


class ConsoleSessionError(ScimitarError):
    '''Raised when encountering an unexpected response during terminal sessions.'''
    pass

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

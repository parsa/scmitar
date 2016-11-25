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
from collections import namedtuple
from config import *


class HostNotConfiguredError(Exception):
    '''Raised when the target system doesn't exist in the configuration'''
    pass

# FIXME: Fields should not be hardcoded
# NOTE: Does not support default values as is although it is possible to have
# them with the following:
# HostConfig.__new__.__defaults__ = (None,) * len(HostConfig._fields)
HostConfig = namedtuple(
    'HostConfig',
    'login_node user PS1 node_ls_cmd node_ls_fn app_name_cmd app_name_fn pid_ls_cmd pid_ls_fn'
)


def get_host_config(name):
    '''Verifies if the target system exists in the configuration and returns
    the configuration dictionary as an object'''
    # Check if configuration is available under name
    if not name in remotes:
        raise HostNotConfiguredError
    # Get configuration
    return HostConfig(**remotes[name])


def get_gdb_config():
    return settings['gdb']

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

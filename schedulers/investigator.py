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

import re
import errors
import pexpect
import console
import pbs
import slurm


class slurm_type:
    pass


class pbs_type:
    pass


scheduler = None


class MoreThanOneActiveJobError(errors.ScimitarError):
    '''Raised when more than one active job is found.'''
    pass


class NoActiveJobError(errors.ScimitarError):
    '''Raised when no active job is found on the system'''
    pass


class NoSchedulerFoundError(errors.ScimitarError):
    '''Raised when the type of scheduler cannot be determined.'''
    pass


class InvalidJobError(errors.ScimitarError):
    '''Raised when the job id doesn't seem to be valid.'''
    pass


class NoRunningAppFoundError(errors.ScimitarError):
    '''Raised when no running application is found on the system'''
    pass


def which_scheduler(term):
    if term.test_query('type squeue'):
        return slurm_type
    if term.test_query('type qstat'):
        return pbs_type
    return None


def detect_scheduler(term):
    global scheduler
    scheduler = {
        slurm_type: slurm,
        pbs_type: pbs,
        None: None,
    }[which_scheduler(term)]
    if not scheduler:
        raise NoSchedulerFoundError
    return scheduler


def ls_user_jobs(term):
    if not scheduler:
        raise NoSchedulerFoundError
    return scheduler.ls_user_jobs(term)


def detect_active_job(term):
    if not scheduler:
        raise NoSchedulerFoundError
    user_jobs = ls_user_jobs(term)
    if len(user_jobs) > 1:
        raise MoreThanOneActiveJobError
    try:
        return next(iter(user_jobs or []))
    except StopIteration:
        raise NoActiveJobError


def ls_job_pids(term, job_id, job_app = None):
    job_nodes = scheduler.ls_job_nodes(term, job_id)

    if len(job_nodes) == 0:
        raise InvalidJobError

    if not job_app:
        node_0 = job_nodes[0]
        try:
            job_app = scheduler.which_appname(term, node_0)
        except IndexError:
            raise NoRunningAppFoundError

    pid_dict = {}
    for node in job_nodes:
        pids = scheduler.ls_pids(term, node, job_app)
        pid_dict[node] = pids

    return pid_dict

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

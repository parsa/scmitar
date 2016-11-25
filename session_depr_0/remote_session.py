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
from .exceptions import *
from . import modes
from util import configuration, print_ahead
import pexpect.pxssh as sp
##############################
# mode: remote
##############################

global session

# FIXME: RemoteSession should live in a different thread. Whenever connection
# dies or is closed session mode should change instantly. Exceptions must be
# handled properly, too


# TODO: Move this. GDB commands should be processed inside debugging_session
# TODO: If response didn't come by after a certain timeout passes return pending
def process(cmd, args):
    """Sends a query and retrieves the response"""
    response = None
    line = cmd + ' '.join(args)
    try:
        response = session.query(line)
    # FIXME: Find out what exceptions will be passed and handle them properly
    except Exception as e:
        pass
    return (modes.remote, response)


def launch(name, jobid):
    global session
    session = RemoteSession(name, jobid)
    #session.disconnect_all()


class RemoteSession():

    def __init__(self, name, jobid):
        """Starts an SSH connection, finds all computing nodes in the batch job
        and connects to each to find the PIDs belonging to the HPX application.
        NOTE: Only PBS is supported at this point"""
        # NOTE: We're assuming host configurations are all in utils/config.py.
        # Try to get the configuration
        try:
            self.config = configuration.get_host_config(name)
        except configuration.HostNotConfiguredError:
            raise BadArgsError(
                'remote',
                '{name} not found in "utils/config.py"'.format_map(
                    name = name
                )
            )
        # Scheduler Job ID
        self.jobid = jobid
        self.app_name, self.nodes, self.job = None, None, {}
        # Find application name, nodes, PIDs
        self.examine_job()

        self.remote_terminals = None
        self.active_terminal = None
        self.connect_all()

    @classmethod
    def try_attach_to_job(cls, name, job_id = None):
        # Try getting the config
        # Get an examiner
        # Query for user jobs
        # If no job_id given:
        #   If there's only one active job:
        #       Pass the examiner to attempt_launch
        #   Else:
        #       Parse the list and return the results
        # If job_id is given:
        #   If job_id is among active jobs:
        #       Pass the examiner to attempt_launch
        #   Else:
        #       raise an error
        raise CommandImplementationIncompleteError

    @classmethod
    def try_list_jobs(cls, examiner):
        raise CommandImplementationIncompleteError

    @classmethod
    def inspect_job(cls, examiner):
        raise CommandImplementationIncompleteError

    @classmethod
    def try_launch(cls, name, layout):
        # Try getting the config
        # Connect to login node
        # Try launching
        raise CommandImplementationIncompleteError

    def query(self, line):
        self.active_terminal.sendline(line)
        self.active_terminal.prompt()
        return self.active_terminal.before

    # FIXME: Changed this to assume one locality per node.
    # MERGE: hpx_pids (4c2e6efda9334f50a97498ff3df4ca37)
    # TODO: This function's too long. It needs to be refactored.
    def examine_job(self):
        '''Attempts to retrieve job information. Returns a tuple of a)
        application name, b) list of nodes, and c) a dictionary of PIDs'''
        try:
            # SSH to the head node.
            print_ahead(
                'Connecting to {host}...', host = self.config.login_node
            )
            with RemoteJobExaminer(self.config) as examiner:
                # Retrieve list of nodes
                self.nodes = examiner.try_list_nodes(self.jobid)
                print_ahead(
                    'Nodes in job {u1}{jobid}{u0}: {u1}{nodes}{u0}',
                    jobid = self.jobid,
                    nodes = ' '.join(self.nodes)
                )
                # Retrieve application name
                self.app_name = examiner.try_find_running_app(self.nodes[0])
                print_ahead(
                    'Application name: {u1}{app_name}{u0}',
                    app_name = self.app_name
                )
                app_short_name = self.app_name.split('/')[-1]

                # Retrieve the PIDs
                self.job = examiner.try_list_pids(self.nodes, app_short_name)
                print_ahead('PIDs:\n{0}', repr(self.job))

        # Broken pipe
        except sp.ExceptionPxssh as e:
            raise CommandFailedError('examine_job', e.expectation)

    def connect_all(self):
        '''Connects to appropriate remote machines and launches a GDB session
        per each PID'''
        gdb_config = configuration.settings['gdb']
        gdb_cmd = gdb_config['cmd']

        self.remote_terminals = []

        for node, pids in self.job.items():
            for pid in pids:
                try:
                    conn = sp.pxssh(echo = False)
                    conn.login(
                        self.config.login_node, self.config.user,
                        self.config.PS1
                    )

                    # Build the command line and launch GDB
                    gdb_cmd += [gdb_config['attach'].format(pid = pid)]
                    cmd = ['ssh', node].extend(gdb_cmd)
                    cmd_str = ' '.join(cmd)

                    conn.PROMPT = gdb_config['mi_prompt_pattern']
                    conn.sendline(cmd_str)

                    self.remote_terminals.append(conn)

                except sp.ExceptionPxssh as e:
                    raise e

        self.active_terminal = self.remote_terminals[0]

    def disconnect_all(remote_terms):
        '''Disconnects the SSH connections of all GDB sessions'''
        if self.remote_terminal:
            self.active_terminal = None
            for term in self.remote_terminals:
                term.close()

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        self.disconnect_all()


class RemoteJobExaminer:

    def __init__(self, cfg):
        self.cfg = cfg
        self.conn = None

    def __enter__(self):
        # SSH to the head node.
        self.conn = sp.pxssh(echo = False)
        self.conn.login(
            self.cfg.login_node, self.cfg.user, original_prompt = self.cfg.PS1
        )
        return self

    def __exit__(self, _type, _value, _traceback):
        self.conn.close()

    def try_list_nodes(self, jobid):
        # Get list of nodes.
        node_ls_cmd = self.cfg.node_ls_cmd.format(jobid = jobid)
        node_ls_raw = self.query(node_ls_cmd)
        # Check if the command actually succeeded
        self.verify_command_success(
            '''
Cannot list nodes in job {jobid}. Listing failed with exit status code {status_code}.
Make sure Job ID {jobid} is correct and the job has started''',
            '''
Got an unexpected response from the listing command. Cannot proceed''',
            jobid = jobid
        )
        # Process the result and get the hostnames
        # TODO: Handle potential exceptions when the text was messed up.
        # TODO: Handle potential exceptions when the function messes up.
        nodes = self.cfg.node_ls_fn(node_ls_raw)
        if type(nodes) is not list:
            raise CommandFailedError(
                'examine_job', '''
Processing function did not return a list'''
            )
        return nodes

    def try_find_running_app(self, node_0):
        # TODO: Check if it actually returned a name
        # Retrieves application name
        app_name_cmd = self.cfg.app_name_cmd.format(host = node_0)
        app_name_raw = self.query(app_name_cmd)
        # Check if the command actually succeeded
        self.verify_command_success(
            '''
Cannot retrieve running application's name. Please make sure the app is
running''', '''
Got an unexpected response while trying to retrieve running application'
name. Cannot proceed'''
        )
        if not app_name_raw:
            raise NoRunningAppFoundError
        return self.cfg.app_name_fn(app_name_raw)

    def try_list_pids(self, nodes, app_short_name):
        job = {}
        # Connect and collect PIDs
        for node in nodes:
            # TODO: Check if it actually returned PIDs
            # Build the command
            pid_ls_cmd = self.cfg.pid_ls_cmd.format(
                host = node, appname = app_short_name
            )
            # Send the command
            pids_raw = self.query(pid_ls_cmd)
            # Process the list
            pids = self.cfg.pid_ls_fn(pids_raw)
            # See if it actually is a list or not
            if type(pids) is not list:
                raise CommandFailedError(
                    'list_pids', '''
Processing function did not return a list'''
                )
            # Add to the dictionary
            job[node] = pids
        return job

    def query(self, msg):
        self.conn.sendline(msg)
        self.conn.prompt()
        return self.conn.before

    def verify_command_success(self, fail_msg, error_msg, **kwargs):
        # Check if the listing command was successful.
        status = self.query('echo $?')
        try:
            status = int(status)
            kwargs['status_code'] = status
            # If it had failed
            if status != 0:
                raise CommandFailedError(
                    'examine_job', fail_msg.format(**kwargs)
                )
        except ValueError:
            raise CommandFailedError('examine_job', error_msg.format(**kwargs))

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

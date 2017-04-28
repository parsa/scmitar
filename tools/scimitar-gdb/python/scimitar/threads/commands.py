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
'''
hpx.py - A set of functions to help debug a HPX binary inside of GDB
'''

import gdb
import re
import boost
import stl
import scimitar
from hpx_thread import HPXThread
from hpx_gdb_state import HPXGdbState


class HPXCommand(gdb.Command):
    "Commands to introspect the state of a HPX program."

    def __init__(self):
        gdb.Command.__init__(
            self, "hpx", scimitar.GDB_CMD_TYPE, gdb.COMPLETE_NONE, True
        )

    #def invoke(self, arg, from_tty):
    #    print("Hello World")


class HPXListCommand(gdb.Command):
    "List various HPX states"

    def __init__(self):
        super(
            HPXListCommand, self
        ).__init__("hpx list", scimitar.GDB_CMD_TYPE, gdb.COMPLETE_NONE, True)

    #def invoke(self, arg, from_tty):
    #    print("Hello World")


class HPXListThreadsCommand(gdb.Command):
    '''
    Get the list of all HPX threads on this locality
    '''

    def __init__(self):
        super(HPXListThreadsCommand, self).__init__(
            "hpx list threads", scimitar.GDB_CMD_TYPE, gdb.COMPLETE_NONE, False
        )

    def deref_stack(self, addr):
        return addr.reinterpret_cast(gdb.lookup_type("std::size_t").pointer()
                                     ).dereference()

    def invoke(self, arg, from_tty):
        runtime = gdb.parse_and_eval("hpx::runtime::runtime_")["ptr_"
                                                               ].dereference()
        thread_manager_ptr = runtime.cast(runtime.dynamic_type
                                          )["thread_manager_"]['px']
        thread_manager = thread_manager_ptr.cast(
            thread_manager_ptr.dynamic_type
        ).dereference()

        scheduler = thread_manager['pool_']['sched_']

        # queues_, std::vector
        item = scheduler['queues_']['_M_impl']['_M_start']
        end = scheduler['queues_']['_M_impl']['_M_finish']

        count = 0
        while not item == end:
            print('Thread queue %d:' % count)
            thread_map = stl.StdUnorderedSet(
                item.dereference().dereference()['thread_map_']
            )
            for k, v in thread_map:
                thread = HPXThread(v['px'].dereference())

                thread.info()
                print('')
            item = item + 1
            count = count + 1
        # high_priority_queues_, std::vector
        item = scheduler['high_priority_queues_']['_M_impl']['_M_start']
        end = scheduler['high_priority_queues_']['_M_impl']['_M_finish']

        count = 0
        while not item == end:
            print('High Priority Thread queue %d:' % count)
            thread_map = stl.StdUnorderedSet(
                item.dereference().dereference()['thread_map_']
            )
            for k, v in thread_map:
                thread = HPXThread(v['px'])

                thread.info()
                print('')
            item = item + 1
            count = count + 1

        print('Low priority queue:')
        thread_map = stl.StdUnorderedSet(
            scheduler['low_priority_queue_']['thread_map_']
        )
        for k, v in thread_map:
            thread = HPXThread(v['px'])

            thread.info()
            print('')


class HPXSelectThreadCommand(gdb.Command):
    '''
    This command let's you overwrite the current frame with a suspended HPX thread.
    To get a list of currently running hpx threads see 'hpx list threads'.

    Arguments:
       <thread-id>: A thread id to switch to
       restore: Restores the state of the overwritten threads
    '''

    def __init__(self):
        super(HPXSelectThreadCommand, self).__init__(
            'hpx thread', scimitar.GDB_CMD_TYPE, gdb.COMPLETE_NONE, False
        )

    def deref_stack(self, addr):
        return addr.reinterpret_cast(gdb.lookup_type('std::size_t').pointer()
                                     ).dereference()

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)
        if len(argv) != 1:
            print(
                'Error: You need to supply at least one argument. See help hpx thread'
            )
            return

        if argv[0] == 'restore':
            state.restore()
            return

        if argv[0][0:2] == '0x':#.beginswith('0x'):
            thread_id = gdb.Value(int(argv[0], 16))
        else:
            thread_id = gdb.Value(int(argv[0]))

        print('%s %x' % (argv[0][0:2], thread_id))

        thread_id = thread_id.reinterpret_cast(gdb.lookup_type('hpx::threads::thread_data').pointer())

        thread = HPXThread(thread_id)

        print('Switched to HPX Thread 0x%x' % thread_id)
        print(thread.pc_string)

        state.save_context(thread.context.switch())


def restore_context(event):
    state.restore()


class HPXContinueCommand(gdb.Command):
    '''
    Similiar to 'continue' but restores any selected HPX threads before continuing.
    '''

    def __init__(self):
        super(HPXContinueCommand, self).__init__(
            'hpx continue', scimitar.GDB_CMD_TYPE, gdb.COMPLETE_NONE, False
        )

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)
        state.restore()

        #gdb.execute('thread 15', False, True)
        #cur_os_thread = gdb.selected_thread().num

        frame = gdb.newest_frame()

        handle_attach = False
        count = 0
        while True:
            function = frame.function()
            if function and function.name == 'hpx::util::command_line_handling::handle_attach_debugger()':
                handle_attach = True
                break
            frame = frame.older()
            if not frame or count > 5:
                break
            count = count + 1

        if handle_attach:
            frame.select()
            gdb.execute('set var i = 1', True)

        #gdb.execute('thread %d' % cur_os_thread, False, True)

        if len(argv) == 0:
            print('Continuing...')
            gdb.execute('continue')
        else:
            if argv[0] != 'hook':
                print('wrong argument ...')


state = HPXGdbState()
scimitar.commands.extend([
    HPXCommand,
    HPXContinueCommand,
    HPXListCommand,
    HPXListThreadsCommand,
    HPXSelectThreadCommand,
])

#gdb.events.cont.connect(restore_context)

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
import gdb
import re


class HPXThread():

    class Context(object):

        def __init__(self):
            self.pc = gdb.parse_and_eval('$pc')
            self.r15 = gdb.parse_and_eval('$r15')
            self.r14 = gdb.parse_and_eval('$r14')
            self.r13 = gdb.parse_and_eval('$r13')
            self.r12 = gdb.parse_and_eval('$r12')
            self.rdx = gdb.parse_and_eval('$rdx')
            self.rax = gdb.parse_and_eval('$rax')
            self.rbx = gdb.parse_and_eval('$rbx')
            self.rbp = gdb.parse_and_eval('$rbp')
            self.sp = gdb.parse_and_eval('$sp')

        def switch(self):
            prev_ctx = self

            def set_reg(reg, value):
                gdb.execute("set $%s = 0x%x" % (reg, value & 2 ** 64 - 1))

            set_reg('pc', self.pc)
            set_reg('r15', self.r15)
            set_reg('r14', self.r14)
            set_reg('r13', self.r13)
            set_reg('r12', self.r12)
            set_reg('rdx', self.rdx)
            set_reg('rax', self.rax)
            set_reg('rbx', self.rbx)
            set_reg('rbp', self.rbp)
            set_reg('sp', self.sp)

            return prev_ctx

    def __init__(self, thread_data):
        self.thread_data = thread_data

        #  current_state_ = {
        #    <boost::atomics::detail::base_atomic
        #       <hpx::threads::detail::combined_tagged_state
        #           <hpx::threads::thread_state_enum,
        #           hpx::threads::thread_state_ex_enum
        #       >, void>
        #    > = { m_storage = 360569445166350338 }, <No data fields>
        #  },
        #  component_id_ = 8198320,
        #  description_ = thread_description {{ [desc] {0x7ffff4aa0cb5 "call_startup_functions_action"} }},
        #  lco_description_ = thread_description {{ [desc] {0x7ffff4918a9d "<unknown>"} }},
        #  parent_locality_id_ = 0,
        #  parent_thread_id_ = 0x7f3090,
        #  parent_thread_phase_ = 1,
        #  marked_state_ = hpx::threads::unknown,
        #  priority_ = hpx::threads::thread_priority_normal,
        #  requested_interrupt_ = false,
        #  enabled_interrupt_ = true,
        #  ran_exit_funcs_ = false,
        #  exit_funcs_ = std::deque with 0 elements,
        #  scheduler_base_ = 0x7cf5b8,
        #  count_ = {
        #    value_ = {
        #      <boost::atomics::detail::base_atomic<long, int>> = {
        #        m_storage = 1
        #      }, <No data fields>
        #    }
        #  },
        #  stacksize_ = 131072,
        #  coroutine_ = {
        #    m_pimpl = (boost::intrusive_ptr<hpx::threads::coroutines::detail::coroutine_impl>) 0x7fffee728180
        #  },
        #  pool_ = 0x7e9a60
        #}

        context_impl = self.thread_data['coroutine_']['m_pimpl']['px']
        self.stack_end = context_impl['m_stack'] + context_impl['m_stack_size']
        self.stack_start = context_impl['m_stack']
        self.m_sp = context_impl['m_sp']

        self.id = context_impl['m_thread_id']
        self.parent_id = self.thread_data['parent_thread_id_']
        self.description = self.thread_data['description_']
        self.lco_description = self.thread_data['lco_description_']

        combined_state = self.thread_data['current_state_']['m_storage']

        current_state_type = gdb.lookup_type('hpx::threads::thread_state_enum')
        self.state = combined_state
        self.state = self.state.cast(current_state_type)
        self.state = self.state >> 56 & 0xff

        current_state_ex_type = gdb.lookup_type(
            'hpx::threads::thread_state_ex_enum'
        )
        self.state_ex = combined_state
        self.state_ex = self.state_ex.cast(current_state_ex_type)
        self.state_ex = self.state_ex >> 48 & 0xff

        self.size_t = gdb.lookup_type("std::size_t")
        stack = self.m_sp.reinterpret_cast(self.size_t)

        self.context = HPXThread.Context()
        self.context.pc = self.deref_stack(stack + (8 * 8))
        self.context.r15 = self.deref_stack(stack + (8 * 0))
        self.context.r14 = self.deref_stack(stack + (8 * 1))
        self.context.r13 = self.deref_stack(stack + (8 * 2))
        self.context.r12 = self.deref_stack(stack + (8 * 3))
        self.context.rdx = self.deref_stack(stack + (8 * 4))
        self.context.rax = self.deref_stack(stack + (8 * 5))
        self.context.rbx = self.deref_stack(stack + (8 * 6))
        self.context.rbp = self.deref_stack(stack + (8 * 7))
        self.context.sp = stack + (8 * 8)

        prev_context = self.context.switch()
        frame = gdb.newest_frame()
        function_name = frame.name()
        p = re.compile("^hpx::util::coroutines.*$")

        try:
            while p.match(function_name):
                if frame.older() is None:
                    break
                frame = frame.older()
                function_name = frame.name()

            if frame.older() is not None:
                frame = frame.older()
                function_name = frame.name()

            line = frame.function().line
            filename = frame.find_sal().symtab.filename

            self.pc_string = "0x%x in " % frame.pc(
            ) + "%s at " % function_name + "%s:" % filename + "%d" % line
        except:
            self.pc_string = "0x%x in " % frame.pc() + "<unkown>"

        self.frame = frame

        prev_context.switch()

    def deref_stack(self, addr):
        return addr.reinterpret_cast(self.size_t.pointer()).dereference()

    def info(self):
        print(" Thread 0x%x" % self.id)
        if self.m_sp.reinterpret_cast(self.m_sp.dereference().type
                                      ) > self.stack_end:
            print(" This thread has a stack overflow")
        print("  parent thread = %s" % self.parent_id)
        print("  description = %s" % self.description)
        print(self.lco_description.type)
        print(self.lco_description.address)
        print("  lco_description = %s" % self.lco_description)
        print("  state = %s" % self.state)
        print("  state_ex = %s" % self.state_ex)
        print("  pc = %s" % self.pc_string)

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

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
import scimitar


class FuturePrinter(object):

    def __init__(self, val, type_):
        self.val = val
        self.type_ = type_
        # Values
        self.px = self.val['shared_state_']['px']
        self.state_ = self.px['state_']
        if 'storage_' in self.px:
            self.storage_ = self.px['storage_']
        else:
            self.storage_ = None

        # Template type
        self.tmpl = str(self.val.type.template_argument(0))
        # Conditions
        # enum hpx::lcos::detail::future_data<T>::state:
        #   empty = 0
        #   ready = 1
        #   value = 3
        #   exception = 5
        self.is_void = self.tmpl == 'void'
        self.is_exception = bool(self.state_ == 5)
        self.is_value = bool(self.state_ == 3)

        if self.is_void:
            if self.is_exception:
                #value_t = gdb.lookup_type('boost::exception_ptr').pointer()
                #self.value = self.storage_.address.cast(value_t).dereference()
                pass
        else:
            if self.is_value:
                value_t = gdb.lookup_type(self.tmpl).pointer()
                self.value = self.storage_.address.cast(value_t).dereference()
            if self.is_exception:
                value_t = gdb.lookup_type('boost::exception_ptr').pointer()
                self.value = self.storage_.address.cast(value_t).dereference()

    def to_string(self):
        display_string = 'px: %s, state: %s' % (self.px,
                                                self.state_, )
        return "%s: {{ %s }} %s" % (
            self.type_,
            display_string,
            self.val.address,
        )

    def children(self):
        result = []
        if self.is_void:
            pass
            #if self.is_exception:
            #    result.extend([('value', self.value), ])
        else:
            if self.is_value:
                result.extend([('value', self.value), ])
            elif self.is_exception:
                result.extend([('value', self.value), ])
            else:
                result.extend([('value', '(unknown)'), ])
        return result


scimitar.pretty_printers['hpx::lcos::(shared_)?future<.+>'] = FuturePrinter

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

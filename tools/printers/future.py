#!/usr/bin/env python
# coding: utf-8
'''
    Scimitar: Ye Distributed Debugger
    ~~~~~~~~
    :copyright:
    Copyright (c) 2016 Parsa Amini
    Copyright (c) 2016 Hartmut Kaiser
    Copyright (c) 2016 Thomas Heller
    :license:
    Distributed under the Boost Software License, Version 1.0. (See accompanying
    file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
'''
import gdb

printer_dict = {}

class FuturePrinter(object):
    def __init__(self, expr, val, tmpltype):
        self.val = val
        self.expr = expr

    def display_hint(self):
        return self.expr

    def to_string(self):
        txt = '%s' % gdb.parse_and_eval('shared_state_.px')
        return "(%s) {{ %s }} %#02x" % (self.expr, txt, self.val.address)

    def children(self):
        result = []
        if self.tmpltype == 'void':
            # FIXME: Something's not right here
            if bool(gdb.parse_and_eval('shared_state_.px->state_ == 5')):
                result.extend([
                    ('value', '%s' % gdb.parse_and_eval('*((boost::exception_ptr*)(shared_state_.px->storage_._Pad))')),
                ])
        else:
            if bool(gdb.parse_and_eval('shared_state_.px->state_ == 3')):
                result.extend([
                    ('value', '%s' % gdb.parse_and_eval('*(($T1 *)(shared_state_.px->storage_._Pad))')),
                ])
            elif bool(gdb.parse_and_eval('shared_state_.px->state_ == 5')):
                result.extend([
                    ('value', '%s' % gdb.parse_and_eval('*((boost::exception_ptr*)(shared_state_.px->storage_._Pad))')),
                ])
                
        return result
printer_dict['hpx::lcos::(shared_)?future<(?P<tmpl>\w*)>'] = FuturePrinter

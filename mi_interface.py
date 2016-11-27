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

_result_pattern = re.compile(
    r'\^(?:(done)(?:,([^\r\n]+))?|(running)|(connected)|(error),msg="((?:\\.|[^"\\])+)"(?:,code="((?:\\.|[^"\\])+))?|(exit))'
)
_stream_pattern = re.compile(r'([~@&])"((?:\\.|[^\"\\])+)"')

#_async_pattern = re.compile(r'')


def _safe_unescape(msg):
    if type(msg) is str:
        return msg.decode('string_escape')
    return ''


def _safe_join_unescape(msg_col):
    if msg_col:
        return _safe_unescape(''.join(msg_col))
    return ''


def parse(output_records):
    result_records = re.findall(_result_pattern, output_records)
    stream_records = re.findall(_stream_pattern, output_records)

    result_indicator = None
    if result_records:
        result_record = result_records[0]
        result_indicator_regex = next((
            result_record[index] for index in (0, 2, 3, 4, 7)
            if result_record[index]
        ), None)

        result_indicator = {
            'done': (indicator_done, _safe_unescape(result_record[1])),
            'running': (indicator_running, ),
            'connected': (indicator_connected, ),
            'error': (
                indicator_error, _safe_unescape(result_record[5]),
                _safe_unescape(result_record[6])
            ),
            'exit': (indicator_exit, ),
        }[result_indicator_regex]

    console_list, target_list, log_list = [], [], []
    for stream in stream_records:
        {
            '~': console_list,
            '@': target_list,
            '&': log_list,
        }[stream[0]].append(stream[1])

    console_out = _safe_join_unescape(console_list)
    target_out = _safe_join_unescape(target_list)
    log_out = _safe_join_unescape(log_list)

    return result_indicator, console_out, target_out, log_out


class indicator_done:
    pass


class indicator_running:
    pass


class indicator_connected:
    pass


class indicator_error:
    pass


class indicator_exit:
    pass

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

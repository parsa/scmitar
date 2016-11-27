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


class CommandCompleter(object):

    def __init__(self):
        self.current_candidates = []

    def _prune_nonmatches(candidates, being_completed):
        if being_completed:
            self.current_candidates = [
                candidate for candidate in candidates
                if candidate.startswith(being_completed)
            ]
        else:
            self.current_candidates = candidates

    def _complete_command(self):
        raise NotImplementedError('Must override _complete_command')
        return commands.keys()

    def _complete_command_arguments(self, command, tokens):
        raise NotImplementedError('Must override _complete_command_arguments')
        return self.options[command]

    def _build_match_list(self, original_line, begin_index, end_index):
        tokens = original_line.split()
        # if first token
        if not tokens:
            self.matches = self._complete_command()
        else:
            try:
                if begin_index == 0:
                    candidates = commands.keys()
                else:
                    first_token = words[0]
                    candidates = self._complete_command_arguments(
                        first_token, tokens
                    )
                self._prune_nonmatches(
                    candidates, original_line[begin_index:end_index]
                )
            except (KeyError, IndexError):
                self.current_candidates = []

    def complete(self, text, state):
        if state == 0:
            self._build_match_list(
                readline.get_line_buffer(),
                readline.get_begidx(), readline.get_endidx()
            )
        try:
            return self.current_candidates[state]
        except IndexError:
            pass
        return None

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

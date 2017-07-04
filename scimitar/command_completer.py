# -*- coding: utf-8 -*-
#
# Scimitar: Ye Distributed Debugger
# 
# Copyright (c) 2016-2017 Parsa Amini
# Copyright (c) 2016 Hartmut Kaiser
# Copyright (c) 2016 Thomas Heller
#
# Distributed under the Boost Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
from prompt_toolkit.completion import Completer, Completion


class CommandCompleter(Completer):

    def __init__(self):
        self.current_candidates = []

    def _complete_command(self):
        raise NotImplementedError('Must override _complete_command')

    def _complete_command_arguments(self, command, words):
        raise NotImplementedError('Must override _complete_command_arguments')

    def _prune_nonmatches(self, candidates, being_completed):
        if being_completed:
            result = [
                candidate for candidate in candidates
                if candidate.startswith(being_completed)
            ]
        else:
            result = candidates

        # If it's the only choice
        if result and len(result) == 1:
            return [result[0] + ' ']
        return result

    def get_completions(self, document, complete_event):
        last_word = document.get_word_before_cursor()

        # First token
        if not document.current_line or not ' ' in document.current_line:
            candidates = self._complete_command()
        else:
            words = document.current_line.split()

            candidates = self._complete_command_arguments(
                words[0], words[1:]
            )

        matches = self._prune_nonmatches(
            candidates, last_word
        )

        if not matches:
            return []
        return [Completion(i, start_position=-len(last_word)) for i in matches]

# vim: :ai:sw=4:ts=4:sts=4:et:ft=python:fo=corqj2:sm:tw=79:

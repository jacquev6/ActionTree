# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import ctypes
import subprocess
import sys
import tempfile
import time
import unittest

try:
    import unittest.mock
except ImportError:  # Not unittested: test code for Python 2
    import mock
    unittest.mock = mock

from ActionTree import *

libc = ctypes.CDLL(None)


class TestAction(Action):
    def __init__(
        self, label,
        exception, return_value, delay,
        events_file, end_event,
        print_on_stdout, print_on_stderr, puts_on_stdout, echo_on_stdout,
        accept_failed_dependencies,
    ):
        super(TestAction, self).__init__(label=label, accept_failed_dependencies=accept_failed_dependencies)
        self.__exception = exception
        self.__return_value = return_value
        self.__delay = delay
        self.__events_file = events_file
        self.__end_event = end_event
        self.__print_on_stdout = print_on_stdout
        self.__print_on_stderr = print_on_stderr
        self.__puts_on_stdout = puts_on_stdout
        self.__echo_on_stdout = echo_on_stdout

    def do_execute(self, dependency_statuses):
        for d in self.dependencies:
            assert self.accept_failed_dependencies or dependency_statuses[d].status == SUCCESSFUL
        with open(self.__events_file, "a") as f:
            f.write("{}\n".format(str(self.label).lower()))
        if self.__delay:
            time.sleep(self.__delay)
        if self.__end_event:
            with open(self.__events_file, "a") as f:
                f.write("{}\n".format(str(self.label).upper()))
        if isinstance(self.__print_on_stdout, str):
            print(self.__print_on_stdout)
        elif isinstance(self.__print_on_stdout, list):
            for (p, d) in self.__print_on_stdout:
                print(p)
                sys.stdout.flush()
                time.sleep(d)
        if self.__print_on_stderr:
            print(self.__print_on_stderr, file=sys.stderr)
        if self.__puts_on_stdout:
            libc.puts(self.__puts_on_stdout)
        if self.__echo_on_stdout:
            subprocess.check_call(["echo", self.__echo_on_stdout])
        if self.__exception:
            raise self.__exception
        else:
            return self.__return_value


class ActionTreeTestCase(unittest.TestCase):
    def setUp(self):
        # print(self.id())
        (fd, events_file) = tempfile.mkstemp()
        os.close(fd)
        self.__events_file = events_file

    def tearDown(self):
        os.unlink(self.__events_file)

    def _action(
        self, label,
        exception=None, return_value=None, delay=None,
        end_event=False,
        print_on_stdout=None, print_on_stderr=None, puts_on_stdout=None, echo_on_stdout=None,
        accept_failed_dependencies=False,
        *args, **kwds
    ):
        return TestAction(
            label,
            exception, return_value, delay,
            self.__events_file, end_event,
            print_on_stdout, print_on_stderr, puts_on_stdout, echo_on_stdout,
            accept_failed_dependencies,
            *args, **kwds
        )

    def assertEventsEqual(self, groups):
        with open(self.__events_file) as f:
            events = [line.strip() for line in f.readlines()]
        for group in groups.split(" "):
            self.assertEqual(sorted(group), sorted(events[:len(group)]))
            events = events[len(group):]
        self.assertEqual(events, [])

    def assertEventsIn(self, expected_events):
        with open(self.__events_file) as f:
            events = [line.strip() for line in f.readlines()]
        self.assertIn(events, expected_events)


# class TestHooks(Hooks):
#     def action_pending(self, time, action):
#         print("action_pending", time, action.label)

#     def action_ready(self, time, action):
#         print("action_ready", time, action.label)

#     def action_canceled(self, time, action):
#         print("action_canceled", time, action.label)

#     def action_started(self, time, action):
#         print("action_started", time, action.label)

#     def action_printed(self, time, action, text):
#         print("action_printed", time, action.label, text)

#     def action_successful(self, time, action, return_value):
#         print("action_successful", time, action.label, return_value)

#     def action_failed(self, time, action, exception):
#         print("action_failed", time, action.label, exception)

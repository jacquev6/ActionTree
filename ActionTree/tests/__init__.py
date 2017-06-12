# coding: utf8

# Copyright 2013-2015 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import ctypes
import subprocess
import sys
import tempfile
import time
import unittest

try:
    import unittest.mock
except ImportError:
    import mock
    unittest.mock = mock

from ActionTree import *

libc = ctypes.CDLL(None)


class TestAction(Action):
    def __init__(
        self, name,
        exception, return_value, delay,
        events_file, end_event,
        print_on_stdout, print_on_stderr, puts_on_stdout, echo_on_stdout,
    ):
        super(TestAction, self).__init__(name)
        self.__exception = exception
        self.__return_value = return_value
        self.__delay = delay
        self.__events_file = events_file
        self.__end_event = end_event
        self.__print_on_stdout = print_on_stdout
        self.__print_on_stderr = print_on_stderr
        self.__puts_on_stdout = puts_on_stdout
        self.__echo_on_stdout = echo_on_stdout

    def do_execute(self):  # pragma no cover (Test code executed in child process)
        with open(self.__events_file, "a") as f:
            f.write("{}\n".format(self.label.lower()))
        if self.__delay:
            time.sleep(self.__delay)
        if self.__end_event:
            with open(self.__events_file, "a") as f:
                f.write("{}\n".format(self.label.upper()))
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
        self, name,
        exception=None, return_value=None, delay=None,
        end_event=False,
        print_on_stdout=None, print_on_stderr=None, puts_on_stdout=None, echo_on_stdout=None,
    ):
        return TestAction(
            name,
            exception, return_value, delay,
            self.__events_file, end_event,
            print_on_stdout, print_on_stderr, puts_on_stdout, echo_on_stdout
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

# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

from ActionTree import *
from . import *


class ExecutionTestCase(ActionTreeTestCase):
    def test_successful_nothing(self):
        a = self._action("a")
        report = execute(a)

        self.assertEqual(report.get_action_status(a).output, "")

    def test_failed_nothing(self):
        a = self._action("a", exception=Exception())
        report = execute(a, do_raise=False)

        self.assertEqual(report.get_action_status(a).output, "")

    def test_canceled_nothing(self):
        a = self._action("a")
        a.add_dependency(self._action("b", exception=Exception()))
        report = execute(a, do_raise=False)

        self.assertIsNone(report.get_action_status(a).output)

    def test_print(self):
        a = self._action("a", print_on_stdout="printed on stdout")
        report = execute(a)

        self.assertEqual(report.get_action_status(a).output, "printed on stdout\n")

    def test_print_stderr(self):
        a = self._action("a", print_on_stderr="printed on stderr")
        report = execute(a)

        self.assertEqual(report.get_action_status(a).output, "printed on stderr\n")

    def test_echo(self):
        a = self._action("a", echo_on_stdout="echoed on stdout")
        report = execute(a)

        self.assertEqual(report.get_action_status(a).output, "echoed on stdout\n")

    def test_puts(self):
        a = self._action("a", puts_on_stdout=b"putsed on stdout")
        report = execute(a)

        self.assertEqual(report.get_action_status(a).output, "putsed on stdout\n")

    def test_many_print(self):
        MANY = 5
        a = self._action("a")
        x = self._action("x", print_on_stdout=[("x", 0.1)] * MANY)
        y = self._action("y", print_on_stdout=[("y", 0.1)] * MANY)
        a.add_dependency(x)
        a.add_dependency(y)
        report = execute(a)

        self.assertEqual(report.get_action_status(x).output, "x\n" * MANY)
        self.assertEqual(report.get_action_status(y).output, "y\n" * MANY)

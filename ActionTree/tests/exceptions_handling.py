# coding: utf8

# Copyright 2013-2017 Vincent Jacques <vincent@vincent-jacques.net>

from __future__ import division, absolute_import, print_function

import random

from ActionTree import *
from . import *


class ExceptionsHandlingTestCase(ActionTreeTestCase):
    def test_simple_failure(self):
        a = self._action("a", exception=Exception("foobar"))

        with self.assertRaises(CompoundException) as catcher:
            execute(a)
        report = catcher.exception.execution_report

        self.assertEqual(len(catcher.exception.exceptions), 1)
        self.assertEqual(catcher.exception.exceptions[0].args, ("foobar",))

        self.assertFalse(report.is_success)
        self.assertEqual(report.get_action_status(a).status, FAILED)

    def test_exit(self):
        a = self._action("a", exception=SystemExit())

        with self.assertRaises(CompoundException) as catcher:
            execute(a)
        report = catcher.exception.execution_report

        self.assertEqual(len(catcher.exception.exceptions), 1)
        self.assertEqual(catcher.exception.exceptions[0].__class__, SystemExit)

        self.assertFalse(report.is_success)
        self.assertEqual(report.get_action_status(a).status, FAILED)

    def test_keyboard_interrupt(self):
        a = self._action("a", exception=KeyboardInterrupt())

        with self.assertRaises(CompoundException) as catcher:
            execute(a)
        report = catcher.exception.execution_report

        self.assertEqual(len(catcher.exception.exceptions), 1)
        self.assertEqual(catcher.exception.exceptions[0].__class__, KeyboardInterrupt)

        self.assertFalse(report.is_success)
        self.assertEqual(report.get_action_status(a).status, FAILED)

    def test_simple_failure_without_raise(self):
        a = self._action("a", exception=Exception("foobar"))

        report = execute(a, do_raise=False)

        self.assertFalse(report.is_success)
        self.assertEqual(report.get_action_status(a).status, FAILED)
        self.assertEqual(report.get_action_status(a).exception.args, ("foobar",))

    def test_exception_in_dependency(self):
        a = self._action("a")
        b = self._action("b", exception=Exception("foobar"))
        a.add_dependency(b)

        with self.assertRaises(CompoundException) as catcher:
            execute(a)
        report = catcher.exception.execution_report

        self.assertEqual(len(catcher.exception.exceptions), 1)
        self.assertEqual(catcher.exception.exceptions[0].args, ("foobar",))

        self.assertFalse(report.is_success)
        self.assertEqual(report.get_action_status(a).status, CANCELED)
        self.assertEqual(report.get_action_status(b).status, FAILED)

    def test_exceptions_in_dependency_with_accept_failed_dependencies(self):
        a = self._action("a", accept_failed_dependencies=True)
        b = self._action("b", exception=Exception("foobar"))
        a.add_dependency(b)

        with self.assertRaises(CompoundException) as catcher:
            execute(a)
        report = catcher.exception.execution_report

        self.assertFalse(report.is_success)
        self.assertEqual(report.get_action_status(a).status, SUCCESSFUL)
        self.assertEqual(report.get_action_status(b).status, FAILED)

    def test_exceptions_in_dependencies_with_keep_going(self):
        a = self._action("a")
        b = self._action("b", exception=Exception("eb"))
        c = self._action("c", exception=Exception("ec"))
        d = self._action("d")
        a.add_dependency(b)
        a.add_dependency(c)
        a.add_dependency(d)

        with self.assertRaises(CompoundException) as catcher:
            execute(a, cpu_cores=1, keep_going=True)
        report = catcher.exception.execution_report

        self.assertEqual(len(catcher.exception.exceptions), 2)
        self.assertEqual(sorted(ex.args for ex in catcher.exception.exceptions), [("eb",), ("ec",)])

        self.assertEqual(report.get_action_status(a).status, CANCELED)
        self.assertEqual(report.get_action_status(b).status, FAILED)
        self.assertEqual(report.get_action_status(c).status, FAILED)
        self.assertEqual(report.get_action_status(d).status, SUCCESSFUL)

    def test_exceptions_in_long_branch_dependencies_with_keep_going(self):
        a = self._action("a")
        b = self._action("b")
        c = self._action("c")
        d = self._action("d")
        e = self._action("e", exception=Exception("foobar"))
        f = self._action("f")
        g = self._action("g")
        a.add_dependency(b)
        b.add_dependency(c)
        a.add_dependency(d)
        d.add_dependency(e)
        a.add_dependency(f)
        f.add_dependency(g)

        with self.assertRaises(CompoundException) as catcher:
            execute(a, cpu_cores=1, keep_going=True)
        report = catcher.exception.execution_report

        self.assertEqual(len(catcher.exception.exceptions), 1)
        self.assertEqual(catcher.exception.exceptions[0].args, ("foobar",))

        self.assertEqual(report.get_action_status(a).status, CANCELED)
        self.assertEqual(report.get_action_status(b).status, SUCCESSFUL)
        self.assertEqual(report.get_action_status(c).status, SUCCESSFUL)
        self.assertEqual(report.get_action_status(d).status, CANCELED)
        self.assertEqual(report.get_action_status(e).status, FAILED)
        self.assertEqual(report.get_action_status(f).status, SUCCESSFUL)
        self.assertEqual(report.get_action_status(g).status, SUCCESSFUL)

    def test_exceptions_in_dependencies_without_keep_going(self):
        c_was_canceled = False
        c_was_executed = False
        b_was_added_before_c = False
        b_was_added_after_c = False
        # This is a probabilistic test:
        # - when c is executed before b, c cannot be canceled
        # - when c is executed after b, c is canceled
        # We repeat the test until we see both behaviors or we reach a limit
        for i in xrange(100):  # Not unittested: test code
            a = self._action("a")
            b = self._action("b", exception=Exception())
            c = self._action("c")
            if random.random() < 0.5:
                a.add_dependency(b)
                a.add_dependency(c)
                b_was_added_before_c = True
            else:
                a.add_dependency(c)
                a.add_dependency(b)
                b_was_added_after_c = True

            report = execute(a, cpu_cores=1, keep_going=False, do_raise=False)

            self.assertEqual(report.get_action_status(a).status, CANCELED)
            self.assertEqual(report.get_action_status(b).status, FAILED)
            if report.get_action_status(c).status == CANCELED:
                c_was_canceled = True
            else:
                self.assertEqual(report.get_action_status(c).status, SUCCESSFUL)
                c_was_executed = True
            if c_was_canceled and c_was_executed and b_was_added_before_c and b_was_added_after_c:
                break
        self.assertTrue(c_was_canceled)
        self.assertTrue(c_was_executed)
